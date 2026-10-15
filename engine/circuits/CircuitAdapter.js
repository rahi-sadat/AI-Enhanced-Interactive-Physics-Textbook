/**
 * engine/circuits/CircuitAdapter.js
 * 
 * Pure mathematical simulation adapter for the electrical circuits domain:
 * - CircuitCompiler (topology and branch indexing)
 * - CircuitSolver (64-bit Modified Nodal Analysis matrix engine)
 * Completely decoupled from frontend stores and view renderers.
 */

import { SimulationAdapter } from '../core/SimulationAdapter.js';
import { CircuitCompiler } from './CircuitCompiler.js';
import { CircuitSolver } from './CircuitSolver.js';
import { UnsupportedPhysicsSubtypeError, PhysicsSceneValidationError } from '../core/errors.js';

export class CircuitAdapter extends SimulationAdapter {
  static domain = 'circuits';

  constructor() {
    super();
    this.subtype = 'dc';
    this.model = null;
    this.solver = null;
    this.electricalState = null;
  }

  static canHandle(scene) {
    const domain = scene?.domain;
    return domain === 'circuits' || Boolean(scene?.circuit);
  }

  canHandle(scene) {
    return CircuitAdapter.canHandle(scene);
  }

  async initialize(scene, container = null, options = {}) {
    await super.initialize(scene, container, options);
    if (!scene.subtype) {
      throw new PhysicsSceneValidationError([{
        code: 'MISSING_SUBTYPE',
        path: 'subtype',
        message: 'Circuit scene must explicitly declare a canonical subtype (e.g. "dc").'
      }]);
    }
    this.subtype = scene.subtype;

    if (this.subtype !== 'dc' && this.subtype !== 'dc_linear') {
      throw new UnsupportedPhysicsSubtypeError('circuits', this.subtype);
    }

    if (!scene.circuit) {
      throw new PhysicsSceneValidationError([{
        code: 'MISSING_CIRCUIT_DEFINITION',
        path: 'circuit',
        message: 'Circuits adapter requires an explicit circuit graph definition.'
      }]);
    }

    // 1. Compile topology and initial solve using verified MNA engine
    this.model = CircuitCompiler.compile(scene);
    this.solver = new CircuitSolver(this.model);
    this.solve();

    this.notifyStateChange(this.getState());
  }

  solve() {
    if (!this.solver) return;
    this.electricalState = this.solver.solveDC();
  }

  /**
   * Internal hook called by SimulationAdapter after atomic validation, unit conversion,
   * and scene mutation succeed.
   */
  _applyParameterUpdate(address, convertedVal, key, targetId, incomingUnit) {
    const rawTarget = targetId || address || key;
    const compId = rawTarget.split('.')[0].replace(/_(resistance|voltage|current)$/, '');
    const comp = this.scene.circuit?.components?.find(c => c.id === compId || c.id === rawTarget || c.label === rawTarget);
    if (comp && typeof convertedVal === 'number') {
      comp.value = convertedVal;
    }
    if (this.scene?.parameters?.[compId]) {
      this.scene.parameters[compId].value = convertedVal;
    }
    if (this.scene?.parameters?.[address]) {
      this.scene.parameters[address].value = convertedVal;
    }

    if (key === 'closed' || key === 'state' || typeof convertedVal === 'boolean') {
      const swId = targetId || address.split('.')[0];
      const sw = this.scene.circuit?.components?.find(c => c.id === swId || (c.type === 'switch' && (!targetId || targetId === c.id)));
      if (sw) {
        sw.state = (convertedVal === true || convertedVal === 'closed') ? 'closed' : 'open';
      }
    }

    this.model = CircuitCompiler.compile(this.scene);
    this.solver.load(this.model);
    this.solve();
    this.notifyStateChange(this.getState());
  }

  reset() {
    super.reset();
    this.model = CircuitCompiler.compile(this.scene);
    this.solver.load(this.model);
    this.solve();
    this.notifyStateChange(this.getState());
  }

  getOutput() {
    const state = this.getState();
    const model = this.model || {};

    // Map compiled wires with topology-aware directional branch current
    const wires = (model.wires || []).map(w => {
      const flow = this._resolveWireFlow(w, model, state);

      return {
        id: w.id,
        node: w.node,
        from: w.from,
        to: w.to,
        points: w.points,
        totalLength: w.totalLength,
        segmentLengths: w.segmentLengths,
        cumulativeLengths: w.cumulativeLengths,
        current_A: flow.current_A,
        direction: flow.direction,
        getPointAtDistance: w.getPointAtDistance
      };
    });

    // Map components with live currents, power, and coordinate geometry
    const components = Array.from(model.componentById?.values() || []).map(c => {
      const cur = state.branchCurrents?.[c.id] || 0.0;
      const power = state.branchPowers?.[c.id] || 0.0;
      return {
        id: c.id,
        type: c.type,
        label: c.label,
        value: c.value,
        unit: c.unit,
        state: c.state,
        geometry: c.geometry || {},
        bbox_source_px: c.bbox_source_px || c.geometry?.bbox_source_px,
        center_source_px: c.geometry?.center_source_px,
        label_bbox_source_px: c.label_bbox_source_px || c.geometry?.label_bbox_source_px,
        terminals: c.terminals || [],
        current_A: cur,
        power_W: power
      };
    });

    // Map switches with hit targets ONLY when geometric evidence exists in scene
    const switches = (model.switches || []).map(s => {
      let hitTarget = null;
      const tA = s.terminals?.[0]?.source_px;
      const tB = s.terminals?.[1]?.source_px;
      const center = s.geometry?.center_source_px;
      const bbox = s.geometry?.bbox_source_px;

      if (center && Array.isArray(center) && center.length >= 2) {
        const radius = bbox ? Math.max(20, Math.hypot(bbox[2] - bbox[0], bbox[3] - bbox[1]) / 2) : 35;
        hitTarget = { x: center[0], y: center[1], radius };
      } else if (tA && tB && Array.isArray(tA) && Array.isArray(tB)) {
        const midX = (tA[0] + tB[0]) / 2;
        const midY = (tA[1] + tB[1]) / 2;
        const radius = Math.max(25, Math.hypot(tB[0] - tA[0], tB[1] - tA[1]) / 2 + 10);
        hitTarget = { x: midX, y: midY, radius };
      }
      // If neither center nor terminal coordinates exist: hitTarget remains null.
      // Interaction is unavailable without geometry evidence.

      return {
        id: s.id,
        state: s.state || 'closed',
        closed: s.state !== 'open',
        terminals: s.terminals || [],
        hitTarget
      };
    });

    return {
      domain: 'circuits',
      subtype: this.subtype,
      time: 0.0,
      state,
      geometry: {
        nodeVoltages: state.nodeVoltages,
        branchCurrents: state.branchCurrents,
        wires,
        components,
        switches,
        nodeLabels: model.nodeLabels ? Object.fromEntries(model.nodeLabels) : {},
        referenceNode: model.refNodeId
      },
      telemetry: state,
      events: [],
      editableParameters: this.getParameters()
    };
  }

  /**
   * Resolves physical current magnitude and flow direction for a wire polyline.
   * Accounts for node potentials, terminal locations, and charge conservation.
   * @private
   */
  _resolveWireFlow(w, model, state) {
    const pts = w.points || [];
    if (pts.length < 2) {
      return { current_A: 0.0, direction: 'none' };
    }

    const node = w.node;
    const nodeVoltages = state.nodeVoltages || {};
    const branchCurrents = state.branchCurrents || state.componentCurrents || {};

    // 1. Authoritative explicit from/to terminals
    if (w.from && w.to && model.terminalById) {
      const fromId = typeof w.from === 'object' ? w.from.terminalId : w.from;
      const toId = typeof w.to === 'object' ? w.to.terminalId : w.to;
      const tFrom = model.terminalById.get(fromId);
      const tTo = model.terminalById.get(toId);

      if (tFrom && tTo && tFrom.node !== tTo.node) {
        const vFrom = nodeVoltages[tFrom.node] ?? 0.0;
        const vTo = nodeVoltages[tTo.node] ?? 0.0;
        if (Math.abs(vFrom - vTo) > 1e-5) {
          const dir = vFrom > vTo ? 'forward' : 'backward';
          let cur = Math.abs(state.primaryCurrent || 0.0);
          if (w.currentReference?.componentId && branchCurrents[w.currentReference.componentId] !== undefined) {
            cur = Math.abs(branchCurrents[w.currentReference.componentId]);
          }
          return { current_A: cur, direction: dir };
        }
      }

      if (w.currentReference?.componentId && branchCurrents[w.currentReference.componentId] !== undefined) {
        const refCur = branchCurrents[w.currentReference.componentId];
        const sign = w.currentReference.sign ?? 1;
        const signedCur = refCur * sign;
        if (Math.abs(signedCur) > 1e-6) {
          return {
            current_A: Math.abs(signedCur),
            direction: signedCur > 0 ? 'forward' : 'backward'
          };
        }
      }
    }

    // 2. Intra-node or unanchored wire: determine flow direction from node terminals
    const terminalsOnNode = [];
    const components = Array.from(model.componentById?.values() || []);

    for (const c of components) {
      const isSource = (c.type === 'voltage_source' || c.type === 'battery' || c.type === 'dc_source');
      const terms = c.terminals || [];
      for (let idx = 0; idx < terms.length; idx++) {
        const t = terms[idx];
        const tNode = t.node || c.nodes?.[idx];
        if (tNode === node) {
          let tPos = null;
          if (t.source_px && Array.isArray(t.source_px) && t.source_px.length >= 2) {
            tPos = { x: t.source_px[0], y: t.source_px[1] };
          } else if (c.geometry?.center_source_px) {
            tPos = { x: c.geometry.center_source_px[0], y: c.geometry.center_source_px[1] };
          }

          let inj = 0.0;
          if (isSource) {
            const rawCur = branchCurrents[c.id] ?? 0.0;
            const iDelivered = -rawCur;
            const isPos = (t.polarity === '+' || t.nodeIndex === 0 || idx === 0);
            inj = isPos ? iDelivered : -iDelivered;
          } else if (c.type === 'resistor') {
            const otherNode = (c.nodes || []).find(n => n !== node) || node;
            const vOther = nodeVoltages[otherNode] ?? 0.0;
            const vThis = nodeVoltages[node] ?? 0.0;
            const rVal = c.value || 10.0;
            inj = (vOther - vThis) / rVal;
          } else if (c.type === 'switch') {
            if (c.state !== 'open') {
              const iBranch = branchCurrents[c.id] ?? 0.0;
              inj = (idx === 1) ? iBranch : -iBranch;
            }
          }

          if (tPos) {
            terminalsOnNode.push({
              id: t.id || `${c.id}.t${idx}`,
              componentId: c.id,
              componentType: c.type,
              pos: tPos,
              inj,
              branchCurrent: Math.abs(branchCurrents[c.id] ?? 0.0)
            });
          }
        }
      }
    }

    if (terminalsOnNode.length === 0) {
      if (w.currentReference?.componentId && branchCurrents) {
        const refCur = branchCurrents[w.currentReference.componentId];
        if (refCur !== undefined) {
          const cur = Math.abs(refCur);
          const dir = refCur > 0 ? 'forward' : (refCur < 0 ? 'backward' : 'none');
          return { current_A: cur, direction: dir };
        }
      }
      return { current_A: 0.0, direction: 'none' };
    }

    const p0 = { x: pts[0][0], y: pts[0][1] };
    const pEnd = { x: pts[pts.length - 1][0], y: pts[pts.length - 1][1] };
    const dx = pEnd.x - p0.x;
    const dy = pEnd.y - p0.y;

    // Find nearest terminal to wire endpoints
    let nearestTerm = terminalsOnNode[0];
    let minD = Infinity;
    for (const t of terminalsOnNode) {
      const d0 = Math.hypot(p0.x - t.pos.x, p0.y - t.pos.y);
      const d1 = Math.hypot(pEnd.x - t.pos.x, pEnd.y - t.pos.y);
      const d = Math.min(d0, d1);
      if (d < minD) {
        minD = d;
        nearestTerm = t;
      }
    }

    let curMagnitude = nearestTerm.branchCurrent;
    const spanX = Math.abs(dx);
    if (spanX > 250) {
      curMagnitude = Math.max(...terminalsOnNode.map(t => t.branchCurrent));
    }
    if ((w.from || w.to) && w.currentReference?.componentId && branchCurrents[w.currentReference.componentId] !== undefined) {
      curMagnitude = Math.abs(branchCurrents[w.currentReference.componentId]);
    }

    if (curMagnitude < 1e-6) {
      return { current_A: 0.0, direction: 'none' };
    }

    let direction = 'forward';
    const isHorizontal = Math.abs(dx) >= Math.abs(dy);

    if (isHorizontal) {
      let posWeightX = 0, sumPos = 0;
      let negWeightX = 0, sumNeg = 0;
      for (const t of terminalsOnNode) {
        if (t.inj > 1e-5) {
          posWeightX += t.pos.x * t.inj;
          sumPos += t.inj;
        } else if (t.inj < -1e-5) {
          negWeightX += t.pos.x * Math.abs(t.inj);
          sumNeg += Math.abs(t.inj);
        }
      }

      if (sumPos > 1e-5 && sumNeg > 1e-5) {
        const xIn = posWeightX / sumPos;
        const xOut = negWeightX / sumNeg;
        const flowDirX = Math.sign(xOut - xIn);
        const wireDirX = Math.sign(dx);
        direction = (wireDirX === flowDirX) ? 'forward' : 'backward';
      }
    } else {
      const d0 = Math.hypot(p0.x - nearestTerm.pos.x, p0.y - nearestTerm.pos.y);
      const d1 = Math.hypot(pEnd.x - nearestTerm.pos.x, pEnd.y - nearestTerm.pos.y);
      const pNearIsP0 = d0 < d1;

      if (nearestTerm.inj > 1e-5) {
        direction = pNearIsP0 ? 'forward' : 'backward';
      } else if (nearestTerm.inj < -1e-5) {
        direction = pNearIsP0 ? 'backward' : 'forward';
      }
    }

    return { current_A: curMagnitude, direction };
  }

  getState() {
    const es = this.electricalState || {};
    const nodeVoltages = es.nodeVoltages || {};
    const branchCurrents = es.componentCurrents || es.branchCurrents || {};
    const branchPowers = es.branchPowers || es.componentPower || {};

    let totalPower = es.totalPower !== undefined ? es.totalPower : 0.0;
    if (totalPower === 0.0 && branchPowers) {
      for (const p of Object.values(branchPowers)) {
        if (p > 0) totalPower += p;
      }
    }

    // Compute individual source currents delivered into the circuit
    const sourceCurrents = {};
    let totalSourceCurrent = 0.0;
    if (this.model?.voltageSources && branchCurrents) {
      for (const vs of this.model.voltageSources) {
        const cur = branchCurrents[vs.id];
        if (cur !== undefined) {
          const delivered = -cur;
          sourceCurrents[vs.id] = Number(delivered.toFixed(4));
          if (delivered > 1e-6) {
            totalSourceCurrent += delivered;
          }
        }
      }
    }

    const numSources = this.model?.voltageSources?.length || 0;
    // Only expose totalCurrent_A and loopCurrent_A when there is a single source with a well-defined loop/total current.
    // For arbitrary multi-source circuits, preserve branch/source currents rather than inventing an authoritative single current.
    const hasSingleSource = numSources === 1;
    const singleSourceCurrent = hasSingleSource ? (Object.values(sourceCurrents)[0] ?? 0.0) : undefined;
    const totalCurrent_A = hasSingleSource ? Number(singleSourceCurrent.toFixed(4)) : undefined;

    const state = {
      domain: 'circuits',
      subtype: this.subtype,
      running: this.running,
      nodeVoltages,
      branchCurrents,
      branchPowers,
      sourceCurrents,
      totalDeliveredSourceCurrent_A: Number(totalSourceCurrent.toFixed(4)),
      totalPower: Number(totalPower.toFixed(4))
    };

    if (totalCurrent_A !== undefined) {
      state.totalCurrent_A = totalCurrent_A;
      state.loopCurrent_A = totalCurrent_A;
    }

    return state;
  }

  getParameters() {
    const params = {};

    // 1. Include explicit scene parameters ONLY if declared editable
    if (this.scene?.parameters) {
      for (const [key, p] of Object.entries(this.scene.parameters)) {
        if (p && p.editable === true) {
          params[key] = { ...p };
        }
      }
    }

    // 2. Include components ONLY if explicitly declared editable in scene or component
    if (this.scene?.circuit?.components) {
      for (const comp of this.scene.circuit.components) {
        if (params[comp.id] || params[`${comp.id}.resistance`] || params[`${comp.id}.voltage`] || params[`${comp.id}.closed`]) {
          continue;
        }

        // Only expose if component explicitly declared editable: true
        if (comp.editable === true || comp.parameter?.editable === true) {
          if (comp.type === 'switch') {
            params[`${comp.id}.closed`] = {
              value: comp.state !== 'open',
              label: comp.label || `${comp.id} (Switch)`,
              type: 'boolean',
              editable: true,
              provenance: comp.provenance || 'observed',
              control: comp.control || { type: 'toggle' }
            };
          } else if (comp.value !== undefined) {
            const key = (comp.type === 'voltage_source' || comp.type === 'battery') ? 'voltage' : 'resistance';
            const unit = comp.unit || ((comp.type === 'voltage_source' || comp.type === 'battery') ? 'V' : 'Ω');
            const pMeta = comp.parameter || {};
            params[`${comp.id}.${key}`] = {
              value: comp.value,
              unit,
              label: comp.label || `${comp.id} (${key})`,
              editable: true,
              provenance: comp.provenance || pMeta.provenance || 'observed',
              ...(pMeta.min !== undefined ? { min: pMeta.min } : {}),
              ...(pMeta.max !== undefined ? { max: pMeta.max } : {}),
              ...(pMeta.step !== undefined ? { step: pMeta.step } : {}),
              control: pMeta.control || comp.control || { type: 'number' }
            };
          }
        }
      }
    }
    return params;
  }

  dispose() {
    this.model = null;
    this.solver = null;
    this.electricalState = null;
    super.dispose();
  }
}

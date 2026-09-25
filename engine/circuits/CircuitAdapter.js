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
      let current_A = 0.0;
      let direction = 'none';

      // 1. Authoritative structural currentReference (from scene or compiler)
      if (w.currentReference?.componentId && state.branchCurrents) {
        const refCur = state.branchCurrents[w.currentReference.componentId];
        if (refCur !== undefined) {
          const sign = w.currentReference.sign ?? 1;
          current_A = refCur * sign;
        }
      }

      // If cannot be mapped confidently, return direction: "none" rather than inventing current flow
      if (Math.abs(current_A) > 1e-6) {
        direction = current_A > 0 ? 'forward' : 'backward';
      } else {
        current_A = 0.0;
        direction = 'none';
      }

      return {
        id: w.id,
        node: w.node,
        from: w.from,
        to: w.to,
        points: w.points,
        totalLength: w.totalLength,
        segmentLengths: w.segmentLengths,
        cumulativeLengths: w.cumulativeLengths,
        current_A,
        direction
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

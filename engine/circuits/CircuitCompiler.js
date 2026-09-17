/**
 * circuits/CircuitCompiler.js
 * Compiles a raw CircuitScene v3 into an indexed, solver-ready CircuitModel
 * and precomputes polyline metrics for 60 FPS particle animation and hit testing.
 */

export class CircuitCompiler {
  /**
   * Compile a raw CircuitScene into a structured CircuitModel.
   * @param {object} scene - Raw canonical CircuitScene v3 object
   * @returns {object} Compiled CircuitModel
   */
  static compile(scene) {
    if (!scene || !scene.circuit) {
      throw new Error('[CircuitCompiler] Invalid scene: missing circuit definition.');
    }

    const rawCircuit = scene.circuit;
    const rawNodes = rawCircuit.nodes || [];
    const rawComponents = rawCircuit.components || [];
    const rawWires = rawCircuit.wires || [];

    // 1. Identify or auto-select reference ground node
    let refNodeId = rawCircuit.reference_node;
    if (!refNodeId) {
      // Auto-select negative terminal of first voltage source or first node
      const vSource = rawComponents.find(c => c.type === 'voltage_source' || c.type === 'battery');
      if (vSource && vSource.terminals) {
        const negTerm = vSource.terminals.find(t => t.polarity === '-' || t.id?.endsWith('.n'));
        refNodeId = negTerm?.node || vSource.nodes?.[1] || rawNodes[0]?.id;
      } else {
        refNodeId = rawNodes[0]?.id || 'N0';
      }
    }

    // 2. Build Node Index Map (excluding reference node which is fixed at 0V)
    const nodeIndex = new Map();
    const nodeLabels = new Map();
    let nextNodeIdx = 0;

    for (const node of rawNodes) {
      const id = typeof node === 'string' ? node : node.id;
      const label = (typeof node === 'object' && node.label) || id;
      nodeLabels.set(id, label);

      if (id === refNodeId) {
        nodeIndex.set(id, -1); // Ground reference
      } else if (!nodeIndex.has(id)) {
        nodeIndex.set(id, nextNodeIdx++);
      }
    }

    // Ensure any nodes referenced by components exist in nodeIndex
    for (const comp of rawComponents) {
      const nodes = comp.nodes || (Array.isArray(comp.terminals) ? comp.terminals.map(t => t.node).filter(Boolean) : []);
      for (const nid of nodes) {
        if (!nodeIndex.has(nid)) {
          if (nid === refNodeId) {
            nodeIndex.set(nid, -1);
          } else {
            nodeIndex.set(nid, nextNodeIdx++);
            nodeLabels.set(nid, nid);
          }
        }
      }
    }

    const numUnknownNodes = nextNodeIdx;

    // 3. Classify components and assign auxiliary source current variables
    const voltageSources = [];
    const resistors = [];
    const switches = [];
    const ammeters = [];
    const voltmeters = [];
    const componentById = new Map();
    const terminalById = new Map();

    let nextSourceIdx = 0;

    for (const comp of rawComponents) {
      const c = { ...comp };

      // Ensure nodes array is populated from terminals if not present
      if ((!c.nodes || c.nodes.length === 0) && Array.isArray(c.terminals)) {
        c.nodes = c.terminals.map(t => t.node).filter(Boolean);
      }

      // Ensure value and unit are populated from parameters if not present
      if (c.value === undefined && c.parameters) {
        const p = c.parameters.voltage_v || c.parameters.voltage ||
                  c.parameters.resistance_ohm || c.parameters.resistance ||
                  c.parameters.current_a || c.parameters.current ||
                  c.parameters.capacitance_f || c.parameters.capacitance;
        if (p && p.value !== undefined) {
          c.value = Number(p.value);
          c.unit = p.unit || c.unit;
        }
      }

      // Ensure geometry is populated
      if (!c.geometry) {
        c.geometry = {};
      }
      if (c.bbox_source_px && !c.geometry.bbox_source_px) {
        c.geometry.bbox_source_px = c.bbox_source_px;
      }
      if (c.geometry.bbox_source_px && !c.geometry.center_source_px) {
        const [x1, y1, x2, y2] = c.geometry.bbox_source_px;
        c.geometry.center_source_px = [(x1 + x2) / 2, (y1 + y2) / 2];
      }

      if (!c.label) {
        c.label = `${c.id} (${c.type})`;
      }

      componentById.set(c.id, c);

      // Index terminals
      if (Array.isArray(c.terminals)) {
        for (const t of c.terminals) {
          terminalById.set(t.id, {
            ...t,
            componentId: c.id,
            source_px: t.source_px ? [...t.source_px] : [0, 0]
          });
        }
      }

      switch (c.type) {
        case 'voltage_source':
        case 'battery':
        case 'dc_source':
          c.sourceVarIndex = nextSourceIdx++;
          voltageSources.push(c);
          break;

        case 'resistor':
        case 'bulb':
        case 'lamp':
          resistors.push(c);
          break;

        case 'switch':
          // Closed switch adds a 0V constraint between its nodes
          if (c.state !== 'open') {
            c.sourceVarIndex = nextSourceIdx++;
          } else {
            c.sourceVarIndex = -1;
          }
          switches.push(c);
          break;

        case 'ammeter':
          // Ideal ammeter acts as a 0V voltage source to measure series current
          c.sourceVarIndex = nextSourceIdx++;
          ammeters.push(c);
          break;

        case 'voltmeter':
          // Ideal voltmeter is high impedance (open circuit probe)
          c.sourceVarIndex = -1;
          voltmeters.push(c);
          break;

        default:
          console.warn(`[CircuitCompiler] Unknown component type "${c.type}" on ${c.id}`);
          break;
      }
    }

    const numAuxVariables = nextSourceIdx;
    const matrixSize = numUnknownNodes + numAuxVariables;

    // 4. Precompute Wire Polylines and Parametric Lengths for Smooth Particle Flow
    const compiledWires = [];
    const wireById = new Map();

    for (const wire of rawWires) {
      const pts = wire.polyline_source_px || wire.points || [];
      const poly = this._compilePolyline(pts);
      const compiledWire = {
        id: wire.id,
        node: wire.node,
        points: pts,
        totalLength: poly.totalLength,
        segmentLengths: poly.segmentLengths,
        cumulativeLengths: poly.cumulativeLengths,
        getPointAtDistance: (d) => poly.getPointAtDistance(d)
      };
      compiledWires.push(compiledWire);
      wireById.set(wire.id, compiledWire);
    }

    return {
      scene,
      refNodeId,
      nodeIndex,
      nodeLabels,
      numUnknownNodes,
      numAuxVariables,
      matrixSize,
      voltageSources,
      resistors,
      switches,
      ammeters,
      voltmeters,
      componentById,
      terminalById,
      wires: compiledWires,
      wireById,
      // Helper to update a parameter without full recompile if topology didn't change
      setParameter(compOriginalId, paramKey, value) {
        const target = componentById.get(compOriginalId);
        if (target) {
          target[paramKey] = value;
          if (target.parameter && target.parameter[paramKey]) {
            target.parameter[paramKey].value = value;
          }
        }
      },
      // Helper to toggle a switch
      toggleSwitch(switchId) {
        const sw = componentById.get(switchId);
        if (sw && sw.type === 'switch') {
          sw.state = (sw.state === 'open') ? 'closed' : 'open';
        }
      }
    };
  }

  /**
   * Precomputes length profiles and fast distance lookup for polyline wires.
   * @private
   */
  static _compilePolyline(pts) {
    if (!pts || pts.length < 2) {
      return {
        totalLength: 0,
        segmentLengths: [],
        cumulativeLengths: [0],
        getPointAtDistance: () => ({ x: pts?.[0]?.[0] || 0, y: pts?.[0]?.[1] || 0, angle: 0 })
      };
    }

    const segmentLengths = [];
    const cumulativeLengths = [0];
    let totalLength = 0;

    for (let i = 0; i < pts.length - 1; i++) {
      const dx = pts[i + 1][0] - pts[i][0];
      const dy = pts[i + 1][1] - pts[i][1];
      const len = Math.hypot(dx, dy);
      segmentLengths.push(len);
      totalLength += len;
      cumulativeLengths.push(totalLength);
    }

    const getPointAtDistance = (dist) => {
      if (totalLength <= 0) return { x: pts[0][0], y: pts[0][1], angle: 0 };

      // Wrap distance inside [0, totalLength)
      const d = ((dist % totalLength) + totalLength) % totalLength;

      // Find segment containing distance d
      for (let i = 0; i < segmentLengths.length; i++) {
        const segStart = cumulativeLengths[i];
        const segEnd = cumulativeLengths[i + 1];
        const segLen = segmentLengths[i];

        if (d >= segStart && d <= segEnd && segLen > 0) {
          const t = (d - segStart) / segLen;
          const x = pts[i][0] + t * (pts[i + 1][0] - pts[i][0]);
          const y = pts[i][1] + t * (pts[i + 1][1] - pts[i][1]);
          const angle = Math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]);
          return { x, y, angle };
        }
      }

      const last = pts[pts.length - 1];
      return { x: last[0], y: last[1], angle: 0 };
    };

    return { totalLength, segmentLengths, cumulativeLengths, getPointAtDistance };
  }
}

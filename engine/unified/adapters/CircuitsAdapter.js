/**
 * CircuitsAdapter.js
 * 
 * Domain adapter for electrical networks compiling DC circuits into the UnifiedEngineCore.
 * Formulates Modified Nodal Analysis (MNA) equations as residual functions F(z) = 0
 * and analytical Jacobian matrices for the core linear solver.
 * 
 * Invariant Rules:
 *   - Zero solving logic: delegates matrix inversion and equilibrium to UnifiedEngineCore.
 *   - No imports of other domain adapters — only shared core primitives.
 *   - Physical laws (KCL, Ohm's Law, KVL) are explicitly commented on every equation.
 */

export class CircuitsAdapter {
  constructor() {
    this.core = null;
    this.scene = null;

    // Compiled topology
    this.referenceNode = 'N0';
    this.nodes = [];            // List of all node IDs
    this.nonRefNodes = [];       // List of non-reference node IDs
    this.nodeIndexMap = new Map(); // nodeId -> index (0..n-1)

    this.components = [];        // List of all components
    this.resistors = [];         // [{ id, node1, node2, value }]
    this.voltageSources = [];    // [{ id, nodePlus, nodeMinus, value, auxIndex }]
    this.switches = [];          // [{ id, node1, node2, state, auxIndex }]
    this.ammeters = [];          // [{ id, node1, node2, auxIndex }]

    this.totalUnknowns = 0;      // n (nodes) + m (voltage constraints)
    this.state = null;
  }

  attachCore(core) {
    this.core = core;
  }

  /**
   * Compiles canonical circuit scene JSON into MNA indices and initial algebraic state.
   * @param {object} scene - Canonical CircuitScene v3 or compatible object
   * @returns {{ isAlgebraic: boolean, algebraicState: number[] }}
   */
  compileScene(scene) {
    this.scene = scene;
    const circuit = scene.circuit || scene;

    this.referenceNode = circuit.reference_node || 'N0';

    // 1. Gather all unique nodes
    const rawNodes = new Set();
    if (Array.isArray(circuit.nodes)) {
      circuit.nodes.forEach(n => {
        if (typeof n === 'string') rawNodes.add(n);
        else if (n && n.id) rawNodes.add(n.id);
      });
    }
    const rawComponents = circuit.components || scene.elements || [];

    rawComponents.forEach(c => {
      const nodes = c.nodes || [c.nodePlus, c.nodeMinus] || [];
      nodes.forEach(n => { if (n) rawNodes.add(n); });
    });

    this.nodes = Array.from(rawNodes);
    if (!this.nodes.includes(this.referenceNode)) {
      this.nodes.unshift(this.referenceNode);
    }

    this.nonRefNodes = this.nodes.filter(n => n !== this.referenceNode);
    this.nodeIndexMap.clear();
    this.nonRefNodes.forEach((nodeId, idx) => {
      this.nodeIndexMap.set(nodeId, idx);
    });

    // 2. Classify components
    this.resistors = [];
    this.voltageSources = [];
    this.switches = [];
    this.ammeters = [];
    this.components = [];

    let auxIdx = 0;

    rawComponents.forEach(c => {
      const type = c.type || c.semantic_label;
      const compObj = {
        id: c.id,
        type,
        nodes: c.nodes || [],
        value: Number(c.value ?? 0),
        state: c.state || 'closed'
      };
      this.components.push(compObj);

      if (type === 'resistor' || type === 'galvanometer' || type === 'bulb') {
        this.resistors.push({
          id: c.id,
          node1: c.nodes[0],
          node2: c.nodes[1],
          value: Math.max(1e-9, Number(c.value ?? 10.0))
        });
      } else if (type === 'voltage_source' || type === 'battery' || type === 'dc_source') {
        this.voltageSources.push({
          id: c.id,
          nodePlus: c.nodes[0],
          nodeMinus: c.nodes[1],
          value: Number(c.value ?? 12.0),
          auxIndex: auxIdx++
        });
      } else if (type === 'switch') {
        const isOpen = c.state === 'open';
        this.switches.push({
          id: c.id,
          node1: c.nodes[0],
          node2: c.nodes[1],
          state: isOpen ? 'open' : 'closed',
          auxIndex: isOpen ? -1 : auxIdx++ // Closed switches enforce 0V branch constraint
        });
      } else if (type === 'ammeter') {
        this.ammeters.push({
          id: c.id,
          node1: c.nodes[0],
          node2: c.nodes[1],
          auxIndex: auxIdx++ // Ideal ammeters enforce 0V branch constraint
        });
      }
    });

    const numNodes = this.nonRefNodes.length;
    const numAux = auxIdx;
    this.totalUnknowns = numNodes + numAux;

    return {
      isAlgebraic: true,
      algebraicState: new Array(this.totalUnknowns).fill(0.0)
    };
  }

  /**
   * Evaluates Modified Nodal Analysis residual vector F(z) = 0.
   * Unknown vector:
   *   z = [V_1, V_2, ..., V_n, I_{V1}, ..., I_{Vm}]^T
   * 
   * PHYSICAL LAWS ENCODED:
   * 1. Kirchhoff's Current Law (KCL) at each non-reference node:
   *      sum_{connected} I_out = 0
   * 2. Ohm's Law for Resistors:
   *      I_{ij} = G_{ij} * (V_i - V_j) where G = 1/R
   * 3. Voltage Source Constitutive Law (Branch KVL):
   *      V_plus - V_minus = V_s
   * 4. Ideal Closed Switch & Ammeter Constraint:
   *      V_1 - V_2 = 0
   */
  evaluateResiduals(z) {
    const n = this.nonRefNodes.length;
    const F = new Float64Array(this.totalUnknowns);

    const getV = (nodeId) => {
      if (nodeId === this.referenceNode) return 0.0;
      const idx = this.nodeIndexMap.get(nodeId);
      return idx !== undefined ? z[idx] : 0.0;
    };

    // 1. Resistor KCL contributions: I = G * (V_i - V_j)
    for (const r of this.resistors) {
      const v1 = getV(r.node1);
      const v2 = getV(r.node2);
      const G = 1.0 / r.value;
      const I = G * (v1 - v2);

      const idx1 = this.nodeIndexMap.get(r.node1);
      const idx2 = this.nodeIndexMap.get(r.node2);

      // Physical Law: Current leaving node 1 enters node 2 (KCL)
      if (idx1 !== undefined) F[idx1] += I;
      if (idx2 !== undefined) F[idx2] -= I;
    }

    // 2. Voltage Source KCL & Constitutive Equations
    for (const vs of this.voltageSources) {
      const idxPlus = this.nodeIndexMap.get(vs.nodePlus);
      const idxMinus = this.nodeIndexMap.get(vs.nodeMinus);
      const branchI = z[n + vs.auxIndex];

      // Physical Law: Current leaving (+) terminal into circuit
      if (idxPlus !== undefined) F[idxPlus] += branchI;
      if (idxMinus !== undefined) F[idxMinus] -= branchI;

      // Physical Law: Constitutive Voltage Law: V_plus - V_minus - V_s = 0
      const vPlus = getV(vs.nodePlus);
      const vMinus = getV(vs.nodeMinus);
      F[n + vs.auxIndex] = (vPlus - vMinus) - vs.value;
    }

    // 3. Closed Switches (0V voltage constraint)
    for (const sw of this.switches) {
      if (sw.state === 'closed' && sw.auxIndex >= 0) {
        const idx1 = this.nodeIndexMap.get(sw.node1);
        const idx2 = this.nodeIndexMap.get(sw.node2);
        const branchI = z[n + sw.auxIndex];

        if (idx1 !== undefined) F[idx1] += branchI;
        if (idx2 !== undefined) F[idx2] -= branchI;

        // Physical Law: Zero voltage drop across ideal closed switch: V_1 - V_2 = 0
        const v1 = getV(sw.node1);
        const v2 = getV(sw.node2);
        F[n + sw.auxIndex] = v1 - v2;
      }
    }

    // 4. Ideal Ammeters (0V branch constraint)
    for (const am of this.ammeters) {
      const idx1 = this.nodeIndexMap.get(am.node1);
      const idx2 = this.nodeIndexMap.get(am.node2);
      const branchI = z[n + am.auxIndex];

      if (idx1 !== undefined) F[idx1] += branchI;
      if (idx2 !== undefined) F[idx2] -= branchI;

      // Physical Law: Ideal ammeter has 0 Ohm resistance: V_1 - V_2 = 0
      const v1 = getV(am.node1);
      const v2 = getV(am.node2);
      F[n + am.auxIndex] = v1 - v2;
    }

    return F;
  }

  /**
   * Assembles analytical MNA Jacobian matrix J = dF / dz.
   * Stamped directly with conductances G and constraint coefficients +/-1.
   * @param {Float64Array} z
   * @returns {Float64Array} Flat (totalUnknowns x totalUnknowns) matrix
   */
  evaluateJacobian(z) {
    const N = this.totalUnknowns;
    const n = this.nonRefNodes.length;
    const J = new Float64Array(N * N);

    const stamp = (r, c, val) => {
      if (r >= 0 && r < N && c >= 0 && c < N) {
        J[r * N + c] += val;
      }
    };

    // Resistors: Conductance stamps
    for (const r of this.resistors) {
      const i = this.nodeIndexMap.get(r.node1);
      const j = this.nodeIndexMap.get(r.node2);
      const G = 1.0 / r.value;

      if (i !== undefined) stamp(i, i, G);
      if (j !== undefined) stamp(j, j, G);
      if (i !== undefined && j !== undefined) {
        stamp(i, j, -G);
        stamp(j, i, -G);
      }
    }

    // Voltage Sources: B & C stamps
    for (const vs of this.voltageSources) {
      const i = this.nodeIndexMap.get(vs.nodePlus);
      const j = this.nodeIndexMap.get(vs.nodeMinus);
      const k = n + vs.auxIndex;

      if (i !== undefined) {
        stamp(i, k, 1.0);  // KCL auxiliary current out
        stamp(k, i, 1.0);  // Constitutive V_plus
      }
      if (j !== undefined) {
        stamp(j, k, -1.0); // KCL auxiliary current in
        stamp(k, j, -1.0); // Constitutive V_minus
      }
    }

    // Closed Switches
    for (const sw of this.switches) {
      if (sw.state === 'closed' && sw.auxIndex >= 0) {
        const i = this.nodeIndexMap.get(sw.node1);
        const j = this.nodeIndexMap.get(sw.node2);
        const k = n + sw.auxIndex;

        if (i !== undefined) { stamp(i, k, 1.0); stamp(k, i, 1.0); }
        if (j !== undefined) { stamp(j, k, -1.0); stamp(k, j, -1.0); }
      }
    }

    // Ammeters
    for (const am of this.ammeters) {
      const i = this.nodeIndexMap.get(am.node1);
      const j = this.nodeIndexMap.get(am.node2);
      const k = n + am.auxIndex;

      if (i !== undefined) { stamp(i, k, 1.0); stamp(k, i, 1.0); }
      if (j !== undefined) { stamp(j, k, -1.0); stamp(k, j, -1.0); }
    }

    return J;
  }

  setParameter(id, value) {
    const num = Number(value);
    const comp = this.components.find(c => c.id === id);
    if (!comp) return;

    if (comp.type === 'resistor') {
      const r = this.resistors.find(r => r.id === id);
      if (r && num > 0) {
        r.value = num;
        comp.value = num;
      }
    } else if (comp.type === 'voltage_source') {
      const vs = this.voltageSources.find(v => v.id === id);
      if (vs) {
        vs.value = num;
        comp.value = num;
      }
    } else if (comp.type === 'switch') {
      const sw = this.switches.find(s => s.id === id);
      if (sw) {
        sw.state = value === 'open' ? 'open' : 'closed';
        comp.state = sw.state;
        const rawComp = (this.scene?.circuit?.components || this.scene?.components || this.scene?.elements || []).find(c => c.id === id);
        if (rawComp) rawComp.state = sw.state;
        // Re-compile indices because switch open/close alters aux constraints
        if (this.core) {
          const compiled = this.compileScene(this.scene);
          this.core.z = new Float64Array(compiled.algebraicState);
        }
      }
    }
  }

  toggleSwitch(id) {
    const sw = this.switches.find(s => s.id === id);
    if (sw) {
      this.setParameter(id, sw.state === 'closed' ? 'open' : 'closed');
    }
  }

  extractState(core) {
    const z = core.z || new Float64Array(this.totalUnknowns);
    const n = this.nonRefNodes.length;

    const nodeVoltages = { [this.referenceNode]: 0.0 };
    this.nonRefNodes.forEach((nodeId, idx) => {
      nodeVoltages[nodeId] = Number(z[idx] ?? 0.0);
    });

    const getV = (nodeId) => nodeVoltages[nodeId] ?? 0.0;

    const componentVoltages = {};
    const componentCurrents = {};
    const componentPower = {};

    let totalPower = 0.0;

    // Resistors
    for (const r of this.resistors) {
      const vDrop = Math.abs(getV(r.node1) - getV(r.node2));
      const I = vDrop / r.value;
      const P = vDrop * I;

      componentVoltages[r.id] = vDrop;
      componentCurrents[r.id] = I;
      componentPower[r.id] = P;
      totalPower += P;
    }

    // Voltage Sources
    let primaryCurrent = 0.0;
    for (const vs of this.voltageSources) {
      const I = Math.abs(z[n + vs.auxIndex] ?? 0.0);
      componentVoltages[vs.id] = vs.value;
      componentCurrents[vs.id] = I;
      componentPower[vs.id] = vs.value * I;
      if (I > primaryCurrent) primaryCurrent = I;
    }

    // Switches
    for (const sw of this.switches) {
      const vDrop = Math.abs(getV(sw.node1) - getV(sw.node2));
      let I = 0.0;
      if (sw.state === 'closed' && sw.auxIndex >= 0) {
        I = Math.abs(z[n + sw.auxIndex] ?? 0.0);
      }
      componentVoltages[sw.id] = vDrop;
      componentCurrents[sw.id] = I;
      componentPower[sw.id] = 0.0;
    }

    // Ammeters
    for (const am of this.ammeters) {
      const I = Math.abs(z[n + am.auxIndex] ?? 0.0);
      componentVoltages[am.id] = 0.0;
      componentCurrents[am.id] = I;
      componentPower[am.id] = 0.0;
    }

    // Equivalent resistance of the circuit: R_eq = V_source / I_primary
    const mainV = this.voltageSources[0]?.value || 12.0;
    const equivalentResistance = primaryCurrent > 1e-9 ? mainV / primaryCurrent : Infinity;

    return {
      domain: 'circuits',
      type: 'dc_network',
      success: true,
      nodeVoltages,
      componentVoltages,
      componentCurrents,
      componentPower,
      primaryCurrent,
      totalPower,
      equivalentResistance
    };
  }
}

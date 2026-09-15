/**
 * circuits/CircuitSolver.js
 * Browser-native Modified Nodal Analysis (MNA) solver for DC linear circuits.
 * Solves A * x = z to compute node voltages, branch currents, and component power.
 */

import { LinearSystem } from './LinearSystem.js';

export class CircuitSolver {
  /**
   * @param {object} model - Compiled CircuitModel from CircuitCompiler
   */
  constructor(model) {
    this.model = model;
  }

  /**
   * Update or reload the compiled circuit model.
   * @param {object} model
   */
  load(model) {
    this.model = model;
  }

  /**
   * Solve DC Operating Point.
   * @returns {object} ElectricalState
   */
  solveDC() {
    const {
      refNodeId,
      nodeIndex,
      numUnknownNodes,
      matrixSize,
      voltageSources,
      resistors,
      switches,
      ammeters,
      voltmeters
    } = this.model;

    if (matrixSize === 0) {
      return this._emptyState();
    }

    const n = matrixSize;
    const A = LinearSystem.createMatrix(n);
    const z = LinearSystem.createVector(n);

    // Helper to add conductance G between node1 and node2
    const stampConductance = (node1Id, node2Id, G) => {
      const i = nodeIndex.get(node1Id);
      const j = nodeIndex.get(node2Id);

      if (i !== undefined && i >= 0) {
        A[i * n + i] += G;
      }
      if (j !== undefined && j >= 0) {
        A[j * n + j] += G;
      }
      if (i !== undefined && i >= 0 && j !== undefined && j >= 0) {
        A[i * n + j] -= G;
        A[j * n + i] -= G;
      }
    };

    // Helper to stamp ideal voltage constraint (V_pos - V_neg = V_val)
    const stampVoltageSource = (posNodeId, negNodeId, vValue, auxIndex) => {
      const i = nodeIndex.get(posNodeId);
      const j = nodeIndex.get(negNodeId);
      const row = numUnknownNodes + auxIndex;

      if (i !== undefined && i >= 0) {
        A[row * n + i] += 1.0;
        A[i * n + row] += 1.0;
      }
      if (j !== undefined && j >= 0) {
        A[row * n + j] -= 1.0;
        A[j * n + row] -= 1.0;
      }
      z[row] = vValue;
    };

    // 1. Stamp Resistors
    for (const r of resistors) {
      const resistance = Number(r.value ?? r.resistance ?? 10.0);
      if (resistance <= 0) {
        throw new Error(`Invalid non-positive resistance on ${r.id}: ${resistance} Ω`);
      }
      const G = 1.0 / resistance;
      const [n1, n2] = r.nodes || [];
      stampConductance(n1, n2, G);
    }

    // 2. Stamp Voltage Sources
    for (const vs of voltageSources) {
      const [nPos, nNeg] = vs.nodes || [];
      const val = Number(vs.value ?? vs.voltage ?? 0.0);
      stampVoltageSource(nPos, nNeg, val, vs.sourceVarIndex);
    }

    // 3. Stamp Switches
    for (const sw of switches) {
      if (sw.state !== 'open' && sw.sourceVarIndex >= 0) {
        // Closed switch is stamped as a 0V constraint between its nodes
        const [n1, n2] = sw.nodes || [];
        stampVoltageSource(n1, n2, 0.0, sw.sourceVarIndex);
      }
      // If switch is open, it has no branch stamp (conductance = 0)
    }

    // 4. Stamp Ammeters (0V branch constraint to read current directly)
    for (const am of ammeters) {
      if (am.sourceVarIndex >= 0) {
        const [n1, n2] = am.nodes || [];
        stampVoltageSource(n1, n2, 0.0, am.sourceVarIndex);
      }
    }

    // 5. Solve linear system A * x = z
    let x;
    try {
      x = LinearSystem.solve(n, A, z);
    } catch (err) {
      console.warn('[CircuitSolver] Linear solve failed:', err.message);
      return this._fallbackState(err.message);
    }

    // 6. Assemble complete ElectricalState
    const nodeVoltages = { [refNodeId]: 0.0 };
    for (const [nodeId, idx] of nodeIndex.entries()) {
      if (idx >= 0 && idx < numUnknownNodes) {
        nodeVoltages[nodeId] = x[idx];
      }
    }

    const componentVoltages = {};
    const componentCurrents = {};
    const componentPower = {};

    // Compute Resistor quantities
    for (const r of resistors) {
      const [n1, n2] = r.nodes || [];
      const v1 = nodeVoltages[n1] ?? 0.0;
      const v2 = nodeVoltages[n2] ?? 0.0;
      const vDrop = v1 - v2;
      const resistance = Number(r.value ?? r.resistance ?? 10.0);
      const current = vDrop / resistance;

      componentVoltages[r.id] = vDrop;
      componentCurrents[r.id] = current;
      componentPower[r.id] = Math.abs(vDrop * current);
    }

    // Compute Voltage Source quantities
    let primarySourceCurrent = 0.0;
    for (const vs of voltageSources) {
      const [nPos, nNeg] = vs.nodes || [];
      const vPos = nodeVoltages[nPos] ?? 0.0;
      const vNeg = nodeVoltages[nNeg] ?? 0.0;
      const row = numUnknownNodes + vs.sourceVarIndex;
      // In our stamp: KCL row had +1 at nodePos, so x[row] is current entering nodePos from source
      const iSource = x[row];

      componentVoltages[vs.id] = vPos - vNeg;
      componentCurrents[vs.id] = iSource;
      componentPower[vs.id] = Math.abs((vPos - vNeg) * iSource);

      if (primarySourceCurrent === 0.0) {
        primarySourceCurrent = Math.abs(iSource);
      }
    }

    // Compute Switch quantities
    for (const sw of switches) {
      const [n1, n2] = sw.nodes || [];
      const v1 = nodeVoltages[n1] ?? 0.0;
      const v2 = nodeVoltages[n2] ?? 0.0;
      if (sw.state === 'open') {
        componentVoltages[sw.id] = v1 - v2;
        componentCurrents[sw.id] = 0.0;
        componentPower[sw.id] = 0.0;
      } else {
        const row = numUnknownNodes + sw.sourceVarIndex;
        componentVoltages[sw.id] = 0.0;
        componentCurrents[sw.id] = x[row];
        componentPower[sw.id] = 0.0;
      }
    }

    // Compute Ammeter quantities
    for (const am of ammeters) {
      const row = numUnknownNodes + am.sourceVarIndex;
      componentVoltages[am.id] = 0.0;
      componentCurrents[am.id] = x[row];
      componentPower[am.id] = 0.0;
    }

    // Compute Voltmeter quantities (high impedance probe)
    for (const vm of voltmeters) {
      const [n1, n2] = vm.nodes || [];
      const v1 = nodeVoltages[n1] ?? 0.0;
      const v2 = nodeVoltages[n2] ?? 0.0;
      componentVoltages[vm.id] = v1 - v2;
      componentCurrents[vm.id] = 0.0;
      componentPower[vm.id] = 0.0;
    }

    // Summary calculations
    const primaryVs = voltageSources[0];
    const sourceV = primaryVs ? Number(primaryVs.value ?? 12.0) : 12.0;
    const equivalentResistance = primarySourceCurrent > 1e-12 ? sourceV / primarySourceCurrent : Infinity;
    const totalPower = Object.values(componentPower).reduce((acc, p) => acc + p, 0) / 2.0; // split between source & loads

    return {
      success: true,
      time: 0,
      refNodeId,
      nodeVoltages,
      componentVoltages,
      componentCurrents,
      componentPower,
      equivalentResistance,
      totalPower,
      primaryCurrent: primarySourceCurrent
    };
  }

  _emptyState() {
    return {
      success: true,
      refNodeId: this.model.refNodeId || 'N0',
      nodeVoltages: {},
      componentVoltages: {},
      componentCurrents: {},
      componentPower: {},
      equivalentResistance: 0,
      totalPower: 0,
      primaryCurrent: 0
    };
  }

  _fallbackState(errorMsg) {
    return {
      success: false,
      error: errorMsg,
      refNodeId: this.model.refNodeId || 'N0',
      nodeVoltages: {},
      componentVoltages: {},
      componentCurrents: {},
      componentPower: {},
      equivalentResistance: 0,
      totalPower: 0,
      primaryCurrent: 0
    };
  }
}

/**
 * test/test_circuit_solver.js
 * Automated unit test suite verifying browser Modified Nodal Analysis (MNA) solver
 * against exact analytical circuit physics.
 */

import assert from 'node:assert';
import { CircuitCompiler } from '../src/circuits/CircuitCompiler.js';
import { CircuitSolver } from '../src/circuits/CircuitSolver.js';

let passed = 0;
let total = 0;

function test(name, fn) {
  total++;
  try {
    fn();
    console.log(`  ✓ ${name}`);
    passed++;
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    ${err.message}`);
  }
}

function approx(actual, expected, tol = 1e-9, msg = '') {
  const diff = Math.abs(actual - expected);
  assert(diff <= tol, `${msg} Expected ${expected}, got ${actual} (diff: ${diff.toExponential(3)})`);
}

console.log('\n=== Testing Circuit MNA Solver & Linear Algebra ===\n');

// -----------------------------------------------------------------------------
// 1. Series DC Circuit (NCTB Textbook Standard)
// -----------------------------------------------------------------------------
test('Series Circuit: 12V Battery + S1 (closed) + 10Ω (R1) + 20Ω (R2)', () => {
  const scene = {
    circuit: {
      reference_node: 'N0',
      nodes: ['N0', 'N1', 'N1b', 'N2'],
      components: [
        { id: 'V1', type: 'voltage_source', value: 12.0, nodes: ['N1', 'N0'] },
        { id: 'S1', type: 'switch', state: 'closed', nodes: ['N1', 'N1b'] },
        { id: 'R1', type: 'resistor', value: 10.0, nodes: ['N1b', 'N2'] },
        { id: 'R2', type: 'resistor', value: 20.0, nodes: ['N2', 'N0'] }
      ]
    }
  };

  const model = CircuitCompiler.compile(scene);
  const solver = new CircuitSolver(model);
  const state = solver.solveDC();

  assert(state.success, 'Solver should succeed');
  approx(state.nodeVoltages['N1'], 12.0, 1e-12, 'Node N1 voltage');
  approx(state.nodeVoltages['N1b'], 12.0, 1e-12, 'Node N1b voltage (closed switch)');
  approx(state.nodeVoltages['N2'], 8.0, 1e-12, 'Node N2 voltage (divider midpoint)');
  approx(state.nodeVoltages['N0'], 0.0, 1e-12, 'Reference ground N0 voltage');

  approx(state.componentCurrents['R1'], 0.4, 1e-12, 'Current through R1 (0.4A)');
  approx(state.componentCurrents['R2'], 0.4, 1e-12, 'Current through R2 (0.4A)');
  approx(state.componentVoltages['R1'], 4.0, 1e-12, 'Voltage drop across R1 (4V)');
  approx(state.componentVoltages['R2'], 8.0, 1e-12, 'Voltage drop across R2 (8V)');

  approx(state.componentPower['R1'], 1.6, 1e-12, 'Power R1 (1.6W)');
  approx(state.componentPower['R2'], 3.2, 1e-12, 'Power R2 (3.2W)');
  approx(state.equivalentResistance, 30.0, 1e-12, 'Equivalent resistance (30Ω)');
  approx(state.totalPower, 4.8, 1e-12, 'Total power (4.8W)');
});

// -----------------------------------------------------------------------------
// 2. Switch Toggle (Open State)
// -----------------------------------------------------------------------------
test('Series Circuit with Switch OPEN: Current must be 0A', () => {
  const scene = {
    circuit: {
      reference_node: 'N0',
      nodes: ['N0', 'N1', 'N1b', 'N2'],
      components: [
        { id: 'V1', type: 'voltage_source', value: 12.0, nodes: ['N1', 'N0'] },
        { id: 'S1', type: 'switch', state: 'open', nodes: ['N1', 'N1b'] },
        { id: 'R1', type: 'resistor', value: 10.0, nodes: ['N1b', 'N2'] },
        { id: 'R2', type: 'resistor', value: 20.0, nodes: ['N2', 'N0'] }
      ]
    }
  };

  const model = CircuitCompiler.compile(scene);
  const solver = new CircuitSolver(model);
  const state = solver.solveDC();

  assert(state.success, 'Solver should succeed');
  approx(state.nodeVoltages['N1'], 12.0, 1e-12, 'Battery terminal N1 at 12V');
  approx(state.nodeVoltages['N1b'], 0.0, 1e-12, 'Open circuit node N1b at 0V');
  approx(state.nodeVoltages['N2'], 0.0, 1e-12, 'Downstream node N2 at 0V');
  approx(state.componentCurrents['R1'], 0.0, 1e-12, 'No current through R1');
  approx(state.componentCurrents['R2'], 0.0, 1e-12, 'No current through R2');
  approx(state.primaryCurrent, 0.0, 1e-12, 'Primary current is 0A');
});

// -----------------------------------------------------------------------------
// 3. Parallel DC Circuit
// -----------------------------------------------------------------------------
test('Parallel Circuit: 12V Battery across 6Ω (R1) || 3Ω (R2)', () => {
  const scene = {
    circuit: {
      reference_node: 'N0',
      nodes: ['N0', 'N1'],
      components: [
        { id: 'V1', type: 'voltage_source', value: 12.0, nodes: ['N1', 'N0'] },
        { id: 'R1', type: 'resistor', value: 6.0, nodes: ['N1', 'N0'] },
        { id: 'R2', type: 'resistor', value: 3.0, nodes: ['N1', 'N0'] }
      ]
    }
  };

  const model = CircuitCompiler.compile(scene);
  const solver = new CircuitSolver(model);
  const state = solver.solveDC();

  assert(state.success, 'Solver should succeed');
  approx(state.componentCurrents['R1'], 2.0, 1e-12, 'I_R1 = 12/6 = 2A');
  approx(state.componentCurrents['R2'], 4.0, 1e-12, 'I_R2 = 12/3 = 4A');
  approx(state.primaryCurrent, 6.0, 1e-12, 'I_total = 2 + 4 = 6A');
  approx(state.equivalentResistance, 2.0, 1e-12, 'R_eq = (6*3)/(6+3) = 2Ω');
  approx(state.totalPower, 72.0, 1e-12, 'P_tot = 12 * 6 = 72W');
});

// -----------------------------------------------------------------------------
// 4. Ideal Ammeter in Series Branch
// -----------------------------------------------------------------------------
test('Ideal Ammeter: 0V voltage drop, measures exact branch current', () => {
  const scene = {
    circuit: {
      reference_node: 'N0',
      nodes: ['N0', 'N1', 'N_am', 'N2'],
      components: [
        { id: 'V1', type: 'voltage_source', value: 10.0, nodes: ['N1', 'N0'] },
        { id: 'R1', type: 'resistor', value: 50.0, nodes: ['N1', 'N_am'] },
        { id: 'A1', type: 'ammeter', nodes: ['N_am', 'N2'] },
        { id: 'R2', type: 'resistor', value: 50.0, nodes: ['N2', 'N0'] }
      ]
    }
  };

  const model = CircuitCompiler.compile(scene);
  const solver = new CircuitSolver(model);
  const state = solver.solveDC();

  assert(state.success, 'Solver should succeed');
  approx(state.componentVoltages['A1'], 0.0, 1e-12, 'Ammeter voltage drop is 0V');
  approx(state.componentCurrents['A1'], 0.1, 1e-12, 'Ammeter reads 10V / 100Ω = 0.1A');
  approx(state.nodeVoltages['N_am'], 5.0, 1e-12, 'N_am voltage');
  approx(state.nodeVoltages['N2'], 5.0, 1e-12, 'N2 voltage matches N_am');
});

// -----------------------------------------------------------------------------
// 5. Balanced Wheatstone Bridge
// -----------------------------------------------------------------------------
test('Wheatstone Bridge (Balanced): Galvanometer current must be 0A', () => {
  const scene = {
    circuit: {
      reference_node: 'B',
      nodes: ['B', 'A', 'C', 'D'],
      components: [
        { id: 'V1', type: 'voltage_source', value: 10.0, nodes: ['A', 'B'] },
        { id: 'R1', type: 'resistor', value: 100.0, nodes: ['A', 'C'] },
        { id: 'R2', type: 'resistor', value: 100.0, nodes: ['A', 'D'] },
        { id: 'R3', type: 'resistor', value: 100.0, nodes: ['C', 'B'] },
        { id: 'R4', type: 'resistor', value: 100.0, nodes: ['D', 'B'] },
        { id: 'R5', type: 'resistor', value: 50.0, nodes: ['C', 'D'] } // Bridge
      ]
    }
  };

  const model = CircuitCompiler.compile(scene);
  const solver = new CircuitSolver(model);
  const state = solver.solveDC();

  assert(state.success, 'Solver should succeed');
  approx(state.nodeVoltages['C'], 5.0, 1e-12, 'Node C at 5.0V');
  approx(state.nodeVoltages['D'], 5.0, 1e-12, 'Node D at 5.0V');
  approx(state.componentVoltages['R5'], 0.0, 1e-12, 'Bridge voltage drop = 0V');
  approx(state.componentCurrents['R5'], 0.0, 1e-12, 'Galvanometer current = 0A');
  approx(state.equivalentResistance, 100.0, 1e-12, 'Bridge total equivalent resistance = 100Ω');
});

// -----------------------------------------------------------------------------
// 6. Dynamic Parameter Modification & Recalculation
// -----------------------------------------------------------------------------
test('Interactive Adjustment: R2 changed from 20Ω to 50Ω recalculates instantly', () => {
  const scene = {
    circuit: {
      reference_node: 'N0',
      nodes: ['N0', 'N1', 'N2'],
      components: [
        { id: 'V1', type: 'voltage_source', value: 12.0, nodes: ['N1', 'N0'] },
        { id: 'R1', type: 'resistor', value: 10.0, nodes: ['N1', 'N2'] },
        { id: 'R2', type: 'resistor', value: 20.0, nodes: ['N2', 'N0'] }
      ]
    }
  };

  const model = CircuitCompiler.compile(scene);
  const solver = new CircuitSolver(model);

  // Before edit
  const s1 = solver.solveDC();
  approx(s1.primaryCurrent, 0.4, 1e-12, 'Initial current = 0.4A');

  // Student modifies R2: 20 -> 50 Ω
  model.setParameter('R2', 'value', 50.0);
  const s2 = solver.solveDC();

  // R_eq = 10 + 50 = 60 Ω => I = 12 / 60 = 0.2A
  approx(s2.primaryCurrent, 0.2, 1e-12, 'Updated current = 0.2A');
  approx(s2.componentVoltages['R1'], 2.0, 1e-12, 'Updated V_R1 = 2V');
  approx(s2.componentVoltages['R2'], 10.0, 1e-12, 'Updated V_R2 = 10V');
  approx(s2.equivalentResistance, 60.0, 1e-12, 'Updated R_eq = 60Ω');
});

console.log(`\nResults: ${passed} / ${total} passed\n`);
if (passed !== total) process.exit(1);

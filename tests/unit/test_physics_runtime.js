/**
 * tests/unit/test_physics_runtime.js
 * 
 * Automated unit test suite verifying the Common Interactive Content Runtime v1:
 * 1. Canonical PhysicsScene v1 contract and parameter provenance
 * 2. SolverRegistry domain mapping and adapter resolution
 * 3. PhysicsRuntime lifecycle (load, play, pause, reset, destroy)
 * 4. MechanicsAdapter wrapping PendulumSimulation (parameter updates, RK4 state)
 * 5. OpticsAdapter wrapping ThinLensEngine (parameter updates, analytical ray trace)
 * 6. CircuitAdapter wrapping CircuitSolver (parameter updates, MNA solve)
 * 7. Parameter mutation with provenance tracking ('student' source preservation)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

import { PhysicsRuntime } from '../../engine/core/PhysicsRuntime.js';
import { SolverRegistry, defaultRegistry } from '../../engine/core/SolverRegistry.js';
import { MechanicsAdapter } from '../../engine/mechanics/MechanicsAdapter.js';
import { OpticsAdapter } from '../../engine/optics/OpticsAdapter.js';
import { CircuitAdapter } from '../../engine/circuits/CircuitAdapter.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    console.log(`  ✓ PASS: ${message}`);
  } else {
    failed++;
    console.error(`  ✗ FAIL: ${message}`);
  }
}

function assertClose(actual, expected, tol = 0.05, message = '') {
  const diff = Math.abs(actual - expected);
  assert(diff <= tol, `${message} (expected ~${expected}, got ${actual})`);
}

console.log('====================================================');
console.log('  TESTING COMMON INTERACTIVE CONTENT RUNTIME v1');
console.log('====================================================\n');

// Helper to load canonical test scene JSONs from filesystem
function loadTestScene(filename) {
  const filePath = path.resolve(__dirname, '../../apps/web/public/scenes/canonical', filename);
  const raw = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(raw);
}

// -----------------------------------------------------------------
// 1. SOLVER REGISTRY TESTS
// -----------------------------------------------------------------
console.log('[1/4] Testing SolverRegistry registration and resolution:');
{
  const registry = new SolverRegistry();
  registry.register(MechanicsAdapter);
  registry.register(OpticsAdapter);
  registry.register(CircuitAdapter);

  const adapters = registry.getRegisteredAdapters();
  assert(adapters.length === 3, 'Registry contains 3 domain adapters');

  const mechAdapter = registry.resolve({ domain: 'mechanics' });
  assert(mechAdapter instanceof MechanicsAdapter, 'Resolves MechanicsAdapter for domain "mechanics"');

  const optAdapter = registry.resolve({ domain: 'optics' });
  assert(optAdapter instanceof OpticsAdapter, 'Resolves OpticsAdapter for domain "optics"');

  const circAdapter = registry.resolve({ domain: 'circuits' });
  assert(circAdapter instanceof CircuitAdapter, 'Resolves CircuitAdapter for domain "circuits"');

  let throwsOnUnknown = false;
  try {
    registry.resolve({ domain: 'quantum_relativity' });
  } catch (_) {
    throwsOnUnknown = true;
  }
  assert(throwsOnUnknown, 'Throws error for unregistered or unknown physics domain');
}

// -----------------------------------------------------------------
// 2. TEST 1: MECHANICS (PENDULUM) RUNTIME
// -----------------------------------------------------------------
console.log('\n[2/4] Testing MechanicsAdapter (Nonlinear Pendulum):');
{
  const scene = loadTestScene('pendulum_figure.json');
  assert(scene.schemaVersion === '1.0', 'Schema version is 1.0');
  assert(scene.domain === 'mechanics', 'Scene domain is mechanics');
  assert(scene.parameters.length.provenance === 'observed', 'Length has observed provenance');
  assert(scene.parameters.gravity.provenance === 'assumed', 'Gravity has assumed provenance');

  const runtime = new PhysicsRuntime();
  await runtime.load(scene);

  const state1 = runtime.getState();
  assert(state1.domain === 'mechanics', 'Runtime state reports domain mechanics');
  assert(state1.type === 'pendulum', 'Runtime state reports type pendulum');
  assertClose(state1.length, 1.2, 0.01, 'Initial length is 1.2 m');
  assertClose(state1.thetaDeg, -27.4, 0.5, 'Initial angle is -27.4°');
  assert(state1.running === false, 'Initially paused');


  // Play, Pause, Reset
  runtime.play();
  assert(runtime.getState().running === true, 'Runtime starts playback on play()');

  runtime.pause();
  assert(runtime.getState().running === false, 'Runtime pauses on pause()');

  runtime.reset();
  assert(runtime.getState().running === false, 'Runtime resets state on reset()');

  // Parameter modification with provenance preservation
  runtime.setParameter('length', 2.0);
  const state2 = runtime.getState();
  assertClose(state2.length, 2.0, 0.01, 'Updated length to 2.0 m');

  const paramSpec = runtime.getParameter('length');
  assert(paramSpec.value === 2.0, 'Parameter value in spec updated to 2.0');
  assert(paramSpec.provenance === 'student', 'Modified parameter has student provenance');

  runtime.destroy();
  assert(runtime.adapter === null, 'Runtime cleans up adapter on destroy()');
}

// -----------------------------------------------------------------
// 3. TEST 2: OPTICS (CONVEX LENS) RUNTIME
// -----------------------------------------------------------------
console.log('\n[3/4] Testing OpticsAdapter (Thin Convex Lens):');
{
  const scene = loadTestScene('lens_figure.json');
  assert(scene.domain === 'optics', 'Scene domain is optics');
  assert(scene.parameters.focalLength.value === 130.0, 'Focal length is 130.0 px');
  assert(scene.parameters.objectDistance.value === 260.0, 'Object distance is 260.0 px');

  const runtime = new PhysicsRuntime();
  await runtime.load(scene);

  // For f = 130, u = 260 (which is 2f):
  // v = (f * u) / (u - f) = (130 * 260) / 130 = 260
  // magnification = -(v / u) = -(260 / 260) = -1.0
  const state1 = runtime.getState();
  assert(state1.domain === 'optics', 'Runtime state reports domain optics');
  assert(state1.type === 'thin_lens', 'Runtime state reports type thin_lens');
  assertClose(state1.focalLength, 130, 0.1, 'Focal length is 130');
  assertClose(state1.u, 260, 0.1, 'Object distance u = 260');
  assertClose(state1.v, 260, 0.1, 'Image distance v = 260 (at 2f)');
  assertClose(state1.magnification, -1.0, 0.05, 'Magnification m = -1.0 (same size)');
  assert(state1.isReal === true, 'Image is real');
  assert(state1.isInverted === true, 'Image is inverted');

  // Change focal length to 100:
  // v = (100 * 260) / (260 - 100) = 26000 / 160 = 162.5
  // m = -(162.5 / 260) = -0.625
  runtime.setParameter('focalLength', 100);
  const state2 = runtime.getState();
  assertClose(state2.focalLength, 100, 0.1, 'Updated focal length to 100');
  assertClose(state2.v, 162.5, 0.5, 'Recalculated image distance v = 162.5 px');
  assertClose(state2.magnification, -0.625, 0.05, 'Recalculated magnification m = -0.625');
  assert(state2.imageType === 'real_diminished', 'Image type is real_diminished');

  const fParam = runtime.getParameter('focalLength');
  assert(fParam.provenance === 'student', 'Focal length provenance updated to student');

  runtime.destroy();
}

// -----------------------------------------------------------------
// 4. TEST 3: CIRCUITS (DC RESISTOR NETWORK) RUNTIME
// -----------------------------------------------------------------
console.log('\n[4/4] Testing CircuitAdapter (DC Series Loop with MNA):');
{
  const scene = loadTestScene('circuit_figure.json');
  assert(scene.domain === 'circuits', 'Scene domain is circuits');
  assert(scene.parameters.V1.value === 12.0, 'V1 is 12 V');
  assert(scene.parameters.R1.value === 10.0, 'R1 is 10 Ω');
  assert(scene.parameters.R2.value === 20.0, 'R2 is 20 Ω');

  const runtime = new PhysicsRuntime();
  await runtime.load(scene);

  // V1 = 12 V, S1 closed, R1 = 10 ohm, R2 = 20 ohm -> R_total = 30 ohm
  // I = 12 / 30 = 0.4 A = 400 mA
  // V(N1) = V(N1b) = 12 V, V(N2) = 8 V, V(N0) = 0 V
  // P_total = 12 * 0.4 = 4.8 W
  const state1 = runtime.getState();
  assert(state1.domain === 'circuits', 'Runtime state reports domain circuits');
  assertClose(state1.nodeVoltages.N1, 12.0, 0.1, 'Node N1 voltage is 12.0 V');
  assertClose(state1.nodeVoltages.N1b, 12.0, 0.1, 'Node N1b voltage is 12.0 V');
  assertClose(state1.nodeVoltages.N2, 8.0, 0.1, 'Node N2 voltage is 8.0 V');
  assertClose(state1.nodeVoltages.N0, 0.0, 0.01, 'Node N0 (ground) is 0.0 V');
  assertClose(state1.branchCurrents['R1.branch'], 400.0, 1.0, 'Branch current through R1 is 400 mA');
  assertClose(state1.totalPower, 4.8, 0.2, 'Total DC power is 4.8 W');

  // Change R1 from 10 Ω to 20 Ω:
  // R_total = 20 + 20 = 40 Ω
  // I = 12 / 40 = 0.3 A = 300 mA
  // V(N2) = 0.3 * 20 = 6.0 V
  // P_total = 12 * 0.3 = 3.6 W
  runtime.setParameter('R1', 20.0);
  const state2 = runtime.getState();
  assertClose(state2.nodeVoltages.N2, 6.0, 0.1, 'Updated node N2 voltage is 6.0 V');
  assertClose(state2.branchCurrents['R1.branch'], 300.0, 1.0, 'Updated branch current is 300 mA');
  assertClose(state2.totalPower, 3.6, 0.2, 'Updated total power is 3.6 W');

  const r1Param = runtime.getParameter('R1');
  assert(r1Param.provenance === 'student', 'R1 provenance updated to student');

  runtime.destroy();
}

console.log('\n====================================================');
console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
console.log('====================================================');

if (failed > 0) {
  process.exit(1);
} else {
  process.exit(0);
}

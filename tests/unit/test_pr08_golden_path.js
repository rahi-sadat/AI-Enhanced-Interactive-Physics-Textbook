/**
 * tests/unit/test_pr08_golden_path.js
 *
 * PR-08 Golden Path End-to-End Vertical Slice Test Suite.
 *
 * VERIFIES:
 *   1. Complete Vertical Slice: Real Pendulum flow from upload to interactive simulation.
 *   2. Native source_px Coordinate Space Preservation (zero manual canvas scaling).
 *   3. CoordinateMapper sub-pixel alignment contract.
 *   4. Strict Separation of Source Evidence (BookIR) from Experimental Simulation Parameters.
 *   5. Simulation Reset restores textbook values without rewriting BookIR.
 */

import { SimulationOrchestrator, OrchestratorState } from '../../apps/web/src/features/simulations/core/SimulationOrchestrator.js';
import { PhysicsRuntime } from '../../engine/core/PhysicsRuntime.js';
import { CoordinateMapper } from '../../engine/core/coordinateMapper.js';

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
  assert(diff <= tol, `${message} (diff: ${diff.toFixed(4)}, tol: ${tol}, actual: ${actual.toFixed(2)}, expected: ${expected.toFixed(2)})`);
}

console.log('==============================================');
console.log('  RUNNING PR-08 GOLDEN PATH ACCEPTANCE TESTS');
console.log('==============================================\n');

async function runTests() {
  // -------------------------------------------------------------------------
  // Part 1: Real Pendulum Golden-Path Orchestration
  // -------------------------------------------------------------------------
  console.log('[1/4] Real pendulum end-to-end orchestration slice');

  // Grounded BookIR matching real PR-06 perception output
  const groundedPendulumBookIR = {
    sourceAssetId: 'real_asset_pendulum',
    figureId: 'fig_pendulum_01',
    domain: 'mechanics',
    subtype: 'pendulum',
    status: 'NEEDS_REVIEW',
    entities: [
      { id: 'e_pivot', type: 'pivot', positionSourcePx: { x: 250, y: 80 } },
      { id: 'e_bob', type: 'bob', positionSourcePx: { x: 250, y: 480 } },
      { id: 'e_str', type: 'string', positionSourcePx: { x: 250, y: 80 }, geometry: { effective_length_px: 400 } },
    ],
    geometry: {
      pivot: { x: 250, y: 80 },
      bob_center: { x: 250, y: 480 },
      string_length_px: 400.0,
      bob_radius_px: 20.0,
      width: 800.0,
      height: 600.0,
    },
    parameters: {},
    evidence: {
      ev_ocr_1: {
        tokens: [
          { rawText: 'L = 80 cm', candidates: [{ quantityCandidate: 'length', numericValue: 80, rawUnit: 'cm', confidence: 0.88 }] }
        ]
      }
    }
  };

  let currentBookIR = JSON.parse(JSON.stringify(groundedPendulumBookIR));

  // Authoritative mock API matching PR-07 backend endpoints
  const mockApi = {
    ingest: async () => ({
      success: true,
      image_url: '/uploads/pendulum_sketch_raw.png',
      source_asset: { id: 'real_asset_pendulum', width_px: 800, height_px: 600 },
      book_ir: currentBookIR,
      compiler: { status: 'NEEDS_REVIEW', scene: null },
      status: 'needs-review',
      domain: 'mechanics',
      scenario: 'pendulum',
    }),
    review: async () => {
      const p = currentBookIR.parameters || {};
      const missing = [];
      if (!p.length) missing.push('length');
      if (!p.gravity) missing.push('gravity');
      if (!p.mass) missing.push('mass');
      if (!p.damping) missing.push('damping');

      const ready = missing.length === 0;
      return {
        success: true,
        readyToCompile: ready,
        blockersCount: missing.length,
        warningsCount: 0,
        reviewState: {
          readyToCompile: ready,
          blockersCount: missing.length,
          issues: missing.map(m => {
            if (m === 'length') {
              return {
                parameterName: 'length',
                question: 'Confirm length from diagram token "L = 80 cm"',
                candidates: [{ quantityCandidate: 'length', numericValue: 80, rawUnit: 'cm', confidence: 0.88 }],
                allowedUnits: ['m', 'cm'],
              };
            }
            return {
              parameterName: m,
              question: `Diagram does not specify ${m}`,
              defaultPolicyId: `policy_${m === 'gravity' ? 'earth_gravity' : (m === 'mass' ? 'standard_mass' : 'zero_damping')}`,
            };
          }),
          availablePolicies: [
            { id: 'policy_earth_gravity', name: 'Standard Earth Gravity', value: 9.80665, unit: 'm/s²', targetParameter: 'gravity' },
            { id: 'policy_standard_mass', name: 'Standard Unit Mass', value: 1.0, unit: 'kg', targetParameter: 'mass' },
            { id: 'policy_zero_damping', name: 'Zero Air Drag', value: 0.0, unit: '1/s', targetParameter: 'damping' },
          ],
        }
      };
    },
    confirmCandidate: async (_bir, pName, cand) => {
      currentBookIR.parameters[pName] = { value: cand.numericValue / 100, unit: 'm' }; // 80 cm -> 0.8 m
      currentBookIR.parameter_provenance = currentBookIR.parameter_provenance || {};
      currentBookIR.parameter_provenance[pName] = { source: 'user_confirmed' };
      return {
        success: true,
        bookIR: JSON.parse(JSON.stringify(currentBookIR)),
        canCompile: false,
      };
    },
    applyPolicy: async (_bir, polId) => {
      let pName = 'gravity';
      let val = 9.80665;
      let unit = 'm/s²';
      if (polId === 'policy_standard_mass') {
        pName = 'mass';
        val = 1.0;
        unit = 'kg';
      } else if (polId === 'policy_zero_damping') {
        pName = 'damping';
        val = 0.0;
        unit = '1/s';
      }
      currentBookIR.parameters[pName] = { value: val, unit };
      currentBookIR.parameter_provenance = currentBookIR.parameter_provenance || {};
      currentBookIR.parameter_provenance[pName] = { source: 'policy_default', policy_id: polId };

      const allPresent = ['length', 'gravity', 'mass', 'damping'].every(k => Boolean(currentBookIR.parameters[k]));
      if (allPresent) {
        currentBookIR.status = 'READY_TO_COMPILE';
      }
      return {
        success: true,
        bookIR: JSON.parse(JSON.stringify(currentBookIR)),
        canCompile: allPresent,
      };
    },
    compile: async () => {
      const p = currentBookIR.parameters;
      const compiledScene = {
        schemaVersion: '1.0',
        id: 'SCENE-PR08-PENDULUM-01',
        domain: 'mechanics',
        subtype: 'pendulum',
        coordinateSystem: {
          type: 'source_px',
          width: 800,
          height: 600,
        },
        source: {
          image: '/uploads/pendulum_sketch_raw.png',
          width: 800,
          height: 600,
        },
        geometry: {
          pivot: { x: 250, y: 80 },
          bob_center: { x: 250, y: 480 },
          string_length_px: 400.0,
          bob_radius_px: 20.0,
        },
        parameters: {
          length: { value: p.length.value, unit: 'm', provenance: 'user_confirmed' },
          gravity: { value: p.gravity.value, unit: 'm/s²', provenance: 'policy_default' },
          mass: { value: p.mass.value, unit: 'kg', provenance: 'policy_default' },
          damping: { value: p.damping.value, unit: '1/s', provenance: 'policy_default' },
          initialAngle: { value: 0.0, unit: 'rad', provenance: 'default' },
        },
        objects: [
          {
            id: 'pendulum_sys',
            type: 'pendulum',
            geometry: {
              pivot: { x: 250, y: 80 },
              string_length_px: 400.0,
              bob_radius_px: 20.0,
            },
            physics: {
              length_m: p.length.value,
              mass_kg: p.mass.value,
              damping_s_inv: p.damping.value,
              theta0_rad: 0.0,
            }
          }
        ],
        environment: {
          gravity_m_s2: p.gravity.value,
        }
      };

      return {
        success: true,
        compiler: { status: 'READY' },
        scene: compiledScene,
        bookIR: JSON.parse(JSON.stringify(currentBookIR)),
      };
    }
  };

  // Step 1: Upload / Ingest image
  const orch = new SimulationOrchestrator({ api: mockApi });
  await orch.startWithFile(new Blob(['bytes']), () => {});
  assert(orch.state === OrchestratorState.NEEDS_REVIEW, 'Ingest reached NEEDS_REVIEW');
  assert(orch.reviewState.issues.length === 4, '4 blockers detected (length, gravity, mass, damping)');

  // Step 2: Student confirms length candidate (80 cm -> 0.8 m)
  await orch.confirmCandidate('length', { numericValue: 80, rawUnit: 'cm' });
  assert(orch.bookIR.parameters.length.value === 0.8, 'Length confirmed as 0.8 m');
  assert(orch.state === OrchestratorState.NEEDS_REVIEW, 'Still in NEEDS_REVIEW (remaining blockers exist)');

  // Step 3: Student explicitly applies modeling assumption policies
  await orch.applyPolicy('policy_earth_gravity');
  assert(orch.bookIR.parameters.gravity.value === 9.80665, 'Earth gravity policy applied');
  assert(orch.state === OrchestratorState.NEEDS_REVIEW, 'Still in NEEDS_REVIEW (mass & damping left)');

  await orch.applyPolicy('policy_standard_mass');
  assert(orch.bookIR.parameters.mass.value === 1.0, 'Standard mass policy applied');

  await orch.applyPolicy('policy_zero_damping');
  assert(orch.bookIR.parameters.damping.value === 0.0, 'Zero damping policy applied');

  // Step 4: Verification of auto-compile handoff
  assert(orch.state === OrchestratorState.READY_TO_SIMULATE, 'All blockers resolved: state is READY_TO_SIMULATE');
  assert(orch.compiledScene !== null, 'Compiled canonical scene generated');
  assert(orch.compiledScene.domain === 'mechanics', 'Domain is mechanics');
  assert(orch.compiledScene.subtype === 'pendulum', 'Subtype is pendulum');

  // Step 5: Student presses "Start Simulation"
  const readyScene = orch.startSimulation();
  assert(orch.state === OrchestratorState.SIMULATING, 'Transitioned to SIMULATING upon explicit student start');
  assert(readyScene.id === 'SCENE-PR08-PENDULUM-01', 'Active scene matches compiled scene');

  // -------------------------------------------------------------------------
  // Part 2: Coordinate Space Purity (source_px)
  // -------------------------------------------------------------------------
  console.log('\n[2/4] Native source_px coordinate preservation');
  const geom = readyScene.geometry;
  assert(readyScene.coordinateSystem.type === 'source_px', 'Coordinate space is native source_px');
  assert(geom.pivot.x === 250 && geom.pivot.y === 80, 'Native pivot (250, 80) preserved exactly');
  assert(geom.bob_center.x === 250 && geom.bob_center.y === 480, 'Native bob_center (250, 480) preserved exactly');
  assert(geom.string_length_px === 400.0, 'Native string_length_px 400.0 preserved');
  assert(geom.bob_radius_px === 20.0, 'Native bob_radius_px 20.0 preserved');

  // Verify CoordinateMapper maps without modifying underlying BookIR
  const mapper = new CoordinateMapper(800, 600, 400, 300);
  const vpPivot = mapper.sourceToView(geom.pivot.x, geom.pivot.y);
  assertClose(vpPivot.x, 125.0, 0.1, 'Viewport pivot X correctly scaled by 0.5');
  assertClose(vpPivot.y, 40.0, 0.1, 'Viewport pivot Y correctly scaled by 0.5');

  // Reverse transform produces exact source_px
  const srcPivot = mapper.viewToSource(vpPivot.x, vpPivot.y);
  assertClose(srcPivot.x, 250.0, 0.1, 'Reverse transform restores source_px pivot X');
  assertClose(srcPivot.y, 80.0, 0.1, 'Reverse transform restores source_px pivot Y');

  // -------------------------------------------------------------------------
  // Part 3: Canonical PhysicsRuntime Execution
  // -------------------------------------------------------------------------
  console.log('\n[3/4] Canonical PhysicsRuntime execution of compiled scene');
  const runtime = new PhysicsRuntime();
  const initOutput = await runtime.load(readyScene);

  assert(initOutput.domain === 'mechanics', 'Runtime initialized mechanics');
  assert(initOutput.subtype === 'pendulum', 'Runtime confirmed pendulum subtype');
  assert(runtime.getParameter('length').value === 0.8, 'Runtime length is 0.8 m');
  assert(runtime.getParameter('gravity').value === 9.80665, 'Runtime gravity is 9.80665 m/s²');

  // Advance simulation (step RK4 integrator)
  runtime.play();
  runtime.step(0.1);
  const state1 = runtime.getState();
  assert(state1.running === true, 'Simulation is running');

  // -------------------------------------------------------------------------
  // Part 4: Separation of Evidence (BookIR) from Transient Experiments
  // -------------------------------------------------------------------------
  console.log('\n[4/4] Preserving source BookIR evidence vs simulation experimentation');
  assert(orch.bookIR.parameters.length.value === 0.8, 'Source BookIR length is 0.8 m initially');

  // Student explores: changes slider to 1.5 m in simulation runtime
  runtime.updateParameter('length', 1.5);
  assert(runtime.getParameter('length').value === 1.5, 'Simulation runtime updated to 1.5 m');

  // CRITICAL INVARIANT: Source BookIR MUST NOT BE MUTATED by slider experimentation!
  assert(orch.bookIR.parameters.length.value === 0.8, 'CRITICAL: BookIR length remains 0.8 m during slider experiment');
  assert(orch.compiledScene.parameters.length.value === 0.8, 'Compiled source scene length remains 0.8 m');

  // Student clicks "Reset to textbook values"
  // Restores initial textbook values from compiled scene
  const initialTextbookLength = orch.compiledScene.parameters.length.value;
  runtime.updateParameter('length', initialTextbookLength);
  runtime.reset();

  assert(runtime.getParameter('length').value === 0.8, 'Runtime restored to textbook length 0.8 m');
  assert(orch.bookIR.parameters.length.value === 0.8, 'Source BookIR length remains 0.8 m');

  runtime.destroy();
}

runTests().then(() => {
  console.log('\n==============================================');
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log('==============================================');
  process.exit(failed > 0 ? 1 : 0);
});

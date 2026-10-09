/**
 * tests/unit/test_pr08_orchestrator.js
 *
 * Verifies SimulationOrchestrator state machine, transitions,
 * monotonic operation sequencing (race-condition protection),
 * and zero client-side parameter fabrication.
 */

import { SimulationOrchestrator, OrchestratorState } from '../../apps/web/src/features/simulations/core/SimulationOrchestrator.js';
import { CompilationGatingError } from '../../apps/web/src/features/simulations/core/SimulationApi.js';

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

console.log('==============================================');
console.log('  RUNNING PR-08 SIMULATION ORCHESTRATOR TESTS');
console.log('==============================================\n');

async function runTests() {
  // Test 1: Initial State is IDLE
  console.log('[1/8] Verifying initial orchestrator state');
  const orch = new SimulationOrchestrator();
  assert(orch.state === OrchestratorState.IDLE, 'Initial state is IDLE');
  assert(orch.bookIR === null, 'Initial bookIR is null');
  assert(orch.compiledScene === null, 'Initial compiledScene is null');

  // Test 2: Ingest flow -> NEEDS_REVIEW with review state
  console.log('\n[2/8] Ingest flow transitions to NEEDS_REVIEW when evidence is incomplete');
  const mockApiNeedsReview = {
    ingest: async () => ({
      success: true,
      image_url: '/uploads/pendulum.png',
      source_asset: { id: 'asset_1', width_px: 800, height_px: 600 },
      book_ir: {
        id: 'book_ir_1',
        domain: 'mechanics',
        subtype: 'pendulum',
        status: 'NEEDS_REVIEW',
        parameters: {},
      },
      compiler: { status: 'NEEDS_REVIEW', scene: null, issues: [] },
      status: 'needs-review',
    }),
    review: async () => ({
      success: true,
      readyToCompile: false,
      blockersCount: 3,
      warningsCount: 0,
      reviewState: {
        readyToCompile: false,
        blockersCount: 3,
        issues: [
          { parameterName: 'length', candidates: [{ numericValue: 80, rawUnit: 'cm', confidence: 0.85 }] },
          { parameterName: 'gravity', defaultPolicyId: 'policy_earth_gravity' },
          { parameterName: 'damping', defaultPolicyId: 'policy_zero_damping' },
        ],
        availablePolicies: [
          { id: 'policy_earth_gravity', name: 'Earth Gravity', value: 9.80665, unit: 'm/s²' },
          { id: 'policy_zero_damping', name: 'Zero Damping', value: 0.0, unit: '1/s' },
        ],
      },
    }),
  };

  const orch2 = new SimulationOrchestrator({ api: mockApiNeedsReview });
  const recordedStates = [];
  orch2.onStateChange((st) => recordedStates.push(st));

  await orch2.startWithFile(new Blob(['bytes']), () => {});

  assert(orch2.state === OrchestratorState.NEEDS_REVIEW, 'Final state is NEEDS_REVIEW');
  assert(recordedStates.includes(OrchestratorState.UPLOADING), 'Went through UPLOADING');
  assert(recordedStates.includes(OrchestratorState.ANALYZING), 'Went through ANALYZING');
  assert(orch2.reviewState.issues.length === 3, 'Recorded 3 review issues');
  assert(orch2.imageUrl === '/uploads/pendulum.png', 'Stored imageUrl');

  // Test 3: Resolution mutation replaces BookIR with backend authority
  console.log('\n[3/8] Resolution mutation replaces BookIR authoritatively');
  const updatedBookIR = {
    id: 'book_ir_1',
    domain: 'mechanics',
    subtype: 'pendulum',
    status: 'NEEDS_REVIEW',
    parameters: { length: { value: 0.8, unit: 'm' } },
  };

  mockApiNeedsReview.confirmCandidate = async () => ({
    success: true,
    bookIR: updatedBookIR,
    canCompile: false,
  });

  await orch2.confirmCandidate('length', { numericValue: 80, rawUnit: 'cm' });
  assert(orch2.bookIR.parameters.length.value === 0.8, 'BookIR updated with backend returned length');
  assert(orch2.getResearchMetrics().candidateConfirmations === 1, 'Metric candidateConfirmations recorded');

  // Test 4: Complete resolution -> READY_TO_COMPILE -> auto-compile -> READY_TO_SIMULATE
  console.log('\n[4/8] Resolving all blockers triggers compile -> READY_TO_SIMULATE');
  const compiledMockScene = {
    schemaVersion: '1.0',
    id: 'SCENE-PENDULUM',
    domain: 'mechanics',
    subtype: 'pendulum',
    parameters: { length: { value: 0.8, unit: 'm' }, gravity: { value: 9.80665, unit: 'm/s²' } },
  };

  mockApiNeedsReview.applyPolicy = async () => ({
    success: true,
    bookIR: {
      ...updatedBookIR,
      status: 'READY_TO_COMPILE',
      parameters: { ...updatedBookIR.parameters, gravity: { value: 9.80665 } },
    },
    canCompile: true,
  });

  mockApiNeedsReview.review = async () => ({
    success: true,
    readyToCompile: true,
    blockersCount: 0,
    reviewState: { readyToCompile: true, blockersCount: 0, issues: [] },
  });

  mockApiNeedsReview.compile = async () => ({
    success: true,
    scene: compiledMockScene,
    compiler: { status: 'READY' },
  });

  await orch2.applyPolicy('policy_earth_gravity', 'gravity');

  assert(orch2.state === OrchestratorState.READY_TO_SIMULATE, 'State transitioned to READY_TO_SIMULATE');
  assert(orch2.compiledScene !== null, 'Compiled scene is present');
  assert(orch2.compiledScene.domain === 'mechanics', 'Compiled scene domain is mechanics');
  assert(orch2.getResearchMetrics().policiesAccepted === 1, 'Metric policiesAccepted recorded');
  assert(orch2.getResearchMetrics().timeToReadyMs !== null, 'timeToReadyMs recorded');

  // Test 5: Compilation and simulation activation are decoupled
  console.log('\n[5/8] Decoupled simulation start: user action moves to SIMULATING');
  assert(orch2.state === OrchestratorState.READY_TO_SIMULATE, 'Remains READY_TO_SIMULATE before student click');
  const activeScene = orch2.startSimulation();
  assert(orch2.state === OrchestratorState.SIMULATING, 'Transitions to SIMULATING upon startSimulation()');
  assert(activeScene.id === 'SCENE-PENDULUM', 'startSimulation() returned compiled scene');

  // Test 6: Removing a resolution reverts state to NEEDS_REVIEW and invalidates scene
  console.log('\n[6/8] Reversibility: removeResolution invalidates compiled scene');
  mockApiNeedsReview.removeResolution = async () => ({
    success: true,
    bookIR: {
      ...updatedBookIR,
      status: 'NEEDS_REVIEW',
      parameters: {},
    },
    canCompile: false,
    parameterName: 'gravity',
  });
  mockApiNeedsReview.review = async () => ({
    success: true,
    readyToCompile: false,
    blockersCount: 1,
    reviewState: { readyToCompile: false, blockersCount: 1, issues: [{ parameterName: 'gravity' }] },
  });

  await orch2.removeResolution('gravity');
  assert(orch2.state === OrchestratorState.NEEDS_REVIEW, 'State reverted to NEEDS_REVIEW');
  assert(orch2.compiledScene === null, 'Compiled scene was invalidated');

  // Test 7: Unsupported diagram cleanly reaches UNSUPPORTED with friendly message
  console.log('\n[7/8] Unsupported diagram reaches UNSUPPORTED without fallback');
  const mockApiUnsupported = {
    ingest: async () => ({
      success: true,
      status: 'unsupported',
      book_ir: { status: 'UNSUPPORTED' },
    }),
  };
  const orchUnsupported = new SimulationOrchestrator({ api: mockApiUnsupported });
  await orchUnsupported.startWithFile(new Blob(['bytes']), () => {});
  assert(orchUnsupported.state === OrchestratorState.UNSUPPORTED, 'Transitions to UNSUPPORTED');
  assert(orchUnsupported.currentError.includes('not supported yet'), 'Friendly unsupported message');
  assert(orchUnsupported.compiledScene === null, 'No fake scene created for unsupported diagram');

  // Test 8: Monotonic operation ID protects against async race conditions
  console.log('\n[8/8] Stale async race condition protection');
  let slowResolveFinished = false;
  const mockApiRacing = {
    review: async () => new Promise((resolve) => {
      setTimeout(() => {
        slowResolveFinished = true;
        resolve({
          success: true,
          readyToCompile: false,
          reviewState: { issues: [{ parameterName: 'STALE_SLUG' }] },
        });
      }, 50);
    }),
  };

  const orchRacing = new SimulationOrchestrator({ api: mockApiRacing });
  // Start slow review
  orchRacing.startWithBookIR({ status: 'NEEDS_REVIEW' });
  // Immediately reset / cancel before slow review completes
  orchRacing.reset();
  assert(orchRacing.state === OrchestratorState.IDLE, 'Orchestrator was reset to IDLE');

  // Wait for the slow promise to finish
  await new Promise((r) => setTimeout(r, 80));
  assert(slowResolveFinished === true, 'Slow promise did complete');
  assert(orchRacing.state === OrchestratorState.IDLE, 'State remained IDLE (stale response was ignored)');
  assert(orchRacing.reviewState === null, 'Stale reviewState was NOT written');
}

runTests().then(() => {
  console.log('\n==============================================');
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log('==============================================');
  if (failed > 0) process.exit(1);
});

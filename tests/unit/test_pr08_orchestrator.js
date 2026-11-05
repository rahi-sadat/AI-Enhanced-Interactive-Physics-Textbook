/**
 * tests/unit/test_pr08_orchestrator.js
 *
 * Verifies SimulationOrchestrator state machine, transitions,
 * monotonic operation sequencing (race-condition protection),
 * and zero client-side parameter fabrication.
 */

import { SimulationOrchestrator, OrchestratorState } from '../../apps/web/src/features/simulations/core/SimulationOrchestrator.js';
import { CompilationGatingError, SimulationApi } from '../../apps/web/src/features/simulations/core/SimulationApi.js';

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
  const originalPost = SimulationApi._postJson;
  const preparedBook = { status: 'READY_TO_COMPILE', parameters: { gravity: 9.80665 } };
  try {
    SimulationApi._postJson = async () => ({ success: true, book_ir: preparedBook,
      ready_to_compile: true, review_state: { issues: [] } });
    const response = await SimulationApi.review({ status: 'NEEDS_REVIEW', parameters: {} });
    assert(response.bookIR === preparedBook, 'Review API preserves backend-resolved BookIR for compilation');
  } finally {
    SimulationApi._postJson = originalPost;
  }
  console.log('[defaults] Backend policies fill missing values without altering diagram evidence');
  const appliedDefaults = [];
  const policyIssues = [
    { parameterName: 'gravity', defaultPolicyId: 'gravity-policy' },
    { parameterName: 'component.R1.value', defaultPolicyId: 'resistor-policy' },
    { parameterName: 'component.R2.value', defaultPolicyId: 'resistor-policy' },
    { parameterName: 'length', defaultPolicyId: 'length-policy', candidates: [{ numericValue: 0.8 }] },
    { parameterName: 'launch_position', issueType: 'ungrounded_geometry' },
  ];
  const availablePolicies = [
    { id: 'gravity-policy' }, { id: 'resistor-policy' }, { id: 'length-policy' },
  ];
  const defaultsApi = {
    applyPolicy: async (book, policyId, parameter) => {
      appliedDefaults.push([policyId, parameter]);
      const updated = structuredClone(book);
      if (parameter.startsWith('component.')) {
        const id = parameter.split('.')[1];
        updated.parameters.components.find((c) => c.id === id).value = 100;
      } else updated.parameters[parameter] = 9.80665;
      updated.resolutions[parameter] = { policyId, resolvedValue: parameter === 'gravity' ? 9.80665 : 100,
        canonicalUnit: parameter === 'gravity' ? 'm/s²' : 'Ω', notes: 'Disclosed example value' };
      return { bookIR: updated, canCompile: false };
    },
    review: async (book) => ({ readyToCompile: false, reviewState: {
      issues: policyIssues.filter((item) => !book.resolutions[item.parameterName]), availablePolicies,
    } }),
  };
  const defaultsOrch = new SimulationOrchestrator({ api: defaultsApi });
  defaultsOrch.state = OrchestratorState.NEEDS_REVIEW;
  defaultsOrch.bookIR = { status: 'NEEDS_REVIEW', parameters: { gravity: null, components: [
    { id: 'R1', value: null }, { id: 'R2', value: 220 },
  ] }, resolutions: {}, geometry: { launch_position: null } };
  defaultsOrch.reviewState = { issues: policyIssues, availablePolicies };
  await defaultsOrch.useStandardDefaults();
  assert(appliedDefaults.length === 2, 'Only missing gravity and the individual missing resistor receive defaults');
  assert(defaultsOrch.bookIR.parameters.components[1].value === 220, 'Existing resistance is preserved');
  assert(defaultsOrch.bookIR.parameters.length === undefined, 'OCR candidate is not overwritten by a default');
  assert(defaultsOrch.bookIR.geometry.launch_position === null, 'Missing geometry is not invented');
  assert(defaultsOrch.state === OrchestratorState.NEEDS_REVIEW, 'Structural blockers still require review');
  await defaultsOrch.useStandardDefaults();
  assert(appliedDefaults.length === 2, 'Repeated default application is idempotent');
  const normalized = defaultsOrch._normalizeSceneBackground({});
  assert(normalized.assumptions.length === 2, 'Applied defaults are disclosed in runtime assumptions');

  const readyOrch = new SimulationOrchestrator({ api: {
    ...defaultsApi,
    review: async (book) => ({ bookIR: { ...book, status: 'READY_TO_COMPILE' },
      readyToCompile: true, reviewState: { issues: [], availablePolicies: [] } }),
    compile: async (book) => ({ success: true, bookIR: book, scene: { domain: 'mechanics' } }),
  } });
  readyOrch.state = OrchestratorState.NEEDS_REVIEW;
  readyOrch.bookIR = { parameters: {}, resolutions: {} };
  readyOrch.reviewState = { issues: [policyIssues[0]], availablePolicies };
  await readyOrch.useStandardDefaults();
  assert(readyOrch.state === OrchestratorState.READY_TO_SIMULATE, 'Final default advances to a compiled scene when backend confirms readiness');
  assert(readyOrch.compiledScene.assumptions[0].parameter === 'gravity', 'Compiled scene retains the default disclosure');

  let refusedAttempts = 0;
  const refusedOrch = new SimulationOrchestrator({ api: {
    applyPolicy: async () => { refusedAttempts++; throw new Error('Policy refused'); },
  } });
  refusedOrch.state = OrchestratorState.NEEDS_REVIEW;
  refusedOrch.bookIR = { parameters: {} };
  refusedOrch.reviewState = { issues: [policyIssues[0]], availablePolicies };
  await refusedOrch.useStandardDefaults();
  assert(refusedAttempts === 1, 'Refused default is not retried in an endless loop');
  assert(refusedOrch.compiledScene === null, 'Refused default does not generate a scene');

  const blockedCompilation = new SimulationOrchestrator({ api: {
    compile: async () => { throw new CompilationGatingError('BookIR is not ready to compile.', [
      'Battery voltage is missing.', { message: 'Resistor resistance is missing.' },
    ]); },
  } });
  blockedCompilation.bookIR = { status: 'NEEDS_REVIEW' };
  await blockedCompilation.compile();
  assert(blockedCompilation.currentError.includes('Battery voltage is missing.'), 'Compilation reports the specific missing voltage');
  assert(blockedCompilation.currentError.includes('Resistor resistance is missing.'), 'Compilation reports structured blockers as readable messages');

  // A provider outage is retryable infrastructure failure, not a bad diagram.
  const providerOutage = new SimulationOrchestrator({ api: {
    ingest: async () => ({ status: 'unresolved', book_ir: {
      status: 'UNRESOLVED', domain: null, subtype: null,
      provenance: { error_type: 'VisionProviderError', error: '503 UNAVAILABLE' },
    } }),
  } });
  providerOutage.reviewState = { issues: [{ parameterName: 'previous_figure' }] };
  await providerOutage.startWithFile({ name: 'neutral.jpg' });
  assert(providerOutage.state === OrchestratorState.ERROR, 'Provider outage does not produce a simulation');
  assert(providerOutage.currentError.includes('temporarily unavailable'), 'Provider outage is explained honestly');
  assert(providerOutage.currentError.includes('retry'), 'Retry is offered with the current image');
  assert(providerOutage.reviewState === null, 'Previous figure review is cleared on a new upload');
  assert(providerOutage.compiledScene === null, 'No canned scene replaces a failed provider');

  let circuitReviewCalls = 0;
  let circuitIssues = [{ code: 'SHORTED_CIRCUIT_SOURCE' }];
  const circuitUpload = new SimulationOrchestrator({ api: {
    ingest: async () => ({ status: 'needs-review', book_ir: {
      domain: 'circuits', subtype: 'dc_linear', status: 'NEEDS_REVIEW', reviewIssues: circuitIssues,
    } }),
    review: async () => { circuitReviewCalls++; },
  } });
  await circuitUpload.startWithFile(new Blob(['bytes']));
  assert(circuitUpload.state === OrchestratorState.ERROR, 'A shorted circuit stops in the upload dialog');
  assert(circuitUpload.currentError.includes('Short circuit detected'), 'The detected short is explained');
  circuitIssues = [{ code: 'SHORTED_CIRCUIT_SOURCE' }, { code: 'GROUNDING_INCOMPLETE' }];
  await circuitUpload.startWithFile(new Blob(['bytes']));
  assert(circuitUpload.currentError.includes('Try a clear crop'), 'An ungrounded circuit offers a retry');
  assert(!circuitUpload.currentError.includes('Short circuit detected'), 'Incomplete grounding cannot establish a short circuit');
  assert(circuitReviewCalls === 0 && circuitUpload.reviewState === null, 'Circuit uploads skip evidence review');

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

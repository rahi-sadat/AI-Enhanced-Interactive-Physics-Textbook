/**
 * tests/unit/test_pr08_no_fabrication.js
 *
 * Anti-Fabrication & Strict Gating Frontend Test Suite.
 *
 * Verifies that the frontend:
 *   1. NEVER invents missing physical parameters (e.g. no silent 9.81 fallback).
 *   2. Rejects simulation launch when BookIR is in NEEDS_REVIEW.
 *   3. Refuses to fall back to canned demo scenes on compilation failure.
 *   4. Does not route unsupported subtypes to nearest available renderer.
 *   5. Keeps backend as the sole authoritative evaluator of compilation readiness.
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
console.log('  RUNNING PR-08 NO-FABRICATION FRONTEND TESTS');
console.log('==============================================\n');

async function runTests() {
  // Test 1: Incomplete BookIR missing gravity produces ZERO simulation scene
  console.log('[1/5] Incomplete BookIR missing gravity never fabricates default');
  const mockApiIncomplete = {
    ingest: async () => ({
      success: true,
      image_url: '/uploads/pendulum_missing_g.png',
      book_ir: {
        domain: 'mechanics',
        subtype: 'pendulum',
        status: 'NEEDS_REVIEW',
        parameters: {
          length: { value: 0.8, unit: 'm' },
          // gravity is strictly MISSING
        },
      },
      compiler: { status: 'NEEDS_REVIEW', scene: null, issues: [{ code: 'MISSING_GRAVITY' }] },
      status: 'needs-review',
    }),
    review: async () => ({
      success: true,
      readyToCompile: false,
      blockersCount: 1,
      reviewState: {
        readyToCompile: false,
        blockersCount: 1,
        issues: [{ parameterName: 'gravity', question: 'Missing gravity parameter' }],
        availablePolicies: [{ id: 'policy_earth_gravity', value: 9.80665 }],
      },
    }),
  };

  const orch1 = new SimulationOrchestrator({ api: mockApiIncomplete });
  await orch1.startWithFile(new Blob(['bytes']), () => {});

  assert(orch1.state === OrchestratorState.NEEDS_REVIEW, 'State is NEEDS_REVIEW, not READY_TO_SIMULATE');
  assert(orch1.compiledScene === null, 'CRITICAL: compiledScene is strictly null');
  assert(orch1.bookIR.parameters.gravity === undefined, 'CRITICAL: gravity is NOT fabricated in BookIR');

  let attemptedStartFailed = false;
  try {
    orch1.startSimulation();
  } catch (err) {
    attemptedStartFailed = true;
  }
  assert(attemptedStartFailed === true, 'startSimulation() threw error when unready (cannot launch)');

  // Test 2: Compilation gating refusal produces NO fallback scene
  console.log('\n[2/5] Compilation gating failure never falls back to demo scene');
  const mockApiRefusal = {
    compile: async () => {
      throw new CompilationGatingError('BookIR is not ready to compile.', ['gravity is missing'], 'NEEDS_REVIEW');
    },
  };
  const orch2 = new SimulationOrchestrator({ api: mockApiRefusal });
  orch2.bookIR = { status: 'NEEDS_REVIEW' };

  await orch2.compile();
  assert(orch2.state === OrchestratorState.ERROR, 'State is ERROR on compilation failure');
  assert(orch2.compiledScene === null, 'CRITICAL: No canned scene substituted on error');
  assert(orch2.currentError.includes('not ready yet'), 'Honest gating error message displayed');

  // Test 3: Unsupported subtype never routes to nearest solver
  console.log('\n[3/5] Unsupported subtype strictly halts in UNSUPPORTED');
  const mockApiUnsupported = {
    ingest: async () => ({
      success: true,
      status: 'unsupported',
      book_ir: {
        domain: 'optics',
        subtype: 'kaleidoscope_prism_array',
        status: 'UNSUPPORTED',
      },
      compiler: { status: 'UNSUPPORTED', scene: null },
    }),
  };
  const orch3 = new SimulationOrchestrator({ api: mockApiUnsupported });
  await orch3.startWithFile(new Blob(['bytes']), () => {});

  assert(orch3.state === OrchestratorState.UNSUPPORTED, 'Transitions to UNSUPPORTED');
  assert(orch3.compiledScene === null, 'No nearest-renderer fallback scene created');

  // Test 4: Offline backend produces ERROR, not demo physics
  console.log('\n[4/5] Backend offline network failure cleanly fails without canned demo');
  const mockApiOffline = {
    ingest: async () => {
      throw new Error('Backend server is offline (port 8000).');
    },
  };
  const orch4 = new SimulationOrchestrator({ api: mockApiOffline });
  await orch4.startWithFile(new Blob(['bytes']), () => {});

  assert(orch4.state === OrchestratorState.ERROR, 'Transitions to ERROR');
  assert(orch4.compiledScene === null, 'CRITICAL: No canned demo simulation launched on network failure');
  assert(orch4.currentError.includes('offline'), 'Displays actual offline error');

  // Test 5: Browser does not mark READY_TO_COMPILE on its own
  console.log('\n[5/5] Invariant: Only backend can confirm readiness');
  const mockApiStayUnready = {
    confirmCandidate: async () => ({
      success: true,
      bookIR: { status: 'NEEDS_REVIEW', parameters: { length: { value: 0.8 } } },
      canCompile: false,
    }),
    review: async () => ({
      success: true,
      readyToCompile: false, // Backend says NOT ready
      reviewState: { readyToCompile: false, issues: [{ parameterName: 'gravity' }] },
    }),
  };

  const orch5 = new SimulationOrchestrator({ api: mockApiStayUnready });
  orch5.bookIR = { status: 'NEEDS_REVIEW', parameters: {} };
  orch5.state = OrchestratorState.NEEDS_REVIEW;

  await orch5.confirmCandidate('length', { numericValue: 80, rawUnit: 'cm' });
  assert(orch5.state === OrchestratorState.NEEDS_REVIEW, 'State remains NEEDS_REVIEW when backend says not ready');
  assert(orch5.bookIR.status === 'NEEDS_REVIEW', 'BookIR status remains NEEDS_REVIEW');
}

runTests().then(() => {
  console.log('\n==============================================');
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log('==============================================');
  if (failed > 0) process.exit(1);
});

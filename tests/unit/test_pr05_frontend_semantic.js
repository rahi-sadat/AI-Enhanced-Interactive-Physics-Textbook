/**
 * tests/unit/test_pr05_frontend_semantic.js
 *
 * Verifies frontend PR-05 semantic understanding contracts:
 *   1. IngestResult provides typed accessors for classification, entities, relationships, visibleLabels, candidates, confidence.
 *   2. Supported pendulum diagram:
 *      - domain === 'mechanics'
 *      - scenario === 'pendulum'
 *      - status === 'needs-review'
 *      - isReady === false (NO simulation until CV/OCR)
 *      - scene === null
 *      - statusMessage contains clear domain/scenario guidance.
 *   3. Unsupported physics diagram:
 *      - domain === null
 *      - scenario === null
 *      - status === 'unsupported'
 *      - isReady === false
 *   4. Non-physics image:
 *      - classification === 'non_physics'
 *      - domain === null
 *      - scenario === null
 *      - status === 'unresolved'
 *   5. Numerical labels remain unverified in visibleLabels, NOT in trusted parameters.
 */

import { IngestResult } from '../../apps/web/src/features/simulations/core/UploadService.js';

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
console.log('  RUNNING PR-05 FRONTEND SEMANTIC TESTS');
console.log('==============================================\n');

async function runTests() {
  // Test 1: Supported Pendulum Envelope
  console.log('[1/4] Testing IngestResult with supported pendulum');
  const pendulumEnvelope = {
    success: true,
    pipeline: 'PR-05',
    status: 'needs-review',
    domain: 'mechanics',
    scenario: 'pendulum',
    scene: null,
    source_asset: { id: 'asset_001', width_px: 800, height_px: 600 },
    page_ir: { version: '1.0' },
    book_ir: {
      domain: 'mechanics',
      subtype: 'pendulum',
      status: 'NEEDS_REVIEW',
      statusNotes: 'Semantically understood as mechanics/pendulum. Precise extraction needed.',
      entities: [
        { id: 'e1', type: 'pivot', label: null, attributes: { confidence: 0.95 } },
        { id: 'e2', type: 'bob', label: 'm', attributes: { confidence: 0.98 } },
        { id: 'e3', type: 'string', label: null, attributes: { confidence: 0.91 } },
      ],
      relationships: [
        { type: 'connected_to', from: 'e1', to: 'e3', confidence: 0.92 },
      ],
      parameters: {}, // Zero fabricated parameters
      provenance: {
        classification: 'supported',
        provider: 'gemini',
        model: 'gemini-3.8-flash',
        visible_labels: [
          { text: 'L = 1.0 m', confidence: 0.85, verified: false },
        ],
        candidates: [],
      },
      confidence: { isPhysics: 0.99, domain: 0.96, subtype: 0.94 },
    },
    compiler: {
      status: 'NEEDS_REVIEW',
      scene: null,
      issues: [
        { code: 'MISSING_PENDULUM_BOB_POSITION', message: 'Bob position not yet extracted by CV.' },
      ],
    },
  };

  const res1 = new IngestResult(pendulumEnvelope);
  assert(res1.status === 'needs-review', 'Status is needs-review');
  assert(res1.domain === 'mechanics', 'Domain is mechanics');
  assert(res1.scenario === 'pendulum', 'Scenario is pendulum');
  assert(res1.classification === 'supported', 'Classification is supported');
  assert(res1.isReady === false, 'isReady is false (enforces zero fabrication without CV)');
  assert(res1.scene === null, 'Scene is strictly null');
  assert(res1.entities.length === 3, 'Preserves 3 semantic entities');
  assert(res1.entities[0].type === 'pivot', 'First entity role is pivot');
  assert(res1.entities[1].type === 'bob', 'Second entity role is bob');
  assert(res1.relationships.length === 1, 'Preserves relationship');
  assert(res1.visibleLabels.length === 1, 'Preserves visibleLabels');
  assert(res1.visibleLabels[0].verified === false, 'Visible label is explicitly unverified');
  assert(res1.statusMessage.includes('Recognized mechanics / pendulum'), 'Status message identifies concept');

  // Test 2: Unsupported Physics Envelope (e.g. Wave Diagram)
  console.log('\n[2/4] Testing IngestResult with unsupported physics diagram');
  const unsupportedEnvelope = {
    success: true,
    pipeline: 'PR-05',
    status: 'unsupported',
    domain: null,
    scenario: null,
    scene: null,
    book_ir: {
      domain: null,
      subtype: null,
      status: 'UNSUPPORTED',
      statusNotes: 'Image contains a physics diagram for which no interactive solver is implemented.',
      provenance: {
        classification: 'unsupported_physics',
        provider: 'gemini',
        model: 'gemini-3.8-flash',
      },
      confidence: { isPhysics: 0.96, domain: 0.0, subtype: 0.0 },
    },
    compiler: { status: 'UNSUPPORTED', scene: null, issues: [] },
  };

  const res2 = new IngestResult(unsupportedEnvelope);
  assert(res2.status === 'unsupported', 'Status is unsupported');
  assert(res2.domain === null, 'Domain is null');
  assert(res2.scenario === null, 'Subtype is null (never a status word)');
  assert(res2.classification === 'unsupported_physics', 'Classification is unsupported_physics');
  assert(res2.isReady === false, 'isReady is false');
  assert(res2.scene === null, 'Scene is null');
  assert(res2.statusMessage.includes('no simulation solver is currently available'), 'Status message states solver unavailable');

  // Test 3: Non-Physics Image (e.g. Landscape / Cat)
  console.log('\n[3/4] Testing IngestResult with non-physics photograph');
  const nonPhysicsEnvelope = {
    success: true,
    pipeline: 'PR-05',
    status: 'unresolved',
    domain: null,
    scenario: null,
    scene: null,
    book_ir: {
      domain: null,
      subtype: null,
      status: 'UNRESOLVED',
      statusNotes: 'Image does not depict a recognizable physics diagram or experiment.',
      provenance: {
        classification: 'non_physics',
        provider: 'gemini',
        model: 'gemini-3.8-flash',
      },
      confidence: { isPhysics: 0.02, domain: 0.0, subtype: 0.0 },
    },
    compiler: { status: 'UNRESOLVED', scene: null, issues: [] },
  };

  const res3 = new IngestResult(nonPhysicsEnvelope);
  assert(res3.status === 'unresolved', 'Status is unresolved');
  assert(res3.domain === null, 'Domain is null');
  assert(res3.scenario === null, 'Subtype is null');
  assert(res3.classification === 'non_physics', 'Classification is non_physics');
  assert(res3.isReady === false, 'isReady is false');

  // Test 4: Ambiguous diagram with candidate interpretations
  console.log('\n[4/4] Testing IngestResult with candidate interpretations');
  const ambiguousEnvelope = {
    success: true,
    pipeline: 'PR-05',
    status: 'unresolved',
    domain: null,
    scenario: null,
    scene: null,
    book_ir: {
      domain: null,
      subtype: null,
      status: 'UNRESOLVED',
      provenance: {
        classification: 'unknown',
        candidates: [
          { domain: 'optics', subtype: 'thin_lens', confidence: 0.55 },
          { domain: 'optics', subtype: 'spherical_mirror', confidence: 0.38 },
        ],
      },
      confidence: { isPhysics: 0.70, domain: 0.55, subtype: 0.55 },
    },
    compiler: { status: 'UNRESOLVED', scene: null, issues: [] },
  };

  const res4 = new IngestResult(ambiguousEnvelope);
  assert(res4.candidates.length === 2, 'Preserves 2 candidate interpretations');
  assert(res4.candidates[0].subtype === 'thin_lens', 'First candidate is thin_lens');
  assert(res4.candidates[1].subtype === 'spherical_mirror', 'Second candidate is spherical_mirror');
  assert(res4.domain === null, 'Canonical domain remains null below threshold');
  assert(res4.scenario === null, 'Canonical subtype remains null below threshold');

  console.log('\n==============================================');
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log('==============================================\n');

  if (failed > 0) {
    process.exit(1);
  }
}

runTests().catch(err => {
  console.error('Test execution failed:', err);
  process.exit(1);
});

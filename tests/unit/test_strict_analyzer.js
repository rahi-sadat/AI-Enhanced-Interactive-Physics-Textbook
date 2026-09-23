/**
 * tests/unit/test_strict_analyzer.js
 *
 * Verifies frontend strictness contract in diagramAnalyzer.js:
 *   1. uploadDiagramFile rejects when backend is unavailable and demo fallback is disabled.
 *   2. uploadDiagramFile allows local blob fallback only when VITE_ENABLE_DEMO_FALLBACK === 'true'.
 *   3. analyzeDiagram rejects on backend network failure without demo fallback.
 *   4. analyzeDiagram does not synthesize local scenes on needs_review / unsupported responses.
 *   5. analyzeDiagram sends null for unspecified focalLengthCm and gravity.
 */

import { uploadDiagramFile, analyzeDiagram } from '../../apps/web/src/features/simulations/core/diagramAnalyzer.js';

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
console.log('  RUNNING STRICT DIAGRAM ANALYZER TESTS');
console.log('==============================================\n');

const originalFetch = globalThis.fetch;

async function runTests() {
  // Test 1: uploadDiagramFile throws when backend is unavailable and VITE_ENABLE_DEMO_FALLBACK is disabled
  console.log('[1/5] Testing uploadDiagramFile strict rejection on backend failure');
  delete process.env.VITE_ENABLE_DEMO_FALLBACK;
  globalThis.fetch = async () => {
    throw new Error('Connection refused: 500');
  };

  const dummyFile = new Blob(['fake image content'], { type: 'image/png' });
  let uploadErrorCaught = false;
  try {
    await uploadDiagramFile(dummyFile);
  } catch (err) {
    uploadErrorCaught = true;
    assert(err.message.includes('Backend upload endpoint unavailable'), 'Upload threw strict backend error');
  }
  assert(uploadErrorCaught, 'Upload must strictly reject when backend fails and demo fallback is off');

  // Test 2: uploadDiagramFile allows local fallback when VITE_ENABLE_DEMO_FALLBACK is enabled
  console.log('\n[2/5] Testing uploadDiagramFile fallback behind VITE_ENABLE_DEMO_FALLBACK');
  process.env.VITE_ENABLE_DEMO_FALLBACK = 'true';
  globalThis.URL = globalThis.URL || {};
  globalThis.URL.createObjectURL = () => 'blob:http://localhost/demo-blob-123';
  globalThis.Image = class {
    constructor() {
      setTimeout(() => {
        this.naturalWidth = 800;
        this.naturalHeight = 600;
        if (this.onload) this.onload();
      }, 5);
    }
  };

  const fallbackUpload = await uploadDiagramFile(dummyFile);
  assert(fallbackUpload.success === true, 'Upload fallback succeeds when demo flag is on');
  assert(fallbackUpload.isLocal === true, 'Upload fallback marked as local');
  assert(fallbackUpload.image_url === 'blob:http://localhost/demo-blob-123', 'Returns blob URL under demo flag');

  // Test 3: analyzeDiagram throws on network failure when VITE_ENABLE_DEMO_FALLBACK is disabled
  console.log('\n[3/5] Testing analyzeDiagram strict rejection on network failure');
  delete process.env.VITE_ENABLE_DEMO_FALLBACK;
  globalThis.fetch = async () => {
    throw new Error('Network unreachable');
  };

  let analyzeErrorCaught = false;
  try {
    await analyzeDiagram('/uploads/test1.jpg', 'auto', {});
  } catch (err) {
    analyzeErrorCaught = true;
    assert(err.message.includes('Network unreachable'), 'Analysis threw strict error on backend failure');
  }
  assert(analyzeErrorCaught, 'analyzeDiagram must not synthesize scenes when backend fails');

  // Test 4: analyzeDiagram preserves needs_review and does NOT fabricate a scene
  console.log('\n[4/5] Testing analyzeDiagram preserves needs_review without scene fabrication');
  globalThis.fetch = async (url, opts) => {
    return {
      ok: true,
      json: async () => ({
        success: true,
        status: 'needs_review',
        domain: null,
        scenario: null,
        scene: null,
        analysis: {
          mode: 'automatic',
          source: { width: 797, height: 652, coordinate_space: 'source_px' },
        },
        issues: [
          {
            code: 'NO_CONFIDENT_SUPPORTED_CONCEPT',
            message: 'No supported physics concept was identified with sufficient confidence.',
          },
        ],
      }),
    };
  };

  const reviewResult = await analyzeDiagram('/uploads/test1.jpg', 'auto', {});
  assert(reviewResult.status === 'needs_review', 'Result status is needs_review');
  assert(reviewResult.scene === null, 'Result scene is strictly null');
  assert(reviewResult.issues.length === 1, 'Issues preserved');
  assert(reviewResult.issues[0].code === 'NO_CONFIDENT_SUPPORTED_CONCEPT', 'Issue code matches backend');

  // Test 5: analyzeDiagram sends null for unspecified focal length and gravity
  console.log('\n[5/5] Testing payload passes null for unspecified focal length and gravity');
  let capturedPayload = null;
  globalThis.fetch = async (url, opts) => {
    capturedPayload = JSON.parse(opts.body);
    return {
      ok: true,
      json: async () => ({
        success: true,
        status: 'needs_review',
        scene: null,
        issues: [],
      }),
    };
  };

  await analyzeDiagram('/uploads/test1.jpg', 'auto', { scenario: 'auto' });
  assert(capturedPayload !== null, 'Request payload captured');
  assert(capturedPayload.focal_length_cm === null, 'focal_length_cm is null, not 20.0');
  assert(capturedPayload.gravity === null, 'gravity is null, not 1.0');

  // Restore fetch
  globalThis.fetch = originalFetch;

  console.log(`\n==============================================`);
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log(`==============================================`);

  if (failed > 0) {
    process.exit(1);
  }
}

runTests().catch((err) => {
  console.error('Fatal error in strict analyzer tests:', err);
  process.exit(1);
});

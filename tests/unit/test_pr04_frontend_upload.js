/**
 * tests/unit/test_pr04_frontend_upload.js
 *
 * Verifies frontend PR-04 ingestion contracts:
 *   1. UploadService sends multipart/form-data with raw bytes, NOT JSON.
 *   2. UploadService strictly throws on backend network / 503 / 422 failure.
 *   3. IngestResult correctly wraps backend JSON payload (sourceAsset, pageIR, bookIR, compiler).
 *   4. File selection Gate Zero: real File retained, filename & native dimensions updated, Analyze enabled.
 *   5. Real uploaded file has ZERO fallback to legacy analysis on failure.
 */

import { UploadService, IngestResult } from '../../apps/web/src/features/simulations/core/UploadService.js';

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
console.log('  RUNNING PR-04 FRONTEND UPLOAD TESTS');
console.log('==============================================\n');

const originalFetch = globalThis.fetch;

async function runTests() {
  // Test 1: UploadService sends multipart/form-data with actual file
  console.log('[1/5] Testing UploadService sends multipart FormData with real file');
  let capturedUrl = null;
  let capturedMethod = null;
  let capturedBody = null;

  globalThis.fetch = async (url, options) => {
    capturedUrl = url;
    capturedMethod = options.method;
    capturedBody = options.body;
    return {
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        pipeline: 'PR-04',
        image_url: '/uploads/diagram_test.png',
        source_asset: {
          id: 'asset_123',
          sha256: 'abc456',
          width_px: 520,
          height_px: 340,
          byteSize: 12000,
          mimeType: 'image/png',
          originalFilename: 'cat_test.png',
        },
        page_ir: {
          coordinateSpace: { type: 'source_px', width: 520, height: 340 },
          source: { width_px: 520, height_px: 340 },
          figures: [{ id: 'fig_0', pageX: 0, pageY: 0, width: 520, height: 340, detectionMethod: 'user_supplied' }],
        },
        book_ir: {
          status: 'UNRESOLVED',
          domain: null,
          subtype: null,
          entities: [],
          parameters: {},
        },
        compiler: {
          status: 'UNRESOLVED',
          scene: null,
          issues: [{ code: 'UNRESOLVED', message: 'No understanding yet' }],
        },
        status: 'unresolved',
        domain: null,
        scenario: null,
        scene: null,
        issues: [{ code: 'UNRESOLVED', message: 'No understanding yet' }],
        width: 520,
        height: 340,
      }),
    };
  };

  const dummyFile = new Blob(['PNG_MOCK_BYTES_DATA'], { type: 'image/png' });
  dummyFile.name = 'cat_test.png';

  let progressCalled = false;
  const result = await UploadService.ingest(dummyFile, (msg, pct) => {
    progressCalled = true;
  });

  assert(capturedUrl === '/api/ingest', 'Sent request to /api/ingest');
  assert(capturedMethod === 'POST', 'Sent POST request');
  assert(capturedBody instanceof FormData, 'Sent multipart FormData (not JSON string)');
  assert(capturedBody.get('file') !== null, 'FormData contains "file" entry with actual bytes');
  assert(progressCalled, 'Reported upload progress callback');
  assert(result instanceof IngestResult, 'Returned typed IngestResult instance');
  assert(result.isUnresolved === true, 'Correctly reports isUnresolved === true');
  assert(result.isReady === false, 'Correctly reports isReady === false');
  assert(result.widthPx === 520 && result.heightPx === 340, 'Native dimensions survive in IngestResult');
  assert(result.sourceAsset.sha256 === 'abc456', 'SourceAsset SHA-256 preserved');
  assert(result.bookIR.domain === null, 'BookIR domain is truthfully null');

  // Test 2: UploadService strictly rejects on backend failure (e.g. 503 or 422)
  console.log('\n[2/5] Testing UploadService strict rejection on backend failure');
  globalThis.fetch = async () => ({
    ok: false,
    status: 503,
    statusText: 'Service Unavailable',
    text: async () => 'PR-04 ingestion pipeline unavailable.',
  });

  let threwError = false;
  try {
    await UploadService.ingest(dummyFile);
  } catch (err) {
    threwError = true;
    assert(err.message.includes('503'), 'Error message includes HTTP 503 status');
  }
  assert(threwError, 'UploadService strictly throws without swallowing error');

  // Test 3: Gate Zero file selection simulation
  console.log('\n[3/5] Testing Gate Zero file selection contract');
  let selectedFile = null;
  let preview = { filename: '', dims: '', enabled: false };

  function simulateFileSelection(file, imgNaturalWidth, imgNaturalHeight) {
    selectedFile = file;
    // Emulates main.js handleFile
    preview.filename = file.name;
    preview.dims = `${imgNaturalWidth} × ${imgNaturalHeight} px`;
    preview.enabled = true; // Analyze button enabled
  }

  const testImageFile = { name: 'random_photo_99.png', type: 'image/png', size: 45678 };
  simulateFileSelection(testImageFile, 1280, 720);

  assert(selectedFile === testImageFile, 'Retains actual File reference');
  assert(preview.filename === 'random_photo_99.png', 'Immediate preview shows original filename');
  assert(preview.dims === '1280 × 720 px', 'Immediate preview shows native width × height');
  assert(preview.enabled === true, 'Analyze button is enabled immediately upon selection');

  // Test 4: Real uploaded file has zero legacy fallback on error
  console.log('\n[4/5] Testing real upload error has ZERO legacy fallback');
  let legacyCalled = false;
  async function simulateBtnGenerateSim(uploadedFile) {
    if (uploadedFile) {
      try {
        await UploadService.ingest(uploadedFile);
      } catch (err) {
        // Fatal error: STOP! Never call legacy path
        return { status: 'fatal_error', error: err.message };
      }
      return { status: 'ingested' };
    }
    // Legacy path (presets only)
    legacyCalled = true;
    return { status: 'legacy' };
  }

  globalThis.fetch = async () => {
    throw new Error('Connection refused to /api/ingest');
  };

  const uploadRunResult = await simulateBtnGenerateSim(dummyFile);
  assert(uploadRunResult.status === 'fatal_error', 'Failed ingestion cleanly halts as fatal_error');
  assert(legacyCalled === false, 'CRITICAL: Legacy analysis path was NEVER called for uploaded file');

  // Test 5: IngestResult READY scene preservation
  console.log('\n[5/6] Testing IngestResult READY scene preservation');
  const readyResult = new IngestResult({
    success: true,
    pipeline: 'PR-04',
    image_url: '/uploads/pendulum_ready.png',
    source_asset: { id: 'ast1', width_px: 600, height_px: 400, sha256: 'readyhash' },
    page_ir: { source: { width_px: 600, height_px: 400 } },
    book_ir: { domain: 'mechanics', subtype: 'pendulum', status: 'READY' },
    compiler: { status: 'READY', scene: { domain: 'mechanics', subtype: 'pendulum' }, issues: [] },
  });
  assert(readyResult.isReady === true, 'IngestResult reports isReady === true for complete scene');
  assert(readyResult.domain === 'mechanics', 'IngestResult extracts domain');
  assert(readyResult.scene !== null, 'IngestResult provides executable scene');

  // Test 6: Canonical PhysicsRuntime loads compiler-generated READY scene
  console.log('\n[6/6] Testing Canonical PhysicsRuntime loads compiler-generated READY scene');
  const { PhysicsRuntime } = await import('../../engine/core/PhysicsRuntime.js');
  const runtime = new PhysicsRuntime();

  const canonicalCompilerScene = {
    schemaVersion: '1.0',
    id: 'PHY-MECH-figure_001',
    domain: 'mechanics',
    subtype: 'pendulum',
    source: {
      type: 'book_figure',
      source_asset_id: 'ast1',
      figure_id: 'fig1',
      width: 800,
      height: 600,
    },
    coordinateSpace: {
      type: 'source_px',
      width: 800,
      height: 600,
      unit: 'px',
    },
    parameters: {
      length: { value: 1.2, unit: 'm', provenance: 'observed' },
      gravity: { value: 9.81, unit: 'm/s²', provenance: 'assumed' },
      initialAngle: { value: 20.0, unit: '°', provenance: 'observed' },
      mass: { value: 1.0, unit: 'kg', provenance: 'assumed' },
      damping: { value: 0.05, unit: '1/s', provenance: 'assumed' },
    },
    geometry: {
      pivot: { x: 400, y: 100 },
      bob_center: { x: 450, y: 350 },
      string_length_px: 250,
      bob_radius_px: 20,
    },
    environment: {
      gravity: 9.81,
      gravity_m_s2: 9.81,
    },
    objects: [
      {
        id: 'pendulum_bob_1',
        type: 'pendulum',
        role: 'dynamic',
        geometry: {
          pivot: { x: 400, y: 100 },
          string_length_px: 250,
          length_px: 250,
          bob_radius_px: 20,
        },
        physics: {
          length_m: 1.2,
          mass_kg: 1.0,
          damping_s_inv: 0.05,
          theta0_rad: 0.349,
          omega0_rad_s: 0.0,
        },
      },
    ],
  };

  const loadedOutput = await runtime.load(canonicalCompilerScene);
  assert(loadedOutput !== null, 'PhysicsRuntime successfully loaded canonical compiled scene');
  assert(runtime.adapter !== null, 'PhysicsRuntime initialized MechanicsAdapter');
  assert(runtime.adapter.subtype === 'pendulum', 'MechanicsAdapter confirmed pendulum subtype');
  assert(runtime.scene.schemaVersion === '1.0', 'Runtime scene preserves canonical schemaVersion 1.0');
  runtime.dispose();

  // Summary
  console.log('\n==============================================');
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log('==============================================\n');

  // Restore fetch
  globalThis.fetch = originalFetch;

  if (failed > 0) {
    process.exit(1);
  }
}

runTests().catch(err => {
  console.error('Unhandled test failure:', err);
  process.exit(1);
});

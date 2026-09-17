/**
 * test/test_coordinateMapper.js
 * 
 * Release-gate tests for CoordinateMapper precision:
 * - Round-trip source -> view -> source numerical error < 1e-9 px
 * - Aspect-ratio contain scaling across multiple image dimensions
 * - HiDPI DPR scaling
 */

import { CoordinateMapper } from '../../engine/core/coordinateMapper.js';

function assert(condition, message) {
  if (!condition) {
    console.error(`❌ FAIL: ${message}`);
    process.exit(1);
  }
  console.log(`  ✓ PASS: ${message}`);
}

function assertClose(actual, expected, tol = 1e-6, message = '') {
  const diff = Math.abs(actual - expected);
  if (diff > tol) {
    console.error(`❌ FAIL: ${message} (expected ~${expected}, got ${actual}, diff: ${diff})`);
    process.exit(1);
  }
  console.log(`  ✓ PASS: ${message}`);
}

console.log('\n==============================================');
console.log('  RUNNING COORDINATEMAPPER PRECISION TESTS');
console.log('==============================================');

// TEST 1: Exact Aspect Ratio Contain & Letterbox Offsets
console.log('\n[1/3] Testing contain letterbox calculations across aspect ratios');
{
  // 393x328 in 800x600 container (Wide letterbox)
  const mapper1 = new CoordinateMapper(393, 328, 800, 600, 1);
  const expectedScale1 = Math.min(800 / 393, 600 / 328); // 1.829268...
  assertClose(mapper1.scale, expectedScale1, 1e-6, '393x328 in 800x600: scale matches min ratio');
  assertClose(mapper1.renderedWidth, 393 * expectedScale1, 1e-6, 'Rendered width');
  assertClose(mapper1.offsetX, (800 - 393 * expectedScale1) / 2.0, 1e-6, 'Horizontal letterbox offset');
  assertClose(mapper1.offsetY, 0.0, 1e-6, 'Vertical offset is zero for wide letterbox');

  // 797x652 in 1280x900 container (Tall letterbox)
  const mapper2 = new CoordinateMapper(797, 652, 1280, 900, 1);
  const expectedScale2 = Math.min(1280 / 797, 900 / 652);
  assertClose(mapper2.scale, expectedScale2, 1e-6, '797x652 in 1280x900: scale matches min ratio');
  assertClose(mapper2.offsetY, (900 - 652 * expectedScale2) / 2.0, 1e-6, 'Vertical letterbox offset');
}

// TEST 2: Round-Trip Conversion Precision (< 1e-9 px numerical error)
console.log('\n[2/3] Testing round-trip source -> view -> source inversion');
{
  const mapper = new CoordinateMapper(797, 652, 1024, 768, 2.0);
  const testPoints = [
    { x: 0, y: 0 },
    { x: 246.580128, y: 527.56464 },
    { x: 468.01835, y: 99.726816 },
    { x: 797, y: 652 },
    { x: 398.5, y: 326.0 },
  ];

  testPoints.forEach((pt, i) => {
    const view = mapper.sourceToView(pt);
    const roundTrip = mapper.viewToSource(view);
    assertClose(roundTrip.x, pt.x, 1e-9, `Point ${i} X round-trip numerical error < 1e-9`);
    assertClose(roundTrip.y, pt.y, 1e-9, `Point ${i} Y round-trip numerical error < 1e-9`);

    // Scalar length
    const len = 481.746915;
    const vLen = mapper.sourceLengthToView(len);
    const rtLen = mapper.viewLengthToSource(vLen);
    assertClose(rtLen, len, 1e-9, `Scalar length round-trip numerical error < 1e-9`);
  });
}

// TEST 3: Dynamic Viewport Resize & DPR Scaling
console.log('\n[3/3] Testing dynamic viewport update & device pixel scaling');
{
  const mapper = new CoordinateMapper(800, 600, 800, 600, 1.0);
  assertClose(mapper.scale, 1.0, 1e-6, 'Initial 1:1 scale');

  // Resize container to 1600x1200 with DPR = 2.0
  mapper.updateViewport(1600, 1200, 2.0);
  assertClose(mapper.scale, 2.0, 1e-6, 'Scale updated to 2.0 after container resize');
  assertClose(mapper.dpr, 2.0, 1e-6, 'DPR updated to 2.0');

  const devPt = mapper.sourceToDevice({ x: 100, y: 100 });
  // View = 100 * 2 = 200 CSS px; Device = 200 * 2 = 400 screen px
  assertClose(devPt.x, 400.0, 1e-6, 'Device screen coordinate accounts for DPR');
  assertClose(devPt.y, 400.0, 1e-6, 'Device screen coordinate accounts for DPR');
}

console.log('\nAll CoordinateMapper tests passed successfully!\n');

/**
 * test/test_coordinate_mapper.js
 * Unit tests for CoordinateMapper.
 */
import { CoordinateMapper } from '../src/core/coordinateMapper.js';

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

function assertClose(actual, expected, tol = 0.001, message = '') {
  const diff = Math.abs(actual - expected);
  assert(diff <= tol, `${message} (expected ~${expected}, got ${actual})`);
}

console.log('==============================================');
console.log('  RUNNING COORDINATE MAPPER TESTS');
console.log('==============================================\n');

// 1. Pillarboxed Image (393 x 328 in 800 x 600 viewport)
console.log('[1/4] Testing Pillarbox Mapping (393x328 in 800x600)');
const mapperPillar = new CoordinateMapper(393, 328, 800, 600);
assertClose(mapperPillar.scale, 600 / 328, 0.0001, 'Uniform scale fits height');
assertClose(mapperPillar.offsetY, 0.0, 0.0001, 'Y offset is 0');
assertClose(mapperPillar.offsetX, (800 - 393 * (600 / 328)) / 2, 0.0001, 'X offset is ~40.55');

// Normal line at source x=214
const ptNormal = mapperPillar.sourceToView(214, 0);
assertClose(ptNormal.x, 40.5488 + 214 * (600 / 328), 0.01, 'Normal line mapped to 432.0px');

// Boundary line at source y=159
const ptBound = mapperPillar.sourceToView(0, 159);
assertClose(ptBound.y, 159 * (600 / 328), 0.01, 'Boundary line mapped to 290.85px');

// 2. Letterboxed Image (1536 x 1024 in 800 x 600 viewport)
console.log('\n[2/4] Testing Letterbox Mapping (1536x1024 in 800x600)');
const mapperLetter = new CoordinateMapper(1536, 1024, 800, 600);
assertClose(mapperLetter.scale, 800 / 1536, 0.0001, 'Uniform scale fits width');
assertClose(mapperLetter.offsetX, 0.0, 0.0001, 'X offset is 0');
assertClose(mapperLetter.offsetY, (600 - 1024 * (800 / 1536)) / 2, 0.0001, 'Y offset is ~33.33');

// 3. Bidirectional Inversion Test
console.log('\n[3/4] Testing Bidirectional Inversion');
const testPoints = [
  { x: 0, y: 0 },
  { x: 100, y: 200 },
  { x: 393, y: 328 },
  { x: 214.65, y: 158.82 },
];
testPoints.forEach(pt => {
  const v = mapperPillar.sourceToView(pt.x, pt.y);
  const back = mapperPillar.viewToSource(v.x, v.y);
  assertClose(back.x, pt.x, 0.0001, `Invert X (${pt.x}, ${pt.y})`);
  assertClose(back.y, pt.y, 0.0001, `Invert Y (${pt.x}, ${pt.y})`);
});

// 4. Length & Box Scaling
console.log('\n[4/4] Testing Length & Box Scaling');
const srcLen = 50;
const viewLen = mapperPillar.sourceLengthToView(srcLen);
assertClose(mapperPillar.viewLengthToSource(viewLen), srcLen, 0.0001, 'Bidirectional length scaling');

const box = { x: 10, y: 20, width: 60, height: 40 };
const vBox = mapperPillar.sourceBoxToView(box);
const sBox = mapperPillar.viewBoxToSource(vBox);
assertClose(sBox.x, box.x, 0.0001, 'Box round-trip X');
assertClose(sBox.y, box.y, 0.0001, 'Box round-trip Y');
assertClose(sBox.width, box.width, 0.0001, 'Box round-trip width');
assertClose(sBox.height, box.height, 0.0001, 'Box round-trip height');

console.log(`\nResults: ${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);

/** test/test_optics_engines.js
 * Automated unit test suite verifying physics calculations for:
 * 1. Thin Lens Engine (all 5 core textbook cases)
 * 2. Ray Geometry (vector reflection, Snell refraction, TIR)
 * 3. Prism Engine (vector refraction, deviation angle, TIR)
 * 4. Mirror Engine (concave, convex, plane)
 */
import { solveThinLens } from '../src/optics/engines/thinLensEngine.js';
import { solvePrismRefraction } from '../src/optics/engines/prismEngine.js';
import { solveMirror } from '../src/optics/engines/mirrorEngine.js';
import { solveSnellInterface, traceInterfaceRefraction } from '../src/optics/engines/snellInterfaceEngine.js';
import { normalize, dot, reflect, refract } from '../src/optics/engines/rayGeometry.js';

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

function assertClose(actual, expected, tol = 0.01, message = '') {
  const diff = Math.abs(actual - expected);
  assert(diff <= tol, `${message} (expected ~${expected}, got ${actual})`);
}

console.log('==============================================');
console.log('  RUNNING OPTICS2D PHYSICS SUITE TESTS');
console.log('==============================================\n');

// ----------------------------------------------------
// 1. THIN LENS ENGINE TESTS
// ----------------------------------------------------
console.log('[1/4] Testing Thin Lens Formula (1/f = 1/u + 1/v)');
const f = 100;
const lensX = 400;
const axisY = 300;
const h0 = -80; // upright object height

// Case 1: u > 2f (e.g. u = 300 > 200) -> f < v < 2f, diminished real image
{
  const res = solveThinLens({ lensX, axisY, objectX: lensX - 300, objectHeight: h0, focalLength: f });
  assert(res.isReal === true, 'Case 1 (u > 2f): image is real');
  assert(res.isInverted === true, 'Case 1 (u > 2f): image is inverted');
  assertClose(res.v, 150, 0.1, 'Case 1: v = (f*u)/(u-f) = (100*300)/200 = 150');
  assertClose(res.magnification, -0.5, 0.01, 'Case 1: m = -v/u = -150/300 = -0.5');
  assert(res.imageType.includes('diminished'), 'Case 1: image is diminished');
}

// Case 2: u = 2f (u = 200) -> v = 2f = 200, m = -1 (same size)
{
  const res = solveThinLens({ lensX, axisY, objectX: lensX - 200, objectHeight: h0, focalLength: f });
  assert(res.isReal === true, 'Case 2 (u = 2f): image is real');
  assertClose(res.v, 200, 0.1, 'Case 2: v = 200');
  assertClose(res.magnification, -1.0, 0.01, 'Case 2: m = -1.0 (same size)');
  assert(res.imageType.includes('same_size'), 'Case 2: imageType is same_size');
}

// Case 3: f < u < 2f (u = 150) -> v > 2f, magnified real image
{
  const res = solveThinLens({ lensX, axisY, objectX: lensX - 150, objectHeight: h0, focalLength: f });
  assert(res.isReal === true, 'Case 3 (f < u < 2f): image is real');
  assertClose(res.v, 300, 0.1, 'Case 3: v = (100*150)/50 = 300');
  assertClose(res.magnification, -2.0, 0.01, 'Case 3: m = -300/150 = -2.0');
  assert(res.imageType.includes('magnified'), 'Case 3: image is magnified');
}

// Case 4: u = f (u = 100) -> Image at infinity
{
  const res = solveThinLens({ lensX, axisY, objectX: lensX - 100, objectHeight: h0, focalLength: f });
  assert(res.imageType === 'infinity', 'Case 4 (u = f): imageType is infinity');
  assert(res.v === Infinity, 'Case 4: v = Infinity');
}

// Case 5: u < f (u = 50) -> Virtual, upright, magnified image behind object
{
  const res = solveThinLens({ lensX, axisY, objectX: lensX - 50, objectHeight: h0, focalLength: f });
  assert(res.isReal === false, 'Case 5 (u < f): image is virtual');
  assert(res.isInverted === false, 'Case 5: image is upright');
  assertClose(res.v, -100, 0.1, 'Case 5: v = (100*50)/(-50) = -100');
  assertClose(res.magnification, 2.0, 0.01, 'Case 5: m = -(-100)/50 = +2.0');
  assert(res.rays.some(r => r.dashed), 'Case 5: contains dashed virtual ray extensions');
}

// Case 6: Concave Diverging Lens (f = -100, u = 150) -> Virtual, upright, diminished
{
  const resConcaveLens = solveThinLens({ lensX, axisY, objectX: lensX - 150, objectHeight: h0, focalLength: -100 });
  assert(resConcaveLens.isReal === false, 'Case 6 (Concave lens): image is virtual');
  assert(resConcaveLens.isInverted === false, 'Case 6: image is upright');
  assert(resConcaveLens.imageType.includes('diminished'), 'Case 6: image is diminished');
  assertClose(resConcaveLens.v, -60, 0.1, 'Case 6: v = (-100*150)/(150 - (-100)) = -60');
  assertClose(resConcaveLens.magnification, 0.4, 0.01, 'Case 6: m = -(-60)/150 = +0.4');
  assert(resConcaveLens.lensType === 'concave', 'Case 6: lensType is concave');
}

console.log('\n[2/4] Testing Ray Vector Geometry & Snell Refraction');
{
  const v = normalize({ x: 3, y: 4 });
  assertClose(Math.hypot(v.x, v.y), 1.0, 0.0001, 'normalize produces unit length vector');

  // Law of reflection
  const inc = normalize({ x: 1, y: 1 });
  const normal = { x: 0, y: -1 }; // horizontal surface pointing down
  const refl = reflect(inc, normal);
  assertClose(refl.x, inc.x, 0.001, 'reflect preserves tangential component');
  assertClose(refl.y, -inc.y, 0.001, 'reflect inverts normal component');

  // Snell refraction: normal incidence doesn\'t bend
  const refrNormal = refract({ x: 0, y: 1 }, { x: 0, y: -1 }, 1.0, 1.5);
  assertClose(refrNormal.direction.x, 0, 0.001, 'Normal incidence has no bending');
  assert(refrNormal.type === 'refracted', 'Normal incidence is refracted');

  // Total internal reflection (glass n=1.5 to air n=1.0 at 60 deg incidence)
  // Normal is {-1, 0}, so ray moving towards +x with 60 deg angle: x = 0.5, y = sqrt(3)/2
  const refrTir = refract(normalize({ x: 0.5, y: Math.sqrt(3)/2 }), { x: -1, y: 0 }, 1.5, 1.0);
  assert(refrTir.type === 'tir', 'High incidence angle (60 deg > 41.8 deg) inside dense medium triggers TIR');
}

console.log('\n[3/4] Testing Prism & Refractive Polygon Engines');
{
  // 1. Triangular Prism
  const prismVertices = [
    { x: 300, y: 440 },
    { x: 440, y: 160 },
    { x: 580, y: 440 }
  ];
  const resPrism = solvePrismRefraction({
    prismVertices,
    refractiveIndex: 1.52,
    rayOrigin: { x: 100, y: 350 },
    rayDirection: { x: 250, y: 0 }
  });

  assert(resPrism.hitPrism === true, 'Ray intersects triangular prism');
  assert(resPrism.segments.length === 3, 'Ray has incident, internal, and emergent segments');
  assert(resPrism.normals.length === 2, '2 surface normal lines generated');
  assert(resPrism.angles.i1Deg > 0, 'Incidence angle i1 calculated');
  assert(resPrism.angles.r1Deg > 0 && resPrism.angles.r1Deg < resPrism.angles.i1Deg, 'Refraction angle r1 obeys Snell law (r1 < i1)');
  assert(resPrism.angles.deviationDeg > 0, 'Deviation angle delta calculated');
  assertClose(resPrism.angles.criticalAngleDeg, 41.14, 0.2, 'Critical angle theta_c ~ 41.14 deg for n=1.52');

  // 2. Rectangular Glass Slab (Parallel Faces -> Zero Deviation)
  const slabVertices = [
    { x: 240, y: 210 },
    { x: 560, y: 210 },
    { x: 560, y: 390 },
    { x: 240, y: 390 }
  ];
  const resSlab = solvePrismRefraction({
    prismVertices: slabVertices,
    refractiveIndex: 1.50,
    rayOrigin: { x: 120, y: 90 },
    rayDirection: { x: 220, y: 120 }
  });
  assert(resSlab.hitPrism === true, 'Ray enters rectangular glass slab');
  assert(resSlab.tir === false, 'Ray transmits through glass slab without TIR');
  assertClose(resSlab.angles.deviationDeg, 0, 0.01, 'Glass slab emergent ray is parallel to incident ray (delta = 0)');

  // 3. 45-90-45 Right-Angle Periscope Prism (TIR at 45 deg)
  const tirVertices = [
    { x: 260, y: 180 },
    { x: 260, y: 440 },
    { x: 520, y: 440 }
  ];
  const resTirPrism = solvePrismRefraction({
    prismVertices: tirVertices,
    refractiveIndex: 1.52,
    rayOrigin: { x: 100, y: 310 },
    rayDirection: { x: 160, y: 0 }
  });
  assert(resTirPrism.hitPrism === true, 'Ray enters 45-90-45 right angle prism');
  assert(resTirPrism.tir === true, 'Ray undergoes 100% TIR at 45 deg hypotenuse');
  assert(resTirPrism.segments[2].type === 'tir_reflected', 'Segment 3 is TIR reflected downwards');
}

console.log('\n[4/4] Testing Spherical & Plane Mirror Engine');
{
  // Concave mirror (f = 100, object at u = 250 > 2f = 200)
  const resConcave = solveMirror({
    mirrorType: 'concave',
    mirrorX: 500,
    axisY: 300,
    objectX: 250, // u = 250
    objectHeight: -60,
    focalLength: 100
  });
  assert(resConcave.isReal === true, 'Concave mirror (u > 2f): image is real');
  assertClose(resConcave.v, 166.67, 0.5, 'Concave mirror: v = (100*250)/150 = 166.7');
  assert(resConcave.isInverted === true, 'Concave mirror: real image is inverted');

  // Convex mirror (diverging, f = 100, u = 150)
  const resConvex = solveMirror({
    mirrorType: 'convex',
    mirrorX: 500,
    axisY: 300,
    objectX: 350, // u = 150
    objectHeight: -60,
    focalLength: 100
  });
  assert(resConvex.isReal === false, 'Convex mirror: image is always virtual');
  assert(resConvex.isInverted === false, 'Convex mirror: image is upright');
  assert(resConvex.magnification < 1.0, 'Convex mirror: image is diminished');

  // Plane mirror (u = 150)
  const resPlane = solveMirror({
    mirrorType: 'plane',
    mirrorX: 500,
    axisY: 300,
    objectX: 350, // u = 150
    objectHeight: -60,
    focalLength: 0
  });
  assert(resPlane.isReal === false, 'Plane mirror: image is virtual');
  assertClose(resPlane.v, -150, 0.01, 'Plane mirror: v = -u = -150');
  assertClose(resPlane.magnification, 1.0, 0.01, 'Plane mirror: m = 1.0');
}

// ----------------------------------------------------
// 5. INTERFACE REFRACTION (SNELL'S LAW & TIR) TESTS
// ----------------------------------------------------
console.log('\n[5/5] Testing Snell Interface Refraction & TIR');
{
  // Air to Glass (n1=1.0, n2=1.5, theta1=30 deg)
  const r1 = solveSnellInterface(1.0, 1.5, 30);
  assert(r1.isTIR === false, 'Air to Glass at 30 deg is not TIR');
  assertClose(r1.theta2Deg, 19.47, 0.1, 'Air to Glass: sin(19.47) ~ 1.0*sin(30)/1.5');
  assert(r1.thetaCritDeg === null, 'No critical angle when going rarer -> denser');

  // Glass to Air (n1=1.5, n2=1.0)
  const r2 = solveSnellInterface(1.5, 1.0, 30);
  assert(r2.isTIR === false, 'Glass to Air at 30 deg (< theta_c) is not TIR');
  assertClose(r2.thetaCritDeg, 41.81, 0.1, 'Critical angle for glass/air is 41.81 deg');
  assertClose(r2.theta2Deg, 48.59, 0.1, 'Glass to Air: theta2 is 48.59 deg');

  // Glass to Air above critical angle (theta1 = 50 deg > 41.81 deg) -> TIR!
  const r3 = solveSnellInterface(1.5, 1.0, 50);
  assert(r3.isTIR === true, 'Glass to Air at 50 deg (> theta_c) exhibits TIR');
  assert(r3.theta2Rad === null, 'No refraction angle in TIR');

  // Ray trace
  const trace = traceInterfaceRefraction({
    boundaryY: 300,
    normalX: 400,
    n1: 1.0,
    n2: 1.5,
    source: { x: 200, y: 100 },
    targetPoint: { x: 400, y: 300 }
  });
  assert(trace.incidentRay != null, 'Incident ray generated');
  assert(trace.refractedRay != null, 'Refracted ray generated');
  assertClose(trace.angles.theta1Deg, 45.0, 0.2, 'Incidence angle computed correctly');
}

console.log('\n==============================================');
console.log(`  TEST RESULTS: ${passed} passed, ${failed} failed`);
console.log('==============================================\n');

if (failed > 0) {
  process.exit(1);
} else {
  console.log('All optics physics engine tests passed successfully!\n');
}


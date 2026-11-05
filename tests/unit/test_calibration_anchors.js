import assert from 'node:assert/strict';
import { calibrationAnchorsFromScene } from '../../apps/web/src/components/calibrationAnchors.js';

for (const subtype of ['pendulum', 'projectile', 'thin_lens', 'spherical_mirror',
  'interface_refraction', 'prism', 'dc_linear']) {
  assert.deepEqual(calibrationAnchorsFromScene({ subtype, geometry: {}, circuit: {} }), [],
    `${subtype} must not show a guessed reticle`);
}

assert.deepEqual(calibrationAnchorsFromScene({
  subtype: 'pendulum', geometry: { pivot: { x: 29, y: 31 }, bob_center: { x: 50, y: 80 } }
}).map(({ id, x, y }) => [id, x, y]), [['pivot', 29, 31], ['bob', 50, 80]]);

assert.deepEqual(calibrationAnchorsFromScene({
  subtype: 'interface_refraction', geometry: { normalX: 249, boundaryY: 177 }
}).map(({ id, x, y }) => [id, x, y]), [['incidence', 249, 177]]);

assert.deepEqual(calibrationAnchorsFromScene({
  subtype: 'dc_linear',
  circuit: { components: [{ id: 'R1', terminals: [
    { id: 'R1.t1', source_px: [513, 145] },
    { id: 'R1.t2', source_px: [600, 145] }
  ] }] }
}).map(({ id, x, y }) => [id, x, y]), [
  ['R1.t1', 513, 145], ['R1.t2', 600, 145]
]);

assert.deepEqual(calibrationAnchorsFromScene({
  subtype: 'thin_lens', geometry: { lens_center: { x: Number.NaN, y: 300 } }
}), [], 'non-finite coordinates must not be displayed');

console.log('Calibration reticles use only finite source coordinates.');

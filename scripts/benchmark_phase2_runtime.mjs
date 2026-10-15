/** Load the actual reviewed image scene from the Python benchmark into the JS runtime. */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { PhysicsRuntime } from '../engine/core/PhysicsRuntime.js';
import '../engine/mechanics/MechanicsAdapter.js';

const resultPath = process.argv[2] ?? new URL('../storage/generated/phase2_benchmark.json', import.meta.url);
const benchmark = JSON.parse(readFileSync(resultPath, 'utf8'));
const cases = benchmark.cases.filter(row => row.auto_scene || row.review?.scene);
assert.ok(cases.length > 0, 'No compiled scene in benchmark output');

const results = [];
for (const row of cases) {
  const runtime = new PhysicsRuntime();
  const scene = row.auto_scene || row.review.scene;
  try {
    const initial = await runtime.load(scene);
    assert.equal(initial.domain, row.domain);
    assert.equal(initial.subtype, row.subtype);
    const before = runtime.getState();
    runtime.start();
    for (let step = 0; step < 30; step += 1) runtime.step(1 / 60);
    const after = runtime.getState();
    if (row.domain === 'mechanics') {
      assert.ok(Number.isFinite(after.time) && after.time > before.time,
        `${row.id}: simulation time did not advance`);
    }
    if (row.subtype === 'pendulum') {
      assert.ok(Number.isFinite(after.thetaRad) && Number.isFinite(after.omega),
        `${row.id}: pendulum state is nonfinite`);
      assert.notEqual(after.thetaRad, before.thetaRad,
        `${row.id}: pendulum angle did not evolve`);
      const { length, mass, gravity } = scene.parameters;
      const energy = state => 0.5 * mass.value * (length.value * state.omega) ** 2 +
        mass.value * gravity.value * length.value * (1 - Math.cos(state.thetaRad));
      const initialEnergy = energy(before);
      const relativeEnergyError = Math.abs(energy(after) - initialEnergy) / initialEnergy;
      assert.ok(relativeEnergyError < 0.001,
        `${row.id}: undamped pendulum energy drift ${relativeEnergyError}`);
      assert.equal(length.provenance, 'user_supplied');
      assert.equal(gravity.provenance, 'policy_default');
      assert.equal(scene.parameters.damping.value, 0);
      row.runtime_energy_relative_error = relativeEnergyError;
    } else if (row.subtype === 'projectile') {
      const { speed, angle, gravity } = scene.parameters;
      const radians = angle.value * Math.PI / 180;
      const expectedX = speed.value * Math.cos(radians) * after.time;
      const expectedY = speed.value * Math.sin(radians) * after.time -
        0.5 * gravity.value * after.time ** 2;
      assert.ok(Math.abs(after.xM - expectedX) < 0.002,
        `${row.id}: horizontal position disagrees with analytic trajectory`);
      assert.ok(Math.abs(after.yM - expectedY) < 0.002,
        `${row.id}: vertical position disagrees with analytic trajectory`);
      row.runtime_position_error_m = Math.hypot(after.xM - expectedX, after.yM - expectedY);
    } else if (row.subtype === 'interface_refraction') {
      const { n1, n2, theta1 } = scene.parameters;
      const solution = after.solution;
      assert.ok(solution && !solution.isTIR, `${row.id}: expected refracted ray`);
      const expectedTheta2 = Math.asin((n1.value / n2.value) *
        Math.sin(theta1.value * Math.PI / 180)) * 180 / Math.PI;
      assert.ok(Math.abs(solution.theta2Deg - expectedTheta2) < 0.01,
        `${row.id}: refracted angle disagrees with Snell's law`);
      row.runtime_angle_error_deg = Math.abs(solution.theta2Deg - expectedTheta2);
    }
    runtime.reset();
    const reset = runtime.getState();
    if (row.domain === 'mechanics') {
      assert.ok(Math.abs(reset.time - before.time) < 1e-9,
        `${row.id}: reset did not restore initial time`);
    }
    results.push({ id: row.id, runtime_loaded: true, advanced_time: after.time,
      reset_time: reset.time, energy_relative_error: row.runtime_energy_relative_error,
      position_error_m: row.runtime_position_error_m,
      angle_error_deg: row.runtime_angle_error_deg });
  } finally {
    runtime.dispose();
  }
}
console.log(JSON.stringify({ cases: results.length, results }, null, 2));

// Benchmark-only bridge: use the real canonical runtime and the existing
// source-position method, with no duplicated pendulum equations or DOM mocks.
import fs from 'node:fs';
import { PhysicsRuntime } from '../../engine/core/physicsRuntime.js';
import { PendulumSimulation } from '../../engine/mechanics/pendulumSimulation.js';

// Optional prepared-case file supports separate Python/Node environments.
const input = JSON.parse(fs.readFileSync(process.argv[2] || 0, 'utf8').replace(/^\uFEFF/, ''));
const scene = input.scene || input;
const runtime = new PhysicsRuntime();
try {
  await runtime.load(scene);
  if (runtime.scene.subtype !== 'pendulum') throw new Error('This benchmark bridge supports pendulum only');
  const snapshot = () => {
    const kernel = runtime.adapter.physicsKernel;
    if (kernel.simTime !== 0) throw new Error('Expected an unstepped t=0 kernel');
    const geometry = { pivot: kernel.pivot, string_length_px: kernel.stringLengthPx };
    const bob = PendulumSimulation.prototype.getBobSourcePosition.call({ geometry, theta: kernel.theta });
    return {
      time_s: kernel.simTime,
      theta_rad: kernel.theta,
      landmarks: { pivot: { ...kernel.pivot }, bob },
      lines: { string: { start: { ...kernel.pivot }, end: bob } },
    };
  };
  const initial = snapshot();
  // Physical-parameter perturbation, not a fixture-coordinate offset.
  runtime.updateParameter({ key: 'initialAngle', value: initial.theta_rad * 180 / Math.PI + 30, unit: 'deg' });
  const perturbed = snapshot();
  if (Math.abs(perturbed.theta_rad - initial.theta_rad - Math.PI / 6) > 1e-9) {
    throw new Error('Runtime did not apply the requested 30 degree control');
  }
  process.stdout.write(JSON.stringify({ initial, perturbed }));
} finally {
  runtime.dispose();
}

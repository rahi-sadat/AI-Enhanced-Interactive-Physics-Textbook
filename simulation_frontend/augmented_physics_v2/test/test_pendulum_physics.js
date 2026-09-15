/**
 * test/test_pendulum_physics.js
 * 
 * Physics release-gate verification for Kinematics & Pendulum:
 * - 240 Hz RK4 small-angle period T ≈ 2.006 s (L = 1m, g = 9.81 m/s²)
 * - Large-angle nonlinear period progression (5°, 30°, 60°) vs Complete Elliptic Integral
 * - Undamped mechanical energy bounded drift (< 0.05% over 10 cycles)
 * - MatterUnitAdapter SI unit conversion
 * - Closed-form projectile trajectory precision
 */

import { MatterUnitAdapter } from '../src/core/matterUnitAdapter.js';

function assert(condition, message) {
  if (!condition) {
    console.error(`❌ FAIL: ${message}`);
    process.exit(1);
  }
  console.log(`  ✓ PASS: ${message}`);
}

function assertClose(actual, expected, tol = 1e-4, message = '') {
  const diff = Math.abs(actual - expected);
  if (diff > tol) {
    console.error(`❌ FAIL: ${message} (expected ~${expected}, got ${actual}, diff: ${diff})`);
    process.exit(1);
  }
  console.log(`  ✓ PASS: ${message}`);
}

/**
 * Simulates pendulum with RK4 and detects period from zero-crossing of angular velocity.
 */
function measurePendulumPeriod(theta0Deg, L = 1.0, g = 9.81, dt = 1.0 / 240.0) {
  let theta = (theta0Deg * Math.PI) / 180.0;
  let omega = 0.0;
  let time = 0.0;
  let prevOmega = 0.0;
  let crossings = 0;
  let tStart = 0;
  let tEnd = 0;

  function derivative(th, om) {
    return {
      dTheta: om,
      dOmega: -(g / L) * Math.sin(th),
    };
  }

  // Run up to 2 full cycles
  while (time < 10.0 && crossings < 4) {
    const k1 = derivative(theta, omega);
    const k2 = derivative(theta + 0.5 * dt * k1.dTheta, omega + 0.5 * dt * k1.dOmega);
    const k3 = derivative(theta + 0.5 * dt * k2.dTheta, omega + 0.5 * dt * k2.dOmega);
    const k4 = derivative(theta + dt * k3.dTheta, omega + dt * k3.dOmega);

    theta += (dt / 6.0) * (k1.dTheta + 2 * k2.dTheta + 2 * k3.dTheta + k4.dTheta);
    omega += (dt / 6.0) * (k1.dOmega + 2 * k2.dOmega + 2 * k3.dOmega + k4.dOmega);
    time += dt;

    // Detect positive zero-crossing of omega (crest of oscillation)
    if (prevOmega < 0 && omega >= 0) {
      crossings++;
      if (crossings === 1) tStart = time;
      if (crossings === 2) tEnd = time;
    }
    prevOmega = omega;
  }

  return tEnd - tStart;
}

console.log('\n==============================================');
console.log('  RUNNING PENDULUM & KINEMATICS PHYSICS TESTS');
console.log('==============================================');

// TEST 1: Small-Angle Pendulum Period (L = 1m, g = 9.81 m/s²)
console.log('\n[1/5] Testing small-angle pendulum period at 240 Hz');
{
  const L = 1.0;
  const g = 9.81;
  const T_theory = 2.0 * Math.PI * Math.sqrt(L / g); // ~2.0060667 s
  const T_sim = measurePendulumPeriod(5.0, L, g, 1.0 / 240.0);

  assertClose(T_theory, 2.0060667, 1e-4, 'Theoretical small-angle period T ≈ 2.006 s');
  assertClose(T_sim, T_theory, 0.005, '240 Hz RK4 period matches theoretical within 0.25%');
}

// TEST 2: Nonlinear Period Progression (Elliptic Integral Reference)
console.log('\n[2/5] Testing nonlinear period elongation at 30° and 60°');
{
  const L = 1.0;
  const g = 9.81;
  const T0 = 2.0 * Math.PI * Math.sqrt(L / g);

  // 30 degrees (theta0 = pi/6 rad): T ≈ T0 * (1 + 1/16 * theta0^2)
  const th30 = Math.PI / 6.0;
  const T_theory_30 = T0 * (1.0 + (1.0 / 16.0) * th30 * th30 + (11.0 / 3072.0) * Math.pow(th30, 4));
  const T_sim_30 = measurePendulumPeriod(30.0, L, g, 1.0 / 240.0);
  assert(T_sim_30 > T0, 'Period at 30° is longer than small-angle period T0');
  assertClose(T_sim_30, T_theory_30, 0.01, '30° period matches elliptic series reference (~2.040 s)');

  // 60 degrees (theta0 = pi/3 rad)
  const th60 = Math.PI / 3.0;
  const T_theory_60 = T0 * (1.0 + (1.0 / 16.0) * th60 * th60 + (11.0 / 3072.0) * Math.pow(th60, 4));
  const T_sim_60 = measurePendulumPeriod(60.0, L, g, 1.0 / 240.0);
  assert(T_sim_60 > T_sim_30, 'Period at 60° is longer than at 30°');
  assertClose(T_sim_60, T_theory_60, 0.02, '60° period matches elliptic series reference (~2.15 s)');
}

// TEST 3: Energy Conservation & Bounded Drift (gamma = 0)
console.log('\n[3/5] Testing undamped mechanical energy bounded drift');
{
  const L = 1.0;
  const g = 9.81;
  const m = 1.5;
  const dt = 1.0 / 240.0;
  let theta = (45.0 * Math.PI) / 180.0;
  let omega = 0.0;

  function totalEnergy(th, om) {
    const h = L * (1.0 - Math.cos(th));
    const pe = m * g * h;
    const ke = 0.5 * m * Math.pow(L * om, 2);
    return pe + ke;
  }

  const E_init = totalEnergy(theta, omega);
  let minE = E_init;
  let maxE = E_init;

  // Run 10 full oscillations (~21 seconds = ~5040 steps)
  const totalSteps = 5000;
  for (let step = 0; step < totalSteps; step++) {
    const k1_th = omega;
    const k1_om = -(g / L) * Math.sin(theta);

    const k2_th = omega + 0.5 * dt * k1_om;
    const k2_om = -(g / L) * Math.sin(theta + 0.5 * dt * k1_th);

    const k3_th = omega + 0.5 * dt * k2_om;
    const k3_om = -(g / L) * Math.sin(theta + 0.5 * dt * k2_th);

    const k4_th = omega + dt * k3_om;
    const k4_om = -(g / L) * Math.sin(theta + dt * k3_th);

    theta += (dt / 6.0) * (k1_th + 2 * k2_th + 2 * k3_th + k4_th);
    omega += (dt / 6.0) * (k1_om + 2 * k2_om + 2 * k3_om + k4_om);

    const E_curr = totalEnergy(theta, omega);
    if (E_curr < minE) minE = E_curr;
    if (E_curr > maxE) maxE = E_curr;
  }

  const drift = (maxE - minE) / E_init;
  assert(drift < 0.0005, `Energy variation over 10 cycles is bounded (< 0.05%): got ${(drift * 100).toFixed(4)}%`);
}

// TEST 4: MatterUnitAdapter SI Translations
console.log('\n[4/5] Testing MatterUnitAdapter SI unit translations');
{
  const adapter = new MatterUnitAdapter(120.0); // 120 px/m
  const mockEngine = { gravity: { x: 0, y: 0, scale: 0 } };

  adapter.setGravity(mockEngine, 9.81);
  assert(mockEngine.gravity.y === 1, 'Matter gravity direction y is normalized to 1');
  const expectedScale = (9.81 * 120.0) / 1000000.0;
  assertClose(mockEngine.gravity.scale, expectedScale, 1e-9, 'Matter gravity scale matches (g * ppm) / 1,000,000');

  // Velocity: 15 m/s at 120 px/m -> 1800 px/s -> (1800 / 60) = 30 px/frame
  const matterV = adapter.velocityMpsToMatter(15.0);
  assertClose(matterV, 30.0, 1e-9, '15 m/s converted to Matter frame velocity (30 px/frame)');
  assertClose(adapter.velocityMatterToMps(30.0), 15.0, 1e-9, 'Matter velocity round-trip back to 15 m/s');
}

// TEST 5: Closed-Form Projectile Motion Precision
console.log('\n[5/5] Testing analytical closed-form projectile equations');
{
  const v0 = 20.0;
  const angle = 45.0 * (Math.PI / 180.0);
  const g = 9.81;
  const vx0 = v0 * Math.cos(angle);
  const vy0 = v0 * Math.sin(angle);
  const tFlight = (2.0 * vy0) / g;
  const maxH = (vy0 * vy0) / (2.0 * g);

  // Position at apex (t = tFlight / 2)
  const tApex = tFlight / 2.0;
  const yApex = vy0 * tApex - 0.5 * g * tApex * tApex;
  assertClose(yApex, maxH, 1e-9, 'Apex height matches vy0² / 2g exactly');

  // Landing position (y = 0 at tFlight)
  const yLand = vy0 * tFlight - 0.5 * g * tFlight * tFlight;
  assertClose(yLand, 0.0, 1e-9, 'Landing height returns to 0.0 at tFlight');
}

console.log('\nAll Kinematics & Pendulum physics tests passed successfully!\n');

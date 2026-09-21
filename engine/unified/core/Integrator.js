/**
 * Integrator.js
 * 
 * Symplectic Semi-Implicit Euler numerical integrator for dynamic systems.
 * 
 * Formulations:
 *   v_{t + dt} = v_t + dt * M^{-1} * F(q_t, v_t)
 *   q_{t + dt} = q_t + dt * v_{t + dt}
 * 
 * Symplectic nature preserves phase-space area and guarantees bounded
 * energy behavior over long simulation horizons, replacing ad-hoc integrators.
 */

export class Integrator {
  /**
   * Advances generalized coordinates q and velocities v by timestep dt.
   * 
   * @param {object} params
   * @param {Float64Array} params.q - Generalized positions/coordinates (length n)
   * @param {Float64Array} params.v - Generalized velocities (length n)
   * @param {Float64Array|number[]} params.invMass - Inverse mass array M^{-1} (length n)
   * @param {Function} params.forceFn - Evaluates generalized forces F(q, v) -> Float64Array of length n
   * @param {number} params.dt - Timestep in seconds
   * @param {Function} [params.constraintProjectionFn] - Optional post-step projection to eliminate drift C(q) = 0
   * @returns {{ q: Float64Array, v: Float64Array }}
   */
  static stepSemiImplicit({
    q,
    v,
    invMass,
    forceFn,
    dt,
    constraintProjectionFn = null
  }) {
    const n = q.length;
    const nextQ = new Float64Array(n);
    const nextV = new Float64Array(n);

    // 1. Evaluate total forces at current state
    const forces = forceFn(q, v);

    // 2. Velocity update: v_{t+dt} = v_t + dt * (F / m)
    for (let i = 0; i < n; i++) {
      const a = forces[i] * invMass[i];
      nextV[i] = v[i] + dt * a;
    }

    // 3. Position update using new velocity: q_{t+dt} = q_t + dt * v_{t+dt}
    for (let i = 0; i < n; i++) {
      nextQ[i] = q[i] + dt * nextV[i];
    }

    // 4. Optional algebraic constraint projection (Baumgarte / coordinate projection)
    if (typeof constraintProjectionFn === 'function') {
      const projected = constraintProjectionFn(nextQ, nextV);
      if (projected?.q) nextQ.set(projected.q);
      if (projected?.v) nextV.set(projected.v);
    }

    return { q: nextQ, v: nextV };
  }
}

/**
 * NewtonRaphson.js
 * 
 * Domain-agnostic multi-dimensional Newton-Raphson root finder and equation solver.
 * Solves F(x) = 0 using direct Jacobian linear solves J * dx = -F(x)
 * with backtracking line search for global convergence.
 */

import { LinearSolver } from './LinearSolver.js';

export class NewtonRaphson {
  /**
   * Solves F(x) = 0 starting from initial guess x0.
   * 
   * @param {object} options
   * @param {Float64Array|number[]} options.initialGuess - Initial vector x0
   * @param {Function} options.residualFn - Computes F(x) -> Float64Array or number[] of same length
   * @param {Function} [options.jacobianFn] - Optional analytical Jacobian J(x) -> Float64Array (flat n x n)
   * @param {number} [options.tol=1e-10] - Residual infinity norm convergence threshold
   * @param {number} [options.maxIterations=50] - Maximum allowable iterations
   * @param {number} [options.finiteDiffStep=1e-7] - Perturbation step h for numerical Jacobian
   * @param {boolean} [options.lineSearch=true] - Enable Armijo-type backtracking line search
   * @returns {{ converged: boolean, x: Float64Array, iterations: number, residualNorm: number }}
   */
  static solve({
    initialGuess,
    residualFn,
    jacobianFn = null,
    tol = 1e-10,
    maxIterations = 50,
    finiteDiffStep = 1e-7,
    lineSearch = true
  }) {
    const n = initialGuess.length;
    let x = new Float64Array(initialGuess);

    let fx = new Float64Array(residualFn(x));
    let normF = this.infinityNorm(fx);

    if (normF < tol) {
      return { converged: true, x, iterations: 0, residualNorm: normF };
    }

    for (let iter = 1; iter <= maxIterations; iter++) {
      // 1. Assemble Jacobian J
      let J;
      if (typeof jacobianFn === 'function') {
        J = jacobianFn(x);
      } else {
        J = this.computeNumericalJacobian(residualFn, x, fx, n, finiteDiffStep);
      }

      // 2. Prepare -F(x)
      const negF = new Float64Array(n);
      for (let i = 0; i < n; i++) negF[i] = -fx[i];

      // 3. Solve J * dx = -F(x)
      let dx;
      try {
        dx = LinearSolver.solve(J, negF);
      } catch (err) {
        return {
          converged: false,
          x,
          iterations: iter,
          residualNorm: normF,
          error: `Jacobian singular at iteration ${iter}: ${err.message}`
        };
      }

      const normDx = this.infinityNorm(dx);
      if (normDx < tol) {
        return { converged: true, x, iterations: iter, residualNorm: normF };
      }

      // 4. Update x with optional backtracking line search
      let alpha = 1.0;
      let nextX = new Float64Array(n);
      let nextF;
      let nextNorm = Infinity;

      if (lineSearch) {
        // Backtracking line search
        let stepAccepted = false;
        for (let attempt = 0; attempt < 8; attempt++) {
          for (let i = 0; i < n; i++) {
            nextX[i] = x[i] + alpha * dx[i];
          }
          nextF = new Float64Array(residualFn(nextX));
          nextNorm = this.infinityNorm(nextF);

          if (nextNorm < normF || nextNorm < tol) {
            stepAccepted = true;
            break;
          }
          alpha *= 0.5;
        }

        if (!stepAccepted) {
          // If line search failed to strictly decrease, take the full Newton step
          for (let i = 0; i < n; i++) nextX[i] = x[i] + dx[i];
          nextF = new Float64Array(residualFn(nextX));
          nextNorm = this.infinityNorm(nextF);
        }
      } else {
        for (let i = 0; i < n; i++) nextX[i] = x[i] + dx[i];
        nextF = new Float64Array(residualFn(nextX));
        nextNorm = this.infinityNorm(nextF);
      }

      x = nextX;
      fx = nextF;
      normF = nextNorm;

      if (normF < tol) {
        return { converged: true, x, iterations: iter, residualNorm: normF };
      }
    }

    return {
      converged: normF < tol,
      x,
      iterations: maxIterations,
      residualNorm: normF
    };
  }

  /**
   * Computes numerical Jacobian using central difference:
   * J_ij = (F_i(x + h e_j) - F_i(x - h e_j)) / (2h)
   * @param {Function} residualFn
   * @param {Float64Array} x
   * @param {Float64Array} fx
   * @param {number} n
   * @param {number} h
   * @returns {Float64Array} Flat n x n matrix
   */
  static computeNumericalJacobian(residualFn, x, fx, n, h = 1e-7) {
    const J = new Float64Array(n * n);
    const xPlus = new Float64Array(x);
    const xMinus = new Float64Array(x);

    for (let j = 0; j < n; j++) {
      const orig = x[j];
      const step = h * Math.max(1.0, Math.abs(orig));

      xPlus[j] = orig + step;
      xMinus[j] = orig - step;

      const fPlus = residualFn(xPlus);
      const fMinus = residualFn(xMinus);

      const denom = 2.0 * step;
      for (let i = 0; i < n; i++) {
        J[i * n + j] = (fPlus[i] - fMinus[i]) / denom;
      }

      xPlus[j] = orig;
      xMinus[j] = orig;
    }

    return J;
  }

  /**
   * Computes infinity norm (max absolute value) of a vector.
   * @param {Float64Array|number[]} vec
   * @returns {number}
   */
  static infinityNorm(vec) {
    let max = 0.0;
    for (let i = 0; i < vec.length; i++) {
      const abs = Math.abs(vec[i]);
      if (abs > max) max = abs;
    }
    return max;
  }
}

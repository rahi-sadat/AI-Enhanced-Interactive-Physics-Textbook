/**
 * circuits/LinearSystem.js
 * High-precision numerical linear algebra solver delegating to the unified LinearSolver core.
 * Physical Law: Solves Modified Nodal Analysis (MNA) system A * x = z via LU Decomposition with Partial Pivoting.
 */

import { LinearSolver } from '../unified/core/LinearSolver.js';

export class LinearSystem {
  /**
   * Solve A * x = z using LU Decomposition with Partial Pivoting.
   * @param {number} n - Matrix dimension
   * @param {Float64Array} A - Row-major matrix of size n x n
   * @param {Float64Array} z - RHS vector of length n
   * @param {number} [tol=1e-14] - Singularity tolerance
   * @returns {Float64Array} Solution vector x of length n
   */
  static solve(n, A, z, tol = 1e-14) {
    if (n <= 0) return new Float64Array(0);
    return LinearSolver.solve(A, z, tol);
  }

  /**
   * Helper to allocate and format a dense MNA matrix.
   */
  static createMatrix(size) {
    return new Float64Array(size * size);
  }

  /**
   * Helper to allocate a vector.
   */
  static createVector(size) {
    return new Float64Array(size);
  }
}

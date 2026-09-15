/**
 * circuits/LinearSystem.js
 * High-precision numerical linear algebra solver on Float64Array.
 * Implements LU Decomposition with Partial Pivoting for Modified Nodal Analysis (MNA).
 */

export class LinearSystem {
  /**
   * Solve A * x = z using LU Decomposition with Partial Pivoting.
   * @param {number} n - Matrix dimension
   * @param {Float64Array} A - Row-major matrix of size n x n (will be copied)
   * @param {Float64Array} z - RHS vector of length n (will be copied)
   * @param {number} [tol=1e-14] - Singularity tolerance
   * @returns {Float64Array} Solution vector x of length n
   */
  static solve(n, A, z, tol = 1e-14) {
    if (n <= 0) return new Float64Array(0);

    // Working copies
    const lu = new Float64Array(A);
    const b = new Float64Array(z);
    const piv = new Int32Array(n);

    // Initialize pivot indices
    for (let i = 0; i < n; i++) piv[i] = i;

    // --- LU Decomposition with Partial Pivoting ---
    for (let j = 0; j < n; j++) {
      // Find pivot in column j (from row j downward)
      let maxVal = 0.0;
      let maxRow = j;
      for (let i = j; i < n; i++) {
        const val = Math.abs(lu[i * n + j]);
        if (val > maxVal) {
          maxVal = val;
          maxRow = i;
        }
      }

      if (maxVal < tol) {
        throw new Error(
          `Circuit matrix is singular or ill-conditioned at index ${j} (pivot: ${maxVal.toExponential(2)}). ` +
          `Check for floating nodes, shorted ideal voltage sources, or open circuit branches.`
        );
      }

      // Swap rows if necessary
      if (maxRow !== j) {
        // Swap rows in LU
        for (let k = 0; k < n; k++) {
          const tmp = lu[j * n + k];
          lu[j * n + k] = lu[maxRow * n + k];
          lu[maxRow * n + k] = tmp;
        }
        // Swap pivot tracker
        const tmpPiv = piv[j];
        piv[j] = piv[maxRow];
        piv[maxRow] = tmpPiv;
      }

      // Compute multipliers for rows below pivot
      const pivotVal = lu[j * n + j];
      for (let i = j + 1; i < n; i++) {
        lu[i * n + j] /= pivotVal;
        const mult = lu[i * n + j];
        for (let k = j + 1; k < n; k++) {
          lu[i * n + k] -= mult * lu[j * n + k];
        }
      }
    }

    // --- Forward Substitution: L * y = P * z ---
    const y = new Float64Array(n);
    for (let i = 0; i < n; i++) {
      let sum = b[piv[i]];
      for (let k = 0; k < i; k++) {
        sum -= lu[i * n + k] * y[k];
      }
      y[i] = sum;
    }

    // --- Back Substitution: U * x = y ---
    const x = new Float64Array(n);
    for (let i = n - 1; i >= 0; i--) {
      let sum = y[i];
      for (let k = i + 1; k < n; k++) {
        sum -= lu[i * n + k] * x[k];
      }
      x[i] = sum / lu[i * n + i];
    }

    return x;
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

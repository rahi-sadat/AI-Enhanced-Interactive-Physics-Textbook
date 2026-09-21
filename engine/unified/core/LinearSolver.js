/**
 * LinearSolver.js
 * 
 * High-performance direct linear system solver (A * x = b) using
 * LU Decomposition with Partial Row Pivoting (PA = LU).
 * Implemented on native Float64Array with zero external dependencies.
 */

export class LinearSolver {
  /**
   * Solves A * x = b for x.
   * @param {Float64Array|number[][]|number[]} A - Matrix of dimension n x n (flat 1D or 2D array)
   * @param {Float64Array|number[]} b - Right-hand side vector of length n
   * @param {number} [tol=1e-14] - Numeric singularity tolerance
   * @returns {Float64Array} Solution vector x of length n
   */
  static solve(A, b, tol = 1e-14) {
    const n = b.length;
    const { LU, piv } = this.decompose(A, n, tol);
    return this.solveFromLU(LU, piv, b, n);
  }

  /**
   * Performs in-place Doolittle LU decomposition with partial row pivoting.
   * P * A = L * U
   * @param {Float64Array|number[][]|number[]} A - n x n matrix
   * @param {number} n - Dimension
   * @param {number} tol - Singularity threshold
   * @returns {{ LU: Float64Array, piv: Int32Array, detSign: number }}
   */
  static decompose(A, n, tol = 1e-14) {
    const LU = new Float64Array(n * n);

    // Copy A into flat row-major Float64Array
    if (Array.isArray(A) && Array.isArray(A[0])) {
      for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
          LU[i * n + j] = A[i][j];
        }
      }
    } else {
      for (let k = 0; k < n * n; k++) {
        LU[k] = A[k];
      }
    }

    const piv = new Int32Array(n);
    for (let i = 0; i < n; i++) piv[i] = i;
    let detSign = 1;

    for (let j = 0; j < n; j++) {
      // Find pivot element in column j
      let maxVal = Math.abs(LU[j * n + j]);
      let maxRow = j;
      for (let i = j + 1; i < n; i++) {
        const val = Math.abs(LU[i * n + j]);
        if (val > maxVal) {
          maxVal = val;
          maxRow = i;
        }
      }

      if (maxVal < tol) {
        throw new Error(`[LinearSolver] Singular or ill-conditioned matrix: pivot at column ${j} is ~0 (maxVal = ${maxVal.toExponential(4)})`);
      }

      // Swap rows in LU and piv if necessary
      if (maxRow !== j) {
        for (let k = 0; k < n; k++) {
          const tmp = LU[j * n + k];
          LU[j * n + k] = LU[maxRow * n + k];
          LU[maxRow * n + k] = tmp;
        }
        const tmpP = piv[j];
        piv[j] = piv[maxRow];
        piv[maxRow] = tmpP;
        detSign = -detSign;
      }

      // Elimination
      const pivotVal = LU[j * n + j];
      for (let i = j + 1; i < n; i++) {
        LU[i * n + j] /= pivotVal;
        const multiplier = LU[i * n + j];
        for (let k = j + 1; k < n; k++) {
          LU[i * n + k] -= multiplier * LU[j * n + k];
        }
      }
    }

    return { LU, piv, detSign };
  }

  /**
   * Solves A * x = b given precomputed LU decomposition and pivot vector.
   * L * y = P * b (forward substitution)
   * U * x = y     (back substitution)
   * @param {Float64Array} LU
   * @param {Int32Array} piv
   * @param {Float64Array|number[]} b
   * @param {number} n
   * @returns {Float64Array}
   */
  static solveFromLU(LU, piv, b, n) {
    const x = new Float64Array(n);

    // Forward substitution: L * y = P * b (L has unit diagonal)
    for (let i = 0; i < n; i++) {
      let sum = b[piv[i]];
      for (let k = 0; k < i; k++) {
        sum -= LU[i * n + k] * x[k];
      }
      x[i] = sum;
    }

    // Back substitution: U * x = y
    for (let i = n - 1; i >= 0; i--) {
      let sum = x[i];
      for (let k = i + 1; k < n; k++) {
        sum -= LU[i * n + k] * x[k];
      }
      x[i] = sum / LU[i * n + i];
    }

    return x;
  }

  /**
   * Computes determinant of matrix A.
   * @param {Float64Array|number[][]|number[]} A
   * @param {number} n
   * @returns {number}
   */
  static determinant(A, n) {
    try {
      const { LU, detSign } = this.decompose(A, n);
      let det = detSign;
      for (let i = 0; i < n; i++) {
        det *= LU[i * n + i];
      }
      return det;
    } catch (_) {
      return 0.0;
    }
  }
}

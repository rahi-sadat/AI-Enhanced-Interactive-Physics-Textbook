/**
 * apps/web/src/features/simulations/core/SimulationApi.js
 *
 * Typed client for AugmentedPhysics backend endpoints:
 *   - POST /api/ingest (multipart/form-data upload -> Grounded BookIR)
 *   - POST /api/resolution/review (ReviewState & blockers analysis)
 *   - POST /api/resolution/resolve (Apply candidate confirmation, policy, or user value)
 *   - POST /api/resolution/evaluate (Evaluate compilation readiness invariant)
 *   - POST /api/resolution/compile (Gated compile -> Canonical PhysicsScene)
 *   - GET  /api/ingest/health (Pipeline capabilities check)
 *
 * Enforces zero client-side parameter fabrication:
 * Backend remains the sole authoritative source of physics validation and compilation readiness.
 */

export class CompilationGatingError extends Error {
  /**
   * @param {string} message
   * @param {Array<string>} blockers
   * @param {string} status
   */
  constructor(message, blockers = [], status = 'NEEDS_REVIEW') {
    super(message);
    this.name = 'CompilationGatingError';
    this.blockers = blockers;
    this.status = status;
  }
}

export class SimulationApi {
  /**
   * Ingests an image file through POST /api/ingest.
   *
   * @param {File|Blob} file - Binary image file.
   * @param {function(string, number): void} [onProgress]
   * @returns {Promise<object>} Ingestion envelope
   */
  static async ingest(file, onProgress = () => {}) {
    if (!file || (!(file instanceof File) && !(file instanceof Blob))) {
      throw new TypeError('[SimulationApi] ingest() requires a File or Blob object');
    }

    onProgress('Uploading diagram bytes to server...', 20);

    const formData = new FormData();
    formData.append('file', file);

    let res;
    try {
      res = await fetch('/api/ingest', {
        method: 'POST',
        body: formData,
      });
    } catch (networkErr) {
      if (networkErr.message === 'Failed to fetch' || networkErr.name === 'TypeError') {
        throw new Error('Backend server is offline (port 8000). Please ensure the FastAPI backend is running.');
      }
      throw new Error(`Network error during ingestion: ${networkErr.message}`);
    }

    if (!res.ok) {
      let detail = `Server returned HTTP ${res.status}`;
      try {
        const errBody = await res.json();
        detail = errBody.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    onProgress('Processing AI analysis & evidence grounding...', 70);
    const data = await res.json();
    onProgress('Analysis complete', 100);

    return data;
  }

  /**
   * Requests deterministic review analysis for a grounded BookIR.
   *
   * @param {object} bookIR
   * @returns {Promise<{success: boolean, reviewState: object, readyToCompile: boolean, blockersCount: number, warningsCount: number}>}
   */
  static async review(bookIR) {
    if (!bookIR) {
      throw new TypeError('[SimulationApi] review() requires a bookIR object');
    }

    const res = await this._postJson('/api/resolution/review', { book_ir: bookIR });
    return {
      success: Boolean(res.success),
      reviewState: res.review_state || {},
      readyToCompile: Boolean(res.ready_to_compile),
      blockersCount: Number(res.blockers_count || 0),
      warningsCount: Number(res.warnings_count || 0),
    };
  }

  /**
   * Applies an explicit resolution decision (user value or manual correction).
   *
   * @param {object} bookIR
   * @param {object} resolution - { parameterName, resolvedValue, canonicalUnit, resolutionSource, ... }
   * @returns {Promise<{success: boolean, bookIR: object, canCompile: boolean, readinessReport: object, resolvedValue: any}>}
   */
  static async resolve(bookIR, resolution) {
    if (!bookIR || !resolution) {
      throw new TypeError('[SimulationApi] resolve() requires bookIR and resolution');
    }

    const payload = {
      book_ir: bookIR,
      resolution: {
        parameterName: resolution.parameterName || resolution.parameter_name,
        resolvedValue: resolution.resolvedValue !== undefined ? resolution.resolvedValue : resolution.value,
        canonicalUnit: resolution.canonicalUnit || resolution.unit || null,
        originalEnteredValue: resolution.originalEnteredValue || resolution.rawInput || String(resolution.resolvedValue),
        resolutionSource: resolution.resolutionSource || resolution.source || 'user_supplied',
        notes: resolution.notes || 'Resolved via student review UI',
      },
    };

    const res = await this._postJson('/api/resolution/resolve', payload);
    return {
      success: Boolean(res.success),
      bookIR: res.book_ir,
      canCompile: Boolean(res.can_compile),
      readinessReport: res.readiness_report || null,
      resolvedValue: res.resolvedValue,
      raw: res,
    };
  }

  /**
   * Confirms an evidence-backed candidate (e.g. from OCR).
   *
   * @param {object} bookIR
   * @param {string} parameterName
   * @param {object} candidate
   * @returns {Promise<{success: boolean, bookIR: object, canCompile: boolean, readinessReport: object}>}
   */
  static async confirmCandidate(bookIR, parameterName, candidate) {
    if (!bookIR || !parameterName || !candidate) {
      throw new TypeError('[SimulationApi] confirmCandidate() requires bookIR, parameterName, and candidate');
    }

    const payload = {
      book_ir: bookIR,
      parameter_name: parameterName,
      confirm_candidate: candidate,
    };

    const res = await this._postJson('/api/resolution/resolve', payload);
    return {
      success: Boolean(res.success),
      bookIR: res.book_ir,
      canCompile: Boolean(res.can_compile),
      readinessReport: res.readiness_report || null,
      raw: res,
    };
  }

  /**
   * Applies an explicit named default policy (e.g. policy_earth_gravity).
   *
   * @param {object} bookIR
   * @param {string} policyId
   * @param {string} [parameterName]
   * @returns {Promise<{success: boolean, bookIR: object, canCompile: boolean, readinessReport: object}>}
   */
  static async applyPolicy(bookIR, policyId, parameterName = null) {
    if (!bookIR || !policyId) {
      throw new TypeError('[SimulationApi] applyPolicy() requires bookIR and policyId');
    }

    const payload = {
      book_ir: bookIR,
      policy_id: policyId,
    };
    if (parameterName) {
      payload.parameter_name = parameterName;
    }

    const res = await this._postJson('/api/resolution/resolve', payload);
    return {
      success: Boolean(res.success),
      bookIR: res.book_ir,
      canCompile: Boolean(res.can_compile),
      readinessReport: res.readiness_report || null,
      raw: res,
    };
  }

  /**
   * Removes a previously applied resolution or policy, returning BookIR to NEEDS_REVIEW.
   *
   * @param {object} bookIR
   * @param {string} parameterName
   * @returns {Promise<{success: boolean, bookIR: object, canCompile: boolean, parameterName: string}>}
   */
  static async removeResolution(bookIR, parameterName) {
    if (!bookIR || !parameterName) {
      throw new TypeError('[SimulationApi] removeResolution() requires bookIR and parameterName');
    }

    const payload = {
      book_ir: bookIR,
      remove_parameter: parameterName,
    };

    const res = await this._postJson('/api/resolution/resolve', payload);
    return {
      success: Boolean(res.success),
      bookIR: res.book_ir,
      canCompile: Boolean(res.can_compile),
      parameterName: res.parameter_name,
      readinessReport: res.readiness_report || null,
      raw: res,
    };
  }

  /**
   * Evaluates compilation readiness invariant without mutating parameters.
   *
   * @param {object} bookIR
   * @returns {Promise<{success: boolean, readinessReport: object, bookIR: object, canCompile: boolean}>}
   */
  static async evaluate(bookIR) {
    if (!bookIR) {
      throw new TypeError('[SimulationApi] evaluate() requires bookIR');
    }

    const res = await this._postJson('/api/resolution/evaluate', { book_ir: bookIR });
    return {
      success: Boolean(res.success),
      readinessReport: res.readiness_report || {},
      bookIR: res.book_ir,
      canCompile: Boolean(res.can_compile),
    };
  }

  /**
   * Compiles legitimately resolved BookIR into a Canonical PhysicsScene.
   * Throws CompilationGatingError if BookIR is not ready to compile.
   *
   * @param {object} bookIR
   * @returns {Promise<{success: boolean, compiler: object, scene: object, bookIR: object}>}
   */
  static async compile(bookIR) {
    if (!bookIR) {
      throw new TypeError('[SimulationApi] compile() requires bookIR');
    }

    let res;
    try {
      res = await fetch('/api/resolution/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ book_ir: bookIR }),
      });
    } catch (networkErr) {
      throw new Error(`Network error during compilation: ${networkErr.message}`);
    }

    if (!res.ok) {
      let detailMsg = `Compilation rejected (HTTP ${res.status})`;
      let blockers = [];
      let status = 'NEEDS_REVIEW';

      try {
        const errJson = await res.json();
        if (typeof errJson.detail === 'object' && errJson.detail !== null) {
          detailMsg = errJson.detail.message || detailMsg;
          blockers = errJson.detail.blockers || [];
          status = errJson.detail.status || status;
        } else if (typeof errJson.detail === 'string') {
          detailMsg = errJson.detail;
        }
      } catch (_) {}

      throw new CompilationGatingError(detailMsg, blockers, status);
    }

    const data = await res.json();
    return {
      success: Boolean(data.success),
      compiler: data.compiler || {},
      scene: data.scene || null,
      bookIR: data.book_ir || bookIR,
    };
  }

  /**
   * Checks health and capabilities of the ingestion and resolution pipeline.
   *
   * @returns {Promise<object>}
   */
  static async checkHealth() {
    try {
      const res = await fetch('/api/ingest/health');
      if (!res.ok) return { available: false, status: res.status };
      return await res.json();
    } catch (err) {
      return { available: false, error: err.message };
    }
  }

  /**
   * Helper for POST JSON requests with error handling.
   * @private
   */
  static async _postJson(url, payload) {
    let res;
    try {
      res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (networkErr) {
      throw new Error(`Network error connecting to ${url}: ${networkErr.message}`);
    }

    if (!res.ok) {
      let detail = `Endpoint ${url} failed with HTTP ${res.status}`;
      try {
        const errJson = await res.json();
        detail = errJson.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    return await res.json();
  }
}

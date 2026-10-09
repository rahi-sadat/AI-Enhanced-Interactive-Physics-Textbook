/**
 * apps/web/src/features/simulations/core/SimulationOrchestrator.js
 *
 * Deterministic client-side lifecycle orchestrator for an analyzed physics figure session.
 * Coordinates:
 *   IDLE -> UPLOADING -> ANALYZING -> [NEEDS_REVIEW <-> APPLYING_RESOLUTION <-> EVALUATING]
 *        -> READY_TO_COMPILE -> COMPILING -> READY_TO_SIMULATE -> SIMULATING
 *
 * INVARIANTS:
 *   1. Backend is authoritative: Browser NEVER marks BookIR as READY_TO_COMPILE on its own.
 *   2. Zero parameter fabrication: Browser NEVER injects default physics constants.
 *   3. BookIR immutability on client: Local BookIR is ALWAYS replaced with the backend's
 *      authoritative returned BookIR after every mutation.
 *   4. Compilation and Simulation activation are decoupled:
 *      READY_TO_SIMULATE requires explicit student initiation ("Start Simulation") to enter SIMULATING.
 *   5. Monotonic operation ID guards against stale async race conditions.
 */

import { SimulationApi, CompilationGatingError } from './SimulationApi.js';

export const OrchestratorState = Object.freeze({
  IDLE: 'IDLE',
  UPLOADING: 'UPLOADING',
  ANALYZING: 'ANALYZING',
  NEEDS_REVIEW: 'NEEDS_REVIEW',
  APPLYING_RESOLUTION: 'APPLYING_RESOLUTION',
  EVALUATING: 'EVALUATING',
  READY_TO_COMPILE: 'READY_TO_COMPILE',
  COMPILING: 'COMPILING',
  READY_TO_SIMULATE: 'READY_TO_SIMULATE',
  SIMULATING: 'SIMULATING',
  ERROR: 'ERROR',
  UNSUPPORTED: 'UNSUPPORTED',
});

export class SimulationOrchestrator {
  /**
   * @param {object} [options={}]
   * @param {typeof SimulationApi} [options.api=SimulationApi]
   */
  constructor(options = {}) {
    this.api = options.api || SimulationApi;

    this.state = OrchestratorState.IDLE;
    this.sourceAsset = null;
    this.imageUrl = '';
    this.pageIR = null;
    this.bookIR = null;
    this.reviewState = null;
    this.readinessReport = null;
    this.compiledScene = null;
    this.currentError = null;
    this.resolutionHistory = [];

    this._listeners = new Set();
    this._operationId = 0;

    this._metrics = {
      startTime: null,
      timeToReadyMs: null,
      reviewIssuesCount: 0,
      candidateConfirmations: 0,
      candidateCorrections: 0,
      manualValuesEntered: 0,
      policiesAccepted: 0,
      failedResolutions: 0,
    };
  }

  /**
   * Registers a listener for state and context changes.
   * @param {function(string, object): void} callback
   * @returns {function(): void} unsubscribe
   */
  onStateChange(callback) {
    this._listeners.add(callback);
    return () => this._listeners.delete(callback);
  }

  /**
   * Internal transition method.
   * @private
   */
  _setState(nextState, error = null) {
    this.state = nextState;
    if (error !== undefined) {
      this.currentError = error;
    }
    const ctx = this.getSessionContext();
    for (const listener of this._listeners) {
      try {
        listener(this.state, ctx);
      } catch (err) {
        console.error('[SimulationOrchestrator] Listener error:', err);
      }
    }
  }

  /**
   * Returns current figure session context.
   */
  getSessionContext() {
    return {
      state: this.state,
      imageUrl: this.imageUrl,
      sourceAsset: this.sourceAsset,
      bookIR: this.bookIR,
      reviewState: this.reviewState,
      readinessReport: this.readinessReport,
      compiledScene: this.compiledScene,
      currentError: this.currentError,
      resolutionHistory: [...this.resolutionHistory],
      metrics: this.getResearchMetrics(),
    };
  }

  /**
   * Starts orchestration with an uploaded File or Blob.
   *
   * @param {File|Blob} file
   * @param {function(string, number): void} [onProgress]
   */
  async startWithFile(file, onProgress = () => {}) {
    const opId = ++this._operationId;
    this._metrics.startTime = Date.now();
    this._metrics.timeToReadyMs = null;
    this.currentError = null;
    this.compiledScene = null;
    this.resolutionHistory = [];

    this._setState(OrchestratorState.UPLOADING);

    try {
      const ingestData = await this.api.ingest(file, (msg, pct) => {
        if (opId !== this._operationId) return;
        if (pct < 50 && this.state !== OrchestratorState.UPLOADING) {
          this._setState(OrchestratorState.UPLOADING);
        } else if (pct >= 50 && this.state !== OrchestratorState.ANALYZING) {
          this._setState(OrchestratorState.ANALYZING);
        }
        onProgress(msg, pct);
      });

      if (opId !== this._operationId) return;

      if (this.state !== OrchestratorState.ANALYZING) {
        this._setState(OrchestratorState.ANALYZING);
      }

      this.imageUrl = ingestData.image_url || '';
      this.sourceAsset = ingestData.source_asset || null;
      this.pageIR = ingestData.page_ir || null;
      this.bookIR = ingestData.book_ir || null;

      const compilerResult = ingestData.compiler || {};
      const status = (ingestData.status || compilerResult.status || this.bookIR?.status || 'unresolved')
        .toUpperCase()
        .replace('-', '_');

      // 1. Unsupported domain or subtype
      if (status === 'UNSUPPORTED' || this.bookIR?.status === 'UNSUPPORTED') {
        this._setState(
          OrchestratorState.UNSUPPORTED,
          'This physics diagram is not supported yet. AugmentedPhysics currently supports Kinematics (pendulums, projectiles), Geometric Optics (lenses, mirrors, prisms, refraction), and DC Circuits.'
        );
        return;
      }

      // 2. Unresolved without understanding
      if (status === 'UNRESOLVED' && (!this.bookIR?.domain || !this.bookIR?.subtype)) {
        this._setState(
          OrchestratorState.ERROR,
          "We couldn't reliably analyze this diagram. Try a clearer image or review the detected diagram region."
        );
        return;
      }

      // 3. Immediately ready with compiled scene from backend
      if (status === 'READY' && ingestData.scene) {
        this.compiledScene = this._normalizeSceneBackground(ingestData.scene);
        this._metrics.timeToReadyMs = Date.now() - this._metrics.startTime;
        this._setState(OrchestratorState.READY_TO_SIMULATE);
        return;
      }

      // 4. Ingestion returned ready status but no scene -> trigger explicit compile
      if (status === 'READY_TO_COMPILE' || this.bookIR?.status === 'READY_TO_COMPILE') {
        this._setState(OrchestratorState.READY_TO_COMPILE);
        await this.compile();
        return;
      }

      // 5. Normal student path: NEEDS_REVIEW
      if (status === 'NEEDS_REVIEW' || this.bookIR?.status === 'NEEDS_REVIEW' || status === 'UNRESOLVED') {
        await this._fetchReviewAnalysis(opId);
      } else {
        this._setState(
          OrchestratorState.ERROR,
          `Unexpected diagram analysis status: ${status}`
        );
      }
    } catch (err) {
      if (opId !== this._operationId) return;
      console.error('[SimulationOrchestrator] Ingestion error:', err);
      this._setState(OrchestratorState.ERROR, err.message || 'Diagram analysis failed.');
    }
  }

  /**
   * Starts orchestration with an existing grounded BookIR (e.g. for testing or re-review).
   *
   * @param {object} bookIR
   * @param {string} [imageUrl='']
   */
  async startWithBookIR(bookIR, imageUrl = '') {
    const opId = ++this._operationId;
    this._metrics.startTime = Date.now();
    this.bookIR = bookIR;
    this.imageUrl = imageUrl;
    this.compiledScene = null;
    this.currentError = null;

    if (bookIR.status === 'READY_TO_COMPILE') {
      this._setState(OrchestratorState.READY_TO_COMPILE);
      await this.compile();
      return;
    }

    if (bookIR.status === 'UNSUPPORTED') {
      this._setState(
        OrchestratorState.UNSUPPORTED,
        'This physics diagram is not supported yet.'
      );
      return;
    }

    await this._fetchReviewAnalysis(opId);
  }

  /**
   * Internal helper to fetch PR-07 ReviewState.
   * @private
   */
  async _fetchReviewAnalysis(opId) {
    try {
      const revRes = await this.api.review(this.bookIR);
      if (opId !== this._operationId) return;

      this.reviewState = revRes.reviewState;
      this._metrics.reviewIssuesCount = this.reviewState.issues?.length || 0;

      if (revRes.readyToCompile) {
        this._metrics.timeToReadyMs = Date.now() - this._metrics.startTime;
        this._setState(OrchestratorState.READY_TO_COMPILE);
        await this.compile();
      } else {
        this._setState(OrchestratorState.NEEDS_REVIEW);
      }
    } catch (err) {
      if (opId !== this._operationId) return;
      console.error('[SimulationOrchestrator] Review analysis error:', err);
      this._setState(
        OrchestratorState.ERROR,
        `Review check failed: ${err.message || err}`
      );
    }
  }

  /**
   * Confirms a diagram-extracted candidate value.
   *
   * @param {string} parameterName
   * @param {object} candidate
   */
  async confirmCandidate(parameterName, candidate) {
    if (this.state !== OrchestratorState.NEEDS_REVIEW && this.state !== OrchestratorState.READY_TO_SIMULATE) {
      throw new Error(`Cannot confirm candidate in state ${this.state}`);
    }

    const opId = ++this._operationId;
    this._setState(OrchestratorState.APPLYING_RESOLUTION);

    try {
      const res = await this.api.confirmCandidate(this.bookIR, parameterName, candidate);
      if (opId !== this._operationId) return;

      this.bookIR = res.bookIR;
      this.readinessReport = res.readinessReport;
      this._metrics.candidateConfirmations++;
      this.resolutionHistory.push({
        action: 'confirm_candidate',
        parameterName,
        value: candidate.numericValue,
        unit: candidate.rawUnit,
        timestamp: Date.now(),
      });

      await this._evaluateAndAdvance(opId, res.canCompile);
    } catch (err) {
      if (opId !== this._operationId) return;
      console.error('[SimulationOrchestrator] Candidate confirmation error:', err);
      this._metrics.failedResolutions++;
      this.currentError = err.message || 'Failed to confirm candidate value.';
      this._setState(OrchestratorState.NEEDS_REVIEW);
    }
  }

  /**
   * Applies an explicit named default policy (e.g. policy_earth_gravity).
   *
   * @param {string} policyId
   * @param {string} [parameterName]
   */
  async applyPolicy(policyId, parameterName = null) {
    if (this.state !== OrchestratorState.NEEDS_REVIEW && this.state !== OrchestratorState.READY_TO_SIMULATE) {
      throw new Error(`Cannot apply policy in state ${this.state}`);
    }

    const opId = ++this._operationId;
    this._setState(OrchestratorState.APPLYING_RESOLUTION);

    try {
      const res = await this.api.applyPolicy(this.bookIR, policyId, parameterName);
      if (opId !== this._operationId) return;

      this.bookIR = res.bookIR;
      this.readinessReport = res.readinessReport;
      this._metrics.policiesAccepted++;
      this.resolutionHistory.push({
        action: 'apply_policy',
        policyId,
        parameterName,
        timestamp: Date.now(),
      });

      await this._evaluateAndAdvance(opId, res.canCompile);
    } catch (err) {
      if (opId !== this._operationId) return;
      console.error('[SimulationOrchestrator] Policy application error:', err);
      this._metrics.failedResolutions++;
      this.currentError = err.message || 'Failed to apply modeling policy.';
      this._setState(OrchestratorState.NEEDS_REVIEW);
    }
  }

  /**
   * Submits a student-entered numeric value and unit.
   *
   * @param {string} parameterName
   * @param {number|string} value
   * @param {string} [unit=null]
   * @param {string} [notes='']
   */
  async submitManualValue(parameterName, value, unit = null, notes = '') {
    if (this.state !== OrchestratorState.NEEDS_REVIEW && this.state !== OrchestratorState.READY_TO_SIMULATE) {
      throw new Error(`Cannot submit manual value in state ${this.state}`);
    }

    const num = Number(value);
    if (!Number.isFinite(num)) {
      this.currentError = `Invalid number entered for ${parameterName}: "${value}".`;
      this._setState(this.state);
      return;
    }

    const opId = ++this._operationId;
    this._setState(OrchestratorState.APPLYING_RESOLUTION);

    try {
      const res = await this.api.resolve(this.bookIR, {
        parameterName,
        resolvedValue: num,
        canonicalUnit: unit,
        originalEnteredValue: String(value),
        resolutionSource: 'user_supplied',
        notes: notes || 'Entered manually via review dialog',
      });
      if (opId !== this._operationId) return;

      this.bookIR = res.bookIR;
      this.readinessReport = res.readinessReport;
      this._metrics.manualValuesEntered++;
      this.resolutionHistory.push({
        action: 'manual_value',
        parameterName,
        value: num,
        unit,
        timestamp: Date.now(),
      });

      await this._evaluateAndAdvance(opId, res.canCompile);
    } catch (err) {
      if (opId !== this._operationId) return;
      console.error('[SimulationOrchestrator] Manual resolution error:', err);
      this._metrics.failedResolutions++;
      this.currentError = err.message || `Validation error for ${parameterName}.`;
      this._setState(OrchestratorState.NEEDS_REVIEW);
    }
  }

  /**
   * Corrects a previously candidate-detected value with a student-entered value.
   *
   * @param {string} parameterName
   * @param {number|string} value
   * @param {string} [unit=null]
   */
  async correctCandidate(parameterName, value, unit = null) {
    this._metrics.candidateCorrections++;
    return this.submitManualValue(parameterName, value, unit, 'Corrected by student via review dialog');
  }

  /**
   * Reverts / removes a resolution, returning BookIR to NEEDS_REVIEW.
   *
   * @param {string} parameterName
   */
  async removeResolution(parameterName) {
    const opId = ++this._operationId;
    this._setState(OrchestratorState.APPLYING_RESOLUTION);

    try {
      const res = await this.api.removeResolution(this.bookIR, parameterName);
      if (opId !== this._operationId) return;

      this.bookIR = res.bookIR;
      this.compiledScene = null; // Stale scene invalidated immediately
      this.readinessReport = res.readinessReport;
      this.resolutionHistory.push({
        action: 'remove_resolution',
        parameterName,
        timestamp: Date.now(),
      });

      await this._evaluateAndAdvance(opId, false);
    } catch (err) {
      if (opId !== this._operationId) return;
      console.error('[SimulationOrchestrator] Remove resolution error:', err);
      this.currentError = err.message || 'Failed to remove resolution.';
      this._setState(OrchestratorState.NEEDS_REVIEW);
    }
  }

  /**
   * Evaluates updated readiness and transitions accordingly.
   * @private
   */
  async _evaluateAndAdvance(opId, hintCanCompile = false) {
    this._setState(OrchestratorState.EVALUATING);

    try {
      const revRes = await this.api.review(this.bookIR);
      if (opId !== this._operationId) return;

      this.reviewState = revRes.reviewState;
      const isReady = revRes.readyToCompile || hintCanCompile;

      if (isReady) {
        if (!this._metrics.timeToReadyMs && this._metrics.startTime) {
          this._metrics.timeToReadyMs = Date.now() - this._metrics.startTime;
        }
        this._setState(OrchestratorState.READY_TO_COMPILE);
        await this.compile();
      } else {
        this._setState(OrchestratorState.NEEDS_REVIEW);
      }
    } catch (err) {
      if (opId !== this._operationId) return;
      console.error('[SimulationOrchestrator] Evaluation advance error:', err);
      this.currentError = err.message || 'Evaluation error.';
      this._setState(OrchestratorState.NEEDS_REVIEW);
    }
  }

  /**
   * Authoritatively compiles legitimately resolved BookIR via backend.
   */
  async compile() {
    const opId = ++this._operationId;
    this._setState(OrchestratorState.COMPILING);

    try {
      const compRes = await this.api.compile(this.bookIR);
      if (opId !== this._operationId) return;

      if (!compRes.success || !compRes.scene) {
        const issues = compRes.compiler?.issues || [];
        const msg = issues.map(i => i.message || i.code).join('; ') || 'Compilation did not produce a physics scene.';
        throw new CompilationGatingError(msg, issues, compRes.compiler?.status || 'NEEDS_REVIEW');
      }

      this.bookIR = compRes.bookIR || this.bookIR;
      this.compiledScene = this._normalizeSceneBackground(compRes.scene);
      this._setState(OrchestratorState.READY_TO_SIMULATE);
    } catch (err) {
      if (opId !== this._operationId) return;
      console.error('[SimulationOrchestrator] Compilation error:', err);
      this.compiledScene = null;
      if (err instanceof CompilationGatingError) {
        this._setState(
          OrchestratorState.ERROR,
          `The simulation is not ready yet: ${err.message}`
        );
      } else {
        this._setState(
          OrchestratorState.ERROR,
          `Compilation failed: ${err.message || err}`
        );
      }
    }
  }

  /**
   * Student action: Starts simulation playback and activates overlay.
   */
  startSimulation() {
    if (this.state !== OrchestratorState.READY_TO_SIMULATE && this.state !== OrchestratorState.SIMULATING) {
      throw new Error(`Cannot start simulation in state ${this.state}. Must be READY_TO_SIMULATE.`);
    }

    if (!this.compiledScene) {
      throw new Error('No compiled PhysicsScene available to simulate.');
    }

    this._setState(OrchestratorState.SIMULATING);
    return this.compiledScene;
  }

  /**
   * Reopens setup review while preserving session.
   */
  reopenReview() {
    this._setState(OrchestratorState.NEEDS_REVIEW);
  }

  /**
   * Ensures the background URL in compiled scene points to the uploaded image.
   * @private
   */
  _normalizeSceneBackground(scene) {
    if (!scene) return null;
    const cloned = JSON.parse(JSON.stringify(scene));
    if (!cloned.visual) cloned.visual = {};
    if (!cloned.visual.background_url && this.imageUrl) {
      cloned.visual.background_url = this.imageUrl;
    }
    if (!cloned.source) cloned.source = {};
    if (!cloned.source.image && this.imageUrl) {
      cloned.source.image = this.imageUrl;
    }
    return cloned;
  }

  /**
   * Resets orchestrator back to IDLE.
   */
  reset() {
    this._operationId++;
    this.state = OrchestratorState.IDLE;
    this.sourceAsset = null;
    this.imageUrl = '';
    this.pageIR = null;
    this.bookIR = null;
    this.reviewState = null;
    this.readinessReport = null;
    this.compiledScene = null;
    this.currentError = null;
    this.resolutionHistory = [];
    this._metrics = {
      startTime: null,
      timeToReadyMs: null,
      reviewIssuesCount: 0,
      candidateConfirmations: 0,
      candidateCorrections: 0,
      manualValuesEntered: 0,
      policiesAccepted: 0,
      failedResolutions: 0,
    };
    this._setState(OrchestratorState.IDLE);
  }

  /**
   * Returns research metrics for PR-10 evaluation (NO PII).
   */
  getResearchMetrics() {
    return {
      reviewIssuesCount: this._metrics.reviewIssuesCount,
      candidateConfirmations: this._metrics.candidateConfirmations,
      candidateCorrections: this._metrics.candidateCorrections,
      manualValuesEntered: this._metrics.manualValuesEntered,
      policiesAccepted: this._metrics.policiesAccepted,
      failedResolutions: this._metrics.failedResolutions,
      timeToReadyMs: this._metrics.timeToReadyMs,
      compilationSucceeded: Boolean(this.compiledScene),
      totalResolutionsApplied: this.resolutionHistory.length,
    };
  }
}

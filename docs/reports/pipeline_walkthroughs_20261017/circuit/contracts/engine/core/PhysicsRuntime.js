/**
 * engine/core/PhysicsRuntime.js
 * 
 * Master client-facing runtime for canonical interactive physics simulations.
 * Provides a book-agnostic, solver-agnostic API that validates scenes deterministically
 * and routes them to specialized domain adapters without fabricating physical data.
 */

import { defaultRegistry } from './SolverRegistry.js';
import { normalizeLegacyScene, validatePhysicsScene } from './validation.js';
import { PhysicsSceneValidationError } from './errors.js';
import { defaultCapabilityRegistry } from './capabilities.js';

export class PhysicsRuntime {
  /**
   * @param {object} [options={}]
   * @param {import('./SolverRegistry.js').SolverRegistry} [options.registry] - Custom adapter registry
   */
  constructor(options = {}) {
    this.registry = options.registry || defaultRegistry;
    this.adapter = null;
    this._scene = null;
    this.container = null;
    this._listeners = new Set();
    this._stateUnsubscribe = null;
  }

  /**
   * Normalizes legacy scene aliases into canonical fields.
   * @param {object} rawScene
   * @returns {object} Canonical PhysicsScene
   */
  normalizeScene(rawScene) {
    if (!rawScene) {
      throw new PhysicsSceneValidationError([{
        code: 'SCENE_NULL',
        path: '',
        message: 'Cannot load null or undefined scene.'
      }]);
    }
    return normalizeLegacyScene(rawScene);
  }

  /**
   * Validates and loads a scene into the target DOM container (or headlessly).
   * @param {object} rawScene - Canonical or compatible scene object
   * @param {HTMLElement|null} [container=null] - DOM container element
   * @param {object} [options={}] - Additional runtime configurations
   * @returns {Promise<import('./types.js').RuntimeOutput>}
   */
  async load(rawScene, container = null, options = {}) {
    if (this.adapter) {
      this.adapter.dispose();
      this.adapter = null;
    }

    if (this._stateUnsubscribe) {
      this._stateUnsubscribe();
      this._stateUnsubscribe = null;
    }

    // 1. Normalize legacy aliases (type -> subtype, coordinateSystem -> coordinateSpace)
    const normalizedScene = this.normalizeScene(rawScene);

    // 2. Strict pre-execution validation
    const validation = validatePhysicsScene(normalizedScene);
    if (!validation.valid) {
      throw new PhysicsSceneValidationError(validation.issues);
    }

    // 3. Resolve interactive capabilities without fabricating physical data
    const interactiveScene = defaultCapabilityRegistry.resolve(normalizedScene);

    this.scene = interactiveScene;
    if (container) {
      this.container = container;
    }

    // 4. Resolve domain adapter deterministically
    this.adapter = this.registry.resolve(interactiveScene);

    // 5. Initialize adapter (adapter performs subtype routing)
    await this.adapter.initialize(interactiveScene, this.container, options);

    // 5. Subscribe to reactive state updates
    this._stateUnsubscribe = this.adapter.onStateChange((state) => {
      this._notifyStateChange(state);
    });

    const output = this.getOutput();
    this._notifyStateChange(this.getState());
    return output;
  }

  /**
   * Authoritative canonical scene representation.
   * @returns {object|null}
   */
  get scene() {
    return this.adapter?.scene || this._scene;
  }

  set scene(s) {
    this._scene = s;
  }

  /**
   * Whether the simulation is currently active and running.
   * @returns {boolean}
   */
  get running() {
    return Boolean(this.adapter?.running);
  }

  /**
   * Starts or resumes simulation playback.
   */
  start() {
    this.adapter?.start();
  }

  /** Backward-compatible alias for start() */
  play() {
    this.start();
  }

  /**
   * Pauses simulation playback.
   */
  pause() {
    this.adapter?.pause();
  }

  /**
   * Advances simulation by discrete time step dt.
   * @param {number} [dt=1/60]
   */
  step(dt = 1 / 60) {
    this.adapter?.step(dt);
  }

  /**
   * Resets simulation to initial conditions.
   */
  reset() {
    this.adapter?.reset();
  }

  /**
   * Updates parameter value targeted by address with student provenance.
   * Supports e.g. "R2.resistance" or { targetId: "R2", key: "resistance", value: 50, unit: "Ω" }.
   * @param {string|object} addressOrSpec
   * @param {*} [value]
   */
  updateParameter(addressOrSpec, value) {
    this.adapter?.updateParameter(addressOrSpec, value);
  }

  /** Backward-compatible alias for updateParameter */
  setParameter(name, value) {
    this.updateParameter(name, value);
  }

  /**
   * Gets parameter specification.
   * @param {string} name
   * @returns {object|null}
   */
  getParameter(name) {
    return this.adapter?.getParameter(name) ?? null;
  }

  /**
   * Gets all parameter specifications.
   * @returns {Record<string, object>}
   */
  getParameters() {
    return this.adapter?.getParameters() ?? {};
  }

  /**
   * Returns normalized runtime output from active solver.
   * @returns {import('./types.js').RuntimeOutput|null}
   */
  getOutput() {
    return this.adapter?.getOutput() ?? null;
  }

  /**
   * Returns current physics state snapshot.
   * @returns {object}
   */
  getState() {
    return this.adapter?.getState() ?? { running: false, time: 0.0 };
  }

  /**
   * Resizes viewport renderer.
   * @param {number} width
   * @param {number} height
   */
  resize(width, height) {
    this.adapter?.resize(width, height);
  }

  /**
   * Disposes active simulation, canvases, and observers.
   */
  dispose() {
    if (this._stateUnsubscribe) {
      this._stateUnsubscribe();
      this._stateUnsubscribe = null;
    }
    this.adapter?.dispose();
    this.adapter = null;
    this.scene = null;
    this.container = null;
    this._listeners.clear();
  }

  /** Backward-compatible alias for dispose() */
  destroy() {
    this.dispose();
  }

  /**
   * Registers a reactive listener for physics telemetry.
   * @param {Function} listener
   * @returns {Function} Unsubscribe
   */
  onStateChange(listener) {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  _notifyStateChange(state) {
    for (const listener of this._listeners) {
      try {
        listener(state);
      } catch (err) {
        console.error('[PhysicsRuntime] Error in runtime state listener:', err);
      }
    }
  }
}

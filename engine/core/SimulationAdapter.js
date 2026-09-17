/**
 * engine/core/SimulationAdapter.js
 * 
 * Abstract base class defining the contract for domain simulation adapters.
 * All domain adapters (Mechanics, Optics, Circuits) wrap their existing solvers
 * and implement this interface without modifying underlying physics algorithms.
 */

export class SimulationAdapter {
  constructor() {
    this.scene = null;
    this.container = null;
    this.running = false;
    this._listeners = new Set();
    this._parameterOverrides = new Map();
  }

  /**
   * Evaluates if this adapter can execute the given scene specification.
   * @param {object} scene - Canonical PhysicsScene or compatible scene object
   * @returns {boolean}
   */
  canHandle(scene) {
    throw new Error('SimulationAdapter.canHandle must be implemented by subclass.');
  }

  /**
   * Initializes the simulation inside the target DOM container.
   * @param {object} scene - Canonical PhysicsScene
   * @param {HTMLElement} container - DOM container element
   * @param {object} [options={}] - Additional runtime configurations
   * @returns {Promise<void>}
   */
  async initialize(scene, container, options = {}) {
    this.scene = scene;
    this.container = container;
    this.running = false;
    this._parameterOverrides.clear();
  }

  /**
   * Starts or resumes the simulation.
   */
  play() {
    this.running = true;
  }

  /**
   * Pauses the simulation.
   */
  pause() {
    this.running = false;
  }

  /**
   * Resets the simulation to its initial state.
   */
  reset() {
    this.running = false;
  }

  /**
   * Updates a simulation parameter dynamically while preserving evidentiary provenance.
   * @param {string} name - Parameter identifier
   * @param {*} value - New parameter value
   */
  setParameter(name, value) {
    const currentParam = this.getParameter(name);
    const originalValue = currentParam?.value ?? value;

    this._parameterOverrides.set(name, {
      name,
      originalValue,
      overrideValue: value,
      provenance: 'student',
      source: 'runtime_interaction',
      timestamp: Date.now()
    });

    if (this.scene?.parameters?.[name]) {
      this.scene.parameters[name].value = value;
      this.scene.parameters[name].provenance = 'student';
    }
  }

  /**
   * Retrieves the current specification of a parameter including provenance metadata.
   * @param {string} name
   * @returns {object|null}
   */
  getParameter(name) {
    if (this.scene?.parameters?.[name]) {
      return { ...this.scene.parameters[name] };
    }
    return null;
  }

  /**
   * Returns the entire parameter dictionary with provenance metadata.
   * @returns {object}
   */
  getParameters() {
    return this.scene?.parameters || {};
  }

  /**
   * Returns an immutable snapshot of current physics state / telemetry.
   * @returns {object}
   */
  getState() {
    return {
      running: this.running,
      timestamp: performance.now()
    };
  }

  /**
   * Signals responsive dimension changes to the adapter renderer.
   * @param {number} [width]
   * @param {number} [height]
   */
  resize(width, height) {}

  /**
   * Disposes all canvases, animations, event listeners, and observers.
   */
  destroy() {
    this.pause();
    this._listeners.clear();
    this._parameterOverrides.clear();
    this.scene = null;
    this.container = null;
  }

  /**
   * Registers a reactive listener for physics state / telemetry updates.
   * @param {Function} listener - Callback (state: object) => void
   * @returns {Function} Unsubscribe callback
   */
  onStateChange(listener) {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  /**
   * Emits a telemetry update to all registered observers.
   * @param {object} state
   */
  notifyStateChange(state) {
    for (const listener of this._listeners) {
      try {
        listener(state);
      } catch (err) {
        console.error('[SimulationAdapter] Error in state listener:', err);
      }
    }
  }
}

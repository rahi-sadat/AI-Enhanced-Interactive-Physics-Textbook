/**
 * engine/core/PhysicsRuntime.js
 * 
 * Master client-facing runtime for interactive physics simulations.
 * Provides a book-agnostic, solver-agnostic API that can be embedded into
 * any textbook page, AI tutor, exam question, or upload studio.
 */

import { defaultRegistry } from './SolverRegistry.js';

export class PhysicsRuntime {
  /**
   * @param {object} [options={}]
   * @param {import('./SolverRegistry.js').SolverRegistry} [options.registry] - Custom adapter registry
   */
  constructor(options = {}) {
    this.registry = options.registry || defaultRegistry;
    this.adapter = null;
    this.scene = null;
    this.container = null;
    this._listeners = new Set();
    this._stateUnsubscribe = null;
  }

  /**
   * Normalizes any scene format (Canonical v1, Schema 2.x, or legacy compat)
   * into a standard schema representation while preserving all parameters and provenance.
   * @param {object} rawScene
   * @returns {object}
   */
  normalizeScene(rawScene) {
    if (!rawScene) {
      throw new Error('[PhysicsRuntime] Cannot load null or undefined scene.');
    }

    // Clone to prevent direct mutation of static json imports
    const scene = JSON.parse(JSON.stringify(rawScene));

    // Resolve domain
    const domain = scene.domain ||
      scene.simulation?.domain ||
      (scene.simulation_type === 'kinematics' ? 'mechanics' :
       scene.simulation_type === 'optics' ? 'optics' :
       scene.simulation_type === 'circuits' ? 'circuits' : 'mechanics');

    // Resolve type / subtype
    const type = scene.type ||
      scene.simulation?.subtype ||
      (domain === 'mechanics' ? (scene.objects?.some(o => o.type === 'pendulum') ? 'pendulum' : 'projectile') :
       domain === 'optics' ? (scene.elements?.some(e => e.semantic_label === 'prism') ? 'prism' : 'thin_lens') :
       domain === 'circuits' ? 'series_parallel' : 'generic');

    // Resolve source metadata
    const source = scene.source || {
      type: 'book_figure',
      image: scene.visual?.background_url || null,
      width: scene.geometry?.source_width || 800,
      height: scene.geometry?.source_height || 600
    };

    // Resolve coordinate system
    const coordinateSystem = scene.coordinateSystem || {
      width: source.width || scene.geometry?.source_width || 800,
      height: source.height || scene.geometry?.source_height || 600,
      unit: 'source-pixel',
      pixelsPerUnit: 1.0
    };

    // Ensure parameters object with provenance
    const parameters = scene.parameters || {};

    // Backward-compatibility: extract legacy mechanics parameters if not present
    if (domain === 'mechanics' && Object.keys(parameters).length === 0) {
      const pObj = scene.objects?.find(o => o.type === 'pendulum') || scene.objects?.[0];
      if (pObj?.physics) {
        parameters.length = {
          value: Number(pObj.physics.length_m || 1.0),
          unit: 'm',
          label: 'Length (L)',
          min: 0.2,
          max: 3.0,
          step: 0.05,
          provenance: pObj.physics.length_m ? 'observed' : 'assumed',
          source: 'scene_specification',
          confidence: 0.95
        };
        parameters.gravity = {
          value: Number(scene.environment?.gravity_m_s2 || 9.81),
          unit: 'm/s²',
          label: 'Gravity (g)',
          min: 0.0,
          max: 25.0,
          step: 0.1,
          provenance: 'assumed',
          source: 'earth_standard',
          confidence: 1.0
        };
        parameters.initialAngle = {
          value: Number((((pObj.physics.theta0_rad || 0.35) * 180) / Math.PI).toFixed(1)),
          unit: '°',
          label: 'Initial Angle (θ₀)',
          min: -60,
          max: 60,
          step: 1,
          provenance: 'observed',
          source: 'diagram_measurement',
          confidence: 0.92
        };
        parameters.mass = {
          value: Number(pObj.physics.mass_kg || 1.0),
          unit: 'kg',
          label: 'Bob Mass (m)',
          min: 0.1,
          max: 10.0,
          step: 0.1,
          provenance: 'assumed',
          source: 'standard_default',
          confidence: 1.0
        };
      }
    }

    return {
      schemaVersion: scene.schemaVersion || '1.0',
      id: scene.id || `PHY-${domain.toUpperCase().slice(0, 3)}-${Date.now()}`,
      domain,
      type,
      title: scene.title || `${domain.charAt(0).toUpperCase() + domain.slice(1)} Simulation`,
      description: scene.description || '',
      source,
      coordinateSystem,
      parameters,
      geometry: scene.geometry || {},
      objects: scene.objects || scene.elements || [],
      visual: scene.visual || {},
      circuit: scene.circuit,
      metadata: scene.metadata || {}
    };
  }

  /**
   * Loads a scene into the specified DOM container using the registered adapter.
   * @param {object} scene - Canonical or compatible scene object
   * @param {HTMLElement} [container] - DOM container element (if omitted, reuses existing)
   * @param {object} [options={}] - Additional runtime configurations
   * @returns {Promise<object>} Current state telemetry after loading
   */
  async load(scene, container = null, options = {}) {
    if (this.adapter) {
      this.adapter.destroy();
      this.adapter = null;
    }

    if (this._stateUnsubscribe) {
      this._stateUnsubscribe();
      this._stateUnsubscribe = null;
    }

    const normalizedScene = this.normalizeScene(scene);
    this.scene = normalizedScene;
    if (container) {
      this.container = container;
    }

    // Resolve domain adapter
    this.adapter = this.registry.resolve(normalizedScene);

    // Initialize adapter with container
    await this.adapter.initialize(normalizedScene, this.container, options);

    // Subscribe to state changes from adapter
    this._stateUnsubscribe = this.adapter.onStateChange((state) => {
      this._notifyStateChange(state);
    });

    const state = this.getState();
    this._notifyStateChange(state);
    return state;
  }

  /**
   * Starts simulation playback.
   */
  play() {
    this.adapter?.play();
  }

  /**
   * Pauses simulation playback.
   */
  pause() {
    this.adapter?.pause();
  }

  /**
   * Resets simulation to initial state.
   */
  reset() {
    this.adapter?.reset();
  }

  /**
   * Sets a physical parameter by name while tracking provenance.
   * @param {string} name
   * @param {*} value
   */
  setParameter(name, value) {
    this.adapter?.setParameter(name, value);
  }

  /**
   * Gets parameter definition and value by name.
   * @param {string} name
   * @returns {object|null}
   */
  getParameter(name) {
    return this.adapter?.getParameter(name) || null;
  }

  /**
   * Gets all parameters defined in the current scene.
   * @returns {object}
   */
  getParameters() {
    return this.adapter?.getParameters() || {};
  }

  /**
   * Gets current state and telemetry snapshot.
   * @returns {object}
   */
  getState() {
    return this.adapter?.getState() || { running: false };
  }

  /**
   * Gets the active canonical scene.
   * @returns {object|null}
   */
  getScene() {
    return this.scene;
  }

  /**
   * Signals dimension resize to adapter.
   * @param {number} [width]
   * @param {number} [height]
   */
  resize(width, height) {
    this.adapter?.resize(width, height);
  }

  /**
   * Disposes current simulation adapter and all listeners.
   */
  destroy() {
    if (this._stateUnsubscribe) {
      this._stateUnsubscribe();
      this._stateUnsubscribe = null;
    }
    this.adapter?.destroy();
    this.adapter = null;
    this.scene = null;
    this.container = null;
    this._listeners.clear();
  }

  /**
   * Subscribes to simulation state telemetry changes.
   * @param {Function} listener
   * @returns {Function} Unsubscribe callback
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

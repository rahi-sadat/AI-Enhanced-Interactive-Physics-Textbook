/**
 * engine/core/SimulationAdapter.js
 * 
 * Abstract base class defining the contract for domain simulation adapters.
 * All domain adapters (Mechanics, Optics, Circuits) wrap their existing solvers
 * and implement this interface without modifying underlying physics algorithms.
 */

import { PhysicsSceneValidationError } from './errors.js';
import { resolveParameterSpec, validateAndConvertParameterUpdate } from './units.js';
import { defaultCapabilityRegistry } from './capabilities.js';

export class SimulationAdapter {
  constructor() {
    this.scene = null;
    this.container = null;
    this.running = false;
    this.time = 0.0;
    this._listeners = new Set();
    this._parameterOverrides = new Map();
  }

  /**
   * Evaluates if this adapter can execute the given scene specification.
   * @param {object} scene - Canonical PhysicsScene
   * @returns {boolean}
   */
  canHandle(scene) {
    throw new Error('SimulationAdapter.canHandle must be implemented by subclass.');
  }

  /**
   * Initializes the simulation inside the target DOM container (or headlessly).
   * @param {object} scene - Canonical PhysicsScene
   * @param {HTMLElement|null} [container=null] - DOM container element
   * @param {object} [options={}] - Additional runtime configurations
   * @returns {Promise<void>}
   */
  async initialize(scene, container = null, options = {}) {
    const interactiveScene = defaultCapabilityRegistry.resolve(scene);
    this.scene = interactiveScene;
    this._initialScene = interactiveScene ? JSON.parse(JSON.stringify(interactiveScene)) : null;
    this.container = container;
    this.running = false;
    this.time = 0.0;
    this._parameterOverrides.clear();
  }

  /**
   * Starts or resumes the simulation.
   */
  start() {
    this.running = true;
  }

  /** Backward-compatible alias for start() */
  play() {
    this.start();
  }

  /**
   * Pauses the simulation.
   */
  pause() {
    this.running = false;
  }

  /**
   * Advances the simulation by a discrete time step dt.
   * @param {number} dt - Step duration in seconds
   */
  step(dt = 1 / 60) {
    this.time += dt;
  }

  /**
   * Resets the simulation to its initial state.
   */
  reset() {
    this.running = false;
    this.time = 0.0;
    this._parameterOverrides.clear();
    if (this._initialScene) {
      this.scene = JSON.parse(JSON.stringify(this._initialScene));
    }
  }

  /**
   * Updates a simulation parameter targeted by address with explicit student provenance.
   * Supports:
   *   - "length", 2.0
   *   - "R2.resistance", 50
   *   - "components.R2.resistance", 50
   *   - { targetId: "R2", key: "resistance", value: 50, unit: "Ω" }
   * @param {string|object} addressOrSpec - Parameter address string or target object
   * @param {*} [value] - New parameter value
   */
  updateParameter(addressOrSpec, value) {
    let address = '';
    let key = '';
    let targetId = '';
    let incomingVal = value;
    let incomingUnit = null;

    if (typeof addressOrSpec === 'object' && addressOrSpec !== null) {
      targetId = addressOrSpec.targetId || '';
      key = addressOrSpec.key || '';
      address = addressOrSpec.address || (targetId ? `${targetId}.${key}` : key);
      incomingVal = addressOrSpec.value !== undefined ? addressOrSpec.value : value;
      incomingUnit = addressOrSpec.unit || null;
    } else {
      address = String(addressOrSpec);
      const parts = address.split('.');
      key = parts[parts.length - 1];
      if (parts.length >= 2) {
        targetId = parts[parts.length - 2];
      }
      incomingVal = value;
    }

    if (!address) {
      throw new PhysicsSceneValidationError([{
        code: 'EMPTY_PARAMETER_ADDRESS',
        path: '',
        message: 'Parameter address must not be empty.'
      }]);
    }

    const isBooleanParam = key === 'closed' || key === 'state' || typeof incomingVal === 'boolean' || incomingVal === 'open' || incomingVal === 'closed';

    // 1. Validate numeric finite (or boolean for switch states)
    if (!isBooleanParam) {
      if (incomingVal === null || incomingVal === undefined || !Number.isFinite(Number(incomingVal))) {
        throw new PhysicsSceneValidationError([{
          code: 'INVALID_PARAMETER_VALUE',
          path: address,
          message: `Parameter "${address}" value must be a valid finite number: got ${incomingVal}`
        }]);
      }
    }

    // 2. Resolve target specification
    const targetSpec = resolveParameterSpec(this.scene, address) || resolveParameterSpec(this.scene, key);
    const lookupId = targetId || key;
    let comp = null;
    if (this.scene?.circuit?.components && lookupId) {
      comp = this.scene.circuit.components.find(c => c.id === lookupId || c.label === lookupId);
    }
    let obj = null;
    if (this.scene?.objects && lookupId) {
      obj = this.scene.objects.find(o => o.id === lookupId);
    }

    if (!targetSpec && !comp && !obj && !this.scene?.parameters?.[address] && !this.scene?.parameters?.[key]) {
      throw new PhysicsSceneValidationError([{
        code: 'PARAMETER_NOT_FOUND',
        path: address,
        message: `Cannot update unknown parameter "${address}". Target does not exist in scene.`
      }]);
    }

    // 3. Determine canonical solver unit and convert
    let canonicalUnit = targetSpec?.unit || null;
    if (key === 'length' || key === 'length_m') {
      canonicalUnit = 'm';
    } else if (key === 'initialAngle' || key === 'theta0') {
      canonicalUnit = targetSpec?.unit || 'rad';
    } else if (key === 'angle' || key === 'launch_angle_deg') {
      canonicalUnit = targetSpec?.unit || 'deg';
    } else if (key === 'resistance') {
      canonicalUnit = 'Ω';
    } else if (key === 'voltage') {
      canonicalUnit = 'V';
    } else if (key === 'current') {
      canonicalUnit = 'A';
    } else if (key === 'speed') {
      canonicalUnit = 'm/s';
    } else if (key === 'gravity') {
      canonicalUnit = 'm/s²';
    }

    const convertedVal = isBooleanParam
      ? (incomingVal === true || incomingVal === 'closed' || incomingVal === 1 || incomingVal === '1')
      : validateAndConvertParameterUpdate(this.scene, address, incomingVal, incomingUnit, canonicalUnit);

    // 4. Validate physical domain constraints
    const isResistance = key === 'resistance' || targetSpec?.unit === 'Ω' || comp?.type === 'resistor';
    const isLength = key === 'length' || key === 'length_m' || targetSpec?.unit === 'm' || targetSpec?.unit === 'cm';
    const isMass = key === 'mass' || targetSpec?.unit === 'kg';
    const isRefractiveIndex = key === 'refractiveIndex' || key === 'n' || key === 'n1' || key === 'n2';

    if ((isLength || isResistance) && convertedVal <= 0) {
      throw new PhysicsSceneValidationError([{
        code: 'NON_POSITIVE_VALUE',
        path: address,
        message: `Parameter "${address}" must be positive (> 0), got ${convertedVal}`
      }]);
    }
    if (isMass && convertedVal <= 0) {
      throw new PhysicsSceneValidationError([{
        code: 'NON_POSITIVE_VALUE',
        path: address,
        message: `Parameter "${address}" must be positive (> 0), got ${convertedVal}`
      }]);
    }
    if (isRefractiveIndex && convertedVal < 1.0) {
      throw new PhysicsSceneValidationError([{
        code: 'INVALID_REFRACTIVE_INDEX',
        path: address,
        message: `Refractive index must be >= 1.0, got ${convertedVal}`
      }]);
    }
    if ((key === 'speed' || key === 'gravity') && convertedVal < 0) {
      throw new PhysicsSceneValidationError([{
        code: 'NEGATIVE_VALUE',
        path: address,
        message: `Parameter "${address}" cannot be negative, got ${convertedVal}`
      }]);
    }

    // 5. ATOMIC MUTATION: Only apply to scene after all validations passed
    const originalValue = targetSpec?.value ?? convertedVal;
    this._parameterOverrides.set(address, {
      name: address,
      originalValue,
      overrideValue: convertedVal,
      provenance: 'student',
      source: 'student_interaction',
      timestamp: Date.now()
    });

    if (this.scene?.parameters?.[address]) {
      this.scene.parameters[address].value = convertedVal;
      this.scene.parameters[address].provenance = 'student';
      this.scene.parameters[address].editable = true;
    } else if (this.scene?.parameters?.[key]) {
      this.scene.parameters[key].value = convertedVal;
      this.scene.parameters[key].provenance = 'student';
      this.scene.parameters[key].editable = true;
    } else if (targetId && this.scene?.parameters?.[targetId]) {
      this.scene.parameters[targetId].value = convertedVal;
      this.scene.parameters[targetId].provenance = 'student';
      this.scene.parameters[targetId].editable = true;
    }

    if (comp) {
      comp.value = convertedVal;
      if (comp.parameters?.[key]) {
        comp.parameters[key].value = convertedVal;
        comp.parameters[key].provenance = 'student';
      }
      if (comp[key] !== undefined) comp[key] = convertedVal;
    }

    if (obj) {
      if (obj.physics?.[key] !== undefined) obj.physics[key] = convertedVal;
      if (obj.parameters?.[key]) {
        obj.parameters[key].value = convertedVal;
        obj.parameters[key].provenance = 'student';
      }
    }

    // Delegate to subclass domain adapter for solver updates
    if (typeof this._applyParameterUpdate === 'function') {
      this._applyParameterUpdate(address, convertedVal, key, targetId, incomingUnit);
    }
  }

  /**
   * Backward-compatible alias for updateParameter.
   * @param {string} name
   * @param {*} value
   */
  setParameter(name, value) {
    this.updateParameter(name, value);
  }

  /**
   * Retrieves parameter specification including provenance metadata.
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
   * Returns parameter dictionary for editable parameters with provenance metadata.
   * Strictly filters for parameters declared with editable === true.
   * @returns {Record<string, object>}
   */
  getParameters() {
    const params = this.scene?.parameters || {};
    const editable = {};
    for (const [k, p] of Object.entries(params)) {
      if (p && p.editable === true) {
        editable[k] = { ...p };
      }
    }
    return editable;
  }

  /**
   * Returns normalized runtime output for this solver.
   * @returns {import('./types.js').RuntimeOutput}
   */
  getOutput() {
    const rawState = this.getState();
    return {
      domain: rawState.domain || this.scene?.domain || 'unknown',
      subtype: rawState.type || rawState.subtype || this.scene?.subtype || 'unknown',
      time: this.time,
      state: rawState,
      geometry: rawState.geometry || {},
      telemetry: rawState.telemetry || rawState,
      events: rawState.events || [],
      editableParameters: this.getParameters()
    };
  }

  /**
   * Returns immutable snapshot of current physics state / telemetry.
   * @returns {object}
   */
  getState() {
    return {
      running: this.running,
      time: this.time,
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
  dispose() {
    this.pause();
    this._listeners.clear();
    this._parameterOverrides.clear();
    this.scene = null;
    this.container = null;
  }

  /** Backward-compatible alias for dispose() */
  destroy() {
    this.dispose();
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

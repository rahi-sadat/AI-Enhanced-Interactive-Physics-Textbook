/**
 * engine/core/SolverRegistry.js
 * 
 * Central registry mapping canonical PhysicsScene specifications
 * to appropriate domain SimulationAdapter implementations.
 */

export class SolverRegistry {
  constructor() {
    this._adapters = [];
  }

  /**
   * Registers a SimulationAdapter class.
   * @param {typeof import('./SimulationAdapter.js').SimulationAdapter} AdapterClass
   */
  register(AdapterClass) {
    if (!AdapterClass) return;
    if (!this._adapters.includes(AdapterClass)) {
      this._adapters.push(AdapterClass);
    }
  }

  /**
   * Unregisters an adapter class.
   * @param {typeof import('./SimulationAdapter.js').SimulationAdapter} AdapterClass
   */
  unregister(AdapterClass) {
    const idx = this._adapters.indexOf(AdapterClass);
    if (idx !== -1) {
      this._adapters.splice(idx, 1);
    }
  }

  /**
   * Finds the first registered adapter class capable of handling the scene.
   * @param {object} scene - Canonical PhysicsScene
   * @returns {typeof import('./SimulationAdapter.js').SimulationAdapter|null}
   */
  findAdapterClass(scene) {
    for (const AdapterClass of this._adapters) {
      try {
        // Instantiate temporary lightweight probe or check static canHandle
        if (typeof AdapterClass.canHandle === 'function' && AdapterClass.canHandle(scene)) {
          return AdapterClass;
        }
        const probe = new AdapterClass();
        if (probe.canHandle(scene)) {
          return AdapterClass;
        }
      } catch (err) {
        console.warn('[SolverRegistry] Adapter probe failed:', err);
      }
    }
    return null;
  }

  /**
   * Instantiates the matching SimulationAdapter for the scene.
   * @param {object} scene
   * @returns {import('./SimulationAdapter.js').SimulationAdapter}
   */
  resolve(scene) {
    const AdapterClass = this.findAdapterClass(scene);
    if (!AdapterClass) {
      const domain = scene?.domain || scene?.simulation?.domain || scene?.simulation_type || 'unknown';
      throw new Error(`[SolverRegistry] No simulation adapter registered for domain/type: ${domain}`);
    }
    return new AdapterClass();
  }

  /**
   * Returns list of all registered adapter classes.
   */
  getRegisteredAdapters() {
    return [...this._adapters];
  }

  /**
   * Clears all registered adapters.
   */
  clear() {
    this._adapters = [];
  }
}

import { MechanicsAdapter } from '../mechanics/MechanicsAdapter.js';
import { OpticsAdapter } from '../optics/OpticsAdapter.js';
import { CircuitAdapter } from '../circuits/CircuitAdapter.js';

/** Global default registry instance */
export const defaultRegistry = new SolverRegistry();
defaultRegistry.register(MechanicsAdapter);
defaultRegistry.register(OpticsAdapter);
defaultRegistry.register(CircuitAdapter);


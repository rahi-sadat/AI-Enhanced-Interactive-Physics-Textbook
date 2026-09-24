/**
 * engine/core/SolverRegistry.js
 * 
 * Central deterministic registry mapping canonical PhysicsScene specifications
 * to appropriate domain SimulationAdapter implementations.
 */

import { UnsupportedPhysicsDomainError } from './errors.js';
import { MechanicsAdapter } from '../mechanics/MechanicsAdapter.js';
import { OpticsAdapter } from '../optics/OpticsAdapter.js';
import { CircuitAdapter } from '../circuits/CircuitAdapter.js';

export class SolverRegistry {
  constructor() {
    /** @type {Map<string, typeof import('./SimulationAdapter.js').SimulationAdapter>} */
    this._domainMap = new Map();
  }

  /**
   * Registers a SimulationAdapter class for a domain.
   * @param {string|typeof import('./SimulationAdapter.js').SimulationAdapter} domainOrClass
   * @param {typeof import('./SimulationAdapter.js').SimulationAdapter} [AdapterClass]
   */
  register(domainOrClass, AdapterClass) {
    if (typeof domainOrClass === 'string' && AdapterClass) {
      this._domainMap.set(domainOrClass.toLowerCase(), AdapterClass);
      return;
    }

    const Cls = AdapterClass || domainOrClass;
    if (Cls && typeof Cls.domain === 'string' && Cls.domain.trim()) {
      this._domainMap.set(Cls.domain.toLowerCase(), Cls);
      return;
    }

    throw new Error(`[SolverRegistry] Registration requires an explicit domain string or a static "domain" property on the adapter class.`);
  }

  /**
   * Unregisters an adapter class or domain.
   * @param {string|typeof import('./SimulationAdapter.js').SimulationAdapter} domainOrClass
   */
  unregister(domainOrClass) {
    if (typeof domainOrClass === 'string') {
      this._domainMap.delete(domainOrClass.toLowerCase());
      return;
    }
    for (const [d, cls] of this._domainMap.entries()) {
      if (cls === domainOrClass) {
        this._domainMap.delete(d);
      }
    }
  }

  /**
   * Retrieves registered adapter class by domain.
   * @param {string} domain
   * @returns {typeof import('./SimulationAdapter.js').SimulationAdapter}
   */
  get(domain) {
    if (!domain || typeof domain !== 'string') {
      throw new UnsupportedPhysicsDomainError(String(domain));
    }
    const AdapterClass = this._domainMap.get(domain.toLowerCase());
    if (!AdapterClass) {
      throw new UnsupportedPhysicsDomainError(domain);
    }
    return AdapterClass;
  }

  /**
   * Finds the registered adapter class for a canonical scene.
   * @param {object} scene - Canonical PhysicsScene
   * @returns {typeof import('./SimulationAdapter.js').SimulationAdapter|null}
   */
  findAdapterClass(scene) {
    const domain = scene?.domain;
    if (!domain || typeof domain !== 'string') return null;
    return this._domainMap.get(domain.toLowerCase()) || null;
  }

  /**
   * Instantiates the matching SimulationAdapter for the scene.
   * Throws UnsupportedPhysicsDomainError if domain is not registered.
   * @param {object} scene - Canonical PhysicsScene
   * @returns {import('./SimulationAdapter.js').SimulationAdapter}
   */
  resolve(scene) {
    const domain = scene?.domain;
    if (!domain || typeof domain !== 'string') {
      throw new UnsupportedPhysicsDomainError(domain || 'unknown');
    }
    const AdapterClass = this.get(domain);
    return new AdapterClass();
  }

  /**
   * Returns list of all registered adapter classes.
   */
  getRegisteredAdapters() {
    return [...new Set(this._domainMap.values())];
  }

  /**
   * Clears all registered adapters.
   */
  clear() {
    this._domainMap.clear();
  }
}

/** Global default registry instance */
export const defaultRegistry = new SolverRegistry();
defaultRegistry.register('mechanics', MechanicsAdapter);
defaultRegistry.register('optics', OpticsAdapter);
defaultRegistry.register('circuits', CircuitAdapter);

/**
 * apps/web/src/features/simulations/core/RendererRegistry.js
 * 
 * Domain-isolated registry for simulation renderers.
 * Resolves the appropriate renderer by canonical domain and subtype
 * without checking filenames, hashes, or hardcoded screenshot conditions.
 */

export class RendererRegistry {
  constructor() {
    this._domainMap = new Map();
    this._subtypeMap = new Map();
  }

  /**
   * Registers a renderer class for a domain or specific (domain, subtype) pair.
   * @param {string} domain - "optics" | "circuits" | "mechanics"
   * @param {string|Function} subtypeOrRenderer - Subtype string or renderer constructor
   * @param {Function} [rendererClass] - Renderer constructor if subtype was provided
   */
  register(domain, subtypeOrRenderer, rendererClass = null) {
    if (typeof subtypeOrRenderer === 'function') {
      this._domainMap.set(domain, subtypeOrRenderer);
    } else if (typeof subtypeOrRenderer === 'string' && typeof rendererClass === 'function') {
      const key = `${domain}:${subtypeOrRenderer}`;
      this._subtypeMap.set(key, rendererClass);
    } else {
      throw new Error(`[RendererRegistry] Invalid registration for domain "${domain}". Expected renderer constructor.`);
    }
  }

  /**
   * Resolves and instantiates the appropriate renderer for a scene or output.
   * @param {object} sceneOrOutput - PhysicsScene or RuntimeOutput
   * @returns {import('./SimulationRenderer.js').SimulationRenderer}
   */
  resolve(sceneOrOutput) {
    if (!sceneOrOutput) {
      throw new Error('[RendererRegistry] Cannot resolve renderer for null or undefined scene.');
    }

    const domain = sceneOrOutput.domain || sceneOrOutput.simulation?.domain || sceneOrOutput.simulation_type;
    const subtype = sceneOrOutput.subtype || sceneOrOutput.type || sceneOrOutput.scenario;

    if (!domain) {
      throw new Error('[RendererRegistry] Scene or output is missing a declared "domain".');
    }

    // 1. Try subtype-specific registration first
    if (subtype) {
      const key = `${domain}:${subtype}`;
      if (this._subtypeMap.has(key)) {
        const RendererCls = this._subtypeMap.get(key);
        return new RendererCls();
      }
    }

    // 2. Fall back to domain-level renderer
    if (this._domainMap.has(domain)) {
      const RendererCls = this._domainMap.get(domain);
      return new RendererCls();
    }

    throw new Error(`[RendererRegistry] No renderer registered for domain "${domain}" (subtype: "${subtype || 'unspecified'}").`);
  }

  /**
   * Checks whether a renderer is available for the given domain and subtype.
   * @param {string} domain
   * @param {string} [subtype]
   * @returns {boolean}
   */
  has(domain, subtype = null) {
    if (subtype && this._subtypeMap.has(`${domain}:${subtype}`)) {
      return true;
    }
    return this._domainMap.has(domain);
  }

  /**
   * Clears all registered renderers (useful in tests).
   */
  clear() {
    this._domainMap.clear();
    this._subtypeMap.clear();
  }
}

import { OpticsRenderer } from '../optics/OpticsRenderer.js';
import { CircuitRenderer } from '../circuits/CircuitRenderer.js';

export const defaultRendererRegistry = new RendererRegistry();
defaultRendererRegistry.register('optics', OpticsRenderer);
defaultRendererRegistry.register('circuits', CircuitRenderer);


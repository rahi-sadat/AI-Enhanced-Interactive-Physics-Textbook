/**
 * engine/optics/prismEngine.js
 * 
 * Polygonal prism and slab refraction solver delegating to the unified domain-agnostic engine core.
 * Physical Law: Snell's Law & Total Internal Reflection across polygonal boundaries.
 */

import { solvePrismRefraction as unifiedSolvePrismRefraction } from '../unified/compat/EngineCompatibilityLayer.js';

export function solvePrismRefraction(params) {
  return unifiedSolvePrismRefraction(params);
}

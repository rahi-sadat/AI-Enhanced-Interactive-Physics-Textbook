/**
 * engine/optics/thinLensEngine.js
 * 
 * Thin Lens physics solver delegating to the unified domain-agnostic engine core.
 * Physical Law: Gaussian Thin Lens Law: 1/v - 1/u = 1/f
 */

import { solveThinLens as unifiedSolveThinLens } from '../unified/compat/EngineCompatibilityLayer.js';

export function solveThinLens(params) {
  return unifiedSolveThinLens(params);
}

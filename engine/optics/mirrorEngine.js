/**
 * engine/optics/mirrorEngine.js
 * 
 * Spherical and plane mirror solver delegating to the unified domain-agnostic engine core.
 * Physical Law: Spherical Mirror Law: 1/v + 1/u = 1/f
 * Solves concave, convex, and plane mirrors with bidirectional facing support.
 */

import { solveMirror as unifiedSolveMirror } from '../unified/compat/EngineCompatibilityLayer.js';

export function solveMirror(params) {
  return unifiedSolveMirror(params);
}

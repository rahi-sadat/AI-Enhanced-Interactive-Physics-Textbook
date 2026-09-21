/**
 * engine/optics/snellInterfaceEngine.js
 * 
 * Planar media interface refraction and critical angle solver delegating to unified core.
 * Physical Law: Snell's Law: n1 * sin(theta1) = n2 * sin(theta2)
 * Total Internal Reflection (TIR): theta_c = arcsin(n2 / n1) when n1 > n2.
 */

import {
  traceInterfaceRefraction as unifiedTraceInterfaceRefraction,
  solveSnellInterface as unifiedSolveSnellInterface
} from '../unified/compat/EngineCompatibilityLayer.js';

export function traceInterfaceRefraction(config) {
  return unifiedTraceInterfaceRefraction(config);
}

export function solveSnellInterface(n1, n2, theta1Deg) {
  return unifiedSolveSnellInterface(n1, n2, theta1Deg);
}

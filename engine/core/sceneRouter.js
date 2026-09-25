/**
 * engine/core/sceneRouter.js
 * 
 * Domain resolution and routing for canonical physics scenes.
 * Book-agnostic core module. STRICTLY ZERO IMPORTS FROM apps/ OR DOM.
 */

export function resolveDomain(scene) {
  if (scene?.simulation?.domain) return scene.simulation.domain;
  if (scene?.domain)             return scene.domain;
  if (scene?.simulation_type === 'kinematics') return 'mechanics';
  if (scene?.simulation_type === 'optics')     return 'optics';
  if (scene?.simulation_type === 'circuits')   return 'circuits';
  return null;
}

/**
 * Legacy router placeholder.
 * Engine files cannot import UI controllers from apps/.
 * For runtime execution, use PhysicsRuntime and domain SimulationRenderers.
 * For legacy studio canvas, use apps/web createLegacySimulation.
 */
export function createSimulation(scene, overlayStage) {
  throw new Error(
    '[engine/sceneRouter] createSimulation() in engine/core/ has been retired. ' +
    'The physics engine cannot import UI controllers. Use PhysicsRuntime + apps/web SimulationRenderer.'
  );
}

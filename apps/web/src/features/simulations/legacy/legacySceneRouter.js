/**
 * apps/web/src/features/simulations/legacy/legacySceneRouter.js
 * 
 * Legacy simulation factory for Studio view mode (primarily kinematics).
 * Retained for backward-compatibility with legacy canvas controllers
 * while Optics and Circuits run on canonical PhysicsRuntime + SimulationRenderer.
 */

import { MechanicsController } from '../mechanics/mechanicsController.js';
import { OpticsController }    from '../optics/opticsController.js';
import { CircuitController }   from '../circuits/CircuitController.js';
import { resolveDomain }       from '@engine/core/sceneRouter.js';

export function createLegacySimulation(scene, overlayStage) {
  const domain = resolveDomain(scene);
  if (domain === 'mechanics') return new MechanicsController(scene, overlayStage);
  if (domain === 'optics')    return new OpticsController(scene, overlayStage);
  if (domain === 'circuits')  return new CircuitController(scene, overlayStage);
  throw new Error('Unsupported legacy domain: ' + domain);
}

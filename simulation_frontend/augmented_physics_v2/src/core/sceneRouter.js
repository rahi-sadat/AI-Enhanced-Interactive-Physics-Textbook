/** core/sceneRouter.js - Routes scene.simulation.domain to the right controller. */
import { MechanicsController } from '../mechanics/mechanicsController.js';
import { OpticsController }    from '../optics/opticsController.js';

function resolveDomain(scene) {
  if (scene?.simulation?.domain) return scene.simulation.domain;
  if (scene?.simulation_type === 'kinematics') return 'mechanics';
  if (scene?.simulation_type === 'optics')     return 'optics';
  return 'mechanics';
}

export function createSimulation(scene, overlayStage) {
  const domain = resolveDomain(scene);
  console.log('[Router] domain:', domain);
  if (domain === 'mechanics') return new MechanicsController(scene, overlayStage);
  if (domain === 'optics')    return new OpticsController(scene, overlayStage);
  throw new Error('Unsupported domain: ' + domain);
}

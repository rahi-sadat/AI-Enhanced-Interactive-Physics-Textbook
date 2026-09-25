/**
 * apps/web/src/features/simulations/core/SimulationRenderer.js
 * 
 * Generic base contract for book-agnostic simulation renderers.
 * Decoupled from numerical physics engines: receives solved RuntimeOutput
 * and renders source-aligned overlays on top of the original textbook diagram.
 */

export class SimulationRenderer {
  constructor() {
    this.container = null;
    this.sourceImage = null;
    this.scene = null;
    this.coordinateMapper = null;
    this.onInteract = null;
    this.runtimeOutput = null;
    this.mounted = false;
  }

  /**
   * Mounts the renderer into the target overlay container.
   * @param {object} params
   * @param {HTMLElement} params.container - Viewport overlay DOM container
   * @param {string|null} [params.sourceImage=null] - Diagram image URL
   * @param {object} params.scene - Canonical PhysicsScene
   * @param {import('@engine/core/coordinateMapper.js').CoordinateMapper} params.coordinateMapper
   * @param {Function} [params.onInteract] - Callback for semantic parameter mutations: ({ targetId, key, value, unit }) => void
   */
  mount({ container, sourceImage = null, scene, coordinateMapper, onInteract = () => {} }) {
    if (!container) {
      throw new Error('[SimulationRenderer] Mount container element is required.');
    }
    this.container = container;
    this.sourceImage = sourceImage;
    this.scene = scene;
    this.coordinateMapper = coordinateMapper;
    this.onInteract = onInteract;
    this.mounted = true;
  }

  /**
   * Renders the latest solved physics geometry and telemetry.
   * Renderer must NOT re-solve physics equations.
   * @param {import('@engine/core/types.js').RuntimeOutput} runtimeOutput
   */
  render(runtimeOutput) {
    this.runtimeOutput = runtimeOutput;
  }

  /**
   * Resizes viewport renderer and syncs coordinate mapper.
   * @param {import('@engine/core/coordinateMapper.js').CoordinateMapper} coordinateMapper
   */
  resize(coordinateMapper) {
    this.coordinateMapper = coordinateMapper;
  }

  /**
   * Resets renderer visual handles and animations to initial state.
   */
  reset() {}

  /**
   * Disposes DOM elements, listeners, and animation loops.
   */
  dispose() {
    this.container = null;
    this.sourceImage = null;
    this.scene = null;
    this.coordinateMapper = null;
    this.onInteract = null;
    this.runtimeOutput = null;
    this.mounted = false;
  }
}

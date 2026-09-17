/**
 * engine/optics/OpticsAdapter.js
 * 
 * SimulationAdapter wrapping existing optics solvers:
 * - Thin Lens Engine (solveThinLens)
 * - Mirror Engine (solveMirror)
 * - Prism Engine (solvePrismRefraction)
 * - Snell Interface Engine (traceInterfaceRefraction)
 * and P5OpticsView.
 */

import { SimulationAdapter } from '../core/SimulationAdapter.js';
import { solveThinLens } from './thinLensEngine.js';
import { solveMirror } from './mirrorEngine.js';
import { solvePrismRefraction } from './prismEngine.js';
import { traceInterfaceRefraction } from './snellInterfaceEngine.js';

export class OpticsAdapter extends SimulationAdapter {
  constructor() {
    super();
    this.view = null;
    this.model = null;
    this.solution = null;
    this.subtype = 'thin_lens';
    this.focalLength = 130;
    this.lensX = 400;
    this.axisY = 300;
    this.objectX = 140;
    this.objectHeight = -80;
    this.sourceWidth = 800;
    this.sourceHeight = 600;
  }

  static canHandle(scene) {
    const domain = scene?.domain || scene?.simulation?.domain || scene?.simulation_type;
    return domain === 'optics';
  }

  canHandle(scene) {
    return OpticsAdapter.canHandle(scene);
  }

  async initialize(scene, container, options = {}) {
    await super.initialize(scene, container, options);

    this.sourceWidth = scene.coordinateSystem?.width || scene.source?.width || 800;
    this.sourceHeight = scene.coordinateSystem?.height || scene.source?.height || 600;
    this.axisY = scene.geometry?.axisY || Math.round(this.sourceHeight * 0.5);
    this.lensX = scene.geometry?.lensX || Math.round(this.sourceWidth * 0.5);

    this.subtype = scene.type || scene.simulation?.subtype || 'thin_lens';

    // Read initial parameters
    const params = scene.parameters || {};
    this.focalLength = Number(params.focalLength?.value ?? 130);
    const objectDist = Number(params.objectDistance?.value ?? 260);
    this.objectX = this.lensX - objectDist;
    this.objectHeight = Number(params.objectHeight?.value ?? -80);

    this._buildInternalModel();
    this.solve();

    // Mount P5OpticsView only if in browser environment
    if (typeof window !== 'undefined' && container) {
      try {
        const { P5OpticsView } = await import('../../apps/web/src/features/simulations/optics/view/p5OpticsView.js');
        this.view = new P5OpticsView(container, {
          onDragLens: (x, h) => this.setObjectPosition(x, h),
          onDragMirror: (x, h) => this.setObjectPosition(x, h),
          onDragPrism: (x, y) => this.setLightSourcePosition(x, y),
          onDragInterface: (x, y) => this.setLightSourcePosition(x, y),
        });
        this.view.render(this.model, this.solution);
      } catch (err) {
        console.warn('[OpticsAdapter] Could not initialize P5OpticsView:', err);
      }
    }

    this.notifyStateChange(this.getState());
  }

  _buildInternalModel() {
    this.model = {
      subtype: this.subtype,
      sourceWidth: this.sourceWidth,
      sourceHeight: this.sourceHeight,
      axisY: this.axisY,
      lens: {
        x: this.lensX,
        y: this.axisY,
        focalLength: this.focalLength,
        lensType: this.focalLength < 0 ? 'concave' : 'convex'
      },
      mirror: {
        x: this.lensX,
        y: this.axisY,
        focalLength: this.focalLength,
        mirrorType: this.focalLength < 0 ? 'convex' : 'concave'
      },
      object: {
        x: this.objectX,
        height: this.objectHeight
      },
      lightSource: {
        x: this.objectX,
        y: this.axisY + this.objectHeight
      }
    };
  }

  solve() {
    const bounds = {
      minX: 0,
      minY: 0,
      maxX: this.sourceWidth,
      maxY: this.sourceHeight,
      width: this.sourceWidth,
      height: this.sourceHeight
    };

    if (this.subtype === 'mirror') {
      this.solution = solveMirror({
        mirrorX: this.lensX,
        axisY: this.axisY,
        objectX: this.objectX,
        objectHeight: this.objectHeight,
        focalLength: this.focalLength,
        mirrorType: this.focalLength < 0 ? 'convex' : 'concave',
        bounds
      });
    } else {
      // Default thin lens
      this.solution = solveThinLens({
        lensX: this.lensX,
        axisY: this.axisY,
        objectX: this.objectX,
        objectHeight: this.objectHeight,
        focalLength: this.focalLength,
        bounds
      });
    }

    if (this.view && this.model) {
      this.view.render(this.model, this.solution);
    }
  }

  setObjectPosition(x, height = null) {
    this.objectX = x;
    if (height != null) this.objectHeight = height;

    const u = Math.round(this.lensX - this.objectX);
    this.setParameter('objectDistance', u);
    if (height != null) {
      this.setParameter('objectHeight', Math.round(height));
    }

    if (this.model?.object) {
      this.model.object.x = this.objectX;
      if (height != null) this.model.object.height = this.objectHeight;
    }

    this.solve();
    this.notifyStateChange(this.getState());
  }

  setLightSourcePosition(x, y) {
    if (this.model?.lightSource) {
      this.model.lightSource.x = x;
      this.model.lightSource.y = y;
    }
    this.solve();
    this.notifyStateChange(this.getState());
  }

  play() {
    super.play();
    this.notifyStateChange(this.getState());
  }

  pause() {
    super.pause();
    this.notifyStateChange(this.getState());
  }

  reset() {
    super.reset();
    const origF = this.scene?.parameters?.focalLength?.value ?? 130;
    const origU = this.scene?.parameters?.objectDistance?.value ?? 260;
    const origH = this.scene?.parameters?.objectHeight?.value ?? -80;

    this.focalLength = Number(origF);
    this.objectX = this.lensX - Number(origU);
    this.objectHeight = Number(origH);

    this._buildInternalModel();
    this.solve();
    this.notifyStateChange(this.getState());
  }

  setParameter(name, value) {
    super.setParameter(name, value);
    const numVal = Number(value);

    if (name === 'focalLength') {
      this.focalLength = numVal;
      if (this.model?.lens) this.model.lens.focalLength = numVal;
      if (this.model?.mirror) this.model.mirror.focalLength = numVal;
    } else if (name === 'objectDistance') {
      this.objectX = this.lensX - numVal;
      if (this.model?.object) this.model.object.x = this.objectX;
    } else if (name === 'objectHeight') {
      this.objectHeight = numVal;
      if (this.model?.object) this.model.object.height = numVal;
    }

    this.solve();
    this.notifyStateChange(this.getState());
  }

  getState() {
    return {
      domain: 'optics',
      type: this.subtype,
      running: this.running,
      focalLength: Number(this.focalLength.toFixed(1)),
      u: Number((this.solution?.u ?? (this.lensX - this.objectX)).toFixed(1)),
      v: Number.isFinite(this.solution?.v) ? Number(this.solution.v.toFixed(1)) : 'Infinity',
      magnification: Number.isFinite(this.solution?.magnification) ? Number(this.solution.magnification.toFixed(2)) : 'Infinity',
      imageType: this.solution?.imageType || 'real_same_size',
      isReal: Boolean(this.solution?.isReal),
      isInverted: Boolean(this.solution?.isInverted),
      rayCount: this.solution?.rays?.length || 0
    };
  }

  resize(width, height) {
    this.view?.resize?.();
  }

  destroy() {
    this.view?.destroy();
    this.view = null;
    this.model = null;
    this.solution = null;
    super.destroy();
  }
}

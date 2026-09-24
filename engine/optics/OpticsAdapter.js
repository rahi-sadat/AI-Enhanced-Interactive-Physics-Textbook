/**
 * engine/optics/OpticsAdapter.js
 * 
 * Pure mathematical simulation adapter for the optics domain:
 * - Thin Lens Engine (solveThinLens)
 * - Spherical Mirror Engine (solveMirror)
 * - Snell Interface Engine (traceInterfaceRefraction)
 * - Prism Engine (solvePrismRefraction)
 * Completely decoupled from frontend rendering views.
 * Strictly adheres to zero fabrication: missing physical evidence throws typed errors.
 */

import { SimulationAdapter } from '../core/SimulationAdapter.js';
import { solveThinLens } from './thinLensEngine.js';
import { solveMirror } from './mirrorEngine.js';
import { solvePrismRefraction } from './prismEngine.js';
import { traceInterfaceRefraction } from './snellInterfaceEngine.js';
import {
  UnsupportedPhysicsSubtypeError,
  PhysicsSceneValidationError,
  MissingRequiredParameterError
} from '../core/errors.js';
import { getParameterInUnit } from '../core/units.js';

export class OpticsAdapter extends SimulationAdapter {
  static domain = 'optics';

  constructor() {
    super();
    this.subtype = 'thin_lens';
    this.solution = null;
    this.model = null;

    // Numerical state variables
    this.sourceWidth = null;
    this.sourceHeight = null;
    this.axisY = null;
    this.lensX = null;
    this.focalLength = null;
    this.objectX = null;
    this.objectHeight = null;
  }

  static canHandle(scene) {
    const domain = scene?.domain;
    return domain === 'optics';
  }

  canHandle(scene) {
    return OpticsAdapter.canHandle(scene);
  }

  async initialize(scene, container = null, options = {}) {
    await super.initialize(scene, container, options);
    if (!scene.subtype) {
      throw new PhysicsSceneValidationError([{
        code: 'MISSING_SUBTYPE',
        path: 'subtype',
        message: 'Optics scene must explicitly declare a canonical subtype.'
      }]);
    }
    this.subtype = scene.subtype;

    const cs = scene.coordinateSpace;
    if (!cs) {
      throw new MissingRequiredParameterError('coordinateSpace', 'coordinateSpace');
    }

    if (cs.type === 'source_px' || cs.type === 'local') {
      if (!Number.isFinite(cs.width) || cs.width <= 0) {
        throw new MissingRequiredParameterError('coordinateSpace.width', 'coordinateSpace.width');
      }
      if (!Number.isFinite(cs.height) || cs.height <= 0) {
        throw new MissingRequiredParameterError('coordinateSpace.height', 'coordinateSpace.height');
      }
      this.sourceWidth = cs.width;
      this.sourceHeight = cs.height;
    } else if (cs.type === 'world') {
      if (!cs.bounds || !Number.isFinite(cs.bounds.maxX) || cs.bounds.maxX <= 0) {
        throw new MissingRequiredParameterError('coordinateSpace.bounds.maxX', 'coordinateSpace.bounds.maxX');
      }
      if (!Number.isFinite(cs.bounds.maxY) || cs.bounds.maxY <= 0) {
        throw new MissingRequiredParameterError('coordinateSpace.bounds.maxY', 'coordinateSpace.bounds.maxY');
      }
      this.sourceWidth = cs.bounds.maxX;
      this.sourceHeight = cs.bounds.maxY;
    }

    this.solve();
    this.notifyStateChange(this.getState());
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

    switch (this.subtype) {
      case 'thin_lens':
        return this._solveThinLens(bounds);
      case 'spherical_mirror':
      case 'mirror':
        return this._solveMirror(bounds);
      case 'interface_refraction':
        return this._solveInterfaceRefraction(bounds);
      case 'prism':
        return this._solvePrism(bounds);
      default:
        throw new UnsupportedPhysicsSubtypeError('optics', this.subtype || 'unknown');
    }
  }

  _solveThinLens(bounds) {
    const geom = this.scene.geometry || {};
    const lensEl = this.scene.objects?.find(e => e.optics?.model === 'thin_lens');

    if (geom.axisY !== undefined) {
      this.axisY = Number(geom.axisY);
    } else if (lensEl?.optics?.center?.y !== undefined) {
      this.axisY = Number(lensEl.optics.center.y);
    } else {
      throw new MissingRequiredParameterError('axisY', 'geometry.axisY or objects[0].optics.center.y');
    }

    if (geom.lensX !== undefined) {
      this.lensX = Number(geom.lensX);
    } else if (lensEl?.optics?.center?.x !== undefined) {
      this.lensX = Number(lensEl.optics.center.x);
    } else {
      throw new MissingRequiredParameterError('lensX', 'geometry.lensX or objects[0].optics.center.x');
    }

    // Extract focalLength
    if (this.focalLength === null) {
      if (this.scene.parameters?.focalLength) {
        this.focalLength = Number(this.scene.parameters.focalLength.value);
      } else if (lensEl?.optics?.focal_length_px?.value !== undefined) {
        this.focalLength = Number(lensEl.optics.focal_length_px.value);
      } else {
        throw new MissingRequiredParameterError('focalLength', 'parameters.focalLength');
      }
    }

    // Extract objectDistance and objectHeight
    if (this.objectX === null) {
      if (this.scene.parameters?.objectDistance) {
        const u = Number(this.scene.parameters.objectDistance.value);
        this.objectX = this.lensX - u;
      } else {
        const arrowEl = this.scene.objects?.find(e => e.optics?.model === 'optical_object');
        if (arrowEl?.optics?.base?.x !== undefined) {
          this.objectX = Number(arrowEl.optics.base.x);
        } else {
          throw new MissingRequiredParameterError('objectDistance', 'parameters.objectDistance');
        }
      }
    }

    if (this.objectHeight === null) {
      if (this.scene.parameters?.objectHeight) {
        this.objectHeight = Number(this.scene.parameters.objectHeight.value);
      } else {
        const arrowEl = this.scene.objects?.find(e => e.optics?.model === 'optical_object');
        if (arrowEl?.optics?.height_px !== undefined) {
          this.objectHeight = -Math.abs(Number(arrowEl.optics.height_px));
        } else {
          throw new MissingRequiredParameterError('objectHeight', 'parameters.objectHeight');
        }
      }
    }

    this.solution = solveThinLens({
      lensX: this.lensX,
      axisY: this.axisY,
      objectX: this.objectX,
      objectHeight: this.objectHeight,
      focalLength: this.focalLength,
      bounds
    });
  }

  _solveMirror(bounds) {
    const geom = this.scene.geometry || {};
    const mirrorEl = this.scene.objects?.find(e => e.optics?.model === 'mirror');

    if (geom.axisY !== undefined) {
      this.axisY = Number(geom.axisY);
    } else if (mirrorEl?.optics?.center?.y !== undefined) {
      this.axisY = Number(mirrorEl.optics.center.y);
    } else {
      throw new MissingRequiredParameterError('axisY', 'geometry.axisY or objects[0].optics.center.y');
    }

    if (geom.mirrorX !== undefined) {
      this.lensX = Number(geom.mirrorX);
    } else if (geom.lensX !== undefined) {
      this.lensX = Number(geom.lensX);
    } else if (mirrorEl?.optics?.center?.x !== undefined) {
      this.lensX = Number(mirrorEl.optics.center.x);
    } else {
      throw new MissingRequiredParameterError('mirrorX', 'geometry.mirrorX or objects[0].optics.center.x');
    }

    let mirrorType = 'concave';
    if (this.scene.parameters?.mirrorType?.value) {
      mirrorType = String(this.scene.parameters.mirrorType.value);
    } else if (mirrorEl?.optics?.mirrorType) {
      mirrorType = mirrorEl.optics.mirrorType;
    }

    if (this.focalLength === null) {
      if (this.scene.parameters?.focalLength) {
        this.focalLength = Number(this.scene.parameters.focalLength.value);
      } else if (mirrorType !== 'plane') {
        throw new MissingRequiredParameterError('focalLength', 'parameters.focalLength');
      } else {
        this.focalLength = Infinity;
      }
    }

    if (this.objectX === null) {
      if (this.scene.parameters?.objectDistance) {
        const u = Number(this.scene.parameters.objectDistance.value);
        this.objectX = this.lensX - u;
      } else {
        throw new MissingRequiredParameterError('objectDistance', 'parameters.objectDistance');
      }
    }

    if (this.objectHeight === null) {
      if (this.scene.parameters?.objectHeight) {
        this.objectHeight = Number(this.scene.parameters.objectHeight.value);
      } else {
        const arrowEl = this.scene.objects?.find(e => e.optics?.model === 'optical_object');
        if (arrowEl?.optics?.height_px !== undefined) {
          this.objectHeight = -Math.abs(Number(arrowEl.optics.height_px));
        } else {
          throw new MissingRequiredParameterError('objectHeight', 'parameters.objectHeight');
        }
      }
    }

    this.solution = solveMirror({
      mirrorType,
      mirrorX: this.lensX,
      axisY: this.axisY,
      objectX: this.objectX,
      objectHeight: this.objectHeight,
      focalLength: this.focalLength,
      bounds
    });
  }

  _solveInterfaceRefraction(bounds) {
    const geom = this.scene.geometry || {};
    const boundEl = this.scene.objects?.find(e => e.optics?.model === 'interface_boundary');

    let boundaryY = null;
    if (geom.boundaryY !== undefined) {
      boundaryY = Number(geom.boundaryY);
    } else if (boundEl?.optics?.boundaryY !== undefined) {
      boundaryY = Number(boundEl.optics.boundaryY);
    } else {
      throw new MissingRequiredParameterError('boundaryY', 'geometry.boundaryY or objects[0].optics.boundaryY');
    }

    let normalX = null;
    if (geom.normalX !== undefined) {
      normalX = Number(geom.normalX);
    } else if (boundEl?.optics?.normalX !== undefined) {
      normalX = Number(boundEl.optics.normalX);
    } else {
      throw new MissingRequiredParameterError('normalX', 'geometry.normalX or objects[0].optics.normalX');
    }

    let n1 = null;
    if (this.scene.parameters?.n1?.value !== undefined) {
      n1 = Number(this.scene.parameters.n1.value);
    } else if (boundEl?.optics?.medium1?.n !== undefined) {
      n1 = Number(boundEl.optics.medium1.n);
    } else {
      throw new MissingRequiredParameterError('n1', 'parameters.n1.value or objects[0].optics.medium1.n');
    }

    let n2 = null;
    if (this.scene.parameters?.n2?.value !== undefined) {
      n2 = Number(this.scene.parameters.n2.value);
    } else if (boundEl?.optics?.medium2?.n !== undefined) {
      n2 = Number(boundEl.optics.medium2.n);
    } else {
      throw new MissingRequiredParameterError('n2', 'parameters.n2.value or objects[0].optics.medium2.n');
    }

    let source = null;
    const srcEl = this.scene.objects?.find(e => e.optics?.model === 'ray_source');
    if (srcEl?.optics?.position) {
      source = { x: Number(srcEl.optics.position.x), y: Number(srcEl.optics.position.y) };
    } else if (geom.sourcePosition) {
      source = { x: Number(geom.sourcePosition.x), y: Number(geom.sourcePosition.y) };
    } else if (this.scene.parameters?.theta1 !== undefined) {
      source = null; // traceInterfaceRefraction handles explicit theta1Deg
    } else {
      throw new MissingRequiredParameterError('sourcePosition', 'geometry.sourcePosition or objects[0].optics.position');
    }

    this.solution = traceInterfaceRefraction({
      boundaryY,
      normalX,
      n1,
      n2,
      source,
      theta1Deg: this.scene.parameters?.theta1?.value !== undefined ? Number(this.scene.parameters.theta1.value) : undefined,
      bounds
    });
  }

  _solvePrism(bounds) {
    const geom = this.scene.geometry || {};
    let prismVertices = geom.prismVertices;

    if (!prismVertices) {
      const prismEl = this.scene.objects?.find(e => e.optics?.model === 'prism');
      if (prismEl?.optics?.vertices) {
        prismVertices = prismEl.optics.vertices;
      }
    }

    if (!Array.isArray(prismVertices) || prismVertices.length < 3) {
      throw new MissingRequiredParameterError('prismVertices', 'geometry.prismVertices or objects[0].optics.vertices');
    }

    let n = null;
    if (this.scene.parameters?.refractiveIndex?.value !== undefined) {
      n = Number(this.scene.parameters.refractiveIndex.value);
    } else if (this.scene.parameters?.n?.value !== undefined) {
      n = Number(this.scene.parameters.n.value);
    } else {
      const prismEl = this.scene.objects?.find(e => e.optics?.model === 'prism');
      if (prismEl?.optics?.refractiveIndex !== undefined) {
        n = Number(prismEl.optics.refractiveIndex);
      } else {
        throw new MissingRequiredParameterError('refractiveIndex', 'parameters.refractiveIndex.value or objects[0].optics.refractiveIndex');
      }
    }

    let rayOrigin = geom.rayOrigin;
    let rayDirection = geom.rayDirection;

    if (!rayOrigin || !Number.isFinite(rayOrigin.x) || !Number.isFinite(rayOrigin.y)) {
      throw new MissingRequiredParameterError('rayOrigin', 'geometry.rayOrigin');
    }
    if (!rayDirection || !Number.isFinite(rayDirection.x) || !Number.isFinite(rayDirection.y)) {
      throw new MissingRequiredParameterError('rayDirection', 'geometry.rayDirection');
    }

    this.solution = solvePrismRefraction({
      prismVertices,
      refractiveIndex: n,
      rayOrigin,
      rayDirection,
      bounds
    });
    if (this.solution && !this.solution.rays && this.solution.segments) {
      this.solution.rays = this.solution.segments;
    }
  }

  reset() {
    super.reset();
    this.solve();
    this.notifyStateChange(this.getState());
  }

  /**
   * Internal hook called by SimulationAdapter after atomic validation, unit conversion,
   * and scene mutation succeed.
   */
  _applyParameterUpdate(address, convertedVal, key, targetId, incomingUnit) {
    if (key === 'focalLength') {
      this.focalLength = convertedVal;
    } else if (key === 'objectDistance') {
      this.objectX = this.lensX - convertedVal;
    } else if (key === 'objectHeight') {
      this.objectHeight = convertedVal;
    }

    this.solve();
    this.notifyStateChange(this.getState());
  }

  getOutput() {
    return {
      domain: 'optics',
      subtype: this.subtype,
      time: 0.0,
      state: this.getState(),
      geometry: this.solution || {},
      telemetry: this.solution || {},
      events: [],
      editableParameters: this.getParameters()
    };
  }

  getState() {
    return {
      domain: 'optics',
      subtype: this.subtype,
      type: this.subtype,
      running: this.running,
      focalLength: this.focalLength !== null ? Number(this.focalLength.toFixed(1)) : null,
      u: this.solution?.u !== undefined ? Number(this.solution.u.toFixed(1)) : null,
      v: Number.isFinite(this.solution?.v) ? Number(this.solution.v.toFixed(1)) : 'Infinity',
      magnification: Number.isFinite(this.solution?.magnification) ? Number(this.solution.magnification.toFixed(2)) : 'Infinity',
      imageType: this.solution?.imageType || null,
      isReal: Boolean(this.solution?.isReal),
      isInverted: Boolean(this.solution?.isInverted),
      rayCount: this.solution?.rays?.length || this.solution?.segments?.length || 0,
      solution: this.solution
    };
  }

  dispose() {
    this.solution = null;
    this.model = null;
    super.dispose();
  }
}

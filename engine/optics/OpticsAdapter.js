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
  MissingRequiredParameterError,
  MissingCalibrationError
} from '../core/errors.js';
import { getParameterInUnit, convertUnit } from '../core/units.js';

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
    this.pixelsPerUnit = 1.0;
    this.calibration = { pixelsPerUnit: 1.0, unit: 'px' };
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

    // Check if any parameter uses physical distance units (cm, m, mm, etc.)
    const physicalUnits = new Set(['cm', 'm', 'mm', 'in', 'ft']);
    let hasPhysicalParam = false;
    let physicalUnit = null;
    let physicalParamKey = null;

    if (scene.parameters) {
      for (const [k, p] of Object.entries(scene.parameters)) {
        if (p?.unit && physicalUnits.has(String(p.unit).toLowerCase())) {
          hasPhysicalParam = true;
          physicalUnit = p.unit;
          physicalParamKey = k;
          break;
        }
      }
    }

    // Extract calibration scale and unit if provided (pixels per physical unit, e.g. px/cm)
    let ppu = null;
    let calibUnit = null;
    const csLegacy = scene.coordinateSystem || {};
    const calib = cs.calibration || csLegacy.calibration || scene.calibration;

    if (calib?.pixels_per_cm !== undefined && Number.isFinite(Number(calib.pixels_per_cm)) && Number(calib.pixels_per_cm) > 0) {
      ppu = Number(calib.pixels_per_cm);
      calibUnit = 'cm';
    } else if (calib?.pixels_per_meter !== undefined && Number.isFinite(Number(calib.pixels_per_meter)) && Number(calib.pixels_per_meter) > 0) {
      ppu = Number(calib.pixels_per_meter);
      calibUnit = 'm';
    } else if (cs.pixelsPerUnit !== undefined && Number.isFinite(Number(cs.pixelsPerUnit)) && Number(cs.pixelsPerUnit) > 0) {
      ppu = Number(cs.pixelsPerUnit);
      calibUnit = cs.unit || cs.physicalUnit || calib?.unit || null;
    } else if (csLegacy.pixelsPerUnit !== undefined && Number.isFinite(Number(csLegacy.pixelsPerUnit)) && Number(csLegacy.pixelsPerUnit) > 0) {
      ppu = Number(csLegacy.pixelsPerUnit);
      calibUnit = csLegacy.unit || csLegacy.physicalUnit || calib?.unit || null;
    } else if (calib?.pixelsPerUnit !== undefined && Number.isFinite(Number(calib.pixelsPerUnit)) && Number(calib.pixelsPerUnit) > 0) {
      ppu = Number(calib.pixelsPerUnit);
      calibUnit = calib.unit || null;
    } else {
      const fRes = this._resolveFocalLengthParam();
      const lensEl = scene.objects?.find(e => e.optics?.model === 'thin_lens');
      if (fRes?.param?.unit && physicalUnits.has(String(fRes.param.unit).toLowerCase()) && lensEl?.optics?.focal_length_px?.value) {
        ppu = Number(lensEl.optics.focal_length_px.value) / Number(fRes.param.value);
        calibUnit = String(fRes.param.unit).toLowerCase();
      }
    }

    // Never silently default to 1.0 for physical units without calibration evidence
    if (hasPhysicalParam) {
      if (!ppu || !Number.isFinite(ppu) || ppu <= 0) {
        throw new MissingCalibrationError(physicalUnit, physicalParamKey);
      }
      calibUnit = calibUnit || physicalUnit;
      this.calibration = { pixelsPerUnit: ppu, unit: calibUnit };
      this.pixelsPerUnit = ppu;
    } else {
      this.calibration = { pixelsPerUnit: (Number.isFinite(ppu) && ppu > 0) ? ppu : 1.0, unit: calibUnit || 'px' };
      this.pixelsPerUnit = this.calibration.pixelsPerUnit;
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

  _resolveFocalLengthParam() {
    if (this.scene?.parameters?.focalLength) {
      return { key: 'focalLength', address: 'focalLength', param: this.scene.parameters.focalLength };
    }
    const lensEntity = this.scene?.objects?.find(e => e.optics?.model === 'thin_lens' || e.optics?.model === 'lens' || e.optics?.model === 'mirror');
    if (lensEntity && this.scene?.parameters?.[`${lensEntity.id}.focalLength`]) {
      return { key: 'focalLength', address: `${lensEntity.id}.focalLength`, param: this.scene.parameters[`${lensEntity.id}.focalLength`] };
    }
    if (this.scene?.parameters) {
      for (const [k, v] of Object.entries(this.scene.parameters)) {
        if (k.endsWith('.focalLength')) {
          return { key: 'focalLength', address: k, param: v };
        }
      }
    }
    return null;
  }

  _resolveObjectDistanceParam() {
    if (this.scene?.parameters?.objectDistance) {
      return { key: 'objectDistance', address: 'objectDistance', param: this.scene.parameters.objectDistance };
    }
    const objEntity = this.scene?.objects?.find(e => e.optics?.model === 'optical_object' || e.type === 'optical_object' || e.type === 'object');
    if (objEntity && this.scene?.parameters?.[`${objEntity.id}.objectDistance`]) {
      return { key: 'objectDistance', address: `${objEntity.id}.objectDistance`, param: this.scene.parameters[`${objEntity.id}.objectDistance`] };
    }
    if (this.scene?.parameters) {
      for (const [k, v] of Object.entries(this.scene.parameters)) {
        if (k.endsWith('.objectDistance')) {
          return { key: 'objectDistance', address: k, param: v };
        }
      }
    }
    return null;
  }

  _resolveObjectHeightParam() {
    if (this.scene?.parameters?.objectHeight) {
      return { key: 'objectHeight', address: 'objectHeight', param: this.scene.parameters.objectHeight };
    }
    const objEntity = this.scene?.objects?.find(e => e.optics?.model === 'optical_object' || e.type === 'optical_object' || e.type === 'object');
    if (objEntity && this.scene?.parameters?.[`${objEntity.id}.objectHeight`]) {
      return { key: 'objectHeight', address: `${objEntity.id}.objectHeight`, param: this.scene.parameters[`${objEntity.id}.objectHeight`] };
    }
    if (this.scene?.parameters) {
      for (const [k, v] of Object.entries(this.scene.parameters)) {
        if (k.endsWith('.objectHeight')) {
          return { key: 'objectHeight', address: k, param: v };
        }
      }
    }
    return null;
  }

  _paramToPixels(val, unit) {
    if (val === null || val === undefined) return null;
    const num = Number(val);
    if (!Number.isFinite(num)) return num;
    if (!unit || unit === 'px') return num;
    if (!this.calibration || !this.calibration.pixelsPerUnit) return num;

    const calibUnit = this.calibration.unit || unit;
    const valInCalibUnit = (unit === calibUnit) ? num : convertUnit(num, unit, calibUnit);
    return valInCalibUnit * this.calibration.pixelsPerUnit;
  }

  _pixelsToParam(px, targetUnit) {
    if (px === null || px === undefined) return null;
    const num = Number(px);
    if (!Number.isFinite(num)) return num;
    if (!targetUnit || targetUnit === 'px') return num;
    if (!this.calibration || !this.calibration.pixelsPerUnit) return num;

    const calibUnit = this.calibration.unit || targetUnit;
    const valInCalibUnit = num / this.calibration.pixelsPerUnit;
    const valInTarget = (targetUnit === calibUnit) ? valInCalibUnit : convertUnit(valInCalibUnit, calibUnit, targetUnit);
    return Number(valInTarget.toFixed(2));
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

    // Extract focalLength in solver pixels (scaling by calibration if parameter is in physical unit)
    if (this.focalLength === null) {
      const fRes = this._resolveFocalLengthParam();
      if (fRes?.param?.value !== undefined) {
        this.focalLength = this._paramToPixels(fRes.param.value, fRes.param.unit);
      } else if (lensEl?.optics?.focal_length_px?.value !== undefined) {
        this.focalLength = Number(lensEl.optics.focal_length_px.value);
      } else {
        throw new MissingRequiredParameterError('focalLength', 'parameters.focalLength');
      }
    }

    // Extract objectDistance and objectHeight in solver pixels
    if (this.objectX === null) {
      const uRes = this._resolveObjectDistanceParam();
      if (uRes?.param?.value !== undefined) {
        const uPx = this._paramToPixels(uRes.param.value, uRes.param.unit);
        this.objectX = this.lensX - uPx;
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
      const hRes = this._resolveObjectHeightParam();
      if (hRes?.param?.value !== undefined) {
        const hPx = this._paramToPixels(hRes.param.value, hRes.param.unit);
        this.objectHeight = -Math.abs(hPx);
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
    } else if (geom.poleX !== undefined) {
      this.lensX = Number(geom.poleX);
    } else if (geom.lensX !== undefined) {
      this.lensX = Number(geom.lensX);
    } else if (mirrorEl?.optics?.center?.x !== undefined) {
      this.lensX = Number(mirrorEl.optics.center.x);
    } else {
      throw new MissingRequiredParameterError('mirrorX', 'geometry.mirrorX, geometry.poleX, or objects[0].optics.center.x');
    }

    let mirrorType = null;
    if (this.scene.parameters?.mirrorType?.value) {
      mirrorType = String(this.scene.parameters.mirrorType.value);
    } else if (mirrorEl?.optics?.mirrorType) {
      mirrorType = mirrorEl.optics.mirrorType;
    } else if (geom.mirrorType) {
      mirrorType = geom.mirrorType;
    } else if (geom.isConcave !== undefined) {
      mirrorType = geom.isConcave ? 'concave' : 'convex';
    } else {
      throw new MissingRequiredParameterError('mirrorType', 'parameters.mirrorType, objects[0].optics.mirrorType, or geometry.mirrorType');
    }

    if (this.focalLength === null) {
      if (mirrorType === 'concave' || mirrorType === 'convex') {
        const fRes = this._resolveFocalLengthParam();
        if (fRes?.param?.value !== undefined) {
          this.focalLength = this._paramToPixels(fRes.param.value, fRes.param.unit);
        } else if (mirrorEl?.optics?.focal_length_px?.value !== undefined) {
          this.focalLength = Number(mirrorEl.optics.focal_length_px.value);
        } else {
          throw new MissingRequiredParameterError('focalLength', 'parameters.focalLength');
        }
      } else if (mirrorType !== 'plane') {
        throw new MissingRequiredParameterError('focalLength', 'parameters.focalLength');
      } else {
        this.focalLength = Infinity;
      }
    }

    if (this.objectX === null) {
      const uRes = this._resolveObjectDistanceParam();
      if (uRes?.param?.value !== undefined) {
        const uPx = this._paramToPixels(uRes.param.value, uRes.param.unit);
        this.objectX = this.lensX - uPx;
      } else {
        throw new MissingRequiredParameterError('objectDistance', 'parameters.objectDistance');
      }
    }

    if (this.objectHeight === null) {
      const hRes = this._resolveObjectHeightParam();
      if (hRes?.param?.value !== undefined) {
        const hPx = this._paramToPixels(hRes.param.value, hRes.param.unit);
        this.objectHeight = -Math.abs(hPx);
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
    } else if (geom.interfaceY !== undefined) {
      boundaryY = Number(geom.interfaceY);
    } else if (boundEl?.optics?.boundaryY !== undefined) {
      boundaryY = Number(boundEl.optics.boundaryY);
    } else {
      throw new MissingRequiredParameterError('boundaryY', 'geometry.boundaryY, geometry.interfaceY, or objects[0].optics.boundaryY');
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
    let prismVertices = geom.prismVertices || geom.vertices;

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

    if (!rayOrigin) {
      const srcEl = this.scene.objects?.find(e => e.optics?.model === 'ray_source');
      if (srcEl?.optics?.position) {
        rayOrigin = { x: Number(srcEl.optics.position.x), y: Number(srcEl.optics.position.y) };
      }
    }
    if (!rayDirection) {
      const srcEl = this.scene.objects?.find(e => e.optics?.model === 'ray_source');
      if (srcEl?.optics?.direction) {
        rayDirection = { x: Number(srcEl.optics.direction.x), y: Number(srcEl.optics.direction.y) };
      }
    }

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
    this.focalLength = null;
    this.objectX = null;
    this.objectHeight = null;
    this.solve();
    this.notifyStateChange(this.getState());
  }

  /**
   * Internal hook called by SimulationAdapter after atomic validation, unit conversion,
   * and scene mutation succeed.
   */
  _applyParameterUpdate(address, convertedVal, key, targetId, incomingUnit) {
    if (key === 'focalLength' || address.endsWith('focalLength')) {
      const fRes = this._resolveFocalLengthParam();
      const p = this.scene.parameters?.[address] || fRes?.param;
      const unit = p?.unit;
      this.focalLength = this._paramToPixels(convertedVal, unit);
      if (p) p.value = convertedVal;
    } else if (key === 'objectDistance' || address.endsWith('objectDistance')) {
      const uRes = this._resolveObjectDistanceParam();
      const p = this.scene.parameters?.[address] || uRes?.param;
      const unit = p?.unit;
      const uPx = this._paramToPixels(convertedVal, unit);
      this.objectX = this.lensX - uPx;
      if (p) p.value = convertedVal;
    } else if (key === 'objectHeight' || address.endsWith('objectHeight')) {
      const hRes = this._resolveObjectHeightParam();
      const p = this.scene.parameters?.[address] || hRes?.param;
      const unit = p?.unit;
      const hPx = this._paramToPixels(convertedVal, unit);
      this.objectHeight = -Math.abs(hPx);
      if (p) p.value = convertedVal;
    } else if (key === 'theta1' || address.endsWith('theta1')) {
      if (this.scene.parameters?.[address]) {
        this.scene.parameters[address].value = convertedVal;
      } else if (this.scene.parameters?.theta1) {
        this.scene.parameters.theta1.value = convertedVal;
      }
    } else if (key === 'n1' || key === 'n2') {
      if (this.scene.parameters?.[address]) {
        this.scene.parameters[address].value = convertedVal;
      } else if (this.scene.parameters?.[key]) {
        this.scene.parameters[key].value = convertedVal;
      }
    } else if (key === 'refractiveIndex' || key === 'n') {
      if (this.scene.parameters?.[address]) {
        this.scene.parameters[address].value = convertedVal;
      } else if (this.scene.parameters?.refractiveIndex) {
        this.scene.parameters.refractiveIndex.value = convertedVal;
      } else if (this.scene.parameters?.n) {
        this.scene.parameters.n.value = convertedVal;
      }
    }

    this.solve();
    this.notifyStateChange(this.getState());
  }

  getOutput() {
    const sol = this.solution || {};
    const f = this.focalLength;
    const ax = this.axisY;
    const lx = this.lensX;
    const ox = this.objectX;
    const oh = this.objectHeight;
    const hasGeometry = ax !== null && lx !== null;

    let landmarks = {};
    if (hasGeometry && this.subtype === 'thin_lens') {
      landmarks = {
        lensCenter: { x: lx, y: ax },
        focalPoints: [
          { id: 'f1', label: 'F₁', x: lx - f, y: ax },
          { id: 'f2', label: 'F₂', x: lx + f, y: ax },
          { id: '2f1', label: '2F₁', x: lx - 2 * f, y: ax },
          { id: '2f2', label: '2F₂', x: lx + 2 * f, y: ax }
        ]
      };
    } else if (hasGeometry && (this.subtype === 'mirror' || this.subtype === 'spherical_mirror')) {
      landmarks = {
        pole: { x: lx, y: ax, label: 'P' },
        focus: { x: lx - f, y: ax, label: 'F' },
        center: { x: lx - 2 * f, y: ax, label: 'C' },
        focalPoints: [
          { id: 'f', label: 'F', x: lx - f, y: ax },
          { id: 'c', label: 'C', x: lx - 2 * f, y: ax }
        ]
      };
    }

    const hasImage = Number.isFinite(sol.imageX) && Number.isFinite(sol.imageHeight) && hasGeometry;
    const image = hasImage ? {
      x: sol.imageX,
      height: sol.imageHeight,
      isReal: Boolean(sol.isReal),
      isInverted: Boolean(sol.isInverted),
      magnification: sol.magnification,
      base: { x: sol.imageX, y: ax },
      tip: { x: sol.imageX, y: ax + sol.imageHeight }
    } : null;

    const object = (hasGeometry && ox !== null && oh !== null && (this.subtype === 'thin_lens' || this.subtype === 'mirror' || this.subtype === 'spherical_mirror')) ? {
      x: ox,
      height: oh,
      base: { x: ox, y: ax },
      tip: { x: ox, y: ax + oh }
    } : null;

    const objEntity = this.scene.objects?.find(e => e.optics?.model === 'optical_object' || e.type === 'optical_object' || e.type === 'object');
    const uRes = this._resolveObjectDistanceParam();
    const hRes = this._resolveObjectHeightParam();
    const fRes = this._resolveFocalLengthParam();

    const uParam = uRes?.param || (uRes?.address ? this.scene.parameters?.[uRes.address] : null);
    const hParam = hRes?.param || (hRes?.address ? this.scene.parameters?.[hRes.address] : null);
    const fParam = fRes?.param || (this.scene.parameters?.focalLength ? this.scene.parameters.focalLength : null);

    const objTargetId = objEntity?.id || uParam?.targetId || hParam?.targetId || (uRes?.address && uRes.address.includes('.') ? uRes.address.split('.')[0] : (hRes?.address && hRes.address.includes('.') ? hRes.address.split('.')[0] : null));
    const uParamAddress = uRes?.address || (objTargetId && this.scene.parameters?.[`${objTargetId}.objectDistance`] ? `${objTargetId}.objectDistance` : (this.scene.parameters?.objectDistance ? 'objectDistance' : null));
    const hParamAddress = hRes?.address || (objTargetId && this.scene.parameters?.[`${objTargetId}.objectHeight`] ? `${objTargetId}.objectHeight` : (this.scene.parameters?.objectHeight ? 'objectHeight' : null));

    const isUEditable = Boolean((uParam?.editable === true || objEntity?.editable === true) && uParamAddress);
    const isHEditable = Boolean((hParam?.editable === true || objEntity?.editable === true) && hParamAddress);

    const uUnit = uParam?.unit || 'px';
    const hUnit = hParam?.unit || 'px';
    const fUnit = fParam?.unit || 'px';

    const ppuU = this._paramToPixels(1, uUnit);
    const ppuH = this._paramToPixels(1, hUnit);

    const handles = {};
    if (object && objTargetId && (isUEditable || isHEditable)) {
      handles.objectArrow = {
        id: objTargetId,
        targetId: objTargetId,
        type: 'drag',
        x: ox,
        y: ax + oh,
        lensX: lx,
        axisY: ax,
        pixelsPerUnit: ppuU,
        axes: {
          x: {
            parameter: uParamAddress,
            parameterKey: 'objectDistance',
            editable: isUEditable,
            unit: uUnit,
            pixelsPerUnit: ppuU,
            min: uParam?.control?.min ?? (uParam?.min !== undefined ? uParam.min : null),
            max: uParam?.control?.max ?? (uParam?.max !== undefined ? uParam.max : null),
            step: uParam?.control?.step ?? (uParam?.step !== undefined ? uParam.step : null)
          },
          y: {
            parameter: hParamAddress,
            parameterKey: 'objectHeight',
            editable: isHEditable,
            unit: hUnit,
            pixelsPerUnit: ppuH,
            min: hParam?.control?.min ?? (hParam?.min !== undefined ? hParam.min : null),
            max: hParam?.control?.max ?? (hParam?.max !== undefined ? hParam.max : null),
            step: hParam?.control?.step ?? (hParam?.step !== undefined ? hParam.step : null)
          }
        }
      };
    }

    // Interface refraction handles (only when explicitly editable, with targetId and parameter address)
    const ifaceObj = this.scene.objects?.find(o => o.type === 'interface' || o.type === 'boundary');
    const ifaceTargetId = ifaceObj?.id;
    const theta1Address = ifaceTargetId && this.scene.parameters?.[`${ifaceTargetId}.theta1`] ? `${ifaceTargetId}.theta1` : (this.scene.parameters?.theta1 ? 'theta1' : null);
    const theta1Param = theta1Address ? this.scene.parameters?.[theta1Address] : null;
    const isTheta1Editable = Boolean(theta1Param?.editable === true || ifaceObj?.editable === true);

    if (this.subtype === 'interface_refraction' && isTheta1Editable && ifaceTargetId && theta1Address) {
      handles.lightSource = {
        id: ifaceTargetId,
        targetId: ifaceTargetId,
        key: 'theta1',
        parameter: theta1Address,
        editable: true,
        unit: 'deg'
      };
    }

    let rays = sol.rays || sol.segments || [];
    if (this.subtype === 'interface_refraction' && (!rays || rays.length === 0)) {
      rays = [];
      if (sol.incidentRay) {
        rays.push({ id: 'incident_ray', points: sol.incidentRay.points || sol.incidentRay });
      }
      if (sol.refractedRay && !sol.isTIR) {
        rays.push({ id: 'refracted_ray', points: sol.refractedRay.points || sol.refractedRay });
      }
      if (sol.reflectedRay) {
        rays.push({ id: 'reflected_ray', points: sol.reflectedRay.points || sol.reflectedRay, isTIR: sol.isTIR });
      }
    }

    const opticalAxis = hasGeometry ? {
      y: ax,
      minX: 0,
      maxX: this.sourceWidth
    } : null;

    const lensGeom = (this.subtype === 'thin_lens' && hasGeometry) ? {
      x: lx,
      axisY: ax,
      focalLength: f,
      lensType: sol.lensType || (f < 0 ? 'concave' : 'convex'),
      apertureHeight: this.scene.geometry?.apertureHeight || this.scene.geometry?.aperture_px || null
    } : null;

    const mirrorGeom = ((this.subtype === 'mirror' || this.subtype === 'spherical_mirror') && hasGeometry) ? {
      x: lx,
      axisY: ax,
      focalLength: f,
      model: sol.mirrorType || this.scene.geometry?.mirrorType || null,
      curvatureRadius: this.scene.geometry?.curvatureRadius || (f !== null ? 2 * Math.abs(f) : null),
      apertureHeight: this.scene.geometry?.apertureHeight || this.scene.geometry?.aperture_px || null
    } : null;

    const geometry = {
      ...sol,
      opticalAxis,
      landmarks,
      lens: lensGeom,
      mirror: mirrorGeom,
      object,
      image,
      rays,
      prismPolygon: this.scene?.geometry?.prismVertices || this.scene?.geometry?.vertices || (this.scene?.objects?.find(e => e.optics?.model === 'prism')?.optics?.vertices),
      handles
    };

    const telemetry = {
      ...sol,
      imageDistance: Number.isFinite(sol.v) ? this._pixelsToParam(sol.v, uUnit) : 'Infinity',
      objectDistance: sol.u !== undefined ? this._pixelsToParam(sol.u, uUnit) : null,
      focalLength: f !== null ? this._pixelsToParam(f, fUnit) : null,
      refractedAngle_deg: sol.theta2Deg !== undefined ? sol.theta2Deg : sol.refractedAngle_deg,
      tir: sol.isTIR !== undefined ? sol.isTIR : Boolean(sol.tir)
    };

    return {
      domain: 'optics',
      subtype: this.subtype,
      time: 0.0,
      state: this.getState(),
      geometry,
      telemetry,
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

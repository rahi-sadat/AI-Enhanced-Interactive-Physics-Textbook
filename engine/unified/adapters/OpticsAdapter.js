/**
 * OpticsAdapter.js
 * 
 * Domain adapter for geometric and wave ray optics compiling diagram scenes into the UnifiedEngineCore.
 * Supports:
 *   1. Thin lenses (Gaussian formulation 1/v - 1/u = 1/f)
 *   2. Spherical & plane mirrors (1/u + 1/v = 1/f) with bidirectional orientation ('left' | 'right')
 *   3. Triangular & slab prisms with multiple face Snell refraction, TIR, and net deviation delta
 *   4. Planar media interface refraction & reflection
 * 
 * Invariant Rules:
 *   - Zero solving logic: delegates ray intersections & redirects to EventEngine and core.
 *   - No imports of other domain adapters — only shared core primitives.
 *   - Geometry and bounds are strictly in native source pixels (source_px).
 *   - Physical laws are explicitly commented on every equation.
 */

import { EventEngine } from '../core/EventEngine.js';

const EPSILON = 0.5;

export class OpticsAdapter {
  constructor() {
    this.core = null;
    this.subtype = 'thin_lens'; // 'thin_lens' | 'mirror' | 'prism' | 'interface_refraction'
    this.scene = null;

    // Optical element specifications
    this.lens = null;      // { x, y, focalLength, model: 'convex'|'concave' }
    this.mirror = null;    // { x, y, focalLength, model: 'concave'|'convex'|'plane', facing: 'left'|'right' }
    this.object = null;    // { x, height }
    this.prism = null;     // { vertices: [{x,y}], refractiveIndex }
    this.interface = null; // { boundaryY, normalX, n1, n2, source: {x,y}, target: {x,y} }
    this.lightSource = null;

    this.sourceWidth = 800;
    this.sourceHeight = 600;
    this.pixelPerCm = 7.0;

    this.solution = null;
  }

  attachCore(core) {
    this.core = core;
  }

  /**
   * Compiles canonical optics scene graph into boundary and parameter specifications.
   * @param {object} scene - Canonical PhysicsScene or compatible scene object
   * @returns {{ isAlgebraic: boolean, algebraicState: number[] }}
   */
  compileScene(scene) {
    this.scene = scene;

    this.sourceWidth = Number(scene.source?.width || scene.coordinateSystem?.width || scene.source?.image_width_px || 800);
    this.sourceHeight = Number(scene.source?.height || scene.coordinateSystem?.height || scene.source?.image_height_px || 600);
    this.pixelPerCm = Number(scene.coordinate_system?.calibration?.pixels_per_cm?.value ?? 7.0);

    const elements = scene.elements || scene.objects || [];
    const subtype = scene.simulation?.subtype || scene.type || 'thin_lens';
    this.subtype = subtype;

    const axisY = Number(scene.geometry?.optical_axis_y ?? (this.sourceHeight * 0.5));

    if (subtype === 'mirror' || elements.some(e => e.semantic_label?.includes('mirror'))) {
      this.subtype = 'mirror';
      const mEl = elements.find(e => e.semantic_label?.includes('mirror')) || {};
      const objEl = elements.find(e => e.semantic_label?.includes('object')) || {};

      const mirrorX = Number(mEl.optics?.optical_center?.x ?? mEl.geometry?.optical_center?.x ?? mEl.geometry?.position?.x ?? 600.0);
      const mirrorY = Number(mEl.optics?.optical_center?.y ?? mEl.geometry?.optical_center?.y ?? mEl.geometry?.position?.y ?? axisY);
      const rawFocal = mEl.optics?.focal_length_px?.value ?? mEl.optics?.focal_length_px ?? scene.parameters?.focalLength?.value ?? 140.0;
      const focalLength = Number(rawFocal);
      const model = mEl.optics?.model || (focalLength < 0 ? 'convex' : 'concave');
      const facing = mEl.optics?.facing || scene.parameters?.facing?.value || (objEl.geometry?.position?.x > mirrorX ? 'right' : 'left');

      const objectX = Number(objEl.optics?.base?.x ?? objEl.geometry?.position?.x ?? (facing === 'right' ? mirrorX + 250 : mirrorX - 250));
      const objectH = objEl.optics?.height_px ?? (objEl.optics?.tip && objEl.optics?.base ? objEl.optics.tip.y - objEl.optics.base.y : null);
      const objectHeight = Number(objectH ?? objEl.geometry?.height_px ?? scene.parameters?.objectHeight?.value ?? -85.0);

      this.mirror = { x: mirrorX, y: mirrorY, focalLength, model, facing };
      this.object = { x: objectX, height: objectHeight };
    } else if (subtype === 'prism' || elements.some(e => e.semantic_label?.includes('prism'))) {
      this.subtype = 'prism';
      const pEl = elements.find(e => e.semantic_label?.includes('prism')) || {};
      const srcEl = elements.find(e => e.semantic_label?.includes('source') || e.semantic_label?.includes('ray')) || {};

      const defaultVertices = [
        { x: this.sourceWidth * 0.5, y: this.sourceHeight * 0.2 },
        { x: this.sourceWidth * 0.3, y: this.sourceHeight * 0.75 },
        { x: this.sourceWidth * 0.7, y: this.sourceHeight * 0.75 }
      ];

      this.prism = {
        vertices: pEl.geometry?.vertices || defaultVertices,
        refractiveIndex: Number(pEl.optics?.refractive_index ?? scene.parameters?.refractiveIndex?.value ?? 1.52)
      };

      const sx = Number(srcEl.geometry?.position?.x ?? (this.sourceWidth * 0.15));
      const sy = Number(srcEl.geometry?.position?.y ?? (this.sourceHeight * 0.55));
      const tx = Number(srcEl.geometry?.target?.x ?? (this.sourceWidth * 0.42));
      const ty = Number(srcEl.geometry?.target?.y ?? (this.sourceHeight * 0.45));

      this.lightSource = { x: sx, y: sy, targetX: tx, targetY: ty };
    } else if (subtype === 'interface_refraction' || elements.some(e => e.semantic_label?.includes('interface'))) {
      this.subtype = 'interface_refraction';
      const bY = Number(scene.geometry?.boundary_y ?? (this.sourceHeight * 0.5));
      const nX = Number(scene.geometry?.normal_x ?? (this.sourceWidth * 0.5));
      const n1 = Number(scene.parameters?.n1?.value ?? 1.0);
      const n2 = Number(scene.parameters?.n2?.value ?? 1.83); // Calibrated NCTB diagram standard

      const sx = Number(scene.geometry?.source?.x ?? (this.sourceWidth * 0.25));
      const sy = Number(scene.geometry?.source?.y ?? (this.sourceHeight * 0.25));

      this.interface = {
        boundaryY: bY,
        normalX: nX,
        n1,
        n2,
        source: { x: sx, y: sy },
        targetPoint: { x: nX, y: bY }
      };
    } else {
      // Default: thin_lens
      this.subtype = 'thin_lens';
      const lensEl = elements.find(e => e.semantic_label?.includes('lens')) || {};
      const objEl = elements.find(e => e.semantic_label?.includes('object')) || {};

      const lensX = Number(lensEl.optics?.optical_center?.x ?? lensEl.geometry?.optical_center?.x ?? lensEl.geometry?.source_px?.centroid_px?.[0] ?? (this.sourceWidth * 0.5));
      const lensY = Number(lensEl.optics?.optical_center?.y ?? lensEl.geometry?.optical_center?.y ?? lensEl.geometry?.source_px?.centroid_px?.[1] ?? axisY);
      const rawFocal = lensEl.optics?.focal_length_px?.value ?? lensEl.optics?.focal_length_px ?? scene.parameters?.focalLength?.value ?? 130.0;
      const focalLength = Number(rawFocal);
      const model = lensEl.optics?.model || (focalLength < 0 ? 'concave' : 'convex');

      const objectX = Number(objEl.optics?.base?.x ?? objEl.geometry?.position?.x ?? (lensX - 240.0));
      const objectH = objEl.optics?.height_px ?? (objEl.optics?.tip && objEl.optics?.base ? objEl.optics.tip.y - objEl.optics.base.y : null);
      const objectHeight = Number(objectH ?? objEl.geometry?.height_px ?? scene.parameters?.objectHeight?.value ?? -80.0);

      this.lens = { x: lensX, y: lensY, focalLength, model };
      this.object = { x: objectX, height: objectHeight };
    }

    return {
      isAlgebraic: true,
      algebraicState: [0.0] // Trigger single instant solve
    };
  }

  /**
   * Residual function for algebraic optical equilibrium.
   * Compiles the exact ray trajectories and image formation parameters.
   */
  evaluateResiduals(z) {
    this.solution = this.solveOptics();
    return new Float64Array([0.0]); // Instantly satisfied
  }

  solveOptics() {
    const bounds = {
      minX: 0,
      minY: 0,
      maxX: this.sourceWidth,
      maxY: this.sourceHeight
    };

    if (this.subtype === 'thin_lens') {
      return this._solveThinLens(bounds);
    } else if (this.subtype === 'mirror') {
      return this._solveMirror(bounds);
    } else if (this.subtype === 'prism') {
      return this._solvePrism(bounds);
    } else if (this.subtype === 'interface_refraction') {
      return this._solveInterface(bounds);
    }

    return null;
  }

  /**
   * Thin Lens Solver:
   * Encodes Gaussian Lens Law:
   *   1/v - 1/u = 1/f  =>  v = (u * f) / (u - f)
   * Magnification:
   *   m = -v / u
   */
  _solveThinLens(bounds) {
    const { x: lx, y: ly, focalLength, model } = this.lens;
    const { x: ox, height: oh } = this.object;

    // Physical Law: Signed focal length (f > 0 for convex/converging, f < 0 for concave/diverging)
    const isConcave = model === 'concave' || focalLength < 0;
    const f = isConcave ? -Math.abs(focalLength) : Math.abs(focalLength);

    // Object distance u (positive to the left of the lens)
    const u = lx - ox;

    // Physical Law: Focal plane singularity (object placed at focus)
    if (Math.abs(u - f) < EPSILON) {
      const slope = -oh / f;
      const r1End = EventEngine.rayToBounds({ x: lx, y: ly + oh }, { x: 1, y: slope }, bounds);
      const r2End = EventEngine.rayToBounds({ x: lx, y: ly }, { x: 1, y: slope }, bounds);
      return {
        subtype: 'thin_lens',
        lensType: isConcave ? 'concave' : 'convex',
        lensX: lx,
        axisY: ly,
        u,
        v: Infinity,
        magnification: Infinity,
        imageX: Infinity,
        imageHeight: Infinity,
        imageType: 'infinity',
        isReal: false,
        isInverted: null,
        rays: [
          { id: 'ri1', dashed: false, points: [{ x: ox, y: ly + oh }, { x: lx, y: ly + oh }, r1End] },
          { id: 'ri2', dashed: false, points: [{ x: ox, y: ly + oh }, { x: lx, y: ly }, r2End] }
        ]
      };
    }

    // Physical Law: Gaussian Thin Lens Equation: v = (f * u) / (u - f)
    const v = (f * u) / (u - f);
    const m = -(v / u);
    const isReal = v > 0;
    const ix = lx + v; // Real image formed to the right of lens
    const ih = oh * m;

    let imageType = isReal ? 'real' : 'virtual';
    if (Math.abs(m) > 1.05) imageType += '_magnified';
    else if (Math.abs(m) < 0.95) imageType += '_diminished';
    else imageType += '_same_size';

    // Trace 3 Principal Canonical Rays
    const rays = this._traceThinLensRays(lx, ly, ox, oh, f, ix, ih, v, isConcave, bounds);

    return {
      subtype: 'thin_lens',
      lensType: isConcave ? 'concave' : 'convex',
      lensX: lx,
      axisY: ly,
      u,
      v,
      magnification: m,
      imageX: ix,
      imageHeight: ih,
      imageType,
      isReal,
      isInverted: m < 0,
      rays
    };
  }

  _traceThinLensRays(lx, ly, ox, oh, f, ix, ih, v, isConcave, bounds) {
    const tip = { x: ox, y: ly + oh };
    const rays = [];

    // Ray 1: Parallel to principal axis -> emerges through Focus F2 (or diverges from F1)
    const r1Hit = { x: lx, y: ly + oh };
    const focusX = lx + f; // F2 to right if f > 0; to left if f < 0

    // Refracted ray direction: (focusX - lx, -oh)
    const r1Dir = { x: focusX - lx, y: ly - (ly + oh) };
    const r1Len = Math.hypot(r1Dir.x, r1Dir.y);
    const r1NormDir = { x: r1Dir.x / r1Len, y: r1Dir.y / r1Len };
    const r1End = EventEngine.rayToBounds(r1Hit, r1NormDir, bounds);

    rays.push({
      id: 'r1',
      dashed: false,
      points: [tip, r1Hit, r1End]
    });

    if (v < 0 || isConcave) {
      // Virtual backward extension to virtual image tip
      rays.push({
        id: 'r1v',
        dashed: true,
        points: [r1Hit, { x: ix, y: ly + ih }]
      });
    }

    // Ray 2: Central ray passing undeflected through Optical Center (lx, ly)
    const r2Dir = { x: lx - ox, y: ly - tip.y };
    const r2Len = Math.hypot(r2Dir.x, r2Dir.y);
    const r2NormDir = { x: r2Dir.x / r2Len, y: r2Dir.y / r2Len };
    const r2End = EventEngine.rayToBounds(tip, r2NormDir, bounds);

    rays.push({
      id: 'r2',
      dashed: false,
      points: [tip, { x: lx, y: ly }, r2End]
    });

    if (v < 0 || isConcave) {
      rays.push({
        id: 'r2v',
        dashed: true,
        points: [{ x: lx, y: ly }, { x: ix, y: ly + ih }]
      });
    }

    // Ray 3: Through/from F1 -> exits parallel to principal axis at height (ly + ih)
    const r3Hit = { x: lx, y: ly + ih };
    const r3End = EventEngine.rayToBounds(r3Hit, { x: 1, y: 0 }, bounds);

    if (v < 0 || isConcave) {
      rays.push({
        id: 'r3',
        dashed: false,
        points: [tip, r3Hit, r3End]
      });
      rays.push({
        id: 'r3v',
        dashed: true,
        points: [r3Hit, { x: ix, y: ly + ih }]
      });
    } else {
      const maxX = Math.max(ix, r3End.x);
      rays.push({
        id: 'r3',
        dashed: false,
        points: [tip, r3Hit, { x: maxX, y: ly + ih }]
      });
    }

    return rays;
  }

  /**
   * Spherical & Plane Mirror Solver:
   * Encodes Mirror Law:
   *   1/u + 1/v = 1/f  =>  v = (u * f) / (u - f)
   * Magnification:
   *   m = -v / u
   * 
   * BUG GUARD & INVARIANT:
   * Bidirectional orientation ('left' | 'right') is strictly supported.
   * Surface normal points outwards into the reflective half-space.
   * If facing == 'right': mirror pole is at mx, reflective space is x >= mx, direction factor dir = +1.
   * If facing == 'left': mirror pole is at mx, reflective space is x <= mx, direction factor dir = -1.
   */
  _solveMirror(bounds) {
    const { x: mx, y: my, focalLength, model, facing = 'left' } = this.mirror;
    const { x: ox, height: oh } = this.object;

    const isPlane = model === 'plane';
    const isConvex = model === 'convex';
    const dir = facing === 'right' ? 1.0 : -1.0;

    // Physical Law: Object distance u (positive in front of reflective mirror face)
    // If facing 'left': object is at ox < mx => u = -1 * (ox - mx) = mx - ox > 0
    // If facing 'right': object is at ox > mx => u = +1 * (ox - mx) > 0
    const u = dir * (ox - mx);

    if (isPlane) {
      // Physical Law: Plane mirror: v = -u, m = +1.0
      const v = -u;
      const m = 1.0;
      const ix = mx - dir * u;
      const ih = oh;

      const rays = this._tracePlaneMirrorRays(mx, my, ox, oh, u, dir, bounds);
      return {
        subtype: 'mirror',
        mirrorType: 'plane',
        facing,
        u,
        v,
        magnification: m,
        imageX: ix,
        imageHeight: ih,
        imageType: 'virtual_same_size',
        isReal: false,
        isInverted: false,
        rays
      };
    }

    // Signed focal length: positive for concave (focal point in front), negative for convex
    const f = isConvex ? -Math.abs(focalLength) : Math.abs(focalLength);

    if (Math.abs(u - f) < EPSILON) {
      return {
        subtype: 'mirror',
        mirrorType: isConvex ? 'convex' : 'concave',
        facing,
        u,
        v: Infinity,
        magnification: Infinity,
        imageX: Infinity,
        imageHeight: Infinity,
        imageType: 'infinity',
        isReal: false,
        isInverted: null,
        rays: []
      };
    }

    // Physical Law: Spherical Mirror Formula: 1/v + 1/u = 1/f => v = (f * u) / (u - f)
    const v = (f * u) / (u - f);
    const m = -(v / u);
    const isReal = v > 0;

    // Real image (v > 0) forms in front of mirror (same side as object, +dir * v from pole)
    // Virtual image (v < 0) forms behind mirror (-dir * |v| from pole)
    const ix = mx + dir * v;
    const ih = oh * m;

    let imageType = isReal ? 'real' : 'virtual';
    if (Math.abs(m) > 1.05) imageType += '_magnified';
    else if (Math.abs(m) < 0.95) imageType += '_diminished';
    else imageType += '_same_size';

    const rays = this._traceSphericalMirrorRays(mx, my, ox, oh, f, ix, ih, v, isConvex, dir, bounds);

    return {
      subtype: 'mirror',
      mirrorType: isConvex ? 'convex' : 'concave',
      facing,
      u,
      v,
      magnification: m,
      imageX: ix,
      imageHeight: ih,
      imageType,
      isReal,
      isInverted: m < 0,
      rays
    };
  }

  _tracePlaneMirrorRays(mx, my, ox, oh, u, dir, bounds) {
    const tip = { x: ox, y: my + oh };
    const ix = mx - dir * u;
    const ih = oh;

    // Normal unit pointing away from mirror into reflective side
    const normal = { x: dir, y: 0 };
    const r1Hit = { x: mx, y: my + oh };
    const r1Dir = { x: dir, y: 0 };
    const r1End = EventEngine.rayToBounds(r1Hit, r1Dir, bounds);

    const r2Hit = { x: mx, y: my };
    const r2IncDir = { x: mx - ox, y: my - tip.y };
    const r2IncLen = Math.hypot(r2IncDir.x, r2IncDir.y);
    const r2NormInc = { x: r2IncDir.x / r2IncLen, y: r2IncDir.y / r2IncLen };
    const r2Refl = EventEngine.redirectReflection(r2NormInc, normal);
    const r2End = EventEngine.rayToBounds(r2Hit, r2Refl, bounds);

    return [
      { id: 'mr1', dashed: false, points: [tip, r1Hit, r1End] },
      { id: 'mr1v', dashed: true, points: [r1Hit, { x: ix, y: my + ih }] },
      { id: 'mr2', dashed: false, points: [tip, r2Hit, r2End] },
      { id: 'mr2v', dashed: true, points: [r2Hit, { x: ix, y: my + ih }] }
    ];
  }

  _traceSphericalMirrorRays(mx, my, ox, oh, f, ix, ih, v, isConvex, dir, bounds) {
    const tip = { x: ox, y: my + oh };
    const focusX = mx + dir * f;
    const rays = [];

    // Ray 1: Incident parallel to principal axis -> hits mirror at (mx, my + oh)
    const r1Hit = { x: mx, y: my + oh };
    // Reflected ray passes through Focus (focusX, my)
    const r1ReflVec = { x: focusX - mx, y: my - r1Hit.y };
    const r1Len = Math.hypot(r1ReflVec.x, r1ReflVec.y);
    // Ensure reflected ray travels out into reflective space (x * dir > 0)
    let r1NormDir = { x: r1ReflVec.x / r1Len, y: r1ReflVec.y / r1Len };
    if (r1NormDir.x * dir < 0) {
      r1NormDir = { x: -r1NormDir.x, y: -r1NormDir.y };
    }
    const r1End = EventEngine.rayToBounds(r1Hit, r1NormDir, bounds);

    rays.push({
      id: 'smr1',
      dashed: false,
      points: [tip, r1Hit, r1End]
    });

    if (v < 0) {
      rays.push({
        id: 'smr1v',
        dashed: true,
        points: [r1Hit, { x: ix, y: my + ih }]
      });
    }

    // Ray 2: Aimed at Pole (mx, my) -> reflects symmetrically across principal axis
    const r2Hit = { x: mx, y: my };
    const normalAtPole = { x: dir, y: 0 };
    const r2IncVec = { x: mx - ox, y: my - tip.y };
    const r2IncLen = Math.hypot(r2IncVec.x, r2IncVec.y);
    const r2NormInc = { x: r2IncVec.x / r2IncLen, y: r2IncVec.y / r2IncLen };
    const r2Refl = EventEngine.redirectReflection(r2NormInc, normalAtPole);
    const r2End = EventEngine.rayToBounds(r2Hit, r2Refl, bounds);

    rays.push({
      id: 'smr2',
      dashed: false,
      points: [tip, r2Hit, r2End]
    });

    if (v < 0) {
      rays.push({
        id: 'smr2v',
        dashed: true,
        points: [r2Hit, { x: ix, y: my + ih }]
      });
    }

    return rays;
  }

  /**
   * Triangular / Polygon Prism Solver:
   * Propagates incident ray through multiple faces using EventEngine Snell refraction.
   * Computes net angular deviation: delta = i1 + r2 - A
   */
  _solvePrism(bounds) {
    const { vertices, refractiveIndex } = this.prism;
    const { x: sx, y: sy, targetX: tx, targetY: ty } = this.lightSource;

    const rayOrigin = { x: sx, y: sy };
    const incVec = { x: tx - sx, y: ty - sy };
    const incLen = Math.hypot(incVec.x, incVec.y) || 1.0;
    const rayDir = { x: incVec.x / incLen, y: incVec.y / incLen };

    const nAir = 1.0;
    const nGlass = refractiveIndex;

    const segments = [];
    const numVerts = vertices.length;

    // Face 1 Intersection
    let firstHit = null;
    let hitEdgeIdx = -1;
    for (let i = 0; i < numVerts; i++) {
      const p1 = vertices[i];
      const p2 = vertices[(i + 1) % numVerts];
      const hit = EventEngine.rayIntersectSegment(rayOrigin, rayDir, p1, p2);
      if (hit && (!firstHit || hit.distance < firstHit.distance)) {
        firstHit = hit;
        hitEdgeIdx = i;
      }
    }

    if (!firstHit) {
      // Ray misses prism completely
      const missEnd = EventEngine.rayToBounds(rayOrigin, rayDir, bounds);
      return {
        subtype: 'prism',
        deviationDeg: 0.0,
        rays: [{ id: 'p_miss', points: [rayOrigin, missEnd] }]
      };
    }

    // Compute centroid of prism to orient outward normals if needed
    let cx = 0, cy = 0;
    vertices.forEach(v => { cx += v.x; cy += v.y; });
    const centroid = { x: cx / numVerts, y: cy / numVerts };

    // Normal lines for visual rendering (drawn 35px outward & inward)
    const normalViz1 = {
      p1: { x: firstHit.point.x + firstHit.normal.x * 35, y: firstHit.point.y + firstHit.normal.y * 35 },
      p2: { x: firstHit.point.x - firstHit.normal.x * 35, y: firstHit.point.y - firstHit.normal.y * 35 }
    };

    // Angle of incidence i1 (angle between incident ray and -N1)
    const cosI1 = Math.min(1.0, Math.max(0.0, -EventEngine.dot(rayDir, firstHit.normal)));
    const i1Deg = (Math.acos(cosI1) * 180) / Math.PI;

    // Refract into glass at Face 1
    const refr1 = EventEngine.redirectRefraction(rayDir, firstHit.normal, nAir, nGlass);

    // Internal ray direction
    const I_internal = refr1.direction;
    const cosR1 = Math.min(1.0, Math.max(0.0, EventEngine.dot(I_internal, { x: -firstHit.normal.x, y: -firstHit.normal.y })));
    const r1Deg = (Math.acos(cosR1) * 180) / Math.PI;

    segments.push(rayOrigin);
    segments.push(firstHit.point);

    // Interior ray propagation to Face 2
    let secondHit = null;
    for (let i = 0; i < numVerts; i++) {
      if (i === hitEdgeIdx) continue; // Skip entering face
      const p1 = vertices[i];
      const p2 = vertices[(i + 1) % numVerts];
      const hit = EventEngine.rayIntersectSegment(firstHit.point, refr1.direction, p1, p2);
      if (hit && (!secondHit || hit.distance < secondHit.distance)) {
        secondHit = hit;
      }
    }

    let isTir = false;
    let emergentEnd;
    let normalViz2 = null;

    if (secondHit) {
      segments.push(secondHit.point);
      normalViz2 = {
        p1: { x: secondHit.point.x + secondHit.normal.x * 35, y: secondHit.point.y + secondHit.normal.y * 35 },
        p2: { x: secondHit.point.x - secondHit.normal.x * 35, y: secondHit.point.y - secondHit.normal.y * 35 }
      };

      // Refract out of glass into air at Face 2
      const refr2 = EventEngine.redirectRefraction(refr1.direction, secondHit.normal, nGlass, nAir);
      isTir = refr2.tir;
      emergentEnd = EventEngine.rayToBounds(secondHit.point, refr2.direction, bounds);
      segments.push(emergentEnd);
    } else {
      emergentEnd = EventEngine.rayToBounds(firstHit.point, refr1.direction, bounds);
      segments.push(emergentEnd);
    }

    // Physical Law: Deviation angle delta between initial incident vector and emergent vector
    const initialAngle = Math.atan2(rayDir.y, rayDir.x);
    const finalDir = secondHit ? { x: emergentEnd.x - secondHit.point.x, y: emergentEnd.y - secondHit.point.y } : rayDir;
    const finalAngle = Math.atan2(finalDir.y, finalDir.x);
    let deltaRad = Math.abs(finalAngle - initialAngle);
    if (deltaRad > Math.PI) deltaRad = 2.0 * Math.PI - deltaRad;
    const deviationDeg = (deltaRad * 180.0) / Math.PI;

    const normals = [normalViz1];
    if (normalViz2) normals.push(normalViz2);

    const segmentObjs = [
      { type: 'incident', start: rayOrigin, end: firstHit.point },
      { type: 'internal', start: firstHit.point, end: secondHit ? secondHit.point : emergentEnd },
      ...(secondHit ? [{ type: isTir ? 'tir_reflected' : 'emergent', start: secondHit.point, end: emergentEnd }] : [])
    ];

    const criticalAngleDeg = (Math.asin(nAir / nGlass) * 180.0) / Math.PI;

    return {
      subtype: 'prism',
      hitPrism: true,
      tir: isTir,
      deviationDeg: isTir ? null : deviationDeg,
      normals,
      segments: segmentObjs,
      angles: {
        i1Deg,
        r1Deg,
        deviationDeg: isTir ? null : deviationDeg,
        criticalAngleDeg
      },
      rays: [{ id: 'prism_path', dashed: false, points: segments }]
    };
  }

  /**
   * Planar Media Interface Refraction:
   * Encodes Snell's Law across a horizontal boundary:
   *   n1 * sin(theta1) = n2 * sin(theta2)
   * With Total Internal Reflection when n1 > n2 and theta1 > theta_critical.
   */
  _solveInterface(bounds) {
    const { boundaryY, normalX, n1, n2, source, targetPoint } = this.interface;

    const incVec = { x: targetPoint.x - source.x, y: targetPoint.y - source.y };
    const incLen = Math.hypot(incVec.x, incVec.y) || 1.0;
    const incDir = { x: incVec.x / incLen, y: incVec.y / incLen };

    // Normal points upwards into medium 1: (0, -1)
    const normal = { x: 0, y: -1 };
    const refr = EventEngine.redirectRefraction(incDir, normal, n1, n2);

    const endPoint = EventEngine.rayToBounds(targetPoint, refr.direction, bounds);

    // Calculate angles relative to the normal (vertical)
    const theta1Rad = Math.atan2(Math.abs(incDir.x), Math.abs(incDir.y));
    const theta2Rad = refr.tir ? null : Math.atan2(Math.abs(refr.direction.x), Math.abs(refr.direction.y));
    const theta1Deg = (theta1Rad * 180.0) / Math.PI;
    const theta2Deg = theta2Rad !== null ? (theta2Rad * 180.0) / Math.PI : null;

    const incidentRay = [source, targetPoint];
    incidentRay.start = source;
    incidentRay.end = targetPoint;
    incidentRay.points = [source, targetPoint];

    const refractedRay = refr.tir ? null : [targetPoint, endPoint];
    if (refractedRay) {
      refractedRay.start = targetPoint;
      refractedRay.end = endPoint;
      refractedRay.points = [targetPoint, endPoint];
    }

    const reflDir = EventEngine.redirectReflection(incDir, normal);
    const reflEnd = EventEngine.rayToBounds(targetPoint, reflDir, bounds);
    const reflectedRay = [targetPoint, reflEnd];
    reflectedRay.start = targetPoint;
    reflectedRay.end = reflEnd;
    reflectedRay.points = [targetPoint, reflEnd];

    return {
      subtype: 'interface_refraction',
      n1,
      n2,
      theta1Deg,
      theta2Deg,
      isTir: refr.tir,
      criticalAngleDeg: refr.criticalAngleDeg,
      incidentRay,
      refractedRay,
      reflectedRay,
      angles: {
        theta1Deg,
        theta2Deg,
        theta1Rad,
        theta2Rad,
        criticalAngleDeg: refr.criticalAngleDeg
      },
      rays: [
        { id: 'incident_ray', dashed: false, points: [source, targetPoint] },
        ...(refractedRay ? [{ id: 'refracted_ray', dashed: false, points: [targetPoint, endPoint] }] : []),
        ...(reflectedRay ? [{ id: 'reflected_ray', dashed: refr.tir ? false : true, points: [targetPoint, reflEnd] }] : [])
      ]
    };
  }

  setParameter(name, value) {
    const val = Number(value);
    if (name === 'focalLength') {
      if (this.lens) this.lens.focalLength = val;
      if (this.mirror) this.mirror.focalLength = val;
    } else if (name === 'objectDistance') {
      if (this.lens) this.object.x = this.lens.x - val;
      if (this.mirror) {
        const dir = this.mirror.facing === 'right' ? 1 : -1;
        this.object.x = this.mirror.x + dir * val;
      }
    } else if (name === 'objectHeight') {
      if (this.object) this.object.height = val;
    } else if (name === 'refractiveIndex' && this.prism) {
      this.prism.refractiveIndex = val;
    } else if (name === 'n2' && this.interface) {
      this.interface.n2 = val;
    }
    this.solution = this.solveOptics();
  }

  extractState(core) {
    const sol = this.solution || this.solveOptics();
    return {
      domain: 'optics',
      type: this.subtype,
      solution: sol,
      focalLength: Number((this.lens?.focalLength || this.mirror?.focalLength || 0).toFixed(1)),
      u: sol?.u ? Number(sol.u.toFixed(1)) : 0,
      v: sol?.v !== undefined && Number.isFinite(sol.v) ? Number(sol.v.toFixed(1)) : 'Infinity',
      magnification: sol?.magnification !== undefined && Number.isFinite(sol.magnification) ? Number(sol.magnification.toFixed(2)) : 'Infinity',
      isReal: Boolean(sol?.isReal),
      isInverted: Boolean(sol?.isInverted),
      rayCount: sol?.rays?.length || 0
    };
  }
}

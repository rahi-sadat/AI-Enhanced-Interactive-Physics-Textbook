/** optics/opticsSceneAdapter.js
 * Translates Canonical PhysicsScene v2/v3 / legacy JSON into the optics model.
 * All adapted geometry is authoritative in native SOURCE IMAGE PIXELS.
 */

export function unwrapVal(v, fallback = null) {
  if (v === null || v === undefined) return fallback;
  if (typeof v === 'object' && 'value' in v) return v.value ?? fallback;
  return v;
}

export function requireResolved(value, name, isPrecision = false) {
  const unwrapped = unwrapVal(value);
  if (unwrapped === null || unwrapped === undefined || Number.isNaN(Number(unwrapped))) {
    if (isPrecision) {
      throw new Error(`[OpticsPrecision] ${name} is unresolved in Precision Mode.`);
    }
    return null;
  }
  return Number(unwrapped);
}

function readPoint(point, name, isPrecision = false, fallback = null) {
  if (!point || !Number.isFinite(Number(point.x)) || !Number.isFinite(Number(point.y))) {
    if (isPrecision) {
      throw new Error(`[OpticsPrecision] Missing required point: ${name}`);
    }
    return fallback;
  }
  return {
    x: Number(point.x),
    y: Number(point.y),
  };
}

export function adaptOpticsScene(scene, options = {}) {
  const isPrecision = options.precisionMode ?? scene.precision_mode ?? false;
  const all = [...(scene.elements || []), ...(scene.sources || [])];
  const ann = scene.annotations || [];

  const sourceWidth = scene.source?.image_width_px ??
    scene.render?.source_width_px ??
    scene.coordinate_system?.render?.source_width_px ??
    800;
  const sourceHeight = scene.source?.image_height_px ??
    scene.render?.source_height_px ??
    scene.coordinate_system?.render?.source_height_px ??
    600;

  const subtype = scene.simulation?.subtype ||
    (all.some(e => ['interface_refraction', 'snell_refraction', 'boundary_refraction', 'interface', 'boundary'].includes(e.semantic_label)) ? 'interface_refraction' :
    (all.some(e => e.semantic_label === 'prism') ? 'prism' :
    (all.some(e => e.semantic_label?.includes('mirror')) ? 'mirror' : 'thin_lens')));

  const rawPxPerCm = scene.coordinate_system?.physical_scale?.pixels_per_cm ??
    scene.physical_scale?.pixels_per_cm ??
    scene.coordinate_system?.calibration?.pixels_per_cm ??
    scene.calibration?.pixels_per_cm;
  const pixelPerCm = unwrapVal(rawPxPerCm, null);
  const backgroundUrl = scene.visual?.background_url || scene.source?.image || null;

  // 1. Interface Refraction
  if (['interface_refraction', 'snell_refraction', 'boundary_refraction'].includes(subtype)) {
    const boundaryEl = all.find(e => ['interface', 'boundary', 'medium_boundary', 'refractive_interface', 'plane_interface'].includes(e.semantic_label)) || all[0];
    const normalEl = all.find(e => ['normal', 'normal_line'].includes(e.semantic_label));
    const lightEl = all.find(e => ['light_source', 'ray_source', 'incident_ray', 'incident_ray_source'].includes(e.semantic_label)) || all[1];

    const boundaryY = unwrapVal(
      boundaryEl?.optics?.y ?? boundaryEl?.optics?.boundary_y ?? boundaryEl?.geometry?.position?.y,
      isPrecision ? null : 300
    );
    if (isPrecision && boundaryY === null) throw new Error('[OpticsPrecision] Boundary Y position is unresolved.');

    const normalX = unwrapVal(
      normalEl?.optics?.x ?? boundaryEl?.optics?.normal_x ?? boundaryEl?.geometry?.position?.x,
      isPrecision ? null : 400
    );
    if (isPrecision && normalX === null) throw new Error('[OpticsPrecision] Normal X position is unresolved.');

    const rawN1 = unwrapVal(boundaryEl?.optics?.medium1?.n ?? boundaryEl?.optics?.n1, 1.0);
    const rawN2 = unwrapVal(boundaryEl?.optics?.medium2?.n ?? boundaryEl?.optics?.n2, isPrecision ? null : 1.83);
    if (isPrecision && (rawN2 === null || boundaryEl?.optics?.medium2?.status === 'unresolved')) {
      throw new Error('[OpticsPrecision] Refractive index n2 is unresolved.');
    }

    const n1 = Number(rawN1) || 1.0;
    const n2 = Number(rawN2) || 1.83;
    const m1Name = boundaryEl?.optics?.medium1?.name ?? 'Air (Rarer)';
    const m2Name = boundaryEl?.optics?.medium2?.name ?? 'Denser Medium';

    const rawSrc = lightEl?.optics?.position ?? lightEl?.geometry?.position;
    const sourcePos = readPoint(rawSrc, 'light source position', isPrecision, { x: normalX - 160, y: boundaryY - 160 });
    const p1 = boundaryEl?.optics?.boundary?.p1 ?? { x: 0, y: boundaryY };
    const p2 = boundaryEl?.optics?.boundary?.p2 ?? { x: sourceWidth, y: boundaryY };

    return {
      subtype: 'interface_refraction',
      coordinateSpace: 'source_px',
      backgroundUrl,
      sourceWidth,
      sourceHeight,
      boundary: { y: boundaryY, p1, p2 },
      normal: { x: normalX },
      medium1: { name: m1Name, n: n1 },
      medium2: { name: m2Name, n: n2 },
      interface: { boundaryY, normalX, n1, n2 },
      lightSource: { x: sourcePos.x, y: sourcePos.y },
      pixelPerCm,
    };
  }

  // 2. Prism
  if (subtype === 'prism') {
    const prismEl = all.find(e => ['prism', 'refractive_polygon'].includes(e.semantic_label)) || all[0];
    const lightEl = all.find(e => ['light_source', 'ray_source'].includes(e.semantic_label)) || all[1];

    const rawVerts = prismEl?.optics?.vertices ?? prismEl?.geometry?.vertices;
    if (isPrecision && (!rawVerts || rawVerts.length < 3)) {
      throw new Error('[OpticsPrecision] Prism vertices are unresolved.');
    }
    const vertices = rawVerts ?? [
      { x: 400, y: 170 }, { x: 260, y: 430 }, { x: 540, y: 430 }
    ];

    const rawN = unwrapVal(prismEl?.optics?.refractive_index, isPrecision ? null : 1.52);
    if (isPrecision && (rawN === null || prismEl?.optics?.refractive_index?.status === 'unresolved')) {
      throw new Error('[OpticsPrecision] Prism refractive index is unresolved.');
    }
    const n = Number(rawN) || 1.52;

    const sourcePos = lightEl?.optics?.position ?? lightEl?.geometry?.position ?? { x: vertices[1].x - 100, y: (vertices[0].y + vertices[1].y) / 2 };
    const targetPos = lightEl?.optics?.target ?? lightEl?.geometry?.target ?? { x: (vertices[0].x + vertices[1].x) / 2, y: (vertices[0].y + vertices[1].y) / 2 };

    return {
      subtype: 'prism',
      coordinateSpace: 'source_px',
      backgroundUrl,
      sourceWidth,
      sourceHeight,
      prism: {
        vertices: vertices.map(v => ({ x: Number(v.x), y: Number(v.y) })),
        refractiveIndex: n,
        apexAngle: unwrapVal(prismEl?.optics?.apex_angle_deg, 60.0),
      },
      lightSource: {
        x: Number(sourcePos.x),
        y: Number(sourcePos.y),
        targetX: Number(targetPos.x),
        targetY: Number(targetPos.y),
      },
      pixelPerCm,
    };
  }

  // 3. Mirror
  if (subtype === 'mirror') {
    const mirrorEl = all.find(e => e.semantic_label?.includes('mirror')) || all[0];
    const objEl = all.find(e => ['object_arrow', 'optical_object'].includes(e.semantic_label) || e.author_role === 'dynamic');

    const poleRaw = mirrorEl?.optics?.pole ?? mirrorEl?.geometry?.optical_center ?? mirrorEl?.geometry?.source_px?.centroid_px;
    const mirrorX = unwrapVal(
      typeof poleRaw === 'object' ? (poleRaw.x ?? poleRaw[0]) : poleRaw,
      isPrecision ? null : 600
    );
    if (isPrecision && mirrorX === null) throw new Error('[OpticsPrecision] Mirror pole X is unresolved.');

    const axisY = unwrapVal(
      typeof poleRaw === 'object' ? (poleRaw.y ?? poleRaw[1]) : null,
      isPrecision ? null : 300
    );
    if (isPrecision && axisY === null) throw new Error('[OpticsPrecision] Optical axis Y is unresolved.');

    const fPxRaw = unwrapVal(mirrorEl?.optics?.focal_length_px, isPrecision ? null : 140);
    if (isPrecision && fPxRaw === null) throw new Error('[OpticsPrecision] Mirror focal length is unresolved.');
    const fPx = Number(fPxRaw) || 140;

    const curRadius = unwrapVal(mirrorEl?.optics?.curvature_radius_px, 2 * Math.abs(fPx));
    const aperH = unwrapVal(mirrorEl?.optics?.aperture_height_px, isPrecision ? null : 240);
    const model = mirrorEl?.optics?.concavity ?? mirrorEl?.optics?.model ?? 'concave';

    const objBase = objEl?.optics?.base;
    const objTip = objEl?.optics?.tip;
    let objX = unwrapVal(objBase?.x ?? objEl?.geometry?.position?.x, mirrorX - 2.0 * Math.abs(fPx));
    let objH = unwrapVal(
      objTip && objBase ? (objTip.y - objBase.y) :
      (objEl?.geometry?.height_px ?? (objEl?.optics?.height_px ? -objEl.optics.height_px : -85)),
      -85
    );

    const spriteUrl = objEl?.visual?.sprite_url || null;

    return {
      subtype: 'mirror',
      coordinateSpace: 'source_px',
      backgroundUrl,
      sourceWidth,
      sourceHeight,
      mirror: {
        x: mirrorX,
        y: axisY,
        focalLength: fPx,
        curvatureRadius: curRadius,
        apertureHeight: aperH,
        model,
      },
      object: { x: objX, height: objH, spriteUrl },
      axisY,
      focalPoints: _buildMirrorFP(ann, mirrorX, fPx),
      pixelPerCm,
    };
  }

  // 4. Thin Lens (default)
  const lensEl = all.find(e => ['convex_lens', 'concave_lens', 'lens', 'thin_lens'].includes(e.semantic_label)) || all[0];
  if (!lensEl && isPrecision) throw new Error('[OpticsPrecision] No optical lens element in scene.');

  const ocRaw = lensEl?.optics?.optical_center ?? lensEl?.geometry?.optical_center ?? lensEl?.geometry?.source_px?.centroid_px;
  const lensX = unwrapVal(
    typeof ocRaw === 'object' ? (ocRaw.x ?? ocRaw[0]) : ocRaw,
    isPrecision ? null : 400
  );
  if (isPrecision && lensX === null) throw new Error('[OpticsPrecision] Lens optical center X is unresolved.');

  const axisY = unwrapVal(
    typeof ocRaw === 'object' ? (ocRaw.y ?? ocRaw[1]) : null,
    isPrecision ? null : 300
  );
  if (isPrecision && axisY === null) throw new Error('[OpticsPrecision] Lens optical axis Y is unresolved.');

  const fPxRaw = unwrapVal(lensEl?.optics?.focal_length_px, isPrecision ? null : 130);
  if (isPrecision && (fPxRaw === null || lensEl?.optics?.focal_length_px?.status === 'unresolved')) {
    throw new Error('[OpticsPrecision] Lens focal length is unresolved.');
  }
  const fPx = Number(fPxRaw) || 130;

  const aperH = unwrapVal(lensEl?.optics?.aperture_height_px ?? lensEl?.geometry?.aperture_height_px, isPrecision ? null : 220);
  const model = lensEl?.optics?.concavity ?? lensEl?.optics?.model ?? (fPx < 0 ? 'concave' : 'convex');

  const objEl = all.find(e => ['object_arrow', 'optical_object'].includes(e.semantic_label) || e.author_role === 'dynamic');
  const objBase = objEl?.optics?.base;
  const objTip = objEl?.optics?.tip;

  let objX = unwrapVal(objBase?.x ?? objEl?.geometry?.position?.x, lensX - Math.abs(fPx) * 2.0);
  let objH = unwrapVal(
    objTip && objBase ? (objTip.y - objBase.y) :
    (objEl?.geometry?.height_px ?? (objEl?.optics?.height_px ? -objEl.optics.height_px : -90)),
    -90
  );
  const spriteUrl = objEl?.visual?.sprite_url || null;

  return {
    subtype: 'thin_lens',
    coordinateSpace: 'source_px',
    backgroundUrl,
    sourceWidth,
    sourceHeight,
    lens: {
      x: lensX,
      y: axisY,
      focalLength: fPx,
      apertureHeight: aperH,
      model,
    },
    object: { x: objX, height: objH, spriteUrl },
    axisY,
    focalPoints: _buildFP(ann, lensX, fPx),
    pixelPerCm,
  };
}

function _buildFP(ann, lx, f) {
  const fromAnn = ann.filter(a => /^[2]?F/.test(a.label)).map(a => ({
    label: a.label,
    x: unwrapVal(a.source_position?.x ?? a.position?.x, lx)
  }));
  if (fromAnn.length > 0) return fromAnn;
  const af = Math.abs(f);
  return [
    { label: '2F₁', x: lx - 2 * af },
    { label: 'F₁',  x: lx - af },
    { label: 'F₂',  x: lx + af },
    { label: '2F₂', x: lx + 2 * af },
  ];
}

function _buildMirrorFP(ann, mx, f) {
  const fromAnn = ann.map(a => ({
    label: a.label,
    x: unwrapVal(a.source_position?.x ?? a.position?.x, mx)
  }));
  if (fromAnn.length > 0) return fromAnn;
  return [
    { label: 'C', x: mx - 2 * f },
    { label: 'F', x: mx - f },
    { label: 'P', x: mx },
  ];
}

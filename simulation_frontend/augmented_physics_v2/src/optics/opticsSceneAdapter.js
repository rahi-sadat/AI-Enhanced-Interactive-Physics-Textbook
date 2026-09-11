/** optics/opticsSceneAdapter.js
 * Translates Canonical PhysicsScene v2 / legacy JSON into the optics model.
 */
function unwrapVal(v, fallback = null) {
  if (v === null || v === undefined) return fallback;
  if (typeof v === 'object' && 'value' in v) return v.value ?? fallback;
  return v;
}

export function adaptOpticsScene(scene) {
  const all = [...(scene.elements || []), ...(scene.sources || [])];
  const ann = scene.annotations || [];
  const subtype = scene.simulation?.subtype ||
    (all.some(e => ['interface_refraction', 'snell_refraction', 'boundary_refraction', 'interface', 'boundary'].includes(e.semantic_label)) ? 'interface_refraction' :
    (all.some(e => e.semantic_label === 'prism') ? 'prism' :
    (all.some(e => e.semantic_label?.includes('mirror')) ? 'mirror' : 'thin_lens')));

  const rawPxPerCm = scene.coordinate_system?.physical_scale?.pixels_per_cm ??
    scene.physical_scale?.pixels_per_cm ??
    scene.coordinate_system?.calibration?.pixels_per_cm ??
    scene.calibration?.pixels_per_cm;
  const pixelPerCm = unwrapVal(rawPxPerCm, null);

  if (['interface_refraction', 'snell_refraction', 'boundary_refraction'].includes(subtype)) {
    const boundaryEl = all.find(e => ['interface', 'boundary', 'medium_boundary', 'refractive_interface', 'plane_interface'].includes(e.semantic_label)) || all[0];
    const normalEl = all.find(e => ['normal', 'normal_line'].includes(e.semantic_label));
    const lightEl = all.find(e => ['light_source', 'ray_source', 'incident_ray', 'incident_ray_source'].includes(e.semantic_label)) || all[1];

    const boundaryY = unwrapVal(boundaryEl?.optics?.y ?? boundaryEl?.optics?.boundary_y ?? boundaryEl?.geometry?.position?.y, 300);
    const normalX   = unwrapVal(normalEl?.optics?.x ?? boundaryEl?.optics?.normal_x ?? boundaryEl?.geometry?.position?.x, 400);
    const n1 = unwrapVal(boundaryEl?.optics?.medium1?.n ?? boundaryEl?.optics?.n1 ?? boundaryEl?.optics?.refractive_index_1, 1.0);
    const n2 = unwrapVal(boundaryEl?.optics?.medium2?.n ?? boundaryEl?.optics?.n2 ?? boundaryEl?.optics?.refractive_index_2, 1.5);
    const m1Name = boundaryEl?.optics?.medium1?.name ?? 'Air (Rarer)';
    const m2Name = boundaryEl?.optics?.medium2?.name ?? 'Glass / Denser';

    const sourcePos = lightEl?.optics?.position ?? lightEl?.geometry?.position ?? { x: normalX - 160, y: boundaryY - 160 };

    return {
      subtype: 'interface_refraction',
      boundary: { y: boundaryY },
      normal: { x: normalX },
      medium1: { name: m1Name, n: n1 },
      medium2: { name: m2Name, n: n2 },
      interface: { boundaryY, normalX, n1, n2 },
      lightSource: {
        x: sourcePos.x,
        y: sourcePos.y,
      },
      pixelPerCm,
    };
  }

  if (subtype === 'prism') {
    const prismEl = all.find(e => ['prism', 'refractive_polygon'].includes(e.semantic_label)) || all[0];
    const lightEl = all.find(e => ['light_source', 'ray_source'].includes(e.semantic_label)) || all[1];
    const vertices = prismEl?.optics?.vertices ?? prismEl?.geometry?.vertices ?? [
      { x: 400, y: 170 }, { x: 260, y: 430 }, { x: 540, y: 430 }
    ];
    const n = unwrapVal(prismEl?.optics?.refractive_index, 1.52);
    const sourcePos = lightEl?.optics?.position ?? lightEl?.geometry?.position ?? { x: 160, y: 380 };
    const targetPos = lightEl?.optics?.target ?? lightEl?.geometry?.target ?? { x: 340, y: 280 };

    return {
      subtype: 'prism',
      prism: { vertices, refractiveIndex: n },
      lightSource: {
        x: sourcePos.x,
        y: sourcePos.y,
        targetX: targetPos.x,
        targetY: targetPos.y,
      },
      pixelPerCm,
    };
  }

  if (subtype === 'mirror') {
    const mirrorEl = all.find(e => e.semantic_label?.includes('mirror')) || all[0];
    const objEl = all.find(e => ['object_arrow','optical_object'].includes(e.semantic_label) || e.author_role === 'dynamic');
    const mirrorX = unwrapVal(mirrorEl?.optics?.pole?.x ?? mirrorEl?.geometry?.optical_center?.x ?? mirrorEl?.geometry?.render?.centroid?.x, 600);
    const axisY = unwrapVal(mirrorEl?.optics?.pole?.y ?? mirrorEl?.geometry?.optical_center?.y ?? mirrorEl?.geometry?.render?.centroid?.y, 300);
    const fPx = unwrapVal(mirrorEl?.optics?.focal_length_px, 140);
    const model = mirrorEl?.optics?.concavity ?? mirrorEl?.optics?.model ?? 'concave';
    const objX = unwrapVal(objEl?.optics?.base?.x ?? objEl?.geometry?.position?.x ?? objEl?.geometry?.render?.centroid?.x, 260);
    const objH = unwrapVal(
      objEl?.optics?.tip && objEl?.optics?.base ? (objEl.optics.tip.y - objEl.optics.base.y) :
      (objEl?.geometry?.height_px ?? (objEl?.optics?.height_px ? -objEl.optics.height_px : -85)),
      -85
    );
    const spriteUrl = objEl?.visual?.sprite_url || null;

    return {
      subtype: 'mirror',
      mirror: { x: mirrorX, focalLength: fPx, model },
      object: { x: objX, height: objH, spriteUrl },
      axisY,
      focalPoints: _buildMirrorFP(ann, mirrorX, fPx),
      pixelPerCm,
    };
  }

  // Thin Lens (default)
  const lensEl = all.find(e => ['convex_lens','concave_lens','lens','thin_lens'].includes(e.semantic_label)) || all[0];
  if (!lensEl) throw new Error('[OpticsAdapter] No optical element in scene.');

  const lensX = unwrapVal(lensEl.optics?.optical_center?.x ?? lensEl.geometry?.optical_center?.x ?? lensEl.geometry?.render?.centroid?.x, 400);
  const axisY = unwrapVal(lensEl.optics?.optical_center?.y ?? lensEl.geometry?.optical_center?.y ?? lensEl.geometry?.render?.centroid?.y, 300);
  const fPx   = unwrapVal(lensEl.optics?.focal_length_px, 130);
  const aperH = unwrapVal(lensEl.optics?.aperture_height_px ?? lensEl.geometry?.aperture_height_px, 220);
  const model = lensEl?.optics?.concavity ?? lensEl?.optics?.model ?? (fPx < 0 ? 'concave' : 'convex');

  const objEl = all.find(e => ['object_arrow','optical_object'].includes(e.semantic_label) || e.author_role === 'dynamic');
  const objX  = unwrapVal(objEl?.optics?.base?.x ?? objEl?.geometry?.position?.x ?? objEl?.geometry?.render?.centroid?.x, lensX - Math.abs(fPx) * 2);
  const objH  = unwrapVal(
    objEl?.optics?.tip && objEl?.optics?.base ? (objEl.optics.tip.y - objEl.optics.base.y) :
    (objEl?.geometry?.height_px ?? (objEl?.optics?.height_px ? -objEl.optics.height_px : -90)),
    -90
  );
  const spriteUrl = objEl?.visual?.sprite_url || null;

  return {
    subtype: 'thin_lens',
    lens:   { x: lensX, focalLength: fPx, apertureHeight: aperH, model },
    object: { x: objX, height: objH, spriteUrl },
    axisY,
    focalPoints: _buildFP(ann, lensX, fPx),
    pixelPerCm,
  };
}

function _buildFP(ann, lx, f) {
  const fromAnn = ann.filter(a => /^[2]?F/.test(a.label)).map(a => ({ label: a.label, x: a.position.x }));
  if (fromAnn.length > 0) return fromAnn;
  const af = Math.abs(f);
  return [
    { label: '2F₁', x: lx - 2*af },
    { label: 'F₁',  x: lx - af   },
    { label: 'F₂',  x: lx + af   },
    { label: '2F₂', x: lx + 2*af },
  ];
}

function _buildMirrorFP(ann, mx, f) {
  const fromAnn = ann.map(a => ({ label: a.label, x: a.position.x }));
  if (fromAnn.length > 0) return fromAnn;
  return [
    { label: 'C', x: mx - 2*f },
    { label: 'F', x: mx - f },
    { label: 'P', x: mx },
  ];
}

/** optics/engines/thinLensEngine.js
 * Thin-lens equation solver — pure math, no DOM.
 *
 * Sign convention (real-positive):
 *   u = lensX - objectX   (positive when object is LEFT of lens)
 *   1/v = 1/f - 1/u       (v positive = real image RIGHT of lens)
 *   m  = -v/u
 */
const EPS = 0.5;

export function solveThinLens({lensX, axisY, objectX, objectHeight, focalLength}) {
  const f = focalLength;
  const u = lensX - objectX;

  if (Math.abs(u - f) < EPS) {
    return {u, v:Infinity, magnification:Infinity,
            imageX:Infinity, imageHeight:Infinity,
            imageType:'infinity', isReal:false, isInverted:null,
            lensX, axisY,
            rays: _infinityRays(lensX, axisY, objectX, objectHeight, f)};
  }

  const v  = (f * u) / (u - f);
  const m  = -(v / u);
  const ix = lensX + v;
  const ih = objectHeight * m;
  const isReal = v > 0;

  let imageType = 'virtual_magnified';
  if (f < 0) {
    imageType = 'virtual_diminished';
  } else {
    if      (u > 2*f + EPS)          imageType = 'real_diminished';
    else if (Math.abs(u - 2*f) < EPS) imageType = 'real_same_size';
    else if (u > f + EPS)             imageType = 'real_magnified';
  }

  return {
    u, v, magnification:m,
    imageX:ix, imageHeight:ih,
    imageType, isReal, isInverted: m < 0,
    lensX, axisY,
    lensType: f < 0 ? 'concave' : 'convex',
    rays: _principalRays(lensX, axisY, objectX, objectHeight, f, ix, ih, v)
  };
}

function _principalRays(lx, ay, ox, oh, f, ix, ih, v) {
  const tip   = {x: ox, y: ay + oh};
  const isVirt = v < 0;
  const rays  = [];
  const slopeCenter = -oh / (lx - ox); // slope through optical center

  // Ray 1: Parallel to principal axis -> refracted through F2 (lx + f, ay)
  const slopeF2 = -oh / f;
  if (isVirt) {
    // Real path exits lens to the right
    rays.push({
      id: 'r1',
      dashed: false,
      points: [tip, {x: lx, y: ay + oh}, {x: 800, y: (ay + oh) + slopeF2 * (800 - lx)}]
    });
    // Virtual extension backwards to image tip
    rays.push({
      id: 'r1v',
      dashed: true,
      points: [{x: lx, y: ay + oh}, {x: ix, y: ay + ih}]
    });
  } else {
    rays.push({
      id: 'r1',
      dashed: false,
      points: [tip, {x: lx, y: ay + oh}, {x: Math.max(ix, 800), y: (ay + oh) + slopeF2 * (Math.max(ix, 800) - lx)}]
    });
  }

  // Ray 2: Undeviated through optical center O (lx, ay)
  if (isVirt) {
    rays.push({
      id: 'r2',
      dashed: false,
      points: [tip, {x: lx, y: ay}, {x: 800, y: ay + slopeCenter * (800 - lx)}]
    });
    rays.push({
      id: 'r2v',
      dashed: true,
      points: [{x: lx, y: ay}, {x: ix, y: ay + ih}]
    });
  } else {
    rays.push({
      id: 'r2',
      dashed: false,
      points: [tip, {x: lx, y: ay}, {x: Math.max(ix, 800), y: ay + slopeCenter * (Math.max(ix, 800) - lx)}]
    });
  }

  // Ray 3: Through/from F1 -> exits parallel to principal axis at height (ay + ih)
  if (isVirt) {
    // Virtual ray: dashed line from F1 through tip to lens, then solid parallel to right
    rays.push({
      id: 'r3',
      dashed: false,
      points: [tip, {x: lx, y: ay + ih}, {x: 800, y: ay + ih}]
    });
    rays.push({
      id: 'r3v',
      dashed: true,
      points: [{x: lx, y: ay + ih}, {x: ix, y: ay + ih}]
    });
  } else {
    rays.push({
      id: 'r3',
      dashed: false,
      points: [tip, {x: lx, y: ay + ih}, {x: Math.max(ix, 800), y: ay + ih}]
    });
  }

  return rays;
}

function _infinityRays(lx, ay, ox, oh, f) {
  const tip = {x: ox, y: ay + oh};
  const slope = -oh / f;
  return [
    {
      id: 'ri1',
      dashed: false,
      points: [tip, {x: lx, y: ay + oh}, {x: 800, y: (ay + oh) + slope * (800 - lx)}]
    },
    {
      id: 'ri2',
      dashed: false,
      points: [tip, {x: lx, y: ay}, {x: 800, y: ay + slope * (800 - lx)}]
    }
  ];
}

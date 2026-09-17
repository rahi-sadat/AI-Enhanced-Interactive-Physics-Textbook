import { rayToBounds } from './rayGeometry.js';

const EPS = 0.5;

export function solveThinLens({
  lensX,
  axisY,
  objectX,
  objectHeight,
  focalLength,
  bounds = {}
}) {
  const f = focalLength;
  const u = lensX - objectX;
  const boundBox = {
    minX: bounds.minX ?? 0,
    minY: bounds.minY ?? 0,
    maxX: bounds.maxX ?? bounds.width ?? 800,
    maxY: bounds.maxY ?? bounds.height ?? 600,
  };

  if (Math.abs(u - f) < EPS) {
    return {
      u,
      v: Infinity,
      magnification: Infinity,
      imageX: Infinity,
      imageHeight: Infinity,
      imageType: 'infinity',
      isReal: false,
      isInverted: null,
      lensX,
      axisY,
      rays: _infinityRays(lensX, axisY, objectX, objectHeight, f, boundBox),
    };
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
    u,
    v,
    magnification: m,
    imageX: ix,
    imageHeight: ih,
    imageType,
    isReal,
    isInverted: m < 0,
    lensX,
    axisY,
    lensType: f < 0 ? 'concave' : 'convex',
    rays: _principalRays(lensX, axisY, objectX, objectHeight, f, ix, ih, v, boundBox),
  };
}

function _principalRays(lx, ay, ox, oh, f, ix, ih, v, bounds) {
  const tip   = { x: ox, y: ay + oh };
  const isVirt = v < 0;
  const rays  = [];
  const slopeCenter = -oh / (lx - ox); // slope through optical center

  // Ray 1: Parallel to principal axis -> refracted through F2 (lx + f, ay)
  const slopeF2 = -oh / f;
  const r1Dir = { x: 1, y: slopeF2 };
  const r1End = rayToBounds({ x: lx, y: ay + oh }, r1Dir, bounds);

  if (isVirt) {
    // Real path exits lens to the right
    rays.push({
      id: 'r1',
      dashed: false,
      points: [tip, { x: lx, y: ay + oh }, r1End]
    });
    // Virtual extension backwards to image tip
    rays.push({
      id: 'r1v',
      dashed: true,
      points: [{ x: lx, y: ay + oh }, { x: ix, y: ay + ih }]
    });
  } else {
    const maxX = Math.max(ix, r1End.x);
    rays.push({
      id: 'r1',
      dashed: false,
      points: [tip, { x: lx, y: ay + oh }, { x: maxX, y: (ay + oh) + slopeF2 * (maxX - lx) }]
    });
  }

  // Ray 2: Undeviated through optical center O (lx, ay)
  const r2Dir = { x: 1, y: slopeCenter };
  const r2End = rayToBounds({ x: lx, y: ay }, r2Dir, bounds);

  if (isVirt) {
    rays.push({
      id: 'r2',
      dashed: false,
      points: [tip, { x: lx, y: ay }, r2End]
    });
    rays.push({
      id: 'r2v',
      dashed: true,
      points: [{ x: lx, y: ay }, { x: ix, y: ay + ih }]
    });
  } else {
    const maxX = Math.max(ix, r2End.x);
    rays.push({
      id: 'r2',
      dashed: false,
      points: [tip, { x: lx, y: ay }, { x: maxX, y: ay + slopeCenter * (maxX - lx) }]
    });
  }

  // Ray 3: Through/from F1 -> exits parallel to principal axis at height (ay + ih)
  const r3End = rayToBounds({ x: lx, y: ay + ih }, { x: 1, y: 0 }, bounds);

  if (isVirt) {
    rays.push({
      id: 'r3',
      dashed: false,
      points: [tip, { x: lx, y: ay + ih }, r3End]
    });
    rays.push({
      id: 'r3v',
      dashed: true,
      points: [{ x: lx, y: ay + ih }, { x: ix, y: ay + ih }]
    });
  } else {
    const maxX = Math.max(ix, r3End.x);
    rays.push({
      id: 'r3',
      dashed: false,
      points: [tip, { x: lx, y: ay + ih }, { x: maxX, y: ay + ih }]
    });
  }

  return rays;
}

function _infinityRays(lx, ay, ox, oh, f, bounds) {
  const tip = { x: ox, y: ay + oh };
  const slope = -oh / f;
  const r1End = rayToBounds({ x: lx, y: ay + oh }, { x: 1, y: slope }, bounds);
  const r2End = rayToBounds({ x: lx, y: ay }, { x: 1, y: slope }, bounds);
  return [
    {
      id: 'ri1',
      dashed: false,
      points: [tip, { x: lx, y: ay + oh }, r1End]
    },
    {
      id: 'ri2',
      dashed: false,
      points: [tip, { x: lx, y: ay }, r2End]
    }
  ];
}

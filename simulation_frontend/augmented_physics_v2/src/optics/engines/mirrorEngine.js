import { rayToBounds } from './rayGeometry.js';

const EPS = 0.5;

export function solveMirror({
  mirrorType = 'concave', // 'concave' | 'convex' | 'plane'
  mirrorX,
  axisY,
  objectX,
  objectHeight,
  focalLength,
  bounds = {},
}) {
  const isPlane = mirrorType === 'plane';
  const isConvex = mirrorType === 'convex';
  const boundBox = {
    minX: bounds.minX ?? 0,
    minY: bounds.minY ?? 0,
    maxX: bounds.maxX ?? bounds.width ?? 800,
    maxY: bounds.maxY ?? bounds.height ?? 600,
  };

  // Object distance u (positive to the left of mirror)
  const u = mirrorX - objectX;

  if (isPlane) {
    const v = -u; // behind mirror
    const m = 1.0;
    return {
      mirrorType,
      u,
      v,
      magnification: m,
      imageX: mirrorX - v,
      imageHeight: objectHeight,
      imageType: 'virtual_same_size',
      isReal: false,
      isInverted: false,
      rays: _planeMirrorRays(mirrorX, axisY, objectX, objectHeight, u, boundBox),
    };
  }

  // Signed focal length: positive for concave, negative for convex
  const f = isConvex ? -Math.abs(focalLength) : Math.abs(focalLength);

  if (Math.abs(u - f) < EPS) {
    return {
      mirrorType,
      u,
      v: Infinity,
      magnification: Infinity,
      imageX: Infinity,
      imageHeight: Infinity,
      imageType: 'infinity',
      isReal: false,
      isInverted: null,
      rays: [],
    };
  }

  // 1/v = 1/f - 1/u => v = (f * u) / (u - f)
  const v = (f * u) / (u - f);
  const m = -(v / u);
  const isReal = v > 0;
  const ix = mirrorX - v; // In front of mirror if v > 0 (left), behind if v < 0 (right)
  const ih = objectHeight * m;

  let imageType = isReal ? 'real' : 'virtual';
  if (Math.abs(m) > 1.05) imageType += '_magnified';
  else if (Math.abs(m) < 0.95) imageType += '_diminished';
  else imageType += '_same_size';

  return {
    mirrorType,
    u,
    v,
    magnification: m,
    imageX: ix,
    imageHeight: ih,
    imageType,
    isReal,
    isInverted: m < 0,
    rays: _sphericalMirrorRays(mirrorX, axisY, objectX, objectHeight, f, ix, ih, v, isConvex, boundBox),
  };
}

function _planeMirrorRays(mx, ay, ox, oh, u, bounds) {
  const tip = { x: ox, y: ay + oh };
  const ix = mx + u; // virtual image behind mirror
  const ih = oh;

  const r1End = rayToBounds({ x: mx, y: ay + oh }, { x: -1, y: 0 }, bounds);
  const r2End = rayToBounds({ x: mx, y: ay }, { x: -1, y: -oh / Math.max(1, mx - ox) }, bounds);

  return [
    // Ray 1: Normal incident (horizontal)
    {
      id: 'mr1',
      dashed: false,
      points: [tip, { x: mx, y: ay + oh }, r1End]
    },
    {
      id: 'mr1v',
      dashed: true,
      points: [{ x: mx, y: ay + oh }, { x: ix, y: ay + ih }]
    },
    // Ray 2: Incident to pole
    {
      id: 'mr2',
      dashed: false,
      points: [tip, { x: mx, y: ay }, r2End]
    },
    {
      id: 'mr2v',
      dashed: true,
      points: [{ x: mx, y: ay }, { x: ix, y: ay + ih }]
    }
  ];
}

function _sphericalMirrorRays(mx, ay, ox, oh, f, ix, ih, v, isConvex, bounds) {
  const tip = { x: ox, y: ay + oh };
  const rays = [];
  const focusX = mx - f;

  // Ray 1: Parallel to principal axis -> reflects through Focus
  const slopeF = (ay - (ay + oh)) / (focusX - mx);
  // Reflected ray goes leftwards from mirror surface: dx = -1, dy = -slopeF
  const r1End = rayToBounds({ x: mx, y: ay + oh }, { x: -1, y: -slopeF }, bounds);

  rays.push({
    id: 'smr1',
    dashed: false,
    points: [tip, { x: mx, y: ay + oh }, r1End]
  });

  if (v < 0) {
    // Virtual extension backwards behind mirror to image tip
    rays.push({
      id: 'smr1v',
      dashed: true,
      points: [{ x: mx, y: ay + oh }, { x: ix, y: ay + ih }]
    });
  }

  // Ray 2: Aimed at Pole (mx, ay) -> reflects at equal angle below axis
  const slopePole = -oh / (mx - ox);
  const r2End = rayToBounds({ x: mx, y: ay }, { x: -1, y: -slopePole }, bounds);

  rays.push({
    id: 'smr2',
    dashed: false,
    points: [tip, { x: mx, y: ay }, r2End]
  });

  if (v < 0) {
    rays.push({
      id: 'smr2v',
      dashed: true,
      points: [{ x: mx, y: ay }, { x: ix, y: ay + ih }]
    });
  }

  return rays;
}

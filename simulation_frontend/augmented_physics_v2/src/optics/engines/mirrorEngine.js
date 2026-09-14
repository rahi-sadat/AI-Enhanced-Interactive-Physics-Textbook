/** optics/engines/mirrorEngine.js
 * Pure mathematical solver for spherical and plane mirrors.
 * Handles concave, convex, and plane mirrors with principal rays and virtual dashed extensions.
 */
const EPS = 0.5;

export function solveMirror({
  mirrorType = 'concave', // 'concave' | 'convex' | 'plane'
  mirrorX,
  axisY,
  objectX,
  objectHeight,
  focalLength,
  facing = 'left' // 'left' | 'right'
}) {
  const isPlane = mirrorType === 'plane';
  const isConvex = mirrorType === 'convex';
  const dir = facing === 'right' ? 1 : -1;

  // Object distance u (positive on the reflective side of mirror)
  const u = dir * (objectX - mirrorX);

  if (isPlane) {
    const v = -u; // behind mirror
    const m = 1.0;
    return {
      mirrorType,
      facing,
      u,
      v,
      magnification: m,
      imageX: mirrorX + dir * v,
      imageHeight: objectHeight,
      imageType: 'virtual_same_size',
      isReal: false,
      isInverted: false,
      rays: _planeMirrorRays(mirrorX, axisY, objectX, objectHeight, u, dir)
    };
  }

  // Signed focal length: positive for concave, negative for convex
  const f = isConvex ? -Math.abs(focalLength) : Math.abs(focalLength);

  if (Math.abs(u - f) < EPS) {
    return {
      mirrorType,
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

  // 1/v = 1/f - 1/u => v = (f * u) / (u - f)
  const v = (f * u) / (u - f);
  const m = -(v / u);
  const isReal = v > 0;
  // In front of mirror if v > 0, behind if v < 0
  const ix = mirrorX + dir * v;
  const ih = objectHeight * m;

  let imageType = isReal ? 'real' : 'virtual';
  if (Math.abs(m) > 1.05) imageType += '_magnified';
  else if (Math.abs(m) < 0.95) imageType += '_diminished';
  else imageType += '_same_size';

  return {
    mirrorType,
    facing,
    u,
    v,
    magnification: m,
    imageX: ix,
    imageHeight: ih,
    imageType,
    isReal,
    isInverted: m < 0,
    rays: _sphericalMirrorRays(mirrorX, axisY, objectX, objectHeight, f, ix, ih, v, isConvex, dir)
  };
}

function _planeMirrorRays(mx, ay, ox, oh, u, dir = -1) {
  const tip = { x: ox, y: ay + oh };
  const ix = mx - dir * u; // virtual image behind mirror
  const ih = oh;
  const farX = dir === 1 ? 800 : 0;

  return [
    // Ray 1: Normal incident (horizontal)
    {
      id: 'mr1',
      dashed: false,
      points: [tip, { x: mx, y: ay + oh }, { x: farX, y: ay + oh }]
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
      points: [tip, { x: mx, y: ay }, { x: farX, y: ay - oh }]
    },
    {
      id: 'mr2v',
      dashed: true,
      points: [{ x: mx, y: ay }, { x: ix, y: ay + ih }]
    }
  ];
}

function _sphericalMirrorRays(mx, ay, ox, oh, f, ix, ih, v, isConvex, dir = -1) {
  const tip = { x: ox, y: ay + oh };
  const rays = [];
  const focusX = mx + dir * f;
  const farX = dir === 1 ? 800 : 0;

  // Ray 1: Parallel to principal axis -> reflects through Focus
  const slopeF = (ay - (ay + oh)) / (focusX - mx);

  rays.push({
    id: 'smr1',
    dashed: false,
    points: [tip, { x: mx, y: ay + oh }, { x: farX, y: (ay + oh) + slopeF * (farX - mx) }]
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
  rays.push({
    id: 'smr2',
    dashed: false,
    points: [tip, { x: mx, y: ay }, { x: farX, y: ay + slopePole * (farX - mx) }]
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

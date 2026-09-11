/** optics/engines/rayGeometry.js
 * Shared 2D vector math for all optics solvers. No DOM, no canvas.
 */
export function normalize(v) {
  const len = Math.hypot(v.x, v.y);
  return len === 0 ? {x:0,y:0} : {x: v.x/len, y: v.y/len};
}
export function dot(a, b) { return a.x*b.x + a.y*b.y; }
export function scale(v, s) { return {x: v.x*s, y: v.y*s}; }
export function add(a, b)   { return {x: a.x+b.x, y: a.y+b.y}; }
export function sub(a, b)   { return {x: a.x-b.x, y: a.y-b.y}; }

export function reflect(incident, normal) {
  const d = dot(incident, normal);
  return {x: incident.x - 2*d*normal.x, y: incident.y - 2*d*normal.y};
}

export function refract(incident, normal, n1, n2) {
  const I = normalize(incident);
  let N   = normalize(normal);
  let cosI = -dot(N, I);
  if (cosI < 0) { N = {x:-N.x, y:-N.y}; cosI = -dot(N, I); }
  const eta = n1 / n2;
  const k   = 1 - eta*eta*(1 - cosI*cosI);
  if (k < 0) return { type: 'tir', direction: normalize(reflect(I, N)) };
  const sq = Math.sqrt(k);
  return {
    type: 'refracted',
    direction: normalize({x: eta*I.x+(eta*cosI-sq)*N.x, y: eta*I.y+(eta*cosI-sq)*N.y})
  };
}

export function rayToCanvasBoundary(origin, dir, W=800, H=600) {
  const {x:ox,y:oy} = origin, {x:dx,y:dy} = dir;
  let t = Infinity;
  if (dx>0) t = Math.min(t,(W-ox)/dx);
  if (dx<0) t = Math.min(t,(0-ox)/dx);
  if (dy>0) t = Math.min(t,(H-oy)/dy);
  if (dy<0) t = Math.min(t,(0-oy)/dy);
  return {x: ox+dx*t, y: oy+dy*t};
}

export function raySegmentIntersection(origin, dir, A, B) {
  const dx = dir.x, dy = dir.y;
  const sx = B.x - A.x, sy = B.y - A.y;
  const det = dx * sy - dy * sx;
  if (Math.abs(det) < 1e-7) return null;

  const qx = A.x - origin.x, qy = A.y - origin.y;
  const t = (qx * sy - qy * sx) / det;
  const u = (qx * dy - qy * dx) / det;

  if (t > 1e-4 && u >= 0 && u <= 1) {
    return {
      point: { x: origin.x + dx * t, y: origin.y + dy * t },
      distance: t,
      paramU: u
    };
  }
  return null;
}

export function getEdgeNormal(A, B, insidePoint) {
  // Edge vector from A to B: (dx, dy). Normal is (-dy, dx) or (dy, -dx)
  const dx = B.x - A.x, dy = B.y - A.y;
  let N = normalize({ x: -dy, y: dx });
  // Ensure normal points OUTWARD (opposite to insidePoint relative to edge center)
  const mid = { x: (A.x + B.x) / 2, y: (A.y + B.y) / 2 };
  const toInside = { x: insidePoint.x - mid.x, y: insidePoint.y - mid.y };
  if (dot(N, toInside) > 0) {
    N = { x: -N.x, y: -N.y };
  }
  return N;
}


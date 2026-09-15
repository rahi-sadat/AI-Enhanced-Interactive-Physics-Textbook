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

export function rayToBounds(origin, direction, bounds = {}) {
  const minX = bounds.minX ?? 0;
  const minY = bounds.minY ?? 0;
  const maxX = bounds.maxX ?? bounds.width ?? 800;
  const maxY = bounds.maxY ?? bounds.height ?? 600;

  const dx = direction.x;
  const dy = direction.y;
  const candidates = [];

  if (Math.abs(dx) > 1e-12) {
    const t1 = (minX - origin.x) / dx;
    const t2 = (maxX - origin.x) / dx;
    if (t1 > 1e-6) candidates.push(t1);
    if (t2 > 1e-6) candidates.push(t2);
  }

  if (Math.abs(dy) > 1e-12) {
    const t1 = (minY - origin.y) / dy;
    const t2 = (maxY - origin.y) / dy;
    if (t1 > 1e-6) candidates.push(t1);
    if (t2 > 1e-6) candidates.push(t2);
  }

  let best = Infinity;
  for (const t of candidates) {
    const x = origin.x + dx * t;
    const y = origin.y + dy * t;
    if (
      x >= minX - 1e-4 &&
      x <= maxX + 1e-4 &&
      y >= minY - 1e-4 &&
      y <= maxY + 1e-4
    ) {
      best = Math.min(best, t);
    }
  }

  if (!Number.isFinite(best)) {
    return { x: origin.x + dx * 1000, y: origin.y + dy * 1000 };
  }

  return {
    x: origin.x + dx * best,
    y: origin.y + dy * best,
  };
}

export function boundaryNormal(p1, p2) {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const len = Math.hypot(dx, dy);
  if (len === 0) return { x: 0, y: 1 };
  return {
    x: -dy / len,
    y: dx / len,
  };
}

export function rayToCanvasBoundary(origin, dir, W = 800, H = 600) {
  return rayToBounds(origin, dir, { minX: 0, minY: 0, maxX: W, maxY: H });
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


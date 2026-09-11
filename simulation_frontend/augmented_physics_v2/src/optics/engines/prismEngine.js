/** optics/engines/prismEngine.js
 * Pure mathematical solver for polygonal prism refraction via Snell's Law.
 * Does not depend on DOM, canvas, or p5.
 */
import {
  normalize,
  dot,
  refract,
  reflect,
  raySegmentIntersection,
  getEdgeNormal,
  rayToCanvasBoundary
} from './rayGeometry.js';

export function solvePrismRefraction({ prismVertices, refractiveIndex = 1.52, rayOrigin, rayDirection }) {
  const nAir = 1.0;
  const nGlass = refractiveIndex;
  const I0 = normalize(rayDirection);

  // Compute centroid of prism to orient surface normals outward
  let cx = 0, cy = 0;
  const nVerts = prismVertices.length;
  prismVertices.forEach(v => { cx += v.x; cy += v.y; });
  const centroid = { x: cx / nVerts, y: cy / nVerts };

  const edges = [];
  for (let i = 0; i < nVerts; i++) {
    const A = prismVertices[i];
    const B = prismVertices[(i + 1) % nVerts];
    edges.push({ A, B, normal: getEdgeNormal(A, B, centroid) });
  }

  // 1. Find first intersection (Air -> Glass)
  let hit1 = null;
  let minT1 = Infinity;
  let hitEdge1 = null;

  for (const edge of edges) {
    const hit = raySegmentIntersection(rayOrigin, I0, edge.A, edge.B);
    if (hit && hit.distance < minT1) {
      minT1 = hit.distance;
      hit1 = hit.point;
      hitEdge1 = edge;
    }
  }

  if (!hit1) {
    // Ray misses prism completely
    const exitPt = rayToCanvasBoundary(rayOrigin, I0);
    return {
      hitPrism: false,
      segments: [{ type: 'incident', start: rayOrigin, end: exitPt }],
      normals: [],
      angles: null,
      tir: false
    };
  }

  // Refraction at face 1 (Air -> Glass)
  const N1 = hitEdge1.normal; // Points outward from prism
  const refr1 = refract(I0, N1, nAir, nGlass);

  // Normal lines for visual rendering (drawn 35px outward & inward)
  const normalViz1 = {
    p1: { x: hit1.x + N1.x * 35, y: hit1.y + N1.y * 35 },
    p2: { x: hit1.x - N1.x * 35, y: hit1.y - N1.y * 35 }
  };

  // Angle of incidence i1 (angle between incident ray and -N1)
  const cosI1 = Math.min(1.0, Math.max(0.0, -dot(I0, N1)));
  const i1Deg = (Math.acos(cosI1) * 180) / Math.PI;

  // Internal ray direction
  const I_internal = refr1.direction;
  const cosR1 = Math.min(1.0, Math.max(0.0, dot(I_internal, { x: -N1.x, y: -N1.y })));
  const r1Deg = (Math.acos(cosR1) * 180) / Math.PI;

  // 2. Find second intersection (Glass -> Air) inside prism
  let hit2 = null;
  let minT2 = Infinity;
  let hitEdge2 = null;

  for (const edge of edges) {
    if (edge === hitEdge1) continue; // Ray came from this edge
    const hit = raySegmentIntersection(hit1, I_internal, edge.A, edge.B);
    if (hit && hit.distance < minT2) {
      minT2 = hit.distance;
      hit2 = hit.point;
      hitEdge2 = edge;
    }
  }

  if (!hit2) {
    return {
      hitPrism: true,
      segments: [
        { type: 'incident', start: rayOrigin, end: hit1 },
        { type: 'internal', start: hit1, end: rayToCanvasBoundary(hit1, I_internal) }
      ],
      normals: [normalViz1],
      angles: { i1: i1Deg, r1: r1Deg },
      tir: false
    };
  }

  // Refraction at face 2 (Glass -> Air)
  const N2 = hitEdge2.normal; // Outward normal
  const normalViz2 = {
    p1: { x: hit2.x + N2.x * 35, y: hit2.y + N2.y * 35 },
    p2: { x: hit2.x - N2.x * 35, y: hit2.y - N2.y * 35 }
  };

  const refr2 = refract(I_internal, N2, nGlass, nAir);
  const isTir = refr2.type === 'tir';

  const emergentDir = refr2.direction;
  const endPoint = rayToCanvasBoundary(hit2, emergentDir);

  // Compute angle of deviation delta = angle between I0 and emergentDir
  const cosDelta = Math.min(1.0, Math.max(-1.0, dot(I0, emergentDir)));
  const deviationDeg = (Math.acos(cosDelta) * 180) / Math.PI;

  return {
    hitPrism: true,
    tir: isTir,
    hit1,
    hit2,
    N1,
    N2,
    I0,
    I_internal,
    segments: [
      { type: 'incident', start: rayOrigin, end: hit1 },
      { type: 'internal', start: hit1, end: hit2 },
      { type: isTir ? 'tir_reflected' : 'emergent', start: hit2, end: endPoint }
    ],
    normals: [normalViz1, normalViz2],
    angles: {
      i1Deg,
      r1Deg,
      deviationDeg: isTir ? null : deviationDeg,
      criticalAngleDeg: (Math.asin(nAir / nGlass) * 180) / Math.PI
    }
  };
}

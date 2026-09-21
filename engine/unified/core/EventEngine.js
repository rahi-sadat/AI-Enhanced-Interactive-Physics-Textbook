/**
 * EventEngine.js
 * 
 * Shared, domain-agnostic event detection and boundary intersection engine.
 * Solves 2D geometric intersections (ray-segment, ray-arc, particle-boundary)
 * and dispatches event redirects via physical rules (impulse, Snell's law, reflection).
 */

const EPSILON = 1e-9;

export class EventEngine {
  static dot(a, b) {
    return a.x * b.x + a.y * b.y;
  }

  static normalize(v) {
    const len = Math.hypot(v.x, v.y);
    return len < EPSILON ? { x: 0, y: 0 } : { x: v.x / len, y: v.y / len };
  }

  /**
   * Finds the intersection between a ray (origin, dir) and a finite line segment (p1 -> p2).
   * 
   * @param {{x: number, y: number}} origin - Ray origin
   * @param {{x: number, y: number}} dir - Normalized ray direction
   * @param {{x: number, y: number}} p1 - Segment start
   * @param {{x: number, y: number}} p2 - Segment end
   * @returns {{ hit: boolean, distance: number, point: {x: number, y: number}, normal: {x: number, y: number} }|null}
   */
  static rayIntersectSegment(origin, dir, p1, p2) {
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;

    const cross = dir.x * dy - dir.y * dx;
    if (Math.abs(cross) < EPSILON) {
      return null; // Parallel or collinear
    }

    const qx = p1.x - origin.x;
    const qy = p1.y - origin.y;

    const t = (qx * dy - qy * dx) / cross; // Ray parametric distance
    const u = (qx * dir.y - qy * dir.x) / cross; // Segment fraction [0, 1]

    if (t > EPSILON && u >= -EPSILON && u <= 1.0 + EPSILON) {
      // Outward unit normal to segment (p1 -> p2) rotated counter-clockwise
      const segLen = Math.hypot(dx, dy);
      if (segLen < EPSILON) return null;

      let nx = -dy / segLen;
      let ny = dx / segLen;

      // Ensure normal faces against incident direction (dot(dir, normal) <= 0)
      if (dir.x * nx + dir.y * ny > 0) {
        nx = -nx;
        ny = -ny;
      }

      return {
        hit: true,
        distance: t,
        point: {
          x: origin.x + t * dir.x,
          y: origin.y + t * dir.y
        },
        normal: { x: nx, y: ny }
      };
    }

    return null;
  }

  /**
   * Finds the intersection between a ray and a circular arc.
   * Circle equation: (x - cx)^2 + (y - cy)^2 = R^2
   * @param {{x: number, y: number}} origin
   * @param {{x: number, y: number}} dir
   * @param {{x: number, y: number}} center
   * @param {number} radius
   * @param {number} [startAngle=0]
   * @param {number} [endAngle=Math.PI*2]
   * @returns {{ hit: boolean, distance: number, point: {x: number, y: number}, normal: {x: number, y: number} }|null}
   */
  static rayIntersectArc(origin, dir, center, radius, startAngle = 0, endAngle = Math.PI * 2) {
    const ox = origin.x - center.x;
    const oy = origin.y - center.y;

    // Quadratic: t^2 * (dir.x^2 + dir.y^2) + 2t*(ox*dir.x + oy*dir.y) + (ox^2 + oy^2 - R^2) = 0
    const a = dir.x * dir.x + dir.y * dir.y;
    const b = 2.0 * (ox * dir.x + oy * dir.y);
    const c = ox * ox + oy * oy - radius * radius;

    const disc = b * b - 4.0 * a * c;
    if (disc < 0) return null;

    const sqrtDisc = Math.sqrt(disc);
    const t1 = (-b - sqrtDisc) / (2.0 * a);
    const t2 = (-b + sqrtDisc) / (2.0 * a);

    const candidates = [t1, t2].filter(t => t > EPSILON).sort((p, q) => p - q);

    for (const t of candidates) {
      const hitX = origin.x + t * dir.x;
      const hitY = origin.y + t * dir.y;

      // Check arc angle constraint
      let angle = Math.atan2(hitY - center.y, hitX - center.x);
      if (angle < 0) angle += 2.0 * Math.PI;

      let inArc = false;
      const sA = (startAngle % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
      const eA = (endAngle % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);

      if (sA <= eA) {
        inArc = angle >= sA - EPSILON && angle <= eA + EPSILON;
      } else {
        inArc = angle >= sA - EPSILON || angle <= eA + EPSILON;
      }

      if (inArc) {
        let nx = (hitX - center.x) / radius;
        let ny = (hitY - center.y) / radius;

        if (dir.x * nx + dir.y * ny > 0) {
          nx = -nx;
          ny = -ny;
        }

        return {
          hit: true,
          distance: t,
          point: { x: hitX, y: hitY },
          normal: { x: nx, y: ny }
        };
      }
    }

    return null;
  }

  /**
   * Intersects a ray with rectangular bounds (axis-aligned bounding box).
   * @param {{x: number, y: number}} origin
   * @param {{x: number, y: number}} dir
   * @param {{minX: number, minY: number, maxX: number, maxY: number}} bounds
   * @returns {{x: number, y: number}} Bounded endpoint
   */
  static rayToBounds(origin, dir, bounds) {
    const minX = bounds.minX ?? 0;
    const minY = bounds.minY ?? 0;
    const maxX = bounds.maxX ?? 800;
    const maxY = bounds.maxY ?? 600;

    let tMin = Infinity;

    if (Math.abs(dir.x) > EPSILON) {
      const tLeft = (minX - origin.x) / dir.x;
      if (tLeft > EPSILON) {
        const y = origin.y + tLeft * dir.y;
        if (y >= minY - EPSILON && y <= maxY + EPSILON && tLeft < tMin) tMin = tLeft;
      }
      const tRight = (maxX - origin.x) / dir.x;
      if (tRight > EPSILON) {
        const y = origin.y + tRight * dir.y;
        if (y >= minY - EPSILON && y <= maxY + EPSILON && tRight < tMin) tMin = tRight;
      }
    }

    if (Math.abs(dir.y) > EPSILON) {
      const tTop = (minY - origin.y) / dir.y;
      if (tTop > EPSILON) {
        const x = origin.x + tTop * dir.x;
        if (x >= minX - EPSILON && x <= maxX + EPSILON && tTop < tMin) tMin = tTop;
      }
      const tBottom = (maxY - origin.y) / dir.y;
      if (tBottom > EPSILON) {
        const x = origin.x + tBottom * dir.x;
        if (x >= minX - EPSILON && x <= maxX + EPSILON && tBottom < tMin) tMin = tBottom;
      }
    }

    if (tMin < Infinity) {
      return {
        x: origin.x + tMin * dir.x,
        y: origin.y + tMin * dir.y
      };
    }

    // Fallback: large distance clamp
    return {
      x: origin.x + 2000 * dir.x,
      y: origin.y + 2000 * dir.y
    };
  }

  // =========================================================================
  // PHYSICAL REDIRECT DISPATCH RULES
  // =========================================================================

  /**
   * Elastic/Inelastic Collision Redirect Rule:
   * v' = v - (1 + restitution) * (v . normal) * normal
   * 
   * @param {{x: number, y: number}} velocity
   * @param {{x: number, y: number}} normal - Unit surface normal pointing away from obstacle
   * @param {number} [restitution=1.0] - Coefficient of restitution (0 = plastic, 1 = elastic)
   * @returns {{x: number, y: number}} Reflected velocity
   */
  static redirectCollision(velocity, normal, restitution = 1.0) {
    const vDotN = velocity.x * normal.x + velocity.y * normal.y;
    if (vDotN >= 0) return { x: velocity.x, y: velocity.y }; // Moving away

    const factor = (1.0 + restitution) * vDotN;
    return {
      x: velocity.x - factor * normal.x,
      y: velocity.y - factor * normal.y
    };
  }

  /**
   * Optical Mirror Law of Reflection Redirect Rule:
   * r = d - 2 * (d . normal) * normal
   * 
   * @param {{x: number, y: number}} dir - Incident ray unit direction
   * @param {{x: number, y: number}} normal - Surface unit normal
   * @returns {{x: number, y: number}} Reflected unit direction
   */
  static redirectReflection(dir, normal) {
    const dDotN = dir.x * normal.x + dir.y * normal.y;
    return {
      x: dir.x - 2.0 * dDotN * normal.x,
      y: dir.y - 2.0 * dDotN * normal.y
    };
  }

  /**
   * Snell's Law Vector Refraction Redirect Rule:
   * Computes transmitted unit vector through medium 1 -> medium 2 interface.
   * Handles Total Internal Reflection (TIR) when sin(theta2) > 1.
   * 
   * @param {{x: number, y: number}} dir - Incident ray unit direction
   * @param {{x: number, y: number}} normal - Surface unit normal (facing medium 1)
   * @param {number} n1 - Refractive index of incident medium
   * @param {number} n2 - Refractive index of transmitted medium
   * @returns {{ refracted: boolean, tir: boolean, direction: {x: number, y: number}, criticalAngleDeg: number|null }}
   */
  static redirectRefraction(dir, normal, n1, n2) {
    let nx = normal.x;
    let ny = normal.y;
    let dDotN = dir.x * nx + dir.y * ny;

    let eta = n1 / n2;
    if (dDotN > 0) {
      // Ray is passing from medium 2 to medium 1 (inside to outside)
      nx = -nx;
      ny = -ny;
      dDotN = -dDotN;
      eta = n2 / n1;
    }

    // cos(theta1) = - (dir . n)
    const cosTheta1 = -dDotN;
    const sin2Theta1 = Math.max(0.0, 1.0 - cosTheta1 * cosTheta1);
    const sin2Theta2 = eta * eta * sin2Theta1;

    let criticalAngleDeg = null;
    if (n1 > n2) {
      criticalAngleDeg = (Math.asin(n2 / n1) * 180.0) / Math.PI;
    }

    // Total Internal Reflection check
    if (sin2Theta2 > 1.0 + EPSILON) {
      // Ray undergoes TIR -> redirect as reflection
      const reflDir = this.redirectReflection(dir, { x: nx, y: ny });
      return {
        refracted: false,
        tir: true,
        direction: reflDir,
        criticalAngleDeg
      };
    }

    // Snell vector formulation:
    // t = eta * dir + (eta * cosTheta1 - sqrt(1 - sin2Theta2)) * n
    const cosTheta2 = Math.sqrt(Math.max(0.0, 1.0 - sin2Theta2));
    const factor = eta * cosTheta1 - cosTheta2;

    const tx = eta * dir.x + factor * nx;
    const ty = eta * dir.y + factor * ny;

    // Normalize resulting vector
    const tLen = Math.hypot(tx, ty) || 1.0;

    return {
      refracted: true,
      tir: false,
      direction: { x: tx / tLen, y: ty / tLen },
      criticalAngleDeg
    };
  }
}

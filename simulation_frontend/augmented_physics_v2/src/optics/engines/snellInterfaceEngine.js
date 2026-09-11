/** optics/engines/snellInterfaceEngine.js
 * Physics solver for Single-Surface Plane Interface Refraction (Snell's Law).
 *
 * Models light propagation across a plane boundary between Medium 1 (top) and Medium 2 (bottom):
 *   - Snell's Law: n1 * sin(theta1) = n2 * sin(theta2)
 *   - Critical Angle: theta_c = arcsin(n2 / n1) when n1 > n2
 *   - Total Internal Reflection (TIR) when theta1 > theta_c
 *   - Generates incident ray, refracted ray, reflected ray, normal line, and angle arcs.
 */

export function traceInterfaceRefraction(config) {
  const boundaryY = config.boundaryY ?? 300;
  const normalX   = config.normalX   ?? 400;
  const n1        = Math.max(1.0, config.n1 ?? 1.0);  // e.g. 1.0 for air / rarer medium
  const n2        = Math.max(1.0, config.n2 ?? 1.52); // e.g. 1.52 for denser medium

  const canvasW = config.canvasW ?? 800;
  const canvasH = config.canvasH ?? 600;

  // Incident point on boundary
  const P0 = { x: normalX, y: boundaryY };

  // Calculate incident angle theta1
  let theta1Rad = 0;
  let sourceX = normalX - 180;
  let sourceY = boundaryY - 180;

  if (config.source) {
    sourceX = config.source.x;
    sourceY = config.source.y;
    // Angle relative to vertical normal
    const dx = P0.x - sourceX;
    const dy = P0.y - sourceY;
    theta1Rad = Math.atan2(Math.abs(dx), Math.max(0.1, dy));
  } else if (config.theta1Deg !== undefined) {
    theta1Rad = (config.theta1Deg * Math.PI) / 180;
    const rayLen = 220;
    sourceX = normalX - rayLen * Math.sin(theta1Rad);
    sourceY = boundaryY - rayLen * Math.cos(theta1Rad);
  } else {
    // Default 45 degrees
    theta1Rad = (45 * Math.PI) / 180;
    sourceX = normalX - 180;
    sourceY = boundaryY - 180;
  }

  // Clamp theta1 to [0, 89.9 deg]
  theta1Rad = Math.max(0, Math.min(1.56, theta1Rad));
  const theta1Deg = (theta1Rad * 180) / Math.PI;

  // Direction: coming from left or right of normal
  const fromLeft = sourceX <= normalX;
  const signX = fromLeft ? 1 : -1;

  // Critical angle (only exists if n1 > n2)
  let criticalAngleDeg = null;
  let isTIR = false;
  let theta2Rad = 0;

  if (n1 > n2) {
    const critRad = Math.asin(n2 / n1);
    criticalAngleDeg = (critRad * 180) / Math.PI;
    if (theta1Rad > critRad) {
      isTIR = true;
    }
  }

  // Calculate refraction angle theta2 via Snell's Law
  const sinTheta2 = (n1 / n2) * Math.sin(theta1Rad);
  if (sinTheta2 > 1.0) {
    isTIR = true;
  } else if (!isTIR) {
    theta2Rad = Math.asin(Math.max(-1.0, Math.min(1.0, sinTheta2)));
  }

  const theta2Deg = (theta2Rad * 180) / Math.PI;

  // Build rays
  const incidentRay = [
    { x: sourceX, y: sourceY },
    P0,
  ];

  let refractedRay = null;
  let reflectedRay = null;

  const rayExtension = Math.max(canvasW, canvasH);

  if (isTIR) {
    // Total Internal Reflection back into Medium 1
    const reflectEnd = {
      x: P0.x + signX * rayExtension * Math.sin(theta1Rad),
      y: P0.y - rayExtension * Math.cos(theta1Rad),
    };
    reflectedRay = [P0, reflectEnd];
  } else {
    // Refraction into Medium 2
    const refractEnd = {
      x: P0.x + signX * rayExtension * Math.sin(theta2Rad),
      y: P0.y + rayExtension * Math.cos(theta2Rad),
    };
    refractedRay = [P0, refractEnd];

    // Weak partial reflection in Medium 1
    const partialReflectEnd = {
      x: P0.x + signX * 180 * Math.sin(theta1Rad),
      y: P0.y - 180 * Math.cos(theta1Rad),
    };
    reflectedRay = [P0, partialReflectEnd];
  }

  // Normal line (dashed, passes through P0)
  const normalTop = { x: normalX, y: Math.max(20, boundaryY - 220) };
  const normalBottom = { x: normalX, y: Math.min(canvasH - 20, boundaryY + 220) };
  const normalLine = [normalTop, normalBottom];

  // Boundary line
  const boundaryLine = [
    { x: 0, y: boundaryY },
    { x: canvasW, y: boundaryY },
  ];

  return {
    subtype: 'interface_refraction',
    P0,
    boundaryY,
    normalX,
    n1,
    n2,
    theta1Deg,
    theta2Deg,
    criticalAngleDeg,
    angles: {
      theta1Deg,
      theta2Deg,
      theta1Rad,
      theta2Rad,
      criticalAngleDeg,
    },
    isTIR,
    incidentRay,
    refractedRay,
    reflectedRay,
    normalLine,
    boundaryLine,
    source: { x: sourceX, y: sourceY },
    hud: {
      title: 'Refraction at Interface (Snell\'s Law)',
      n1: n1.toFixed(2),
      n2: n2.toFixed(2),
      theta1: `${theta1Deg.toFixed(1)}°`,
      theta2: isTIR ? 'TIR (No transmission)' : `${theta2Deg.toFixed(1)}°`,
      criticalAngle: criticalAngleDeg !== null ? `${criticalAngleDeg.toFixed(1)}°` : 'None (n1 ≤ n2)',
      isTIR,
      stateLabel: isTIR
        ? '⚡ TOTAL INTERNAL REFLECTION (θ₁ > θc)'
        : (n1 < n2 ? 'Bends TOWARDS normal (n₁ < n₂)' : 'Bends AWAY from normal (n₁ > n₂)'),
      formula: 'n₁ · sin(θ₁) = n₂ · sin(θ₂)',
    },
  };
}

export function solveSnellInterface(n1, n2, theta1Deg) {
  const theta1Rad = (theta1Deg * Math.PI) / 180;
  const sinTheta1 = Math.sin(theta1Rad);
  let thetaCritDeg = null;
  let isTIR = false;
  let theta2Rad = null;
  let theta2Deg = null;

  if (n1 > n2) {
    const critRad = Math.asin(n2 / n1);
    thetaCritDeg = (critRad * 180) / Math.PI;
    if (theta1Deg > thetaCritDeg) {
      isTIR = true;
    }
  }

  if (!isTIR) {
    const sinTheta2 = (n1 / n2) * sinTheta1;
    if (Math.abs(sinTheta2) <= 1.0) {
      theta2Rad = Math.asin(sinTheta2);
      theta2Deg = (theta2Rad * 180) / Math.PI;
    } else {
      isTIR = true;
    }
  }

  return {
    isTIR,
    thetaCritDeg,
    theta1Deg,
    theta1Rad,
    theta2Deg,
    theta2Rad,
  };
}


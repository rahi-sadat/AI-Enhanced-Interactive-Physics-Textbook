/**
 * PlaceholderMechanicsAdapter.js
 * 
 * Minimal mechanics adapter used for headless validation of the UnifiedEngineCore.
 * Models a 1D damped harmonic oscillator (Hooke's Law + viscous damping)
 * and particle bouncing off a ground plane (Newton's law of restitution).
 */

import { EventEngine } from '../core/EventEngine.js';

export class PlaceholderMechanicsAdapter {
  constructor() {
    this.core = null;
    this.mass = 1.0;
    this.k = 10.0;          // Spring constant (N/m)
    this.restLength = 0.0;  // Equilibrium position
    this.damping = 0.0;     // Viscous drag coefficient (N*s/m)
    this.gravity = 9.81;    // Gravitational acceleration (m/s^2)
    this.groundY = 500.0;   // Ground collision boundary (px)
    this.restitution = 0.8; // Bouncing coefficient
  }

  attachCore(core) {
    this.core = core;
  }

  compileScene(scene) {
    this.mass = Number(scene?.mass ?? 1.0);
    this.k = Number(scene?.k ?? 10.0);
    this.restLength = Number(scene?.restLength ?? 0.0);
    this.damping = Number(scene?.damping ?? 0.0);
    this.gravity = Number(scene?.gravity ?? 0.0);
    this.groundY = Number(scene?.groundY ?? 500.0);
    this.restitution = Number(scene?.restitution ?? 0.8);

    const initialQ = scene?.initialPosition ?? [1.0];
    const initialV = scene?.initialVelocity ?? [0.0];

    return {
      isAlgebraic: false,
      q: initialQ,
      v: initialV,
      invMass: [1.0 / this.mass]
    };
  }

  /**
   * Evaluates generalized forces at state (q, v).
   * Encodes:
   *   1. Hooke's Law: F_spring = -k * (x - x_0)
   *   2. Stokes' Viscous Drag: F_drag = -gamma * v
   *   3. Newton's Second Law with Gravity: F_grav = m * g
   */
  evaluateForces(q, v, t) {
    const x = q[0];
    const vx = v[0];

    // Physical Law 1: Hooke's Law restoring force: F = -k * (x - x_0)
    const fSpring = -this.k * (x - this.restLength);

    // Physical Law 2: Viscous friction damping: F = -damping * v
    const fDamping = -this.damping * vx;

    // Physical Law 3: Constant gravity force: F = m * g
    const fGravity = this.mass * this.gravity;

    const totalForce = fSpring + fDamping + fGravity;
    return new Float64Array([totalForce]);
  }

  /**
   * Boundary event detection:
   * Checks if particle penetrates ground barrier y >= groundY.
   * Encodes Newton's Experimental Law of Restitution: v' = -e * v.
   */
  checkEvents(q, v, dt) {
    if (this.gravity > 0 && q[0] >= this.groundY) {
      q[0] = this.groundY;
      // Physical Law: Restitution impulse redirect
      const redirected = EventEngine.redirectCollision(
        { x: 0, y: v[0] },
        { x: 0, y: -1 }, // Normal pointing upwards from ground
        this.restitution
      );
      v[0] = redirected.y;
    }
  }

  hasConstraints() {
    return false;
  }

  extractState(core) {
    const x = core.q[0] || 0;
    const v = core.v[0] || 0;
    // Mechanical energy: E = 0.5 * m * v^2 + 0.5 * k * x^2
    const kineticEnergy = 0.5 * this.mass * v * v;
    const potentialEnergy = 0.5 * this.k * Math.pow(x - this.restLength, 2);

    return {
      position: x,
      velocity: v,
      kineticEnergy,
      potentialEnergy,
      totalEnergy: kineticEnergy + potentialEnergy
    };
  }
}

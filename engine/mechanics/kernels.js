/**
 * engine/mechanics/kernels.js
 * 
 * Pure mathematical physics kernels for Mechanics domain.
 * Completely headless, zero DOM/Canvas dependencies.
 * Shared directly as the single authoritative physics source of truth
 * for both headless runtime verification and browser rendering.
 */

export class PendulumKernel {
  constructor({ lengthM, gravityMS2, theta0Rad, omega0Rad = 0.0, massKg, damping }) {
    if (!Number.isFinite(lengthM) || lengthM <= 0) {
      throw new Error(`[PendulumKernel] Invalid length: ${lengthM}`);
    }
    if (!Number.isFinite(gravityMS2) || gravityMS2 < 0) {
      throw new Error(`[PendulumKernel] Invalid gravity: ${gravityMS2}`);
    }
    if (!Number.isFinite(theta0Rad)) {
      throw new Error(`[PendulumKernel] Invalid initial angle: ${theta0Rad}`);
    }
    if (!Number.isFinite(massKg) || massKg <= 0) {
      throw new Error(`[PendulumKernel] Invalid mass: ${massKg}`);
    }
    if (!Number.isFinite(damping) || damping < 0) {
      throw new Error(`[PendulumKernel] Invalid damping: ${damping}`);
    }

    this.lengthM = lengthM;
    this.g = gravityMS2;
    this.theta0 = theta0Rad;
    this.omega0 = omega0Rad;
    this.massKg = massKg;
    this.damping = damping;

    this.theta = theta0Rad;
    this.omega = omega0Rad;
    this.simTime = 0.0;
  }

  derivative(th, om) {
    return {
      thetaDot: om,
      omegaDot: -(this.g / this.lengthM) * Math.sin(th) - this.damping * om
    };
  }

  step(dt) {
    const subDt = 1.0 / 240.0;
    let remaining = dt;
    while (remaining > 0) {
      const stepSize = Math.min(remaining, subDt);
      const t0 = this.theta;
      const w0 = this.omega;

      const k1 = this.derivative(t0, w0);
      const k2 = this.derivative(t0 + 0.5 * stepSize * k1.thetaDot, w0 + 0.5 * stepSize * k1.omegaDot);
      const k3 = this.derivative(t0 + 0.5 * stepSize * k2.thetaDot, w0 + 0.5 * stepSize * k2.omegaDot);
      const k4 = this.derivative(t0 + stepSize * k3.thetaDot, w0 + stepSize * k3.omegaDot);

      this.theta += (stepSize / 6.0) * (k1.thetaDot + 2.0 * k2.thetaDot + 2.0 * k3.thetaDot + k4.thetaDot);
      this.omega += (stepSize / 6.0) * (k1.omegaDot + 2.0 * k2.omegaDot + 2.0 * k3.omegaDot + k4.omegaDot);
      this.simTime += stepSize;
      remaining -= stepSize;
    }
  }

  reset() {
    this.theta = this.theta0;
    this.omega = this.omega0;
    this.simTime = 0.0;
  }

  getEnergy() {
    const heightM = this.lengthM * (1.0 - Math.cos(this.theta));
    const speed = Math.abs(this.omega * this.lengthM);
    const pe = this.massKg * this.g * heightM;
    const ke = 0.5 * this.massKg * speed * speed;
    return { pe, ke, total: pe + ke, speed };
  }
}

export class ProjectileKernel {
  constructor({ speedMps, angleDeg, gravityMS2, x0 = 0.0, y0 = 0.0 }) {
    if (!Number.isFinite(speedMps) || speedMps < 0) {
      throw new Error(`[ProjectileKernel] Invalid speed: ${speedMps}`);
    }
    if (!Number.isFinite(angleDeg)) {
      throw new Error(`[ProjectileKernel] Invalid angle: ${angleDeg}`);
    }
    if (!Number.isFinite(gravityMS2) || gravityMS2 < 0) {
      throw new Error(`[ProjectileKernel] Invalid gravity: ${gravityMS2}`);
    }

    this.speedMps = speedMps;
    this.angleDeg = angleDeg;
    this.g = gravityMS2;
    this.x0 = x0;
    this.y0 = y0;
    this.simTime = 0.0;
  }

  get vx0() {
    return this.speedMps * Math.cos((this.angleDeg * Math.PI) / 180.0);
  }

  get vy0() {
    return this.speedMps * Math.sin((this.angleDeg * Math.PI) / 180.0);
  }

  get flightTime() {
    return (2.0 * this.vy0) / this.g;
  }

  get maxHeightM() {
    return (this.vy0 * this.vy0) / (2.0 * this.g);
  }

  get rangeM() {
    return this.vx0 * this.flightTime;
  }

  step(dt) {
    this.simTime += dt;
  }

  reset() {
    this.simTime = 0.0;
  }

  getState(t = this.simTime) {
    const clampedT = Math.max(0, Math.min(t, this.flightTime));
    const xM = this.vx0 * clampedT;
    const yM = this.vy0 * clampedT - 0.5 * this.g * clampedT * clampedT;
    const vx = this.vx0;
    const vy = this.vy0 - this.g * clampedT;
    return {
      xM,
      yM,
      vx,
      vy,
      hasLanded: t >= this.flightTime
    };
  }
}

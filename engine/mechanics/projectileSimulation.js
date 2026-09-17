/**
 * mechanics/projectileSimulation.js
 * 
 * High-precision analytical projectile motion solver.
 * Uses exact closed-form kinematic equations:
 *   x(t) = x₀ + v₀ * cos(θ) * t
 *   y(t) = y₀ + v₀ * sin(θ) * t - 0.5 * g * t²
 * with zero numerical drift and sub-pixel trajectory rendering.
 */

import { CoordinateMapper } from '../core/coordinateMapper.js';

export class ProjectileSimulation {
  /**
   * @param {HTMLElement} container
   * @param {object} scene
   */
  constructor(container, scene) {
    this.container = container;
    this.scene = scene;

    const ballObj = scene.objects?.find(o => o.type === 'projectile' || o.type === 'circle') || scene.objects?.[0];
    this.object = ballObj;

    // Physical calibration
    this.ppm = Number(scene.calibration?.pixels_per_meter) || 50.0;
    this.g = Number(scene.environment?.gravity_m_s2) || 9.81;

    // Physics parameters in SI units
    const phys = ballObj?.physics || {};
    this.speedMps = Number(phys.speed_m_s) || 15.0;
    this.angleDeg = Number(phys.launch_angle_deg) || 45.0;

    // Source launch position
    const initPos = ballObj?.geometry?.launch_source_px || ballObj?.initial_position || { x: 120, y: 450 };
    this.launchSource = { x: Number(initPos.x) || 120, y: Number(initPos.y) || 450 };
    this.ballRadiusPx = Number(ballObj?.geometry?.radius_source_px || ballObj?.radius) || 18.0;

    this.simTime = 0.0;
    this.running = false;
    this.timeScale = 1.0;
    this.lastTime = null;
    this.raf = null;

    // Calculate flight properties
    this._computeFlightParams();

    // Canvas overlay
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'projectile-overlay-canvas';
    this.canvas.style.position = 'absolute';
    this.canvas.style.inset = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.container.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');

    this.resize();
    this.resizeObserver = new ResizeObserver(() => {
      this.resize();
      this.render();
    });
    this.resizeObserver.observe(this.container);

    this.render();
  }

  _computeFlightParams() {
    const rad = (this.angleDeg * Math.PI) / 180.0;
    this.vx0 = this.speedMps * Math.cos(rad);
    this.vy0 = this.speedMps * Math.sin(rad);

    // Max height above launch point
    this.maxHeightM = (this.vy0 * this.vy0) / (2.0 * this.g);
    this.timeToApex = this.vy0 / this.g;

    // Flight time to return to launch Y
    this.flightTime = (2.0 * this.vy0) / this.g;
    this.rangeM = this.vx0 * this.flightTime;
  }

  resize() {
    const width = this.container.clientWidth || 800;
    const height = this.container.clientHeight || 600;
    const dpr = window.devicePixelRatio || 1;

    this.canvas.width = Math.round(width * dpr);
    this.canvas.height = Math.round(height * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const sourceW = this.scene.source?.image_width_px || 800;
    const sourceH = this.scene.source?.image_height_px || 600;

    this.mapper = new CoordinateMapper(sourceW, sourceH, width, height, dpr);
    this.viewWidth = width;
    this.viewHeight = height;
  }

  /**
   * Evaluates position in meters relative to launch point.
   */
  getPositionMeters(t = this.simTime) {
    const clampedT = Math.max(0, Math.min(t, this.flightTime));
    const xM = this.vx0 * clampedT;
    const yM = this.vy0 * clampedT - 0.5 * this.g * clampedT * clampedT;
    const vx = this.vx0;
    const vy = this.vy0 - this.g * clampedT;
    return { xM, yM, vx, vy, hasLanded: t >= this.flightTime };
  }

  /**
   * Converts relative meter coordinates to native source_px.
   */
  sourcePositionAt(t = this.simTime) {
    const pos = this.getPositionMeters(t);
    // Physics Y is UP (+), Image Y is DOWN (+)
    return {
      x: this.launchSource.x + pos.xM * this.ppm,
      y: this.launchSource.y - pos.yM * this.ppm,
      vx: pos.vx,
      vy: pos.vy,
      hasLanded: pos.hasLanded,
    };
  }

  tick = (now) => {
    if (!this.running) return;

    if (this.lastTime === null) {
      this.lastTime = now;
    }

    const elapsed = Math.min((now - this.lastTime) / 1000.0, 0.05);
    this.lastTime = now;

    this.simTime += elapsed * this.timeScale;

    if (this.simTime >= this.flightTime) {
      this.simTime = this.flightTime;
      this.pause();
    }

    this.render();

    if (this.running) {
      this.raf = requestAnimationFrame(this.tick);
    }
  };

  play() {
    if (this.simTime >= this.flightTime) {
      this.simTime = 0.0;
    }
    this.running = true;
    this.lastTime = null;
    this.raf = requestAnimationFrame(this.tick);
  }

  pause() {
    this.running = false;
    if (this.raf) {
      cancelAnimationFrame(this.raf);
      this.raf = null;
    }
  }

  reset() {
    this.pause();
    this.simTime = 0.0;
    this.render();
  }

  setGravity(value) {
    this.g = Number(value) || 9.81;
    this._computeFlightParams();
    this.render();
  }

  setSpeed(value) {
    this.timeScale = Number(value) || 1.0;
  }

  setLaunchSpeed(v) {
    this.speedMps = Number(v) || 15.0;
    this._computeFlightParams();
    this.render();
  }

  setLaunchAngle(deg) {
    this.angleDeg = Number(deg) || 45.0;
    this._computeFlightParams();
    this.render();
  }

  setWireframes() {}

  getTime() {
    return this.simTime;
  }

  render() {
    const ctx = this.ctx;
    const mapper = this.mapper;
    if (!ctx || !mapper) return;

    ctx.clearRect(0, 0, this.viewWidth, this.viewHeight);

    // 1. Draw Analytical Parabolic Trajectory
    ctx.save();
    ctx.beginPath();
    const steps = 80;
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * this.flightTime;
      const ptSrc = this.sourcePositionAt(t);
      const ptView = mapper.sourceToView(ptSrc);
      if (i === 0) ctx.moveTo(ptView.x, ptView.y);
      else ctx.lineTo(ptView.x, ptView.y);
    }
    ctx.setLineDash([5, 4]);
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.7)';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();

    // 2. Draw Apex Marker
    const apexSrc = this.sourcePositionAt(this.timeToApex);
    const apexView = mapper.sourceToView(apexSrc);
    ctx.save();
    ctx.beginPath();
    ctx.arc(apexView.x, apexView.y, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = '#fbbf24';
    ctx.fill();
    ctx.font = '11px Inter, sans-serif';
    ctx.fillStyle = 'rgba(251, 191, 36, 0.9)';
    ctx.fillText(`Apex: ${this.maxHeightM.toFixed(1)}m`, apexView.x + 8, apexView.y - 6);
    ctx.restore();

    // 3. Draw Projectile Ball
    const currSrc = this.sourcePositionAt(this.simTime);
    const currView = mapper.sourceToView(currSrc);
    const rView = mapper.sourceLengthToView(this.ballRadiusPx);

    ctx.save();
    ctx.shadowColor = 'rgba(56, 189, 248, 0.8)';
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(currView.x, currView.y, rView, 0, Math.PI * 2);
    ctx.fillStyle = '#38bdf8';
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();

    // Velocity Vector Arrow
    const speedRatio = 2.0;
    const vEndView = {
      x: currView.x + currSrc.vx * speedRatio,
      y: currView.y - currSrc.vy * speedRatio,
    };
    ctx.beginPath();
    ctx.moveTo(currView.x, currView.y);
    ctx.lineTo(vEndView.x, vEndView.y);
    ctx.strokeStyle = '#34d399';
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();

    // 4. Telemetry Card
    this._renderHUD(ctx);
  }

  _renderHUD(ctx) {
    ctx.save();
    const boxX = 14;
    const boxY = 14;
    const boxW = 200;
    const boxH = 108;

    ctx.fillStyle = 'rgba(15, 23, 42, 0.82)';
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.25)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(boxX, boxY, boxW, boxH, 8);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#38bdf8';
    ctx.font = '700 11px Inter, sans-serif';
    ctx.fillText('PROJECTILE MOTION (ANALYTIC)', boxX + 10, boxY + 18);

    ctx.font = '12px Inter, sans-serif';
    ctx.fillStyle = '#f1f5f9';
    ctx.fillText(`Time t: ${this.simTime.toFixed(2)} s / ${this.flightTime.toFixed(2)} s`, boxX + 10, boxY + 36);
    ctx.fillText(`Speed v₀: ${this.speedMps.toFixed(1)} m/s @ ${this.angleDeg.toFixed(0)}°`, boxX + 10, boxY + 52);
    ctx.fillText(`Max Height: ${this.maxHeightM.toFixed(2)} m`, boxX + 10, boxY + 68);
    ctx.fillText(`Total Range: ${this.rangeM.toFixed(2)} m`, boxX + 10, boxY + 84);

    ctx.fillStyle = '#34d399';
    ctx.font = '600 10px Inter, sans-serif';
    ctx.fillText(`Zero Numerical Drift (Exact)`, boxX + 10, boxY + 100);

    ctx.restore();
  }

  destroy() {
    this.pause();
    this.resizeObserver?.disconnect();
    this.canvas?.remove();
  }
}

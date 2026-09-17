/**
 * mechanics/pendulumSimulation.js
 * 
 * High-precision, sub-pixel aligned pendulum simulation engine.
 * Solves the full nonlinear differential equation:
 *   d²θ/dt² = -(g / L) * sin(θ) - γ * ω
 * using a 240 Hz fixed-step 4th-Order Runge-Kutta (RK4) integrator
 * with state interpolation for jitter-free display at any refresh rate.
 */

import { CoordinateMapper } from '../core/coordinateMapper.js';

export class PendulumSimulation {
  /**
   * @param {HTMLElement} container
   * @param {object} scene - Canonical Schema 3.0 scene
   */
  constructor(container, scene) {
    this.container = container;
    this.scene = scene;

    const pendulumObj = scene.objects?.find(o => o.type === 'pendulum') || scene.objects?.[0];
    if (!pendulumObj) {
      throw new Error('[PendulumSimulation] No pendulum object found in scene specification.');
    }

    this.object = pendulumObj;
    this.geometry = pendulumObj.geometry;
    this.physics = pendulumObj.physics || {};

    // Physics parameters in SI units
    this.g = Number(scene.environment?.gravity_m_s2) || 9.81;
    this.lengthM = Number(this.physics.length_m) || 1.0;
    this.calibrated = Boolean(this.physics.length_m && this.physics.length_m > 0);
    this.massKg = Number(this.physics.mass_kg) || 1.0; // Used for energy display
    this.damping = Number(this.physics.damping_s_inv) || 0.0;

    // Initial state: theta measured from downward vertical (rad)
    this.theta0 = Number(this.physics.theta0_rad) || 0.0;
    this.omega0 = Number(this.physics.omega0_rad_s) || 0.0;

    this.theta = this.theta0;
    this.omega = this.omega0;
    this.prevState = { theta: this.theta0, omega: this.omega0 };

    // Numerical integration parameters (240 Hz)
    this.fixedDt = 1.0 / 240.0;
    this.accumulator = 0.0;
    this.simTime = 0.0;
    this.timeScale = 1.0;
    this.lastTime = null;
    this.running = false;
    this.raf = null;
    this.dragging = false;
    this.wasRunning = false;

    // Trajectory trail
    this.trail = [];
    this.maxTrailPoints = 120;

    // Bob sprite image (if extracted)
    this.bobSprite = null;
    const spriteUrl = pendulumObj.visual?.sprite_url;
    if (spriteUrl) {
      this.bobSprite = new Image();
      this.bobSprite.src = spriteUrl;
    }

    // Mount canvas overlay
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'pendulum-overlay-canvas';
    this.canvas.style.position = 'absolute';
    this.canvas.style.inset = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.touchAction = 'none';
    this.canvas.style.pointerEvents = 'auto';
    this.container.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');

    // Resize handling with DPR & ResizeObserver
    this.resize();
    this.resizeObserver = new ResizeObserver(() => {
      this.resize();
      this.render(this.theta, this.omega);
    });
    this.resizeObserver.observe(this.container);

    // Pointer events for drag & release interaction
    this.abortController = new AbortController();
    this._bindPointerEvents();

    // Initial render
    this.render(this.theta, this.omega);
  }

  resize() {
    const width = this.container.clientWidth || 800;
    const height = this.container.clientHeight || 600;
    const dpr = window.devicePixelRatio || 1;

    this.canvas.width = Math.round(width * dpr);
    this.canvas.height = Math.round(height * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const sourceW = this.scene.source?.image_width_px || this.geometry?.bob_center?.x * 2 || 800;
    const sourceH = this.scene.source?.image_height_px || this.geometry?.bob_center?.y * 1.5 || 600;

    this.mapper = new CoordinateMapper(sourceW, sourceH, width, height, dpr);
    this.viewWidth = width;
    this.viewHeight = height;
  }

  /**
   * Evaluates angular acceleration: d²θ/dt² = -(g/L)*sin(θ) - γ*ω
   */
  derivative(theta, omega) {
    return {
      thetaDot: omega,
      omegaDot: -(this.g / this.lengthM) * Math.sin(theta) - this.damping * omega,
    };
  }

  /**
   * 4th-Order Runge-Kutta step
   */
  integrateRK4(dt) {
    const t0 = this.theta;
    const w0 = this.omega;

    const k1 = this.derivative(t0, w0);
    const k2 = this.derivative(t0 + 0.5 * dt * k1.thetaDot, w0 + 0.5 * dt * k1.omegaDot);
    const k3 = this.derivative(t0 + 0.5 * dt * k2.thetaDot, w0 + 0.5 * dt * k2.omegaDot);
    const k4 = this.derivative(t0 + dt * k3.thetaDot, w0 + dt * k3.omegaDot);

    this.theta += (dt / 6.0) * (k1.thetaDot + 2.0 * k2.thetaDot + 2.0 * k3.thetaDot + k4.thetaDot);
    this.omega += (dt / 6.0) * (k1.omegaDot + 2.0 * k2.omegaDot + 2.0 * k3.omegaDot + k4.omegaDot);
  }

  /**
   * Computes bob center in native source_px for a given angle theta.
   */
  getBobSourcePosition(theta = this.theta) {
    const pivot = this.geometry.pivot;
    const L = this.geometry.string_length_px;
    // Source image: Y increases downwards. theta=0 is downwards.
    return {
      x: pivot.x + L * Math.sin(theta),
      y: pivot.y + L * Math.cos(theta),
    };
  }

  /**
   * Animation loop with fixed-step accumulator and render interpolation.
   */
  tick = (now) => {
    if (!this.running) return;

    if (this.lastTime === null) {
      this.lastTime = now;
    }

    let elapsed = (now - this.lastTime) / 1000.0;
    this.lastTime = now;

    // Prevent large spiral after background tab suspension
    elapsed = Math.min(elapsed, 0.05);
    this.accumulator += elapsed * this.timeScale;

    while (this.accumulator >= this.fixedDt) {
      this.prevState = { theta: this.theta, omega: this.omega };
      this.integrateRK4(this.fixedDt);
      this.simTime += this.fixedDt;
      this.accumulator -= this.fixedDt;
    }

    // Hermite / linear interpolation between previous and current state
    const alpha = Math.max(0.0, Math.min(1.0, this.accumulator / this.fixedDt));
    const interpTheta = this.prevState.theta + alpha * (this.theta - this.prevState.theta);
    const interpOmega = this.prevState.omega + alpha * (this.omega - this.prevState.omega);

    // Record trail
    const bobSrc = this.getBobSourcePosition(interpTheta);
    this.trail.push(bobSrc);
    if (this.trail.length > this.maxTrailPoints) {
      this.trail.shift();
    }

    this.render(interpTheta, interpOmega);
    this.raf = requestAnimationFrame(this.tick);
  };

  play() {
    if (this.running) return;
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
    this.theta = this.theta0;
    this.omega = this.omega0;
    this.prevState = { theta: this.theta0, omega: this.omega0 };
    this.simTime = 0.0;
    this.accumulator = 0.0;
    this.trail = [];
    this.render(this.theta, this.omega);
  }

  setGravity(value) {
    const val = Number(value);
    if (Number.isFinite(val) && val >= 0) {
      this.g = val;
    }
  }

  setSpeed(value) {
    const val = Number(value);
    if (Number.isFinite(val) && val > 0) {
      this.timeScale = val;
    }
  }

  setLengthMeters(value) {
    const L = Number(value);
    if (Number.isFinite(L) && L > 0) {
      this.lengthM = L;
      this.calibrated = true;
    }
  }

  setWireframes() {}

  getTime() {
    return this.simTime;
  }

  render(renderTheta = this.theta, renderOmega = this.omega) {
    const ctx = this.ctx;
    const mapper = this.mapper;
    if (!ctx || !mapper) return;

    ctx.clearRect(0, 0, this.viewWidth, this.viewHeight);

    const pivotSrc = this.geometry.pivot;
    const bobSrc = this.getBobSourcePosition(renderTheta);

    const pivotView = mapper.sourceToView(pivotSrc);
    const bobView = mapper.sourceToView(bobSrc);
    const radiusView = mapper.sourceLengthToView(this.geometry.bob_radius_px);
    const stringLenView = mapper.sourceLengthToView(this.geometry.string_length_px);

    // 1. Draw equilibrium reference line (downward vertical dashed)
    ctx.save();
    ctx.beginPath();
    ctx.setLineDash([4, 4]);
    ctx.moveTo(pivotView.x, pivotView.y);
    ctx.lineTo(pivotView.x, pivotView.y + stringLenView);
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.45)';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.restore();

    // 2. Trajectory trail (arc)
    if (this.trail.length > 1) {
      ctx.save();
      ctx.beginPath();
      for (let i = 0; i < this.trail.length; i++) {
        const ptView = mapper.sourceToView(this.trail[i]);
        if (i === 0) ctx.moveTo(ptView.x, ptView.y);
        else ctx.lineTo(ptView.x, ptView.y);
      }
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
      ctx.lineWidth = 2.0;
      ctx.stroke();
      ctx.restore();
    }

    // 3. Pendulum String (high-contrast anti-aliased with subtle glow)
    ctx.save();
    ctx.shadowColor = 'rgba(56, 189, 248, 0.6)';
    ctx.shadowBlur = 6;
    ctx.beginPath();
    ctx.moveTo(pivotView.x, pivotView.y);
    ctx.lineTo(bobView.x, bobView.y);
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();

    // 4. Pivot Pin
    ctx.save();
    ctx.beginPath();
    ctx.arc(pivotView.x, pivotView.y, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#fbbf24';
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();
    ctx.restore();

    // 5. Bob (Sprite or styled glowing sphere)
    ctx.save();
    if (this.bobSprite && this.bobSprite.complete && this.bobSprite.naturalWidth > 0) {
      const spriteW = radiusView * 2.2;
      const spriteH = radiusView * 2.2;
      ctx.drawImage(
        this.bobSprite,
        bobView.x - spriteW / 2.0,
        bobView.y - spriteH / 2.0,
        spriteW,
        spriteH
      );
      // Ring outline for augmented clarity
      ctx.beginPath();
      ctx.arc(bobView.x, bobView.y, radiusView, 0, Math.PI * 2);
      ctx.lineWidth = 2;
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
      ctx.stroke();
    } else {
      ctx.shadowColor = 'rgba(56, 189, 248, 0.8)';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.arc(bobView.x, bobView.y, radiusView, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(56, 189, 248, 0.85)';
      ctx.fill();
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();
    }
    ctx.restore();

    // 6. Educational Telemetry HUD
    this._renderHUD(ctx, pivotView, bobView, renderTheta, renderOmega);
  }

  _renderHUD(ctx, pivotView, bobView, theta, omega) {
    ctx.save();
    const thetaDeg = (theta * 180.0) / Math.PI;
    const speedMps = Math.abs(omega * this.lengthM);
    const heightM = this.lengthM * (1.0 - Math.cos(theta));
    const pe = this.massKg * this.g * heightM;
    const ke = 0.5 * this.massKg * speedMps * speedMps;
    const totalE = pe + ke;

    // Small angle indicator near pivot
    ctx.font = '600 12px Inter, sans-serif';
    ctx.fillStyle = '#f8fafc';
    ctx.fillText(`θ = ${thetaDeg.toFixed(1)}°`, pivotView.x + 14, pivotView.y + 18);

    // Top-left telemetry card
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
    ctx.fillText('NONLINEAR PENDULUM (RK4)', boxX + 10, boxY + 18);

    ctx.font = '12px Inter, sans-serif';
    ctx.fillStyle = '#f1f5f9';
    ctx.fillText(`Time t: ${this.simTime.toFixed(2)} s`, boxX + 10, boxY + 36);
    ctx.fillText(`Angle θ: ${thetaDeg.toFixed(2)}°`, boxX + 10, boxY + 52);
    ctx.fillText(`Speed v: ${speedMps.toFixed(2)} m/s`, boxX + 10, boxY + 68);
    ctx.fillText(`Total E: ${totalE.toFixed(2)} J`, boxX + 10, boxY + 84);

    if (this.calibrated) {
      ctx.fillStyle = '#34d399';
      ctx.font = '600 11px Inter, sans-serif';
      ctx.fillText(`✓ Calibrated (L = ${this.lengthM.toFixed(2)} m)`, boxX + 10, boxY + 100);
    } else {
      ctx.fillStyle = '#fbbf24';
      ctx.font = '600 10px Inter, sans-serif';
      ctx.fillText('⚠ L unresolved (using 1.0 m)', boxX + 10, boxY + 100);
    }

    ctx.restore();
  }

  _bindPointerEvents() {
    const signal = this.abortController.signal;

    this.canvas.addEventListener(
      'pointerdown',
      (e) => {
        const rect = this.canvas.getBoundingClientRect();
        const ptView = { x: e.clientX - rect.left, y: e.clientY - rect.top };
        const bobView = this.mapper.sourceToView(this.getBobSourcePosition());
        const rView = this.mapper.sourceLengthToView(this.geometry.bob_radius_px);

        const dist = Math.hypot(ptView.x - bobView.x, ptView.y - bobView.y);
        if (dist <= rView + 18) {
          this.dragging = true;
          this.wasRunning = this.running;
          this.pause();
          try {
            this.canvas.setPointerCapture(e.pointerId);
          } catch (_) {}
        }
      },
      { signal }
    );

    this.canvas.addEventListener(
      'pointermove',
      (e) => {
        if (!this.dragging) return;
        const rect = this.canvas.getBoundingClientRect();
        const ptView = { x: e.clientX - rect.left, y: e.clientY - rect.top };
        const ptSrc = this.mapper.viewToSource(ptView);
        const pivot = this.geometry.pivot;

        // Angle from downward vertical: Y increases downward
        const dx = ptSrc.x - pivot.x;
        const dy = ptSrc.y - pivot.y;
        this.theta = Math.atan2(dx, dy);
        this.omega = 0.0;
        this.prevState = { theta: this.theta, omega: 0.0 };
        this.render(this.theta, 0.0);
      },
      { signal }
    );

    const onRelease = (e) => {
      if (!this.dragging) return;
      this.dragging = false;
      try {
        this.canvas.releasePointerCapture(e.pointerId);
      } catch (_) {}
      if (this.wasRunning) {
        this.play();
      }
    };

    this.canvas.addEventListener('pointerup', onRelease, { signal });
    this.canvas.addEventListener('pointercancel', onRelease, { signal });
  }

  destroy() {
    this.pause();
    this.abortController?.abort();
    this.resizeObserver?.disconnect();
    this.canvas?.remove();
  }
}

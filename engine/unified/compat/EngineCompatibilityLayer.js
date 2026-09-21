/**
 * EngineCompatibilityLayer.js
 * 
 * Thin compatibility bridge exposing the exact interfaces expected by the existing frontend:
 * 1. Adapter wrappers compatible with PhysicsRuntime & SolverRegistry:
 *    - UnifiedMechanicsAdapter
 *    - UnifiedOpticsAdapter
 *    - UnifiedCircuitAdapter
 * 2. Drop-in solver functions for legacy optics and circuit controllers:
 *    - solveThinLens
 *    - solveMirror (with bidirectional facing support)
 *    - solvePrismRefraction
 *    - traceInterfaceRefraction
 * 3. UnifiedMechanicsSimulation:
 *    - Drop-in replacement for Matter.js / standalone RK4 Simulation in MechanicsController
 * 
 * All calls are internally executed by UnifiedEngineCore and the unified domain adapters.
 */

import { UnifiedEngineCore } from '../core/UnifiedEngineCore.js';
import { MechanicsAdapter } from '../adapters/MechanicsAdapter.js';
import { OpticsAdapter } from '../adapters/OpticsAdapter.js';
import { CircuitsAdapter } from '../adapters/CircuitsAdapter.js';

// Base adapter class mirroring SimulationAdapter contract
export class BaseSimulationAdapter {
  constructor() {
    this.scene = null;
    this.container = null;
    this.running = false;
    this._listeners = new Set();
    this._parameterOverrides = new Map();
  }

  canHandle(scene) { return false; }

  async initialize(scene, container, options = {}) {
    this.scene = scene;
    this.container = container;
    this.running = false;
    this._parameterOverrides.clear();
  }

  play() { this.running = true; }
  pause() { this.running = false; }
  reset() { this.running = false; }

  setParameter(name, value) {
    if (this.scene?.parameters?.[name]) {
      this.scene.parameters[name].value = value;
      this.scene.parameters[name].provenance = 'student';
    }
  }

  getParameter(name) {
    if (this.scene?.parameters?.[name]) {
      return { ...this.scene.parameters[name] };
    }
    return null;
  }

  getParameters() {
    return this.scene?.parameters || {};
  }

  getState() {
    return { running: this.running, timestamp: performance.now() };
  }

  resize(width, height, renderContext = null) {}

  destroy() {
    this.pause();
    this._listeners.clear();
    this._parameterOverrides.clear();
    this.scene = null;
    this.container = null;
  }

  onStateChange(listener) {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  notifyStateChange(state) {
    for (const listener of this._listeners) {
      try { listener(state); } catch (err) { console.error('[Adapter] Listener error:', err); }
    }
  }
}

// =============================================================================
// 1. UNIFIED MECHANICS ADAPTER (Runtime & Canvas Rendering)
// =============================================================================

export class UnifiedMechanicsAdapter extends BaseSimulationAdapter {
  constructor() {
    super();
    this.core = new UnifiedEngineCore();
    this.adapter = new MechanicsAdapter();
    this.core.setAdapter(this.adapter);
    this.canvas = null;
    this.ctx = null;
    this.raf = null;
    this.lastTime = null;
    this.fixedDt = 1.0 / 240.0;
    this.accumulator = 0.0;
  }

  static canHandle(scene) {
    const domain = scene?.domain || scene?.simulation?.domain || scene?.simulation_type;
    return domain === 'mechanics' || domain === 'kinematics';
  }

  canHandle(scene) {
    return UnifiedMechanicsAdapter.canHandle(scene);
  }

  async initialize(scene, container, options = {}) {
    await super.initialize(scene, container, options);
    this.core.loadScene(scene);

    if (container) {
      this._setupCanvas(container);
    }

    this.notifyStateChange(this.getState());
  }

  _setupCanvas(container) {
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'unified-mechanics-canvas';
    this.canvas.style.position = 'absolute';
    this.canvas.style.inset = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.pointerEvents = 'none';

    container.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this.resize(container.clientWidth || 800, container.clientHeight || 600);
    this._render();
  }

  play() {
    super.play();
    this.core.play();
    this.lastTime = null;
    this._tick(performance.now());
    this.notifyStateChange(this.getState());
  }

  pause() {
    super.pause();
    this.core.pause();
    if (this.raf) {
      cancelAnimationFrame(this.raf);
      this.raf = null;
    }
    this.notifyStateChange(this.getState());
  }

  reset() {
    super.reset();
    this.core.reset();
    this.accumulator = 0.0;
    this._render();
    this.notifyStateChange(this.getState());
  }

  setParameter(name, value) {
    super.setParameter(name, value);
    this.core.setParameter(name, value);
    this._render();
    this.notifyStateChange(this.getState());
  }

  getState() {
    const coreState = this.core.getState();
    return {
      domain: 'mechanics',
      running: this.running,
      ...coreState
    };
  }

  resize(width, height, renderContext = null) {
    if (!this.canvas) return;
    const dpr = typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1;
    this.canvas.width = Math.round(width * dpr);
    this.canvas.height = Math.round(height * dpr);
    if (this.ctx) {
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    this._render();
  }

  _tick = (now) => {
    if (!this.running) return;

    if (this.lastTime === null) this.lastTime = now;
    let elapsed = (now - this.lastTime) / 1000.0;
    this.lastTime = now;
    elapsed = Math.min(elapsed, 0.05);
    this.accumulator += elapsed;

    while (this.accumulator >= this.fixedDt) {
      this.core.step(this.fixedDt);
      this.accumulator -= this.fixedDt;
    }

    this._render();
    this.notifyStateChange(this.getState());
    this.raf = requestAnimationFrame(this._tick);
  };

  _render() {
    const ctx = this.ctx;
    if (!ctx || !this.canvas) return;

    const w = this.canvas.width;
    const h = this.canvas.height;
    ctx.clearRect(0, 0, w, h);

    const state = this.core.getState();
    if (state.type === 'pendulum' && state.bobs) {
      state.bobs.forEach((bob, i) => {
        // String
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(bob.pivot.x, bob.pivot.y);
        ctx.lineTo(bob.x, bob.y);
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Pivot
        ctx.beginPath();
        ctx.arc(bob.pivot.x, bob.pivot.y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#fbbf24';
        ctx.fill();

        // Bob
        ctx.beginPath();
        ctx.arc(bob.x, bob.y, bob.radiusPx || 24, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(56, 189, 248, 0.85)';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();
        ctx.restore();
      });
    } else if (state.type === 'projectile' && state.particles) {
      state.particles.forEach(p => {
        ctx.save();
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radiusPx || 12, 0, Math.PI * 2);
        ctx.fillStyle = '#f43f5e';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();
        ctx.restore();
      });
    } else if (state.type === 'spring_mass' && state.masses) {
      state.masses.forEach(m => {
        ctx.save();
        if (m.anchor) {
          ctx.beginPath();
          ctx.moveTo(m.anchor.x, m.anchor.y);
          ctx.lineTo(m.x, m.y);
          ctx.strokeStyle = '#94a3b8';
          ctx.lineWidth = 3;
          ctx.stroke();
        }
        const mw = m.widthPx || 40;
        const mh = m.heightPx || 30;
        ctx.fillStyle = '#10b981';
        ctx.fillRect(m.x - mw / 2, m.y - mh / 2, mw, mh);
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#ffffff';
        ctx.strokeRect(m.x - mw / 2, m.y - mh / 2, mw, mh);
        ctx.restore();
      });
    }
  }

  destroy() {
    this.pause();
    if (this.canvas && this.canvas.parentElement) {
      this.canvas.parentElement.removeChild(this.canvas);
    }
    this.canvas = null;
    this.ctx = null;
    super.destroy();
  }
}

// =============================================================================
// 2. UNIFIED OPTICS ADAPTER (Runtime)
// =============================================================================

export class UnifiedOpticsAdapter extends BaseSimulationAdapter {
  constructor() {
    super();
    this.core = new UnifiedEngineCore();
    this.adapter = new OpticsAdapter();
    this.core.setAdapter(this.adapter);
  }

  static canHandle(scene) {
    const domain = scene?.domain || scene?.simulation?.domain || scene?.simulation_type;
    return domain === 'optics';
  }

  canHandle(scene) {
    return UnifiedOpticsAdapter.canHandle(scene);
  }

  async initialize(scene, container, options = {}) {
    await super.initialize(scene, container, options);
    this.core.loadScene(scene);
    this.notifyStateChange(this.getState());
  }

  setParameter(name, value) {
    super.setParameter(name, value);
    this.core.setParameter(name, value);
    this.notifyStateChange(this.getState());
  }

  getState() {
    return {
      domain: 'optics',
      running: this.running,
      ...this.core.getState()
    };
  }
}

// =============================================================================
// 3. UNIFIED CIRCUITS ADAPTER (Runtime)
// =============================================================================

export class UnifiedCircuitsAdapter extends BaseSimulationAdapter {
  constructor() {
    super();
    this.core = new UnifiedEngineCore();
    this.adapter = new CircuitsAdapter();
    this.core.setAdapter(this.adapter);
  }

  static canHandle(scene) {
    const domain = scene?.domain || scene?.simulation?.domain || scene?.simulation_type;
    return domain === 'circuits';
  }

  canHandle(scene) {
    return UnifiedCircuitsAdapter.canHandle(scene);
  }

  async initialize(scene, container, options = {}) {
    await super.initialize(scene, container, options);
    this.core.loadScene(scene);
    this.notifyStateChange(this.getState());
  }

  setParameter(name, value) {
    super.setParameter(name, value);
    this.core.setParameter(name, value);
    this.notifyStateChange(this.getState());
  }

  getState() {
    return {
      domain: 'circuits',
      running: this.running,
      ...this.core.getState()
    };
  }
}

// =============================================================================
// 4. DROP-IN PROCEDURAL SOLVER FUNCTIONS
// =============================================================================

export function solveThinLens({
  lensX = 400,
  axisY = 300,
  objectX = 160,
  objectHeight = -80,
  focalLength = 120,
  bounds = {}
}) {
  const core = new UnifiedEngineCore();
  const adapter = new OpticsAdapter();
  core.setAdapter(adapter);

  const scene = {
    type: 'thin_lens',
    source: { width: bounds.maxX || 800, height: bounds.maxY || 600 },
    geometry: { optical_axis_y: axisY },
    elements: [
      {
        semantic_label: 'lens',
        optics: { focal_length_px: focalLength, model: focalLength < 0 ? 'concave' : 'convex' },
        geometry: { optical_center: { x: lensX, y: axisY } }
      },
      {
        semantic_label: 'object',
        geometry: { position: { x: objectX, y: axisY }, height_px: objectHeight }
      }
    ]
  };

  core.loadScene(scene);
  return adapter.extractState(core).solution;
}

export function solveMirror({
  mirrorType = 'concave',
  mirrorX = 600,
  axisY = 300,
  objectX = 260,
  objectHeight = -85,
  focalLength = 140,
  facing,
  bounds = {}
}) {
  const core = new UnifiedEngineCore();
  const adapter = new OpticsAdapter();
  core.setAdapter(adapter);

  const determinedFacing = facing !== undefined ? facing : (objectX > mirrorX ? 'right' : 'left');

  const scene = {
    type: 'mirror',
    source: { width: bounds.maxX || 800, height: bounds.maxY || 600 },
    geometry: { optical_axis_y: axisY },
    elements: [
      {
        semantic_label: 'mirror',
        optics: { focal_length_px: focalLength, model: mirrorType, facing: determinedFacing },
        geometry: { optical_center: { x: mirrorX, y: axisY } }
      },
      {
        semantic_label: 'object',
        geometry: { position: { x: objectX, y: axisY }, height_px: objectHeight }
      }
    ]
  };

  core.loadScene(scene);
  return adapter.extractState(core).solution;
}

export function solvePrismRefraction({
  prismVertices,
  refractiveIndex = 1.52,
  rayOrigin,
  rayDirection,
  bounds = {}
}) {
  const core = new UnifiedEngineCore();
  const adapter = new OpticsAdapter();
  core.setAdapter(adapter);

  const scene = {
    type: 'prism',
    source: { width: bounds.maxX || 800, height: bounds.maxY || 600 },
    elements: [
      {
        semantic_label: 'prism',
        optics: { refractive_index: refractiveIndex },
        geometry: { vertices: prismVertices }
      },
      {
        semantic_label: 'source',
        geometry: {
          position: rayOrigin,
          target: { x: rayOrigin.x + rayDirection.x, y: rayOrigin.y + rayDirection.y }
        }
      }
    ]
  };

  core.loadScene(scene);
  return adapter.extractState(core).solution;
}

export function traceInterfaceRefraction(config = {}) {
  const boundaryY = config.boundaryY ?? 300;
  const normalX = config.normalX ?? 400;
  const n1 = config.n1 ?? 1.0;
  const n2 = config.n2 ?? 1.5;
  const source = config.source ?? { x: normalX - 180, y: boundaryY - 180 };
  const targetPoint = config.targetPoint ?? config.pointOfIncidence ?? { x: normalX, y: boundaryY };
  const bounds = config.bounds ?? {};

  const core = new UnifiedEngineCore();
  const adapter = new OpticsAdapter();
  core.setAdapter(adapter);

  const scene = {
    type: 'interface_refraction',
    source: { width: bounds.maxX || 800, height: bounds.maxY || 600 },
    geometry: { boundary_y: boundaryY, normal_x: normalX, source, targetPoint },
    parameters: { n1: { value: n1 }, n2: { value: n2 } }
  };

  core.loadScene(scene);
  return adapter.extractState(core).solution;
}

export function solveSnellInterface(n1, n2, theta1Deg) {
  // Physical Law: Snell's Law n1 * sin(theta1) = n2 * sin(theta2)
  // Critical Angle: theta_c = asin(n2 / n1) when n1 > n2
  const theta1Rad = (theta1Deg * Math.PI) / 180.0;
  const sinTheta1 = Math.sin(theta1Rad);
  let thetaCritDeg = null;
  let isTIR = false;
  let theta2Rad = null;
  let theta2Deg = null;

  if (n1 > n2) {
    const critRad = Math.asin(n2 / n1);
    thetaCritDeg = (critRad * 180.0) / Math.PI;
    if (theta1Deg > thetaCritDeg) {
      isTIR = true;
    }
  }

  if (!isTIR) {
    const sinTheta2 = (n1 / n2) * sinTheta1;
    if (Math.abs(sinTheta2) <= 1.0) {
      theta2Rad = Math.asin(sinTheta2);
      theta2Deg = (theta2Rad * 180.0) / Math.PI;
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
    theta2Rad
  };
}

// =============================================================================
// 5. UNIFIED MECHANICS SIMULATION (Drop-in for Legacy MechanicsController)
// =============================================================================

export class UnifiedMechanicsSimulation {
  constructor(container) {
    this.container = container;
    this.adapter = new UnifiedMechanicsAdapter();
    this.scene = null;
  }

  loadScene(scene, mapper = null) {
    this.scene = scene;
    this.adapter.initialize(scene, this.container, { mapper });
  }

  play() { this.adapter.play(); }
  pause() { this.adapter.pause(); }
  reset() { this.adapter.reset(); }
  setGravity(g) { this.adapter.setParameter('gravity', g); }
  setSpeed(s) { /* handled via dt scaling if needed */ }
  setObjectVelocity(id, v) { this.adapter.setParameter('initialAngle', v); }
  setWireframes(w) {}
  destroy() { this.adapter.destroy(); }
}

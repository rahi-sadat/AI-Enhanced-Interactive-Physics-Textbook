/**
 * UnifiedEngineCore.js
 * 
 * Shared, domain-agnostic physics simulation core.
 * Coordinates flat state vectors, Newton-Raphson iteration for algebraic constraints,
 * semi-implicit Euler integration for dynamics, and event/boundary intersection handling.
 * 
 * Domain-specific laws exist purely as residual functions F(x) = 0 and force functions
 * provided by thin adapters; this core contains all solving logic.
 */

import { LinearSolver } from './LinearSolver.js';
import { NewtonRaphson } from './NewtonRaphson.js';
import { Integrator } from './Integrator.js';
import { EventEngine } from './EventEngine.js';

export class UnifiedEngineCore {
  constructor() {
    this.adapter = null;
    this.scene = null;

    // Flat numerical state vector
    this.q = new Float64Array(0);       // Generalized positions / coordinates
    this.v = new Float64Array(0);       // Generalized velocities
    this.invMass = new Float64Array(0); // Inverse masses (1/m or 1/I)
    this.z = new Float64Array(0);       // Algebraic variables (e.g. node voltages, currents)

    this.time = 0.0;
    this.running = false;
    this.isAlgebraic = false;

    // Engine settings
    this.solverTol = 1e-10;
    this.maxNewtonIterations = 50;
  }

  /**
   * Attaches a domain adapter to this engine core.
   * @param {object} adapter - Instance of a domain adapter
   */
  setAdapter(adapter) {
    this.adapter = adapter;
    this.adapter.attachCore(this);
  }

  /**
   * Compiles and loads a scene graph specification.
   * @param {object} scene
   */
  loadScene(scene) {
    this.scene = scene;
    this.time = 0.0;
    this.running = false;

    if (!this.adapter) {
      throw new Error('[UnifiedEngineCore] Cannot load scene without an active domain adapter.');
    }

    const compiled = this.adapter.compileScene(scene);
    this.isAlgebraic = Boolean(compiled.isAlgebraic);

    if (this.isAlgebraic) {
      this.z = new Float64Array(compiled.algebraicState || []);
      this.solveAlgebraic();
    } else {
      this.q = new Float64Array(compiled.q || []);
      this.v = new Float64Array(compiled.v || []);
      this.invMass = new Float64Array(compiled.invMass || new Array(this.q.length).fill(1.0));
    }
  }

  /**
   * Advances the simulation by timestep dt seconds.
   * For dynamics: semi-implicit Euler integration + event handling.
   * For algebraic systems: single Newton-Raphson equilibrium solve.
   * 
   * @param {number} dt - Timestep in seconds
   * @returns {object} Updated state snapshot
   */
  step(dt) {
    if (!this.adapter) return this.getState();

    if (this.isAlgebraic) {
      this.solveAlgebraic();
      this.time += dt;
      return this.getState();
    }

    // 1. Evaluate forces from adapter
    const forceFn = (q, v) => this.adapter.evaluateForces(q, v, this.time);

    // 2. Optional holonomic constraint projection
    const constraintProjectionFn = this.adapter.hasConstraints?.()
      ? (q, v) => this.adapter.projectConstraints(q, v)
      : null;

    // 3. Symplectic Semi-Implicit Euler Step
    const nextState = Integrator.stepSemiImplicit({
      q: this.q,
      v: this.v,
      invMass: this.invMass,
      forceFn,
      dt,
      constraintProjectionFn
    });

    this.q = nextState.q;
    this.v = nextState.v;

    // 4. Check & dispatch discrete boundary events (e.g. collisions)
    if (this.adapter.checkEvents) {
      this.adapter.checkEvents(this.q, this.v, dt);
    }

    this.time += dt;
    return this.getState();
  }

  /**
   * Performs an instant algebraic equilibrium solve using Newton-Raphson iteration.
   * Used directly for DC resistor networks (MNA) and static ray tracing paths.
   * 
   * @returns {{ converged: boolean, residualNorm: number }}
   */
  solveAlgebraic() {
    if (!this.adapter || !this.adapter.evaluateResiduals) {
      return { converged: true, residualNorm: 0.0 };
    }

    const residualFn = (z) => this.adapter.evaluateResiduals(z);
    const jacobianFn = this.adapter.evaluateJacobian
      ? (z) => this.adapter.evaluateJacobian(z)
      : null;

    const result = NewtonRaphson.solve({
      initialGuess: this.z,
      residualFn,
      jacobianFn,
      tol: this.solverTol,
      maxIterations: this.maxNewtonIterations
    });

    this.z = result.x;
    return result;
  }

  /**
   * Sets a physical parameter dynamically.
   * @param {string} name
   * @param {*} value
   */
  setParameter(name, value) {
    if (this.adapter?.setParameter) {
      this.adapter.setParameter(name, value);
    }
    if (this.isAlgebraic) {
      this.solveAlgebraic();
    }
  }

  /**
   * Returns current physics state snapshot.
   * @returns {object}
   */
  getState() {
    const base = {
      time: this.time,
      running: this.running,
      isAlgebraic: this.isAlgebraic,
      q: Array.from(this.q),
      v: Array.from(this.v),
      z: Array.from(this.z)
    };

    if (this.adapter?.extractState) {
      return { ...base, ...this.adapter.extractState(this) };
    }

    return base;
  }

  play() { this.running = true; }
  pause() { this.running = false; }
  reset() {
    this.pause();
    if (this.scene) this.loadScene(this.scene);
  }
}

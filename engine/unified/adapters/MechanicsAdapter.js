/**
 * MechanicsAdapter.js
 * 
 * Domain adapter for classical mechanics compiling diagram scenes into the UnifiedEngineCore.
 * Supports:
 *   1. Nonlinear simple pendulum & multi-bob Newton's cradle
 *   2. 2D projectile kinematics
 *   3. Spring-mass oscillator & inclined plane with Coulomb friction
 * 
 * Invariant Rules:
 *   - Zero solving logic: delegates integration & residual solves to UnifiedEngineCore.
 *   - No imports of other domain adapters — only shared core primitives.
 *   - Coordinates & lengths are strictly in native source pixels (source_px).
 *   - Physical laws are explicitly commented on every force/residual function.
 */

import { EventEngine } from '../core/EventEngine.js';

export class MechanicsAdapter {
  constructor() {
    this.core = null;
    this.subtype = 'pendulum'; // 'pendulum' | 'projectile' | 'spring_mass' | 'inclined_plane'
    this.scene = null;

    // Environment
    this.gravity = 9.81; // m/s^2
    this.pixelsPerMeter = 100.0; // Calibration scale (source_px / m)

    // Pendulum state specifications
    this.bobs = []; // Array of { pivot: {x,y}, lengthPx: number, lengthM: number, mass: number, radiusPx: number, damping: number }

    // Projectile state specifications
    this.projectile = null; // { x0, y0, vx0, vy0, mass, dragCoeff }

    // Spring-mass specifications
    this.springSystem = null; // { k, restLengthPx, mass, frictionCoeff, inclineAngleRad }
  }

  attachCore(core) {
    this.core = core;
  }

  /**
   * Compiles canonical scene JSON into generalized state vectors for UnifiedEngineCore.
   * @param {object} scene - Canonical PhysicsScene or compatible scene object
   * @returns {{ isAlgebraic: boolean, q: number[], v: number[], invMass: number[] }}
   */
  compileScene(scene) {
    this.scene = scene;

    // 1. Resolve environment parameters
    this.gravity = Number(scene.environment?.gravity_m_s2 ?? scene.parameters?.gravity?.value ?? 9.81);
    this.pixelsPerMeter = Number(scene.coordinateSystem?.pixelsPerUnit ?? scene.coordinate_system?.calibration?.pixels_per_meter?.value ?? 100.0);

    // 2. Identify subtype
    const objects = scene.objects || scene.elements || [];
    const isCradle = objects.some(o => o.id?.includes('cradle') || o.semantic_label?.includes('cradle'));
    const hasPendulum = objects.some(o => o.type === 'pendulum' || o.semantic_label?.includes('pendulum'));
    const hasProjectile = objects.some(o => o.type === 'projectile' || o.semantic_label?.includes('projectile'));
    const hasSpring = objects.some(o => o.type === 'spring' || o.id?.includes('spring'));

    if (hasPendulum || isCradle || scene.type === 'pendulum') {
      this.subtype = 'pendulum';
      return this._compilePendulum(scene, objects);
    } else if (hasProjectile || scene.type === 'projectile') {
      this.subtype = 'projectile';
      return this._compileProjectile(scene, objects);
    } else if (hasSpring || scene.type === 'spring_mass' || scene.type === 'incline') {
      this.subtype = 'spring_mass';
      return this._compileSpringMass(scene, objects);
    }

    // Default fallback: pendulum
    this.subtype = 'pendulum';
    return this._compilePendulum(scene, objects);
  }

  _compilePendulum(scene, objects) {
    const pendulumObjs = objects.filter(o => o.type === 'pendulum' || o.id?.includes('pendulum') || o.id?.includes('bob'));

    this.bobs = [];
    const qList = [];
    const vList = [];
    const invMassList = [];

    // Global scene geometry fallbacks
    const srcW = scene.coordinateSystem?.width || scene.source?.width || 800;
    const srcH = scene.coordinateSystem?.height || scene.source?.height || 600;

    const defaultPivot = scene.geometry?.pivot || { x: srcW * 0.5, y: srcH * 0.15 };
    const defaultLengthPx = Number(scene.geometry?.string_length_px || scene.geometry?.length_px || 250.0);
    const defaultLengthM = Number(scene.parameters?.length?.value ?? (defaultLengthPx / this.pixelsPerMeter));
    const defaultRadiusPx = Number(scene.geometry?.bob_radius_px || 24.0);
    const defaultMass = Number(scene.parameters?.mass?.value ?? 1.0);
    const defaultDamping = Number(scene.parameters?.damping?.value ?? 0.0);

    // Initial angle calculation
    let initialAngleRad = 0.0;
    if (scene.geometry?.bob_center && scene.geometry?.pivot) {
      // Physical Law: theta0 = arctan((x_bob - x_pivot) / (y_bob - y_pivot))
      const dx = scene.geometry.bob_center.x - scene.geometry.pivot.x;
      const dy = scene.geometry.bob_center.y - scene.geometry.pivot.y;
      initialAngleRad = Math.atan2(dx, dy);
    } else if (scene.parameters?.initialAngle?.value !== undefined) {
      initialAngleRad = (Number(scene.parameters.initialAngle.value) * Math.PI) / 180.0;
    } else {
      initialAngleRad = -0.47746; // -27.35 deg standard NCTB test1.jpg default
    }

    if (pendulumObjs.length === 0) {
      // Single synthesized pendulum
      this.bobs.push({
        id: 'pendulum_bob_1',
        pivot: { ...defaultPivot },
        lengthPx: defaultLengthPx,
        lengthM: defaultLengthM > 0 ? defaultLengthM : defaultLengthPx / this.pixelsPerMeter,
        radiusPx: defaultRadiusPx,
        mass: defaultMass,
        damping: defaultDamping
      });
      qList.push(initialAngleRad);
      vList.push(0.0);
      // Generalized inverse inertia: 1 / (m * L^2)
      const inertia = defaultMass * Math.pow(this.bobs[0].lengthM, 2);
      invMassList.push(1.0 / inertia);
    } else {
      pendulumObjs.forEach((obj, idx) => {
        const pivot = obj.geometry?.pivot || obj.pivot || defaultPivot;
        const lengthPx = Number(obj.geometry?.string_length_px || obj.geometry?.length_px || obj.length || defaultLengthPx);
        const lengthM = Number(obj.physics?.length_m || (obj.length ? obj.length / this.pixelsPerMeter : defaultLengthPx / this.pixelsPerMeter));
        const radiusPx = Number(obj.geometry?.bob_radius_px || obj.geometry?.radius || obj.radius || defaultRadiusPx);
        const mass = Number(obj.physics?.mass_kg || obj.mass_kg || defaultMass);
        const damping = Number(obj.physics?.damping_s_inv || obj.damping || defaultDamping);

        let theta0 = 0.0;
        if (obj.bob_position && pivot) {
          const dx = obj.bob_position.x - pivot.x;
          const dy = obj.bob_position.y - pivot.y;
          theta0 = Math.atan2(dx, dy);
        } else if (obj.physics?.theta0_rad !== undefined) {
          theta0 = Number(obj.physics.theta0_rad);
        } else if (idx === 0) {
          theta0 = initialAngleRad;
        }

        const omega0 = Number(obj.physics?.omega0_rad_s || 0.0);

        this.bobs.push({
          id: obj.id || `bob_${idx + 1}`,
          pivot: { ...pivot },
          lengthPx,
          lengthM: lengthM > 0 ? lengthM : lengthPx / this.pixelsPerMeter,
          radiusPx,
          mass,
          damping
        });

        qList.push(theta0);
        vList.push(omega0);
        const inertia = mass * Math.pow(lengthM, 2);
        invMassList.push(1.0 / inertia);
      });
    }

    return {
      isAlgebraic: false,
      q: qList,
      v: vList,
      invMass: invMassList
    };
  }

  _compileProjectile(scene, objects) {
    const projObj = objects.find(o => o.type === 'projectile' || o.role === 'dynamic' || o.type === 'circle') || objects[0] || {};
    const srcW = scene.coordinateSystem?.width || scene.source?.image_width_px || scene.source?.width || 800;
    const srcH = scene.coordinateSystem?.height || scene.source?.image_height_px || scene.source?.height || 600;

    const x0 = Number(projObj.geometry?.position?.x ?? projObj.geometry?.launch_source_px?.x ?? projObj.initial_position?.x ?? 120.0);
    const y0 = Number(projObj.geometry?.position?.y ?? projObj.geometry?.launch_source_px?.y ?? projObj.initial_position?.y ?? srcH - 150.0);

    const speedMps = Number(scene.parameters?.initialVelocity?.value ?? projObj.physics?.speed_m_s ?? projObj.speed_m_s ?? 20.0);
    const angleDeg = Number(scene.parameters?.launchAngle?.value ?? projObj.physics?.launch_angle_deg ?? projObj.launch_angle_deg ?? 45.0);
    const angleRad = (angleDeg * Math.PI) / 180.0;

    // Convert SI velocity (m/s) to source pixel velocity (px/s)
    let vx0 = 0.0;
    let vy0 = 0.0;
    if (projObj.initial_velocity?.x !== undefined && projObj.initial_velocity?.y !== undefined) {
      vx0 = Number(projObj.initial_velocity.x);
      vy0 = Number(projObj.initial_velocity.y);
    } else {
      const speedPxS = speedMps * this.pixelsPerMeter;
      vx0 = speedPxS * Math.cos(angleRad);
      vy0 = -speedPxS * Math.sin(angleRad); // Negative because Y points down in screen coords
    }

    const groundY = Number(scene.geometry?.ground_y ?? projObj.ground_y ?? scene.environment?.ground_y ?? srcH - 50.0);
    const restitution = Number(projObj.physics?.restitution ?? projObj.restitution ?? scene.parameters?.restitution?.value ?? 0.6);

    this.projectile = {
      x0,
      y0,
      mass: Number(scene.parameters?.mass?.value ?? projObj.physics?.mass_kg ?? projObj.mass_kg ?? 1.0),
      radiusPx: Number(projObj.geometry?.radius_source_px ?? projObj.geometry?.radius_px ?? projObj.radius ?? 15.0),
      groundY,
      restitution,
      dragCoeff: Number(scene.parameters?.airResistance?.value ?? projObj.physics?.drag_coeff ?? projObj.drag_coeff ?? 0.0)
    };

    return {
      isAlgebraic: false,
      q: [x0, y0],
      v: [vx0, vy0],
      invMass: [1.0 / this.projectile.mass, 1.0 / this.projectile.mass]
    };
  }

  _compileSpringMass(scene, objects) {
    const k = Number(scene.parameters?.springConstant?.value ?? 50.0); // N/m
    const mass = Number(scene.parameters?.mass?.value ?? 1.0);
    const friction = Number(scene.parameters?.friction?.value ?? 0.1);
    const angleDeg = Number(scene.parameters?.inclineAngle?.value ?? 0.0);
    const angleRad = (angleDeg * Math.PI) / 180.0;

    const restLenPx = Number(scene.geometry?.spring_rest_length_px ?? 200.0);
    const x0 = Number(scene.geometry?.initial_position_px ?? 300.0);

    this.springSystem = {
      k,
      mass,
      friction,
      inclineAngleRad: angleRad,
      restLengthPx: restLenPx
    };

    return {
      isAlgebraic: false,
      q: [x0],
      v: [0.0],
      invMass: [1.0 / mass]
    };
  }

  /**
   * Evaluates generalized forces / torques for the active mechanics configuration.
   * 
   * PHYSICAL LAWS ENCODED:
   * 1. Simple Pendulum Equation of Motion:
   *      tau = -m * g * L * sin(theta) - gamma * m * L^2 * omega
   * 2. Projectile Dynamics under Gravity & Quadratic Drag:
   *      F_x = -drag * |v| * v_x
   *      F_y = +m * g_px - drag * |v| * v_y
   * 3. Hooke's Law & Coulomb Friction on Incline:
   *      F = -k * (s - s_0) + m * g * sin(alpha) - mu * m * g * cos(alpha) * sign(v)
   */
  evaluateForces(q, v, t) {
    if (this.subtype === 'pendulum') {
      const forces = new Float64Array(this.bobs.length);
      for (let i = 0; i < this.bobs.length; i++) {
        const bob = this.bobs[i];
        const theta = q[i];
        const omega = v[i];

        // Physical Law: Gravitational restoring torque: tau_g = -m * g * L * sin(theta)
        const tauGrav = -bob.mass * this.gravity * bob.lengthM * Math.sin(theta);

        // Physical Law: Viscous angular damping torque: tau_d = -damping * I * omega
        const inertia = bob.mass * Math.pow(bob.lengthM, 2);
        const tauDamping = -bob.damping * inertia * omega;

        // Total generalized torque applied to theta coordinate
        forces[i] = tauGrav + tauDamping;
      }
      return forces;
    }

    if (this.subtype === 'projectile') {
      // 2D particle dynamics
      const vx = v[0];
      const vy = v[1];
      const speed = Math.hypot(vx, vy);

      // Physical Law: Constant downward gravity force (Y-axis points down): F_y = m * g_px
      const gPx = this.gravity * this.pixelsPerMeter;
      const fGravY = this.projectile.mass * gPx;

      // Physical Law: Quadratic air resistance drag: F_drag = -c * |v| * v
      const fDragX = -this.projectile.dragCoeff * speed * vx;
      const fDragY = -this.projectile.dragCoeff * speed * vy;

      return new Float64Array([fDragX, fGravY + fDragY]);
    }

    if (this.subtype === 'spring_mass') {
      const x = q[0];
      const vx = v[0];
      const sys = this.springSystem;

      // Physical Law: Hooke's law: F_spring = -k * (s - s_0) in SI Newtons
      const deltaM = (x - sys.restLengthPx) / this.pixelsPerMeter;
      const fSpringN = -sys.k * deltaM;
      const fSpringPx = fSpringN * this.pixelsPerMeter;

      // Physical Law: Downhill gravity component: F_parallel = m * g * sin(alpha)
      const gPx = this.gravity * this.pixelsPerMeter;
      const fDownhill = sys.mass * gPx * Math.sin(sys.inclineAngleRad);

      // Physical Law: Coulomb kinetic friction: f_k = -mu * N * sign(v) where N = m * g * cos(alpha)
      const normalForce = sys.mass * gPx * Math.cos(sys.inclineAngleRad);
      const fFriction = Math.abs(vx) > 1e-4 ? -sys.friction * normalForce * Math.sign(vx) : 0.0;

      return new Float64Array([fSpringPx + fDownhill + fFriction]);
    }

    return new Float64Array(q.length);
  }

  /**
   * Event detection and impulse redirection:
   * - Pendulum: Collisions between adjacent bobs in Newton's cradle.
   * - Projectile: Landing on ground boundary.
   */
  checkEvents(q, v, dt) {
    if (this.subtype === 'pendulum' && this.bobs.length > 1) {
      // Newton's cradle inter-bob collision detection
      for (let i = 0; i < this.bobs.length - 1; i++) {
        const bobA = this.bobs[i];
        const bobB = this.bobs[i + 1];

        const posA = this.getBobPosition(i, q[i]);
        const posB = this.getBobPosition(i + 1, q[i + 1]);

        const dist = Math.hypot(posB.x - posA.x, posB.y - posA.y);
        const minDist = bobA.radiusPx + bobB.radiusPx;

        // Physical Law: Elastic 1D Momentum Exchange between equal mass bobs
        if (dist <= minDist && v[i] > v[i + 1]) {
          const tmp = v[i];
          v[i] = v[i + 1];
          v[i + 1] = tmp;

          // Prevent overlap penetration
          const overlap = minDist - dist;
          q[i] -= (overlap / bobA.lengthPx) * 0.5;
          q[i + 1] += (overlap / bobB.lengthPx) * 0.5;
        }
      }
    } else if (this.subtype === 'projectile') {
      const y = q[1];
      const vy = v[1];
      if (y >= this.projectile.groundY && vy > 0) {
        q[1] = this.projectile.groundY;
        const rest = this.projectile.restitution ?? 0.6;
        // Physical Law: Ground impact inelastic bounce
        const bounced = EventEngine.redirectCollision({ x: v[0], y: vy }, { x: 0, y: -1 }, rest);
        v[0] = bounced.x * 0.85; // Ground friction
        v[1] = Math.abs(bounced.y) < 10.0 ? 0.0 : bounced.y;
      }
    }
  }

  /**
   * Computes bob center in native source pixels for bob index i and angle theta.
   * Coordinate contract: theta = 0 is downward vertical, Y increases downwards.
   */
  getBobPosition(index, theta) {
    const bob = this.bobs[index] || this.bobs[0];
    const pivot = bob.pivot;
    const L = bob.lengthPx;
    return {
      x: pivot.x + L * Math.sin(theta),
      y: pivot.y + L * Math.cos(theta)
    };
  }

  setParameter(name, value) {
    const val = Number(value);
    if (!Number.isFinite(val)) return;

    if (name === 'length' || name === 'string_length') {
      this.bobs.forEach(bob => {
        bob.lengthM = val;
        bob.lengthPx = val * this.pixelsPerMeter;
      });
      // Update generalized inertia
      if (this.core) {
        for (let i = 0; i < this.bobs.length; i++) {
          this.core.invMass[i] = 1.0 / (this.bobs[i].mass * Math.pow(val, 2));
        }
      }
    } else if (name === 'gravity') {
      this.gravity = val;
    } else if (name === 'mass') {
      this.bobs.forEach((bob, i) => {
        bob.mass = val;
        if (this.core) {
          this.core.invMass[i] = 1.0 / (val * Math.pow(bob.lengthM, 2));
        }
      });
      if (this.projectile && this.core) {
        this.projectile.mass = val;
        this.core.invMass[0] = 1.0 / val;
        this.core.invMass[1] = 1.0 / val;
      }
    } else if (name === 'initialAngle') {
      const rad = (val * Math.PI) / 180.0;
      if (this.core && this.core.q.length > 0) {
        this.core.q[0] = rad;
        this.core.v[0] = 0.0;
      }
    } else if (name === 'initialVelocity' || name === 'launchSpeed' || name === 'speed') {
      if (this.projectile && this.core) {
        const rad = Math.atan2(-this.core.v[1], this.core.v[0]);
        const speedPxS = val * this.pixelsPerMeter;
        this.core.v[0] = speedPxS * Math.cos(rad);
        this.core.v[1] = -speedPxS * Math.sin(rad);
      }
    } else if (name === 'launchAngle' || name === 'angle') {
      if (this.projectile && this.core) {
        const speedPxS = Math.hypot(this.core.v[0], this.core.v[1]);
        const rad = (val * Math.PI) / 180.0;
        this.core.v[0] = speedPxS * Math.cos(rad);
        this.core.v[1] = -speedPxS * Math.sin(rad);
      }
    } else if (name === 'airResistance' || name === 'drag') {
      if (this.projectile) {
        this.projectile.dragCoeff = val;
      }
    }
  }

  extractState(core) {
    if (this.subtype === 'pendulum') {
      const theta = core.q[0] || 0.0;
      const omega = core.v[0] || 0.0;
      const primaryBob = this.bobs[0] || {};
      const L_m = primaryBob.lengthM || 1.0;
      const m_kg = primaryBob.mass || 1.0;

      // Physical Law: Small-angle theoretical period: T = 2 * pi * sqrt(L / g)
      const periodTheory = 2.0 * Math.PI * Math.sqrt(L_m / this.gravity);

      // Physical Law: Mechanical energy: PE = m*g*L*(1 - cos(theta)), KE = 0.5 * m * (L*omega)^2
      const pe = m_kg * this.gravity * L_m * (1.0 - Math.cos(theta));
      const ke = 0.5 * m_kg * Math.pow(L_m * omega, 2);

      const bobPositions = this.bobs.map((b, i) => {
        const th = core.q[i] || 0.0;
        const pos = this.getBobPosition(i, th);
        return {
          id: b.id,
          x: pos.x,
          y: pos.y,
          theta: th,
          thetaDeg: (th * 180.0) / Math.PI,
          omega: core.v[i] || 0.0,
          radiusPx: b.radiusPx,
          lengthPx: b.lengthPx,
          pivot: b.pivot
        };
      });

      return {
        domain: 'mechanics',
        type: 'pendulum',
        length: L_m,
        gravity: this.gravity,
        thetaDeg: (theta * 180.0) / Math.PI,
        omegaDegS: (omega * 180.0) / Math.PI,
        periodTheory,
        energyTotal: pe + ke,
        potentialEnergy: pe,
        kineticEnergy: ke,
        bobCenter: bobPositions[0],
        bobs: bobPositions
      };
    }

    if (this.subtype === 'projectile') {
      const x = core.q[0] || 0.0;
      const y = core.q[1] || 0.0;
      const vx = core.v[0] || 0.0;
      const vy = core.v[1] || 0.0;

      return {
        domain: 'mechanics',
        type: 'projectile',
        x,
        y,
        vx,
        vy,
        speedMps: Math.hypot(vx, vy) / this.pixelsPerMeter,
        altitudePx: this.projectile ? Math.max(0.0, this.projectile.groundY - y) : 0.0
      };
    }

    if (this.subtype === 'spring_mass') {
      const x = core.q[0] || 0.0;
      const v = core.v[0] || 0.0;
      return {
        domain: 'mechanics',
        type: 'spring_mass',
        positionPx: x,
        velocityPxS: v
      };
    }

    return { domain: 'mechanics' };
  }
}

/**
 * engine/mechanics/MechanicsAdapter.js
 * 
 * SimulationAdapter wrapping specialized mechanics solvers:
 * - PendulumSimulation (nonlinear RK4 integrator)
 * - ProjectileSimulation (exact analytical kinematics)
 * Features an authoritative, pure mathematical physics kernel shared across both
 * headless execution and browser canvas rendering.
 * Rejects unsupported subtypes (inclined_plane, spring_mass) explicitly without fabrication.
 */

import { SimulationAdapter } from '../core/SimulationAdapter.js';
import { PendulumSimulation } from './pendulumSimulation.js';
import { ProjectileSimulation } from './projectileSimulation.js';
import { PendulumKernel, ProjectileKernel } from './kernels.js';
import {
  UnsupportedPhysicsSubtypeError,
  PhysicsSceneValidationError,
  MissingRequiredParameterError
} from '../core/errors.js';
import { getParameterInUnit, convertUnit } from '../core/units.js';

export class MechanicsAdapter extends SimulationAdapter {
  static domain = 'mechanics';

  constructor() {
    super();
    this.sim = null;
    this.subtype = 'pendulum';
    this.physicsKernel = null;
    this._ticker = null;
  }

  static canHandle(scene) {
    const domain = scene?.domain;
    return domain === 'mechanics' || domain === 'kinematics';
  }

  canHandle(scene) {
    return MechanicsAdapter.canHandle(scene);
  }

  async initialize(scene, container = null, options = {}) {
    await super.initialize(scene, container, options);
    this.subtype = scene.subtype;

    switch (this.subtype) {
      case 'pendulum':
        return this._initPendulum(scene, container, options);
      case 'projectile':
        return this._initProjectile(scene, container, options);
      case 'inclined_plane':
        throw new UnsupportedPhysicsSubtypeError('mechanics', 'inclined_plane');
      case 'spring_mass':
        throw new UnsupportedPhysicsSubtypeError('mechanics', 'spring_mass');
      default:
        throw new UnsupportedPhysicsSubtypeError('mechanics', this.subtype || 'unknown');
    }
  }

  _initPendulum(scene, container, options) {
    const pendulumObj = scene.objects?.find(o => o.type === 'pendulum') || scene.objects?.[0];
    if (!pendulumObj) {
      throw new PhysicsSceneValidationError([{
        code: 'MISSING_PENDULUM_OBJECT',
        path: 'objects',
        message: 'Mechanics scene with subtype "pendulum" requires a pendulum object in objects array.'
      }]);
    }

    // 1. Physical Parameters: strict extraction without fabrication
    let lengthM = null;
    if (scene.parameters?.length) {
      lengthM = getParameterInUnit(scene, 'length', 'm');
    } else if (pendulumObj.physics?.length_m !== undefined) {
      lengthM = Number(pendulumObj.physics.length_m);
    } else {
      throw new MissingRequiredParameterError('length', 'parameters.length or objects[0].physics.length_m');
    }

    if (!Number.isFinite(lengthM) || lengthM <= 0) {
      throw new PhysicsSceneValidationError([{
        code: 'INVALID_PENDULUM_LENGTH',
        path: 'parameters.length',
        message: `Pendulum length must be a positive finite number: ${lengthM}`
      }]);
    }

    let gravityMS2 = null;
    if (scene.parameters?.gravity) {
      gravityMS2 = getParameterInUnit(scene, 'gravity', 'm/s²');
    } else if (scene.environment?.gravity_m_s2 !== undefined) {
      gravityMS2 = Number(scene.environment.gravity_m_s2);
    } else if (scene.environment?.gravity !== undefined) {
      gravityMS2 = Number(scene.environment.gravity);
    } else {
      throw new MissingRequiredParameterError('gravity', 'environment.gravity_m_s2 or parameters.gravity');
    }

    if (!Number.isFinite(gravityMS2) || gravityMS2 < 0) {
      throw new PhysicsSceneValidationError([{
        code: 'INVALID_GRAVITY',
        path: 'parameters.gravity',
        message: `Gravitational acceleration must be a non-negative finite number: ${gravityMS2}`
      }]);
    }

    let theta0Rad = null;
    if (scene.parameters?.initialAngle) {
      theta0Rad = getParameterInUnit(scene, 'initialAngle', 'rad');
    } else if (scene.parameters?.angle) {
      theta0Rad = getParameterInUnit(scene, 'angle', 'rad');
    } else if (pendulumObj.physics?.theta0_rad !== undefined) {
      theta0Rad = Number(pendulumObj.physics.theta0_rad);
    } else {
      throw new MissingRequiredParameterError('initialAngle', 'parameters.initialAngle or objects[0].physics.theta0_rad');
    }

    let massKg = null;
    if (scene.parameters?.mass) {
      massKg = getParameterInUnit(scene, 'mass', 'kg');
    } else if (pendulumObj.physics?.mass_kg !== undefined) {
      massKg = Number(pendulumObj.physics.mass_kg);
    } else {
      throw new MissingRequiredParameterError('mass', 'parameters.mass or objects[0].physics.mass_kg');
    }

    if (!Number.isFinite(massKg) || massKg <= 0) {
      throw new PhysicsSceneValidationError([{
        code: 'INVALID_PENDULUM_MASS',
        path: 'parameters.mass',
        message: `Pendulum mass must be a positive finite number: ${massKg}`
      }]);
    }

    let damping = null;
    if (scene.parameters?.damping) {
      damping = Number(scene.parameters.damping.value);
    } else if (pendulumObj.physics?.damping_s_inv !== undefined) {
      damping = Number(pendulumObj.physics.damping_s_inv);
    } else {
      throw new MissingRequiredParameterError('damping', 'parameters.damping or objects[0].physics.damping_s_inv');
    }

    if (!Number.isFinite(damping) || damping < 0) {
      throw new PhysicsSceneValidationError([{
        code: 'INVALID_PENDULUM_DAMPING',
        path: 'parameters.damping',
        message: `Pendulum damping must be a non-negative finite number: ${damping}`
      }]);
    }

    // 2. Geometry: must be explicitly declared in object
    const pivot = pendulumObj.geometry?.pivot || pendulumObj.pivot;
    if (!pivot || !Number.isFinite(pivot.x) || !Number.isFinite(pivot.y)) {
      throw new MissingRequiredParameterError('pivot', 'objects[0].geometry.pivot');
    }

    const stringLengthPx = pendulumObj.geometry?.string_length_px || pendulumObj.length || pendulumObj.geometry?.length_px;
    if (!stringLengthPx || !Number.isFinite(stringLengthPx)) {
      throw new MissingRequiredParameterError('string_length_px', 'objects[0].geometry.string_length_px');
    }

    const bobRadiusPx = pendulumObj.geometry?.bob_radius_px || pendulumObj.geometry?.radius_px || pendulumObj.radius;
    if (!bobRadiusPx || !Number.isFinite(bobRadiusPx) || bobRadiusPx <= 0) {
      throw new MissingRequiredParameterError('bob_radius_px', 'objects[0].geometry.bob_radius_px');
    }

    // 3. Construct Authoritative Numerical Physics Kernel (240 Hz RK4 Integrator)
    this.physicsKernel = new PendulumKernel({
      lengthM,
      gravityMS2,
      theta0Rad,
      omega0Rad: 0.0,
      massKg,
      damping
    });
    this.physicsKernel.pivot = pivot;
    this.physicsKernel.stringLengthPx = stringLengthPx;
    this.physicsKernel.bobRadiusPx = bobRadiusPx;

    // 4. Adapt scene for browser simulation if container is provided
    const adaptedScene = JSON.parse(JSON.stringify(scene));
    const adaptedObj = adaptedScene.objects.find(o => o.type === 'pendulum') || adaptedScene.objects[0];
    adaptedObj.geometry = {
      pivot,
      bob_radius_px: bobRadiusPx,
      string_length_px: stringLengthPx,
      length_px: stringLengthPx
    };
    adaptedObj.physics = {
      length_m: lengthM,
      mass_kg: massKg,
      damping_s_inv: damping,
      theta0_rad: theta0Rad,
      omega0_rad_s: 0.0
    };
    adaptedScene.environment = {
      gravity_m_s2: gravityMS2
    };

    if (container && typeof document !== 'undefined') {
      this.sim = new PendulumSimulation(container, adaptedScene, {
        kernel: this.physicsKernel,
        pivot,
        stringLengthPx,
        bobRadiusPx
      });
      this.sim.onStateChange?.(() => {
        this.notifyStateChange(this.getState());
      });
    }

    if (typeof setInterval !== 'undefined') {
      this._ticker = setInterval(() => {
        if (this.running) {
          this.notifyStateChange(this.getState());
        }
      }, 100);
    }

    this.notifyStateChange(this.getState());
  }

  _initProjectile(scene, container, options) {
    const ballObj = scene.objects?.find(o => o.type === 'projectile' || o.type === 'circle') || scene.objects?.[0];
    if (!ballObj) {
      throw new PhysicsSceneValidationError([{
        code: 'MISSING_PROJECTILE_OBJECT',
        path: 'objects',
        message: 'Mechanics scene with subtype "projectile" requires a projectile object in objects array.'
      }]);
    }

    // 1. Physical Parameters: strict extraction without fabrication
    let speedMps = null;
    if (scene.parameters?.speed) {
      speedMps = getParameterInUnit(scene, 'speed', 'm/s');
    } else if (ballObj.physics?.speed_m_s !== undefined) {
      speedMps = Number(ballObj.physics.speed_m_s);
    } else {
      throw new MissingRequiredParameterError('speed', 'parameters.speed or objects[0].physics.speed_m_s');
    }

    if (!Number.isFinite(speedMps) || speedMps < 0) {
      throw new PhysicsSceneValidationError([{
        code: 'INVALID_PROJECTILE_SPEED',
        path: 'parameters.speed',
        message: `Projectile launch speed must be a non-negative finite number: ${speedMps}`
      }]);
    }

    let angleDeg = null;
    if (scene.parameters?.angle) {
      const rad = getParameterInUnit(scene, 'angle', 'rad');
      angleDeg = (rad * 180.0) / Math.PI;
    } else if (ballObj.physics?.launch_angle_deg !== undefined) {
      angleDeg = Number(ballObj.physics.launch_angle_deg);
    } else {
      throw new MissingRequiredParameterError('angle', 'parameters.angle or objects[0].physics.launch_angle_deg');
    }

    let gravityMS2 = null;
    if (scene.parameters?.gravity) {
      gravityMS2 = getParameterInUnit(scene, 'gravity', 'm/s²');
    } else if (scene.environment?.gravity_m_s2 !== undefined) {
      gravityMS2 = Number(scene.environment.gravity_m_s2);
    } else if (scene.environment?.gravity !== undefined) {
      gravityMS2 = Number(scene.environment.gravity);
    } else {
      throw new MissingRequiredParameterError('gravity', 'environment.gravity_m_s2 or parameters.gravity');
    }

    // 2. Geometry: launch position must be explicitly declared
    const launchPos = ballObj.geometry?.launch_source_px || ballObj.initial_position;
    if (!launchPos || !Number.isFinite(launchPos.x) || !Number.isFinite(launchPos.y)) {
      throw new MissingRequiredParameterError('launch_source_px', 'objects[0].geometry.launch_source_px');
    }

    const radiusSourcePx = Number(ballObj.geometry?.radius_source_px || ballObj.geometry?.radius_px || ballObj.radius);
    if (!Number.isFinite(radiusSourcePx) || radiusSourcePx <= 0) {
      throw new MissingRequiredParameterError('radius_source_px', 'objects[0].geometry.radius_source_px');
    }

    let ppm = null;
    if (scene.calibration?.pixels_per_meter !== undefined) {
      ppm = Number(scene.calibration.pixels_per_meter);
    } else if (scene.coordinateSpace?.type === 'source_px') {
      throw new MissingRequiredParameterError('pixels_per_meter', 'calibration.pixels_per_meter');
    } else {
      ppm = 1.0;
    }
    if (!Number.isFinite(ppm) || ppm <= 0) {
      throw new PhysicsSceneValidationError([{
        code: 'INVALID_PIXELS_PER_METER',
        path: 'calibration.pixels_per_meter',
        message: `Pixels per meter must be a positive finite number: ${ppm}`
      }]);
    }

    // 3. Construct Authoritative Numerical Physics Kernel (Exact Kinematics)
    this.physicsKernel = new ProjectileKernel({
      speedMps,
      angleDeg,
      gravityMS2,
      x0: launchPos.x,
      y0: launchPos.y
    });
    this.physicsKernel.ppm = ppm;
    this.physicsKernel.radiusSourcePx = radiusSourcePx;

    // 4. Adapt scene for browser simulation if container is provided
    const adaptedScene = JSON.parse(JSON.stringify(scene));
    const adaptedBall = adaptedScene.objects.find(o => o.type === 'projectile' || o.type === 'circle') || adaptedScene.objects[0];
    adaptedBall.physics = {
      speed_m_s: speedMps,
      launch_angle_deg: angleDeg
    };
    adaptedBall.geometry = {
      launch_source_px: launchPos,
      radius_source_px: radiusSourcePx
    };
    adaptedScene.environment = {
      gravity_m_s2: gravityMS2
    };

    if (container && typeof document !== 'undefined') {
      this.sim = new ProjectileSimulation(container, adaptedScene, {
        kernel: this.physicsKernel,
        ppm,
        ballRadiusPx: radiusSourcePx,
        launchSource: launchPos
      });
    }

    this.notifyStateChange(this.getState());
  }

  start() {
    super.start();
    if (this.sim) {
      this.sim.play();
    }
    this.notifyStateChange(this.getState());
  }

  pause() {
    super.pause();
    if (this.sim) {
      this.sim.pause();
    }
    this.notifyStateChange(this.getState());
  }

  reset() {
    super.reset();
    if (this.physicsKernel) {
      this.physicsKernel.reset();
    }
    if (this.sim) {
      this.sim.reset();
    }
    this.notifyStateChange(this.getState());
  }

  step(dt = 1 / 60) {
    super.step(dt);
    if (this.physicsKernel) {
      this.physicsKernel.step(dt);
    }
    if (this.sim) {
      if (this.subtype === 'pendulum') {
        this.sim.render?.(this.physicsKernel.theta, this.physicsKernel.omega);
      } else if (this.subtype === 'projectile') {
        this.sim.render?.();
      }
    }
    this.notifyStateChange(this.getState());
  }

  /**
   * Internal hook called by SimulationAdapter after atomic validation, unit conversion,
   * and scene mutation succeed.
   */
  _applyParameterUpdate(address, convertedVal, key, targetId, incomingUnit) {
    if (this.subtype === 'pendulum') {
      if (key === 'length' || key === 'length_m') {
        this.physicsKernel.lengthM = convertedVal;
        if (this.sim) this.sim.render?.(this.physicsKernel.theta, this.physicsKernel.omega);
      } else if (key === 'gravity' || key === 'gravity_m_s2') {
        this.physicsKernel.g = convertedVal;
        if (this.sim) this.sim.render?.(this.physicsKernel.theta, this.physicsKernel.omega);
      } else if (key === 'initialAngle' || key === 'theta0' || key === 'angle') {
        this.physicsKernel.theta0 = convertedVal;
        this.physicsKernel.theta = convertedVal;
        this.physicsKernel.omega = 0.0;
        if (this.sim) {
          this.sim.render?.(convertedVal, 0.0);
        }
      } else if (key === 'damping' || key === 'damping_s_inv') {
        this.physicsKernel.damping = convertedVal;
      } else if (key === 'mass' || key === 'mass_kg') {
        this.physicsKernel.massKg = convertedVal;
      }
    } else if (this.subtype === 'projectile') {
      if (key === 'speed' || key === 'speed_m_s') {
        this.physicsKernel.speedMps = convertedVal;
        if (this.sim) {
          this.sim.render?.();
        }
      } else if (key === 'angle' || key === 'launch_angle_deg') {
        const deg = (convertedVal * 180.0) / Math.PI;
        this.physicsKernel.angleDeg = deg;
        if (this.sim) {
          this.sim.render?.();
        }
      } else if (key === 'gravity' || key === 'gravity_m_s2') {
        this.physicsKernel.g = convertedVal;
        if (this.sim) {
          this.sim.render?.();
        }
      }
    }

    this.notifyStateChange(this.getState());
  }

  getOutput() {
    const state = this.getState();
    return {
      domain: 'mechanics',
      subtype: this.subtype,
      time: state.time || 0.0,
      state,
      geometry: {
        thetaRad: (state.thetaDeg !== undefined ? (state.thetaDeg * Math.PI) / 180.0 : 0.0),
        lengthM: state.length || 0.0,
        xM: state.xM || 0.0,
        yM: state.yM || 0.0
      },
      telemetry: state,
      events: [],
      editableParameters: this.getParameters()
    };
  }

  getState() {
    if (this.subtype === 'projectile') {
      const k = this.physicsKernel;
      const pos = k ? k.getState() : { xM: 0, yM: 0, vx: 0, vy: 0, hasLanded: false };
      return {
        domain: 'mechanics',
        type: 'projectile',
        subtype: 'projectile',
        running: this.running,
        time: Number((k ? k.simTime : 0).toFixed(2)),
        speed: Number((k ? k.speedMps : 0).toFixed(2)),
        angleDeg: Number((k ? k.angleDeg : 0).toFixed(1)),
        gravity: Number((k ? k.g : 0).toFixed(2)),
        xM: Number(pos.xM.toFixed(3)),
        yM: Number(pos.yM.toFixed(3)),
        vx: Number(pos.vx.toFixed(3)),
        vy: Number(pos.vy.toFixed(3)),
        hasLanded: Boolean(pos.hasLanded)
      };
    }

    // Pendulum state
    const k = this.physicsKernel;
    if (!k) return {};

    const thetaDeg = (k.theta * 180.0) / Math.PI;
    const energy = k.getEnergy();

    return {
      domain: 'mechanics',
      type: 'pendulum',
      subtype: 'pendulum',
      running: this.running,
      time: Number(k.simTime.toFixed(2)),
      thetaDeg: Number(thetaDeg.toFixed(1)),
      thetaRad: Number(k.theta.toFixed(4)),
      omega: Number(k.omega.toFixed(4)),
      speed: Number(energy.speed.toFixed(2)),
      length: Number(k.lengthM.toFixed(2)),
      gravity: Number(k.g.toFixed(2)),
      potentialEnergy: Number(energy.pe.toFixed(2)),
      kineticEnergy: Number(energy.ke.toFixed(2)),
      totalEnergy: Number(energy.total.toFixed(2)),
      calibrated: true
    };
  }

  dispose() {
    if (this._ticker) {
      clearInterval(this._ticker);
      this._ticker = null;
    }
    if (this.sim?.destroy) {
      this.sim.destroy();
    }
    this.sim = null;
    this.physicsKernel = null;
    super.dispose();
  }
}

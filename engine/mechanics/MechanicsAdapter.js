/**
 * engine/mechanics/MechanicsAdapter.js
 * 
 * SimulationAdapter wrapping existing mechanics solvers (e.g. PendulumSimulation).
 * Preserves all underlying RK4 numerical integration without altering the physics logic.
 */

import { SimulationAdapter } from '../core/SimulationAdapter.js';
import { PendulumSimulation } from './pendulumSimulation.js';

export class MechanicsAdapter extends SimulationAdapter {
  constructor() {
    super();
    this.sim = null;
    this._ticker = null;
  }

  static canHandle(scene) {
    const domain = scene?.domain || scene?.simulation?.domain || scene?.simulation_type;
    return domain === 'mechanics' || domain === 'kinematics';
  }

  canHandle(scene) {
    return MechanicsAdapter.canHandle(scene);
  }

  async initialize(scene, container, options = {}) {
    await super.initialize(scene, container, options);

    // Build or adapt scene objects for PendulumSimulation if needed
    let adaptedScene = JSON.parse(JSON.stringify(scene));

    let pendulumObj = adaptedScene.objects?.find(o => o.type === 'pendulum');
    if (!pendulumObj) {
      // Auto-synthesize standard pendulum object based on parameters and geometry
      const srcW = scene.coordinateSystem?.width || scene.source?.width || 800;
      const srcH = scene.coordinateSystem?.height || scene.source?.height || 600;
      const pivot = scene.geometry?.pivot || { x: srcW * 0.5, y: srcH * 0.2 };
      const lengthPx = scene.geometry?.length_px || 250;
      const theta0Deg = Number(scene.parameters?.initialAngle?.value ?? 25);
      const theta0Rad = (theta0Deg * Math.PI) / 180.0;

      pendulumObj = {
        id: 'pendulum_main',
        type: 'pendulum',
        role: 'dynamic',
        geometry: {
          pivot,
          bob_radius_px: scene.geometry?.bob_radius_px || 24,
          string_length_px: scene.geometry?.string_length_px || lengthPx,
          length_px: lengthPx
        },
        physics: {
          length_m: Number(scene.parameters?.length?.value ?? 1.2),
          mass_kg: Number(scene.parameters?.mass?.value ?? 1.0),
          damping_s_inv: Number(scene.parameters?.damping?.value ?? 0.0),
          theta0_rad: theta0Rad,
          omega0_rad_s: 0.0
        },
        visual: scene.visual || {}
      };

      adaptedScene.objects = [pendulumObj];
      adaptedScene.environment = {
        gravity_m_s2: Number(scene.parameters?.gravity?.value ?? 9.81)
      };
    } else {
      // Synchronize scene parameters into the existing object specification
      if (!pendulumObj.geometry) {
        pendulumObj.geometry = {
          pivot: pendulumObj.pivot || { x: 400, y: 150 },
          bob_radius_px: pendulumObj.radius || 24,
          string_length_px: pendulumObj.string_length_px || pendulumObj.length || 250,
          length_px: pendulumObj.length || 250
        };
      } else {
        pendulumObj.geometry.string_length_px = pendulumObj.geometry.string_length_px || pendulumObj.geometry.length_px || 250;
      }
      if (!pendulumObj.physics) {
        pendulumObj.physics = {
          length_m: Number(scene.parameters?.length?.value ?? 1.0),
          mass_kg: Number(scene.parameters?.mass?.value ?? 1.0),
          damping_s_inv: 0.0,
          theta0_rad: (Number(scene.parameters?.initialAngle?.value ?? -27.4) * Math.PI) / 180.0,
          omega0_rad_s: 0.0
        };
      }

      if (scene.parameters?.length?.value) {
        pendulumObj.physics.length_m = Number(scene.parameters.length.value);
      }
      if (scene.parameters?.gravity?.value) {
        adaptedScene.environment = adaptedScene.environment || {};
        adaptedScene.environment.gravity_m_s2 = Number(scene.parameters.gravity.value);
      }
    }

    // Instantiate existing, verified PendulumSimulation inside container
    if (container) {
      this.sim = new PendulumSimulation(container, adaptedScene);
    }

    // Start state telemetry heartbeat (60 Hz when running, or on change)
    this._ticker = setInterval(() => {
      if (this.sim?.running) {
        this.notifyStateChange(this.getState());
      }
    }, 100);

    this.notifyStateChange(this.getState());
  }

  play() {
    super.play();
    this.sim?.play();
    this.notifyStateChange(this.getState());
  }

  pause() {
    super.pause();
    this.sim?.pause();
    this.notifyStateChange(this.getState());
  }

  reset() {
    super.reset();
    this.sim?.reset();
    this.notifyStateChange(this.getState());
  }

  setParameter(name, value) {
    super.setParameter(name, value);
    const numVal = Number(value);

    if (name === 'length' || name === 'length_m') {
      this.sim?.setLengthMeters(numVal);
    } else if (name === 'gravity' || name === 'gravity_m_s2') {
      this.sim?.setGravity(numVal);
    } else if (name === 'speed' || name === 'timeScale') {
      this.sim?.setSpeed(numVal);
    } else if (name === 'initialAngle' || name === 'theta0') {
      const rad = (numVal * Math.PI) / 180.0;
      if (this.sim) {
        this.sim.theta0 = rad;
        this.sim.theta = rad;
        this.sim.omega = 0.0;
        this.sim.prevState = { theta: rad, omega: 0.0 };
        this.sim.render();
      }
    } else if (name === 'damping') {
      if (this.sim) this.sim.damping = numVal;
    } else if (name === 'mass') {
      if (this.sim) this.sim.massKg = numVal;
    }

    this.notifyStateChange(this.getState());
  }

  getState() {
    if (!this.sim) {
      return {
        domain: 'mechanics',
        type: 'pendulum',
        running: this.running,
        time: 0,
        thetaDeg: Number(this.scene?.parameters?.initialAngle?.value ?? 25),
        omega: 0,
        speed: 0,
        length: Number(this.scene?.parameters?.length?.value ?? 1.2),
        gravity: Number(this.scene?.parameters?.gravity?.value ?? 9.81),
        potentialEnergy: 0,
        kineticEnergy: 0,
        totalEnergy: 0,
        calibrated: true
      };
    }

    const thetaDeg = (this.sim.theta * 180.0) / Math.PI;
    const speed = Math.abs(this.sim.omega * this.sim.lengthM);
    const heightM = this.sim.lengthM * (1.0 - Math.cos(this.sim.theta));
    const pe = this.sim.massKg * this.sim.g * heightM;
    const ke = 0.5 * this.sim.massKg * speed * speed;

    return {
      domain: 'mechanics',
      type: 'pendulum',
      running: Boolean(this.sim.running),
      time: Number(this.sim.simTime.toFixed(2)),
      thetaDeg: Number(thetaDeg.toFixed(1)),
      omega: Number(this.sim.omega.toFixed(3)),
      speed: Number(speed.toFixed(2)),
      length: Number(this.sim.lengthM.toFixed(2)),
      gravity: Number(this.sim.g.toFixed(2)),
      potentialEnergy: Number(pe.toFixed(2)),
      kineticEnergy: Number(ke.toFixed(2)),
      totalEnergy: Number((pe + ke).toFixed(2)),
      calibrated: Boolean(this.sim.calibrated)
    };
  }

  resize(width, height, renderContext = null) {
    this.sim?.resize(width, height, renderContext);
    this.sim?.render();
  }

  destroy() {
    if (this._ticker) {
      clearInterval(this._ticker);
      this._ticker = null;
    }
    this.sim?.destroy();
    this.sim = null;
    super.destroy();
  }
}

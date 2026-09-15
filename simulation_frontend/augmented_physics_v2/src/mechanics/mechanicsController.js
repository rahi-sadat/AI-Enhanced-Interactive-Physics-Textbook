/**
 * mechanics/mechanicsController.js
 * 
 * Routes mechanics scenes to appropriate precision engines:
 * - Pendulum: Analytical RK4 (PendulumSimulation)
 * - Projectile: Closed-form kinematics (ProjectileSimulation)
 * - Contact/Rigid-Body: Matter.js with SI unit adapter (Simulation)
 * 
 * Manages clean lifecycle with AbortController to prevent duplicate listeners.
 */

import decomp from 'poly-decomp';
import { Common } from 'matter-js';
Common.setDecomp(decomp);

import { Simulation } from './simulation.js';
import { PendulumSimulation } from './pendulumSimulation.js';
import { ProjectileSimulation } from './projectileSimulation.js';

export class MechanicsController {
  constructor(scene, overlayStage) {
    this.scene = scene;
    this.overlayStage = overlayStage;
    this.abort = new AbortController();

    // Clean overlay and set background
    overlayStage.clearOverlay();
    overlayStage.setBackground(scene?.visual?.background_url ?? null);

    // Resolve domain subtype
    let subtype = scene?.simulation?.subtype;
    if (!subtype) {
      if (scene?.objects?.some(o => o.type === 'pendulum')) {
        subtype = 'pendulum';
      } else if (scene?.objects?.some(o => o.type === 'projectile')) {
        subtype = 'projectile';
      } else {
        subtype = 'generic';
      }
    }
    this.subtype = subtype;

    // Instantiate appropriate solver
    if (subtype === 'pendulum') {
      this.sim = new PendulumSimulation(overlayStage.getContainer(), scene);
    } else if (subtype === 'projectile') {
      this.sim = new ProjectileSimulation(overlayStage.getContainer(), scene);
    } else {
      this.sim = new Simulation(overlayStage.getContainer());
      this.sim.loadScene(scene);
    }

    this._bindControls(scene);
    this._showPanel();
  }

  _bindControls(scene) {
    const sim = this.sim;
    const signal = this.abort.signal;

    // Simulation lifecycle buttons
    document.getElementById('play-button')?.addEventListener('click', () => sim.play(), { signal });
    document.getElementById('pause-button')?.addEventListener('click', () => sim.pause(), { signal });
    document.getElementById('reset-button')?.addEventListener('click', () => sim.reset(), { signal });
    document.getElementById('toggle-colliders')?.addEventListener(
      'change',
      (e) => sim.setWireframes?.(e.target.checked),
      { signal }
    );

    // Gravity slider (SI m/s²)
    const gs = document.getElementById('gravity-slider');
    const gv = document.getElementById('gravity-value');
    if (gs) {
      const defaultG = scene.environment?.gravity_m_s2 ?? (scene.environment?.gravity === 1.0 ? 9.81 : (scene.environment?.gravity || 9.81));
      gs.value = defaultG;
      if (gv) gv.textContent = `${Number(defaultG).toFixed(2)} m/s²`;

      gs.addEventListener(
        'input',
        () => {
          const val = Number(gs.value);
          sim.setGravity(val);
          if (gv) gv.textContent = `${val.toFixed(2)} m/s²`;
        },
        { signal }
      );
    }

    // Speed slider
    const ss = document.getElementById('speed-slider');
    const sv = document.getElementById('speed-value');
    ss?.addEventListener(
      'input',
      () => {
        sim.setSpeed(ss.value);
        if (sv) sv.textContent = ss.value + 'x';
      },
      { signal }
    );

    // Pendulum-specific controls
    const pendGroup = document.getElementById('pendulum-controls-group');
    const pendLenInput = document.getElementById('pendulum-length-input');
    if (pendGroup) {
      pendGroup.style.display = this.subtype === 'pendulum' ? 'block' : 'none';
    }
    if (pendLenInput && this.subtype === 'pendulum') {
      const initLen = scene.objects?.[0]?.physics?.length_m || 1.0;
      pendLenInput.value = initLen;
      pendLenInput.addEventListener(
        'change',
        () => {
          sim.setLengthMeters?.(Number(pendLenInput.value));
        },
        { signal }
      );
    }

    // Target object & Velocity controls (for rigid body scenes)
    const dynGroup = document.getElementById('target-object-group');
    const velGroup = document.getElementById('velocity-control-group');
    if (dynGroup) dynGroup.style.display = this.subtype === 'generic' ? 'block' : 'none';
    if (velGroup) velGroup.style.display = this.subtype === 'generic' ? 'block' : 'none';

    const dynObjs = (scene.objects || []).filter(o => o.role === 'dynamic' || o.type === 'pendulum');
    const sel = document.getElementById('target-object-select');
    if (sel && this.subtype === 'generic') {
      sel.innerHTML = '';
      dynObjs.forEach((o, i) => {
        const opt = document.createElement('option');
        opt.value = o.id;
        opt.textContent = o.id + ' (' + o.type + ')';
        if (i === 0) opt.selected = true;
        sel.appendChild(opt);
      });
    }

    const vs = document.getElementById('velocity-slider');
    const vv = document.getElementById('velocity-value');
    vs?.addEventListener(
      'input',
      () => {
        if (vv) vv.textContent = vs.value + ' m/s';
      },
      { signal }
    );
    document.getElementById('apply-velocity-button')?.addEventListener(
      'click',
      () => {
        const id = sel?.value || dynObjs[0]?.id;
        if (id) sim.setObjectVelocity?.(id, vs?.value ?? 0);
      },
      { signal }
    );
  }

  _showPanel() {
    const mc = document.getElementById('mechanics-controls');
    const oc = document.getElementById('optics-controls');
    if (mc) mc.style.display = 'flex';
    if (oc) oc.style.display = 'none';
  }

  destroy() {
    this.abort.abort();
    this.sim?.destroy?.();
  }
}

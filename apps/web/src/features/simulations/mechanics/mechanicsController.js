/** mechanics/mechanicsController.js
 * Multi-solver coordinator for Kinematics & Mechanics domain.
 * Supports:
 *   1. Rigid body Matter.js physics (inclined plane, springs, Newton's cradle)
 *   2. High-precision analytical projectile motion (ProjectileSimulation)
 * Manages clean lifecycle with AbortController to prevent duplicate listeners.
 */
import decomp from 'poly-decomp';
import { Common } from 'matter-js';
Common.setDecomp(decomp);

import { Simulation } from '@engine/mechanics/simulation.js';
import { ProjectileSimulation } from '@engine/mechanics/projectileSimulation.js';

export class MechanicsController {
  constructor(scene, overlayStage) {
    this.scene = scene;
    this.overlayStage = overlayStage;
    this.abort = new AbortController();

    const srcW = scene.geometry?.source_width ?? scene.coordinate_system?.width ?? scene.render?.source_width_px ?? scene.coordinate_system?.render?.source_width_px ?? scene.source?.image_width_px ?? 800;
    const srcH = scene.geometry?.source_height ?? scene.coordinate_system?.height ?? scene.render?.source_height_px ?? scene.coordinate_system?.render?.source_height_px ?? scene.source?.image_height_px ?? 600;
    overlayStage.setBackground(scene?.visual?.background_url ?? null, srcW, srcH);

    this._initSimulation(scene);
    this._bindControls(scene);
    this._showPanel();
  }

  _initSimulation(scene) {
    this.isProjectile = scene?.simulation_type === 'projectile'
      || scene?.scenario === 'projectile'
      || scene?.simulation?.subtype === 'projectile'
      || (scene.objects || []).some(o => o.type === 'projectile' || o.id?.includes('projectile'));

    this.overlayStage.clearOverlay();

    if (this.isProjectile) {
      this.sim = new ProjectileSimulation(this.overlayStage.getContainer(), scene);
    } else {
      this.sim = new Simulation(this.overlayStage.getContainer());
      this.sim.loadScene(scene);
    }
  }

  _bindControls(scene) {
    const sim = this.sim;
    const signal = this.abort.signal;

    document.getElementById('play-button')?.addEventListener('click',  () => sim.play(), { signal });
    document.getElementById('pause-button')?.addEventListener('click', () => sim.pause(), { signal });
    document.getElementById('reset-button')?.addEventListener('click', () => sim.reset(), { signal });
    document.getElementById('toggle-colliders')?.addEventListener('change',
      e => sim.setWireframes(e.target.checked), { signal });

    const gs = document.getElementById('gravity-slider');
    const gv = document.getElementById('gravity-value');
    if (gs) {
      const gVal = scene.environment?.gravity ?? 1.0;
      gs.value = gVal;
      if (gv) gv.textContent = String(gVal);
      gs.addEventListener('input', () => {
        if (this.isProjectile) {
          sim.setGravity(9.81 * Number(gs.value));
        } else {
          sim.setGravity(gs.value);
        }
        if (gv) gv.textContent = gs.value;
      }, { signal });
    }

    const ss = document.getElementById('speed-slider');
    const sv = document.getElementById('speed-value');
    if (ss) {
      ss.value = 1;
      if (sv) sv.textContent = '1x';
      ss.addEventListener('input', () => {
        sim.setSpeed(ss.value);
        if (sv) sv.textContent = ss.value + 'x';
      }, { signal });
    }

    const dynObjs = (scene.objects || []).filter(o => o.role === 'dynamic' || o.type === 'pendulum' || o.type === 'projectile');
    const sel = document.getElementById('target-object-select');
    if (sel) {
      sel.innerHTML = '';
      dynObjs.forEach((o, i) => {
        const opt = document.createElement('option');
        opt.value = o.id;
        opt.textContent = o.id + ' (' + o.type + ')';
        if (i === 0) opt.selected = true;
        sel.appendChild(opt);
      });
    }

    // NCTB Kinematics Diagram Scenario Switcher
    const mSelect = document.getElementById('mechanics-scene-select');
    if (mSelect) {
      const isCradle = (scene.objects || []).some(o => o.id?.includes('cradle'));
      if (this.isProjectile) {
        mSelect.value = 'projectile';
      } else if (isCradle) {
        mSelect.value = 'newtons_cradle';
      } else {
        mSelect.value = 'with_spring';
      }

      mSelect.addEventListener('change', async (e) => {
        let url = '/scenes/kinematics/physics_scene.json';
        if (e.target.value === 'newtons_cradle') {
          url = '/scenes/kinematics/newtons_cradle_scene.json';
        } else if (e.target.value === 'projectile') {
          url = '/scenes/kinematics/projectile_scene.json';
        }
        const res = await fetch(url + '?t=' + Date.now());
        const data = await res.json();
        this.loadNewScene(data);
      }, { signal });
    }

    // Toggle projectile vs rigidbody control groups
    const projGroup = document.getElementById('projectile-controls-group');
    const rbGroup   = document.getElementById('rigidbody-controls-group');
    if (projGroup) projGroup.style.display = this.isProjectile ? '' : 'none';
    if (rbGroup)   rbGroup.style.display   = this.isProjectile ? 'none' : '';

    // ── PROJECTILE MODE: Speed + Angle sliders ──────────────────────────────
    const vs = document.getElementById('velocity-slider');
    const vv = document.getElementById('velocity-value');
    if (vs && this.isProjectile) {
      const initSpeed = scene.objects?.[0]?.physics?.speed_m_s ?? 25;
      vs.value = initSpeed;
      if (vv) vv.textContent = initSpeed + ' m/s';
      vs.addEventListener('input', () => {
        if (vv) vv.textContent = vs.value + ' m/s';
      }, { signal });
    }

    const as = document.getElementById('angle-slider');
    const av = document.getElementById('angle-value');
    if (as && this.isProjectile) {
      const initAngle = scene.objects?.[0]?.physics?.launch_angle_deg ?? 45;
      as.value = initAngle;
      if (av) av.textContent = initAngle + '\u00b0';
      as.addEventListener('input', () => {
        if (av) av.textContent = as.value + '\u00b0';
        sim.setLaunchAngle?.(Number(as.value));
      }, { signal });
    }

    document.getElementById('apply-velocity-button')?.addEventListener('click', () => {
      if (this.isProjectile) {
        sim.setLaunchSpeed(Number(vs?.value ?? 25));
        sim.setLaunchAngle?.(Number(as?.value ?? 45));
        sim.reset?.();
      }
    }, { signal });

    // ── RIGID BODY MODE: X-velocity slider ──────────────────────────────────
    const rvs = document.getElementById('rb-velocity-slider');
    const rvv = document.getElementById('rb-velocity-value');
    if (rvs && !this.isProjectile) {
      rvs.value = 0;
      if (rvv) rvv.textContent = '0 m/s';
      rvs.addEventListener('input', () => {
        if (rvv) rvv.textContent = rvs.value + ' m/s';
      }, { signal });
    }

    document.getElementById('apply-rb-velocity-button')?.addEventListener('click', () => {
      if (!this.isProjectile) {
        const id = sel?.value || dynObjs[0]?.id;
        if (id) sim.setObjectVelocity(id, rvs?.value ?? 0);
      }
    }, { signal });
  }

  loadNewScene(newScene) {
    this.abort.abort();
    this.abort = new AbortController();

    this.sim?.destroy?.();
    this.scene = newScene;

    const srcW = newScene.geometry?.source_width ?? newScene.coordinate_system?.width ?? newScene.render?.source_width_px ?? newScene.coordinate_system?.render?.source_width_px ?? newScene.source?.image_width_px ?? 800;
    const srcH = newScene.geometry?.source_height ?? newScene.coordinate_system?.height ?? newScene.render?.source_height_px ?? newScene.coordinate_system?.render?.source_height_px ?? newScene.source?.image_height_px ?? 600;
    this.overlayStage.setBackground(newScene?.visual?.background_url ?? null, srcW, srcH);

    this._initSimulation(newScene);
    this._bindControls(newScene);
  }

  _showPanel() {
    const mc = document.getElementById('mechanics-controls');
    const oc = document.getElementById('optics-controls');
    const cc = document.getElementById('circuit-controls');
    if (mc) mc.style.display = 'flex';
    if (oc) oc.style.display = 'none';
    if (cc) cc.style.display = 'none';
  }

  destroy() {
    this.abort.abort();
    this.sim?.destroy?.();
    this.overlayStage.clearOverlay();
    const mc = document.getElementById('mechanics-controls');
    if (mc) mc.style.display = 'none';
  }
}

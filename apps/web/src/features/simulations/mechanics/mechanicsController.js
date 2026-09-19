/** mechanics/mechanicsController.js
 * Wraps Simulation + wires HUD controls for kinematics domain.
 * Manages clean lifecycle with AbortController to prevent duplicate listeners.
 */
import decomp from 'poly-decomp';
import { Common } from 'matter-js';
Common.setDecomp(decomp);

import { Simulation } from '@engine/mechanics/simulation.js';

export class MechanicsController {
  constructor(scene, overlayStage) {
    this.scene = scene;
    this.overlayStage = overlayStage;
    this.abort = new AbortController();

    const srcW = scene.geometry?.source_width ?? scene.coordinate_system?.width ?? scene.render?.source_width_px ?? scene.coordinate_system?.render?.source_width_px ?? 800;
    const srcH = scene.geometry?.source_height ?? scene.coordinate_system?.height ?? scene.render?.source_height_px ?? scene.coordinate_system?.render?.source_height_px ?? 600;
    overlayStage.setBackground(scene?.visual?.background_url ?? null, srcW, srcH);

    this.sim = new Simulation(overlayStage.getContainer());
    this.sim.loadScene(scene);

    this._bindControls(scene);
    this._showPanel();
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
        sim.setGravity(gs.value);
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

    const dynObjs = (scene.objects || []).filter(o => o.role === 'dynamic' || o.type === 'pendulum');
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
      mSelect.value = isCradle ? 'newtons_cradle' : 'with_spring';
      mSelect.addEventListener('change', async (e) => {
        const url = e.target.value === 'newtons_cradle'
          ? '/scenes/kinematics/newtons_cradle_scene.json'
          : '/scenes/kinematics/physics_scene.json';
        const res = await fetch(url + '?t=' + Date.now());
        const data = await res.json();
        this.loadNewScene(data);
      }, { signal });
    }

    const vs = document.getElementById('velocity-slider');
    const vv = document.getElementById('velocity-value');
    vs?.addEventListener('input', () => {
      if (vv) vv.textContent = vs.value + ' m/s';
    }, { signal });

    document.getElementById('apply-velocity-button')?.addEventListener('click', () => {
      const id = sel?.value || dynObjs[0]?.id;
      if (id) sim.setObjectVelocity(id, vs?.value ?? 0);
    }, { signal });
  }

  loadNewScene(newScene) {
    this.abort.abort();
    this.abort = new AbortController();

    this.scene = newScene;
    const srcW = newScene.geometry?.source_width ?? newScene.coordinate_system?.width ?? newScene.render?.source_width_px ?? newScene.coordinate_system?.render?.source_width_px ?? 800;
    const srcH = newScene.geometry?.source_height ?? newScene.coordinate_system?.height ?? newScene.render?.source_height_px ?? newScene.coordinate_system?.render?.source_height_px ?? 600;
    this.overlayStage.setBackground(newScene?.visual?.background_url ?? null, srcW, srcH);
    this.sim.loadScene(newScene);
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
    const mc = document.getElementById('mechanics-controls');
    if (mc) mc.style.display = 'none';
  }
}

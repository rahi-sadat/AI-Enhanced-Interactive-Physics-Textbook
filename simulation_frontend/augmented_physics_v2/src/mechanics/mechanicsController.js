/** mechanics/mechanicsController.js
 * Wraps Simulation + wires HUD controls for kinematics domain.
 */
import decomp from 'poly-decomp';
import { Common } from 'matter-js';
Common.setDecomp(decomp);

import { Simulation } from './simulation.js';

export class MechanicsController {
  constructor(scene, overlayStage) {
    this.scene = scene;
    this.overlayStage = overlayStage;
    const srcW = scene.render?.source_width_px ?? scene.coordinate_system?.render?.source_width_px;
    const srcH = scene.render?.source_height_px ?? scene.coordinate_system?.render?.source_height_px;
    overlayStage.setBackground(scene?.visual?.background_url ?? null, srcW, srcH);
    this.sim = new Simulation(overlayStage.getContainer());
    this.sim.loadScene(scene, overlayStage.getMapper());
    overlayStage.onMapperChanged((mapper) => {
      this.sim.loadScene(this.scene, mapper);
    });
    this._bindControls(scene);
    this._showPanel();
  }

  _bindControls(scene) {
    const sim = this.sim;
    document.getElementById('play-button')?.addEventListener('click',  () => sim.play());
    document.getElementById('pause-button')?.addEventListener('click', () => sim.pause());
    document.getElementById('reset-button')?.addEventListener('click', () => sim.reset());
    document.getElementById('toggle-colliders')?.addEventListener('change',
      e => sim.setWireframes(e.target.checked));

    const gs = document.getElementById('gravity-slider');
    const gv = document.getElementById('gravity-value');
    gs?.addEventListener('input', () => { sim.setGravity(gs.value); if(gv) gv.textContent = gs.value; });

    const ss = document.getElementById('speed-slider');
    const sv = document.getElementById('speed-value');
    ss?.addEventListener('input', () => { sim.setSpeed(ss.value); if(sv) sv.textContent = ss.value + 'x'; });

    const dynObjs = (scene.objects||[]).filter(o => o.role === 'dynamic' || o.type === 'pendulum');
    const sel = document.getElementById('target-object-select');
    if (sel) {
      sel.innerHTML = '';
      dynObjs.forEach((o, i) => {
        const opt = document.createElement('option');
        opt.value = o.id; opt.textContent = o.id + ' (' + o.type + ')';
        if (i === 0) opt.selected = true;
        sel.appendChild(opt);
      });
    }

    // NCTB Kinematics Diagram Scenario Switcher
    const mSelect = document.getElementById('mechanics-scene-select');
    if (mSelect) {
      const isCradle = (scene.objects || []).some(o => o.id?.includes('cradle'));
      mSelect.value = isCradle ? 'newtons_cradle' : 'with_spring';
      mSelect.onchange = async (e) => {
        const url = e.target.value === 'newtons_cradle'
          ? '/scenes/kinematics/newtons_cradle_scene.json'
          : '/scenes/kinematics/physics_scene.json';
        const res = await fetch(url);
        const data = await res.json();
        this.loadNewScene(data);
      };
    }

    const vs = document.getElementById('velocity-slider');
    const vv = document.getElementById('velocity-value');
    vs?.addEventListener('input', () => { if(vv) vv.textContent = vs.value + ' m/s'; });
    document.getElementById('apply-velocity-button')?.addEventListener('click', () => {
      const id = sel?.value || dynObjs[0]?.id;
      if (id) sim.setObjectVelocity(id, vs?.value ?? 0);
    });
  }

  loadNewScene(newScene) {
    this.scene = newScene;
    const srcW = newScene.render?.source_width_px ?? newScene.coordinate_system?.render?.source_width_px ?? 800;
    const srcH = newScene.render?.source_height_px ?? newScene.coordinate_system?.render?.source_height_px ?? 600;
    this.overlayStage.setBackground(newScene?.visual?.background_url ?? null, srcW, srcH);
    this.sim.loadScene(newScene, this.overlayStage.getMapper());
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
    this.sim?.pause();
    const mc = document.getElementById('mechanics-controls');
    if (mc) mc.style.display = 'none';
  }
}

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
    overlayStage.setBackground(scene?.visual?.background_url ?? null);
    this.sim = new Simulation(overlayStage.getContainer());
    this.sim.loadScene(scene);
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

    const vs = document.getElementById('velocity-slider');
    const vv = document.getElementById('velocity-value');
    vs?.addEventListener('input', () => { if(vv) vv.textContent = vs.value + ' m/s'; });
    document.getElementById('apply-velocity-button')?.addEventListener('click', () => {
      const id = sel?.value || dynObjs[0]?.id;
      if (id) sim.setObjectVelocity(id, vs?.value ?? 0);
    });
  }

  _showPanel() {
    const mc = document.getElementById('mechanics-controls');
    const oc = document.getElementById('optics-controls');
    if (mc) mc.style.display = 'flex';
    if (oc) oc.style.display = 'none';
  }

  destroy() { this.sim?.pause(); }
}

/**
 * engine/circuits/CircuitAdapter.js
 * 
 * SimulationAdapter wrapping existing MNA circuit solver:
 * - CircuitCompiler (topology & branch graph)
 * - CircuitSolver (MNA Modified Nodal Analysis on Float64Array)
 * - CircuitStore (multi-layer reactive state manager)
 * - P5CircuitView (current particle flow & visual halos)
 */

import { SimulationAdapter } from '../core/SimulationAdapter.js';
import { CircuitCompiler } from './CircuitCompiler.js';
import { CircuitSolver } from './CircuitSolver.js';

export class CircuitAdapter extends SimulationAdapter {
  constructor() {
    super();
    this.model = null;
    this.solver = null;
    this.electricalState = null;
    this.store = null;
    this.view = null;
    this.subtype = 'series_parallel';
  }

  static canHandle(scene) {
    const domain = scene?.domain || scene?.simulation?.domain || scene?.simulation_type;
    return domain === 'circuits' || Boolean(scene?.circuit);
  }

  canHandle(scene) {
    return CircuitAdapter.canHandle(scene);
  }

  async initialize(scene, container, options = {}) {
    await super.initialize(scene, container, options);

    this.subtype = scene.type || scene.simulation?.subtype || 'series_parallel';

    // 1. Compile topology and initial solve using verified MNA engine
    this.model = CircuitCompiler.compile(scene);
    this.solver = new CircuitSolver(this.model);
    this.electricalState = this.solver.solveDC();

    // 2. Initialize CircuitStore if in browser or module environment
    try {
      const { CircuitStore } = await import('../../apps/web/src/features/simulations/circuits/CircuitStore.js');
      this.store = new CircuitStore(scene, this.model, this.electricalState);
      this.store.subscribe((type) => {
        if (type === 'SWITCH_TOGGLED') {
          this.model = CircuitCompiler.compile(this.scene);
          this.solver.load(this.model);
          this.store.model = this.model;
          this.solve();
          this.notifyStateChange(this.getState());
        }
      });
    } catch (err) {
      console.warn('[CircuitAdapter] CircuitStore loaded in fallback mode:', err);
    }

    // 3. Mount P5CircuitView if container and browser window are available
    if (typeof window !== 'undefined' && container && this.store) {
      try {
        const { P5CircuitView } = await import('../../apps/web/src/features/simulations/circuits/view/P5CircuitView.js');
        const { CoordinateMapper } = await import('../core/coordinateMapper.js');

        const sw = scene.coordinateSystem?.width || scene.source?.width || 800;
        const sh = scene.coordinateSystem?.height || scene.source?.height || 600;
        const cw = container.clientWidth || 800;
        const ch = container.clientHeight || 600;
        const mapper = new CoordinateMapper(sw, sh, cw, ch);

        this.view = new P5CircuitView(container, this.store, mapper);
      } catch (err) {
        console.warn('[CircuitAdapter] Could not mount P5CircuitView:', err);
      }
    }

    this.notifyStateChange(this.getState());
  }

  solve() {
    if (!this.solver) return;
    this.electricalState = this.solver.solveDC();
    if (this.store) {
      this.store.electricalState = this.electricalState;
      this.store.notify('SOLVE_COMPLETED', { state: this.electricalState });
    }
  }

  play() {
    super.play();
    if (this.store) {
      this.store.uiState.animationEnabled = true;
      this.store.notify('ANIMATION_TOGGLED', { enabled: true });
    }
    this.notifyStateChange(this.getState());
  }

  pause() {
    super.pause();
    if (this.store) {
      this.store.uiState.animationEnabled = false;
      this.store.notify('ANIMATION_TOGGLED', { enabled: false });
    }
    this.notifyStateChange(this.getState());
  }

  reset() {
    super.reset();
    if (this.store) {
      this.store.resetToTextbook();
      this.solve();
    }
    this.notifyStateChange(this.getState());
  }

  setParameter(name, value) {
    super.setParameter(name, value);
    const numVal = Number(value);

    // Try matching component ID directly (e.g. "R1", "V1", "R2")
    const comp = this.model?.componentById?.get(name);
    if (comp) {
      if (this.store) {
        this.store.setParameter(name, 'value', numVal);
      } else {
        comp.value = numVal;
      }
      this.solve();
    } else {
      // Check if parameter has an associated component in scene
      const sceneComp = this.scene?.circuit?.components?.find(c => c.id === name || c.label === name);
      if (sceneComp) {
        sceneComp.value = numVal;
        this.model = CircuitCompiler.compile(this.scene);
        this.solver.load(this.model);
        this.solve();
      }
    }

    this.notifyStateChange(this.getState());
  }

  getState() {
    const nodeV = {};
    if (this.electricalState?.nodeVoltages) {
      for (const [k, v] of Object.entries(this.electricalState.nodeVoltages)) {
        nodeV[k] = Number(Number(v).toFixed(2));
      }
    }

    const branchI = {};
    if (this.electricalState?.componentCurrents) {
      for (const [k, v] of Object.entries(this.electricalState.componentCurrents)) {
        const valMA = Number((Number(v) * 1000.0).toFixed(2)); // in mA for readability
        branchI[k] = valMA;
        branchI[`${k}.branch`] = valMA;
      }
    }

    const comps = Array.from(this.model?.componentById?.values() || []).map(c => ({
      id: c.id,
      type: c.type,
      value: c.value,
      unit: c.unit
    }));

    return {
      domain: 'circuits',
      type: this.subtype,
      running: Boolean(this.store ? this.store.uiState.animationEnabled : this.running),
      totalPower: Number((this.electricalState?.totalPower || 0).toFixed(2)),
      nodeVoltages: nodeV,
      branchCurrents: branchI,
      componentVoltages: this.electricalState?.componentVoltages || {},
      components: comps
    };
  }


  resize(width, height, renderContext = null) {
    this.view?.resize?.(width, height, renderContext);
  }

  destroy() {
    this.view?.destroy?.();
    this.view = null;
    this.store = null;
    this.solver = null;
    this.model = null;
    this.electricalState = null;
    super.destroy();
  }
}

/**
 * engine/circuits/CircuitAdapter.js
 * 
 * Pure mathematical simulation adapter for the electrical circuits domain:
 * - CircuitCompiler (topology and branch indexing)
 * - CircuitSolver (64-bit Modified Nodal Analysis matrix engine)
 * Completely decoupled from frontend stores and view renderers.
 */

import { SimulationAdapter } from '../core/SimulationAdapter.js';
import { CircuitCompiler } from './CircuitCompiler.js';
import { CircuitSolver } from './CircuitSolver.js';
import { UnsupportedPhysicsSubtypeError, PhysicsSceneValidationError } from '../core/errors.js';

export class CircuitAdapter extends SimulationAdapter {
  static domain = 'circuits';

  constructor() {
    super();
    this.subtype = 'dc';
    this.model = null;
    this.solver = null;
    this.electricalState = null;
  }

  static canHandle(scene) {
    const domain = scene?.domain;
    return domain === 'circuits' || Boolean(scene?.circuit);
  }

  canHandle(scene) {
    return CircuitAdapter.canHandle(scene);
  }

  async initialize(scene, container = null, options = {}) {
    await super.initialize(scene, container, options);
    if (!scene.subtype) {
      throw new PhysicsSceneValidationError([{
        code: 'MISSING_SUBTYPE',
        path: 'subtype',
        message: 'Circuit scene must explicitly declare a canonical subtype (e.g. "dc").'
      }]);
    }
    this.subtype = scene.subtype;

    if (this.subtype !== 'dc' && this.subtype !== 'dc_linear') {
      throw new UnsupportedPhysicsSubtypeError('circuits', this.subtype);
    }

    if (!scene.circuit) {
      throw new PhysicsSceneValidationError([{
        code: 'MISSING_CIRCUIT_DEFINITION',
        path: 'circuit',
        message: 'Circuits adapter requires an explicit circuit graph definition.'
      }]);
    }

    // 1. Compile topology and initial solve using verified MNA engine
    this.model = CircuitCompiler.compile(scene);
    this.solver = new CircuitSolver(this.model);
    this.solve();

    this.notifyStateChange(this.getState());
  }

  solve() {
    if (!this.solver) return;
    this.electricalState = this.solver.solveDC();
  }

  /**
   * Internal hook called by SimulationAdapter after atomic validation, unit conversion,
   * and scene mutation succeed.
   */
  _applyParameterUpdate(address, convertedVal, key, targetId, incomingUnit) {
    this.model = CircuitCompiler.compile(this.scene);
    this.solver.load(this.model);
    this.solve();
    this.notifyStateChange(this.getState());
  }

  reset() {
    super.reset();
    this.solve();
    this.notifyStateChange(this.getState());
  }

  getOutput() {
    const state = this.getState();
    return {
      domain: 'circuits',
      subtype: this.subtype,
      time: 0.0,
      state,
      geometry: {
        nodeVoltages: state.nodeVoltages,
        branchCurrents: state.branchCurrents
      },
      telemetry: state,
      events: [],
      editableParameters: this.getParameters()
    };
  }

  getState() {
    const es = this.electricalState || {};
    const nodeVoltages = es.nodeVoltages || {};
    const branchCurrents = es.componentCurrents || es.branchCurrents || {};
    const branchPowers = es.branchPowers || es.componentPower || {};

    let totalPower = es.totalPower !== undefined ? es.totalPower : 0.0;
    if (totalPower === 0.0 && branchPowers) {
      for (const p of Object.values(branchPowers)) {
        if (p > 0) totalPower += p;
      }
    }

    return {
      domain: 'circuits',
      subtype: this.subtype,
      running: this.running,
      nodeVoltages,
      branchCurrents,
      branchPowers,
      totalPower: Number(totalPower.toFixed(4))
    };
  }

  dispose() {
    this.model = null;
    this.solver = null;
    this.electricalState = null;
    super.dispose();
  }
}

/**
 * circuits/ProbeManager.js
 * Manages virtual instruments: Voltmeter probes, Ammeter probes,
 * KCL junction inspection, and KVL loop walks.
 */

import { KCLInspector } from './KCLInspector.js';
import { KVLInspector } from './KVLInspector.js';

export class ProbeManager {
  /**
   * @param {object} store - CircuitStore instance
   */
  constructor(store) {
    this.store = store;
  }

  /**
   * Handle click in 'voltage-probe' mode.
   * Alternates between Red lead (+) and Black lead (-).
   * @param {object} hit - Hit result from CircuitHitTest
   */
  handleVoltageProbeClick(hit) {
    const nodeId = hit?.nodeId || hit?.terminal?.node;
    if (!nodeId) return null;

    const probe = this.store.uiState.voltageProbe;

    if (!probe.leadRed || (probe.leadRed && probe.leadBlack)) {
      // Set Red lead (+)
      probe.active = true;
      probe.leadRed = {
        nodeId,
        x: hit.sourcePoint?.x || 0,
        y: hit.sourcePoint?.y || 0
      };
      probe.leadBlack = null;
      probe.reading = null;
      this.store.notify('PROBE_UPDATED', { type: 'voltage', status: 'set_red', nodeId });
      return { step: 'need_black', nodeId };
    } else {
      // Set Black lead (-)
      probe.leadBlack = {
        nodeId,
        x: hit.sourcePoint?.x || 0,
        y: hit.sourcePoint?.y || 0
      };

      // Calculate potential difference V_AB = V_red - V_black
      const state = this.store.electricalState;
      const vRed = state?.nodeVoltages?.[probe.leadRed.nodeId] ?? 0.0;
      const vBlack = state?.nodeVoltages?.[probe.leadBlack.nodeId] ?? 0.0;
      probe.reading = vRed - vBlack;

      this.store.notify('PROBE_UPDATED', {
        type: 'voltage',
        status: 'measured',
        reading: probe.reading,
        redNode: probe.leadRed.nodeId,
        blackNode: probe.leadBlack.nodeId
      });

      return {
        step: 'complete',
        reading: probe.reading,
        vRed,
        vBlack,
        label: `V(${probe.leadRed.nodeId}, ${probe.leadBlack.nodeId}) = ${probe.reading >= 0 ? '+' : ''}${probe.reading.toFixed(2)} V`
      };
    }
  }

  /**
   * Handle click in 'current-probe' mode.
   * Directly measures branch current through the clicked component or wire.
   */
  handleCurrentProbeClick(hit) {
    const compId = hit?.componentId || (hit?.type === 'component' ? hit.id : null);
    if (!compId) return null;

    const state = this.store.electricalState;
    const current = state?.componentCurrents?.[compId] ?? 0.0;
    const comp = this.store.model.componentById.get(compId);

    this.store.uiState.currentProbe = {
      active: true,
      targetBranch: compId,
      reading: current
    };

    this.store.notify('PROBE_UPDATED', {
      type: 'current',
      status: 'measured',
      componentId: compId,
      reading: current
    });

    return {
      componentId: compId,
      reading: current,
      label: `I(${comp?.label || compId}) = ${(Math.abs(current) * 1000).toFixed(1)} mA`
    };
  }

  /**
   * Handle click in 'kcl' mode.
   * Derives \sum I_in = \sum I_out at clicked junction.
   */
  handleKCLClick(hit) {
    const nodeId = hit?.nodeId || hit?.terminal?.node;
    if (!nodeId) return null;

    const res = KCLInspector.inspectNode(nodeId, this.store.model, this.store.electricalState);
    if (res) {
      this.store.uiState.kclResult = res;
      this.store.notify('KCL_INSPECTED', res);
    }
    return res;
  }

  /**
   * Handle activation of 'kvl' mode.
   * Traces closed loop voltage drops \sum V = 0.
   */
  handleKVLTrace() {
    const res = KVLInspector.traceLoop(this.store.model, this.store.electricalState);
    if (res) {
      this.store.uiState.kvlResult = res;
      this.store.notify('KVL_TRACED', res);
    }
    return res;
  }

  /**
   * Clear active probes and law inspectors.
   */
  clearProbes() {
    this.store.uiState.voltageProbe = { active: false, leadRed: null, leadBlack: null, reading: null };
    this.store.uiState.currentProbe = { active: false, targetBranch: null, reading: null };
    this.store.uiState.kclResult = null;
    this.store.uiState.kvlResult = null;
    this.store.notify('PROBE_UPDATED', { type: 'cleared' });
  }
}

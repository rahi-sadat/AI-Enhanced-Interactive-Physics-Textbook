/**
 * circuits/KCLInspector.js
 * Interactive inspector for Kirchhoff's Current Law (KCL).
 * When the student clicks any node/junction:
 * - Identifies all branches and components incident on that node
 * - Computes signed incoming vs. outgoing currents
 * - Verifies \sum I_in = \sum I_out (\sum I = 0)
 * - Returns structured data for visual overlay and tutor explanations
 */

export class KCLInspector {
  /**
   * Inspect a junction node for KCL compliance.
   * @param {string} nodeId - Target node ID (e.g. 'N1', 'N2', 'N0')
   * @param {object} model - Compiled CircuitModel
   * @param {object} state - Solved ElectricalState
   * @returns {object} KCL verification result
   */
  static inspectNode(nodeId, model, state) {
    if (!nodeId || !model || !state || !state.success) {
      return null;
    }

    const connectedBranches = [];
    let sumCurrents = 0.0;
    const incoming = [];
    const outgoing = [];

    // Check all components connected to this node
    for (const [cId, comp] of model.componentById.entries()) {
      const nodes = comp.nodes || [];
      const nodeIndexInComp = nodes.indexOf(nodeId);
      if (nodeIndexInComp === -1) continue;

      const iBranch = state.componentCurrents?.[cId] ?? 0.0;
      let currentEnteringNode = 0.0;

      if (comp.type === 'voltage_source' || comp.type === 'battery') {
        // Current flows through source from neg terminal to pos terminal
        // If this node is positive terminal (index 0), current is leaving source into node
        currentEnteringNode = (nodeIndexInComp === 0) ? -iBranch : iBranch;
      } else if (comp.type === 'resistor' || comp.type === 'bulb') {
        // In resistor, current flows from higher potential to lower potential
        // If node is at index 0, current leaves node if V(n0) > V(n1)
        currentEnteringNode = (nodeIndexInComp === 0) ? -iBranch : iBranch;
      } else if (comp.type === 'switch') {
        currentEnteringNode = (nodeIndexInComp === 0) ? -iBranch : iBranch;
      }

      sumCurrents += currentEnteringNode;

      const branchInfo = {
        componentId: cId,
        label: comp.label || cId,
        current: Math.abs(iBranch),
        signedCurrent: currentEnteringNode,
        direction: currentEnteringNode >= 0 ? 'incoming' : 'outgoing'
      };

      connectedBranches.push(branchInfo);

      if (currentEnteringNode >= 0) {
        incoming.push(branchInfo);
      } else {
        outgoing.push(branchInfo);
      }
    }

    const sumIn = incoming.reduce((acc, b) => acc + b.current, 0);
    const sumOut = outgoing.reduce((acc, b) => acc + b.current, 0);
    const residual = Math.abs(sumIn - sumOut);
    const isSatisfied = residual < 1e-5;

    return {
      nodeId,
      nodeLabel: model.nodeLabels?.get(nodeId) || nodeId,
      connectedBranches,
      incoming,
      outgoing,
      sumIn,
      sumOut,
      residual,
      isSatisfied,
      formula: `\\sum I_{\\text{in}} = \\sum I_{\\text{out}}`,
      derivation: `${incoming.map(b => `${(b.current * 1000).toFixed(1)} mA`).join(' + ') || '0 mA'} = ${outgoing.map(b => `${(b.current * 1000).toFixed(1)} mA`).join(' + ') || '0 mA'}`,
      banglaExplanation: isSatisfied
        ? `নোড <strong>${nodeId}</strong>-এ কার্শফের তড়িৎ প্রবাহ সূত্র (KCL) প্রমাণিত: মোট প্রবেশরত প্রবাহ (${(sumIn * 1000).toFixed(1)} mA) = মোট নির্গত প্রবাহ (${(sumOut * 1000).toFixed(1)} mA)।`
        : `নোড ${nodeId}-এ KCL ব্যত্যয়: অবশিষ্ট কারেন্ট ${residual.toExponential(2)} A।`
    };
  }
}

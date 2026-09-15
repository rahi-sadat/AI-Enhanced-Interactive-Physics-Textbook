/**
 * circuits/KVLInspector.js
 * Interactive inspector for Kirchhoff's Voltage Law (KVL).
 * Traces closed electrical loops, computes directed voltage rises and drops,
 * verifies \sum V = 0, and returns structured derivations.
 */

export class KVLInspector {
  /**
   * Trace the primary closed loop of the circuit.
   * @param {object} model - Compiled CircuitModel
   * @param {object} state - Solved ElectricalState
   * @returns {object} KVL verification result
   */
  static traceLoop(model, state) {
    if (!model || !state || !state.success) return null;

    const vs = model.voltageSources?.[0];
    const resistors = model.resistors || [];
    if (!vs || resistors.length === 0) return null;

    const sourceV = Number(vs.value ?? 12.0);
    const elements = [];
    let loopSum = 0.0;

    // 1. Source Voltage Rise: +V
    elements.push({
      id: vs.id,
      label: vs.label || vs.id,
      type: 'source_rise',
      voltage: sourceV,
      sign: '+',
      description: `ব্যাটারি বিভব যোগান (Voltage Rise)`
    });
    loopSum += sourceV;

    // 2. Resistor Voltage Drops: -V_R
    for (const r of resistors) {
      const drop = state.componentVoltages?.[r.id] ?? 0.0;
      elements.push({
        id: r.id,
        label: r.label || r.id,
        type: 'resistor_drop',
        voltage: Math.abs(drop),
        sign: '-',
        description: `রোধক বিভব পতন (Voltage Drop)`
      });
      loopSum -= Math.abs(drop);
    }

    const residual = Math.abs(loopSum);
    const isSatisfied = residual < 1e-4;

    const terms = elements.map(el => `${el.sign} ${el.voltage.toFixed(2)} V`).join(' ');

    return {
      loopName: 'Primary Series Loop (V₁ → R₁ → R₂ → V₁)',
      elements,
      sourceV,
      residual,
      isSatisfied,
      formula: `\\sum_{loop} V = 0`,
      derivation: `${terms} = ${loopSum.toFixed(3)} V`,
      banglaExplanation: isSatisfied
        ? `আবদ্ধ লুপে কার্শফের ভোল্টেজ সূত্র (KVL) প্রমাণিত: মোট সরবরাহকৃত বিভব (${sourceV.toFixed(2)} V) সমান সকল রোধকের বিভব পতনের যোগফল (${elements.filter(e => e.sign === '-').map(e => e.voltage.toFixed(2) + 'V').join(' + ')}), অর্থাৎ বীজগাণিতিক যোগফল শূন্য।`
        : `লুপে KVL ব্যত্যয়: অবশিষ্ট বিভব ${residual.toFixed(4)} V।`
    };
  }
}

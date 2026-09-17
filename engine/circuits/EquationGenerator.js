/**
 * circuits/EquationGenerator.js
 * Generates deterministic mathematical derivations and step-by-step physical equations
 * directly from solver facts (never hallucinated by AI).
 */

export class EquationGenerator {
  /**
   * Generate complete step-by-step derivation for the current circuit state.
   * @param {object} model - Compiled CircuitModel
   * @param {object} state - Solved ElectricalState
   * @returns {object} Structured derivation steps
   */
  static generateDerivations(model, state) {
    if (!state || !state.success) {
      return {
        summary: 'Circuit is open or unpowered. Current is 0 A.',
        steps: []
      };
    }

    const steps = [];
    const resistors = model.resistors || [];
    const vs = model.voltageSources?.[0];
    const sourceV = vs ? Number(vs.value ?? 12.0) : 12.0;
    const current = state.primaryCurrent ?? 0.0;
    const req = state.equivalentResistance ?? 0.0;

    // 1. Equivalent Resistance Derivation
    if (resistors.length >= 2 && isFinite(req) && req > 0) {
      const rValues = resistors.map(r => Number(r.value ?? 10.0));
      const rNames = resistors.map(r => r.label || r.id);
      const isSimpleSeries = model.switches.every(sw => sw.state !== 'open');

      if (isSimpleSeries) {
        steps.push({
          title: '1. সমতুল্য রোধ নির্ণয় (Equivalent Resistance in Series)',
          formula: 'R_{eq} = ' + rNames.join(' + '),
          substitution: `R_{eq} = ` + rValues.map(v => `${v} Ω`).join(' + '),
          result: `R_{eq} = ${req.toFixed(1)} Ω`,
          explanation: `অনুক্রমিক বর্তনীতে সকল রোধকের মান সরাসরি যোগ করে সমতুল্য রোধ নির্ণয় করা হয়।`
        });
      }
    }

    // 2. Total Circuit Current (Ohm's Law)
    if (sourceV > 0 && req > 0 && isFinite(req)) {
      steps.push({
        title: "2. মূল তড়িৎ প্রবাহ নির্ণয় (Total Circuit Current via Ohm's Law)",
        formula: 'I = \\frac{V}{R_{eq}}',
        substitution: `I = \\frac{${sourceV.toFixed(1)} \\text{ V}}{${req.toFixed(1)} \\, \\Omega}`,
        result: `I = ${current.toFixed(3)} A (${(current * 1000).toFixed(1)} mA)`,
        explanation: `ওহমের সূত্রানুসারে, বর্তনীর মোট বিভব পার্থক্যকে সমতুল্য রোধ দ্বারা ভাগ করলে মোট প্রবাহ পাওয়া যায়।`
      });
    }

    // 3. Voltage Drops across individual resistors
    for (const r of resistors) {
      const vDrop = state.componentVoltages?.[r.id] ?? 0.0;
      const iR = state.componentCurrents?.[r.id] ?? current;
      const rVal = Number(r.value ?? 10.0);
      const pR = state.componentPower?.[r.id] ?? (vDrop * iR);

      steps.push({
        title: `3. ${r.label || r.id}-এর প্রান্তীয় বিভব পার্থক্য ও ক্ষমতা (Potential Drop & Power)`,
        formula: `V_{${r.id}} = I \\cdot ${r.id}, \\quad P_{${r.id}} = V_{${r.id}} \\cdot I`,
        substitution: `V_{${r.id}} = ${iR.toFixed(3)} \\text{ A} \\times ${rVal.toFixed(1)} \\, \\Omega = ${vDrop.toFixed(2)} \\text{ V}`,
        result: `V = ${vDrop.toFixed(2)} V, \\quad P = ${pR.toFixed(2)} W`,
        explanation: `রোধকটির মধ্য দিয়ে প্রবাহিত তড়িৎ এবং তার রোধের গুণফলই হলো এর বিভব পতন।`
      });
    }

    // 4. Kirchhoff's Voltage Law (KVL) Verification
    if (resistors.length > 0 && sourceV > 0) {
      const vDrops = resistors.map(r => state.componentVoltages?.[r.id] ?? 0.0);
      const sumDrops = vDrops.reduce((a, b) => a + b, 0);
      const residual = Math.abs(sourceV - sumDrops);

      steps.push({
        title: "4. কার্শফের ভোল্টেজ সূত্রের প্রমাণ (KVL Closed-Loop Walk)",
        formula: '\\sum V = V_{source} - (V_{R1} + V_{R2} + \\dots) = 0',
        substitution: `${sourceV.toFixed(2)} \\text{ V} - (${vDrops.map(v => v.toFixed(2) + ' V').join(' + ')}) = ${(sourceV - sumDrops).toFixed(3)} \\text{ V}`,
        result: residual < 1e-4 ? '✓ KVL Loop Satisfied (∑V = 0)' : 'KVL Residual: ' + residual.toFixed(4) + ' V',
        explanation: `একটি আবদ্ধ লুপে সরবরাহকৃত মোট বিভব এবং সকল উপাদানের বিভব পতনের বীজগাণিতিক যোগফল শূন্য।`
      });
    }

    return {
      summary: `I = ${current.toFixed(3)} A, R_{eq} = ${req.toFixed(1)} Ω, P_{tot} = ${(state.totalPower ?? 0).toFixed(2)} W`,
      steps
    };
  }
}

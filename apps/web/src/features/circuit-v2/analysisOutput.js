// Transport backend solutions to the existing renderer without re-solving or
// borrowing a neighbouring component's current for an unmeasured wire.
export function analysisOutput(analysis) {
  const solved = ['IDEAL_SOLVED', 'NON_IDEAL_SOLVED'].includes(analysis.status)
    && analysis.validation?.valid === true && analysis.electrical_state;
  const graph = analysis.graph || { wires: [], components: [] };
  return {
    geometry: {
      wires: (graph.wires || []).map(w => {
        const value = solved ? analysis.wire_currents_a?.[w.id] : null;
        const current = Number.isFinite(value) ? value : null;
        return { ...structuredClone(w), current_A: current,
          direction: current === null || current === 0 ? 'none' : current < 0 ? 'backward' : 'forward',
          fault: w.id === analysis.fault_path_id,
          shortRoute: (analysis.short_path_wire_ids || []).includes(w.id) };
      }),
      components: structuredClone(graph.components || []), nodes: [], switches: [],
    },
    telemetry: solved ? structuredClone(analysis.electrical_state) : null,
  };
}

export function faultInputs(internalText, pathText) {
  const number = text => text.trim() === '' ? null : Number(text);
  const internal = number(internalText), path = number(pathText);
  if ((internal !== null && (!Number.isFinite(internal) || internal < 0))
      || (path !== null && (!Number.isFinite(path) || path <= 0))) {
    throw new Error('Source internal resistance must be ≥ 0 Ω; short-path resistance must be > 0 Ω.');
  }
  return {source_internal_resistance_ohm: internal, short_path_resistance_ohm: path};
}

export function parseAnalysisResponse(text, status) {
  try { return JSON.parse(text); }
  catch { throw new Error(`API connection failed (HTTP ${status}). The backend may be offline or restarting. Retry the upload.`); }
}

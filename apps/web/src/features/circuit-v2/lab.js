import { GroundedCircuitView } from './GroundedCircuitView.js';
import { faultInputs, parseAnalysisResponse } from './analysisOutput.js';
import './lab.css';

document.querySelector('#lab').innerHTML = `
  <header><a href="/">← Textbook studio</a><h1>Circuit v2 laboratory</h1>
  <p>Analyze the uploaded circuit with local detection, OCR and measured conductor paths.</p></header>
  <form id="upload"><input id="image" type="file" accept="image/*" required><button>Analyze image</button></form>
  <p id="status" role="status">Choose a circuit image. Inference runs locally.</p>
  <div id="controls" hidden>
    <label>Analysis mode <select id="mode"><option value="ideal">Ideal circuit analysis</option>
      <option value="qualitative">Qualitative fault visualization</option>
      <option value="non_ideal">Non-ideal numerical fault simulation</option></select></label>
    <fieldset id="assumptions" hidden><legend>User assumptions for the fault model</legend>
      <label>Source internal resistance (Ω) <input id="internal" type="number" min="0" step="any" placeholder="Explicit value required"></label>
      <label>Short-path resistance (Ω) <input id="path-resistance" type="number" min="0" step="any" placeholder="Explicit positive value required"></label>
      <label>Measured fault path <select id="fault-path"></select></label>
      <p>Both resistance values are user assumptions. Textbook measurements stay unchanged.</p>
    </fieldset>
    <button id="recalculate" type="button">Analyze selected mode</button>
    <button id="playback" type="button">Pause indicators</button>
    <p>Conventional-current direction and magnitude come from the solver. Animation speed uses a visual scale, not charge-drift velocity.</p>
  </div>
  <p id="warning" hidden></p><div id="figure"></div>
  <section id="measurements" hidden><h2>Textbook measurements</h2><div id="values"></div></section>
  <form id="correction" hidden><h2>Correct a verified component value</h2>
    <select id="correct-component" aria-label="Component to correct"></select>
    <input id="correct-value" type="number" step="any" required aria-label="Corrected value">
    <span id="correct-unit"></span><button>Apply explicit correction</button>
    <p>Original OCR and geometry stay in the evidence. Missing symbols or wires require a clearer complete upload.</p>
  </form>
  <section id="telemetry" hidden><h2>Numerical solution</h2><p id="validation"></p><div id="readings"></div></section>
  <section id="diagnostics" hidden><h2>Pipeline diagnostics</h2><p id="model"></p><ol id="stages"></ol>
    <button id="download">Download full diagnostics</button>
    <details><summary>Detections and evidence</summary><pre id="raw"></pre></details>
  </section>`;
const el = id => document.getElementById(id);
let view, response, currentAnalysis, sequence = 0;

function table(host, headers, rows) {
  host.replaceChildren();
  const result = document.createElement('table'), head = result.createTHead().insertRow();
  for (const title of headers) { const cell = document.createElement('th'); cell.textContent = title; head.append(cell); }
  const body = result.createTBody();
  for (const row of rows) { const tr = body.insertRow(); for (const value of row) tr.insertCell().textContent = value; }
  host.append(result);
}

function show(analysis) {
  currentAnalysis = analysis;
  view.show(analysis);
  el('status').textContent = analysis.status;
  const explanation = analysis.error || analysis.explanation;
  el('warning').hidden = !explanation;
  el('warning').textContent = explanation || '';
  const state = ['IDEAL_SOLVED','NON_IDEAL_SOLVED'].includes(analysis.status) && analysis.validation?.valid
    ? analysis.electrical_state : null;
  el('telemetry').hidden = !state;
  el('readings').replaceChildren();
  if (state) {
    const labels = Object.fromEntries((analysis.graph?.components || []).map(c => [c.id,c.label || c.id]));
    table(el('readings'), ['Branch','Voltage (V)','Signed current (A)','Power magnitude (W)'],
      Object.entries(state.components).map(([id,s]) => [labels[id] || id,s.voltage_v,s.current_a,s.power_w]));
    const v = analysis.validation;
    el('validation').textContent = `Validated MNA · KCL residual ${v.kcl_residual_a.toExponential(2)} A · `
      + `KVL residual ${v.kvl_constitutive_residual_v.toExponential(2)} V · Power balance ${v.power_balance_w.toExponential(2)} W`;
  }
  el('raw').textContent = JSON.stringify(response, null, 2);
}

async function recalculate() {
  if (!response?.analysis_id) return;
  const requestNumber = ++sequence, originalResponse = response, mode = el('mode').value;
  el('assumptions').hidden = mode !== 'non_ideal';
  const waiting = {...currentAnalysis, status:'ANALYZING', electrical_state:null, validation:null};
  show(waiting);
  try {
    const inputs = mode === 'non_ideal' ? faultInputs(el('internal').value, el('path-resistance').value) : {};
    const http = await fetch('/api/experiments/circuit-v2/analysis', {method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({analysis_id:response.analysis_id,mode,fault_path_id:el('fault-path').value || null,...inputs})});
    const analysis = parseAnalysisResponse(await http.text(),http.status);
    if (requestNumber !== sequence || originalResponse !== response) return;
    if (!http.ok) throw new Error(typeof analysis.detail === 'string' ? analysis.detail : JSON.stringify(analysis.detail));
    (response.analysis_history ||= []).push(analysis);
    show(analysis);
  } catch (error) {
    if (requestNumber === sequence) show({...waiting,status:'INVALID_PARAMETERS',error:error.message});
  }
}

el('upload').addEventListener('submit', async event => {
  event.preventDefault();
  const file = el('image').files[0];
  if (!file) return;
  ++sequence;
  const button = event.submitter;
  button.disabled = true;
  el('status').textContent = 'Detecting components → OCR/CV → SAM2 → validating circuit…';
  for (const id of ['diagnostics','controls','measurements','correction','telemetry','warning']) el(id).hidden = true;
  view?.destroy(); view = null; response = null;
  el('figure').replaceChildren();
  try {
    const form = new FormData(); form.append('file',file);
    const http = await fetch('/api/experiments/circuit-v2',{method:'POST',body:form});
    const result = parseAnalysisResponse(await http.text(),http.status);
    if (!http.ok) throw new Error(typeof result.detail === 'string' ? result.detail : JSON.stringify(result.detail));
    response = result;
    view = new GroundedCircuitView(el('figure'),response);
    el('diagnostics').hidden = false;
    el('controls').hidden = !response.analysis_id;
    el('model').textContent = `${response.model?.checkpoint || 'Checkpoint unavailable'} | SHA-256: ${response.model?.sha256 || 'unavailable'}`;
    el('stages').replaceChildren();
    for (const stage of response.stages) {
      const row = document.createElement('li'); row.className = stage.status;
      row.textContent = `${stage.stage}: ${stage.status} (${stage.duration_ms} ms) ${stage.message || ''} `
        + (stage.issues || []).map(i => `${i.code}: ${i.message}`).join('; ');
      el('stages').append(row);
    }
    const components = response.book_ir?.parameters?.components || [];
    el('measurements').hidden = !components.length;
    table(el('values'),['Component','Value','Unit','Evidence'],components.map(c =>
      [c.label || c.id,c.value ?? 'Needs review',c.unit || '',c.value_provenance?.source || 'No accepted value']));
    el('correct-component').replaceChildren();
    for (const c of components.filter(c=>c.verification_status==='VERIFIED' && c.type!=='switch'))
      el('correct-component').add(new Option(c.label || c.id,c.id));
    el('correction').hidden=!el('correct-component').options.length;
    updateCorrectionUnit();
    const paths = response.fault_analysis?.fault_paths || [];
    el('fault-path').replaceChildren(new Option('Select a measured conductor',''));
    for (const path of paths) el('fault-path').add(new Option(path.id,path.id));
    el('fault-path').value = response.fault_analysis?.fault_path_id || '';
    el('internal').value = ''; el('path-resistance').value = '';
    el('mode').value = 'ideal'; el('assumptions').hidden = true;
    show(response.ideal_analysis || {status:'NEEDS_REVIEW',error:response.first_blocker?.message});
  } catch (error) { el('status').textContent = error.message; }
  finally { button.disabled = false; }
});
el('mode').addEventListener('change',recalculate);
function updateCorrectionUnit() {
  const c=response?.book_ir?.parameters?.components?.find(c=>c.id===el('correct-component').value);
  el('correct-unit').textContent=c?.unit || ({resistor:'ohm',voltage_source:'V',capacitor:'F'}[c?.type] || '');
}
el('correct-component').addEventListener('change',updateCorrectionUnit);
el('correction').addEventListener('submit',async event=>{
  event.preventDefault();const n=++sequence,original=response;
  try {
    const value=Number(el('correct-value').value);
    if (!el('correct-value').value.trim() || !Number.isFinite(value)) throw new Error('Enter a finite explicit value.');
    const http=await fetch('/api/experiments/circuit-v2/correct-value',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({analysis_id:response.analysis_id,component_id:el('correct-component').value,value,unit:el('correct-unit').textContent})});
    const corrected=parseAnalysisResponse(await http.text(),http.status);
    if (!http.ok) throw new Error(typeof corrected.detail==='string'?corrected.detail:JSON.stringify(corrected.detail));
    if(n!==sequence || original!==response)return;
    response={...response,...corrected,correction_history:[...(response.correction_history || []),{parent_analysis_id:corrected.parent_analysis_id,book_ir:original.book_ir}]};
    view.destroy();view=new GroundedCircuitView(el('figure'),response);
    table(el('values'),['Component','Value','Unit','Evidence'],response.book_ir.parameters.components.map(c=>
      [c.label || c.id,c.value ?? 'Needs review',c.unit || '',c.value_provenance?.source || 'No accepted value']));
    el('mode').value='ideal';show(response.ideal_analysis);
  } catch(error) {if(n===sequence)show({...currentAnalysis,status:'NEEDS_REVIEW',electrical_state:null,error:error.message});}
});
el('recalculate').addEventListener('click',recalculate);
for (const id of ['internal','path-resistance','fault-path']) el(id).addEventListener('change',recalculate);
el('playback').addEventListener('click', () => { el('playback').textContent = view?.toggle() ? 'Pause indicators' : 'Play indicators'; });
el('download').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(response,null,2)],{type:'application/json'}));
  const link = document.createElement('a'); link.href=url; link.download='circuit-v2-diagnostics.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url),1000);
});

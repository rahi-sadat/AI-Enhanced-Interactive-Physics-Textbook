import { InteractiveFigure } from '../../components/InteractiveFigure.js';
import './lab.css';

document.querySelector('#lab').innerHTML = `
  <header><a href="/">← Textbook studio</a><h1>Circuit v2 experiment</h1>
  <p>Upload a diagram to run the trained local model through grounding, compilation and the existing physics engine.</p></header>
  <form id="upload"><input id="image" type="file" accept="image/*" required>
    <button>Run v2 model</button><label><input id="force" type="checkbox" checked> Play experimental preview if compilation is blocked</label></form>
  <p id="status" role="status">Choose a circuit image. All inference runs locally.</p>
  <p id="warning" hidden></p><div id="figure"></div>
  <section id="diagnostics" hidden><h2>Where did this run stop?</h2><p id="model"></p><ol id="stages"></ol>
    <button id="preview">Play guessed preview</button><button id="download">Download full diagnostics</button>
    <details><summary>Raw model detections and evidence</summary><pre id="raw"></pre></details>
  </section>`;
const el = id => document.getElementById(id);
let figure, response, animationFrame;

function animateFigure(previous = performance.now()) {
  animationFrame = requestAnimationFrame(now => {
    if (!figure) return;
    if (figure.runtime.getState().running) figure.runtime.step(Math.min((now-previous)/1000, .05));
    // CircuitAdapter has no clock of its own. Forward its actual state so the
    // existing view updates playback controls and capacitor telemetry too.
    figure.runtime.adapter?.notifyStateChange(figure.runtime.getState());
    animateFigure(now);
  });
}

function recordRuntime(status, message) {
  const row = document.createElement('li');
  row.className = status;
  row.textContent = `runtime / rendering: ${status} — ${message}`;
  el('stages').append(row);
  (response.runtime ||= []).push({status, message});
}

async function play(scene, experimental) {
  el('warning').hidden = !experimental;
  el('warning').textContent = 'EXPERIMENTAL — connections, terminals and values below are guessed. This preview may be wrong. Original evidence and compilation blockers are preserved below.';
  cancelAnimationFrame(animationFrame);
  figure?.destroy();
  figure = new InteractiveFigure(el('figure'));
  try {
    // Uploaded images are served by the API. Keep the same-origin Vite API proxy.
    scene = structuredClone(scene);
    scene.source ||= {};
    scene.source.image = response.image_url;
    await figure.load(scene);
    figure.play();
    animateFigure();
    const output = figure.runtime.getOutput();
    const state = figure.runtime.adapter?.electricalState || output?.telemetry || {};
    if (state.success === false || state.singular || state.status === 'singular' || state.status === 'unsolved' || state.error) {
      throw new Error(state.error || state.error_message || 'The circuit matrix could not be solved.');
    }
    recordRuntime('passed', experimental ? 'Experimental preview is playing.' : 'Compiled source circuit is playing.');
    el('status').textContent = experimental ? 'Playing an experimental guessed circuit. Inspect the blockers and assumptions.' : 'v2 circuit compiled and playback started.';
  } catch (error) {
    recordRuntime('failed', error.message);
    el('status').textContent = `Runtime / rendering stopped: ${error.message}`;
  }
}

el('upload').addEventListener('submit', async event => {
  event.preventDefault();
  const file = el('image').files[0];
  if (!file) return;
  const button = event.submitter;
  button.disabled = true;
  el('status').textContent = 'Running local v2 detection → OCR/CV → readiness → compiler…';
  el('diagnostics').hidden = true;
  el('warning').hidden = true;
  cancelAnimationFrame(animationFrame);
  figure?.destroy(); figure = null;
  el('figure').replaceChildren();
  try {
    const form = new FormData(); form.append('file', file);
    const http = await fetch('/api/experiments/circuit-v2', {method:'POST', body:form});
    const body = await http.text();
    try { response = JSON.parse(body); }
    catch { throw new Error(`API connection failed (HTTP ${http.status}). The backend may be offline or restarting. Retry the upload.`); }
    if (!http.ok) throw new Error(typeof response.detail === 'string' ? response.detail : JSON.stringify(response.detail));
    el('diagnostics').hidden = false;
    el('model').textContent = `${response.model?.checkpoint || 'Checkpoint unavailable'} | SHA-256: ${response.model?.sha256 || 'unavailable'}`;
    el('stages').replaceChildren();
    for (const stage of response.stages) {
      const li = document.createElement('li'); li.className = stage.status;
      li.textContent = `${stage.stage}: ${stage.status} (${stage.duration_ms} ms) ${stage.message || ''} ${(stage.issues || []).map(i => `${i.code}: ${i.message}`).join('; ')}`;
      el('stages').append(li);
    }
    el('raw').textContent = JSON.stringify(response, null, 2);
    el('preview').disabled = !response.preview_scene;
    if (response.scene) await play(response.scene, false);
    else if (el('force').checked && response.preview_scene) await play(response.preview_scene, true);
    else el('status').textContent = `Stopped at ${response.first_blocker?.stage || 'compilation'}. See diagnostics below.`;
  } catch (error) { el('status').textContent = error.message; }
  finally { button.disabled = false; }
});
el('preview').addEventListener('click', () => play(response.preview_scene, true));
el('download').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(response,null,2)],{type:'application/json'}));
  const link = document.createElement('a'); link.href=url; link.download='circuit-v2-diagnostics.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url),1000);
});

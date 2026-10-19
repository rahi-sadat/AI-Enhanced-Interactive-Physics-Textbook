/** Opt-in real-image circuit browser acceptance against a live Gemini backend.
 * Requires explicit permission to send the two user images to Gemini.
 * Never run as part of the offline npm test command.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const port = process.env.PHASE4_WEB_PORT || '8002';
const targets = await (await fetch('http://127.0.0.1:9222/json')).json();
const target = targets.find(item => item.type === 'page' && item.url.includes(`:${port}`));
assert.ok(target, `No Chrome page at web port ${port}`);
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
let nextId = 1;
const pending = new Map();
socket.onmessage = ({ data }) => {
  const message = JSON.parse(data);
  if (!message.id || !pending.has(message.id)) return;
  const { resolve, reject } = pending.get(message.id);
  pending.delete(message.id);
  message.error ? reject(new Error(JSON.stringify(message.error))) : resolve(message.result);
};
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = nextId++;
  pending.set(id, { resolve, reject });
  socket.send(JSON.stringify({ id, method, params }));
});
const evaluate = async expression => {
  const response = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (response.exceptionDetails) throw new Error(response.exceptionDetails.exception?.description || response.exceptionDetails.text);
  return response.result?.value;
};
const waitFor = async (expression, limitMs = 180000) => {
  const until = Date.now() + limitMs;
  while (Date.now() < until) {
    if (await evaluate(expression)) return;
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  throw new Error(`Timed out waiting for ${expression}`);
};
const upload = async filename => {
  const bytes = fs.readFileSync(path.join(root, 'tests/fixtures/unseen', filename));
  const base64 = bytes.toString('base64');
  await evaluate(`(() => {
    const raw = atob(${JSON.stringify(base64)});
    const data = Uint8Array.from(raw, char => char.charCodeAt(0));
    const file = new File([data], ${JSON.stringify(filename)}, { type: 'image/jpeg' });
    window.__orchestrator.startWithFile(file);
    return true;
  })()`);
  await waitFor(`['NEEDS_REVIEW', 'READY_TO_SIMULATE', 'ERROR', 'UNSUPPORTED'].includes(window.__orchestrator.state)`);
  const state = await evaluate('window.__orchestrator.state');
  if (state === 'ERROR') throw new Error(await evaluate('window.__orchestrator.currentError'));
  return state;
};

try {
  await send('Runtime.enable');
  await waitFor('Boolean(window.__orchestrator && window.__activeFigure)', 15000);
  const openState = await upload('user_circuit_open_switch.jpg');
  assert.equal(openState, 'NEEDS_REVIEW', 'Open switch must require review');
  assert.equal(await evaluate('window.__orchestrator.compiledScene'), null,
    'Open switch produced an executable circuit');
  assert.equal(await evaluate(`window.__orchestrator.bookIR.entities.some(entity => entity.type === 'switch' || entity.type === 'open_switch')`),
    true, 'Live semantic switch was lost before browser review');

  await evaluate('window.__orchestrator.reset()');
  const parallelState = await upload('user_circuit_parallel_network.jpg');
  assert.equal(parallelState, 'READY_TO_SIMULATE', 'Grounded parallel circuit did not compile');
  assert.equal(await evaluate('window.__orchestrator.compiledScene.subtype'), 'dc_linear');
  await evaluate(`(() => {
    window.__reviewModal.open();
    const button = document.querySelector('[data-action="start-sim-banner"]') ||
      document.querySelector('[data-el="btnStartSim"]');
    if (!button) throw new Error('Start Simulation button missing');
    button.click();
    return true;
  })()`);
  await waitFor(`window.__orchestrator.state === 'SIMULATING' &&
    window.__activeFigure.scene?.subtype === 'dc_linear' &&
    window.__activeFigure.runtime.getState()?.running === true`);
  const beforeEvidence = await evaluate('JSON.stringify(window.__orchestrator.bookIR)');
  const initial = await evaluate(`(() => ({
    resistance: window.__activeFigure.runtime.scene.parameters.R1.value,
    current: Math.abs(window.__activeFigure.runtime.getState().branchCurrents.R1)
  }))()`);
  assert.equal(initial.resistance, 50);
  assert.ok(Math.abs(initial.current - 12 / 250) < 1e-5, 'Initial circuit current disagrees with Ohm law');
  await evaluate(`(() => {
    const input = document.querySelector('.interactive-figure-root [data-param-key="R1"] .if-val-input');
    if (!input) throw new Error('R1 control missing');
    input.value = '75';
    input.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  })()`);
  const changed = await evaluate(`(() => ({
    resistance: window.__activeFigure.runtime.scene.parameters.R1.value,
    current: Math.abs(window.__activeFigure.runtime.getState().branchCurrents.R1)
  }))()`);
  assert.equal(changed.resistance, 75);
  assert.ok(Math.abs(changed.current - 12 / 275) < 1e-5, 'Edited circuit current disagrees with Ohm law');
  assert.equal(await evaluate('JSON.stringify(window.__orchestrator.bookIR)'), beforeEvidence,
    'Student exploration mutated BookIR');
  await evaluate('document.querySelector(".interactive-figure-root [data-el=btnReset]").click()');
  const restored = await evaluate('window.__activeFigure.runtime.scene.parameters.R1.value');
  assert.equal(restored, 50, 'Reset did not restore source resistance');
  console.log(JSON.stringify({ open_switch: openState, parallel: parallelState,
    initial_current_A: initial.current, edited_current_A: changed.current,
    book_ir_unchanged: true, reset_resistance_ohm: restored }));
} finally {
  socket.close();
}

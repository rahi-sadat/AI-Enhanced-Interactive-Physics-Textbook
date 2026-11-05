/** Opt-in live browser upload acceptance for explicitly authorized images.
 *
 * Requires the real Gemini API backend, local preview server, and Chrome CDP.
 * This exercises the visible upload button and the application's automatic
 * upload-to-simulation path. It is excluded from offline npm tests.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const benchmarkPath = process.argv[2] || path.join(root, 'storage/generated/phase5_live_http_all_nine.json');
const benchmark = JSON.parse(fs.readFileSync(benchmarkPath, 'utf8').replace(/^\uFEFF/, ''));
const rows = benchmark.cases;
assert.equal(rows.length, 9, 'Expected nine explicitly authorized images');

const port = process.env.PHASE4_WEB_PORT || '8002';
const cdpPort = process.env.PHASE4_CDP_PORT || '9222';
const targets = await (await fetch(`http://127.0.0.1:${cdpPort}/json`)).json();
const target = targets.find(item => item.type === 'page' && item.url.includes(`:${port}`));
assert.ok(target, `No Chrome page at web port ${port}`);
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
let nextId = 1;
const pending = new Map();
let loadedResolve;
socket.onmessage = ({ data }) => {
  const message = JSON.parse(data);
  if (message.method === 'Page.loadEventFired') loadedResolve?.();
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
const waitFor = async (expression, limitMs = 220000) => {
  const until = Date.now() + limitMs;
  while (Date.now() < until) {
    if (await evaluate(expression)) return;
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  throw new Error(`Timed out waiting for ${expression}`);
};

const results = [];
try {
  await send('Runtime.enable');
  await send('Page.enable');
  // Wait for the new document: a ready old window can disappear between the
  // first readiness poll and reset() immediately after Page.reload.
  let loadTimeout;
  const loaded = new Promise((resolve, reject) => {
    loadedResolve = () => { clearTimeout(loadTimeout); resolve(); };
    loadTimeout = setTimeout(() => reject(new Error('Browser reload timed out')), 20000);
  });
  await send('Page.reload', { ignoreCache: true });
  await loaded;
  await waitFor('Boolean(window.__orchestrator && window.__activeFigure)', 20000);
  for (const [index, row] of rows.entries()) {
    const fixture = path.join(root, 'tests/fixtures/unseen', row.path);
    const encoded = fs.readFileSync(fixture).toString('base64');
    const extension = path.extname(fixture).toLowerCase();
    const mime = extension === '.png' ? 'image/png' : 'image/jpeg';
    const filename = `neutral_browser_${index + 1}${extension}`;
    await evaluate(`(() => {
      window.__orchestrator.reset();
      document.getElementById('btn-open-upload').click();
      const bytes = Uint8Array.from(atob(${JSON.stringify(encoded)}), char => char.charCodeAt(0));
      const file = new File([bytes], ${JSON.stringify(filename)}, { type: ${JSON.stringify(mime)} });
      const transfer = new DataTransfer();
      transfer.items.add(file);
      const input = document.getElementById('file-input');
      input.files = transfer.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    })()`);
    await waitFor('document.getElementById("btn-generate-sim").disabled === false', 10000);
    await evaluate('document.getElementById("btn-generate-sim").click()');
    await waitFor(`['SIMULATING', 'NEEDS_REVIEW', 'ERROR', 'UNSUPPORTED'].includes(window.__orchestrator.state)`);
    const actual = await evaluate(`(() => {
      const orch = window.__orchestrator;
      const fig = window.__activeFigure;
      const state = fig.runtime.getState() || {};
      const source = orch.sourceAsset || {};
      const image = fig.viewport?._dom?.image;
      return {
        state: orch.state, domain: orch.bookIR?.domain, subtype: orch.bookIR?.subtype,
        sceneSubtype: orch.compiledScene?.subtype || null,
        runtimeSubtype: fig.scene?.subtype || null,
        running: Boolean(state.running),
        sourceWidth: source.width_px, sourceHeight: source.height_px,
        naturalWidth: image?.naturalWidth || 0, naturalHeight: image?.naturalHeight || 0,
        currentError: orch.currentError || null,
        issues: orch.reviewState?.issues?.length || 0
      };
    })()`);
    // Preserve the real UI failure before a domain assertion obscures it.
    if (actual.state === 'ERROR' || actual.domain !== row.domain) {
      console.error(JSON.stringify({ id: row.id, ...actual }));
      const screenshot = await send('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(path.join(root, 'storage/generated/last_upload_failure.png'), Buffer.from(screenshot.data, 'base64'));
    }
    assert.equal(actual.domain, row.domain, `${row.id}: wrong live domain`);
    assert.equal(actual.subtype, row.subtype, `${row.id}: wrong live subtype`);
    if (row.scene_created) {
      assert.equal(actual.state, 'SIMULATING', `${row.id}: automatic UI path did not start`);
      assert.equal(actual.sceneSubtype, row.subtype, `${row.id}: wrong compiled subtype`);
      assert.equal(actual.runtimeSubtype, row.subtype, `${row.id}: wrong runtime subtype`);
      assert.equal(actual.running, true, `${row.id}: runtime did not run`);
      assert.equal(actual.naturalWidth, actual.sourceWidth, `${row.id}: browser source width mismatch`);
      assert.equal(actual.naturalHeight, actual.sourceHeight, `${row.id}: browser source height mismatch`);
    } else {
      assert.equal(actual.state, 'NEEDS_REVIEW', `${row.id}: negative diagram did not abstain`);
      assert.equal(actual.sceneSubtype, null, `${row.id}: negative diagram compiled`);
    }
    results.push({ id: row.id, subtype: row.subtype, state: actual.state,
      running: actual.running, source_dimensions_match: row.scene_created
        ? actual.naturalWidth === actual.sourceWidth && actual.naturalHeight === actual.sourceHeight
        : null });
    process.stdout.write(`${row.id}: ${actual.state}\n`);
  }
  const output = { cases: results.length, automatic_simulations: results.filter(r => r.state === 'SIMULATING').length,
    correct_abstentions: results.filter(r => r.state === 'NEEDS_REVIEW').length, results };
  fs.writeFileSync(path.join(root, 'storage/generated/phase5_live_upload_browser_matrix.json'), JSON.stringify(output, null, 2));
  console.log(JSON.stringify({ cases: output.cases, automatic_simulations: output.automatic_simulations,
    correct_abstentions: output.correct_abstentions }));
} finally {
  socket.close();
}

/** Browser runtime smoke check for scenes compiled from real fixture images.
 *
 * This checks rendering and resize registration after compilation. The source
 * benchmark used MockVisionProvider; this script does not test live VLM or
 * the review flow. Run with the Phase 4 preview server and Chrome CDP open.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const benchmarkPath = process.argv[2] || path.join(root, 'storage/generated/phase3_full_benchmark.json');
const benchmark = JSON.parse(fs.readFileSync(benchmarkPath, 'utf8').replace(/^\uFEFF/, ''));
const rows = benchmark.cases.filter(row => row.auto_scene || row.review?.scene);
assert.ok(rows.length > 0, 'Benchmark has no compiled scenes');

const port = process.env.PHASE4_WEB_PORT || '8002';
const cdpPort = process.env.PHASE4_CDP_PORT || '9222';
const targets = await (await fetch(`http://127.0.0.1:${cdpPort}/json`)).json();
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
  const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text + ': ' + result.exceptionDetails.exception?.description);
  return result.result?.value;
};

try {
  await send('Runtime.enable');
  const ready = await evaluate('Boolean(window.__activeFigure && window.__orchestrator)');
  assert.equal(ready, true, 'Web app did not initialize');
  const checked = [];
  for (const row of rows) {
    const scene = structuredClone(row.auto_scene || row.review.scene);
    const file = path.join(root, 'tests/fixtures/unseen', row.path);
    const extension = path.extname(file).toLowerCase();
    const mime = extension === '.png' ? 'image/png' : 'image/jpeg';
    const imageUrl = `data:${mime};base64,${fs.readFileSync(file).toString('base64')}`;
    scene.source = { ...scene.source, image: imageUrl };
    scene.visual = { ...scene.visual, background_url: imageUrl };
    await evaluate(`(async () => {
      const figure = window.__activeFigure;
      figure.pause();
      await figure.load(${JSON.stringify(scene)});
      figure.play();
      return true;
    })()`);
    for (const [width, height, deviceScaleFactor] of [[1280, 900, 1], [900, 700, 1], [901, 703, 1.25], [393, 328, 2]]) {
      await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor, mobile: false });
      await new Promise(resolve => setTimeout(resolve, 250));
      const actual = await evaluate(`(() => {
        const fig = window.__activeFigure;
        const v = fig.viewport;
        const image = v._dom.image;
        const a = image.getBoundingClientRect();
        const b = v._dom.overlay.getBoundingClientRect();
        return {
          domain: fig.currentDomain,
          subtype: fig.scene?.subtype,
          running: Boolean(fig.runtime.getState()?.running),
          solverState: (() => {
            const state = fig.runtime.getState() || {};
            return {
              opticsSolved: Boolean(state.solution),
              nodeVoltages: state.nodeVoltages || {},
              branchCurrents: state.branchCurrents || {},
              time: state.time
            };
          })(),
          imageLoaded: image.complete && image.naturalWidth > 0,
          naturalWidth: image.naturalWidth,
          naturalHeight: image.naturalHeight,
          sourceWidth: v.sourceW,
          sourceHeight: v.sourceH,
          anchors: v.calibrationAnchors.map(({ id, x, y }) => ({ id, x, y })),
          width: a.width,
          height: a.height,
          maxEdgeError: Math.max(...['left', 'top', 'right', 'bottom'].map(edge => Math.abs(a[edge] - b[edge])))
        };
      })()`);
      assert.equal(actual.domain, row.domain, `${row.id}: wrong domain`);
      assert.equal(actual.subtype, row.subtype, `${row.id}: wrong subtype`);
      assert.equal(actual.running, true, `${row.id}: runtime not running`);
      if (row.domain === 'optics') {
        assert.equal(actual.solverState.opticsSolved, true, `${row.id}: optics solver has no solution`);
      } else if (row.domain === 'circuits') {
        assert.ok(Object.keys(actual.solverState.nodeVoltages).length > 0,
          `${row.id}: circuit solver has no node voltages`);
        assert.ok(Object.keys(actual.solverState.branchCurrents).length > 0,
          `${row.id}: circuit solver has no branch currents`);
        assert.ok(Object.values(actual.solverState.nodeVoltages).every(Number.isFinite),
          `${row.id}: circuit solver has nonfinite node voltage`);
        assert.ok(Object.values(actual.solverState.branchCurrents).every(Number.isFinite),
          `${row.id}: circuit solver has nonfinite branch current`);
      } else {
        assert.ok(Number.isFinite(actual.solverState.time), `${row.id}: mechanics solver has nonfinite time`);
      }
      assert.equal(actual.imageLoaded, true, `${row.id}: image not loaded`);
      assert.equal(actual.naturalWidth, actual.sourceWidth, `${row.id}: source width mismatch`);
      assert.equal(actual.naturalHeight, actual.sourceHeight, `${row.id}: source height mismatch`);
      assert.ok(actual.width > 0 && actual.height > 0, `${row.id}: image invisible`);
      assert.ok(actual.maxEdgeError <= 2, `${row.id}: image/overlay edge error ${actual.maxEdgeError}px`);
      assert.ok(actual.anchors.length > 0, `${row.id}: no evidenced inspection anchors`);
      assert.ok(actual.anchors.every(anchor => Number.isFinite(anchor.x) && Number.isFinite(anchor.y)),
        `${row.id}: invalid inspection anchor`);
      if (row.subtype === 'dc_linear') {
        assert.ok(actual.anchors.every(anchor => anchor.id.includes('.t')),
          `${row.id}: circuit inspector displayed a synthetic component marker`);
      }
      checked.push({ id: row.id, subtype: row.subtype, viewport: `${width}x${height}`,
        device_pixel_ratio: deviceScaleFactor,
        edge_error_px: actual.maxEdgeError, evidence_anchors: actual.anchors.length });
    }
  }
  console.log(JSON.stringify({ scenes: rows.length, checks: checked }, null, 2));
} finally {
  await send('Emulation.clearDeviceMetricsOverride').catch(() => {});
  socket.close();
}

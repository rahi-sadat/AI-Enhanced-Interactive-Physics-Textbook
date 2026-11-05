/** Opt-in audit of actual compiled scenes and explicitly experimental previews. */
import fs from 'node:fs';
import path from 'node:path';
import { PhysicsRuntime } from '../engine/core/PhysicsRuntime.js';

const directory = process.argv[2] || 'outputs/circuit_v2_pipeline_99';
const rows = [];
for (const name of fs.readdirSync(path.join(directory, 'results')).filter(n => n.endsWith('.json')).sort()) {
  const result = JSON.parse(fs.readFileSync(path.join(directory, 'results', name)));
  const row = {filename: result.filename};
  for (const key of ['scene', 'preview_scene']) {
    if (!result[key]) continue;
    const runtime = new PhysicsRuntime();
    try {
      await runtime.load(result[key]);
      const electrical = runtime.adapter?.electricalState;
      if (electrical?.success === false) throw new Error(electrical.error || 'Solver failed');
      runtime.play();
      runtime.adapter.step(1/60);
      const stepped = runtime.adapter?.electricalState;
      if (stepped?.success === false) throw new Error(stepped.error || 'Solver failed after playback step');
      row[key] = {status: 'passed', current_A: runtime.getState().totalCurrent_A ?? null};
    } catch (error) { row[key] = {status: 'failed', message: error.message}; }
    finally { runtime.destroy(); }
  }
  rows.push(row);
}
const totals = Object.fromEntries(['scene','preview_scene'].map(key => [key, {
  tested: rows.filter(r=>r[key]).length,
  passed: rows.filter(r=>r[key]?.status==='passed').length,
  failed: rows.filter(r=>r[key]?.status==='failed').length,
}]));
fs.writeFileSync(path.join(directory,'runtime_results.json'),JSON.stringify({totals,images:rows},null,2));
console.log(JSON.stringify(totals));
for (const row of rows.filter(r=>Object.values(r).some(v=>v?.status==='failed'))) console.log(JSON.stringify(row));

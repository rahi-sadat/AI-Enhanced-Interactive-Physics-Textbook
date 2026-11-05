/** Offline artifact/visual QA for the detailed manuals. No app or model requests. */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const repo=path.resolve(import.meta.dirname,'../..');
const root=path.join(repo,'docs/reports/pipeline_walkthroughs_20261017');
const evidence=path.join(repo,'storage/generated/debug_traces/20261017/walkthrough_qa');
fs.mkdirSync(evidence,{recursive:true});
const rows=JSON.parse(fs.readFileSync(path.join(root,'manifest.json')));
const secrets=fs.existsSync(path.join(repo,'.env'))?fs.readFileSync(path.join(repo,'.env'),'utf8').split(/\r?\n/).filter(s=>/^\s*(GEMINI_API_KEY|GOOGLE_API_KEY)\s*=/.test(s)).map(s=>s.slice(s.indexOf('=')+1).trim().replace(/^['"]|['"]$/g,'')).filter(Boolean):[];
const results=[];
for(const row of rows){
  const file=path.join(root,row.html),dir=path.dirname(file),manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json')));
  const report=fs.readFileSync(file,'utf8'),missing=[],failures=[];
  if(manifest.stages.length!==34)failures.push('Expected 34 stages');
  for(const ref of report.matchAll(/(?:href|src)="([^"]+)"/g)){
    if(/^(#|data:|https?:)/.test(ref[1]))continue;
    if(!fs.existsSync(path.resolve(dir,decodeURIComponent(ref[1].split('#')[0]))))missing.push(ref[1]);
  }
  for(const stage of manifest.stages){
    const data=JSON.parse(fs.readFileSync(path.join(dir,stage.bundle)));
    for(const k of ['actual_input','expected_input','actual_output','expected_output_contract','expected_diagram','status','change_or_loss'])if(!(k in data))failures.push(stage.stage+' missing '+k);
    for(const rec of data.actual_input.records){
      if(rec.call){const actual=JSON.parse(fs.readFileSync(path.join(repo,'storage/generated/debug_traces/20261016',row.trace,'calls',rec.call,'actual_input.json')));if(JSON.stringify(actual)!==JSON.stringify(rec.value))failures.push('Input mismatch '+rec.call);}
    }
    for(const rec of data.actual_output.records){
      if(rec.call){const actual=JSON.parse(fs.readFileSync(path.join(repo,'storage/generated/debug_traces/20261016',row.trace,'calls',rec.call,'actual_output.json')));if(JSON.stringify(actual)!==JSON.stringify(rec.return_value))failures.push('Output mismatch '+rec.call);}
    }
    if(row.diagram==='Series DC circuit'&&stage.stage>=28&&stage.execution!=='NOT EXECUTED')failures.push('Circuit has invented runtime execution');
  }
  const leaks=[];
  function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else{const text=fs.readFileSync(p,'utf8');if(secrets.some(s=>text.includes(s)))leaks.push(path.relative(dir,p));}}}
  walk(dir);
  const t=await (await fetch('http://127.0.0.1:9223/json/new?'+encodeURIComponent(pathToFileURL(file).href),{method:'PUT'})).json();
  const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);let id=0;const pending=new Map();
  ws.onmessage=({data})=>{const m=JSON.parse(data);if(pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id);}};
  const send=(method,params={})=>new Promise(r=>{pending.set(++id,r);ws.send(JSON.stringify({id,method,params}));});
  const ev=async expression=>{const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.error||r.result.exceptionDetails)throw new Error(JSON.stringify(r));return r.result.result.value;};
  const shots=[];
  try{
    await send('Page.bringToFront');await new Promise(r=>setTimeout(r,600));
    for(const stage of ['stage-13','stage-14','stage-33']){
      await ev(`document.getElementById(${JSON.stringify(stage)}).scrollIntoView()`);
      await ev(`Promise.all([...document.getElementById(${JSON.stringify(stage)}).querySelectorAll('img')].map(i=>{i.loading='eager';return i.decode().catch(()=>null)}))`);
      const shot=await send('Page.captureScreenshot',{format:'png'});const name=path.basename(dir)+'_'+stage+'.png';fs.writeFileSync(path.join(evidence,name),Buffer.from(shot.result.data,'base64'));shots.push(name);
    }
    // Expand the complete-data panels in one stage to verify long JSON stays within layout.
    await ev("[...document.getElementById('stage-16').querySelectorAll('details')].forEach(d=>d.open=true)");
    const visual=await ev("({title:document.title,stages:document.querySelectorAll('section[id^=stage-]').length,overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),fullDataPanels:document.querySelectorAll('details').length})");
    results.push({diagram:row.diagram,stages:manifest.stages.length,recorded_calls:manifest.backend_calls,missing_links:missing,failures,credential_leak_paths:leaks,visual,screenshots:shots});
  }finally{ws.close();}
}
fs.writeFileSync(path.join(evidence,'verification.json'),JSON.stringify(results,null,2));
console.log(JSON.stringify(results,null,2));
if(results.some(r=>r.missing_links.length||r.failures.length||r.credential_leak_paths.length||r.visual.overflow||r.visual.broken.length))process.exitCode=1;

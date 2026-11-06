/** Real-file browser acceptance against the running local API and Vite lab.
 * Uses a dedicated headless Chrome debug profile, never a user's existing tab.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { parseArgs } from 'node:util';
const {values:args}=parseArgs({options:Object.fromEntries(['cdp','url','output','c3','series-parallel','holdout'].map(k=>[k,{type:'string'}]))});
for(const key of ['cdp','url','output','c3','series-parallel']) assert.ok(args[key],`Missing --${key}`);
fs.mkdirSync(args.output,{recursive:false});
const health=await fetch(new URL('/api/health',args.url));
assert.ok(health.ok,'Wait for the local API and Vite proxy to be ready before browser acceptance');
const targets=await (await fetch(args.cdp+'/json')).json();
const target=targets.find(t=>t.type==='page');
const socket=new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
let id=0;const pending=new Map(),errors=[],checks=[];
socket.onmessage=({data})=>{
  const m=JSON.parse(data);
  if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);
  if(!pending.has(m.id))return;
  const {resolve,reject}=pending.get(m.id);pending.delete(m.id);
  m.error?reject(new Error(JSON.stringify(m.error))):resolve(m.result);
};
const send=(method,params={})=>new Promise((resolve,reject)=>{const key=++id;pending.set(key,{resolve,reject});socket.send(JSON.stringify({id:key,method,params}));});
const evaluate=async expression=>{
  const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
  if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);
  return r.result?.value;
};
const wait=async expression=>{
  const until=Date.now()+180000;
  while(Date.now()<until){if(await evaluate(expression))return;await new Promise(r=>setTimeout(r,250));}
  throw new Error('Timeout: '+expression+'; '+await evaluate('document.body.innerText'));
};
const raw=()=>evaluate('JSON.parse(document.querySelector("#raw").textContent)');
const set=async(selector,value)=>evaluate(`(()=>{const el=document.querySelector(${JSON.stringify(selector)});el.value=${JSON.stringify(value)};el.dispatchEvent(new Event('change',{bubbles:true}));})()`);
const screenshot=async name=>{
  const height=await evaluate('document.documentElement.scrollHeight');
  const width=await evaluate('window.innerWidth');
  const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width,height,scale:1}});
  fs.writeFileSync(path.join(args.output,name),Buffer.from(r.data,'base64'));
};
async function upload(file,status){
  const doc=await send('DOM.getDocument');
  const input=await send('DOM.querySelector',{nodeId:doc.root.nodeId,selector:'#image'});
  await send('DOM.setFileInputFiles',{nodeId:input.nodeId,files:[path.resolve(file)]});
  await evaluate('document.querySelector("#upload").requestSubmit(document.querySelector("#upload button"))');
  await wait(`document.querySelector('#status').textContent===${JSON.stringify(status)}`);
  await wait('document.querySelector(".figure-viewport-img")?.naturalWidth>0');
  const integrity=await evaluate(`(async()=>{const r=JSON.parse(document.querySelector('#raw').textContent),img=document.querySelector('.figure-viewport-img');
    const bytes=await (await fetch(img.src)).arrayBuffer();const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
    return {hash,expected:r.source_asset.sha256,width:img.naturalWidth,height:img.naturalHeight,source:r.source_asset};})()`);
  assert.equal(integrity.hash,integrity.expected);
  assert.equal(integrity.width,integrity.source.width_px);assert.equal(integrity.height,integrity.source.height_px);
  const geometry=await evaluate(`(()=>{const r=JSON.parse(document.querySelector('#raw').textContent);return (r.book_ir.parameters.components||[]).map(c=>{
    const rect=document.querySelector('[data-component-id="'+c.id+'"]');return {expected:c.geometry.bbox_source_px,
      actual:['x','y','width','height'].map(k=>Number(rect.getAttribute(k))),orientation:rect.dataset.orientation,expectedOrientation:c.geometry.orientation,
      terminals:c.terminals.map(t=>{const p=document.querySelector('[data-terminal-id="'+t.id+'"]');return {expected:t.source_px,actual:[Number(p.getAttribute('cx')),Number(p.getAttribute('cy'))]};})};});})()`);
  for(const c of geometry){
    assert.deepEqual(c.actual,[c.expected[0],c.expected[1],c.expected[2]-c.expected[0],c.expected[3]-c.expected[1]]);
    assert.equal(c.orientation,c.expectedOrientation);
    for(const t of c.terminals)assert.deepEqual(t.actual,t.expected);
  }
  checks.push({test:'source bytes and component/terminal coordinates',hash:integrity.hash,components:geometry.length});
}
try{
  await send('Runtime.enable');await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:1200,height:1000,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:args.url});await wait('Boolean(document.querySelector("#upload"))');
  await upload(args['series-parallel'],'IDEAL_SOLVED');
  let result=await raw();
  assert.equal(result.preview_scene,null);
  assert.equal(result.scene.coordinateSpace.width,403);assert.equal(result.scene.coordinateSpace.height,178);
  assert.equal(result.ideal_analysis.electrical_state.equivalent_resistance_ohm,8);
  assert.equal(await evaluate('document.querySelector(".figure-viewport-img").naturalWidth'),403);
  const originalSeries=JSON.stringify(result.book_ir);
  for(const [width,dpr] of [[900,1],[1400,2]]){
    await send('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:dpr,mobile:false});
    await wait(`window.innerWidth===${width}`);
    const layout=await evaluate(`(()=>{const a=document.querySelector('.figure-viewport-img').getBoundingClientRect(),b=document.querySelector('.circuit-overlay-svg').getBoundingClientRect();return {image:{x:a.x,y:a.y,w:a.width,h:a.height},svg:{x:b.x,y:b.y,w:b.width,h:b.height},viewBox:document.querySelector('svg').getAttribute('viewBox')};})()`);
    for(const key of ['x','y','w','h'])assert.ok(Math.abs(layout.image[key]-layout.svg[key])<.2,JSON.stringify(layout));
    assert.equal(layout.viewBox,'0 0 403 178');checks.push({test:'registration',width,dpr,...layout});
  }
  await wait('document.querySelectorAll(".circuit-layer-flow circle").length>0');
  await screenshot('series_parallel.png');
  fs.writeFileSync(path.join(args.output,'series_parallel.json'),JSON.stringify(result,null,2));
  assert.equal(JSON.stringify((await raw()).book_ir),originalSeries);
  const correctionId=result.book_ir.parameters.components.find(c=>c.label==='R1').id;
  await set('#correct-component',correctionId);
  const beforeCorrection=result.analysis_id;
  await evaluate('document.querySelector("#correct-value").value="6";document.querySelector("#correction").requestSubmit()');
  await wait(`JSON.parse(document.querySelector('#raw').textContent).analysis_id!==${JSON.stringify(beforeCorrection)}`);
  result=await raw();assert.equal(result.ideal_analysis.electrical_state.equivalent_resistance_ohm,9);
  assert.deepEqual(result.book_ir.evidence,JSON.parse(originalSeries).evidence);
  assert.deepEqual(result.book_ir.parameters.geometric_conductor_graph,JSON.parse(originalSeries).parameters.geometric_conductor_graph);
  assert.equal(result.book_ir.parameters.components.find(c=>c.id===correctionId).value_provenance.source,'user_corrected');
  await screenshot('explicit_value_correction.png');checks.push({test:'explicit correction preserves OCR and source graph',resistance_ohm:9});
  await upload(args.c3,'IDEAL_REJECTED');result=await raw();
  const faultId=result.ideal_analysis.fault_path_id;
  const faultWire=result.book_ir.parameters.wires.find(w=>w.id===faultId);
  assert.ok(Math.max(...faultWire.points.map(p=>p[0]))>1400);
  const originalBook=JSON.stringify(result.book_ir),graphId=result.ideal_analysis.original_graph_id;
  assert.equal(await evaluate('document.querySelector("#telemetry").hidden'),true);
  assert.equal(await evaluate('document.querySelectorAll(".circuit-layer-flow circle").length'),0);
  assert.equal(await evaluate('document.querySelector("[data-fault=true]").dataset.wireId'),faultId);
  await set('#mode','qualitative');await wait('document.querySelector("#status").textContent==="QUALITATIVE_FAULT"');
  assert.equal(await evaluate('document.querySelector("#telemetry").hidden'),true);
  await screenshot('c3_qualitative.png');
  await set('#mode','non_ideal');await wait('document.querySelector("#status").textContent==="QUALITATIVE_FAULT"');
  await set('#internal','1');await set('#path-resistance','2');
  await wait('document.querySelector("#status").textContent==="NON_IDEAL_SOLVED"');
  result=await raw();let latest=result.analysis_history.at(-1);
  assert.equal(latest.original_graph_id,graphId);
  assert.equal(latest.electrical_state.components.det_voltage_source_5.current_a,-6.24);
  assert.ok(Math.abs(latest.electrical_state.components['fault_path:'+faultId].current_a-2.88)<1e-12);
  assert.ok(Math.abs(Number(await evaluate(`document.querySelector('[data-wire-id="${faultId}"]').dataset.currentA`))-2.88)<1e-12);
  const paths=await evaluate(`Array.from(document.querySelectorAll('[data-wire-id]'),p=>({id:p.dataset.wireId,d:p.getAttribute('d')}))`);
  for(const wire of latest.graph.wires){
    const expected=wire.points.map((p,i)=>`${i?'L':'M'} ${p[0]} ${p[1]}`).join(' ');
    assert.equal(paths.find(p=>p.id===wire.id).d,expected);
  }
  assert.equal(JSON.stringify(result.book_ir),originalBook);
  await screenshot('c3_non_ideal.png');
  fs.writeFileSync(path.join(args.output,'c3_non_ideal.json'),JSON.stringify(result,null,2));
  await set('#internal','2');await wait('document.querySelector("#status").textContent==="NON_IDEAL_SOLVED"');
  latest=(await raw()).analysis_history.at(-1);
  assert.ok(Math.abs(latest.electrical_state.components.det_voltage_source_5.current_a+78/19)<1e-6);
  await set('#path-resistance','');await wait('document.querySelector("#status").textContent==="QUALITATIVE_FAULT"');
  assert.equal(await evaluate('document.querySelector("#telemetry").hidden'),true);
  await set('#internal','-1');await wait('document.querySelector("#status").textContent==="INVALID_PARAMETERS"');
  assert.equal(await evaluate('document.querySelector("#telemetry").hidden'),true);
  await set('#internal','0');await set('#path-resistance','2');
  await wait('document.querySelector("#status").textContent==="NON_IDEAL_SOLVED"');
  assert.equal((await raw()).analysis_history.at(-1).electrical_state.components.det_voltage_source_5.current_a,-13);
  await evaluate('document.querySelector("#playback").click()');
  assert.equal(await evaluate('document.querySelectorAll(".circuit-layer-flow circle").length'),0);
  await evaluate('document.querySelector("#playback").click()');
  await wait('document.querySelectorAll(".circuit-layer-flow circle").length>0');
  await set('#mode','ideal');await wait('document.querySelector("#status").textContent==="IDEAL_REJECTED"');
  assert.equal(await evaluate('document.querySelector("#telemetry").hidden'),true);
  assert.equal(JSON.stringify((await raw()).book_ir),originalBook);
  if(args.holdout)for(const item of JSON.parse(fs.readFileSync(args.holdout,'utf8'))) {
    await upload(item.source,'IDEAL_SOLVED');const r=await raw();
    assert.ok(Math.abs(r.ideal_analysis.electrical_state.equivalent_resistance_ohm-item.expected_resistance_ohm)<1e-8);
    assert.equal(r.ideal_analysis.validation.valid,true);
    const wireData=await evaluate(`Array.from(document.querySelectorAll('[data-wire-id]'),p=>({id:p.dataset.wireId,current:p.dataset.currentA,direction:p.dataset.direction}))`);
    for(const w of wireData) {
      const current=r.ideal_analysis.wire_currents_a[w.id];
      assert.ok(Math.abs(Number(w.current)-current)<1e-10);
      assert.equal(w.direction,Math.abs(current)<1e-9?'none':current>0?'forward':'backward');
    }
    await screenshot(item.id+'.png');checks.push({test:'additional holdout source and runtime',id:item.id,resistance_ohm:item.expected_resistance_ohm});
  }
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(args.output,'summary.json'),JSON.stringify({passed:true,checks,errors,
    cases:['series-parallel ideal','C3 ideal rejection','C3 qualitative','C3 non-ideal','parameter edits','missing/invalid parameters','zero internal resistance','pause/play','evidence immutability','exact conductor polylines']},null,2));
  console.log('Browser acceptance passed');
}finally{socket.close();}

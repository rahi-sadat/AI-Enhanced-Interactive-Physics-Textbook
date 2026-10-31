/** Opt-in offline Chrome acceptance. Requires circuit_repair_server.py, Vite,
 * and a dedicated Chrome debugging profile on port 9223. No external services.
 * Exercises real file input, multipart API, orchestrator, renderer and runtime.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../..');
const out=path.join(root,'storage/generated/circuit_repair_20261018');
const targets=await (await fetch('http://127.0.0.1:9223/json')).json();
const target=targets.find(t=>t.type==='page');
const socket=new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
let id=0;const pending=new Map();const errors=[];
socket.onmessage=({data})=>{
 const m=JSON.parse(data);
 if(m.method==='Runtime.exceptionThrown') errors.push(m.params.exceptionDetails);
 if(!pending.has(m.id))return;
 const {resolve,reject}=pending.get(m.id);pending.delete(m.id);
 m.error?reject(new Error(JSON.stringify(m.error))):resolve(m.result);
};
const send=(method,params={})=>new Promise((resolve,reject)=>{
 const key=++id;pending.set(key,{resolve,reject});socket.send(JSON.stringify({id:key,method,params}));
});
const evaluate=async expression=>{
 const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
 if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);
 return r.result?.value;
};
const wait=async expression=>{
 const until=Date.now()+45000;
 while(Date.now()<until){if(await evaluate(expression))return;await new Promise(r=>setTimeout(r,100));}
 throw new Error('Timeout: '+expression+'; '+JSON.stringify(await evaluate('document.body.innerText')));
};
const click=async selector=>{
 const p=await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});if(!e)throw new Error('Missing target');e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()`);
 await send('Input.dispatchMouseEvent',{type:'mousePressed',...p,button:'left',clickCount:1});
 await send('Input.dispatchMouseEvent',{type:'mouseReleased',...p,button:'left',clickCount:1});
};
const screenshot=async(name,clip)=>{
 const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,...(clip?{clip}: {})});
 fs.writeFileSync(path.join(out,name),Buffer.from(r.data,'base64'));
};
const current=()=>evaluate('Math.abs(window.__activeFigure.runtime.getState().branchCurrents.resistor_1)');
try {
 await send('Runtime.enable');await send('Page.enable');
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 await send('Page.navigate',{url:'http://127.0.0.1:5173/@fs/'+root.replaceAll('\\','/')+'/tests/acceptance/circuit_repair.html'});
 await wait('Boolean(window.__orchestrator)');
 const doc=await send('DOM.getDocument');
 const input=await send('DOM.querySelector',{nodeId:doc.root.nodeId,selector:'#file'});
 const source=path.join(root,'storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017/00_source/original.jpg');
 await send('DOM.setFileInputFiles',{nodeId:input.nodeId,files:[source]});
 await wait("['READY_TO_SIMULATE','NEEDS_REVIEW','ERROR'].includes(window.__orchestrator.state)");
 assert.equal(await evaluate('window.__orchestrator.state'),'READY_TO_SIMULATE');
 assert.equal(await evaluate('window.__activeFigure.scene'),null,'Activation must be explicit');
 const originalEvidence=await evaluate('JSON.stringify(window.__orchestrator.bookIR)');
 await click('#start');await wait('window.__figureReady===true');
 await wait('document.querySelector(".figure-viewport-img")?.naturalWidth===1280');
 assert.equal(await current(),0);
 const snapshot=await evaluate(`(()=>{
 const f=window.__activeFigure,im=document.querySelector('.figure-viewport-img');
 const lever=document.querySelector('.circuit-layer-switches line');
 return {source:window.__orchestrator.sourceAsset,state:f.runtime.getState(),
 image:{src:im.src,width:im.naturalWidth,height:im.naturalHeight},
 arm:['x1','y1','x2','y2'].map(k=>Number(lever.getAttribute(k))),
 expectedArm:f.runtime.scene.circuit.components.find(c=>c.type==='switch').geometry.arm_source_px.flat()};
 })()`);
 assert.deepEqual(snapshot.arm,snapshot.expectedArm,'Measured open arm must survive rendering');
 assert.equal(snapshot.source.sha256,'e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63');
 const clip=await evaluate(`(()=>{const r=document.querySelector('.figure-viewport-img').getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height,scale:1};})()`);
 await screenshot('12_compiled_scene_t0_on_source.png',clip);
 await screenshot('13_browser_overlay_t0.png');
 await click('[data-el="btnPlayPause"]');
 await wait('window.__activeFigure.runtime.getState().running===true');
 assert.equal(await evaluate('document.body.innerText.includes("[object Object]")'),false);
 await click('[data-action="toggle_switch"]');
 assert.ok(Math.abs(await current()-.4)<1e-8);
 const closed=await evaluate('window.__activeFigure.runtime.getState()');
 await evaluate(`(()=>{const e=document.querySelector('[data-param-key="resistor_1"] .if-val-input');e.value='20';e.dispatchEvent(new Event('change',{bubbles:true}));})()`);
 assert.ok(Math.abs(await current()-.3)<1e-8);
 const edited=await evaluate('window.__activeFigure.runtime.getState()');
 const layouts=[];
 for(const [width,dpr] of [[900,1],[1280,2]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:dpr,mobile:false});
  await new Promise(r=>setTimeout(r,250));
  const layout=await evaluate(`(()=>{const im=document.querySelector('.figure-viewport-img').getBoundingClientRect(),sv=document.querySelector('.circuit-overlay-svg').getBoundingClientRect();return {image:[im.x,im.y,im.width,im.height],overlay:[sv.x,sv.y,sv.width,sv.height]};})()`);
  layout.width=width;layout.dpr=dpr;layouts.push(layout);
  assert.ok(layout.image.every((v,i)=>Math.abs(v-layout.overlay[i])<.1));
  await click('[data-action="toggle_switch"]');assert.equal(await current(),0);
  await click('[data-action="toggle_switch"]');assert.ok(Math.abs(await current()-.3)<1e-8);
 }
 await click('[data-el="btnReset"]');
 assert.equal(await current(),0);
 assert.equal(await evaluate('window.__activeFigure.runtime.scene.parameters.resistor_1.value'),10);
 assert.equal(await evaluate('JSON.stringify(window.__orchestrator.bookIR)'),originalEvidence);
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'browser_results.json'),JSON.stringify({mode:'offline recorded semantic/OCR replay; real browser/core services',
  initial:snapshot,closed,edited,layouts,resetCurrent:0,resetResistance:10,evidenceUnchanged:true,errors},null,2));
 console.log(JSON.stringify({pass:true,initialCurrent:0,closedCurrent:.4,editedCurrent:.3,resetCurrent:0,layouts:layouts.length,evidenceUnchanged:true}));
} catch(error){
 await screenshot('browser_failure.png');
 console.error(JSON.stringify({errors}));throw error;
} finally {socket.close();}

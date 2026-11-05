/** Browser acceptance: saved live ingest responses, fresh production review/resolve/compile and real main UI. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../..');
const out=path.join(root,'storage/generated/circuit_generalization_live');
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
const results=[];
let responseFile;
socket.addEventListener('message',async ({data})=>{
 const message=JSON.parse(data);
 if(message.method==='Fetch.requestPaused') {
  await send('Fetch.fulfillRequest',{requestId:message.params.requestId,responseCode:200,
   responseHeaders:[{name:'Content-Type',value:'application/json'}],
   body:fs.readFileSync(responseFile).toString('base64')});
 }
});
const readState=()=>evaluate('window.__activeFigure.runtime.getState()');
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);
async function upload(stem,extension,source=null) {
 responseFile=path.join(out,`${stem}_ingest.json`);
 await send('Page.navigate',{url:'http://127.0.0.1:5173/?debug=true'});
 await wait('Boolean(window.__orchestrator && window.__activeFigure)');
 await click('#btn-open-upload');
 const doc=await send('DOM.getDocument');
 const input=await send('DOM.querySelector',{nodeId:doc.root.nodeId,selector:'#file-input'});
 await send('DOM.setFileInputFiles',{nodeId:input.nodeId,files:[source || path.join(root,'tests/fixtures/circuit_generalization',`${stem}.${extension}`)]});
 await wait('!document.querySelector("#btn-generate-sim").disabled');
 await click('#btn-generate-sim');
 await wait('["READY_TO_SIMULATE","NEEDS_REVIEW","SIMULATING","ERROR"].includes(window.__orchestrator.state)');
}
try {
 await send('Runtime.enable');await send('Page.enable');
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
 await send('Fetch.enable',{patterns:[{urlPattern:'*/api/ingest',requestStage:'Request'}]});
 for(const [stem,ext,expected] of [['mixed_four_resistors','jpg',.048],['parallel_three_plate','jpeg',1]]) {
  await upload(stem,ext);
  await wait('window.__activeFigure.runtime?.scene?.domain==="circuits"');
  const state=await readState();near(Math.abs(state.totalCurrent_A),expected);
  const immutable=await evaluate('JSON.stringify(window.__orchestrator.bookIR)');
  await screenshot(`${stem}_browser.png`);
  await evaluate(`(()=>{const e=document.querySelector('[data-param-key="resistor_1"] .if-val-input');e.value=String(Number(e.value)*2);e.dispatchEvent(new Event('change',{bubbles:true}));})()`);
  assert.notEqual((await readState()).totalCurrent_A,state.totalCurrent_A);
  await click('[data-el="btnReset"]');near(Math.abs((await readState()).totalCurrent_A),expected);
  assert.equal(await evaluate('JSON.stringify(window.__orchestrator.bookIR)'),immutable);
  results.push({stem,initial:state,parameterEdit:true,reset:true,evidenceUnchanged:true});
 }
 await upload('symbolic_single_loop','png');
 await wait('window.__reviewModal.isOpen && document.querySelectorAll(".prm-policy-box").length===2');
 await screenshot('symbolic_review_browser.png');
 // Choose voltage default and enter a custom resistance using actual controls.
 const voltageSelector=await evaluate(`(()=>{const cards=[...document.querySelectorAll('.prm-issue-card')];return cards.map(c=>c.innerText);})()`);
 await evaluate(`(()=>{const boxes=[...document.querySelectorAll('.prm-policy-box')];const box=boxes.find(b=>b.innerText.includes('Voltage'));if(!box)throw Error('Missing voltage policy');box.querySelector('button').click();})()`);
 await wait('window.__orchestrator.state==="NEEDS_REVIEW" && document.querySelectorAll(".prm-policy-box").length===1');
 await evaluate(`(()=>{const form=document.querySelector('.prm-manual-form');form.querySelector('input').value='220';form.querySelector('select').value='Ω';form.querySelector('button').click();})()`);
 await wait('["READY_TO_COMPILE","READY_TO_SIMULATE"].includes(window.__orchestrator.state)');
 await click('[data-action="start-sim-banner"]');
 await wait('window.__activeFigure.runtime?.scene?.domain==="circuits"');
 const state=await readState();near(Math.abs(state.branchCurrents.resistor_1),10/220);
 await screenshot('symbolic_resolved_browser.png');
 results.push({stem:'symbolic_single_loop',voltageDefault:10,resistanceEntered:220,state});
 if(process.argv.includes('--rc')) {
  await upload('rc_synthetic_replay','png',path.join(out,'rc_synthetic_replay.png'));
  await wait('window.__reviewModal.isOpen && document.querySelectorAll(".prm-policy-box").length===1');
  await click('[data-action="apply-policy"]');
  await wait('["READY_TO_COMPILE","READY_TO_SIMULATE"].includes(window.__orchestrator.state)');
  await click('[data-action="start-sim-banner"]');
  await wait('window.__activeFigure.runtime?.getState().capacitorVoltages?.storage>2');
  await evaluate('window.__activeFigure.pause()');
  const charged=await readState();
  const immutable=await evaluate('JSON.stringify(window.__orchestrator.bookIR)');
  assert.ok(charged.capacitorVoltages.storage>2 && charged.capacitorVoltages.storage<10);
  assert.ok(await evaluate('document.querySelector(".circuit-capacitor-reading").textContent.includes("Vc =")'));
  await screenshot('rc_charge_browser.png');
  await evaluate(`(()=>{const e=document.querySelector('[data-param-key="supply"] .if-val-input');e.value='0';e.dispatchEvent(new Event('change',{bubbles:true}));window.__activeFigure.play();})()`);
  await wait(`window.__activeFigure.runtime.getState().capacitorVoltages.storage < ${charged.capacitorVoltages.storage*.7}`);
  await evaluate('window.__activeFigure.pause()');
  const discharged=await readState();
  await screenshot('rc_discharge_browser.png');
  assert.ok(discharged.branchCurrents.load<0 || discharged.branchCurrents.storage<0);
  await click('[data-el="btnReset"]');near((await readState()).capacitorVoltages.storage,0);
  assert.equal(await evaluate('JSON.stringify(window.__orchestrator.bookIR)'),immutable);
  results.push({stem:'rc_synthetic_replay',mode:'Annotated synthetic image, fresh CV/grounding and production resolution',charged,discharged,reset:true,evidenceUnchanged:true});
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'browser_results.json'),JSON.stringify({mode:'Saved live ingest responses; fresh production resolve/compile; actual main UI and runtime',results,errors},null,2));
 console.log(JSON.stringify({pass:true,cases:results.length}));
} catch(error) {
 await screenshot('browser_failure.png');console.error(await evaluate('document.body.innerText'));throw error;
} finally {socket.close();}

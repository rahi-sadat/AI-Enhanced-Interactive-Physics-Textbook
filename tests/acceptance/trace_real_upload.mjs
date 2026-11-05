/** Opt-in real UI diagnostic; sends only the four explicitly supplied files. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root = path.resolve(import.meta.dirname, '../..');
const out = path.join(root, 'storage/generated/debug_traces/20261016');
fs.mkdirSync(out, {recursive:true});
const cases = [
  ['TRACE-LENS-20261016-001','photo_2026-10-10_12-06-36 (2).jpg'],
  ['TRACE-CIRCUIT-20261016-002','photo_2026-10-10_12-06-37 (2).jpg'],
  ['TRACE-PENDULUM-20261016-003','photo_2026-10-10_12-06-38 (2).jpg'],
  ['TRACE-PRISM-20261016-004','photo_2026-10-10_12-06-37.jpg'],
].map(([id,file])=>[id+(process.env.TRACE_RUN_SUFFIX||''),file]);
const selectedIndex = process.argv[2] === undefined ? null : Number(process.argv[2]);
const selectedCases = selectedIndex === null ? cases : [cases[selectedIndex]];
const targets = await (await fetch('http://127.0.0.1:9222/json')).json();
const target = selectedIndex === null
  ? targets.find(t=>t.type==='page' && t.url.includes(':5173'))
  : await (await fetch('http://127.0.0.1:9222/json/new?'+encodeURIComponent('http://127.0.0.1:5173/?trace='+selectedCases[0][0]),{method:'PUT'})).json();
if (!target) throw new Error('Real application tab unavailable');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
let sequence=1;
const pending=new Map();
let consoleLog=[];
ws.onmessage=({data})=>{const m=JSON.parse(data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}}else if(m.method==='Runtime.consoleAPICalled'||m.method==='Runtime.exceptionThrown')consoleLog.push(m);};
const send=(method,params={})=>new Promise((resolve,reject)=>{const id=sequence++;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
const ev=async expression=>{const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result?.value;};
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const wait=async(expression,ms=30000)=>{const end=Date.now()+ms;while(Date.now()<end){if(await ev(expression))return;await delay(400);}throw new Error('Timeout: '+expression);};
const save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2));
const screenshot=async p=>{const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});fs.writeFileSync(p,Buffer.from(r.data,'base64'));};
function install(tid){
  window.__traceId=tid;
  window.__traceEvents=[];
  const copy=v=>{try{return JSON.parse(JSON.stringify(v,(k,x)=>x instanceof Element?{tag:x.tagName}:x));}catch(e){return {captureError:String(e)};}};
  const emit=(component,phase,data)=>window.__traceEvents.push({traceId:tid,component,phase,wallTime:performance.now(),data:copy(data)});
  window.__traceSnapshot=()=>{
    const fig=window.__activeFigure, orch=window.__orchestrator;
    const elements=[...document.querySelectorAll('img,canvas,svg,.figure-viewport,.figure-viewport-overlay,.if-viewport-host')].map(e=>{
      const s=getComputedStyle(e),r=e.getBoundingClientRect();
      return {tag:e.tagName,id:e.id,className:e.getAttribute('class'),src:e.currentSrc||e.src||null,naturalWidth:e.naturalWidth,naturalHeight:e.naturalHeight,width:e.width,height:e.height,viewBox:e.getAttribute('viewBox'),rect:r.toJSON(),css:Object.fromEntries(['width','height','objectFit','objectPosition','padding','margin','border','transform','transformOrigin','zoom','display','position'].map(k=>[k,s[k]]))};
    });
    return copy({traceId:tid,orchestrator:{state:orch.state,currentError:orch.currentError,bookIR:orch.bookIR,pageIR:orch.pageIR,compiledScene:orch.compiledScene,sourceAsset:orch.sourceAsset,reviewState:orch.reviewState,readinessReport:orch.readinessReport},figure:{scene:fig.scene,output:fig.runtime.getOutput(),state:fig.runtime.getState(),mapper:fig.viewport.mapper,sourceW:fig.viewport.sourceW,sourceH:fig.viewport.sourceH,renderer:fig.renderer?.constructor.name},browser:{devicePixelRatio,innerWidth,innerHeight,outerWidth,outerHeight,scrollX,scrollY,visualViewport:visualViewport?{width:visualViewport.width,height:visualViewport.height,scale:visualViewport.scale,offsetLeft:visualViewport.offsetLeft,offsetTop:visualViewport.offsetTop}:null},elements});
  };
  const originalFetch=window.fetch;
  window.fetch=async function(input,init){
    if(!String(input).startsWith('/api/'))return originalFetch.apply(this,arguments);
    const headers=new Headers(init?.headers);headers.set('X-Physics-Trace-ID',tid);
    const body=init?.body instanceof FormData?[...init.body.entries()].map(([k,v])=>({key:k,name:v.name,size:v.size,type:v.type})):init?.body;
    emit('fetch','input',{url:String(input),method:init?.method,body});
    const response=await originalFetch.call(this,input,{...init,headers});
    const text=await response.clone().text();
    emit('fetch','output',{url:String(input),status:response.status,traceId:response.headers.get('x-physics-trace-id'),body:text});
    return response;
  };
  function wrap(obj,name,label,after){
    const orig=obj?.[name];if(typeof orig!=='function')return;
    obj[name]=function(...args){
      emit(label||name,'input',args);
      const done=v=>{emit(label||name,'output',v);if(after)after(v);return v;};
      try {const result=orig.apply(this,args);return result?.then?result.then(done):done(result);}catch(e){emit(label||name,'exception',String(e));throw e;}
    };
  }
  const fig=window.__activeFigure;
  for(const name of ['startWithFile','_setState','_normalizeSceneBackground','compile','startSimulation'])wrap(window.__orchestrator,name,'SimulationOrchestrator.'+name);
  for(const name of ['load','normalizeScene','start','reset'])wrap(fig.runtime,name,'PhysicsRuntime.'+name);
  wrap(fig,'load','InteractiveFigure.load',()=>emit('t0','snapshot',window.__traceSnapshot()));
  wrap(fig.viewport,'setBackground','FigureViewport.setBackground');
  wrap(fig.viewport,'recalculate','FigureViewport.recalculate',()=>emit('FigureViewport','layout',fig.viewport.mapper));
}
try {
  await send('Runtime.enable');await send('Page.enable');
  for(const [tid,filename] of selectedCases){
    const dir=path.join(out,tid);
    if(fs.existsSync(dir))throw new Error('Trace ID already exists; set a new TRACE_RUN_SUFFIX to preserve prior evidence: '+tid);
    fs.mkdirSync(path.join(dir,'00_source'),{recursive:true});fs.mkdirSync(path.join(dir,'15_browser'),{recursive:true});
    const source=path.join('C:/Users/saher/Downloads',filename),bytes=fs.readFileSync(source);
    fs.writeFileSync(path.join(dir,'00_source/original.jpg'),bytes);
    save(path.join(dir,'00_source/file.json'),{traceId:tid,source,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length});
    await send('Page.reload',{ignoreCache:true});await delay(1800);
    await wait('Boolean(window.__orchestrator && window.__activeFigure)');
    consoleLog=[];
    await ev(`(${install.toString()})(${JSON.stringify(tid)})`);
    await ev(`(()=>{document.getElementById('btn-open-upload').click();const b=Uint8Array.from(atob(${JSON.stringify(bytes.toString('base64'))}),c=>c.charCodeAt(0));const d=new DataTransfer();d.items.add(new File([b],${JSON.stringify(filename)},{type:'image/jpeg'}));const e=document.getElementById('file-input');e.files=d.files;e.dispatchEvent(new Event('change',{bubbles:true}));})()`);
    await wait('document.getElementById("btn-generate-sim").disabled===false');
    save(path.join(dir,'15_browser/upload_preview.json'),await ev('window.__traceSnapshot()'));
    await screenshot(path.join(dir,'15_browser/upload_preview.png'));
    await ev('document.getElementById("btn-generate-sim").click()');
    console.log(tid+': uploaded through UI');
    let timedOut=false;
    try{await wait(`['SIMULATING','NEEDS_REVIEW','ERROR','UNSUPPORTED'].includes(window.__orchestrator.state)`,600000);}catch(e){timedOut=true;}
    await delay(1000);
    const snapshot=await ev('window.__traceSnapshot()');
    save(path.join(dir,'15_browser/final_state.json'),snapshot);
    await screenshot(path.join(dir,'15_browser/final_browser.png'));
    if(snapshot.orchestrator.state==='SIMULATING'){
      await ev('window.__activeFigure.dom.btnPlayPause.click();window.__activeFigure.dom.btnReset.click()');await delay(200);
      save(path.join(dir,'15_browser/runtime_t0.json'),await ev('window.__traceSnapshot()'));
      await screenshot(path.join(dir,'15_browser/runtime_t0_browser.png'));
      await ev('window.__activeFigure.dom.btnPlayPause.click()');await delay(500);
      save(path.join(dir,'15_browser/runtime_after_play.json'),await ev('window.__traceSnapshot()'));
      await screenshot(path.join(dir,'15_browser/runtime_after_play.png'));
      await ev('window.__activeFigure.pause()');
    }
    save(path.join(dir,'15_browser/events.json'),await ev('window.__traceEvents'));
    save(path.join(dir,'15_browser/console.json'),consoleLog);
    save(path.join(dir,'15_browser/result.json'),{state:snapshot.orchestrator.state,timedOut});
    console.log(tid+': '+snapshot.orchestrator.state);
    if(timedOut)throw new Error('Upload still running; preserving trace rather than contaminating next request.');
  }
} finally {ws.close();}

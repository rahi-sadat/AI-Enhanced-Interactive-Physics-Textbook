/** Read-only source-to-browser audit of the real uploaded scenes, after normal Reset. */
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../../storage/generated/debug_traces/20261016');
const targets=await (await fetch('http://127.0.0.1:9222/json')).json();
function audit(){
  const f=window.__activeFigure,o=window.__orchestrator;
  if(!o.compiledScene||f.scene?.source?.source_asset_id!==o.sourceAsset?.id)return {traceId:window.__traceId,execution:'NOT EXECUTED',reason:'No source-matched compiled scene; no startup/demo values captured.'};
  if(f.runtime.running)f.dom.btnPlayPause.click();f.dom.btnReset.click();
  const mapper=f.viewport.mapper,sim=f.runtime.adapter?.sim,points=[];
  const imageRect=f.viewport._dom.image.getBoundingClientRect();
  const add=(label,p)=>{if(!p||!Number.isFinite(p.x)||!Number.isFinite(p.y))return;const overlay=mapper.sourceToOverlay(p),view=mapper.sourceToView(p);points.push({label,source:p,view,overlay,inverse:mapper.viewToSource(view),browser:{x:imageRect.x+overlay.x,y:imageRect.y+overlay.y}});};
  const walk=(v,label)=>{if(Array.isArray(v)){v.forEach((p,i)=>walk(p,label+'['+i+']'));return;}if(!v||typeof v!=='object')return;if(Number.isFinite(v.x)&&Number.isFinite(v.y)){if(!/direction|normal|velocity|I0|I_internal|N1|N2/.test(label))add(label,v);return;}for(const [k,p]of Object.entries(v))if(!/provenance|attributes|parameters/.test(k))walk(p,label+'.'+k);};
  walk(f.scene.geometry,'scene.geometry');walk(f.scene.entities,'scene.entities');walk(f.runtime.getOutput(),'runtime.output');
  if(sim?.getBobSourcePosition){add('sim.geometry.pivot',sim.geometry.pivot);add('sim.getBobSourcePosition()',sim.getBobSourcePosition());}
  const primitiveKernel=f.runtime.adapter?.physicsKernel?Object.fromEntries(Object.entries(f.runtime.adapter.physicsKernel).filter(([k,v])=>typeof v!=='function'&&k!=='listeners')):null;
  return {traceId:window.__traceId,execution:'EXECUTED',mapper,imageRect:imageRect.toJSON(),landmarks:points,mechanics:sim?{geometry:sim.geometry,theta:sim.theta,bobSource:sim.getBobSourcePosition?.(),mapper:sim.mapper,kernel:primitiveKernel}:null,snapshot:window.__traceSnapshot()};
}
for(const t of targets.filter(t=>t.type==='page'&&t.url.includes('NATIVE-RETRY-20261017'))){
  const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
  let id=0;const pending=new Map();ws.onmessage=({data})=>{let m=JSON.parse(data);if(pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id);}};
  const send=(method,params={})=>new Promise(r=>{pending.set(++id,r);ws.send(JSON.stringify({id,method,params}));});
  try{const r=await send('Runtime.evaluate',{expression:`(${audit.toString()})()`,returnByValue:true});if(r.result.exceptionDetails)throw Error(JSON.stringify(r.result.exceptionDetails));const d=r.result.result.value;fs.mkdirSync(path.join(root,d.traceId,'14_renderer'),{recursive:true});fs.writeFileSync(path.join(root,d.traceId,'14_renderer/coordinate_audit.json'),JSON.stringify(d,null,2));console.log(JSON.stringify({traceId:d.traceId,landmarks:d.landmarks?.length,mechanics:d.mechanics}));}finally{ws.close();}
}

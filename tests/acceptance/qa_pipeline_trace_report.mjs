/** Visual QA of saved local HTML only. */
import fs from 'node:fs';
const root='D:/AugmentedPhysics/storage/generated/debug_traces/20261017';
const targets=['INDEX.html',...JSON.parse(fs.readFileSync(root+'/summary.json')).map(r=>r.report)];
const results=[];
for(let k=0;k<targets.length;k++){
  const url=new URL(targets[k],'file:///'+root+'/').href;
  const t=await (await fetch('http://127.0.0.1:9222/json/new?'+encodeURIComponent(url),{method:'PUT'})).json();
  const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);let id=0;const pending=new Map();
  ws.onmessage=({data})=>{const m=JSON.parse(data);if(pending.has(m.id)){pending.get(m.id)(m.result);pending.delete(m.id);}};
  const send=(method,params={})=>new Promise(r=>{pending.set(++id,r);ws.send(JSON.stringify({id,method,params}));});
  try{await new Promise(r=>setTimeout(r,800));await send('Page.bringToFront');const a=await send('Runtime.evaluate',{expression:'({title:document.title,overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src)})',returnByValue:true});results.push(a.result.value);const shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(root+`/visual_qa_${k}.png`,Buffer.from(shot.data,'base64'));}finally{ws.close();}
}
fs.writeFileSync(root+'/browser_report_qa.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results));

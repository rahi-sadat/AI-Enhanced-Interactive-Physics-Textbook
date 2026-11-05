/** Read-only capture of the real trace tabs; no application values changed. */
import fs from 'node:fs';
import path from 'node:path';
const out=path.resolve(import.meta.dirname,'../../storage/generated/debug_traces/20261016');
const targets=await (await fetch('http://127.0.0.1:9222/json')).json();
for(const t of targets.filter(t=>t.type==='page'&&t.url.includes(':5173'))){
  const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
  let id=1;const pending=new Map();
  ws.onmessage=({data})=>{const m=JSON.parse(data);if(pending.has(m.id)){pending.get(m.id)(m.result);pending.delete(m.id);}};
  const send=(method,params={})=>new Promise(r=>{const k=id++;pending.set(k,r);ws.send(JSON.stringify({id:k,method,params}));});
  const response=await send('Runtime.evaluate',{expression:'window.__traceSnapshot ? {snapshot:window.__traceSnapshot(),events:window.__traceEvents} : null',returnByValue:true});
  const data=response?.result?.value;
  if(data?.snapshot?.traceId){
    const folder=path.join(out,data.snapshot.traceId,'15_browser');fs.mkdirSync(folder,{recursive:true});
    fs.writeFileSync(path.join(folder,'pending_state.json'),JSON.stringify(data.snapshot,null,2));
    fs.writeFileSync(path.join(folder,'events.json'),JSON.stringify(data.events,null,2));
    await send('Page.bringToFront');
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
    fs.writeFileSync(path.join(folder,'pending_browser.png'),Buffer.from(shot.data,'base64'));
    console.log(data.snapshot.traceId+': '+data.snapshot.orchestrator.state);
  }
  ws.close();
}

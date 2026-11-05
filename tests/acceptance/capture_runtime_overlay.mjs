/** Capture the existing real renderer on the original source, using measured DOM transforms.
 * Uses only normal Pause/Reset UI controls. No solver/scene/coordinate values are changed.
 */
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../../storage/generated/debug_traces/20261016');
const tid=process.argv[2];
const targets=await (await fetch('http://127.0.0.1:9222/json')).json();
const t=targets.find(t=>t.type==='page'&&t.url.includes('trace='+tid));
if(!t)throw new Error('Trace tab not available: '+tid);
const ws=new WebSocket(t.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let id=1;const pending=new Map();
ws.onmessage=({data})=>{const m=JSON.parse(data);if(pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}};
const send=(method,params={})=>new Promise((resolve,reject)=>{const k=id++;pending.set(k,{resolve,reject});ws.send(JSON.stringify({id:k,method,params}));});
const ev=async expression=>{const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result?.value;};
async function capture(){
  const fig=window.__activeFigure;
  const image=fig.viewport._dom.image;
  const imageRect=image.getBoundingClientRect();
  const canvas=document.createElement('canvas');canvas.width=image.naturalWidth;canvas.height=image.naturalHeight;
  const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0);
  const scaleX=canvas.width/imageRect.width,scaleY=canvas.height/imageRect.height;
  const transforms=[];const svgs=[];const canvases=[];
  for(const el of fig.viewport.getOverlayContainer().querySelectorAll('svg,canvas')){
    if(el.parentElement.closest('svg'))continue;
    const rect=el.getBoundingClientRect();
    const dest={x:(rect.x-imageRect.x)*scaleX,y:(rect.y-imageRect.y)*scaleY,width:rect.width*scaleX,height:rect.height*scaleY};
    transforms.push({tag:el.tagName,rect:rect.toJSON(),imageRect:imageRect.toJSON(),scaleX,scaleY,dest});
    if(el.tagName.toLowerCase()==='canvas'){
      const png=el.toDataURL('image/png');canvases.push(png);
      ctx.drawImage(el,dest.x,dest.y,dest.width,dest.height);
    }else{
      const clone=el.cloneNode(true);const originals=[el,...el.querySelectorAll('*')];const clones=[clone,...clone.querySelectorAll('*')];
      for(let i=0;i<clones.length;i++){
        const style=getComputedStyle(originals[i]);
        for(const key of ['fill','fill-opacity','stroke','stroke-width','stroke-opacity','stroke-dasharray','stroke-linecap','opacity','font-family','font-size','font-weight','text-anchor','visibility','display'])clones[i].style.setProperty(key,style.getPropertyValue(key));
      }
      clone.setAttribute('xmlns','http://www.w3.org/2000/svg');clone.setAttribute('width',rect.width);clone.setAttribute('height',rect.height);clone.style.width=rect.width+'px';clone.style.height=rect.height+'px';
      const xml=new XMLSerializer().serializeToString(clone);svgs.push({original:el.outerHTML,rendered:xml,viewBox:el.getAttribute('viewBox')});
      const url=URL.createObjectURL(new Blob([xml],{type:'image/svg+xml'}));const raster=new Image();raster.src=url;
      await raster.decode();ctx.drawImage(raster,dest.x,dest.y,dest.width,dest.height);URL.revokeObjectURL(url);
    }
  }
  return {overlay:canvas.toDataURL('image/png'),svgs,canvases,transforms,snapshot:window.__traceSnapshot()};
}
try{
  await send('Page.bringToFront');
  const valid=await ev(`Boolean(window.__orchestrator.compiledScene && window.__activeFigure.scene?.source?.source_asset_id === window.__orchestrator.sourceAsset?.id)`);
  if(!valid)throw new Error('No source-matched uploaded scene; refusing startup/demo capture.');
  await ev(`(()=>{const f=window.__activeFigure;if(f.runtime.running)f.dom.btnPlayPause.click();f.dom.btnReset.click();})()`);
  await new Promise(r=>setTimeout(r,150));
  const data=await ev(`(${capture.toString()})()`);
  const dir=path.join(root,tid,'14_renderer');fs.mkdirSync(dir,{recursive:true});
  fs.writeFileSync(path.join(dir,'runtime_t0_overlay.png'),Buffer.from(data.overlay.split(',')[1],'base64'));delete data.overlay;
  data.canvases.forEach((png,i)=>fs.writeFileSync(path.join(dir,`canvas_${i}.png`),Buffer.from(png.split(',')[1],'base64')));delete data.canvases;
  data.svgs.forEach((svg,i)=>{fs.writeFileSync(path.join(dir,`actual_svg_${i}.svg`),svg.original);fs.writeFileSync(path.join(dir,`computed_style_svg_${i}.svg`),svg.rendered);});
  fs.writeFileSync(path.join(dir,'runtime_t0_capture.json'),JSON.stringify(data,null,2));
  const shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(dir,'runtime_t0_browser.png'),Buffer.from(shot.data,'base64'));
  console.log(JSON.stringify({traceId:tid,state:data.snapshot.figure.state,transforms:data.transforms}));
}finally{ws.close();}

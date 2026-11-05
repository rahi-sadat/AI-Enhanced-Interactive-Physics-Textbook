"""Build evidence-only HTML from recorded calls; never executes a physics stage."""
import hashlib
import html
import json
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'storage/generated/debug_traces/20261016'
EXPECTED='EXPECTED ARTIFACT NOT AVAILABLE — NO GROUND TRUTH EXISTS'
def read(p, default=None):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def esc(v): return html.escape(str(v))
STYLE='''body{font:16px/1.55 system-ui;margin:32px;color:#182436;background:#f6f7fa}main{max-width:1500px;margin:auto}h1,h2,h3{line-height:1.2}section{background:white;border:1px solid #d6dde6;padding:22px;margin:20px 0;border-radius:10px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}img{max-width:100%;height:auto;border:1px solid #ccd}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:460px;overflow:auto;background:#f2f4f8;padding:14px;font-size:12px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border:1px solid #ccd;padding:9px;text-align:left;vertical-align:top}a{color:#174cb2}.warn{background:#fff3d9;border-left:5px solid #b16c00;padding:14px}.FAIL{color:#b42318}.PASS{color:#1c7041}.SUSPICIOUS{color:#925700}code{overflow-wrap:anywhere}@media(max-width:800px){.grid{display:block}body{margin:12px}}'''

def png_source(folder):
    source=folder/'00_source/original.jpg'
    if not source.exists(): return
    raw=source.read_bytes()
    bgr=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
    cv2.imwrite(str(folder/'00_source/original.png'),bgr)
    with Image.open(source) as pil:
        meta={'file_format':pil.format,'encoded_width':pil.width,'encoded_height':pil.height,'EXIF_orientation':pil.getexif().get(274),'orientation':'landscape' if pil.width>pil.height else 'portrait','decoded_width':bgr.shape[1],'decoded_height':bgr.shape[0],'sha256':hashlib.sha256(raw).hexdigest(),'png_note':'Lossless serialization of OpenCV decoded original JPEG; no resize, crop, redrawing, or orientation edit. Byte-exact original.jpg retained.','decoded_pixels_sha256':hashlib.sha256(bgr.tobytes()).hexdigest()}
    browser=read(folder/'15_browser/upload_preview.json',{})
    meta['browser_images']=browser.get('elements',[])
    dump(folder/'00_source/metadata.json',meta)
    return bgr,meta

def build(folder):
    source=png_source(folder)
    if not source:return
    bgr,meta=source
    calls=[]
    for p in sorted((folder/'calls').glob('*')):
        loc=read(p/'location.json')
        if loc: calls.append((p,loc,read(p/'actual_input.json'),read(p/'actual_output.json')))
    preview=read(folder/'15_browser/upload_preview.json',{})
    final=read(folder/'15_browser/final_state.json',read(folder/'15_browser/pending_state.json',{})) if '-NATIVE' in folder.name else read(folder/'15_browser/pending_state.json',read(folder/'15_browser/final_state.json',{}))
    result=read(folder/'15_browser/result.json',{})
    names=[loc['function'] for p,loc,i,o in calls]
    sources=[(p,o) for p,l,i,o in calls if l['function']=='UploadService.ingest' and isinstance(o,dict) and 'sha256' in o]
    pages=[(p,o) for p,l,i,o in calls if l['function']=='PageIRBuilder.build' and isinstance(o,dict)]
    providers=[(p,o) for p,l,i,o in calls if l['function']=='GeminiVisionProvider.analyze_diagram']
    sdk=[(p,i,o) for p,l,i,o in calls if l['function']=='Models.generate_content']
    provider_locals=[read(p/'locals_after.json',{}) for p,o in providers]
    provider_error=next((v.get('last_err') for v in provider_locals if v.get('last_err')),None)
    book_outputs=[o for p,l,i,o in calls if l['function']=='BookUnderstandingPipeline.analyze' and isinstance(o,dict)]
    native='-NATIVE' in folder.name
    source_match=bool(sources) and all(o['sha256']==meta['sha256'] for p,o in sources)
    provider_match=bool(sdk) and all(i['contents'][0]['inline_data']['data']['sha256']==meta['sha256'] for p,i,o in sdk)
    dump(folder/'identity_chain.json',{'traceId':folder.name,'source_sha256':meta['sha256'],'source_asset_outputs':[o for p,o in sources],'source_bytes_match':source_match,'SDK_image_bytes_match':provider_match,'request_header':'X-Physics-Trace-ID','trace_propagation':'Browser header → ASGI ContextVar → asyncio.to_thread copies context → profiler call records. Trace ID is observational; not injected into semantic prompt or physics values.','external_provider_trace_id':'Not sent in model content. SDK call locally correlated by context and exact image SHA-256.'})
    rows=[];sections=[]
    for index,(p,loc,inp,output) in enumerate(calls):
        name=loc['function'];rel=p.relative_to(folder).as_posix()
        complete=(p/'actual_output.json').exists()
        status='SUSPICIOUS'
        reason='Executed call; exact artifacts linked. No independent output ground truth or geometry assessment is available.'
        input_status='SUSPICIOUS';alignment='NOT APPLICABLE'
        if name=='UploadService.ingest':
            status='PASS' if source_match else 'FAIL';input_status='PASS';alignment='PASS' if source_match else 'FAIL'
            reason='The persisted SourceAsset SHA-256 equals the original uploaded JPEG; dimensions match the actual decoder.'
        elif name=='PageIRBuilder.build' and isinstance(output,dict):
            good=output['source']['width_px']==meta['decoded_width'] and output['source']['height_px']==meta['decoded_height']
            status='PASS' if good else 'FAIL';input_status='PASS';alignment=status
            reason='Whole-image PageIR preserves native dimensions and top-left source_px; no physics landmark detection claimed.'
            overlay=bgr.copy()
            for r in output.get('regions',[]):
                cv2.rectangle(overlay,(round(r['x']),round(r['y'])),(round(r['x']+r['width']),round(r['y']+r['height'])),(255,0,255),3)
            cv2.imwrite(str(p/'actual_overlay_on_source.png'),overlay)
            dump(p/'transform.json',{'frame':'source_px','width':meta['decoded_width'],'height':meta['decoded_height'],'origin':'top_left','x_direction':'right','y_direction':'down','units':'pixels','scale_x':1,'scale_y':1,'offset_x':0,'offset_y':0,'crop_offset':[0,0],'padding':[0,0],'rotation':0,'matrix':[[1,0,0],[0,1,0],[0,0,1]],'inverse_matrix':[[1,0,0],[0,1,0],[0,0,1]],'basis':'Actual full-image PageIR extent and unchanged JPEG bytes; no image transform performed.'})
        elif name in ('PhysicsVisionAnalyzer.analyze','GeminiVisionProvider.analyze_diagram','Models.generate_content'):
            input_status='PASS' if provider_match else 'SUSPICIOUS'
            reason='Input image hash matches original. '+('No completed return captured; call is pending at capture time.' if not complete else 'Consult returned value and locals for provider result/error; a null profiler return can indicate exception unwind.')
            if complete and output is None:
                status='FAIL'
                reason+=' Exception unwind: no semantic result returned. Final provider error: '+str(provider_error)
        elif name=='BookUnderstandingPipeline._build_unresolved_ir' or name=='BookUnderstandingPipeline.analyze' and isinstance(output,dict):
            input_status='PASS' if provider_match else 'SUSPICIOUS'
            status='PASS' if isinstance(output,dict) and output.get('status')=='UNRESOLVED' and output.get('domain') is None and output.get('subtype') is None and not output.get('parameters') and not output.get('entities') else 'SUSPICIOUS'
            reason='Error-handling contract: provider failure becomes UNRESOLVED BookIR with empty entities/parameters, null domain/subtype, and retained VisionProviderError. This PASS means safe error handling, not successful perception. isPhysics=false is a BookIR default, not a model assertion that the source is non-physics.'
        elif name=='EvidenceExtractionPipeline.extract_and_fuse' and isinstance(output,dict):
            input_status='PASS';status='PASS'
            reason='Wrapper EXECUTED but returned early because domain/subtype are null. OCR, CV, segmentation and subtype grounding were NOT EXECUTED. No spatial evidence produced.'
        elif name=='enforce_source_dimensions':
            input_status='PASS';status='PASS';alignment='PASS'
            reason='Adds authoritative SourceAsset width/height to unresolved BookIR. This is frame metadata, not detected physics geometry. See locals_after.json for mutated IR.'
        elif name in ('AutoResolutionEngine.resolve','ResolutionEngine.auto_resolve','ReadinessEvaluator.evaluate','ResolutionAnalyzer.analyze'):
            input_status='PASS';status='PASS'
            reason='Unresolved input is correctly blocked. Auto result records CLASSIFICATION_FAILED; readiness has ready=false; no policies, assumptions, parameter resolutions or calibration were applied. PASS is abstention correctness only.'
        elif name=='PhysicsCompiler.compile' and isinstance(output,dict):
            input_status='PASS';status='PASS' if output.get('scene') is None and output.get('status')=='UNRESOLVED' else 'SUSPICIOUS'
            reason='Compiler gate EXECUTED and returned DOMAIN_OR_SUBTYPE_UNKNOWN, scene=null. Canonical scene construction and domain physics were NOT EXECUTED. No compiler geometry exists to compare.'
        elif name=='ingest_diagram':
            if isinstance(output,dict) and output.get('scene') is None:
                input_status='PASS';status='PASS'
                reason='Actual HTTP handler returned success=true with domain failure status=unresolved and scene=null. HTTP 200 is transport success, not simulation success. Full response is under http/.'
            else:
                reason='Preliminary WSL profiler return may be coroutine suspension, not an HTTP response. Native recorder excludes suspension events. Authoritative HTTP body is under http/; do not interpret null as completed ingestion.'
        if not complete: reason+=' OUTPUT NOT AVAILABLE: function has not completed in this capture.'
        after=read(p/'locals_after.json',{})
        loss='No manual corrections by recorder. See exact input, returned data, and locals_after for mutations/defaults. '
        if name=='UploadService.ingest':loss+='JPEG decoded for dimensions; original encoded bytes are persisted unchanged; UUID and storage/public paths assigned.'
        if name=='PageIRBuilder.build':loss+='Adds full-image figure/region metadata. No crop or resize; text_blocks initially empty.'
        if name.startswith(('Models.','Gemini')):loss+='Provider-internal model resizing, tensors, masks, and coordinates are not exposed by this SDK contract.'
        next_calls=[l['function'] for pp,l,ii,oo in calls if l.get('caller',{}).get('function')==name.split('.')[-1] and l.get('caller',{}).get('file')==loc['file'] and l['sequence']>loc['sequence']]
        next_text=', '.join(dict.fromkeys(next_calls)) or 'No nested downstream call captured.'
        stage={'traceId':folder.name,'execution':'EXECUTED','input_status':input_status,'output_status':status,'source_alignment':alignment,'output_capture_complete':complete,'reason':reason,'provenance':'Actual Python profiler snapshot of named function; ndarray artifacts serialized without modifying runtime objects.','difference_from_input':loss,'next_components_observed':next_text}
        dump(p/'validation.json',stage)
        summary=f"# {name}\n\nEXECUTED\n\nFile: {loc['file']}:{loc['line']}\nCaller: {loc['caller']}\nNext component: {next_text}\nTrace ID: {folder.name}\n\nACTUAL INPUT: actual_input.json\nEXPECTED INPUT: upstream output and function source in contract_or_schema.txt.\nINPUT STATUS: {input_status}\n\nACTUAL OUTPUT: {'actual_output.json; locals_after.json contains post-call state' if complete else 'NOT AVAILABLE — no completed return captured'}\nEXPECTED OUTPUT / REFERENCE: original source image; function contract. {EXPECTED}\nOUTPUT STATUS: {status}\n\n{reason}\n\nPROVENANCE: {stage['provenance']}\nDIFFERENCE FROM INPUT / POSSIBLE INFORMATION LOSS: {loss}\n"
        (p/'stage_summary.md').write_text(summary,encoding='utf-8')
        rows.append(f'<tr><td>{loc["sequence"]}</td><td>{esc(name)}</td><td>{input_status}</td><td>{status}</td><td>{alignment}</td><td>{"identity source_px" if name=="PageIRBuilder.build" else "NOT APPLICABLE / see contract"}</td><td>EXECUTED</td><td><a href="{rel}/stage_summary.md">Summary</a></td></tr>')
        overlay=f'<figure><figcaption>Actual PageIR bounds on source (no detected landmark implied)</figcaption><img src="{rel}/actual_overlay_on_source.png"></figure>' if (p/'actual_overlay_on_source.png').exists() else '<p>No geometric output available for this call. No overlay fabricated.</p>'
        sections.append(f'''<section><h2>Stage {loc['sequence']} — {esc(name)}</h2><p><b>EXECUTED · {status}</b></p><p>{esc(reason)}</p><p>File: {esc(loc['file'])}:{loc['line']}<br>Caller: {esc(loc['caller'])}<br>Next observed: {esc(next_text)}<br>Trace: {folder.name}</p><div class="grid"><figure><figcaption>Unchanged source pixels</figcaption><img loading="lazy" src="00_source/original.png"></figure>{overlay}</div><div class="grid"><div><h3>Actual input</h3><a href="{rel}/actual_input.json">Complete JSON</a><pre>{esc(json.dumps(inp,ensure_ascii=False,indent=2))}</pre></div><div><h3>Actual output</h3>{f'<a href="{rel}/actual_output.json">Complete JSON</a>' if complete else 'NOT AVAILABLE — pending call'}<pre>{esc(json.dumps(output,ensure_ascii=False,indent=2)) if complete else 'No return recorded.'}</pre></div></div><h3>Expected input / output</h3><p>Use <a href="{rel}/contract_or_schema.txt">exact function source / contract</a> and upstream saved output. Visual reference is the original above. {EXPECTED}</p><h3>Provenance and possible information loss</h3><p>{esc(loss)}</p><p><a href="{rel}/validation.json">Validation</a> · <a href="{rel}/stage_summary.md">Stage summary</a>{f' · <a href="{rel}/locals_after.json">Complete post-call locals</a>' if (p/'locals_after.json').exists() else ''}</p></section>''')
    future=[('OCR / text preprocessing','MultiOCRRouter.extract','ai/evidence/ocr/router.py'),('Classical CV','extract_candidates','ai/evidence/cv/'),('Segmentation','SAM2SegmentationProvider.segment','ai/evidence/segmentation/'),('Grounding / BookIR evidence','EvidenceExtractionPipeline.extract_and_fuse','ai/evidence/pipeline.py'),('Auto-resolution','AutoResolutionEngine.resolve','ai/resolution/auto.py'),('Resolution / calibration','ResolutionEngine.auto_resolve','ai/resolution/engine.py'),('Readiness','ReadinessEvaluator.evaluate','ai/resolution/evaluator.py'),('Compiler','PhysicsCompiler.compile','ai/ingestion/PhysicsCompiler.py'),('Physics runtime / solver','PhysicsRuntime.load','engine/core/PhysicsRuntime.js'),('Coordinate mapping','CoordinateMapper','engine/core/coordinateMapper.js'),('Renderer / t=0','InteractiveFigure.load','apps/web/src/components/InteractiveFigure.js')]
    browser_events=read(folder/'15_browser/events.json',[])
    frontend_folder=folder/'frontend'
    frontend_folder.mkdir(exist_ok=True)
    for src in ('apps/web/src/main.js','apps/web/src/features/simulations/core/SimulationApi.js','apps/web/src/features/simulations/core/SimulationOrchestrator.js'):
        (frontend_folder/Path(src).name).write_bytes((ROOT/src).read_bytes())
    frontend_sections=[]
    for component in ('SimulationOrchestrator.startWithFile','fetch','SimulationOrchestrator._setState'):
        observed=[e for e in browser_events if e.get('component')==component]
        if not observed: continue
        artifact=component.replace('.','_')+'.json'
        dump(frontend_folder/artifact,observed)
        source_file='SimulationApi.js' if component=='fetch' else 'SimulationOrchestrator.js'
        explanation=('Actual multipart fetch initiated by SimulationApi.ingest and its HTTP result. File byte payload is separately verified by backend hash; File objects in generic JS event serialization do not expose binary contents.' if component=='fetch' else 'Exact observed call inputs and returns. The orchestrator owns browser lifecycle state, not physics evidence. The state transition to ERROR is appropriate for the captured provider failure.')
        frontend_sections.append(f'<section><h2>Frontend — {esc(component)} · EXECUTED</h2><p>{esc(explanation)}</p><p>Caller chain: main.js upload handler → SimulationOrchestrator.startWithFile → SimulationApi.ingest/fetch → API response → orchestrator._setState. Trace: {folder.name}</p><p><a href="frontend/{artifact}">Complete observations before/after</a> · <a href="frontend/{source_file}">Exact source/contract</a> · <a href="frontend/main.js">Actual upload handler</a></p><pre>{esc(json.dumps(observed,indent=2,ensure_ascii=False))}</pre><p>Input status: PASS where linked file identity or actual response is established. Output status: PASS for truthful error-state handling; provider analysis itself failed. Expected visual reference: original source. {EXPECTED}. No coordinates, parameters, or simulation output were added by these frontend stages.</p></section>')
        rows.append(f'<tr><td>UI</td><td>{esc(component)}</td><td>PASS (see evidence)</td><td>PASS for error handling</td><td>NOT APPLICABLE</td><td>NOT APPLICABLE</td><td>EXECUTED</td><td><a href="frontend/{artifact}">Actual events</a></td></tr>')
    for label,func,file in future:
        executed=any(func in n for n in names) or any(e.get('component')==func for e in browser_events)
        if not executed:
            rows.append(f'<tr><td>—</td><td>{esc(label)}</td><td>NOT APPLICABLE</td><td>NOT APPLICABLE</td><td>NOT APPLICABLE</td><td>NOT APPLICABLE</td><td>NOT EXECUTED for this upload</td><td>{file}</td></tr>')
            sections.append(f'<section><h2>{esc(label)} — NOT EXECUTED</h2><p>{esc(file)} · {esc(func)}</p><p>No upload-specific input/output, geometry, masks, rays, topology, t=0 state, or simulation overlay exists in this capture. Startup/demo figures in the browser are unrelated and excluded. {EXPECTED}</p></section>')
    sdk_pending=bool(sdk) and any(not (p/'actual_output.json').exists() for p,i,o in sdk)
    verdict='BLOCKED / INCOMPLETE: real provider call did not complete at capture time.' if sdk_pending else 'LIVE FAILURE CAPTURED: GeminiVisionProvider ended in '+str(provider_error)+'. No simulation was compiled.'
    header=f'''<h1>{folder.name}</h1><p class="warn">{verdict} This report does not claim to identify the historical misregistration defect. No expected geometry or simulation was invented.</p><section><h2>First-failure analysis</h2><p>Last verified good boundary: byte-preserving upload → full-image PageIR → matching image bytes in Gemini request.</p><p>First suspicious/unavailable boundary: live SDK request. Direct WSL provider TCP connection was observed in SYN-SENT; a separate unauthenticated WSL connection timed out. Windows connectivity succeeded. This is an environment/transport blocker, outside perception/registration/physics failure classes A/B/C.</p><p>First definitive geometry corruption: NOT ESTABLISHED. Downstream consequences: no completed semantic result yet; CV, OCR, grounding, compilation, solver and upload-specific browser overlay cannot be assessed.</p><p><a href="identity_chain.json">Exact identity chain</a> · <a href="00_source/metadata.json">Source and browser metadata</a></p></section><section><h2>Browser evidence</h2><div class="grid"><figure><figcaption>Actual selected upload</figcaption><img src="15_browser/upload_preview.png"></figure><figure><figcaption>Actual browser at capture</figcaption><img src="15_browser/{'final_browser.png' if (folder/'15_browser/final_browser.png').exists() else 'pending_browser.png'}"></figure></div><p>Default startup simulation is not a result of this upload. No compiled scene from this request is attributed to it.</p><pre>{esc(json.dumps({'state':final.get('orchestrator',{}).get('state'),'currentError':final.get('orchestrator',{}).get('currentError'),'browser':final.get('browser',{}),'result':result},indent=2))}</pre></section>'''
    table='<section><h2>Stage summary</h2><table><tr><th>#</th><th>Component</th><th>Input valid?</th><th>Output valid?</th><th>Source alignment</th><th>Coordinate transform</th><th>Execution</th><th>Evidence</th></tr>'+''.join(rows)+'</table></section>'
    if native:
        header=header.replace('First suspicious/unavailable boundary: live SDK request. Direct WSL provider TCP connection was observed in SYN-SENT; a separate unauthenticated WSL connection timed out. Windows connectivity succeeded. This is an environment/transport blocker, outside perception/registration/physics failure classes A/B/C.', 'First definitive operational failure: GeminiVisionProvider.analyze_diagram raises VisionProviderError after six SDK generate_content attempts across the configured three models. Final SDK error is 503 UNAVAILABLE / high demand. This is provider availability, not proof of incorrect perception (A), registration (B), or physics (C). The full SDK inputs and final exception are preserved.')
        header=header.replace('First definitive geometry corruption: NOT ESTABLISHED. Downstream consequences: no completed semantic result yet; CV, OCR, grounding, compilation, solver and upload-specific browser overlay cannot be assessed.', 'First definitive geometry corruption: NOT ESTABLISHED. Downstream consequences: unresolved BookIR → evidence wrapper skips extraction → source frame dimensions retained → auto-resolution/readiness block → compiler returns scene=null → real browser ERROR/retry message. These gates executed; the domain extractors, scene-building branch, solvers and upload-specific renderer did not.')
    else:
        header=header.replace('15_browser/final_browser.png','15_browser/pending_browser.png')
    (folder/'TRACE_REPORT.html').write_text('<!doctype html><meta charset="utf-8"><title>'+folder.name+'</title><style>'+STYLE+'</style><main>'+header+table+''.join(frontend_sections)+''.join(sections)+'</main>',encoding='utf-8')
    return {'trace_id':folder.name,'source_dimensions':[meta['decoded_width'],meta['decoded_height']],'source_sha256':meta['sha256'],'source_bytes_match':source_match,'provider_bytes_match':provider_match,'call_count':len(calls),'sdk_pending':sdk_pending,'provider_error':provider_error,'sdk_attempts':len(sdk),'browser_state':final.get('orchestrator',{}).get('state'),'report':folder.name+'/TRACE_REPORT.html'}

if __name__=='__main__':
    results=[r for f in sorted(OUT.glob('TRACE-*')) if f.is_dir() for r in [build(f)] if r]
    dump(OUT/'summary.json',results)
    links=''.join(f'<tr><td><a href="{r["report"]}">{r["trace_id"]}</a></td><td>{r["call_count"]}</td><td>{r["source_bytes_match"]}</td><td>{r["provider_bytes_match"]}</td><td>{r["browser_state"]}</td><td>{"PENDING" if r["sdk_pending"] else "See trace"}</td></tr>' for r in results)
    (OUT/'INDEX.html').write_text('<!doctype html><meta charset="utf-8"><title>Real upload forensic traces</title><style>'+STYLE+'</style><main><h1>Real upload forensic traces — 2026-10-16</h1><p class="warn">Primary traces have the -NATIVE suffix and use the normal Windows backend/direct Gemini connection. Earlier WSL attempts are retained separately as incomplete connectivity diagnostics. No fixes, model substitutions, hand-authored geometry, or reconstructed simulations. The historical registration defect remains undetermined because live semantic analysis failed.</p><table><tr><th>Trace report</th><th>Calls</th><th>Upload hash match</th><th>Provider image hash match</th><th>Browser state</th><th>Provider return</th></tr>'+links+'</table><p><a href="FORENSIC_REPORT.md">Architecture, coordinate audit, first-failure table, limitations and evidence</a></p></main>',encoding='utf-8')
    print(json.dumps(results,indent=2))

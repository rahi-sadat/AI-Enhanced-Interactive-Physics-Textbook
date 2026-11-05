"""Build forensic reports exclusively from saved real-request artifacts. No pipeline rerun."""
import hashlib
import html
import json
import os
from pathlib import Path
import re
import cv2
import numpy as np
from build_trace_report import STYLE, png_source, read, dump

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'storage/generated/debug_traces/20261016'
OUT = ROOT / 'storage/generated/debug_traces/20261017'
EXPECTED = 'EXPECTED ARTIFACT NOT AVAILABLE — NO GROUND TRUTH EXISTS'
esc = lambda s: html.escape(str(s))
CASES = {
 'LENS': {
  'title':'Convex lens', 'cv':'ThinLensCVCandidateExtractor.extract',
  'first':'OCR edge masking erases part of the incident ray beside the Object label; CV subsequently omits the printed object arrow and selects a partial lens centerline.',
  'good':'Source identity, semantic subtype and selected OCR focal-length text (15 cm).',
  'suspicious':'Secondary OCR misreads the focal label; router retains the correct RapidOCR result. The Object OCR box (188,220,135,57) is valid text evidence, but its four-pixel expansion reaches adjacent ray geometry.',
  'cv_detail':'Returned lens_center=(641,432), lens_line=(641,423)→(641,189), object_arrow=null. The partial line becomes aperture_height_px=234. The original shows an object arrow and a full lens; the selected overlay exposes this loss.',
  'ground':'Grounder retains the center/partial aperture and observes focal_length=0.15 m from OCR, but does not ground the object or printed focal-marker spacing.',
  'auto':'_normalize_lens_focal_length substitutes aperture×0.5=117 px as focal length. _normalize_lens_exploration_object supplies objectDistance=234 px and objectHeight=81.9 px despite the semantic object already being present in the source. These are auto_policy assumptions, not observed placements. No user accepted them during this trace.',
  'compile':'Compiler carries lens_center=(641,432), f=117, u=234 into the scene and normalizes objectHeight to −81.9 in source Y-down coordinates. Runtime object base=(407,432), tip=(407,350.1); image is x=875, height=81.9. Model output is consistent with the substituted parameters, not registered to the original object/rays.',
  'runtime':'Thin-lens runtime returns u=234, v=234, magnification=−1. No numerical solver defect is established. The actual t=0 renderer makes already incorrect source geometry visible.'},
 'CIRCUIT': {
  'title':'Series DC circuit','cv':'CircuitCVCandidateExtractor.extract',
  'first':'CV promotes fragmented evidence into full horizontal rails across source gaps and empty interior.',
  'good':'Exact source, semantic dc_linear classification and OCR 12 V / 10 Ω / 20 Ω.',
  'suspicious':'Raw line candidates include the current annotation shaft and open-switch arm as wire candidates.',
  'cv_detail':'components=[]; branches_x=[231,992]; rails_y=[255,416,668]. Returned rails span x=231→992 at all three Y values. y=416 crosses empty circuit interior; y=255 bridges the open switch/components. The implementation accepts a span with more than ten edge pixels, without requiring continuous wire support.',
  'ground':'CircuitGrounder creates R2 at (1149,416), with horizontal terminals (1115,416)/(1183,416), near the OCR label instead of the vertical resistor. It creates R1=(757,255), V1=(231,457), but nodes and component node lists are empty. Renaming semantic entity IDs to R1/R2/V1 leaves old relationship endpoints dangling. The switch is not grounded.',
  'auto':'Auto-resolution cannot establish two-node component connections. Readiness blocks compilation. The source shows an open switch; neither a closed-circuit current nor a synthetic topology was supplied for this audit.',
  'compile':'Compiler gate returns scene=null. Browser subsequently calls /api/resolution/compile after NEEDS_REVIEW; HTTP 400 “BookIR is not ready to compile” becomes UI ERROR. This is a separate frontend handling defect after the perception failure.',
  'runtime':'Circuit solver/MNA, uploaded-scene renderer and t=0 overlay NOT EXECUTED. Do not interpret startup/demo state as this uploaded circuit. No current result exists.'},
 'PENDULUM': {
  'title':'Simple pendulum','cv':'PendulumCVCandidateExtractor.extract_candidates',
  'first':'CV accepts a pivot above the detected support while reporting the disagreement in its own validation metadata.',
  'good':'Exact source, correct semantic pendulum roles and symbolic OCR; no printed numeric length/mass is claimed.',
  'suspicious':'Selected visible string begins at (556,67), extending into the mounting hatch region.',
  'cv_detail':'Selected pivot=(562,79.23811193908072), bob=(841.3633806409911,649.0514992664916), radius=37.03476174228877. Method vertical_reference_intersection reports support_residual_px=16.761888060919276 yet is_geometrically_consistent=true. The consistency predicate checks vertical-reference and string residuals but omits support_residual. The source and selected overlay show the misplaced mounting point.',
  'ground':'SAM2 independently finds bob centroid=(841.8054054054054,650.2034594594595), bbox=(804,612,75,76), area=4625. Grounder retains the CV bob/pivot; CV–SAM agreement is about 1.23 px. SAM verifies the bob, not the pivot. String length is rounded from 634.6110579092531 to 634.61 px.',
  'auto':'Length=1 m, mass=1 kg, gravity=9.80665 m/s² and damping=0 are policy values. L and m in the source are symbols, not evidence for those numbers. Calibration derives from policy length, so it is not a measured textbook scale.',
  'compile':'Compiler preserves pivot and 634.61-pixel string; initialAngle=26.117406100584446°. The actual runtime reset kernel has theta=0.45583472853565193 rad and simTime=0. Its own getBobSourcePosition() returns (841.3629149366802,649.0505493762439). The tiny bob difference is rounding; the pivot error was already in CV.',
  'runtime':'MechanicsAdapter → PendulumKernel / PendulumSimulation. t=0 bob is source-aligned while pivot is above the printed support. No integration defect is established; physical time-scale accuracy has no numeric source ground truth.'},
 'PRISM': {
  'title':'Glass prism','cv':'PrismCVCandidateExtractor.extract',
  'first':'OCR edge masking erases prism-side pixels around A=60°; CV then infers an incorrect base from sloped-segment extents.',
  'good':'Exact source, correct prism semantics and OCR A=60°. Raw edges before OCR suppression retain the source boundaries.',
  'suspicious':'The axis-aligned A=60° OCR box (556,184,128,49) and its four-pixel expansion intersect the slanted prism boundary. Later contour detection yields best_area=0; rays also includes body edges and normals.',
  'cv_detail':'Fallback left_max_y=771 and right_max_y=743 yield base_y=(771+743)/2=757. Actual horizontal base candidates remain around y=766–773 in the same output. Returned vertices are (621.3,80.9),(229.2,757),(1003.9,757). The selected polygon visibly lies above the printed base. Incident segment (47,456)→(237,420) is retained correctly.',
  'ground':'Grounder preserves polygon and incident ray, records OCR apex angle=60°, but does not ground internal/emergent ray entities. Raw detected ray segments remain in evidence, not constraints for the runtime solution.',
  'auto':'A refractive index of 1.52 is auto-policy glass, not printed evidence. Existing incident origin/direction are retained; this run did NOT use a default horizontal incident ray.',
  'compile':'Compiler preserves CV vertices and incident input. Runtime recomputes refraction using n=1.52: hit1=(447.8163870862532,380.0386653684882), hit2=(807.0350434576367,409.11605562391077). The computed internal/emergent rays disagree visibly with the source. This is model re-synthesis from assumptions and incomplete observed ray constraints, not a proven Snell-law implementation error.',
  'runtime':'Optics runtime reports incidence=40.842553023013416°, refraction=25.48353691375652°, deviation=39.754070946628936°, no TIR. Exact solver output and actual SVG are saved.'}
}

def link(base, target): return os.path.relpath(target, base).replace('\\','/')
def pre(v): return '<pre>'+esc(json.dumps(v,ensure_ascii=False,indent=2))+'</pre>'
def page(title, body): return '<!doctype html><html><head><meta charset="utf-8"><title>'+esc(title)+'</title><style>'+STYLE+'</style></head><body><main><h1>'+esc(title)+'</h1>'+body+'</main></body></html>'
def data_links(base, folder):
    return ' · '.join(f'<a href="{link(base,p)}">{esc(p.name)}</a>' for p in folder.iterdir() if p.is_file() and p.suffix in ('.json','.txt','.npy','.bin'))

def geometry_overlay(source, value, dest):
    """Only draw explicitly typed points/lines/boxes/polygons; never guess array bbox convention."""
    img=source.copy(); inventory=[]; seen=set()
    def point(p): return isinstance(p,dict) and isinstance(p.get('x'),(int,float)) and isinstance(p.get('y'),(int,float))
    def xy(p): return (round(p['x']),round(p['y']))
    def mark(kind,coords,label,draw):
        key=json.dumps([kind,coords],sort_keys=True)
        if key in seen:return
        seen.add(key); inventory.append({'kind':kind,'path':label,'coordinates':coords});draw()
    def walk(v,label):
        if any(k in label.lower() for k in ('vlmapproxbbox','direction','normal_vector','provenance','parameter_associations')):return
        if isinstance(v,list):
            for i,x in enumerate(v):walk(x,f'{label}[{i}]')
        elif isinstance(v,dict):
            if 'shape' in v and 'artifact' in v:return
            if point(v.get('start')) and point(v.get('end')):
                mark('line',[v['start'],v['end']],label,lambda:cv2.line(img,xy(v['start']),xy(v['end']),(255,0,200),2))
            elif isinstance(v.get('points'),list) and len(v['points'])>=3 and all(point(p) for p in v['points']):
                mark('polygon',v['points'],label,lambda:cv2.polylines(img,[np.array([xy(p) for p in v['points']],np.int32)],True,(255,120,0),2))
            elif point(v) and all(isinstance(v.get(k),(int,float)) for k in ('width','height')):
                mark('bbox_xywh',v,label,lambda:cv2.rectangle(img,xy(v),(round(v['x']+v['width']),round(v['y']+v['height'])),(0,160,255),2))
            elif point(v.get('center')) and isinstance(v.get('radius_px'),(int,float)):
                mark('circle',{'center':v['center'],'radius_px':v['radius_px']},label,lambda:cv2.circle(img,xy(v['center']),round(v['radius_px']),(0,160,255),2))
            elif point(v):
                mark('point',v,label,lambda:cv2.drawMarker(img,xy(v),(0,0,255),cv2.MARKER_CROSS,12,2))
            for k,x in v.items():
                if k not in ('start','end','points') and not (point(v) and k in ('x','y')):walk(x,label+'.'+k)
    walk(value,'output')
    if inventory:
        cv2.imwrite(str(dest),img);dump(dest.with_suffix('.json'),{'frame':'source_px','source_shape':list(source.shape),'scale':[1,1],'offset':[0,0],'geometry':inventory,'note':'Rasterization rounds only when drawing. JSON retains original precision. Orange boxes/circles, magenta lines, blue polygons, red points. Array-valued ambiguous boxes are not guessed.'})
    return len(inventory)

def delta(a,b,path=''):
    if type(a)!=type(b):return [{'path':path,'before':a,'after':b}]
    if isinstance(a,dict):
        out=[]
        for k in sorted(a.keys()|b.keys()):
            if k not in a:out.append({'path':path+'/'+k,'added':b[k]})
            elif k not in b:out.append({'path':path+'/'+k,'removed':a[k]})
            else:out.extend(delta(a[k],b[k],path+'/'+k))
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [{'path':path,'before':a,'after':b}]
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in delta(x,y,path+'/'+str(i))]
    return [] if a==b else [{'path':path,'before':a,'after':b}]

def assessment(name,c):
    if name=='mask_out_text_regions' and c['title']=='Glass prism':
        return 'PASS','FAIL','First demonstrated geometric information loss: masking the A=60° box (556,184,128,49), margin=4, erases slanted prism-side pixels. Other label masks also remove angle/normal strokes. Saved removed-edge overlay proves the loss; it does not prove this is the sole cause of contour failure or the later base error.'
    if name=='mask_out_text_regions' and c['title']=='Convex lens':
        return 'PASS','FAIL','First demonstrated geometric information loss: Object bbox=(188,220,135,57), margin=4 masks through exclusive y=281. Removed-edge overlay shows incident-ray pixels erased beside the label. This does not by itself prove why the vertical object arrow is later omitted; that is a separate CV failure.'
    if name==c['cv']:return 'PASS','FAIL',c['cv_detail']
    if name.endswith('Grounder.ground'):return 'FAIL','FAIL',c['ground']
    if name.startswith('AutoResolutionEngine.'):
        return 'FAIL','FAIL' if c['title']=='Convex lens' else 'SUSPICIOUS',c['auto']
    if name=='ReadinessEvaluator.evaluate':
        return 'FAIL','PASS' if c['title']=='Series DC circuit' else 'FAIL',('Blocks missing topology correctly.' if c['title']=='Series DC circuit' else 'READY is not proof of source registration: this evaluator checks resolved requirements, units/ranges, provenance and analyzer issues, but never compares the scene to image pixels. Auto-policy values may satisfy opt-in requirements via resolvedBy=auto_policy.')
    if name=='PhysicsCompiler.compile':return 'FAIL','PASS' if c['title']=='Series DC circuit' else 'SUSPICIOUS',c['compile']
    if name in ('UploadService.ingest','PageIRBuilder.build'):return 'PASS','PASS','Exact original bytes and full native frame retained; identity chain checked separately.'
    if name in ('MultiOCRRouter.extract','PhysicsVisionAnalyzer.analyze','GeminiVisionProvider.analyze_diagram','BookUnderstandingPipeline.analyze'):
        return 'PASS','PASS','Accepted semantics/text agree at the domain and parameter-label level. Full raw output is retained; this PASS does not certify every label/relationship or any source geometry.'
    if name=='SAM2SegmentationProvider.segment':return 'SUSPICIOUS','PASS',c['ground']
    if name in ('preprocess_diagram','preprocess_for_geometry','mask_out_text_regions'):
        return 'PASS','SUSPICIOUS','Native image dimensions preserved. Grayscale, blur, Canny and OCR suppression remove image information; exact before/after arrays and removed-edge overlay are linked. No manually repaired edge map.'
    return 'SUSPICIOUS','SUSPICIOUS','Executed helper recorded for completeness. Status means no independent correctness verdict, not a proven defect. Use parent-stage verdict, exact function contract and before/after artifacts.'

def build(folder,c):
    source,meta=png_source(folder)
    calls=[]
    for p in sorted((folder/'calls').iterdir()):
        loc=read(p/'location.json')
        if loc:calls.append((p,loc,read(p/'actual_input.json'),read(p/'actual_output.json'),read(p/'locals_after.json',{})))
    source_match=[];sdk_match=[];rows=[];main=[];landmarks=[]
    for p,loc,inp,out,after in calls:
        n=loc['function']
        if n=='UploadService.ingest' and isinstance(out,dict):source_match.append(out.get('sha256')==meta['sha256'])
        if n=='Models.generate_content':
            try:sdk_match.append(inp['contents'][0]['inline_data']['data']['sha256']==meta['sha256'])
            except (KeyError,TypeError,IndexError):sdk_match.append(False)
        ins,outs,reason=assessment(n,c)
        nexts=list(dict.fromkeys(l['function'] for _,l,_,_,_ in calls if l.get('caller',{}).get('file')==loc['file'] and l.get('caller',{}).get('function')==n.split('.')[-1] and l['sequence']>loc['sequence']))
        important= n in (c['cv'],'PageIRBuilder.build','MultiOCRRouter.extract','SAM2SegmentationProvider.segment','EvidenceExtractionPipeline.extract_and_fuse','AutoResolutionEngine.resolve','PhysicsCompiler.compile','ReadinessEvaluator.evaluate','BookUnderstandingPipeline.analyze','Models.generate_content','GeminiVisionProvider.analyze_diagram','PhysicsVisionAnalyzer.analyze','enforce_source_dimensions','preprocess_diagram','preprocess_for_geometry','mask_out_text_regions') or n.endswith('Grounder.ground')
        overlay=None
        if important:
            spatial=out
            if n==c['cv']:
                geometry_overlay(source,out,p/'all_candidates_overlay.png')
                spatial={k:v for k,v in (out or {}).items() if k not in ('all_lines','all_circles','paired_candidates','pin_candidates','rays','circle_candidates','line_candidates','bob_candidates','string_candidates','joint_candidates','pivot_candidates')}
            if geometry_overlay(source,spatial,p/'actual_overlay_on_source.png'):overlay=p/'actual_overlay_on_source.png'
        if n=='mask_out_text_regions':
            a=inp.get('edge_map',{});b=out or {}
            if a.get('artifact') and b.get('artifact'):
                before=np.load(RAW/a['artifact']);end=np.load(RAW/b['artifact']);removed=(before!=0)&(end==0)
                diagnostic=source.copy();diagnostic[removed]=(0,0,255);cv2.imwrite(str(p/'removed_edges_on_source.png'),diagnostic)
                dump(p/'removed_edges.json',{'removed_pixel_count':int(removed.sum()),'frame':'source_px','before':a,'after':b,'red':'Pixels removed by actual OCR suppression; not an assertion that every removed pixel was wrong.'})
        if n=='SAM2SegmentationProvider.segment' and after.get('mask_u8',{}).get('artifact'):
            mask=np.load(RAW/after['mask_u8']['artifact']);mask=np.squeeze(mask)>0
            visual=source.copy();visual[mask]=(visual[mask].astype(float)*.5+np.array([255,0,0])*.5).astype(np.uint8)
            cv2.imwrite(str(p/'actual_mask_on_source.png'),visual)
        if n=='AutoResolutionEngine.resolve':dump(p/'field_changes.json',delta(inp['book_ir'],out['book_ir']))
        if n=='PhysicsCompiler.compile':dump(p/'ir_to_scene.json',{'IR':inp['book_ir'],'scene':(out or {}).get('scene'),'interpretation':c['compile']})
        if important:landmarks.append({'component':n,'input':inp,'output':out})
        validation={'traceId':folder.name,'execution':'EXECUTED','input_status':ins,'output_status':outs,'reason':reason,'next_observed':nexts,'coordinate_frame':'source_px for authoritative geometry; VLM approximate boxes quarantined, physical quantities carry units','dimensions':[1280,960],'origin':'top_left','x_direction':'right','y_direction':'down','transform':'Identity at application-level image/CV/IR boundary; no app crop or resize. Internal model transforms are not exposed by this recorder.'}
        dump(p/'validation.json',validation)
        diffnote='Complete input/output and post-call locals preserve mutations, rounding and policy provenance. No modifications to the runtime data were made by this reporter.'
        if n=='AutoResolutionEngine.resolve':diffnote+=' field_changes.json lists every changed/added/removed field.'
        imgs=''.join(f'<figure><figcaption>{esc(f.name)}</figcaption><img loading="lazy" src="{f.name}"></figure>' for f in p.glob('*source.png'))
        if (p/'all_candidates_overlay.png').exists():imgs+='<figure><figcaption>All returned candidates (not all selected)</figcaption><img loading="lazy" src="all_candidates_overlay.png"></figure>'
        arrays=[]
        def array_refs(v):
            if isinstance(v,dict):
                if 'image' in v and 'artifact' in v:arrays.append(v)
                for x in v.values():array_refs(x)
            elif isinstance(v,list):
                for x in v:array_refs(x)
        array_refs(inp);array_refs(out);array_refs(after)
        arrlinks=''.join(f'<a href="{link(p,RAW/v["image"])}">actual array image {esc(v.get("shape"))}</a> · ' for v in {v['image']:v for v in arrays}.values())
        text=f'<p>EXECUTED · trace {folder.name}</p><p>File: {esc(loc["file"])}:{loc["line"]}<br>Caller: {esc(loc.get("caller"))}<br>Next observed: {esc(nexts)}</p><p>INPUT {ins} / OUTPUT {outs}: {esc(reason)}</p><p>{data_links(p,p)}</p><div class="grid"><div><h2>Actual input</h2>{pre(inp)}</div><div><h2>Actual output</h2>{pre(out)}</div></div><h2>Expected input / output</h2><p>Expected input is the upstream actual output and the saved function contract. Structural reference: contract_or_schema.txt. Visual reference: <a href="{link(p,folder/"00_source/original.png")}">unchanged original</a>. No independently annotated expected geometry or expected physics parameters exist: {EXPECTED}.</p><h2>Provenance, changes and possible loss</h2><p>{esc(diffnote)}</p>{pre(validation)}<p>{arrlinks}</p><div class="grid">{imgs}</div>'
        (p/'STAGE.html').write_text(page(n,text),encoding='utf-8')
        rows.append(f'<tr><td>{loc["sequence"]}</td><td><a href="{link(folder,p/"STAGE.html")}">{esc(n)}</a></td><td>{ins}</td><td>{outs}</td><td>EXECUTED</td></tr>')
        if important:
            main.append(f'<section><h2>{loc["sequence"]}. {esc(n)}</h2><p>Input {ins}; output {outs}. {esc(reason)}</p><p><a href="{link(folder,p/"STAGE.html")}">Full before/after, contract, caller, next calls, provenance and images</a></p>'+(f'<img loading="lazy" src="{link(folder,overlay)}">' if overlay else '')+'</section>')
    events=read(folder/'15_browser/events.json',[])
    frontend=folder/'frontend';frontend.mkdir(exist_ok=True)
    for component in dict.fromkeys(e.get('component') for e in events):
        if not component:continue
        dump(frontend/(re.sub(r'[^a-zA-Z0-9_-]','_',component)+'.json'),[e for e in events if e.get('component')==component])
    contracts=['apps/web/src/main.js','apps/web/src/components/InteractiveFigure.js','engine/core/PhysicsRuntime.js','engine/core/coordinateMapper.js','engine/mechanics/MechanicsAdapter.js','engine/mechanics/pendulumSimulation.js','ai/resolution/evaluator.py','ai/resolution/analyzer.py']
    for src in contracts:
        f=ROOT/src
        if f.exists():(frontend/(src.replace('/','__')+'.txt')).write_bytes(f.read_bytes())
    dump(folder/'stage_landmark_chain.json',landmarks)
    identity={'trace_id':folder.name,'original_sha256':meta['sha256'],'upload_byte_identity':bool(source_match) and all(source_match),'SDK_image_byte_identity':bool(sdk_match) and all(sdk_match),'sdk_attempts':len(sdk_match),'call_count':len(calls),'same_request':'Browser X-Physics-Trace-ID → ASGI context → asyncio.to_thread → Python profiler. SDK image SHA ties semantic request to original. ID is not inserted into semantic model content. Frontend events and compiled source_asset_id bind solver/renderer.'}
    dump(folder/'identity_chain.json',identity)
    final=read(folder/'15_browser/final_state.json',{})
    result=read(folder/'15_browser/result.json',{})
    audit=read(folder/'14_renderer/coordinate_audit.json',{})
    render='<p>NOT EXECUTED: no source-matched scene, solver, MNA or t=0 overlay. Scene remains null.</p>' if c['title']=='Series DC circuit' else '<img src="14_renderer/runtime_t0_overlay.png"><p><a href="14_renderer/runtime_t0_capture.json">Actual renderer/SVG/DOM capture</a> · <a href="15_browser/runtime_after_play.json">Actual later runtime frame (use recorded time)</a></p>'
    summary=f'<p class="warn">FIRST DEFINITIVE FAILURE: {esc(c["first"])}</p><p>Last known good: {esc(c["good"])}</p><p>First suspicious: {esc(c["suspicious"])}</p><p>{esc(c["auto"])}</p><p>{esc(c["compile"])}</p><p>{esc(c["runtime"])}</p>'
    summary+=f'<section><h2>Source identity</h2>{pre(identity)}<img src="00_source/original.png"><p><a href="00_source/metadata.json">Dimensions, EXIF and original pixel metadata</a></p></section>'
    summary+='<section><h2>Actual t=0 on original source</h2>'+render+'</section><section><h2>Frontend and coordinate audit</h2><p><a href="14_renderer/coordinate_audit.json">Every captured source→mapper→inverse→browser landmark</a> · <a href="15_browser/events.json">Complete frontend input/output events</a> · <a href="15_browser/final_state.json">Complete browser state and CSS</a> · <a href="stage_landmark_chain.json">Full CV→IR→compiler chain</a></p>'+pre({'result':result,'mapper':audit.get('mapper'),'imageRect':audit.get('imageRect'),'landmarks':audit.get('landmarks'),'mechanics':audit.get('mechanics')})+'</section>'
    summary+='<section><h2>Coverage and limitations</h2><p>All captured Python calls are indexed below, with exact input/output, locals and function source. SUSPICIOUS on helper calls means unverified, not failed. Profiling is restricted to repository code and GenAI model boundary; OpenCV C internals, OCR neural preprocessing, SAM tensor preprocessing and private provider tensors were not traced. Internal SDK/model preprocessing transforms are unavailable, not assumed identity. Some profiler null returns are exception unwinds; use HTTP result and caller locals. Two class-serialization recorder errors occurred during circuit module imports; reported primary stage snapshots are present. Browser adapter initialization and renderer internals were observed via runtime boundary, output, DOM and saved source, not individually instrumented function-by-function. Native screen coordinates/browser chrome zoom are unavailable; measured CSS layout, DPR and visualViewport are recorded. No exact 0.5/1.0-second frame is claimed. Report overlays are annotations of actual values, not ground truth corrections.</p><p>SAM segmentation: '+('EXECUTED for bob only.' if c['title']=='Simple pendulum' else 'NOT EXECUTED in this domain path.')+'</p></section>'
    (folder/'TRACE_REPORT.html').write_text(page(c['title']+' — '+folder.name,summary+''.join(main)+'<section><h2>Every captured executed call</h2><table><tr><th>Sequence</th><th>Component</th><th>Input</th><th>Output</th><th>Execution</th></tr>'+''.join(rows)+'</table></section>'),encoding='utf-8')
    return {'case':c['title'],'trace_id':folder.name,'state':result.get('state'),'identity':identity,'report':link(OUT,folder/'TRACE_REPORT.html'),'mapper':audit.get('mapper'),'first_failure':c['first']}

def main():
    OUT.mkdir(exist_ok=True)
    results=[]
    for key,c in CASES.items():
        folder=next(RAW.glob('TRACE-'+key+'-*-NATIVE-RETRY-20261017'))
        existing=read(OUT/'summary.json',[])
        previous=next((r for r in existing if r['case']==c['title']),None)
        import sys
        results.append(previous if '--refresh-lens' in sys.argv and key!='LENS' and previous else build(folder,c))
    dump(OUT/'summary.json',results)
    table='<table><tr><th>Diagram / full report</th><th>Browser</th><th>First failure</th><th>Calls</th></tr>'+''.join(f'<tr><td><a href="{r["report"]}">{r["case"]}</a></td><td>{r["state"]}</td><td>{esc(r["first_failure"])}</td><td>{r["identity"]["call_count"]}</td></tr>' for r in results)+'</table>'
    md=['# 1. Active Runtime Architecture','Real native Windows frontend at port 5173 → standard Vite proxy → native FastAPI at 8000 → existing direct Gemini SDK connection. No TLS tunnel. Four unique real browser upload requests on 2026-10-17; prior 2026-10-16 provider-503 runs are historical and do not describe these successful semantic runs.','`main.js → SimulationOrchestrator.startWithFile → SimulationApi.ingest → /api/ingest → UploadService.ingest → PageIRBuilder.build → asyncio.to_thread(BookUnderstandingPipeline.analyze → PhysicsVisionAnalyzer.analyze → GeminiVisionProvider.analyze_diagram → Models.generate_content) → EvidenceExtractionPipeline.extract_and_fuse → MultiOCRRouter.extract → domain CV → optional SAM2 bob segmentation → domain Grounder → enforce_source_dimensions → AutoResolutionEngine.resolve → ResolutionEngine.auto_resolve / ReadinessEvaluator.evaluate → ai/ingestion/PhysicsCompiler.py → response → orchestrator → InteractiveFigure.load → FigureViewport / PhysicsRuntime.normalizeScene / load → domain adapter → solver → actual renderer.`','`ai/scene_compiler/physics_compiler.py` is a re-export; compiler execution is in `ai/ingestion/PhysicsCompiler.py`. Mechanics uses MechanicsAdapter/PendulumSimulation; optics uses registry SVG renderers. main.js automatically calls startSimulation after successful load in this executed path. Circuit follows NEEDS_REVIEW → review API → an attempted compile → HTTP 400 → ERROR. No circuit solver runs.','Every backend call has file/function/caller/next observed calls, saved function contract and exact before/after artifacts in its STAGE.html. Frontend event boundaries and full actual DOM/runtime captures are linked per case.']
    for i,(key,c) in enumerate(CASES.items(),2):
        r=results[i-2]
        md += [f'# {i}. Trace Results — Diagram {i-1}: {c["title"]}',f'[{r["trace_id"]}]({r["report"]})',f'Last known good: {c["good"]}',f'First suspicious: {c["suspicious"]}',f'First definitive failure: {c["first"]}',c['cv_detail'],c['ground'],c['auto'],c['compile'],c['runtime']]
    md+=['# 6. Coordinate Transformation Audit','Original JPEGs and lossless original.png are 1280×960, no EXIF orientation; source bytes match the upload and the SDK inline image for every request. Application geometry uses source_px, origin top-left, X right, Y down. No application crop/resize offset was introduced. Model-internal transforms remain unavailable.','Measured t=0 lens image/SVG rectangle=(139,227,800,600), mapper scale=.625. Pendulum image/canvas and prism image/SVG rectangle=(219,227,640,480), scale=.5. DPR=1; viewBox=0 0 1280 960 for optics. Source-to-overlay is (s*x,s*y); source-to-browser adds the measured image origin. Inverse mapping is captured by actual CoordinateMapper.viewToSource, with full precision per landmark in coordinate_audit.json. No manual alignment or changed solver coordinates.','Pendulum pivot stays (562,79.23811193908072) through CV, grounding, compiled scene and runtime. The runtime bob is (841.3629149366802,649.0505493762439); the original CV bob differs only by rounding the stored length. Lens center stays (641,432), while object base/tip are created by policy/compiler. Prism vertices stay unchanged from CV to scene to SVG. Circuit has no source-matched browser mapper/solver; no startup demo evidence is substituted.','The existing mapper correctly places the supplied points in all three runnable cases. This does not validate those points against the textbook. Private preprocessing tensors and native screen-pixel/browser-chrome coordinates: '+EXPECTED+'.', '# 7. First-Failure Table','| Diagram | First definitive component | Failure class | Downstream consequence |','|---|---|---|---|','| Lens | ThinLensCVCandidateExtractor.extract | A perception, then assumption-based reconstruction | Missing object/partial aperture → assumed focal/object placement → wrong t=0 rays |','| Circuit | CircuitCVCandidateExtractor.extract | A perception/topology | False rails → misplaced component terminals / missing graph → readiness blocks |','| Pendulum | PendulumCVCandidateExtractor.extract_candidates | A perception | Pivot fails support agreement → copied into IR/scene → displaced mounting point |','| Prism | PrismCVCandidateExtractor.extract | A perception, then model re-synthesis | Side-extents base inference → shifted polygon; assumed n yields different ray |','# 8. Cross-Diagram Root Cause','No single shared CSS-coordinate defect is established. Every case has domain-specific classical CV selection or reconstruction failure. Semantic classification succeeds for all four; these traces do not support blaming Gemini classification for the geometry. Grounding propagates weak geometry and, for circuits, introduces additional wrong placement and dangling relationship IDs.','Mechanics-only: support residual is recorded but excluded from pivot consistency. Optics-only: lens physical OCR focal length loses authority to an uncalibrated pixel policy; prism observed internal/emergent rays are not runtime constraints. Circuit-only: synthetic rails, empty topology, label-driven component placement and relationship mismatch.','Shared readiness weakness across the three runnable cases: checks concern required values, units/ranges, provenance and unresolved issues; they do not establish pixel registration. Auto-policy may satisfy requirements without human acceptance. Circuit topology is correctly blocked. Shared frontend issue observed: automatic simulation activation; circuit attempts compile after NEEDS_REVIEW and surfaces an error.','Compiler preserves already-wrong geometry or creates model geometry from assumptions. No independently proven C-class numerical solver defect. Source physical ground truth for mass/length/index is absent; behavior correctness cannot be inferred from animation alone.','# 9. Evidence','Full HTML reports above contain stage overlays, input/output JSON, arrays/masks, contracts, provenance, deltas, source SHA chains and actual runtime screenshots. Every new trace remains under `../20261016/<trace>-NATIVE-RETRY-20261017/`; date in directory is the recorder session root, not a claim that these requests ran on October 16.','Per trace: `00_source/original.jpg`, `original.png`, `metadata.json`; `calls/<sequence_component>/actual_input.json`, `actual_output.json`, `locals_after.json`, `contract_or_schema.txt`, `STAGE.html`, overlays; `arrays/*.npy`; `http/`; `15_browser/events.json`, final_state and runtime frames; `14_renderer/coordinate_audit.json`, actual SVG/canvas and runtime_t0_overlay.png where compiled. Auto-resolution has field_changes.json; compiler has ir_to_scene.json. Full stage_landmark_chain.json retains values before and after all key boundaries.','Coverage limitations: profiler did not intercept internal C/neural-library operations or every JS function. Original and application boundary arrays are preserved; unavailable private tensors and transforms are explicitly not reconstructed. Two recorder errors during class serialization are retained in the raw log; major stage I/O exists. No arbitrary expected diagram or numerical ground truth was authored. Later-frame timestamps are actual saved state, not exact requested 0.5/1.0 seconds. The source itself is the sole visual reference.','Verification: prior unchanged production working tree passed frontend 17 test commands and Python unit/integration 247 tests. Those were offline, separate from explicitly live acceptance traces. No production fix, parameter correction or physics algorithm change was made. Existing user changes remain untouched.','# 10. Root Cause Ranking','1. Strongest: CV output contradicted by source and/or its own candidates: circuit fabricated spans; pendulum ignored support residual; prism averaged side endpoints into an unsupported base; lens missing object/partial lens.','2. Strong: lens auto-policy reconstructs printed geometry; circuit grounding misplaces R2 and invalidates relationship references.','3. Strong: readiness admits complete, provenance-bearing values without a source-registration check.','4. Strong mechanism, limited physical ground truth: prism ray re-synthesis from assumed refractive index and incomplete observed constraints.','5. Downstream UX: circuit compile attempt despite NEEDS_REVIEW; automatic activation.','6. Not supported as root cause by these captures: shared CSS/mapper shift, DPR mismatch, Gemini domain misclassification, or numerical integrator/Snell/MNA implementation defect.']
    report='\n\n'.join(md)+'\n'
    report=report.replace('| Lens | ThinLensCVCandidateExtractor.extract | A perception, then assumption-based reconstruction | Missing object/partial aperture → assumed focal/object placement → wrong t=0 rays |', '| Lens | mask_out_text_regions, followed by ThinLensCVCandidateExtractor.extract | A preprocessing/perception, then assumption-based reconstruction | OCR margin erases ray pixels; CV misses object/partial aperture → assumed placement → wrong t=0 rays |')
    report=report.replace('Every case has domain-specific classical CV selection or reconstruction failure.', 'Every case has domain-specific classical CV selection or reconstruction failure. The earliest demonstrated lens information loss is OCR edge masking, before those CV selections; its causal connection to the missing object arrow is not proven.')
    report=report.replace('| Prism | PrismCVCandidateExtractor.extract | A perception, then model re-synthesis | Side-extents base inference → shifted polygon; assumed n yields different ray |', '| Prism | mask_out_text_regions, followed by PrismCVCandidateExtractor.extract | A preprocessing/perception, then model re-synthesis | OCR masking removes side pixels; side-extents inference shifts base; assumed n yields different ray |')
    report=report.replace('No single shared CSS-coordinate defect is established.', 'No single shared CSS-coordinate defect is established. Lens and prism share demonstrated geometric edge loss in OCR masking. Masked-out pixels are shown directly on each original; causality from that loss to every later detector error is not established.')
    (OUT/'FORENSIC_REPORT.md').write_text(report,encoding='utf-8')
    docs=ROOT/'docs/reports/DIAGRAM_PIPELINE_FORENSICS_20261017.md'
    docs_report=report
    for r in results:docs_report=docs_report.replace(']('+r['report']+')',']('+link(docs.parent,OUT/r['report'])+')')
    docs_report+='\n[Open the HTML evidence index]('+link(docs.parent,OUT/'INDEX.html')+').\n'
    docs.write_text(docs_report,encoding='utf-8')
    body='<p class="warn">Four fresh real requests completed. Three reproduce t=0 source misregistration; circuit is blocked before simulation. Diagnostic only: no production fixes.</p>'+table+'<p><a href="FORENSIC_REPORT.md">Full ten-section forensic report</a> · <a href="summary.json">Machine-readable summary</a></p>'
    walkthroughs=ROOT/'docs/reports/pipeline_walkthroughs_20261017'
    if (walkthroughs/'INDEX.html').exists():
        body='<section><h2>Read each diagram from beginning to end</h2><p>34 ordered stages per diagram, with actual input, expected input, actual output, expected output, evidence and the effect on the next component.</p><p>'+ ' · '.join(f'<a href="{link(OUT,walkthroughs/key.lower()/"WALKTHROUGH.html")}">{esc(c["title"])}</a>' for key,c in CASES.items())+'</p><p><a href="'+link(OUT,walkthroughs/'INDEX.html')+'">All complete debugging documents (HTML and Markdown)</a></p></section>'+body
    for key,c in CASES.items():body+='<section><h2>'+c['title']+'</h2><p>'+esc(c['cv_detail'])+'</p><p>'+esc(c['auto'])+'</p></section>'
    (OUT/'INDEX.html').write_text(page('Diagram → simulation forensic audit — 2026-10-17',body),encoding='utf-8')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()

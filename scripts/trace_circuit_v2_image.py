"""Record real Circuit V2 stages and native-source diagnostic images.

Explicit local acceptance CLI. It observes production functions without replacing
any detector, OCR, segmentation, grounder, compiler or numerical solver.
"""
import argparse
from collections import defaultdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    def save(name,value):
        (args.output/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
    source=args.source.resolve();source_bytes=source.read_bytes()
    digest=hashlib.sha256(source_bytes).hexdigest()
    (args.output/('00_original'+source.suffix.lower())).write_bytes(source_bytes)
    import cv2
    import numpy as np
    import torch
    from apps.api.main import _get_ingestion_pipeline
    from ai.perception.circuits.v2_experiment import run_experiment
    from tests.acceptance.circuit_v2_real_acceptance import plain
    from ai.evidence.grounding.circuits import parse_and_cluster_circuit_tokens
    image=cv2.imdecode(np.frombuffer(source_bytes,np.uint8),cv2.IMREAD_COLOR)
    assert image is not None
    torch.set_num_threads(4)
    save('00_execution',dict(source_path=str(source),source_sha256=digest,source_width=image.shape[1],source_height=image.shape[0],
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        working_diff_sha256=hashlib.sha256(subprocess.check_output(['git','diff'],cwd=ROOT)).hexdigest(),
        packages={**{p:importlib.metadata.version(p) for p in ('torch','torchvision','ultralytics','rapidocr')},'opencv_module':cv2.__version__},
        cuda_available=torch.cuda.is_available(),device='cpu',real_inference=True,providers_replaced=False))
    captures={};calls=defaultdict(list);started={}
    selected={
        'UploadService.py':{'ingest'},'PageIRBuilder.py':{'build'},
        'router.py':{'extract'},'circuits_cv.py':{'extract'},
        'circuit_geometry_validator.py':{'validate'},'circuit_prompts.py':{'segment_circuit_candidates'},
        'circuits.py':{'fuse'},'circuit_graph.py':{'build_conductor_graph','build_geometric_conductor_graph'},
        'mna_solver.py':{'solve_dc'},'PhysicsCompiler.py':{'compile'},
        'circuit_ocr_refinement.py':{'refine_circuit_ocr'}}
    def observe(frame,event,value):
        file=Path(frame.f_code.co_filename).name;fn=frame.f_code.co_name
        if fn not in selected.get(file,set()):return
        if event=='call':started[id(frame)]=time.perf_counter();return
        if event!='return':return
        duration=(time.perf_counter()-started.pop(id(frame),time.perf_counter()))*1000
        calls[file+':'+fn].append(dict(duration_ms=round(duration,2),output=plain(value)))
        if file=='circuits_cv.py' and fn=='extract' and isinstance(value,dict):
            captures['cv']=value
            np.savez_compressed(args.output/'04_cv_native_arrays.npz',**{k:v for k,v in value.items() if isinstance(v,np.ndarray)})
        elif file=='circuit_geometry_validator.py' and fn=='validate':captures['validated_cv']=value
        elif file=='router.py' and fn=='extract' and (frame.f_locals.get('source_width'),frame.f_locals.get('source_height'))==(image.shape[1],image.shape[0]):
            captures['ocr']=value
        elif file=='PageIRBuilder.py' and fn=='build':captures['page']=value
    services=_get_ingestion_pipeline()
    start=time.perf_counter();sys.setprofile(observe)
    try:result=run_experiment(source_bytes,source.name,'image/jpeg' if source.suffix.lower() in {'.jpg','.jpeg'} else 'image/png',services)
    finally:sys.setprofile(None)
    save('15_result',result);save('01_page_ir',plain(captures.get('page')))
    save('02_model_and_detections',dict(model=result.get('model'),detections=result.get('detections')))
    save('03_ocr',plain(captures.get('ocr')))
    save('04_cv_candidates',plain(captures.get('cv')))
    save('07_geometry_validation',plain(captures.get('validated_cv')))
    save('16_function_trace',dict(calls));save('17_duration',dict(total_seconds=time.perf_counter()-start))
    cv=captures.get('cv') or {};checked=captures.get('validated_cv') or {}
    book=result.get('book_ir') or {};parameters=book.get('parameters') or {};provenance=book.get('provenance') or {}
    save('08_geometric_conductor_graph',parameters.get('geometric_conductor_graph'))
    save('09_ideal_electrical_graph',{k:parameters.get(k) for k in ('components','nodes','wires','reference_node')})
    save('10_reconciliation',provenance.get('circuit_reconciliation'))
    save('11_value_ownership',dict(components=parameters.get('components'),associations=provenance.get('candidate_parameters'),
        refinements=provenance.get('circuit_ocr_refinements')))
    save('12_readiness_and_compiler',dict(stages=result.get('stages'),compiler=result.get('compiler'),first_blocker=result.get('first_blocker')))
    save('13_solver',result.get('ideal_analysis'))
    if captures.get('ocr'):
        save('03_ocr_clusters',plain(parse_and_cluster_circuit_tokens(captures['ocr'].tokens,keep_standalone_values=True)))
    def write(name,canvas):cv2.imwrite(str(args.output/(name+'.png')),canvas)
    def tag(canvas,text,x,y,color=(0,90,0)):
        x,y=max(0,int(x)),max(13,int(y));x=min(x,max(0,canvas.shape[1]-8*len(text)))
        cv2.putText(canvas,text,(x,y),cv2.FONT_HERSHEY_SIMPLEX,.38,(255,255,255),3,cv2.LINE_AA)
        cv2.putText(canvas,text,(x,y),cv2.FONT_HERSHEY_SIMPLEX,.38,color,1,cv2.LINE_AA)
    canvas=image.copy()
    for i,d in enumerate(result.get('detections',[]),1):
        b=d['bbox'];x,y,w,h=[round(b[k]) for k in ('x','y','width','height')]
        cv2.rectangle(canvas,(x,y),(x+w,y+h),(0,150,0),1);tag(canvas,f'D{i} {d["kind"]} {d["confidence"]:.2f}',x,y-4)
    write('02_detection_overlay',canvas)
    canvas=image.copy()
    for i,t in enumerate((plain(captures.get('ocr')) or {}).get('tokens',[]),1):
        b=t.get('bboxSourcePx')
        if not b:continue
        x,y,w,h=[round(b[k]) for k in ('x','y','width','height')]
        cv2.rectangle(canvas,(x,y),(x+w,y+h),(180,60,0),1);tag(canvas,'T'+str(i),x,y-2,(180,60,0))
    write('03_ocr_boxes',canvas)
    for key,name in [('gray','04_grayscale'),('original_binary','04_original_binary'),('body_mask_before','05_after_text_suppression'),
        ('conductor_mask','06_conductor_mask'),('skeleton','06_wire_skeleton'),('removed_symbol_pixels','05_exact_removed_pixels')]:
        array=cv.get(key)
        if array is None:continue
        if key=='gray':write(name,array)
        else:write(name,255-(array!=0).astype(np.uint8)*255)
    canvas=image.copy()
    mask=cv.get('component_body_mask')
    if mask is not None:
        selected_pixels=mask!=0;canvas[selected_pixels]=(canvas[selected_pixels]*.35+np.array([0,0,255])*.65).astype(np.uint8)
    write('05_body_pixel_overlay',canvas)
    canvas=image.copy()
    for path in cv.get('wire_paths',[]):
        cv2.polylines(canvas,[np.rint(path['points']).astype(np.int32)],False,(230,100,0),1)
    write('06_measured_wire_paths',canvas)
    canvas=image.copy()
    for i,c in enumerate(checked.get('components',[]),1):
        b=c['bbox'];color=(0,150,0) if c.get('verification_status')=='VERIFIED' else (0,70,230)
        cv2.rectangle(canvas,(round(b.x),round(b.y)),(round(b.x_max),round(b.y_max)),color,1)
        tag(canvas,'C'+str(i),b.x,b.y-2,color)
        for key in ('terminal_1','terminal_2'):
            t=c[key];cv2.circle(canvas,(round(t.x),round(t.y)),2,color,-1)
    write('07_verified_terminals',canvas)
    masks=provenance.get('circuit_segmentation',[]);save('06_sam2_masks',masks)
    canvas=image.copy();mask_manifest=[]
    for i,record in enumerate(masks,1):
        for j,m in enumerate(record.get('masks',[]),1):
            counts=json.loads(m['rleCounts']);raster=np.repeat(np.arange(len(counts))%2,counts).reshape(image.shape[:2]).astype(bool)
            accepted=m.get('promptProvenance',{}).get('verification_status')=='CORROBORATING'
            color=np.array([30,170,0] if accepted else [0,40,230]);single=image.copy()
            single[raster]=(single[raster]*.55+color*.45).astype(np.uint8)
            canvas[raster]=(canvas[raster]*.55+color*.45).astype(np.uint8)
            name=f'06_sam_candidate_{i}_mask_{j}';write(name,single)
            mask_manifest.append(dict(image=name+'.png',candidate_id=record['entity_candidate_id'],accepted=accepted,
                reasons=m.get('promptProvenance',{}).get('rejection_reasons',[])))
    write('06_sam_all_masks',canvas);save('06_sam_visual_index',mask_manifest)
    canvas=image.copy();palette=[(190,60,0),(0,150,0),(170,0,170),(0,120,210),(140,90,0)]
    node_ids=sorted({w['node'] for w in parameters.get('wires',[])})
    for wire in parameters.get('wires',[]):
        color=palette[node_ids.index(wire['node'])%len(palette)]
        cv2.polylines(canvas,[np.rint(wire['points']).astype(np.int32)],False,color,2)
        midpoint=wire['points'][len(wire['points'])//2];tag(canvas,wire['node'],midpoint[0],midpoint[1]-3,color)
    write('09_electrical_node_overlay',canvas)
    canvas=image.copy()
    for i,c in enumerate(parameters.get('components',[]),1):
        g=c['geometry'];point=g['center_source_px'];b=g.get('label_bbox_source_px')
        if b:
            cx,cy=b[0]+b[2]/2,b[1]+b[3]/2
            cv2.line(canvas,tuple(map(round,point)),(round(cx),round(cy)),(200,80,0),1)
            cv2.rectangle(canvas,(round(b[0]),round(b[1])),(round(b[0]+b[2]),round(b[1]+b[3])),(200,80,0),1)
        tag(canvas,f'C{i}: {c.get("value","?")} {c.get("unit","")}',point[0]+6,point[1]-8)
    write('11_value_owner_overlay',canvas)
    analysis=result.get('ideal_analysis') or {};state=analysis.get('electrical_state')
    canvas=image.copy()
    if (analysis.get('validation') or {}).get('valid') and state:
        for c in parameters.get('components',[]):
            current=state['components'][c['id']]['current_a'];point=c['geometry']['center_source_px']
            tag(canvas,f'{abs(current)*1000:.3f} mA',point[0]+8,point[1]-8)
    write('14_analysis_overlay',canvas)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    save('18_preservation',dict(original_unchanged=True,sha256=digest,preview_scene=result.get('preview_scene')))
    print(json.dumps(dict(output=str(args.output),compiler=result.get('compiler',{}).get('status'),
        analysis=analysis.get('status'),first_blocker=result.get('first_blocker')),ensure_ascii=False),flush=True)


if __name__=='__main__':main()

"""Real local inference against frozen, training-disjoint source annotations.

This explicit CLI is not a fast/mock test. Missing reference data is reported as
unverified. Source annotations precede inference; outputs never become truth.
"""
import argparse
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def iou(a,b):
    area=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    return area/max(1e-12,(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-area)


def matches(truth,predictions,threshold=.5,type_aware=True):
    import numpy as np
    from scipy.optimize import linear_sum_assignment
    costs=np.ones((len(truth),len(predictions)))
    for i,t in enumerate(truth):
        for j,p in enumerate(predictions):
            overlap=iou(t['bbox'],p['bbox'])
            if overlap>=threshold and (not type_aware or t['type']==p['type']):costs[i,j]=1-overlap
    rows,cols=linear_sum_assignment(costs)
    return [(int(i),int(j)) for i,j in zip(rows,cols) if costs[i,j]<1]


def exact_graph(truth,components,pairs):
    if len(pairs)!=len(truth) or len(components)!=len(truth):return False
    gt_nodes=sorted({n for c in truth for n in c['nodes']})
    actual_nodes=sorted({n for c in components for n in c['nodes'] if n})
    if len(gt_nodes)!=len(actual_nodes) or len(gt_nodes)>8:return False
    for order in itertools.permutations(actual_nodes):
        mapping=dict(zip(gt_nodes,order))
        if all({mapping[n] for n in truth[i]['nodes']}==set(components[j]['nodes']) for i,j in pairs):return True
    return False


def wire_scores(shape,truth,actual,tolerance=3):
    import cv2
    import numpy as np
    def mask(paths):
        raster=np.zeros(shape[:2],np.uint8)
        for p in paths:
            cv2.polylines(raster,[np.rint(p).astype(np.int32)],False,1,1)
        return raster
    gt=mask(truth);pred=mask(actual)
    kernel=np.ones((2*tolerance+1,)*2,np.uint8)
    precision=float(np.mean(cv2.dilate(gt,kernel)[pred!=0]!=0)) if pred.any() else 0.
    recall=float(np.mean(cv2.dilate(pred,kernel)[gt!=0]!=0)) if gt.any() else None
    return dict(precision=precision,recall=recall,tolerance_px=tolerance)


def evaluate(case,result,image):
    import numpy as np
    truth=case['components']
    predictions=[]
    for d in result.get('detections',[]):
        b=d['bbox'];predictions.append(dict(type=d['kind'],bbox=[b['x'],b['y'],b['x']+b['width'],b['y']+b['height']]))
    pairs=matches(truth,predictions)
    agnostic=matches(truth,predictions,type_aware=False)
    components=(result.get('book_ir') or {}).get('parameters',{}).get('components',[])
    cp=[dict(type=c['type'],bbox=c['geometry']['bbox_source_px']) for c in components]
    grounded=matches(truth,cp,threshold=.2)
    terminal_errors=[]
    values=0
    currents=[]
    analysis=result.get('ideal_analysis') or {}
    state=(analysis.get('electrical_state') or {}).get('components',{})
    for i,j in grounded:
        expected,actual=truth[i],components[j]
        if abs(expected['value']-actual.get('value',float('inf')))<1e-8 and actual.get('value_provenance',{}).get('source')=='ocr':values+=1
        a=np.array(expected['terminals']);b=np.array([t['source_px'] for t in actual['terminals']])
        errors=min((np.linalg.norm(a-order,axis=1).tolist() for order in (b,b[::-1])),key=sum)
        terminal_errors.extend(errors)
        if actual['id'] in state:
            currents.append(abs(abs(state[actual['id']]['current_a'])-expected['current_a'])<1e-6)
    book=result.get('book_ir') or {};geometry=book.get('geometry',{});topology=geometry.get('circuit_topology',{})
    measured_junctions=[j['center'] for j in topology.get('junction_evidence',[])]
    def point_score(expected,actual):
        if not expected:return 1. if not actual else 0.
        return sum(any(np.linalg.norm(np.subtract(p,q))<=5 for q in actual) for p in expected)/len(expected) if actual else 0.
    graph_ok=exact_graph(truth,components,grounded)
    wires=book.get('parameters',{}).get('wires',[])
    valid=case['valid'];ready=result.get('compiler',{}).get('status')=='READY'
    numerical=analysis.get('status')=='IDEAL_SOLVED' and analysis.get('validation',{}).get('valid',False)
    fault=analysis.get('status')=='IDEAL_REJECTED' and analysis.get('electrical_state') is None
    values_ok=values==len(truth)
    reference_ok=graph_ok and values_ok and all(currents) and len(currents)==len(truth)
    return dict(id=case['id'],strata=case['strata'],valid=valid,
        component=dict(tp=len(pairs),fp=len(predictions)-len(pairs),fn=len(truth)-len(pairs),
            precision=len(pairs)/len(predictions) if predictions else 0,recall=len(pairs)/len(truth),
            type_accuracy=sum(truth[i]['type']==predictions[j]['type'] for i,j in agnostic)/len(agnostic) if agnostic else None),
        terminal_error_px=dict(mean=float(np.mean(terminal_errors)) if terminal_errors else None,
            max=max(terminal_errors) if terminal_errors else None,matched=len(terminal_errors)),
        wire=wire_scores(image.shape,case['wires'],[w['points'] for w in wires]),
        junction_recall=point_score(case['junctions'],measured_junctions),
        crossing_count_correct=len(topology.get('crossing_evidence',[]))==len(case['crossings']),
        exact_graph=graph_ok,correct_value_associations=values,total_values=len(truth),
        canonical_ready=ready,valid_canonical_success=bool(valid and ready and numerical and reference_ok),
        correct_fault_detection=bool(not valid and fault),
        false_ready=bool(ready and (not valid or not reference_ok)),
        analysis_status=analysis.get('status'),compiler_status=result.get('compiler',{}).get('status'),
        source_overlay_alignment='UNVERIFIED_UNTIL_BROWSER_ACCEPTANCE',
        blockers=result.get('first_blocker'),all_branch_current_reference_pass=bool(currents and all(currents)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=ROOT/'tests/fixtures/circuit_v2_holdout.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    def save(name,value):
        (args.output/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
    manifest=json.loads(args.manifest.read_text(encoding='utf8'))
    training=json.loads((ROOT/'runs/augmented_physics/circuits_real_v2_20261031/data_manifest.json').read_text())
    training_hashes={r['source_sha256'] for r in training['records'] if r['split']=='train'}
    frozen=deepcopy(manifest)
    for case in frozen['cases']:
        case['source_sha256']=sha(ROOT/case['source'])
        assert case['source_sha256'] not in training_hashes,'Training image cannot be an unseen case'
    save('frozen_annotations_before_inference',frozen)
    save('execution',dict(manifest_sha256=sha(args.manifest),real_local_inference=True,
        segmentation='Explicitly unavailable to test deterministic CV fallback; actual SAM inference is verified separately.',
        annotation_provenance=manifest['annotation_provenance']))
    import cv2
    import numpy as np
    import torch
    from apps.api.main import _get_ingestion_pipeline
    from ai.evidence.segmentation import UnavailableSegmentationProvider
    from ai.perception.circuits.v2_experiment import run_experiment
    from tests.acceptance.circuit_v2_real_acceptance import plain
    torch.set_num_threads(4)
    services=_get_ingestion_pipeline();services[3].segmentation_provider=UnavailableSegmentationProvider()
    metrics=[]
    for case in frozen['cases']:
        source=ROOT/case['source'];image=cv2.imread(str(source))
        assert sha(source)==case['source_sha256']
        captures={}
        def observe(frame,event,value):
            if event=='return' and frame.f_code.co_filename.replace('\\','/').endswith('/ai/evidence/cv/circuits_cv.py') and frame.f_code.co_name=='extract':
                captures['cv']=plain(value)
                np.savez_compressed(args.output/(case['id']+'_pixels.npz'),**{k:v for k,v in value.items() if isinstance(v,np.ndarray)})
        sys.setprofile(observe)
        try:result=run_experiment(source.read_bytes(),source.name,'image/png',services)
        finally:sys.setprofile(None)
        save(case['id']+'_result',result);save(case['id']+'_perception',captures)
        metric=evaluate(case,result,image);metrics.append(metric);save(case['id']+'_metrics',metric)
        overlay=image.copy()
        for c in (result.get('book_ir') or {}).get('parameters',{}).get('components',[]):
            x1,y1,x2,y2=map(round,c['geometry']['bbox_source_px']);cv2.rectangle(overlay,(x1,y1),(x2,y2),(0,180,0),1)
            for t in c['terminals']:cv2.circle(overlay,tuple(map(round,t['source_px'])),2,(0,0,255),-1)
        for w in (result.get('book_ir') or {}).get('parameters',{}).get('wires',[]):
            cv2.polylines(overlay,[np.rint(w['points']).astype(np.int32)],False,(200,120,0),1)
        cv2.imwrite(str(args.output/(case['id']+'_source_overlay.png')),overlay)
        print(case['id'],metric,flush=True)
        assert sha(source)==case['source_sha256']
    save('metrics',metrics)
    strata={s:[m for m in metrics if s in m['strata']] for s in sorted({s for m in metrics for s in m['strata']})}
    save('stratified_summary',{s:dict(cases=len(ms),canonical_success=sum(m['valid_canonical_success'] for m in ms),
        false_ready=sum(m['false_ready'] for m in ms)) for s,ms in strata.items()})


if __name__=='__main__':main()

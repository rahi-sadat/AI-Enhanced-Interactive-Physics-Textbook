"""Explicit local real-model acceptance; never collected by fast unit suites.

Requires the two original images and explicit non-ideal test parameters. No
vision/segmentation/OCR providers are replaced. All evidence goes to a new folder.
"""
import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value):
    import numpy as np
    if isinstance(value,np.ndarray):return {'shape':list(value.shape),'dtype':str(value.dtype)}
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,Enum):return value.value
    if hasattr(value,'to_dict'):return plain(value.to_dict())
    if is_dataclass(value):return plain(asdict(value))
    if isinstance(value,dict):return {str(k):plain(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [plain(v) for v in value]
    return value


def close(actual,expected):
    assert abs(actual-expected)<1e-6,(actual,expected)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--c3',type=Path,required=True)
    parser.add_argument('--series-parallel',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-internal-resistance-ohm',type=float,required=True)
    parser.add_argument('--short-path-resistance-ohm',type=float,required=True)
    args=parser.parse_args()
    assert args.source_internal_resistance_ohm>=0 and args.short_path_resistance_ohm>0
    expected={'c3':'c76d6e931a337cb7786764dc1452ab2ca9f1a326908224282f8ecacc0a512346',
              'series_parallel':'30a0e9f48da206782234147846dbbbe4fd6c9f45b49b0c7145b57b8b4996b200'}
    sources={'c3':args.c3,'series_parallel':args.series_parallel}
    for name,p in sources.items():assert p.is_file() and digest(p)==expected[name],f'Wrong/missing original {name}'
    args.output.mkdir(parents=True,exist_ok=False)
    def save(name,value):
        (args.output/(name+'.json')).write_text(json.dumps(plain(value),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
    # Freeze all supplied historical diagnostics, not just the two input rasters.
    historical={str(p):digest(p) for folder in (ROOT/'outputs/c3_pipeline_20261106',ROOT/'outputs/series_parallel_pipeline_20261106')
                for p in folder.rglob('*') if p.is_file() and not p.name.startswith('~$')}
    save('historical_evidence_before',historical)
    import cv2
    import numpy as np
    import torch
    from apps.api.main import _get_ingestion_pipeline
    from ai.perception.circuits.v2_experiment import run_experiment
    from ai.perception.circuits.fault_analysis import analyze_book_circuit
    from shared.schemas.ingestion import BookIR
    torch.set_num_threads(4)
    services=_get_ingestion_pipeline()
    summary={}
    for name,path in sources.items():
        captures={}
        def observe(frame,event,result):
            if event!='return':return
            filename=frame.f_code.co_filename.replace('\\','/')
            fn=frame.f_code.co_name
            if filename.endswith('/ai/evidence/cv/circuits_cv.py') and fn=='extract' and isinstance(result,dict):
                captures['cv']=plain(result)
                arrays={k:v for k,v in result.items() if isinstance(v,np.ndarray)}
                np.savez_compressed(args.output/(name+'_cv_arrays.npz'),**arrays)
            if filename.endswith('/ai/evidence/cv/circuit_geometry_validator.py') and fn=='validate':
                captures['geometry_validation']=plain(result)
            if filename.endswith('/ai/evidence/ocr/router.py') and fn=='extract':captures['ocr']=plain(result)
        sys.setprofile(observe)
        try:r=run_experiment(path.read_bytes(),name+'.png','image/png',services)
        finally:sys.setprofile(None)
        save(name+'_result',r);save(name+'_perception',captures)
        assert r['model']['sha256']=='95bc8a1f76aaed83ad907e87bdee0255da1837fdb8f9c8405a723779e8ed0c46'
        assert r['preview_scene'] is None
        book=BookIR.from_dict(r['book_ir']);components=book.parameters['components']
        bylabel={c['label']:c for c in components}
        wanted=({'R1':4,'R2':6,'R3':4,'R4':8,'R5':12,'V1':12} if name=='c3' else
                {'R1':5,'R2':3,'R3':6,'R4':1,'V1':12})
        assert {k:c['value'] for k,c in bylabel.items()}==wanted
        assert all(c['value_provenance']['source']=='ocr' for c in components)
        assert all(c['verification_status']=='VERIFIED' for c in components)
        assert all(w['verification_status']=='VERIFIED' and len(w['ends'])==2 for w in book.parameters['wires'])
        assert not book.assumptions
        seg=book.provenance['circuit_segmentation']
        assert len(seg)==len(r['detections']) and all(d['status']=='success' and d['masks'] for d in seg)
        assert all(d['readiness']['state']=='READY' for d in seg)
        masks=[m for d in seg for m in d['masks']]
        verdicts=Counter(m['promptProvenance']['verification_status'] for m in masks)
        overlay=cv2.imread(str(path))
        for m in masks:
            counts=json.loads(m['rleCounts'])
            raster=np.repeat(np.arange(len(counts))%2,counts).reshape(overlay.shape[:2]).astype(np.uint8)
            contours,_=cv2.findContours(raster,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay,contours,-1,(0,150,0) if m['promptProvenance']['verification_status']=='CORROBORATING' else (0,0,220),1)
        cv2.imwrite(str(args.output/(name+'_mask_boundaries.png')),overlay)
        ideal=r['ideal_analysis']
        if name=='series_parallel':
            assert r['compiler']['status']=='READY' and ideal['status']=='IDEAL_SOLVED',ideal
            assert frozenset(bylabel['R2']['nodes'])==frozenset(bylabel['R3']['nodes'])
            assert bylabel['R1']['geometry']['orientation']==bylabel['R4']['geometry']['orientation']=='horizontal'
            assert all(bylabel[k]['geometry']['orientation']=='vertical' for k in ('R2','R3','V1'))
            states=ideal['electrical_state']['components']
            for label,current in {'V1':1.5,'R1':1.5,'R4':1.5,'R2':1,'R3':.5}.items():
                close(abs(states[bylabel[label]['id']]['current_a']),current)
            close(ideal['electrical_state']['equivalent_resistance_ohm'],8)
        else:
            assert r['scene'] is None and ideal['status']=='IDEAL_REJECTED' and ideal['electrical_state'] is None
            assert any(i['code']=='SHORTED_CIRCUIT_SOURCE' for i in book.review_issues)
            fault_id=ideal['fault_path_id']
            measured=next(w for w in book.parameters['wires'] if w['id']==fault_id)
            # Path numbering changes when pixel-accurate masks retain more ink.
            # The independent oracle is the visible far-right rail bypass.
            assert max(p[0] for p in measured['points'])>1400
            assert min(p[1] for p in measured['points'])<210 and max(p[1] for p in measured['points'])>820
            original=book.to_dict()
            qualitative=analyze_book_circuit(book,mode='non_ideal')
            assert qualitative['status']=='QUALITATIVE_FAULT' and qualitative['electrical_state'] is None
            fault=analyze_book_circuit(book,mode='non_ideal',source_internal_resistance_ohm=args.source_internal_resistance_ohm,
                short_path_resistance_ohm=args.short_path_resistance_ohm)
            save('c3_qualitative',qualitative);save('c3_non_ideal',fault)
            assert fault['status']=='NON_IDEAL_SOLVED' and fault['validation']['valid'],fault
            # Independent full-network calculation: 4 || 6 || (4+8) || 12 || Rfault.
            conductance=1/4+1/6+1/12+1/12+1/args.short_path_resistance_ohm
            expected_source=12/(args.source_internal_resistance_ohm+1/conductance)
            voltage=12-expected_source*args.source_internal_resistance_ohm
            states=fault['electrical_state']['components']
            close(abs(states[bylabel['V1']['id']]['current_a']),expected_source)
            for label,resistance in {'R1':4,'R2':6,'R3':12,'R4':12,'R5':12}.items():
                close(abs(states[bylabel[label]['id']]['current_a']),voltage/resistance)
            close(abs(states['fault_path:'+fault_id]['current_a']),voltage/args.short_path_resistance_ohm)
            assert book.to_dict()==original and fault['original_graph_id']==ideal['original_graph_id']
        summary[name]=dict(status=ideal['status'],components=len(components),wires=len(book.parameters['wires']),
            masks=dict(verdicts),source_sha256=digest(path),terminal_ground_truth_available=False)
        print(name,summary[name],flush=True)
    assert all(Path(p).is_file() and digest(Path(p))==sha for p,sha in historical.items())
    save('summary',dict(cases=summary,historical_evidence_unchanged=True,real_models=True,device='cpu'))


if __name__=='__main__':main()

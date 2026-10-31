"""Replay recorded semantic/OCR evidence against the unchanged real source.

No live model calls. All CV, verification, grounding, readiness and compilation
execute afresh. Artifacts explicitly distinguish replayed from fresh evidence.
Run: python -m tests.acceptance.circuit_repair_replay (or execute this file).
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np

from shared.schemas.evidence import OCRToken, SourceBBox
from shared.schemas.ingestion import BookIR, SourceAsset
from ai.ingestion.PageIRBuilder import PageIRBuilder
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.evidence.pipeline import EvidenceExtractionPipeline
from ai.evidence.ocr.mock import MockOCRProvider
from ai.evidence.segmentation import UnavailableSegmentationProvider
from ai.evidence.cv.circuits_cv import CircuitCVCandidateExtractor
from ai.evidence.cv.circuit_geometry_validator import CircuitGeometryValidator

TRACE=ROOT/'storage/generated/debug_traces/20261016/TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017'
BUNDLES=ROOT/'docs/reports/pipeline_walkthroughs_20261017/circuit/stage_data'
OUT=ROOT/'storage/generated/circuit_repair_20261018'


def serial(value):
    if hasattr(value,'to_dict'):
        return value.to_dict()
    if isinstance(value,np.ndarray):
        return {'shape':list(value.shape),'sha256':hashlib.sha256(value.tobytes()).hexdigest()}
    if isinstance(value,np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def load_recorded():
    source=TRACE/'00_source/original.jpg'
    data=source.read_bytes()
    meta=json.loads((TRACE/'00_source/file.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(data).hexdigest()==meta['sha256']
    image=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR)
    raw=json.loads((BUNDLES/'07_book.json').read_text(encoding='utf-8'))['actual_output']['records'][0]['return_value']
    book=BookIR.from_dict(raw)
    ocr=json.loads((BUNDLES/'11_ocr.json').read_text(encoding='utf-8'))['actual_output']['records'][0]['return_value']
    tokens=[OCRToken(id=t['id'],raw_text=t['raw_text'],confidence=t['confidence'],
                     bbox_source_px=SourceBBox(**t['bbox_source_px']),provider=t.get('provider','recorded'))
            for t in ocr['tokens']]
    h,w=image.shape[:2]
    asset=SourceAsset(id=book.source_asset_id,mime_type='image/jpeg',original_filename=source.name,
                      byte_size=len(data),width_px=w,height_px=h,sha256=meta['sha256'],storage_path=str(source))
    return image,asset,book,tokens


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    image,asset,book,tokens=load_recorded()
    page=PageIRBuilder().build(asset,public_url='/circuit-repair-source.jpg')
    pipeline=EvidenceExtractionPipeline(ocr_provider=MockOCRProvider(tokens),
                                        segmentation_provider=UnavailableSegmentationProvider())
    grounded=pipeline.extract_and_fuse(asset,page,book)
    compiled=PhysicsCompiler().compile(grounded)
    cv=CircuitCVCandidateExtractor().extract(image,source_width=asset.width_px,source_height=asset.height_px,
                                           ocr_boxes=[t.bbox_source_px for t in tokens])
    verified=CircuitGeometryValidator().validate(image,cv,source_asset_id=asset.id,figure_id=book.figure_id)
    outputs={'source':asset.to_dict(),'replayed_stages':['semantic VLM','OCR'],
             'sam2':'UNAVAILABLE (explicit offline provider)',
             'stage14':cv,'pre_grounding':verified,'stage17':grounded.to_dict(),
             'stage24':compiled.to_dict()}
    before={}
    for prefix in ('14','16','17','19','23','24'):
        file=next(BUNDLES.glob(prefix+'_*'))
        recorded=json.loads(file.read_text(encoding='utf-8'))
        before[prefix]={'artifact':str(file.relative_to(ROOT)),
            'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
            'execution':recorded['execution'],'status':recorded['status'],'finding':recorded['finding']}
    (OUT/'before_manifest.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
    stages=[]
    for stage,function,input_summary,actual,result in [
        (14,'CircuitCVCandidateExtractor.extract','Native raster + recorded OCR boxes',cv,
         'Candidate geometry only'),
        ('pre_grounding','CircuitGeometryValidator.validate','Native raster + CV candidates',verified,
         verified['geometry_validation']['status']),
        (16,'CircuitGrounder.ground','Verified geometry + recorded semantic/OCR identities',
         grounded.provenance['grounding_diagnostics'],grounded.status),
        (17,'validate_circuit_integrity','Grounded BookIR references',grounded.to_dict(),grounded.review_issues),
        (24,'PhysicsCompiler.compile','Readiness-evaluated BookIR',compiled.to_dict(),compiled.status)]:
        stages.append({'stage':stage,'function':function,'input_summary':input_summary,
            'actual_output':actual,'validation_result':result,
            'rejected_candidates':verified['validation_issues'] if stage in (14,'pre_grounding') else [],
            'uncertainty':{'stroke_width_px':cv['stroke_width_px'],
                           'note':'Heuristic measurement uncertainty; no independent real-image landmark ground truth'},
            'source_coordinates':{'frame':'source_px','width':asset.width_px,'height':asset.height_px},
            'evidence_references':list(grounded.evidence),
            'failure_reason':compiled.issues if stage==24 else verified['validation_issues'],
            'downstream_impact':'Runnable canonical circuit' if compiled.scene else 'Review required; scene is null'})
    (OUT/'stage_diagnostics.json').write_text(json.dumps(stages,default=serial,indent=2),encoding='utf-8')
    (OUT/'diagnostics.json').write_text(json.dumps(outputs,default=serial,indent=2),encoding='utf-8')
    (OUT/'book_ir.json').write_text(json.dumps(grounded.to_dict(),default=serial,indent=2),encoding='utf-8')
    if compiled.scene:
        compiled.scene.setdefault('visual',{})['background_url']='/circuit-repair-source.jpg'
        compiled.scene['source']['image']='/circuit-repair-source.jpg'
        (OUT/'scene.json').write_text(json.dumps(compiled.scene,default=serial,indent=2),encoding='utf-8')
    cv2.imwrite(str(OUT/'01_original_source.png'),image)
    cv2.imwrite(str(OUT/'02_grayscale.png'),cv['gray'])
    cv2.imwrite(str(OUT/'03_edge_map.png'),cv['edges'])
    overlay=image.copy()
    for t in tokens:
        b=t.bbox_source_px
        cv2.rectangle(overlay,(int(b.x),int(b.y)),(int(b.x_max),int(b.y_max)),(255,120,0),2)
    cv2.imwrite(str(OUT/'04_ocr_boxes_on_source.png'),overlay)
    for name,candidates in [('05_raw_cv_candidates_on_source.png',cv),('06_accepted_cv_geometry_on_source.png',verified),
                            ('09_verified_geometry_on_source.png',verified)]:
        overlay=image.copy()
        for p in candidates['wire_paths']:
            cv2.polylines(overlay,[np.rint(p['points']).astype(np.int32)],False,(0,160,0),2)
        for c in candidates['components']:
            b=c['bbox']
            cv2.rectangle(overlay,(int(b.x),int(b.y)),(int(b.x_max),int(b.y_max)),(0,0,255),2)
        cv2.imwrite(str(OUT/name),overlay)
    overlay=image.copy()
    for c in cv['rejected_candidates']:
        x,y,w,h=c['bbox']
        cv2.rectangle(overlay,(x,y),(x+w,y+h),(0,170,255),1)
    cv2.imwrite(str(OUT/'07_rejected_cv_candidates_on_source.png'),overlay)
    overlay=image.copy()
    for c in cv['components']:
        b=c['bbox'];cv2.rectangle(overlay,(int(b.x),int(b.y)),(int(b.x_max),int(b.y_max)),(255,0,180),2)
    cv2.putText(overlay,'CV PROMPTS ONLY - SAM2 UNAVAILABLE',(20,35),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,0,200),2)
    cv2.imwrite(str(OUT/'08_sam2_prompts_and_masks_on_source.png'),overlay)
    overlay=image.copy()
    for c in grounded.parameters['components']:
        center=c['geometry']['center_source_px']
        cv2.putText(overlay,c['id'],tuple(np.rint(center).astype(int)),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,0,0),1)
        for t in c['terminals']:
            pt=tuple(np.rint(t['source_px']).astype(int))
            cv2.circle(overlay,pt,5,(0,0,255),2)
            cv2.putText(overlay,t['node'],(pt[0]+5,pt[1]-5),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,0,0),1)
    cv2.imwrite(str(OUT/'10_grounded_components_and_terminals.png'),overlay)
    for wire in grounded.parameters['wires']:
        cv2.polylines(overlay,[np.rint(wire['points']).astype(np.int32)],False,(0,180,0),2)
    cv2.imwrite(str(OUT/'11_verified_wire_and_node_graph.png'),overlay)
    print(json.dumps({'status':grounded.status,'compiler':compiled.status,'issues':compiled.issues,
                      'components':[(c['id'],c['type'],c.get('value'),c.get('state'),c['nodes'])
                                    for c in grounded.parameters['components']],
                      'artifacts':str(OUT)}))
    return grounded,compiled


if __name__=='__main__':
    run()

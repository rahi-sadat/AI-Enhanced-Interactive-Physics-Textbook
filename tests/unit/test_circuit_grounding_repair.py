"""Offline circuit perception regressions with explicit synthetic ground truth.

Synthetic fixtures are independently rendered test inputs, never substitutes for
the recorded real source. No VLM, OCR engine, SAM model, or network is contacted.
"""
from copy import deepcopy
import json
import cv2
import numpy as np
import pytest

from shared.schemas.evidence import (SourceBBox, SourceLine, SourcePoint, OCRToken,
    OCRExtractionResult, ExtractionStatus, MaskArtifact, SegmentationResult)
from shared.schemas.ingestion import BookIR, BookEntity, SourceAsset
from ai.evidence.cv.circuits_cv import CircuitCVCandidateExtractor
from ai.evidence.cv.circuit_geometry_validator import CircuitGeometryValidator
from ai.evidence.cv.geometry_helpers import merge_collinear_lines
from ai.evidence.grounding.circuits import CircuitGrounder
from ai.evidence.grounding.circuit_graph import build_conductor_graph
from ai.evidence.grounding.circuit_integrity import validate_circuit_integrity
from ai.evidence.segmentation.circuit_prompts import segment_circuit_candidates
from ai.evidence.segmentation import UnavailableSegmentationProvider
from ai.ingestion.PhysicsCompiler import PhysicsCompiler


def schematic(*, closed=False, notation='rectangle', parallel=False, scale=1, rotate=False):
    image=np.full((700,1000,3),255,np.uint8)
    line=lambda a,b: cv2.line(image,tuple(map(int,a)),tuple(map(int,b)),(0,0,0),3)
    def resistor(a,b):
        a,b=np.array(a),np.array(b);axis=(b-a)/np.linalg.norm(b-a);normal=np.array([-axis[1],axis[0]])
        if notation=='rectangle':
            points=np.array([a+normal*15,b+normal*15,b-normal*15,a-normal*15],np.int32)
            cv2.polylines(image,[points],True,(0,0,0),3)
        else:
            points=[a]+[a+(b-a)*i/8+normal*15*(-1)**i for i in range(1,8)]+[b]
            cv2.polylines(image,[np.array(points,np.int32)],False,(0,0,0),3)
    line((140,140),(220,140));line((300,140),(480,140))
    cv2.circle(image,(220,140),6,(0,0,0),3);cv2.circle(image,(300,140),6,(0,0,0),3)
    line((225,140),(294,140) if closed else (290,110))
    line((140,140),(140,290));line((140,310),(140,520));line((140,290),(105,290));line((140,290),(175,290))
    line((125,310),(155,310));line((140,520),(800,520))
    if parallel:
        line((480,140),(800,140));line((480,140),(480,270));resistor((480,270),(480,370));line((480,370),(480,520))
        line((800,140),(800,270));resistor((800,270),(800,370));line((800,370),(800,520))
        cv2.circle(image,(480,140),6,(0,0,0),-1);cv2.circle(image,(480,520),6,(0,0,0),-1)
        centers={'r1':(480,320),'r2':(800,320)}
        labels=[('R1 = 10 ohm',(505,300,160,25)),('R2 = 20 ohm',(825,300,160,25))]
    else:
        resistor((480,140),(580,140));line((580,140),(800,140));line((800,140),(800,270))
        resistor((800,270),(800,370));line((800,370),(800,520))
        centers={'r1':(530,140),'r2':(800,320)}
        labels=[('R1 = 10 ohm',(455,85,160,25)),('R2 = 20 ohm',(825,300,160,25))]
    labels += [('12 V',(40,285,60,25)),('S',(240,70,20,25))]
    tokens=[]
    for i,(text,(x,y,w,h)) in enumerate(labels):
        cv2.putText(image,text,(x,y+h-5),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        tokens.append(OCRToken(id=f't{i}',raw_text=text,confidence=.95,bbox_source_px=SourceBBox(x,y,w,h)))
    centers.update(v=(140,300),s=(260,125 if not closed else 140))
    book=BookIR(source_asset_id='synthetic-circuit',figure_id='figure',domain='circuits',subtype='dc_linear',
                status='NEEDS_REVIEW',entities=[BookEntity(id='r1',type='resistor',label='R1'),
                BookEntity(id='r2',type='resistor',label='R2'),BookEntity(id='v',type='voltage_source',label='12 V'),
                BookEntity(id='s',type='switch',label='S')],
                relationships=[{'type':'connected_in_series','from':'v','to':'s'}] if not parallel else [])
    if rotate:
        image=cv2.rotate(image,cv2.ROTATE_90_CLOCKWISE)
        for tok in tokens:
            b=tok.bbox_source_px;tok.bbox_source_px=SourceBBox(700-b.y_max,b.x,b.height,b.width)
        centers={key:(699-y,x) for key,(x,y) in centers.items()}
    if scale!=1:
        image=cv2.resize(image,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
        for tok in tokens:
            b=tok.bbox_source_px;tok.bbox_source_px=SourceBBox(b.x*scale,b.y*scale,b.width*scale,b.height*scale)
        centers={key:(x*scale,y*scale) for key,(x,y) in centers.items()}
    return image,book,tokens,centers


def ground_fixture(**kwargs):
    image,book,tokens,centers=schematic(**kwargs)
    h,w=image.shape[:2]
    cv=CircuitCVCandidateExtractor().extract(image,source_width=w,source_height=h,
                                           ocr_boxes=[t.bbox_source_px for t in tokens])
    validated=CircuitGeometryValidator().validate(image,cv,source_asset_id=book.source_asset_id,figure_id=book.figure_id)
    outcome=CircuitGrounder().ground(book,validated,OCRExtractionResult(status=ExtractionStatus.SUCCESS,
                                    tokens=tokens,provider='mock_ocr'),source_width=w,source_height=h)
    return image,validated,outcome.grounded_book_ir,centers


@pytest.mark.parametrize('options',[{}, {'closed':True},{'scale':.7},{'scale':1.5},{'rotate':True},
                                      {'notation':'zigzag'},{'parallel':True},{'parallel':True,'closed':True}])
def test_synthetic_layouts_compile_from_measured_geometry(options):
    image,cv,book,centers=ground_fixture(**options)
    assert book.status=='READY_TO_COMPILE', (cv['validation_issues'],book.review_issues,book.provenance['grounding_diagnostics'])
    assert validate_circuit_integrity(book)==[]
    compiled=PhysicsCompiler().compile(book)
    assert compiled.status=='READY',compiled.issues
    assert len(book.parameters['components'])==4
    for c in book.parameters['components']:
        # Independent known render locations, not detector output as its own oracle.
        assert np.linalg.norm(np.subtract(c['geometry']['center_source_px'],centers[c['id']])) < 10*options.get('scale',1)
        assert all(t['node'] in {n['id'] for n in book.parameters['nodes']} for t in c['terminals'])
    switch=next(c for c in book.parameters['components'] if c['id']=='s')
    assert switch['state']==('closed' if options.get('closed') else 'open')
    assert switch['nodes'][0]!=switch['nodes'][1]
    r2=next(c for c in book.parameters['components'] if c['id']=='r2')
    assert r2['geometry']['orientation']==('horizontal' if options.get('rotate') else 'vertical')
    assert next(c for c in book.parameters['components'] if c['id']=='r1')['value']==10
    assert r2['value']==20


def test_reject_full_span_gap_and_body_short():
    image,cv,book,_=ground_fixture()
    damaged=deepcopy(cv)
    damaged['wire_paths'].append({'id':'fake-rail','points':[[140,140],[800,140]],'ends':[999,998]})
    checked=CircuitGeometryValidator().validate(image,damaged)
    assert 'fake-rail' not in {w['id'] for w in checked['wire_paths']}
    assert any(i['code']=='UNSUPPORTED_WIRE_PATH' for i in checked['validation_issues'])


def test_missing_symbol_and_direct_unverified_candidates_never_compile():
    image,book,tokens,_=schematic()
    outcome=CircuitGrounder().ground(book,{'components':[],'rails_y':[140,520],'branches_x':[140,800]},
        OCRExtractionResult(status=ExtractionStatus.SUCCESS,tokens=tokens),source_width=1000,source_height=700)
    grounded=outcome.grounded_book_ir
    assert grounded.status=='NEEDS_REVIEW'
    assert grounded.parameters['components']==[]
    assert grounded.parameters['nodes']==[]
    assert PhysicsCompiler().compile(grounded).scene is None
    assert all(e.position_source_px is None for e in grounded.entities)


def test_ids_relationships_and_serialization():
    _,_,book,_=ground_fixture()
    restored=BookIR.from_dict(book.to_dict())
    assert validate_circuit_integrity(restored)==[]
    restored.entities.append(deepcopy(restored.entities[0]))
    restored.relationships.append({'from':'missing','to':'r1'})
    codes={i['code'] for i in validate_circuit_integrity(restored)}
    assert {'DUPLICATE_OR_MISSING_ID','DANGLING_RELATIONSHIP'} <= codes
    assert PhysicsCompiler().compile(restored).scene is None


def test_sam_unavailable_and_conflicting_masks_preserve_cv():
    image,cv,book,_=ground_fixture()
    asset=SourceAsset(id='test',mime_type='image/png',original_filename='synthetic.png',byte_size=1,
                      width_px=1000,height_px=700,sha256='test',storage_path='unused')
    before=[c['center'].to_dict() for c in cv['components']]
    unavailable=segment_circuit_candidates(UnavailableSegmentationProvider(),image,cv,asset)
    assert unavailable.status==ExtractionStatus.UNAVAILABLE and not unavailable.masks
    class Conflict:
        name='mock_conflicting_segmentation'
        def available(self): return True
        def segment(self,*args,**kwargs):
            return SegmentationResult(status=ExtractionStatus.SUCCESS,masks=[MaskArtifact(id='bad',
                source_width=1000,source_height=700,bbox_source_px=SourceBBox(0,0,1000,700),area_px=700000)])
    result=segment_circuit_candidates(Conflict(),image,cv,asset)
    assert all(m.prompt_provenance['verification_status']=='REJECTED' and not m.verified for m in result.masks)
    assert before==[c['center'].to_dict() for c in cv['components']]


def test_bent_diagonal_wire_and_crossings():
    for dotted in (False,True):
        image=np.full((400,400,3),255,np.uint8)
        cv2.line(image,(40,200),(360,200),(0,0,0),3)
        cv2.line(image,(200,40),(200,360),(0,0,0),3)
        if dotted: cv2.circle(image,(200,200),8,(0,0,0),-1)
        cv=CircuitCVCandidateExtractor().extract(image,source_width=400,source_height=400)
        assert bool(cv['junctions'])==dotted
        assert bool(cv['crossings'])!=dotted
    image=np.full((300,400,3),255,np.uint8)
    cv2.polylines(image,[np.array([[30,40],[130,140],[300,140]],np.int32)],False,(0,0,0),3)
    cv=CircuitCVCandidateExtractor().extract(image,source_width=400,source_height=300)
    checked=CircuitGeometryValidator().validate(image,cv)
    assert any(len(w['points'])>=3 for w in checked['wire_paths'])


def test_collinear_candidates_retain_independent_extents():
    lines=[SourceLine(SourcePoint(0,0),SourcePoint(40,0)),SourceLine(SourcePoint(20,0),SourcePoint(100,0)),
           SourceLine(SourcePoint(110,0),SourcePoint(160,0))]
    merged=merge_collinear_lines(lines,dist_thresh=2)
    assert len(merged)==3


def test_disconnected_conductor_and_fabricated_symbol_fail_validation():
    image,book,tokens,_=schematic()
    image[515:526,350:381]=255  # A real break in the bottom conductor.
    cv=CircuitCVCandidateExtractor().extract(image,source_width=1000,source_height=700,
                                            ocr_boxes=[t.bbox_source_px for t in tokens])
    checked=CircuitGeometryValidator().validate(image,cv,source_asset_id=book.source_asset_id,figure_id=book.figure_id)
    result=CircuitGrounder().ground(book,checked,OCRExtractionResult(status=ExtractionStatus.SUCCESS,tokens=tokens),
                                   source_width=1000,source_height=700).grounded_book_ir
    assert result.status=='NEEDS_REVIEW'
    assert any(i['code']=='DISCONNECTED_TERMINAL' for i in validate_circuit_integrity(result))
    assert PhysicsCompiler().compile(result).scene is None
    damaged=deepcopy(cv)
    damaged['components'][0]['symbol_path']=[[400,400],[450,450],[500,400]]
    checked=CircuitGeometryValidator().validate(image,damaged)
    assert checked['components'][0]['verification_status']=='AMBIGUOUS'


def test_source_identity_terminal_and_value_references_cannot_drift():
    _,_,book,_=ground_fixture()
    changed=deepcopy(book)
    c=changed.parameters['components'][0]
    c['provenance']['source_asset_id']='another-upload'
    c['terminals'][0]['source_px']=[float('nan'),0]
    c['value_provenance']['evidence_refs']=['missing-ocr']
    codes={i['code'] for i in validate_circuit_integrity(changed)}
    assert {'SOURCE_IDENTITY_MISMATCH','TERMINAL_ATTACHMENT_INVALID','DANGLING_PARAMETER_EVIDENCE'}<=codes
    assert PhysicsCompiler().compile(changed).scene is None


def test_compiled_value_provenance_is_ocr_and_geometry_stays_cv():
    _,_,book,_=ground_fixture()
    scene=PhysicsCompiler().compile(book).scene
    assert scene['parameters']['r1']['provenance']=='ocr'
    assert scene['circuit']['components'][0]['provenance']['method']=='classical_cv'


def test_malformed_serialized_reference_containers_need_review():
    _,_,book,_=ground_fixture()
    for key,value in [('nodes',[{'id':[]}]),('components',[None]),('wires',None)]:
        changed=deepcopy(book);changed.parameters[key]=value
        assert any(i['code']=='INVALID_CIRCUIT_STRUCTURE' for i in validate_circuit_integrity(changed))
        assert PhysicsCompiler().compile(changed).scene is None
    changed=deepcopy(book);changed.parameters['components'][0]['terminals']=None
    assert PhysicsCompiler().compile(changed).scene is None


def test_sam_cache_uses_full_pixels_and_retains_mask_encoding(monkeypatch):
    from ai.evidence.segmentation.sam2_provider import SAM2SegmentationProvider
    from ai.evidence.segmentation.base import SegmentationPrompt
    class Predictor:
        sets=0
        def set_image(self,image): self.sets+=1
        def predict(self,**kwargs):
            mask=np.zeros((1,40,40),bool);mask[:,10:20,10:20]=True
            return mask,np.array([.8]),None
    predictor=Predictor();provider=SAM2SegmentationProvider()
    monkeypatch.setattr(provider,'available',lambda:True)
    monkeypatch.setattr(provider,'_get_predictor',lambda:predictor)
    image=np.full((40,40,3),255,np.uint8)
    prompt=SegmentationPrompt(box=SourceBBox(8,8,15,15),points=[(12,12)],labels=[1])
    for _ in range(2):
        result=provider.segment(image,prompt,source_width=40,source_height=40,entity_id='symbol')
    assert predictor.sets==1
    image[15,15]=0  # Same allocation, dimensions and corner pixels.
    result=provider.segment(image,prompt,source_width=40,source_height=40,entity_id='symbol')
    assert predictor.sets==2
    counts=json.loads(result.masks[0].rle_counts)
    decoded=np.repeat(np.arange(len(counts))%2,counts).reshape(40,40)
    assert decoded.sum()==100
    assert result.masks[0].prompt_provenance['entity_candidate_id']=='symbol'
    assert not result.masks[0].verified


def test_recorded_source_replay_when_available():
    from tests.acceptance.circuit_repair_replay import load_recorded,TRACE
    if not (TRACE/'00_source/original.jpg').exists(): pytest.skip('Original recorded source is not installed')
    image,asset,book,tokens=load_recorded()
    h,w=image.shape[:2]
    cv=CircuitCVCandidateExtractor().extract(image,source_width=w,source_height=h,ocr_boxes=[t.bbox_source_px for t in tokens])
    cv=CircuitGeometryValidator().validate(image,cv,source_asset_id=asset.id,figure_id=book.figure_id)
    result=CircuitGrounder().ground(book,cv,OCRExtractionResult(status=ExtractionStatus.SUCCESS,
        tokens=tokens,provider='recorded_ocr_replay'),source_width=w,source_height=h).grounded_book_ir
    assert result.status=='READY_TO_COMPILE',result.review_issues
    assert next(c for c in result.parameters['components'] if c['type']=='switch')['state']=='open'
    assert next(c for c in result.parameters['components'] if c['id']=='resistor_2')['geometry']['orientation']=='vertical'
    assert PhysicsCompiler().compile(result).status=='READY'

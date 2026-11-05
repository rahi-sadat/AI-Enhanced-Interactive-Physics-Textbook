"""Offline synthetic RC diagrams; raster and labels have explicit test ground truth."""
from copy import deepcopy
import cv2
import numpy as np
import pytest
from shared.schemas.ingestion import BookIR, BookEntity
from shared.schemas.evidence import OCRToken, SourceBBox, OCRExtractionResult, ExtractionStatus
from ai.evidence.cv.circuits_cv import CircuitCVCandidateExtractor
from ai.evidence.cv.circuit_geometry_validator import CircuitGeometryValidator
from ai.evidence.grounding.circuits import CircuitGrounder
from ai.resolution.engine import ResolutionEngine
from ai.resolution.analyzer import ResolutionAnalyzer
from ai.ingestion.PhysicsCompiler import PhysicsCompiler


def rc_fixture(rotate=False, scale=1, symbolic=False):
    im=np.full((600,900,3),255,np.uint8)
    def line(a,b): cv2.line(im,a,b,(0,0,0),3)
    line((150,140),(390,140));line((490,140),(700,140))
    cv2.rectangle(im,(390,125),(490,155),(0,0,0),3)
    line((150,140),(150,290));line((110,290),(190,290))
    line((130,320),(170,320));line((150,320),(150,480));line((150,480),(700,480))
    line((700,140),(700,290));line((660,290),(740,290))
    line((660,320),(740,320));line((700,320),(700,480))
    labels=[('R1' if symbolic else 'R1 = 1000 ohm',(360,80,200,25)),
            ('C1' if symbolic else 'C1 = 1000 uF',(750,285,140,25)),
            ('V1' if symbolic else 'V1 = 10 V',(10,290,100,25))]
    tokens=[]
    for i,(text,box) in enumerate(labels):
        cv2.putText(im,text,(box[0],box[1]+20),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
        tokens.append(OCRToken(id=f't{i}',raw_text=text,confidence=.95,bbox_source_px=SourceBBox(*box)))
    if rotate:
        im=cv2.rotate(im,cv2.ROTATE_90_CLOCKWISE)
        for t in tokens:
            b=t.bbox_source_px;t.bbox_source_px=SourceBBox(600-b.y_max,b.x,b.height,b.width)
    if scale!=1:
        im=cv2.resize(im,None,fx=scale,fy=scale)
        for t in tokens:
            b=t.bbox_source_px;t.bbox_source_px=SourceBBox(b.x*scale,b.y*scale,b.width*scale,b.height*scale)
    book=BookIR(source_asset_id='synthetic-rc',figure_id='rc',domain='circuits',subtype='dc_linear',entities=[
        BookEntity(id='supply',type='voltage_source',label='V1'),BookEntity(id='load',type='resistor',label='R1'),
        BookEntity(id='storage',type='capacitor',label='C1')])
    return im,book,tokens


def grounded_rc(**options):
    im,book,tokens=rc_fixture(**options);h,w=im.shape[:2]
    raw=CircuitCVCandidateExtractor().extract(im,source_width=w,source_height=h,ocr_boxes=[t.bbox_source_px for t in tokens])
    checked=CircuitGeometryValidator().validate(im,raw,source_asset_id=book.source_asset_id,figure_id=book.figure_id)
    result=CircuitGrounder().ground(book,checked,OCRExtractionResult(status=ExtractionStatus.SUCCESS,tokens=tokens,
        provider='annotated_synthetic'),source_width=w,source_height=h)
    return im,result.grounded_book_ir,checked


@pytest.mark.parametrize('options',[{}, {'rotate':True}, {'scale':.75}, {'scale':1.5}])
def test_capacitor_symbol_grounding_and_initial_condition_gate(options):
    _,book,checked=grounded_rc(**options)
    assert book.geometry['circuit_validation']['topology'],checked['validation_issues']
    c=next(c for c in book.parameters['components'] if c['type']=='capacitor')
    assert c['value']==.001 and c['unit']=='F'
    assert PhysicsCompiler().compile(book).scene is None
    issues=ResolutionAnalyzer.analyze(book).to_dict()['issues']
    assert any(i['parameterName']=='component.storage.initial_voltage' for i in issues)
    assert ResolutionEngine.apply_policy(book,'policy_uncharged_capacitor','component.storage.initial_voltage').success
    compiled=PhysicsCompiler().compile(book)
    assert compiled.status=='READY',compiled.issues
    assert compiled.scene['parameters']['storage']['provenance']=='ocr'
    assert next(c for c in compiled.scene['circuit']['components'] if c['id']=='storage')['initial_voltage']==0


def test_symbolic_rc_defaults_are_explicit_reversible_and_keep_provenance():
    _,book,checked=grounded_rc(symbolic=True)
    assert book.geometry['circuit_validation']['topology'],checked['validation_issues']
    evidence=deepcopy(book.evidence)
    for cid,policy in [('supply','policy_standard_dc_voltage'),('load','policy_standard_dc_resistance'),
                       ('storage','policy_standard_capacitance')]:
        result=ResolutionEngine.apply_policy(book,policy,f'component.{cid}.value')
        assert result.success,result.error
    assert PhysicsCompiler().compile(book).scene is None
    result=ResolutionEngine.apply_resolution(book,dict(parameterName='component.storage.initial_voltage',
        resolvedValue=5,canonicalUnit='V',resolutionSource='user_supplied'))
    assert result.success,result.error
    compiled=PhysicsCompiler().compile(book)
    assert compiled.status=='READY',compiled.issues
    assert compiled.scene['parameters']['storage']['provenance']=='policy_default'
    assert book.evidence==evidence
    ResolutionEngine.remove_resolution(book,'component.storage.initial_voltage')
    assert PhysicsCompiler().compile(book).scene is None
    assert not ResolutionEngine.apply_resolution(book,dict(parameterName='component.storage.value',
        resolvedValue=-1,canonicalUnit='F',resolutionSource='user_supplied')).success

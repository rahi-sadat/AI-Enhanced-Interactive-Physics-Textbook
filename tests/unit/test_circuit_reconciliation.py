"""Local class disagreements require measured features, never confidence."""
from copy import deepcopy

import cv2
import numpy as np
import pytest

from ai.evidence.cv import circuits_cv
from ai.evidence.cv.circuit_geometry_validator import CircuitGeometryValidator
from ai.evidence.cv.circuit_symbols import proposal
from ai.evidence.grounding.circuit_reconciliation import reconcile_candidate
from shared.schemas.evidence import SourceBBox
from tests.unit.test_circuit_body_mask import drawing


def test_historical_r4_low_iou_is_refined_from_pixels_without_lowering_gate(monkeypatch):
    image,points=drawing()
    region=SourceBBox(68,56,39,18)
    broad=proposal('resistor',points[1:],[points[1],points[-1]],1,notation='zigzag')
    broad.update(id='oversized_R4',bbox=SourceBBox(68,56,39/.1835247,18))
    assert region.iou(broad['bbox'])==pytest.approx(.1835247)
    original=circuits_cv.detect_symbols
    calls=[]
    def detector(ink,*args,**kwargs):
        calls.append(ink.shape)
        return ([deepcopy(broad)],[]) if len(calls)==1 else original(ink,*args,**kwargs)
    monkeypatch.setattr(circuits_cv,'detect_symbols',detector)
    cv=circuits_cv.CircuitCVCandidateExtractor().extract(image,source_width=310,source_height=130,
        symbol_regions=[('resistor',region)])
    checked=CircuitGeometryValidator().validate(image,cv)
    symbol=next(c for c in checked['components'] if c['id'].startswith('cv_local'))
    score,record=reconcile_candidate(region,'resistor',symbol,checked)
    assert score is not None and all(record['checks'].values())
    assert record['refinement_evidence'][0]['proposal_iou']==pytest.approx(.1835247)
    assert symbol['bbox'].x_max<115 and np.all(cv['conductor_mask'][65,110:290])
    broad.update(verification_status='VERIFIED',body_mask_status='ACCEPTED',
        terminal_attachments=symbol['terminal_attachments'])
    score,record=reconcile_candidate(region,'resistor',broad,checked)
    assert score is None and not record['checks']['body_bbox_agreement']


def plate_diagram(equal=False):
    image=np.full((150,200,3),255,np.uint8)
    plates=[(60,22),(75,22)] if equal else [(60,10),(65,22),(70,10),(75,22)]
    for y,length in plates:
        cv2.line(image,(50-length//2,y),(50+length//2,y),(0,0,0),1)
    cv2.line(image,(50,30),(50,60),(0,0,0),1)
    cv2.line(image,(50,75),(50,120),(0,0,0),1)
    return image


def test_battery_capacitor_disagreement_resolved_by_complete_plate_group(monkeypatch):
    image=plate_diagram()
    region=SourceBBox(37,58,26,20)
    old=proposal('capacitor',[[39,65],[61,75]],[[50,65],[50,75]],1,
        notation='parallel_plates',plates=[[39,65,23,1],[39,75,23,1]])
    old['id']='incomplete_plate_group'
    original=circuits_cv.detect_symbols
    calls=[]
    def detector(ink,*args,**kwargs):
        calls.append(ink.shape)
        return ([old],[]) if len(calls)==1 else original(ink,*args,**kwargs)
    monkeypatch.setattr(circuits_cv,'detect_symbols',detector)
    cv=circuits_cv.CircuitCVCandidateExtractor().extract(image,source_width=200,source_height=150,
        symbol_regions=[('voltage_source',region)])
    checked=CircuitGeometryValidator().validate(image,cv)
    source=next(c for c in checked['components'] if c['type']=='voltage_source')
    assert any(e['type']=='capacitor' for e in source['refinement_evidence'])
    score,record=reconcile_candidate(region,'voltage_source',source,checked)
    assert score is not None and record['checks']['symbol_specific_features']
    assert len(source['plates'])==4 and source['terminal_1'].y>source['terminal_2'].y


def test_detector_battery_class_cannot_override_equal_capacitor_plates():
    image=plate_diagram(equal=True)
    region=SourceBBox(37,58,26,20)
    cv=circuits_cv.CircuitCVCandidateExtractor().extract(image,source_width=200,source_height=150,
        symbol_regions=[('voltage_source',region)])
    checked=CircuitGeometryValidator().validate(image,cv)
    capacitor=next(c for c in checked['components'] if c['type']=='capacitor')
    score,record=reconcile_candidate(region,'voltage_source',capacitor,checked)
    assert score is None and record['status']=='UNRESOLVED'
    assert record['checks']['symbol_specific_features'] and not record['checks']['type_agreement']

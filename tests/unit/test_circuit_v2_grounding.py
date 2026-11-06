"""Offline parser/association and measured-boundary regressions."""
from copy import deepcopy

import cv2
import numpy as np
import pytest

from ai.evidence.cv.circuits_cv import CircuitCVCandidateExtractor
from ai.evidence.cv.circuit_geometry_validator import CircuitGeometryValidator
from ai.evidence.grounding.circuits import parse_and_cluster_circuit_tokens, _associate_local_ocr
from shared.schemas.evidence import OCRToken, SourceBBox


@pytest.mark.parametrize('text,expected', [('R1 (5Ω)',5), ('R_3 (6Ω)',6), ('R4(1Ω)',1),
    ('(3Ω)',3), ('R₂ = 2.5 Ω',2.5), ('R১ (৫Ω)',5)])
def test_printed_resistance_notation_keeps_raw_evidence(text, expected):
    token = OCRToken(id='t',raw_text=text,confidence=.9,bbox_source_px=SourceBBox(1,1,45,20))
    before = deepcopy(token)
    parsed = parse_and_cluster_circuit_tokens([token],keep_standalone_values=True)
    assert len(parsed) == 1 and parsed[0]['val'] == expected
    assert token == before


def test_diagonal_nearest_label_is_not_geometric_association():
    c = dict(type='resistor',bbox=SourceBBox(50,50,40,10),orientation='horizontal')
    labels = parse_and_cluster_circuit_tokens([
        OCRToken(id='t',raw_text='4Ω',bbox_source_px=SourceBBox(95,65,20,12))])
    assert _associate_local_ocr({'r':c},labels,200) == {}


def test_ambiguous_equal_labels_require_review():
    c = dict(type='resistor',bbox=SourceBBox(50,50,40,10),orientation='horizontal')
    labels = parse_and_cluster_circuit_tokens([
        OCRToken(id=str(i),raw_text=f'{i+1}Ω',bbox_source_px=SourceBBox(55,25 if i==0 else 73,20,12))
        for i in range(2)],keep_standalone_values=True)
    assert _associate_local_ocr({'r':c},labels,200) == {}


def test_small_four_plate_source_uses_pixel_lengths_not_detector_identity():
    image=np.full((150,200,3),255,np.uint8)
    for y,length in [(60,10),(65,22),(70,10),(75,22)]:
        cv2.line(image,(50-length//2,y),(50+length//2,y),(0,0,0),1)
    cv2.line(image,(50,30),(50,60),(0,0,0),1)
    cv2.line(image,(50,75),(50,120),(0,0,0),1)
    cv=CircuitCVCandidateExtractor().extract(image,source_width=200,source_height=150,
        symbol_regions=[('voltage_source',SourceBBox(37,58,26,20))])
    source=next(c for c in cv['components'] if c['type']=='voltage_source')
    assert len(source['plates']) == 4 and source['polarity_verified']
    assert source['terminal_1'].y > source['terminal_2'].y
    assert source['orientation'] == 'vertical'


def test_resistor_does_not_absorb_long_adjacent_conductor():
    image=np.full((130,310,3),255,np.uint8)
    points=np.array([[10,65],[70,65],[74,58],[80,72],[86,58],[92,72],[98,58],[104,65],[290,65]],np.int32)
    cv2.polylines(image,[points],False,(0,0,0),1)
    cv=CircuitCVCandidateExtractor().extract(image,source_width=310,source_height=130,
        symbol_regions=[('resistor',SourceBBox(68,56,39,18))])
    resistor=next(c for c in cv['components'] if c['type']=='resistor')
    assert resistor['bbox'].x_max < 115
    checked=CircuitGeometryValidator().validate(image,cv)
    assert any(max(p[0] for p in w['points']) > 280 for w in checked['wire_paths'])

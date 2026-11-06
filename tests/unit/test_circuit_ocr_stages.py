from copy import deepcopy

import pytest

from ai.evidence.grounding.circuit_ocr import normalize_circuit_text,parse_circuit_label,parse_circuit_ocr_tokens
from ai.evidence.grounding.circuits import parse_and_cluster_circuit_tokens,_associate_local_ocr
from shared.schemas.evidence import OCRToken,SourceBBox


@pytest.mark.parametrize('raw,expected',[('R1 (5Ω)',5),('R_3 (6Ω)',6),('R4(1Ω)',1),
    ('(3Ω)',3),('R₂ = 2.5 kΩ',2500),('12V',12),('V = 12 V',12),
    ('R₁ = .25 MΩ',250000),('R4 = 2.5 mΩ',.0025),('V1 = 250 mV',.25),('C₁ = 2.2 μF',2.2e-6)])
def test_normalization_and_physical_parsing_are_separate(raw,expected):
    normalized=normalize_circuit_text(raw)
    assert parse_circuit_label(normalized)['val']==pytest.approx(expected)
    token=OCRToken(id='raw',raw_text=raw,bbox_source_px=SourceBBox(0,0,100,20))
    before=deepcopy(token)
    parsed=parse_circuit_ocr_tokens([token])
    assert parsed[0]['val']==pytest.approx(expected) and token==before


def test_split_number_unit_and_separate_designator_preserve_every_raw_token():
    tokens=[OCRToken(id=str(i),raw_text=text,bbox_source_px=SourceBBox(x,20,w,20))
            for i,(text,x,w) in enumerate([('R2',10,22),('2.5',37,25),('kΩ',66,23)])]
    before=deepcopy(tokens)
    parsed=parse_and_cluster_circuit_tokens(tokens,keep_standalone_values=True)
    assert len(parsed)==1 and parsed[0]['id']=='R2' and parsed[0]['val']==2500
    assert {t.id for t in parsed[0]['tokens']}=={'0','1','2'} and tokens==before


def test_parenthesized_value_and_separate_r2_have_one_verified_owner():
    tokens=[OCRToken(id=str(i),raw_text=text,bbox_source_px=SourceBBox(x,20,w,20))
            for i,(text,x,w) in enumerate([('R2',10,20),('(3Ω)',33,35)])]
    clusters=parse_and_cluster_circuit_tokens(tokens,keep_standalone_values=True)
    owned=_associate_local_ocr({'a':dict(type='resistor',orientation='horizontal',bbox=SourceBBox(10,50,60,10)),
        'b':dict(type='resistor',orientation='horizontal',bbox=SourceBBox(150,50,60,10))},clusters,250)
    assert set(owned)=={'a'} and owned['a']['val']==3 and owned['a']['id']=='R2'


def test_unit_between_equal_numbers_is_ambiguous_and_cannot_supply_two_values():
    tokens=[OCRToken(id=str(i),raw_text=text,bbox_source_px=SourceBBox(x,20,20,20))
            for i,(text,x) in enumerate([('2.5',10),('Ω',35),('3.5',60)])]
    assert parse_and_cluster_circuit_tokens(tokens,keep_standalone_values=True)==[]


def test_bare_number_never_acquires_a_resistance_unit():
    assert parse_circuit_label('12')['unit'] is None
    assert parse_circuit_label('R1 = 12 V') is None

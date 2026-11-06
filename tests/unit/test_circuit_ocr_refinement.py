from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np

from ai.evidence.grounding.circuit_ocr_refinement import refine_circuit_ocr
from shared.schemas.evidence import ExtractionStatus,OCRExtractionResult,OCRToken,SourceBBox
from tests.unit.test_circuit_grounding_repair import ground_fixture


def test_retry_uses_verified_mask_and_keeps_both_raw_recognition_records():
    image,cv,_,_=ground_fixture()
    token=OCRToken(id='raw',raw_text='SR2 (4Ω)',bbox_source_px=SourceBBox(470,130,190,40),confidence=.9)
    raw=OCRExtractionResult(status=ExtractionStatus.SUCCESS,tokens=[token]);before=deepcopy(raw);pixels=image.copy()
    provider=SimpleNamespace(extract=Mock(return_value=OCRExtractionResult(status=ExtractionStatus.SUCCESS,tokens=[
        OCRToken(id='fresh',raw_text='R2 (4Ω)',bbox_source_px=SourceBBox(20,10,120,20),confidence=.9)])))
    refined,records=refine_circuit_ocr(provider,image,cv,raw)
    assert raw==before and np.array_equal(image,pixels)
    assert len(refined.tokens)==2 and refined.tokens[0]==token
    assert refined.tokens[1].bbox_source_px==SourceBBox(480,135,60,10)
    assert records[0]['removed_pixels']>0 and records[0]['parent_token_id']=='raw'
    assert refined.tokens[1].raw_text=='R2 (4Ω)' and not records[0].get('error')
    provider.extract.assert_called_once()


def test_parsed_label_does_not_trigger_speculative_recognition():
    image,cv,_,_=ground_fixture()
    raw=OCRExtractionResult(status=ExtractionStatus.SUCCESS,tokens=[OCRToken(id='raw',raw_text='R2 (4Ω)',bbox_source_px=SourceBBox(470,130,190,40))])
    provider=SimpleNamespace(extract=Mock(side_effect=AssertionError('Already parsed')))
    result,records=refine_circuit_ocr(provider,image,cv,raw)
    assert result.tokens==raw.tokens and not records
    provider.extract.assert_not_called()

"""Focused regressions for measured Phase 3 OCR association failures."""

import numpy as np

from ai.evidence.grounding.physical_value_parser import parse_physical_value_candidate
from ai.evidence.ocr.mock import MockOCRProvider
from ai.evidence.ocr.router import MultiOCRRouter
from shared.schemas.evidence import OCRToken, SourceBBox


def test_explicit_focal_length_candidate_keeps_centimeter_unit():
    token = OCRToken(id="focal", raw_text="f = 15 cm", confidence=0.97)
    candidates = parse_physical_value_candidate(token)
    assert any(c.quantity_candidate == "focal_length" and c.numeric_value == 15
               and c.raw_unit == "cm" for c in candidates)


def test_high_confidence_angle_survives_low_confidence_overlapping_bangla_reading():
    box = SourceBBox(20, 20, 120, 30)
    primary = OCRToken(id="primary", raw_text="\u03b8=30\u00b0", confidence=0.99,
                       bbox_source_px=box)
    bangla = OCRToken(id="bangla", raw_text="\u0995\u09cb\u09a3 # 30'", confidence=0.43,
                      bbox_source_px=box)
    router = MultiOCRRouter(primary_provider=MockOCRProvider([primary]),
                            bangla_provider=MockOCRProvider([bangla]))
    result = router.extract(np.full((100, 200, 3), 255, dtype=np.uint8),
                            source_width=200, source_height=100)
    assert any(token.raw_text == "\u03b8=30\u00b0" for token in result.tokens)
    assert any(alt.get("text") == bangla.raw_text
               for token in result.tokens for alt in token.candidate_alternatives)

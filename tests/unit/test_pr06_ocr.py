"""PR-06 Unit Tests — OCR Provider Abstraction & Physical Value Parser.

Tests:
  - MockOCRProvider deterministic token extraction
  - UnavailableOCRProvider honest failure state
  - RapidOCRProvider execution when available
  - OCR token normalization and raw text preservation
  - Physical value candidate extraction (values, units, symbols)
  - Zero fabrication: standalone symbol 'L' yields numeric_value=None
"""
from __future__ import annotations

import unittest
import numpy as np

from shared.schemas.evidence import (
    ExtractionStatus,
    OCRToken,
    SourceBBox,
    SourcePoint,
    SourcePolygon,
)
from ai.evidence.ocr import MockOCRProvider, RapidOCRProvider, UnavailableOCRProvider
from ai.evidence.grounding.physical_value_parser import (
    normalize_ocr_text,
    parse_physical_value_candidate,
)


class TestPR06OCR(unittest.TestCase):
    """Test suite for OCR providers and value parsing."""

    def test_mock_ocr_provider(self):
        token = OCRToken(
            id="tok_01",
            raw_text="20 cm",
            bbox_source_px=SourceBBox(x=10.0, y=20.0, width=50.0, height=15.0),
            confidence=0.98,
        )
        provider = MockOCRProvider(canned_tokens=[token])
        self.assertTrue(provider.available())
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        result = provider.extract(img, source_width=100, source_height=100)

        self.assertEqual(result.status, ExtractionStatus.SUCCESS)
        self.assertEqual(len(result.tokens), 1)
        self.assertEqual(result.tokens[0].raw_text, "20 cm")
        self.assertEqual(result.tokens[0].bbox_source_px.x, 10.0)

    def test_unavailable_ocr_provider(self):
        provider = UnavailableOCRProvider()
        self.assertFalse(provider.available())
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        result = provider.extract(img, source_width=100, source_height=100)
        self.assertEqual(result.status, ExtractionStatus.UNAVAILABLE)
        self.assertEqual(len(result.tokens), 0)

    def test_rapidocr_provider_available(self):
        provider = RapidOCRProvider()
        # rapidocr-onnxruntime was installed in .venv, so it should report available
        self.assertTrue(provider.available())

    def test_ocr_normalization_preserves_raw_text(self):
        raw = "1O Ω"
        normalized = normalize_ocr_text(raw)
        self.assertEqual(normalized, "10 Ω")
        self.assertEqual(raw, "1O Ω")  # Raw unchanged

    def test_parse_physical_value_candidates_numeric(self):
        token = OCRToken(
            id="t1",
            raw_text="20 cm",
            confidence=0.95,
        )
        candidates = parse_physical_value_candidate(token)
        self.assertEqual(len(candidates), 1)
        cand = candidates[0]
        self.assertEqual(cand.numeric_value, 20.0)
        self.assertEqual(cand.raw_unit, "cm")
        self.assertEqual(cand.quantity_candidate, "length")
        self.assertEqual(token.raw_text, "20 cm")

    def test_parse_angle_candidate(self):
        token = OCRToken(id="t2", raw_text="θ = 30°", confidence=0.92)
        candidates = parse_physical_value_candidate(token)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].numeric_value, 30.0)
        self.assertEqual(candidates[0].raw_unit, "°")
        self.assertEqual(candidates[0].quantity_candidate, "angle")

    def test_parse_voltage_and_resistance(self):
        token_v = OCRToken(id="t_v", raw_text="12 V", confidence=0.96)
        candidates_v = parse_physical_value_candidate(token_v)
        self.assertEqual(candidates_v[0].numeric_value, 12.0)
        self.assertEqual(candidates_v[0].quantity_candidate, "voltage")

        token_r = OCRToken(id="t_r", raw_text="1O Ω", confidence=0.94)
        candidates_r = parse_physical_value_candidate(token_r)
        self.assertEqual(candidates_r[0].numeric_value, 10.0)
        self.assertEqual(candidates_r[0].quantity_candidate, "resistance")

    def test_zero_fabrication_on_standalone_symbol(self):
        """CRITICAL: Symbol 'L' with no number yields numeric_value=None."""
        token_l = OCRToken(id="t_sym", raw_text="L", confidence=0.90)
        candidates = parse_physical_value_candidate(token_l)
        self.assertEqual(len(candidates), 1)
        self.assertIsNone(candidates[0].numeric_value)
        self.assertEqual(candidates[0].quantity_candidate, "length_symbol")
        self.assertEqual(candidates[0].raw_text, "L")


if __name__ == "__main__":
    unittest.main()

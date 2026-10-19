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

    def test_textbook_physics_expressions_comprehensive(self):
        """Section 13: Test full suite of standard textbook physics forms."""
        test_cases = [
            ("m = 2 kg", 2.0, "kg", "mass"),
            ("L = 1.5 m", 1.5, "m", "length"),
            ("v = 20 m/s", 20.0, "m/s", "velocity"),
            ("u = 15 m/s", 15.0, "m/s", "velocity"),
            ("g = 9.8 m/s²", 9.8, "m/s²", "acceleration"),
            ("g = 9.8 m/s^2", 9.8, "m/s²", "acceleration"),
            ("θ = 30°", 30.0, "°", "angle"),
            ("θ = 30 deg", 30.0, "°", "angle"),
            ("f = 20 cm", 20.0, "cm", "focal_length"),
            ("R = 10 Ω", 10.0, "ohm", "resistance"),
            ("R1 = 2 kΩ", 2.0, "kohm", "resistance"),
            ("V = 12 V", 12.0, "V", "voltage"),
            ("I = 250 mA", 250.0, "mA", "current"),
            ("n = 1.50", 1.50, None, "refractive_index"),
        ]
        for text, exp_val, exp_unit, exp_qty in test_cases:
            token = OCRToken(id=f"tok_{text}", raw_text=text, confidence=0.95)
            candidates = parse_physical_value_candidate(token)
            self.assertTrue(len(candidates) >= 1, f"Failed to parse: {text}")
            cand = candidates[0]
            self.assertAlmostEqual(cand.numeric_value, exp_val, msg=f"Value mismatch for {text}")
            self.assertEqual(cand.canonical_unit, exp_unit, msg=f"Unit mismatch for {text}")
            self.assertEqual(cand.quantity_candidate, exp_qty, msg=f"Quantity mismatch for {text}")

    def test_parameter_binder_mandatory_dimensions_and_resolution_invariance(self):
        """Section 8: Parameter binding must not assume 800x600 and must be resolution-invariant."""
        from ai.document_intelligence.parsing.parameter_binder import (
            TextFragment,
            bind_parameters_to_components,
        )
        from shared.schemas.circuit_models import Component

        resistor = Component(
            id="R1",
            type="resistor",
            bbox_source_px=[100.0, 100.0, 200.0, 150.0],
            terminals=[],
            parameters={},
        )
        battery = Component(
            id="V1",
            type="battery",
            bbox_source_px=[300.0, 100.0, 400.0, 150.0],
            terminals=[],
            parameters={},
        )
        r_fragment = TextFragment(
            text="10 Ω",
            center_x=150.0,
            center_y=80.0,
            bbox=[130.0, 70.0, 170.0, 90.0],
        )
        v_fragment = TextFragment(
            text="12 V",
            center_x=350.0,
            center_y=80.0,
            bbox=[330.0, 70.0, 370.0, 90.0],
        )

        # 1. Invalid or missing dimensions must raise error
        with self.assertRaises(ValueError):
            bind_parameters_to_components([resistor], [r_fragment], 0, 600)
        with self.assertRaises(ValueError):
            bind_parameters_to_components([resistor], [r_fragment], 800, -100)

        # 2. Test multiple resolutions across small and large images
        resolutions = [
            (393, 328),
            (800, 600),
            (1536, 1024),
            (2048, 1536),
        ]
        for w, h in resolutions:
            scale_x = w / 800.0
            scale_y = h / 600.0
            r_scaled = Component(
                id="R1",
                type="resistor",
                bbox_source_px=[100.0 * scale_x, 100.0 * scale_y, 200.0 * scale_x, 150.0 * scale_y],
                terminals=[],
                parameters={},
            )
            v_scaled = Component(
                id="V1",
                type="battery",
                bbox_source_px=[300.0 * scale_x, 100.0 * scale_y, 400.0 * scale_x, 150.0 * scale_y],
                terminals=[],
                parameters={},
            )
            rf_scaled = TextFragment(
                text="10 Ω",
                center_x=150.0 * scale_x,
                center_y=80.0 * scale_y,
                bbox=[130.0 * scale_x, 70.0 * scale_y, 170.0 * scale_x, 90.0 * scale_y],
            )
            vf_scaled = TextFragment(
                text="12 V",
                center_x=350.0 * scale_x,
                center_y=80.0 * scale_y,
                bbox=[330.0 * scale_x, 70.0 * scale_y, 370.0 * scale_x, 90.0 * scale_y],
            )

            bound = bind_parameters_to_components(
                [r_scaled, v_scaled],
                [rf_scaled, vf_scaled],
                image_width=w,
                image_height=h,
            )

            # Resistance bound to resistor, NEVER battery
            self.assertIn("resistance_ohm", r_scaled.parameters)
            self.assertEqual(r_scaled.parameters["resistance_ohm"].value, 10.0)
            self.assertNotIn("resistance_ohm", v_scaled.parameters)

            # Voltage bound to battery, NEVER resistor
            self.assertIn("voltage_v", v_scaled.parameters)
            self.assertEqual(v_scaled.parameters["voltage_v"].value, 12.0)
            self.assertNotIn("voltage_v", r_scaled.parameters)

    def test_merge_collinear_lines_perpendicular_invariance(self):
        """Perpendicular lines intersecting must not be falsely merged as collinear."""
        from ai.evidence.cv.geometry_helpers import merge_collinear_lines
        from shared.schemas.evidence import SourceLine, SourcePoint

        horizontal = SourceLine(start=SourcePoint(50.0, 175.0), end=SourcePoint(550.0, 175.0))
        vertical = SourceLine(start=SourcePoint(300.0, 50.0), end=SourcePoint(300.0, 300.0))

        merged = merge_collinear_lines([horizontal, vertical], dist_thresh=12.0, angle_thresh_deg=6.0)
        self.assertEqual(len(merged), 2, "Perpendicular intersecting lines must both be preserved")

    def test_ocr_spatial_deduplication_contained_prefix(self):
        """Regression test: One OCR box mostly/fully contained inside another containing the same prefix.

        Example:
          - Larger box: 'Fig. 1 Simple Pendulum' at (383, 936, 677, 89)
          - Nested box: 'Fig. 1' at (384, 941, 174, 81)
        The smaller contained token must NOT survive as a redundant independent token,
        but be subsumed into candidate_alternatives of the canonical token.
        """
        from ai.evidence.ocr.router import deduplicate_spatial_tokens

        tok_full = OCRToken(
            id="tok_caption_full",
            raw_text="Fig. 1 Simple Pendulum",
            bbox_source_px=SourceBBox(x=383.0, y=936.0, width=677.0, height=89.0),
            confidence=0.98,
            provider="rapidocr",
        )
        tok_prefix = OCRToken(
            id="tok_caption_prefix",
            raw_text="Fig. 1",
            bbox_source_px=SourceBBox(x=384.0, y=941.0, width=174.0, height=81.0),
            confidence=0.92,
            provider="rapidocr",
        )
        tok_other = OCRToken(
            id="tok_mass",
            raw_text="m",
            bbox_source_px=SourceBBox(x=1014.0, y=716.0, width=71.0, height=56.0),
            confidence=0.95,
            provider="rapidocr",
        )

        deduped = deduplicate_spatial_tokens([tok_full, tok_prefix, tok_other])

        self.assertEqual(len(deduped), 2, "Contained prefix token must be deduplicated")
        texts = [t.raw_text for t in deduped]
        self.assertIn("Fig. 1 Simple Pendulum", texts)
        self.assertNotIn("Fig. 1", texts)
        self.assertIn("m", texts)

        # Canonical token preserves subsumed token diagnostics in candidate_alternatives
        kept_caption = next(t for t in deduped if t.id == "tok_caption_full")
        subsumed_ids = [alt.get("subsumed_id") for alt in kept_caption.candidate_alternatives]
        self.assertIn("tok_caption_prefix", subsumed_ids)

    def test_greek_symbol_visual_ocr_recognition(self):
        """Regression test for Greek symbol visual OCR (θ, Ω, etc.).

        Verifies:
          1. GreekSymbolVisualOCR is available.
          2. Isolated θ contour yields OCRToken with raw_text='θ' and script_candidate='greek'.
          3. Standalone symbol parser yields quantity_candidate='angle_symbol' with ZERO numeric value fabrication.
        """
        import cv2
        from ai.evidence.ocr.greek_symbols import GreekSymbolVisualOCR

        provider = GreekSymbolVisualOCR()
        self.assertTrue(provider.available())

        # Synthesize a clean white canvas with a clear black θ (theta)
        canvas = np.ones((200, 200, 3), dtype=np.uint8) * 255
        # Draw outer oval
        cv2.ellipse(canvas, (100, 100), (20, 32), 0, 0, 360, (0, 0, 0), thickness=4)
        # Draw horizontal crossbar
        cv2.line(canvas, (82, 100), (118, 100), (0, 0, 0), thickness=4)

        tokens = provider.extract_symbols(canvas, source_width=200, source_height=200)
        self.assertEqual(len(tokens), 1, "Must recognize synthetic θ symbol")
        theta_tok = tokens[0]
        self.assertEqual(theta_tok.raw_text, "θ")
        self.assertEqual(theta_tok.script_candidate, "greek")
        self.assertEqual(theta_tok.provider, "greek_symbol_ocr")

        # Zero fabrication invariant: Standalone θ yields numeric_value=None
        candidates = parse_physical_value_candidate(theta_tok)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].quantity_candidate, "angle_symbol")
        self.assertIsNone(candidates[0].numeric_value, "Numeric value must NOT be fabricated for standalone θ")


if __name__ == "__main__":
    unittest.main()



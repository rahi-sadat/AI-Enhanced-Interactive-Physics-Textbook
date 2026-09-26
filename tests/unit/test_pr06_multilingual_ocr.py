"""PR-06 Unit Tests — Multilingual OCR, Bengali Unicode Safety, Greek Physics Symbols & Confusables.

Tests:
  - Bengali Unicode safety (preservation of vowel signs, combining marks, conjuncts)
  - Bengali digit conversion (০-৯ -> 0-9) and Bangla physical units
  - Greek physics symbols recognition (θ, Ω, μ, λ, α, β, ω, φ, Δ, etc.)
  - Confusables disambiguation (O / 0 / Ω, 8 / θ, u / μ, etc.) with retained alternatives
  - FormulaRecognitionProvider abstraction
  - Benchmarking metric calculation (exact token accuracy, CER, symbol accuracy)
"""
from __future__ import annotations

import unicodedata
import unittest
import numpy as np

from shared.schemas.evidence import (
    ExtractionStatus,
    FormulaRecognitionResult,
    OCRToken,
    SourceBBox,
)
from ai.evidence.ocr.bangla import EasyOCRBanglaProvider, is_bengali_text, normalize_bengali_unicode
from ai.evidence.ocr.formula import (
    FormulaRecognitionProvider,
    MockFormulaRecognitionProvider,
    UnavailableFormulaRecognitionProvider,
)
from ai.evidence.ocr.greek_symbols import (
    GREEK_PHYSICS_SYMBOLS,
    GreekSymbolOCRProvider,
    detect_symbol_in_token,
)
from ai.evidence.ocr.router import MultiOCRRouter
from ai.evidence.grounding.physical_value_parser import (
    bengali_digits_to_ascii,
    normalize_ocr_text,
    parse_physical_value_candidate,
)


class TestPR06MultilingualOCR(unittest.TestCase):
    """Multilingual OCR unit test suite."""

    def test_bengali_unicode_nfc_safety(self):
        """Bangla text must preserve combining marks, vowel signs, and conjuncts under NFC."""
        # 'সরল দোলক' (simple pendulum), 'রোধ' (resistance), 'ভর' (mass), 'কোণ' (angle)
        bangla_samples = [
            "সরল দোলক",
            "রোধটির মান ১০ ওহম",
            "ভোল্টেজ = ১২ V",
            "কৌণিক বিস্তার θ = ৪°",
            "আলোর প্রতিসরণ",
            "ফোকাস দূরত্ব ২০ সেমি",
        ]
        for sample in bangla_samples:
            normalized = normalize_bengali_unicode(sample)
            # Must be NFC normalized
            self.assertEqual(normalized, unicodedata.normalize("NFC", sample))
            # Must identify as Bengali text
            self.assertTrue(is_bengali_text(sample))
            # Must not strip Bengali characters
            self.assertIn(sample[0], normalized)

    def test_bengali_digits_conversion(self):
        """Bengali numerals ০-৯ should accurately map to 0-9 for numeric parsing."""
        bn_str = "১০.৫ সেমি"
        ascii_digits = bengali_digits_to_ascii(bn_str)
        self.assertEqual(ascii_digits, "10.5 সেমি")

        token = OCRToken(id="bn_tok_1", raw_text="১০ ওহম", confidence=0.95)
        candidates = parse_physical_value_candidate(token)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].numeric_value, 10.0)
        self.assertEqual(candidates[0].raw_unit, "ওহম")
        self.assertEqual(candidates[0].quantity_candidate, "resistance")

    def test_bengali_voltage_and_length_units(self):
        """Bangla physical value parsing for voltage and length."""
        token_v = OCRToken(id="bn_v", raw_text="১২ ভোল্ট", confidence=0.92)
        cand_v = parse_physical_value_candidate(token_v)
        self.assertEqual(len(cand_v), 1)
        self.assertEqual(cand_v[0].numeric_value, 12.0)
        self.assertEqual(cand_v[0].quantity_candidate, "voltage")

        token_l = OCRToken(id="bn_l", raw_text="২৫ সেমি", confidence=0.93)
        cand_l = parse_physical_value_candidate(token_l)
        self.assertEqual(len(cand_l), 1)
        self.assertEqual(cand_l[0].numeric_value, 25.0)
        self.assertEqual(cand_l[0].quantity_candidate, "length")

    def test_greek_symbol_enrichment(self):
        """Greek symbols should be properly tagged with script and normalized."""
        provider = GreekSymbolOCRProvider()
        for sym in ["θ", "Ω", "μ", "λ", "α", "β", "ω", "φ", "Δ", "π", "τ", "ρ"]:
            token = OCRToken(id=f"sym_{sym}", raw_text=sym, confidence=0.90)
            provider.enrich_token(token)
            self.assertEqual(token.script_candidate, "greek")
            self.assertEqual(token.language_candidate, "el")
            self.assertTrue(len(token.candidate_alternatives) >= 1)

    def test_confusables_handling_o_0_omega(self):
        """Confusables like 'O' vs '0' vs 'Ω' must retain alternatives without silent overwrite."""
        provider = GreekSymbolOCRProvider()
        token = OCRToken(id="tok_conf_1", raw_text="10 O", confidence=0.82)
        provider.enrich_token(token)

        # Token raw text must remain unchanged
        self.assertEqual(token.raw_text, "10 O")
        # Candidate alternatives must contain Ω
        alt_texts = [alt["text"] for alt in token.candidate_alternatives]
        self.assertTrue(any("Ω" in alt or alt == "Ω" for alt in alt_texts))

        # Physical value parser should parse resistance candidate from alternative
        candidates = parse_physical_value_candidate(token)
        quantities = [c.quantity_candidate for c in candidates]
        self.assertIn("resistance", quantities)

    def test_confusables_handling_8_theta(self):
        """Confusable '8' vs 'θ' for angle markers."""
        provider = GreekSymbolOCRProvider()
        token = OCRToken(id="tok_conf_2", raw_text="8 = 30°", confidence=0.78)
        provider.enrich_token(token)
        alt_texts = [alt["text"] for alt in token.candidate_alternatives]
        self.assertTrue(any("θ" in alt for alt in alt_texts))

    def test_confusables_handling_u_mu(self):
        """Confusable 'u' vs 'μ' (e.g. for friction or micro-units)."""
        provider = GreekSymbolOCRProvider()
        token = OCRToken(id="tok_conf_3", raw_text="u = 0.2", confidence=0.85)
        provider.enrich_token(token)
        alt_texts = [alt["text"] for alt in token.candidate_alternatives]
        self.assertTrue(any("μ" in alt for alt in alt_texts))

    def test_formula_recognition_abstraction(self):
        """Formula recognition provider abstraction and mocks."""
        unavail = UnavailableFormulaRecognitionProvider()
        self.assertFalse(unavail.available())
        dummy_img = np.zeros((50, 200, 3), dtype=np.uint8)
        res_unavail = unavail.recognize_formula(dummy_img, source_width=200, source_height=50)
        self.assertEqual(res_unavail.status, ExtractionStatus.UNAVAILABLE)

        mock_prov = MockFormulaRecognitionProvider(canned_latex=r"T = 2\pi\sqrt{\frac{L}{g}}", canned_confidence=0.96)
        self.assertTrue(mock_prov.available())
        res_mock = mock_prov.recognize_formula(dummy_img, source_width=200, source_height=50)
        self.assertEqual(res_mock.status, ExtractionStatus.SUCCESS)
        self.assertEqual(res_mock.latex, r"T = 2\pi\sqrt{\frac{L}{g}}")
        self.assertEqual(res_mock.confidence, 0.96)

    def test_ocr_benchmark_metrics(self):
        """Evaluate real OCR accuracy metrics by rendering text to an image and running MultiOCRRouter."""
        from PIL import Image, ImageDraw, ImageFont

        # Ground truth annotations with positions
        ground_truth = [
            {"text": "20 cm", "category": "english_numeric", "bbox": (40, 30, 150, 40)},
            {"text": "12 V", "category": "english_numeric", "bbox": (40, 90, 120, 40)},
            {"text": "R1 = 10 ohm", "category": "english_numeric", "bbox": (40, 150, 220, 40)},
            {"text": "10 O", "category": "greek_confusable", "bbox": (40, 210, 100, 40)},
            {"text": "১০ ওহম", "category": "bangla", "bbox": (40, 270, 150, 40)},
        ]

        img_w, img_h = 500, 360
        img = Image.new("RGB", (img_w, img_h), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        try:
            font_en = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
        except Exception:
            font_en = ImageFont.load_default()

        try:
            font_bn = ImageFont.truetype("C:/Windows/Fonts/Nirmala.ttc", 28)
        except Exception:
            font_bn = font_en

        for item in ground_truth:
            x, y, w, h = item["bbox"]
            chosen_font = font_bn if item["category"] == "bangla" else font_en
            draw.text((x, y), item["text"], fill=(0, 0, 0), font=chosen_font)

        np_img = np.array(img)
        router = MultiOCRRouter()
        res = router.extract(np_img, source_width=img_w, source_height=img_h)

        self.assertEqual(res.status, ExtractionStatus.SUCCESS)
        self.assertTrue(len(res.tokens) > 0, "Router must extract at least one token from rendered text")

        def levenshtein(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            prev = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                curr = [i + 1]
                for j, c2 in enumerate(s2):
                    cost = 0 if c1 == c2 else 1
                    curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
                prev = curr
            return prev[-1]

        # Align each GT token to best predicted token by normalized text or spatial overlap
        matched_predictions = []
        ious = []
        for gt in ground_truth:
            gt_text = gt["text"]
            gt_x, gt_y, gt_w, gt_h = gt["bbox"]

            best_tok = None
            best_dist = float("inf")
            best_iou = 0.0

            for tok in res.tokens:
                cand_texts = [tok.raw_text, tok.normalized_text or tok.raw_text]
                for alt in tok.candidate_alternatives:
                    if isinstance(alt, dict) and "text" in alt:
                        cand_texts.append(alt["text"])
                    elif isinstance(alt, str):
                        cand_texts.append(alt)

                dist = min(levenshtein(gt_text, ct) for ct in cand_texts)
                if dist < best_dist:
                    best_dist = dist
                    best_tok = tok

                if tok.bbox_source_px:
                    bx, by, bw, bh = tok.bbox_source_px.x, tok.bbox_source_px.y, tok.bbox_source_px.width, tok.bbox_source_px.height
                    iw = max(0.0, min(gt_x + gt_w, bx + bw) - max(gt_x, bx))
                    ih = max(0.0, min(gt_y + gt_h, by + bh) - max(gt_y, by))
                    iarea = iw * ih
                    if iarea > 0:
                        uarea = (gt_w * gt_h) + (bw * bh) - iarea
                        iou = iarea / uarea if uarea > 0 else 0.0
                        if iou > best_iou:
                            best_iou = iou

            matched_predictions.append({
                "gt": gt,
                "best_token": best_tok,
                "best_dist": best_dist,
                "best_iou": best_iou,
            })
            ious.append(best_iou)

        # Calculate actual metrics from real inference
        total_gt_chars = sum(len(gt["text"]) for gt in ground_truth)
        total_char_errors = sum(m["best_dist"] for m in matched_predictions)
        cer = total_char_errors / total_gt_chars if total_gt_chars > 0 else 0.0

        exact_matches = sum(1 for m in matched_predictions if m["best_dist"] == 0)
        token_accuracy = exact_matches / len(ground_truth)

        # Category metrics
        bn_items = [m for m in matched_predictions if m["gt"]["category"] == "bangla"]
        bn_accuracy = sum(1 for m in bn_items if m["best_dist"] <= 2) / len(bn_items) if bn_items else 0.0

        greek_items = [m for m in matched_predictions if m["gt"]["category"] == "greek_confusable"]
        # Confusable handling should enrich '10 O' with Ω alternative
        greek_resolved = 0
        for m in greek_items:
            tok = m["best_token"]
            if tok and any("Ω" in str(alt) for alt in tok.candidate_alternatives):
                greek_resolved += 1
        greek_accuracy = greek_resolved / len(greek_items) if greek_items else 0.0

        mean_iou = sum(ious) / len(ious) if ious else 0.0

        # Assert truthful criteria from actual inference
        self.assertLess(cer, 0.40, f"CER ({cer:.2f}) exceeds acceptable bound")
        self.assertGreater(token_accuracy, 0.40, f"Token accuracy ({token_accuracy:.2f}) below expected bound")
        self.assertGreaterEqual(greek_accuracy, 0.5, "Greek confusable resolver should resolve at least 50% of symbol alternatives")


if __name__ == "__main__":
    unittest.main()

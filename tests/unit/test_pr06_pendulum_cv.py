"""PR-06 Unit Tests — Classical CV & Pendulum Candidate Extraction.

Tests:
  - Sub-pixel circle & line fitting on synthetic geometry
  - Text box edge suppression
  - Geometric pairing of bob, string, and pivot
  - Candidate extraction on real fixture (pendulum_sketch_raw.png)
"""
from __future__ import annotations

import math
import unittest
from pathlib import Path

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourcePoint
from ai.evidence.cv import (
    PendulumCVCandidateExtractor,
    fit_circle_subpixel,
    fit_line_subpixel,
    mask_out_text_regions,
    preprocess_diagram,
)


class TestPR06PendulumCV(unittest.TestCase):
    """Test suite for classical CV primitives and pendulum extractor."""

    def test_subpixel_circle_fitting(self):
        # Create 200x200 canvas with drawn circle at (100, 100) with radius 30
        canvas = np.zeros((200, 200), dtype=np.uint8)
        cv2.circle(canvas, (100, 100), 30, 255, 1)

        fit_cx, fit_cy, fit_r = fit_circle_subpixel(canvas, (99.0, 101.0), 30.0)
        self.assertAlmostEqual(fit_cx, 100.0, delta=1.0)
        self.assertAlmostEqual(fit_cy, 100.0, delta=1.0)
        self.assertAlmostEqual(fit_r, 30.0, delta=1.0)

    def test_subpixel_line_fitting(self):
        # Create 200x200 canvas with vertical line from (100, 20) to (100, 180)
        canvas = np.zeros((200, 200), dtype=np.uint8)
        cv2.line(canvas, (100, 20), (100, 180), 255, 1)

        mean_pt, direction = fit_line_subpixel(canvas, (100.0, 20.0), (100.0, 180.0))
        self.assertAlmostEqual(mean_pt[0], 100.0, delta=1.0)
        self.assertAlmostEqual(abs(direction[1]), 1.0, delta=0.05)  # Vertical direction

    def test_mask_out_text_regions(self):
        canvas = np.zeros((100, 100), dtype=np.uint8)
        # Draw some lines representing text
        canvas[20:30, 40:60] = 255
        self.assertGreater(np.sum(canvas), 0)

        box = SourceBBox(x=38.0, y=18.0, width=24.0, height=14.0)
        cleaned = mask_out_text_regions(canvas, [box], margin_px=2)
        self.assertEqual(np.sum(cleaned), 0)

    def test_synthetic_pendulum_extraction(self):
        # Draw synthetic pendulum: pivot at (150, 40), string to (220, 200), bob at (220, 200) with r=20
        img = np.ones((300, 300, 3), dtype=np.uint8) * 255
        # Line
        cv2.line(img, (150, 40), (220, 200), (0, 0, 0), 2)
        # Bob
        cv2.circle(img, (220, 200), 20, (0, 0, 0), -1)

        extractor = PendulumCVCandidateExtractor()
        res = extractor.extract_candidates(img, 300, 300)

        best = res["best_proposal"]
        self.assertIsNotNone(best)
        bob = best["bob"]
        self.assertAlmostEqual(bob["center"].x, 220.0, delta=2.5)
        self.assertAlmostEqual(bob["center"].y, 200.0, delta=2.5)
        self.assertAlmostEqual(bob["radius_px"], 20.0, delta=3.0)

        string = best["string"]
        self.assertAlmostEqual(string["start"].x, 150.0, delta=5.0)
        self.assertAlmostEqual(string["start"].y, 40.0, delta=5.0)

    def test_real_fixture_pendulum_extraction(self):
        fixture_path = Path("tests/fixtures/unseen/mechanics/pendulum_sketch_raw.png")
        if not fixture_path.exists():
            self.skipTest("Real pendulum fixture not found")

        img = cv2.imread(str(fixture_path))
        self.assertIsNotNone(img)
        h, w = img.shape[:2]

        extractor = PendulumCVCandidateExtractor()
        # Suppress text around "Pivot" (around x=379, y=81, w=81, h=14)
        ocr_boxes = [SourceBBox(x=379.0, y=81.0, width=81.0, height=14.0)]
        res = extractor.extract_candidates(img, w, h, ocr_boxes=ocr_boxes)

        best = res["best_proposal"]
        self.assertIsNotNone(best, "Should detect pendulum proposal on real fixture")

        bob = best["bob"]
        # Ground truth center is approximately (549.6, 399.2) with radius ~21px
        self.assertAlmostEqual(bob["center"].x, 549.6, delta=6.0)
        self.assertAlmostEqual(bob["center"].y, 399.2, delta=6.0)
        self.assertAlmostEqual(bob["radius_px"], 21.0, delta=3.0)

        string = best["string"]
        # Distance from pivot to bob center is approximately 354px
        self.assertAlmostEqual(string["length_to_bob_center_px"], 354.0, delta=15.0)

        pivot = best["pivot"]
        # Pivot point is approximately (389.8, 82.6)
        self.assertAlmostEqual(pivot.x, 389.8, delta=15.0)
        self.assertAlmostEqual(pivot.y, 82.6, delta=15.0)

    def test_bengali_textbook_pendulum_extraction(self):
        fixture_path = Path("tests/fixtures/unseen/acceptance/pendulum_bengali_textbook.png")
        if not fixture_path.exists():
            self.skipTest("Bengali pendulum fixture not found")

        img = cv2.imread(str(fixture_path))
        self.assertIsNotNone(img)
        h, w = img.shape[:2]

        extractor = PendulumCVCandidateExtractor()
        res = extractor.extract_candidates(img, w, h)

        best = res["best_proposal"]
        self.assertIsNotNone(best, "Should detect pendulum proposal on Bengali textbook fixture")

        bob = best["bob"]
        # Actual bob is visually at (611.9, 792.5) with radius ~47px (NEVER 238, 998 with r=190)
        self.assertAlmostEqual(bob["center"].x, 611.9, delta=5.0)
        self.assertAlmostEqual(bob["center"].y, 792.5, delta=5.0)
        self.assertAlmostEqual(bob["radius_px"], 47.2, delta=4.0)
        self.assertLess(bob["radius_px"], 80.0, "Bob radius must never be enormous false candidate")

        string = best["string"]
        # Actual string connects from pivot (333, 101) to bob (594, 749), length ~686px
        self.assertAlmostEqual(string["start"].x, 333.3, delta=10.0)
        self.assertAlmostEqual(string["start"].y, 101.2, delta=15.0)
        self.assertAlmostEqual(string["end"].x, 594.0, delta=10.0)
        self.assertAlmostEqual(string["end"].y, 749.0, delta=10.0)
        self.assertAlmostEqual(string["length_to_bob_center_px"], 745.0, delta=20.0)

        # Vertical reference line: near vertical from pivot extending ~778px
        vref = res["vertical_reference"]
        self.assertIsNotNone(vref, "Should detect vertical reference line")
        self.assertAlmostEqual(vref.start.x, 334.0, delta=10.0)
        self.assertAlmostEqual(vref.end.y, 895.0, delta=15.0)


if __name__ == "__main__":
    unittest.main()

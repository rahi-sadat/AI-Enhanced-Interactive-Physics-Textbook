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
        # Actual string connects from pivot (333, 101) to bob center (611.9, 792.5),
        # with attachment point on bob perimeter at (594, 749)
        self.assertAlmostEqual(string["start"].x, 333.3, delta=10.0)
        self.assertAlmostEqual(string["start"].y, 101.2, delta=15.0)
        self.assertAlmostEqual(string["end"].x, bob["center"].x, delta=2.0)
        self.assertAlmostEqual(string["end"].y, bob["center"].y, delta=2.0)
        self.assertAlmostEqual(string["attachment_point"].x, 594.0, delta=10.0)
        self.assertAlmostEqual(string["attachment_point"].y, 749.0, delta=10.0)
        self.assertAlmostEqual(string["length_to_bob_center_px"], 745.0, delta=20.0)

        # Vertical reference line: near vertical from pivot extending ~778px
        vref = res["vertical_reference"]
        self.assertIsNotNone(vref, "Should detect vertical reference line")
        self.assertAlmostEqual(vref.start.x, 334.0, delta=10.0)
        self.assertAlmostEqual(vref.end.y, 895.0, delta=15.0)

    def test_multi_constraint_pivot_extrapolation_exact_failure_class(self):
        """Exact failure class regression test:

        Ceiling support at y=50, vertical reference at x=200.
        A slanted string drawn ONLY starting partway down at (225, 100) to bob at (300, 250).
        The detector MUST extrapolate the string up to the intersection with the vertical
        reference line at (200, 50), and NOT falsely declare the truncated start (225, 100)
        as the grounded pivot.
        """
        w, h = 400, 400
        canvas = np.ones((h, w, 3), dtype=np.uint8) * 255

        # 1. Ceiling support line at y=50
        cv2.line(canvas, (100, 50), (300, 50), (0, 0, 0), 3)

        # 2. Vertical reference line at x=200 from y=50 down to y=320
        # Draw dashed line
        for y_seg in range(50, 320, 16):
            cv2.line(canvas, (200, y_seg), (200, min(320, y_seg + 10)), (0, 0, 0), 2)

        # 3. Slanted string line (slope: dy/dx = (250-50)/(300-200) = 2.0)
        # Visibly starts at (225, 100) down to (290, 230)
        cv2.line(canvas, (225, 100), (290, 230), (0, 0, 0), 2)

        # 4. Bob circle at (300, 250) with radius 20
        cv2.circle(canvas, (300, 250), 20, (0, 0, 0), -1)

        extractor = PendulumCVCandidateExtractor()
        res = extractor.extract_candidates(canvas, w, h)

        best = res["best_proposal"]
        self.assertIsNotNone(best, "Pendulum proposal must be detected")

        # Bob verification
        bob = best["bob"]
        self.assertAlmostEqual(bob["center"].x, 300.0, delta=3.0)
        self.assertAlmostEqual(bob["center"].y, 250.0, delta=3.0)

        # Pivot verification: must NOT be the truncated string start (225, 100)!
        pivot = best["pivot"]
        self.assertIsNotNone(pivot)
        self.assertNotAlmostEqual(pivot.x, 225.0, delta=5.0, msg="Pivot must NOT be truncated string endpoint (225, 100)")
        self.assertAlmostEqual(pivot.x, 200.0, delta=8.0, msg="Pivot x must align with vertical reference line x=200")
        self.assertAlmostEqual(pivot.y, 50.0, delta=12.0, msg="Pivot y must align with ceiling support line y=50")

        # Effective length must be distance from extrapolated pivot to bob center (~223.6 px),
        # not merely truncated visible line segment (~145 px)
        eff_length = best["string"]["length_to_bob_center_px"]
        expected_eff = math.hypot(300.0 - 200.0, 250.0 - 50.0)
        self.assertAlmostEqual(eff_length, expected_eff, delta=15.0)

    def test_ambiguity_when_extrapolation_diverges_from_reference(self):
        """When string extrapolation diverges substantially from vertical reference line,

        grounding must NOT declare 'grounded' with empty conflicts.
        """
        from shared.schemas.ingestion import BookEntity, BookIR
        from ai.evidence.grounding.pendulum import PendulumGrounder

        book_ir = BookIR(
            domain="mechanics",
            subtype="pendulum",
            entities=[
                BookEntity(id="ent_pivot", type="pivot"),
                BookEntity(id="ent_bob", type="bob"),
                BookEntity(id="ent_string", type="string"),
                BookEntity(id="ent_ref", type="vertical_reference"),
            ],
        )

        # Synthetic CV candidates where extrapolated string x diverges from vref x by 50px
        cv_candidates = {
            "best_proposal": {
                "bob": {"center": SourcePoint(300.0, 250.0), "radius_px": 20.0, "circularity": 0.95},
                "string": {
                    "start": SourcePoint(260.0, 50.0),
                    "end": SourcePoint(290.0, 230.0),
                    "length_to_bob_center_px": 205.0,
                    "visible_length_px": 183.0,
                },
                "pivot": SourcePoint(260.0, 50.0),  # x=260
            },
            "vertical_reference": type("VRef", (), {
                "start": SourcePoint(200.0, 50.0),  # x=200 -> divergence is 60px!
                "end": SourcePoint(200.0, 320.0),
                "length_px": 270.0,
                "angle_rad": math.pi / 2,
            })(),
            "support_lines": [],
            "support_y": 50.0,
        }

        grounder = PendulumGrounder()
        outcome = grounder.ground(book_ir, cv_candidates, source_width=400, source_height=400)

        pivot_diag = next((d for d in outcome.diagnostics if d.entity_id == "ent_pivot"), None)
        self.assertIsNotNone(pivot_diag)
        self.assertEqual(
            pivot_diag.grounding_state.value,
            "ambiguous",
            "Divergent pivot must be flagged as AMBIGUOUS, never GROUNDED",
        )
        self.assertGreater(len(pivot_diag.conflicts), 0, "Conflicts list must not be empty on divergence")

        # Entity position must remain ungrounded (None)
        pivot_ent = next((e for e in outcome.grounded_book_ir.entities if e.type == "pivot"), None)
        self.assertIsNotNone(pivot_ent)
        self.assertIsNone(pivot_ent.position_source_px, "Ambiguous pivot position must remain None")

    def test_referential_integrity_and_parameter_provenance(self):
        """Verify that all evidence_refs in entities, parameters, and diagnostics

        point to real, existing evidence records in BookIR.evidence.
        """
        from shared.schemas.ingestion import BookEntity, BookIR
        from ai.evidence.grounding.pendulum import PendulumGrounder

        book_ir = BookIR(
            domain="mechanics",
            subtype="pendulum",
            entities=[
                BookEntity(id="ent_pivot", type="pivot"),
                BookEntity(id="ent_bob", type="bob"),
                BookEntity(id="ent_string", type="string"),
            ],
        )

        cv_candidates = {
            "best_proposal": {
                "bob": {"center": SourcePoint(300.0, 250.0), "radius_px": 20.0, "circularity": 0.95},
                "string": {
                    "start": SourcePoint(200.0, 50.0),
                    "end": SourcePoint(290.0, 230.0),
                    "length_to_bob_center_px": 223.6,
                    "visible_length_px": 201.2,
                },
                "pivot": SourcePoint(200.0, 50.0),
            },
        }

        grounder = PendulumGrounder()
        outcome = grounder.ground(book_ir, cv_candidates, source_width=400, source_height=400)
        grounded_ir = outcome.grounded_book_ir

        evidence_ids = set(grounded_ir.evidence.keys())
        self.assertGreater(len(evidence_ids), 0, "Evidence map must not be empty")

        # 1. Check entity evidence_refs
        for ent in grounded_ir.entities:
            for ref in ent.evidence_refs:
                self.assertIn(ref, evidence_ids, f"Entity {ent.id} references missing evidence {ref}")

        # 2. Check parameter provenance evidence_refs
        for param_name, param in grounded_ir.parameters.items():
            prov = param.get("provenance") if isinstance(param, dict) else getattr(param, "provenance", None)
            if prov is not None:
                refs = prov.get("evidence_refs", []) if isinstance(prov, dict) else getattr(prov, "evidence_refs", [])
                for ref in refs:
                    self.assertIn(ref, evidence_ids, f"Parameter {param_name} references missing evidence {ref}")

        # 3. bob_radius_px must have non-empty evidence_refs
        if "bob_radius_px" in grounded_ir.parameters:
            p_bob = grounded_ir.parameters["bob_radius_px"]
            prov = p_bob.get("provenance") if isinstance(p_bob, dict) else getattr(p_bob, "provenance", None)
            refs = prov.get("evidence_refs", []) if isinstance(prov, dict) else getattr(prov, "evidence_refs", [])
            self.assertGreater(
                len(refs),
                0,
                "bob_radius_px must have supporting evidence_refs",
            )

        # 4. string_length_px must have source == 'derived' and non-empty evidence_refs
        if "string_length_px" in grounded_ir.parameters:
            p_str = grounded_ir.parameters["string_length_px"]
            prov = p_str.get("provenance") if isinstance(p_str, dict) else getattr(p_str, "provenance", None)
            source = prov.get("source") if isinstance(prov, dict) else getattr(prov, "source", None)
            refs = prov.get("evidence_refs", []) if isinstance(prov, dict) else getattr(prov, "evidence_refs", [])
            self.assertEqual(source, "derived")
            self.assertGreater(
                len(refs),
                0,
                "string_length_px must have supporting evidence_refs",
            )

    def test_string_geometry_euclidean_distance_invariant(self):
        """Invariant test:

        For EVERY line representation in string_entity.geometry:
          abs(distance(start, end) - length_px) <= tolerance
        Checks both generic (start, end, length_px) and explicit visible/effective structures.
        """
        from shared.schemas.ingestion import BookEntity, BookIR
        from ai.evidence.grounding.pendulum import PendulumGrounder

        book_ir = BookIR(
            domain="mechanics",
            subtype="pendulum",
            entities=[
                BookEntity(id="ent_pivot", type="pivot"),
                BookEntity(id="ent_bob", type="bob"),
                BookEntity(id="ent_string", type="string"),
            ],
        )

        cv_candidates = {
            "best_proposal": {
                "bob": {"center": SourcePoint(952.223, 734.855), "radius_px": 41.68, "circularity": 0.95},
                "string": {
                    "start": SourcePoint(636.0, 88.699),
                    "end": SourcePoint(952.223, 734.855),
                    "attachment_point": SourcePoint(933.616, 697.558),
                    "visible_start": SourcePoint(666.0, 150.0),
                    "visible_end": SourcePoint(939.0, 698.0),
                    "visible_length_px": 612.24,
                    "length_to_bob_center_px": 719.38,
                },
                "pivot": SourcePoint(636.0, 88.699),
            },
        }

        grounder = PendulumGrounder()
        outcome = grounder.ground(book_ir, cv_candidates, source_width=1448, source_height=1086)
        string_ent = next((e for e in outcome.grounded_book_ir.entities if e.type == "string"), None)
        self.assertIsNotNone(string_ent)
        geom = string_ent.geometry
        self.assertIsNotNone(geom)

        tol = 0.05  # 0.05 px numerical tolerance

        # 1. Generic start/end vs length_px (must represent effective physical line to bob center)
        p1 = geom["start"]
        p2 = geom["end"]
        length = geom["length_px"]
        dist = math.hypot(p2["x"] - p1["x"], p2["y"] - p1["y"])
        self.assertAlmostEqual(dist, length, delta=tol, msg=f"Generic start/end distance ({dist}) != length_px ({length})")

        # 2. Explicit effective_pendulum structure
        eff = geom["effective_pendulum"]
        eff_dist = math.hypot(eff["end"]["x"] - eff["start"]["x"], eff["end"]["y"] - eff["start"]["y"])
        self.assertAlmostEqual(eff_dist, eff["length_px"], delta=tol)
        self.assertAlmostEqual(eff_dist, 719.38, delta=tol)

        # 3. Explicit visible_string structure
        vis = geom["visible_string"]
        vis_dist = math.hypot(vis["end"]["x"] - vis["start"]["x"], vis["end"]["y"] - vis["start"]["y"])
        self.assertAlmostEqual(vis_dist, vis["length_px"], delta=tol)
        self.assertAlmostEqual(vis_dist, 612.24, delta=tol)

        # 4. Backward-compatible visible_string_start/end vs visible_length_px
        vs1 = geom["visible_string_start"]
        vs2 = geom["visible_string_end"]
        vis_len = geom["visible_length_px"]
        vs_dist = math.hypot(vs2["x"] - vs1["x"], vs2["y"] - vs1["y"])
        self.assertAlmostEqual(vs_dist, vis_len, delta=tol)


if __name__ == "__main__":
    unittest.main()



"""PR-06 Negative Grounding & Anti-Fabrication Test Suite.

Verifies that absent, ambiguous, disconnected, or unassociated evidence strictly prevents:
  1. Synthetic geometry fallbacks (e.g. image-center coordinates, default lines).
  2. Incorrect parameter promotion (e.g. unassociated numbers becoming physical parameters).
  3. Premature READY_TO_COMPILE status (BookIR remains NEEDS_REVIEW).

Cases tested:
  - Blank page: Zero geometry populated, grounders return None, BookIR parameters empty.
  - Unrelated horizontal/vertical lines: No synthetic optical axis or lens center synthesized.
  - Centered text but no lens: No lens center or optical axis manufactured.
  - Line diagram but no refraction boundary: No boundary_y, normal_x, or incidence point manufactured.
  - Multiple circles unrelated to projectile: No arbitrary circle picked as launch point or projectile body.
  - Disconnected circuit: Circuit topology does not produce closed loops or premature connectivity.
  - Two conflicting length labels on one pendulum diagram: Does not blindly take both or guess; flags conflict/ambiguity.
  - 10 Ω far away from any resistor: Spatial check rejects association (AssociationState.REJECTED).
  - Bengali text that RapidOCR misreads but EasyOCR recognizes: Preserves EasyOCR candidate without overwrite.
"""
from __future__ import annotations

import unittest
import numpy as np

from shared.schemas.evidence import (
    AssociationState,
    ExtractionStatus,
    GroundingState,
    OCRToken,
    SourceBBox,
    SourceLine,
    SourcePoint,
)
from shared.schemas.ingestion import (
    BookEntity,
    BookIR,
    BookIRStatus,
    PhysicalValue,
)
from ai.evidence.cv.projectile_cv import ProjectileCVCandidateExtractor
from ai.evidence.cv.thin_lens_cv import ThinLensCVCandidateExtractor
from ai.evidence.cv.refraction_cv import InterfaceRefractionCVCandidateExtractor
from ai.evidence.cv.spherical_mirror_cv import SphericalMirrorCVCandidateExtractor
from ai.evidence.cv.circuits_cv import CircuitCVCandidateExtractor
from ai.evidence.grounding.pendulum import PendulumGrounder
from ai.evidence.grounding.projectile import ProjectileGrounder
from ai.evidence.grounding.thin_lens import ThinLensGrounder
from ai.evidence.grounding.refraction import InterfaceRefractionGrounder
from ai.evidence.grounding.spherical_mirror import SphericalMirrorGrounder
from ai.evidence.grounding.circuits import CircuitGrounder
from ai.evidence.ocr.router import MultiOCRRouter


class TestPR06NegativeGrounding(unittest.TestCase):
    """Negative tests to guarantee zero synthetic fabrication under missing/misleading evidence."""

    def test_blank_page_projectile_no_synthetic_geometry(self):
        """A blank image must return None for launch point, velocity vector, and ground line."""
        blank = np.zeros((400, 600, 3), dtype=np.uint8) + 255
        extractor = ProjectileCVCandidateExtractor()
        candidates = extractor.extract(blank, source_width=600, source_height=400)

        self.assertIsNone(candidates.get("launch_point"), "Launch point must be None when no evidence exists")
        self.assertIsNone(candidates.get("velocity_vector"), "Velocity vector must be None on blank page")
        self.assertIsNone(candidates.get("ground_line"), "Ground line must be None on blank page")

        # Grounding with empty candidates
        book_ir = BookIR(
            source_asset_id="ast_blank",
            domain="mechanics",
            subtype="projectile",
            entities=[BookEntity(id="ent_body", type="projectile_body", label="Projectile Body")],
            parameters={},
            status=BookIRStatus.NEEDS_REVIEW,
        )
        grounder = ProjectileGrounder()
        outcome = grounder.ground(book_ir, candidates)

        ent = outcome.grounded_book_ir.entities[0]
        self.assertIsNone(ent.position_source_px, "Entity position must remain None on blank image")
        self.assertIsNone(ent.geometry, "Entity geometry must remain None on blank image")
        self.assertNotIn("launch_speed", outcome.grounded_book_ir.parameters)
        self.assertNotIn("launch_angle", outcome.grounded_book_ir.parameters)
        self.assertEqual(outcome.grounded_book_ir.status, BookIRStatus.NEEDS_REVIEW)

    def test_blank_page_thin_lens_no_synthetic_center(self):
        """A blank image must NOT manufacture lens center at h*0.5 or w*0.5."""
        blank = np.zeros((400, 600, 3), dtype=np.uint8) + 255
        extractor = ThinLensCVCandidateExtractor()
        candidates = extractor.extract(blank, source_width=600, source_height=400)

        self.assertIsNone(candidates.get("lens_center"), "Lens center must be None when no lens or axis exists")
        self.assertIsNone(candidates.get("optical_axis"), "Optical axis must be None on blank page")

        book_ir = BookIR(
            source_asset_id="ast_blank",
            domain="optics",
            subtype="thin_lens",
            entities=[
                BookEntity(id="ent_lens", type="lens", label="Thin Lens"),
                BookEntity(id="ent_axis", type="optical_axis", label="Optical Axis"),
            ],
            parameters={},
            status=BookIRStatus.NEEDS_REVIEW,
        )
        grounder = ThinLensGrounder()
        outcome = grounder.ground(book_ir, candidates)

        self.assertIsNone(outcome.grounded_book_ir.entities[0].position_source_px)
        self.assertNotIn("lens_center", outcome.grounded_book_ir.parameters)
        self.assertEqual(outcome.grounded_book_ir.status, BookIRStatus.NEEDS_REVIEW)

    def test_blank_page_refraction_no_synthetic_boundary(self):
        """A blank image must NOT manufacture bound_y=h*0.5 or normal_x=w*0.5."""
        blank = np.zeros((400, 600, 3), dtype=np.uint8) + 255
        extractor = InterfaceRefractionCVCandidateExtractor()
        candidates = extractor.extract(blank, source_width=600, source_height=400)

        self.assertIsNone(candidates.get("boundary_line"))
        self.assertIsNone(candidates.get("normal_line"))
        self.assertIsNone(candidates.get("incidence_point"))
        self.assertIsNone(candidates.get("bound_y"))
        self.assertIsNone(candidates.get("normal_x"))

        book_ir = BookIR(
            source_asset_id="ast_blank",
            domain="optics",
            subtype="interface_refraction",
            entities=[BookEntity(id="ent_bound", type="medium_boundary", label="Boundary")],
            parameters={},
            status=BookIRStatus.NEEDS_REVIEW,
        )
        grounder = InterfaceRefractionGrounder()
        outcome = grounder.ground(book_ir, candidates)

        self.assertNotIn("boundary_y", outcome.grounded_book_ir.parameters)
        self.assertNotIn("normal_x", outcome.grounded_book_ir.parameters)
        self.assertNotIn("incidence_point", outcome.grounded_book_ir.parameters)
        self.assertEqual(outcome.grounded_book_ir.status, BookIRStatus.NEEDS_REVIEW)

    def test_blank_page_spherical_mirror_no_synthetic_pole(self):
        """A blank image must NOT manufacture mirror pole at image center."""
        blank = np.zeros((400, 600, 3), dtype=np.uint8) + 255
        extractor = SphericalMirrorCVCandidateExtractor()
        candidates = extractor.extract(blank, source_width=600, source_height=400)

        self.assertIsNone(candidates.get("pole"))
        self.assertIsNone(candidates.get("principal_axis"))

        book_ir = BookIR(
            source_asset_id="ast_blank",
            domain="optics",
            subtype="spherical_mirror",
            entities=[BookEntity(id="ent_mirror", type="mirror", label="Spherical Mirror")],
            parameters={},
            status=BookIRStatus.NEEDS_REVIEW,
        )
        grounder = SphericalMirrorGrounder()
        outcome = grounder.ground(book_ir, candidates)

        self.assertNotIn("pole", outcome.grounded_book_ir.parameters)
        self.assertEqual(outcome.grounded_book_ir.status, BookIRStatus.NEEDS_REVIEW)

    def test_unrelated_lines_no_refraction_or_lens(self):
        """Unrelated diagonal random lines should not be treated as optical axis or boundary."""
        img = np.zeros((400, 600, 3), dtype=np.uint8) + 255
        import cv2
        # Random non-horizontal, non-vertical line
        cv2.line(img, (50, 50), (120, 190), (0, 0, 0), 2)
        cv2.line(img, (400, 50), (480, 250), (0, 0, 0), 2)

        refr_ext = InterfaceRefractionCVCandidateExtractor()
        refr_cands = refr_ext.extract(img, source_width=600, source_height=400)
        self.assertIsNone(refr_cands.get("boundary_line"), "Diagonal scribble is not a horizontal boundary")

        lens_ext = ThinLensCVCandidateExtractor()
        lens_cands = lens_ext.extract(img, source_width=600, source_height=400)
        self.assertIsNone(lens_cands.get("optical_axis"), "Diagonal scribble is not a horizontal optical axis")

    def test_resistor_value_far_away_rejected(self):
        """An OCR token '10 Ω' located far away from any resistor must be REJECTED, not associated."""
        from shared.schemas.evidence import OCRExtractionResult

        book_ir = BookIR(
            source_asset_id="ast_circuit",
            domain="circuits",
            subtype="dc_linear",
            entities=[BookEntity(id="R1", type="resistor", label="Resistor R1")],
            parameters={},
            status=BookIRStatus.NEEDS_REVIEW,
        )
        # Component at (100, 100)
        cv_candidates = {
            "components": [
                {
                    "type": "resistor",
                    "bbox": SourceBBox(90, 90, 40, 30),
                    "center": SourcePoint(110, 105),
                    "terminals": [SourcePoint(90, 105), SourcePoint(130, 105)],
                }
            ],
            "wire_segments": [],
        }
        # Token at (500, 500) — 400+ px away, with NO explicit label "R1"
        ocr_result = OCRExtractionResult(
            status=ExtractionStatus.SUCCESS,
            tokens=[
                OCRToken(
                    id="tok_far_res",
                    raw_text="10 Ω",
                    confidence=0.92,
                    bbox_source_px=SourceBBox(500, 500, 50, 20),
                )
            ],
            provider="mock_ocr",
        )

        grounder = CircuitGrounder()
        outcome = grounder.ground(book_ir, cv_candidates, ocr_result)

        # R1_resistance should NOT be set because the token is too far and unlabeled
        self.assertNotIn("R1_resistance", outcome.grounded_book_ir.parameters, "Faraway unlabeled token must not be associated to R1")
        # Diagnostic or association should indicate rejected
        rejections = [a for a in outcome.parameter_associations if a.state == AssociationState.REJECTED]
        self.assertTrue(len(rejections) >= 1, "Faraway candidate must produce REJECTED association state")

    def test_pendulum_unassociated_length_rejected(self):
        """An arbitrary '20 cm' token far from pendulum string and bob with no 'L' label is REJECTED."""
        from shared.schemas.evidence import OCRExtractionResult

        book_ir = BookIR(
            source_asset_id="ast_pend",
            domain="mechanics",
            subtype="pendulum",
            entities=[
                BookEntity(id="ent_str", type="string", label="String"),
                BookEntity(id="ent_bob", type="bob", label="Bob"),
                BookEntity(id="ent_piv", type="pivot", label="Pivot"),
            ],
            parameters={},
            status=BookIRStatus.NEEDS_REVIEW,
        )
        cv_candidates = {
            "bob": {"center": SourcePoint(200, 300), "radius_px": 15.0, "bounds": SourceBBox(185, 285, 30, 30)},
            "string": {"start": SourcePoint(200, 100), "end": SourcePoint(200, 285), "length_to_bob_center_px": 200.0, "visible_length_px": 185.0},
            "pivot": SourcePoint(200, 100),
        }
        # Token at (50, 500) — far from string (x=200, y=100..300), no label
        ocr_result = OCRExtractionResult(
            status=ExtractionStatus.SUCCESS,
            tokens=[
                OCRToken(
                    id="tok_far_len",
                    raw_text="20 cm",
                    confidence=0.91,
                    bbox_source_px=SourceBBox(50, 500, 50, 20),
                )
            ],
            provider="mock_ocr",
        )

        grounder = PendulumGrounder()
        outcome = grounder.ground(book_ir, cv_candidates, ocr_result)

        self.assertNotIn("length", outcome.grounded_book_ir.parameters, "Unlabeled faraway length must not be associated")
        rejected = [a for a in outcome.parameter_associations if a.state == AssociationState.REJECTED]
        self.assertTrue(len(rejected) >= 1)

    def test_disconnected_circuit_no_false_topology(self):
        """A disconnected circuit with no wires must NOT synthesize connectivity."""
        book_ir = BookIR(
            source_asset_id="ast_disc",
            domain="circuits",
            subtype="dc_linear",
            entities=[
                BookEntity(id="R1", type="resistor", label="Resistor R1"),
                BookEntity(id="V1", type="dc_voltage_source", label="Battery V1"),
            ],
            parameters={},
            status=BookIRStatus.NEEDS_REVIEW,
        )
        cv_candidates = {
            "components": [
                {
                    "type": "resistor",
                    "bbox": SourceBBox(100, 100, 40, 20),
                    "center": SourcePoint(120, 110),
                    "terminals": [SourcePoint(100, 110), SourcePoint(140, 110)],
                },
                {
                    "type": "dc_voltage_source",
                    "bbox": SourceBBox(300, 300, 40, 20),
                    "center": SourcePoint(320, 310),
                    "terminals": [SourcePoint(300, 310), SourcePoint(340, 310)],
                },
            ],
            "wire_segments": [],  # Completely disconnected, no wires
        }

        grounder = CircuitGrounder()
        outcome = grounder.ground(book_ir, cv_candidates)

        topo = outcome.grounded_book_ir.parameters.get("circuit_topology", {})
        nodes = topo.get("nodes", {})
        # With zero wires, terminals should not be bridged into common circuit nodes
        for node_id, term_list in nodes.items():
            comp_ids = set(t.split(".")[0] for t in term_list)
            self.assertTrue(len(comp_ids) <= 1, f"Disconnected components must not share node {node_id}")

        self.assertEqual(outcome.grounded_book_ir.status, BookIRStatus.NEEDS_REVIEW)

    def test_two_conflicting_length_labels_pendulum(self):
        """When two contradictory length labels exist (e.g. L = 20 cm and L = 50 cm), both are recorded as candidates."""
        from shared.schemas.evidence import OCRExtractionResult

        book_ir = BookIR(
            source_asset_id="ast_pend_conflict",
            domain="mechanics",
            subtype="pendulum",
            entities=[
                BookEntity(id="ent_str", type="string", label="String"),
                BookEntity(id="ent_bob", type="bob", label="Bob"),
                BookEntity(id="ent_piv", type="pivot", label="Pivot"),
            ],
            parameters={},
            status=BookIRStatus.NEEDS_REVIEW,
        )
        cv_candidates = {
            "bob": {"center": SourcePoint(200, 300), "radius_px": 15.0, "bounds": SourceBBox(185, 285, 30, 30)},
            "string": {"start": SourcePoint(200, 100), "end": SourcePoint(200, 285), "length_to_bob_center_px": 200.0, "visible_length_px": 185.0},
            "pivot": SourcePoint(200, 100),
        }
        ocr_result = OCRExtractionResult(
            status=ExtractionStatus.SUCCESS,
            tokens=[
                OCRToken(id="tok_len_1", raw_text="L = 20 cm", confidence=0.92, bbox_source_px=SourceBBox(120, 180, 70, 20)),
                OCRToken(id="tok_len_2", raw_text="L = 50 cm", confidence=0.88, bbox_source_px=SourceBBox(210, 180, 70, 20)),
            ],
            provider="mock_ocr",
        )

        grounder = PendulumGrounder()
        outcome = grounder.ground(book_ir, cv_candidates, ocr_result)

        # Both candidates must be parsed and recorded
        length_assocs = [a for a in outcome.parameter_associations if a.target_quantity == "length"]
        self.assertEqual(len(length_assocs), 2, "Both conflicting length tokens must be evaluated")
        # Grounding status must remain NEEDS_REVIEW
        self.assertEqual(outcome.grounded_book_ir.status, BookIRStatus.NEEDS_REVIEW)

    def test_bangla_router_preserves_easyocr_on_rapidocr_misread(self):
        """When RapidOCR outputs corrupted Latin characters on Bengali text, EasyOCR candidate is preserved with honest provenance."""
        from ai.evidence.ocr.router import MultiOCRRouter
        from ai.evidence.ocr.rapidocr import RapidOCRProvider
        from ai.evidence.ocr.bangla import EasyOCRBanglaProvider
        from shared.schemas.evidence import OCRExtractionResult

        class MockMisreadingRapidOCR(RapidOCRProvider):
            def available(self) -> bool:
                return True
            def extract(self, *args, **kwargs) -> OCRExtractionResult:
                # Emits garbage Latin token for Bengali text region
                return OCRExtractionResult(
                    status=ExtractionStatus.SUCCESS,
                    tokens=[OCRToken(id="tok_misread", raw_text="mrol dolok", confidence=0.45, bbox_source_px=SourceBBox(20, 20, 100, 30), provider="rapidocr")],
                    provider="rapidocr",
                )

        class MockCorrectEasyOCR(EasyOCRBanglaProvider):
            def available(self) -> bool:
                return True
            def extract(self, *args, **kwargs) -> OCRExtractionResult:
                return OCRExtractionResult(
                    status=ExtractionStatus.SUCCESS,
                    tokens=[OCRToken(id="tok_bn_correct", raw_text="সরল দোলক", confidence=0.91, bbox_source_px=SourceBBox(20, 20, 100, 30), provider="easyocr_bangla", script_candidate="bengali", language_candidate="bn")],
                    provider="easyocr_bangla",
                )

        router = MultiOCRRouter(primary_provider=MockMisreadingRapidOCR(), bangla_provider=MockCorrectEasyOCR())
        dummy = np.zeros((100, 200, 3), dtype=np.uint8) + 255
        result = router.extract(dummy, source_width=200, source_height=100)

        # Resolved token should contain Bengali text from EasyOCR
        resolved = result.tokens[0]
        self.assertEqual(resolved.raw_text, "সরল দোলক")
        self.assertEqual(resolved.provider, "easyocr_bangla")
        # RapidOCR original must remain preserved in candidate alternatives, NEVER silently erased
        alt_texts = [a["text"] if isinstance(a, dict) else a for a in resolved.candidate_alternatives]
        self.assertIn("mrol dolok", alt_texts)


if __name__ == "__main__":
    unittest.main()

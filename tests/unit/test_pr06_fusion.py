"""PR-06 Unit Tests — Evidence Fusion & Grounding Safety.

Tests:
  - Fusion Agreement: CV + SAM agreement promotes canonical coordinates
  - Fusion Conflict: CV + SAM spatial disagreement leaves coordinates None (AMBIGUOUS)
  - Missing Provider Resilience: Unavailable SAM continues with classical CV
  - Physical Length Safety: Visible 'L' symbol leaves physical length unknown, compiler NEEDS_REVIEW, scene=None
  - No Filename Routing: Target filename does not drive grounding or compiler outcomes
"""
from __future__ import annotations

import copy
import io
import os
import tempfile
import unittest

import numpy as np

from shared.schemas.evidence import (
    ExtractionStatus,
    GroundingState,
    MaskArtifact,
    OCRExtractionResult,
    OCRToken,
    SegmentationResult,
    SourceBBox,
    SourcePoint,
)
from shared.schemas.ingestion import (
    BookEntity,
    BookIR,
    BookIRStatus,
    PageFigure,
    PageIR,
    PageRegion,
    PhysicalValue,
    ProvenanceRecord,
    SourceAsset,
    compute_sha256,
)
from ai.evidence.grounding import PendulumGrounder
from ai.evidence.grounding.physical_value_parser import parse_physical_value_candidate
from ai.evidence.pipeline import EvidenceExtractionPipeline
from ai.evidence.ocr import MockOCRProvider, UnavailableOCRProvider
from ai.evidence.segmentation import MockSegmentationProvider, UnavailableSegmentationProvider
from ai.ingestion.PhysicsCompiler import PhysicsCompiler


def _build_test_book_ir() -> BookIR:
    return BookIR(
        version="1.0",
        source_asset_id="asset_test_01",
        page_ir_version="1.0",
        figure_id="fig_01",
        domain="mechanics",
        subtype="pendulum",
        entities=[
            BookEntity(id="e_pivot", type="pivot", label="O", position_source_px=None, geometry=None),
            BookEntity(id="e_bob", type="bob", label="m", position_source_px=None, geometry=None),
            BookEntity(id="e_string", type="string", label="L", position_source_px=None, geometry=None),
        ],
        relationships=[],
        parameters={},
        geometry={},
        provenance={"classification": "supported"},
        status=BookIRStatus.NEEDS_REVIEW,
    )


class TestPR06Fusion(unittest.TestCase):
    """Test suite for evidence fusion rules and safety invariants."""

    def test_fusion_agreement_success(self):
        """When CV and SAM centroids agree within tolerance, coordinates are promoted."""
        book_ir = _build_test_book_ir()
        grounder = PendulumGrounder()

        cv_candidates = {
            "best_proposal": {
                "bob": {
                    "center": SourcePoint(x=200.0, y=300.0),
                    "radius_px": 25.0,
                    "bounds": SourceBBox(x=175.0, y=275.0, width=50.0, height=50.0),
                },
                "string": {
                    "start": SourcePoint(x=150.0, y=80.0),
                    "end": SourcePoint(x=190.0, y=277.0),
                    "visible_length_px": 202.0,
                    "length_to_bob_center_px": 225.6,
                },
                "pivot": SourcePoint(x=150.0, y=80.0),
            }
        }

        # SAM mask centroid at (201.5, 301.0) -> dist = 1.8px (well within tolerance)
        seg_result = SegmentationResult(
            status=ExtractionStatus.SUCCESS,
            masks=[
                MaskArtifact(
                    id="mask_bob_test",
                    centroid_source_px=SourcePoint(x=201.5, y=301.0),
                    bbox_source_px=SourceBBox(x=174.0, y=274.0, width=52.0, height=52.0),
                    area_px=1960.0,
                    confidence=0.96,
                )
            ],
        )

        outcome = grounder.ground(
            book_ir=book_ir,
            cv_candidates=cv_candidates,
            ocr_result=None,
            seg_result=seg_result,
            source_width=400,
            source_height=500,
        )

        grounded = outcome.grounded_book_ir
        bob = next(e for e in grounded.entities if e.type == "bob")
        pivot = next(e for e in grounded.entities if e.type == "pivot")
        string = next(e for e in grounded.entities if e.type == "string")

        # Bob promoted
        self.assertIsNotNone(bob.position_source_px)
        self.assertEqual(bob.position_source_px["x"], 200.0)
        self.assertEqual(bob.position_source_px["y"], 300.0)
        self.assertEqual(bob.geometry["radius_px"], 25.0)
        self.assertEqual(bob.geometry["mask_ref"], "mask_bob_test")

        # Pivot promoted
        self.assertIsNotNone(pivot.position_source_px)
        self.assertEqual(pivot.position_source_px["x"], 150.0)
        self.assertEqual(pivot.position_source_px["y"], 80.0)

        # String promoted
        self.assertIsNotNone(string.geometry)
        self.assertAlmostEqual(string.geometry["length_px"], 225.6, places=1)

        # Diagnostics show all GROUNDED
        for d in outcome.diagnostics:
            self.assertEqual(d.grounding_state, GroundingState.GROUNDED)

    def test_fusion_conflict_disagreement_leaves_coordinates_none(self):
        """When CV and SAM centroids disagree beyond tolerance, position remains None."""
        book_ir = _build_test_book_ir()
        grounder = PendulumGrounder()

        cv_candidates = {
            "best_proposal": {
                "bob": {
                    "center": SourcePoint(x=200.0, y=300.0),
                    "radius_px": 20.0,
                    "bounds": SourceBBox(x=180.0, y=280.0, width=40.0, height=40.0),
                },
                "string": {
                    "start": SourcePoint(x=150.0, y=80.0),
                    "end": SourcePoint(x=190.0, y=280.0),
                    "visible_length_px": 203.0,
                    "length_to_bob_center_px": 225.6,
                },
                "pivot": SourcePoint(x=150.0, y=80.0),
            }
        }

        # SAM mask centroid at (265.0, 300.0) -> dist = 65px (conflict!)
        seg_result = SegmentationResult(
            status=ExtractionStatus.SUCCESS,
            masks=[
                MaskArtifact(
                    id="mask_conflict",
                    centroid_source_px=SourcePoint(x=265.0, y=300.0),
                    bbox_source_px=SourceBBox(x=245.0, y=280.0, width=40.0, height=40.0),
                    area_px=1250.0,
                    confidence=0.91,
                )
            ],
        )

        outcome = grounder.ground(
            book_ir=book_ir,
            cv_candidates=cv_candidates,
            ocr_result=None,
            seg_result=seg_result,
            source_width=400,
            source_height=500,
        )

        grounded = outcome.grounded_book_ir
        bob = next(e for e in grounded.entities if e.type == "bob")

        # CRITICAL TRUTHFULNESS INVARIANT: Coordinates must NOT be fabricated on conflict!
        self.assertIsNone(bob.position_source_px)
        self.assertIsNone(bob.geometry)

        # Diagnostics must record AMBIGUOUS conflict
        bob_diag = next(d for d in outcome.diagnostics if d.entity_id == bob.id)
        self.assertEqual(bob_diag.grounding_state, GroundingState.AMBIGUOUS)
        self.assertGreater(len(bob_diag.conflicts), 0)

    def test_missing_segmentation_provider_resilience(self):
        """When SAM is unavailable, classical CV continues and grounds bob safely."""
        book_ir = _build_test_book_ir()
        grounder = PendulumGrounder()

        cv_candidates = {
            "best_proposal": {
                "bob": {
                    "center": SourcePoint(x=200.0, y=300.0),
                    "radius_px": 20.0,
                    "bounds": SourceBBox(x=180.0, y=280.0, width=40.0, height=40.0),
                },
                "string": {
                    "start": SourcePoint(x=150.0, y=80.0),
                    "end": SourcePoint(x=190.0, y=280.0),
                    "visible_length_px": 203.0,
                    "length_to_bob_center_px": 225.6,
                },
                "pivot": SourcePoint(x=150.0, y=80.0),
            }
        }

        # Segmentation result is UNAVAILABLE
        seg_result = SegmentationResult(
            status=ExtractionStatus.UNAVAILABLE,
            masks=[],
            error="SAM not available",
        )

        outcome = grounder.ground(
            book_ir=book_ir,
            cv_candidates=cv_candidates,
            ocr_result=None,
            seg_result=seg_result,
            source_width=400,
            source_height=500,
        )

        grounded = outcome.grounded_book_ir
        bob = next(e for e in grounded.entities if e.type == "bob")
        self.assertIsNotNone(bob.position_source_px)
        self.assertEqual(bob.position_source_px["method"], "classical_cv")

    def test_physical_length_safety_invariant(self):
        """CRITICAL: Diagram with only symbol 'L' leaves physical length unknown, compiler NEEDS_REVIEW, scene=None."""
        book_ir = _build_test_book_ir()
        grounder = PendulumGrounder()

        cv_candidates = {
            "best_proposal": {
                "bob": {
                    "center": SourcePoint(x=200.0, y=300.0),
                    "radius_px": 20.0,
                    "bounds": SourceBBox(x=180.0, y=280.0, width=40.0, height=40.0),
                },
                "string": {
                    "start": SourcePoint(x=150.0, y=80.0),
                    "end": SourcePoint(x=190.0, y=280.0),
                    "visible_length_px": 203.0,
                    "length_to_bob_center_px": 225.6,
                },
                "pivot": SourcePoint(x=150.0, y=80.0),
            }
        }

        # OCR detects standalone 'L' label only (no numbers)
        ocr_result = OCRExtractionResult(
            status=ExtractionStatus.SUCCESS,
            tokens=[
                OCRToken(
                    id="t_L",
                    raw_text="L",
                    bbox_source_px=SourceBBox(x=160.0, y=170.0, width=15.0, height=15.0),
                    confidence=0.92,
                )
            ],
            provider="mock_ocr",
        )

        outcome = grounder.ground(
            book_ir=book_ir,
            cv_candidates=cv_candidates,
            ocr_result=ocr_result,
            seg_result=None,
            source_width=400,
            source_height=500,
        )

        grounded = outcome.grounded_book_ir

        # Verify pixel string length is present (geometry)
        self.assertIn("string_length_px", grounded.parameters)

        # Verify physical length in meters is UNKNOWN (not fabricated!)
        self.assertNotIn("length", grounded.parameters)
        self.assertNotIn("string_length_m", grounded.parameters)

        # Run through canonical PhysicsCompiler
        compiler = PhysicsCompiler()
        compile_result = compiler.compile(grounded)

        # Must NOT be READY, scene must be strictly None
        self.assertNotEqual(compile_result.status, "READY")
        self.assertEqual(compile_result.status, "NEEDS_REVIEW")
        self.assertIsNone(compile_result.scene)

    def test_no_filename_routing(self):
        """Testing identical evidence under arbitrary filenames produces identical grounding."""
        grounder = PendulumGrounder()
        cv_candidates = {
            "best_proposal": {
                "bob": {
                    "center": SourcePoint(x=100.0, y=150.0),
                    "radius_px": 15.0,
                    "bounds": SourceBBox(x=85.0, y=135.0, width=30.0, height=30.0),
                },
                "string": {
                    "start": SourcePoint(x=80.0, y=40.0),
                    "end": SourcePoint(x=95.0, y=136.0),
                    "visible_length_px": 97.0,
                    "length_to_bob_center_px": 111.8,
                },
                "pivot": SourcePoint(x=80.0, y=40.0),
            }
        }

        filenames = ["random.png", "pendulum.png", "cat.png", "diagram_99.jpg"]
        results = []

        for fname in filenames:
            ir = _build_test_book_ir()
            ir.provenance["original_filename"] = fname
            out = grounder.ground(ir, cv_candidates, None, None, 300, 300)
            bob_pos = out.grounded_book_ir.entities[1].position_source_px
            results.append((bob_pos["x"], bob_pos["y"]))

        # All results must be identical
        first = results[0]
        for r in results[1:]:
            self.assertEqual(r, first)


if __name__ == "__main__":
    unittest.main()

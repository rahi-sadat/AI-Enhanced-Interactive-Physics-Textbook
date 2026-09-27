"""PR-06 Integration Tests — Precise Evidence Extraction, Grounding & Fusion Pipeline.

Tests the full PR-06 flow:
  1. End-to-end pipeline with synthetic/fixture pendulum diagram:
     - OCR extracts text tokens (e.g. 'L', 'm', 'θ') in source_px.
     - Classical CV extracts candidates for bob, pivot, string in source_px.
     - Segmentation produces bob mask in source_px.
     - PendulumGrounder fuses evidence and promotes verified geometry to BookEntity objects.
     - Evidence registry is populated in BookIR.evidence.
     - Zero Parameter Fabrication: missing physical parameters (length, mass) remain unknown.
     - PhysicsCompiler honestly returns NEEDS_REVIEW with scene=None.
  2. Full API route integration via TestClient:
     - POST /api/ingest returns pipeline="PR-06", evidence, grounding diagnostics, and debug_overlay_url.
  3. Fusion Conflict handling:
     - Large spatial conflict between CV and segmentation prevents promotion (AMBIGUOUS state).
  4. Non-physics image:
     - Skips subtype-specific CV/segmentation grounding cleanly.
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import unittest
import numpy as np
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from shared.schemas.evidence import (
    EvidenceMethod,
    ExtractionStatus,
    GroundingState,
    SourcePoint,
    SourceBBox,
    MaskArtifact,
    SegmentationResult,
)
from shared.schemas.ingestion import BookIRStatus, PageFigure, PageIR, PageRegion, SourceAsset, compute_sha256
from shared.schemas.semantic import (
    SemanticAnalysisResult,
    SemanticConfidence,
    SemanticEntity,
    SemanticRelationship,
    SemanticVisibleLabel,
)
from ai.ingestion.PageIRBuilder import PageIRBuilder
from ai.ingestion.BookUnderstandingPipeline import BookUnderstandingPipeline
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.mock_provider import MockVisionProvider
from ai.evidence.pipeline import EvidenceExtractionPipeline
from ai.evidence.segmentation.mock import MockSegmentationProvider
from ai.evidence.ocr.mock import MockOCRProvider
from apps.api.main import app, _get_ingestion_pipeline
import apps.api.main as api_main


def _create_pendulum_image_bytes(width: int = 400, height: int = 400) -> bytes:
    """Draw a clean, deterministic pendulum diagram."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Support / ceiling line at top
    draw.line([(100, 40), (300, 40)], fill=(0, 0, 0), width=4)
    # Pivot dot
    draw.ellipse([197, 37, 203, 43], fill=(0, 0, 0))
    # String from (200, 40) to (200, 240)
    draw.line([(200, 40), (200, 240)], fill=(0, 0, 0), width=3)
    # Bob (circle radius 25 centered at 200, 265)
    draw.ellipse([175, 240, 225, 290], fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestPR06PipelineIntegration(unittest.TestCase):
    """End-to-end integration tests for PR-06 evidence extraction & grounding."""

    def setUp(self):
        self.client = TestClient(app)

    def test_01_end_to_end_pendulum_grounding(self):
        """End-to-end pipeline grounds pendulum entities and retains compiler safety."""
        img_bytes = _create_pendulum_image_bytes(400, 400)
        sha = compute_sha256(img_bytes)

        # Temporary storage for test
        storage_dir = Path("storage/test_pr06")
        storage_dir.mkdir(parents=True, exist_ok=True)
        img_path = storage_dir / f"pendulum_{sha[:8]}.png"
        img_path.write_bytes(img_bytes)

        asset = SourceAsset(
            id=f"asset_test_{sha[:8]}",
            sha256=sha,
            original_filename="pendulum_grounding_test.png",
            mime_type="image/png",
            byte_size=len(img_bytes),
            width_px=400,
            height_px=400,
            storage_path=str(img_path.resolve()),
        )

        page_ir_builder = PageIRBuilder()
        page_ir = page_ir_builder.build(asset, f"/storage/test_pr06/{img_path.name}")

        # PR-05 Mock Semantic Result
        mock_semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="mechanics",
            subtype="pendulum",
            confidence=SemanticConfidence(overall=0.92, is_physics=0.95, domain=0.92, subtype=0.90),
            entities=[
                SemanticEntity(temporary_id="ent_pivot", role="pivot", confidence=0.90),
                SemanticEntity(temporary_id="ent_bob", role="bob", confidence=0.92),
                SemanticEntity(temporary_id="ent_string", role="string", confidence=0.88),
            ],
            relationships=[
                SemanticRelationship(type="suspends", source_id="ent_pivot", target_id="ent_string"),
                SemanticRelationship(type="attaches", source_id="ent_string", target_id="ent_bob"),
            ],
            visible_labels=[
                SemanticVisibleLabel(text="L", confidence=0.85, verified=False),
            ],
        )

        vision_provider = MockVisionProvider(default_result=mock_semantic)
        book_pipeline = BookUnderstandingPipeline(analyzer=PhysicsVisionAnalyzer(provider=vision_provider))
        book_ir = book_pipeline.analyze(page_ir, asset=asset)

        # PR-05 invariant: positions are null before PR-06
        for ent in book_ir.entities:
            self.assertIsNone(ent.position_source_px)
            self.assertIsNone(ent.geometry)

        # Run PR-06 Evidence Extraction & Grounding
        evidence_pipeline = EvidenceExtractionPipeline(
            ocr_provider=MockOCRProvider(canned_tokens=[]),
            segmentation_provider=MockSegmentationProvider(),
        )

        grounded_book_ir = evidence_pipeline.extract_and_fuse(
            asset=asset,
            page_ir=page_ir,
            book_ir=book_ir,
        )

        # Verify Evidence Registry
        self.assertIn("evidence", grounded_book_ir.to_dict())
        self.assertGreater(len(grounded_book_ir.evidence), 0)

        # Verify Grounded Entities
        entities_by_type = {e.type: e for e in grounded_book_ir.entities}

        bob = entities_by_type.get("bob")
        self.assertIsNotNone(bob)
        self.assertIsNotNone(bob.position_source_px, "Bob position_source_px must be grounded")
        bob_x = bob.position_source_px["x"] if isinstance(bob.position_source_px, dict) else bob.position_source_px.x
        bob_y = bob.position_source_px["y"] if isinstance(bob.position_source_px, dict) else bob.position_source_px.y
        self.assertAlmostEqual(bob_x, 200.0, delta=5.0)
        self.assertAlmostEqual(bob_y, 265.0, delta=5.0)
        self.assertIsNotNone(bob.geometry)
        self.assertIn("bounds", bob.geometry)
        self.assertGreater(len(bob.evidence_refs), 0)

        pivot = entities_by_type.get("pivot")
        self.assertIsNotNone(pivot)
        self.assertIsNotNone(pivot.position_source_px, "Pivot position_source_px must be grounded")
        pivot_x = pivot.position_source_px["x"] if isinstance(pivot.position_source_px, dict) else pivot.position_source_px.x
        pivot_y = pivot.position_source_px["y"] if isinstance(pivot.position_source_px, dict) else pivot.position_source_px.y
        self.assertAlmostEqual(pivot_x, 200.0, delta=10.0)
        self.assertAlmostEqual(pivot_y, 40.0, delta=15.0)
        self.assertGreater(len(pivot.evidence_refs), 0)

        string_ent = entities_by_type.get("string")
        self.assertIsNotNone(string_ent)
        self.assertIsNotNone(string_ent.geometry)
        self.assertIn("start", string_ent.geometry)
        self.assertIn("end", string_ent.geometry)
        self.assertGreater(len(string_ent.evidence_refs), 0)

        # Verify Zero Parameter Fabrication
        # Diagram has no physical length in meters or mass in kg!
        self.assertNotIn("length", grounded_book_ir.parameters)
        self.assertNotIn("mass", grounded_book_ir.parameters)

        # PhysicsCompiler must honestly report NEEDS_REVIEW and scene=None
        compiler = PhysicsCompiler()
        compiler_result = compiler.compile(grounded_book_ir)
        self.assertEqual(compiler_result.status, "NEEDS_REVIEW")
        self.assertIsNone(compiler_result.scene)

    def test_02_api_ingest_pr06_payload(self):
        """POST /api/ingest returns PR-06 response structure with evidence and grounding."""
        img_bytes = _create_pendulum_image_bytes(300, 300)

        # Patch BookUnderstandingPipeline analyzer to mock semantic provider
        orig_pipeline = api_main._BOOK_PIPELINE
        mock_semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="mechanics",
            subtype="pendulum",
            confidence=SemanticConfidence(overall=0.95, is_physics=0.99, domain=0.98, subtype=0.95),
            entities=[
                SemanticEntity(temporary_id="e_pivot", role="pivot"),
                SemanticEntity(temporary_id="e_bob", role="bob"),
                SemanticEntity(temporary_id="e_string", role="string"),
            ],
        )
        api_main._BOOK_PIPELINE = BookUnderstandingPipeline(
            analyzer=PhysicsVisionAnalyzer(provider=MockVisionProvider(default_result=mock_semantic))
        )

        try:
            res = self.client.post(
                "/api/ingest",
                files={"file": ("test_pendulum.png", img_bytes, "image/png")},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()

            self.assertTrue(data["success"])
            self.assertEqual(data["pipeline"], "PR-06")
            self.assertIn("evidence", data)
            self.assertIn("grounding", data)
            self.assertIn("debug_overlay_url", data)
            self.assertEqual(data["domain"], "mechanics")
            self.assertEqual(data["scenario"], "pendulum")

            # Invariant: scene must remain null (no fabricated simulation)
            self.assertIsNone(data["scene"])

            # Verify entities inside book_ir are grounded
            entities = data["book_ir"]["entities"]
            bob_ents = [e for e in entities if e["type"] == "bob"]
            self.assertEqual(len(bob_ents), 1)
            pos = bob_ents[0].get("positionSourcePx") or bob_ents[0].get("position_source_px")
            self.assertIsNotNone(pos)
        finally:
            api_main._BOOK_PIPELINE = orig_pipeline

    def test_03_fusion_conflict_handling(self):
        """When CV and segmentation disagree beyond tolerance, position remains UNPROMOTED."""
        img_bytes = _create_pendulum_image_bytes(400, 400)
        sha = compute_sha256(img_bytes)

        storage_dir = Path("storage/test_pr06")
        storage_dir.mkdir(parents=True, exist_ok=True)
        img_path = storage_dir / f"conflict_{sha[:8]}.png"
        img_path.write_bytes(img_bytes)

        asset = SourceAsset(
            id=f"asset_conf_{sha[:8]}",
            sha256=sha,
            original_filename="conflict_test.png",
            mime_type="image/png",
            byte_size=len(img_bytes),
            width_px=400,
            height_px=400,
            storage_path=str(img_path.resolve()),
        )
        page_ir = PageIRBuilder().build(asset, f"/storage/test_pr06/{img_path.name}")

        mock_semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="mechanics",
            subtype="pendulum",
            confidence=SemanticConfidence(overall=0.90, is_physics=0.95, domain=0.90, subtype=0.90),
            entities=[SemanticEntity(temporary_id="e_bob", role="bob")],
        )

        book_ir = BookUnderstandingPipeline(
            analyzer=PhysicsVisionAnalyzer(provider=MockVisionProvider(default_result=mock_semantic))
        ).analyze(page_ir, asset=asset)

        # Mock segmentation that intentionally returns a mask FAR from the actual CV bob at (200, 265)
        # e.g., centroid at (50, 50)
        conflicting_mask = MaskArtifact(
            id="mask_conflict",
            source_asset_id=asset.id,
            source_width=400,
            source_height=400,
            bbox_source_px=SourceBBox(x=35, y=35, width=30, height=30),
            centroid_source_px=SourcePoint(x=50.0, y=50.0),
            area_px=900.0,
            confidence=0.95,
        )

        evidence_pipeline = EvidenceExtractionPipeline(
            ocr_provider=MockOCRProvider(canned_tokens=[]),
            segmentation_provider=MockSegmentationProvider(canned_masks=[conflicting_mask]),
        )

        grounded_book_ir = evidence_pipeline.extract_and_fuse(
            asset=asset,
            page_ir=page_ir,
            book_ir=book_ir,
        )

        bob = [e for e in grounded_book_ir.entities if e.type == "bob"][0]
        # Invariant: Disagreement must NOT promote canonical position!
        self.assertIsNone(bob.position_source_px, "Conflicting candidate must not promote position_source_px")
        self.assertIsNone(bob.geometry, "Conflicting candidate must not promote geometry")

        # Grounding diagnostic must record AMBIGUOUS state
        diagnostics = grounded_book_ir.provenance.get("grounding_diagnostics", [])
        bob_diag = [d for d in diagnostics if (d.get("entityId") == "e_bob" or d.get("entity_id") == "e_bob")]
        self.assertGreater(len(bob_diag), 0)
        state = bob_diag[0].get("groundingState") or bob_diag[0].get("grounding_state")
        self.assertIn(state, (GroundingState.AMBIGUOUS, GroundingState.AMBIGUOUS.value))

    def test_04_non_physics_image_skips_grounding(self):
        """Non-physics image skips subtype grounding without crashing."""
        img_bytes = _create_pendulum_image_bytes(200, 200)
        sha = compute_sha256(img_bytes)

        storage_dir = Path("storage/test_pr06")
        storage_dir.mkdir(parents=True, exist_ok=True)
        img_path = storage_dir / f"non_phys_{sha[:8]}.png"
        img_path.write_bytes(img_bytes)

        asset = SourceAsset(
            id=f"asset_nonphys_{sha[:8]}",
            sha256=sha,
            original_filename="cat.png",
            mime_type="image/png",
            byte_size=len(img_bytes),
            width_px=200,
            height_px=200,
            storage_path=str(img_path.resolve()),
        )
        page_ir = PageIRBuilder().build(asset, f"/storage/test_pr06/{img_path.name}")

        mock_non_phys = SemanticAnalysisResult(
            classification="non_physics",
            is_physics=False,
            domain=None,
            subtype=None,
            confidence=SemanticConfidence(overall=0.1, is_physics=0.05),
            entities=[],
        )

        book_ir = BookUnderstandingPipeline(
            analyzer=PhysicsVisionAnalyzer(provider=MockVisionProvider(default_result=mock_non_phys))
        ).analyze(page_ir, asset=asset)

        evidence_pipeline = EvidenceExtractionPipeline(
            ocr_provider=MockOCRProvider(canned_tokens=[]),
            segmentation_provider=MockSegmentationProvider(),
        )

        grounded_book_ir = evidence_pipeline.extract_and_fuse(
            asset=asset,
            page_ir=page_ir,
            book_ir=book_ir,
        )

        # Invariant: status remains UNRESOLVED, no entities fabricated
        self.assertEqual(grounded_book_ir.status, BookIRStatus.UNRESOLVED)
        self.assertEqual(len(grounded_book_ir.entities), 0)


if __name__ == "__main__":
    unittest.main()

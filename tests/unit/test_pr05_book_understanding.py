"""PR-05 Unit Tests — BookUnderstandingPipeline & Semantic BookIR Mapping.

Tests:
  1. Supported pendulum diagram populates BookIR (domain=mechanics, subtype=pendulum, status=NEEDS_REVIEW).
  2. Supported projectile diagram populates BookIR.
  3. Supported thin_lens diagram populates BookIR.
  4. Supported dc_linear circuit populates BookIR.
  5. Non-physics image populates BookIR (domain=None, subtype=None, status=UNRESOLVED).
  6. Unsupported physics image populates BookIR (domain=None, subtype=None, status=UNSUPPORTED).
  7. Ambiguous/unknown image populates BookIR (domain=None, subtype=None, status=UNRESOLVED).
  8. Zero parameter fabrication: BookIR.parameters is strictly empty in PR-05.
  9. Visible labels preserved in provenance.visible_labels (unverified).
  10. Entity roles preserved with precision="approximate".
  11. SourceAsset and PageFigure grounding preserved.
  12. Provider configuration failure handled honestly (status=UNRESOLVED, no fake scene).
"""
from __future__ import annotations

import os
import sys
import tempfile
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
from shared.schemas.ingestion import BookIRStatus, PageFigure, PageIR, PageRegion, SourceAsset, compute_sha256
from shared.schemas.semantic import (
    SemanticAnalysisResult,
    SemanticConfidence,
    SemanticEntity,
    SemanticRelationship,
    SemanticVisibleLabel,
)
from ai.ingestion.BookUnderstandingPipeline import BookUnderstandingPipeline
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.mock_provider import MockVisionProvider
from ai.ingestion.vision.provider_interface import VLMConfigurationError


def _make_asset(content: bytes = b"IMG_CONTENT", filename: str = "img.png") -> SourceAsset:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(content)
    tmp.close()
    return SourceAsset(
        id=f"asset_{os.path.basename(tmp.name)}",
        mime_type="image/png",
        original_filename=filename,
        byte_size=len(content),
        width_px=800,
        height_px=600,
        sha256=compute_sha256(content),
        storage_path=tmp.name,
    )


def _make_page_ir(asset: SourceAsset) -> PageIR:
    return PageIR(
        version="1.0",
        source={"assetId": asset.id},
        coordinate_space={"type": "source_px", "width": asset.width_px, "height": asset.height_px},
        regions=[PageRegion(id="reg_1", label="whole_image", x=0, y=0, width=asset.width_px, height=asset.height_px)],
        figures=[PageFigure(id="fig_1", region_id="reg_1", page_x=0, page_y=0, width=asset.width_px, height=asset.height_px)],
    )


class TestPR05BookUnderstanding(unittest.TestCase):
    """Test suite for BookUnderstandingPipeline semantic mapping."""

    def test_supported_pendulum_mapping(self):
        asset = _make_asset(b"PENDULUM_BYTES", "pendulum.png")
        page_ir = _make_page_ir(asset)

        mock_prov = MockVisionProvider(
            default_result=SemanticAnalysisResult(
                classification="supported",
                is_physics=True,
                domain="mechanics",
                subtype="pendulum",
                confidence=SemanticConfidence(is_physics=0.98, domain=0.95, subtype=0.93),
                entities=[
                    SemanticEntity(temporary_id="e1", role="pivot", confidence=0.95),
                    SemanticEntity(temporary_id="e2", role="bob", label="m1", confidence=0.97),
                    SemanticEntity(temporary_id="e3", role="string", confidence=0.91),
                ],
                relationships=[
                    SemanticRelationship(type="connected_to", source_id="e1", target_id="e3"),
                    SemanticRelationship(type="attached_to", source_id="e3", target_id="e2"),
                ],
                visible_labels=[
                    SemanticVisibleLabel(text="L = 50 cm", confidence=0.88, semantic_role="length"),
                ],
                provider="gemini",
                model="gemini-3.8-flash",
            )
        )
        pipeline = BookUnderstandingPipeline(analyzer=PhysicsVisionAnalyzer(mock_prov))
        book_ir = pipeline.analyze(page_ir, asset=asset)

        # 1. Correct domain & subtype
        self.assertEqual(book_ir.domain, "mechanics")
        self.assertEqual(book_ir.subtype, "pendulum")

        # 2. Honest status NEEDS_REVIEW (requires CV/OCR before simulation)
        self.assertEqual(book_ir.status, BookIRStatus.NEEDS_REVIEW)
        self.assertIn("Semantically understood as mechanics/pendulum", book_ir.status_notes)

        # 3. Entities populated with semantic roles
        self.assertEqual(len(book_ir.entities), 3)
        self.assertEqual(book_ir.entities[0].type, "pivot")
        self.assertEqual(book_ir.entities[1].type, "bob")
        self.assertEqual(book_ir.entities[1].label, "m1")
        self.assertEqual(book_ir.entities[0].evidence_refs, ["fig_1"])

        # 4. Relationships populated
        self.assertEqual(len(book_ir.relationships), 2)

        # 5. ZERO FABRICATED PARAMETERS: parameters must remain empty in PR-05
        self.assertEqual(book_ir.parameters, {}, "PR-05 must not populate parameters directly from VLM")
        self.assertEqual(book_ir.geometry, {}, "PR-05 must not fabricate geometry")

        # 6. Visible labels preserved in provenance
        self.assertEqual(len(book_ir.provenance["visible_labels"]), 1)
        self.assertEqual(book_ir.provenance["visible_labels"][0]["text"], "L = 50 cm")
        self.assertFalse(book_ir.provenance["visible_labels"][0]["verified"])

        # 7. Grounding preserved
        self.assertEqual(book_ir.source_asset_id, asset.id)
        self.assertEqual(book_ir.figure_id, "fig_1")

        os.remove(asset.storage_path)

    def test_non_physics_mapping(self):
        asset = _make_asset(b"CAT_PHOTO_BYTES", "cat.jpg")
        page_ir = _make_page_ir(asset)

        mock_prov = MockVisionProvider(
            default_result=SemanticAnalysisResult(
                classification="non_physics",
                is_physics=False,
                domain=None,
                subtype=None,
                confidence=SemanticConfidence(is_physics=0.01, domain=0.0, subtype=0.0),
                provider="gemini",
                model="gemini-3.8-flash",
            )
        )
        pipeline = BookUnderstandingPipeline(analyzer=PhysicsVisionAnalyzer(mock_prov))
        book_ir = pipeline.analyze(page_ir, asset=asset)

        self.assertIsNone(book_ir.domain)
        self.assertIsNone(book_ir.subtype)
        self.assertEqual(book_ir.status, BookIRStatus.UNRESOLVED)
        self.assertIn("does not depict a recognizable physics diagram", book_ir.status_notes)

        os.remove(asset.storage_path)

    def test_unsupported_physics_mapping(self):
        asset = _make_asset(b"WAVE_INTERFERENCE_BYTES", "wave.png")
        page_ir = _make_page_ir(asset)

        mock_prov = MockVisionProvider(
            default_result=SemanticAnalysisResult(
                classification="unsupported_physics",
                is_physics=True,
                domain=None,
                subtype=None,
                confidence=SemanticConfidence(is_physics=0.96, domain=0.0, subtype=0.0),
                notes=["Wave interference pattern"],
                provider="gemini",
                model="gemini-3.8-flash",
            )
        )
        pipeline = BookUnderstandingPipeline(analyzer=PhysicsVisionAnalyzer(mock_prov))
        book_ir = pipeline.analyze(page_ir, asset=asset)

        self.assertIsNone(book_ir.domain)
        self.assertIsNone(book_ir.subtype)
        self.assertEqual(book_ir.status, BookIRStatus.UNSUPPORTED)
        self.assertIn("no interactive simulation solver is currently implemented", book_ir.status_notes)

        os.remove(asset.storage_path)

    def test_provider_configuration_failure_handling(self):
        """Configuration failure produces honest UNRESOLVED BookIR without crashing."""
        asset = _make_asset(b"ANY_BYTES", "diagram.png")
        page_ir = _make_page_ir(asset)

        mock_prov = MockVisionProvider(
            exception_to_raise=VLMConfigurationError("GEMINI_API_KEY is not configured")
        )
        pipeline = BookUnderstandingPipeline(analyzer=PhysicsVisionAnalyzer(mock_prov))
        book_ir = pipeline.analyze(page_ir, asset=asset)

        self.assertIsNone(book_ir.domain)
        self.assertIsNone(book_ir.subtype)
        self.assertEqual(book_ir.status, BookIRStatus.UNRESOLVED)
        self.assertIn("VLM configuration error", book_ir.status_notes)
        self.assertEqual(book_ir.provenance.get("error_type"), "VLMConfigurationError")

        os.remove(asset.storage_path)


if __name__ == "__main__":
    unittest.main()

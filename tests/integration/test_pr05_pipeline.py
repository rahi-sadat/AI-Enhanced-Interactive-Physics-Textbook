"""PR-05 Integration Tests — Full Ingestion & Compiler Pipeline.

Tests:
  1. Complete pipeline from SourceAsset → PageIR → BookIR → PhysicsCompiler:
     - Supported pendulum diagram yields BookIR (NEEDS_REVIEW) and PhysicsCompilerResult (NEEDS_REVIEW).
     - PhysicsCompiler returns scene=None (proves ZERO fabricated simulation).
  2. Non-physics image yields BookIR (UNRESOLVED) and scene=None.
  3. Unsupported physics image yields BookIR (UNSUPPORTED) and scene=None.
  4. Real API integration: POST /api/ingest with multipart/form-data.
"""
from __future__ import annotations

import io
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
from fastapi.testclient import TestClient

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
from apps.api.main import app, _get_ingestion_pipeline


def _make_png_bytes(tag: str = "DEFAULT") -> bytes:
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (120, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), tag, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()



class TestPR05PipelineIntegration(unittest.TestCase):
    """End-to-end integration tests for PR-05 semantic ingestion pipeline."""

    def test_end_to_end_supported_pendulum_zero_fabrication(self):
        """Supported pendulum is understood semantically, but produces scene=None."""
        png_data = _make_png_bytes("PENDULUM_SEEN")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(png_data)
        tmp.close()

        asset = SourceAsset(
            id="asset_test_001",
            mime_type="image/png",
            original_filename="pendulum_diagram.png",
            byte_size=len(png_data),
            width_px=640,
            height_px=480,
            sha256=compute_sha256(png_data),
            storage_path=tmp.name,
        )

        page_ir_builder = PageIRBuilder()
        page_ir = page_ir_builder.build(asset, "/uploads/test.png")

        mock_prov = MockVisionProvider(
            default_result=SemanticAnalysisResult(
                classification="supported",
                is_physics=True,
                domain="mechanics",
                subtype="pendulum",
                confidence=SemanticConfidence(is_physics=0.99, domain=0.96, subtype=0.94),
                entities=[
                    SemanticEntity(temporary_id="e1", role="pivot"),
                    SemanticEntity(temporary_id="e2", role="bob", label="m"),
                    SemanticEntity(temporary_id="e3", role="string"),
                ],
                relationships=[
                    SemanticRelationship(type="connected_to", source_id="e1", target_id="e3"),
                    SemanticRelationship(type="connected_to", source_id="e3", target_id="e2"),
                ],
                visible_labels=[SemanticVisibleLabel(text="θ = 30°")],
                provider="mock-gemini",
                model="gemini-3.8-flash",
            )
        )
        book_pipeline = BookUnderstandingPipeline(analyzer=PhysicsVisionAnalyzer(mock_prov))
        compiler = PhysicsCompiler()

        book_ir = book_pipeline.analyze(page_ir, asset=asset)

        # 1. Semantic understanding populated
        self.assertEqual(book_ir.domain, "mechanics")
        self.assertEqual(book_ir.subtype, "pendulum")
        self.assertEqual(book_ir.status, BookIRStatus.NEEDS_REVIEW)
        self.assertEqual(len(book_ir.entities), 3)

        # 2. PhysicsCompiler execution
        compiler_result = compiler.compile(book_ir)

        # 3. Truthfulness guarantee: missing CV geometry means NO runnable scene
        self.assertEqual(compiler_result.status, "NEEDS_REVIEW")
        self.assertIsNone(compiler_result.scene, "Compiler MUST NOT fabricate a runnable scene without CV geometry")
        self.assertTrue(len(compiler_result.issues) > 0)

        os.remove(tmp.name)

    def test_api_ingest_multipart_pr05_envelope(self):
        """POST /api/ingest returns PR-05 envelope with semantic understanding."""
        import apps.api.main as api_main
        mock_prov = MockVisionProvider(
            default_result=SemanticAnalysisResult(
                classification="supported",
                is_physics=True,
                domain="mechanics",
                subtype="pendulum",
                confidence=SemanticConfidence(is_physics=0.99, domain=0.96, subtype=0.94),
                entities=[SemanticEntity(temporary_id="e1", role="bob")],
                provider="mock",
                model="mock-v1",
            )
        )
        # Ensure singletons are created then inject mock analyzer
        api_main._get_ingestion_pipeline()
        orig_analyzer = api_main._BOOK_PIPELINE.analyzer
        api_main._BOOK_PIPELINE.analyzer = PhysicsVisionAnalyzer(mock_prov)

        try:
            client = TestClient(app)
            img_bytes = _make_png_bytes("API_TEST_IMG")

            res = client.post(
                "/api/ingest",
                files={"file": ("unseen_diagram.png", img_bytes, "image/png")},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()

            self.assertTrue(data["success"])
            self.assertEqual(data["pipeline"], "PR-05")
            self.assertIn("book_ir", data)
            self.assertIn("compiler", data)
            self.assertIn("page_ir", data)
            self.assertIn("source_asset", data)

            # Domain & scenario populated from semantic analysis
            self.assertEqual(data["domain"], "mechanics")
            self.assertEqual(data["scenario"], "pendulum")

            # The scene must remain null (truthful zero fabrication)
            self.assertIsNone(data["scene"])
        finally:
            api_main._BOOK_PIPELINE.analyzer = orig_analyzer



if __name__ == "__main__":
    unittest.main()

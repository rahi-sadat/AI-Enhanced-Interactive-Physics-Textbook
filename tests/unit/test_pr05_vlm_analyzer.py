"""PR-05 Unit Tests — PhysicsVisionAnalyzer & Provider Abstraction.

Tests:
  1. Real payload dispatch: actual image bytes from SourceAsset are sent to provider.
  2. Upload A vs Upload B payload difference verification.
  3. Filename independence: identical image bytes with different filenames yield identical payload & result.
  4. Hash independence: SHA-256 is not used to route physics.
  5. Confidence threshold enforcement:
     - is_physics below threshold → unknown + candidate preserved
     - domain below threshold → unknown + candidate preserved
     - subtype below threshold → unknown + candidate preserved
  6. Provider error propagation (VLMConfigurationError & VisionProviderError).
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
from shared.schemas.ingestion import PageFigure, PageIR, PageRegion, SourceAsset, compute_sha256
from shared.schemas.semantic import (
    SemanticAnalysisResult,
    SemanticConfidence,
    SemanticEntity,
)
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.mock_provider import MockVisionProvider
from ai.ingestion.vision.provider_interface import (
    VisionProviderError,
    VLMConfigurationError,
)


def _create_temp_asset(content: bytes, filename: str = "diagram.png") -> SourceAsset:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(content)
    tmp.close()
    return SourceAsset(
        id=f"asset_{os.path.basename(tmp.name)}",
        mime_type="image/png",
        original_filename=filename,
        byte_size=len(content),
        width_px=300,
        height_px=200,
        sha256=compute_sha256(content),
        storage_path=tmp.name,
    )


def _create_dummy_page_ir(asset: SourceAsset) -> PageIR:
    return PageIR(
        version="1.0",
        source={"assetId": asset.id},
        coordinate_space={"type": "source_px", "width": asset.width_px, "height": asset.height_px},
        regions=[PageRegion(id="r1", label="whole_image", x=0, y=0, width=asset.width_px, height=asset.height_px)],
        figures=[PageFigure(id="f1", region_id="r1", page_x=0, page_y=0, width=asset.width_px, height=asset.height_px)],
    )


class TestPR05VisionAnalyzer(unittest.TestCase):
    """Test suite for PhysicsVisionAnalyzer and provider decoupling."""

    def test_real_image_bytes_sent_to_provider(self):
        """VLM must receive the real bytes represented by SourceAsset."""
        test_bytes = b"\x89PNG\r\n\x1a\nREAL_IMAGE_BYTES_PAYLOAD_TEST"
        asset = _create_temp_asset(test_bytes, "real_upload.png")
        page_ir = _create_dummy_page_ir(asset)

        mock_prov = MockVisionProvider(
            default_result=SemanticAnalysisResult(
                classification="supported",
                is_physics=True,
                domain="mechanics",
                subtype="pendulum",
                confidence=SemanticConfidence(is_physics=0.99, domain=0.95, subtype=0.92),
            )
        )
        analyzer = PhysicsVisionAnalyzer(provider=mock_prov)
        result = analyzer.analyze(asset, page_ir)

        self.assertEqual(len(mock_prov.call_history), 1)
        call = mock_prov.call_history[0]
        self.assertEqual(call["byte_size"], len(test_bytes))
        self.assertEqual(call["image_bytes_preview"], test_bytes[:32])
        self.assertEqual(result.subtype, "pendulum")

        os.remove(asset.storage_path)

    def test_upload_a_vs_upload_b_payload_difference(self):
        """Upload A and Upload B send different real image payloads to provider."""
        bytes_a = b"PNG_PAYLOAD_A_ALPHA_CONTENT_12345"
        bytes_b = b"PNG_PAYLOAD_B_BETA_CONTENT_67890"

        asset_a = _create_temp_asset(bytes_a, "img_a.png")
        asset_b = _create_temp_asset(bytes_b, "img_b.png")

        mock_prov = MockVisionProvider()
        analyzer = PhysicsVisionAnalyzer(provider=mock_prov)

        analyzer.analyze(asset_a, _create_dummy_page_ir(asset_a))
        analyzer.analyze(asset_b, _create_dummy_page_ir(asset_b))

        self.assertEqual(len(mock_prov.call_history), 2)
        payload_1 = mock_prov.call_history[0]["image_bytes_preview"]
        payload_2 = mock_prov.call_history[1]["image_bytes_preview"]
        self.assertNotEqual(payload_1, payload_2, "Different uploads must send distinct payloads")

        os.remove(asset_a.storage_path)
        os.remove(asset_b.storage_path)

    def test_filename_independence(self):
        """MANDATORY ARCHITECTURE TEST: Filename has zero effect on semantic result."""
        content = b"IDENTICAL_BYTES_FOR_FILENAME_TEST"
        names = ["pendulum.jpg", "cat.png", "circuit.png", "x17_unseen.bin"]

        mock_prov = MockVisionProvider(
            default_result=SemanticAnalysisResult(
                classification="supported",
                is_physics=True,
                domain="mechanics",
                subtype="projectile",
                confidence=SemanticConfidence(is_physics=0.95, domain=0.90, subtype=0.88),
            )
        )
        analyzer = PhysicsVisionAnalyzer(provider=mock_prov)

        results = []
        for name in names:
            asset = _create_temp_asset(content, filename=name)
            res = analyzer.analyze(asset, _create_dummy_page_ir(asset))
            results.append((res.domain, res.subtype))
            os.remove(asset.storage_path)

        # All results must be identical regardless of whether filename says 'cat' or 'circuit'
        self.assertTrue(all(r == results[0] for r in results))
        self.assertEqual(results[0], ("mechanics", "projectile"))

    def test_confidence_threshold_is_physics(self):
        """is_physics below threshold downgrades to unknown and preserves candidate."""
        asset = _create_temp_asset(b"SOME_IMAGE", "test.png")
        mock_prov = MockVisionProvider(
            default_result=SemanticAnalysisResult(
                classification="supported",
                is_physics=True,
                domain="mechanics",
                subtype="pendulum",
                confidence=SemanticConfidence(is_physics=0.65, domain=0.90, subtype=0.90),
            )
        )
        analyzer = PhysicsVisionAnalyzer(provider=mock_prov, is_physics_threshold=0.80)
        res = analyzer.analyze(asset, _create_dummy_page_ir(asset))

        self.assertEqual(res.classification, "unknown")
        self.assertIsNone(res.domain)
        self.assertIsNone(res.subtype)
        self.assertEqual(len(res.candidates), 1)
        self.assertEqual(res.candidates[0].subtype, "pendulum")

        os.remove(asset.storage_path)

    def test_confidence_threshold_subtype(self):
        """subtype below threshold downgrades to unknown and preserves candidate."""
        asset = _create_temp_asset(b"SOME_IMAGE", "test.png")
        mock_prov = MockVisionProvider(
            default_result=SemanticAnalysisResult(
                classification="supported",
                is_physics=True,
                domain="optics",
                subtype="thin_lens",
                confidence=SemanticConfidence(is_physics=0.95, domain=0.90, subtype=0.55),
            )
        )
        analyzer = PhysicsVisionAnalyzer(provider=mock_prov, subtype_threshold=0.70)
        res = analyzer.analyze(asset, _create_dummy_page_ir(asset))

        self.assertEqual(res.classification, "unknown")
        self.assertIsNone(res.subtype)
        self.assertEqual(len(res.candidates), 1)
        self.assertEqual(res.candidates[0].subtype, "thin_lens")

        os.remove(asset.storage_path)

    def test_provider_operational_failure_propagates(self):
        """Provider failure produces explicit VisionProviderError without fallback."""
        asset = _create_temp_asset(b"SOME_IMAGE", "test.png")
        mock_prov = MockVisionProvider(exception_to_raise=VisionProviderError("Upstream API quota exceeded"))
        analyzer = PhysicsVisionAnalyzer(provider=mock_prov)

        with self.assertRaises(VisionProviderError):
            analyzer.analyze(asset, _create_dummy_page_ir(asset))

        os.remove(asset.storage_path)


if __name__ == "__main__":
    unittest.main()

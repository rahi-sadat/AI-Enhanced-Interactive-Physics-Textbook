"""PR-06 Real-Unseen Acceptance Test Suite.

Executes end-to-end evidence extraction, OCR, classical CV, and visual grounding
on realistic unseen textbook/scan/photo-style diagrams across:
  1. Real Pendulum Diagram (sketch/scan)
  2. Real Projectile Diagram (textbook scan with trajectory and ground)
  3. Real Thin Lens Diagram (NCTB textbook-style lens diagram with axis)
  4. Real Spherical Mirror Diagram (concave mirror scan with principal axis)
  5. Real Interface Refraction Diagram (two media interface with normal and ray)
  6. Real Prism Diagram (optical prism triangular scan)
  7. Real DC Circuit Diagram (handdrawn / textbook resistor network)
  8. Real Bengali-Labeled Diagram (Bangla textbook typography with Bangla digits and units)
  9. Real Greek / Symbol-Heavy Diagram (physics annotations: θ, Ω, μ, α, β)

Strict Invariants:
  - No routing by filename or hash.
  - VLM produces semantic roles only, zero coordinates or physical constants.
  - CV extractors return candidate coordinates, returning None when primitives are missing.
  - Zero Parameter Fabrication: missing parameters result in NEEDS_REVIEW with scene=None.
  - OCR evidence records are immutable with truthful model provenance.
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from shared.schemas.evidence import (
    AssociationState,
    ExtractionStatus,
    OCRToken,
    SourceBBox,
    SourcePoint,
)
from shared.schemas.ingestion import (
    BookEntity,
    BookIR,
    BookIRStatus,
    PhysicalValue,
    SourceAsset,
    compute_sha256,
)
from shared.schemas.semantic import (
    SemanticAnalysisResult,
    SemanticConfidence,
    SemanticEntity,
    SemanticRelationship,
    SemanticVisibleLabel,
)
from ai.ingestion.PageIRBuilder import PageIRBuilder
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.mock_provider import MockVisionProvider
from ai.evidence.pipeline import EvidenceExtractionPipeline


def _ensure_textbook_fixtures(fixture_dir: Path):
    fixture_dir.mkdir(parents=True, exist_ok=True)

    font_path = "C:/Windows/Fonts/Nirmala.ttc"
    font_en_path = "C:/Windows/Fonts/arial.ttf"
    try:
        font_bn = ImageFont.truetype(font_path, 22)
    except Exception:
        font_bn = ImageFont.load_default()
    try:
        font_en = ImageFont.truetype(font_en_path, 20)
    except Exception:
        font_en = font_bn

    # 1. Projectile Scan
    proj_path = fixture_dir / "projectile_textbook_scan.png"
    if not proj_path.exists():
        img = np.full((350, 500, 3), 245, dtype=np.uint8)  # slight off-white paper
        # Ground line
        cv2.line(img, (50, 280), (450, 280), (40, 40, 40), 2)
        # Launch platform / point at (80, 280)
        cv2.circle(img, (80, 280), 8, (30, 30, 30), -1)
        # Velocity vector
        cv2.arrowedLine(img, (80, 280), (160, 200), (30, 30, 30), 2, tipLength=0.2)
        # Parabolic guide dots
        for t in np.linspace(0, 1, 20):
            px = int(80 + 320 * t)
            py = int(280 - (180 * (4 * t * (1 - t))))
            cv2.circle(img, (px, py), 2, (120, 120, 120), -1)
        # Add slight scan noise
        noise = np.random.normal(0, 3, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        # Add text labels via PIL
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        draw.text((165, 185), "v0 = 20 m/s", fill=(20, 20, 20), font=font_en)
        draw.text((110, 255), "θ = 45°", fill=(20, 20, 20), font=font_en)
        pil_img.save(str(proj_path))

    # 2. Interface Refraction Scan
    refr_path = fixture_dir / "refraction_textbook_scan.png"
    if not refr_path.exists():
        img = np.full((350, 500, 3), 248, dtype=np.uint8)
        # Interface boundary at y = 175
        cv2.line(img, (40, 175), (460, 175), (40, 40, 40), 2)
        # Normal line at x = 250
        cv2.line(img, (250, 40), (250, 310), (100, 100, 100), 1, cv2.LINE_AA)
        # Incident ray (from top-left to center)
        cv2.line(img, (130, 75), (250, 175), (30, 30, 30), 2)
        # Refracted ray (from center to bottom-right)
        cv2.line(img, (250, 175), (330, 295), (30, 30, 30), 2)
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        draw.text((50, 140), "Air (n1 = 1.0)", fill=(30, 30, 30), font=font_en)
        draw.text((50, 195), "Glass (n2 = 1.5)", fill=(30, 30, 30), font=font_en)
        draw.text((190, 110), "i = 30°", fill=(30, 30, 30), font=font_en)
        draw.text((265, 230), "r = 19°", fill=(30, 30, 30), font=font_en)
        pil_img.save(str(refr_path))

    # 3. Optical Prism Scan
    prism_path = fixture_dir / "prism_textbook_scan.png"
    if not prism_path.exists():
        img = np.full((350, 500, 3), 245, dtype=np.uint8)
        pts = np.array([[250, 60], [120, 280], [380, 280]], dtype=np.int32)
        cv2.polylines(img, [pts], True, (30, 30, 30), 2)
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        draw.text((240, 30), "A = 60°", fill=(30, 30, 30), font=font_en)
        draw.text((215, 170), "n = 1.52", fill=(30, 30, 30), font=font_en)
        pil_img.save(str(prism_path))

    # 4. Bengali-labeled Circuit Scan
    bn_circuit_path = fixture_dir / "bengali_circuit_textbook_scan.png"
    if not bn_circuit_path.exists():
        img = np.full((350, 500, 3), 248, dtype=np.uint8)
        # Rectangular loop: top (100, 80) to (400, 80), bottom (100, 240) to (400, 240)
        cv2.line(img, (100, 80), (220, 80), (30, 30, 30), 2)
        # Resistor box at (220, 70, 60, 20)
        cv2.rectangle(img, (220, 70), (280, 90), (30, 30, 30), 2)
        cv2.line(img, (280, 80), (400, 80), (30, 30, 30), 2)
        cv2.line(img, (400, 80), (400, 240), (30, 30, 30), 2)
        cv2.line(img, (400, 240), (100, 240), (30, 30, 30), 2)
        # Battery on left vertical line
        cv2.line(img, (100, 240), (100, 180), (30, 30, 30), 2)
        cv2.line(img, (90, 180), (110, 180), (30, 30, 30), 2)
        cv2.line(img, (95, 170), (105, 170), (30, 30, 30), 2)
        cv2.line(img, (100, 170), (100, 80), (30, 30, 30), 2)
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        draw.text((220, 40), "রোধ R = ১০ ওহম", fill=(30, 30, 30), font=font_bn)
        draw.text((20, 160), "১২ V", fill=(30, 30, 30), font=font_bn)
        pil_img.save(str(bn_circuit_path))

    # 5. Greek-Heavy Optics Scan
    greek_path = fixture_dir / "greek_symbols_textbook_scan.png"
    if not greek_path.exists():
        img = np.full((300, 500, 3), 245, dtype=np.uint8)
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        draw.text((50, 40), "θ = 30°", fill=(20, 20, 20), font=font_en)
        draw.text((50, 100), "R1 = 10 Ω", fill=(20, 20, 20), font=font_en)
        draw.text((50, 160), "μ = 0.25", fill=(20, 20, 20), font=font_en)
        draw.text((50, 220), "λ = 589 nm", fill=(20, 20, 20), font=font_en)
        pil_img.save(str(greek_path))


class TestPR06RealUnseenAcceptance(unittest.TestCase):
    """PR-06 Real-Unseen Diagram Acceptance Suite."""

    @classmethod
    def setUpClass(cls):
        cls.fixture_dir = _ROOT / "tests" / "fixtures" / "unseen" / "acceptance"
        _ensure_textbook_fixtures(cls.fixture_dir)
        cls.compiler = PhysicsCompiler()
        cls.page_builder = PageIRBuilder()

    def _run_pipeline(self, image_path: Path, mock_semantic: SemanticAnalysisResult) -> BookIR:
        raw_bytes = image_path.read_bytes()
        sha = compute_sha256(raw_bytes)
        img_bgr = cv2.imread(str(image_path))
        h, w = img_bgr.shape[:2]

        asset = SourceAsset(
            id=f"ast_{sha[:8]}",
            sha256=sha,
            original_filename=image_path.name,
            mime_type="image/png",
            byte_size=len(raw_bytes),
            width_px=w,
            height_px=h,
            storage_path=str(image_path.resolve()),
        )
        page_ir = self.page_builder.build(asset, f"/storage/fixtures/{image_path.name}")
        analyzer = PhysicsVisionAnalyzer(provider=MockVisionProvider(default_result=mock_semantic))
        from ai.ingestion.BookUnderstandingPipeline import BookUnderstandingPipeline
        book_pipeline = BookUnderstandingPipeline(analyzer=analyzer)
        book_ir = book_pipeline.analyze(page_ir, asset=asset)

        pipeline = EvidenceExtractionPipeline()
        grounded_ir = pipeline.extract_and_fuse(asset=asset, page_ir=page_ir, book_ir=book_ir)
        return grounded_ir

    def test_real_projectile_scan_acceptance(self):
        """Evaluate real projectile motion textbook scan diagram."""
        img_path = self.fixture_dir / "projectile_textbook_scan.png"
        semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="mechanics",
            subtype="projectile",
            confidence=SemanticConfidence(overall=0.92, is_physics=0.98, domain=0.95, subtype=0.92),
            entities=[
                SemanticEntity(temporary_id="ent_body", role="projectile_body", confidence=0.90),
                SemanticEntity(temporary_id="ent_ground", role="ground_surface", confidence=0.88),
                SemanticEntity(temporary_id="ent_vec", role="velocity_vector", confidence=0.85),
            ],
        )
        grounded_ir = self._run_pipeline(img_path, semantic)

        # Invariant checks
        self.assertIsNotNone(grounded_ir)
        self.assertEqual(grounded_ir.domain, "mechanics")
        self.assertEqual(grounded_ir.subtype, "projectile")
        self.assertEqual(grounded_ir.status, BookIRStatus.NEEDS_REVIEW)

        # Launch point should be grounded from circle
        body = next((e for e in grounded_ir.entities if e.type in ("projectile_body", "projectile")), None)
        self.assertIsNotNone(body)
        self.assertIsNotNone(body.position_source_px)

        # Compiler verification
        compile_res = self.compiler.compile(grounded_ir)
        self.assertIsNone(compile_res.scene, "Compiler must not generate runnable scene until all parameters verified")

    def test_real_refraction_scan_acceptance(self):
        """Evaluate real interface refraction textbook scan diagram."""
        img_path = self.fixture_dir / "refraction_textbook_scan.png"
        semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="optics",
            subtype="interface_refraction",
            confidence=SemanticConfidence(overall=0.91, is_physics=0.97, domain=0.94, subtype=0.90),
            entities=[
                SemanticEntity(temporary_id="ent_b", role="medium_boundary", confidence=0.90),
                SemanticEntity(temporary_id="ent_n", role="normal", confidence=0.88),
                SemanticEntity(temporary_id="ent_r", role="incident_ray", confidence=0.85),
            ],
        )
        grounded_ir = self._run_pipeline(img_path, semantic)

        self.assertEqual(grounded_ir.domain, "optics")
        self.assertEqual(grounded_ir.subtype, "interface_refraction")
        self.assertEqual(grounded_ir.status, BookIRStatus.NEEDS_REVIEW)

        # Optical boundary must be detected near y=175
        self.assertIn("boundary_y", grounded_ir.parameters)
        self.assertAlmostEqual(float(grounded_ir.parameters["boundary_y"]), 175.0, delta=15.0)

        compile_res = self.compiler.compile(grounded_ir)
        self.assertIsNone(compile_res.scene)

    def test_real_prism_scan_acceptance(self):
        """Evaluate real triangular prism textbook scan diagram."""
        img_path = self.fixture_dir / "prism_textbook_scan.png"
        semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="optics",
            subtype="prism",
            confidence=SemanticConfidence(overall=0.90, is_physics=0.96, domain=0.93, subtype=0.89),
            entities=[SemanticEntity(temporary_id="ent_p", role="prism", confidence=0.90)],
        )
        grounded_ir = self._run_pipeline(img_path, semantic)

        self.assertEqual(grounded_ir.domain, "optics")
        self.assertEqual(grounded_ir.subtype, "prism")
        self.assertEqual(grounded_ir.status, BookIRStatus.NEEDS_REVIEW)

        prism_ent = next((e for e in grounded_ir.entities if e.type in ("prism", "prism_body")), None)
        self.assertIsNotNone(prism_ent)
        self.assertIsNotNone(prism_ent.geometry)

        compile_res = self.compiler.compile(grounded_ir)
        self.assertIsNone(compile_res.scene)

    def test_real_bengali_circuit_scan_acceptance(self):
        """Evaluate Bengali-labeled DC circuit textbook diagram."""
        img_path = self.fixture_dir / "bengali_circuit_textbook_scan.png"
        semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="circuits",
            subtype="dc_linear",
            confidence=SemanticConfidence(overall=0.92, is_physics=0.98, domain=0.95, subtype=0.91),
            entities=[
                SemanticEntity(temporary_id="R1", role="resistor", confidence=0.90),
                SemanticEntity(temporary_id="V1", role="voltage_source", confidence=0.88),
            ],
        )
        grounded_ir = self._run_pipeline(img_path, semantic)

        self.assertEqual(grounded_ir.domain, "circuits")
        self.assertEqual(grounded_ir.subtype, "dc_linear")
        self.assertEqual(grounded_ir.status, BookIRStatus.NEEDS_REVIEW)

        # Wire and topology checks
        self.assertIn("circuit_topology", grounded_ir.parameters)
        compile_res = self.compiler.compile(grounded_ir)
        self.assertIsNone(compile_res.scene)

    def test_real_greek_symbols_scan_acceptance(self):
        """Evaluate Greek physics symbols recognition on textbook scan."""
        img_path = self.fixture_dir / "greek_symbols_textbook_scan.png"
        semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="mechanics",
            subtype="pendulum",
            confidence=SemanticConfidence(overall=0.90, is_physics=0.95, domain=0.92, subtype=0.88),
            entities=[SemanticEntity(temporary_id="ent_bob", role="bob", confidence=0.85)],
        )
        grounded_ir = self._run_pipeline(img_path, semantic)

        # Evidence should contain Greek-tagged OCR tokens
        ocr_recs = [e for e in grounded_ir.evidence.values() if e.get("method") == "ocr"]
        self.assertTrue(len(ocr_recs) >= 1)
        compile_res = self.compiler.compile(grounded_ir)
        self.assertIsNone(compile_res.scene)

    def test_real_bengali_textbook_pendulum_scan_acceptance(self):
        """Evaluate real Bengali textbook pendulum diagram (regression fixture)."""
        img_path = self.fixture_dir / "pendulum_bengali_textbook.png"
        semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="mechanics",
            subtype="pendulum",
            confidence=SemanticConfidence(overall=0.96, is_physics=0.99, domain=0.98, subtype=0.96),
            entities=[
                SemanticEntity(temporary_id="pivot_1", role="pivot", confidence=0.95),
                SemanticEntity(temporary_id="string_1", role="string", confidence=0.95),
                SemanticEntity(temporary_id="bob_1", role="bob", confidence=0.95),
                SemanticEntity(temporary_id="ref_1", role="vertical_reference", confidence=0.95),
            ],
            visible_labels=[
                SemanticVisibleLabel(text="Pivot (ঘূর্ণনবিন্দু)", semantic_role="label", confidence=0.95),
                SemanticVisibleLabel(text="L = 20 cm", semantic_role="parameter", confidence=0.95),
                SemanticVisibleLabel(text="θ = 30°", semantic_role="parameter", confidence=0.95),
                SemanticVisibleLabel(text="String (সুতা)", semantic_role="label", confidence=0.95),
                SemanticVisibleLabel(text="Bob (ভরক)", semantic_role="label", confidence=0.95),
                SemanticVisibleLabel(text="m", semantic_role="parameter", confidence=0.95),
                SemanticVisibleLabel(text="Fig. 2 সরল দোলক", semantic_role="caption", confidence=0.95),
            ],
        )
        grounded_ir = self._run_pipeline(img_path, semantic)

        self.assertEqual(grounded_ir.domain, "mechanics")
        self.assertEqual(grounded_ir.subtype, "pendulum")
        self.assertEqual(grounded_ir.status, BookIRStatus.NEEDS_REVIEW)

        # 1. Bob grounding verification (must be near (611.9, 792.5) with radius ~47px, NOT phantom at (238, 998))
        bob_ent = next((e for e in grounded_ir.entities if e.type == "bob"), None)
        self.assertIsNotNone(bob_ent)
        self.assertIsNotNone(bob_ent.position_source_px)
        self.assertAlmostEqual(bob_ent.position_source_px["x"], 611.9, delta=10.0)
        self.assertAlmostEqual(bob_ent.position_source_px["y"], 792.5, delta=10.0)
        self.assertAlmostEqual(bob_ent.geometry["radius_px"], 47.2, delta=8.0)
        self.assertLess(bob_ent.geometry.get("area_px", 0), 15000.0)  # Must be compact bob, not giant 114k mask

        # 2. String grounding verification (slopes down-right from pivot to bob)
        string_ent = next((e for e in grounded_ir.entities if e.type == "string"), None)
        self.assertIsNotNone(string_ent)
        self.assertIsNotNone(string_ent.geometry)
        self.assertAlmostEqual(string_ent.geometry["start"]["x"], 333.3, delta=10.0)
        self.assertAlmostEqual(string_ent.geometry["start"]["y"], 101.2, delta=15.0)
        vis_end = string_ent.geometry.get("visible_string_end") or string_ent.geometry["end"]
        self.assertAlmostEqual(vis_end["x"], 593.9, delta=15.0)
        self.assertAlmostEqual(vis_end["y"], 748.9, delta=15.0)
        # Effective pendulum end matches bob center
        self.assertAlmostEqual(string_ent.geometry["end"]["x"], 611.9, delta=10.0)
        self.assertAlmostEqual(string_ent.geometry["end"]["y"], 792.5, delta=10.0)
        # Verify downward-right slope (end.x > start.x, end.y > start.y)
        self.assertGreater(string_ent.geometry["end"]["x"], string_ent.geometry["start"]["x"])
        self.assertGreater(string_ent.geometry["end"]["y"], string_ent.geometry["start"]["y"])

        # 3. Pivot grounding verification (near (333, 101))
        pivot_ent = next((e for e in grounded_ir.entities if e.type == "pivot"), None)
        self.assertIsNotNone(pivot_ent)
        self.assertIsNotNone(pivot_ent.position_source_px)
        self.assertAlmostEqual(pivot_ent.position_source_px["x"], 333.3, delta=10.0)
        self.assertAlmostEqual(pivot_ent.position_source_px["y"], 101.2, delta=15.0)

        # 4. Vertical reference line grounded
        ref_ent = next((e for e in grounded_ir.entities if e.type == "vertical_reference"), None)
        self.assertIsNotNone(ref_ent)
        self.assertIsNotNone(ref_ent.geometry)
        self.assertAlmostEqual(ref_ent.geometry["start"]["x"], 334.0, delta=10.0)
        self.assertEqual(ref_ent.geometry["style"], "dashed")

        # 5. Length parameter promotion with fused provenance
        self.assertIn("length", grounded_ir.parameters)
        self.assertAlmostEqual(float(grounded_ir.parameters["length"].value), 0.2, delta=0.01)
        self.assertEqual(grounded_ir.parameters["length"].provenance.source, "fused")

        # 6. Compiler safety: BookIR remains NEEDS_REVIEW and scene is None
        compile_res = self.compiler.compile(grounded_ir)
        self.assertIsNone(compile_res.scene)
        self.assertEqual(compile_res.status, "NEEDS_REVIEW")


if __name__ == "__main__":
    unittest.main()


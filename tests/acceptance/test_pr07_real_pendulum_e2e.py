"""PR-07 Real Pendulum Acceptance Test Suite.

Demonstrates the complete end-to-end PR-06 -> PR-07 -> PhysicsCompiler pipeline
on the real unseen textbook pendulum sketch (pendulum_sketch_raw.png).

VERIFIES:
  1. PR-06 Grounding: Produces honest grounded BookIR in NEEDS_REVIEW with verified source_px coordinates.
  2. Strict Compiler Gate: PhysicsCompiler refuses to compile (status: NEEDS_REVIEW, scene: None).
  3. PR-07 Resolution Analysis: Deterministically detects missing physical parameters (length, gravity, mass, damping).
  4. Non-fabrication & Geometry preservation: Grounded pivot and bob_center coordinates remain 100% untouched.
  5. User Resolution: User provides physical length (0.8 m); spatial calibration is derived without modifying source_px.
  6. Explicit Policies: Applies named policies (policy_earth_gravity, policy_standard_mass, policy_zero_damping).
  7. Compilation Readiness: Invariant satisfies READY_TO_COMPILE with complete parameter provenance.
  8. Canonical Scene Compilation: PhysicsCompiler produces runnable Canonical PhysicsScene (status: READY).
  9. Deterministic Reversibility: Removing a resolution returns status to NEEDS_REVIEW and blocks compilation.
"""
from __future__ import annotations

from pathlib import Path
import pytest

from shared.schemas.ingestion import (
    SourceAsset,
    BookIR,
    BookEntity,
    BookIRStatus,
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
from ai.ingestion.BookUnderstandingPipeline import BookUnderstandingPipeline
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.mock_provider import MockVisionProvider
from ai.evidence.pipeline import EvidenceExtractionPipeline

from ai.resolution import (
    ResolutionAnalyzer,
    ResolutionEngine,
    ReadinessEvaluator,
    PolicyRegistry,
)

_ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_PATH = _ROOT / "tests" / "fixtures" / "unseen" / "mechanics" / "pendulum_sketch_raw.png"


class TestPR07RealPendulumE2E:
    """Full PR-06 -> PR-07 -> PhysicsCompiler end-to-end acceptance test."""

    @pytest.fixture
    def grounded_pendulum(self) -> BookIR:
        """Run real PR-06 perception pipeline on pendulum_sketch_raw.png."""
        assert _FIXTURE_PATH.exists(), f"Missing fixture: {_FIXTURE_PATH}"

        raw_bytes = _FIXTURE_PATH.read_bytes()
        sha = compute_sha256(raw_bytes)
        import cv2
        img = cv2.imread(str(_FIXTURE_PATH))
        assert img is not None, "Failed to decode image"
        h, w = img.shape[:2]

        asset = SourceAsset(
            id=f"real_asset_{sha[:8]}",
            sha256=sha,
            original_filename=_FIXTURE_PATH.name,
            mime_type="image/png",
            byte_size=len(raw_bytes),
            width_px=w,
            height_px=h,
            storage_path=str(_FIXTURE_PATH.resolve()),
        )
        page_ir = PageIRBuilder().build(asset, f"/storage/fixtures/{_FIXTURE_PATH.name}")

        mock_semantic = SemanticAnalysisResult(
            classification="supported",
            is_physics=True,
            domain="mechanics",
            subtype="pendulum",
            confidence=SemanticConfidence(overall=0.94, is_physics=0.98, domain=0.95, subtype=0.92),
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
                SemanticVisibleLabel(text="Pivot", confidence=0.85, verified=False),
            ],
        )

        vision_analyzer = PhysicsVisionAnalyzer(provider=MockVisionProvider(default_result=mock_semantic))
        book_pipeline = BookUnderstandingPipeline(analyzer=vision_analyzer)
        book_ir = book_pipeline.analyze(page_ir, asset=asset)

        evidence_pipeline = EvidenceExtractionPipeline()
        grounded_book_ir = evidence_pipeline.extract_and_fuse(
            asset=asset,
            page_ir=page_ir,
            book_ir=book_ir,
        )
        return grounded_book_ir

    def test_real_pendulum_end_to_end(self, grounded_pendulum: BookIR):
        book_ir = grounded_pendulum

        # -------------------------------------------------------------------
        # Step 1: Verify PR-06 honestly grounded state
        # -------------------------------------------------------------------
        assert book_ir.domain == "mechanics"
        assert book_ir.subtype == "pendulum"
        assert book_ir.status == BookIRStatus.NEEDS_REVIEW

        entities = {e.type: e for e in book_ir.entities}
        assert "pivot" in entities
        assert "bob" in entities
        pivot_ent = entities["pivot"]
        bob_ent = entities["bob"]

        assert pivot_ent.position_source_px is not None
        assert bob_ent.position_source_px is not None

        orig_pivot_x = pivot_ent.position_source_px["x"]
        orig_pivot_y = pivot_ent.position_source_px["y"]
        orig_bob_x = bob_ent.position_source_px["x"]
        orig_bob_y = bob_ent.position_source_px["y"]

        # -------------------------------------------------------------------
        # Step 2: Strict compiler gate rejects incomplete BookIR
        # -------------------------------------------------------------------
        compiler = PhysicsCompiler()
        pre_compile = compiler.compile(book_ir)
        assert pre_compile.status == "NEEDS_REVIEW"
        assert pre_compile.scene is None
        assert pre_compile.issues[0]["code"] == "BOOK_IR_NOT_READY"

        # -------------------------------------------------------------------
        # Step 3: PR-07 Deterministic Resolution Analysis
        # -------------------------------------------------------------------
        review_state = ResolutionAnalyzer.analyze(book_ir)
        assert review_state.ready_to_compile is False
        assert review_state.blockers_count > 0

        # Verify missing physical compile requirements detected
        missing = set(review_state.missing_requirements)
        assert "length" in missing or "pixels_per_meter" in missing
        assert "gravity" in missing
        assert "mass" in missing
        assert "damping" in missing

        # -------------------------------------------------------------------
        # Step 4: Apply PR-07 User Resolutions & Explicit Policies
        # -------------------------------------------------------------------
        # User supplies physical length: 0.8 m
        res_len = ResolutionEngine.apply_resolution(book_ir, {
            "parameterName": "length",
            "resolvedValue": 0.8,
            "canonicalUnit": "m",
            "resolutionSource": "user_supplied",
            "notes": "Length supplied by user via review modal",
        })
        assert res_len.success is True

        # Apply standard Earth gravity policy (9.80665 m/s²)
        res_grav = ResolutionEngine.apply_policy(book_ir, "policy_earth_gravity")
        assert res_grav.success is True

        # Apply standard unit mass policy (1.0 kg)
        res_mass = ResolutionEngine.apply_policy(book_ir, "policy_standard_mass")
        assert res_mass.success is True

        # Apply ideal undamped oscillation policy (0.0 1/s)
        res_damp = ResolutionEngine.apply_policy(book_ir, "policy_zero_damping")
        assert res_damp.success is True

        # -------------------------------------------------------------------
        # Step 5: Verify Geometry Remains 100% Untouched
        # -------------------------------------------------------------------
        assert pivot_ent.position_source_px["x"] == orig_pivot_x
        assert pivot_ent.position_source_px["y"] == orig_pivot_y
        assert bob_ent.position_source_px["x"] == orig_bob_x
        assert bob_ent.position_source_px["y"] == orig_bob_y

        # Verify spatial calibration was derived without changing source_px
        assert book_ir.calibration is not None
        assert book_ir.calibration.pixels_per_meter > 0
        assert book_ir.calibration.reference_physical_m == 0.8
        assert book_ir.calibration.reference_parameter == "length"

        # -------------------------------------------------------------------
        # Step 6: Compilation Readiness Invariant
        # -------------------------------------------------------------------
        readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
        assert readiness.ready is True
        assert book_ir.status == BookIRStatus.READY_TO_COMPILE
        assert len(readiness.blockers) == 0

        # Check parameter provenance integrity
        assert "length" in book_ir.parameter_provenance
        assert "gravity" in book_ir.parameter_provenance
        assert "mass" in book_ir.parameter_provenance
        assert "damping" in book_ir.parameter_provenance

        assert book_ir.parameter_provenance["length"].source == "user_supplied"
        assert book_ir.parameter_provenance["gravity"].source == "policy_default"
        assert book_ir.parameter_provenance["gravity"].policy_id == "policy_earth_gravity"
        assert book_ir.parameter_provenance["mass"].policy_id == "policy_standard_mass"
        assert book_ir.parameter_provenance["damping"].policy_id == "policy_zero_damping"

        # -------------------------------------------------------------------
        # Step 7: PhysicsCompiler produces runnable Canonical PhysicsScene
        # -------------------------------------------------------------------
        compile_result = compiler.compile(book_ir)
        assert compile_result.status == "READY"
        scene = compile_result.scene
        assert scene is not None
        assert scene["domain"] == "mechanics"
        assert scene["subtype"] == "pendulum"

        # Validate scene parameters match resolved values
        params = scene["parameters"]
        assert params["length"]["value"] == 0.8
        assert params["gravity"]["value"] == 9.80665
        assert params["mass"]["value"] == 1.0
        assert params["damping"]["value"] == 0.0

        # Validate native source_px visual alignment
        geom = scene["geometry"]
        assert geom["pivot"]["x"] == orig_pivot_x
        assert geom["pivot"]["y"] == orig_pivot_y
        assert geom["bob_center"]["x"] == orig_bob_x
        assert geom["bob_center"]["y"] == orig_bob_y

        # -------------------------------------------------------------------
        # Step 8: Deterministic Reversibility / Invalidation
        # -------------------------------------------------------------------
        rev_res = ResolutionEngine.remove_resolution(book_ir, "gravity")
        assert rev_res.ready is False
        assert "gravity" not in book_ir.parameters

        # Status immediately reverts to NEEDS_REVIEW
        re_eval = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
        assert re_eval.ready is False
        assert book_ir.status == BookIRStatus.NEEDS_REVIEW
        assert any("gravity" in b for b in re_eval.blockers)

        # PhysicsCompiler immediately refuses to compile
        refuse_result = compiler.compile(book_ir)
        assert refuse_result.status == "NEEDS_REVIEW"
        assert refuse_result.scene is None

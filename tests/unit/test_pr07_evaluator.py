"""PR-07 Unit Tests: Compilation Readiness Evaluator & Serialization Roundtrip.

Verifies:
  - Deterministic enforcement of the canonical READY_TO_COMPILE invariant.
  - Partial resolution stays NEEDS_REVIEW.
  - Non-finite or negative values are rejected as blockers.
  - Missing provenance for any required parameter is rejected.
  - Ambiguous geometry rejects compilation.
  - Reversibility: removing a resolution immediately invalidates readiness.
  - Serialization roundtrip: to_dict / from_dict preserves resolutions, provenance, calibration.
"""
import json
import pytest
from ai.resolution.evaluator import ReadinessEvaluator
from ai.resolution.engine import ResolutionEngine
from shared.schemas.ingestion import BookIR, BookEntity, BookIRStatus


def _create_ready_pendulum() -> BookIR:
    b = BookIR(
        source_asset_id="asset_ready",
        figure_id="fig_ready",
        domain="mechanics",
        subtype="pendulum",
        status="NEEDS_REVIEW",
        entities=[
            BookEntity(id="e_pivot", type="pivot", position_source_px={"x": 200, "y": 100}),
            BookEntity(id="e_bob", type="bob", position_source_px={"x": 200, "y": 500}),
            BookEntity(id="e_string", type="string", position_source_px={"x": 200, "y": 100}, geometry={"effective_length_px": 400}),
        ],
        geometry={
            "pivot": {"x": 200, "y": 100},
            "bob_center": {"x": 200, "y": 500},
            "string_length_px": 400.0,
            "bob_radius_px": 20.0,
            "width": 800.0,
            "height": 600.0,
        },
        parameters={},
    )
    ResolutionEngine.apply_resolution(b, {
        "parameterName": "length",
        "resolvedValue": 0.8,
        "canonicalUnit": "m",
        "resolutionSource": "user_supplied",
    })
    ResolutionEngine.apply_policy(b, "policy_earth_gravity")
    ResolutionEngine.apply_policy(b, "policy_standard_mass")
    ResolutionEngine.apply_policy(b, "policy_zero_damping")
    return b


class TestReadinessEvaluator:
    """Verify deterministic readiness evaluation."""

    def test_complete_resolution_reaches_ready(self):
        b = _create_ready_pendulum()
        report = ReadinessEvaluator.evaluate(b, mutate_status=True)
        assert report.ready is True
        assert b.status == BookIRStatus.READY_TO_COMPILE
        assert len(report.blockers) == 0

    def test_partial_resolution_stays_needs_review(self):
        b = _create_ready_pendulum()
        # Remove damping
        ResolutionEngine.remove_resolution(b, "damping")

        report = ReadinessEvaluator.evaluate(b, mutate_status=True)
        assert report.ready is False
        assert b.status == BookIRStatus.NEEDS_REVIEW
        assert any("damping" in blk.lower() for blk in report.blockers)

    def test_negative_length_rejected(self):
        b = _create_ready_pendulum()
        b.parameters["length"] = -0.5

        report = ReadinessEvaluator.evaluate(b, mutate_status=True)
        assert report.ready is False
        assert b.status == BookIRStatus.NEEDS_REVIEW
        assert any("strictly positive" in blk.lower() for blk in report.blockers)

    def test_missing_provenance_rejected(self):
        b = _create_ready_pendulum()
        # Delete provenance record for gravity
        del b.parameter_provenance["gravity"]
        del b.resolutions["gravity"]

        report = ReadinessEvaluator.evaluate(b, mutate_status=True)
        assert report.ready is False
        assert any("lacks explicit provenance" in blk.lower() for blk in report.blockers)

    def test_unrelated_entity_evidence_does_not_satisfy_physical_parameter_provenance(self):
        """Negative test: an unrelated entity evidence ref must NEVER satisfy provenance for a physical parameter."""
        b = _create_ready_pendulum()
        # Add entity evidence ref to bob
        b.entities[1].evidence_refs = ["ev_visual_bob_sketch_123"]
        # Delete provenance and resolution for gravity
        del b.parameter_provenance["gravity"]
        del b.resolutions["gravity"]

        report = ReadinessEvaluator.evaluate(b, mutate_status=True)
        assert report.ready is False
        assert b.status == BookIRStatus.NEEDS_REVIEW
        assert any("gravity' lacks explicit provenance" in blk for blk in report.blockers)

    def test_ambiguous_geometry_rejected(self):
        b = _create_ready_pendulum()
        b.entities[0].attributes["is_ambiguous"] = True

        report = ReadinessEvaluator.evaluate(b, mutate_status=True)
        assert report.ready is False
        assert len(report.unresolved_ambiguities) > 0


class TestSerializationRoundtrip:
    """Verify serialization to JSON dict and reconstruction preserves all PR-07 state."""

    def test_roundtrip_preserves_resolutions_and_calibration(self):
        b = _create_ready_pendulum()
        report_before = ReadinessEvaluator.evaluate(b)
        assert report_before.ready is True

        # Serialize to dict and JSON string
        b_dict = b.to_dict()
        json_str = json.dumps(b_dict)
        reloaded_dict = json.loads(json_str)

        # Deserialize back to BookIR
        b_reloaded = BookIR.from_dict(reloaded_dict)

        # Verify all fields survived
        assert b_reloaded.status == b.status
        assert b_reloaded.parameters["length"] == b.parameters["length"]
        assert b_reloaded.parameters["gravity"] == b.parameters["gravity"]
        assert len(b_reloaded.resolutions) == len(b.resolutions)
        assert len(b_reloaded.parameter_provenance) == len(b.parameter_provenance)

        # Verify calibration survived
        assert b_reloaded.calibration is not None
        calib = b_reloaded.calibration
        ppm = calib.get("pixels_per_meter") if isinstance(calib, dict) else calib.pixels_per_meter
        assert ppm == pytest.approx(500.0)

        # Verify readiness evaluation on reloaded BookIR is IDENTICAL
        report_after = ReadinessEvaluator.evaluate(b_reloaded)
        assert report_after.ready is True
        assert report_after.status == BookIRStatus.READY_TO_COMPILE

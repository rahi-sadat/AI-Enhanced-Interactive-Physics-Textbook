"""PR-07 Unit Tests: Resolution Engine, Evidence Preservation & Auditability.

Verifies:
  - Analysis is deterministic and pure (does not mutate BookIR).
  - OCR candidates can be confirmed or corrected.
  - User correction records superseded value without mutating BookIR.evidence.
  - Spatial calibration is derived without altering native source_px geometry.
  - Idempotence: re-applying a resolution does not corrupt state.
  - Dependency invalidation: modifying a reference parameter updates derived calibration.
"""
import pytest
from ai.resolution.analyzer import ResolutionAnalyzer
from ai.resolution.engine import ResolutionEngine
from ai.resolution.calibration import CalibrationEngine
from ai.resolution.evaluator import ReadinessEvaluator
from shared.schemas.ingestion import BookIR, BookEntity
from shared.schemas.evidence import OCRToken, OCRExtractionResult, EvidenceRecord, EvidenceMethod
from shared.schemas.resolution import ResolutionSource, ReviewIssueType


def _make_grounded_pendulum_ir() -> BookIR:
    """Helper creating a grounded pendulum BookIR from PR-06 with unverified OCR token."""
    return BookIR(
        source_asset_id="asset_pendulum",
        figure_id="fig_1",
        domain="mechanics",
        subtype="pendulum",
        status="NEEDS_REVIEW",
        entities=[
            BookEntity(id="e_pivot", type="pivot", position_source_px={"x": 392.1, "y": 86.2}),
            BookEntity(id="e_bob", type="bob", position_source_px={"x": 549.7, "y": 399.4}),
            BookEntity(
                id="e_string",
                type="string",
                position_source_px={"x": 392.1, "y": 86.2},
                geometry={"effective_length_px": 350.5},
            ),
        ],
        geometry={
            "pivot": {"x": 392.1, "y": 86.2},
            "bob_center": {"x": 549.7, "y": 399.4},
            "string_length_px": 350.5,
            "bob_radius_px": 25.0,
            "width": 800.0,
            "height": 600.0,
        },
        parameters={},
        evidence={
            "ev_ocr_1": {
                "id": "ev_ocr_1",
                "method": "ocr",
                "tokens": [
                    {
                        "id": "tok_l",
                        "rawText": "L = 80 cm",
                        "candidates": [
                            {
                                "quantityCandidate": "length",
                                "numericValue": 80.0,
                                "rawUnit": "cm",
                                "confidence": 0.75,
                            }
                        ],
                    }
                ],
            }
        },
    )


class TestResolutionAnalyzer:
    """Verify ResolutionAnalyzer analysis pass."""

    def test_analyzer_is_pure(self):
        b = _make_grounded_pendulum_ir()
        initial_status = b.status
        initial_params = dict(b.parameters)

        state = ResolutionAnalyzer.analyze(b)
        assert state.ready_to_compile is False
        assert b.status == initial_status
        assert b.parameters == initial_params

    def test_detects_candidate_confirmation(self):
        b = _make_grounded_pendulum_ir()
        state = ResolutionAnalyzer.analyze(b)

        # Should find candidate confirmation for length
        confirm_issue = next((iss for iss in state.issues if iss.parameter_name == "length"), None)
        assert confirm_issue is not None
        assert confirm_issue.issue_type == ReviewIssueType.UNVERIFIED_OCR_CANDIDATE.value
        assert len(confirm_issue.candidates) == 1
        assert confirm_issue.candidates[0]["value"] == 80.0

    def test_detects_ambiguous_geometry_blocker(self):
        b = _make_grounded_pendulum_ir()
        # Mark bob as ambiguous
        b.entities[1].attributes["is_ambiguous"] = True

        state = ResolutionAnalyzer.analyze(b)
        assert state.ready_to_compile is False
        ambig_issue = next((iss for iss in state.issues if iss.entity_id == "e_bob"), None)
        assert ambig_issue is not None
        assert ambig_issue.issue_type == ReviewIssueType.AMBIGUOUS_GEOMETRY.value
        assert ambig_issue.is_blocker is True


class TestEvidencePreservationAndCorrection:
    """Verify user confirmation and correction preserve evidence."""

    def test_confirm_candidate_preserves_ocr(self):
        b = _make_grounded_pendulum_ir()
        state = ResolutionAnalyzer.analyze(b)
        length_issue = next(iss for iss in state.issues if iss.parameter_name == "length")

        candidate = length_issue.candidates[0]
        res = ResolutionEngine.confirm_candidate(b, "length", candidate)
        assert res.success is True
        assert b.parameters["length"] == pytest.approx(0.8)

        # Check provenance
        prov = b.parameter_provenance["length"]
        assert prov.source == ResolutionSource.USER_CONFIRMED.value
        assert "tok_l" in prov.evidence_refs

        # Check original OCR evidence was NOT mutated or destroyed
        raw_token = b.evidence["ev_ocr_1"]["tokens"][0]
        assert raw_token["rawText"] == "L = 80 cm"
        assert raw_token["candidates"][0]["confidence"] == 0.75  # Not magically 1.0!

    def test_correct_candidate_preserves_superseded_value(self):
        b = _make_grounded_pendulum_ir()
        # First confirm 0.8 m
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 0.8,
            "canonicalUnit": "m",
            "resolutionSource": "user_confirmed",
        })
        assert b.parameters["length"] == 0.8

        # User now corrects to 0.75 m
        res_corr = ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 0.75,
            "canonicalUnit": "m",
            "resolutionSource": "user_corrected",
        })
        assert res_corr.success is True
        assert b.parameters["length"] == 0.75

        # Check superseded value recorded
        dec = b.resolutions["length"]
        assert dec["supersededValue"] == 0.8
        assert dec["resolutionSource"] == ResolutionSource.USER_CORRECTED.value

        # Check original OCR token in evidence is still completely intact
        raw_token = b.evidence["ev_ocr_1"]["tokens"][0]
        assert raw_token["rawText"] == "L = 80 cm"


class TestCalibrationDerivation:
    """Verify pixel-to-physical calibration without mutating native source_px."""

    def test_calibration_preserves_source_px(self):
        b = _make_grounded_pendulum_ir()
        orig_pivot_x = b.geometry["pivot"]["x"]
        orig_bob_y = b.geometry["bob_center"]["y"]

        ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 0.701,  # 350.5 px / 0.701 m = 500 px/m
            "canonicalUnit": "m",
            "resolutionSource": "user_supplied",
        })

        assert b.calibration is not None
        assert b.calibration.pixels_per_meter == pytest.approx(500.0, rel=1e-2)
        assert b.calibration.reference_parameter == "length"

        # Verify native source_px coordinates are UNCHANGED
        assert b.geometry["pivot"]["x"] == orig_pivot_x
        assert b.geometry["bob_center"]["y"] == orig_bob_y
        assert b.entities[0].position_source_px["x"] == 392.1

    def test_calibration_updates_when_length_changes(self):
        b = _make_grounded_pendulum_ir()
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 0.701,
            "canonicalUnit": "m",
            "resolutionSource": "user_supplied",
        })
        ppm_first = b.calibration.pixels_per_meter

        # Change length to 1.402 m (double length -> half ppm)
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 1.402,
            "canonicalUnit": "m",
            "resolutionSource": "user_supplied",
        })
        ppm_second = b.calibration.pixels_per_meter

        assert ppm_second == pytest.approx(ppm_first / 2.0, rel=1e-2)


class TestIdempotence:
    """Verify repeated resolution application produces deterministic, uncorrupted state."""

    def test_idempotent_application(self):
        b = _make_grounded_pendulum_ir()
        res1 = ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 0.8,
            "canonicalUnit": "m",
            "resolutionSource": "user_supplied",
        })
        state1 = b.to_dict()

        res2 = ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 0.8,
            "canonicalUnit": "m",
            "resolutionSource": "user_supplied",
        })
        state2 = b.to_dict()

        assert res1.success is True
        assert res2.success is True
        assert state1["parameters"] == state2["parameters"]
        assert state1["resolutions"] == state2["resolutions"]


class TestResolutionValidationAndNegativeScenarios:
    """Verify strict validation and rejection of invalid parameter names, ranges, and categories."""

    def test_unknown_parameter_name_rejected(self):
        b = _make_grounded_pendulum_ir()
        res = ResolutionEngine.apply_resolution(b, {
            "parameterName": "made_up_parameter",
            "resolvedValue": 5.0,
            "canonicalUnit": "kg",
            "resolutionSource": "user_supplied",
        })
        assert res.success is False
        assert "UNKNOWN_PARAMETER_FOR_SUBTYPE" in res.error
        assert "made_up_parameter" not in b.parameters
        assert "made_up_parameter" not in (b.resolutions or {})

    def test_projectile_launch_angle_180_degrees_rejected(self):
        b = BookIR(
            source_asset_id="asset_proj_neg",
            figure_id="fig_proj_neg",
            domain="mechanics",
            subtype="projectile",
            status="NEEDS_REVIEW",
            parameters={},
        )
        res = ResolutionEngine.apply_resolution(b, {
            "parameterName": "launch_angle_deg",
            "resolvedValue": 180.0,
            "canonicalUnit": "deg",
            "resolutionSource": "user_supplied",
        })
        assert res.success is False
        assert "launch_angle_deg" not in b.parameters

    def test_mirror_concavity_banana_rejected(self):
        b = BookIR(
            source_asset_id="asset_mirror_neg",
            figure_id="fig_mirror_neg",
            domain="optics",
            subtype="spherical_mirror",
            status="NEEDS_REVIEW",
            parameters={},
        )
        res = ResolutionEngine.apply_resolution(b, {
            "parameterName": "concavity",
            "resolvedValue": "banana",
            "resolutionSource": "user_supplied",
        })
        assert res.success is False
        assert "INVALID_CATEGORICAL_VALUE" in res.error
        assert "concavity" not in b.parameters

    def test_prism_apex_angle_outside_range_rejected(self):
        b = BookIR(
            source_asset_id="asset_prism_neg",
            figure_id="fig_prism_neg",
            domain="optics",
            subtype="prism",
            status="NEEDS_REVIEW",
            parameters={},
        )
        res = ResolutionEngine.apply_resolution(b, {
            "parameterName": "apex_angle_deg",
            "resolvedValue": 250.0,
            "canonicalUnit": "deg",
            "resolutionSource": "user_supplied",
        })
        assert res.success is False
        assert "apex_angle_deg" not in b.parameters

    def test_parameter_alias_canonicalization_stores_canonical_keys(self):
        # 1. Projectile: launch_angle -> launch_angle_deg, speed -> launch_speed
        b_proj = BookIR(
            source_asset_id="asset_proj_alias",
            figure_id="fig_proj_alias",
            domain="mechanics",
            subtype="projectile",
            status="NEEDS_REVIEW",
            parameters={},
        )
        res1 = ResolutionEngine.apply_resolution(b_proj, {
            "parameterName": "launch_angle",
            "resolvedValue": 30.0,
            "canonicalUnit": "deg",
            "resolutionSource": "user_supplied",
        })
        assert res1.success is True
        assert "launch_angle_deg" in b_proj.parameters
        assert b_proj.parameters["launch_angle_deg"] == 30.0
        assert "launch_angle" not in b_proj.parameters
        assert "launch_angle_deg" in b_proj.resolutions
        assert "launch_angle_deg" in b_proj.parameter_provenance

        res2 = ResolutionEngine.apply_resolution(b_proj, {
            "parameterName": "speed",
            "resolvedValue": 15.0,
            "canonicalUnit": "m/s",
            "resolutionSource": "user_supplied",
        })
        assert res2.success is True
        assert "launch_speed" in b_proj.parameters
        assert b_proj.parameters["launch_speed"] == 15.0
        assert "speed" not in b_proj.parameters

        # 2. Thin lens: focalLength -> focal_length_px
        b_lens = BookIR(
            source_asset_id="asset_lens_alias",
            figure_id="fig_lens_alias",
            domain="optics",
            subtype="thin_lens",
            status="NEEDS_REVIEW",
            parameters={},
        )
        res3 = ResolutionEngine.apply_resolution(b_lens, {
            "parameterName": "focalLength",
            "resolvedValue": 120.0,
            "canonicalUnit": "px",
            "resolutionSource": "user_supplied",
        })
        assert res3.success is True
        assert "focal_length_px" in b_lens.parameters
        assert b_lens.parameters["focal_length_px"] == 120.0
        assert "focalLength" not in b_lens.parameters

    def test_lens_mirror_does_not_derive_calibration_from_focal_length_px(self):
        """Physical calibration requires one pixel measurement and one independently grounded physical-length measurement.
        Optical focal_length_px must NEVER fabricate pixels_per_meter."""
        # 1. CalibrationEngine.derive_for_subtype returns None for thin_lens and spherical_mirror
        derived_lens = CalibrationEngine.derive_for_subtype(
            subtype="thin_lens",
            entities=[],
            parameters={"focal_length_px": 150.0},
            resolutions={},
        )
        assert derived_lens is None

        derived_mirror = CalibrationEngine.derive_for_subtype(
            subtype="spherical_mirror",
            entities=[],
            parameters={"focal_length_px": 100.0},
            resolutions={},
        )
        assert derived_mirror is None

        # 2. Applying focal_length_px via ResolutionEngine does not populate book_ir.calibration
        b_lens = BookIR(
            source_asset_id="asset_lens_calib",
            figure_id="fig_lens_calib",
            domain="optics",
            subtype="thin_lens",
            status="NEEDS_REVIEW",
            parameters={},
        )
        res = ResolutionEngine.apply_resolution(b_lens, {
            "parameterName": "focal_length_px",
            "resolvedValue": 150.0,
            "canonicalUnit": "px",
            "resolutionSource": "user_supplied",
        })
        assert res.success is True
        assert b_lens.calibration is None


"""Unit tests for ModelCandidate fitting, ranking, and geometry predictors (Phase 5)."""
import pytest
from shared.schemas.evidence import SourcePoint, SourceLine
from ai.registration.base import PredictedGeometry
from ai.registration.candidate import (
    CandidateRegistration,
    CandidateStatus,
    ModelCandidate,
    rank_candidates,
    select_best_candidate,
)
from ai.registration.predictors import (
    CircuitGeometryPredictor,
    PendulumGeometryPredictor,
    ProjectileGeometryPredictor,
    ThinLensGeometryPredictor,
)


def test_pendulum_geometry_predictor():
    """Verify PendulumGeometryPredictor generates expected landmarks and string line."""
    pred = PendulumGeometryPredictor.predict(
        source_asset_id="asset_1",
        figure_id="fig_1",
        source_width=400,
        source_height=500,
        pivot={"x": 200, "y": 50},
        bob_center={"x": 250, "y": 300},
        string_length_px=254.95,
        bob_radius_px=20.0,
    )
    assert isinstance(pred, PredictedGeometry)
    assert pred.domain == "mechanics"
    assert pred.subtype == "pendulum"
    assert "pivot" in pred.landmarks
    assert "bob_center" in pred.landmarks
    assert "string" in pred.lines
    assert pred.landmarks["pivot"].x == 200
    assert pred.landmarks["bob_center"].x == 250


def test_thin_lens_geometry_predictor():
    """Verify ThinLensGeometryPredictor generates focal points, object/image and rays."""
    pred = ThinLensGeometryPredictor.predict(
        source_asset_id="asset_lens",
        figure_id="fig_lens",
        source_width=600,
        source_height=400,
        lens_center={"x": 300, "y": 200},
        focal_length_px=80.0,
        object_x=140.0,
        object_height_px=50.0,
        axis_y=200.0,
    )
    assert pred.domain == "optics"
    assert pred.subtype == "thin_lens"
    assert "lens_center" in pred.landmarks
    assert "focal_F1" in pred.landmarks
    assert "focal_F2" in pred.landmarks
    assert "object_base" in pred.landmarks
    assert "image_base" in pred.landmarks
    assert "ray_parallel" in pred.lines


def test_projectile_geometry_predictor():
    """Verify ProjectileGeometryPredictor generates trajectory curve."""
    pred = ProjectileGeometryPredictor.predict(
        source_asset_id="asset_proj",
        figure_id="fig_proj",
        source_width=800,
        source_height=600,
        launch_position={"x": 50, "y": 500},
        launch_angle_deg=45.0,
        launch_speed=20.0,
    )
    assert pred.domain == "mechanics"
    assert pred.subtype == "projectile"
    assert "launch_position" in pred.landmarks
    assert "trajectory" in pred.curves
    assert len(pred.curves["trajectory"]) > 1


def test_circuit_geometry_predictor():
    """Verify CircuitGeometryPredictor generates topology."""
    pred = CircuitGeometryPredictor.predict(
        source_asset_id="asset_circ",
        figure_id="fig_circ",
        source_width=500,
        source_height=400,
        topology={"V1": ["N1", "N2"], "R1": ["N2", "N1"]},
    )
    assert pred.domain == "circuits"
    assert pred.subtype == "dc_linear"
    assert pred.topology["V1"] == ["N1", "N2"]


def test_candidate_ranking_physics_validity_first():
    """Candidates with invalid physics must always rank behind valid physics candidates."""
    cand_invalid_physics = ModelCandidate(
        id="cand_invalid",
        domain="optics",
        subtype="thin_lens",
        physics_valid=False,
        registration=CandidateRegistration(mean_error_px=1.0),
    )
    cand_valid = ModelCandidate(
        id="cand_valid",
        domain="optics",
        subtype="thin_lens",
        physics_valid=True,
        registration=CandidateRegistration(mean_error_px=4.0),
    )
    ranked = rank_candidates([cand_invalid_physics, cand_valid])
    assert ranked[0].id == "cand_valid"
    assert ranked[0].status == CandidateStatus.VALID
    assert ranked[1].status == CandidateStatus.REJECTED_PHYSICS


def test_candidate_ranking_smallest_error():
    """Among valid candidates, smallest visual error wins."""
    cand_low_error = ModelCandidate(
        id="cand_low",
        domain="mechanics",
        subtype="pendulum",
        registration=CandidateRegistration(mean_error_px=1.5, p95_error_px=2.5),
        evidence_refs=["ref1", "ref2"],
    )
    cand_high_error = ModelCandidate(
        id="cand_high",
        domain="mechanics",
        subtype="pendulum",
        registration=CandidateRegistration(mean_error_px=5.5, p95_error_px=8.0),
        evidence_refs=["ref1", "ref2"],
    )
    ranked = rank_candidates([cand_high_error, cand_low_error])
    assert ranked[0].id == "cand_low"


def test_select_best_candidate():
    """select_best_candidate returns viable candidate or None."""
    cand1 = ModelCandidate(
        id="cand1",
        domain="mechanics",
        subtype="pendulum",
        physics_valid=True,
        registration=CandidateRegistration(mean_error_px=2.0),
    )
    best = select_best_candidate([cand1])
    assert best is not None
    assert best.id == "cand1"

    # With blockers, should return None
    cand_blocked = ModelCandidate(
        id="cand_blocked",
        domain="mechanics",
        subtype="pendulum",
        physics_valid=True,
        registration=CandidateRegistration(mean_error_px=2.0, blockers=["error > 5px"]),
    )
    assert select_best_candidate([cand_blocked]) is None

"""Initial source-versus-model registration, independent of solver readiness."""
from .base import PredictedGeometry, RegistrationThresholds
from .candidate import (
    CandidateRegistration,
    CandidateStatus,
    ModelCandidate,
    rank_candidates,
    select_best_candidate,
)
from .evaluator import InitialRegistrationGate
from .metrics import (
    mask_iou,
    point_error_px,
    polyline_distances_px,
    topology_matches,
)
from .predictors import (
    CircuitGeometryPredictor,
    PendulumGeometryPredictor,
    ProjectileGeometryPredictor,
    ThinLensGeometryPredictor,
)

__all__ = [
    "CandidateRegistration",
    "CandidateStatus",
    "CircuitGeometryPredictor",
    "InitialRegistrationGate",
    "ModelCandidate",
    "PendulumGeometryPredictor",
    "PredictedGeometry",
    "ProjectileGeometryPredictor",
    "RegistrationThresholds",
    "ThinLensGeometryPredictor",
    "mask_iou",
    "point_error_px",
    "polyline_distances_px",
    "rank_candidates",
    "select_best_candidate",
    "topology_matches",
]

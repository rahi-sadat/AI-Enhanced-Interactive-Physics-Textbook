"""Self-correcting candidate fitting framework (Phase 5).

Provides ModelCandidate for ranked candidate evaluation against source geometry.
The candidate with valid physics, strongest evidence, and smallest visual residual
is selected. Selection is never based solely on largest Hough line or nearest OCR token.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from shared.schemas.evidence import SourceLine, SourcePoint


class CandidateStatus(str, Enum):
    PENDING = "PENDING"
    VALID = "VALID"
    REJECTED_PHYSICS = "REJECTED_PHYSICS"
    REJECTED_VISUAL = "REJECTED_VISUAL"
    REJECTED_EVIDENCE = "REJECTED_EVIDENCE"


@dataclass
class CandidateRegistration:
    """Lightweight registration summary for a single candidate."""
    mean_error_px: float = float("inf")
    p95_error_px: float = float("inf")
    landmark_errors: Dict[str, float] = field(default_factory=dict)
    line_errors: Dict[str, float] = field(default_factory=dict)
    curve_errors: Dict[str, float] = field(default_factory=dict)
    mask_iou: Optional[float] = None
    topology_match: Optional[bool] = None
    blockers: List[str] = field(default_factory=list)

    @property
    def has_blockers(self) -> bool:
        return bool(self.blockers)

    @property
    def composite_error(self) -> float:
        """Composite error for ranking. Lower is better."""
        if self.has_blockers:
            return float("inf")
        errors = []
        if math.isfinite(self.mean_error_px):
            errors.append(self.mean_error_px)
        if math.isfinite(self.p95_error_px):
            errors.append(self.p95_error_px * 0.5)  # p95 weight
        if self.mask_iou is not None:
            errors.append(max(0, 1.0 - self.mask_iou) * 10.0)  # IoU penalty
        if self.topology_match is False:
            return float("inf")
        return sum(errors) / max(1, len(errors)) if errors else float("inf")


@dataclass
class ModelCandidate:
    """A candidate physical model interpretation of a source diagram.

    Contains the proposed parameters, predicted t=0 geometry, evidence
    references, registration result, and overall confidence score.
    The candidate fitting pipeline evaluates multiple candidates and
    selects the one with valid physics, strongest evidence, and
    smallest visual residual.
    """
    id: str
    domain: str
    subtype: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    geometry: Dict[str, Any] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)

    # Predicted t=0 geometry in source_px
    predicted_landmarks: Dict[str, SourcePoint] = field(default_factory=dict)
    predicted_lines: Dict[str, SourceLine] = field(default_factory=dict)
    predicted_curves: Dict[str, List[SourcePoint]] = field(default_factory=dict)

    # Registration against observed geometry
    registration: CandidateRegistration = field(default_factory=CandidateRegistration)

    # Overall confidence and status
    confidence: float = 0.0
    status: CandidateStatus = CandidateStatus.PENDING
    rejection_reason: str = ""

    # Physics validity flag
    physics_valid: bool = True
    physics_notes: str = ""

    def __post_init__(self):
        if not self.id:
            raise ValueError("Candidate must have an ID")

    @property
    def visual_error(self) -> float:
        return self.registration.composite_error

    @property
    def is_viable(self) -> bool:
        return (self.status in (CandidateStatus.PENDING, CandidateStatus.VALID)
                and self.physics_valid
                and not self.registration.has_blockers)

    def reject(self, reason: str, status: CandidateStatus = CandidateStatus.REJECTED_VISUAL):
        self.status = status
        self.rejection_reason = reason
        self.confidence = 0.0


def rank_candidates(candidates: List[ModelCandidate]) -> List[ModelCandidate]:
    """Rank candidates by: valid physics first, then strongest evidence, then smallest visual error.

    Returns a new list sorted best-first. Does not mutate the input.
    """
    if not candidates:
        return []

    def sort_key(c: ModelCandidate):
        # Primary: valid physics (True sorts before False with negative)
        physics_ok = 0 if c.physics_valid else 1
        # Secondary: no registration blockers
        has_blockers = 0 if not c.registration.has_blockers else 1
        # Tertiary: visual error (lower is better)
        error = c.visual_error if math.isfinite(c.visual_error) else 1e9
        # Quaternary: evidence count (more is better, negate for sort)
        evidence = -len(c.evidence_refs)
        return (physics_ok, has_blockers, error, evidence)

    ranked = sorted(candidates, key=sort_key)

    # Mark best candidate as VALID, rest get their status
    for i, candidate in enumerate(ranked):
        if i == 0 and candidate.physics_valid and not candidate.registration.has_blockers:
            candidate.status = CandidateStatus.VALID
        elif candidate.status == CandidateStatus.PENDING:
            if not candidate.physics_valid:
                candidate.status = CandidateStatus.REJECTED_PHYSICS
            elif candidate.registration.has_blockers:
                candidate.status = CandidateStatus.REJECTED_VISUAL

    return ranked


def select_best_candidate(candidates: List[ModelCandidate]) -> Optional[ModelCandidate]:
    """Select the single best candidate, or None if all are rejected."""
    ranked = rank_candidates(candidates)
    if ranked and ranked[0].is_viable:
        return ranked[0]
    return None

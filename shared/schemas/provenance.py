"""Centralized provenance source taxonomy (Phase 3).

Every inferred, derived, or assumed value must carry one of these provenance
sources. The categories describe HOW a value was obtained, independent of its
physical dimension or SI unit.
"""
from __future__ import annotations

from enum import Enum


class ProvenanceSource(str, Enum):
    """How a parameter or geometry value was obtained."""

    # Directly measured from source image pixels via classical CV
    OBSERVED = "observed"

    # Extracted via OCR from printed text in the source diagram
    OCR = "ocr"

    # Mathematically derived from other observed/OCR values
    DERIVED = "derived"

    # Fitted by minimizing visual residual against source geometry
    INVERSE_FIT = "inverse_fit"

    # Standard physics constant (e.g., Earth gravity, zero damping)
    # that does NOT affect source geometry reproduction
    STANDARD_PHYSICS_ASSUMPTION = "standard_physics_assumption"

    # Normalized visual assumption that DOES affect geometry
    # (e.g., default focal length ratio, default object position)
    # Must NOT be used when source geometry should be detected
    NORMALIZED_VISUAL_ASSUMPTION = "normalized_visual_assumption"

    # Explicitly confirmed or corrected by a human user
    USER_CONFIRMED = "user_confirmed"

    # VLM semantic classification (not usable for grounding)
    VLM_SEMANTIC = "vlm_semantic"


# Sources that can ground faithful source reproduction
GROUNDING_SOURCES = frozenset({
    ProvenanceSource.OBSERVED,
    ProvenanceSource.OCR,
    ProvenanceSource.DERIVED,
    ProvenanceSource.INVERSE_FIT,
    ProvenanceSource.USER_CONFIRMED,
})

# Sources that only support normalized/exploration simulation
ASSUMPTION_SOURCES = frozenset({
    ProvenanceSource.STANDARD_PHYSICS_ASSUMPTION,
    ProvenanceSource.NORMALIZED_VISUAL_ASSUMPTION,
})

# Sources that NEVER ground geometry
NON_GROUNDING_SOURCES = frozenset({
    ProvenanceSource.VLM_SEMANTIC,
    ProvenanceSource.NORMALIZED_VISUAL_ASSUMPTION,
})

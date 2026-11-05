"""PR-06 Subtype-Specific Grounder Protocol and Outcomes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from shared.schemas.evidence import (
    EntityGroundingDiagnostic,
    EvidenceRecord,
    GroundingState,
    OCRExtractionResult,
    ParsedPhysicalValueCandidate,
    SegmentationResult,
)
from shared.schemas.ingestion import BookIR


@dataclass
class GroundingOutcome:
    """Outcome of fusing evidence into a BookIR for a specific physical subtype."""
    grounded_book_ir: BookIR
    diagnostics: List[EntityGroundingDiagnostic] = field(default_factory=list)
    new_evidence_records: Dict[str, EvidenceRecord] = field(default_factory=dict)
    candidate_parameters: List[ParsedPhysicalValueCandidate] = field(default_factory=list)
    parameter_associations: List[ParameterAssociationResult] = field(default_factory=list)



@runtime_checkable
class EntityGrounder(Protocol):
    """Protocol for subtype-specific evidence grounders."""

    def supports(self, domain: Optional[str], subtype: Optional[str]) -> bool:
        """Check if this grounder supports the given physics domain and subtype."""
        ...

    def ground(
        self,
        book_ir: BookIR,
        cv_candidates: Dict[str, Any],
        ocr_result: Optional[OCRExtractionResult],
        seg_result: Optional[SegmentationResult],
        source_width: int,
        source_height: int,
    ) -> GroundingOutcome:
        """Fuse visual evidence into BookIR entities, geometry, and parameters."""
        ...

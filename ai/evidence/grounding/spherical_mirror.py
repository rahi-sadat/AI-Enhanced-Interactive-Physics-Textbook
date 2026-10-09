"""PR-06 Spherical Mirror Subtype Evidence Grounder.

Grounds spherical mirror optical entities:
  - mirror surface & pole
  - principal optical axis
  - focus (F) and center of curvature (C)

Strict Invariants:
  - Diagram pixel curvature is NEVER fabricated into physical radius of curvature.
  - Missing focal length or radius of curvature retains NEEDS_REVIEW.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from shared.schemas.evidence import (
    AssociationState,
    EntityGroundingDiagnostic,
    EvidenceMethod,
    EvidenceRecord,
    GroundingState,
    OCRExtractionResult,
    ParameterAssociationResult,
    ParsedPhysicalValueCandidate,
    SegmentationResult,
    SourcePoint,
)
from shared.schemas.ingestion import (
    BookEntity,
    BookIR,
    BookIRStatus,
    PhysicalValue,
    ProvenanceRecord,
)
from ai.evidence.grounding.base import GroundingOutcome
from ai.evidence.grounding.physical_value_parser import parse_physical_value_candidate

logger = logging.getLogger(__name__)


class SphericalMirrorGrounder:
    """Specialized evidence grounder for optics / spherical_mirror."""

    @property
    def domain(self) -> str:
        return "optics"

    @property
    def subtype(self) -> str:
        return "spherical_mirror"

    def supports(self, domain: Optional[str], subtype: Optional[str]) -> bool:
        return (domain or "").lower() == "optics" and (subtype or "").lower() in ("spherical_mirror", "mirror", "concave_mirror", "convex_mirror")

    def ground(
        self,
        book_ir: BookIR,
        cv_candidates: Dict[str, Any],
        ocr_result: Optional[OCRExtractionResult] = None,
        seg_result: Optional[SegmentationResult] = None,
        source_width: int = 0,
        source_height: int = 0,
    ) -> GroundingOutcome:
        import copy
        grounded_ir = copy.deepcopy(book_ir)
        if grounded_ir.geometry is None:
            grounded_ir.geometry = {}
        if source_width > 0:
            grounded_ir.geometry["width"] = source_width
        if source_height > 0:
            grounded_ir.geometry["height"] = source_height
        grounded_ir.geometry["coordinate_space"] = "source_px"
        return self.fuse(
            book_ir=grounded_ir,
            cv_candidates=cv_candidates,
            segmentation_candidates=seg_result,
            ocr_result=ocr_result,
        )

    def fuse(
        self,
        book_ir: BookIR,
        cv_candidates: Dict[str, Any],
        segmentation_candidates: Optional[SegmentationResult] = None,
        ocr_result: Optional[OCRExtractionResult] = None,
    ) -> GroundingOutcome:
        grounded_ir = book_ir
        diagnostics: List[EntityGroundingDiagnostic] = []
        new_evidence: Dict[str, EvidenceRecord] = {}
        all_val_candidates: List[ParsedPhysicalValueCandidate] = []
        param_associations: List[ParameterAssociationResult] = []

        cv_ev_id = f"ev_cv_mirror_{grounded_ir.source_asset_id or 'anon'}"
        new_evidence[cv_ev_id] = EvidenceRecord(
            id=cv_ev_id,
            method=EvidenceMethod.CLASSICAL_CV,
            source_asset_id=grounded_ir.source_asset_id,
            figure_id=grounded_ir.figure_id,
            confidence=None,
            verified=False,
            coordinate_space="source_px",
            provider="spherical_mirror_cv_extractor",
            payload={
                "has_axis": cv_candidates.get("principal_axis") is not None,
                "has_pole": cv_candidates.get("pole") is not None,
            },
        )

        mirror_ent = next((e for e in grounded_ir.entities if e.type in ("mirror", "spherical_mirror", "pole")), None)
        axis_ent = next((e for e in grounded_ir.entities if e.type in ("principal_axis", "optical_axis")), None)

        axis_line = cv_candidates.get("principal_axis")
        pole_pt: Optional[SourcePoint] = cv_candidates.get("pole")

        if mirror_ent:
            if pole_pt:
                mirror_ent.position_source_px = {
                    "x": pole_pt.x,
                    "y": pole_pt.y,
                    "coordinate_space": "source_px",
                    "method": "cv_mirror_pole",
                }
                mirror_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=mirror_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"pole": pole_pt.to_dict()},
                        notes="Mirror vertex / pole grounded.",
                    )
                )
                grounded_ir.parameters["pole"] = pole_pt.to_dict()
            else:
                mirror_ent.position_source_px = None
                mirror_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=mirror_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Mirror pole not detected.",
                    )
                )

        if axis_ent:
            if axis_line:
                axis_ent.geometry = {
                    "start": axis_line.start.to_dict() if hasattr(axis_line.start, "to_dict") else axis_line.start,
                    "end": axis_line.end.to_dict() if hasattr(axis_line.end, "to_dict") else axis_line.end,
                    "length_px": getattr(axis_line, "length_px", 0.0),
                }
                axis_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=axis_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"length_px": getattr(axis_line, "length_px", 0.0)},
                        notes="Principal optical axis grounded.",
                    )
                )
            else:
                axis_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=axis_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Principal optical axis not detected.",
                    )
                )

        if ocr_result and ocr_result.tokens:
            for tok in ocr_result.tokens:
                tok_ev_id = f"ev_ocr_{tok.id}"
                new_evidence[tok_ev_id] = EvidenceRecord(
                    id=tok_ev_id,
                    method=EvidenceMethod.OCR,
                    source_asset_id=grounded_ir.source_asset_id,
                    figure_id=grounded_ir.figure_id,
                    confidence=tok.confidence,
                    verified=False,
                    coordinate_space="source_px",
                    provider=ocr_result.provider,
                    payload={"raw_text": tok.raw_text, "bbox": tok.bbox_source_px.to_dict() if tok.bbox_source_px else None},
                )
                val_cands = parse_physical_value_candidate(tok)
                all_val_candidates.extend(val_cands)

                for cand in val_cands:
                    if cand.quantity_candidate == "length" and cand.numeric_value is not None:
                        canonical_m = cand.numeric_value
                        if cand.raw_unit == "cm":
                            canonical_m = cand.numeric_value * 0.01
                        elif cand.raw_unit == "mm":
                            canonical_m = cand.numeric_value * 0.001

                        text_lower = tok.raw_text.lower()
                        is_focal_label = any(lbl in text_lower for lbl in ("f =", "f=", "f:", "focal", "ফোকাস", "focal length")) or tok.raw_text.strip().startswith(("f =", "F =", "f=", "F="))
                        is_roc_label = any(lbl in text_lower for lbl in ("r =", "r=", "c =", "radius", "বক্রতার ব্যাসার্ধ", "curvature")) or tok.raw_text.strip().startswith(("r =", "R =", "r=", "R="))

                        if is_focal_label:
                            grounded_ir.parameters["focal_length"] = PhysicalValue(
                                value=canonical_m,
                                unit="m",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_f_{cand.token_id}",
                                    target_entity_id=mirror_ent.id if mirror_ent else None,
                                    target_quantity="focal_length",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "m",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks={"explicit_label": True},
                                    confidence=cand.confidence,
                                )
                            )
                        elif is_roc_label:
                            grounded_ir.parameters["radius_of_curvature"] = PhysicalValue(
                                value=canonical_m,
                                unit="m",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_r_{cand.token_id}",
                                    target_entity_id=mirror_ent.id if mirror_ent else None,
                                    target_quantity="radius_of_curvature",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "m",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks={"explicit_label": True},
                                    confidence=cand.confidence,
                                )
                            )
                        else:
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_len_{cand.token_id}",
                                    target_entity_id=None,
                                    target_quantity="length",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "m",
                                    state=AssociationState.REJECTED,
                                    supporting_evidence=[],
                                    association_checks={"explicit_label": False},
                                    confidence=cand.confidence,
                                )
                            )

        grounded_ir.evidence.update({k: v.to_dict() for k, v in new_evidence.items()})
        grounded_ir.provenance["grounding_diagnostics"] = [d.to_dict() for d in diagnostics]
        grounded_ir.provenance["candidate_parameters"] = [c.to_dict() for c in all_val_candidates]

        # Status Invariant: Grounders extract and associate; status remains NEEDS_REVIEW for compiler verification
        grounded_ir.status = BookIRStatus.NEEDS_REVIEW
        has_focal = "focal_length" in grounded_ir.parameters or "radius_of_curvature" in grounded_ir.parameters
        if has_focal and pole_pt:
            grounded_ir.status_notes = "Grounded spherical mirror pole and optical parameters; pending compiler verification."
        else:
            grounded_ir.status_notes = "Missing focal length, radius of curvature, or mirror pole."

        return GroundingOutcome(
            grounded_book_ir=grounded_ir,
            diagnostics=diagnostics,
            new_evidence_records=new_evidence,
            candidate_parameters=all_val_candidates,
            parameter_associations=param_associations,
        )

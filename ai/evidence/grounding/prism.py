"""PR-06 Prism Subtype Evidence Grounder.

Grounds prism optical entities:
  - prism polygon & apex
  - incident ray & emergent ray

Strict Invariants:
  - Refractive index n is NEVER fabricated without evidence (no assuming n=1.5).
  - Prism apex angle is NEVER assumed to be 60 degrees without evidence.
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
    SourcePolygon,
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


class PrismGrounder:
    """Specialized evidence grounder for optics / prism."""

    @property
    def domain(self) -> str:
        return "optics"

    @property
    def subtype(self) -> str:
        return "prism"

    def supports(self, domain: Optional[str], subtype: Optional[str]) -> bool:
        return (domain or "").lower() == "optics" and (subtype or "").lower() == "prism"

    def ground(
        self,
        book_ir: BookIR,
        cv_candidates: Dict[str, Any],
        ocr_result: Optional[OCRExtractionResult] = None,
        seg_result: Optional[SegmentationResult] = None,
        source_width: int = 0,
        source_height: int = 0,
    ) -> GroundingOutcome:
        return self.fuse(
            book_ir=book_ir,
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

        cv_ev_id = f"ev_cv_prism_{grounded_ir.source_asset_id or 'anon'}"
        new_evidence[cv_ev_id] = EvidenceRecord(
            id=cv_ev_id,
            method=EvidenceMethod.CLASSICAL_CV,
            source_asset_id=grounded_ir.source_asset_id,
            figure_id=grounded_ir.figure_id,
            confidence=None,
            verified=False,
            coordinate_space="source_px",
            provider="prism_cv_extractor",
            payload={
                "has_polygon": cv_candidates.get("prism_polygon") is not None,
                "has_apex": cv_candidates.get("apex") is not None,
            },
        )

        prism_ent = next((e for e in grounded_ir.entities if e.type in ("prism", "prism_body")), None)
        poly: Optional[SourcePolygon] = cv_candidates.get("prism_polygon")
        apex: Optional[SourcePoint] = cv_candidates.get("apex")

        if prism_ent:
            if poly:
                prism_ent.geometry = {
                    "polygon": poly.to_dict() if hasattr(poly, "to_dict") else poly,
                    "bounds": poly.bbox.to_dict() if hasattr(poly.bbox, "to_dict") else poly.bbox,
                }
                if apex:
                    prism_ent.position_source_px = {
                        "x": apex.x,
                        "y": apex.y,
                        "coordinate_space": "source_px",
                        "method": "cv_prism_apex",
                    }
                prism_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=prism_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"vertex_count": len(poly.points) if hasattr(poly, "points") else 3},
                        notes="Prism triangular body grounded.",
                    )
                )
            else:
                prism_ent.geometry = None
                prism_ent.position_source_px = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=prism_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Prism triangular geometry not detected.",
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
                    text_lower = tok.raw_text.lower()
                    if cand.quantity_candidate == "angle" and cand.numeric_value is not None:
                        is_apex = any(lbl in text_lower for lbl in ("a =", "a=", "apex", "প্রিজম কোণ", "কোণ a")) or tok.raw_text.strip().startswith(("a =", "A =", "a=", "A="))
                        if is_apex:
                            grounded_ir.parameters["apex_angle"] = PhysicalValue(
                                value=cand.numeric_value,
                                unit="deg",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_apex_{cand.token_id}",
                                    target_entity_id=prism_ent.id if prism_ent else None,
                                    target_quantity="apex_angle",
                                    value=cand.numeric_value,
                                    unit="deg",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks={"explicit_label": True},
                                    confidence=cand.confidence,
                                )
                            )
                        else:
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_ang_{cand.token_id}",
                                    target_entity_id=None,
                                    target_quantity="angle",
                                    value=cand.numeric_value,
                                    unit="deg",
                                    state=AssociationState.REJECTED,
                                    supporting_evidence=[],
                                    association_checks={"explicit_label": False},
                                    confidence=cand.confidence,
                                )
                            )

                    elif cand.quantity_candidate in ("refractive_index", "dimensionless") and cand.numeric_value is not None:
                        if any(lbl in text_lower for lbl in ("n =", "n=", "μ =", "mu =", "refractive index", "প্রতিসরাঙ্ক")):
                            grounded_ir.parameters["refractive_index"] = PhysicalValue(
                                value=cand.numeric_value,
                                unit="dimensionless",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_n_{cand.token_id}",
                                    target_entity_id=prism_ent.id if prism_ent else None,
                                    target_quantity="refractive_index",
                                    value=cand.numeric_value,
                                    unit="dimensionless",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks={"explicit_label": True},
                                    confidence=cand.confidence,
                                )
                            )

        grounded_ir.evidence.update({k: v.to_dict() for k, v in new_evidence.items()})
        grounded_ir.provenance["grounding_diagnostics"] = [d.to_dict() for d in diagnostics]
        grounded_ir.provenance["candidate_parameters"] = [c.to_dict() for c in all_val_candidates]

        # Status Invariant: Grounders extract and associate; status remains NEEDS_REVIEW for compiler verification
        grounded_ir.status = BookIRStatus.NEEDS_REVIEW
        has_n = "n" in grounded_ir.parameters or "refractive_index" in grounded_ir.parameters
        has_apex = "apex_angle" in grounded_ir.parameters

        if has_n and has_apex and poly:
            grounded_ir.status_notes = "Grounded prism polygon, apex angle, and refractive index; pending compiler verification."
        else:
            grounded_ir.status_notes = "Missing refractive index, apex angle, or prism polygon geometry."

        return GroundingOutcome(
            grounded_book_ir=grounded_ir,
            diagnostics=diagnostics,
            new_evidence_records=new_evidence,
            candidate_parameters=all_val_candidates,
            parameter_associations=param_associations,
        )

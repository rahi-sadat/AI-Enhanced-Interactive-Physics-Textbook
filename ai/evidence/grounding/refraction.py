"""PR-06 Interface Refraction Subtype Evidence Grounder.

Grounds refraction optical entities:
  - medium boundary
  - normal line
  - incident ray & refracted ray
  - point of incidence

Strict Invariants:
  - Image-space angles are recorded as geometric evidence; authoritative physical values require OCR evidence.
  - Refractive index n2 is NEVER fabricated without evidence (e.g. no assuming n=1.5).
"""
from __future__ import annotations

import logging
import math
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


class InterfaceRefractionGrounder:
    """Specialized evidence grounder for optics / interface_refraction."""

    @property
    def domain(self) -> str:
        return "optics"

    @property
    def subtype(self) -> str:
        return "interface_refraction"

    def supports(self, domain: Optional[str], subtype: Optional[str]) -> bool:
        return (domain or "").lower() == "optics" and (subtype or "").lower() in ("interface_refraction", "refraction", "snell")

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

        cv_ev_id = f"ev_cv_refract_{grounded_ir.source_asset_id or 'anon'}"
        new_evidence[cv_ev_id] = EvidenceRecord(
            id=cv_ev_id,
            method=EvidenceMethod.CLASSICAL_CV,
            source_asset_id=grounded_ir.source_asset_id,
            figure_id=grounded_ir.figure_id,
            confidence=None,
            verified=False,
            coordinate_space="source_px",
            provider="interface_refraction_cv_extractor",
            payload={
                "has_boundary": cv_candidates.get("boundary_line") is not None,
                "has_normal": cv_candidates.get("normal_line") is not None,
                "has_incident_ray": cv_candidates.get("incident_ray") is not None,
            },
        )

        bound_ent = next((e for e in grounded_ir.entities if e.type in ("medium_boundary", "boundary", "interface")), None)
        normal_ent = next((e for e in grounded_ir.entities if e.type in ("normal", "surface_normal")), None)
        inc_ent = next((e for e in grounded_ir.entities if e.type in ("incident_ray", "light_ray")), None)

        bound_line = cv_candidates.get("boundary_line")
        norm_line = cv_candidates.get("normal_line")
        inc_ray = cv_candidates.get("incident_ray")
        refr_ray = cv_candidates.get("refracted_ray")
        inc_pt: Optional[SourcePoint] = cv_candidates.get("incidence_point")

        if bound_ent:
            if bound_line:
                bound_ent.geometry = {
                    "start": bound_line.start.to_dict() if hasattr(bound_line.start, "to_dict") else bound_line.start,
                    "end": bound_line.end.to_dict() if hasattr(bound_line.end, "to_dict") else bound_line.end,
                    "y": cv_candidates.get("bound_y"),
                }
                bound_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=bound_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"boundary_y": cv_candidates.get("bound_y")},
                        notes="Medium boundary interface grounded.",
                    )
                )
            else:
                bound_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=bound_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Medium boundary interface not detected.",
                    )
                )

        if normal_ent:
            if norm_line:
                normal_ent.geometry = {
                    "start": norm_line.start.to_dict() if hasattr(norm_line.start, "to_dict") else norm_line.start,
                    "end": norm_line.end.to_dict() if hasattr(norm_line.end, "to_dict") else norm_line.end,
                    "x": cv_candidates.get("normal_x"),
                }
                normal_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=normal_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"normal_x": cv_candidates.get("normal_x")},
                        notes="Surface normal line grounded.",
                    )
                )
            else:
                normal_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=normal_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Surface normal line not detected.",
                    )
                )

        if inc_ent:
            if inc_ray:
                inc_ent.geometry = {
                    "start": inc_ray.start.to_dict() if hasattr(inc_ray.start, "to_dict") else inc_ray.start,
                    "end": inc_ray.end.to_dict() if hasattr(inc_ray.end, "to_dict") else inc_ray.end,
                }
                inc_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=inc_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"ray_length": getattr(inc_ray, "length_px", 0.0)},
                        notes="Incident ray path grounded.",
                    )
                )
            else:
                inc_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=inc_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Incident ray not detected.",
                    )
                )

        # Store geometric evidence only if detected
        if cv_candidates.get("bound_y") is not None:
            grounded_ir.parameters["boundary_y"] = float(cv_candidates["bound_y"])
        if cv_candidates.get("normal_x") is not None:
            grounded_ir.parameters["normal_x"] = float(cv_candidates["normal_x"])
        if inc_pt is not None:
            grounded_ir.parameters["incidence_point"] = inc_pt.to_dict() if hasattr(inc_pt, "to_dict") else inc_pt

        # 4. OCR Values & Strict Parameter Association
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
                        is_inc_label = any(lbl in text_lower for lbl in ("i =", "i=", "θ1", "theta1", "theta_1", "আপতন", "incidence")) or tok.raw_text.strip().startswith(("i =", "I =", "i=", "I="))
                        is_refr_label = any(lbl in text_lower for lbl in ("r =", "r=", "θ2", "theta2", "theta_2", "প্রতিসরণ", "refraction")) or tok.raw_text.strip().startswith(("r =", "R =", "r=", "R="))

                        if is_inc_label:
                            grounded_ir.parameters["incident_angle"] = PhysicalValue(
                                value=cand.numeric_value,
                                unit="deg",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_i_{cand.token_id}",
                                    target_entity_id=inc_ent.id if inc_ent else None,
                                    target_quantity="incident_angle",
                                    value=cand.numeric_value,
                                    unit="deg",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks={"explicit_label": True},
                                    confidence=cand.confidence,
                                )
                            )
                        elif is_refr_label:
                            grounded_ir.parameters["refracted_angle"] = PhysicalValue(
                                value=cand.numeric_value,
                                unit="deg",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_r_{cand.token_id}",
                                    target_entity_id=None,
                                    target_quantity="refracted_angle",
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
                        is_n2 = any(lbl in text_lower for lbl in ("n2", "n_2", "medium 2", "গ্লাস", "পানি", "জল", "water", "glass"))
                        is_n1 = any(lbl in text_lower for lbl in ("n1", "n_1", "air", "বায়ু"))
                        if is_n2 or "n =" in text_lower or "n=" in text_lower:
                            grounded_ir.parameters["n2"] = PhysicalValue(
                                value=cand.numeric_value,
                                unit="dimensionless",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_n2_{cand.token_id}",
                                    target_entity_id=None,
                                    target_quantity="n2",
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
        has_n2 = "n2" in grounded_ir.parameters or "medium2_index" in grounded_ir.parameters
        has_angles = "incident_angle" in grounded_ir.parameters or "refracted_angle" in grounded_ir.parameters

        if has_n2 and has_angles and bound_line:
            grounded_ir.status_notes = "Grounded refraction interface and optical parameters; pending compiler verification."
        else:
            grounded_ir.status_notes = "Missing refractive index n2, optical angles, or boundary interface."

        return GroundingOutcome(
            grounded_book_ir=grounded_ir,
            diagnostics=diagnostics,
            new_evidence_records=new_evidence,
            candidate_parameters=all_val_candidates,
            parameter_associations=param_associations,
        )

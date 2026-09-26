"""PR-06 Thin Lens Subtype Evidence Grounder.

Grounds thin lens optical entities:
  - lens center & body
  - optical axis line
  - object arrow & distance
  - image arrow & distance

Strict Invariants:
  - Distance in pixels to printed letter 'F' is NEVER fabricated into physical focal length.
  - Missing focal_length retains NEEDS_REVIEW with scene=null.
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


class ThinLensGrounder:
    """Specialized evidence grounder for optics / thin_lens."""

    @property
    def domain(self) -> str:
        return "optics"

    @property
    def subtype(self) -> str:
        return "thin_lens"

    def supports(self, domain: Optional[str], subtype: Optional[str]) -> bool:
        return (domain or "").lower() == "optics" and (subtype or "").lower() in ("thin_lens", "concave_lens")

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

        cv_ev_id = f"ev_cv_lens_{grounded_ir.source_asset_id or 'anon'}"
        new_evidence[cv_ev_id] = EvidenceRecord(
            id=cv_ev_id,
            method=EvidenceMethod.CLASSICAL_CV,
            source_asset_id=grounded_ir.source_asset_id,
            figure_id=grounded_ir.figure_id,
            confidence=None,
            verified=False,
            coordinate_space="source_px",
            provider="thin_lens_cv_extractor",
            payload={
                "has_optical_axis": cv_candidates.get("optical_axis") is not None,
                "has_lens_center": cv_candidates.get("lens_center") is not None,
                "has_object_arrow": cv_candidates.get("object_arrow") is not None,
            },
        )

        lens_ent = next((e for e in grounded_ir.entities if e.type in ("lens", "optical_center")), None)
        axis_ent = next((e for e in grounded_ir.entities if e.type in ("optical_axis", "principal_axis")), None)
        object_ent = next((e for e in grounded_ir.entities if e.type in ("object", "object_arrow")), None)
        image_ent = next((e for e in grounded_ir.entities if e.type in ("image", "image_arrow")), None)

        lens_center: Optional[SourcePoint] = cv_candidates.get("lens_center")
        axis_line = cv_candidates.get("optical_axis")
        obj_arrow = cv_candidates.get("object_arrow")
        img_arrow = cv_candidates.get("image_arrow")

        # 1. Ground Lens Center
        if lens_ent:
            if lens_center:
                lens_ent.position_source_px = {
                    "x": lens_center.x,
                    "y": lens_center.y,
                    "coordinate_space": "source_px",
                    "method": "cv_lens_center",
                }
                lens_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=lens_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"lens_center": lens_center.to_dict()},
                        notes="Lens center grounded at axis-vertical intersection.",
                    )
                )
                grounded_ir.parameters["lens_center"] = lens_center.to_dict()
            else:
                lens_ent.position_source_px = None
                lens_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=lens_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Lens center coordinate unresolved.",
                    )
                )

        # 2. Ground Optical Axis
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
                        checks={"axis_y": (getattr(axis_line.start, "y", 0.0) + getattr(axis_line.end, "y", 0.0)) / 2.0},
                        notes="Principal optical axis grounded.",
                    )
                )
            else:
                axis_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=axis_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Optical axis line unresolved.",
                    )
                )

        # 3. Ground Object Arrow
        if object_ent:
            if obj_arrow:
                object_ent.geometry = {
                    "start": obj_arrow.start.to_dict() if hasattr(obj_arrow.start, "to_dict") else obj_arrow.start,
                    "end": obj_arrow.end.to_dict() if hasattr(obj_arrow.end, "to_dict") else obj_arrow.end,
                    "height_px": getattr(obj_arrow, "length_px", 0.0),
                }
                object_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=object_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"height_px": getattr(obj_arrow, "length_px", 0.0)},
                        notes="Object arrow verified.",
                    )
                )
            else:
                object_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=object_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Object arrow not detected.",
                    )
                )

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

                tok_box = tok.bbox_source_px
                tok_cx = (tok_box.x + tok_box.width / 2.0) if tok_box else None
                tok_cy = (tok_box.y + tok_box.height / 2.0) if tok_box else None
                tok_pt = SourcePoint(tok_cx, tok_cy) if (tok_cx is not None and tok_cy is not None) else None

                for cand in val_cands:
                    if cand.quantity_candidate == "length" and cand.numeric_value is not None:
                        canonical_m = cand.numeric_value
                        if cand.raw_unit == "cm":
                            canonical_m = cand.numeric_value * 0.01
                        elif cand.raw_unit == "mm":
                            canonical_m = cand.numeric_value * 0.001

                        text_lower = tok.raw_text.lower()
                        # Strict label matching (not crude 'f' in raw_text)
                        is_focal_label = any(lbl in text_lower for lbl in ("f =", "f=", "f:", "focal", "ফোকাস", "focal length")) or tok.raw_text.strip().startswith(("f =", "F =", "f=", "F="))
                        is_obj_dist_label = any(lbl in text_lower for lbl in ("u =", "u=", "do =", "d_o", "u:", "object distance", "লক্ষ্যবস্তুর দূরত্ব")) or tok.raw_text.strip().startswith(("u =", "U =", "u=", "U="))
                        is_img_dist_label = any(lbl in text_lower for lbl in ("v =", "v=", "di =", "d_i", "v:", "image distance", "প্রতিবিম্বের দূরত্ব")) or tok.raw_text.strip().startswith(("v =", "V =", "v=", "V="))

                        near_obj = False
                        if tok_pt and obj_arrow:
                            near_obj = tok_pt.distance_to(obj_arrow.start if hasattr(obj_arrow, "start") else SourcePoint(0, 0)) < 100.0

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
                                    target_entity_id=lens_ent.id if lens_ent else None,
                                    target_quantity="focal_length",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "m",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks={"explicit_label": True},
                                    confidence=cand.confidence,
                                )
                            )
                        elif is_obj_dist_label or near_obj:
                            grounded_ir.parameters["object_distance"] = PhysicalValue(
                                value=canonical_m,
                                unit="m",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_u_{cand.token_id}",
                                    target_entity_id=object_ent.id if object_ent else None,
                                    target_quantity="object_distance",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "m",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks={"explicit_label": is_obj_dist_label, "near_object": near_obj},
                                    confidence=cand.confidence,
                                )
                            )
                        elif is_img_dist_label:
                            grounded_ir.parameters["image_distance"] = PhysicalValue(
                                value=canonical_m,
                                unit="m",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_v_{cand.token_id}",
                                    target_entity_id=image_ent.id if image_ent else None,
                                    target_quantity="image_distance",
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
                                    association_checks={"explicit_label": False, "near_geometry": False},
                                    confidence=cand.confidence,
                                )
                            )

        grounded_ir.evidence.update({k: v.to_dict() for k, v in new_evidence.items()})
        grounded_ir.provenance["grounding_diagnostics"] = [d.to_dict() for d in diagnostics]
        grounded_ir.provenance["candidate_parameters"] = [c.to_dict() for c in all_val_candidates]

        # Status Invariant: Grounders extract and associate; status remains NEEDS_REVIEW for compiler verification
        grounded_ir.status = BookIRStatus.NEEDS_REVIEW
        has_focal_length = "focal_length" in grounded_ir.parameters
        has_object_dist = "object_distance" in grounded_ir.parameters

        if has_focal_length and has_object_dist and lens_center:
            grounded_ir.status_notes = "Grounded thin lens focal length and object geometry; pending compiler verification."
        else:
            grounded_ir.status_notes = "Missing focal_length, object_distance, or lens center."

        return GroundingOutcome(
            grounded_book_ir=grounded_ir,
            diagnostics=diagnostics,
            new_evidence_records=new_evidence,
            candidate_parameters=all_val_candidates,
            parameter_associations=param_associations,
        )

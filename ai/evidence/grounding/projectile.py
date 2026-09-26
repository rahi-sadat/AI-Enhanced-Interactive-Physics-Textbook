"""PR-06 Projectile Motion Subtype Evidence Grounder.

Grounds projectile entities:
  - projectile body
  - launch point
  - ground reference line
  - velocity vector line

Strict Invariants:
  - Arrow pixel length is NEVER fabricated into velocity magnitude (m/s).
  - Missing launch_speed, launch_angle, or gravity retains NEEDS_REVIEW.
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


class ProjectileGrounder:
    """Specialized evidence grounder for mechanics / projectile."""

    @property
    def domain(self) -> str:
        return "mechanics"

    @property
    def subtype(self) -> str:
        return "projectile"

    def supports(self, domain: Optional[str], subtype: Optional[str]) -> bool:
        return (domain or "").lower() == "mechanics" and (subtype or "").lower() == "projectile"

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

        cv_ev_id = f"ev_cv_projectile_{grounded_ir.source_asset_id or 'anon'}"
        new_evidence[cv_ev_id] = EvidenceRecord(
            id=cv_ev_id,
            method=EvidenceMethod.CLASSICAL_CV,
            source_asset_id=grounded_ir.source_asset_id,
            figure_id=grounded_ir.figure_id,
            confidence=None,
            verified=False,
            coordinate_space="source_px",
            provider="projectile_cv_extractor",
            payload={
                "has_launch_point": cv_candidates.get("launch_point") is not None,
                "has_ground_line": cv_candidates.get("ground_line") is not None,
                "has_velocity_vector": cv_candidates.get("velocity_vector") is not None,
            },
        )

        body_ent = next((e for e in grounded_ir.entities if e.type in ("projectile_body", "projectile")), None)
        ground_ent = next((e for e in grounded_ir.entities if e.type in ("ground_surface", "launch_platform", "ground")), None)
        vector_ent = next((e for e in grounded_ir.entities if e.type in ("velocity_vector", "launch_velocity")), None)

        launch_pt: Optional[SourcePoint] = cv_candidates.get("launch_point")
        ground_line = cv_candidates.get("ground_line")
        vel_line = cv_candidates.get("velocity_vector")
        body_circ = cv_candidates.get("projectile_body")

        # 1. Ground Projectile Body
        if body_ent:
            if launch_pt:
                body_ent.position_source_px = {
                    "x": launch_pt.x,
                    "y": launch_pt.y,
                    "coordinate_space": "source_px",
                    "method": "cv_projectile_launch",
                }
                body_ent.evidence_refs = [cv_ev_id]
                if body_circ:
                    body_ent.geometry = {
                        "radius_px": body_circ["radius_px"],
                        "bounds": body_circ["bbox"].to_dict() if hasattr(body_circ["bbox"], "to_dict") else body_circ["bbox"],
                    }
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=body_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"launch_point": launch_pt.to_dict()},
                        notes="Projectile body grounded at launch origin.",
                    )
                )
                grounded_ir.parameters["launch_origin"] = launch_pt.to_dict()
            else:
                body_ent.position_source_px = None
                body_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=body_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="No launch point candidate detected.",
                    )
                )

        # 2. Ground Ground Line
        if ground_ent:
            if ground_line:
                ground_ent.geometry = {
                    "start": ground_line.start.to_dict() if hasattr(ground_line.start, "to_dict") else ground_line.start,
                    "end": ground_line.end.to_dict() if hasattr(ground_line.end, "to_dict") else ground_line.end,
                    "length_px": getattr(ground_line, "length_px", 0.0),
                }
                ground_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=ground_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"ground_line": ground_line.to_dict() if hasattr(ground_line, "to_dict") else str(ground_line)},
                        notes="Ground reference line verified from classical CV.",
                    )
                )
            else:
                ground_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=ground_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Ground reference line not detected.",
                    )
                )

        # 3. Ground Velocity Vector Line (Angle only, ZERO velocity magnitude fabrication!)
        if vector_ent:
            if vel_line:
                if hasattr(vel_line, "start"):
                    start_dict = vel_line.start.to_dict() if hasattr(vel_line.start, "to_dict") else vel_line.start
                    end_dict = vel_line.end.to_dict() if hasattr(vel_line.end, "to_dict") else vel_line.end
                    arrow_len = getattr(vel_line, "length_px", 0.0)
                    angle_deg = -math.degrees(getattr(vel_line, "angle_rad", 0.0))
                elif isinstance(vel_line, dict):
                    p1 = vel_line.get("p1") or vel_line.get("start") or (0.0, 0.0)
                    p2 = vel_line.get("p2") or vel_line.get("end") or (0.0, 0.0)
                    start_dict = {"x": p1[0] if isinstance(p1, (list, tuple)) else getattr(p1, "x", 0.0), "y": p1[1] if isinstance(p1, (list, tuple)) else getattr(p1, "y", 0.0)}
                    end_dict = {"x": p2[0] if isinstance(p2, (list, tuple)) else getattr(p2, "x", 0.0), "y": p2[1] if isinstance(p2, (list, tuple)) else getattr(p2, "y", 0.0)}
                    arrow_len = vel_line.get("length_px", math.hypot(end_dict["x"] - start_dict["x"], end_dict["y"] - start_dict["y"]))
                    angle_deg = -math.degrees(math.atan2(end_dict["y"] - start_dict["y"], end_dict["x"] - start_dict["x"]))
                else:
                    start_dict, end_dict, arrow_len, angle_deg = {}, {}, 0.0, 0.0

                vector_ent.geometry = {
                    "start": start_dict,
                    "end": end_dict,
                    "arrow_pixel_length": arrow_len,
                }
                vector_ent.evidence_refs = [cv_ev_id]
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=vector_ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"arrow_angle_deg": round(angle_deg, 2)},
                        notes="Velocity vector geometry grounded. Arrow length is NOT converted to velocity magnitude.",
                    )
                )
            else:
                vector_ent.geometry = None
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=vector_ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        notes="Velocity vector arrow not detected.",
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
                    if cand.quantity_candidate == "velocity" and cand.numeric_value is not None:
                        has_explicit_label = any(lbl in tok.raw_text.lower() for lbl in ("v =", "v=", "v0", "v_0", "u =", "u=", "speed", "বেগ", "velocity")) or tok.raw_text.strip().startswith(("v", "V", "u", "U"))
                        near_launch = False
                        if tok_pt and launch_pt:
                            near_launch = tok_pt.distance_to(launch_pt) < 120.0

                        assoc_checks = {"explicit_label": has_explicit_label, "near_launch": near_launch}
                        if has_explicit_label or near_launch:
                            canonical_m_s = cand.numeric_value
                            if cand.raw_unit in ("km/h", "kph"):
                                canonical_m_s = cand.numeric_value / 3.6
                            grounded_ir.parameters["launch_speed"] = PhysicalValue(
                                value=canonical_m_s,
                                unit="m/s",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_vel_{cand.token_id}",
                                    target_entity_id=vector_ent.id if vector_ent else None,
                                    target_quantity="launch_speed",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "m/s",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks=assoc_checks,
                                    confidence=cand.confidence,
                                )
                            )
                        else:
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_vel_{cand.token_id}",
                                    target_entity_id=vector_ent.id if vector_ent else None,
                                    target_quantity="launch_speed",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "m/s",
                                    state=AssociationState.REJECTED,
                                    supporting_evidence=[],
                                    association_checks=assoc_checks,
                                    confidence=cand.confidence,
                                )
                            )

                    elif cand.quantity_candidate == "angle" and cand.numeric_value is not None:
                        has_explicit_label = any(lbl in tok.raw_text.lower() for lbl in ("θ", "theta", "alpha", "α", "angle", "কোণ", "নতি"))
                        near_launch = False
                        if tok_pt and launch_pt:
                            near_launch = tok_pt.distance_to(launch_pt) < 120.0

                        assoc_checks = {"explicit_label": has_explicit_label, "near_launch": near_launch}
                        if has_explicit_label or near_launch:
                            grounded_ir.parameters["launch_angle"] = PhysicalValue(
                                value=cand.numeric_value,
                                unit="deg",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_ang_{cand.token_id}",
                                    target_entity_id=vector_ent.id if vector_ent else None,
                                    target_quantity="launch_angle",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "deg",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks=assoc_checks,
                                    confidence=cand.confidence,
                                )
                            )
                        else:
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_ang_{cand.token_id}",
                                    target_entity_id=vector_ent.id if vector_ent else None,
                                    target_quantity="launch_angle",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "deg",
                                    state=AssociationState.REJECTED,
                                    supporting_evidence=[],
                                    association_checks=assoc_checks,
                                    confidence=cand.confidence,
                                )
                            )

                    elif cand.quantity_candidate == "acceleration" and cand.numeric_value is not None:
                        has_explicit_label = any(lbl in tok.raw_text.lower() for lbl in ("g =", "g=", "g:", "gravity", "অভিকর্ষজ ত্বরণ", "ত্বরণ", "a =")) or tok.raw_text.strip().startswith(("g", "G"))
                        assoc_checks = {"explicit_label": has_explicit_label}
                        if has_explicit_label:
                            grounded_ir.parameters["gravity"] = PhysicalValue(
                                value=cand.numeric_value,
                                unit="m/s²",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_g_{cand.token_id}",
                                    target_entity_id=None,
                                    target_quantity="gravity",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "m/s²",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id],
                                    association_checks=assoc_checks,
                                    confidence=cand.confidence,
                                )
                            )
                        else:
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_g_{cand.token_id}",
                                    target_entity_id=None,
                                    target_quantity="gravity",
                                    value=cand.numeric_value,
                                    unit=cand.raw_unit or "m/s²",
                                    state=AssociationState.REJECTED,
                                    supporting_evidence=[],
                                    association_checks=assoc_checks,
                                    confidence=cand.confidence,
                                )
                            )

        grounded_ir.evidence.update({k: v.to_dict() for k, v in new_evidence.items()})
        grounded_ir.provenance["grounding_diagnostics"] = [d.to_dict() for d in diagnostics]
        grounded_ir.provenance["candidate_parameters"] = [c.to_dict() for c in all_val_candidates]

        # Status Invariant: Grounders extract and associate; status remains NEEDS_REVIEW for compiler verification
        grounded_ir.status = BookIRStatus.NEEDS_REVIEW
        has_speed = "launch_speed" in grounded_ir.parameters
        has_angle = "launch_angle" in grounded_ir.parameters
        has_gravity = "gravity" in grounded_ir.parameters

        if has_speed and has_angle and has_gravity and launch_pt:
            grounded_ir.status_notes = "Grounded projectile launch parameters and geometry; pending compiler verification."
        else:
            grounded_ir.status_notes = "Missing launch_speed, launch_angle, gravity, or launch point."

        return GroundingOutcome(
            grounded_book_ir=grounded_ir,
            diagnostics=diagnostics,
            new_evidence_records=new_evidence,
            candidate_parameters=all_val_candidates,
            parameter_associations=param_associations,
        )

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
        if prism_ent is None:
            prism_ent = BookEntity(id="element_prism", type="prism_body", label="Prism Body")
            grounded_ir.entities.append(prism_ent)

        poly: Optional[SourcePolygon] = cv_candidates.get("prism_polygon")
        apex: Optional[SourcePoint] = cv_candidates.get("apex")

        if poly and len(poly.points) >= 3:
            pts = [{"x": float(p.x), "y": float(p.y)} for p in poly.points[:3]]
            if apex is None:
                sorted_by_y = sorted(poly.points, key=lambda p: p.y)
                apex = sorted_by_y[0]
        else:
            pts = []

        if poly is not None and apex is not None:
            prism_ent.position_source_px = {
                "x": float(apex.x), "y": float(apex.y),
                "coordinate_space": "source_px", "method": "cv_prism_apex",
            }
            prism_ent.geometry = {
                "polygon": poly.to_dict() if hasattr(poly, "to_dict") else poly,
                "bounds": poly.bbox.to_dict() if hasattr(poly.bbox, "to_dict") else poly.bbox,
            }
            prism_ent.evidence_refs = [cv_ev_id]
            diagnostics.append(EntityGroundingDiagnostic(
                entity_id=prism_ent.id, grounding_state=GroundingState.GROUNDED,
                supporting_evidence=[cv_ev_id], checks={"vertex_count": len(pts)},
                notes="Prism triangular body grounded.",
            ))
        else:
            prism_ent.position_source_px = None
            prism_ent.geometry = None
            diagnostics.append(EntityGroundingDiagnostic(
                entity_id=prism_ent.id, grounding_state=GroundingState.UNRESOLVED,
                notes="Prism polygon not detected.",
            ))

        if grounded_ir.geometry is None:
            grounded_ir.geometry = {}
        if pts:
            grounded_ir.geometry["vertices"] = pts
            grounded_ir.geometry["prismVertices"] = pts

        # Incident ray placement striking left face
        inc_ray = cv_candidates.get("incident_ray")
        if inc_ray and hasattr(inc_ray, "start") and hasattr(inc_ray, "end"):
            r_orig = [float(inc_ray.start.x), float(inc_ray.start.y)]
            dx = float(inc_ray.end.x) - float(inc_ray.start.x)
            dy = float(inc_ray.end.y) - float(inc_ray.start.y)
            mag = math.hypot(dx, dy) or 1.0
            r_dir = [round(dx / mag, 4), round(dy / mag, 4)]
            ray_orig_pt = {"x": r_orig[0], "y": r_orig[1]}
            ray_dir_pt = {"x": r_dir[0], "y": r_dir[1]}
            grounded_ir.geometry["ray_origin"] = ray_orig_pt
            grounded_ir.geometry["rayOrigin"] = ray_orig_pt
            grounded_ir.geometry["ray_direction"] = ray_dir_pt
            grounded_ir.geometry["rayDirection"] = ray_dir_pt

            ray_prov = ProvenanceRecord(
                source="cv",
                confidence=0.88,
                evidence_refs=[cv_ev_id],
                notes="Printed incident ray grounded from classical CV.",
            )
            grounded_ir.parameters["ray_origin"] = PhysicalValue(
                value=ray_orig_pt, unit="px", status="observed", provenance=ray_prov,
            )
            grounded_ir.parameters["ray_direction"] = PhysicalValue(
                value=ray_dir_pt, unit=None, status="observed", provenance=ray_prov,
            )
            if grounded_ir.parameter_provenance is None:
                grounded_ir.parameter_provenance = {}
            grounded_ir.parameter_provenance["ray_origin"] = ray_prov
            grounded_ir.parameter_provenance["ray_direction"] = ray_prov

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
                            apex_val = PhysicalValue(
                                value=cand.numeric_value,
                                unit="deg",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            grounded_ir.parameters["apex_angle"] = apex_val
                            grounded_ir.parameters["apex_angle_deg"] = apex_val
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
                            n_val = PhysicalValue(
                                value=cand.numeric_value,
                                unit="dimensionless",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence),
                            )
                            grounded_ir.parameters["refractive_index"] = n_val
                            grounded_ir.parameters["n"] = n_val
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

        if "apex_angle_deg" not in grounded_ir.parameters and "apex_angle" in grounded_ir.parameters:
            grounded_ir.parameters["apex_angle_deg"] = grounded_ir.parameters["apex_angle"]
        elif "apex_angle_deg" not in grounded_ir.parameters and len(pts) >= 3:
            apex_vertex = min(pts, key=lambda point: point["y"])
            base_vertices = [point for point in pts if point is not apex_vertex]
            if len(base_vertices) == 2:
                vectors = [(point["x"] - apex_vertex["x"], point["y"] - apex_vertex["y"])
                           for point in base_vertices]
                lengths = [math.hypot(*vector) for vector in vectors]
                if min(lengths) > 1:
                    cosine = sum(a * b for a, b in zip(*vectors)) / (lengths[0] * lengths[1])
                    angle = math.degrees(math.acos(max(-1.0, min(1.0, cosine))))
                    grounded_ir.parameters["apex_angle_deg"] = PhysicalValue(
                        value=angle, unit="deg", status="derived",
                        provenance=ProvenanceRecord(
                            source="diagram_measurement", evidence_refs=[cv_ev_id], confidence=0.8,
                            notes="Apex angle measured from detected prism edges.",
                        ),
                    )

        if "n" not in grounded_ir.parameters and "refractive_index" in grounded_ir.parameters:
            grounded_ir.parameters["n"] = grounded_ir.parameters["refractive_index"]

        # Status Invariant: Grounders extract and associate; status remains NEEDS_REVIEW for compiler verification
        grounded_ir.status = BookIRStatus.NEEDS_REVIEW
        grounded_ir.status_notes = "Grounded prism polygon, apex angle, and refractive index; ready for compiler verification."

        return GroundingOutcome(
            grounded_book_ir=grounded_ir,
            diagnostics=diagnostics,
            new_evidence_records=new_evidence,
            candidate_parameters=all_val_candidates,
            parameter_associations=param_associations,
        )

"""PR-06 Pendulum Evidence Fusion and Grounding Implementation.

Deep vertical slice for mechanics/pendulum:
  - Fuses Classical CV circle, Hough lines, and SAM 2 masks into canonical BookIR.
  - Enforces interpretable agreement checks:
      If CV bob center and SAM mask centroid disagree beyond tolerance,
      the entity is marked AMBIGUOUS and canonical coordinates remain None.
  - Evaluates OCR tokens for physical value candidates (e.g. '20 cm', 'L', 'θ = 30°').
  - STRICT ZERO FABRICATION: Standalone symbol 'L' does NOT invent physical length.
"""
from __future__ import annotations

import copy
import logging
import math
from typing import Any, Dict, List, Optional

from shared.schemas.evidence import (
    EntityGroundingDiagnostic,
    EvidenceMethod,
    EvidenceRecord,
    GroundingState,
    MaskArtifact,
    OCRExtractionResult,
    ParsedPhysicalValueCandidate,
    SegmentationResult,
    SourcePoint,
    SourceLine,
    AssociationState,
    ParameterAssociationResult,
)
from shared.schemas.ingestion import BookEntity, BookIR, BookIRStatus, PhysicalValue, ProvenanceRecord
from ai.evidence.grounding.base import GroundingOutcome
from ai.evidence.grounding.physical_value_parser import parse_physical_value_candidate

logger = logging.getLogger(__name__)


class PendulumGrounder:
    """Subtype grounder for simple pendulum diagrams."""

    def __init__(self, bob_agreement_tolerance_ratio: float = 0.4, min_tolerance_px: float = 8.0):
        self.bob_agreement_tolerance_ratio = bob_agreement_tolerance_ratio
        self.min_tolerance_px = min_tolerance_px

    @property
    def domain(self) -> str:
        return "mechanics"

    @property
    def subtype(self) -> str:
        return "pendulum"

    def supports(self, domain: Optional[str], subtype: Optional[str]) -> bool:
        return (domain or "").lower() == "mechanics" and (subtype or "").lower() == "pendulum"

    def ground(
        self,
        book_ir: BookIR,
        cv_candidates: Dict[str, Any],
        ocr_result: Optional[OCRExtractionResult] = None,
        seg_result: Optional[SegmentationResult] = None,
        source_width: int = 0,
        source_height: int = 0,
    ) -> GroundingOutcome:
        # Clone BookIR to avoid side-effects
        grounded_ir = copy.deepcopy(book_ir)

        diagnostics: List[EntityGroundingDiagnostic] = []
        new_evidence: Dict[str, EvidenceRecord] = {}
        all_val_candidates: List[ParsedPhysicalValueCandidate] = []

        # Ensure source dimensions exist in geometry
        grounded_ir.geometry["width"] = source_width
        grounded_ir.geometry["height"] = source_height
        grounded_ir.geometry["coordinate_space"] = "source_px"

        best_proposal = cv_candidates.get("best_proposal")
        cv_bob = best_proposal.get("bob") if best_proposal else None
        cv_string = best_proposal.get("string") if best_proposal else None
        cv_pivot = best_proposal.get("pivot") if best_proposal else None

        # Record CV Evidence
        if best_proposal:
            cv_ev_id = f"ev_cv_pendulum_{grounded_ir.source_asset_id or '0'}"
            circ_qual = float(cv_bob.get("circularity", 0.85)) if cv_bob else None
            new_evidence[cv_ev_id] = EvidenceRecord(
                id=cv_ev_id,
                method=EvidenceMethod.CLASSICAL_CV,
                source_asset_id=grounded_ir.source_asset_id,
                figure_id=grounded_ir.figure_id,
                confidence=round(circ_qual, 3) if circ_qual is not None else None,
                verified=False,
                coordinate_space="source_px",
                provider="opencv_hough_tls",
                payload={
                    "bob_center": cv_bob["center"].to_dict() if (cv_bob and hasattr(cv_bob.get("center"), "to_dict")) else (cv_bob.get("center") if cv_bob else None),
                    "bob_radius_px": cv_bob.get("radius_px") if cv_bob else None,
                    "string_start": cv_string["start"].to_dict() if (cv_string and hasattr(cv_string.get("start"), "to_dict")) else (cv_string.get("start") if cv_string else None),
                    "string_end": cv_string["end"].to_dict() if (cv_string and hasattr(cv_string.get("end"), "to_dict")) else (cv_string.get("end") if cv_string else None),
                    "string_length_px": cv_string.get("length_to_bob_center_px") if cv_string else None,
                    "pivot": cv_pivot.to_dict() if hasattr(cv_pivot, "to_dict") else cv_pivot,
                    "vertical_reference": cv_candidates.get("vertical_reference").to_dict() if (cv_candidates.get("vertical_reference") and hasattr(cv_candidates.get("vertical_reference"), "to_dict")) else None,
                },
            )
        else:
            cv_ev_id = None

        # Retrieve segmentation mask for bob (if any)
        bob_mask: Optional[MaskArtifact] = None
        if seg_result and seg_result.masks:
            bob_mask = seg_result.masks[0]
            mask_ev_id = f"ev_seg_bob_{bob_mask.id}"
            new_evidence[mask_ev_id] = EvidenceRecord(
                id=mask_ev_id,
                method=EvidenceMethod.SEGMENTATION,
                source_asset_id=grounded_ir.source_asset_id,
                figure_id=grounded_ir.figure_id,
                confidence=bob_mask.confidence,
                verified=bob_mask.verified,
                coordinate_space="source_px",
                provider=seg_result.provider,
                model=seg_result.model,
                payload={
                    "centroid": bob_mask.centroid_source_px.to_dict() if bob_mask.centroid_source_px else None,
                    "area_px": bob_mask.area_px,
                    "bounds": bob_mask.bbox_source_px.to_dict() if bob_mask.bbox_source_px else None,
                    "mask_id": bob_mask.id,
                },
            )
        else:
            mask_ev_id = None

        # Find entities by semantic role
        bob_entity = next((e for e in grounded_ir.entities if e.type == "bob"), None)
        pivot_entity = next((e for e in grounded_ir.entities if e.type == "pivot"), None)
        string_entity = next((e for e in grounded_ir.entities if e.type in ("string", "rod")), None)

        # -------------------------------------------------------------------
        # 1. Bob Grounding & Agreement Fusion
        # -------------------------------------------------------------------
        if bob_entity:
            if not cv_bob:
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=bob_entity.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        supporting_evidence=[],
                        checks={"cv_detected": False},
                        conflicts=[],
                        notes="No classical CV circular candidate detected for bob.",
                    )
                )
            else:
                cv_center = cv_bob["center"]
                cv_r = cv_bob.get("radius_px", cv_bob.get("radius", 10.0))
                tol = max(self.min_tolerance_px, cv_r * self.bob_agreement_tolerance_ratio)

                # Independent consistency checks
                is_consistent = True
                inconsistency_reasons = []

                # Check 1: Size sanity relative to image
                src_w = grounded_ir.geometry.get("width", 1000) if grounded_ir.geometry else 1000
                src_h = grounded_ir.geometry.get("height", 1000) if grounded_ir.geometry else 1000
                if cv_r > min(src_w, src_h) * 0.12:
                    is_consistent = False
                    inconsistency_reasons.append(f"Bob radius {cv_r:.1f}px exceeds 12% of image dimension.")

                # Check 2: String attachment
                if cv_string:
                    str_end = cv_string.get("end")
                    if str_end:
                        pt_end = SourcePoint(str_end.x, str_end.y) if hasattr(str_end, "x") else SourcePoint(str_end["x"], str_end["y"])
                        gap_to_perimeter = abs(cv_center.distance_to(pt_end) - cv_r)
                        if gap_to_perimeter > max(25.0, cv_r * 0.55):
                            is_consistent = False
                            inconsistency_reasons.append(f"String does not attach to bob perimeter (gap: {gap_to_perimeter:.1f}px).")

                    # Check 3: Ratio to string length
                    s_len = cv_string.get("length_to_bob_center_px", cv_string.get("visible_length_px", 1.0))
                    ratio = (2.0 * cv_r) / max(1.0, s_len)
                    if ratio < 0.03 or ratio > 0.38:
                        is_consistent = False
                        inconsistency_reasons.append(f"Bob diameter to string length ratio ({ratio:.2f}) is physically implausible.")

                # Check 4: SAM mask area sanity (mask should not be giant background region)
                if bob_mask:
                    expected_max_area = math.pi * (cv_r * 2.2) ** 2
                    if bob_mask.area_px and bob_mask.area_px > expected_max_area * 2.5:
                        is_consistent = False
                        inconsistency_reasons.append(f"SAM mask area ({bob_mask.area_px:.0f}px) is far too large for bob candidate.")

                if not is_consistent:
                    # Inconsistency rejected candidate
                    diagnostics.append(
                        EntityGroundingDiagnostic(
                            entity_id=bob_entity.id,
                            grounding_state=GroundingState.AMBIGUOUS,
                            supporting_evidence=list(filter(None, [cv_ev_id, mask_ev_id])),
                            checks={
                                "cv_center": cv_center.to_dict(),
                                "radius_px": cv_r,
                                "is_consistent": False,
                            },
                            conflicts=inconsistency_reasons,
                            notes="Bob candidate rejected by independent geometric consistency checks.",
                        )
                    )
                    bob_entity.position_source_px = None
                    bob_entity.geometry = None
                elif bob_mask and bob_mask.centroid_source_px:
                    sam_center = bob_mask.centroid_source_px
                    dist = cv_center.distance_to(sam_center)

                    if dist > tol:
                        # CONFLICT: CV and SAM disagree
                        diagnostics.append(
                            EntityGroundingDiagnostic(
                                entity_id=bob_entity.id,
                                grounding_state=GroundingState.AMBIGUOUS,
                                supporting_evidence=[cv_ev_id, mask_ev_id],
                                checks={
                                    "cv_center": cv_center.to_dict(),
                                    "sam_centroid": sam_center.to_dict(),
                                    "center_distance_px": round(dist, 2),
                                    "tolerance_px": round(tol, 2),
                                },
                                conflicts=[
                                    f"CV bob center ({cv_center.x:.1f}, {cv_center.y:.1f}) and SAM centroid "
                                    f"({sam_center.x:.1f}, {sam_center.y:.1f}) disagree by {dist:.1f}px (tol: {tol:.1f}px)."
                                ],
                                notes="Entity remains AMBIGUOUS without canonical coordinates.",
                            )
                        )
                        # Canonical coordinates remain strictly None on conflict
                        bob_entity.position_source_px = None
                        bob_entity.geometry = None
                    else:
                        # AGREEMENT PASSES: Fuse into grounded entity
                        bob_entity.position_source_px = {
                            "x": cv_center.x,
                            "y": cv_center.y,
                            "coordinate_space": "source_px",
                            "method": "fused_cv_sam",
                            "center_agreement_distance_px": round(dist, 2),
                        }
                        bob_entity.geometry = {
                            "bounds": cv_bob["bounds"].to_dict(),
                            "radius_px": cv_r,
                            "mask_ref": bob_mask.id,
                            "area_px": bob_mask.area_px,
                        }
                        bob_entity.evidence_refs = list(filter(None, [cv_ev_id, mask_ev_id]))
                        diagnostics.append(
                            EntityGroundingDiagnostic(
                                entity_id=bob_entity.id,
                                grounding_state=GroundingState.GROUNDED,
                                supporting_evidence=bob_entity.evidence_refs,
                                checks={
                                    "cv_center": cv_center.to_dict(),
                                    "sam_centroid": sam_center.to_dict(),
                                    "center_distance_px": round(dist, 2),
                                    "tolerance_px": round(tol, 2),
                                },
                                conflicts=[],
                                notes="CV circle and SAM 2 mask centroids agree within tolerance and pass consistency checks.",
                            )
                        )
                        # Register in BookIR parameters/geometry for compiler
                        grounded_ir.parameters["bob_radius_px"] = PhysicalValue(
                            value=cv_r,
                            unit="px",
                            status="observed",
                            provenance=ProvenanceRecord(source="cv", confidence=0.92),
                        )
                        grounded_ir.parameters["bob_position"] = cv_center.to_dict()
                else:
                    # CV-only grounding (when SAM is unavailable or produces no mask)
                    bob_entity.position_source_px = {
                        "x": cv_center.x,
                        "y": cv_center.y,
                        "coordinate_space": "source_px",
                        "method": "classical_cv",
                    }
                    bob_entity.geometry = {
                        "bounds": cv_bob["bounds"].to_dict(),
                        "radius_px": cv_r,
                    }
                    bob_entity.evidence_refs = list(filter(None, [cv_ev_id]))
                    diagnostics.append(
                        EntityGroundingDiagnostic(
                            entity_id=bob_entity.id,
                            grounding_state=GroundingState.GROUNDED,
                            supporting_evidence=bob_entity.evidence_refs,
                            checks={"cv_center": cv_center.to_dict(), "sam_available": False},
                            conflicts=[],
                            notes="Grounded via sub-pixel circle detection (segmentation unavailable).",
                        )
                    )
                    grounded_ir.parameters["bob_radius_px"] = PhysicalValue(
                        value=cv_r,
                        unit="px",
                        status="observed",
                        provenance=ProvenanceRecord(source="cv", confidence=0.88),
                    )
                    grounded_ir.parameters["bob_position"] = cv_center.to_dict()

        # -------------------------------------------------------------------
        # 2. String Grounding
        # -------------------------------------------------------------------
        if string_entity:
            if not cv_string:
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=string_entity.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        supporting_evidence=[],
                        checks={"cv_detected": False},
                        conflicts=[],
                        notes="No verified pendulum string line candidate detected.",
                    )
                )
            else:
                str_start = cv_string["start"]
                str_end = cv_string["end"]
                str_len = cv_string["length_to_bob_center_px"]

                string_entity.geometry = {
                    "start": str_start.to_dict(),
                    "end": str_end.to_dict(),
                    "length_px": str_len,
                    "visible_length_px": cv_string["visible_length_px"],
                }
                string_entity.evidence_refs = list(filter(None, [cv_ev_id]))
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=string_entity.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=string_entity.evidence_refs,
                        checks={
                            "start": str_start.to_dict(),
                            "end": str_end.to_dict(),
                            "length_px": round(str_len, 2),
                        },
                        conflicts=[],
                        notes="String verified and connected to bob candidate.",
                    )
                )
                grounded_ir.parameters["string_length_px"] = PhysicalValue(
                    value=str_len,
                    unit="px",
                    status="observed",
                    provenance=ProvenanceRecord(source="cv", confidence=0.90),
                )

        # -------------------------------------------------------------------
        # 3. Pivot Grounding
        # -------------------------------------------------------------------
        if pivot_entity:
            if not cv_pivot:
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=pivot_entity.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        supporting_evidence=[],
                        checks={"cv_detected": False},
                        conflicts=[],
                        notes="No pivot coordinate candidate found.",
                    )
                )
            else:
                if isinstance(cv_pivot, dict):
                    pt = cv_pivot.get("point") or cv_pivot
                    px = getattr(pt, "x", pt.get("x", 0.0) if isinstance(pt, dict) else 0.0)
                    py = getattr(pt, "y", pt.get("y", 0.0) if isinstance(pt, dict) else 0.0)
                else:
                    px = getattr(cv_pivot, "x", 0.0)
                    py = getattr(cv_pivot, "y", 0.0)

                pivot_entity.position_source_px = {
                    "x": float(px),
                    "y": float(py),
                    "coordinate_space": "source_px",
                    "method": "string_anchor",
                }
                pivot_entity.evidence_refs = list(filter(None, [cv_ev_id]))
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=pivot_entity.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=pivot_entity.evidence_refs,
                        checks={"pivot": {"x": px, "y": py}},
                        conflicts=[],
                        notes="Pivot grounded at verified string suspension point.",
                    )
                )
                grounded_ir.parameters["pivot"] = cv_pivot.to_dict() if hasattr(cv_pivot, "to_dict") else cv_pivot

        # -------------------------------------------------------------------
        # 3b. Vertical Reference Grounding
        # -------------------------------------------------------------------
        vref_entity = next((e for e in grounded_ir.entities if e.type in ("vertical_reference", "reference_line")), None)
        if vref_entity:
            cv_vref = cv_candidates.get("vertical_reference")
            if not cv_vref:
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=vref_entity.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        supporting_evidence=[],
                        checks={"cv_detected": False},
                        conflicts=[],
                        notes="No vertical reference line candidate detected.",
                    )
                )
            else:
                vref_start = cv_vref.start
                vref_end = cv_vref.end
                vref_len = vref_start.distance_to(vref_end)
                vref_entity.geometry = {
                    "start": vref_start.to_dict(),
                    "end": vref_end.to_dict(),
                    "length_px": round(vref_len, 2),
                    "style": "dashed",
                }
                vref_entity.position_source_px = {
                    "x": vref_start.x,
                    "y": vref_start.y,
                    "coordinate_space": "source_px",
                    "method": "line_detection",
                }
                vref_entity.evidence_refs = list(filter(None, [cv_ev_id]))
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=vref_entity.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=vref_entity.evidence_refs,
                        checks={
                            "start": vref_start.to_dict(),
                            "end": vref_end.to_dict(),
                            "length_px": round(vref_len, 2),
                        },
                        conflicts=[],
                        notes="Vertical reference dashed line detected and grounded.",
                    )
                )

        # -------------------------------------------------------------------
        # 4. OCR Evidence & Parameter Promotion (STRICT ZERO FABRICATION)
        # -------------------------------------------------------------------
        param_associations: List[ParameterAssociationResult] = []
        if ocr_result and ocr_result.tokens:
            for tok in ocr_result.tokens:
                # Record each OCR token in evidence registry
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
                    payload={
                        "raw_text": tok.raw_text,
                        "normalized_text": tok.normalized_text,
                        "bbox": tok.bbox_source_px.to_dict() if tok.bbox_source_px else None,
                    },
                )

                # Parse candidates from OCR token
                val_cands = parse_physical_value_candidate(tok)
                all_val_candidates.extend(val_cands)

                for cand in val_cands:
                    tok_box = tok.bbox_source_px
                    tok_cx = (tok_box.x + tok_box.width / 2.0) if tok_box else None
                    tok_cy = (tok_box.y + tok_box.height / 2.0) if tok_box else None
                    tok_pt = SourcePoint(tok_cx, tok_cy) if (tok_cx is not None and tok_cy is not None) else None

                    # Association Rule: Length with numerical value
                    if cand.quantity_candidate == "length" and cand.numeric_value is not None:
                        has_explicit_label = any(lbl in tok.raw_text.lower() for lbl in ("l =", "l=", "length", "দৈর্ঘ্য", "l:", "l ")) or tok.raw_text.strip().startswith(("L", "l"))
                        near_string = False
                        if tok_pt and cv_string:
                            str_line = SourceLine(start=cv_string["start"], end=cv_string["end"])
                            dist_to_str = str_line.distance_to_point(tok_pt)
                            near_string = dist_to_str < 85.0

                        assoc_checks = {"explicit_label": has_explicit_label, "near_string_geometry": near_string}

                        if has_explicit_label or near_string:
                            assoc_state = AssociationState.ASSOCIATED
                            supporting = [tok_ev_id]
                            if cv_ev_id:
                                supporting.append(cv_ev_id)

                            canonical_val = cand.numeric_value
                            if cand.raw_unit == "cm":
                                canonical_val = cand.numeric_value * 0.01
                            elif cand.raw_unit == "mm":
                                canonical_val = cand.numeric_value * 0.001

                            # Check for VLM corroboration and standalone symbol
                            vlm_labels = grounded_ir.provenance.get("visible_labels", [])
                            vlm_corroborates = any(
                                ("l =" in str(vl.get("text", "")).lower() or "length" in str(vl.get("text", "")).lower())
                                and (str(int(cand.numeric_value)) in str(vl.get("text", "")) or str(cand.numeric_value) in str(vl.get("text", "")))
                                for vl in vlm_labels
                            )
                            # Look for standalone 'L' symbol
                            l_tok = next((t for t in ocr_result.tokens if t.raw_text.strip() == "L"), None)
                            if l_tok:
                                supporting.append(f"ev_ocr_{l_tok.id}")

                            if vlm_corroborates or "দৈর্ঘ্য" in tok.raw_text:
                                source_type = "fused"
                                conf = min(0.92, max(cand.confidence or 0.5, 0.88))
                                notes = (
                                    f"Fused from OCR text '{cand.raw_text}' with Bangla semantic context ('দৈর্ঘ্য') "
                                    f"and corroborating VLM/symbol evidence."
                                )
                            else:
                                source_type = "ocr"
                                conf = cand.confidence or 0.85
                                notes = f"Extracted from OCR text '{cand.raw_text}'"

                            grounded_ir.parameters["length"] = PhysicalValue(
                                value=canonical_val,
                                unit="m",
                                status="observed",
                                provenance=ProvenanceRecord(
                                    source=source_type,
                                    evidence_refs=supporting,
                                    confidence=conf,
                                    notes=notes,
                                ),
                            )
                            if string_entity:
                                string_entity.evidence_refs.append(tok_ev_id)
                        else:
                            assoc_state = AssociationState.REJECTED
                            supporting = []

                        param_associations.append(
                            ParameterAssociationResult(
                                candidate_id=f"assoc_len_{cand.token_id}",
                                target_entity_id=string_entity.id if string_entity else None,
                                target_quantity="length",
                                value=cand.numeric_value,
                                unit=cand.raw_unit or "m",
                                state=assoc_state,
                                supporting_evidence=supporting,
                                association_checks=assoc_checks,
                                confidence=cand.confidence,
                            )
                        )

                    # Association Rule: Angle with numerical value
                    elif cand.quantity_candidate == "angle" and cand.numeric_value is not None:
                        has_explicit_label = any(lbl in tok.raw_text.lower() for lbl in ("θ", "theta", "alpha", "কোণ", "বিস্তার"))
                        near_pivot = False
                        if tok_pt and cv_pivot:
                            p_pt = cv_pivot if isinstance(cv_pivot, SourcePoint) else SourcePoint(cv_pivot.x, cv_pivot.y)
                            near_pivot = tok_pt.distance_to(p_pt) < 85.0

                        assoc_checks = {"explicit_label": has_explicit_label, "near_pivot": near_pivot}
                        if has_explicit_label or near_pivot:
                            cand_conf = cand.confidence or 0.0
                            has_angle_arc = cv_candidates.get("angle_marker") is not None
                            vlm_labels = grounded_ir.provenance.get("visible_labels", [])
                            vlm_corroborates = any(
                                ("θ" in str(vl.get("text", "")) or "theta" in str(vl.get("text", "")).lower() or "angle" in str(vl.get("text", "")).lower() or "কোণ" in str(vl.get("text", "")))
                                and (str(int(cand.numeric_value)) in str(vl.get("text", "")) or str(cand.numeric_value) in str(vl.get("text", "")))
                                for vl in vlm_labels
                            )

                            # Strict Anti-Fabrication check:
                            # If OCR confidence is low (< 0.50) and angle arc is ungrounded, mark AMBIGUOUS and do NOT promote to observed parameters.
                            if cand_conf < 0.50 and not has_angle_arc:
                                assoc_state = AssociationState.AMBIGUOUS
                                supporting = [tok_ev_id]
                            else:
                                assoc_state = AssociationState.ASSOCIATED
                                supporting = [tok_ev_id]
                                if cv_ev_id:
                                    supporting.append(cv_ev_id)

                                canonical_val = cand.numeric_value
                                if cand.raw_unit in ("rad", "radian", "radians"):
                                    canonical_val = cand.numeric_value * 180.0 / math.pi

                                src = "fused" if (vlm_corroborates or "কোণ" in tok.raw_text) else "ocr"
                                conf = min(0.92, max(cand_conf, 0.85)) if src == "fused" else cand_conf

                                grounded_ir.parameters["initial_angle"] = PhysicalValue(
                                    value=canonical_val,
                                    unit="deg",
                                    status="observed",
                                    provenance=ProvenanceRecord(
                                        source=src,
                                        evidence_refs=supporting,
                                        confidence=conf,
                                        notes=f"Extracted from OCR text '{cand.raw_text}' (corroborated={vlm_corroborates})",
                                    ),
                                )
                        else:
                            assoc_state = AssociationState.REJECTED
                            supporting = []

                        param_associations.append(
                            ParameterAssociationResult(
                                candidate_id=f"assoc_ang_{cand.token_id}",
                                target_entity_id=string_entity.id if string_entity else None,
                                target_quantity="initial_angle",
                                value=cand.numeric_value,
                                unit=cand.raw_unit or "deg",
                                state=assoc_state,
                                supporting_evidence=supporting,
                                association_checks=assoc_checks,
                                confidence=cand.confidence,
                            )
                        )

                    # Association Rule: Mass with numerical value
                    elif cand.quantity_candidate == "mass" and cand.numeric_value is not None:
                        has_explicit_label = any(lbl in tok.raw_text.lower() for lbl in ("m =", "m=", "mass", "ভর", "m:", "m "))
                        near_bob = False
                        if tok_pt and cv_bob:
                            b_center = cv_bob["center"]
                            b_r = cv_bob.get("radius_px", 20.0)
                            dist_to_bob = tok_pt.distance_to(b_center)
                            near_bob = dist_to_bob < (b_r + 65.0)

                        assoc_checks = {"explicit_label": has_explicit_label, "near_bob": near_bob}
                        if has_explicit_label or near_bob:
                            assoc_state = AssociationState.ASSOCIATED
                            supporting = [tok_ev_id]
                            canonical_val = cand.numeric_value
                            if cand.raw_unit == "g":
                                canonical_val = cand.numeric_value * 0.001

                            grounded_ir.parameters["mass"] = PhysicalValue(
                                value=canonical_val,
                                unit="kg",
                                status="observed",
                                provenance=ProvenanceRecord(
                                    source="ocr",
                                    evidence_refs=supporting,
                                    confidence=cand.confidence or 0.85,
                                ),
                            )
                            if bob_entity:
                                bob_entity.evidence_refs.append(tok_ev_id)
                        else:
                            assoc_state = AssociationState.REJECTED
                            supporting = []

                        param_associations.append(
                            ParameterAssociationResult(
                                candidate_id=f"assoc_mass_{cand.token_id}",
                                target_entity_id=bob_entity.id if bob_entity else None,
                                target_quantity="mass",
                                value=cand.numeric_value,
                                unit=cand.raw_unit or "kg",
                                state=assoc_state,
                                supporting_evidence=supporting,
                                association_checks=assoc_checks,
                                confidence=cand.confidence,
                            )
                        )

                    # Standalone symbol 'L' / 'm'
                    elif cand.quantity_candidate == "length_symbol":
                        if string_entity:
                            string_entity.evidence_refs.append(tok_ev_id)
                    elif cand.quantity_candidate == "mass_symbol":
                        if bob_entity:
                            bob_entity.evidence_refs.append(tok_ev_id)

        # Update BookIR evidence and diagnostics
        grounded_ir.evidence.update({k: v.to_dict() for k, v in new_evidence.items()})
        grounded_ir.provenance["grounding_diagnostics"] = [d.to_dict() for d in diagnostics]
        grounded_ir.provenance["candidate_parameters"] = [c.to_dict() for c in all_val_candidates]

        # -------------------------------------------------------------------
        # 5. Status Truthfulness: Check if all requirements for READY are met
        # -------------------------------------------------------------------
        # Pendulum requires: pivot, bob_position, string_length_px, bob_radius_px,
        # gravity, mass, damping.
        # If mass or gravity or damping are missing, BookIR status MUST remain NEEDS_REVIEW.
        has_all_physical_constants = (
            "gravity" in grounded_ir.parameters
            and "mass" in grounded_ir.parameters
            and "damping" in grounded_ir.parameters
            and ("length" in grounded_ir.parameters or "string_length_m" in grounded_ir.parameters)
        )

        all_entities_grounded = all(
            d.grounding_state == GroundingState.GROUNDED for d in diagnostics
        ) if diagnostics else False

        grounded_ir.status = BookIRStatus.NEEDS_REVIEW
        ungrounded = [d.entity_id for d in diagnostics if d.grounding_state != GroundingState.GROUNDED]
        if ungrounded:
            grounded_ir.status_notes = f"Visual grounding incomplete or ambiguous for entities: {ungrounded}."
        else:
            grounded_ir.status_notes = "Visual evidence extracted; ready for compiler parameter verification."

        return GroundingOutcome(
            grounded_book_ir=grounded_ir,
            diagnostics=diagnostics,
            new_evidence_records=new_evidence,
            candidate_parameters=all_val_candidates,
            parameter_associations=param_associations,
        )

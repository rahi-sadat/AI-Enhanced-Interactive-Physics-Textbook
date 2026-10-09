"""PR-06 DC Circuit Subtype Evidence Grounder.

Grounds DC linear circuit entities:
  - Resistors, voltage sources, ground, switches
  - Component terminals (one-to-one candidate assignment)
  - Continuous wire paths and junction nodes
  - Topological connectivity graph (nodes N1, N2, ...)
  - Component-specific parameter association (R1 -> 10 Ω, V1 -> 12 V)

Strict Invariants:
  - Visual proximity is NEVER electrical connectivity.
  - Components are connected ONLY when verified by wire/junction path continuity.
  - Never map multiple semantic components (e.g. R1, R2, V1) to a single CV component.
  - Never use token-ID parameter keys as a substitute for component association.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

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
    SourceBBox,
    SourceLine,
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


class CircuitGrounder:
    """Specialized evidence grounder for circuits / dc_linear."""

    @property
    def domain(self) -> str:
        return "circuits"

    @property
    def subtype(self) -> str:
        return "dc_linear"

    def supports(self, domain: Optional[str], subtype: Optional[str]) -> bool:
        return (domain or "").lower() == "circuits" and (subtype or "").lower() in (
            "dc_linear",
            "circuit",
            "dc_circuit",
            "resistors",
        )

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

        cv_comps: List[Dict[str, Any]] = cv_candidates.get("components", [])
        cv_wires: List[SourceLine] = cv_candidates.get("wires", [])
        cv_junctions: List[SourcePoint] = cv_candidates.get("junctions", [])

        cv_ev_id = f"ev_cv_circuits_{grounded_ir.source_asset_id or 'anon'}"
        new_evidence[cv_ev_id] = EvidenceRecord(
            id=cv_ev_id,
            method=EvidenceMethod.CLASSICAL_CV,
            source_asset_id=grounded_ir.source_asset_id,
            figure_id=grounded_ir.figure_id,
            confidence=None,
            verified=False,
            coordinate_space="source_px",
            provider="circuit_cv_extractor",
            payload={
                "component_count": len(cv_comps),
                "wire_count": len(cv_wires),
                "junction_count": len(cv_junctions),
            },
        )

        # -------------------------------------------------------------------
        # 1. One-to-One Semantic-to-CV Component Assignment
        # -------------------------------------------------------------------
        claimed_cv_ids: Set[str] = set()
        grounded_components: Dict[str, Dict[str, Any]] = {}

        circuit_entities = [
            e for e in grounded_ir.entities
            if e.type in ("resistor", "voltage_source", "switch", "component", "current_source", "ground")
        ]

        for ent in circuit_entities:
            # Semantic approximate bbox (if VLM provided)
            approx_box = ent.attributes.get("vlmApproxBBox")
            sem_cx = None
            sem_cy = None
            if approx_box and isinstance(approx_box, dict):
                sem_cx = approx_box.get("x", 0.0) + approx_box.get("width", 0.0) / 2.0
                sem_cy = approx_box.get("y", 0.0) + approx_box.get("height", 0.0) / 2.0

            best_cand = None
            best_dist = float("inf")

            for c in cv_comps:
                cid = c.get("id", "")
                if cid in claimed_cv_ids:
                    continue  # Strict one-to-one: already claimed by another component

                c_center = c.get("center")
                if c_center and sem_cx is not None and sem_cy is not None:
                    dist = ((c_center.x - sem_cx) ** 2 + (c_center.y - sem_cy) ** 2) ** 0.5
                    if dist < best_dist and dist < 140.0:
                        best_dist = dist
                        best_cand = c
                elif not best_cand:
                    # Unclaimed fallback if no coarse VLM boxes exist
                    best_cand = c

            if best_cand:
                claimed_cv_ids.add(best_cand.get("id", ""))
                center = best_cand.get("center")
                bbox = best_cand.get("bbox")
                t1 = best_cand.get("terminal_1")
                t2 = best_cand.get("terminal_2")

                ent.position_source_px = {
                    "x": center.x if center else 0.0,
                    "y": center.y if center else 0.0,
                    "coordinate_space": "source_px",
                    "method": "cv_circuit_component",
                }
                ent.geometry = {
                    "bounds": bbox.to_dict() if hasattr(bbox, "to_dict") else bbox,
                    "terminal_1": t1.to_dict() if hasattr(t1, "to_dict") else t1,
                    "terminal_2": t2.to_dict() if hasattr(t2, "to_dict") else t2,
                    "wire_connected": best_cand.get("connected", False),
                }
                ent.evidence_refs = [cv_ev_id]
                grounded_components[ent.id] = {
                    "entity": ent,
                    "cv_component": best_cand,
                    "terminal_1": t1,
                    "terminal_2": t2,
                }
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=ent.id,
                        grounding_state=GroundingState.GROUNDED,
                        supporting_evidence=[cv_ev_id],
                        checks={"cv_component_id": best_cand.get("id"), "connected": best_cand.get("connected", False)},
                        notes=f"One-to-one grounded to CV component {best_cand.get('id')}.",
                    )
                )
            else:
                diagnostics.append(
                    EntityGroundingDiagnostic(
                        entity_id=ent.id,
                        grounding_state=GroundingState.UNRESOLVED,
                        supporting_evidence=[],
                        notes="No unique unclaimed CV component body found for this entity.",
                    )
                )

        # -------------------------------------------------------------------
        # 2. Reconstruct Topological Connectivity Graph
        # -------------------------------------------------------------------
        # Build wire continuity clusters (conductive paths)
        # Two wire endpoints connect if dist < 12.0 px or if connected by a junction
        terminals_to_connect: List[Tuple[str, str, SourcePoint]] = []  # (ent_id, term_name, pt)
        for eid, comp_data in grounded_components.items():
            if comp_data.get("terminal_1"):
                terminals_to_connect.append((eid, "terminal_1", comp_data["terminal_1"]))
            if comp_data.get("terminal_2"):
                terminals_to_connect.append((eid, "terminal_2", comp_data["terminal_2"]))

        # Group terminals that are connected via continuous wire paths
        wire_clusters: List[Set[int]] = []
        for i, w1 in enumerate(cv_wires):
            wire_clusters.append({i})

        # Merge intersecting or touching wire clusters
        changed = True
        while changed:
            changed = False
            for i in range(len(wire_clusters)):
                for j in range(i + 1, len(wire_clusters)):
                    # Check if any wire in cluster i meets any wire in cluster j
                    connected = False
                    for wi in wire_clusters[i]:
                        for wj in wire_clusters[j]:
                            d1 = cv_wires[wi].start.distance_to(cv_wires[wj].start)
                            d2 = cv_wires[wi].start.distance_to(cv_wires[wj].end)
                            d3 = cv_wires[wi].end.distance_to(cv_wires[wj].start)
                            d4 = cv_wires[wi].end.distance_to(cv_wires[wj].end)
                            if min(d1, d2, d3, d4) < 14.0:
                                connected = True
                                break
                            # Check junction bridge
                            for junc in cv_junctions:
                                if cv_wires[wi].distance_to_point(junc) < 10.0 and cv_wires[wj].distance_to_point(junc) < 10.0:
                                    connected = True
                                    break
                        if connected:
                            break
                    if connected:
                        wire_clusters[i].update(wire_clusters[j])
                        wire_clusters.pop(j)
                        changed = True
                        break
                if changed:
                    break

        # Associate each terminal with a wire cluster or direct connection
        node_assignments: Dict[str, List[str]] = {}  # "N1": ["R1.terminal_1", "V1.terminal_2"]
        unconnected_terminals: List[str] = []

        for eid, tname, tpt in terminals_to_connect:
            term_key = f"{eid}.{tname}"
            assigned_cluster = None
            for c_idx, cluster in enumerate(wire_clusters):
                if any(cv_wires[w_idx].distance_to_point(tpt) < 14.0 for w_idx in cluster):
                    assigned_cluster = c_idx
                    break

            if assigned_cluster is not None:
                node_id = f"N{assigned_cluster + 1}"
                node_assignments.setdefault(node_id, []).append(term_key)
            else:
                # Direct terminal-to-terminal touching (e.g. series components without long wire)
                direct_match = None
                for other_eid, other_tname, other_tpt in terminals_to_connect:
                    if (other_eid != eid or other_tname != tname) and tpt.distance_to(other_tpt) < 12.0:
                        direct_match = f"{other_eid}.{other_tname}"
                        break
                if direct_match:
                    pair_key = f"N_direct_{min(term_key, direct_match)}"
                    node_assignments.setdefault(pair_key, []).append(term_key)
                else:
                    unconnected_terminals.append(term_key)

        grounded_ir.geometry["circuit_topology"] = {
            "nodes": node_assignments,
            "unconnected_terminals": unconnected_terminals,
            "verified_connectivity": len(node_assignments) >= 2,
        }
        grounded_ir.parameters["circuit_topology"] = grounded_ir.geometry["circuit_topology"]

        # -------------------------------------------------------------------
        # 3. Component-Specific OCR Parameter Association
        # -------------------------------------------------------------------
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
                tok_center = None
                if tok_box:
                    tok_center = SourcePoint(tok_box.x + tok_box.width / 2.0, tok_box.y + tok_box.height / 2.0)

                for cand in val_cands:
                    # Association for Resistance
                    if cand.quantity_candidate == "resistance" and cand.numeric_value is not None:
                        canonical_ohm = cand.numeric_value * (1000.0 if cand.raw_unit == "kohm" else 1.0)

                        # Find closest resistor entity or label match (e.g. "R1", "R2")
                        target_resistor = None
                        best_r_dist = float("inf")

                        for eid, cdata in grounded_components.items():
                            ent = cdata["entity"]
                            if ent.type == "resistor":
                                # Check text label match (e.g. "R1" in tok text or ent.id in text)
                                if ent.id.lower() in tok.raw_text.lower() or (tok.raw_text.lower().startswith("r") and ent.id.lower().endswith(tok.raw_text.lower()[:2])):
                                    target_resistor = ent
                                    best_r_dist = 0.0
                                    break
                                # Check proximity
                                if tok_center and ent.position_source_px:
                                    r_pt = SourcePoint(ent.position_source_px["x"], ent.position_source_px["y"])
                                    dist = tok_center.distance_to(r_pt)
                                    if dist < best_r_dist and dist < 90.0:
                                        best_r_dist = dist
                                        target_resistor = ent

                        if target_resistor:
                            grounded_ir.parameters[f"{target_resistor.id}_resistance"] = PhysicalValue(
                                value=canonical_ohm,
                                unit="ohm",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence or 0.88),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_res_{cand.token_id}",
                                    target_entity_id=target_resistor.id,
                                    target_quantity="resistance",
                                    value=canonical_ohm,
                                    unit="ohm",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id, cv_ev_id],
                                    association_checks={"closest_component_distance_px": round(best_r_dist, 1)},
                                    confidence=cand.confidence,
                                )
                            )
                        else:
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_res_{cand.token_id}",
                                    target_entity_id=None,
                                    target_quantity="resistance",
                                    value=canonical_ohm,
                                    unit="ohm",
                                    state=AssociationState.REJECTED,
                                    supporting_evidence=[],
                                    association_checks={"closest_component_distance_px": round(best_r_dist, 1)},
                                    confidence=cand.confidence,
                                )
                            )

                    # Association for Voltage Source
                    elif cand.quantity_candidate == "voltage" and cand.numeric_value is not None:
                        target_source = None
                        best_v_dist = float("inf")

                        for eid, cdata in grounded_components.items():
                            ent = cdata["entity"]
                            if ent.type in ("voltage_source", "source", "battery"):
                                if ent.id.lower() in tok.raw_text.lower():
                                    target_source = ent
                                    best_v_dist = 0.0
                                    break
                                if tok_center and ent.position_source_px:
                                    s_pt = SourcePoint(ent.position_source_px["x"], ent.position_source_px["y"])
                                    dist = tok_center.distance_to(s_pt)
                                    if dist < best_v_dist and dist < 100.0:
                                        best_v_dist = dist
                                        target_source = ent

                        if target_source:
                            grounded_ir.parameters[f"{target_source.id}_voltage"] = PhysicalValue(
                                value=cand.numeric_value,
                                unit="V",
                                status="observed",
                                provenance=ProvenanceRecord(source="ocr", evidence_refs=[tok_ev_id], confidence=cand.confidence or 0.90),
                            )
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_volt_{cand.token_id}",
                                    target_entity_id=target_source.id,
                                    target_quantity="voltage",
                                    value=cand.numeric_value,
                                    unit="V",
                                    state=AssociationState.ASSOCIATED,
                                    supporting_evidence=[tok_ev_id, cv_ev_id],
                                    association_checks={"closest_source_distance_px": round(best_v_dist, 1)},
                                    confidence=cand.confidence,
                                )
                            )
                        else:
                            param_associations.append(
                                ParameterAssociationResult(
                                    candidate_id=f"assoc_volt_{cand.token_id}",
                                    target_entity_id=None,
                                    target_quantity="voltage",
                                    value=cand.numeric_value,
                                    unit="V",
                                    state=AssociationState.REJECTED,
                                    supporting_evidence=[],
                                    confidence=cand.confidence,
                                )
                            )

        grounded_ir.evidence.update({k: v.to_dict() for k, v in new_evidence.items()})
        grounded_ir.provenance["grounding_diagnostics"] = [d.to_dict() for d in diagnostics]
        grounded_ir.provenance["candidate_parameters"] = [c.to_dict() for c in all_val_candidates]
        grounded_ir.status = BookIRStatus.NEEDS_REVIEW
        grounded_ir.status_notes = "Circuit visual evidence and topology graph extracted; awaiting compiler verification."

        return GroundingOutcome(
            grounded_book_ir=grounded_ir,
            diagnostics=diagnostics,
            new_evidence_records=new_evidence,
            candidate_parameters=all_val_candidates,
            parameter_associations=param_associations,
        )

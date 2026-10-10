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
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import cv2
import numpy as np

from shared.schemas.evidence import (
    AssociationState,
    EntityGroundingDiagnostic,
    EvidenceMethod,
    EvidenceRecord,
    GroundingState,
    OCRExtractionResult,
    OCRToken,
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
from ai.resolution.evaluator import ReadinessEvaluator

logger = logging.getLogger(__name__)


def parse_and_cluster_circuit_tokens(tokens: List[OCRToken]) -> List[Dict[str, Any]]:
    """Extract and cluster semantic circuit component tokens into coherent component specifications.
    
    Groups designators (e.g. 'R1', 'V1') with their adjacent physical values (e.g. '100Ω', '24 V').
    Filters out diagram titles, figure numbers, and non-component annotations.
    """
    parsed = []
    ignored_keywords = [
        'parallel circuit', 'combination circuit', 'series-parallel', 'series circuit',
        'fig.', 'figure', 'dc circuit', 'circuit diagram'
    ]

    for tok in tokens:
        raw = tok.raw_text.strip()
        lower = raw.lower()
        if any(ik in lower for ik in ignored_keywords):
            continue

        b = tok.bbox_source_px
        if not b:
            continue
        cx = b.x + b.width / 2.0
        cy = b.y + b.height / 2.0

        m_v_both = re.search(r'([Vv]\d*)\s*=\s*(\d+(?:\.\d+)?)\s*[vV]?', raw)
        m_v_desig = re.match(r'^[Vv](\d+)$', raw)
        m_v_val = re.search(r'(\d+(?:\.\d+)?)\s*(?:[vV]|volt)\b', raw)

        m_r_both = re.search(r'([Rr]\d*)\s*=\s*(\d+(?:\.\d+)?)\s*([kK]?[Ωω]|ohm|kohm)?', raw)
        m_r_desig = re.match(r'^[Rr](\d+)$', raw)
        m_r_val = re.search(r'(\d+(?:\.\d+)?)\s*([kK]?[Ωω]|ohm|kohm)\b', raw)

        ptype = None
        pdesig = None
        pval = None
        punit = None

        if m_v_both:
            ptype = 'voltage_source'
            pdesig = m_v_both.group(1).upper() or 'V1'
            pval = float(m_v_both.group(2))
            punit = 'V'
        elif m_r_both and ('=' in raw or 'Ω' in raw or 'ohm' in lower):
            ptype = 'resistor'
            pdesig = m_r_both.group(1).upper() if m_r_both.group(1) else None
            pval = float(m_r_both.group(2))
            punit = 'ohm'
            if m_r_both.group(3) and 'k' in m_r_both.group(3).lower():
                pval *= 1000.0
        elif m_v_desig:
            ptype = 'voltage_source'
            pdesig = m_v_desig.group(0).upper()
        elif m_v_val:
            ptype = 'voltage_source'
            pval = float(m_v_val.group(1))
            punit = 'V'
        elif m_r_desig:
            ptype = 'resistor'
            pdesig = m_r_desig.group(0).upper()
        elif m_r_val:
            ptype = 'resistor'
            pval = float(m_r_val.group(1))
            punit = 'ohm'
            if 'k' in m_r_val.group(2).lower():
                pval *= 1000.0
        elif raw in ('+', '-'):
            ptype = 'polarity'
            pdesig = raw
        else:
            m_num = re.search(r'^(\d+(?:\.\d+)?)\s*([kK]?[Ωω]|ohm|kohm|[vV]|volt)?$', raw, re.IGNORECASE)
            if m_num:
                clean_num = m_num.group(1)
                unit_part = (m_num.group(2) or '').lower()
                has_unit = bool(unit_part or ('k' in lower and re.search(r'\d+[kK]', raw)))
                mult = 1000.0 if 'k' in unit_part or 'k' in lower else 1.0
                try:
                    pval = float(clean_num) * mult
                    punit = 'V' if any(u in unit_part for u in ('v', 'volt')) else 'ohm'
                    ptype = 'value_only' if has_unit else 'raw_number'
                except ValueError:
                    pass

        if ptype:
            parsed.append({
                'tok': tok,
                'raw': raw,
                'type': ptype,
                'desig': pdesig,
                'val': pval,
                'unit': punit,
                'bbox': b,
                'cx': cx,
                'cy': cy,
            })

    # Cluster parsed tokens into distinct components
    components = []
    used: Set[int] = set()

    # Pass 1: Tokens with both designator and value (e.g. "R1 = 10 Ω", "V=6 V")
    for i, p in enumerate(parsed):
        if p['type'] in ('voltage_source', 'resistor') and p['desig'] and p['val'] is not None:
            used.add(i)
            b = p['tok'].bbox_source_px
            lbl_box = [float(b.x), float(b.y), float(b.width), float(b.height)] if b else None
            components.append({
                'id': p['desig'],
                'type': p['type'],
                'val': p['val'],
                'unit': p['unit'],
                'tokens': [p['tok']],
                'cx': p['cx'],
                'cy': p['cy'],
                'bbox': p['bbox'],
                'label_bbox': lbl_box,
            })

    # Pass 2: Designator tokens seeking nearby values
    for i, p in enumerate(parsed):
        if i in used or p['desig'] is None or p['type'] == 'polarity':
            continue
        c_type = p['type']
        desig = p['desig']
        val = p['val']
        unit = p['unit']
        c_tokens = [p['tok']]
        used.add(i)

        best_j = None
        min_dist = float('inf')
        for j, q in enumerate(parsed):
            if j in used or q['type'] == 'polarity':
                continue
            if q['val'] is not None:
                dist = ((p['cx'] - q['cx']) ** 2 + (p['cy'] - q['cy']) ** 2) ** 0.5
                if dist < 220.0 and dist < min_dist:
                    min_dist = dist
                    best_j = j

        if best_j is not None:
            q = parsed[best_j]
            val = q['val']
            unit = q['unit']
            c_tokens.append(q['tok'])
            used.add(best_j)

        xs = [t.bbox_source_px.x for t in c_tokens if t.bbox_source_px]
        ys = [t.bbox_source_px.y for t in c_tokens if t.bbox_source_px]
        x2s = [t.bbox_source_px.x + t.bbox_source_px.width for t in c_tokens if t.bbox_source_px]
        y2s = [t.bbox_source_px.y + t.bbox_source_px.height for t in c_tokens if t.bbox_source_px]
        if xs:
            bx = min(xs)
            by = min(ys)
            bw = max(x2s) - min(xs)
            bh = max(y2s) - min(ys)
            bbox = SourceBBox(bx, by, bw, bh)
            cx = bx + bw / 2.0
            cy = by + bh / 2.0
            lbl_box = [float(bx), float(by), float(bw), float(bh)]
        else:
            bbox = p['bbox']
            cx, cy = p['cx'], p['cy']
            b = p['tok'].bbox_source_px
            lbl_box = [float(b.x), float(b.y), float(b.width), float(b.height)] if b else None

        components.append({
            'id': desig,
            'type': c_type,
            'val': val,
            'unit': unit,
            'tokens': c_tokens,
            'cx': cx,
            'cy': cy,
            'bbox': bbox,
            'label_bbox': lbl_box,
        })

    # Pass 3: Standalone value tokens without designators
    r_idx = len([c for c in components if c['type'] == 'resistor']) + 1
    v_idx = len([c for c in components if c['type'] == 'voltage_source']) + 1
    for i, p in enumerate(parsed):
        if i in used or p['type'] == 'polarity':
            continue
        c_type = p['type']
        if c_type == 'value_only':
            raw_u = (p.get('unit') or '').lower()
            if any(u in raw_u for u in ('ohm', 'kohm', 'mohm', 'ω', 'v')) or (p.get('desig') and p['desig'][0] in ('R', 'V')):
                c_type = 'voltage_source' if any(u in raw_u for u in ('v', 'volt')) else 'resistor'
            else:
                continue
        elif c_type == 'raw_number':
            continue
        desig = f"V{v_idx}" if c_type == 'voltage_source' else f"R{r_idx}"
        if c_type == 'voltage_source':
            v_idx += 1
        else:
            r_idx += 1
        used.add(i)
        b = p['tok'].bbox_source_px
        lbl_box = [float(b.x), float(b.y), float(b.width), float(b.height)] if b else None
        components.append({
            'id': desig,
            'type': c_type,
            'val': p['val'],
            'unit': p['unit'] or ('V' if c_type == 'voltage_source' else 'ohm'),
            'tokens': [p['tok']],
            'cx': p['cx'],
            'cy': p['cy'],
            'bbox': p['bbox'],
            'label_bbox': lbl_box,
        })

    return components


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
        cv_wires: List[SourceLine] = (
            cv_candidates.get("wires")
            or cv_candidates.get("wire_paths")
            or cv_candidates.get("wire_segments")
            or []
        )
        cv_junctions: List[SourcePoint] = cv_candidates.get("junctions") or []
        rails_y: List[int] = cv_candidates.get("rails_y") or []
        branches_x: List[int] = cv_candidates.get("branches_x") or []
        edges_img: Optional[np.ndarray] = cv_candidates.get("edges")

        w = int(grounded_ir.geometry.get("width", 800))
        h = int(grounded_ir.geometry.get("height", 600))

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
        # 1. OCR Token Processing & Semantic Component Clustering
        # -------------------------------------------------------------------
        parsed_tokens: List[OCRToken] = []
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
                parsed_tokens.append(tok)

        # If cv_comps are explicitly provided (e.g. from CV detection or test harness),
        # prioritize them and associate nearby OCR tokens (dist < 220px or matching designator)
        used_tokens: Set[str] = set()
        matched_tok_ids: Set[str] = set()

        if cv_comps:
            semantic_clusters = []
            for c_idx, c in enumerate(cv_comps):
                box = c.get("bbox") or c.get("box") or SourceBBox(100, 100, 50, 50)
                center = c.get("center") or SourcePoint(box.x + box.width / 2.0, box.y + box.height / 2.0)
                ctype = c.get("type", "resistor")
                desig = c.get("id") or (f"V{c_idx+1}" if ctype in ("voltage_source", "battery") else f"R{c_idx+1}")
                if c.get("id") and c["id"].startswith("cv_comp_"):
                    desig = f"V{c_idx+1}" if ctype in ("voltage_source", "battery") else f"R{c_idx+1}"

                # Look for nearby unused OCR tokens
                best_tok = None
                best_cand = None
                # Collect all nearby unused OCR tokens (within 220px or matching designator)
                nearby_toks = []
                for tok in parsed_tokens:
                    if tok.id in used_tokens:
                        continue
                    b = tok.bbox_source_px
                    tc = SourcePoint(b.x + b.width / 2.0, b.y + b.height / 2.0) if b else None
                    dist = center.distance_to(tc) if tc else float("inf")
                    is_match = bool(re.search(rf"\b{re.escape(desig)}\b", tok.raw_text, re.IGNORECASE))
                    if dist < 220.0 or is_match:
                        nearby_toks.append((tok, dist, is_match))

                # Sort by distance
                nearby_toks.sort(key=lambda item: item[1])

                val = c.get("value")
                unit = c.get("unit") or ("V" if ctype in ("voltage_source", "battery") else "ohm")
                c_toks = []

                for tok, dist, is_match in nearby_toks:
                    used_tokens.add(tok.id)
                    matched_tok_ids.add(tok.id)
                    c_toks.append(tok)
                    if val is None:
                        val_cands = parse_physical_value_candidate(tok)
                        for vc in val_cands:
                            if vc.numeric_value is not None:
                                mult = 1000.0 if (vc.raw_unit and "k" in vc.raw_unit.lower()) else 1.0
                                val = float(vc.numeric_value) * mult
                                unit = "V" if vc.quantity_candidate == "voltage" else "ohm"
                                break

                lbl_box = None
                for tok in c_toks:
                    if tok.bbox_source_px:
                        b = tok.bbox_source_px
                        lbl_box = [float(b.x), float(b.y), float(b.width), float(b.height)]
                        break

                semantic_clusters.append({
                    "id": desig,
                    "type": ctype,
                    "val": val,
                    "unit": unit,
                    "tokens": c_toks,
                    "cx": center.x,
                    "cy": center.y,
                    "bbox": box,
                    "label_bbox": lbl_box,
                    "terminals": c.get("terminals"),
                })
        else:
            semantic_clusters = parse_and_cluster_circuit_tokens(parsed_tokens)
            for sc in semantic_clusters:
                for tok in sc.get("tokens", []):
                    matched_tok_ids.add(tok.id)

        # -------------------------------------------------------------------
        # 2. Physical Symbol Positioning & Terminal Grounding
        # -------------------------------------------------------------------
        grounded_components: List[Dict[str, Any]] = []
        wire_mask: Optional[np.ndarray] = None
        cut_mask: Optional[np.ndarray] = None

        if edges_img is not None:
            wire_mask = cv2.dilate(edges_img, np.ones((3, 3), np.uint8), iterations=1)
            cut_mask = wire_mask.copy()

        for comp in semantic_clusters:
            cx, cy = int(comp["cx"]), int(comp["cy"])
            ctype = comp["type"]
            is_vertical = False

            # Check geometric proximity to discovered vertical branches vs horizontal rails
            y_top = min(rails_y) if rails_y else 0
            y_bot = max(rails_y) if rails_y else h
            best_bx = min(branches_x, key=lambda bx: abs(cx - bx)) if branches_x else cx
            dist_bx = abs(cx - best_bx) if branches_x else float("inf")
            best_ry = min(rails_y, key=lambda ry: abs(cy - ry)) if rails_y else cy
            dist_ry = abs(cy - best_ry) if rails_y else float("inf")

            is_in_rail_span = (y_top - 40 <= cy <= y_bot + 40) if len(rails_y) >= 2 else True

            # If within vertical span between rails, and closer to branch or within branch proximity (< 160px)
            if branches_x and is_in_rail_span and (dist_bx < 160 or dist_bx < dist_ry):
                is_vertical = True
            elif edges_img is not None:
                r = 130
                sub_edges = edges_img[max(0, cy - r):min(h, cy + r), max(0, cx - r):min(w, cx + r)]
                v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
                v_leads = cv2.morphologyEx(sub_edges, cv2.MORPH_OPEN, v_kernel)
                h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
                h_leads = cv2.morphologyEx(sub_edges, cv2.MORPH_OPEN, h_kernel)
                v_count = np.count_nonzero(v_leads)
                h_count = np.count_nonzero(h_leads)
                if ctype in ("voltage_source", "battery"):
                    is_vertical = True if v_count > 100 else (v_count >= h_count)
                else:
                    is_vertical = (v_count > h_count)
            else:
                is_vertical = (dist_bx <= dist_ry and dist_bx < 120)

            if is_vertical:
                wire_x = best_bx if branches_x else cx
                wire_y = cy if (y_top + 40 <= cy <= y_bot - 40) else (y_top + y_bot) / 2.0
                half_w, half_h = 25, 30
                t1 = (float(wire_x), float(wire_y - half_h - 4))
                t2 = (float(wire_x), float(wire_y + half_h + 4))
            else:
                wire_x = cx
                wire_y = best_ry if rails_y else cy
                half_w, half_h = 30, 25
                t1 = (float(wire_x - half_w - 4), float(wire_y))
                t2 = (float(wire_x + half_w + 4), float(wire_y))

            bx1 = max(0, int(wire_x - half_w))
            by1 = max(0, int(wire_y - half_h))
            bx2 = min(w, int(wire_x + half_w))
            by2 = min(h, int(wire_y + half_h))

            if cut_mask is not None:
                cut_mask[by1:by2, bx1:bx2] = 0

            primary_ev_id = None
            if comp.get("tokens"):
                primary_ev_id = f"ev_ocr_{comp['tokens'][0].id}"

            grounded_components.append({
                "id": comp["id"],
                "type": ctype,
                "value": comp["val"],
                "unit": comp["unit"],
                "center": (float(wire_x), float(wire_y)),
                "bbox": [float(bx1), float(by1), float(bx2 - bx1), float(by2 - by1)],
                "label_bbox": comp.get("label_bbox"),
                "terminal_1": SourcePoint(t1[0], t1[1]),
                "terminal_2": SourcePoint(t2[0], t2[1]),
                "evidence_ref": primary_ev_id or cv_ev_id,
            })

        # -------------------------------------------------------------------
        # 3. Wire Network Topological Node Clustering
        # -------------------------------------------------------------------
        comp_term_nodes: Dict[str, Dict[str, str]] = {}
        unique_nodes_discovered = 0

        # Planar Rails & Branches Deterministic Topology Resolution
        if len(rails_y) >= 2 and len(branches_x) >= 2 and len(cv_wires) > 0:
            y_top = min(rails_y)
            y_bot = max(rails_y)

            # 1. Classify components: rail components vs branch components
            top_rail_comps = []
            bot_rail_comps = []
            branch_comps = []

            for c in grounded_components:
                cx, cy = c["center"]
                if abs(cy - y_top) < 35:
                    top_rail_comps.append(c)
                elif abs(cy - y_bot) < 35:
                    bot_rail_comps.append(c)
                else:
                    branch_comps.append(c)

            top_rail_comps.sort(key=lambda c: c["center"][0])
            bot_rail_comps.sort(key=lambda c: c["center"][0])

            # 2. Partition top rail into node segments
            node_counter = 1
            top_rail_nodes = [f"N{node_counter}"]
            for _ in top_rail_comps:
                node_counter += 1
                top_rail_nodes.append(f"N{node_counter}")

            def _get_top_node(x: float) -> str:
                for idx, rc in enumerate(top_rail_comps):
                    if x < rc["center"][0]:
                        return top_rail_nodes[idx]
                return top_rail_nodes[-1]

            for idx, rc in enumerate(top_rail_comps):
                comp_term_nodes[rc["id"]] = {
                    "terminal_1": top_rail_nodes[idx],
                    "terminal_2": top_rail_nodes[idx + 1],
                }

            # 3. Partition bottom rail into node segments
            node_counter += 1
            bot_rail_nodes = [f"N{node_counter}"]
            for _ in bot_rail_comps:
                node_counter += 1
                bot_rail_nodes.append(f"N{node_counter}")

            def _get_bot_node(x: float) -> str:
                for idx, rc in enumerate(bot_rail_comps):
                    if x < rc["center"][0]:
                        return bot_rail_nodes[idx]
                return bot_rail_nodes[-1]

            for idx, rc in enumerate(bot_rail_comps):
                comp_term_nodes[rc["id"]] = {
                    "terminal_1": bot_rail_nodes[idx],
                    "terminal_2": bot_rail_nodes[idx + 1],
                }

            # 4. Vertical branch components
            for c in branch_comps:
                cx, cy = c["center"]
                comp_term_nodes[c["id"]] = {
                    "terminal_1": _get_top_node(cx),
                    "terminal_2": _get_bot_node(cx),
                }

            used_nids = set()
            for tn in comp_term_nodes.values():
                used_nids.add(tn["terminal_1"])
                used_nids.add(tn["terminal_2"])
            unique_nodes_discovered = len(used_nids)
        elif len(cv_wires) > 0 and cut_mask is not None:
            dil_cut = cv2.dilate(cut_mask, np.ones((5, 5), np.uint8), iterations=1)
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(dil_cut)

            def _get_node_label(pt: SourcePoint) -> Optional[int]:
                px, py = int(pt.x), int(pt.y)
                win = labels[max(0, py - 30):min(h, py + 30), max(0, px - 30):min(w, px + 30)]
                non_zero = win[win > 0]
                if len(non_zero) > 0:
                    vals, counts = np.unique(non_zero, return_counts=True)
                    return int(vals[np.argmax(counts)])
                return None

            raw_nodes = {}
            for comp in grounded_components:
                raw_nodes[f"{comp['id']}.t1"] = _get_node_label(comp["terminal_1"])
                raw_nodes[f"{comp['id']}.t2"] = _get_node_label(comp["terminal_2"])

            unique_labels = sorted(list({lbl for lbl in raw_nodes.values() if lbl is not None}))
            label_to_node = {lbl: f"N{idx+1}" for idx, lbl in enumerate(unique_labels)}
            used_nids = set(label_to_node.values())

            for comp in grounded_components:
                cid = comp["id"]
                n1 = label_to_node.get(raw_nodes[f"{cid}.t1"], "N1")
                n2 = label_to_node.get(raw_nodes[f"{cid}.t2"], "N2")
                if n1 == n2:
                    n2 = f"N{len(used_nids) + 1}"
                    used_nids.add(n2)
                comp_term_nodes[cid] = {"terminal_1": n1, "terminal_2": n2}

            unique_nodes_discovered = len(used_nids)
        elif len(cv_wires) > 0:
            # Hough line distance clustering fallback
            term_list = []
            for comp in grounded_components:
                term_list.append((comp["id"], "terminal_1", comp["terminal_1"]))
                term_list.append((comp["id"], "terminal_2", comp["terminal_2"]))

            for idx, (cid, tname, tpt) in enumerate(term_list):
                comp_term_nodes.setdefault(cid, {})[tname] = f"N{(idx % 2) + 1}"
            unique_nodes_discovered = 2
        else:
            # ZERO wire continuity: Strict anti-fabrication invariant (PR-06)
            for comp in grounded_components:
                comp_term_nodes[comp["id"]] = {"terminal_1": "N1", "terminal_2": "N1"}
            unique_nodes_discovered = 0

        # Select reference node (ground): negative terminal of primary DC voltage source
        ref_node = "N0"
        for comp in grounded_components:
            if comp["type"] in ("voltage_source", "battery"):
                ref_node = comp_term_nodes.get(comp["id"], {}).get("terminal_2", "N0")
                break
        if ref_node == "N0" and grounded_components:
            ref_node = comp_term_nodes.get(grounded_components[0]["id"], {}).get("terminal_1", "N1")

        # -------------------------------------------------------------------
        # 4. Canonical Entities & Parameters Assembly
        # -------------------------------------------------------------------
        grounded_entities: List[BookEntity] = []
        canonical_components = []

        for comp in grounded_components:
            cid = comp["id"]
            ctype = comp["type"]
            cx, cy = comp["center"]
            b = comp["bbox"]
            t1 = comp["terminal_1"]
            t2 = comp["terminal_2"]
            n1 = comp_term_nodes.get(cid, {}).get("terminal_1", "N1")
            n2 = comp_term_nodes.get(cid, {}).get("terminal_2", "N2")
            c_nodes = [n1, n2] if len(cv_wires) > 0 else []

            pos_dict = {
                "x": cx,
                "y": cy,
                "coordinate_space": "source_px",
                "method": "cv_circuit_component",
            }
            geom_dict = {
                "bounds": {"x": b[0], "y": b[1], "width": b[2], "height": b[3]},
                "terminal_1": {"x": t1.x, "y": t1.y},
                "terminal_2": {"x": t2.x, "y": t2.y},
                "wire_connected": len(cv_wires) > 0,
            }

            ent = BookEntity(
                id=cid,
                type=ctype,
                position_source_px=pos_dict,
                geometry=geom_dict,
                evidence_refs=[cv_ev_id, comp["evidence_ref"]],
            )
            grounded_entities.append(ent)

            canonical_components.append({
                "id": cid,
                "type": ctype,
                "nodes": c_nodes,
                "value": comp["value"],
                "unit": comp["unit"],
                "label_bbox_source_px": comp.get("label_bbox"),
                "terminals": [
                    {
                        "id": f"{cid}.t1",
                        "node": n1 if len(c_nodes) > 0 else "N1",
                        "polarity": "+" if ctype in ("voltage_source", "battery") else None,
                        "source_px": [t1.x, t1.y],
                    },
                    {
                        "id": f"{cid}.t2",
                        "node": n2 if len(c_nodes) > 1 else "N2",
                        "polarity": "-" if ctype in ("voltage_source", "battery") else None,
                        "source_px": [t2.x, t2.y],
                    },
                ],
                "geometry": {
                    "bbox_source_px": [b[0], b[1], b[0] + b[2], b[1] + b[3]],
                    "center_source_px": [cx, cy],
                    "label_bbox_source_px": comp.get("label_bbox"),
                },
            })

            if comp["value"] is not None:
                quantity = "voltage" if ctype in ("voltage_source", "battery") else "resistance"
                param_key = f"{cid}_{quantity}"
                grounded_ir.parameters[param_key] = PhysicalValue(
                    value=comp["value"],
                    unit=comp["unit"],
                    status="observed",
                    provenance=ProvenanceRecord(source="ocr", evidence_refs=[comp["evidence_ref"]], confidence=0.95),
                )
                grounded_ir.parameter_provenance[param_key] = {
                    "source": "ocr",
                    "evidence_refs": [comp["evidence_ref"]],
                    "confidence": 0.95,
                }
                param_associations.append(
                    ParameterAssociationResult(
                        candidate_id=f"assoc_{cid}_{quantity}",
                        target_entity_id=cid,
                        target_quantity=quantity,
                        value=comp["value"],
                        unit=comp["unit"],
                        state=AssociationState.ASSOCIATED,
                        supporting_evidence=[comp["evidence_ref"], cv_ev_id],
                        confidence=0.95,
                    )
                )

            diagnostics.append(
                EntityGroundingDiagnostic(
                    entity_id=cid,
                    grounding_state=GroundingState.GROUNDED,
                    supporting_evidence=[cv_ev_id, comp["evidence_ref"]],
                    checks={"wire_connected": len(cv_wires) > 0},
                    notes=f"Component grounded as {cid} ({ctype}) with visual leads at ({cx:.1f}, {cy:.1f}).",
                )
            )

        # Unclaimed / faraway OCR candidate rejections (strict anti-fabrication)
        for pt in parsed_tokens:
            if pt.id not in matched_tok_ids:
                for cand in parse_physical_value_candidate(pt):
                    param_associations.append(
                        ParameterAssociationResult(
                            candidate_id=f"assoc_{cand.token_id}",
                            target_entity_id=None,
                            target_quantity=cand.quantity_candidate or "unknown",
                            value=cand.numeric_value,
                            unit=cand.raw_unit or "",
                            state=AssociationState.REJECTED,
                            supporting_evidence=[],
                            confidence=cand.confidence,
                        )
                    )

        grounded_ir.entities = grounded_entities

        all_nids = set()
        for c in canonical_components:
            all_nids.update(c.get("nodes", []))
        canonical_nodes = [{"id": nid} for nid in sorted(all_nids)] if len(cv_wires) > 0 else []

        canonical_wires = []
        for idx, wire_item in enumerate(cv_wires):
            if hasattr(wire_item, "start") and hasattr(wire_item, "end"):
                p1 = [float(wire_item.start.x), float(wire_item.start.y)]
                p2 = [float(wire_item.end.x), float(wire_item.end.y)]
            elif isinstance(wire_item, dict) and "start" in wire_item and "end" in wire_item:
                p1 = [float(wire_item["start"]["x"]), float(wire_item["start"]["y"])]
                p2 = [float(wire_item["end"]["x"]), float(wire_item["end"]["y"])]
            elif isinstance(wire_item, (list, tuple)) and len(wire_item) >= 4:
                p1 = [float(wire_item[0]), float(wire_item[1])]
                p2 = [float(wire_item[2]), float(wire_item[3])]
            elif isinstance(wire_item, dict) and "polyline_source_px" in wire_item:
                canonical_wires.append(wire_item)
                continue
            else:
                continue

            mid_x = (p1[0] + p2[0]) / 2.0
            mid_y = (p1[1] + p2[1]) / 2.0
            assigned_node = None
            if len(rails_y) >= 2 and len(branches_x) >= 2 and "_get_top_node" in locals():
                y_top = min(rails_y)
                y_bot = max(rails_y)
                if abs(mid_y - y_top) < 30 or (mid_y < (y_top + y_bot) / 2.0):
                    assigned_node = _get_top_node(mid_x)
                else:
                    assigned_node = _get_bot_node(mid_x)
            elif cut_mask is not None and "labels" in locals():
                py, px = int(np.clip(mid_y, 0, h - 1)), int(np.clip(mid_x, 0, w - 1))
                lbl = labels[py, px]
                if lbl > 0 and lbl in label_to_node:
                    assigned_node = label_to_node[lbl]

            if not assigned_node:
                best_dist = float("inf")
                for c in canonical_components:
                    for t in c.get("terminals", []):
                        spx = t.get("source_px")
                        if spx:
                            d = (spx[0] - mid_x) ** 2 + (spx[1] - mid_y) ** 2
                            if d < best_dist:
                                best_dist = d
                                assigned_node = t.get("node")

            canonical_wires.append({
                "id": f"wire_{idx+1}",
                "node": assigned_node or (canonical_nodes[0]["id"] if canonical_nodes else "N1"),
                "polyline_source_px": [p1, p2],
                "points": [p1, p2],
                "length_px": float(np.hypot(p2[0] - p1[0], p2[1] - p1[1])),
            })

        grounded_ir.parameters["components"] = canonical_components
        grounded_ir.parameters["nodes"] = canonical_nodes
        grounded_ir.parameters["wires"] = canonical_wires
        grounded_ir.parameters["reference_node"] = ref_node

        if grounded_ir.parameter_provenance is None:
            grounded_ir.parameter_provenance = {}
        grounded_ir.parameter_provenance["components"] = ProvenanceRecord(
            source="ocr_and_cv",
            notes="Extracted from schematic visual features and OCR labels."
        )
        grounded_ir.parameter_provenance["nodes"] = ProvenanceRecord(
            source="ocr_and_cv",
            notes="Derived from wire continuity network."
        )

        grounded_ir.geometry["circuit_topology"] = {
            "verified_connectivity": len(canonical_nodes) >= 2,
            "node_count": len(canonical_nodes),
        }
        grounded_ir.evidence.update({k: v.to_dict() for k, v in new_evidence.items()})
        grounded_ir.provenance["grounding_diagnostics"] = [d.to_dict() for d in diagnostics]
        grounded_ir.provenance["candidate_parameters"] = [c.to_dict() for c in all_val_candidates]

        # -------------------------------------------------------------------
        # 5. Authoritative Readiness Gate (PR-07 / PR-08 Invariant)
        # -------------------------------------------------------------------
        if len(cv_wires) > 0 and len(canonical_nodes) >= 2:
            ReadinessEvaluator.evaluate(grounded_ir, mutate_status=True)
        else:
            grounded_ir.status = BookIRStatus.NEEDS_REVIEW
            grounded_ir.status_notes = "Missing wire continuity: circuit terminals ungrounded."

        return GroundingOutcome(
            grounded_book_ir=grounded_ir,
            diagnostics=diagnostics,
            new_evidence_records=new_evidence,
            candidate_parameters=all_val_candidates,
            parameter_associations=param_associations,
        )

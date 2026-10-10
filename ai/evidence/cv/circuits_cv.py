"""PR-06 DC Circuit Classical CV Candidate Extractor.

Extracts deterministic geometric candidates for:
  - component bodies (resistors, voltage sources, switches)
  - component terminals
  - wire segments
  - junction nodes
  - structural connectivity graph (wire path continuity)
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourceLine, SourcePoint
from ai.evidence.cv.geometry_helpers import merge_collinear_lines
from ai.evidence.cv.preprocessing import preprocess_for_geometry

logger = logging.getLogger(__name__)


class CircuitCVCandidateExtractor:
    """Extracts geometric components, terminals, and wire paths for DC linear circuits."""

    def extract(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        ocr_boxes: Optional[List[SourceBBox]] = None,
    ) -> Dict[str, Any]:
        h, w = image_bgr.shape[:2]
        gray, edges = preprocess_for_geometry(image_bgr, ocr_boxes=ocr_boxes)

        # 1. Detect Wires (Hough Lines)
        min_len = int(round(min(w, h) * 0.06))
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 20, minLineLength=min_len, maxLineGap=8)

        raw_lines = []
        if lines is not None:
            for l in lines:
                pts = l.reshape(-1)
                raw_lines.append(SourceLine(start=SourcePoint(float(pts[0]), float(pts[1])), end=SourcePoint(float(pts[2]), float(pts[3]))))

        merged_wires = merge_collinear_lines(raw_lines, dist_thresh=6.0, angle_thresh_deg=5.0)

        # 2. Structural Branch & Rail Detection (planar circuits with horizontal and vertical rails/branches)
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(12, int(h * 0.025))))
        v_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, v_kernel)
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(12, int(w * 0.025)), 1))
        h_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, h_kernel)

        col_sums = np.sum(v_lines > 0, axis=0)
        row_sums = np.sum(h_lines > 0, axis=1)

        def _cluster_1d(indices, max_gap=16):
            clusters = []
            curr = []
            for idx in indices:
                if not curr or idx - curr[-1] <= max_gap:
                    curr.append(idx)
                else:
                    clusters.append(int(np.mean(curr)))
                    curr = [idx]
            if curr:
                clusters.append(int(np.mean(curr)))
            return clusters

        branches_x = _cluster_1d([x for x in range(w) if col_sums[x] > h * 0.08])
        rails_y = _cluster_1d([y for y in range(h) if row_sums[y] > w * 0.08])

        # Also incorporate OCR box anchors to find branches/rails that might be interrupted by labels
        if ocr_boxes:
            for b in ocr_boxes:
                bx_center = int(b.x + b.width / 2.0)
                by_center = int(b.y + b.height / 2.0)
                near_x = [x for x in branches_x if abs(x - bx_center) < 60]
                if not near_x:
                    local_cols = np.sum(v_lines[:, max(0, bx_center - 35):min(w, bx_center + 35)] > 0, axis=0)
                    if len(local_cols) > 0 and np.max(local_cols) > h * 0.08:
                        best_local_x = max(0, bx_center - 35) + int(np.argmax(local_cols))
                        branches_x.append(best_local_x)
            branches_x = sorted(_cluster_1d(sorted(branches_x)))

        valid_rails_y = []
        min_spans = 2 if len(branches_x) >= 2 else 1
        for ry in rails_y:
            span_count = sum(1 for bx in branches_x if np.any(edges[max(0, ry - 14):min(h, ry + 14), max(0, bx - 18):min(w, bx + 18)] > 0))
            if span_count >= min_spans:
                valid_rails_y.append(ry)

        if len(valid_rails_y) >= 2 and len(branches_x) >= 2:
            y_top = min(valid_rails_y)
            y_bot = max(valid_rails_y)
            x_min = min(branches_x)
            x_max = max(branches_x)

            top_rail = SourceLine(start=SourcePoint(float(x_min), float(y_top)), end=SourcePoint(float(x_max), float(y_top)))
            bot_rail = SourceLine(start=SourcePoint(float(x_min), float(y_bot)), end=SourcePoint(float(x_max), float(y_bot)))
            merged_wires.append(top_rail)
            merged_wires.append(bot_rail)

            # Check for intermediate horizontal rails (e.g. in multi-stage / series-parallel circuits)
            mid_rails = [ry for ry in valid_rails_y if y_top + 30 < ry < y_bot - 30]
            for mry in mid_rails:
                merged_wires.append(SourceLine(start=SourcePoint(float(x_min), float(mry)), end=SourcePoint(float(x_max), float(mry))))

        # 2b. Detect Component Bodies (rectangular contours or symbols)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        components = []
        for idx, c in enumerate(contours):
            area = cv2.contourArea(c)
            # Typical resistor / component body area
            if (w * h * 0.001) <= area <= (w * h * 0.08):
                bx, by, bw, bh = cv2.boundingRect(c)
                cx = float(bx + bw / 2.0)
                cy = float(by + bh / 2.0)

                # Filter out contours outside the circuit bounds (e.g. titles, figure captions)
                if len(valid_rails_y) >= 2 and len(branches_x) >= 2:
                    if not (min(branches_x) - 45 <= cx <= max(branches_x) + 45 and min(valid_rails_y) - 40 <= cy <= max(valid_rails_y) + 40):
                        continue

                # Filter out contours that overlap OCR text boxes (labels, digits, units)
                if ocr_boxes:
                    c_box = SourceBBox(float(bx), float(by), float(bw), float(bh))
                    if any(c_box.iou(b) > 0.10 or (b.x - 5 <= cx <= b.x + b.width + 5 and b.y - 5 <= cy <= b.y + b.height + 5) for b in ocr_boxes):
                        continue

                aspect = max(bw, bh) / (min(bw, bh) + 1e-5)
                if aspect > 5.0:
                    continue

                # Determine terminals: left/right or top/bottom endpoints
                if bw >= bh:
                    t1 = SourcePoint(float(bx), cy)
                    t2 = SourcePoint(float(bx + bw), cy)
                else:
                    t1 = SourcePoint(cx, float(by))
                    t2 = SourcePoint(cx, float(by + bh))

                components.append({
                    "id": f"cv_comp_{idx+1:02d}",
                    "bbox": SourceBBox(float(bx), float(by), float(bw), float(bh)),
                    "center": SourcePoint(cx, cy),
                    "terminal_1": t1,
                    "terminal_2": t2,
                    "area": float(area),
                })

        # 3. Detect Junctions (where wire endpoints meet within 14 px)
        junctions: List[SourcePoint] = []
        wire_endpoints = []
        for wire in merged_wires:
            wire_endpoints.append(wire.start)
            wire_endpoints.append(wire.end)

        for i, pt1 in enumerate(wire_endpoints):
            matches = [pt2 for j, pt2 in enumerate(wire_endpoints) if i != j and pt1.distance_to(pt2) < 14.0]
            if len(matches) >= 2:  # At least 3 wire ends meeting
                if not any(junc.distance_to(pt1) < 12.0 for junc in junctions):
                    junctions.append(pt1)

        # 4. Verified Connectivity: Check which components have terminals connected to wires
        for comp in components:
            t1 = comp["terminal_1"]
            t2 = comp["terminal_2"]
            c1_connected = any(w.distance_to_point(t1) < 22.0 for w in merged_wires)
            c2_connected = any(w.distance_to_point(t2) < 22.0 for w in merged_wires)
            comp["connected"] = c1_connected and c2_connected

        return {
            "components": components,
            "wires": merged_wires,
            "junctions": junctions,
            "rails_y": valid_rails_y if len(valid_rails_y) >= 2 else rails_y,
            "branches_x": branches_x,
            "edges": edges,
        }

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

        # 2. Detect Component Bodies (rectangular contours or symbols)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        components = []
        for idx, c in enumerate(contours):
            area = cv2.contourArea(c)
            # Typical resistor / component body area
            if (w * h * 0.001) <= area <= (w * h * 0.08):
                bx, by, bw, bh = cv2.boundingRect(c)
                aspect = max(bw, bh) / (min(bw, bh) + 1e-5)
                # Resistors often have aspect ratio between 1.5 and 5.0
                cx = float(bx + bw / 2.0)
                cy = float(by + bh / 2.0)

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

        # 3. Detect Junctions (where wire endpoints meet within 8 px)
        junctions: List[SourcePoint] = []
        wire_endpoints = []
        for wire in merged_wires:
            wire_endpoints.append(wire.start)
            wire_endpoints.append(wire.end)

        for i, pt1 in enumerate(wire_endpoints):
            matches = [pt2 for j, pt2 in enumerate(wire_endpoints) if i != j and pt1.distance_to(pt2) < 8.0]
            if len(matches) >= 2:  # At least 3 wire ends meeting
                if not any(junc.distance_to(pt1) < 10.0 for junc in junctions):
                    junctions.append(pt1)

        # 4. Verified Connectivity: Check which components have terminals connected to wires
        connected_pairs = []
        for comp in components:
            t1 = comp["terminal_1"]
            t2 = comp["terminal_2"]
            c1_connected = any(w.distance_to_point(t1) < 10.0 for w in merged_wires)
            c2_connected = any(w.distance_to_point(t2) < 10.0 for w in merged_wires)
            comp["connected"] = c1_connected and c2_connected

        return {
            "components": components,
            "wires": merged_wires,
            "junctions": junctions,
        }

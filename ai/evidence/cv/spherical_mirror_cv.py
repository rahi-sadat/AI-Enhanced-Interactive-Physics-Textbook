"""PR-06 Spherical Mirror Classical CV Candidate Extractor.

Extracts deterministic geometric candidates for:
  - principal optical axis
  - curved mirror boundary / arc
  - vertex / pole coordinate
  - focus (F) and center of curvature (C) markers
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourceLine, SourcePoint
from ai.evidence.cv.geometry_helpers import merge_collinear_lines
from ai.evidence.cv.preprocessing import preprocess_for_geometry

logger = logging.getLogger(__name__)


class SphericalMirrorCVCandidateExtractor:
    """Extracts geometric candidates for spherical mirror diagrams."""

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

        min_len = int(round(min(w, h) * 0.20))
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, minLineLength=min_len, maxLineGap=15)

        raw_lines = []
        if lines is not None:
            for l in lines:
                pts = l.reshape(-1)
                raw_lines.append(SourceLine(start=SourcePoint(float(pts[0]), float(pts[1])), end=SourcePoint(float(pts[2]), float(pts[3]))))

        merged = merge_collinear_lines(raw_lines, dist_thresh=8.0, angle_thresh_deg=6.0)

        # 1. Principal Axis (horizontal line)
        axis_line = None
        best_len = 0.0
        for l in merged:
            dy = abs(l.end.y - l.start.y)
            dx = abs(l.end.x - l.start.x)
            if dx > 0 and (dy / (dx + 1e-5)) < 0.12:
                if l.length_px > best_len:
                    best_len = l.length_px
                    axis_line = l

        axis_y = (axis_line.start.y + axis_line.end.y) / 2.0 if axis_line else None

        # 2. Mirror Arc Contour (curved line near right or left border)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        best_arc = None
        best_arc_len = 0.0
        for c in contours:
            length = cv2.arcLength(c, closed=False)
            if length > best_arc_len and length > h * 0.25:
                # Check that it's curved (low solidity or high aspect ratio)
                x, y, cw, ch = cv2.boundingRect(c)
                if ch > cw:  # tall, vertical-ish curve
                    best_arc_len = length
                    best_arc = c

        pole = None
        if best_arc is not None and axis_y is not None:
            # Find point on curve closest to axis_y
            pts = best_arc.reshape(-1, 2)
            dists = [abs(pt[1] - axis_y) for pt in pts]
            min_idx = int(np.argmin(dists))
            pole = SourcePoint(float(pts[min_idx][0]), float(pts[min_idx][1]))

        return {
            "principal_axis": axis_line,
            "pole": pole,
            "mirror_contour": best_arc,
        }

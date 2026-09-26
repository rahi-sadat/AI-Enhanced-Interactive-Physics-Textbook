"""PR-06 Interface Refraction Classical CV Candidate Extractor.

Extracts deterministic geometric candidates for:
  - medium boundary line (interface)
  - surface normal line (perpendicular to interface)
  - incident ray line
  - refracted ray line
  - reflected ray line
  - point of incidence (intersection of ray and boundary)
"""
from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourceLine, SourcePoint
from ai.evidence.cv.geometry_helpers import line_intersection, merge_collinear_lines
from ai.evidence.cv.preprocessing import preprocess_for_geometry

logger = logging.getLogger(__name__)


class InterfaceRefractionCVCandidateExtractor:
    """Extracts geometric candidates for Snell's law interface refraction diagrams."""

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

        min_len = int(round(min(w, h) * 0.15))
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 28, minLineLength=min_len, maxLineGap=12)

        raw_lines = []
        if lines is not None:
            for l in lines:
                pts = l.reshape(-1)
                raw_lines.append(SourceLine(start=SourcePoint(float(pts[0]), float(pts[1])), end=SourcePoint(float(pts[2]), float(pts[3]))))

        merged = merge_collinear_lines(raw_lines, dist_thresh=8.0, angle_thresh_deg=6.0)

        # 1. Boundary Line: prominent horizontal interface line
        boundary_line = None
        best_b_len = 0.0
        for l in merged:
            dy = abs(l.end.y - l.start.y)
            dx = abs(l.end.x - l.start.x)
            if dx > 0 and (dy / (dx + 1e-5)) < 0.20:
                mid_y = (l.start.y + l.end.y) / 2.0
                if abs(mid_y - h * 0.5) < h * 0.35 and l.length_px > best_b_len:
                    best_b_len = l.length_px
                    boundary_line = l

        bound_y = (boundary_line.start.y + boundary_line.end.y) / 2.0 if boundary_line else None

        # 2. Normal Line: predominantly vertical line crossing boundary
        normal_line = None
        best_norm_len = 0.0
        for l in merged:
            dy = abs(l.end.y - l.start.y)
            dx = abs(l.end.x - l.start.x)
            if dy > 0 and (dx / (dy + 1e-5)) < 0.20:
                if l.length_px > best_norm_len:
                    best_norm_len = l.length_px
                    normal_line = l

        normal_x = (normal_line.start.x + normal_line.end.x) / 2.0 if normal_line else None
        incidence_point = (
            SourcePoint(float(normal_x), float(bound_y))
            if (normal_x is not None and bound_y is not None)
            else None
        )

        # 3. Ray lines (slanted lines converging at/near incidence point)
        incident_ray = None
        refracted_ray = None

        if incidence_point is not None and bound_y is not None:
            slanted = [l for l in merged if l != boundary_line and l != normal_line]
            for l in slanted:
                d_start = l.start.distance_to(incidence_point)
                d_end = l.end.distance_to(incidence_point)
                if min(d_start, d_end) < 40.0:
                    mid_y = (l.start.y + l.end.y) / 2.0
                    if mid_y < bound_y and not incident_ray:
                        incident_ray = l
                    elif mid_y > bound_y and not refracted_ray:
                        refracted_ray = l

        return {
            "boundary_line": boundary_line,
            "normal_line": normal_line,
            "incidence_point": incidence_point,
            "incident_ray": incident_ray,
            "refracted_ray": refracted_ray,
            "bound_y": bound_y,
            "normal_x": normal_x,
        }

"""PR-06 Prism Classical CV Candidate Extractor.

Extracts deterministic geometric candidates for:
  - triangular prism body polygon
  - apex point
  - base line
  - incident ray path
  - internal ray path
  - emergent ray path
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourceLine, SourcePoint, SourcePolygon
from ai.evidence.cv.preprocessing import preprocess_for_geometry

logger = logging.getLogger(__name__)


class PrismCVCandidateExtractor:
    """Extracts geometric candidates for optical prism dispersion/deviation diagrams."""

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

        # 1. Detect Triangular Contour
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        prism_poly = None
        best_area = 0.0

        for c in contours:
            area = cv2.contourArea(c)
            if area > (w * h * 0.04):
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.04 * peri, True)
                # Triangle has 3 vertices (or approximated 3-4)
                if len(approx) in (3, 4) and area > best_area:
                    best_area = area
                    pts = [SourcePoint(float(p[0][0]), float(p[0][1])) for p in approx]
                    if len(pts) >= 3:
                        prism_poly = SourcePolygon(points=pts[:3])

        apex = None
        base_line = None
        if prism_poly:
            # Apex is highest point (min y)
            sorted_by_y = sorted(prism_poly.points, key=lambda p: p.y)
            apex = sorted_by_y[0]
            base_pts = sorted_by_y[1:3]
            base_line = SourceLine(start=base_pts[0], end=base_pts[1])

        # 2. Detect Ray Lines
        min_len = int(round(min(w, h) * 0.08))
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 25, minLineLength=min_len, maxLineGap=10)
        rays = []
        if lines is not None:
            for l in lines:
                pts = l.reshape(-1)
                rays.append(SourceLine(start=SourcePoint(float(pts[0]), float(pts[1])), end=SourcePoint(float(pts[2]), float(pts[3]))))

        return {
            "prism_polygon": prism_poly,
            "apex": apex,
            "base_line": base_line,
            "rays": rays,
        }

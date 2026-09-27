"""PR-06 Thin Lens Classical CV Candidate Extractor.

Extracts deterministic geometric candidates for:
  - optical axis (horizontal line spanning diagram)
  - lens center / vertical line
  - object arrow (vertical arrow)
  - image arrow (vertical arrow)
  - focal markers (tick marks / points along optical axis)
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


class ThinLensCVCandidateExtractor:
    """Extracts geometric candidates for thin lens ray diagrams."""

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
        hough_lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=30,
            minLineLength=min_len,
            maxLineGap=15,
        )

        raw_lines: List[SourceLine] = []
        if hough_lines is not None:
            for l in hough_lines:
                pts = l.reshape(-1)
                raw_lines.append(
                    SourceLine(
                        start=SourcePoint(float(pts[0]), float(pts[1])),
                        end=SourcePoint(float(pts[2]), float(pts[3])),
                    )
                )

        merged = merge_collinear_lines(raw_lines, dist_thresh=10.0, angle_thresh_deg=6.0)

        # 1. Optical Axis: long horizontal line near vertical center
        optical_axis = None
        best_axis_len = 0.0
        for l in merged:
            dy = abs(l.end.y - l.start.y)
            dx = abs(l.end.x - l.start.x)
            if dx > 0 and (dy / (dx + 1e-5)) < 0.10:
                mid_y = (l.start.y + l.end.y) / 2.0
                if abs(mid_y - h * 0.5) < h * 0.35 and l.length_px > best_axis_len:
                    best_axis_len = l.length_px
                    optical_axis = l

        axis_y = (optical_axis.start.y + optical_axis.end.y) / 2.0 if optical_axis else None

        # 2. Lens Body / Line: prominent vertical line intersecting optical axis near horizontal center
        lens_line = None
        best_lens_len = 0.0
        for l in merged:
            dy = abs(l.end.y - l.start.y)
            dx = abs(l.end.x - l.start.x)
            if dy > 0 and (dx / (dy + 1e-5)) < 0.15:  # predominantly vertical
                mid_x = (l.start.x + l.end.x) / 2.0
                if abs(mid_x - w * 0.5) < w * 0.35 and l.length_px > best_lens_len:
                    best_lens_len = l.length_px
                    lens_line = l

        lens_x = (lens_line.start.x + lens_line.end.x) / 2.0 if lens_line else None
        lens_center = (
            SourcePoint(float(lens_x), float(axis_y))
            if (lens_x is not None and axis_y is not None)
            else None
        )

        # 3. Object and Image Arrows (vertical lines away from lens center)
        vertical_arrows = []
        object_arrow = None
        image_arrow = None

        if lens_x is not None:
            for l in merged:
                if l == lens_line or l == optical_axis:
                    continue
                dy = abs(l.end.y - l.start.y)
                dx = abs(l.end.x - l.start.x)
                if dy > 0 and (dx / (dy + 1e-5)) < 0.20:
                    mid_x = (l.start.x + l.end.x) / 2.0
                    # Must be at least 25 px away from lens center
                    if abs(mid_x - lens_x) > 25.0:
                        vertical_arrows.append(l)

            left_arrows = [a for a in vertical_arrows if ((a.start.x + a.end.x) / 2.0) < lens_x]
            right_arrows = [a for a in vertical_arrows if ((a.start.x + a.end.x) / 2.0) > lens_x]

            if left_arrows:
                object_arrow = max(left_arrows, key=lambda a: a.length_px)
            if right_arrows:
                image_arrow = max(right_arrows, key=lambda a: a.length_px)

        return {
            "optical_axis": optical_axis,
            "lens_center": lens_center,
            "lens_line": lens_line,
            "object_arrow": object_arrow,
            "image_arrow": image_arrow,
            "all_lines": merged,
        }

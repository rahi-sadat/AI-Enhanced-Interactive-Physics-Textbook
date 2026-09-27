"""PR-06 Projectile Motion Classical CV Candidate Extractor.

Extracts deterministic geometric candidates for:
  - projectile launch point (origin)
  - ground reference line
  - projectile body candidate
  - initial velocity arrow / tangent line
  - trajectory parabolic arc / curve
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourceLine, SourcePoint
from ai.evidence.cv.geometry_helpers import fit_circle_subpixel, merge_collinear_lines
from ai.evidence.cv.preprocessing import preprocess_for_geometry

logger = logging.getLogger(__name__)


class ProjectileCVCandidateExtractor:
    """Extracts geometric candidates for 2D projectile diagrams."""

    def __init__(
        self,
        min_line_len_ratio: float = 0.05,
        canny_thresh1: int = 50,
        canny_thresh2: int = 150,
    ):
        self.min_line_len_ratio = min_line_len_ratio
        self.canny_thresh1 = canny_thresh1
        self.canny_thresh2 = canny_thresh2

    def extract(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        ocr_boxes: Optional[List[SourceBBox]] = None,
    ) -> Dict[str, Any]:
        h, w = image_bgr.shape[:2]
        gray, edges = preprocess_for_geometry(
            image_bgr,
            ocr_boxes=ocr_boxes,
            canny_thresh1=self.canny_thresh1,
            canny_thresh2=self.canny_thresh2,
        )

        min_len = int(round(min(w, h) * self.min_line_len_ratio))

        # 1. Detect straight line segments (ground line, launch velocity vector)
        hough_lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=25,
            minLineLength=min_len,
            maxLineGap=12,
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

        merged_lines = merge_collinear_lines(raw_lines, dist_thresh=8.0, angle_thresh_deg=7.0)

        # 2. Identify Ground Line (predominantly horizontal line near lower half)
        ground_line = None
        best_ground_len = 0.0
        for line in merged_lines:
            dy = abs(line.end.y - line.start.y)
            dx = abs(line.end.x - line.start.x)
            if dx > 0 and (dy / (dx + 1e-5)) < 0.25:  # almost horizontal
                mid_y = (line.start.y + line.end.y) / 2.0
                if mid_y > h * 0.3 and line.length_px > best_ground_len:
                    best_ground_len = line.length_px
                    ground_line = line

        # 3. Detect Projectile Body (small circular contour)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        body_candidates = []
        for c in contours:
            area = cv2.contourArea(c)
            if 15.0 <= area <= (w * h * 0.05):
                perim = cv2.arcLength(c, True)
                if perim > 0:
                    circularity = 4.0 * np.pi * area / (perim * perim)
                    if circularity >= 0.40:
                        (cx, cy), cr = cv2.minEnclosingCircle(c)
                        sub_cx, sub_cy, sub_cr = fit_circle_subpixel(edges, (cx, cy), cr)
                        body_candidates.append({
                            "center": SourcePoint(sub_cx, sub_cy),
                            "radius_px": float(sub_cr),
                            "circularity": circularity,
                            "bbox": SourceBBox(max(0, sub_cx - sub_cr), max(0, sub_cy - sub_cr), sub_cr * 2, sub_cr * 2),
                        })

        best_body = None
        if body_candidates:
            # Sort by circularity
            body_candidates.sort(key=lambda x: x["circularity"], reverse=True)
            best_body = body_candidates[0]

        # 4. Launch Point: strictly from detected projectile body or an angled launch/trajectory line touching ground
        launch_point: Optional[SourcePoint] = None
        if best_body:
            launch_point = best_body["center"]
        elif ground_line:
            angled_candidates = [
                l for l in merged_lines
                if l != ground_line and abs(l.end.y - l.start.y) > 10.0
            ]
            for l in angled_candidates:
                d1 = ground_line.distance_to_point(l.start)
                d2 = ground_line.distance_to_point(l.end)
                if min(d1, d2) < 20.0:
                    launch_point = l.start if d1 <= d2 else l.end
                    break

        # 5. Velocity Vector Line Candidate (angled line extending from launch point)
        velocity_vector_line = None
        if launch_point:
            best_dist = float("inf")
            for line in merged_lines:
                d_start = line.start.distance_to(launch_point)
                d_end = line.end.distance_to(launch_point)
                min_d = min(d_start, d_end)
                if min_d < 35.0 and line != ground_line:
                    if min_d < best_dist:
                        best_dist = min_d
                        # Orient line starting from launch point
                        if d_start <= d_end:
                            velocity_vector_line = line
                        else:
                            velocity_vector_line = SourceLine(start=line.end, end=line.start)

        return {
            "launch_point": launch_point,
            "ground_line": ground_line,
            "projectile_body": best_body,
            "velocity_vector": velocity_vector_line,
            "line_candidates": merged_lines,
        }

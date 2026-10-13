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
        # Suppress contours inside OCR boxes and contours below the ground line
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ground_y = (ground_line.start.y + ground_line.end.y) / 2.0 if ground_line else h * 0.75
        body_candidates = []
        for c in contours:
            area = cv2.contourArea(c)
            if 15.0 <= area <= (w * h * 0.05):
                (cx, cy), cr = cv2.minEnclosingCircle(c)
                # Ignore circles strictly below ground line (e.g. captions, hatching)
                if ground_line and cy > (ground_y + 20.0):
                    continue
                # Ignore circles inside OCR text boxes
                if ocr_boxes:
                    in_text = any(
                        b.x - 5 <= cx <= b.x + b.width + 5 and b.y - 5 <= cy <= b.y + b.height + 5
                        for b in ocr_boxes
                    )
                    if in_text:
                        continue
                perim = cv2.arcLength(c, True)
                if perim > 0:
                    circularity = 4.0 * np.pi * area / (perim * perim)
                    if circularity >= 0.35:
                        sub_cx, sub_cy, sub_cr = fit_circle_subpixel(edges, (cx, cy), cr)
                        body_candidates.append({
                            "center": SourcePoint(sub_cx, sub_cy),
                            "radius_px": max(float(sub_cr), 5.0),
                            "circularity": circularity,
                            "bbox": SourceBBox(max(0, sub_cx - sub_cr), max(0, sub_cy - sub_cr), sub_cr * 2, sub_cr * 2),
                        })

        # 4. Launch Point and Landing Point: from angled lines touching ground line
        launch_point: Optional[SourcePoint] = None
        landing_point: Optional[SourcePoint] = None
        velocity_vector_line: Optional[SourceLine] = None

        if ground_line:
            angled_candidates = [
                l for l in merged_lines
                if l != ground_line and abs(l.end.y - l.start.y) > 10.0 and abs(l.end.x - l.start.x) > 5.0
            ]

            ground_touching_lines = []
            for l in angled_candidates:
                d1 = ground_line.distance_to_point(l.start)
                d2 = ground_line.distance_to_point(l.end)
                min_d = min(d1, d2)
                touches_ground_at_start = (d1 <= d2)
                contact_pt = l.start if touches_ground_at_start else l.end
                other_pt = l.end if touches_ground_at_start else l.start
                if min_d < 35.0 and other_pt.y < contact_pt.y:
                    # Forward-pointing vector has other_pt.x > contact_pt.x
                    is_forward = (other_pt.x > contact_pt.x)
                    ground_touching_lines.append({
                        "line": l,
                        "contact_pt": contact_pt,
                        "other_pt": other_pt,
                        "min_d": min_d,
                        "is_forward": is_forward,
                    })

            if ground_touching_lines:
                # Forward-pointing vectors are launch vectors
                forward_lines = [g for g in ground_touching_lines if g["is_forward"]]
                backward_lines = [g for g in ground_touching_lines if not g["is_forward"]]

                if forward_lines:
                    # Sort by x coordinate (launch is leftmost)
                    forward_lines.sort(key=lambda g: g["contact_pt"].x)
                    best_launch = forward_lines[0]
                    launch_point = best_launch["contact_pt"]
                    velocity_vector_line = SourceLine(start=best_launch["contact_pt"], end=best_launch["other_pt"])
                else:
                    ground_touching_lines.sort(key=lambda g: g["contact_pt"].x)
                    best_launch = ground_touching_lines[0]
                    launch_point = best_launch["contact_pt"]
                    velocity_vector_line = SourceLine(start=best_launch["contact_pt"], end=best_launch["other_pt"])

                if backward_lines:
                    backward_lines.sort(key=lambda g: g["contact_pt"].x, reverse=True)
                    landing_point = backward_lines[0]["contact_pt"]

        best_body = None
        if body_candidates:
            if launch_point:
                # Prefer body closest to launch point
                body_candidates.sort(key=lambda b: b["center"].distance_to(launch_point))
                if body_candidates[0]["center"].distance_to(launch_point) < min(w, h) * 0.06:
                    best_body = body_candidates[0]
                    # Refine launch point to the body center
                    launch_point = best_body["center"]
            if not best_body:
                body_candidates.sort(key=lambda x: x["circularity"], reverse=True)
                best_body = body_candidates[0]
                if not launch_point:
                    launch_point = best_body["center"]

        # Fallback body if launch point exists but circle wasn't separated from line
        if launch_point and not best_body:
            best_body = {
                "center": launch_point,
                "radius_px": 15.0,
                "circularity": 0.8,
                "bbox": SourceBBox(launch_point.x - 15, launch_point.y - 15, 30, 30),
            }

        # OCR masks can cover the arrowhead and ground contact. Recover only a
        # geometrically supported launch from the unmasked edge map; never use
        # a text-box center or a fixed canvas coordinate as the launch point.
        if ocr_boxes:
            unmasked = self.extract(image_bgr, source_width=source_width,
                                    source_height=source_height, ocr_boxes=None)
            raw_launch = unmasked.get("launch_point")
            raw_ground = unmasked.get("ground_line")
            if raw_launch and raw_ground and unmasked.get("velocity_vector"):
                raw_ground_y = (raw_ground.start.y + raw_ground.end.y) / 2.0
                same_ground = (ground_line is None or abs(
                    raw_ground_y - (ground_line.start.y + ground_line.end.y) / 2.0
                ) <= h * 0.03)
                raw_contact = abs(raw_launch.y - raw_ground_y) <= max(8.0, h * 0.03)
                inconsistent = (launch_point is None or
                                raw_launch.distance_to(launch_point) > min(w, h) * 0.04)
                if same_ground and raw_contact and inconsistent:
                    launch_point = raw_launch
                    ground_line = raw_ground
                    velocity_vector_line = unmasked["velocity_vector"]
                    best_body = unmasked["projectile_body"]

        measured_range_px = None
        if launch_point and landing_point and landing_point.x > launch_point.x:
            measured_range_px = landing_point.x - launch_point.x
        elif ground_line and launch_point:
            # Trajectory typically spans ground line length
            gl_len = getattr(ground_line, "length_px", 0.0)
            if gl_len > 100:
                measured_range_px = gl_len * 0.85

        # 5. Detect Trajectory Arc & Apex Height
        measured_height_px = None
        apex_point = None
        if launch_point and ground_line:
            x_min = int(launch_point.x)
            x_max = int(landing_point.x) if (landing_point and landing_point.x > launch_point.x) else int(launch_point.x + (measured_range_px or (w * 0.75)))
            y_base = (ground_line.start.y + ground_line.end.y) / 2.0
            launch_y = launch_point.y if launch_point else y_base
            span = x_max - x_min
            if span > 80:
                search_x_start = int(x_min + span * 0.20)
                search_x_end = int(x_min + span * 0.80)
                y_upper_limit = max(0, int(launch_y - h * 0.75))
                y_lower_limit = max(0, int(launch_y - 15))

                sub_gray = gray[y_upper_limit:y_lower_limit, search_x_start:search_x_end]
                mask = (sub_gray < 110)
                if ocr_boxes:
                    for b in ocr_boxes:
                        bx1 = max(0, int(b.x - search_x_start))
                        bx2 = min(search_x_end - search_x_start, int(b.x + b.width - search_x_start))
                        by1 = max(0, int(b.y - y_upper_limit))
                        by2 = min(y_lower_limit - y_upper_limit, int(b.y + b.height - y_upper_limit))
                        if bx2 > bx1 and by2 > by1:
                            mask[by1:by2, bx1:bx2] = False

                dark_ys, dark_xs = np.where(mask)
                if len(dark_ys) > 0:
                    min_y_rel = np.min(dark_ys)
                    apex_candidates_x = dark_xs[dark_ys == min_y_rel]
                    apex_x = search_x_start + int(np.median(apex_candidates_x))
                    apex_y = y_upper_limit + int(min_y_rel)
                    h_cand = launch_y - apex_y
                    if h_cand > 25.0:
                        measured_height_px = float(h_cand)
                        apex_point = SourcePoint(float(apex_x), float(apex_y))

        return {
            "launch_point": launch_point,
            "landing_point": landing_point,
            "measured_range_px": measured_range_px,
            "measured_height_px": measured_height_px,
            "apex_point": apex_point,
            "ground_line": ground_line,
            "projectile_body": best_body,
            "velocity_vector": velocity_vector_line,
            "line_candidates": merged_lines,
        }

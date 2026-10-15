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
        ocr_tokens: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        h, w = image_bgr.shape[:2]
        gray, edges = preprocess_for_geometry(image_bgr, ocr_boxes=ocr_boxes)

        # Multi-scale line extraction:
        # Pass 1: Fine/medium lines (arrows, focal ticks, principal rays)
        min_len_fine = max(12, int(round(min(w, h) * 0.02)))
        hough_fine = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=18,
            minLineLength=min_len_fine,
            maxLineGap=12,
        )

        # Pass 2: Long structural lines (optical axis, lens line)
        min_len_coarse = int(round(min(w, h) * 0.10))
        hough_coarse = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=28,
            minLineLength=min_len_coarse,
            maxLineGap=16,
        )

        raw_lines: List[SourceLine] = []
        for hl in (hough_fine, hough_coarse):
            if hl is not None:
                for l in hl:
                    pts = l.reshape(-1)
                    raw_lines.append(
                        SourceLine(
                            start=SourcePoint(float(pts[0]), float(pts[1])),
                            end=SourcePoint(float(pts[2]), float(pts[3])),
                        )
                    )

        merged = merge_collinear_lines(raw_lines, dist_thresh=8.0, angle_thresh_deg=5.0)

        # 1. Optical Axis: horizontal line cluster near vertical center with maximum horizontal span across diagram
        clusters: List[Dict[str, Any]] = []
        for l in merged:
            dy = abs(l.end.y - l.start.y)
            dx = abs(l.end.x - l.start.x)
            if dx > 0 and (dy / (dx + 1e-5)) < 0.12:
                mid_y = (l.start.y + l.end.y) / 2.0
                if abs(mid_y - h * 0.5) < h * 0.35:
                    added = False
                    for c in clusters:
                        if abs(c["y"] - mid_y) < 12.0:
                            c["lines"].append(l)
                            c["min_x"] = min(c["min_x"], l.start.x, l.end.x)
                            c["max_x"] = max(c["max_x"], l.start.x, l.end.x)
                            c["total_len"] += l.length_px
                            added = True
                            break
                    if not added:
                        clusters.append({
                            "y": mid_y,
                            "min_x": min(l.start.x, l.end.x),
                            "max_x": max(l.start.x, l.end.x),
                            "total_len": l.length_px,
                            "lines": [l],
                        })

        optical_axis = None
        axis_y = None
        if clusters:
            best_cluster = max(
                clusters,
                key=lambda c: (c["max_x"] - c["min_x"]) - abs(c["y"] - h * 0.5) * 0.5,
            )
            axis_y = best_cluster["y"]
            optical_axis = SourceLine(
                start=SourcePoint(float(best_cluster["min_x"]), float(axis_y)),
                end=SourcePoint(float(best_cluster["max_x"]), float(axis_y)),
            )

        # 2. Lens Body / Line: prominent vertical line intersecting optical axis near horizontal center
        lens_line = None
        best_lens_len = 0.0
        for l in merged:
            dy = abs(l.end.y - l.start.y)
            dx = abs(l.end.x - l.start.x)
            if dy > 0 and (dx / (dy + 1e-5)) < 0.18:  # predominantly vertical
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
                if dy > 0 and (dx / (dy + 1e-5)) < 0.25 and l.length_px >= 18.0:
                    mid_x = (l.start.x + l.end.x) / 2.0
                    # Must be at least 20 px away from lens center
                    if abs(mid_x - lens_x) > 20.0:
                        vertical_arrows.append(l)

            left_arrows = [a for a in vertical_arrows if ((a.start.x + a.end.x) / 2.0) < lens_x]
            right_arrows = [a for a in vertical_arrows if ((a.start.x + a.end.x) / 2.0) > lens_x]

            # If OCR tokens are available, use text anchors to prioritize or find arrows
            obj_token_x = None
            img_token_x = None
            if ocr_tokens:
                for tok in ocr_tokens:
                    txt = (getattr(tok, "raw_text", "") or "").strip().lower()
                    b = getattr(tok, "bbox_source_px", None)
                    if not b:
                        continue
                    tcx = b.x + b.width / 2.0
                    if any(k in txt for k in ("object", "বস্তু", "লক্ষ্যবস্তু")) and tcx < lens_x:
                        obj_token_x = tcx
                    elif any(k in txt for k in ("image", "প্রতিবিম্ব", "বিম্ব")) and tcx > lens_x:
                        img_token_x = tcx

            if left_arrows:
                if obj_token_x is not None:
                    # Choose arrow nearest to the Object label
                    object_arrow = min(left_arrows, key=lambda a: abs(((a.start.x + a.end.x) / 2.0) - obj_token_x))
                else:
                    object_arrow = max(left_arrows, key=lambda a: a.length_px)

            if right_arrows:
                if img_token_x is not None:
                    image_arrow = min(right_arrows, key=lambda a: abs(((a.start.x + a.end.x) / 2.0) - img_token_x))
                else:
                    image_arrow = max(right_arrows, key=lambda a: a.length_px)

        # 4. Focal Markers (tick marks on the optical axis or points)
        focal_f1 = None
        focal_f2 = None
        focal_2f1 = None
        focal_2f2 = None
        focal_ticks = []
        if lens_x is not None and axis_y is not None:
            # A. Check for tick marks crossing or touching optical axis
            for l in raw_lines:
                if 3.0 <= l.length_px <= 35.0:
                    mid_y = (l.start.y + l.end.y) / 2.0
                    mid_x = (l.start.x + l.end.x) / 2.0
                    if abs(mid_y - axis_y) < 14.0 and abs(mid_x - lens_x) > 15.0:
                        focal_ticks.append(SourcePoint(x=mid_x, y=axis_y))

            left_ticks = [p for p in focal_ticks if p.x < lens_x]
            right_ticks = [p for p in focal_ticks if p.x > lens_x]
            if left_ticks:
                focal_f1 = min(left_ticks, key=lambda p: abs(p.x - lens_x))
            if right_ticks:
                focal_f2 = min(right_ticks, key=lambda p: abs(p.x - lens_x))

            # B. Ground focal markers from verified OCR tokens near the optical axis
            if ocr_tokens:
                for tok in ocr_tokens:
                    raw_t = (getattr(tok, "raw_text", "") or "").strip()
                    txt_u = raw_t.upper()
                    b = getattr(tok, "bbox_source_px", None)
                    if not b:
                        continue
                    tcx = b.x + b.width / 2.0
                    tcy = b.y + b.height / 2.0
                    # Must be near optical axis vertically
                    if abs(tcy - axis_y) < 70.0 and abs(tcx - lens_x) > 20.0:
                        is_2f = txt_u in ("2F", "2F1", "2F2", "2F'", "C", "C1", "C2")
                        is_f = (txt_u in ("F", "F1", "F2", "F'", "f") or raw_t in ("F", "F₁", "F₂", "f"))
                        if is_f and not is_2f:
                            if tcx < lens_x and (focal_f1 is None or abs(tcx - lens_x) < abs(focal_f1.x - lens_x)):
                                focal_f1 = SourcePoint(x=tcx, y=axis_y)
                            elif tcx > lens_x and (focal_f2 is None or abs(tcx - lens_x) < abs(focal_f2.x - lens_x)):
                                focal_f2 = SourcePoint(x=tcx, y=axis_y)
                        elif is_2f:
                            if tcx < lens_x:
                                focal_2f1 = SourcePoint(x=tcx, y=axis_y)
                            elif tcx > lens_x:
                                focal_2f2 = SourcePoint(x=tcx, y=axis_y)

        # 5. Principal Rays Detection
        principal_rays = {}
        if object_arrow is not None and lens_center is not None:
            obj_x = (object_arrow.start.x + object_arrow.end.x) / 2.0
            obj_tip_y = min(object_arrow.start.y, object_arrow.end.y)
            # Look for horizontal ray from object tip to lens
            for l in merged:
                if l == optical_axis or l == lens_line or l == object_arrow or l == image_arrow:
                    continue
                min_lx = min(l.start.x, l.end.x)
                max_lx = max(l.start.x, l.end.x)
                mid_ly = (l.start.y + l.end.y) / 2.0
                if abs(mid_ly - obj_tip_y) < 14.0 and min_lx <= obj_x + 20 and max_lx >= lens_x - 20:
                    principal_rays["ray_parallel"] = l
                    break

        # 6. Inverse Calibration & Mathematical Parameter Derivation
        fitted_parameters = {}
        if lens_center is not None:
            f_est = None

            # Source A: from grounded focal markers F1 or F2
            if focal_f1 is not None and abs(lens_center.x - focal_f1.x) > 10:
                f_est = abs(lens_center.x - focal_f1.x)
            elif focal_f2 is not None and abs(focal_f2.x - lens_center.x) > 10:
                f_est = abs(focal_f2.x - lens_center.x)

            # Source B: from 2F markers
            if f_est is None:
                if focal_2f1 is not None:
                    f_est = abs(lens_center.x - focal_2f1.x) / 2.0
                elif focal_2f2 is not None:
                    f_est = abs(focal_2f2.x - lens_center.x) / 2.0

            # Source C: from lens equation if both object and image arrows are present
            if object_arrow is not None:
                u_meas = lens_center.x - ((object_arrow.start.x + object_arrow.end.x) / 2.0)
                h_meas = abs(object_arrow.end.y - object_arrow.start.y)

                if f_est is None and image_arrow is not None:
                    v_meas = ((image_arrow.start.x + image_arrow.end.x) / 2.0) - lens_center.x
                    if v_meas > 0 and u_meas > 0:
                        f_est = (u_meas * v_meas) / (u_meas + v_meas)

                if f_est is not None and f_est > 0:
                    fitted_parameters = {
                        "focal_length_px": round(f_est, 2),
                        "object_distance_px": round(u_meas, 2),
                        "object_height_px": round(h_meas, 2),
                        "axis_y": round(axis_y, 2),
                        "lens_x": round(lens_center.x, 2),
                    }
                    if focal_f1 is None:
                        focal_f1 = SourcePoint(x=lens_center.x - f_est, y=axis_y)
                    if focal_f2 is None:
                        focal_f2 = SourcePoint(x=lens_center.x + f_est, y=axis_y)

        return {
            "optical_axis": optical_axis,
            "lens_center": lens_center,
            "lens_line": lens_line,
            "object_arrow": object_arrow,
            "image_arrow": image_arrow,
            "focal_F1": focal_f1,
            "focal_F2": focal_f2,
            "principal_rays": principal_rays,
            "fitted_parameters": fitted_parameters,
            "all_lines": merged,
        }

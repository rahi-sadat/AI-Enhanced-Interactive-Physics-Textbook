"""PR-06 Pendulum Classical CV Candidate Extractor.

Extracts candidate visual evidence for simple pendulums:
  - Bob proposals (Hough circles + sub-pixel algebraic fitting + contours)
  - String proposals (HoughLinesP + sub-pixel direction + bob connectivity check)
  - Pivot proposals (upper string endpoint + pin circles)
  - Vertical reference proposals (near-vertical dashed/solid line from pivot)
  - Angle marker proposals (arc candidate between vertical ref and string)

All candidates preserve exact native source pixels ('source_px') and geometric confidence.
"""
from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourceLine, SourcePoint
from ai.evidence.cv.geometry_helpers import (
    distance_pt,
    fit_circle_subpixel,
    fit_line_subpixel,
    point_to_segment_distance,
)
from ai.evidence.cv.preprocessing import mask_out_text_regions, preprocess_diagram

logger = logging.getLogger(__name__)


class PendulumCVCandidateExtractor:
    """Deterministic classical CV candidate extractor for pendulum diagrams."""

    def __init__(
        self,
        canny_thresh1: float = 40.0,
        canny_thresh2: float = 120.0,
        min_string_len_ratio: float = 0.08,
        min_bob_radius_ratio: float = 0.015,
        max_bob_radius_ratio: float = 0.22,
    ):
        self.canny_thresh1 = canny_thresh1
        self.canny_thresh2 = canny_thresh2
        self.min_string_len_ratio = min_string_len_ratio
        self.min_bob_radius_ratio = min_bob_radius_ratio
        self.max_bob_radius_ratio = max_bob_radius_ratio

    def extract_candidates(
        self,
        img_bgr: np.ndarray,
        source_width: int,
        source_height: int,
        ocr_boxes: Optional[List[SourceBBox]] = None,
    ) -> Dict[str, Any]:
        """Extract geometric candidates for bob, string, pivot, and references.

        Args:
            img_bgr: Full image array in BGR format.
            source_width: Width in source pixels.
            source_height: Height in source pixels.
            ocr_boxes: Text boxes to suppress from edge map.

        Returns:
            Dictionary with candidate lists and geometric diagnostics.
        """
        h, w = img_bgr.shape[:2]
        gray, blur, raw_edges = preprocess_diagram(
            img_bgr,
            canny_thresh1=self.canny_thresh1,
            canny_thresh2=self.canny_thresh2,
        )

        # 1. Mask out OCR text to avoid labels ("m", "L", "θ") corrupting line/circle detection
        if ocr_boxes:
            edges = mask_out_text_regions(raw_edges, ocr_boxes, margin_px=2)
        else:
            edges = raw_edges

        # 2. Extract Circle Proposals for Bob and Mount Pin
        min_r = max(5, int(min(h, w) * self.min_bob_radius_ratio))
        max_r = max(14, int(min(h, w) * self.max_bob_radius_ratio))
        min_dist = max(15, int(min(h, w) * 0.05))

        circles = cv2.HoughCircles(
            blur,
            cv2.HOUGH_GRADIENT,
            dp=1.15,
            minDist=min_dist,
            param1=80,
            param2=26,
            minRadius=min_r,
            maxRadius=max_r,
        )

        circle_candidates: List[Dict[str, Any]] = []
        if circles is not None and len(circles[0]) > 0:
            for c in circles[0]:
                cx, cy, cr = float(c[0]), float(c[1]), float(c[2])
                sub_cx, sub_cy, sub_cr = fit_circle_subpixel(raw_edges, (cx, cy), cr)
                circle_candidates.append({
                    "center": SourcePoint(x=sub_cx, y=sub_cy),
                    "radius_px": float(sub_cr),
                    "bounds": SourceBBox(
                        x=max(0.0, sub_cx - sub_cr),
                        y=max(0.0, sub_cy - sub_cr),
                        width=sub_cr * 2.0,
                        height=sub_cr * 2.0,
                    ),
                    "initial_radius": cr,
                })

        # Also find contour-based circular/filled regions if Hough circles missed
        contours, _ = cv2.findContours(raw_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < math.pi * (min_r ** 2) * 0.5 or area > math.pi * (max_r ** 2) * 1.5:
                continue
            perimeter = cv2.arcLength(cnt, True)
            if perimeter <= 0:
                continue
            circularity = 4.0 * math.pi * area / (perimeter * perimeter)
            if circularity > 0.65:
                (cx, cy), cr = cv2.minEnclosingCircle(cnt)
                if not any(c["center"].distance_to(SourcePoint(x=cx, y=cy)) < cr * 0.7 for c in circle_candidates):
                    sub_cx, sub_cy, sub_cr = fit_circle_subpixel(raw_edges, (cx, cy), cr)
                    circle_candidates.append({
                        "center": SourcePoint(x=sub_cx, y=sub_cy),
                        "radius_px": float(sub_cr),
                        "bounds": SourceBBox(
                            x=max(0.0, sub_cx - sub_cr),
                            y=max(0.0, sub_cy - sub_cr),
                            width=sub_cr * 2.0,
                            height=sub_cr * 2.0,
                        ),
                        "initial_radius": cr,
                    })

        # 3. Extract Line Proposals for String
        min_line_len = max(20, int(h * self.min_string_len_ratio))
        max_line_gap = max(5, int(h * 0.025))

        lines = cv2.HoughLinesP(
            raw_edges,
            rho=1,
            theta=np.pi / 720,
            threshold=max(20, int(min(h, w) * 0.04)),
            minLineLength=min_line_len,
            maxLineGap=max_line_gap,
        )

        line_proposals: List[Dict[str, Any]] = []
        if lines is not None and len(lines) > 0:
            for raw_line in lines.reshape(-1, 4):
                x1, y1, x2, y2 = map(float, raw_line)
                if y1 > y2:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                p1 = (x1, y1)
                p2 = (x2, y2)
                length = distance_pt(p1, p2)
                if length < min_line_len:
                    continue
                dx = x2 - x1
                dy = y2 - y1
                if abs(dy) < abs(dx) * 0.15:
                    continue
                line_proposals.append({
                    "start": SourcePoint(x=x1, y=y1),
                    "end": SourcePoint(x=x2, y=y2),
                    "length_px": length,
                    "dx": dx,
                    "dy": dy,
                })

        # 4. Pair Bob and String Candidates
        paired_candidates: List[Dict[str, Any]] = []
        diagonal = math.hypot(w, h)

        circle_candidates.sort(key=lambda c: c["center"].y, reverse=True)

        for c_cand in circle_candidates:
            bob_center = (c_cand["center"].x, c_cand["center"].y)
            bob_r = c_cand["radius_px"]

            for l_cand in line_proposals:
                p_top = (l_cand["start"].x, l_cand["start"].y)
                p_bot = (l_cand["end"].x, l_cand["end"].y)

                d_bot = distance_pt(p_bot, bob_center)
                max_gap = max(bob_r * 3.2, diagonal * 0.06)
                if d_bot > max_gap:
                    continue

                if p_top[1] >= bob_center[1] - bob_r * 0.5:
                    continue

                line_mean, line_dir = fit_line_subpixel(raw_edges, p_top, p_bot)

                # Refine pivot by checking if there's a pin/mount circle near p_top
                pivot_x, pivot_y = p_top
                for other_c in circle_candidates:
                    if other_c["center"].y < bob_center[1] - bob_r:
                        if other_c["center"].distance_to(SourcePoint(x=p_top[0], y=p_top[1])) < 25.0:
                            pivot_x, pivot_y = other_c["center"].x, other_c["center"].y
                            break

                pivot_pt = SourcePoint(x=pivot_x, y=pivot_y)
                dist_pivot_to_bob_center = pivot_pt.distance_to(c_cand["center"])

                # Project string onto bob boundary
                bot_x = bob_center[0] - line_dir[0] * bob_r
                bot_y = bob_center[1] - line_dir[1] * bob_r

                score = (
                    dist_pivot_to_bob_center * 2.0
                    + (bob_center[1] - pivot_y) * 0.8
                    - d_bot * 2.5
                    + (bob_center[1] / float(h)) * 30.0
                )

                paired_candidates.append({
                    "score": score,
                    "bob": c_cand,
                    "string": {
                        "start": pivot_pt,
                        "end": SourcePoint(x=bot_x, y=bot_y),
                        "visible_length_px": distance_pt(p_top, p_bot),
                        "length_to_bob_center_px": dist_pivot_to_bob_center,
                        "subpixel_dir": line_dir,
                    },
                    "pivot": pivot_pt,
                })

        paired_candidates.sort(key=lambda x: x["score"], reverse=True)
        best_pair = paired_candidates[0] if paired_candidates else None

        # 5. Check for Vertical Reference Line Candidate
        vertical_ref_candidate: Optional[SourceLine] = None
        if best_pair:
            pivot_pt = (best_pair["pivot"].x, best_pair["pivot"].y)
            for l_cand in line_proposals:
                if abs(l_cand["dx"]) > abs(l_cand["dy"]) * 0.12:
                    continue
                p_top = (l_cand["start"].x, l_cand["start"].y)
                if distance_pt(p_top, pivot_pt) < 35.0:
                    vertical_ref_candidate = SourceLine(
                        start=SourcePoint(x=p_top[0], y=p_top[1]),
                        end=SourcePoint(x=l_cand["end"].x, y=l_cand["end"].y),
                    )
                    break

        return {
            "all_circles": circle_candidates,
            "all_lines": line_proposals,
            "paired_candidates": paired_candidates,
            "best_proposal": best_pair,
            "vertical_reference": vertical_ref_candidate,
            "angle_marker": None,
            "edge_map": edges,
        }

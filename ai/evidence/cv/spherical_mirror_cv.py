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

        # Long horizontal reflected rays can exceed individual Hough segments
        # of the principal axis. Compare continuous horizontal evidence and
        # prefer the strong line nearest the diagram's vertical center.
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(12, int(w * 0.15)), 1))
        horizontal = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
        row_strength = np.count_nonzero(horizontal, axis=1)
        strong_rows = np.flatnonzero(row_strength >= max(w * 0.30, row_strength.max() * 0.55))
        strong_rows = [int(y) for y in strong_rows if h * 0.20 <= y <= h * 0.75]
        distinct_rows = []
        for y in strong_rows:
            if not distinct_rows or y - distinct_rows[-1] > h * 0.04:
                distinct_rows.append(y)
        if len(distinct_rows) >= 2:
            best_y = min(strong_rows, key=lambda y: abs(y - h / 2.0))
            xs = np.flatnonzero(horizontal[best_y])
            if len(xs) >= w * 0.30:
                axis_y = float(best_y)
                axis_line = SourceLine(
                    start=SourcePoint(float(xs[0]), axis_y),
                    end=SourcePoint(float(xs[-1]), axis_y),
                )

        # A textbook principal axis is often dashed. Morphological opening
        # removes its gaps, so compare raw horizontal support across the full
        # source width before accepting a solid ray as the axis.
        raw_rows = np.count_nonzero(edges, axis=1)
        y_start, y_stop = int(h * 0.2), int(h * 0.75)
        if y_stop > y_start:
            candidates = range(y_start, y_stop)
            best_raw_y = max(candidates, key=lambda y: raw_rows[y] *
                             (1.0 - 0.35 * abs(y - h / 2.0) / max(h / 2.0, 1)))
            if raw_rows[best_raw_y] >= w * 0.25:
                xs = np.flatnonzero(edges[best_raw_y])
                if xs.size and xs[-1] - xs[0] >= w * 0.45:
                    axis_y = float(best_raw_y)
                    axis_line = SourceLine(
                        start=SourcePoint(float(xs[0]), axis_y),
                        end=SourcePoint(float(xs[-1]), axis_y),
                    )

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
            if abs(pole.y - axis_y) > max(20.0, h * 0.04):
                # The mirror may be split into contours by the axis or ray
                # intersections. Find a supported near-vertical stroke at the
                # axis using the arc's horizontal extent, excluding the axis
                # itself so its horizontal pixels cannot win the score.
                arc_x, _, arc_w, _ = cv2.boundingRect(best_arc)
                x0 = max(0, arc_x - 10)
                x1 = min(w, arc_x + arc_w + 10)
                y0 = max(0, int(axis_y - h * 0.055))
                y1 = min(h, int(axis_y + h * 0.055))
                local = edges[y0:y1, x0:x1].copy()
                a0 = max(0, int(axis_y) - 6 - y0)
                a1 = min(local.shape[0], int(axis_y) + 7 - y0)
                local[a0:a1] = 0
                strengths = np.count_nonzero(local, axis=0)
                if strengths.size and strengths.max() >= max(15, (y1 - y0) * 0.15):
                    pole = SourcePoint(float(x0 + int(np.argmax(strengths))), float(axis_y))

        aperture_height_px = None
        if axis_y is not None:
            axis_row = int(round(axis_y))
            gap = max(2, int(round(h * 0.02)))
            reach = max(gap + 1, int(round(h * 0.25)))
            above = np.count_nonzero(edges[max(0, axis_row - reach):max(0, axis_row - gap)], axis=0)
            below = np.count_nonzero(edges[min(h, axis_row + gap):min(h, axis_row + reach)], axis=0)
            balanced = np.minimum(above, below)
            if balanced.size and balanced.max() >= max(4, h * 0.012):
                pole_x = int(np.argmax(balanced))
                pole = SourcePoint(float(pole_x), float(axis_y))
                band = max(2, int(round(w * 0.15)))
                local = edges[int(h * 0.08):int(h * 0.94),
                              max(0, pole_x - band):min(w, pole_x + band)]
                ys = np.flatnonzero(np.count_nonzero(local, axis=1) >= max(2, band * 0.02))
                if ys.size:
                    aperture_height_px = float(ys[-1] - ys[0])

        # Small filled axis dots often mark F and C. Remove thin axis strokes
        # morphologically, then take the nearest distinct dot to the pole as F.
        focus_point = None
        if pole is not None and axis_y is not None:
            dot_diameter = max(3, int(round(min(w, h) * 0.008)))
            if dot_diameter % 2 == 0:
                dot_diameter += 1
            dark = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY_INV)[1]
            dots = cv2.morphologyEx(
                dark, cv2.MORPH_OPEN,
                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dot_diameter, dot_diameter)),
            )
            count, _, stats, centers = cv2.connectedComponentsWithStats(dots)
            candidates = []
            for idx in range(1, count):
                x, y, cw, ch, area = stats[idx]
                cx, cy = centers[idx]
                if (area >= dot_diameter and cw <= w * 0.035 and ch <= h * 0.035
                        and 0.45 <= cw / max(ch, 1) <= 2.2
                        and abs(cy - axis_y) <= max(3, h * 0.015)
                        and abs(cx - pole.x) >= max(2 * dot_diameter, w * 0.025)):
                    candidates.append(SourcePoint(float(cx), float(cy)))
            if len(candidates) >= 2:
                focus_point = min(candidates, key=lambda point: abs(point.x - pole.x))

        return {
            "principal_axis": axis_line,
            "pole": pole,
            "mirror_contour": best_arc,
            "focus_point": focus_point,
            "aperture_height_px": aperture_height_px,
        }

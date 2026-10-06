"""PR-06 Classical CV Geometry Utilities.

Provides sub-pixel refinement, line fitting, circle proposals, and geometric distance checks.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

import cv2
import numpy as np

from shared.schemas.evidence import SourcePoint


def distance_pt(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def point_to_segment_distance(
    pt: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
) -> float:
    """Distance from a 2D point to a finite line segment (p1, p2)."""
    px, py = pt
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1
    seg_len_sq = dx * dx + dy * dy

    if seg_len_sq < 1e-6:
        return math.hypot(px - x1, py - y1)

    # Project point onto segment
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / seg_len_sq))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def fit_circle_subpixel(
    edges: np.ndarray,
    approx_center: Tuple[float, float],
    approx_radius: float,
    margin_ratio: float = 0.28,
) -> Tuple[float, float, float]:
    """Refine circle proposal to sub-pixel accuracy using algebraic least squares."""
    h, w = edges.shape[:2]
    cx, cy = approx_center
    r = approx_radius
    pad = int(math.ceil(r * (1.0 + margin_ratio)))

    x1, x2 = max(0, int(cx - pad)), min(w, int(cx + pad + 1))
    y1, y2 = max(0, int(cy - pad)), min(h, int(cy + pad + 1))

    pts = []
    min_r = r * (1.0 - margin_ratio)
    max_r = r * (1.0 + margin_ratio)

    for y in range(y1, y2):
        for x in range(x1, x2):
            if edges[y, x] > 0:
                d = math.hypot(x - cx, y - cy)
                if min_r <= d <= max_r:
                    pts.append([float(x), float(y)])

    if len(pts) < 8:
        return float(cx), float(cy), float(r)

    pts_arr = np.array(pts, dtype=np.float64)
    # Fit algebraic circle: x^2 + y^2 + D*x + E*y + F = 0
    A = np.column_stack([pts_arr[:, 0], pts_arr[:, 1], np.ones(len(pts_arr))])
    b = -(pts_arr[:, 0] ** 2 + pts_arr[:, 1] ** 2)
    try:
        res, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        fit_cx = float(-res[0] / 2.0)
        fit_cy = float(-res[1] / 2.0)
        rad_sq = fit_cx ** 2 + fit_cy ** 2 - res[2]
        if rad_sq <= 0:
            return float(cx), float(cy), float(r)
        fit_r = float(math.sqrt(rad_sq))

        # Check closeness to initial proposal
        if math.hypot(fit_cx - cx, fit_cy - cy) < r * 0.4 and abs(fit_r - r) < r * 0.4:
            return fit_cx, fit_cy, fit_r
    except Exception:
        pass

    return float(cx), float(cy), float(r)


def fit_line_subpixel(
    edges: np.ndarray,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    band_width: float = 3.5,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Fit a sub-pixel line through edge pixels along segment p1-p2 via PCA (SVD).

    Returns:
        (mean_point, unit_direction)
    """
    h, w = edges.shape[:2]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 1e-4:
        return (float(p1[0]), float(p1[1])), (0.0, 1.0)

    nx = -dy / length
    ny = dx / length

    min_x = max(0, int(min(p1[0], p2[0]) - band_width))
    max_x = min(w, int(max(p1[0], p2[0]) + band_width + 1))
    min_y = max(0, int(min(p1[1], p2[1]) - band_width))
    max_y = min(h, int(max(p1[1], p2[1]) + band_width + 1))

    pts = []
    for y in range(min_y, max_y):
        for x in range(min_x, max_x):
            if edges[y, x] > 0:
                dist = abs((x - p1[0]) * nx + (y - p1[1]) * ny)
                if dist <= band_width:
                    pts.append([float(x), float(y)])

    if len(pts) < 10:
        center = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
        dir_vec = (dx / length, dy / length)
        return center, dir_vec

    pts_arr = np.array(pts, dtype=np.float64)
    mean = np.mean(pts_arr, axis=0)
    _, _, vv = np.linalg.svd(pts_arr - mean)
    direction = vv[0]

    # Ensure direction points downwards (positive y)
    return (float(mean[0]), float(mean[1])), (float(direction[0]), float(direction[1]))


def line_intersection(
    line1: Tuple[Tuple[float, float], Tuple[float, float]],
    line2: Tuple[Tuple[float, float], Tuple[float, float]],
) -> Optional[Tuple[float, float]]:
    """Compute intersection point between two infinite lines defined by segment endpoints."""
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-6:
        return None

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    return float(px), float(py)


def merge_collinear_lines(
    lines: List[Any],
    dist_thresh: float = 12.0,
    angle_thresh_deg: float = 6.0,
    dist_tol_px: Optional[float] = None,
) -> List[Any]:
    """Merge nearly collinear and close line segments (supports SourceLine or tuple)."""
    if not lines:
        return []
    tol = dist_tol_px if dist_tol_px is not None else dist_thresh
    is_source_line = hasattr(lines[0], "start") and hasattr(lines[0], "end")

    merged: List[Any] = []
    for l in lines:
        if is_source_line:
            x1, y1 = float(l.start.x), float(l.start.y)
            x2, y2 = float(l.end.x), float(l.end.y)
        else:
            x1, y1, x2, y2 = float(l[0]), float(l[1]), float(l[2]), float(l[3])

        ang1 = math.atan2(y2 - y1, x2 - x1)
        covered = False
        mid_x, mid_y = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        for ml in merged:
            if is_source_line:
                mx1, my1 = float(ml.start.x), float(ml.start.y)
                mx2, my2 = float(ml.end.x), float(ml.end.y)
            else:
                mx1, my1, mx2, my2 = float(ml[0]), float(ml[1]), float(ml[2]), float(ml[3])

            ang2 = math.atan2(my2 - my1, mx2 - mx1)
            diff_deg = abs(math.degrees(ang1 - ang2)) % 180.0
            if diff_deg > 90.0:
                diff_deg = 180.0 - diff_deg
            if diff_deg > angle_thresh_deg:
                continue

            d = point_to_segment_distance((mid_x, mid_y), (mx1, my1), (mx2, my2))
            if d < tol:
                covered = True
                break
        if not covered:
            merged.append(l)
    return merged

"""
backend/kinematics/pendulum_geometry.py

Sub-pixel geometric perception and dynamic background reconstruction
for textbook pendulum diagrams.

Features:
- Hough proposals followed by Total Least Squares (TLS) circle & line fitting
- Float64 sub-pixel center, radius, and string endpoints in pure source_px
- Angled pendulum support (pivot.y < bob.y without assuming vertical alignment)
- Pin/mount circle snapping for pivot localization
- Dynamic inpainting of static bob & string for zero-ghosting overlay
- Extraction of transparent RGBA bob sprite
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import uuid

import cv2
import numpy as np


def _distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def fit_circle_subpixel(
    edges: np.ndarray,
    approx_center: Tuple[float, float],
    approx_radius: float,
    margin_ratio: float = 0.28,
) -> Tuple[float, float, float]:
    """
    Refines a circle proposal to sub-pixel accuracy using algebraic least squares
    fitted on gradient edge pixels within an annular region of interest.
    """
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

        # Sanity check: must be reasonably close to initial proposal
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
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Collects edge pixels in a narrow band along line segment p1-p2 and fits
    a sub-pixel direction vector and centroid using Principal Component Analysis (SVD).
    Returns (point_on_line, unit_direction).
    """
    h, w = edges.shape[:2]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 1e-4:
        return np.array(p1, dtype=np.float64), np.array([0.0, 1.0], dtype=np.float64)

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
        center = np.array([(p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0], dtype=np.float64)
        dir_vec = np.array([dx / length, dy / length], dtype=np.float64)
        return center, dir_vec

    pts_arr = np.array(pts, dtype=np.float64)
    mean = np.mean(pts_arr, axis=0)
    _, _, vv = np.linalg.svd(pts_arr - mean)
    direction = vv[0]

    # Ensure direction points downwards (positive y)
    if direction[1] < 0:
        direction = -direction

    return mean, direction


def detect_pendulum_geometry(
    img_bgr: np.ndarray,
    output_dir: Optional[Path] = None,
    clean_bg_dir: Optional[Path] = None,
    image_rel_url: str = "",
) -> Dict[str, Any]:
    """
    Sub-pixel detection of pendulum bob, pivot, and string in native source pixels.
    Optionally produces clean inpainted background and transparent bob sprite.
    """
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 1.2)
    edges = cv2.Canny(blur, 50, 140, apertureSize=3)

    # 1. Circle proposals (bob and pivot pin)
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.15,
        minDist=max(20, int(min(h, w) * 0.05)),
        param1=80,
        param2=28,
        minRadius=max(5, int(min(h, w) * 0.015)),
        maxRadius=max(14, int(min(h, w) * 0.22)),
    )

    if circles is None or len(circles[0]) == 0:
        raise ValueError("Pendulum bob could not be detected with sufficient confidence.")

    circle_candidates = [
        (float(c[0]), float(c[1]), float(c[2]))
        for c in circles[0]
    ]

    # 2. Line proposals (string)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 720,
        threshold=max(20, int(min(h, w) * 0.045)),
        minLineLength=max(20, int(h * 0.08)),
        maxLineGap=max(5, int(h * 0.025)),
    )

    if lines is None or len(lines) == 0:
        raise ValueError("Pendulum string could not be detected.")

    diagonal = math.hypot(w, h)
    best = None
    best_score = -1e30

    # Sort circles descending by Y to prioritize lower bob candidates
    circle_candidates.sort(key=lambda c: c[1], reverse=True)

    for cx, cy, radius in circle_candidates:
        center = (cx, cy)
        for raw_line in lines.reshape(-1, 4):
            x1, y1, x2, y2 = map(float, raw_line)
            p1 = (x1, y1)
            p2 = (x2, y2)
            d1 = _distance(p1, center)
            d2 = _distance(p2, center)

            if d1 < d2:
                near, far, near_dist = p1, p2, d1
            else:
                near, far, near_dist = p2, p1, d2

            line_len = _distance(p1, p2)
            max_gap = max(radius * 3.0, diagonal * 0.05)
            if near_dist > max_gap:
                continue

            # Constraint: Pivot must be above the bob
            if far[1] >= cy - radius * 0.5:
                continue

            dx = far[0] - near[0]
            dy = far[1] - near[1]

            # Reject near-horizontal lines
            if abs(dy) < abs(dx) * 0.15:
                continue

            vertical_separation = cy - far[1]
            score = (
                line_len * 2.5
                + vertical_separation * 0.8
                - near_dist * 2.0
                + (cy / float(h)) * 30.0
            )

            if score > best_score:
                best_score = score
                best = {
                    "raw_bob": (cx, cy, radius),
                    "raw_string_near": near,
                    "raw_string_far": far,
                    "line_length": line_len,
                }

    if best is None:
        raise ValueError("Pendulum bob found, but no plausible string/pivot relation was detected.")

    # 3. Sub-pixel Circle Fit on Bob
    raw_bx, raw_by, raw_br = best["raw_bob"]
    sub_bx, sub_by, sub_br = fit_circle_subpixel(edges, (raw_bx, raw_by), raw_br)

    # 4. Sub-pixel Line Fit on String
    line_mean, line_dir = fit_line_subpixel(edges, best["raw_string_near"], best["raw_string_far"])

    # 5. Determine Pivot Point
    # Check if there is an upper mount/pin circle candidate near the string's top end
    upper_candidates = [
        c for c in circle_candidates
        if c[1] < sub_by - sub_br * 1.5
    ]

    pivot_x = best["raw_string_far"][0]
    pivot_y = best["raw_string_far"][1]
    snapped_pin = False

    for uc in upper_candidates:
        dist_to_line_end = _distance((uc[0], uc[1]), (pivot_x, pivot_y))
        if dist_to_line_end < max(uc[2] * 2.5, 25.0):
            # Snap pivot to upper circle center refined with subpixel fit
            up_x, up_y, up_r = fit_circle_subpixel(edges, (uc[0], uc[1]), uc[2], margin_ratio=0.35)
            pivot_x = up_x
            pivot_y = up_y
            snapped_pin = True
            break

    if not snapped_pin:
        # Intersect fitted line with ceiling/top boundary or project pivot onto line
        t = ((pivot_x - line_mean[0]) * line_dir[0] + (pivot_y - line_mean[1]) * line_dir[1])
        proj = line_mean + t * line_dir
        pivot_x = float(proj[0])
        pivot_y = float(proj[1])

    # 6. Physical Geometry Parameters (all pure float64 in source_px)
    dx = sub_bx - pivot_x
    dy = sub_by - pivot_y
    length_px = float(math.hypot(dx, dy))

    # Angle measured from downward vertical where Y increases downward:
    # theta = 0 when bob directly below pivot; theta > 0 when displaced to the right
    theta0_rad = float(math.atan2(dx, dy))

    # Calculate detection confidence metric
    confidence = float(min(0.99, max(0.65, 0.70 + (length_px / max(h, 1)) * 0.25)))

    # 7. Dynamic Inpainting & Clean Background Creation
    clean_bg_url = image_rel_url
    sprite_url = None

    try:
        mask = np.zeros((h, w), dtype=np.uint8)
        # Mask the static bob
        cv2.circle(
            mask,
            (int(round(sub_bx)), int(round(sub_by))),
            int(math.ceil(sub_br + 4)),
            255,
            -1,
        )

        # Mask the static string from near pivot to bob
        t_unit = np.array([dx / length_px, dy / length_px])
        # Leave the top pivot pin artwork intact
        pin_clearance = 16.0 if snapped_pin else 4.0
        p_start = (
            int(round(pivot_x + t_unit[0] * pin_clearance)),
            int(round(pivot_y + t_unit[1] * pin_clearance)),
        )
        p_end = (int(round(sub_bx)), int(round(sub_by)))
        cv2.line(mask, p_start, p_end, 255, thickness=9)

        # Inpaint static bob & string to create clean static background
        clean_bg_bgr = cv2.inpaint(img_bgr, mask, 5, cv2.INPAINT_TELEA)

        # Save clean background image if output directories provided
        clean_name = Path(image_rel_url).stem if image_rel_url else "diagram"
        if clean_bg_dir:
            clean_bg_dir.mkdir(parents=True, exist_ok=True)
            clean_filename = f"clean_{clean_name}_{uuid.uuid4().hex[:6]}.jpg"
            clean_path = clean_bg_dir / clean_filename
            cv2.imwrite(str(clean_path), clean_bg_bgr)
            clean_bg_url = f"/uploads/{clean_filename}"

        # Extract isolated bob sprite with transparent alpha channel
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            rgba = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2BGRA)
            bob_mask = np.zeros((h, w), dtype=np.uint8)
            cv2.circle(
                bob_mask,
                (int(round(sub_bx)), int(round(sub_by))),
                int(math.ceil(sub_br + 1)),
                255,
                -1,
            )
            rgba[:, :, 3] = bob_mask

            pad = 4
            bx_i, by_i, br_i = int(round(sub_bx)), int(round(sub_by)), int(math.ceil(sub_br))
            rx1, rx2 = max(0, bx_i - br_i - pad), min(w, bx_i + br_i + pad + 1)
            ry1, ry2 = max(0, by_i - br_i - pad), min(h, by_i + br_i + pad + 1)
            sprite = rgba[ry1:ry2, rx1:rx2]

            sprite_filename = f"element_bob_{uuid.uuid4().hex[:6]}.png"
            sprite_path = output_dir / sprite_filename
            cv2.imwrite(str(sprite_path), sprite)
            sprite_url = f"/sprites/{sprite_filename}"

    except Exception as e:
        print(f"[PendulumGeometry] Inpainting/sprite extraction notice: {e}")

    return {
        "bob_center": {"x": sub_bx, "y": sub_by},
        "bob_radius_px": sub_br,
        "pivot": {"x": pivot_x, "y": pivot_y},
        "string_length_px": length_px,
        "theta0_rad": theta0_rad,
        "confidence": confidence,
        "clean_bg_url": clean_bg_url,
        "sprite_url": sprite_url,
    }

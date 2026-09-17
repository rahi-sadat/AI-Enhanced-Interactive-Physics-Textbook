"""Optics-specific geometry extraction.

Builds on top of the shared geometry_utils.extract_geometry() to provide
optical-domain measurements: lens center, aperture height, arrow tip/base,
prism vertices, mirror curvature, and classical CV optical-axis detection.

The general GeometryBundle is always computed first (via SAM mask), then
these functions add domain-specific structure on top.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

# Ensure backend/core is on the path for shared imports.
_BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BACKEND_DIR / "core"))

from geometry_utils import GeometryBundle, extract_geometry  # noqa: E402


# ---------------------------------------------------------------------------
# Dataclasses for optics geometry results
# ---------------------------------------------------------------------------

@dataclass
class LensGeometry:
    """Geometry extracted from a segmented lens mask."""
    optical_center: Dict[str, float]          # {"x": ..., "y": ...}
    aperture_height_px: float                 # vertical extent of the lens
    axis_angle_deg: float                     # 0 = horizontal optical axis
    bbox: Dict[str, float]                    # {"x", "y", "width", "height"}

    def to_dict(self) -> dict:
        return {
            "optical_center": self.optical_center,
            "aperture_height_px": self.aperture_height_px,
            "axis_angle_deg": self.axis_angle_deg,
            "bbox": self.bbox,
        }


@dataclass
class ArrowGeometry:
    """Geometry extracted from a segmented object-arrow mask."""
    base: Dict[str, float]                    # {"x": ..., "y": ...}
    tip: Dict[str, float]                     # {"x": ..., "y": ...}
    height_px: float                          # |tip.y - base.y|

    def to_dict(self) -> dict:
        return {
            "base": self.base,
            "tip": self.tip,
            "height_px": self.height_px,
        }


@dataclass
class PrismGeometry:
    """Geometry extracted from a segmented prism mask."""
    vertices: List[Dict[str, float]]          # 3 principal vertices
    apex_angle_deg: float                     # angle at the apex vertex

    def to_dict(self) -> dict:
        return {
            "vertices": self.vertices,
            "apex_angle_deg": self.apex_angle_deg,
        }


@dataclass
class MirrorGeometry:
    """Geometry extracted from a segmented mirror mask."""
    pole: Dict[str, float]                    # pole position
    aperture_height_px: float
    curvature_radius_px: Optional[float]      # None if could not be estimated
    concavity: str                            # "concave" | "convex" | "plane"

    def to_dict(self) -> dict:
        return {
            "pole": self.pole,
            "aperture_height_px": self.aperture_height_px,
            "curvature_radius_px": self.curvature_radius_px,
            "concavity": self.concavity,
        }


@dataclass
class OpticalAxis:
    """A detected or manually placed optical axis line."""
    start: Dict[str, float]
    end: Dict[str, float]
    angle_deg: float

    def to_dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "angle_deg": self.angle_deg,
        }


# ---------------------------------------------------------------------------
# Lens geometry
# ---------------------------------------------------------------------------

def extract_lens_geometry(
    mask: np.ndarray,
    image_shape: Tuple[int, int],
) -> LensGeometry:
    """Extract optical center and aperture height from a SAM lens mask.

    For NCTB thin-lens diagrams, we only need the center point and the
    vertical aperture. The thin-lens formula handles the physics — we
    do NOT fit the exact curvature of the glass surfaces.

    Parameters
    ----------
    mask : 2D bool/uint8 array — the accepted SAM mask for the lens.
    image_shape : (H, W) of the source image.

    Returns
    -------
    LensGeometry with optical center, aperture, axis angle, and bbox.
    """
    mask_u8 = np.asarray(mask).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("No contour found in lens mask.")
    contour = max(contours, key=cv2.contourArea)

    # Bounding box
    x, y, w, h = cv2.boundingRect(contour)
    bbox = {"x": float(x), "y": float(y), "width": float(w), "height": float(h)}

    # Optical center = centroid of the mask
    moments = cv2.moments(contour)
    if moments["m00"] == 0:
        cx, cy = float(x + w / 2), float(y + h / 2)
    else:
        cx = float(moments["m10"] / moments["m00"])
        cy = float(moments["m01"] / moments["m00"])

    # Aperture height = the vertical extent of the lens body
    aperture_height = float(h)

    # Oriented bounding box to get axis angle
    rect = cv2.minAreaRect(contour)
    rect_w, rect_h = rect[1]
    angle = float(rect[2])
    # Normalize: a lens is taller than wide, so the axis is perpendicular
    # to the long edge. For a vertically-oriented lens the optical axis is horizontal.
    if rect_w > rect_h:
        # Long edge is horizontal → lens is lying down → axis is horizontal
        axis_angle = angle
    else:
        # Long edge is vertical → lens is upright → axis is horizontal (perpendicular)
        axis_angle = angle + 90.0 if angle < 0 else angle - 90.0
    # Normalize to [-90, 90)
    while axis_angle >= 90.0:
        axis_angle -= 180.0
    while axis_angle < -90.0:
        axis_angle += 180.0

    return LensGeometry(
        optical_center={"x": cx, "y": cy},
        aperture_height_px=aperture_height,
        axis_angle_deg=axis_angle,
        bbox=bbox,
    )


# ---------------------------------------------------------------------------
# Arrow / Object geometry
# ---------------------------------------------------------------------------

def extract_arrow_geometry(
    mask: np.ndarray,
    image_shape: Tuple[int, int],
    optical_axis_y: Optional[float] = None,
) -> ArrowGeometry:
    """Extract base and tip positions from an object-arrow mask.

    Uses the skeleton polyline from extract_geometry(). The endpoint
    closest to the optical axis (or the bottom) is the base; the other
    is the tip.

    Parameters
    ----------
    mask : 2D mask of the arrow.
    image_shape : (H, W).
    optical_axis_y : Y-coordinate of the optical axis (if known).
                     Used to decide which end is the base.
    """
    bundle = extract_geometry(mask)
    skeleton = bundle.skeleton_polyline_px

    if len(skeleton) >= 2:
        # Use skeleton endpoints
        p0 = skeleton[0]
        p1 = skeleton[-1]
    else:
        # Fall back to bounding box top-center and bottom-center
        bbox = bundle.bbox_px
        p0 = {"x": bbox["x"] + bbox["width"] / 2, "y": bbox["y"]}
        p1 = {"x": bbox["x"] + bbox["width"] / 2, "y": bbox["y"] + bbox["height"]}

    # Assign base/tip: base is closer to the optical axis (or lower in image)
    if optical_axis_y is not None:
        dist0 = abs(p0["y"] - optical_axis_y)
        dist1 = abs(p1["y"] - optical_axis_y)
        if dist0 <= dist1:
            base, tip = p0, p1
        else:
            base, tip = p1, p0
    else:
        # Default: base is the lower point (larger y in image coordinates)
        if p0["y"] >= p1["y"]:
            base, tip = p0, p1
        else:
            base, tip = p1, p0

    height = abs(tip["y"] - base["y"])

    return ArrowGeometry(
        base={"x": base["x"], "y": base["y"]},
        tip={"x": tip["x"], "y": tip["y"]},
        height_px=height,
    )


# ---------------------------------------------------------------------------
# Prism geometry
# ---------------------------------------------------------------------------

def _angle_between_vectors(v1: np.ndarray, v2: np.ndarray) -> float:
    """Angle between two 2D vectors in degrees."""
    cos_a = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12)
    return float(math.degrees(math.acos(np.clip(cos_a, -1.0, 1.0))))


def extract_prism_geometry(mask: np.ndarray) -> PrismGeometry:
    """Extract the 3 principal vertices of a triangular prism from its mask.

    Simplifies the convex hull to 3 vertices. The apex is identified as the
    vertex with the smallest interior angle.
    """
    mask_u8 = np.asarray(mask).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("No contour found in prism mask.")
    contour = max(contours, key=cv2.contourArea)

    hull = cv2.convexHull(contour)
    perimeter = max(float(cv2.arcLength(hull, True)), 1.0)

    # Aggressively simplify hull to exactly 3 vertices
    ratio = 0.01
    approx = hull
    for _ in range(40):
        approx = cv2.approxPolyDP(hull, ratio * perimeter, True)
        if len(approx) <= 3:
            break
        ratio *= 1.3

    pts = approx.reshape(-1, 2).astype(float)
    if len(pts) < 3:
        # Fall back: take 3 most separated points from hull
        hull_pts = hull.reshape(-1, 2).astype(float)
        # Pick the point farthest from centroid, then farthest from that, etc.
        c = hull_pts.mean(axis=0)
        dists = np.linalg.norm(hull_pts - c, axis=1)
        i0 = int(np.argmax(dists))
        dists = np.linalg.norm(hull_pts - hull_pts[i0], axis=1)
        i1 = int(np.argmax(dists))
        dists = np.linalg.norm(hull_pts - hull_pts[i0], axis=1) + np.linalg.norm(
            hull_pts - hull_pts[i1], axis=1
        )
        i2 = int(np.argmax(dists))
        pts = hull_pts[[i0, i1, i2]]

    pts = pts[:3]
    vertices = [{"x": float(p[0]), "y": float(p[1])} for p in pts]

    # Find apex = vertex with smallest interior angle
    angles = []
    for i in range(3):
        v1 = pts[(i - 1) % 3] - pts[i]
        v2 = pts[(i + 1) % 3] - pts[i]
        angles.append(_angle_between_vectors(v1, v2))

    apex_idx = int(np.argmin(angles))
    apex_angle = angles[apex_idx]

    # Reorder so apex is first
    reordered = [vertices[apex_idx]] + [v for j, v in enumerate(vertices) if j != apex_idx]

    return PrismGeometry(
        vertices=reordered,
        apex_angle_deg=apex_angle,
    )


# ---------------------------------------------------------------------------
# Mirror geometry
# ---------------------------------------------------------------------------

def extract_mirror_geometry(mask: np.ndarray) -> MirrorGeometry:
    """Extract pole, aperture, and curvature from a mirror mask.

    Fits the skeleton polyline (the mirror's curved surface) to a circular
    arc to estimate radius of curvature. Determines concavity by checking
    whether the center of curvature is on the reflective side.
    """
    bundle = extract_geometry(mask)
    bbox = bundle.bbox_px
    cx, cy = bundle.centroid_px

    aperture_height = float(bbox["height"])

    # The pole is the point on the mirror closest to the center of curvature,
    # which for a vertically-oriented mirror is the leftmost or rightmost point.
    mask_u8 = np.asarray(mask).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour = max(contours, key=cv2.contourArea)
    contour_pts = contour.reshape(-1, 2).astype(float)

    # Pole = the point with extreme x (leftmost for right-facing mirror,
    # rightmost for left-facing). Use the centroid-relative position.
    left_x = float(contour_pts[:, 0].min())
    right_x = float(contour_pts[:, 0].max())

    # Determine orientation: if the mirror is thinner on the left, pole is on the left
    left_margin = cx - left_x
    right_margin = right_x - cx

    if left_margin <= right_margin:
        pole_x = left_x
        # Find y at that x
        at_pole = contour_pts[contour_pts[:, 0] <= left_x + 2]
        pole_y = float(at_pole[:, 1].mean()) if len(at_pole) > 0 else cy
    else:
        pole_x = right_x
        at_pole = contour_pts[contour_pts[:, 0] >= right_x - 2]
        pole_y = float(at_pole[:, 1].mean()) if len(at_pole) > 0 else cy

    # Try to fit a circle to the skeleton/contour to estimate curvature
    curvature_radius = None
    concavity = "plane"

    skeleton = bundle.skeleton_polyline_px
    fit_pts = np.array([[p["x"], p["y"]] for p in skeleton], dtype=np.float32) if len(skeleton) >= 5 else contour_pts

    if len(fit_pts) >= 5:
        try:
            # Least-squares circle fit
            A = np.column_stack([2 * fit_pts[:, 0], 2 * fit_pts[:, 1], np.ones(len(fit_pts))])
            b = fit_pts[:, 0] ** 2 + fit_pts[:, 1] ** 2
            result, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
            circle_cx, circle_cy = float(result[0]), float(result[1])
            r_sq = result[2] + circle_cx ** 2 + circle_cy ** 2
            if r_sq > 0:
                curvature_radius = float(math.sqrt(r_sq))

                # Concavity: if the center of curvature is on the reflective
                # side (same side as the object), it's concave.
                # For a mirror with pole on the left, center of curvature on the right → concave
                if pole_x <= cx:
                    concavity = "concave" if circle_cx > pole_x else "convex"
                else:
                    concavity = "concave" if circle_cx < pole_x else "convex"
        except (np.linalg.LinAlgError, ValueError):
            pass

    # If curvature radius is unreasonably large compared to aperture, treat as plane
    if curvature_radius is not None and curvature_radius > aperture_height * 20:
        curvature_radius = None
        concavity = "plane"

    return MirrorGeometry(
        pole={"x": pole_x, "y": pole_y},
        aperture_height_px=aperture_height,
        curvature_radius_px=curvature_radius,
        concavity=concavity,
    )


# ---------------------------------------------------------------------------
# Optical axis detection (classical CV)
# ---------------------------------------------------------------------------

def detect_optical_axis(
    image_gray: np.ndarray,
    known_centers: Optional[List[Dict[str, float]]] = None,
    angle_tolerance_deg: float = 10.0,
) -> Optional[OpticalAxis]:
    """Detect the dominant horizontal line that serves as the optical axis.

    Uses Hough line detection and filters for near-horizontal lines passing
    close to known optical element centers (lens center, mirror pole, etc.).

    Parameters
    ----------
    image_gray : Grayscale image (H, W).
    known_centers : List of {"x": ..., "y": ...} dicts for optical elements.
    angle_tolerance_deg : Max deviation from horizontal to accept as axis.

    Returns
    -------
    OpticalAxis if a suitable line is found, else None.
    """
    if image_gray is None or image_gray.size == 0:
        return None

    # Edge detection
    edges = cv2.Canny(image_gray, 50, 150, apertureSize=3)

    # Probabilistic Hough lines
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=80,
        minLineLength=image_gray.shape[1] * 0.2,
        maxLineGap=20,
    )

    if lines is None:
        return None

    h, w = image_gray.shape[:2]
    best_line = None
    best_score = -1.0

    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx = float(x2 - x1)
        dy = float(y2 - y1)
        length = math.hypot(dx, dy)
        if length < 10:
            continue

        angle = math.degrees(math.atan2(abs(dy), abs(dx)))
        if angle > angle_tolerance_deg:
            continue

        # Score: prefer longer lines closer to known optical centers
        score = length / w

        if known_centers:
            mid_y = (y1 + y2) / 2.0
            min_dist = min(abs(mid_y - c["y"]) for c in known_centers)
            proximity_bonus = max(0.0, 1.0 - min_dist / (h * 0.1))
            score += proximity_bonus

        if score > best_score:
            best_score = score
            best_line = (x1, y1, x2, y2)

    if best_line is None:
        return None

    x1, y1, x2, y2 = best_line
    dx = float(x2 - x1)
    dy = float(y2 - y1)
    angle_deg = math.degrees(math.atan2(dy, dx))

    # Extend the axis line to span the full image width
    if abs(dx) > 1e-6:
        slope = dy / dx
        ext_y_at_0 = y1 - slope * x1
        ext_y_at_w = y1 + slope * (w - 1 - x1)
    else:
        ext_y_at_0 = float(y1)
        ext_y_at_w = float(y2)

    return OpticalAxis(
        start={"x": 0.0, "y": ext_y_at_0},
        end={"x": float(w - 1), "y": ext_y_at_w},
        angle_deg=angle_deg,
    )

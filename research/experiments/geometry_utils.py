from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from collections import deque
from typing import Dict, List, Tuple

import cv2
import numpy as np


@dataclass
class GeometryBundle:
    area_px2: float
    perimeter_px: float
    centroid_px: Tuple[float, float]
    bbox_px: Dict[str, float]
    oriented_bbox_px: Dict[str, float]
    circle_fit_px: Dict[str, float]
    shape_hints: Dict[str, float]
    contour_px: List[Dict[str, float]]
    polygon_px: List[Dict[str, float]]
    convex_collision_polygon_px: List[Dict[str, float]]
    skeleton_polyline_px: List[Dict[str, float]]

    def to_dict(self) -> dict:
        return asdict(self)


def _largest_contour(mask_u8: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("No contour found in accepted mask.")
    return max(contours, key=cv2.contourArea)


def _normalize_rect_angle(box_points: np.ndarray) -> Tuple[float, float, float]:
    pts = np.asarray(box_points, dtype=np.float32)
    edges = []
    for i in range(4):
        vec = pts[(i + 1) % 4] - pts[i]
        edges.append((float(np.linalg.norm(vec)), vec))
    edges.sort(key=lambda item: item[0], reverse=True)
    long_edge, vec = edges[0]
    short_edge = edges[-1][0]
    angle = math.degrees(math.atan2(float(vec[1]), float(vec[0])))
    while angle >= 90.0:
        angle -= 180.0
    while angle < -90.0:
        angle += 180.0
    return long_edge, short_edge, angle


def _simplify_contour(contour: np.ndarray, target_vertices: int = 40) -> np.ndarray:
    perimeter = max(float(cv2.arcLength(contour, True)), 1.0)
    ratio = 0.0015
    approx = contour
    for _ in range(24):
        approx = cv2.approxPolyDP(contour, ratio * perimeter, True)
        if 3 <= len(approx) <= target_vertices:
            break
        ratio *= 1.25
    return approx.reshape(-1, 2)


def _simplify_hull(contour: np.ndarray, target_vertices: int = 24) -> np.ndarray:
    hull = cv2.convexHull(contour)
    perimeter = max(float(cv2.arcLength(hull, True)), 1.0)
    ratio = 0.0015
    approx = hull
    for _ in range(24):
        approx = cv2.approxPolyDP(hull, ratio * perimeter, True)
        if 3 <= len(approx) <= target_vertices:
            break
        ratio *= 1.25
    return approx.reshape(-1, 2)


def _morphological_skeleton(mask_u8: np.ndarray) -> np.ndarray:
    image = (mask_u8 > 0).astype(np.uint8) * 255
    skeleton = np.zeros_like(image)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    # Bound iterations for pathological giant masks.
    for _ in range(max(image.shape)):
        eroded = cv2.erode(image, element)
        opened = cv2.dilate(eroded, element)
        residue = cv2.subtract(image, opened)
        skeleton = cv2.bitwise_or(skeleton, residue)
        image = eroded
        if cv2.countNonZero(image) == 0:
            break
    return skeleton


def _neighbors(pixel: Tuple[int, int], points_set: set[Tuple[int, int]]):
    y, x = pixel
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            candidate = (y + dy, x + dx)
            if candidate in points_set:
                yield candidate


def _bfs_farthest(start: Tuple[int, int], points_set: set[Tuple[int, int]]):
    queue = deque([start])
    parent = {start: None}
    distance = {start: 0}
    farthest = start
    while queue:
        current = queue.popleft()
        if distance[current] > distance[farthest]:
            farthest = current
        for nb in _neighbors(current, points_set):
            if nb in parent:
                continue
            parent[nb] = current
            distance[nb] = distance[current] + 1
            queue.append(nb)
    return farthest, parent, distance


def _trace_skeleton_polyline(skeleton: np.ndarray, max_points: int = 200) -> List[Dict[str, float]]:
    ys, xs = np.nonzero(skeleton > 0)
    if len(xs) < 2 or len(xs) > 20000:
        return []

    points_set = set(zip(ys.tolist(), xs.tolist()))
    # Use a two-sweep graph diameter approximation. It also works when no endpoint exists.
    start = next(iter(points_set))
    a, _, _ = _bfs_farthest(start, points_set)
    b, parent, _ = _bfs_farthest(a, points_set)

    path = []
    current = b
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()

    if len(path) < 2:
        return []

    arr = np.array([[x, y] for y, x in path], dtype=np.float32).reshape(-1, 1, 2)
    epsilon = max(1.0, 0.004 * cv2.arcLength(arr, False))
    simplified = cv2.approxPolyDP(arr, epsilon, False).reshape(-1, 2)

    if len(simplified) > max_points:
        indexes = np.linspace(0, len(simplified) - 1, max_points).astype(int)
        simplified = simplified[indexes]

    return [{"x": float(x), "y": float(y)} for x, y in simplified]


def extract_geometry(mask: np.ndarray) -> GeometryBundle:
    mask_bool = np.asarray(mask).astype(bool)
    if mask_bool.ndim != 2:
        raise ValueError(f"Expected a 2D mask, got {mask_bool.shape}")

    mask_u8 = mask_bool.astype(np.uint8) * 255
    contour = _largest_contour(mask_u8)
    area = float(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))
    if area <= 0 or perimeter <= 0:
        raise ValueError("Accepted mask does not contain usable geometry.")

    moments = cv2.moments(contour)
    cx = float(moments["m10"] / moments["m00"]) if moments["m00"] else 0.0
    cy = float(moments["m01"] / moments["m00"]) if moments["m00"] else 0.0

    x, y, w, h = cv2.boundingRect(contour)
    bbox = {"x": float(x), "y": float(y), "width": float(w), "height": float(h)}

    rect = cv2.minAreaRect(contour)
    rect_box = cv2.boxPoints(rect)
    long_edge, short_edge, angle = _normalize_rect_angle(rect_box)
    oriented_bbox = {
        "center_x": cx,
        "center_y": cy,
        "width": float(long_edge),
        "height": float(short_edge),
        "angle_deg": float(angle),
    }

    (circle_x, circle_y), enclosing_radius = cv2.minEnclosingCircle(contour)
    equivalent_radius = math.sqrt(area / math.pi)
    circle_area = math.pi * max(enclosing_radius, 1e-6) ** 2
    circle_fill_ratio = float(np.clip(area / circle_area, 0.0, 1.0))

    rect_area = max(long_edge * short_edge, 1e-6)
    rectangularity = float(np.clip(area / rect_area, 0.0, 1.0))
    circularity = float(np.clip((4.0 * math.pi * area) / (perimeter * perimeter), 0.0, 1.0))
    aspect_ratio = float(long_edge / max(short_edge, 1e-6))

    circle_fit = {
        "center_x": float(circle_x),
        "center_y": float(circle_y),
        "enclosing_radius": float(enclosing_radius),
        "equivalent_radius": float(equivalent_radius),
        "fill_ratio": circle_fill_ratio,
    }

    contour_points = contour.reshape(-1, 2)
    contour_json = [{"x": float(px), "y": float(py)} for px, py in contour_points]

    polygon = _simplify_contour(contour, target_vertices=40)
    polygon_json = [{"x": float(px), "y": float(py)} for px, py in polygon]

    hull = _simplify_hull(contour, target_vertices=24)
    hull_json = [{"x": float(px), "y": float(py)} for px, py in hull]

    skeleton = _morphological_skeleton(mask_u8)
    skeleton_polyline = _trace_skeleton_polyline(skeleton)

    shape_hints = {
        # Hints only. They are never used to decide physics semantics in the canonical JSON.
        "circularity": circularity,
        "circle_fill_ratio": circle_fill_ratio,
        "rectangularity": rectangularity,
        "aspect_ratio": aspect_ratio,
    }

    return GeometryBundle(
        area_px2=area,
        perimeter_px=perimeter,
        centroid_px=(cx, cy),
        bbox_px=bbox,
        oriented_bbox_px=oriented_bbox,
        circle_fit_px=circle_fit,
        shape_hints=shape_hints,
        contour_px=contour_json,
        polygon_px=polygon_json,
        convex_collision_polygon_px=hull_json,
        skeleton_polyline_px=skeleton_polyline,
    )

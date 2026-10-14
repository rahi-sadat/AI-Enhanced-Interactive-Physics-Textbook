"""PR-06 Prism Classical CV Candidate Extractor.

Extracts deterministic geometric candidates for:
  - triangular prism body polygon
  - apex point
  - base line
  - incident ray path
  - internal ray path
  - emergent ray path
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourceLine, SourcePoint, SourcePolygon
from ai.evidence.cv.preprocessing import preprocess_for_geometry

logger = logging.getLogger(__name__)


class PrismCVCandidateExtractor:
    """Extracts geometric candidates for optical prism dispersion/deviation diagrams."""

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

        # 1. Detect Triangular Contour
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        prism_poly = None
        best_area = 0.0

        for c in contours:
            area = cv2.contourArea(c)
            if area > (w * h * 0.04):
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.04 * peri, True)
                # Triangle has 3 vertices (or approximated 3-4)
                if len(approx) in (3, 4) and area > best_area:
                    best_area = area
                    pts = [SourcePoint(float(p[0][0]), float(p[0][1])) for p in approx]
                    if len(pts) >= 3:
                        prism_poly = SourcePolygon(points=pts[:3])

        apex = None
        base_line = None
        if prism_poly:
            # Apex is highest point (min y)
            sorted_by_y = sorted(prism_poly.points, key=lambda p: p.y)
            apex = sorted_by_y[0]
            base_pts = sorted_by_y[1:3]
            base_line = SourceLine(start=base_pts[0], end=base_pts[1])

        # 2. Detect Ray Lines and Hough Line Fallback
        min_len = int(round(min(w, h) * 0.08))
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 25, minLineLength=min_len, maxLineGap=10)
        rays = []
        if lines is not None:
            for l in lines:
                pts = l.reshape(-1)
                rays.append(SourceLine(start=SourcePoint(float(pts[0]), float(pts[1])), end=SourcePoint(float(pts[2]), float(pts[3]))))

        # 3. Robust Hough Lines Clustering Fallback for Triangle Detection
        if prism_poly is None and lines is not None:
            left_lines = []
            right_lines = []

            for l in lines:
                pts_arr = l.reshape(-1)
                x1, y1, x2, y2 = float(pts_arr[0]), float(pts_arr[1]), float(pts_arr[2]), float(pts_arr[3])
                length = float(np.hypot(x2 - x1, y2 - y1))
                angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
                if angle > 90.0:
                    angle -= 180.0
                elif angle < -90.0:
                    angle += 180.0

                if -78.0 < angle < -42.0 and min(x1, x2) < 0.65 * w:
                    left_lines.append((x1, y1, x2, y2, length, angle))
                elif 42.0 < angle < 78.0 and max(x1, x2) > 0.35 * w:
                    right_lines.append((x1, y1, x2, y2, length, angle))

            def _filter_dominant(line_grp):
                if not line_grp:
                    return []
                med_ang = float(np.median([item[5] for item in line_grp]))
                return [item for item in line_grp if abs(item[5] - med_ang) <= 3.5]

            left_lines = _filter_dominant(left_lines)
            right_lines = _filter_dominant(right_lines)

            def _fit_line(line_list):
                pts_list = []
                for lx1, ly1, lx2, ly2, _, _ in line_list:
                    pts_list.append([lx1, ly1])
                    pts_list.append([lx2, ly2])
                arr = np.array(pts_list, dtype=np.float32)
                vx, vy, x0, y0 = cv2.fitLine(arr, cv2.DIST_L2, 0, 0.01, 0.01)
                return float(vx[0]), float(vy[0]), float(x0[0]), float(y0[0])

            def _intersect(l1, l2):
                vx1, vy1, x1, y1 = l1
                vx2, vy2, x2, y2 = l2
                det = vx1 * (-vy2) - vy1 * (-vx2)
                if abs(det) < 1e-5:
                    return None
                t1 = ((x2 - x1) * (-vy2) - (y2 - y1) * (-vx2)) / det
                return float(x1 + t1 * vx1), float(y1 + t1 * vy1)

            if len(left_lines) >= 2 and len(right_lines) >= 2:
                l_fit = _fit_line(left_lines)
                r_fit = _fit_line(right_lines)
                apex_pt = _intersect(l_fit, r_fit)

                left_max_y = max(max(ly1, ly2) for _, ly1, _, ly2, _, _ in left_lines)
                right_max_y = max(max(ly1, ly2) for _, ly1, _, ly2, _, _ in right_lines)
                base_y = (left_max_y + right_max_y) / 2.0
                base_line_fit = (1.0, 0.0, 0.0, base_y)

                v_left = _intersect(l_fit, base_line_fit)
                v_right = _intersect(r_fit, base_line_fit)

                if apex_pt and v_left and v_right:
                    tri_pts = [
                        SourcePoint(round(apex_pt[0], 1), round(apex_pt[1], 1)),
                        SourcePoint(round(v_left[0], 1), round(v_left[1], 1)),
                        SourcePoint(round(v_right[0], 1), round(v_right[1], 1)),
                    ]
                    if 0 <= tri_pts[0].y < tri_pts[1].y <= h * 1.05 and tri_pts[1].x < tri_pts[2].x:
                        prism_poly = SourcePolygon(points=tri_pts)
                        apex = tri_pts[0]
                        base_line = SourceLine(start=tri_pts[1], end=tri_pts[2])

        # 4. Extract Leftmost Incident Ray
        incident_ray = None
        if prism_poly and rays:
            # Ray should be on the left of apex and pointing toward the prism
            ray_cands = []
            for r in rays:
                rx1, ry1 = float(r.start.x), float(r.start.y)
                rx2, ry2 = float(r.end.x), float(r.end.y)
                if rx1 > rx2:
                    rx1, ry1, rx2, ry2 = rx2, ry2, rx1, ry1
                dx = rx2 - rx1
                dy = ry2 - ry1
                angle = float(np.degrees(np.arctan2(dy, dx)))
                # Incident ray striking left face: x < apex.x, angle roughly between -25 and +15, moving right
                if min(rx1, rx2) < apex.x and dx > 20 and -25.0 <= angle <= 15.0:
                    # Ignore lines that are part of base or text underlines
                    if ry1 < (base_line.start.y - 40 if base_line else h * 0.8):
                        ray_cands.append((rx1, ry1, rx2, ry2, dx, dy, angle))

            if ray_cands:
                # Select the leftmost segment that extends furthest
                ray_cands.sort(key=lambda item: (item[0], -item[4]))
                best = ray_cands[0]
                incident_ray = SourceLine(
                    start=SourcePoint(best[0], best[1]),
                    end=SourcePoint(best[2], best[3]),
                )

        if incident_ray is None and ocr_boxes:
            unmasked = self.extract(
                image_bgr,
                source_width=source_width,
                source_height=source_height,
                ocr_boxes=None,
            )
            if unmasked.get("incident_ray"):
                incident_ray = unmasked["incident_ray"]

        return {
            "prism_polygon": prism_poly,
            "apex": apex,
            "base_line": base_line,
            "rays": rays,
            "incident_ray": incident_ray,
        }

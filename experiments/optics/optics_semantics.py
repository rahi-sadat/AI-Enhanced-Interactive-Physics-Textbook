"""
experiments/optics/optics_semantics.py
Semantic binding, validation, and calibration rules for optical scenes:
- Binds F and 2F points to left (F1, 2F1) and right (F2, 2F2) of the lens center
- Calculates inferred pixel focal length from geometric spacing
- Calculates pixel-to-cm calibration factor when textual values exist
- Annotates parameters with provenance metadata
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple


def bind_focal_points(
    detected_labels: List[dict],
    lens_center_x: float,
    axis_y: float
) -> Tuple[List[dict], Optional[float]]:
    """
    Classify detected F / 2F labels into F1, 2F1 (left) and F2, 2F2 (right)
    relative to lens optical center.
    Computes inferred pixel focal length from the geometric distances.
    """
    f_candidates_left = []
    f_candidates_right = []
    two_f_left = []
    two_f_right = []

    for item in detected_labels:
        lbl = item["label"].upper()
        px = item["position"]["x"]

        if "2F" in lbl:
            if px < lens_center_x:
                two_f_left.append(item)
            else:
                two_f_right.append(item)
        elif "F" in lbl:
            if px < lens_center_x:
                f_candidates_left.append(item)
            else:
                f_candidates_right.append(item)

    bound_annotations = []
    focal_distances = []

    # Process F1 (left)
    if f_candidates_left:
        best_f1 = min(f_candidates_left, key=lambda it: abs(it["position"]["x"] - lens_center_x))
        bound_annotations.append({
            "label": "F1",
            "position": {"x": round(best_f1["position"]["x"], 1), "y": round(axis_y, 1)},
            "confidence": best_f1.get("confidence", 0.92),
        })
        focal_distances.append(abs(best_f1["position"]["x"] - lens_center_x))

    # Process F2 (right)
    if f_candidates_right:
        best_f2 = min(f_candidates_right, key=lambda it: abs(it["position"]["x"] - lens_center_x))
        bound_annotations.append({
            "label": "F2",
            "position": {"x": round(best_f2["position"]["x"], 1), "y": round(axis_y, 1)},
            "confidence": best_f2.get("confidence", 0.92),
        })
        focal_distances.append(abs(best_f2["position"]["x"] - lens_center_x))

    # Process 2F1 (left)
    if two_f_left:
        best_2f1 = max(two_f_left, key=lambda it: abs(it["position"]["x"] - lens_center_x))
        bound_annotations.append({
            "label": "2F1",
            "position": {"x": round(best_2f1["position"]["x"], 1), "y": round(axis_y, 1)},
            "confidence": best_2f1.get("confidence", 0.90),
        })
        focal_distances.append(abs(best_2f1["position"]["x"] - lens_center_x) / 2.0)

    # Process 2F2 (right)
    if two_f_right:
        best_2f2 = max(two_f_right, key=lambda it: abs(it["position"]["x"] - lens_center_x))
        bound_annotations.append({
            "label": "2F2",
            "position": {"x": round(best_2f2["position"]["x"], 1), "y": round(axis_y, 1)},
            "confidence": best_2f2.get("confidence", 0.90),
        })
        focal_distances.append(abs(best_2f2["position"]["x"] - lens_center_x) / 2.0)

    # Inferred focal length
    inferred_f_px = None
    if focal_distances:
        inferred_f_px = round(sum(focal_distances) / len(focal_distances), 1)

    return bound_annotations, inferred_f_px


def calibrate_scale(
    focal_length_px: Optional[float],
    physical_params: dict
) -> Optional[dict]:
    """
    If textual focal length exists in physical_params (e.g. 20 cm) and pixel focal length
    is inferred, calculates pixels_per_cm calibration scale.
    """
    if not focal_length_px:
        return None

    f_cm_meta = physical_params.get("focal_length_cm")
    if not f_cm_meta or not f_cm_meta.get("value"):
        return None

    f_cm = float(f_cm_meta["value"])
    if f_cm <= 0:
        return None

    px_per_cm = focal_length_px / f_cm
    return {
        "value": round(px_per_cm, 3),
        "unit": "pixels_per_cm",
        "source": "focal_length_ocr_and_geometry_ratio",
        "confidence": round(f_cm_meta.get("confidence", 0.9) * 0.95, 2),
    }

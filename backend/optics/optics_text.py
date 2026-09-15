"""OCR label detection and physical-unit calibration for optics diagrams.

Detects and localises text labels commonly found on NCTB optics diagrams:
F, 2F, O, focal-length values, refractive-index values.

Phase 1:  Manual click-placement for F / 2F annotation points.
Phase 4+: Cloud Vision / Tesseract OCR integration (stubbed here).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class DetectedLabel:
    """A text label detected or manually placed on the diagram."""
    text: str                     # "F", "2F", "O", "20 cm", "μ = 1.5"
    center: Dict[str, float]      # {"x": ..., "y": ...}
    bbox: Dict[str, float]        # {"x", "y", "width", "height"}
    confidence: float             # 0.0–1.0
    source: str                   # "manual" | "template" | "ocr"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FocalPointSet:
    """Classified focal / double-focal points relative to an optical center."""
    F1: Optional[Dict[str, float]] = None       # left of center
    F2: Optional[Dict[str, float]] = None       # right of center
    TwoF1: Optional[Dict[str, float]] = None    # 2F left
    TwoF2: Optional[Dict[str, float]] = None    # 2F right
    focal_length_px: Optional[float] = None
    focal_length_source: Optional[str] = None   # "F1_F2_geometry" | "manual" | None
    focal_length_confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "F1": self.F1,
            "F2": self.F2,
            "2F1": self.TwoF1,
            "2F2": self.TwoF2,
            "focal_length_px": {
                "value": self.focal_length_px,
                "source": self.focal_length_source,
                "confidence": self.focal_length_confidence,
            },
        }


@dataclass
class PixelScale:
    """Pixel-to-physical-unit calibration."""
    pixels_per_cm: Optional[float] = None
    source: Optional[str] = None            # "focal_length_calibration" | None
    status: str = "unresolved"              # "calibrated" | "unresolved"

    def to_dict(self) -> dict:
        return {
            "pixels_per_cm": {
                "value": self.pixels_per_cm,
                "source": self.source,
            } if self.pixels_per_cm is not None else None,
            "status": self.status,
        }


# ---------------------------------------------------------------------------
# Manual label creation helpers (Phase 1 — author clicks in GUI)
# ---------------------------------------------------------------------------

def create_manual_label(
    text: str,
    x: float,
    y: float,
    marker_size: float = 12.0,
) -> DetectedLabel:
    """Create a DetectedLabel from a manual click in the authoring GUI."""
    half = marker_size / 2.0
    return DetectedLabel(
        text=text,
        center={"x": x, "y": y},
        bbox={
            "x": x - half,
            "y": y - half,
            "width": marker_size,
            "height": marker_size,
        },
        confidence=1.0,
        source="manual",
    )


# ---------------------------------------------------------------------------
# Focal-point classification
# ---------------------------------------------------------------------------

import math
import statistics

def project_distance_on_axis(
    point: Dict[str, float],
    origin: Dict[str, float],
    axis_angle_deg: float = 0.0,
) -> float:
    """Project displacement vector between point and origin onto the optical axis line."""
    angle_rad = math.radians(axis_angle_deg)
    ux = math.cos(angle_rad)
    uy = math.sin(angle_rad)
    dx = float(point["x"] - origin["x"])
    dy = float(point["y"] - origin["y"])
    return dx * ux + dy * uy


def infer_focal_length_px(
    optical_center: Dict[str, float],
    F1: Optional[Dict[str, float]] = None,
    F2: Optional[Dict[str, float]] = None,
    TwoF1: Optional[Dict[str, float]] = None,
    TwoF2: Optional[Dict[str, float]] = None,
    axis_angle_deg: float = 0.0,
) -> dict:
    """Robust multi-evidence focal length inference from F1, F2, 2F1, and 2F2 markers."""
    candidates = []

    if F1 is not None:
        dist = abs(project_distance_on_axis(F1, optical_center, axis_angle_deg))
        if dist > 1.0:
            candidates.append((dist, "F1"))

    if F2 is not None:
        dist = abs(project_distance_on_axis(F2, optical_center, axis_angle_deg))
        if dist > 1.0:
            candidates.append((dist, "F2"))

    if TwoF1 is not None:
        dist = abs(project_distance_on_axis(TwoF1, optical_center, axis_angle_deg)) / 2.0
        if dist > 1.0:
            candidates.append((dist, "2F1"))

    if TwoF2 is not None:
        dist = abs(project_distance_on_axis(TwoF2, optical_center, axis_angle_deg)) / 2.0
        if dist > 1.0:
            candidates.append((dist, "2F2"))

    if not candidates:
        return {
            "value": None,
            "status": "unresolved",
            "confidence": 0.0,
            "sources": [],
            "uncertainty": None,
        }

    values = [item[0] for item in candidates]
    focal_px = float(statistics.median(values))

    if len(values) > 1:
        deviations = [abs(v - focal_px) / max(focal_px, 1e-6) for v in values]
        mean_error = sum(deviations) / len(deviations)
        confidence = max(0.0, min(0.99, 1.0 - mean_error))
        uncertainty = float(statistics.stdev(values)) if len(values) >= 2 else float(mean_error * focal_px)
    else:
        confidence = 0.75
        uncertainty = float(focal_px * 0.05)

    return {
        "value": focal_px,
        "focal_length_px": focal_px,
        "status": "observed",
        "confidence": round(confidence, 3),
        "sources": [item[1] for item in candidates],
        "uncertainty": round(uncertainty, 2),
    }


def classify_focal_points(
    labels: List[DetectedLabel],
    optical_center_x: float,
    optical_center_y: float = 300.0,
    axis_angle_deg: float = 0.0,
) -> FocalPointSet:
    """Assign detected / manually placed F and 2F labels to F1, F2, 2F1, 2F2.

    Convention:
      F1  = focal point LEFT of the optical center
      F2  = focal point RIGHT of the optical center
      2F1 = double focal distance LEFT
      2F2 = double focal distance RIGHT
    """
    result = FocalPointSet()
    oc = {"x": optical_center_x, "y": optical_center_y}

    f_labels = [lb for lb in labels if lb.text.upper() == "F"]
    twof_labels = [lb for lb in labels if lb.text.upper() == "2F"]

    f_labels.sort(key=lambda lb: lb.center["x"])
    twof_labels.sort(key=lambda lb: lb.center["x"])

    for lb in f_labels:
        if lb.center["x"] < optical_center_x:
            if result.F1 is None:
                result.F1 = lb.center
        else:
            if result.F2 is None:
                result.F2 = lb.center

    for lb in twof_labels:
        if lb.center["x"] < optical_center_x:
            if result.TwoF1 is None:
                result.TwoF1 = lb.center
        else:
            if result.TwoF2 is None:
                result.TwoF2 = lb.center

    inferred = infer_focal_length_px(
        optical_center=oc,
        F1=result.F1,
        F2=result.F2,
        TwoF1=result.TwoF1,
        TwoF2=result.TwoF2,
        axis_angle_deg=axis_angle_deg,
    )

    result.focal_length_px = inferred["value"]
    result.focal_length_source = "+".join(inferred["sources"]) if inferred["sources"] else None
    result.focal_length_confidence = inferred["confidence"]

    return result


# ---------------------------------------------------------------------------
# Pixel-to-physical calibration
# ---------------------------------------------------------------------------

def infer_pixel_scale(
    focal_length_px: Optional[float],
    focal_length_text_cm: Optional[float],
) -> PixelScale:
    """If both pixel and physical focal lengths are known, compute px/cm scale.

    Parameters
    ----------
    focal_length_px : Focal length measured in pixels (from F1/F2 positions).
    focal_length_text_cm : Focal length in cm as stated in the textbook text.

    Returns
    -------
    PixelScale with calibration or "unresolved" status.
    """
    if (
        focal_length_px is not None
        and focal_length_text_cm is not None
        and focal_length_text_cm > 0
        and focal_length_px > 0
    ):
        px_per_cm = focal_length_px / focal_length_text_cm
        return PixelScale(
            pixels_per_cm=px_per_cm,
            source="focal_length_calibration",
            status="calibrated",
        )

    return PixelScale()


# ---------------------------------------------------------------------------
# OCR stub (Phase 4 — Cloud Vision / Tesseract integration)
# ---------------------------------------------------------------------------

def detect_text_values_ocr(image_gray) -> List[DetectedLabel]:
    """Detect numeric values with units from the image using OCR.

    Phase 4 stub — returns an empty list.
    When integrated, this will use Google Cloud Vision or Tesseract to detect:
      - "20 cm", "f = 15 cm", "μ = 1.5", etc.
    """
    return []


def detect_focal_labels_ocr(image_gray, optical_center_x: float) -> List[DetectedLabel]:
    """Detect F and 2F text labels near the optical axis using OCR.

    Phase 4 stub — returns an empty list.
    When integrated, this will find small 'F' and '2F' glyphs
    and return their bounding-box positions.
    """
    return []

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

def classify_focal_points(
    labels: List[DetectedLabel],
    optical_center_x: float,
) -> FocalPointSet:
    """Assign detected / manually placed F and 2F labels to F1, F2, 2F1, 2F2.

    Convention:
      F1  = focal point LEFT of the optical center
      F2  = focal point RIGHT of the optical center
      2F1 = double focal distance LEFT
      2F2 = double focal distance RIGHT

    Parameters
    ----------
    labels : List of DetectedLabel with text in {"F", "2F"}.
    optical_center_x : X-coordinate of the lens / mirror center.

    Returns
    -------
    FocalPointSet with assigned positions and inferred focal length.
    """
    result = FocalPointSet()

    f_labels = [lb for lb in labels if lb.text.upper() == "F"]
    twof_labels = [lb for lb in labels if lb.text.upper() == "2F"]

    # Sort F labels by x-position
    f_labels.sort(key=lambda lb: lb.center["x"])
    twof_labels.sort(key=lambda lb: lb.center["x"])

    # Assign F1 (left) and F2 (right)
    for lb in f_labels:
        if lb.center["x"] < optical_center_x:
            if result.F1 is None:
                result.F1 = lb.center
        else:
            if result.F2 is None:
                result.F2 = lb.center

    # Assign 2F1 (left) and 2F2 (right)
    for lb in twof_labels:
        if lb.center["x"] < optical_center_x:
            if result.TwoF1 is None:
                result.TwoF1 = lb.center
        else:
            if result.TwoF2 is None:
                result.TwoF2 = lb.center

    # Infer focal length in pixels from F positions
    distances = []
    if result.F1 is not None:
        distances.append(abs(optical_center_x - result.F1["x"]))
    if result.F2 is not None:
        distances.append(abs(result.F2["x"] - optical_center_x))

    if distances:
        result.focal_length_px = sum(distances) / len(distances)
        result.focal_length_source = "F1_F2_geometry"
        # Confidence: higher if F1 and F2 are consistent
        if len(distances) == 2:
            ratio = min(distances) / max(max(distances), 1e-6)
            result.focal_length_confidence = float(min(1.0, 0.7 + 0.3 * ratio))
        else:
            result.focal_length_confidence = 0.75

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

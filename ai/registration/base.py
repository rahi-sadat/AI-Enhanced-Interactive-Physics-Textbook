"""Inputs and centralized policy for initial source-image registration.

Predictions are supplied by solver adapters, never manufactured from observations
inside the gate. This module contains no physics equations or image I/O.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field

import numpy as np

from shared.schemas.evidence import SourceLine, SourcePoint


@dataclass(frozen=True)
class RegistrationThresholds:
    landmark_preferred_px: float = 3.0
    landmark_warning_px: float = 5.0
    line_mean_px: float = 3.0
    line_p95_px: float = 5.0
    curve_mean_px: float = 3.0
    curve_p95_px: float = 5.0
    minimum_mask_iou: float = 0.85
    minimum_evidence_confidence: float = 0.8
    sample_spacing_px: float = 1.0
    max_samples: int = 10000

    def __post_init__(self):
        for name, value in asdict(self).items():
            if name == "max_samples":
                if type(value) is not int or value < 2:
                    raise ValueError("max_samples must be an integer >= 2")
            elif type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a positive finite number")
        if self.landmark_preferred_px > self.landmark_warning_px:
            raise ValueError("Preferred landmark bound must not exceed warning bound")
        if self.minimum_mask_iou > 1 or self.minimum_evidence_confidence > 1:
            raise ValueError("IoU and confidence thresholds must be <= 1")

    def to_dict(self):
        return asdict(self)


@dataclass
class PredictedGeometry:
    """Independently produced model geometry at t=0, using observed feature IDs.

    Points may fall outside the source image: those are measurable model errors,
    not observations to clip/rescale. Raster masks must cover the full native
    canvas; the gate does not fetch URLs, decode RLE, or compare bounding boxes as
    masks. Parameters remain in the caller's candidate/solver, not a second
    physics implementation here. The caller is responsible for predicting from
    the candidate being evaluated and rerunning after candidate edits.
    """
    source_asset_id: str
    figure_id: str
    source_width: int
    source_height: int
    domain: str
    subtype: str
    time_s: float = 0.0
    coordinate_space: str = "source_px"
    landmarks: dict[str, SourcePoint] = field(default_factory=dict)
    lines: dict[str, SourceLine] = field(default_factory=dict)
    curves: dict[str, list[SourcePoint]] = field(default_factory=dict)
    text_anchors: dict[str, SourcePoint] = field(default_factory=dict)
    topology: dict[str, list[str]] = field(default_factory=dict)
    masks: dict[str, np.ndarray] = field(default_factory=dict)

    def validate_context(self, book_ir):
        observed = book_ir.visual_reconstruction.observed_geometry
        for name in ("source_asset_id", "figure_id", "domain", "subtype"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value or value != getattr(book_ir, name):
                raise ValueError(f"Prediction {name} does not match grounded BookIR")
        for name in ("source_width", "source_height"):
            value = getattr(self, name)
            if type(value) is not int or value != getattr(observed, name):
                raise ValueError("Prediction dimensions must match the native source image")
        if self.coordinate_space != "source_px":
            raise ValueError("Prediction must use source_px")
        if type(self.time_s) not in (int, float) or self.time_s != 0:
            raise ValueError("Initial registration requires a prediction at t=0")
        for name in ("landmarks", "lines", "curves", "text_anchors", "topology", "masks"):
            group = getattr(self, name)
            if not isinstance(group, dict) or any(not isinstance(key, str) or not key for key in group):
                raise ValueError(f"Prediction {name} must be a named feature map")

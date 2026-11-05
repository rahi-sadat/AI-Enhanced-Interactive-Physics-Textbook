"""Local symbol proposals from the explicitly selected circuit_v2 checkpoint."""
from dataclasses import dataclass
import math
import os
from pathlib import Path
from threading import Lock

import numpy as np

from shared.schemas.evidence import SourceBBox

ROOT = Path(__file__).resolve().parents[3]
CHECKPOINT = ROOT / "runs/augmented_physics/circuits_real_v2_20261031/weights/last.pt"
MODEL_NAME = "circuit_v2"
SYMBOL_TYPES = {"resistor", "voltage_source", "capacitor", "switch"}
MIN_CONFIDENCE = 0.25


@dataclass(frozen=True)
class CircuitDetection:
    kind: str
    confidence: float
    bbox: SourceBBox


class CircuitV2Detector:
    """Cache one predictor per pipeline and serialize its use across uploads."""

    def __init__(self):
        self._model = None
        self._lock = Lock()
        self.checkpoint = Path(os.getenv("CIRCUIT_V2_CHECKPOINT") or CHECKPOINT).resolve()

    def predict(self, image_bgr: np.ndarray) -> list[CircuitDetection]:
        with self._lock:
            if self._model is None:
                if not self.checkpoint.is_file():
                    raise FileNotFoundError(f"Missing local {MODEL_NAME} checkpoint")
                # Configure the SDK before its lazy import so local prediction
                # can run without DNS, analytics, or a writable user profile.
                os.environ.setdefault("YOLO_OFFLINE", "true")
                os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "storage/cache/ultralytics"))
                from ultralytics import YOLO

                self._model = YOLO(str(self.checkpoint))
            result = self._model.predict(
                image_bgr, imgsz=960, conf=MIN_CONFIDENCE, device="cpu", save=False, verbose=False,
            )[0]

        # Ultralytics already removes letterboxing and reports xyxy in the
        # supplied image frame. These boxes remain unverified search regions.
        height, width = image_bgr.shape[:2]
        if result.orig_shape != (height, width):
            raise ValueError(f"{MODEL_NAME} result does not match the source image dimensions")
        detections = []
        for cls, confidence, coords in zip(
            result.boxes.cls.tolist(), result.boxes.conf.tolist(), result.boxes.xyxy.tolist(),
        ):
            kind = result.names.get(int(cls)) if math.isfinite(cls) else None
            if (kind not in SYMBOL_TYPES or not MIN_CONFIDENCE <= confidence <= 1
                    or not all(math.isfinite(v) for v in coords)):
                continue
            x1, y1, x2, y2 = coords
            if 0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height:
                detections.append(CircuitDetection(
                    kind, min(confidence, 0.95), SourceBBox(x1, y1, x2 - x1, y2 - y1),
                ))
        return sorted(detections, key=lambda d: (d.bbox.y, d.bbox.x, d.kind))

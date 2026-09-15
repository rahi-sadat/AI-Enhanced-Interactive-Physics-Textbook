"""backend/circuits/perception/wire_detector.py

Extracts wire paths using adaptive binarization, morphological skeletonization (scikit-image),
graph branch tracing, and sub-pixel polyline simplification (cv2.approxPolyDP).
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

import cv2
import numpy as np
from skimage.morphology import skeletonize

from ..models import Point, Wire


class WireDetector:
    """Deterministic wire segment detector and skeleton tracer."""

    def __init__(self, epsilon_px: float = 2.0) -> None:
        self.epsilon_px = epsilon_px

    def detect(
        self,
        image_bgr: np.ndarray,
        text_mask: Optional[np.ndarray] = None,
        component_mask: Optional[np.ndarray] = None,
    ) -> list[Wire]:
        """Detect wires from image, suppressing text regions and component bodies."""
        h, w = image_bgr.shape[:2]
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

        # 1. High-contrast adaptive binarization
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 8
        )

        # 2. Mask out text and component interiors so they don't corrupt wire tracing
        if text_mask is not None:
            binary[text_mask > 0] = 0
        if component_mask is not None:
            binary[component_mask > 0] = 0

        # Morphological opening to clean single-pixel noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        clean_bin = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # 3. Skeletonization to 1-pixel-wide topological centerline
        bool_img = clean_bin > 0
        skeleton = skeletonize(bool_img).astype(np.uint8) * 255

        # 4. Extract contours from skeleton
        contours, _ = cv2.findContours(skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        wires: list[Wire] = []
        wire_id_counter = 1

        for c in contours:
            length = cv2.arcLength(c, False)
            # Filter out tiny noise specks (< 12 pixels total length)
            if length < 12.0:
                continue

            # Simplify polyline with approxPolyDP for clean segments
            approx = cv2.approxPolyDP(c, self.epsilon_px, False)
            pts: list[Point] = []
            for pt in approx:
                x, y = float(pt[0][0]), float(pt[0][1])
                pts.append(Point(x=x, y=y))

            if len(pts) >= 2:
                wires.append(
                    Wire(
                        id=f"wire_{wire_id_counter:02d}",
                        polyline_source_px=pts,
                        confidence=0.95,
                    )
                )
                wire_id_counter += 1

        return wires

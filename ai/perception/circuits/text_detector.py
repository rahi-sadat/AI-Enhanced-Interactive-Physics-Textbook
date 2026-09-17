"""backend/circuits/perception/text_detector.py

Identifies and masks text/label regions in circuit schematics.
Produces:
  1. A binary mask of text pixels (so wire skeletonization ignores text letters)
  2. Candidate text bounding boxes for OCR/parameter parsing
"""
from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np

try:
    from ai.document_intelligence.parsing.parameter_binder import TextFragment
except (ImportError, ValueError):
    from ..parameters.parameter_binder import TextFragment


class TextDetector:
    """Detects text regions based on connected component stroke and size heuristics."""

    def __init__(self, max_char_h: int = 40, max_char_w: int = 120) -> None:
        self.max_char_h = max_char_h
        self.max_char_w = max_char_w

    def detect(self, image_bgr: np.ndarray) -> Tuple[np.ndarray, list[TextFragment]]:
        """Returns (binary_text_mask, text_fragments)."""
        h, w = image_bgr.shape[:2]
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 9
        )

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)
        text_mask = np.zeros((h, w), dtype=np.uint8)
        fragments: list[TextFragment] = []

        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            bx = stats[i, cv2.CC_STAT_LEFT]
            by = stats[i, cv2.CC_STAT_TOP]
            bw = stats[i, cv2.CC_STAT_WIDTH]
            bh = stats[i, cv2.CC_STAT_HEIGHT]

            # Text characters typically have height 8..40px, width 4..100px, area 20..1200px
            if 6 <= bh <= self.max_char_h and 4 <= bw <= self.max_char_w and 15 <= area <= 1800:
                # Mark into text mask
                text_mask[labels == i] = 255

        # Merge closely adjacent character boxes into word fragments
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 4))
        dilated_text = cv2.dilate(text_mask, kernel)
        word_contours, _ = cv2.findContours(dilated_text, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for wc in word_contours:
            wx, wy, ww, wh = cv2.boundingRect(wc)
            if ww > 6 and wh > 6:
                cx = wx + ww / 2.0
                cy = wy + wh / 2.0
                fragments.append(
                    TextFragment(
                        text="",  # Will be populated by OCR / parameter parser
                        center_x=cx,
                        center_y=cy,
                        bbox=[float(wx), float(wy), float(wx + ww), float(wy + wh)],
                        confidence=0.90,
                    )
                )

        return text_mask, fragments

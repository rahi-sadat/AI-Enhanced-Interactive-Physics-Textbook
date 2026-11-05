"""PR-06 Classical CV Preprocessing & OCR Masking.

Provides deterministic image preprocessing operations and OCR region suppression
to prevent diagram text labels from corrupting geometric line and contour detection.
"""
from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox


def preprocess_diagram(
    img_bgr: np.ndarray,
    blur_ksize: Tuple[int, int] = (5, 5),
    blur_sigma: float = 1.0,
    canny_thresh1: float = 40.0,
    canny_thresh2: float = 120.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Preprocess diagram image into grayscale, blurred, and edge maps.

    Returns:
        (gray, blurred, edges)
    """
    if len(img_bgr.shape) == 3:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_bgr.copy()

    blurred = cv2.GaussianBlur(gray, blur_ksize, blur_sigma)
    edges = cv2.Canny(blurred, canny_thresh1, canny_thresh2, apertureSize=3)
    return gray, blurred, edges


def mask_out_text_regions(
    edge_map: np.ndarray,
    ocr_boxes: List[SourceBBox],
    margin_px: int = 4,
) -> np.ndarray:
    """Zero out edge pixels within expanded bounding boxes of detected OCR text.

    Ensures that labels such as 'm', 'L', 'θ' do not corrupt circle or line fitting.
    """
    clean_edges = edge_map.copy()
    h, w = clean_edges.shape[:2]

    for box in ocr_boxes:
        x1 = max(0, int(math_floor(box.x - margin_px)))
        y1 = max(0, int(math_floor(box.y - margin_px)))
        x2 = min(w, int(math_ceil(box.x + box.width + margin_px)))
        y2 = min(h, int(math_ceil(box.y + box.height + margin_px)))
        clean_edges[y1:y2, x1:x2] = 0

    return clean_edges


def math_floor(x: float) -> int:
    import math
    return int(math.floor(x))


def math_ceil(x: float) -> int:
    import math
    return int(math.ceil(x))


def preprocess_for_geometry(
    img_bgr: np.ndarray,
    ocr_boxes: List[SourceBBox] | None = None,
    canny_thresh1: float = 50.0,
    canny_thresh2: float = 150.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Preprocess image and return (gray, edges) with OCR text masked out."""
    gray, blurred, edges = preprocess_diagram(img_bgr, canny_thresh1=canny_thresh1, canny_thresh2=canny_thresh2)
    if ocr_boxes:
        edges = mask_out_text_regions(edges, ocr_boxes)
    return gray, edges

"""backend/circuits/perception/region_detector.py

Detects the active circuit diagram region within a larger textbook page.
Retains exact affine crop-to-source transform so all coordinates remain in original source_px.
"""
from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np

try:
    from engine.core.coordinate_space import CropTransform
except (ImportError, ValueError):
    try:
        from backend.core.coordinate_space import CropTransform
    except (ImportError, ValueError):
        from core.coordinate_space import CropTransform


def detect_circuit_region(img_bgr: np.ndarray) -> Tuple[np.ndarray, CropTransform]:
    """Detect bounding box containing the circuit diagram and return (cropped_img, crop_transform).
    
    If image already is a cropped circuit diagram (foreground occupies > 40% area),
    returns the original image with an identity transform.
    """
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Adaptive threshold to isolate schematic lines and text
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 9
    )

    # Find connected components or external contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img_bgr, CropTransform(offset_x=0.0, offset_y=0.0, crop_width=float(w), crop_height=float(h))

    # Combine all significant contours (> 50 px area)
    sig_pts = []
    for c in contours:
        if cv2.contourArea(c) > 50:
            sig_pts.append(c.reshape(-1, 2))

    if not sig_pts:
        return img_bgr, CropTransform(offset_x=0.0, offset_y=0.0, crop_width=float(w), crop_height=float(h))

    all_pts = np.vstack(sig_pts)
    min_x, min_y = np.min(all_pts, axis=0)
    max_x, max_y = np.max(all_pts, axis=0)

    # Add 15px padding if within bounds
    pad = 15
    x1 = max(0, int(min_x - pad))
    y1 = max(0, int(min_y - pad))
    x2 = min(w, int(max_x + pad))
    y2 = min(h, int(max_y + pad))

    crop_w = x2 - x1
    crop_h = y2 - y1

    # If crop is already nearly the full image (> 80% span), keep full image
    if crop_w > 0.85 * w and crop_h > 0.85 * h:
        return img_bgr, CropTransform(offset_x=0.0, offset_y=0.0, crop_width=float(w), crop_height=float(h))

    cropped = img_bgr[y1:y2, x1:x2].copy()
    transform = CropTransform(
        offset_x=float(x1),
        offset_y=float(y1),
        crop_width=float(crop_w),
        crop_height=float(crop_h),
    )
    return cropped, transform

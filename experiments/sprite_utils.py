from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import cv2
import numpy as np


def save_rgba_sprite(
    image_rgb: np.ndarray,
    mask: np.ndarray,
    output_path: Path,
    padding: int = 2,
) -> Dict[str, Any]:
    """
    Extracts the pixels belonging to the mask from image_rgb, creates an RGBA image
    with transparent background, tightly crops it to the bounding box plus optional padding,
    and writes it to output_path.

    Returns metadata including bounding box, dimensions, and output path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    mask_bool = mask.astype(bool)
    ys, xs = np.where(mask_bool)

    if len(xs) == 0:
        raise ValueError("Cannot create sprite from empty mask")

    h, w = image_rgb.shape[:2]

    x1 = max(0, int(xs.min()) - padding)
    x2 = min(w, int(xs.max()) + 1 + padding)
    y1 = max(0, int(ys.min()) - padding)
    y2 = min(h, int(ys.max()) + 1 + padding)

    crop_w = x2 - x1
    crop_h = y2 - y1

    crop_rgb = image_rgb[y1:y2, x1:x2]
    crop_alpha = (mask_bool[y1:y2, x1:x2].astype(np.uint8)) * 255

    rgba = np.dstack([crop_rgb, crop_alpha])
    bgra = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)

    cv2.imwrite(str(output_path), bgra)

    return {
        "x": x1,
        "y": y1,
        "width": crop_w,
        "height": crop_h,
        "sprite_path": output_path.as_posix(),
    }

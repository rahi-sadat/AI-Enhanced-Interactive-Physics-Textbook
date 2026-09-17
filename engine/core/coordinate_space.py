"""backend/core/coordinate_space.py

Coordinate space transformations for circuit perception and rendering.
Ensures that source image pixel coordinates (source_px) remain strictly authoritative
even when crops, downsamples, or bounding boxes are used internally during detection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class CropTransform:
    """Represents a crop window (offset_x, offset_y) from original source_px."""
    offset_x: float
    offset_y: float
    crop_width: float
    crop_height: float
    scale_factor: float = 1.0

    def crop_to_source(self, crop_x: float, crop_y: float) -> Tuple[float, float]:
        """Convert coordinates in the cropped image back to original source_px."""
        src_x = (crop_x / self.scale_factor) + self.offset_x
        src_y = (crop_y / self.scale_factor) + self.offset_y
        return (round(src_x, 3), round(src_y, 3))

    def source_to_crop(self, src_x: float, src_y: float) -> Tuple[float, float]:
        """Convert original source_px to cropped coordinates."""
        crop_x = (src_x - self.offset_x) * self.scale_factor
        crop_y = (src_y - self.offset_y) * self.scale_factor
        return (round(crop_x, 3), round(crop_y, 3))


def snap_radius(image_width: int, image_height: int, stroke_width: float = 2.0) -> float:
    """Computes an adaptive geometric snap radius proportional to image resolution.
    Avoids hardcoding arbitrary pixel distance limits.
    """
    diagonal = (image_width ** 2 + image_height ** 2) ** 0.5
    return max(3.0 * stroke_width, diagonal * 0.005)

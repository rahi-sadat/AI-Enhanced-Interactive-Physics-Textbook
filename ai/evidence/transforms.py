"""PR-06 Image and Coordinate Transform Utilities.

Guarantees strict source-pixel coordinate discipline ('source_px').
Never assumes simple scaling when padding, letterboxing, or cropping exists.
All geometry promoted to canonical BookIR must be mapped back to native source_px.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourceLine, SourcePoint, SourcePolygon
from shared.schemas.ingestion import SourceAsset


class CoordinateTransformError(ValueError):
    """Raised when coordinates violate source dimensions or are non-finite."""
    pass


@dataclass(frozen=True)
class ImageTransform:
    """Explicit, invertible coordinate transformation chain between model/working space and source_px.

    Transformation flow:
        source_px
          ↓ (optional crop: -crop_x, -crop_y)
        cropped
          ↓ (scale: *scale_x, *scale_y)
        scaled
          ↓ (optional letterbox padding: +pad_x, +pad_y)
        working_px (model input)

    Inverse flow:
        working_px
          ↓ (remove letterbox padding: -pad_x, -pad_y)
        scaled
          ↓ (undo scale: /scale_x, /scale_y)
        cropped
          ↓ (add crop origin: +crop_x, +crop_y)
        source_px
    """
    source_width: int
    source_height: int
    working_width: int
    working_height: int

    crop_x: float = 0.0
    crop_y: float = 0.0
    crop_width: Optional[float] = None
    crop_height: Optional[float] = None

    pad_x: float = 0.0
    pad_y: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0

    def __post_init__(self):
        if self.source_width <= 0 or self.source_height <= 0:
            raise CoordinateTransformError(
                f"Source dimensions must be positive, got {self.source_width}x{self.source_height}"
            )
        if self.working_width <= 0 or self.working_height <= 0:
            raise CoordinateTransformError(
                f"Working dimensions must be positive, got {self.working_width}x{self.working_height}"
            )

    @classmethod
    def identity(cls, width: int, height: int) -> ImageTransform:
        """Create an identity transform (working space == source_px)."""
        return cls(
            source_width=width,
            source_height=height,
            working_width=width,
            working_height=height,
            crop_x=0.0,
            crop_y=0.0,
            crop_width=float(width),
            crop_height=float(height),
            pad_x=0.0,
            pad_y=0.0,
            scale_x=1.0,
            scale_y=1.0,
        )

    @classmethod
    def create_resized(
        cls,
        source_width: int,
        source_height: int,
        working_width: int,
        working_height: int,
        preserve_aspect_ratio: bool = True,
    ) -> ImageTransform:
        """Create a transform for an image resized to model dimensions, optionally with letterboxing."""
        if not preserve_aspect_ratio:
            sx = working_width / float(source_width)
            sy = working_height / float(source_height)
            return cls(
                source_width=source_width,
                source_height=source_height,
                working_width=working_width,
                working_height=working_height,
                crop_x=0.0,
                crop_y=0.0,
                crop_width=float(source_width),
                crop_height=float(source_height),
                pad_x=0.0,
                pad_y=0.0,
                scale_x=sx,
                scale_y=sy,
            )

        # Scale preserving aspect ratio with centered letterbox padding
        scale = min(working_width / float(source_width), working_height / float(source_height))
        scaled_w = source_width * scale
        scaled_h = source_height * scale
        pad_x = (working_width - scaled_w) / 2.0
        pad_y = (working_height - scaled_h) / 2.0

        return cls(
            source_width=source_width,
            source_height=source_height,
            working_width=working_width,
            working_height=working_height,
            crop_x=0.0,
            crop_y=0.0,
            crop_width=float(source_width),
            crop_height=float(source_height),
            pad_x=pad_x,
            pad_y=pad_y,
            scale_x=scale,
            scale_y=scale,
        )

    @classmethod
    def create_cropped(
        cls,
        source_width: int,
        source_height: int,
        crop_box: SourceBBox,
        working_width: Optional[int] = None,
        working_height: Optional[int] = None,
    ) -> ImageTransform:
        """Create a transform for a cropped region mapped into working space."""
        w_w = working_width or int(round(crop_box.width))
        w_h = working_height or int(round(crop_box.height))
        sx = w_w / float(crop_box.width)
        sy = w_h / float(crop_box.height)
        return cls(
            source_width=source_width,
            source_height=source_height,
            working_width=w_w,
            working_height=w_h,
            crop_x=crop_box.x,
            crop_y=crop_box.y,
            crop_width=crop_box.width,
            crop_height=crop_box.height,
            pad_x=0.0,
            pad_y=0.0,
            scale_x=sx,
            scale_y=sy,
        )

    # -----------------------------------------------------------------------
    # Inverse Mapping: working_px → source_px
    # -----------------------------------------------------------------------

    def to_source_point(self, x: float, y: float, clip: bool = True) -> SourcePoint:
        """Map working coordinate (x, y) back to native source_px."""
        if not (math.isfinite(x) and math.isfinite(y)):
            raise CoordinateTransformError(f"Non-finite input coordinates: ({x}, {y})")

        # 1. Remove letterbox offset
        unpadded_x = x - self.pad_x
        unpadded_y = y - self.pad_y

        # 2. Undo scaling
        if self.scale_x == 0 or self.scale_y == 0:
            raise CoordinateTransformError("Zero scale factor in ImageTransform.")
        scaled_x = unpadded_x / self.scale_x
        scaled_y = unpadded_y / self.scale_y

        # 3. Add crop origin
        src_x = scaled_x + self.crop_x
        src_y = scaled_y + self.crop_y

        if clip:
            src_x = max(0.0, min(float(self.source_width), src_x))
            src_y = max(0.0, min(float(self.source_height), src_y))
        else:
            if src_x < 0.0 or src_x > self.source_width or src_y < 0.0 or src_y > self.source_height:
                raise CoordinateTransformError(
                    f"Mapped coordinate ({src_x:.2f}, {src_y:.2f}) lies outside source bounds (0..{self.source_width}, 0..{self.source_height})"
                )

        return SourcePoint(x=src_x, y=src_y)

    def to_source_bbox(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        clip: bool = True,
    ) -> SourceBBox:
        """Map working bounding box back to native source_px."""
        p1 = self.to_source_point(x, y, clip=clip)
        p2 = self.to_source_point(x + width, y + height, clip=clip)

        min_x = min(p1.x, p2.x)
        min_y = min(p1.y, p2.y)
        max_x = max(p1.x, p2.x)
        max_y = max(p1.y, p2.y)

        src_w = max(1e-3, max_x - min_x)
        src_h = max(1e-3, max_y - min_y)

        return SourceBBox(x=min_x, y=min_y, width=src_w, height=src_h)

    def to_source_line(self, p1: Tuple[float, float], p2: Tuple[float, float], clip: bool = True) -> SourceLine:
        """Map line segment in working space back to native source_px."""
        pt1 = self.to_source_point(p1[0], p1[1], clip=clip)
        pt2 = self.to_source_point(p2[0], p2[1], clip=clip)
        return SourceLine(start=pt1, end=pt2)

    def to_source_polygon(self, pts: List[Tuple[float, float]], clip: bool = True) -> SourcePolygon:
        """Map polygon in working space back to native source_px."""
        src_pts = [self.to_source_point(p[0], p[1], clip=clip) for p in pts]
        return SourcePolygon(points=src_pts)

    # -----------------------------------------------------------------------
    # Forward Mapping: source_px → working_px
    # -----------------------------------------------------------------------

    def to_working_point(self, src_x: float, src_y: float) -> Tuple[float, float]:
        """Map native source_px to working coordinate."""
        rel_x = src_x - self.crop_x
        rel_y = src_y - self.crop_y
        scaled_x = rel_x * self.scale_x
        scaled_y = rel_y * self.scale_y
        w_x = scaled_x + self.pad_x
        w_y = scaled_y + self.pad_y
        return w_x, w_y


# ---------------------------------------------------------------------------
# Source Image Loader & Validator
# ---------------------------------------------------------------------------

def load_and_validate_source_image(asset: SourceAsset) -> np.ndarray:
    """Safely decode and validate image bytes from real SourceAsset.

    Ensures:
      - File exists on disk at asset.storage_path
      - Decodes correctly via OpenCV
      - Decoded dimensions strictly match asset.width_px and asset.height_px
    """
    path = Path(asset.storage_path)
    if not path.exists():
        raise FileNotFoundError(f"SourceAsset storage file missing: {asset.storage_path}")

    # Read binary bytes first to support non-ASCII paths on Windows
    with open(path, "rb") as f:
        file_bytes = f.read()

    nparr = np.frombuffer(file_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_bgr is None:
        raise ValueError(f"Failed to decode image from SourceAsset at {asset.storage_path}")

    h, w = img_bgr.shape[:2]
    if w != asset.width_px or h != asset.height_px:
        raise CoordinateTransformError(
            f"SourceAsset dimension mismatch: asset declares ({asset.width_px}x{asset.height_px}), "
            f"but decoded image has ({w}x{h}). Scaling or corrupt asset detected."
        )

    return img_bgr

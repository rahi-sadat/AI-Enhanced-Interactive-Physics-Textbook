"""Source visual element extraction and background restoration (Phase 6, 13).

Extracts dynamic assets (movable bobs, draggable arrows, clickable switches)
from native source diagram images, creating:
  1. Alpha-matted transparent PNG sprites.
  2. Inpainted background restoration patches (TELEA / Navier-Stokes).
  3. Fully compliant DynamicVisualAsset records preserving source_px coordinates.
"""
from __future__ import annotations

import base64
import math
from typing import List, Optional, Tuple

import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourcePoint
from shared.schemas.visual_reconstruction import DynamicVisualAsset


def _encode_png_data_uri(img: np.ndarray) -> str:
    """Encode an OpenCV BGR or BGRA image array into a base64 PNG data URI."""
    success, buffer = cv2.imencode(".png", img)
    if not success:
        raise ValueError("Failed to encode image to PNG format")
    b64_str = base64.b64encode(buffer).decode("ascii")
    return f"data:image/png;base64,{b64_str}"


def extract_bob_visual_asset(
    img_bgr: np.ndarray,
    bob_center: SourcePoint,
    bob_radius_px: float,
    entity_id: str = "bob",
    evidence_refs: Optional[List[str]] = None,
    pad_px: int = 3,
) -> DynamicVisualAsset:
    """Extract a movable pendulum bob as a DynamicVisualAsset.

    Produces:
      - alpha-matted circular sprite crop
      - inpainted restoration patch removing the bob from the background
      - source-pixel bounding box and absolute anchor coordinates
    """
    h, w = img_bgr.shape[:2]
    cx, cy = bob_center.x, bob_center.y
    r = float(bob_radius_px)

    x0 = max(0, int(math.floor(cx - r - pad_px)))
    y0 = max(0, int(math.floor(cy - r - pad_px)))
    x1 = min(w, int(math.ceil(cx + r + pad_px)))
    y1 = min(h, int(math.ceil(cy + r + pad_px)))

    bw = x1 - x0
    bh = y1 - y0
    if bw <= 0 or bh <= 0:
        raise ValueError(f"Invalid crop dimensions for bob at ({cx}, {cy})")

    # 1. Alpha Sprite Crop
    crop = img_bgr[y0:y1, x0:x1]
    alpha = np.zeros((bh, bw), dtype=np.uint8)
    local_center = (int(round(cx - x0)), int(round(cy - y0)))
    cv2.circle(alpha, local_center, int(round(r)), 255, -1)
    # Smooth edges with 1px blur
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)

    bgra = cv2.cvtColor(crop, cv2.COLOR_BGR2BGRA)
    bgra[:, :, 3] = alpha
    sprite_data_uri = _encode_png_data_uri(bgra)

    # 2. Inpainted Background Restoration
    inpaint_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(inpaint_mask, (int(round(cx)), int(round(cy))), int(round(r + pad_px + 1)), 255, -1)
    restored_full = cv2.inpaint(img_bgr, inpaint_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    restored_patch = restored_full[y0:y1, x0:x1]
    patch_data_uri = _encode_png_data_uri(restored_patch)
    clean_bg_data_uri = _encode_png_data_uri(restored_full)

    source_bbox = SourceBBox(x=x0, y=y0, width=bw, height=bh)
    anchor = SourcePoint(x=cx, y=cy)
    transform_orig = SourcePoint(x=cx, y=cy)

    refs = list(evidence_refs) if evidence_refs else ["cv_bob_extraction"]

    return DynamicVisualAsset(
        entity_id=entity_id,
        source_bbox=source_bbox,
        anchor_source_px=anchor,
        transform_origin=transform_orig,
        sprite_url=sprite_data_uri,
        clean_background_url=clean_bg_data_uri,
        restoration_patch_url=patch_data_uri,
        restoration_bbox=source_bbox,
        extraction_confidence=0.92,
        evidence_refs=refs,
    )


def extract_arrow_visual_asset(
    img_bgr: np.ndarray,
    base_point: SourcePoint,
    tip_point: SourcePoint,
    entity_id: str = "object_arrow",
    evidence_refs: Optional[List[str]] = None,
    thickness_px: int = 12,
    pad_px: int = 4,
) -> DynamicVisualAsset:
    """Extract an optics object/image arrow as a draggable DynamicVisualAsset."""
    h, w = img_bgr.shape[:2]
    min_x = min(base_point.x, tip_point.x)
    max_x = max(base_point.x, tip_point.x)
    min_y = min(base_point.y, tip_point.y)
    max_y = max(base_point.y, tip_point.y)

    x0 = max(0, int(math.floor(min_x - thickness_px - pad_px)))
    y0 = max(0, int(math.floor(min_y - pad_px)))
    x1 = min(w, int(math.ceil(max_x + thickness_px + pad_px)))
    y1 = min(h, int(math.ceil(max_y + pad_px)))

    bw = x1 - x0
    bh = y1 - y0
    if bw <= 0 or bh <= 0:
        raise ValueError(f"Invalid arrow dimensions from {base_point} to {tip_point}")

    # 1. Alpha Sprite Crop
    crop = img_bgr[y0:y1, x0:x1]
    # For arrow, create a convex hull or line mask with antialiasing
    alpha = np.zeros((bh, bw), dtype=np.uint8)
    p1 = (int(round(base_point.x - x0)), int(round(base_point.y - y0)))
    p2 = (int(round(tip_point.x - x0)), int(round(tip_point.y - y0)))
    cv2.line(alpha, p1, p2, 255, thickness=int(thickness_px))
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)

    bgra = cv2.cvtColor(crop, cv2.COLOR_BGR2BGRA)
    bgra[:, :, 3] = alpha
    sprite_data_uri = _encode_png_data_uri(bgra)

    # 2. Inpainted Background Restoration
    inpaint_mask = np.zeros((h, w), dtype=np.uint8)
    ip1 = (int(round(base_point.x)), int(round(base_point.y)))
    ip2 = (int(round(tip_point.x)), int(round(tip_point.y)))
    cv2.line(inpaint_mask, ip1, ip2, 255, thickness=int(thickness_px + 4))
    restored_full = cv2.inpaint(img_bgr, inpaint_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    restored_patch = restored_full[y0:y1, x0:x1]
    patch_data_uri = _encode_png_data_uri(restored_patch)
    clean_bg_data_uri = _encode_png_data_uri(restored_full)

    source_bbox = SourceBBox(x=x0, y=y0, width=bw, height=bh)
    anchor = SourcePoint(x=base_point.x, y=base_point.y)
    transform_orig = SourcePoint(x=base_point.x, y=base_point.y)
    refs = list(evidence_refs) if evidence_refs else ["cv_arrow_extraction"]

    return DynamicVisualAsset(
        entity_id=entity_id,
        source_bbox=source_bbox,
        anchor_source_px=anchor,
        transform_origin=transform_orig,
        sprite_url=sprite_data_uri,
        clean_background_url=clean_bg_data_uri,
        restoration_patch_url=patch_data_uri,
        restoration_bbox=source_bbox,
        extraction_confidence=0.88,
        evidence_refs=refs,
    )

"""Unit tests for DynamicVisualAsset extraction and inpainting (Phase 6, 13)."""
import numpy as np
import pytest
from shared.schemas.evidence import SourcePoint, SourceBBox
from shared.schemas.visual_reconstruction import DynamicVisualAsset
from ai.evidence.cv.visual_extractor import extract_bob_visual_asset, extract_arrow_visual_asset


def test_extract_bob_visual_asset():
    """Verify bob visual extraction produces alpha sprite and clean background patch."""
    # Synthetic white canvas with black circle
    img = np.full((300, 300, 3), 255, dtype=np.uint8)
    import cv2
    cv2.circle(img, (150, 150), 20, (30, 30, 30), -1)

    bob_center = SourcePoint(x=150.0, y=150.0)
    asset = extract_bob_visual_asset(img, bob_center, bob_radius_px=20.0, entity_id="bob_1")

    assert isinstance(asset, DynamicVisualAsset)
    assert asset.entity_id == "bob_1"
    assert asset.source_bbox.width > 40
    assert asset.source_bbox.height > 40
    assert asset.anchor_source_px.x == 150.0
    assert asset.anchor_source_px.y == 150.0
    assert asset.sprite_url.startswith("data:image/png;base64,")
    assert asset.clean_background_url.startswith("data:image/png;base64,")
    assert asset.restoration_patch_url.startswith("data:image/png;base64,")
    assert asset.extraction_confidence > 0.8


def test_extract_arrow_visual_asset():
    """Verify arrow visual extraction produces valid DynamicVisualAsset."""
    img = np.full((300, 300, 3), 255, dtype=np.uint8)
    import cv2
    cv2.arrowedLine(img, (100, 200), (100, 100), (0, 0, 0), 3)

    base = SourcePoint(x=100.0, y=200.0)
    tip = SourcePoint(x=100.0, y=100.0)
    asset = extract_arrow_visual_asset(img, base, tip, entity_id="obj_arrow")

    assert isinstance(asset, DynamicVisualAsset)
    assert asset.entity_id == "obj_arrow"
    assert asset.source_bbox.height >= 100
    assert asset.anchor_source_px.x == 100.0
    assert asset.sprite_url.startswith("data:image/png;base64,")
    assert asset.clean_background_url.startswith("data:image/png;base64,")

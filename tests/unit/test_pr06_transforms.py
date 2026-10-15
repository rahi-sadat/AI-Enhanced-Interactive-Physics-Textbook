"""PR-06 Unit Tests — Coordinate Transformations & Bounds Discipline.

Tests:
  - Identity transform
  - Simple resize round-trip
  - Letterboxed resize round-trip (aspect ratio preservation)
  - Cropped region transform round-trip
  - Bounding box, polygon, and line mappings
  - Strict rejection of non-finite, out-of-bounds, or negative dimensions
  - SourceAsset dimension consistency verification
"""
from __future__ import annotations

import io
import math
import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from shared.schemas.evidence import SourceBBox, SourceLine, SourcePoint, SourcePolygon
from shared.schemas.ingestion import SourceAsset, compute_sha256
from ai.evidence.transforms import (
    CoordinateTransformError,
    ImageTransform,
    load_and_validate_source_image,
)


class TestPR06Transforms(unittest.TestCase):
    """Test suite for explicit source-pixel coordinate mappings."""

    def test_identity_transform(self):
        t = ImageTransform.identity(800, 600)
        pt = t.to_source_point(350.5, 412.25)
        self.assertAlmostEqual(pt.x, 350.5, places=5)
        self.assertAlmostEqual(pt.y, 412.25, places=5)

        w_x, w_y = t.to_working_point(pt.x, pt.y)
        self.assertAlmostEqual(w_x, 350.5, places=5)
        self.assertAlmostEqual(w_y, 412.25, places=5)

    def test_simple_resize_no_aspect_round_trip(self):
        # 1600x1200 downscaled to 800x600 (scale 0.5)
        t = ImageTransform.create_resized(1600, 1200, 800, 600, preserve_aspect_ratio=False)
        src_pt = SourcePoint(x=400.0, y=300.0)
        w_x, w_y = t.to_working_point(src_pt.x, src_pt.y)
        self.assertAlmostEqual(w_x, 200.0, places=5)
        self.assertAlmostEqual(w_y, 150.0, places=5)

        mapped_back = t.to_source_point(w_x, w_y)
        self.assertAlmostEqual(mapped_back.x, src_pt.x, places=5)
        self.assertAlmostEqual(mapped_back.y, src_pt.y, places=5)

    def test_letterboxed_resize_round_trip(self):
        # Source 1000x500 (2:1 aspect ratio), model input 800x800 square
        # Scale = min(800/1000, 800/500) = 0.8
        # Scaled dims: 800 x 400. Letterbox padding: pad_x = 0, pad_y = 200.0
        t = ImageTransform.create_resized(1000, 500, 800, 800, preserve_aspect_ratio=True)
        self.assertAlmostEqual(t.scale_x, 0.8, places=5)
        self.assertAlmostEqual(t.pad_x, 0.0, places=5)
        self.assertAlmostEqual(t.pad_y, 200.0, places=5)

        # Center of source image: (500, 250)
        # Expected working: (500*0.8 + 0, 250*0.8 + 200) = (400, 400)
        w_x, w_y = t.to_working_point(500.0, 250.0)
        self.assertAlmostEqual(w_x, 400.0, places=5)
        self.assertAlmostEqual(w_y, 400.0, places=5)

        mapped_back = t.to_source_point(400.0, 400.0)
        self.assertAlmostEqual(mapped_back.x, 500.0, places=5)
        self.assertAlmostEqual(mapped_back.y, 250.0, places=5)

    def test_cropped_transform_round_trip(self):
        # Crop region in source 1920x1080 at (100, 200) with size 400x300
        crop_box = SourceBBox(x=100.0, y=200.0, width=400.0, height=300.0)
        t = ImageTransform.create_cropped(1920, 1080, crop_box, working_width=800, working_height=600)
        self.assertAlmostEqual(t.scale_x, 2.0, places=5)
        self.assertAlmostEqual(t.scale_y, 2.0, places=5)

        # Point inside crop at source (200, 300) -> relative (100, 100) -> working (200, 200)
        w_x, w_y = t.to_working_point(200.0, 300.0)
        self.assertAlmostEqual(w_x, 200.0, places=5)
        self.assertAlmostEqual(w_y, 200.0, places=5)

        mapped = t.to_source_point(200.0, 200.0)
        self.assertAlmostEqual(mapped.x, 200.0, places=5)
        self.assertAlmostEqual(mapped.y, 300.0, places=5)

    def test_bbox_and_line_transform(self):
        t = ImageTransform.create_resized(1000, 1000, 500, 500, preserve_aspect_ratio=False)
        # Bounding box in working space
        bbox = t.to_source_bbox(x=50.0, y=50.0, width=100.0, height=100.0)
        self.assertAlmostEqual(bbox.x, 100.0, places=5)
        self.assertAlmostEqual(bbox.y, 100.0, places=5)
        self.assertAlmostEqual(bbox.width, 200.0, places=5)
        self.assertAlmostEqual(bbox.height, 200.0, places=5)

        # Line in working space
        line = t.to_source_line((50.0, 50.0), (150.0, 150.0))
        self.assertAlmostEqual(line.start.x, 100.0, places=5)
        self.assertAlmostEqual(line.start.y, 100.0, places=5)
        self.assertAlmostEqual(line.end.x, 300.0, places=5)
        self.assertAlmostEqual(line.end.y, 300.0, places=5)

    def test_polygon_mapping(self):
        t = ImageTransform.identity(500, 500)
        pts = [(10.0, 10.0), (50.0, 10.0), (30.0, 40.0)]
        poly = t.to_source_polygon(pts)
        self.assertEqual(len(poly.points), 3)
        self.assertAlmostEqual(poly.points[0].x, 10.0)
        self.assertAlmostEqual(poly.bbox.width, 40.0)

    def test_invalid_coordinates_and_bounds_rejection(self):
        t = ImageTransform.identity(800, 600)
        # NaN coordinates
        with self.assertRaises(CoordinateTransformError):
            t.to_source_point(float("nan"), 100.0)

        # Infinite coordinates
        with self.assertRaises(CoordinateTransformError):
            t.to_source_point(100.0, float("inf"))

        # Out of bounds when clip=False
        with self.assertRaises(CoordinateTransformError):
            t.to_source_point(-10.0, 200.0, clip=False)
        with self.assertRaises(CoordinateTransformError):
            t.to_source_point(900.0, 200.0, clip=False)

        # Non-finite primitives
        with self.assertRaises(ValueError):
            SourcePoint(x=float("nan"), y=10.0)
        with self.assertRaises(ValueError):
            SourceBBox(x=10.0, y=10.0, width=-5.0, height=20.0)
        with self.assertRaises(ValueError):
            SourcePolygon(points=[SourcePoint(1.0, 2.0), SourcePoint(3.0, 4.0)])  # < 3 points

    def test_source_dimension_validation(self):
        # Create a real 100x80 test image
        img = Image.new("RGB", (100, 80), color=(255, 255, 255))
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(tmp.name)
        tmp.close()

        # Valid asset matching actual dimensions
        valid_asset = SourceAsset(
            id="asset_valid",
            mime_type="image/png",
            original_filename="valid.png",
            byte_size=os.path.getsize(tmp.name),
            width_px=100,
            height_px=80,
            sha256="dummy",
            storage_path=tmp.name,
        )
        loaded = load_and_validate_source_image(valid_asset)
        self.assertEqual(loaded.shape, (80, 100, 3))

        # Invalid asset with falsified dimensions (claims 200x150)
        invalid_asset = SourceAsset(
            id="asset_invalid",
            mime_type="image/png",
            original_filename="invalid.png",
            byte_size=os.path.getsize(tmp.name),
            width_px=200,
            height_px=150,
            sha256="dummy",
            storage_path=tmp.name,
        )
        with self.assertRaises(CoordinateTransformError):
            load_and_validate_source_image(invalid_asset)

        # Clean up
        try:
            os.remove(tmp.name)
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()

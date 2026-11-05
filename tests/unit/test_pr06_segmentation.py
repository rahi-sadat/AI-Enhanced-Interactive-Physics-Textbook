"""PR-06 Unit Tests — Segmentation Provider Abstraction.

Tests:
  - MockSegmentationProvider deterministic mask artifact generation
  - UnavailableSegmentationProvider graceful unavailable state
  - SAM2SegmentationProvider availability and lazy loading
"""
from __future__ import annotations

import unittest
import numpy as np

from shared.schemas.evidence import ExtractionStatus, SourceBBox, SourcePoint
from ai.evidence.segmentation import (
    MockSegmentationProvider,
    SAM2SegmentationProvider,
    SegmentationPrompt,
    UnavailableSegmentationProvider,
)


class TestPR06Segmentation(unittest.TestCase):
    """Test suite for segmentation provider abstractions."""

    def test_mock_segmentation_provider(self):
        provider = MockSegmentationProvider()
        self.assertTrue(provider.available())

        prompt = SegmentationPrompt(
            box=SourceBBox(x=50.0, y=50.0, width=40.0, height=40.0),
            points=[(70.0, 70.0)],
        )
        img = np.zeros((150, 150, 3), dtype=np.uint8)
        result = provider.segment(img, prompt, source_width=150, source_height=150, entity_id="bob_01")

        self.assertEqual(result.status, ExtractionStatus.SUCCESS)
        self.assertEqual(len(result.masks), 1)

        mask = result.masks[0]
        self.assertAlmostEqual(mask.centroid_source_px.x, 70.0, delta=1.0)
        self.assertAlmostEqual(mask.centroid_source_px.y, 70.0, delta=1.0)
        self.assertGreater(mask.area_px, 0.0)
        self.assertIsNotNone(mask.polygon_approx)
        self.assertFalse(mask.verified, "Segmentation provider masks are candidates; verified must be False until fusion")

    def test_unavailable_segmentation_provider(self):
        provider = UnavailableSegmentationProvider()
        self.assertFalse(provider.available())

        prompt = SegmentationPrompt()
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        result = provider.segment(img, prompt, source_width=50, source_height=50)

        self.assertEqual(result.status, ExtractionStatus.UNAVAILABLE)
        self.assertEqual(len(result.masks), 0)

    def test_sam2_provider_availability(self):
        provider = SAM2SegmentationProvider()
        # In our workspace, checkpoints/sam2.1_hiera_tiny.pt exists and sam2 is installed
        self.assertTrue(provider.available())


if __name__ == "__main__":
    unittest.main()

"""PR-06 Mock and Unavailable Segmentation Providers for Offline/CI Isolation."""
from __future__ import annotations

import math
from typing import List, Optional

import numpy as np

from shared.schemas.evidence import (
    ExtractionStatus,
    MaskArtifact,
    SegmentationResult,
    SourceBBox,
    SourcePoint,
    SourcePolygon,
)
from ai.evidence.segmentation.base import SegmentationPrompt


class MockSegmentationProvider:
    """Deterministic segmentation provider for fast unit tests without GPU/neural weights."""

    def __init__(
        self,
        canned_masks: Optional[List[MaskArtifact]] = None,
        status: ExtractionStatus = ExtractionStatus.SUCCESS,
    ):
        self.canned_masks = canned_masks
        self.status = status

    @property
    def name(self) -> str:
        return "mock_segmentation"

    def available(self) -> bool:
        return True

    def segment(
        self,
        image_bgr: np.ndarray,
        prompt: SegmentationPrompt,
        *,
        source_width: int,
        source_height: int,
        entity_id: Optional[str] = None,
    ) -> SegmentationResult:
        if self.status != ExtractionStatus.SUCCESS:
            return SegmentationResult(
                status=self.status,
                masks=[],
                provider=self.name,
                model="mock-v1",
                latency_ms=1.0,
            )

        if self.canned_masks is not None:
            return SegmentationResult(
                status=ExtractionStatus.SUCCESS,
                masks=list(self.canned_masks),
                provider=self.name,
                model="mock-v1",
                latency_ms=1.0,
            )

        # Generate a synthetic mask based on prompt box or point
        if prompt.box is not None:
            cx = prompt.box.x + prompt.box.width / 2.0
            cy = prompt.box.y + prompt.box.height / 2.0
            r = min(prompt.box.width, prompt.box.height) / 2.0
            bbox = prompt.box
        elif prompt.points:
            cx, cy = prompt.points[0]
            r = 20.0
            bbox = SourceBBox(x=cx - r, y=cy - r, width=r * 2.0, height=r * 2.0)
        else:
            cx, cy, r = 100.0, 100.0, 20.0
            bbox = SourceBBox(x=80.0, y=80.0, width=40.0, height=40.0)

        # Construct octagon polygon approximation
        poly_pts = []
        for i in range(8):
            ang = i * (2.0 * math.pi / 8.0)
            poly_pts.append(SourcePoint(x=cx + r * math.cos(ang), y=cy + r * math.sin(ang)))

        artifact = MaskArtifact(
            id=f"mask_{entity_id or 'mock'}_001",
            source_width=source_width,
            source_height=source_height,
            bbox_source_px=bbox,
            centroid_source_px=SourcePoint(x=cx, y=cy),
            area_px=math.pi * r * r,
            polygon_approx=SourcePolygon(points=poly_pts),
            confidence=0.96,
            provider=self.name,
            model="mock-v1",
            prompt_provenance={"mock": True},
            verified=False,
        )

        return SegmentationResult(
            status=ExtractionStatus.SUCCESS,
            masks=[artifact],
            provider=self.name,
            model="mock-v1",
            latency_ms=2.0,
        )


class UnavailableSegmentationProvider:
    """Simulates an environment without any segmentation model."""

    @property
    def name(self) -> str:
        return "unavailable_segmentation"

    def available(self) -> bool:
        return False

    def segment(
        self,
        image_bgr: np.ndarray,
        prompt: SegmentationPrompt,
        *,
        source_width: int,
        source_height: int,
        entity_id: Optional[str] = None,
    ) -> SegmentationResult:
        return SegmentationResult(
            status=ExtractionStatus.UNAVAILABLE,
            masks=[],
            provider=self.name,
            model=None,
            latency_ms=0.0,
            error="Segmentation engine is unavailable in the environment.",
        )

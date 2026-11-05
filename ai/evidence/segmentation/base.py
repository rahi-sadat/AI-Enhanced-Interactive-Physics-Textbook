"""PR-06 Segmentation Provider Base Interface and Prompt Contracts.

Defines the abstract interface for segmentation providers (e.g. SAM 2).
Prompt coordinates and returned mask metrics must be in native source pixels ('source_px').
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Protocol, Tuple, runtime_checkable

import numpy as np

from shared.schemas.evidence import MaskArtifact, SegmentationResult, SourceBBox, SourcePoint


@dataclass
class SegmentationPrompt:
    """Prompts for guiding promptable segmentation models like SAM 2."""
    box: Optional[SourceBBox] = None
    points: List[Tuple[float, float]] = field(default_factory=list)  # (x, y) in source_px
    labels: List[int] = field(default_factory=list)                 # 1 for positive, 0 for negative


@runtime_checkable
class SegmentationProvider(Protocol):
    """Protocol for segmentation engines generating object masks."""

    @property
    def name(self) -> str:
        ...

    def available(self) -> bool:
        ...

    def segment(
        self,
        image_bgr: np.ndarray,
        prompt: SegmentationPrompt,
        *,
        source_width: int,
        source_height: int,
        entity_id: Optional[str] = None,
    ) -> SegmentationResult:
        """Segment an entity within the image given spatial prompts.

        Args:
            image_bgr: Source image array.
            prompt: Spatial box or point prompts in source_px.
            source_width: Source width in source pixels.
            source_height: Source height in source pixels.
            entity_id: Optional target entity ID being segmented.

        Returns:
            SegmentationResult containing MaskArtifact in source_px.
        """
        ...

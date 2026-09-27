"""PR-06 OCR Provider Interface & Contracts.

Defines the abstract interface for OCR extraction.
Concrete providers must map all token geometry strictly into native source pixels ('source_px').
"""
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

import numpy as np

from shared.schemas.evidence import OCRExtractionResult, SourceBBox


@runtime_checkable
class OCRProvider(Protocol):
    """Protocol for OCR engines extracting text from physics diagrams."""

    @property
    def name(self) -> str:
        """Name of the OCR provider (e.g. 'rapidocr', 'mock', 'paddleocr')."""
        ...

    def available(self) -> bool:
        """Check whether the OCR engine is installed and ready to execute."""
        ...

    def extract(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        region: Optional[SourceBBox] = None,
    ) -> OCRExtractionResult:
        """Extract text tokens from an image.

        Args:
            image_bgr: Source or figure image as a BGR numpy array.
            source_width: Width of the source image in source pixels.
            source_height: Height of the source image in source pixels.
            region: Optional crop bounding box in source pixels.

        Returns:
            OCRExtractionResult containing tokens strictly in source_px.
        """
        ...

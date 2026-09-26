"""PR-06 Mock and Unavailable OCR Providers for Offline/CI Isolation."""
from __future__ import annotations

from typing import List, Optional

import numpy as np

from shared.schemas.evidence import (
    ExtractionStatus,
    OCRExtractionResult,
    OCRToken,
    SourceBBox,
)


class MockOCRProvider:
    """Deterministic OCR provider returning configured tokens for tests."""

    def __init__(self, canned_tokens: Optional[List[OCRToken]] = None, status: ExtractionStatus = ExtractionStatus.SUCCESS):
        self.canned_tokens = canned_tokens or []
        self.status = status

    @property
    def name(self) -> str:
        return "mock_ocr"

    def available(self) -> bool:
        return True

    def extract(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        region: Optional[SourceBBox] = None,
    ) -> OCRExtractionResult:
        return OCRExtractionResult(
            status=self.status,
            tokens=list(self.canned_tokens),
            provider=self.name,
            model="mock-v1",
            latency_ms=1.5,
        )


class UnavailableOCRProvider:
    """Simulates an environment where no OCR engine is installed."""

    @property
    def name(self) -> str:
        return "unavailable_ocr"

    def available(self) -> bool:
        return False

    def extract(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        region: Optional[SourceBBox] = None,
    ) -> OCRExtractionResult:
        return OCRExtractionResult(
            status=ExtractionStatus.UNAVAILABLE,
            tokens=[],
            provider=self.name,
            model=None,
            latency_ms=0.0,
            error="OCR engine is unavailable in the environment.",
        )

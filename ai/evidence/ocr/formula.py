"""PR-06 Formula & Mathematical Equation Recognition Abstraction.

Provides an extensible abstraction for LaTeX-style equation recognition
(e.g. PP-FormulaNet-S) without coupling the core application to heavy mathematical OCR weights.
"""
from __future__ import annotations

import logging
import time
from typing import Optional, Protocol, runtime_checkable

import numpy as np

from shared.schemas.evidence import (
    ExtractionStatus,
    FormulaRecognitionResult,
    SourceBBox,
)

logger = logging.getLogger(__name__)


@runtime_checkable
class FormulaRecognitionProvider(Protocol):
    """Protocol for mathematical formula recognition engines."""

    @property
    def name(self) -> str:
        ...

    def available(self) -> bool:
        ...

    def recognize(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        region: Optional[SourceBBox] = None,
    ) -> FormulaRecognitionResult:
        ...


class MockFormulaRecognitionProvider:
    """Deterministic formula recognizer for unit and regression testing."""

    def __init__(
        self,
        default_latex: str = r"T = 2\pi\sqrt{\frac{L}{g}}",
        status: ExtractionStatus = ExtractionStatus.SUCCESS,
        canned_latex: Optional[str] = None,
        canned_confidence: Optional[float] = None,
    ):
        self.default_latex = canned_latex or default_latex
        self.confidence = canned_confidence or 0.92
        self.status = status

    @property
    def name(self) -> str:
        return "mock_formula_recognizer"

    def available(self) -> bool:
        return True

    def recognize(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        region: Optional[SourceBBox] = None,
    ) -> FormulaRecognitionResult:
        return FormulaRecognitionResult(
            status=self.status,
            raw_text="T = 2pi*sqrt(L/g)",
            latex_candidate=self.default_latex,
            confidence=self.confidence,
            bbox_source_px=region,
            provider=self.name,
            model="mock-formula-v1",
            latency_ms=1.2,
        )

    recognize_formula = recognize


class UnavailableFormulaRecognitionProvider:
    """Fallback when no formula recognition weights (e.g. PP-FormulaNet) are present."""

    @property
    def name(self) -> str:
        return "unavailable_formula_recognizer"

    def available(self) -> bool:
        return False

    def recognize(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        region: Optional[SourceBBox] = None,
    ) -> FormulaRecognitionResult:
        return FormulaRecognitionResult(
            status=ExtractionStatus.UNAVAILABLE,
            provider=self.name,
            error="Formula recognition model is not configured in the active environment.",
        )

    recognize_formula = recognize

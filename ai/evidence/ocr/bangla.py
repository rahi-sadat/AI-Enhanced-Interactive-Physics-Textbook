"""PR-06 Bangla & Bilingual Educational OCR Provider.

Provides local Bengali script text recognition using EasyOCR with strict Unicode
preservation (NFC normalization, retaining combining marks, conjuncts, and vowel signs).
"""
from __future__ import annotations

import importlib.metadata
import logging
import time
import unicodedata
from typing import Optional

import numpy as np

from shared.schemas.evidence import (
    ExtractionStatus,
    OCRExtractionResult,
    OCRToken,
    SourceBBox,
    SourcePoint,
    SourcePolygon,
)
from ai.evidence.transforms import ImageTransform

logger = logging.getLogger(__name__)


def is_bengali_text(text: str) -> bool:
    """Check if string contains Bengali script characters (U+0980 to U+09FF)."""
    return any(0x0980 <= ord(c) <= 0x09FF for c in text)


def normalize_bengali_unicode(text: str) -> str:
    """Normalize Bengali text to Unicode NFC without stripping combining marks, vowel signs, or conjuncts."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", text.strip())


# Global singleton cache for EasyOCR reader
_CACHED_EASYOCR_READER = None
_CACHED_READER_GPU = None


class EasyOCRBanglaProvider:
    """Local, offline Bangla and bilingual textbook OCR provider."""

    def __init__(self, languages: tuple[str, ...] = ("bn", "en"), gpu: Optional[bool] = None):
        self.languages = list(languages)
        if gpu is None:
            try:
                import torch
                self.gpu = torch.cuda.is_available()
            except ImportError:
                self.gpu = False
        else:
            self.gpu = gpu
        self._reader = None
        self._package_name = "easyocr"
        self._package_version = "unknown"
        self._detector_model = "craft_mlt_25k.pth"
        self._recognizer_model = "bengali.pth"
        self._model_version = "bengali.pth"

    @property
    def device_name(self) -> str:
        return "cuda" if self.gpu else "cpu"

    @property
    def name(self) -> str:
        return "easyocr_bangla"

    def available(self) -> bool:
        try:
            import easyocr
            return True
        except ImportError:
            return False

    def _get_reader(self):
        global _CACHED_EASYOCR_READER, _CACHED_READER_GPU
        if _CACHED_EASYOCR_READER is not None and _CACHED_READER_GPU == self.gpu:
            self._reader = _CACHED_EASYOCR_READER
            return self._reader
        if self._reader is None:
            import easyocr
            self._package_version = importlib.metadata.version("easyocr")
            logger.info("[EasyOCRBanglaProvider] Initializing EasyOCR reader for languages: %s (gpu=%s)", self.languages, self.gpu)
            try:
                self._reader = easyocr.Reader(self.languages, gpu=self.gpu)
            except Exception as e:
                if self.gpu:
                    logger.warning("[EasyOCRBanglaProvider] GPU init failed, falling back to CPU: %s", e)
                    self.gpu = False
                    self._reader = easyocr.Reader(self.languages, gpu=False)
                else:
                    raise
            _CACHED_EASYOCR_READER = self._reader
            _CACHED_READER_GPU = self.gpu
        return self._reader

    def extract(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        region: Optional[SourceBBox] = None,
    ) -> OCRExtractionResult:
        if not self.available():
            return OCRExtractionResult(
                status=ExtractionStatus.UNAVAILABLE,
                tokens=[],
                provider=self.name,
                model=self._model_version,
                error="easyocr is not installed in the active environment.",
            )

        start_time = time.perf_counter()

        if region is not None:
            rx1 = max(0, int(round(region.x)))
            ry1 = max(0, int(round(region.y)))
            rx2 = min(image_bgr.shape[1], int(round(region.x + region.width)))
            ry2 = min(image_bgr.shape[0], int(round(region.y + region.height)))
            working_img = image_bgr[ry1:ry2, rx1:rx2]
            transform = ImageTransform.create_cropped(
                source_width=source_width,
                source_height=source_height,
                crop_box=region,
                working_width=working_img.shape[1],
                working_height=working_img.shape[0],
            )
        else:
            working_img = image_bgr
            transform = ImageTransform.identity(source_width, source_height)

        if working_img.size == 0:
            return OCRExtractionResult(
                status=ExtractionStatus.NO_EVIDENCE,
                tokens=[],
                provider=self.name,
                model=self._model_version,
                package=self._package_name,
                package_version=self._package_version,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        try:
            reader = self._get_reader()
            # easyocr expects RGB or BGR numpy array
            results = reader.readtext(working_img)
        except Exception as e:
            logger.error("[EasyOCRBanglaProvider] Extraction error: %s", e)
            return OCRExtractionResult(
                status=ExtractionStatus.ERROR,
                tokens=[],
                provider=self.name,
                model=self._model_version,
                package=self._package_name,
                package_version=self._package_version,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
                error=f"EasyOCR error: {e}",
            )

        if not results:
            return OCRExtractionResult(
                status=ExtractionStatus.NO_EVIDENCE,
                tokens=[],
                provider=self.name,
                model=self._model_version,
                package=self._package_name,
                package_version=self._package_version,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        tokens: list[OCRToken] = []
        for idx, (bbox_pts, raw_text, conf) in enumerate(results):
            raw_text = str(raw_text).strip()
            if not raw_text:
                continue

            # CRITICAL: Preserve Unicode combining marks & vowel signs using NFC
            normalized_text = unicodedata.normalize("NFC", raw_text)

            # Map coordinates to source_px
            src_points: list[SourcePoint] = []
            for p in bbox_pts:
                src_pt = transform.to_source_point(float(p[0]), float(p[1]), clip=True)
                src_points.append(src_pt)

            polygon = SourcePolygon(points=src_points)
            bbox = polygon.bbox

            is_bn = is_bengali_text(raw_text)
            token_id = f"bn_tok_{idx+1:03d}"
            tokens.append(
                OCRToken(
                    id=token_id,
                    raw_text=raw_text,
                    normalized_text=normalized_text,
                    bbox_source_px=bbox,
                    polygon_source_px=polygon,
                    confidence=float(conf) if conf is not None else None,
                    script_candidate="bengali" if is_bn else "latin",
                    language_candidate="bn" if is_bn else "en",
                    provider=self.name,
                    recognizer_model=self._model_version,
                    evidence_ref=f"evidence_ocr_{token_id}",
                )
            )

        latency = (time.perf_counter() - start_time) * 1000.0
        return OCRExtractionResult(
            status=ExtractionStatus.SUCCESS,
            tokens=tokens,
            provider=self.name,
            model=self._model_version,
            package=self._package_name,
            package_version=self._package_version,
            detector_model=self._detector_model,
            recognizer_model=self._recognizer_model,
            recognizer_language="bn+en",
            latency_ms=latency,
        )

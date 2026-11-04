"""PR-06 Modern RapidOCR Provider Implementation.

Leverages the unified rapidocr package with ONNX Runtime for deterministic,
local, CPU-friendly OCR on textbook diagrams.
"""
from __future__ import annotations

import importlib.metadata
import logging
import re
import time
from threading import Lock
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


class RapidOCRProvider:
    """Local, deterministic OCR engine using the modern rapidocr package."""

    def __init__(self, model_version: str = "PP-OCRv6-onnx"):
        self._model_version = model_version
        self._engine = None
        self._engine_lock = Lock()
        self._package_name = "rapidocr"
        self._package_version = "unknown"
        self._detector_model = "PP-OCRv6_det_small.onnx"
        self._recognizer_model = "PP-OCRv6_rec_small.onnx"
        self._classifier_model = "ch_ppocr_mobile_v2.0_cls_mobile.onnx"
        self._recognizer_language = "latin_digits_ch"

    @property
    def model_version(self) -> str:
        return self._model_version

    @model_version.setter
    def model_version(self, value: str):
        self._model_version = value

    @property
    def name(self) -> str:
        return "rapidocr"

    def available(self) -> bool:
        try:
            import rapidocr
            return True
        except ImportError:
            try:
                import rapidocr_onnxruntime
                return True
            except ImportError:
                return False

    def _get_engine(self):
        if self._engine is None:
            try:
                from rapidocr import RapidOCR
                self._package_name = "rapidocr"
                self._package_version = importlib.metadata.version("rapidocr")
                self._model_version = "PP-OCRv6-onnx"
                self._engine = RapidOCR()
            except ImportError:
                from rapidocr_onnxruntime import RapidOCR
                self._package_name = "rapidocr-onnxruntime"
                self._package_version = importlib.metadata.version("rapidocr-onnxruntime")
                self._detector_model = "ch_ppocr_v3_det.onnx"
                self._recognizer_model = "ch_ppocr_mobile_v2.0_rec.onnx"
                self._model_version = "PP-OCRv3-onnx"
                self._engine = RapidOCR()
        return self._engine

    def _retry_reversed_values(self, engine, image, readings):
        """Recover an explicit value when the angle classifier flips its line."""
        flipped = [i for i, (_, text, _) in enumerate(readings) if re.search(r"\d\s*=\s*$", text)]
        if not flipped or not getattr(engine, "use_cls", False):
            return {}
        try:
            alternate = engine(image, use_cls=False)
        except Exception as error:
            logger.debug("OCR orientation retry failed: %s", type(error).__name__)
            return {}
        finally:
            # RapidOCR's per-call options persist on the engine.
            engine.use_cls = True

        if alternate.boxes is None or alternate.txts is None or alternate.scores is None:
            return {}
        explicit_value = re.compile(r"=\s*\d+(?:\.\d+)?\s*(?:k?[Ωω]|k?ohm|V)", re.IGNORECASE)
        alternatives = {}
        for index in flipped:
            box, original, confidence = readings[index]
            for new_box, text, score in zip(alternate.boxes, alternate.txts, alternate.scores):
                if (score >= 0.85 and score > (confidence or 0) and explicit_value.fullmatch(text.strip())
                        and np.array_equal(new_box, box)):
                    readings[index] = (box, text, score)
                    alternatives[index] = [{"text": original, "confidence": confidence, "provider": self.name}]
                    break
        return alternatives

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
                model=self.model_version,
                error="Neither rapidocr nor rapidocr-onnxruntime is installed in the active environment.",
            )

        start_time = time.perf_counter()

        # Handle optional region cropping
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
                model=self.model_version,
                package=self._package_name,
                package_version=self._package_version,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        alternatives = {}
        try:
            with self._engine_lock:
                engine = self._get_engine()
                res = engine(working_img)
                if hasattr(res, "boxes") and hasattr(res, "txts"):
                    # Unified rapidocr >= 3.9.0 RapidOCROutput
                    boxes = res.boxes if res.boxes is not None else []
                    txts = res.txts if res.txts is not None else []
                    scores = res.scores if res.scores is not None else []
                    raw_results = list(zip(boxes, txts, scores))
                    alternatives = self._retry_reversed_values(engine, working_img, raw_results)
                elif isinstance(res, (tuple, list)) and len(res) == 2:
                    # Legacy rapidocr_onnxruntime tuple (results, elapse)
                    raw_results, _ = res
                else:
                    raw_results = res
        except Exception as e:
            logger.error("[RapidOCRProvider] Execution failed: %s", e)
            return OCRExtractionResult(
                status=ExtractionStatus.ERROR,
                tokens=[],
                provider=self.name,
                model=self.model_version,
                package=self._package_name,
                package_version=self._package_version,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
                error=f"OCR execution error: {e}",
            )

        if not raw_results:
            return OCRExtractionResult(
                status=ExtractionStatus.NO_EVIDENCE,
                tokens=[],
                provider=self.name,
                model=self.model_version,
                package=self._package_name,
                package_version=self._package_version,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        tokens: list[OCRToken] = []
        for idx, item in enumerate(raw_results):
            pts_list = item[0]
            raw_text = str(item[1]).strip()
            score = float(item[2]) if len(item) > 2 and item[2] is not None else None

            if not raw_text:
                continue

            # Map polygon points back to native source_px
            src_points: list[SourcePoint] = []
            for p in pts_list:
                src_pt = transform.to_source_point(float(p[0]), float(p[1]), clip=True)
                src_points.append(src_pt)

            polygon = SourcePolygon(points=src_points)
            bbox = polygon.bbox

            # Script classification
            if raw_text.replace(".", "").replace("-", "").isdigit():
                script = "numeric"
            elif any(ord(c) >= 0x0980 and ord(c) <= 0x09FF for c in raw_text):
                script = "bengali"
            elif any(ord(c) >= 0x0370 and ord(c) <= 0x03FF for c in raw_text):
                script = "greek"
            elif raw_text.isascii() and any(c.isalpha() for c in raw_text):
                script = "latin"
            else:
                script = "mixed"

            token_id = f"ocr_tok_{idx+1:03d}"
            tokens.append(
                OCRToken(
                    id=token_id,
                    raw_text=raw_text,
                    normalized_text=None,
                    bbox_source_px=bbox,
                    polygon_source_px=polygon,
                    confidence=score,
                    script_candidate=script,
                    language_candidate="en" if script in ("latin", "numeric") else "und",
                    provider=self.name,
                    recognizer_model=self._recognizer_model,
                    evidence_ref=f"evidence_ocr_{token_id}",
                    candidate_alternatives=alternatives.get(idx, []),
                )
            )

        latency = (time.perf_counter() - start_time) * 1000.0
        return OCRExtractionResult(
            status=ExtractionStatus.SUCCESS,
            tokens=tokens,
            provider=self.name,
            model=self.model_version,
            package=self._package_name,
            package_version=self._package_version,
            detector_model=self._detector_model,
            recognizer_model=self._recognizer_model,
            recognizer_language=self._recognizer_language,
            latency_ms=latency,
        )

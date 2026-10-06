"""PR-06 Multi-Engine Multilingual OCR Router.

Orchestrates:
  - RapidOCR: fast local English, digits, coordinates, and primary layout detection.
  - EasyOCR Bangla: Bengali script text recognition with strict Unicode NFC preservation.
  - PhysicsSymbolCandidateResolver: confusable resolution (θ ↔ 8, Ω ↔ O ↔ 0, μ ↔ u, etc.).
  - FormulaRecognition: optional LaTeX equation parsing.

Rules:
  - Raw provider evidence is NEVER overwritten.
  - EasyOCR text is never labeled as coming from RapidOCR.
  - When Bangla OCR is available, it is genuinely executed, not gated on Latin OCR output.
  - Each text region retains immutable candidate records from all participating engines.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import numpy as np

from shared.schemas.evidence import (
    ExtractionStatus,
    OCRCandidate,
    OCRExtractionResult,
    OCRRegion,
    OCRToken,
    SourceBBox,
)
from ai.evidence.ocr.bangla import EasyOCRBanglaProvider, is_bengali_text
from ai.evidence.ocr.formula import (
    FormulaRecognitionProvider,
    UnavailableFormulaRecognitionProvider,
)
from ai.evidence.ocr.greek_symbols import (
    GreekSymbolVisualOCR,
    PhysicsSymbolCandidateResolver,
)
from ai.evidence.ocr.rapidocr import RapidOCRProvider

logger = logging.getLogger(__name__)


def deduplicate_spatial_tokens(tokens: List[OCRToken]) -> List[OCRToken]:
    """Canonical spatial & textual deduplication for OCR tokens.

    If token B is mostly contained within token A (containment >= 0.60 of B's area)
    and B's text is a substring, prefix, or suffix of A's text (e.g. 'Fig. 1' inside 'Fig. 1 Simple Pendulum'),
    or if IoU >= 0.70 between two tokens, subsume token B into token A.

    Preserves subsumed token in A's candidate_alternatives for diagnostic provenance,
    while returning a clean list of non-redundant canonical tokens.
    """
    if len(tokens) <= 1:
        return tokens

    # Sort tokens by area descending (largest text span first)
    sorted_tokens = sorted(
        tokens,
        key=lambda t: (t.bbox_source_px.width * t.bbox_source_px.height) if t.bbox_source_px else 0.0,
        reverse=True,
    )

    kept: List[OCRToken] = []
    dropped_ids = set()

    for i, a in enumerate(sorted_tokens):
        if a.id in dropped_ids:
            continue
        a_box = a.bbox_source_px
        if not a_box:
            kept.append(a)
            continue

        a_text = a.raw_text.strip().lower()
        a_area = a_box.width * a_box.height

        for j in range(i + 1, len(sorted_tokens)):
            b = sorted_tokens[j]
            if b.id in dropped_ids:
                continue
            b_box = b.bbox_source_px
            if not b_box:
                continue

            b_text = b.raw_text.strip().lower()
            b_area = b_box.width * b_box.height

            # Intersection
            ix1 = max(a_box.x, b_box.x)
            iy1 = max(a_box.y, b_box.y)
            ix2 = min(a_box.x + a_box.width, b_box.x + b_box.width)
            iy2 = min(a_box.y + a_box.height, b_box.y + b_box.height)
            iw = max(0.0, ix2 - ix1)
            ih = max(0.0, iy2 - iy1)
            inter_area = iw * ih

            if inter_area <= 0:
                continue

            containment_b = inter_area / (b_area + 1e-5)
            union_area = a_area + b_area - inter_area
            iou = inter_area / (union_area + 1e-5)

            # Check textual containment (prefix, suffix, substring)
            text_contained = (b_text in a_text) or (a_text.startswith(b_text)) or (b_text == "")

            # If B is mostly/fully inside A and text is subsumed, or high IoU
            if (containment_b >= 0.60 and text_contained) or iou >= 0.70:
                dropped_ids.add(b.id)
                a.candidate_alternatives.append({
                    "text": b.raw_text,
                    "bbox": b_box.to_dict() if hasattr(b_box, "to_dict") else b_box,
                    "confidence": b.confidence,
                    "provider": b.provider,
                    "subsumed_id": b.id,
                })

        kept.append(a)

    return kept


class MultiOCRRouter:
    """Intelligent OCR router combining RapidOCR, EasyOCR Bangla, Greek visual OCR, and physics symbol candidate resolution."""

    def __init__(
        self,
        primary_provider: Optional[RapidOCRProvider] = None,
        bangla_provider: Optional[EasyOCRBanglaProvider] = None,
        symbol_resolver: Optional[PhysicsSymbolCandidateResolver] = None,
        greek_provider: Optional[GreekSymbolVisualOCR] = None,
        formula_provider: Optional[FormulaRecognitionProvider] = None,
    ):
        self.primary = primary_provider or RapidOCRProvider()
        self.bangla = bangla_provider or EasyOCRBanglaProvider()
        self.symbol_resolver = symbol_resolver or PhysicsSymbolCandidateResolver()
        self.greek = greek_provider or GreekSymbolVisualOCR()
        self.formula = formula_provider or UnavailableFormulaRecognitionProvider()

    @property
    def name(self) -> str:
        return "multi_ocr_router"

    def available(self) -> bool:
        return self.primary.available() or self.bangla.available()

    def extract(
        self,
        image_bgr: np.ndarray,
        *,
        source_width: int,
        source_height: int,
        region: Optional[SourceBBox] = None,
    ) -> OCRExtractionResult:
        start_time = time.perf_counter()

        # 1. Primary RapidOCR extraction
        primary_result = self.primary.extract(
            image_bgr,
            source_width=source_width,
            source_height=source_height,
            region=region,
        )

        primary_tokens: List[OCRToken] = []
        if primary_result.status == ExtractionStatus.SUCCESS:
            primary_tokens.extend(primary_result.tokens)

        # 2. Genuine Bangla OCR execution when available
        bn_tokens: List[OCRToken] = []
        bn_result: Optional[OCRExtractionResult] = None
        if self.bangla.available():
            try:
                bn_result = self.bangla.extract(
                    image_bgr,
                    source_width=source_width,
                    source_height=source_height,
                    region=region,
                )
                if bn_result.status == ExtractionStatus.SUCCESS and bn_result.tokens:
                    bn_tokens.extend(bn_result.tokens)
            except Exception as e:
                logger.warning("[MultiOCRRouter] Bangla OCR extraction failed: %s", e)

        # 3. Transparent candidate fusion into immutable OCRRegions
        regions: List[OCRRegion] = []
        final_tokens: List[OCRToken] = []
        claimed_bn_indices = set()

        for p_idx, p_tok in enumerate(primary_tokens):
            p_box = p_tok.bbox_source_px
            p_cand = OCRCandidate(
                id=f"cand_primary_{p_idx+1:03d}",
                raw_text=p_tok.raw_text,
                normalized_text=p_tok.normalized_text or p_tok.raw_text,
                provider=p_tok.provider,
                recognizer_model=p_tok.recognizer_model or getattr(primary_result, "recognizer_model", "unknown"),
                confidence=p_tok.confidence,
                script_candidate=p_tok.script_candidate or "latin",
                language_candidate=p_tok.language_candidate or "en",
            )

            # Check overlap with any Bengali tokens
            best_overlap_bn_idx = None
            best_iou = 0.0

            if p_box:
                for b_idx, b_tok in enumerate(bn_tokens):
                    b_box = b_tok.bbox_source_px
                    if not b_box:
                        continue
                    inter_w = max(0.0, min(p_box.x + p_box.width, b_box.x + b_box.width) - max(p_box.x, b_box.x))
                    inter_h = max(0.0, min(p_box.y + p_box.height, b_box.y + b_box.height) - max(p_box.y, b_box.y))
                    inter_area = inter_w * inter_h
                    if inter_area > 0:
                        area_p = p_box.width * p_box.height
                        area_b = b_box.width * b_box.height
                        union_area = area_p + area_b - inter_area
                        iou = inter_area / union_area if union_area > 0 else 0.0
                        containment = inter_area / min(area_p, area_b) if min(area_p, area_b) > 0 else 0.0
                        text_sub = (b_tok.raw_text.strip().lower() in p_tok.raw_text.strip().lower()) or (p_tok.raw_text.strip().lower() in b_tok.raw_text.strip().lower())

                        is_overlapping = (iou > 0.25) or (containment > 0.60) or (text_sub and containment > 0.35)
                        if is_overlapping:
                            claimed_bn_indices.add(b_idx)
                            if (iou > best_iou or containment > 0.80):
                                best_iou = iou
                                best_overlap_bn_idx = b_idx

            candidates = [p_cand]
            resolved_token = p_tok

            if best_overlap_bn_idx is not None:
                claimed_bn_indices.add(best_overlap_bn_idx)
                b_tok = bn_tokens[best_overlap_bn_idx]
                b_cand = OCRCandidate(
                    id=f"cand_bangla_{best_overlap_bn_idx+1:03d}",
                    raw_text=b_tok.raw_text,
                    normalized_text=b_tok.normalized_text or b_tok.raw_text,
                    provider=b_tok.provider,
                    recognizer_model=b_tok.recognizer_model or (getattr(bn_result, "recognizer_model", "bengali.pth") if bn_result else "bengali.pth"),
                    confidence=b_tok.confidence,
                    script_candidate=b_tok.script_candidate or "bengali",
                    language_candidate=b_tok.language_candidate or "bn",
                )
                candidates.append(b_cand)

                # Decision: if Bengali candidate contains actual Bengali characters, resolve to EasyOCR token
                if is_bengali_text(b_tok.raw_text):
                    resolved_token = b_tok
                    resolved_token.candidate_alternatives = list(p_tok.candidate_alternatives)
                    resolved_token.candidate_alternatives.append({
                        "text": p_tok.raw_text,
                        "script": p_tok.script_candidate,
                        "confidence": p_tok.confidence,
                        "provider": p_tok.provider,
                    })
                else:
                    resolved_token.candidate_alternatives.append({
                        "text": b_tok.raw_text,
                        "script": b_tok.script_candidate,
                        "confidence": b_tok.confidence,
                        "provider": b_tok.provider,
                    })

            reg_id = f"ocr_reg_{len(regions)+1:03d}"
            regions.append(
                OCRRegion(
                    id=reg_id,
                    bbox_source_px=p_box or SourceBBox(0, 0, 1, 1),
                    polygon_source_px=p_tok.polygon_source_px,
                    candidates=candidates,
                    resolved_candidate_id=candidates[0].id if resolved_token == p_tok else (candidates[1].id if len(candidates) > 1 else candidates[0].id),
                )
            )
            final_tokens.append(resolved_token)

        # Add unclaimed Bengali tokens
        for b_idx, b_tok in enumerate(bn_tokens):
            if b_idx not in claimed_bn_indices:
                b_cand = OCRCandidate(
                    id=f"cand_bangla_{b_idx+1:03d}",
                    raw_text=b_tok.raw_text,
                    normalized_text=b_tok.normalized_text or b_tok.raw_text,
                    provider=b_tok.provider,
                    recognizer_model=b_tok.recognizer_model or (getattr(bn_result, "recognizer_model", "bengali.pth") if bn_result else "bengali.pth"),
                    confidence=b_tok.confidence,
                    script_candidate=b_tok.script_candidate or "bengali",
                    language_candidate=b_tok.language_candidate or "bn",
                )
                reg_id = f"ocr_reg_{len(regions)+1:03d}"
                regions.append(
                    OCRRegion(
                        id=reg_id,
                        bbox_source_px=b_tok.bbox_source_px or SourceBBox(0, 0, 1, 1),
                        polygon_source_px=b_tok.polygon_source_px,
                        candidates=[b_cand],
                        resolved_candidate_id=b_cand.id,
                    )
                )
                final_tokens.append(b_tok)

        # 4. Canonical spatial and textual deduplication pass
        final_tokens = deduplicate_spatial_tokens(final_tokens)

        # 5. Extract visual Greek & physics symbols from native image pixels
        try:
            greek_tokens = self.greek.extract_symbols(
                image_bgr,
                existing_tokens=final_tokens,
                source_width=source_width,
                source_height=source_height,
            )
            if greek_tokens:
                final_tokens.extend(greek_tokens)
        except Exception as _greek_err:
            logger.warning("[MultiOCRRouter] Greek symbol extraction error: %s", _greek_err)

        # 6. Enrich all final tokens with physics symbol candidate resolver
        for token in final_tokens:
            self.symbol_resolver.enrich_token(token)

        latency = (time.perf_counter() - start_time) * 1000.0
        status = ExtractionStatus.SUCCESS if final_tokens else (primary_result.status if primary_result.status != ExtractionStatus.SUCCESS else ExtractionStatus.NO_EVIDENCE)

        rec_model = getattr(primary_result, "recognizer_model", "PP-OCRv6_rec_small.onnx")
        if self.bangla.available():
            rec_model = f"{rec_model}+bengali.pth"

        return OCRExtractionResult(
            status=status,
            tokens=final_tokens,
            provider=self.name,
            model=getattr(primary_result, "model", "PP-OCRv6"),
            package="rapidocr+easyocr+greek_ocr",
            package_version=getattr(primary_result, "package_version", "3.9.2"),
            detector_model=getattr(primary_result, "detector_model", "PP-OCRv6_det_small.onnx"),
            recognizer_model=rec_model,
            recognizer_language="en+bn+el",
            latency_ms=latency,
            metadata={
                "bangla_available": self.bangla.available(),
                "greek_available": self.greek.available(),
                "formula_available": self.formula.available(),
                "regions_count": len(regions),
                "token_count": len(final_tokens),
            },
        )

"""PR-06 Evidence Extraction Pipeline Orchestrator.

Orchestrates OCR, Classical CV, and Segmentation providers to extract visual
evidence and ground semantic BookIR entities prior to PhysicsCompiler.

Execution Order:
  SourceAsset + PageIR + Semantic BookIR (PR-05)
        ↓
  OCR (RapidOCR / Tesseract / Mock)
        ↓
  Classical CV (deterministic geometry)
        ↓
  Segmentation (SAM 2 / Mock)
        ↓
  Subtype Evidence Fusion (GrounderRegistry)
        ↓
  Grounded BookIR (with verified geometry & parameter candidates)
        ↓
  PhysicsCompiler (Safety Gate)
"""
from __future__ import annotations

import logging
import time
from typing import Dict, Optional

import numpy as np

from shared.schemas.evidence import (
    EvidenceExtractionResult,
    ExtractionStatus,
    OCRExtractionResult,
    SegmentationResult,
    SourceBBox,
)
from shared.schemas.ingestion import BookIR, BookIRStatus, PageIR, PageTextBlock, SourceAsset
from ai.evidence.cv import (
    CircuitCVCandidateExtractor,
    InterfaceRefractionCVCandidateExtractor,
    PendulumCVCandidateExtractor,
    PrismCVCandidateExtractor,
    ProjectileCVCandidateExtractor,
    SphericalMirrorCVCandidateExtractor,
    ThinLensCVCandidateExtractor,
)
from ai.evidence.grounding import GrounderRegistry, get_default_grounder_registry
from ai.evidence.ocr import MultiOCRRouter, OCRProvider, RapidOCRProvider
from ai.evidence.segmentation import (
    SAM2SegmentationProvider,
    SegmentationPrompt,
    SegmentationProvider,
)
from ai.evidence.transforms import load_and_validate_source_image

logger = logging.getLogger(__name__)


class EvidenceExtractionPipeline:
    """Orchestrates evidence extraction (OCR, CV, Segmentation) and entity grounding."""

    def __init__(
        self,
        ocr_provider: Optional[OCRProvider] = None,
        segmentation_provider: Optional[SegmentationProvider] = None,
        grounder_registry: Optional[GrounderRegistry] = None,
    ):
        self.ocr_provider = ocr_provider or MultiOCRRouter()
        self.segmentation_provider = segmentation_provider or SAM2SegmentationProvider()
        self.grounder_registry = grounder_registry or get_default_grounder_registry()
        self.cv_extractors = {
            "pendulum": PendulumCVCandidateExtractor(),
            "projectile": ProjectileCVCandidateExtractor(),
            "thin_lens": ThinLensCVCandidateExtractor(),
            "concave_lens": ThinLensCVCandidateExtractor(),
            "spherical_mirror": SphericalMirrorCVCandidateExtractor(),
            "mirror": SphericalMirrorCVCandidateExtractor(),
            "concave_mirror": SphericalMirrorCVCandidateExtractor(),
            "convex_mirror": SphericalMirrorCVCandidateExtractor(),
            "interface_refraction": InterfaceRefractionCVCandidateExtractor(),
            "refraction": InterfaceRefractionCVCandidateExtractor(),
            "snell": InterfaceRefractionCVCandidateExtractor(),
            "prism": PrismCVCandidateExtractor(),
            "dc_linear": CircuitCVCandidateExtractor(),
            "circuit": CircuitCVCandidateExtractor(),
            "dc_circuit": CircuitCVCandidateExtractor(),
            "resistors": CircuitCVCandidateExtractor(),
        }

    def extract_and_fuse(
        self,
        asset: SourceAsset,
        page_ir: PageIR,
        book_ir: BookIR,
    ) -> BookIR:
        """Run the full evidence extraction and fusion pipeline to produce Grounded BookIR.

        Args:
            asset: Real uploaded SourceAsset with validated bytes on disk.
            page_ir: PageIR structure in source_px.
            book_ir: PR-05 semantic BookIR.

        Returns:
            Grounded BookIR with populated source_px geometry and parameter candidates.
        """
        # Section 94: Do not run grounding on non-physics or unknown diagrams
        classification = book_ir.provenance.get("classification")
        if classification in ("non_physics", "unknown") or book_ir.domain is None or book_ir.subtype is None:
            logger.info("[EvidenceExtractionPipeline] Skipping grounding for non-physics/unresolved BookIR.")
            return book_ir

        # Section 95: Do not run subtype grounding on unsupported physics
        if classification == "unsupported_physics" or book_ir.status == BookIRStatus.UNSUPPORTED:
            logger.info("[EvidenceExtractionPipeline] Skipping grounding for unsupported physics diagram.")
            return book_ir

        # Find matching subtype grounder
        grounder = self.grounder_registry.find_grounder(book_ir.domain, book_ir.subtype)
        if not grounder:
            logger.info(
                "[EvidenceExtractionPipeline] No grounder registered for %s/%s.",
                book_ir.domain,
                book_ir.subtype,
            )
            return book_ir

        start_time = time.perf_counter()

        # 1. Load and strictly validate source image dimensions
        try:
            img_bgr = load_and_validate_source_image(asset)
        except Exception as e:
            logger.error("[EvidenceExtractionPipeline] Image load error: %s", e)
            book_ir.status = BookIRStatus.NEEDS_REVIEW
            book_ir.status_notes = f"Failed to load image for visual grounding: {e}"
            return book_ir

        src_w, src_h = asset.width_px, asset.height_px

        # 2. Extract OCR evidence
        ocr_result: Optional[OCRExtractionResult] = None
        ocr_boxes: list[SourceBBox] = []
        if self.ocr_provider.available():
            try:
                ocr_result = self.ocr_provider.extract(
                    img_bgr,
                    source_width=src_w,
                    source_height=src_h,
                )
                if ocr_result and ocr_result.tokens:
                    ocr_boxes = [t.bbox_source_px for t in ocr_result.tokens if t.bbox_source_px]
            except Exception as e:
                logger.warning("[EvidenceExtractionPipeline] OCR extraction error: %s", e)
                ocr_result = OCRExtractionResult(
                    status=ExtractionStatus.ERROR,
                    tokens=[],
                    provider=self.ocr_provider.name,
                    error=str(e),
                )
        else:
            ocr_result = OCRExtractionResult(
                status=ExtractionStatus.UNAVAILABLE,
                tokens=[],
                provider=self.ocr_provider.name,
                error="OCR provider unavailable.",
            )

        # Section 10: Populate PageIR text blocks from verified OCR tokens
        if ocr_result and ocr_result.tokens:
            page_ir.text_blocks = [
                PageTextBlock(
                    id=t.id,
                    text=t.raw_text,
                    x=float(t.bbox_source_px.x) if t.bbox_source_px else 0.0,
                    y=float(t.bbox_source_px.y) if t.bbox_source_px else 0.0,
                    width=float(t.bbox_source_px.width) if t.bbox_source_px else 0.0,
                    height=float(t.bbox_source_px.height) if t.bbox_source_px else 0.0,
                    confidence=float(t.confidence or 0.0),
                    extraction_method="ocr",
                )
                for t in ocr_result.tokens
            ]
            page_ir.metadata["pipeline"] = "PR-06"
            page_ir.metadata["ocr_provider"] = ocr_result.provider
            page_ir.metadata["note"] = "Single-diagram upload. Text blocks populated via PR-06 OCR pipeline."

        # 3. Extract Classical CV candidates (with OCR text box suppression)
        cv_candidates: Dict[str, Any] = {}
        subtype_key = (book_ir.subtype or "").lower()
        extractor = self.cv_extractors.get(subtype_key)
        if extractor:
            try:
                if hasattr(extractor, "extract_candidates"):
                    cv_candidates = extractor.extract_candidates(
                        img_bgr,
                        source_width=src_w,
                        source_height=src_h,
                        ocr_boxes=ocr_boxes,
                    )
                else:
                    cv_candidates = extractor.extract(
                        img_bgr,
                        source_width=src_w,
                        source_height=src_h,
                        ocr_boxes=ocr_boxes,
                    )
            except Exception as e:
                logger.warning("[EvidenceExtractionPipeline] CV candidate extraction error for %s: %s", subtype_key, e)
                cv_candidates = {"error": str(e), "best_proposal": None}
        else:
            logger.info("[EvidenceExtractionPipeline] No dedicated CV extractor for subtype: %s", subtype_key)

        # 4. Extract Segmentation candidates (bob, optics elements, etc.)
        seg_result: Optional[SegmentationResult] = None
        best_prop = cv_candidates.get("best_proposal")
        if best_prop and best_prop.get("bob"):
            bob_cand = best_prop["bob"]
            # Prompt segmentation using CV candidate bbox and center point
            bob_bounds = bob_cand["bounds"]
            bob_center = bob_cand["center"]
            prompt = SegmentationPrompt(
                box=bob_bounds,
                points=[(bob_center.x, bob_center.y)],
                labels=[1],
            )

            if self.segmentation_provider.available():
                try:
                    seg_result = self.segmentation_provider.segment(
                        img_bgr,
                        prompt,
                        source_width=src_w,
                        source_height=src_h,
                        entity_id="bob",
                    )
                except Exception as e:
                    logger.warning("[EvidenceExtractionPipeline] Segmentation error: %s", e)
                    seg_result = SegmentationResult(
                        status=ExtractionStatus.ERROR,
                        masks=[],
                        provider=self.segmentation_provider.name,
                        error=str(e),
                    )
            else:
                seg_result = SegmentationResult(
                    status=ExtractionStatus.UNAVAILABLE,
                    masks=[],
                    provider=self.segmentation_provider.name,
                    error="Segmentation provider unavailable.",
                )

        # 5. Fuse evidence via Subtype Grounder
        outcome = grounder.ground(
            book_ir=book_ir,
            cv_candidates=cv_candidates,
            ocr_result=ocr_result,
            seg_result=seg_result,
            source_width=src_w,
            source_height=src_h,
        )

        grounded_ir = outcome.grounded_book_ir
        grounded_ir.provenance["evidence_pipeline_latency_ms"] = (time.perf_counter() - start_time) * 1000.0

        return grounded_ir

    def ground(
        self,
        asset: SourceAsset,
        page_ir: PageIR,
        book_ir: BookIR,
    ) -> BookIR:
        """Ground semantic BookIR entities using visual CV, SAM, and OCR evidence.

        Canonical API for the PR-06 grounding orchestration layer.
        """
        return self.extract_and_fuse(asset=asset, page_ir=page_ir, book_ir=book_ir)


# Canonical alias for PR-06 grounding orchestration
GroundingPipeline = EvidenceExtractionPipeline


"""PR-05 BookUnderstandingPipeline — Multimodal VLM Semantic Understanding.

Integrates PhysicsVisionAnalyzer into the real ingestion pipeline:
  real image bytes → SourceAsset → PageIR → VLM semantic analysis → BookIR

Rules:
  - domain and subtype are strictly canonical physics identifiers or null.
  - subtype NEVER contains status words like 'non_physics' or 'unsupported_physics'.
  - VLM-read numbers/text remain unverified semantic evidence in visible_labels,
    NEVER directly trusted into BookIR.parameters.
  - Zero fabricated coordinates or parameters.
  - Status is determined truthfully:
      supported concept → NEEDS_REVIEW (requires CV/OCR geometry before simulation)
      unsupported concept → UNSUPPORTED
      non-physics / unknown → UNRESOLVED
      provider failure → UNRESOLVED with honest failure message
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from shared.schemas.ingestion import (
    BookEntity,
    BookIR,
    BookIRStatus,
    PageIR,
    SourceAsset,
)
from shared.schemas.semantic import (
    SemanticAnalysisResult,
    SemanticCandidate,
    SemanticConfidence,
)
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.provider_interface import (
    VisionProvider,
    VisionProviderError,
    VLMConfigurationError,
)

logger = logging.getLogger(__name__)


class BookUnderstandingPipeline:
    """Semantic physics understanding pipeline for textbook diagrams."""

    PIPELINE_VERSION = "PR-05-vlm"

    def __init__(self, analyzer: Optional[PhysicsVisionAnalyzer] = None):
        self.analyzer = analyzer

    def _get_analyzer(self) -> PhysicsVisionAnalyzer:
        """Lazily build default analyzer with GeminiVisionProvider if none supplied."""
        if self.analyzer is None:
            from ai.ingestion.vision.gemini_provider import GeminiVisionProvider
            provider = GeminiVisionProvider()
            self.analyzer = PhysicsVisionAnalyzer(provider=provider)
        return self.analyzer

    def analyze(
        self,
        page_ir: PageIR,
        asset: Optional[SourceAsset] = None,
    ) -> BookIR:
        """Analyze a PageIR and SourceAsset to produce a semantic BookIR.

        Args:
            page_ir: The PageIR constructed from the uploaded image.
            asset:   The SourceAsset pointing to the actual image file on disk.

        Returns:
            BookIR populated with semantic understanding without fabricated parameters.
        """
        figure_id = page_ir.figures[0].id if page_ir.figures else None
        asset_id = asset.id if asset else page_ir.source.get("assetId")

        # If no asset is provided, we cannot run multimodal vision
        if not asset:
            return self._build_unresolved_ir(
                asset_id=asset_id,
                page_ir_version=page_ir.version,
                figure_id=figure_id,
                reason="No SourceAsset provided to BookUnderstandingPipeline for VLM analysis.",
            )

        try:
            analyzer = self._get_analyzer()
            result: SemanticAnalysisResult = analyzer.analyze(asset, page_ir)
            return self._build_book_ir_from_result(result, asset_id, page_ir.version, figure_id)

        except VLMConfigurationError as ce:
            logger.warning("[BookUnderstandingPipeline] VLM Configuration error: %s", ce)
            return self._build_unresolved_ir(
                asset_id=asset_id,
                page_ir_version=page_ir.version,
                figure_id=figure_id,
                reason=f"VLM configuration error: {ce}",
                error_type="VLMConfigurationError",
            )
        except VisionProviderError as pe:
            logger.error("[BookUnderstandingPipeline] Vision Provider error: %s", pe)
            return self._build_unresolved_ir(
                asset_id=asset_id,
                page_ir_version=page_ir.version,
                figure_id=figure_id,
                reason=f"Vision provider analysis failed: {pe}",
                error_type="VisionProviderError",
            )
        except Exception as e:
            logger.error("[BookUnderstandingPipeline] Unexpected analysis error: %s", e)
            return self._build_unresolved_ir(
                asset_id=asset_id,
                page_ir_version=page_ir.version,
                figure_id=figure_id,
                reason=f"Semantic analysis error: {e}",
                error_type=type(e).__name__,
            )

    def _build_book_ir_from_result(
        self,
        result: SemanticAnalysisResult,
        asset_id: Optional[str],
        page_ir_version: str,
        figure_id: Optional[str],
    ) -> BookIR:
        """Map validated SemanticAnalysisResult into canonical BookIR."""
        # 1. Transform semantic entities into BookEntities
        # CRITICAL RULE (PR-05 vs PR-06 boundary):
        # PR-05 establishes WHAT an entity is (semantic role), NOT WHERE it precisely is.
        # Authoritative position_source_px and geometry remain strictly None until PR-06 CV.
        # Any coarse VLM bbox is preserved only in unverified attributes.
        book_entities: list[BookEntity] = []
        for e in result.entities:
            entity_attrs = {
                "confidence": e.confidence,
                "precision": e.precision,
                "vlmLocalizationVerified": False,
            }
            if e.approx_bbox:
                entity_attrs["vlmApproxBBox"] = e.approx_bbox
                entity_attrs["vlmPrecision"] = "approximate"
                entity_attrs["source"] = "vlm"

            book_entities.append(
                BookEntity(
                    id=e.temporary_id,
                    type=e.role,
                    label=e.label,
                    position_source_px=None,  # STRICTLY None in PR-05
                    geometry=None,            # STRICTLY None in PR-05
                    attributes=entity_attrs,
                    evidence_refs=[figure_id] if figure_id else [],
                )
            )

        # 2. Transform relationships
        relationships = [r.to_dict() for r in result.relationships]

        # 3. Parameters remain EMPTY in PR-05
        # Visible labels remain unverified candidate evidence
        visible_labels_data = [l.to_dict() for l in result.visible_labels]

        # 4. Status determination
        if result.classification == "supported" and result.is_supported:
            status = BookIRStatus.NEEDS_REVIEW
            status_notes = (
                f"Semantically understood as {result.domain}/{result.subtype}. "
                "Precise geometric localization and OCR parameter extraction (PR-06) "
                "required before simulation can be compiled."
            )
        elif result.classification == "unsupported_physics":
            status = BookIRStatus.UNSUPPORTED
            status_notes = (
                "Image contains a physics diagram for which no interactive "
                "simulation solver is currently implemented."
            )
        elif result.classification == "non_physics":
            status = BookIRStatus.UNRESOLVED
            status_notes = "Image does not depict a recognizable physics diagram or experiment."
        else:
            status = BookIRStatus.UNRESOLVED
            status_notes = "Unable to classify diagram into a supported physics scenario with sufficient confidence."

        provenance = {
            "pipeline": self.PIPELINE_VERSION,
            "provider": result.provider,
            "model": result.model,
            "prompt_version": result.prompt_version,
            "timestamp": result.timestamp,
            "classification": result.classification,
            "visible_labels": visible_labels_data,
            "candidates": [c.to_dict() for c in result.candidates],
            "notes": result.notes,
        }
        if result.latency_ms is not None:
            provenance["latency_ms"] = result.latency_ms
        if result.cache_hit:
            provenance["cache_hit"] = result.cache_hit
        if result.fallback_used:
            provenance["fallback_used"] = result.fallback_used
        if result.debug:
            provenance["debug"] = result.debug

        return BookIR(
            version="1.0",
            source_asset_id=asset_id,
            page_ir_version=page_ir_version,
            figure_id=figure_id,
            domain=result.domain,
            subtype=result.subtype,
            entities=book_entities,
            relationships=relationships,
            parameters={},  # STRICTLY EMPTY: PR-06 OCR will promote verified parameters
            geometry={},    # STRICTLY EMPTY: PR-06 CV will provide source_px geometry
            assumptions=[],
            provenance=provenance,
            confidence=result.confidence.to_dict(),
            status=status,
            status_notes=status_notes,
        )

    def _build_unresolved_ir(
        self,
        asset_id: Optional[str],
        page_ir_version: str,
        figure_id: Optional[str],
        reason: str,
        error_type: Optional[str] = None,
    ) -> BookIR:
        """Construct an honest UNRESOLVED BookIR on failure or missing requirements."""
        prov = {
            "pipeline": self.PIPELINE_VERSION,
            "note": reason,
        }
        if error_type:
            prov["error_type"] = error_type
            prov["error"] = reason

        return BookIR(
            version="1.0",
            source_asset_id=asset_id,
            page_ir_version=page_ir_version,
            figure_id=figure_id,
            domain=None,
            subtype=None,
            entities=[],
            relationships=[],
            parameters={},
            geometry={},
            assumptions=[],
            provenance=prov,
            confidence={
                "isPhysics": 0.0,
                "domain": 0.0,
                "subtype": 0.0,
                "overall": 0.0,
            },
            status=BookIRStatus.UNRESOLVED,
            status_notes=reason,
        )

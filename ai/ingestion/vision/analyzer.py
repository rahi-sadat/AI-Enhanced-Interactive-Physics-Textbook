"""PR-05 PhysicsVisionAnalyzer — High-level semantic analysis coordinator.

Responsibilities:
  - Validates that real SourceAsset bytes exist.
  - Passes real bytes to the configured VisionProvider.
  - Applies configurable semantic confidence thresholds.
  - Ensures low-confidence predictions are not hard-classified.
  - Preserves candidate interpretations for ambiguous diagrams.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from shared.schemas.ingestion import PageIR, SourceAsset
from shared.schemas.semantic import (
    SemanticAnalysisResult,
    SemanticCandidate,
    SemanticConfidence,
)
from ai.ingestion.vision.provider_interface import (
    VisionProvider,
    VisionProviderError,
    VLMConfigurationError,
)


class PhysicsVisionAnalyzer:
    """Coordinates multimodal semantic diagram analysis."""

    def __init__(
        self,
        provider: VisionProvider,
        is_physics_threshold: float = 0.80,
        domain_threshold: float = 0.70,
        subtype_threshold: float = 0.70,
    ):
        self.provider = provider
        self.is_physics_threshold = is_physics_threshold
        self.domain_threshold = domain_threshold
        self.subtype_threshold = subtype_threshold

    def analyze(
        self,
        source_asset: SourceAsset,
        page_ir: PageIR,
    ) -> SemanticAnalysisResult:
        """Analyze the real image bytes represented by SourceAsset.

        Args:
            source_asset: The SourceAsset containing file location & dimensions.
            page_ir:      The PageIR describing document regions.

        Returns:
            SemanticAnalysisResult with thresholding applied.
        """
        if not source_asset:
            raise VisionProviderError("SourceAsset is required for semantic analysis.")

        # Read actual image bytes from disk
        path = Path(source_asset.storage_path)
        if not path.is_file():
            raise VisionProviderError(f"SourceAsset storage file not found at {path}")

        try:
            image_bytes = path.read_bytes()
        except Exception as e:
            raise VisionProviderError(f"Failed to read image bytes from {path}: {e}")

        # Delegate to provider
        result = self.provider.analyze_diagram(
            image_bytes=image_bytes,
            mime_type=source_asset.mime_type,
            page_ir=page_ir,
        )

        # Apply confidence thresholds
        return self._apply_thresholds(result)

    def _apply_thresholds(self, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Ensure low-confidence predictions are not treated as hard classifications."""
        conf = result.confidence

        # If non-physics, no domain/subtype thresholds needed
        if result.classification == "non_physics" or result.is_physics is False:
            return result

        # 1. Check is_physics confidence
        if conf.is_physics < self.is_physics_threshold and result.is_physics is True:
            # Low confidence that this is even physics
            if result.domain or result.subtype:
                result.candidates.append(SemanticCandidate(
                    domain=result.domain,
                    subtype=result.subtype,
                    confidence=conf.subtype or conf.domain,
                ))
            result.classification = "unknown"
            result.is_physics = None
            result.domain = None
            result.subtype = None
            result.notes.append(
                f"is_physics confidence {conf.is_physics:.2f} below threshold {self.is_physics_threshold:.2f}; downgraded to unknown."
            )
            return result

        # 2. Check domain confidence
        if conf.domain < self.domain_threshold and result.domain is not None:
            result.candidates.append(SemanticCandidate(
                domain=result.domain,
                subtype=result.subtype,
                confidence=conf.domain,
            ))
            result.classification = "unknown"
            result.domain = None
            result.subtype = None
            result.notes.append(
                f"Domain confidence {conf.domain:.2f} below threshold {self.domain_threshold:.2f}; preserved as candidate."
            )
            return result

        # 3. Check subtype confidence
        if conf.subtype < self.subtype_threshold and result.subtype is not None:
            result.candidates.append(SemanticCandidate(
                domain=result.domain,
                subtype=result.subtype,
                confidence=conf.subtype,
            ))
            result.classification = "unknown"
            result.subtype = None
            result.notes.append(
                f"Subtype confidence {conf.subtype:.2f} below threshold {self.subtype_threshold:.2f}; preserved as candidate."
            )
            return result

        return result

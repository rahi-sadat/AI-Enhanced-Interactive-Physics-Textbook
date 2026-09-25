"""PR-05 Vision Provider Abstraction.

Defines the pluggable interface for multimodal VLM semantic analysis.
The rest of AugmentedPhysics depends only on VisionProvider, NOT on any
specific external SDK or vendor API.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from shared.schemas.ingestion import PageIR, SourceAsset
from shared.schemas.semantic import SemanticAnalysisResult


class VisionProviderError(Exception):
    """Raised when the vision provider encounters an operational or API error."""
    pass


class VLMConfigurationError(VisionProviderError):
    """Raised when required API credentials or configurations are missing."""
    pass


class VisionProvider(ABC):
    """Abstract provider for multimodal physics diagram semantic analysis."""

    @abstractmethod
    def analyze_diagram(
        self,
        image_bytes: bytes,
        mime_type: str,
        page_ir: PageIR,
    ) -> SemanticAnalysisResult:
        """Analyze actual image bytes and return structured semantic analysis.

        Args:
            image_bytes: The raw bytes of the uploaded diagram.
            mime_type:   MIME type (e.g. 'image/png', 'image/jpeg').
            page_ir:     The PageIR describing the document context.

        Returns:
            SemanticAnalysisResult conforming to the PR-05 schema.

        Raises:
            VLMConfigurationError: If API credentials or models are unconfigured.
            VisionProviderError: If the provider call fails or response is invalid.
        """
        pass

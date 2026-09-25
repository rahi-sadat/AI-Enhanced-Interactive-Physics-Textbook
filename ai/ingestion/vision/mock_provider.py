"""PR-05 Mock Vision Provider for Deterministic Unit & Integration Testing.

Allows testing without network dependencies, external API keys, or non-deterministic outputs.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from shared.schemas.ingestion import PageIR
from shared.schemas.semantic import (
    SemanticAnalysisResult,
    SemanticConfidence,
    SemanticEntity,
    SemanticRelationship,
    SemanticVisibleLabel,
    validate_semantic_payload,
)
from ai.ingestion.vision.provider_interface import VisionProvider, VisionProviderError


class MockVisionProvider(VisionProvider):
    """Deterministic mock provider with customizable responses and call inspection."""

    def __init__(
        self,
        default_result: Optional[SemanticAnalysisResult] = None,
        exception_to_raise: Optional[Exception] = None,
    ):
        self.default_result = default_result
        self.exception_to_raise = exception_to_raise
        self.call_history: List[Dict[str, Any]] = []
        self._custom_handler: Optional[Callable[[bytes, str, PageIR], SemanticAnalysisResult]] = None

    def set_handler(self, handler: Callable[[bytes, str, PageIR], SemanticAnalysisResult]):
        """Set a dynamic response generator based on image bytes / page_ir."""
        self._custom_handler = handler

    def analyze_diagram(
        self,
        image_bytes: bytes,
        mime_type: str,
        page_ir: PageIR,
    ) -> SemanticAnalysisResult:
        # Record invocation for assertions (verifying payload received)
        self.call_history.append({
            "byte_size": len(image_bytes),
            "image_bytes_preview": image_bytes[:32],
            "mime_type": mime_type,
            "page_ir_figures": len(page_ir.figures),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        if self.exception_to_raise:
            raise self.exception_to_raise

        if self._custom_handler:
            return self._custom_handler(image_bytes, mime_type, page_ir)

        if self.default_result:
            return self.default_result

        # Default fallback: honest unknown result
        return SemanticAnalysisResult(
            classification="unknown",
            is_physics=None,
            domain=None,
            subtype=None,
            confidence=SemanticConfidence(is_physics=0.0, domain=0.0, subtype=0.0),
            provider="mock",
            model="mock-v1",
            prompt_version="pr05-v1",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

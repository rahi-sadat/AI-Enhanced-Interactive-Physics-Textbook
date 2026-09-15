"""backend/core/provenance.py

Provenance and confidence tracking data structures for physical and electrical parameters.
Ensures that no physical quantity is silently guessed or hallucinated.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SourceType(str, Enum):
    OCR = "ocr"
    VLM = "vlm"
    USER_CONFIRMED = "user_confirmed"
    DEFAULT = "default"
    MANUAL = "manual"
    CALCULATED = "calculated"


class SimulationMode(str, Enum):
    PRECISION = "precision"
    ASSISTED = "assisted"
    APPROXIMATE = "approximate"


@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float

    def to_list(self) -> list[float]:
        return [self.x1, self.y1, self.x2, self.y2]


@dataclass
class ProvenanceRecord:
    source: SourceType
    confidence: float
    raw_text: Optional[str] = None
    bbox_source_px: Optional[list[float]] = None
    binding_confidence: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = {
            "source": self.source.value if isinstance(self.source, SourceType) else str(self.source),
            "confidence": round(float(self.confidence), 4),
        }
        if self.raw_text is not None:
            d["raw_text"] = self.raw_text
        if self.bbox_source_px is not None:
            d["bbox_source_px"] = self.bbox_source_px
        if self.binding_confidence is not None:
            d["binding_confidence"] = round(float(self.binding_confidence), 4)
        if self.metadata:
            d["metadata"] = self.metadata
        return d


@dataclass
class CircuitConfidence:
    component_detection: float = 1.0
    terminal_detection: float = 1.0
    wire_extraction: float = 1.0
    topology: float = 1.0
    parameter_binding: float = 1.0

    def overall(self) -> float:
        """Conservative minimum confidence gating.
        For circuits, high component score + low topology score must not equal precision.
        """
        return min(
            self.component_detection,
            self.terminal_detection,
            self.wire_extraction,
            self.topology,
            self.parameter_binding,
        )

    def determine_mode(self, threshold: float = 0.90) -> SimulationMode:
        if self.topology < threshold or self.parameter_binding < 0.85:
            return SimulationMode.ASSISTED
        return SimulationMode.PRECISION

    def to_dict(self) -> dict[str, float]:
        return {
            "component_detection": round(self.component_detection, 4),
            "terminal_detection": round(self.terminal_detection, 4),
            "wire_extraction": round(self.wire_extraction, 4),
            "topology": round(self.topology, 4),
            "parameter_binding": round(self.parameter_binding, 4),
            "overall": round(self.overall(), 4),
        }

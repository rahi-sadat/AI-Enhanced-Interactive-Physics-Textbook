"""PR-06 Evidence Extraction & Visual Grounding Data Contracts.

Defines schemas and models for precise evidence extraction, visual grounding,
OCR tokens, classical CV primitives, segmentation masks, and evidence fusion.

Rules:
  - Coordinate space is strictly 'source_px' (native uploaded image pixels).
  - Raw OCR evidence and normalized interpretations are strictly separated.
  - Coarse VLM bounding boxes remain distinct from CV/SAM verified geometry.
  - Zero fabricated parameters: uncertain evidence remains UNRESOLVED/AMBIGUOUS.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple, Union


class EvidenceMethod(str, Enum):
    VLM = "vlm"
    OCR = "ocr"
    CLASSICAL_CV = "classical_cv"
    SEGMENTATION = "segmentation"
    FUSED = "fused"
    MANUAL = "manual"


class ExtractionStatus(str, Enum):
    SUCCESS = "success"
    NO_EVIDENCE = "no_evidence"
    AMBIGUOUS = "ambiguous"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class GroundingState(str, Enum):
    GROUNDED = "grounded"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Source-Pixel Geometry Primitives
# ---------------------------------------------------------------------------

@dataclass
class SourcePoint:
    """A 2D point strictly in native source pixels."""
    x: float
    y: float

    def __post_init__(self):
        if not (math.isfinite(self.x) and math.isfinite(self.y)):
            raise ValueError(f"SourcePoint coordinates must be finite: ({self.x}, {self.y})")

    def to_dict(self) -> Dict[str, float]:
        return {"x": float(self.x), "y": float(self.y)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SourcePoint:
        return cls(x=float(data["x"]), y=float(data["y"]))

    def distance_to(self, other: SourcePoint) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)


@dataclass
class SourceBBox:
    """Axis-aligned bounding box strictly in native source pixels."""
    x: float
    y: float
    width: float
    height: float

    def __post_init__(self):
        for val, name in [(self.x, "x"), (self.y, "y"), (self.width, "width"), (self.height, "height")]:
            if not math.isfinite(val):
                raise ValueError(f"SourceBBox {name} must be finite: {val}")
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"SourceBBox dimensions must be positive: width={self.width}, height={self.height}")

    @property
    def x_max(self) -> float:
        return self.x + self.width

    @property
    def y_max(self) -> float:
        return self.y + self.height

    @property
    def center(self) -> SourcePoint:
        return SourcePoint(x=self.x + self.width / 2.0, y=self.y + self.height / 2.0)

    def to_dict(self) -> Dict[str, float]:
        return {
            "x": float(self.x),
            "y": float(self.y),
            "width": float(self.width),
            "height": float(self.height),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SourceBBox:
        return cls(
            x=float(data["x"]),
            y=float(data["y"]),
            width=float(data["width"]),
            height=float(data["height"]),
        )

    def contains(self, pt: SourcePoint) -> bool:
        return self.x <= pt.x <= self.x_max and self.y <= pt.y <= self.y_max

    def iou(self, other: SourceBBox) -> float:
        inter_x1 = max(self.x, other.x)
        inter_y1 = max(self.y, other.y)
        inter_x2 = min(self.x_max, other.x_max)
        inter_y2 = min(self.y_max, other.y_max)

        inter_w = max(0.0, inter_x2 - inter_x1)
        inter_h = max(0.0, inter_y2 - inter_y1)
        inter_area = inter_w * inter_h

        if inter_area <= 0.0:
            return 0.0

        area_self = self.width * self.height
        area_other = other.width * other.height
        union_area = area_self + area_other - inter_area
        return inter_area / union_area if union_area > 0 else 0.0


@dataclass
class SourceLine:
    """A directed line segment strictly in native source pixels."""
    start: SourcePoint
    end: SourcePoint

    @property
    def length_px(self) -> float:
        return self.start.distance_to(self.end)

    @property
    def midpoint(self) -> SourcePoint:
        return SourcePoint(
            x=(self.start.x + self.end.x) / 2.0,
            y=(self.start.y + self.end.y) / 2.0,
        )

    @property
    def angle_rad(self) -> float:
        return math.atan2(self.end.y - self.start.y, self.end.x - self.start.x)

    def distance_to_point(self, pt: SourcePoint | Tuple[float, float]) -> float:
        px = pt.x if hasattr(pt, "x") else pt[0]
        py = pt.y if hasattr(pt, "y") else pt[1]
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y
        dx, dy = x2 - x1, y2 - y1
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq < 1e-6:
            return math.hypot(px - x1, py - y1)
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / seg_len_sq))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "length_px": float(self.length_px),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SourceLine:
        return cls(
            start=SourcePoint.from_dict(data["start"]),
            end=SourcePoint.from_dict(data["end"]),
        )


@dataclass
class SourcePolygon:
    """A polygon strictly in native source pixels."""
    points: List[SourcePoint]

    def __post_init__(self):
        if len(self.points) < 3:
            raise ValueError(f"SourcePolygon must have at least 3 points, got {len(self.points)}")

    def to_dict(self) -> Dict[str, Any]:
        return {"points": [pt.to_dict() for pt in self.points]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SourcePolygon:
        return cls(points=[SourcePoint.from_dict(p) for p in data["points"]])

    @property
    def bbox(self) -> SourceBBox:
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max(1e-3, max_x - min_x)
        h = max(1e-3, max_y - min_y)
        return SourceBBox(x=min_x, y=min_y, width=w, height=h)


# ---------------------------------------------------------------------------
# OCR Contracts & Immutable Candidate Architecture
# ---------------------------------------------------------------------------

@dataclass
class OCRCandidate:
    """An immutable recognition candidate from a specific OCR engine."""
    id: str
    raw_text: str
    normalized_text: str
    provider: str
    recognizer_model: str
    confidence: Optional[float] = None
    script_candidate: str = "unknown"
    language_candidate: str = "unknown"
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rawText": self.raw_text,
            "normalizedText": self.normalized_text,
            "provider": self.provider,
            "recognizerModel": self.recognizer_model,
            "confidence": self.confidence,
            "scriptCandidate": self.script_candidate,
            "languageCandidate": self.language_candidate,
            "diagnostics": self.diagnostics,
        }


@dataclass
class OCRRegion:
    """A detected text region containing immutable candidate recognitions from multiple providers."""
    id: str
    bbox_source_px: SourceBBox
    polygon_source_px: Optional[SourcePolygon] = None
    candidates: List[OCRCandidate] = field(default_factory=list)
    resolved_candidate_id: Optional[str] = None
    resolution_diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "bboxSourcePx": self.bbox_source_px.to_dict(),
            "polygonSourcePx": self.polygon_source_px.to_dict() if self.polygon_source_px else None,
            "candidates": [c.to_dict() for c in self.candidates],
            "resolvedCandidateId": self.resolved_candidate_id,
            "resolutionDiagnostics": self.resolution_diagnostics,
        }


class AssociationState(str, Enum):
    ASSOCIATED = "associated"
    AMBIGUOUS = "ambiguous"
    REJECTED = "rejected"


@dataclass
class ParameterAssociationResult:
    """Rigorous semantic-to-OCR parameter association outcome."""
    candidate_id: str
    target_entity_id: Optional[str]
    target_quantity: str  # e.g. "length", "bob_mass", "initial_angle", "resistance", "voltage"
    value: float
    unit: str
    state: AssociationState
    supporting_evidence: List[str] = field(default_factory=list)
    association_checks: Dict[str, bool] = field(default_factory=dict)
    confidence: Optional[float] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "targetEntityId": self.target_entity_id,
            "targetQuantity": self.target_quantity,
            "value": self.value,
            "unit": self.unit,
            "state": self.state.value,
            "supportingEvidence": self.supporting_evidence,
            "associationChecks": self.association_checks,
            "confidence": self.confidence,
            "diagnostics": self.diagnostics,
        }


@dataclass
class OCRToken:
    """An individual text token extracted by OCR with script and candidate alternatives."""
    id: str
    raw_text: str
    normalized_text: Optional[str] = None
    bbox_source_px: Optional[SourceBBox] = None
    polygon_source_px: Optional[SourcePolygon] = None
    confidence: Optional[float] = None
    script_candidate: Optional[str] = None      # "latin" | "bengali" | "greek" | "numeric" | "math" | "mixed" | "unknown"
    language_candidate: Optional[str] = None    # "en" | "bn" | "el" | "und"
    provider: str = "unknown"
    recognizer_model: Optional[str] = None
    candidate_alternatives: List[Dict[str, Any]] = field(default_factory=list)
    evidence_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rawText": self.raw_text,
            "normalizedText": self.normalized_text,
            "bboxSourcePx": self.bbox_source_px.to_dict() if self.bbox_source_px else None,
            "polygonSourcePx": self.polygon_source_px.to_dict() if self.polygon_source_px else None,
            "confidence": self.confidence,
            "scriptCandidate": self.script_candidate,
            "languageCandidate": self.language_candidate,
            "provider": self.provider,
            "recognizerModel": self.recognizer_model,
            "candidateAlternatives": self.candidate_alternatives,
            "evidenceRef": self.evidence_ref,
        }


@dataclass
class OCRExtractionResult:
    """Outcome of an OCR extraction run on a figure with detailed model provenance."""
    status: ExtractionStatus
    tokens: List[OCRToken] = field(default_factory=list)
    provider: str = "unknown"
    model: Optional[str] = None
    package: Optional[str] = None
    package_version: Optional[str] = None
    detector_model: Optional[str] = None
    recognizer_model: Optional[str] = None
    recognizer_language: Optional[str] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "tokens": [t.to_dict() for t in self.tokens],
            "provider": self.provider,
            "model": self.model,
            "package": self.package,
            "packageVersion": self.package_version,
            "detectorModel": self.detector_model,
            "recognizerModel": self.recognizer_model,
            "recognizerLanguage": self.recognizer_language,
            "latencyMs": self.latency_ms,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class FormulaRecognitionResult:
    """Outcome of specialized formula/equation recognition on a candidate image crop."""
    status: ExtractionStatus
    raw_text: str = ""
    latex_candidate: Optional[str] = None
    confidence: Optional[float] = None
    bbox_source_px: Optional[SourceBBox] = None
    provider: str = "formula_recognizer"
    model: Optional[str] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None

    @property
    def latex(self) -> Optional[str]:
        return self.latex_candidate

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "rawText": self.raw_text,
            "latexCandidate": self.latex_candidate,
            "confidence": self.confidence,
            "bboxSourcePx": self.bbox_source_px.to_dict() if self.bbox_source_px else None,
            "provider": self.provider,
            "model": self.model,
            "latencyMs": self.latency_ms,
            "error": self.error,
        }


@dataclass
class ParsedPhysicalValueCandidate:
    """Physical value parsed from OCR text candidate."""
    raw_text: str
    numeric_value: Optional[float] = None
    raw_unit: Optional[str] = None
    canonical_unit: Optional[str] = None
    quantity_candidate: Optional[str] = None  # "length", "angle", "mass", "time", "voltage", etc.
    source_ocr_token_id: str = ""
    confidence: Optional[float] = None

    @property
    def token_id(self) -> str:
        return self.source_ocr_token_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rawText": self.raw_text,
            "numericValue": self.numeric_value,
            "rawUnit": self.raw_unit,
            "canonicalUnit": self.canonical_unit,
            "quantityCandidate": self.quantity_candidate,
            "sourceOcrTokenId": self.source_ocr_token_id,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Segmentation Contracts
# ---------------------------------------------------------------------------

@dataclass
class MaskArtifact:
    """A compact segmentation mask representation mapped to source pixels."""
    id: str
    source_asset_id: Optional[str] = None
    figure_id: Optional[str] = None
    source_width: int = 0
    source_height: int = 0
    bbox_source_px: Optional[SourceBBox] = None
    centroid_source_px: Optional[SourcePoint] = None
    area_px: float = 0.0
    rle_counts: Optional[str] = None      # Compressed run-length encoding
    polygon_approx: Optional[SourcePolygon] = None
    confidence: Optional[float] = None
    provider: str = "sam2"
    model: Optional[str] = None
    prompt_provenance: Dict[str, Any] = field(default_factory=dict)
    verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sourceAssetId": self.source_asset_id,
            "figureId": self.figure_id,
            "sourceWidth": self.source_width,
            "sourceHeight": self.source_height,
            "bboxSourcePx": self.bbox_source_px.to_dict() if self.bbox_source_px else None,
            "centroidSourcePx": self.centroid_source_px.to_dict() if self.centroid_source_px else None,
            "areaPx": self.area_px,
            "rleCounts": self.rle_counts,
            "polygonApprox": self.polygon_approx.to_dict() if self.polygon_approx else None,
            "confidence": self.confidence,
            "provider": self.provider,
            "model": self.model,
            "promptProvenance": self.prompt_provenance,
            "verified": self.verified,
        }


@dataclass
class SegmentationResult:
    """Outcome of a segmentation operation."""
    status: ExtractionStatus
    masks: List[MaskArtifact] = field(default_factory=list)
    provider: str = "sam2"
    model: Optional[str] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "masks": [m.to_dict() for m in self.masks],
            "provider": self.provider,
            "model": self.model,
            "latencyMs": self.latency_ms,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Generic Evidence Record & Registry
# ---------------------------------------------------------------------------

@dataclass
class EvidenceRecord:
    """A traceable atomic piece of visual, geometric, or textual evidence."""
    id: str
    method: EvidenceMethod
    source_asset_id: Optional[str] = None
    figure_id: Optional[str] = None
    confidence: Optional[float] = None
    verified: bool = False
    coordinate_space: Literal["source_px"] = "source_px"
    provider: Optional[str] = None
    model: Optional[str] = None
    version: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "method": self.method.value,
            "sourceAssetId": self.source_asset_id,
            "figureId": self.figure_id,
            "confidence": self.confidence,
            "verified": self.verified,
            "coordinateSpace": self.coordinate_space,
            "provider": self.provider,
            "model": self.model,
            "version": self.version,
            "payload": self.payload,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceRecord":
        method_raw = data.get("method", "fused")
        if isinstance(method_raw, str):
            try:
                method = EvidenceMethod(method_raw)
            except ValueError:
                method = EvidenceMethod.FUSED
        else:
            method = method_raw

        return cls(
            id=data["id"],
            method=method,
            source_asset_id=data.get("sourceAssetId") or data.get("source_asset_id"),
            figure_id=data.get("figureId") or data.get("figure_id"),
            confidence=data.get("confidence"),
            verified=bool(data.get("verified", False)),
            coordinate_space=data.get("coordinateSpace") or data.get("coordinate_space", "source_px"),
            provider=data.get("provider"),
            model=data.get("model"),
            version=data.get("version"),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {}),
        )


class EvidenceRegistry:
    """Registry validating and storing typed EvidenceRecord instances for BookIR."""

    def __init__(self, initial: Optional[Union[Dict[str, Any], "EvidenceRegistry"]] = None):
        self._records: Dict[str, EvidenceRecord] = {}
        if initial:
            if isinstance(initial, EvidenceRegistry):
                self._records = dict(initial._records)
            elif isinstance(initial, dict):
                for k, v in initial.items():
                    self.add(v, key=k)

    def add(self, record: Union[EvidenceRecord, Dict[str, Any]], key: Optional[str] = None) -> str:
        """Validate and insert an EvidenceRecord, rejecting arbitrary untyped dicts."""
        if isinstance(record, EvidenceRecord):
            rec = record
        elif isinstance(record, dict):
            rec = EvidenceRecord.from_dict(record)
        else:
            raise TypeError(f"EvidenceRegistry only accepts EvidenceRecord or valid dict, got: {type(record)}")
        rec_id = key or rec.id
        self._records[rec_id] = rec
        return rec_id

    def get(self, key: str) -> Optional[EvidenceRecord]:
        return self._records.get(key)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v.to_dict() for k, v in self._records.items()}

    def __iter__(self):
        return iter(self._records)

    def items(self):
        return self._records.items()

    def values(self):
        return self._records.values()

    def keys(self):
        return self._records.keys()

    def __getitem__(self, key: str) -> EvidenceRecord:
        return self._records[key]

    def __setitem__(self, key: str, value: Union[EvidenceRecord, Dict[str, Any]]) -> None:
        self.add(value, key=key)

    def __contains__(self, key: str) -> bool:
        return key in self._records

    def __len__(self) -> int:
        return len(self._records)

    def update(self, other: Union[Dict[str, Any], "EvidenceRegistry"]) -> None:
        if isinstance(other, EvidenceRegistry):
            self._records.update(other._records)
        elif isinstance(other, dict):
            for k, v in other.items():
                self.add(v, key=k)


@dataclass
class EntityGroundingDiagnostic:
    """Explains why an entity was grounded, ambiguous, or unresolved."""
    entity_id: str
    grounding_state: GroundingState
    supporting_evidence: List[str] = field(default_factory=list)
    checks: Dict[str, Any] = field(default_factory=dict)
    conflicts: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entityId": self.entity_id,
            "groundingState": self.grounding_state.value,
            "supportingEvidence": self.supporting_evidence,
            "checks": self.checks,
            "conflicts": self.conflicts,
            "notes": self.notes,
        }


@dataclass
class EvidenceExtractionResult:
    """Overall outcome of the EvidenceExtractionPipeline."""
    status: ExtractionStatus
    evidence: Dict[str, EvidenceRecord] = field(default_factory=dict)
    ocr: Optional[OCRExtractionResult] = None
    geometry_candidates: List[Dict[str, Any]] = field(default_factory=list)
    segmentation_candidates: List[MaskArtifact] = field(default_factory=list)
    physical_value_candidates: List[ParsedPhysicalValueCandidate] = field(default_factory=list)
    parameter_associations: List[ParameterAssociationResult] = field(default_factory=list)
    grounding_diagnostics: List[EntityGroundingDiagnostic] = field(default_factory=list)
    provider_diagnostics: Dict[str, Any] = field(default_factory=dict)
    latency_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "evidence": {k: v.to_dict() for k, v in self.evidence.items()},
            "ocr": self.ocr.to_dict() if self.ocr else None,
            "geometryCandidates": self.geometry_candidates,
            "segmentationCandidates": [m.to_dict() for m in self.segmentation_candidates],
            "physicalValueCandidates": [p.to_dict() for p in self.physical_value_candidates],
            "parameterAssociations": [a.to_dict() for a in self.parameter_associations],
            "groundingDiagnostics": [d.to_dict() for d in self.grounding_diagnostics],
            "providerDiagnostics": self.provider_diagnostics,
            "latencyMs": self.latency_ms,
        }

"""PR-04 Ingestion Data Contracts — SourceAsset, PageIR, BookIR.

These are the canonical, version-tagged schemas that form the real
image-ingestion pipeline.  All coordinates are in native source pixels
(source_px) unless an explicit coordinate_space field says otherwise.

DESIGN RULES (enforced by convention, not yet JSON Schema):
  - PageIR records only what is objectively present in the image.
    It is NOT executable physics.
  - BookIR records what the evidence means semantically.
    domain/subtype may be None when unknown.
  - SourceAsset filename is metadata only.
    It MUST NOT be used to classify domain, subtype, solver, or fixture.
  - sha256 may be used for identity/dedup/caching only.
    It MUST NOT secretly classify physics.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# SourceAsset
# ---------------------------------------------------------------------------

@dataclass
class SourceAsset:
    """Stable uploaded-source identity.

    Created once when image bytes arrive.  Immutable thereafter.
    """
    id: str                    # uuid4 hex
    mime_type: str             # 'image/png' | 'image/jpeg' | …
    original_filename: str     # metadata only — never drives physics routing
    byte_size: int
    width_px: int
    height_px: int
    sha256: str                # for identity/dedup — never drives physics routing
    storage_path: str          # absolute OS path where bytes are saved

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "mimeType": self.mime_type,
            "originalFilename": self.original_filename,
            "byteSize": self.byte_size,
            "width_px": self.width_px,
            "height_px": self.height_px,
            "sha256": self.sha256,
        }


# ---------------------------------------------------------------------------
# PageIR
# ---------------------------------------------------------------------------

@dataclass
class PageRegion:
    """A rectangular region detected (or assumed) in the page."""
    id: str
    label: str                 # e.g. "whole_image" | "detected_figure_1"
    x: float                   # source_px
    y: float
    width: float
    height: float
    confidence: float = 1.0
    detection_method: str = "user_supplied"   # "user_supplied" | "cv" | "sam2" | "vlm"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
            "detectionMethod": self.detection_method,
            "notes": self.notes,
        }


@dataclass
class PageFigure:
    """A physics figure identified within the page (may span a region)."""
    id: str
    region_id: str             # which PageRegion this figure lives in
    # Figure-local coordinate origin relative to page_x / page_y
    page_x: float              # page-level x origin of figure bbox (source_px)
    page_y: float
    width: float
    height: float
    detection_method: str = "user_supplied"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "regionId": self.region_id,
            "pageX": self.page_x,
            "pageY": self.page_y,
            "width": self.width,
            "height": self.height,
            "detectionMethod": self.detection_method,
            "notes": self.notes,
        }

    def local_to_page(self, local_x: float, local_y: float):
        """Convert figure-local source_px → page source_px."""
        return (self.page_x + local_x, self.page_y + local_y)

    def page_to_local(self, page_x: float, page_y: float):
        """Convert page source_px → figure-local source_px."""
        return (page_x - self.page_x, page_y - self.page_y)


@dataclass
class PageTextBlock:
    """A text region extracted by OCR or detected by the user."""
    id: str
    text: str
    x: float                   # source_px bounding box
    y: float
    width: float
    height: float
    confidence: float = 0.0    # 0 if not extracted yet
    extraction_method: str = "pending"   # "pending" | "ocr" | "vlm" | "manual"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
            "extractionMethod": self.extraction_method,
        }


@dataclass
class PageIR:
    """What objectively exists in the uploaded page/image.

    Coordinate system: source_px (native image pixels).
    Browser resizing MUST NOT change PageIR coordinates.
    """
    version: str = "1.0"
    source: Dict[str, Any] = field(default_factory=dict)
    coordinate_space: Dict[str, Any] = field(default_factory=dict)
    regions: List[PageRegion] = field(default_factory=list)
    figures: List[PageFigure] = field(default_factory=list)
    text_blocks: List[PageTextBlock] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "source": self.source,
            "coordinateSpace": self.coordinate_space,
            "regions": [r.to_dict() for r in self.regions],
            "figures": [f.to_dict() for f in self.figures],
            "textBlocks": [tb.to_dict() for tb in self.text_blocks],
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# BookIR
# ---------------------------------------------------------------------------

@dataclass
class ProvenanceRecord:
    """Traces where a value came from."""
    source: str                # "ocr" | "cv" | "vlm" | "derived" | "assumed" | "student" | "author_override"
    evidence_refs: List[str] = field(default_factory=list)   # e.g. ["text_11", "region_19"]
    confidence: float = 0.0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "evidenceRefs": self.evidence_refs,
            "confidence": self.confidence,
            "notes": self.notes,
        }


@dataclass
class PhysicalValue:
    """A physical parameter with optional units and provenance."""
    value: Any                  # numeric, string, or None if unknown
    unit: Optional[str] = None
    status: str = "unknown"     # "observed" | "derived" | "assumed" | "unknown"
    provenance: Optional[ProvenanceRecord] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "value": self.value,
            "unit": self.unit,
            "status": self.status,
        }
        if self.provenance:
            d["provenance"] = self.provenance.to_dict()
        return d


@dataclass
class BookEntity:
    """A semantic entity identified in the figure (lens, bob, wire, etc.)."""
    id: str
    type: str                   # "lens" | "bob" | "wire" | "resistor" | etc.
    label: Optional[str] = None
    position_source_px: Optional[Dict[str, Any]] = None   # {x, y, provenance}
    geometry: Optional[Dict[str, Any]] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "positionSourcePx": self.position_source_px,
            "geometry": self.geometry,
            "attributes": self.attributes,
            "evidenceRefs": self.evidence_refs,
        }


# BookIR status constants
class BookIRStatus:
    UNRESOLVED = "UNRESOLVED"          # not enough information
    NEEDS_REVIEW = "NEEDS_REVIEW"      # partially understood
    UNSUPPORTED = "UNSUPPORTED"        # understood but no solver
    READY_TO_COMPILE = "READY_TO_COMPILE"  # sufficient for PhysicsCompiler


@dataclass
class BookIR:
    """Semantic physics understanding extracted from a PageIR figure.

    domain and subtype may be None.  That is valid and expected when
    the pipeline has not yet understood the content.
    """
    version: str = "1.0"
    source_asset_id: Optional[str] = None
    page_ir_version: Optional[str] = None
    figure_id: Optional[str] = None

    domain: Optional[str] = None      # "mechanics" | "optics" | "circuits" | None
    subtype: Optional[str] = None     # "pendulum" | "thin_lens" | "dc_linear" | None

    entities: List[BookEntity] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)

    parameters: Dict[str, Any] = field(default_factory=dict)   # PhysicalValue dicts
    geometry: Dict[str, Any] = field(default_factory=dict)

    assumptions: List[Dict[str, Any]] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    confidence: Dict[str, Any] = field(default_factory=dict)

    status: str = BookIRStatus.UNRESOLVED
    status_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "sourceAssetId": self.source_asset_id,
            "pageIRVersion": self.page_ir_version,
            "figureId": self.figure_id,
            "domain": self.domain,
            "subtype": self.subtype,
            "entities": [e.to_dict() for e in self.entities],
            "relationships": self.relationships,
            "parameters": self.parameters,
            "geometry": self.geometry,
            "assumptions": self.assumptions,
            "provenance": self.provenance,
            "confidence": self.confidence,
            "status": self.status,
            "statusNotes": self.status_notes,
        }


# ---------------------------------------------------------------------------
# PhysicsCompilerResult
# ---------------------------------------------------------------------------

@dataclass
class PhysicsCompilerResult:
    """Result from PhysicsCompiler.compile(book_ir).

    Only status == READY contains a non-None scene.
    """
    status: str                              # "READY" | "NEEDS_REVIEW" | "UNSUPPORTED" | "UNRESOLVED"
    scene: Optional[Dict[str, Any]] = None
    issues: List[Dict[str, str]] = field(default_factory=list)
    book_ir_status: str = BookIRStatus.UNRESOLVED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "scene": self.scene,
            "issues": self.issues,
            "bookIRStatus": self.book_ir_status,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

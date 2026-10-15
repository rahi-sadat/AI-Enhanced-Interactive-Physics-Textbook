"""Source-image reconstruction contracts (phase 1).

These records describe observations and evaluation results, not a detector,
physics solver, or registration gate. Only grounded CV/OCR/manual evidence may
populate observed geometry; approximate VLM boxes belong in BookIR attributes.
Serialization is camelCase, matching BookIR. No viewport coordinates are stored.
"""
from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Optional

from .evidence import MaskArtifact, SourceBBox, SourceLine, SourcePoint, SourcePolygon


class VisualReadiness(str, Enum):
    NOT_EVALUATED = "NOT_EVALUATED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    AUTO_VISUAL = "AUTO_VISUAL"
    PHYSICS_VERIFIED = "PHYSICS_VERIFIED"


class RegistrationStatus(str, Enum):
    NOT_EVALUATED = "NOT_EVALUATED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    PASSED = "PASSED"
    FAILED = "FAILED"


def _camel(name):
    first, *rest = name.split("_")
    return first + "".join(part.title() for part in rest)


def _encode(value):
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "to_dict"):
        return deepcopy(value.to_dict())
    if isinstance(value, dict):
        return {key: _encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_encode(item) for item in value]
    return deepcopy(value)


class _Contract:
    def to_dict(self):
        # Revalidate after edits to mutable collections, before crossing a boundary.
        self.__post_init__()
        return {_camel(f.name): _encode(getattr(self, f.name)) for f in fields(self)}

    @classmethod
    def from_dict(cls, data):
        """Read the canonical wire format without silently dropping unknown fields."""
        if not isinstance(data, dict):
            raise ValueError(f"{cls.__name__} must be an object")
        names = {_camel(f.name): f.name for f in fields(cls)}
        unknown = data.keys() - names.keys()
        if unknown:
            raise ValueError(f"Unknown {cls.__name__} fields: {sorted(unknown)}")
        return cls(**{names[key]: deepcopy(value) for key, value in data.items()})


def _number(value, name, minimum=None, maximum=None):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite JSON number")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be <= {maximum}")


def _refs(values, name):
    if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
        raise ValueError(f"{name} must contain nonempty string references")
    if len(values) != len(set(values)):
        raise ValueError(f"{name} contains duplicate references")


def _point(value):
    if isinstance(value, dict) and set(value) == {"x", "y"}:
        _number(value["x"], "point.x")
        _number(value["y"], "point.y")
        value = SourcePoint(**value)
    if not isinstance(value, SourcePoint):
        raise ValueError("Expected a source-pixel point")
    _number(value.x, "point.x")
    _number(value.y, "point.y")
    return value


def _bbox(value):
    if isinstance(value, dict) and set(value) == {"x", "y", "width", "height"}:
        for name, number in value.items():
            _number(number, f"bbox.{name}")
        value = SourceBBox(**value)
    if not isinstance(value, SourceBBox):
        raise ValueError("Expected a source-pixel bounding box")
    for name in ("x", "y", "width", "height"):
        _number(getattr(value, name), f"bbox.{name}")
    if value.width <= 0 or value.height <= 0:
        raise ValueError("Bounding box dimensions must be positive")
    return value


def _record(value, cls):
    if isinstance(value, dict):
        return cls.from_dict(value)
    if not isinstance(value, cls):
        raise ValueError(f"Expected {cls.__name__}")
    value.__post_init__()
    return value


def _mask(value):
    if isinstance(value, dict):
        names = {_camel(f.name): f.name for f in fields(MaskArtifact)}
        if value.keys() - names.keys():
            raise ValueError("Unknown MaskArtifact fields")
        value = MaskArtifact(**{names[k]: deepcopy(v) for k, v in value.items()})
    if not isinstance(value, MaskArtifact):
        raise ValueError("Expected MaskArtifact")
    if value.rle_counts is not None and not isinstance(value.rle_counts, str):
        raise ValueError("Mask RLE counts must be a string or null")
    if not isinstance(value.prompt_provenance, dict):
        raise ValueError("Mask prompt provenance must be an object")
    for dimension in (value.source_width, value.source_height):
        if type(dimension) is not int or dimension <= 0:
            raise ValueError("Mask native source dimensions must be positive integers")
    if value.bbox_source_px is not None:
        value.bbox_source_px = _bbox(value.bbox_source_px)
    if value.centroid_source_px is not None:
        value.centroid_source_px = _point(value.centroid_source_px)
    if value.polygon_approx is not None:
        if isinstance(value.polygon_approx, dict) and set(value.polygon_approx) != {"points"}:
            raise ValueError("Unknown source polygon fields")
        points = value.polygon_approx["points"] if isinstance(value.polygon_approx, dict) else value.polygon_approx.points
        value.polygon_approx = SourcePolygon([_point(p) for p in points])
    _number(value.area_px, "mask.area_px", 0)
    if value.confidence is not None:
        _number(value.confidence, "mask.confidence", 0, 1)
    if type(value.verified) is not bool:
        raise ValueError("mask.verified must be a JSON boolean")
    return value


@dataclass
class ObservedGeometry(_Contract):
    """Measured features in one native image; feature IDs are globally unique.

    Curves are ordered sampled polylines. Topology is an undirected adjacency
    map of observed terminal/junction IDs, separate from solver node reduction.
    Evidence refs point into BookIR.evidence; their origin is checked by producers.
    """
    source_width: int
    source_height: int
    coordinate_space: str = "source_px"
    landmarks: dict[str, SourcePoint] = field(default_factory=dict)
    lines: dict[str, SourceLine] = field(default_factory=dict)
    curves: dict[str, list[SourcePoint]] = field(default_factory=dict)
    masks: dict[str, MaskArtifact] = field(default_factory=dict)
    text_anchors: dict[str, SourcePoint] = field(default_factory=dict)
    topology: dict[str, list[str]] = field(default_factory=dict)
    evidence_refs: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self):
        if self.coordinate_space != "source_px":
            raise ValueError("Observed geometry must use source_px")
        for dimension in (self.source_width, self.source_height):
            if type(dimension) is not int or dimension <= 0:
                raise ValueError("Native source dimensions must be positive integers")
        feature_ids = []
        for group in (self.landmarks, self.lines, self.curves, self.masks, self.text_anchors):
            if not isinstance(group, dict):
                raise ValueError("Observed feature collections must be objects")
            feature_ids.extend(group)
        _refs(feature_ids, "Observed feature IDs")
        self.landmarks = {k: self.check_point(v) for k, v in self.landmarks.items()}
        self.text_anchors = {k: self.check_point(v) for k, v in self.text_anchors.items()}
        for key, line in self.lines.items():
            if isinstance(line, dict):
                if set(line) - {"start", "end", "length_px"}:
                    raise ValueError("Unknown source line fields")
                line = SourceLine(self.check_point(line["start"]), self.check_point(line["end"]))
            if not isinstance(line, SourceLine):
                raise ValueError("Expected SourceLine")
            self.check_point(line.start)
            self.check_point(line.end)
            if line.length_px <= 0:
                raise ValueError("Observed lines must have distinct endpoints")
            self.lines[key] = line
        for key, points in self.curves.items():
            if not isinstance(points, list) or len(points) < 2:
                raise ValueError("Observed curves need at least two sampled points")
            self.curves[key] = [self.check_point(p) for p in points]
        for key, mask in self.masks.items():
            mask = _mask(mask)
            if mask.id != key:
                raise ValueError("Mask key must match its artifact ID")
            if (mask.source_width, mask.source_height) != (self.source_width, self.source_height):
                raise ValueError("Mask dimensions must match native source dimensions")
            if mask.bbox_source_px is not None:
                self.check_bbox(mask.bbox_source_px)
            if mask.centroid_source_px is not None:
                self.check_point(mask.centroid_source_px)
            if mask.polygon_approx is not None:
                for point in mask.polygon_approx.points:
                    self.check_point(point)
            self.masks[key] = mask
        if not isinstance(self.topology, dict) or not isinstance(self.evidence_refs, dict):
            raise ValueError("Topology and evidence references must be objects")
        _refs(list(self.topology), "Topology node IDs")
        for node, neighbors in self.topology.items():
            _refs(neighbors, "Topology neighbors")
            if node in neighbors or any(n not in self.topology for n in neighbors):
                raise ValueError("Topology must reference distinct declared nodes")
            if any(node not in self.topology[n] for n in neighbors):
                raise ValueError("Observed topology adjacency must be symmetric")
        for feature_id, refs in self.evidence_refs.items():
            if feature_id not in self.feature_ids:
                raise ValueError("Evidence refers to an undeclared observed feature")
            _refs(refs, "Observed evidence refs")

    @property
    def feature_ids(self):
        return set(self.landmarks) | set(self.lines) | set(self.curves) | set(self.masks) | set(self.text_anchors) | set(self.topology)

    def check_point(self, value):
        point = _point(value)
        if not (0 <= point.x <= self.source_width and 0 <= point.y <= self.source_height):
            raise ValueError("Observed point lies outside the native source image")
        return point

    def check_bbox(self, value):
        bbox = _bbox(value)
        self.check_point(SourcePoint(bbox.x, bbox.y))
        self.check_point(SourcePoint(bbox.x_max, bbox.y_max))
        return bbox


@dataclass
class VisualConstraint(_Contract):
    id: str
    kind: str
    observed_refs: list[str]
    required: bool = True
    evidence_refs: list[str] = field(default_factory=list)

    def __post_init__(self):
        _refs([self.id], "Constraint ID")
        if self.kind not in {"landmark", "line", "curve", "mask", "text_anchor", "topology"}:
            raise ValueError("Unknown visual constraint kind")
        _refs(self.observed_refs, "Constraint observed refs")
        if not self.observed_refs:
            raise ValueError("A visual constraint must reference observed geometry")
        if type(self.required) is not bool:
            raise ValueError("Constraint required must be a JSON boolean")
        _refs(self.evidence_refs, "Constraint evidence refs")


@dataclass
class DynamicVisualAsset(_Contract):
    """Optional extraction/restoration artifacts; anchors remain in source_px.

    The sprite is placed in source_bbox. Its transform origin and anchor are
    absolute source points, not crop-local or CSS coordinates. A restoration
    patch, when present, occupies restoration_bbox (which may exceed the sprite).
    URLs are metadata only; creating this record performs no I/O or extraction.
    """
    entity_id: str
    source_bbox: SourceBBox
    anchor_source_px: SourcePoint
    transform_origin: SourcePoint
    source_mask_url: Optional[str] = None
    sprite_url: Optional[str] = None
    restoration_mask_url: Optional[str] = None
    clean_background_url: Optional[str] = None
    restoration_patch_url: Optional[str] = None
    restoration_bbox: Optional[SourceBBox] = None
    extraction_confidence: float = 0.0
    evidence_refs: list[str] = field(default_factory=list)

    def __post_init__(self):
        _refs([self.entity_id], "Dynamic entity ID")
        self.source_bbox = _bbox(self.source_bbox)
        self.anchor_source_px = _point(self.anchor_source_px)
        self.transform_origin = _point(self.transform_origin)
        if self.restoration_bbox is not None:
            self.restoration_bbox = _bbox(self.restoration_bbox)
        if self.restoration_patch_url and self.restoration_bbox is None:
            raise ValueError("A restoration patch requires a source-pixel bounding box")
        for name in ("source_mask_url", "sprite_url", "restoration_mask_url", "clean_background_url", "restoration_patch_url"):
            url = getattr(self, name)
            if url is not None and (not isinstance(url, str) or not url.strip()):
                raise ValueError(f"{name} must be a nonempty artifact URL or null")
        _number(self.extraction_confidence, "extraction_confidence", 0, 1)
        _refs(self.evidence_refs, "Dynamic asset evidence refs")


@dataclass
class RegistrationMetric(_Contract):
    """One measured comparison; thresholds/evaluation are supplied by phase 2."""
    constraint_id: str
    name: str
    value: float | bool
    unit: str
    passed: bool
    sample_count: int

    def __post_init__(self):
        _refs([self.constraint_id], "Metric constraint ID")
        _refs([self.name], "Metric name")
        if self.unit not in {"source_px", "ratio", "boolean", "degrees"}:
            raise ValueError("Unknown registration metric unit")
        if self.unit == "boolean":
            if type(self.value) is not bool:
                raise ValueError("Boolean metrics require a JSON boolean")
        else:
            _number(self.value, "metric.value", 0, 1 if self.unit == "ratio" else None)
        if type(self.passed) is not bool:
            raise ValueError("Metric passed must be a JSON boolean")
        if type(self.sample_count) is not int or self.sample_count <= 0:
            raise ValueError("Metrics must describe at least one measured sample")


@dataclass
class RegistrationReport(_Contract):
    status: RegistrationStatus = RegistrationStatus.NOT_EVALUATED
    mean_error_px: Optional[float] = None
    p95_error_px: Optional[float] = None
    landmark_errors: dict[str, float] = field(default_factory=dict)
    curve_errors: dict[str, float] = field(default_factory=dict)
    mask_iou: Optional[float] = None
    topology_match: Optional[bool] = None
    confidence: float = 0.0
    blockers: list[str] = field(default_factory=list)
    metrics: list[RegistrationMetric] = field(default_factory=list)

    def __post_init__(self):
        self.status = RegistrationStatus(self.status)
        for value in (self.mean_error_px, self.p95_error_px):
            if value is not None:
                _number(value, "registration error", 0)
        for residuals in (self.landmark_errors, self.curve_errors):
            if not isinstance(residuals, dict):
                raise ValueError("Per-feature residuals must be objects")
            _refs(list(residuals), "Residual feature IDs")
            for value in residuals.values():
                _number(value, "per-feature registration error", 0)
        if self.mask_iou is not None:
            _number(self.mask_iou, "mask_iou", 0, 1)
        if self.topology_match is not None and type(self.topology_match) is not bool:
            raise ValueError("topology_match must be a JSON boolean or null")
        _number(self.confidence, "registration confidence", 0, 1)
        _refs(self.blockers, "Registration blockers")
        self.metrics = [_record(m, RegistrationMetric) for m in self.metrics]
        metric_ids = [(m.constraint_id, m.name) for m in self.metrics]
        if len(metric_ids) != len(set(metric_ids)):
            raise ValueError("Duplicate registration metrics")
        if self.status == RegistrationStatus.NOT_EVALUATED:
            if self.metrics or self.landmark_errors or self.curve_errors or self.confidence != 0 or any(
                value is not None for value in (self.mean_error_px, self.p95_error_px, self.mask_iou, self.topology_match)
            ):
                raise ValueError("Unevaluated registration cannot claim measured results")
        if self.status == RegistrationStatus.PASSED:
            if not self.metrics or not all(m.passed for m in self.metrics) or self.blockers or self.topology_match is False:
                raise ValueError("Passed registration requires measured passing metrics and no blockers")


@dataclass
class VisualReconstruction(_Contract):
    observed_geometry: ObservedGeometry
    version: str = "1.0"
    constraints: list[VisualConstraint] = field(default_factory=list)
    dynamic_visuals: list[DynamicVisualAsset] = field(default_factory=list)
    registration: RegistrationReport = field(default_factory=RegistrationReport)
    visual_readiness: VisualReadiness = VisualReadiness.NOT_EVALUATED
    physics_evidence_refs: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.version != "1.0":
            raise ValueError("Unsupported visual reconstruction version")
        self.observed_geometry = _record(self.observed_geometry, ObservedGeometry)
        self.constraints = [_record(c, VisualConstraint) for c in self.constraints]
        self.dynamic_visuals = [_record(a, DynamicVisualAsset) for a in self.dynamic_visuals]
        self.registration = _record(self.registration, RegistrationReport)
        self.visual_readiness = VisualReadiness(self.visual_readiness)
        _refs(self.physics_evidence_refs, "Physics evidence refs")
        _refs([c.id for c in self.constraints], "Constraint IDs")
        _refs([a.entity_id for a in self.dynamic_visuals], "Dynamic entity IDs")
        groups = {"landmark": self.observed_geometry.landmarks, "line": self.observed_geometry.lines,
                  "curve": self.observed_geometry.curves, "mask": self.observed_geometry.masks,
                  "text_anchor": self.observed_geometry.text_anchors, "topology": self.observed_geometry.topology}
        for constraint in self.constraints:
            if any(ref not in groups[constraint.kind] for ref in constraint.observed_refs):
                raise ValueError("Constraint must reference observed features of its kind")
        constraint_ids = {c.id for c in self.constraints}
        if any(m.constraint_id not in constraint_ids for m in self.registration.metrics):
            raise ValueError("Registration metric references an undeclared constraint")
        for key in self.registration.landmark_errors:
            if key not in self.observed_geometry.landmarks:
                raise ValueError("Landmark residual references an undeclared landmark")
        for key in self.registration.curve_errors:
            if key not in self.observed_geometry.curves:
                raise ValueError("Curve residual references an undeclared curve")
        for asset in self.dynamic_visuals:
            self.observed_geometry.check_bbox(asset.source_bbox)
            self.observed_geometry.check_point(asset.anchor_source_px)
            self.observed_geometry.check_point(asset.transform_origin)
            if asset.restoration_bbox is not None:
                self.observed_geometry.check_bbox(asset.restoration_bbox)
        if self.registration.status == RegistrationStatus.PASSED:
            measured = {m.constraint_id for m in self.registration.metrics}
            if any(c.required and c.id not in measured for c in self.constraints):
                raise ValueError("Passed registration must cover every required constraint")
        if self.visual_readiness in {VisualReadiness.AUTO_VISUAL, VisualReadiness.PHYSICS_VERIFIED}:
            if self.registration.status != RegistrationStatus.PASSED:
                raise ValueError("Visual readiness requires passed registration")
        if self.visual_readiness == VisualReadiness.PHYSICS_VERIFIED and not self.physics_evidence_refs:
            raise ValueError("PHYSICS_VERIFIED requires grounded physical evidence refs")

    def validate_entity_refs(self, entity_ids):
        if any(asset.entity_id not in entity_ids for asset in self.dynamic_visuals):
            raise ValueError("Dynamic visual references an undeclared BookIR entity")

    def validate_evidence_refs(self, evidence, source_asset_id=None, figure_id=None):
        """Resolve supplied references without treating semantic VLM boxes as measurements.

        This checks structural provenance, not whether physical evidence is
        sufficient for a specific solver. That decision belongs to readiness.
        """
        refs = set(self.physics_evidence_refs)
        for feature_refs in self.observed_geometry.evidence_refs.values():
            refs.update(feature_refs)
        for record in [*self.constraints, *self.dynamic_visuals]:
            refs.update(record.evidence_refs)
        for ref in refs:
            if ref not in evidence:
                raise ValueError(f"Reconstruction references undeclared evidence: {ref}")
            record = evidence[ref]
            record = record.to_dict() if hasattr(record, "to_dict") else record
            if not isinstance(record, dict):
                raise ValueError("Reconstruction evidence must be a record")
            if record.get("method") == "vlm" or record.get("source") == "vlm":
                raise ValueError("VLM semantics cannot ground visual reconstruction")
            for camel, snake, expected in (("sourceAssetId", "source_asset_id", source_asset_id),
                                           ("figureId", "figure_id", figure_id)):
                for key in (camel, snake):
                    if record.get(key) is not None and record[key] != expected:
                        raise ValueError("Reconstruction evidence belongs to a different source or figure")

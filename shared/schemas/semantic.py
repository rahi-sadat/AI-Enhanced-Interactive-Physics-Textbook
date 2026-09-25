"""PR-05 Semantic Understanding Data Contracts & Schema Validation.

Defines the structured schema for multimodal VLM semantic analysis:
  - SemanticConfidence
  - SemanticEntity
  - SemanticRelationship
  - SemanticVisibleLabel (candidateEvidence, unverified in PR-05)
  - SemanticCandidate
  - SemanticAnalysisResult

DESIGN RULES (as refined):
  - Structured JSON only; free-form prose rejected.
  - classification must be one of:
      "supported" | "unsupported_physics" | "non_physics" | "unknown"
  - subtype is strictly reserved for canonical supported physics subtypes:
      Mechanics: pendulum, projectile
      Optics: thin_lens, spherical_mirror, interface_refraction, prism
      Circuits: dc_linear
  - subtype is NEVER a status word like "non_physics" or "unknown"; for non-physics
    or unsupported physics, domain and subtype remain null.
  - VLM-read numbers/text remain unverified semantic evidence (verified=False)
    in visibleLabels, NEVER trusted BookIR.parameters.
  - Coarse bounding boxes from VLM are marked precision="approximate".
  - Zero fabricated numerical parameters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


SUPPORTED_DOMAINS = {"mechanics", "optics", "circuits"}

SUPPORTED_SUBTYPES = {
    # Mechanics
    "pendulum",
    "projectile",
    # Optics
    "thin_lens",
    "spherical_mirror",
    "interface_refraction",
    "prism",
    # Circuits
    "dc_linear",
}

VALID_CLASSIFICATIONS = {
    "supported",
    "unsupported_physics",
    "non_physics",
    "unknown",
}


@dataclass
class SemanticConfidence:
    """Confidence scores for semantic categorization."""
    is_physics: float = 0.0
    domain: float = 0.0
    subtype: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "isPhysics": self.is_physics,
            "domain": self.domain,
            "subtype": self.subtype,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SemanticConfidence":
        if not isinstance(d, dict):
            return cls()
        return cls(
            is_physics=float(d.get("isPhysics", d.get("is_physics", 0.0))),
            domain=float(d.get("domain", 0.0)),
            subtype=float(d.get("subtype", 0.0)),
        )


@dataclass
class SemanticEntity:
    """A semantic object role identified in the diagram."""
    temporary_id: str
    role: str                       # e.g., "pivot", "bob", "lens", "resistor"
    label: Optional[str] = None     # visible label if any (e.g. "m1", "R1")
    confidence: float = 1.0
    approx_bbox: Optional[List[float]] = None  # [x, y, w, h] coarse bbox
    precision: str = "approximate"  # ALWAYS coarse/approximate from VLM

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temporaryId": self.temporary_id,
            "role": self.role,
            "label": self.label,
            "confidence": self.confidence,
            "approxBbox": self.approx_bbox,
            "precision": self.precision,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SemanticEntity":
        return cls(
            temporary_id=str(d.get("temporaryId", d.get("temporary_id", f"entity_{id(d)}"))),
            role=str(d.get("role", "unknown")),
            label=d.get("label"),
            confidence=float(d.get("confidence", 1.0)),
            approx_bbox=d.get("approxBbox", d.get("approx_bbox")),
            precision="approximate",
        )


@dataclass
class SemanticRelationship:
    """A coarse semantic relationship between entities."""
    type: str                       # e.g., "connected_to", "mounted_on", "aligned_with"
    source_id: str                  # from temporaryId
    target_id: str                  # to temporaryId
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "from": self.source_id,
            "to": self.target_id,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SemanticRelationship":
        return cls(
            type=str(d.get("type", "related_to")),
            source_id=str(d.get("from", d.get("source_id", ""))),
            target_id=str(d.get("to", d.get("target_id", ""))),
            confidence=float(d.get("confidence", 1.0)),
        )


@dataclass
class SemanticVisibleLabel:
    """Textual or numerical label explicitly visible in the diagram.

    In PR-05, this is unverified semantic evidence. PR-06 OCR will
    verify and promote values into physical parameters.
    """
    text: str
    confidence: float = 1.0
    semantic_role: Optional[str] = None  # e.g. "parameter_value", "component_name"
    source: str = "vlm"
    verified: bool = False               # ALWAYS False in PR-05

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "semanticRole": self.semantic_role,
            "source": self.source,
            "verified": self.verified,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SemanticVisibleLabel":
        return cls(
            text=str(d.get("text", "")),
            confidence=float(d.get("confidence", 1.0)),
            semantic_role=d.get("semanticRole", d.get("semantic_role")),
            source=str(d.get("source", "vlm")),
            verified=False,  # Enforce unverified in PR-05
        )


@dataclass
class SemanticCandidate:
    """Alternative interpretation for ambiguous diagrams."""
    domain: Optional[str]
    subtype: Optional[str]
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "subtype": self.subtype,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SemanticCandidate":
        return cls(
            domain=d.get("domain"),
            subtype=d.get("subtype"),
            confidence=float(d.get("confidence", 0.0)),
        )


@dataclass
class SemanticAnalysisResult:
    """Complete structured semantic understanding output."""
    classification: str             # "supported" | "unsupported_physics" | "non_physics" | "unknown"
    is_physics: Optional[bool]
    domain: Optional[str]           # "mechanics" | "optics" | "circuits" | None
    subtype: Optional[str]          # "pendulum" | "projectile" | ... | None
    confidence: SemanticConfidence

    entities: List[SemanticEntity] = field(default_factory=list)
    relationships: List[SemanticRelationship] = field(default_factory=list)
    visible_labels: List[SemanticVisibleLabel] = field(default_factory=list)
    candidates: List[SemanticCandidate] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    # Metadata for reproducibility and evaluation
    provider: str = ""
    model: str = ""
    prompt_version: str = "pr05-v1"
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classification": self.classification,
            "isPhysics": self.is_physics,
            "domain": self.domain,
            "subtype": self.subtype,
            "confidence": self.confidence.to_dict(),
            "entities": [e.to_dict() for e in self.entities],
            "relationships": [r.to_dict() for r in self.relationships],
            "visibleLabels": [l.to_dict() for l in self.visible_labels],
            "candidates": [c.to_dict() for c in self.candidates],
            "notes": self.notes,
            "metadata": {
                "provider": self.provider,
                "model": self.model,
                "promptVersion": self.prompt_version,
                "timestamp": self.timestamp,
            },
        }

    @property
    def is_supported(self) -> bool:
        """True only if classification is 'supported' with real domain and subtype."""
        return (
            self.classification == "supported"
            and self.is_physics is True
            and self.domain in SUPPORTED_DOMAINS
            and self.subtype in SUPPORTED_SUBTYPES
        )


class SemanticValidationError(ValueError):
    """Raised when VLM output fails schema validation."""
    pass


def validate_semantic_payload(raw: Any) -> SemanticAnalysisResult:
    """Strictly validates a raw dict against the PR-05 semantic schema.

    Rejects free-form strings, missing required fields, or illegal types.
    Enforces that 'subtype' is NEVER populated with status words like
    'non_physics' or 'unsupported_physics'.
    """
    if not isinstance(raw, dict):
        raise SemanticValidationError(
            f"VLM response must be a JSON object, got {type(raw).__name__}"
        )

    # 1. isPhysics
    raw_is_phys = raw.get("isPhysics", raw.get("is_physics"))
    is_physics = bool(raw_is_phys) if raw_is_phys is not None else None

    # 2. classification
    classification = raw.get("classification")
    if classification is not None:
        classification = str(classification).strip().lower()
    else:
        # Infer classification if model omitted it but gave isPhysics/domain/subtype
        if is_physics is False:
            classification = "non_physics"
        elif is_physics is True:
            sub = raw.get("subtype")
            if sub in SUPPORTED_SUBTYPES:
                classification = "supported"
            else:
                classification = "unsupported_physics"
        else:
            classification = "unknown"

    if classification not in VALID_CLASSIFICATIONS:
        classification = "unknown"

    # 3. domain & subtype
    domain = raw.get("domain")
    if domain is not None:
        if not isinstance(domain, str):
            raise SemanticValidationError(f"'domain' must be string or null, got {type(domain).__name__}")
        domain = domain.strip().lower()
        if domain not in SUPPORTED_DOMAINS:
            domain = None

    subtype = raw.get("subtype")
    if subtype is not None:
        if not isinstance(subtype, str):
            raise SemanticValidationError(f"'subtype' must be string or null, got {type(subtype).__name__}")
        subtype = subtype.strip().lower()
        # CRITICAL RULE: If subtype is a status word or unknown, force it to None
        if subtype in ("non_physics", "physics_but_unsupported", "unknown", "none", "null") or subtype not in SUPPORTED_SUBTYPES:
            subtype = None

    # Strict boundary enforcement:
    if classification == "non_physics":
        is_physics = False
        domain = None
        subtype = None
    elif classification == "unsupported_physics":
        is_physics = True
        subtype = None
    elif classification == "unknown":
        domain = None
        subtype = None
    elif classification == "supported":
        if not domain or not subtype:
            # If model claimed supported but domain/subtype are missing, downgrade to unknown
            classification = "unknown"
            domain = None
            subtype = None

    # 4. Confidence
    raw_conf = raw.get("confidence")
    if not isinstance(raw_conf, dict):
        raise SemanticValidationError("Missing or invalid 'confidence' object")
    confidence = SemanticConfidence.from_dict(raw_conf)

    # 5. Entities
    entities: List[SemanticEntity] = []
    raw_entities = raw.get("entities", [])
    if not isinstance(raw_entities, list):
        raise SemanticValidationError("'entities' must be a list")
    for idx, e in enumerate(raw_entities):
        if not isinstance(e, dict):
            raise SemanticValidationError(f"Entity at index {idx} must be a dict")
        role = e.get("role")
        if not role or not isinstance(role, str):
            raise SemanticValidationError(f"Entity at index {idx} must have non-empty string 'role'")
        entities.append(SemanticEntity.from_dict(e))

    # 6. Relationships
    relationships: List[SemanticRelationship] = []
    raw_rels = raw.get("relationships", [])
    if not isinstance(raw_rels, list):
        raise SemanticValidationError("'relationships' must be a list")
    for idx, r in enumerate(raw_rels):
        if not isinstance(r, dict):
            raise SemanticValidationError(f"Relationship at index {idx} must be a dict")
        relationships.append(SemanticRelationship.from_dict(r))

    # 7. Visible Labels (candidate evidence, unverified)
    visible_labels: List[SemanticVisibleLabel] = []
    raw_labels = raw.get("visibleLabels", raw.get("visible_labels", []))
    if not isinstance(raw_labels, list):
        raise SemanticValidationError("'visibleLabels' must be a list")
    for idx, l in enumerate(raw_labels):
        if isinstance(l, str):
            visible_labels.append(SemanticVisibleLabel(text=l))
        elif isinstance(l, dict):
            visible_labels.append(SemanticVisibleLabel.from_dict(l))

    # 8. Candidates
    candidates: List[SemanticCandidate] = []
    raw_cands = raw.get("candidates", [])
    if isinstance(raw_cands, list):
        for c in raw_cands:
            if isinstance(c, dict):
                cand_sub = c.get("subtype")
                if cand_sub not in SUPPORTED_SUBTYPES:
                    cand_sub = None
                candidates.append(SemanticCandidate(
                    domain=c.get("domain") if c.get("domain") in SUPPORTED_DOMAINS else None,
                    subtype=cand_sub,
                    confidence=float(c.get("confidence", 0.0)),
                ))

    # 9. Notes
    raw_notes = raw.get("notes", [])
    notes = [str(n) for n in raw_notes] if isinstance(raw_notes, list) else []

    # 10. Metadata
    meta = raw.get("metadata", {})
    provider = str(meta.get("provider", ""))
    model = str(meta.get("model", ""))
    prompt_version = str(meta.get("promptVersion", meta.get("prompt_version", "pr05-v1")))
    timestamp = str(meta.get("timestamp", ""))

    return SemanticAnalysisResult(
        classification=classification,
        is_physics=is_physics,
        domain=domain,
        subtype=subtype,
        confidence=confidence,
        entities=entities,
        relationships=relationships,
        visible_labels=visible_labels,
        candidates=candidates,
        notes=notes,
        provider=provider,
        model=model,
        prompt_version=prompt_version,
        timestamp=timestamp,
    )

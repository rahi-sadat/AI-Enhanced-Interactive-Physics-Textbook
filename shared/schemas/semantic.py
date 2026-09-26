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


import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


SUPPORTED_DOMAINS = {"mechanics", "optics", "circuits"}

DOMAIN_SUBTYPES: Dict[str, Set[str]] = {
    "mechanics": {
        "pendulum",
        "projectile",
    },
    "optics": {
        "thin_lens",
        "spherical_mirror",
        "interface_refraction",
        "prism",
    },
    "circuits": {
        "dc_linear",
    },
}

SUPPORTED_SUBTYPES = {
    sub for subs in DOMAIN_SUBTYPES.values() for sub in subs
}

VALID_CLASSIFICATIONS = {
    "supported",
    "unsupported_physics",
    "non_physics",
    "unknown",
}

# Enriched Semantic Roles by Physical Subtype (PR-05 Refinements)
PENDULUM_SEMANTIC_ROLES: Set[str] = {
    "pivot",
    "bob",
    "string",
    "rod",
    "support_ceiling",
    "angle_marker",
    "equilibrium_position",
    "force_vector",
    "vertical_reference",
    "extreme_position",
}

SUPPORTED_ROLES_BY_SUBTYPE: Dict[str, Set[str]] = {
    "pendulum": PENDULUM_SEMANTIC_ROLES,
    "projectile": {
        "projectile_body",
        "launch_platform",
        "trajectory_path",
        "landing_surface",
        "velocity_vector",
        "apex_marker",
        "angle_marker",
    },
    "thin_lens": {
        "lens",
        "optical_axis",
        "focal_point",
        "optical_center",
        "object",
        "image",
        "light_ray",
    },
    "spherical_mirror": {
        "mirror",
        "optical_axis",
        "focal_point",
        "center_of_curvature",
        "pole",
        "object",
        "image",
        "light_ray",
    },
    "interface_refraction": {
        "interface_boundary",
        "normal_line",
        "incident_ray",
        "refracted_ray",
        "medium_label",
        "angle_marker",
    },
    "prism": {
        "prism_body",
        "incident_ray",
        "refracted_ray",
        "emergent_ray",
        "normal_line",
        "apex_angle",
        "deviation_angle",
    },
    "dc_linear": {
        "resistor",
        "voltage_source",
        "current_source",
        "wire",
        "ground",
        "junction",
        "switch",
        "ammeter",
        "voltmeter",
    },
}


def _validate_confidence(
    val: Any,
    field_name: str,
    allow_none: bool = False,
    default: float = 0.0,
) -> float:
    """Validate that a confidence score is finite and within [0.0, 1.0]."""
    if val is None:
        if allow_none:
            return default
        raise SemanticValidationError(f"'{field_name}' confidence is required and cannot be null")
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise SemanticValidationError(
            f"'{field_name}' confidence must be a number, got {type(val).__name__}: {val!r}"
        )
    f_val = float(val)
    if not math.isfinite(f_val):
        raise SemanticValidationError(f"'{field_name}' confidence must be finite, got {f_val}")
    if f_val < 0.0 or f_val > 1.0:
        raise SemanticValidationError(
            f"'{field_name}' confidence must be between 0.0 and 1.0, got {f_val}"
        )
    return f_val


@dataclass
class SemanticConfidence:
    """Confidence scores for semantic categorization.

    Preserves raw provider confidence while computing calibrated, realistic metrics.
    Avoids defaulting everything to 1.0; reserves 1.0 strictly for verified ground truth.
    """
    is_physics: float = 0.0
    domain: float = 0.0
    subtype: float = 0.0
    overall: float = 0.0
    raw_provider: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "isPhysics": self.is_physics,
            "domain": self.domain,
            "subtype": self.subtype,
            "overall": self.overall,
        }
        if self.raw_provider is not None:
            d["rawProvider"] = self.raw_provider
        return d

    @classmethod
    def from_dict(
        cls,
        d: Dict[str, Any],
        classification: Optional[str] = None,
    ) -> "SemanticConfidence":
        if not isinstance(d, dict):
            raise SemanticValidationError(f"'confidence' must be a dict, got {type(d).__name__}")

        raw_is_phys = _validate_confidence(d.get("isPhysics", d.get("is_physics")), "isPhysics", allow_none=True, default=0.0)
        raw_dom = _validate_confidence(d.get("domain"), "domain", allow_none=True, default=0.0)
        raw_sub = _validate_confidence(d.get("subtype"), "subtype", allow_none=True, default=0.0)

        # Preserve exact raw provider signals
        raw_prov = d.get("rawProvider", d.get("raw_provider"))
        if raw_prov is None:
            raw_prov = {
                "isPhysics": raw_is_phys,
                "domain": raw_dom,
                "subtype": raw_sub,
            }
            if "overall" in d:
                raw_prov["overall"] = d["overall"]

        # Calibrated values:
        # Avoid overly perfect 1.0 values where unsupported or unverified.
        # Reserve 1.0 only for ground truth / verified certainty.
        is_phys = raw_is_phys
        dom = raw_dom
        sub = raw_sub

        if classification == "supported":
            # If the model output 1.0, gently calibrate it to a realistic maximum (0.98)
            # reserving 1.0 only for strictly verified or author-confirmed ground truth
            if is_phys >= 1.0:
                is_phys = 0.99
            if dom >= 1.0:
                dom = 0.98
            if sub >= 1.0:
                sub = 0.96
        elif classification in ("unsupported_physics", "non_physics", "unknown"):
            # Unambiguously 0.0 for non-supported domain and subtype
            dom = 0.0
            sub = 0.0

        # Calibrated overall confidence score
        raw_overall = d.get("overall")
        if raw_overall is not None:
            overall = _validate_confidence(raw_overall, "overall", allow_none=True, default=0.0)
            if overall >= 1.0 and classification != "author_override":
                overall = 0.98
        else:
            if classification == "supported":
                # Conservative hierarchical confidence: min of all active stages
                overall = round(min(is_phys, dom, sub), 3)
            elif classification == "unsupported_physics":
                overall = round(is_phys, 3)
            elif classification == "non_physics":
                overall = round(1.0 - is_phys, 3) if is_phys < 0.5 else 0.5
            else:
                overall = 0.0

        return cls(
            is_physics=is_phys,
            domain=dom,
            subtype=sub,
            overall=overall,
            raw_provider=raw_prov,
        )



@dataclass
class SemanticEntity:
    """A semantic object role identified in the diagram."""
    temporary_id: str
    role: str                       # e.g., "pivot", "bob", "lens", "resistor"
    label: Optional[str] = None     # visible label if any (e.g. "m1", "R1")
    confidence: float = 0.0         # Default to 0.0 (conservative, never assume 1.0)
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
    def from_dict(cls, d: Dict[str, Any], default_id: Optional[str] = None) -> "SemanticEntity":
        tid = d.get("temporaryId", d.get("temporary_id"))
        if not tid:
            tid = default_id or "entity_1"
        return cls(
            temporary_id=str(tid),
            role=str(d.get("role", "unknown")),
            label=d.get("label"),
            confidence=_validate_confidence(d.get("confidence"), "entity.confidence", allow_none=True, default=0.0),
            approx_bbox=d.get("approxBbox", d.get("approx_bbox")),
            precision="approximate",
        )


@dataclass
class SemanticRelationship:
    """A coarse semantic relationship between entities."""
    type: str                       # e.g., "connected_to", "mounted_on", "aligned_with"
    source_id: str                  # from temporaryId
    target_id: str                  # to temporaryId
    confidence: float = 0.0         # Default to 0.0 (never assume 1.0)

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
            confidence=_validate_confidence(d.get("confidence"), "relationship.confidence", allow_none=True, default=0.0),
        )


@dataclass
class SemanticVisibleLabel:
    """Textual or numerical label explicitly visible in the diagram.

    In PR-05, this is unverified semantic evidence. PR-06 OCR will
    verify and promote values into physical parameters.
    """
    text: str
    confidence: float = 0.0              # Default to 0.0 (conservative, never assume 1.0)
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
            confidence=_validate_confidence(d.get("confidence"), "visibleLabel.confidence", allow_none=True, default=0.0),
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
            confidence=_validate_confidence(d.get("confidence"), "candidate.confidence", allow_none=True, default=0.0),
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
    latency_ms: Optional[int] = None
    cache_hit: bool = False
    fallback_used: bool = False
    debug: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        meta: Dict[str, Any] = {
            "provider": self.provider,
            "model": self.model,
            "promptVersion": self.prompt_version,
            "timestamp": self.timestamp,
        }
        if self.latency_ms is not None:
            meta["latencyMs"] = self.latency_ms
        if self.cache_hit:
            meta["cacheHit"] = self.cache_hit
        if self.fallback_used:
            meta["fallbackUsed"] = self.fallback_used
        if self.debug:
            meta["debug"] = self.debug

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
            "metadata": meta,
        }

    @property
    def is_supported(self) -> bool:
        """True only if classification is 'supported' with real domain and paired subtype."""
        return (
            self.classification == "supported"
            and self.is_physics is True
            and self.domain in SUPPORTED_DOMAINS
            and self.subtype in DOMAIN_SUBTYPES.get(self.domain or "", set())
        )


class SemanticValidationError(ValueError):
    """Raised when VLM output fails schema validation."""
    pass


def validate_semantic_payload(raw: Any) -> SemanticAnalysisResult:
    """Strictly validates a raw dict against the PR-05 semantic schema.

    Enforces:
      - isPhysics is strictly boolean or None (rejects string booleans).
      - Confidence scores are finite floats in [0.0, 1.0].
      - Domain / Subtype pairs must strictly belong together.
      - unsupported_physics clears both domain and subtype to None.
      - Entity IDs are unique and deterministic.
      - Relationships strictly refer to existing entity IDs.
      - Subtype is NEVER populated with status words.
    """
    if not isinstance(raw, dict):
        raise SemanticValidationError(
            f"VLM response must be a JSON object, got {type(raw).__name__}"
        )

    # 1. isPhysics (Strictly bool or None)
    raw_is_phys = raw.get("isPhysics", raw.get("is_physics"))
    if raw_is_phys is not None:
        if not isinstance(raw_is_phys, bool):
            raise SemanticValidationError(
                f"'isPhysics' must be boolean (true/false) or null, got {type(raw_is_phys).__name__}: {raw_is_phys!r}"
            )
    is_physics = raw_is_phys

    # 2. classification
    classification = raw.get("classification")
    if classification is not None:
        if not isinstance(classification, str):
            raise SemanticValidationError(
                f"'classification' must be string, got {type(classification).__name__}"
            )
        classification = classification.strip().lower()
        if classification not in VALID_CLASSIFICATIONS:
            raise SemanticValidationError(
                f"Invalid classification '{classification}'. Valid options: {sorted(VALID_CLASSIFICATIONS)}"
            )
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

    # 3. Domain & Subtype Boundary Enforcement
    if classification == "non_physics":
        is_physics = False
        domain = None
        subtype = None
    elif classification == "unsupported_physics":
        is_physics = True
        domain = None
        subtype = None
    elif classification == "unknown":
        domain = None
        subtype = None
    elif classification == "supported":
        if is_physics is not True:
            raise SemanticValidationError("classification='supported' requires isPhysics=true")
        raw_dom = raw.get("domain")
        if not raw_dom or not isinstance(raw_dom, str):
            raise SemanticValidationError("classification='supported' requires string 'domain'")
        domain = raw_dom.strip().lower()
        if domain not in SUPPORTED_DOMAINS:
            raise SemanticValidationError(f"Invalid domain '{domain}'. Valid domains: {sorted(SUPPORTED_DOMAINS)}")

        raw_sub = raw.get("subtype")
        if not raw_sub or not isinstance(raw_sub, str):
            raise SemanticValidationError("classification='supported' requires string 'subtype'")
        subtype = raw_sub.strip().lower()
        if subtype not in SUPPORTED_SUBTYPES:
            raise SemanticValidationError(f"Invalid subtype '{subtype}'. Valid subtypes: {sorted(SUPPORTED_SUBTYPES)}")
        if subtype not in DOMAIN_SUBTYPES.get(domain, set()):
            raise SemanticValidationError(
                f"Subtype '{subtype}' does not belong to domain '{domain}'. Valid subtypes for {domain}: {sorted(DOMAIN_SUBTYPES[domain])}"
            )
    else:
        domain = None
        subtype = None

    # 4. Confidence (calibrated with classification awareness)
    raw_conf = raw.get("confidence")
    if not isinstance(raw_conf, dict):
        raise SemanticValidationError("Missing or invalid 'confidence' object")
    confidence = SemanticConfidence.from_dict(raw_conf, classification=classification)

    # 5. Entities (Unique, deterministic IDs)
    entities: List[SemanticEntity] = []
    raw_entities = raw.get("entities", [])
    if not isinstance(raw_entities, list):
        raise SemanticValidationError("'entities' must be a list")
    seen_entity_ids: Set[str] = set()
    for idx, e in enumerate(raw_entities):
        if not isinstance(e, dict):
            raise SemanticValidationError(f"Entity at index {idx} must be a dict")
        role = e.get("role")
        if not role or not isinstance(role, str):
            raise SemanticValidationError(f"Entity at index {idx} must have non-empty string 'role'")
        default_id = f"entity_{idx + 1}"
        ent = SemanticEntity.from_dict(e, default_id=default_id)
        if ent.temporary_id in seen_entity_ids:
            raise SemanticValidationError(f"Duplicate entity ID '{ent.temporary_id}' at index {idx}")
        seen_entity_ids.add(ent.temporary_id)
        entities.append(ent)

    # 6. Relationships (Strict reference validation)
    relationships: List[SemanticRelationship] = []
    raw_rels = raw.get("relationships", [])
    if not isinstance(raw_rels, list):
        raise SemanticValidationError("'relationships' must be a list")
    for idx, r in enumerate(raw_rels):
        if not isinstance(r, dict):
            raise SemanticValidationError(f"Relationship at index {idx} must be a dict")
        rel = SemanticRelationship.from_dict(r)
        if rel.source_id not in seen_entity_ids:
            raise SemanticValidationError(
                f"Relationship at index {idx} 'from' reference '{rel.source_id}' does not exist in entities: {sorted(seen_entity_ids)}"
            )
        if rel.target_id not in seen_entity_ids:
            raise SemanticValidationError(
                f"Relationship at index {idx} 'to' reference '{rel.target_id}' does not exist in entities: {sorted(seen_entity_ids)}"
            )
        relationships.append(rel)

    # 7. Visible Labels (candidate evidence, unverified)
    visible_labels: List[SemanticVisibleLabel] = []
    raw_labels = raw.get("visibleLabels", raw.get("visible_labels", []))
    if not isinstance(raw_labels, list):
        raise SemanticValidationError("'visibleLabels' must be a list")
    for idx, l in enumerate(raw_labels):
        if isinstance(l, str):
            visible_labels.append(SemanticVisibleLabel(text=l, confidence=0.0))
        elif isinstance(l, dict):
            visible_labels.append(SemanticVisibleLabel.from_dict(l))
        else:
            raise SemanticValidationError(f"Visible label at index {idx} must be string or dict")

    # 8. Candidates (Valid domain/subtype pairing)
    candidates: List[SemanticCandidate] = []
    raw_cands = raw.get("candidates", [])
    if isinstance(raw_cands, list):
        for c in raw_cands:
            if isinstance(c, dict):
                c_dom = c.get("domain")
                c_sub = c.get("subtype")
                if c_dom and c_dom not in SUPPORTED_DOMAINS:
                    c_dom = None
                if c_sub and c_sub not in SUPPORTED_SUBTYPES:
                    c_sub = None
                if c_dom and c_sub and c_sub not in DOMAIN_SUBTYPES.get(c_dom, set()):
                    c_sub = None
                candidates.append(SemanticCandidate(
                    domain=c_dom,
                    subtype=c_sub,
                    confidence=_validate_confidence(c.get("confidence"), "candidate.confidence", allow_none=True, default=0.0),
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
    latency_ms = meta.get("latencyMs", meta.get("latency_ms"))
    if latency_ms is not None:
        try:
            latency_ms = int(latency_ms)
        except (ValueError, TypeError):
            latency_ms = None
    cache_hit = bool(meta.get("cacheHit", meta.get("cache_hit", False)))
    fallback_used = bool(meta.get("fallbackUsed", meta.get("fallback_used", False)))
    debug = meta.get("debug", {})
    if not isinstance(debug, dict):
        debug = {}

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
        latency_ms=latency_ms,
        cache_hit=cache_hit,
        fallback_used=fallback_used,
        debug=debug,
    )

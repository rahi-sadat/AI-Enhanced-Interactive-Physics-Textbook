"""PR-07 Resolution, Review, and Compilation Readiness Data Contracts.

Defines schemas and models for:
  - Resolution sources and provenance (observed_ocr, user_supplied, user_confirmed,
    user_corrected, policy_default, derived_calibration)
  - Review issues and questions presented to the user
  - Resolution decisions recorded with complete auditability
  - Model requirement specifications for PhysicsCompiler
  - Readiness evaluation and compile gating
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ResolutionSource(str, Enum):
    OBSERVED_VISUAL = "observed_visual"
    OBSERVED_OCR = "observed_ocr"
    DERIVED_GEOMETRY = "derived_geometry"
    USER_SUPPLIED = "user_supplied"
    USER_CONFIRMED = "user_confirmed"
    USER_CORRECTED = "user_corrected"
    POLICY_DEFAULT = "policy_default"
    DERIVED_CALIBRATION = "derived_calibration"
    UNRESOLVED = "unresolved"


class ReviewIssueType(str, Enum):
    MISSING_PARAMETER = "missing_parameter"
    AMBIGUOUS_EVIDENCE = "ambiguous_evidence"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    UNGROUNDED_GEOMETRY = "ungrounded_geometry"
    UNRESOLVED_DISAMBIGUATION = "unresolved_disambiguation"
    CALIBRATION_REQUIRED = "calibration_required"
    POLICY_AVAILABLE = "policy_available"

    # Aliases
    POLICY_SELECTION = "policy_available"
    AMBIGUOUS_GEOMETRY = "ungrounded_geometry"
    AMBIGUOUS_SEMANTICS = "unresolved_disambiguation"
    UNVERIFIED_OCR_CANDIDATE = "ambiguous_evidence"


class ResolutionActionType(str, Enum):
    PROVIDE_NUMERIC = "provide_numeric"
    CONFIRM_CANDIDATE = "confirm_candidate"
    CORRECT_CANDIDATE = "correct_candidate"
    SELECT_OPTION = "select_option"
    APPLY_POLICY = "apply_policy"
    CALIBRATE_SCALE = "calibrate_scale"

    # Aliases
    ENTER_VALUE = "provide_numeric"
    CHOOSE_OPTION = "select_option"
    ACCEPT_POLICY = "apply_policy"


@dataclass
class ReviewIssue:
    """A minimal, model-requirement-driven review issue requiring attention."""
    id: str
    requirement_id: str = ""
    parameter_name: str = ""
    entity_id: Optional[str] = None
    issue_type: ReviewIssueType = ReviewIssueType.MISSING_PARAMETER
    question: str = ""
    title: str = ""
    description: str = ""
    target_subtype: Optional[str] = None
    question_bn: Optional[str] = None
    candidates: List[Dict[str, Any]] = field(default_factory=list)
    options: List[str] = field(default_factory=list)
    allowed_actions: List[ResolutionActionType] = field(default_factory=list)
    action_type: Optional[ResolutionActionType] = None
    default_policy_id: Optional[str] = None
    policy_value: Optional[Any] = None
    blocking: bool = True
    is_blocker: bool = True
    help_text: str = ""
    target_unit: Optional[str] = None
    allowed_units: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.title:
            self.title = self.question
        if not self.description:
            self.description = self.question
        if not self.allowed_actions and self.action_type:
            self.allowed_actions = [self.action_type]
        if self.action_type is None and self.allowed_actions:
            self.action_type = self.allowed_actions[0]
        self.blocking = self.is_blocker

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "requirementId": self.requirement_id,
            "parameterName": self.parameter_name,
            "entityId": self.entity_id,
            "issueType": self.issue_type.value,
            "question": self.question,
            "questionBn": self.question_bn,
            "candidates": self.candidates,
            "allowedActions": [a.value for a in self.allowed_actions],
            "defaultPolicyId": self.default_policy_id,
            "blocking": self.blocking,
            "helpText": self.help_text,
            "targetUnit": self.target_unit,
            "allowedUnits": self.allowed_units,
            "evidenceRefs": self.evidence_refs,
        }

    def model_dump(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReviewIssue":
        return cls(
            id=data["id"],
            requirement_id=data.get("requirementId", data.get("requirement_id", "")),
            parameter_name=data.get("parameterName", data.get("parameter_name", "")),
            entity_id=data.get("entityId", data.get("entity_id")),
            issue_type=ReviewIssueType(data.get("issueType", data.get("issue_type", "missing_parameter"))),
            question=data.get("question", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            target_subtype=data.get("targetSubtype", data.get("target_subtype")),
            question_bn=data.get("questionBn", data.get("question_bn")),
            candidates=data.get("candidates", []),
            options=data.get("options", []),
            allowed_actions=[ResolutionActionType(a) for a in data.get("allowedActions", data.get("allowed_actions", []))],
            default_policy_id=data.get("defaultPolicyId", data.get("default_policy_id")),
            policy_value=data.get("policyValue", data.get("policy_value")),
            blocking=bool(data.get("blocking", True)),
            is_blocker=bool(data.get("isBlocker", data.get("blocking", True))),
            help_text=data.get("helpText", data.get("help_text", "")),
            target_unit=data.get("targetUnit", data.get("target_unit")),
            allowed_units=data.get("allowedUnits", data.get("allowed_units", [])),
            evidence_refs=data.get("evidenceRefs", data.get("evidence_refs", [])),
        )


@dataclass
class ResolutionDecision:
    """An explicit, auditable decision resolving a parameter or requirement."""
    id: str
    requirement_id: str = ""
    parameter_name: str = ""
    value: Any = None
    unit: Optional[str] = None
    raw_input: Optional[str] = None
    source: ResolutionSource = ResolutionSource.USER_SUPPLIED
    policy_id: Optional[str] = None
    policy_version: Optional[str] = None
    superseded_value: Optional[Any] = None
    evidence_refs: List[str] = field(default_factory=list)
    timestamp: str = ""
    notes: str = ""
    target_subtype: Optional[str] = None
    resolved_value: Optional[Any] = None
    canonical_unit: Optional[str] = None
    original_entered_value: Optional[str] = None
    original_unit: Optional[str] = None
    resolution_source: Optional[ResolutionSource] = None
    user_accepted: bool = True
    resolved_by: str = "user"

    def __post_init__(self):
        if self.resolved_value is not None and self.value is None:
            self.value = self.resolved_value
        elif self.value is not None and self.resolved_value is None:
            self.resolved_value = self.value

        if self.canonical_unit is not None and self.unit is None:
            self.unit = self.canonical_unit
        elif self.unit is not None and self.canonical_unit is None:
            self.canonical_unit = self.unit

        if self.original_entered_value is not None and self.raw_input is None:
            self.raw_input = self.original_entered_value
        elif self.raw_input is not None and self.original_entered_value is None:
            self.original_entered_value = self.raw_input

        if self.resolution_source is not None:
            self.source = self.resolution_source
        else:
            self.resolution_source = self.source

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "requirementId": self.requirement_id,
            "parameterName": self.parameter_name,
            "value": self.value,
            "resolvedValue": self.resolved_value,
            "unit": self.unit,
            "canonicalUnit": self.canonical_unit,
            "rawInput": self.raw_input,
            "originalEnteredValue": self.original_entered_value,
            "source": self.source.value if hasattr(self.source, "value") else str(self.source),
            "resolutionSource": self.resolution_source.value if hasattr(self.resolution_source, "value") else str(self.resolution_source),
            "policyId": self.policy_id,
            "policyVersion": self.policy_version,
            "supersededValue": self.superseded_value,
            "evidenceRefs": self.evidence_refs,
            "timestamp": self.timestamp,
            "notes": self.notes,
            "userAccepted": self.user_accepted,
            "resolvedBy": self.resolved_by,
        }

    def model_dump(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResolutionDecision":
        src_raw = data.get("resolutionSource", data.get("source", "user_supplied"))
        try:
            src = ResolutionSource(src_raw)
        except ValueError:
            src = ResolutionSource.USER_SUPPLIED

        val = data.get("resolvedValue", data.get("value"))
        unit = data.get("canonicalUnit", data.get("unit"))
        raw = data.get("originalEnteredValue", data.get("rawInput"))

        return cls(
            id=data.get("id", ""),
            requirement_id=data.get("requirementId", data.get("requirement_id", "")),
            parameter_name=data.get("parameterName", data.get("parameter_name", "")),
            value=val,
            resolved_value=val,
            unit=unit,
            canonical_unit=unit,
            raw_input=raw,
            original_entered_value=raw,
            source=src,
            resolution_source=src,
            policy_id=data.get("policyId", data.get("policy_id")),
            policy_version=data.get("policyVersion", data.get("policy_version")),
            superseded_value=data.get("supersededValue", data.get("superseded_value")),
            evidence_refs=data.get("evidenceRefs", data.get("evidence_refs", [])),
            timestamp=data.get("timestamp", ""),
            notes=data.get("notes", ""),
            user_accepted=bool(data.get("userAccepted", data.get("user_accepted", True))),
            resolved_by=data.get("resolvedBy", data.get("resolved_by", "user")),
        )


@dataclass
class ReviewState:
    """Structured review analysis outcome describing all blockers and questions."""
    book_ir_status: str = "NEEDS_REVIEW"
    ready_to_compile: bool = False
    book_ir_id: str = ""
    subtype: Optional[str] = None
    satisfied_requirements: List[str] = field(default_factory=list)
    missing_requirements: List[str] = field(default_factory=list)
    ambiguous_requirements: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    blockers_count: int = 0
    warnings_count: int = 0
    issues: List[ReviewIssue] = field(default_factory=list)
    available_policies: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.blockers and self.issues:
            self.blockers = [iss.description or iss.question for iss in self.issues if iss.is_blocker]
        if not self.warnings and self.issues:
            self.warnings = [iss.description or iss.question for iss in self.issues if not iss.is_blocker]
        if not self.blockers_count:
            self.blockers_count = len(self.blockers)
        if not self.warnings_count:
            self.warnings_count = len(self.warnings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bookIRStatus": self.book_ir_status,
            "bookIrId": self.book_ir_id,
            "subtype": self.subtype,
            "readyToCompile": self.ready_to_compile,
            "satisfiedRequirements": self.satisfied_requirements,
            "missingRequirements": self.missing_requirements,
            "ambiguousRequirements": self.ambiguous_requirements,
            "blockers": self.blockers,
            "blockersCount": self.blockers_count,
            "warnings": self.warnings,
            "warningsCount": self.warnings_count,
            "issues": [i.to_dict() for i in self.issues],
            "availablePolicies": self.available_policies,
            "diagnostics": self.diagnostics,
        }

    def model_dump(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class ReadinessReport:
    """Outcome of deterministic compilation readiness evaluation."""
    ready: bool
    book_ir_status: str = "NEEDS_REVIEW"
    status: Optional[str] = None
    book_ir_id: str = ""
    subtype: Optional[str] = None
    blockers: List[Any] = field(default_factory=list)
    warnings: List[Any] = field(default_factory=list)
    satisfied_requirements: List[str] = field(default_factory=list)
    resolved_requirements: List[str] = field(default_factory=list)
    missing_requirements: List[str] = field(default_factory=list)
    policy_assumptions: List[Dict[str, Any]] = field(default_factory=list)
    unresolved_ambiguities: List[str] = field(default_factory=list)
    calibration_status: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.status is not None:
            self.book_ir_status = self.status
        else:
            self.status = self.book_ir_status
        if not self.resolved_requirements and self.satisfied_requirements:
            self.resolved_requirements = list(self.satisfied_requirements)
        elif not self.satisfied_requirements and self.resolved_requirements:
            self.satisfied_requirements = list(self.resolved_requirements)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ready": self.ready,
            "bookIRStatus": self.book_ir_status,
            "status": self.status,
            "bookIrId": self.book_ir_id,
            "subtype": self.subtype,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "satisfiedRequirements": self.satisfied_requirements,
            "resolvedRequirements": self.resolved_requirements,
            "missingRequirements": self.missing_requirements,
            "policyAssumptions": self.policy_assumptions,
            "unresolvedAmbiguities": self.unresolved_ambiguities,
            "calibrationStatus": self.calibration_status,
        }

    def model_dump(self) -> Dict[str, Any]:
        return self.to_dict()

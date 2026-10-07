"""PR-07 Core Resolution Engine.

Executes deterministic, auditable parameter resolution over grounded BookIR evidence.
Handles user inputs, candidate confirmation, user corrections, and explicit default policies.
CRITICAL INVARIANTS:
1. Zero fabrication: strictly validates dimensionality, units, and ranges.
2. Evidence preservation: original OCR tokens, confidences, and bboxes in BookIR.evidence are NEVER overwritten.
3. Provenance tracking: every resolution creates an auditable record with full lineage.
4. Idempotence & Reversibility: resolutions can be safely reapplied or removed.
5. Invalidation tracking: foundational edits re-trigger calibration and re-evaluate readiness.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from shared.schemas.ingestion import BookIR, ProvenanceRecord
from shared.schemas.resolution import (
    ReadinessReport,
    ResolutionDecision,
    ResolutionSource,
)
from ai.resolution.calibration import CalibrationEngine
from ai.resolution.evaluator import ReadinessEvaluator
from ai.resolution.policies import PolicyRegistry
from ai.resolution.requirements import RequirementRegistry
from ai.resolution.units import UnitEngine


@dataclass
class ResolutionResult:
    success: bool
    parameter_name: str
    resolved_value: Optional[float] = None
    canonical_unit: Optional[str] = None
    original_entered_value: Optional[str] = None
    resolution: Optional[ResolutionDecision] = None
    readiness_report: Optional[ReadinessReport] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "parameterName": self.parameter_name,
            "resolvedValue": self.resolved_value,
            "canonicalUnit": self.canonical_unit,
            "originalEnteredValue": self.original_entered_value,
            "resolution": self.resolution.model_dump() if self.resolution else None,
            "readinessReport": self.readiness_report.model_dump() if self.readiness_report else None,
            "error": self.error,
        }


class ResolutionEngine:
    """Deterministic, auditable resolution engine for BookIR."""

    @classmethod
    def apply_resolution(
        cls,
        book_ir: BookIR,
        decision: Union[ResolutionDecision, Dict[str, Any]],
    ) -> ResolutionResult:
        """Apply a resolution decision to BookIR.

        Validates numeric input, dimension, units, and constraints.
        Updates book_ir.parameters, book_ir.resolutions, and book_ir.parameter_provenance.
        Does NOT touch BookIR.evidence.
        """
        # Parse decision into typed model if dict
        if isinstance(decision, dict):
            # Normalize camelCase to snake_case for Pydantic if needed
            dec_dict = dict(decision)
            if "parameterName" in dec_dict:
                dec_dict["parameter_name"] = dec_dict.pop("parameterName")
            if "resolvedValue" in dec_dict:
                dec_dict["resolved_value"] = dec_dict.pop("resolvedValue")
            if "resolutionSource" in dec_dict:
                dec_dict["resolution_source"] = dec_dict.pop("resolutionSource")
            if "canonicalUnit" in dec_dict:
                dec_dict["canonical_unit"] = dec_dict.pop("canonicalUnit")
            if "originalEnteredValue" in dec_dict:
                dec_dict["original_entered_value"] = dec_dict.pop("originalEnteredValue")
            if "originalUnit" in dec_dict:
                dec_dict["original_unit"] = dec_dict.pop("originalUnit")
            if "policyId" in dec_dict:
                dec_dict["policy_id"] = dec_dict.pop("policyId")
            if "policyVersion" in dec_dict:
                dec_dict["policy_version"] = dec_dict.pop("policyVersion")
            if "supersededValue" in dec_dict:
                dec_dict["superseded_value"] = dec_dict.pop("supersededValue")
            if "evidenceRefs" in dec_dict:
                dec_dict["evidence_refs"] = dec_dict.pop("evidenceRefs")
            if "targetSubtype" in dec_dict:
                dec_dict["target_subtype"] = dec_dict.pop("targetSubtype")
            if "resolvedBy" in dec_dict:
                dec_dict["resolved_by"] = dec_dict.pop("resolvedBy")
            p_name = dec_dict.get("parameter_name", "param")
            if "id" not in dec_dict or not dec_dict["id"]:
                dec_dict["id"] = f"res_{p_name}"
            dec = ResolutionDecision(**dec_dict)
        else:
            dec = decision

        param_name = dec.parameter_name
        domain = getattr(book_ir, "domain", None)
        subtype = getattr(book_ir, "subtype", None)
        spec = RequirementRegistry.get_spec(subtype) if subtype else None

        if not spec:
            return ResolutionResult(
                success=False,
                parameter_name=param_name,
                original_entered_value=dec.original_entered_value,
                error=f"UNKNOWN_MODEL_SUBTYPE: Subtype '{subtype}' in domain '{domain}' does not have a registered ModelRequirementSpec.",
                readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
            )

        canonical_param = spec.canonicalize_parameter(param_name)
        if canonical_param not in spec.parameters and param_name not in spec.parameters:
            return ResolutionResult(
                success=False,
                parameter_name=param_name,
                original_entered_value=dec.original_entered_value,
                error=f"UNKNOWN_PARAMETER_FOR_SUBTYPE: Parameter '{param_name}' is not recognized for subtype '{subtype}' in domain '{domain}'.",
                readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
            )

        target_param = canonical_param if canonical_param in spec.parameters else param_name
        p_spec = spec.parameters[target_param]

        # 1. Dimensional and unit validation
        expected_dim = p_spec.dimension.value if hasattr(p_spec.dimension, "value") else str(p_spec.dimension)
        parse_result = UnitEngine.parse_quantity(
            value_input=dec.resolved_value if dec.resolved_value is not None else dec.original_entered_value,
            unit_input=dec.canonical_unit or dec.original_unit,
            expected_dimension=expected_dim,
        )

        if not parse_result.success:
            return ResolutionResult(
                success=False,
                parameter_name=target_param,
                original_entered_value=dec.original_entered_value,
                error=parse_result.error,
                readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
            )

        norm_val = parse_result.canonical_value
        canonical_unit = parse_result.canonical_unit

        # 2. Categorical allowed values check
        if p_spec.allowed_categories and norm_val is not None:
            val_str = str(norm_val).lower().strip()
            allowed_cats = [c.lower().strip() for c in p_spec.allowed_categories]
            if val_str not in allowed_cats:
                return ResolutionResult(
                    success=False,
                    parameter_name=target_param,
                    resolved_value=norm_val,
                    original_entered_value=dec.original_entered_value,
                    error=f"INVALID_CATEGORICAL_VALUE: '{norm_val}' is not in allowed categories {p_spec.allowed_categories} for parameter '{target_param}'.",
                    readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
                )

        # 3. Numeric range constraints validation
        if isinstance(norm_val, (int, float)) and not isinstance(norm_val, bool):
            must_be_positive = (p_spec.min_value is not None and p_spec.min_value > 0 and not p_spec.allow_zero)
            range_err = UnitEngine.validate_range(
                norm_val,
                min_value=p_spec.min_value,
                max_value=p_spec.max_value,
                must_be_positive=must_be_positive,
                allow_zero=p_spec.allow_zero,
                param_name=target_param,
            )
            if range_err:
                return ResolutionResult(
                    success=False,
                    parameter_name=target_param,
                    resolved_value=norm_val,
                    original_entered_value=dec.original_entered_value,
                    error=range_err,
                    readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
                )

        # 3. Detect superseded value
        current_val = (book_ir.parameters or {}).get(target_param)
        superseded = None
        if current_val is not None and current_val != norm_val:
            superseded = current_val

        # 4. Construct complete, immutable resolution record with canonical parameter name
        updated_dec = ResolutionDecision(
            id=dec.id or f"res_{target_param}_{int(norm_val * 1000) if isinstance(norm_val, (int, float)) else target_param}",
            parameter_name=target_param,
            target_subtype=subtype,
            resolution_source=dec.resolution_source,
            resolved_value=norm_val,
            canonical_unit=canonical_unit,
            original_entered_value=dec.original_entered_value or str(dec.resolved_value),
            original_unit=dec.original_unit or parse_result.entered_unit,
            policy_id=dec.policy_id,
            policy_version=dec.policy_version,
            user_accepted=dec.user_accepted,
            superseded_value=superseded,
            evidence_refs=list(dec.evidence_refs or []),
            notes=dec.notes,
            resolved_by=dec.resolved_by,
        )

        # 5. Build explicit ProvenanceRecord
        res_src_val = dec.resolution_source.value if hasattr(dec.resolution_source, "value") else str(dec.resolution_source)
        is_user = res_src_val in ("user_supplied", "user_confirmed", "user_corrected")
        prov = ProvenanceRecord(
            source=res_src_val,
            confidence=1.0 if is_user else 0.99,
            policy_id=dec.policy_id,
            policy_version=dec.policy_version,
            user_accepted=dec.user_accepted,
            superseded_value=superseded,
            derived_from=list(dec.evidence_refs or []),
            notes=f"Resolved via {res_src_val}" + (f" (policy: {dec.policy_id})" if dec.policy_id else ""),
        )

        # 6. Apply to BookIR with canonicalized parameter name
        if book_ir.parameters is None:
            book_ir.parameters = {}
        book_ir.parameters[target_param] = norm_val

        if book_ir.resolutions is None:
            book_ir.resolutions = {}
        book_ir.resolutions[target_param] = updated_dec.model_dump()

        if book_ir.parameter_provenance is None:
            book_ir.parameter_provenance = {}
        book_ir.parameter_provenance[target_param] = prov

        # Clean up legacy non-canonical alias key if input differed from canonical name
        if param_name != target_param:
            book_ir.parameters.pop(param_name, None)
            book_ir.resolutions.pop(param_name, None)
            book_ir.parameter_provenance.pop(param_name, None)

        # 7. Spatial calibration derivation (e.g. for pendulum physical length)
        calib_data = CalibrationEngine.derive_for_subtype(
            subtype=subtype,
            entities=book_ir.entities or [],
            parameters=book_ir.parameters,
            resolutions=book_ir.resolutions,
        )
        if calib_data:
            book_ir.calibration = calib_data

        # 8. Re-evaluate readiness and mutate status
        readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)

        return ResolutionResult(
            success=True,
            parameter_name=target_param,
            resolved_value=norm_val,
            canonical_unit=canonical_unit,
            original_entered_value=updated_dec.original_entered_value,
            resolution=updated_dec,
            readiness_report=readiness,
        )

    @classmethod
    def apply_policy(
        cls,
        book_ir: BookIR,
        policy_id: str,
        parameter_name: Optional[str] = None,
        user_accepted: bool = True,
    ) -> ResolutionResult:
        """Apply a named explicit policy from PolicyRegistry."""
        policy = PolicyRegistry.get_policy(policy_id)
        if not policy:
            return ResolutionResult(
                success=False,
                parameter_name=parameter_name or "",
                error=f"Policy '{policy_id}' not found in PolicyRegistry.",
                readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
            )

        domain = getattr(book_ir, "domain", None)
        subtype = getattr(book_ir, "subtype", None)

        # 1. Enforce domain match
        if domain and policy.domain and policy.domain.lower() != domain.lower():
            return ResolutionResult(
                success=False,
                parameter_name=parameter_name or policy.target_parameter,
                error=f"POLICY_DOMAIN_MISMATCH: Policy '{policy_id}' belongs to domain '{policy.domain}', but BookIR domain is '{domain}'.",
                readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
            )

        # 2. Enforce target subtype match if specified on policy
        if policy.target_subtype and subtype and policy.target_subtype.lower() != subtype.lower():
            return ResolutionResult(
                success=False,
                parameter_name=parameter_name or policy.target_parameter,
                error=f"POLICY_SUBTYPE_MISMATCH: Policy '{policy_id}' targets subtype '{policy.target_subtype}', but BookIR subtype is '{subtype}'.",
                readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
            )

        # 3. Retrieve model requirement spec
        spec = RequirementRegistry.get_spec(subtype) if subtype else None
        if not spec:
            return ResolutionResult(
                success=False,
                parameter_name=parameter_name or policy.target_parameter,
                error=f"UNKNOWN_MODEL_SUBTYPE: Subtype '{subtype}' in domain '{domain}' does not have a registered ModelRequirementSpec.",
                readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
            )

        # 4. Enforce policy is listed in spec.allowed_policies
        allowed_policies = spec.allowed_policies or []
        if policy.id not in allowed_policies and policy.policy_id not in allowed_policies:
            return ResolutionResult(
                success=False,
                parameter_name=parameter_name or policy.target_parameter,
                error=f"POLICY_NOT_ALLOWED_FOR_SUBTYPE: Policy '{policy_id}' is not in allowed policies {allowed_policies} for subtype '{subtype}'.",
                readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
            )

        # 5. Determine target parameter
        target_param = parameter_name
        if not target_param:
            if subtype == "interface_refraction":
                if policy.id == "policy_air_refractive_index" and "n1" not in (book_ir.parameters or {}):
                    target_param = "n1"
                elif "n1" in (book_ir.parameters or {}):
                    target_param = "n2"
                else:
                    target_param = "n1"
            elif subtype == "prism":
                target_param = "n"
            else:
                target_param = policy.target_parameter

        canonical_target = spec.canonicalize_parameter(target_param)
        if canonical_target not in spec.parameters and target_param not in spec.parameters:
            return ResolutionResult(
                success=False,
                parameter_name=target_param,
                error=f"POLICY_INVALID_PARAMETER: Parameter '{target_param}' resolved by policy '{policy_id}' is not declared for subtype '{subtype}'.",
                readiness_report=ReadinessEvaluator.evaluate(book_ir, mutate_status=False),
            )

        final_param = canonical_target if canonical_target in spec.parameters else target_param

        dec = ResolutionDecision(
            id=f"res_{final_param}_{policy_id}",
            parameter_name=final_param,
            target_subtype=book_ir.subtype,
            resolution_source=ResolutionSource.POLICY_DEFAULT,
            resolved_value=policy.value,
            canonical_unit=policy.unit,
            original_entered_value=str(policy.value),
            original_unit=policy.unit,
            policy_id=policy.policy_id,
            policy_version=policy.version,
            user_accepted=user_accepted,
            notes=f"Accepted policy default '{policy.name}' ({policy.description})",
            resolved_by="policy_engine",
        )
        return cls.apply_resolution(book_ir, dec)

    @classmethod
    def confirm_candidate(
        cls,
        book_ir: BookIR,
        parameter_name: str,
        candidate: Dict[str, Any],
        user_id: str = "user",
    ) -> ResolutionResult:
        """Confirm an unverified OCR candidate, marking source as USER_CONFIRMED."""
        val = candidate.get("value")
        unit = candidate.get("unit", "")
        ev_id = candidate.get("evidence_id")
        tok_id = candidate.get("token_id")
        refs = [r for r in (ev_id, tok_id) if r]

        dec = ResolutionDecision(
            id=f"res_confirm_{parameter_name}_{tok_id or 'ocr'}",
            parameter_name=parameter_name,
            target_subtype=book_ir.subtype,
            resolution_source=ResolutionSource.USER_CONFIRMED,
            resolved_value=val,
            canonical_unit=unit,
            original_entered_value=str(val),
            original_unit=unit,
            evidence_refs=refs,
            notes="User confirmed detected OCR candidate.",
            resolved_by=user_id,
            user_accepted=True,
        )
        return cls.apply_resolution(book_ir, dec)

    @classmethod
    def remove_resolution(cls, book_ir: BookIR, parameter_name: str) -> ReadinessReport:
        """Remove a resolution decision, ensuring idempotence and reversibility.

        Transitions status back to NEEDS_REVIEW if a required parameter is now missing.
        """
        subtype = getattr(book_ir, "subtype", None)
        spec = RequirementRegistry.get_spec(subtype) if subtype else None
        canonical_param = spec.canonicalize_parameter(parameter_name) if spec else parameter_name

        keys_to_remove = set([parameter_name, canonical_param])
        for k in keys_to_remove:
            if book_ir.parameters and k in book_ir.parameters:
                del book_ir.parameters[k]
            if book_ir.resolutions and k in book_ir.resolutions:
                del book_ir.resolutions[k]
            if book_ir.parameter_provenance and k in book_ir.parameter_provenance:
                del book_ir.parameter_provenance[k]

        # Invalidate calibration if it depended on this parameter
        if hasattr(book_ir, "calibration") and getattr(book_ir, "calibration"):
            calib = getattr(book_ir, "calibration")
            ref_param = calib.reference_parameter if hasattr(calib, "reference_parameter") else (
                calib.get("reference_parameter") if isinstance(calib, dict) else None
            )
            if ref_param in keys_to_remove:
                book_ir.calibration = None

        # Re-evaluate and mutate status
        return ReadinessEvaluator.evaluate(book_ir, mutate_status=True)

"""PR-07 Deterministic Readiness Evaluator.

Evaluates whether a resolved BookIR satisfies the strict READY_TO_COMPILE invariant.
CRITICAL INVARIANTS:
1. Deterministic and reversible: if a required value is removed, returns to NEEDS_REVIEW.
2. Complete provenance check: every resolved parameter must have an explicit provenance record.
3. Strict gating: no hidden compiler patching; zero tolerance for ungrounded or ambiguous geometry.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from shared.schemas.ingestion import BookIR, BookIRStatus
from shared.schemas.resolution import ReadinessReport, ReviewState
from ai.resolution.analyzer import ResolutionAnalyzer
from ai.resolution.requirements import RequirementRegistry
from ai.resolution.units import UnitEngine


class ReadinessEvaluator:
    """Strict gatekeeper verifying that BookIR is legitimately READY_TO_COMPILE."""

    @classmethod
    def evaluate(cls, book_ir: BookIR, mutate_status: bool = False) -> ReadinessReport:
        """Evaluate readiness against the canonical PR-07 READY_TO_COMPILE invariant.

        Args:
            book_ir: The BookIR to evaluate.
            mutate_status: If True, updates book_ir.status to READY_TO_COMPILE or NEEDS_REVIEW.
        """
        review_state: ReviewState = ResolutionAnalyzer.analyze(book_ir)
        subtype = book_ir.subtype
        spec = RequirementRegistry.get_spec(subtype) if subtype else None

        blockers: List[str] = [iss.description for iss in review_state.issues if iss.is_blocker]
        warnings: List[str] = [iss.description for iss in review_state.issues if not iss.is_blocker]
        unresolved_ambiguities: List[str] = [
            iss.description
            for iss in review_state.issues
            if (
                iss.issue_type
                in (
                    "ungrounded_geometry",
                    "ambiguous_geometry",
                    "ambiguous_semantics",
                    "ambiguous_evidence",
                    "conflicting_evidence",
                    "unresolved_disambiguation",
                )
                or getattr(iss.issue_type, "value", str(iss.issue_type))
                in (
                    "ungrounded_geometry",
                    "ambiguous_geometry",
                    "ambiguous_semantics",
                    "ambiguous_evidence",
                    "conflicting_evidence",
                    "unresolved_disambiguation",
                )
            )
        ]

        policy_assumptions: List[Dict[str, Any]] = []
        resolutions = book_ir.resolutions or {}
        parameters = book_ir.parameters or {}
        parameter_provenance = book_ir.parameter_provenance or {}

        # Verify provenance and range constraints for every resolved parameter
        if spec:
            for param in spec.required_parameters:
                p_req = spec.parameters.get(param)

                # Check if this parameter is part of a satisfied one_of group (e.g. length OR pixels_per_meter)
                is_satisfied_by_one_of = False
                for group in spec.one_of_requirements:
                    if param in group:
                        other_satisfied = any(
                            other != param and (
                                (other in parameters and parameters[other] is not None)
                                or (other in resolutions and resolutions[other] is not None)
                                or (other in (book_ir.geometry or {}) and (book_ir.geometry or {})[other] is not None)
                            )
                            for other in group
                        )
                        if other_satisfied:
                            is_satisfied_by_one_of = True
                            break

                val = parameters.get(param)
                if val is None:
                    res = resolutions.get(param)
                    if isinstance(res, dict):
                        val = res.get("resolved_value") if res.get("resolved_value") is not None else (
                            res.get("resolvedValue") if res.get("resolvedValue") is not None else res.get("value")
                        )
                    elif hasattr(res, "resolved_value"):
                        val = getattr(res, "resolved_value") if getattr(res, "resolved_value") is not None else getattr(res, "value", None)

                if val is None and is_satisfied_by_one_of:
                    continue

                if val is not None:
                    # Categorical constraint check
                    if p_req and p_req.allowed_categories:
                        val_str = str(val).lower().strip()
                        allowed_lower = [c.lower().strip() for c in p_req.allowed_categories]
                        if val_str not in allowed_lower:
                            blockers.append(
                                f"Parameter '{param}' has invalid categorical value '{val}' (allowed: {p_req.allowed_categories})."
                            )

                    # Numeric finite and range constraint check
                    if isinstance(val, (int, float)) and not isinstance(val, bool):
                        if not math.isfinite(val):
                            blockers.append(f"Parameter '{param}' has non-finite numeric value: {val}")
                        elif p_req:
                            must_pos = (p_req.min_value is not None and p_req.min_value > 0 and not p_req.allow_zero)
                            range_err = UnitEngine.validate_range(
                                val,
                                min_value=p_req.min_value,
                                max_value=p_req.max_value,
                                must_be_positive=must_pos,
                                allow_zero=p_req.allow_zero,
                                param_name=param,
                            )
                            if range_err:
                                blockers.append(range_err)

                    # Strict, parameter-specific provenance check
                    has_prov = (
                        param in parameter_provenance
                        or param in resolutions
                        or param in (book_ir.provenance or {})
                    )
                    if not has_prov:
                        raw_param = parameters.get(param)
                        if hasattr(raw_param, "provenance") and getattr(raw_param, "provenance") is not None:
                            has_prov = True
                        elif isinstance(raw_param, dict) and raw_param.get("provenance") is not None:
                            has_prov = True

                    # Only geometry-backed parameters may derive provenance from matching geometric elements/entities
                    if not has_prov and p_req and p_req.can_derive_from_geometry:
                        geom = book_ir.geometry or {}
                        geom_val = geom.get(param)
                        if isinstance(geom_val, dict) and geom_val.get("provenance") is not None:
                            has_prov = True
                        elif hasattr(geom_val, "provenance") and getattr(geom_val, "provenance") is not None:
                            has_prov = True
                        else:
                            # Must match the specific semantic entity role tied to this parameter
                            entity_role_map = {
                                "pivot": ("pivot", "anchor"),
                                "bob_position": ("bob", "bob_center"),
                                "bob_radius_px": ("bob",),
                                "string_length_px": ("string", "rod"),
                                "lens_center": ("lens",),
                                "aperture_height_px": ("lens", "mirror"),
                                "pole": ("mirror",),
                                "launch_position": ("launch_source", "projectile_body"),
                                "ball_radius_px": ("projectile_body",),
                                "boundary_y": ("interface_boundary",),
                                "normal_x": ("interface_boundary",),
                                "vertices": ("prism_body", "prism"),
                                "nodes": ("circuit", "resistor"),
                                "components": ("circuit", "resistor"),
                            }
                            target_roles = entity_role_map.get(param, ())
                            for e in (book_ir.entities or []):
                                e_role = getattr(e, "type", None) or getattr(e, "role", None)
                                if e_role in target_roles:
                                    if getattr(e, "provenance", None) or getattr(e, "evidence_refs", None):
                                        has_prov = True
                                        break

                    if not has_prov:
                        blockers.append(f"Parameter '{param}' lacks explicit provenance record.")

        # Collect policy assumptions
        for p_name, res in resolutions.items():
            res_dict = res if isinstance(res, dict) else (res.model_dump() if hasattr(res, "model_dump") else {})
            if res_dict.get("policy_id") or res_dict.get("resolution_source") == "policy_default":
                policy_assumptions.append({
                    "parameter": p_name,
                    "policy_id": res_dict.get("policy_id"),
                    "value": res_dict.get("resolved_value"),
                    "unit": res_dict.get("canonical_unit"),
                })

        calibration_info = None
        if hasattr(book_ir, "calibration") and getattr(book_ir, "calibration"):
            calib = getattr(book_ir, "calibration")
            calibration_info = calib.to_dict() if hasattr(calib, "to_dict") else calib

        is_ready = (len(blockers) == 0 and len(unresolved_ambiguities) == 0 and len(review_state.missing_requirements) == 0)

        new_status = BookIRStatus.READY_TO_COMPILE if is_ready else BookIRStatus.NEEDS_REVIEW
        if mutate_status:
            book_ir.status = new_status

        return ReadinessReport(
            ready=is_ready,
            status=new_status,
            book_ir_id=book_ir.id,
            subtype=subtype,
            blockers=blockers,
            warnings=warnings,
            satisfied_requirements=review_state.satisfied_requirements,
            missing_requirements=review_state.missing_requirements,
            policy_assumptions=policy_assumptions,
            unresolved_ambiguities=unresolved_ambiguities,
            calibration_status=calibration_info,
        )

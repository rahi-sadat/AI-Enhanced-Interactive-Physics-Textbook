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
from ai.resolution.policies import PolicyRegistry
from ai.resolution.units import UnitEngine
from ai.resolution.assumptions import automatic_visual_blockers


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
        blockers.extend(automatic_visual_blockers(book_ir))
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

        # A reviewed decision and the value consumed by the compiler must
        # agree. Otherwise a later edit could leave a valid-looking resolution
        # attached to a different physical value.
        for param, resolution in resolutions.items():
            res_data = resolution if isinstance(resolution, dict) else (
                resolution.model_dump() if hasattr(resolution, "model_dump") else {}
            )
            resolved_value = res_data.get("resolvedValue", res_data.get("resolved_value"))
            if param in parameters and resolved_value is not None:
                current = parameters[param]
                if isinstance(current, dict) and "value" in current:
                    current = current["value"]
                if isinstance(current, (int, float)) and not isinstance(current, bool) and isinstance(resolved_value, (int, float)) and not isinstance(resolved_value, bool):
                    agrees = math.isfinite(current) and math.isfinite(resolved_value) and math.isclose(current, resolved_value, rel_tol=1e-9, abs_tol=1e-12)
                else:
                    agrees = current == resolved_value
                if not agrees:
                    blockers.append(f"Parameter '{param}' conflicts with its recorded resolution.")

            policy_id = res_data.get("policyId", res_data.get("policy_id"))
            if policy_id:
                policy = PolicyRegistry.get_policy(policy_id)
                accepted = res_data.get("userAccepted", res_data.get("user_accepted", False))
                auto_applied = res_data.get("resolvedBy", res_data.get("resolved_by")) == "auto_policy"
                if policy is None or (policy.requires_user_opt_in and accepted is not True and not auto_applied):
                    blockers.append(f"Policy resolution for '{param}' lacks a valid, accepted policy.")

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
                    raw_value = val.get("value") if isinstance(val, dict) and "value" in val else val
                    raw_unit = val.get("unit") if isinstance(val, dict) else None
                    if hasattr(raw_value, "value"):
                        raw_unit = getattr(raw_value, "unit", raw_unit)
                        raw_value = raw_value.value
                    if p_req and p_req.dimension.value not in ("point_2d", "polygon_points", "categorical", "topology_nodes", "topology_components"):
                        expected_dimension = p_req.dimension.value
                        if expected_dimension == "damping" and str(raw_unit).lower() == "hz":
                            raw_unit = "1/s"
                        parsed = UnitEngine.parse_quantity(raw_value, raw_unit, expected_dimension)
                        if not parsed.success:
                            blockers.append(f"Parameter '{param}' has invalid units or value: {parsed.error}")
                        else:
                            raw_value = parsed.canonical_value

                    # Categorical constraint check
                    if p_req and p_req.allowed_categories:
                        val_str = str(raw_value).lower().strip()
                        allowed_lower = [c.lower().strip() for c in p_req.allowed_categories]
                        if val_str not in allowed_lower:
                            blockers.append(
                                f"Parameter '{param}' has invalid categorical value '{val}' (allowed: {p_req.allowed_categories})."
                            )

                    # Numeric finite and range constraint check
                    if isinstance(raw_value, (int, float)) and not isinstance(raw_value, bool):
                        if not math.isfinite(raw_value):
                            blockers.append(f"Parameter '{param}' has non-finite numeric value: {raw_value}")
                        elif p_req:
                            must_pos = (p_req.min_value is not None and p_req.min_value > 0 and not p_req.allow_zero)
                            range_err = UnitEngine.validate_range(
                                raw_value,
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

        readiness_mode = None
        if is_ready:
            new_status = BookIRStatus.READY_TO_COMPILE
            has_si_calibration = False
            calib = getattr(book_ir, "calibration", None)
            if calib and getattr(calib, "verified", False):
                has_si_calibration = True
            elif hasattr(book_ir, "parameters") and book_ir.parameters:
                ppm_prov = (book_ir.parameter_provenance or {}).get("pixels_per_meter")
                if ppm_prov and getattr(ppm_prov, "source", None) in ("ocr", "author_override", "user_confirmed"):
                    has_si_calibration = True
            readiness_mode = "PHYSICS_VERIFIED" if has_si_calibration else "AUTO_VISUAL"
        elif not book_ir.domain or not book_ir.subtype or book_ir.isPhysics is False:
            classification = (book_ir.provenance or {}).get("classification")
            new_status = (BookIRStatus.UNSUPPORTED if classification == "unsupported_physics"
                          else BookIRStatus.UNRESOLVED)
            readiness_mode = "UNSUPPORTED"
        elif len(unresolved_ambiguities) > 0 or len(blockers) > 0:
            new_status = BookIRStatus.NEEDS_REVIEW
            readiness_mode = "NEEDS_VISUAL_REVIEW"
        else:
            new_status = BookIRStatus.NEEDS_REVIEW
            readiness_mode = "SUPPORTED_NEEDS_GROUNDING"

        if mutate_status:
            book_ir.status = new_status
            if hasattr(book_ir, "metadata") and isinstance(book_ir.metadata, dict):
                book_ir.metadata["readiness_mode"] = readiness_mode

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
            readiness_mode=readiness_mode,
        )

"""PR-07 Deterministic Resolution Analyzer.

Inspects grounded BookIR against machine-readable ModelRequirementSpec contracts.
Identifies:
- satisfied requirements
- missing requirements
- unverified OCR candidates needing user confirmation
- policy default options
- ambiguous visual geometry blockers
- conflicting evidence

CRITICAL INVARIANTS:
1. Pure analysis: never mutates BookIR.
2. Zero parameter fabrication: missing values are flagged as blockers.
3. Minimal questions: only asks what blocks compilation or represents real ambiguity.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Set

from shared.schemas.ingestion import BookIR, BookEntity
from shared.schemas.resolution import (
    ResolutionActionType,
    ReviewIssue,
    ReviewIssueType,
    ReviewState,
)
from ai.resolution.policies import PolicyRegistry
from ai.resolution.requirements import ModelRequirementSpec, RequirementRegistry
from ai.resolution.units import UnitEngine


class ResolutionAnalyzer:
    """Deterministic, zero-fabrication analysis pass producing a structured ReviewState."""

    @classmethod
    def analyze(cls, book_ir: BookIR) -> ReviewState:
        """Analyze a grounded BookIR against compiler requirements without mutating it."""
        book_id = book_ir.id
        subtype = book_ir.subtype
        domain = book_ir.domain

        issues: List[ReviewIssue] = []
        satisfied_reqs: List[str] = []
        missing_reqs: List[str] = []

        # 1. Gate: Valid Physics Classification
        if book_ir.isPhysics is False or not domain or not subtype:
            issues.append(
                ReviewIssue(
                    id="issue_non_physics_classification",
                    issue_type=ReviewIssueType.AMBIGUOUS_SEMANTICS,
                    title="Unsupported or Non-Physics Diagram",
                    description="Diagram is not classified as a supported physics domain/subtype.",
                    question="This diagram cannot be compiled because it does not represent a supported physics model.",
                    action_type=ResolutionActionType.CHOOSE_OPTION,
                    is_blocker=True,
                )
            )
            return ReviewState(
                book_ir_id=book_id,
                subtype=subtype,
                ready_to_compile=False,
                blockers_count=len(issues),
                warnings_count=0,
                satisfied_requirements=[],
                missing_requirements=[],
                issues=issues,
                available_policies=[],
            )

        # 2. Gate: Spec Lookup
        spec = RequirementRegistry.get_spec(subtype)
        if not spec:
            issues.append(
                ReviewIssue(
                    id=f"issue_unsupported_subtype_{subtype}",
                    issue_type=ReviewIssueType.AMBIGUOUS_SEMANTICS,
                    title=f"Unsupported Subtype: {subtype}",
                    description=f"No compiler requirement specification registered for subtype '{subtype}'.",
                    question=f"Compiler support for '{subtype}' is not yet registered.",
                    action_type=ResolutionActionType.CHOOSE_OPTION,
                    is_blocker=True,
                )
            )
            return ReviewState(
                book_ir_id=book_id,
                subtype=subtype,
                ready_to_compile=False,
                blockers_count=len(issues),
                warnings_count=0,
                satisfied_requirements=[],
                missing_requirements=[],
                issues=issues,
                available_policies=[],
            )

        # 3. Check Visual Geometry Requirements
        cls._check_geometry_requirements(book_ir, spec, issues)

        # 4. Check Required Physical Parameters
        cls._check_parameter_requirements(book_ir, spec, issues, satisfied_reqs, missing_reqs)

        for group in spec.one_of_requirements:
            value_sources = (book_ir.geometry or {}, book_ir.parameters or {}, book_ir.resolutions or {})
            aliases = {alias for alias, canonical in spec.parameter_aliases.items() if canonical in group}
            if not any(source.get(name) is not None
                       for source in value_sources for name in set(group) | aliases):
                label = " or ".join(group)
                issues.append(ReviewIssue(
                    id=f"issue_missing_one_of_{'_'.join(group)}",
                    issue_type=ReviewIssueType.MISSING_PARAMETER,
                    title=f"Missing {label}",
                    description=f"Simulation requires {label}.",
                    question=f"Provide or verify {label} before simulation.",
                    action_type=ResolutionActionType.CHOOSE_OPTION,
                    target_subtype=subtype,
                    is_blocker=True,
                ))

        if domain == "circuits" and subtype == "dc_linear":
            cls._check_circuit_components(book_ir, issues)

        # 5. Check Optional Parameters
        cls._check_optional_parameters(book_ir, spec, issues, satisfied_reqs)

        # 6. Collate Available Policies for Subtype
        policies = PolicyRegistry.get_policies_for_subtype(subtype, domain=domain)
        if spec and spec.allowed_policies:
            allowed_set = set(spec.allowed_policies)
            policies = [p for p in policies if p.id in allowed_set or p.policy_id in allowed_set]
        available_policies_data = [p.to_dict() for p in policies]

        blockers = [iss for iss in issues if iss.is_blocker]
        warnings = [iss for iss in issues if not iss.is_blocker]

        return ReviewState(
            book_ir_id=book_id,
            subtype=subtype,
            ready_to_compile=len(blockers) == 0,
            blockers_count=len(blockers),
            warnings_count=len(warnings),
            satisfied_requirements=satisfied_reqs,
            missing_requirements=missing_reqs,
            issues=issues,
            available_policies=available_policies_data,
        )

    @classmethod
    def _check_circuit_components(cls, book_ir: BookIR, issues: List[ReviewIssue]) -> None:
        """Keep review readiness aligned with the compiler's DC graph/value gate."""
        params = book_ir.parameters or {}
        components = params.get("components")
        nodes = params.get("nodes")
        components = getattr(components, "value", components)
        nodes = getattr(nodes, "value", nodes)
        if not isinstance(components, list) or not isinstance(nodes, list):
            if any(entity.type in {"switch", "open_switch", "closed_switch"} for entity in book_ir.entities or []):
                issues.append(ReviewIssue(
                    id="issue_circuit_switch_state_unverified",
                    issue_type=ReviewIssueType.AMBIGUOUS_GEOMETRY,
                    title="Switch state and connections require review",
                    description="A switch is present but its state and connections are not grounded in the circuit graph.",
                    question="Verify the switch state and circuit topology before simulation.",
                    action_type=ResolutionActionType.CHOOSE_OPTION,
                    target_subtype="dc_linear",
                    is_blocker=True,
                ))
            return  # The generic requirement checks already report missing topology.

        node_ids = {n if isinstance(n, str) else n.get("id")
                    for n in nodes if isinstance(n, (str, dict))}

        # Switches require grounded connection and defined state
        for entity in book_ir.entities or []:
            if entity.type in {"switch", "open_switch", "closed_switch"}:
                comp = next((c for c in components if isinstance(c, dict) and (c.get("id") == entity.id or c.get("type") in {"switch", "open_switch", "closed_switch"})), None)
                is_grounded = False
                if comp:
                    terminals = comp.get("nodes")
                    has_nodes = isinstance(terminals, list) and len(terminals) == 2 and all(n in node_ids for n in terminals)
                    has_state = comp.get("state") in {"open", "closed"} or comp.get("closed") in {True, False} or comp.get("type") in {"open_switch", "closed_switch"}
                    if has_nodes and has_state:
                        is_grounded = True
                if not is_grounded:
                    issues.append(ReviewIssue(
                        id=f"issue_circuit_switch_state_unverified_{entity.id}",
                        issue_type=ReviewIssueType.AMBIGUOUS_GEOMETRY,
                        title="Switch state and connections require review",
                        description=f"Switch {entity.id} is present but its state and connections are not grounded in the circuit graph.",
                        question="Verify the switch state and circuit topology before simulation.",
                        action_type=ResolutionActionType.CHOOSE_OPTION,
                        target_subtype="dc_linear",
                        is_blocker=True,
                    ))

        node_ids = {n if isinstance(n, str) else n.get("id")
                    for n in nodes if isinstance(n, (str, dict))}
        sources = {"voltage_source", "battery", "dc_source"}
        if not any(isinstance(c, dict) and c.get("type") in sources for c in components):
            issues.append(ReviewIssue(
                id="issue_circuit_missing_source",
                issue_type=ReviewIssueType.UNGROUNDED_GEOMETRY,
                title="Missing grounded DC source",
                description="The circuit graph has no grounded voltage source.",
                question="Confirm the source symbol, terminals, and voltage before simulation.",
                action_type=ResolutionActionType.CHOOSE_OPTION,
                target_subtype="dc_linear",
                is_blocker=True,
            ))

        for index, component in enumerate(components):
            if not isinstance(component, dict):
                continue
            cid = component.get("id") or f"component_{index}"
            terminals = component.get("nodes")
            if (not isinstance(terminals, list) or len(terminals) != 2
                    or any(node not in node_ids for node in terminals)
                    or (component.get("type") in sources and terminals[0] == terminals[1])):
                issues.append(ReviewIssue(
                    id=f"issue_circuit_connection_{cid}",
                    issue_type=ReviewIssueType.UNGROUNDED_GEOMETRY,
                    title=f"Unverified connection for {cid}",
                    description=f"Circuit component {cid} has no valid two-node connection.",
                    question=f"Verify both terminals of {cid} against the diagram.",
                    action_type=ResolutionActionType.CHOOSE_OPTION,
                    target_subtype="dc_linear",
                    is_blocker=True,
                ))

            if component.get("type") in sources | {"resistor", "bulb", "lamp"}:
                value = component.get("value")
                dimension = "voltage" if component.get("type") in sources else "resistance"
                valid = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                if valid and dimension == "resistance":
                    valid = value > 0
                if valid:
                    valid = UnitEngine.parse_quantity(value, component.get("unit"), dimension).success
                if not valid:
                    issues.append(ReviewIssue(
                        id=f"issue_circuit_value_{cid}",
                        issue_type=ReviewIssueType.MISSING_PARAMETER,
                        title=f"Unverified value for {cid}",
                        description=f"Circuit component {cid} lacks a valid grounded {dimension} value and unit.",
                        question=f"Confirm the {dimension} printed for {cid} before simulation.",
                        action_type=ResolutionActionType.CHOOSE_OPTION,
                        target_subtype="dc_linear",
                        is_blocker=True,
                    ))

    @classmethod
    def _check_geometry_requirements(
        cls, book_ir: BookIR, spec: ModelRequirementSpec, issues: List[ReviewIssue]
    ) -> None:
        """Verify all required visual entities and geometry exist, have verified coordinates, and are non-ambiguous."""
        entities = book_ir.entities or []
        geom = book_ir.geometry or {}
        params = book_ir.parameters or {}
        resolutions = book_ir.resolutions or {}

        entity_synonyms = {
            "pivot": ("pivot", "anchor", "support"),
            "bob": ("bob", "mass", "pendulum_bob"),
            "string": ("string", "rod", "wire"),
            "lens": ("lens", "thin_lens", "convex_lens", "concave_lens"),
            "mirror": ("mirror", "spherical_mirror", "concave_mirror", "convex_mirror"),
            "prism": ("prism", "prism_body", "triangular_prism"),
            "prism_body": ("prism", "prism_body", "triangular_prism"),
            "projectile_body": ("projectile_body", "projectile", "ball", "body"),
            "launch_source": ("launch_source", "cannon", "source", "origin"),
            "interface_boundary": ("interface_boundary", "medium_boundary", "boundary", "interface", "surface"),
            "resistor": ("resistor", "component", "circuit"),
        }

        # 1. Check required entities
        for req_ent in spec.required_entities:
            synonyms = entity_synonyms.get(req_ent, (req_ent,))
            matched_ent = next(
                (
                    e
                    for e in entities
                    if getattr(e, "type", None) in synonyms
                    or getattr(e, "role", None) in synonyms
                    or getattr(e, "name", None) in synonyms
                ),
                None,
            )

            if matched_ent is None:
                issues.append(
                    ReviewIssue(
                        id=f"issue_missing_entity_{req_ent}",
                        issue_type=ReviewIssueType.AMBIGUOUS_GEOMETRY,
                        title=f"Missing visual entity: {req_ent}",
                        description=f"Model requires visual entity '{req_ent}', but none was detected.",
                        question=f"Grounded visual entity '{req_ent}' is required to compile.",
                        action_type=ResolutionActionType.CHOOSE_OPTION,
                        is_blocker=True,
                        target_subtype=spec.subtype,
                    )
                )
            else:
                # Check coordinates and ambiguity
                pos = getattr(matched_ent, "position_source_px", None)
                is_ambig = getattr(matched_ent, "is_ambiguous", False) or (
                    getattr(matched_ent, "attributes", {}).get("is_ambiguous", False)
                    if hasattr(matched_ent, "attributes")
                    else False
                )
                if pos is None and req_ent not in ("string", "wire", "nodes", "components"):
                    # For circuits: components parameter holds authoritative grounded coordinates
                    circuit_comps = params.get("components") if spec.domain == "circuits" else None
                    comps_val = getattr(circuit_comps, "value", circuit_comps) if circuit_comps else None
                    has_grounded_comps = isinstance(comps_val, list) and any(
                        isinstance(c, dict) and (c.get("center_source_px") or c.get("bbox_source_px"))
                        for c in comps_val
                    )
                    if not (spec.domain == "circuits" and has_grounded_comps):
                        issues.append(
                            ReviewIssue(
                                id=f"issue_ungrounded_pos_{matched_ent.id}",
                                issue_type=ReviewIssueType.AMBIGUOUS_GEOMETRY,
                                entity_id=matched_ent.id,
                                title=f"Ungrounded position: {req_ent}",
                                description=f"Entity '{matched_ent.id}' ({req_ent}) lacks authoritative source_px coordinates.",
                                question=f"Visual coordinates for '{req_ent}' are ungrounded.",
                                action_type=ResolutionActionType.CHOOSE_OPTION,
                                is_blocker=True,
                                target_subtype=spec.subtype,
                            )
                        )
                elif is_ambig:
                    issues.append(
                        ReviewIssue(
                            id=f"issue_ambiguous_entity_{matched_ent.id}",
                            issue_type=ReviewIssueType.AMBIGUOUS_GEOMETRY,
                            entity_id=matched_ent.id,
                            title=f"Ambiguous visual entity: {req_ent}",
                            description=f"Entity '{matched_ent.id}' ({req_ent}) was flagged as geometrically ambiguous.",
                            question=f"Visual ambiguity in '{req_ent}' must be resolved before compiling.",
                            action_type=ResolutionActionType.CHOOSE_OPTION,
                            is_blocker=True,
                            target_subtype=spec.subtype,
                        )
                    )

        # 2. Check required geometric properties in book_ir.geometry or parameters
        alt_map = {
            "bob_center": ["bob_position", "bobCenter", "bob_center"],
            "string_length_px": ["length_px", "effective_length_px", "string_length_px"],
            "bob_radius_px": ["radius_px", "radius", "radius_source_px", "bob_radius_px"],
            "lens_center": ["optical_center", "center", "lens_center", "lensX", "axisY"],
            "focal_length_px": ["focalLength", "focal_length", "focal_length_px"],
            "boundary_y": ["boundaryY", "boundary_y"],
            "normal_x": ["normalX", "normal_x"],
            "pole": ["mirror_center", "pole", "pole_px", "center"],
            "vertices": ["prismVertices", "vertices"],
            "launch_position": ["launch_source", "launch_source_px", "launch_position", "launch_pos", "launch_origin"],
            "ball_radius_px": ["radius_px", "radius", "radius_source_px", "ball_radius_px"],
            "source_position": ["sourcePosition", "source_position", "ray_source", "ray_origin"],
            "ray_origin": ["rayOrigin", "ray_origin"],
            "ray_direction": ["rayDirection", "ray_direction"],
            "apex_angle_deg": ["apex_angle_deg", "apexAngle"],
            "aperture_height_px": ["aperture_height_px", "aperture"],
        }
        for req_g in spec.required_geometry:
            g_val = geom.get(req_g) or params.get(req_g) or resolutions.get(req_g)
            if g_val is None:
                for alt in alt_map.get(req_g, []):
                    if alt in geom:
                        g_val = geom[alt]
                        break
                    if alt in params:
                        g_val = params[alt]
                        break
                    if alt in resolutions:
                        g_val = resolutions[alt]
                        break

            # If still missing, check entities for geometry attributes
            if g_val is None:
                for e in entities:
                    e_geom = getattr(e, "geometry", None) or {}
                    if req_g in e_geom:
                        g_val = e_geom[req_g]
                        break

            if g_val is None and req_g not in spec.required_entities:
                issues.append(
                    ReviewIssue(
                        id=f"issue_missing_geom_{req_g}",
                        issue_type=ReviewIssueType.AMBIGUOUS_GEOMETRY,
                        title=f"Missing visual geometry: {req_g}",
                        description=f"Model requires grounded geometry property '{req_g}' in BookIR.",
                        question=f"Geometric measurement for '{req_g}' is missing.",
                        action_type=ResolutionActionType.CHOOSE_OPTION,
                        is_blocker=True,
                        target_subtype=spec.subtype,
                    )
                )


    @classmethod
    def _check_parameter_requirements(
        cls,
        book_ir: BookIR,
        spec: ModelRequirementSpec,
        issues: List[ReviewIssue],
        satisfied_reqs: List[str],
        missing_reqs: List[str],
    ) -> None:
        """Check all required physical parameters."""
        parameters = book_ir.parameters or {}
        resolutions = book_ir.resolutions or {}

        for param in spec.required_parameters:
            # Check if already resolved
            is_resolved = False
            if param in resolutions:
                res = resolutions[param]
                if isinstance(res, dict):
                    val = res.get("resolved_value") if res.get("resolved_value") is not None else (
                        res.get("resolvedValue") if res.get("resolvedValue") is not None else res.get("value")
                    )
                else:
                    val = getattr(res, "resolved_value", getattr(res, "value", None))
                if val is not None:
                    is_resolved = True

            if not is_resolved and param in parameters and parameters[param] is not None:
                is_resolved = True

            # Check parameter aliases
            if not is_resolved and spec.parameter_aliases:
                for alias_k, canon_k in spec.parameter_aliases.items():
                    if canon_k == param and alias_k in parameters and parameters[alias_k] is not None:
                        is_resolved = True
                        break

            # Check if satisfiable from geometry
            p_spec = spec.parameters.get(param)
            if not is_resolved and p_spec and p_spec.can_derive_from_geometry:
                geom = book_ir.geometry or {}
                if param in geom and geom[param] is not None:
                    is_resolved = True
                else:
                    alt_map = {
                        "bob_position": ["bob_center", "bobCenter", "bob_position"],
                        "bob_center": ["bob_position", "bobCenter", "bob_center"],
                        "string_length_px": ["length_px", "effective_length_px", "string_length_px"],
                        "bob_radius_px": ["radius_px", "radius", "radius_source_px", "ball_radius_px", "bob_radius_px"],
                        "lens_center": ["optical_center", "center", "lensX", "axisY", "lens_center"],
                        "focal_length_px": ["focalLength", "focal_length", "focal_length_px"],
                        "boundary_y": ["boundaryY", "boundary_y"],
                        "normal_x": ["normalX", "normal_x"],
                        "pole": ["mirror_center", "pole", "pole_px", "center"],
                        "vertices": ["prismVertices", "vertices"],
                        "launch_position": ["launch_source", "launch_source_px", "launch_pos", "launch_position", "launch_origin"],
                        "ball_radius_px": ["radius_px", "radius", "radius_source_px", "ball_radius_px"],
                        "source_position": ["sourcePosition", "source_position", "ray_source", "ray_origin"],
                        "ray_origin": ["rayOrigin", "ray_origin"],
                        "ray_direction": ["rayDirection", "ray_direction"],
                        "apex_angle_deg": ["apex_angle_deg", "apexAngle"],
                        "aperture_height_px": ["aperture_height_px", "aperture"],
                    }
                    for alt in alt_map.get(param, []):
                        if alt in geom and geom[alt] is not None:
                            is_resolved = True
                            break

            # Check one_of_requirements (e.g. length OR pixels_per_meter)
            if not is_resolved:
                for group in spec.one_of_requirements:
                    if param in group:
                        other_satisfied = any(
                            other != param and (
                                (other in resolutions and resolutions[other] is not None)
                                or (other in parameters and parameters[other] is not None)
                                or (other in (book_ir.geometry or {}) and (book_ir.geometry or {})[other] is not None)
                            )
                            for other in group
                        )
                        if other_satisfied:
                            is_resolved = True
                            break

            if is_resolved:
                satisfied_reqs.append(param)
                continue

            # Parameter is missing - investigate evidence
            missing_reqs.append(param)
            ocr_candidate = cls._find_unverified_ocr_candidate(book_ir, param, spec)

            allowed_units = spec.allowed_units.get(param, [])
            expected_dim = spec.expected_dimensions.get(param, "")

            if ocr_candidate is not None:
                # Issue: Candidate confirmation
                cand_val = ocr_candidate.get("value")
                cand_unit = ocr_candidate.get("unit", "")
                conf = ocr_candidate.get("confidence", 0.0)
                ev_id = ocr_candidate.get("evidence_id", "")

                issues.append(
                    ReviewIssue(
                        id=f"issue_confirm_{param}",
                        issue_type=ReviewIssueType.UNVERIFIED_OCR_CANDIDATE,
                        parameter_name=param,
                        target_subtype=spec.subtype,
                        title=f"Confirm OCR candidate for {param}",
                        description=f"OCR extracted candidate value '{cand_val} {cand_unit}' (confidence: {conf:.2f}), requiring verification.",
                        question=f"OCR detected {param} = {cand_val} {cand_unit}. Confirm or enter corrected value?",
                        action_type=ResolutionActionType.CONFIRM_CANDIDATE,
                        is_blocker=True,
                        candidates=[ocr_candidate],
                        allowed_units=allowed_units,
                        evidence_refs=[ev_id] if ev_id else [],
                    )
                )
            else:
                # Check if a policy default exists for this param
                policy = PolicyRegistry.find_policy(spec.subtype, param)
                if policy:
                    issues.append(
                        ReviewIssue(
                            id=f"issue_policy_{param}",
                            issue_type=ReviewIssueType.POLICY_SELECTION,
                            parameter_name=param,
                            target_subtype=spec.subtype,
                            title=f"Select value or policy default for {param}",
                            description=f"Subtype requires '{param}'. No visual/OCR value found. Explicit policy '{policy.name}' ({policy.value} {policy.unit}) is available.",
                            question=f"Accept standard policy for {param} ({policy.name}: {policy.value} {policy.unit}) or enter a custom value?",
                            action_type=ResolutionActionType.ACCEPT_POLICY,
                            is_blocker=True,
                            default_policy_id=policy.policy_id,
                            policy_value=policy.value,
                            allowed_units=allowed_units,
                        )
                    )
                else:
                    # Missing parameter with no candidate and no policy
                    issues.append(
                        ReviewIssue(
                            id=f"issue_missing_{param}",
                            issue_type=ReviewIssueType.MISSING_PARAMETER,
                            parameter_name=param,
                            target_subtype=spec.subtype,
                            title=f"Missing required parameter: {param}",
                            description=f"Physics model requires '{param}' ({expected_dim}). No measurement detected in source.",
                            question=f"Please provide physical value for {param} ({expected_dim}):",
                            action_type=ResolutionActionType.ENTER_VALUE,
                            is_blocker=True,
                            allowed_units=allowed_units,
                        )
                    )

    @classmethod
    def _check_optional_parameters(
        cls,
        book_ir: BookIR,
        spec: ModelRequirementSpec,
        issues: List[ReviewIssue],
        satisfied_reqs: List[str],
    ) -> None:
        """Check optional parameters, surfacing non-blocking policies if available."""
        parameters = book_ir.parameters or {}
        resolutions = book_ir.resolutions or {}

        for param in spec.optional_parameters:
            is_resolved = (param in resolutions and resolutions[param] is not None) or (
                param in parameters and parameters[param] is not None
            )
            if is_resolved:
                satisfied_reqs.append(param)
                continue

            policy = PolicyRegistry.find_policy(spec.subtype, param)
            if policy:
                issues.append(
                    ReviewIssue(
                        id=f"issue_optional_policy_{param}",
                        issue_type=ReviewIssueType.POLICY_SELECTION,
                        parameter_name=param,
                        target_subtype=spec.subtype,
                        title=f"Optional parameter: {param}",
                        description=f"Optional parameter '{param}' is not specified. Policy '{policy.name}' ({policy.value} {policy.unit}) is available.",
                        question=f"Use default {policy.name} for {param}?",
                        action_type=ResolutionActionType.ACCEPT_POLICY,
                        is_blocker=False,  # Non-blocking warning/option
                        default_policy_id=policy.policy_id,
                        policy_value=policy.value,
                        allowed_units=spec.allowed_units.get(param, []),
                    )
                )

    @classmethod
    def _find_unverified_ocr_candidate(
        cls, book_ir: BookIR, param_name: str, spec: ModelRequirementSpec
    ) -> Optional[Dict[str, Any]]:
        """Look for unverified OCR candidates associated with param_name in evidence graph."""
        evidence = book_ir.evidence
        if not evidence:
            return None

        records = evidence.values() if hasattr(evidence, "values") else (evidence if isinstance(evidence, dict) else [])
        for rec in records:
            # rec could be EvidenceRecord or dict
            rec_dict = rec.to_dict() if hasattr(rec, "to_dict") else (rec if isinstance(rec, dict) else {})
            method = rec_dict.get("method")
            if method != "ocr":
                continue

            tokens = rec_dict.get("tokens", [])
            for tok in tokens:
                # Check if token text or candidates match parameter name
                raw = tok.get("rawText", "") if isinstance(tok, dict) else getattr(tok, "raw_text", "")
                candidates = tok.get("candidates", []) if isinstance(tok, dict) else getattr(tok, "candidates", [])
                for cand in candidates:
                    q_cand = cand.get("quantityCandidate") if isinstance(cand, dict) else getattr(cand, "quantity_candidate", None)
                    num_val = cand.get("numericValue") if isinstance(cand, dict) else getattr(cand, "numeric_value", None)
                    raw_unit = cand.get("rawUnit") if isinstance(cand, dict) else getattr(cand, "raw_unit", "")
                    conf = cand.get("confidence") if isinstance(cand, dict) else getattr(cand, "confidence", 0.5)

                    expected_dim = spec.expected_dimensions.get(param_name)
                    if num_val is not None and (q_cand == expected_dim or param_name.lower() in raw.lower()):
                        return {
                            "value": num_val,
                            "unit": raw_unit or "",
                            "confidence": conf or 0.5,
                            "evidence_id": rec_dict.get("id", ""),
                            "token_id": tok.get("id") if isinstance(tok, dict) else getattr(tok, "id", ""),
                            "raw_text": raw,
                        }
        return None

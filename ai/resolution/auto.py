"""Automatic, auditable model assumptions for image-grounded figures.

This stage never creates entities, pixel coordinates, or circuit topology.
Only the named policies below may supply missing model quantities.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any

from ai.resolution.engine import ResolutionEngine
from ai.resolution.evaluator import ReadinessEvaluator
from ai.resolution.policies import PolicyRegistry
from ai.resolution.requirements import RequirementRegistry
from shared.schemas.ingestion import BookIR, BookIRStatus, PhysicalValue, ProvenanceRecord
from shared.schemas.resolution import ResolutionDecision, ResolutionSource


# Restrict automatic assumptions to quantities that do not assert a measured
# diagram landmark or an unobserved circuit connection.
_AUTO_POLICIES = {
    "pendulum": (
        "policy_earth_gravity",
        "policy_zero_damping",
        "policy_standard_mass",
        "policy_standard_pendulum_length",
    ),
    "projectile": (
        "policy_earth_gravity",
        "policy_standard_projectile_speed",
        "policy_standard_projectile_scale",
    ),
    "prism": ("policy_crown_glass_refractive_index",),
}

_POINT_LANDMARKS = {
    "pendulum": ("pivot", "bob_center"),
    "projectile": ("launch_position",),
    "thin_lens": ("lens_center",),
    "spherical_mirror": ("pole",),
    "prism": ("ray_origin",),
}

_GEOMETRY_ALIASES = {"bob_center": "bob_position"}


def _grounded_value(book_ir: BookIR, key: str) -> Any:
    geom = book_ir.geometry or {}
    if geom.get(key) is not None:
        return geom[key]
    name = _GEOMETRY_ALIASES.get(key, key)
    raw = (book_ir.parameters or {}).get(name)
    if raw is None:
        return None
    # A raw semantic guess is not sufficient. Parameter grounding must carry
    # CV/OCR provenance before it can satisfy a visual requirement.
    evidence = (book_ir.parameter_provenance or {}).get(name)
    evidence = evidence or (raw.get("provenance") if isinstance(raw, dict) else getattr(raw, "provenance", None))
    if not evidence:
        return None
    if isinstance(raw, dict) and "value" in raw:
        return raw["value"]
    return getattr(raw, "value", raw)


def _inside_source(point: Any, width: float, height: float) -> bool:
    try:
        x = float(point["x"])
        y = float(point["y"])
        return math.isfinite(x) and math.isfinite(y) and 0 <= x <= width and 0 <= y <= height
    except (TypeError, KeyError, ValueError):
        return False


@dataclass
class AutoResolutionResult:
    book_ir: BookIR
    assumptions: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, str]] = field(default_factory=list)
    readiness: Any = None


class AutoResolutionEngine:
    @staticmethod
    def _normalize_lens_exploration_object(book_ir: BookIR, result: AutoResolutionResult) -> None:
        params = book_ir.parameters
        if params.get("object_position") is not None or params.get("objectDistance") is not None:
            return
        center = (book_ir.geometry or {}).get("lens_center")
        focal = params.get("focal_length_px")
        aperture = params.get("aperture_height_px")
        if not _inside_source(center, book_ir.geometry["width"], book_ir.geometry["height"]):
            return
        if not getattr(focal, "provenance", None) or not getattr(aperture, "provenance", None):
            return
        try:
            focal_px, aperture_px = float(focal.value), float(aperture.value)
        except (TypeError, ValueError):
            return
        if not all(math.isfinite(value) and value > 0 for value in (focal_px, aperture_px)):
            return
        policy_distance = PolicyRegistry.get_policy("policy_normalized_lens_object_distance")
        policy_height = PolicyRegistry.get_policy("policy_normalized_lens_object_height")
        if not policy_distance or not policy_height:
            return
        distance = min(focal_px * float(policy_distance.value), center["x"] * 0.8)
        height = aperture_px * float(policy_height.value)
        if distance <= 1 or height <= 1:
            return
        for name, value, policy, refs in (
            ("objectDistance", distance, policy_distance, focal.provenance.evidence_refs),
            ("object_height_px", height, policy_height, aperture.provenance.evidence_refs),
        ):
            provenance = ProvenanceRecord(
                source="auto_policy", evidence_refs=refs, confidence=0.7,
                policy_id=policy.id, policy_version=policy.version,
                user_accepted=False, notes=policy.description,
            )
            params[name] = PhysicalValue(value=value, unit="px", status="assumed", provenance=provenance)
            book_ir.parameter_provenance[name] = provenance
            result.assumptions.append({"parameter": name, "policyId": policy.id,
                                       "policyVersion": policy.version, "value": value,
                                       "unit": "px", "reason": policy.description,
                                       "derivedFrom": refs, "provenance": "auto_policy",
                                       "confidence": 0.7})

    @staticmethod
    def _normalize_mirror_exploration_object(book_ir: BookIR, result: AutoResolutionResult) -> None:
        params = book_ir.parameters
        if params.get("object_position") is not None or params.get("objectDistance") is not None:
            return
        geom = book_ir.geometry or {}
        pole = geom.get("pole")
        focal = params.get("focal_length_px")
        aperture = params.get("aperture_height_px")
        if not _inside_source(pole, geom["width"], geom["height"]):
            return
        if not getattr(focal, "provenance", None) or not getattr(aperture, "provenance", None):
            return
        try:
            focal_px, aperture_px = float(focal.value), float(aperture.value)
        except (TypeError, ValueError):
            return
        if not all(math.isfinite(value) and value > 0 for value in (focal_px, aperture_px)):
            return
        distance_policy = PolicyRegistry.get_policy("policy_normalized_mirror_object_distance")
        height_policy = PolicyRegistry.get_policy("policy_normalized_mirror_object_height")
        if not distance_policy or not height_policy:
            return
        distance = min(focal_px * float(distance_policy.value), pole["x"] * 0.8)
        height = aperture_px * float(height_policy.value)
        if distance <= 1 or height <= 1:
            return
        for name, value, policy, refs in (
            ("objectDistance", distance, distance_policy, focal.provenance.evidence_refs),
            ("object_height_px", height, height_policy, aperture.provenance.evidence_refs),
        ):
            provenance = ProvenanceRecord(
                source="auto_policy", evidence_refs=refs, confidence=0.7,
                policy_id=policy.id, policy_version=policy.version,
                user_accepted=False, notes=policy.description,
            )
            params[name] = PhysicalValue(value=value, unit="px", status="assumed", provenance=provenance)
            book_ir.parameter_provenance[name] = provenance
            result.assumptions.append({"parameter": name, "policyId": policy.id,
                                       "policyVersion": policy.version, "value": value,
                                       "unit": "px", "reason": policy.description,
                                       "derivedFrom": refs, "provenance": "auto_policy",
                                       "confidence": 0.7})

    @staticmethod
    def _normalize_prism_ray(book_ir: BookIR, result: AutoResolutionResult) -> None:
        geom = book_ir.geometry or {}
        if geom.get("ray_origin") is not None:
            return
        vertices = geom.get("vertices")
        policy = PolicyRegistry.get_policy("policy_normalized_prism_incident_ray")
        prism = next((entity for entity in book_ir.entities
                      if entity.type in {"prism", "prism_body"} and entity.geometry
                      and entity.evidence_refs), None)
        if not policy or not prism or not isinstance(vertices, list) or len(vertices) < 3:
            return
        try:
            points = sorted(({"x": float(v["x"]), "y": float(v["y"])} for v in vertices),
                            key=lambda v: v["y"])
            apex = points[0]
            left_base = min(points[1:], key=lambda v: v["x"])
            span = max(v["x"] for v in points) - min(v["x"] for v in points)
            origin = {"x": left_base["x"] - span * 0.25,
                      "y": (apex["y"] + left_base["y"]) / 2.0}
            if span <= 0 or not _inside_source(origin, geom["width"], geom["height"]):
                return
        except (KeyError, TypeError, ValueError):
            return
        direction = {"x": 1.0, "y": 0.0}
        provenance = ProvenanceRecord(
            source="auto_policy", evidence_refs=prism.evidence_refs, confidence=0.7,
            policy_id=policy.id, policy_version=policy.version, user_accepted=False,
            notes=policy.description,
        )
        geom["ray_origin"] = geom["rayOrigin"] = origin
        geom["ray_direction"] = geom["rayDirection"] = direction
        book_ir.parameters["ray_origin"] = PhysicalValue(
            value=origin, unit="px", status="assumed", provenance=provenance,
        )
        book_ir.parameter_provenance["ray_origin"] = provenance
        result.assumptions.append({"parameter": "ray_origin", "policyId": policy.id,
                                   "policyVersion": policy.version, "value": origin,
                                   "unit": "px", "reason": policy.description,
                                   "derivedFrom": prism.evidence_refs,
                                   "provenance": "auto_policy", "confidence": 0.7})

    @staticmethod
    def _normalize_lens_focal_length(book_ir: BookIR, result: AutoResolutionResult) -> None:
        if book_ir.parameters.get("focal_length_px") is not None:
            return
        aperture = book_ir.parameters.get("aperture_height_px")
        provenance = getattr(aperture, "provenance", None)
        policy = PolicyRegistry.get_policy("policy_normalized_lens_focal_ratio")
        if not provenance or provenance.source != "diagram_measurement" or policy is None:
            return
        try:
            height = float(aperture.value)
        except (TypeError, ValueError):
            return
        if not math.isfinite(height) or height < 10:
            return
        focal = height * float(policy.value)
        assumed = ProvenanceRecord(
            source="auto_policy", evidence_refs=provenance.evidence_refs,
            confidence=0.7, policy_id=policy.id, policy_version=policy.version,
            user_accepted=False, notes=policy.description,
        )
        book_ir.parameters["focal_length_px"] = PhysicalValue(
            value=focal, unit="px", status="assumed", provenance=assumed,
        )
        book_ir.parameter_provenance["focal_length_px"] = assumed
        result.assumptions.append({"parameter": "focal_length_px", "policyId": policy.id,
                                   "policyVersion": policy.version, "value": focal, "unit": "px",
                                   "reason": policy.description, "provenance": "auto_policy",
                                   "derivedFrom": provenance.evidence_refs, "confidence": 0.7})

    @staticmethod
    def _derive_refraction_angle(book_ir: BookIR, result: AutoResolutionResult) -> None:
        params = book_ir.parameters or {}
        if params.get("incident_angle") is not None or params.get("theta1") is not None:
            return
        names = ("n1", "n2", "refracted_angle")
        if any(params.get(name) is None for name in names):
            return
        values = []
        refs = []
        for name in names:
            raw = params[name]
            evidence = getattr(raw, "provenance", None) or (book_ir.parameter_provenance or {}).get(name)
            if not evidence or evidence.source not in {"ocr", "diagram_measurement", "derived"}:
                return
            try:
                value = float(getattr(raw, "value", raw))
            except (TypeError, ValueError):
                return
            if not math.isfinite(value):
                return
            values.append(value)
            refs.extend(evidence.evidence_refs)
        n1, n2, refracted_deg = values
        if n1 <= 0 or n2 <= 0 or not 0 <= refracted_deg < 90:
            return
        sine = n2 * math.sin(math.radians(refracted_deg)) / n1
        if not 0 <= sine <= 1:
            result.failures.append({"code": "PHYSICS_INCONSISTENT", "message": "Observed refracted angle and indices violate Snell's law."})
            return
        provenance = ProvenanceRecord(
            source="derived", evidence_refs=list(dict.fromkeys(refs)), confidence=0.75,
            notes="Incident angle derived from observed refracted angle and refractive indices using Snell's law.",
        )
        book_ir.parameters["incident_angle"] = PhysicalValue(
            value=math.degrees(math.asin(sine)), unit="deg", status="derived", provenance=provenance,
        )
        book_ir.parameter_provenance["incident_angle"] = provenance

    @staticmethod
    def _normalize_grounded_circuit(book_ir: BookIR, result: AutoResolutionResult) -> None:
        topology = (book_ir.geometry or {}).get("circuit_topology") or {}
        components = (book_ir.parameters or {}).get("components")
        nodes = (book_ir.parameters or {}).get("nodes")
        if (topology.get("verified_connectivity") is not True
                or not isinstance(components, list) or not isinstance(nodes, list)
                or any(entity.type in {"switch", "open_switch", "closed_switch"}
                       for entity in book_ir.entities)):
            result.failures.append({"code": "TOPOLOGY_INVALID", "message": "Circuit continuity is not grounded."})
            return
        node_ids = {n if isinstance(n, str) else n.get("id") for n in nodes if isinstance(n, (str, dict))}
        sources = {"voltage_source", "battery", "dc_source"}
        if not any(isinstance(comp, dict) and comp.get("type") in sources for comp in components):
            result.failures.append({"code": "TOPOLOGY_INVALID", "message": "No detected voltage source."})
            return
        for comp in components:
            if not isinstance(comp, dict):
                result.failures.append({"code": "TOPOLOGY_INVALID", "message": "Invalid component."})
                return
            terminals = comp.get("nodes")
            center = (comp.get("geometry") or {}).get("center_source_px")
            if (not isinstance(terminals, list) or len(terminals) != 2
                    or any(node not in node_ids for node in terminals)
                    or (comp.get("type") in sources and terminals[0] == terminals[1])
                    or not isinstance(center, (list, tuple)) or len(center) != 2
                    or not _inside_source({"x": center[0], "y": center[1]},
                                          book_ir.geometry["width"], book_ir.geometry["height"])):
                result.failures.append({"code": "TOPOLOGY_INVALID", "message": f"Unverified terminals for {comp.get('id')}."})
                return
        for comp in components:
            if comp.get("value") is not None:
                continue
            ctype = comp.get("type")
            policy_id = ("policy_standard_dc_voltage" if ctype in sources
                         else "policy_standard_dc_resistance" if ctype in {"resistor", "bulb", "lamp"}
                         else None)
            policy = PolicyRegistry.get_policy(policy_id) if policy_id else None
            if policy is None:
                continue
            comp["value"] = policy.value
            comp["unit"] = "V" if ctype in sources else "ohm"
            comp["provenance"] = {"source": "auto_policy", "policyId": policy.id,
                                  "policyVersion": policy.version, "confidence": 0.8}
            book_ir.parameter_provenance[comp["id"]] = ProvenanceRecord(
                source="auto_policy", confidence=0.8,
                policy_id=policy.id, policy_version=policy.version,
                user_accepted=False,
                notes=f"Normalized circuit model value: {policy.description}",
            )
            result.assumptions.append({"parameter": comp.get("id"), "policyId": policy.id,
                                       "policyVersion": policy.version, "value": policy.value,
                                       "unit": comp["unit"], "reason": policy.description,
                                       "provenance": "auto_policy", "confidence": 0.8})

    @classmethod
    def resolve(cls, book_ir: BookIR) -> AutoResolutionResult:
        result = AutoResolutionResult(book_ir=book_ir)
        subtype = book_ir.subtype
        spec = RequirementRegistry.get_spec(subtype, book_ir.domain)
        if not spec or spec.domain != book_ir.domain or book_ir.isPhysics is False:
            result.failures.append({"code": "CLASSIFICATION_FAILED", "message": "No supported physical model was identified."})
            result.readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
            return result

        geom = book_ir.geometry or {}
        width, height = geom.get("width"), geom.get("height")
        if (not isinstance(width, (int, float)) or not isinstance(height, (int, float))
                or not math.isfinite(width) or not math.isfinite(height)
                or width <= 0 or height <= 0):
            result.failures.append({"code": "REGISTRATION_MISMATCH", "message": "Native source dimensions are missing or invalid."})
            result.readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
            book_ir.status = BookIRStatus.NEEDS_REVIEW
            return result
        # A semantic VLM classification alone is insufficient to authorize a
        # source-aligned simulation. The required points must come from CV.
        if subtype == "prism":
            cls._normalize_prism_ray(book_ir, result)
        missing = [key for key in spec.required_geometry if _grounded_value(book_ir, key) is None]
        if missing:
            result.failures.append({"code": "GEOMETRY_NOT_FOUND", "message": ", ".join(missing)})
            result.readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
            book_ir.status = BookIRStatus.NEEDS_REVIEW
            return result
        invalid_points = [key for key in _POINT_LANDMARKS.get(subtype, ())
                          if not _inside_source(_grounded_value(book_ir, key), width, height)]
        if subtype == "prism" and (not isinstance(geom.get("vertices"), list)
                                    or len(geom["vertices"]) < 3
                                    or any(not _inside_source(p, width, height) for p in geom["vertices"])):
            invalid_points.append("vertices")
        if invalid_points:
            result.failures.append({"code": "REGISTRATION_MISMATCH", "message": ", ".join(invalid_points)})
            result.readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
            book_ir.status = BookIRStatus.NEEDS_REVIEW
            return result

        if subtype == "dc_linear":
            cls._normalize_grounded_circuit(book_ir, result)
            book_ir.assumptions.extend(result.assumptions)
            result.readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
            if result.failures:
                book_ir.status = BookIRStatus.NEEDS_REVIEW
            return result

        if subtype == "interface_refraction":
            cls._derive_refraction_angle(book_ir, result)
        elif subtype == "thin_lens":
            cls._normalize_lens_focal_length(book_ir, result)
            cls._normalize_lens_exploration_object(book_ir, result)
        elif subtype == "spherical_mirror":
            cls._normalize_mirror_exploration_object(book_ir, result)

        for policy_id in _AUTO_POLICIES.get(subtype, ()):
            policy = PolicyRegistry.get_policy(policy_id)
            if not policy or policy_id not in spec.allowed_policies:
                continue
            parameter = policy.target_parameter
            if parameter in (book_ir.parameters or {}) or parameter in (book_ir.resolutions or {}):
                continue
            decision = ResolutionDecision(
                id=f"auto_{policy_id}",
                parameter_name=parameter,
                target_subtype=subtype,
                resolution_source=ResolutionSource.POLICY_DEFAULT,
                resolved_value=policy.value,
                canonical_unit=policy.unit,
                original_entered_value=str(policy.value),
                original_unit=policy.unit,
                policy_id=policy.id,
                policy_version=policy.version,
                user_accepted=False,
                notes=f"Automatic model assumption: {policy.description}",
                resolved_by="auto_policy",
            )
            applied = ResolutionEngine.apply_resolution(book_ir, decision)
            if applied.success:
                result.assumptions.append({
                    "parameter": parameter,
                    "policyId": policy.id,
                    "policyVersion": policy.version,
                    "value": policy.value,
                    "unit": policy.unit,
                    "reason": policy.description,
                    "provenance": "auto_policy",
                    "confidence": 0.8,
                })
            else:
                result.failures.append({"code": "AUTO_RESOLUTION_FAILED", "message": applied.error or policy.id})

        book_ir.assumptions.extend(result.assumptions)
        result.readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
        return result

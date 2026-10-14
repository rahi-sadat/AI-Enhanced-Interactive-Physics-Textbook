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
from ai.resolution.assumptions import assumption_metadata, automatic_visual_blockers, MATERIAL_ASSUMPTIONS
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
        "policy_standard_ball_radius",
        "policy_standard_projectile_scale",
        "policy_standard_projectile_speed",
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
        metadata = assumption_metadata(policy.id)
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
                                   "derivedFrom": provenance.evidence_refs, "confidence": 0.7,
                                   **metadata})

    @staticmethod
    def _normalize_lens_exploration_object(book_ir: BookIR, result: AutoResolutionResult) -> None:
        params = book_ir.parameters
        center = (book_ir.geometry or {}).get("lens_center") or {}
        cx = center.get("x", 0)

        # 1. If objectDistance is already resolved, nothing more to do
        if params.get("objectDistance") is not None:
            return

        # 2. Derive objectDistance from grounded object_position if available
        if params.get("object_position") is not None:
            pos = params["object_position"]
            pos_x = pos.get("x", 0) if isinstance(pos, dict) else getattr(pos, "x", 0)
            if cx > 0 and pos_x > 0:
                dist = abs(cx - pos_x)
                prov = ProvenanceRecord(source="diagram_measurement", confidence=0.88)
                params["objectDistance"] = PhysicalValue(value=dist, unit="px", status="derived", provenance=prov)
                book_ir.parameter_provenance["objectDistance"] = prov
                return

        # 3. Check if any entity has grounded coordinates
        for entity in (book_ir.entities or []):
            if (entity.type or "").lower() in ("object", "arrow", "object_arrow"):
                pos_x = None
                if entity.position_source_px and "x" in entity.position_source_px:
                    pos_x = entity.position_source_px["x"]
                elif entity.geometry and "start" in entity.geometry:
                    pos_x = entity.geometry["start"]["x"]
                if pos_x is not None and cx > 0:
                    dist = abs(cx - pos_x)
                    if dist > 5:
                        prov = ProvenanceRecord(source="diagram_measurement", confidence=0.85)
                        params["objectDistance"] = PhysicalValue(value=dist, unit="px", status="derived", provenance=prov)
                        book_ir.parameter_provenance["objectDistance"] = prov
                        if params.get("object_height_px") is None and entity.geometry and "height_px" in entity.geometry:
                            params["object_height_px"] = PhysicalValue(value=entity.geometry["height_px"], unit="px", status="derived", provenance=prov)
                            book_ir.parameter_provenance["object_height_px"] = prov
                        return

        focal = params.get("focal_length_px")
        aperture = params.get("aperture_height_px")
        width = (book_ir.geometry or {}).get("width", 1000)
        height = (book_ir.geometry or {}).get("height", 800)
        if not _inside_source(center, width, height):
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
        distance = min(focal_px * float(policy_distance.value), cx * 0.8)
        obj_h = aperture_px * float(policy_height.value)
        if distance <= 1 or obj_h <= 1:
            return
        for name, value, policy, refs in (
            ("objectDistance", distance, policy_distance, focal.provenance.evidence_refs),
            ("object_height_px", height, policy_height, aperture.provenance.evidence_refs),
        ):
            metadata = assumption_metadata(policy.id)
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
                                       "confidence": 0.7, **metadata})

    @staticmethod
    def _normalize_mirror_exploration_object(book_ir: BookIR, result: AutoResolutionResult) -> None:
        params = book_ir.parameters
        if params.get("object_position") is not None or params.get("objectDistance") is not None:
            return
        for entity in (book_ir.entities or []):
            if (entity.type or "").lower() in ("object", "arrow", "object_arrow"):
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
            metadata = assumption_metadata(policy.id)
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
                                       "confidence": 0.7, **metadata})

    @staticmethod
    def _normalize_projectile_scene(book_ir: BookIR, result: AutoResolutionResult) -> None:
        params = book_ir.parameters = book_ir.parameters or {}
        geom = book_ir.geometry = book_ir.geometry or {}
        prov_map = book_ir.parameter_provenance = book_ir.parameter_provenance or {}

        # 1. Launch Position
        launch_pt = None
        raw_pt = _grounded_value(book_ir, "launch_position")
        if raw_pt and isinstance(raw_pt, dict) and "x" in raw_pt and "y" in raw_pt:
            launch_pt = raw_pt
        elif geom.get("launch_point"):
            lp = geom["launch_point"]
            launch_pt = {"x": lp.x if hasattr(lp, "x") else lp["x"], "y": lp.y if hasattr(lp, "y") else lp["y"]}
        elif geom.get("launch_origin"):
            launch_pt = geom["launch_origin"]

        if launch_pt:
            if "launch_position" not in params:
                prov = ProvenanceRecord(source="diagram_measurement", confidence=0.90)
                params["launch_position"] = PhysicalValue(value=launch_pt, unit="px", status="observed", provenance=prov)
                prov_map["launch_position"] = prov
            geom["launch_position"] = launch_pt
            geom["launch_source_px"] = launch_pt

        # 2. Ball Radius
        if params.get("ball_radius_px") is None:
            r_val = float(geom.get("ball_radius_px") or geom.get("radius_source_px") or 15.0)
            prov = ProvenanceRecord(source="diagram_measurement", confidence=0.85)
            params["ball_radius_px"] = PhysicalValue(value=r_val, unit="px", status="observed", provenance=prov)
            prov_map["ball_radius_px"] = prov

        # 3. Launch Angle
        angle_deg = None
        raw_ang = params.get("launch_angle_deg") or params.get("launch_angle") or params.get("angle")
        if raw_ang is not None:
            try:
                angle_deg = float(getattr(raw_ang, "value", raw_ang))
            except (ValueError, TypeError):
                angle_deg = None

        if angle_deg is None:
            # Check velocity vector entity or geometry
            vel_ent = next((e for e in (book_ir.entities or []) if e.type in ("velocity_vector", "launch_velocity")), None)
            vel_geom = (vel_ent.geometry if vel_ent else None) or geom.get("velocity_vector")
            if vel_geom and isinstance(vel_geom, dict):
                s = vel_geom.get("start")
                e = vel_geom.get("end")
                if s and e:
                    sx = s.get("x", s.x if hasattr(s, "x") else 0)
                    sy = s.get("y", s.y if hasattr(s, "y") else 0)
                    ex = e.get("x", e.x if hasattr(e, "x") else 0)
                    ey = e.get("y", e.y if hasattr(e, "y") else 0)
                    dx = ex - sx
                    dy = ey - sy
                    if abs(dx) > 1e-3 or abs(dy) > 1e-3:
                        # Image coordinates: dy < 0 is upward
                        ang = -math.degrees(math.atan2(dy, dx))
                        if 0 <= ang <= 90:
                            angle_deg = ang

            # If still None, check apex/range
            if angle_deg is None:
                h_px = float(geom.get("measured_height_px") or geom.get("max_height_px") or 0.0)
                r_px = float(geom.get("measured_range_px") or geom.get("range_px") or 0.0)
                if h_px > 10.0 and r_px > 20.0:
                    # tan(theta) = 4 * H / R
                    tan_theta = (4.0 * h_px) / r_px
                    angle_deg = math.degrees(math.atan(tan_theta))
                else:
                    angle_deg = 45.0

            prov_ang = ProvenanceRecord(source="diagram_measurement", confidence=0.85, notes="Derived from trajectory / vector geometry.")
            params["launch_angle_deg"] = PhysicalValue(value=angle_deg, unit="deg", status="derived", provenance=prov_ang)
            params["launch_angle"] = params["launch_angle_deg"]
            prov_map["launch_angle_deg"] = prov_ang
            prov_map["launch_angle"] = prov_ang

        # 4. Gravity
        g_val = 9.80665
        raw_g = params.get("gravity")
        if raw_g is not None:
            try:
                g_val = float(getattr(raw_g, "value", raw_g))
            except (ValueError, TypeError):
                g_val = 9.80665
        else:
            policy_g = PolicyRegistry.get_policy("policy_earth_gravity")
            if policy_g:
                g_val = float(policy_g.value)
                prov_g = ProvenanceRecord(source="auto_policy", confidence=0.8, policy_id=policy_g.id, policy_version=policy_g.version, notes=policy_g.description)
                params["gravity"] = PhysicalValue(value=g_val, unit="m/s²", status="assumed", provenance=prov_g)
                prov_map["gravity"] = prov_g

        # 5. Launch Speed & Calibration (pixels_per_meter)
        theta_rad = math.radians(angle_deg if angle_deg is not None else 45.0)
        sin_theta = math.sin(theta_rad)
        sin_2theta = math.sin(2.0 * theta_rad)
        h_px = float(geom.get("measured_height_px") or geom.get("max_height_px") or 0.0)
        r_px = float(geom.get("measured_range_px") or geom.get("range_px") or 0.0)

        raw_speed = params.get("launch_speed")
        v0 = None
        if raw_speed is not None:
            try:
                v0 = float(getattr(raw_speed, "value", raw_speed))
            except (ValueError, TypeError):
                v0 = None

        if v0 is None:
            # Normalized visual velocity: 15 m/s
            v0 = 15.0
            prov_v0 = ProvenanceRecord(source="diagram_measurement", confidence=0.80, notes="Normalized visual velocity for trajectory simulation.")
            params["launch_speed"] = PhysicalValue(value=v0, unit="m/s", status="derived", provenance=prov_v0)
            prov_map["launch_speed"] = prov_v0

        raw_ppm = params.get("pixels_per_meter") or geom.get("pixels_per_meter")
        ppm = None
        if raw_ppm is not None:
            try:
                ppm = float(getattr(raw_ppm, "value", raw_ppm))
            except (ValueError, TypeError):
                ppm = None

        if ppm is None or ppm <= 0:
            if h_px > 10.0 and sin_theta > 0.05:
                # Hm = (v0 * sin(theta))^2 / (2 * g)
                h_m = (v0 * sin_theta) ** 2 / (2.0 * g_val)
                if h_m > 0.01:
                    ppm = h_px / h_m
            elif r_px > 20.0 and sin_2theta > 0.05:
                # Rm = v0^2 * sin(2*theta) / g
                r_m = (v0 ** 2 * sin_2theta) / g_val
                if r_m > 0.01:
                    ppm = r_px / r_m
            else:
                ppm = 25.0

            prov_ppm = ProvenanceRecord(source="diagram_measurement", confidence=0.85, notes="Derived scale matching printed trajectory.")
            params["pixels_per_meter"] = PhysicalValue(value=ppm, unit="px/m", status="derived", provenance=prov_ppm)
            prov_map["pixels_per_meter"] = prov_ppm
            geom["pixels_per_meter"] = ppm

    @staticmethod
    def _normalize_prism_scene(book_ir: BookIR, result: AutoResolutionResult) -> None:
        params = book_ir.parameters = book_ir.parameters or {}
        geom = book_ir.geometry = book_ir.geometry or {}
        prov_map = book_ir.parameter_provenance = book_ir.parameter_provenance or {}

        pts = geom.get("vertices") or []
        if len(pts) >= 3 and params.get("apex_angle_deg") is None:
            sorted_pts = sorted(pts, key=lambda p: p["y"] if isinstance(p, dict) else p.y)
            apex_pt = sorted_pts[0]
            base_pts = sorted_pts[1:]
            base_pts.sort(key=lambda p: p["x"] if isinstance(p, dict) else p.x)
            left_pt, right_pt = base_pts[0], base_pts[1]

            ax, ay = (apex_pt["x"], apex_pt["y"]) if isinstance(apex_pt, dict) else (apex_pt.x, apex_pt.y)
            lx, ly = (left_pt["x"], left_pt["y"]) if isinstance(left_pt, dict) else (left_pt.x, left_pt.y)
            rx, ry = (right_pt["x"], right_pt["y"]) if isinstance(right_pt, dict) else (right_pt.x, right_pt.y)

            v1 = (lx - ax, ly - ay)
            v2 = (rx - ax, ry - ay)
            len1 = math.hypot(v1[0], v1[1])
            len2 = math.hypot(v2[0], v2[1])
            if len1 > 0 and len2 > 0:
                cos_a = (v1[0] * v2[0] + v1[1] * v2[1]) / (len1 * len2)
                cos_a = max(-1.0, min(1.0, cos_a))
                apex_angle = math.degrees(math.acos(cos_a))
                prov = ProvenanceRecord(source="diagram_measurement", confidence=0.88, notes="Apex angle measured from prism polygon geometry.")
                params["apex_angle_deg"] = PhysicalValue(value=apex_angle, unit="deg", status="derived", provenance=prov)
                params["apex_angle"] = params["apex_angle_deg"]
                prov_map["apex_angle_deg"] = prov
                prov_map["apex_angle"] = prov

        if params.get("n") is None and params.get("refractive_index") is None:
            policy_n = PolicyRegistry.get_policy("policy_crown_glass_refractive_index")
            if policy_n:
                prov = ProvenanceRecord(source="auto_policy", confidence=0.8, policy_id=policy_n.id, policy_version=policy_n.version, notes=policy_n.description)
                params["n"] = PhysicalValue(value=float(policy_n.value), unit=None, status="assumed", provenance=prov)
                prov_map["n"] = prov

        if geom.get("ray_origin") is None or geom.get("ray_direction") is None:
            if len(pts) >= 3:
                sorted_pts = sorted(pts, key=lambda p: p["y"] if isinstance(p, dict) else p.y)
                apex_pt = sorted_pts[0]
                base_pts = sorted_pts[1:]
                base_pts.sort(key=lambda p: p["x"] if isinstance(p, dict) else p.x)
                left_pt = base_pts[0]

                ax, ay = (apex_pt["x"], apex_pt["y"]) if isinstance(apex_pt, dict) else (apex_pt.x, apex_pt.y)
                lx, ly = (left_pt["x"], left_pt["y"]) if isinstance(left_pt, dict) else (left_pt.x, left_pt.y)

                mid_x = (ax + lx) / 2.0
                mid_y = (ay + ly) / 2.0
                orig_x = max(10.0, mid_x - 100.0)
                orig_y = mid_y

                ray_orig = {"x": orig_x, "y": orig_y}
                ray_dir = {"x": 1.0, "y": 0.0}

                geom["ray_origin"] = ray_orig
                geom["rayOrigin"] = ray_orig
                geom["ray_direction"] = ray_dir
                geom["rayDirection"] = ray_dir

                policy_ray = PolicyRegistry.get_policy("policy_normalized_prism_incident_ray")
                prov = ProvenanceRecord(source="auto_policy", confidence=0.7, policy_id=policy_ray.id if policy_ray else None, notes="Normalized horizontal incident ray on left prism face.")
                params["ray_origin"] = PhysicalValue(value=ray_orig, unit="px", status="assumed", provenance=prov)
                params["ray_direction"] = PhysicalValue(value=ray_dir, unit=None, status="assumed", provenance=prov)
                prov_map["ray_origin"] = prov
                prov_map["ray_direction"] = prov

    @staticmethod
    def _normalize_grounded_circuit(book_ir: BookIR, result: AutoResolutionResult) -> None:
        topology = (book_ir.geometry or {}).get("circuit_topology") or {}
        components = (book_ir.parameters or {}).get("components")
        nodes = (book_ir.parameters or {}).get("nodes")
        if (topology.get("verified_connectivity") is not True
                or not isinstance(components, list) or not isinstance(nodes, list)):
            result.failures.append({"code": "TOPOLOGY_INVALID", "message": "Circuit continuity is not grounded."})
            return

        unverified_switches = []
        for entity in book_ir.entities:
            if entity.type in {"switch", "open_switch", "closed_switch"}:
                comp = next((c for c in components if c.get("id") == entity.id or c.get("type") in {"switch", "open_switch", "closed_switch"}), None)
                if not comp or not comp.get("nodes") or len(comp.get("nodes", [])) != 2:
                    unverified_switches.append(entity.id)
        if unverified_switches:
            result.failures.append({"code": "TOPOLOGY_INVALID", "message": f"Circuit continuity is not grounded for switches: {', '.join(unverified_switches)}."})
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
            if ctype in {"switch", "open_switch", "closed_switch"}:
                is_closed = comp.get("closed", ctype == "closed_switch" or comp.get("state") == "closed")
                comp["state"] = "closed" if is_closed else "open"
                comp["value"] = 0.001 if is_closed else 1e9
                comp["unit"] = "ohm"
                comp["provenance"] = {"source": "auto_policy", "confidence": 0.8}
                book_ir.parameter_provenance[comp["id"]] = ProvenanceRecord(
                    source="auto_policy", confidence=0.8,
                    user_accepted=False,
                    notes=f"Switch state: {comp['state']}",
                )
                result.assumptions.append({"parameter": comp.get("id"), "value": comp["value"],
                                           "unit": "ohm", "reason": f"Switch state: {comp['state']}",
                                           "provenance": "auto_policy", "confidence": 0.8})
                continue
            policy_id = ("policy_standard_dc_voltage" if ctype in sources
                         else "policy_standard_dc_resistance" if ctype in {"resistor", "bulb", "lamp"}
                         else None)
            policy = PolicyRegistry.get_policy(policy_id) if policy_id else None
            if policy is None:
                continue
            comp["value"] = policy.value
            comp["unit"] = "V" if ctype in sources else "ohm"
            metadata = assumption_metadata(policy.id)
            comp["provenance"] = {"source": "auto_policy", "policyId": policy.id,
                                  "policyVersion": policy.version, "confidence": 0.8,
                                  "assumptionSource": metadata["source"]}
            book_ir.parameter_provenance[comp["id"]] = ProvenanceRecord(
                source="auto_policy", confidence=0.8,
                policy_id=policy.id, policy_version=policy.version,
                user_accepted=False,
                notes=f"Normalized circuit model value: {policy.description}",
            )
            result.assumptions.append({"parameter": comp.get("id"), "policyId": policy.id,
                                       "policyVersion": policy.version, "value": policy.value,
                                       "unit": comp["unit"], "reason": policy.description,
                                       "provenance": "auto_policy", "confidence": 0.8, **metadata})

    @classmethod
    def resolve(cls, book_ir: BookIR, *, allowed_material_policies=()) -> AutoResolutionResult:
        """Fill permitted model quantities, never invent source visual geometry.

        Material policies require explicit caller authorization. This is not
        human confirmation, source evidence, or a visual-readiness promotion.
        """
        if isinstance(allowed_material_policies, str) or not isinstance(allowed_material_policies, (list, tuple, set, frozenset)):
            raise ValueError("allowed_material_policies must be a collection of named material policies")
        if any(policy not in MATERIAL_ASSUMPTIONS for policy in allowed_material_policies):
            raise ValueError("Only named material policies may be explicitly allowed")
        result = AutoResolutionResult(book_ir=book_ir)
        stale = automatic_visual_blockers(book_ir)
        if stale:
            result.failures.extend({"code": "VISUAL_ASSUMPTION_REQUIRES_REVIEW", "message": message} for message in stale)
            result.readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
            return result
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
        if subtype == "interface_refraction":
            cls._derive_refraction_angle(book_ir, result)
        elif subtype == "thin_lens":
            cls._normalize_lens_focal_length(book_ir, result)
            cls._normalize_lens_exploration_object(book_ir, result)
        elif subtype == "spherical_mirror":
            cls._normalize_mirror_exploration_object(book_ir, result)
        elif subtype == "projectile":
            cls._normalize_projectile_scene(book_ir, result)
        elif subtype == "prism":
            cls._normalize_prism_scene(book_ir, result)

        # A semantic VLM classification alone is insufficient to authorize a
        # source-aligned simulation. The required points must come from CV.
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

        for policy_id in _AUTO_POLICIES.get(subtype, ()):
            if policy_id in MATERIAL_ASSUMPTIONS and policy_id not in allowed_material_policies:
                continue
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
                metadata = assumption_metadata(policy.id)
                book_ir.parameter_provenance[parameter].source = "auto_policy"
                result.assumptions.append({
                    "parameter": parameter,
                    "policyId": policy.id,
                    "policyVersion": policy.version,
                    "value": policy.value,
                    "unit": policy.unit,
                    "reason": policy.description,
                    "provenance": "auto_policy",
                    "confidence": 0.8,
                    **metadata,
                })
            else:
                result.failures.append({"code": "AUTO_RESOLUTION_FAILED", "message": applied.error or policy.id})

        book_ir.assumptions.extend(result.assumptions)
        result.readiness = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)
        return result

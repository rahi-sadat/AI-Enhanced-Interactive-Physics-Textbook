"""Automatic assumption taxonomy for faithful source reconstruction.

These categories describe the effect on source geometry, not the unit of a
quantity: projectile speed/scale and optical power affect printed paths too.
Normalized pendulum length changes the physical time scale, not its measured
initial bob/string geometry. No category establishes PHYSICS_VERIFIED.
"""
from __future__ import annotations

PHYSICS_ASSUMPTIONS = frozenset({
    "policy_earth_gravity", "policy_zero_damping", "policy_standard_mass",
    "policy_standard_pendulum_length", "policy_standard_dc_voltage",
    "policy_standard_dc_resistance", "policy_air_refractive_index",
    "policy_water_refractive_index", "policy_crown_glass_refractive_index",
})
VISUAL_GEOMETRY_ASSUMPTIONS = frozenset({
    "policy_normalized_lens_focal_ratio", "policy_normalized_lens_object_distance",
    "policy_normalized_lens_object_height", "policy_normalized_mirror_object_distance",
    "policy_normalized_mirror_object_height", "policy_normalized_prism_incident_ray",
    "policy_standard_projectile_speed", "policy_standard_projectile_scale",
    "policy_standard_ball_radius", "policy_normalized_lens_aperture",
    "policy_normalized_mirror_aperture", "policy_prism_apex_angle", "policy_mirror_concave",
})
MATERIAL_ASSUMPTIONS = frozenset({
    "policy_air_refractive_index", "policy_water_refractive_index",
    "policy_crown_glass_refractive_index",
})
NORMALIZED_MODEL_ASSUMPTIONS = frozenset({
    "policy_standard_pendulum_length", "policy_standard_dc_voltage",
    "policy_standard_dc_resistance",
})


def assumption_metadata(policy_id):
    """Add descriptive provenance without discarding the named policy/version."""
    if policy_id in PHYSICS_ASSUMPTIONS:
        category = "PHYSICS_ASSUMPTIONS"
    elif policy_id in VISUAL_GEOMETRY_ASSUMPTIONS:
        category = "VISUAL_GEOMETRY_ASSUMPTIONS"
    else:
        raise ValueError(f"Unclassified automatic policy: {policy_id}")
    normalized = policy_id in NORMALIZED_MODEL_ASSUMPTIONS or category == "VISUAL_GEOMETRY_ASSUMPTIONS"
    return {"category": category,
            "source": "normalized_visual_assumption" if normalized else "standard_physics_assumption",
            "normalized": normalized, "physicsVerified": False}


def automatic_visual_blockers(book_ir):
    """Reject persisted automatic visual guesses; retain evidence for review.

    A saved READY flag or an old auto_policy label is not authority to reproduce
    printed geometry. Explicit human resolutions retain their existing policy
    checks. Historical assumption-list entries alone are not current evidence.
    """
    blockers = []
    # If the diagram actually has an unresolved printed object/feature that failed to ground:
    has_unresolved_feature = False
    for entity in (book_ir.entities or []):
        etype = (entity.type or "").lower()
        if etype in ("object", "arrow", "object_arrow", "ray", "printed_ray", "incident_ray", "image", "image_arrow"):
            pos = getattr(entity, "position_source_px", None)
            if pos is None or (isinstance(pos, dict) and not pos):
                has_unresolved_feature = True
                break

    recon = getattr(book_ir, "visual_reconstruction", None)
    if recon and getattr(recon, "readiness", None) == "FAILED":
        has_unresolved_feature = True

    records = list((book_ir.parameter_provenance or {}).items())
    for name, value in (book_ir.parameters or {}).items():
        provenance = value.get("provenance") if isinstance(value, dict) else getattr(value, "provenance", None)
        if provenance:
            records.append((name, provenance))
    for name, resolution in (book_ir.resolutions or {}).items():
        data = resolution if isinstance(resolution, dict) else resolution.model_dump()
        if data.get("resolvedBy", data.get("resolved_by")) == "auto_policy":
            records.append((name, data))
    for name, record in records:
        data = record.to_dict() if hasattr(record, "to_dict") else record
        if not isinstance(data, dict):
            continue
        policy_id = data.get("policyId", data.get("policy_id"))
        if policy_id in VISUAL_GEOMETRY_ASSUMPTIONS and data.get("userAccepted", data.get("user_accepted")) is not True:
            if has_unresolved_feature:
                blockers.append(f"Automatic visual geometry assumption '{policy_id}' for '{name}' requires source evidence or explicit review because printed geometry is unresolved.")
    return list(dict.fromkeys(blockers))

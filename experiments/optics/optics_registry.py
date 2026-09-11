"""
experiments/optics/optics_registry.py
Semantic preset registry for optical elements in AugmentedPhysics.
Defines entity mappings, physics models, and default author roles.
"""

OPTICS_REGISTRY = {
    "convex_lens": {
        "physics_type": "thin_lens",
        "default_role": "static",
        "description": "Double convex optical lens converging light towards focal point.",
        "default_params": {
            "model": "thin_lens",
            "focal_length_px": 130.0,
            "aperture_height_px": 220.0,
        },
    },
    "concave_lens": {
        "physics_type": "thin_lens",
        "default_role": "static",
        "description": "Double concave diverging lens.",
        "default_params": {
            "model": "thin_lens",
            "focal_length_px": -130.0,
            "aperture_height_px": 220.0,
        },
    },
    "prism": {
        "physics_type": "refractive_polygon",
        "default_role": "static",
        "description": "Triangular or polygonal transparent dispersive prism.",
        "default_params": {
            "refractive_index": 1.52,
        },
    },
    "concave_mirror": {
        "physics_type": "spherical_mirror",
        "default_role": "static",
        "description": "Converging spherical concave mirror.",
        "default_params": {
            "model": "concave",
            "focal_length_px": 130.0,
        },
    },
    "convex_mirror": {
        "physics_type": "spherical_mirror",
        "default_role": "static",
        "description": "Diverging spherical convex mirror.",
        "default_params": {
            "model": "convex",
            "focal_length_px": -130.0,
        },
    },
    "object_arrow": {
        "physics_type": "optical_object",
        "default_role": "dynamic",
        "description": "Interactive optical source object represented as an arrow.",
        "default_params": {
            "height_px": -90.0,
        },
    },
    "optical_object": {
        "physics_type": "optical_object",
        "default_role": "dynamic",
        "description": "General optical source object (e.g. candle, tree, arrow).",
        "default_params": {
            "height_px": -90.0,
        },
    },
    "light_source": {
        "physics_type": "ray_source",
        "default_role": "dynamic",
        "description": "Collimated or point beam light source.",
        "default_params": {
            "ray_count": 1,
            "angle_deg": 0.0,
        },
    },
    "screen": {
        "physics_type": "screen",
        "default_role": "dynamic",
        "description": "Projection screen for observing real images.",
        "default_params": {},
    },
}


def get_preset(semantic_label: str) -> dict:
    """Retrieve preset config for a given semantic label with safe fallbacks."""
    if semantic_label in OPTICS_REGISTRY:
        return OPTICS_REGISTRY[semantic_label]
    for key, val in OPTICS_REGISTRY.items():
        if key in semantic_label.lower():
            return val
    return {
        "physics_type": "generic_optic",
        "default_role": "static",
        "description": f"Custom optical element: {semantic_label}",
        "default_params": {},
    }

"""Semantic presets for optical elements.

Maps semantic labels to physics types and default authoring roles.
Mirrors the mechanics pattern where GUI buttons set 'ball' → dynamic, 'track' → static.
"""
from __future__ import annotations

from typing import Dict, Optional


OPTICS_REGISTRY: Dict[str, Dict[str, str]] = {
    # ── Lenses ──
    "convex_lens": {
        "physics_type": "thin_lens",
        "default_role": "static",
        "description": "Converging (biconvex / plano-convex) lens",
    },
    "concave_lens": {
        "physics_type": "thin_lens",
        "default_role": "static",
        "description": "Diverging (biconcave / plano-concave) lens",
    },

    # ── Prism ──
    "prism": {
        "physics_type": "refractive_polygon",
        "default_role": "static",
        "description": "Triangular glass prism for refraction / dispersion",
    },

    # ── Mirrors ──
    "concave_mirror": {
        "physics_type": "spherical_mirror",
        "default_role": "static",
        "description": "Converging spherical mirror",
    },
    "convex_mirror": {
        "physics_type": "spherical_mirror",
        "default_role": "static",
        "description": "Diverging spherical mirror",
    },
    "plane_mirror": {
        "physics_type": "plane_mirror",
        "default_role": "static",
        "description": "Flat reflective surface",
    },

    # ── Objects & Sources ──
    "object_arrow": {
        "physics_type": "optical_object",
        "default_role": "dynamic",
        "description": "Arrow representing the object placed in front of a lens / mirror",
    },
    "light_source": {
        "physics_type": "ray_source",
        "default_role": "dynamic",
        "description": "Point or parallel light source (candle, lamp, laser)",
    },

    # ── Accessories ──
    "screen": {
        "physics_type": "screen",
        "default_role": "dynamic",
        "description": "Projection screen for capturing real images",
    },
    "glass_slab": {
        "physics_type": "refractive_polygon",
        "default_role": "static",
        "description": "Rectangular glass slab for lateral displacement experiments",
    },
}

# Quick keyboard shortcut map (number key → label, default_role)
OPTICS_SHORTCUTS = {
    "1": ("convex_lens",    "static"),
    "2": ("object_arrow",   "dynamic"),
    "3": ("prism",          "static"),
    "4": ("concave_mirror", "static"),
    "5": ("screen",         "dynamic"),
    "6": ("concave_lens",   "static"),
    "7": ("convex_mirror",  "static"),
    "8": ("light_source",   "dynamic"),
}


def get_preset(label: str) -> Optional[Dict[str, str]]:
    """Look up an optical element preset by semantic label."""
    return OPTICS_REGISTRY.get(label)


def default_role(label: str) -> str:
    """Return the default authoring role for a label, or 'unknown'."""
    preset = OPTICS_REGISTRY.get(label)
    return preset["default_role"] if preset else "unknown"


def physics_type(label: str) -> Optional[str]:
    """Return the physics model type for a label."""
    preset = OPTICS_REGISTRY.get(label)
    return preset["physics_type"] if preset else None


def all_labels() -> list[str]:
    """Return all registered semantic labels."""
    return list(OPTICS_REGISTRY.keys())

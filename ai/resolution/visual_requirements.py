"""Visual-aware model requirements (Phase 4).

Requirements depend on what is actually present in the source diagram.
A model must NOT be considered visually ready merely because physics parameters
exist. For diagrams with observable visual constraints, simulated_geometry(t=0)
must match observed_source_geometry within configured error thresholds.

This module extends ModelRequirementSpec with visual reproduction requirements.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class VisualElementKind(str, Enum):
    """Kind of visual element that can be observed in a source diagram."""
    LANDMARK = "landmark"
    LINE = "line"
    CURVE = "curve"
    MASK = "mask"
    TOPOLOGY = "topology"
    TEXT_ANCHOR = "text_anchor"


@dataclass
class VisualElement:
    """A single observable visual element in a source diagram."""
    id: str
    kind: VisualElementKind
    description: str
    required_when_visible: bool = True
    # If True, this element must be reproduced at t=0
    requires_registration: bool = True
    # Provenance sources that can satisfy this element
    valid_sources: List[str] = field(default_factory=lambda: ["observed", "ocr", "derived", "inverse_fit", "user_confirmed"])


@dataclass
class VisualRequirementSpec:
    """Visual reproduction requirements for a physics model subtype.

    These define what observable elements in the source diagram must be
    detected and reproduced at t=0 for the model to be visually ready.
    Requirements are conditional: they only apply when the corresponding
    element is actually present in the source diagram.
    """
    domain: str
    subtype: str
    # Elements that MUST be reproduced when visible in source
    observable_elements: List[VisualElement] = field(default_factory=list)
    # Dynamic elements that should be extractable for animation
    dynamic_elements: List[str] = field(default_factory=list)
    # Elements that must match exactly (topology)
    exact_match_elements: List[str] = field(default_factory=list)
    notes: str = ""

    @property
    def required_element_ids(self) -> Set[str]:
        return {e.id for e in self.observable_elements if e.required_when_visible}

    @property
    def registration_element_ids(self) -> Set[str]:
        return {e.id for e in self.observable_elements if e.requires_registration}

    def get_element(self, element_id: str) -> Optional[VisualElement]:
        for e in self.observable_elements:
            if e.id == element_id:
                return e
        return None


# =============================================================================
# Per-Domain Visual Requirement Specifications
# =============================================================================

PENDULUM_VISUAL_SPEC = VisualRequirementSpec(
    domain="mechanics",
    subtype="pendulum",
    observable_elements=[
        VisualElement("pivot", VisualElementKind.LANDMARK, "Suspension pivot point"),
        VisualElement("bob_center", VisualElementKind.LANDMARK, "Center of the pendulum bob"),
        VisualElement("string", VisualElementKind.LINE, "Pendulum string from pivot to bob"),
        VisualElement("bob_mask", VisualElementKind.MASK, "Segmented bob shape",
                       required_when_visible=False),
        VisualElement("vertical_ref", VisualElementKind.LINE, "Vertical reference line",
                       required_when_visible=False, requires_registration=False),
    ],
    dynamic_elements=["bob_mask", "string"],
    notes="Bob sprite and string must visually coincide with source at t=0.",
)

PROJECTILE_VISUAL_SPEC = VisualRequirementSpec(
    domain="mechanics",
    subtype="projectile",
    observable_elements=[
        VisualElement("launch_position", VisualElementKind.LANDMARK, "Projectile launch point"),
        VisualElement("trajectory", VisualElementKind.CURVE, "Printed trajectory curve",
                       required_when_visible=True),
        VisualElement("velocity_vector", VisualElementKind.LINE, "Initial velocity vector arrow",
                       required_when_visible=False),
        VisualElement("projectile_mask", VisualElementKind.MASK, "Projectile body",
                       required_when_visible=False),
    ],
    dynamic_elements=["projectile_mask"],
    notes="Predicted trajectory must overlap printed trajectory at t=0.",
)

THIN_LENS_VISUAL_SPEC = VisualRequirementSpec(
    domain="optics",
    subtype="thin_lens",
    observable_elements=[
        VisualElement("lens_center", VisualElementKind.LANDMARK, "Optical center O"),
        VisualElement("optical_axis", VisualElementKind.LINE, "Principal optical axis"),
        VisualElement("lens_line", VisualElementKind.LINE, "Lens body/line"),
        VisualElement("object_base", VisualElementKind.LANDMARK, "Object arrow base on axis",
                       required_when_visible=True),
        VisualElement("object_tip", VisualElementKind.LANDMARK, "Object arrow tip",
                       required_when_visible=True),
        VisualElement("image_base", VisualElementKind.LANDMARK, "Image arrow base on axis",
                       required_when_visible=True),
        VisualElement("image_tip", VisualElementKind.LANDMARK, "Image arrow tip",
                       required_when_visible=True),
        VisualElement("focal_F1", VisualElementKind.LANDMARK, "Focal point F1",
                       required_when_visible=True),
        VisualElement("focal_F2", VisualElementKind.LANDMARK, "Focal point F2",
                       required_when_visible=True),
        VisualElement("ray_parallel", VisualElementKind.LINE, "Parallel principal ray",
                       required_when_visible=True),
        VisualElement("ray_focal", VisualElementKind.LINE, "Focal principal ray",
                       required_when_visible=True),
        VisualElement("ray_center", VisualElementKind.LINE, "Center principal ray",
                       required_when_visible=False),
    ],
    dynamic_elements=["object_arrow"],
    notes="Initial synthetic rays must overlap printed rays.",
)

SPHERICAL_MIRROR_VISUAL_SPEC = VisualRequirementSpec(
    domain="optics",
    subtype="spherical_mirror",
    observable_elements=[
        VisualElement("pole", VisualElementKind.LANDMARK, "Mirror pole P"),
        VisualElement("principal_axis", VisualElementKind.LINE, "Principal axis"),
        VisualElement("mirror_arc", VisualElementKind.CURVE, "Mirror curvature arc",
                       required_when_visible=False),
        VisualElement("focal_F", VisualElementKind.LANDMARK, "Focal point F",
                       required_when_visible=True),
        VisualElement("center_C", VisualElementKind.LANDMARK, "Center of curvature C",
                       required_when_visible=True),
        VisualElement("object_base", VisualElementKind.LANDMARK, "Object base",
                       required_when_visible=True),
        VisualElement("object_tip", VisualElementKind.LANDMARK, "Object tip",
                       required_when_visible=True),
        VisualElement("image_base", VisualElementKind.LANDMARK, "Image base",
                       required_when_visible=True),
        VisualElement("image_tip", VisualElementKind.LANDMARK, "Image tip",
                       required_when_visible=True),
        VisualElement("ray_parallel", VisualElementKind.LINE, "Parallel ray",
                       required_when_visible=True),
        VisualElement("ray_focal", VisualElementKind.LINE, "Focal ray",
                       required_when_visible=True),
    ],
    dynamic_elements=["object_arrow"],
    notes="Same reconstruction philosophy as thin lens.",
)

REFRACTION_VISUAL_SPEC = VisualRequirementSpec(
    domain="optics",
    subtype="interface_refraction",
    observable_elements=[
        VisualElement("boundary", VisualElementKind.LINE, "Media boundary line"),
        VisualElement("normal", VisualElementKind.LINE, "Normal to boundary at incidence point"),
        VisualElement("incidence_point", VisualElementKind.LANDMARK, "Point of incidence"),
        VisualElement("incident_ray", VisualElementKind.LINE, "Incident ray"),
        VisualElement("refracted_ray", VisualElementKind.LINE, "Refracted ray",
                       required_when_visible=True),
        VisualElement("reflected_ray", VisualElementKind.LINE, "Reflected ray",
                       required_when_visible=False),
        VisualElement("source_position", VisualElementKind.LANDMARK, "Light source position",
                       required_when_visible=False),
    ],
    dynamic_elements=[],
    notes="Snell's law cross-validates ray angles.",
)

PRISM_VISUAL_SPEC = VisualRequirementSpec(
    domain="optics",
    subtype="prism",
    observable_elements=[
        VisualElement("prism_polygon", VisualElementKind.CURVE, "Prism polygon outline"),
        VisualElement("incident_ray", VisualElementKind.LINE, "Incident ray"),
        VisualElement("entry_point", VisualElementKind.LANDMARK, "Entry point on prism face"),
        VisualElement("internal_ray", VisualElementKind.LINE, "Internal ray segment",
                       required_when_visible=True),
        VisualElement("exit_point", VisualElementKind.LANDMARK, "Exit point on prism face",
                       required_when_visible=True),
        VisualElement("emergent_ray", VisualElementKind.LINE, "Emergent ray",
                       required_when_visible=True),
    ],
    dynamic_elements=[],
    notes="Incident beam should be directly draggable.",
)

CIRCUIT_VISUAL_SPEC = VisualRequirementSpec(
    domain="circuits",
    subtype="dc_linear",
    observable_elements=[
        VisualElement("wire_skeleton", VisualElementKind.TOPOLOGY, "Wire connectivity skeleton"),
    ],
    dynamic_elements=[],
    exact_match_elements=["wire_skeleton"],
    notes="Current particles must travel on exact wire paths. Switch state must be detected.",
)


# Registry mapping (domain, subtype) -> VisualRequirementSpec
VISUAL_REQUIREMENT_REGISTRY: Dict[str, VisualRequirementSpec] = {
    "mechanics/pendulum": PENDULUM_VISUAL_SPEC,
    "mechanics/projectile": PROJECTILE_VISUAL_SPEC,
    "optics/thin_lens": THIN_LENS_VISUAL_SPEC,
    "optics/spherical_mirror": SPHERICAL_MIRROR_VISUAL_SPEC,
    "optics/interface_refraction": REFRACTION_VISUAL_SPEC,
    "optics/prism": PRISM_VISUAL_SPEC,
    "circuits/dc_linear": CIRCUIT_VISUAL_SPEC,
}


class VisualRequirementRegistry:
    """Registry for querying VisualRequirementSpec contracts."""

    @classmethod
    def get_spec(cls, subtype: Optional[str], domain: Optional[str] = None) -> Optional[VisualRequirementSpec]:
        if not subtype:
            return None
        sub = subtype.lower()
        if domain:
            key = f"{domain.lower()}/{sub}"
            if key in VISUAL_REQUIREMENT_REGISTRY:
                return VISUAL_REQUIREMENT_REGISTRY[key]
        for key, spec in VISUAL_REQUIREMENT_REGISTRY.items():
            if key.endswith(f"/{sub}"):
                return spec
        return None

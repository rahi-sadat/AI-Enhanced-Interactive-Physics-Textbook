"""PR-07 Model Requirement Specifications.

Centralized, machine-readable compiler requirements for every supported
physical subtype. Defines what parameters, geometry, units, and explicit policies
are valid and required before a model can reach READY_TO_COMPILE.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class PhysicalDimension(str, Enum):
    LENGTH = "length"
    MASS = "mass"
    TIME = "time"
    ANGLE = "angle"
    VELOCITY = "velocity"
    ACCELERATION = "acceleration"
    FREQUENCY = "frequency"
    DAMPING = "damping"
    RESISTANCE = "resistance"
    VOLTAGE = "voltage"
    CURRENT = "current"
    CAPACITANCE = "capacitance"
    INDUCTANCE = "inductance"
    REFRACTIVE_INDEX = "refractive_index"
    PIXELS = "pixels"
    PIXELS_PER_METER = "pixels_per_meter"
    POINT_2D = "point_2d"
    POLYGON_POINTS = "polygon_points"
    CATEGORICAL = "categorical"
    TOPOLOGY_NODES = "topology_nodes"
    TOPOLOGY_COMPONENTS = "topology_components"


@dataclass
class ParameterRequirement:
    """Specification of an individual parameter or geometric requirement."""
    id: str
    name: str
    dimension: PhysicalDimension
    required: bool = True
    allowed_units: List[str] = field(default_factory=list)
    canonical_unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allow_zero: bool = False
    allowed_categories: List[str] = field(default_factory=list)
    can_derive_from_geometry: bool = False
    default_policy_id: Optional[str] = None
    prompt_question: str = ""
    prompt_question_bn: Optional[str] = None
    help_text: str = ""
    is_scale_dependent: bool = False


@dataclass
class ModelRequirementSpec:
    """Complete requirement contract for a physical model subtype."""
    domain: str
    subtype: str
    required_entities: List[str] = field(default_factory=list)
    required_geometry: List[str] = field(default_factory=list)
    parameters: Dict[str, ParameterRequirement] = field(default_factory=dict)
    mutually_exclusive_requirements: List[List[str]] = field(default_factory=list)
    one_of_requirements: List[List[str]] = field(default_factory=list)
    allowed_policies: List[str] = field(default_factory=list)
    parameter_aliases: Dict[str, str] = field(default_factory=dict)
    notes: str = ""

    def canonicalize_parameter(self, param_name: str) -> str:
        """Map parameter alias or non-canonical name to canonical spec parameter name."""
        if not param_name:
            return param_name
        return self.parameter_aliases.get(param_name, param_name)

    @property
    def required_parameters(self) -> List[str]:
        return [name for name, p in self.parameters.items() if p.required]

    @property
    def optional_parameters(self) -> List[str]:
        return [name for name, p in self.parameters.items() if not p.required]

    @property
    def expected_dimensions(self) -> Dict[str, str]:
        return {name: p.dimension.value for name, p in self.parameters.items()}

    @property
    def allowed_units(self) -> Dict[str, List[str]]:
        return {name: p.allowed_units for name, p in self.parameters.items()}

    @property
    def allowed_policy_defaults(self) -> Dict[str, str]:
        return {name: p.default_policy_id for name, p in self.parameters.items() if p.default_policy_id}


# ---------------------------------------------------------------------------
# Canonical Model Specifications (Matching PhysicsCompiler.py)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Canonical Model Specifications (Matching PhysicsCompiler.py)
# ---------------------------------------------------------------------------

PENDULUM_SPEC = ModelRequirementSpec(
    domain="mechanics",
    subtype="pendulum",
    required_entities=["pivot", "bob", "string"],
    required_geometry=["pivot", "bob_center", "string_length_px", "bob_radius_px"],
    parameters={
        "pivot": ParameterRequirement(
            id="req_pendulum_pivot",
            name="pivot",
            dimension=PhysicalDimension.POINT_2D,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Pivot point coordinate in source pixels.",
            help_text="Suspension anchor point of the pendulum.",
        ),
        "bob_position": ParameterRequirement(
            id="req_pendulum_bob_position",
            name="bob_position",
            dimension=PhysicalDimension.POINT_2D,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Bob center coordinate in source pixels.",
            help_text="Center of mass of the pendulum bob.",
        ),
        "string_length_px": ParameterRequirement(
            id="req_pendulum_string_length_px",
            name="string_length_px",
            dimension=PhysicalDimension.PIXELS,
            required=True,
            canonical_unit="px",
            min_value=1.0,
            can_derive_from_geometry=True,
            prompt_question="String length in source pixels.",
        ),
        "bob_radius_px": ParameterRequirement(
            id="req_pendulum_bob_radius_px",
            name="bob_radius_px",
            dimension=PhysicalDimension.PIXELS,
            required=True,
            canonical_unit="px",
            min_value=1.0,
            can_derive_from_geometry=True,
            prompt_question="Bob radius in source pixels.",
            help_text="Visual radius of the spherical bob.",
        ),
        "gravity": ParameterRequirement(
            id="req_pendulum_gravity",
            name="gravity",
            dimension=PhysicalDimension.ACCELERATION,
            required=True,
            allowed_units=["m/s²", "m/s^2", "m/s2", "cm/s²"],
            canonical_unit="m/s²",
            min_value=0.0,
            allow_zero=True,
            default_policy_id="policy_earth_gravity",
            prompt_question="Acceleration due to gravity.",
            prompt_question_bn="অভিকর্ষজ ত্বরণ g এর মান কত?",
            help_text="Gravitational acceleration field for the pendulum.",
        ),
        "mass": ParameterRequirement(
            id="req_pendulum_mass",
            name="mass",
            dimension=PhysicalDimension.MASS,
            required=True,
            allowed_units=["kg", "g", "kilogram", "gram"],
            canonical_unit="kg",
            min_value=0.0001,
            default_policy_id="policy_standard_mass",
            prompt_question="Pendulum bob mass.",
            prompt_question_bn="ববের ভর m এর মান কত?",
            help_text="Mass of the pendulum bob (kg).",
        ),
        "damping": ParameterRequirement(
            id="req_pendulum_damping",
            name="damping",
            dimension=PhysicalDimension.DAMPING,
            required=True,
            allowed_units=["1/s", "s^-1", "s_inv", "hz"],
            canonical_unit="1/s",
            min_value=0.0,
            allow_zero=True,
            default_policy_id="policy_zero_damping",
            prompt_question="Oscillation damping coefficient.",
            prompt_question_bn="দোলনের ঘর্ষণ/স্যাঁতসেঁতে সহগ কত?",
            help_text="Air resistance damping factor (0.0 for ideal undamped oscillation).",
        ),
        "length": ParameterRequirement(
            id="req_pendulum_length",
            name="length",
            dimension=PhysicalDimension.LENGTH,
            required=True,
            allowed_units=["m", "cm", "mm", "meter", "centimeter"],
            canonical_unit="m",
            min_value=0.001,
            prompt_question="Physical pendulum string length.",
            prompt_question_bn="দোলক সুতার প্রকৃত দৈর্ঘ্য L কত?",
            help_text="Real-world length of the pendulum string.",
            is_scale_dependent=True,
        ),
        "pixels_per_meter": ParameterRequirement(
            id="req_pendulum_pixels_per_meter",
            name="pixels_per_meter",
            dimension=PhysicalDimension.PIXELS_PER_METER,
            required=False,
            canonical_unit="px/m",
            min_value=0.01,
            prompt_question="Spatial calibration scale (pixels per meter).",
            prompt_question_bn="পিক্সেল প্রতি মিটার স্কেল কত?",
            help_text="Pixel to physical meter calibration factor.",
        ),
    },
    one_of_requirements=[["length", "pixels_per_meter"]],
    allowed_policies=["policy_earth_gravity", "policy_zero_damping", "policy_standard_mass"],
    parameter_aliases={
        "bob_center": "bob_position",
        "length_m": "length",
        "string_length": "string_length_px",
        "length_px": "string_length_px",
        "gravity_m_s2": "gravity",
        "damping_s_inv": "damping",
        "mass_kg": "mass",
    },
    notes="Simple planar gravity pendulum running analytical RK4 dynamics.",
)

PROJECTILE_SPEC = ModelRequirementSpec(
    domain="mechanics",
    subtype="projectile",
    required_entities=["projectile_body"],
    required_geometry=["launch_position", "ball_radius_px"],
    parameters={
        "launch_position": ParameterRequirement(
            id="req_projectile_launch_pos",
            name="launch_position",
            dimension=PhysicalDimension.POINT_2D,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Initial launch position in source pixels.",
        ),
        "launch_speed": ParameterRequirement(
            id="req_projectile_launch_speed",
            name="launch_speed",
            dimension=PhysicalDimension.VELOCITY,
            required=True,
            allowed_units=["m/s", "km/h", "cm/s"],
            canonical_unit="m/s",
            min_value=0.0,
            allow_zero=True,
            prompt_question="Initial launch speed v₀.",
            prompt_question_bn="নিক্ষেপ বেগ v₀ এর মান কত?",
            help_text="Magnitude of initial launch velocity vector.",
        ),
        "launch_angle_deg": ParameterRequirement(
            id="req_projectile_launch_angle",
            name="launch_angle_deg",
            dimension=PhysicalDimension.ANGLE,
            required=True,
            allowed_units=["deg", "degree", "°", "rad"],
            canonical_unit="deg",
            min_value=-90.0,
            max_value=90.0,
            can_derive_from_geometry=True,
            prompt_question="Launch angle θ relative to horizontal.",
            prompt_question_bn="নিক্ষেপ কোণ θ কত ডিগ্রী?",
        ),
        "gravity": ParameterRequirement(
            id="req_projectile_gravity",
            name="gravity",
            dimension=PhysicalDimension.ACCELERATION,
            required=True,
            allowed_units=["m/s²", "m/s^2", "m/s2"],
            canonical_unit="m/s²",
            min_value=0.0,
            allow_zero=True,
            default_policy_id="policy_earth_gravity",
            prompt_question="Acceleration due to gravity.",
            prompt_question_bn="অভিকর্ষজ ত্বরণ g এর মান কত?",
        ),
        "pixels_per_meter": ParameterRequirement(
            id="req_projectile_ppm",
            name="pixels_per_meter",
            dimension=PhysicalDimension.PIXELS_PER_METER,
            required=True,
            canonical_unit="px/m",
            min_value=0.1,
            prompt_question="Calibration scale: pixels per meter.",
            prompt_question_bn="স্কেল ক্যালিব্রেশন (পিক্সেল/মিটার) কত?",
        ),
        "ball_radius_px": ParameterRequirement(
            id="req_projectile_radius",
            name="ball_radius_px",
            dimension=PhysicalDimension.PIXELS,
            required=True,
            canonical_unit="px",
            min_value=1.0,
            can_derive_from_geometry=True,
            prompt_question="Projectile radius in source pixels.",
        ),
    },
    allowed_policies=["policy_earth_gravity"],
    parameter_aliases={
        "launch_angle": "launch_angle_deg",
        "angle": "launch_angle_deg",
        "theta": "launch_angle_deg",
        "launch_pos": "launch_position",
        "launch_source": "launch_position",
        "launch_source_px": "launch_position",
        "speed": "launch_speed",
        "v0": "launch_speed",
        "gravity_m_s2": "gravity",
        "radius": "ball_radius_px",
        "radius_px": "ball_radius_px",
        "ball_radius": "ball_radius_px",
        "radius_source_px": "ball_radius_px",
        "ppm": "pixels_per_meter",
    },
    notes="Closed-form parabolic projectile trajectory simulation.",
)

THIN_LENS_SPEC = ModelRequirementSpec(
    domain="optics",
    subtype="thin_lens",
    required_entities=["lens"],
    required_geometry=["lens_center"],
    parameters={
        "lens_center": ParameterRequirement(
            id="req_lens_center",
            name="lens_center",
            dimension=PhysicalDimension.POINT_2D,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Optical center of lens (source_px).",
        ),
        "focal_length_px": ParameterRequirement(
            id="req_lens_focal_length_px",
            name="focal_length_px",
            dimension=PhysicalDimension.PIXELS,
            required=True,
            canonical_unit="px",
            min_value=1.0,
            can_derive_from_geometry=True,
            prompt_question="Focal length in source pixels.",
            prompt_question_bn="ফোকাস দূরত্ব f (পিক্সেলে) কত?",
            help_text="Distance along the principal axis from optical center to focal point F.",
        ),
        "aperture_height_px": ParameterRequirement(
            id="req_lens_aperture_height_px",
            name="aperture_height_px",
            dimension=PhysicalDimension.PIXELS,
            required=True,
            canonical_unit="px",
            min_value=10.0,
            can_derive_from_geometry=True,
            default_policy_id="policy_standard_lens_aperture",
            prompt_question="Lens aperture height in source pixels.",
            help_text="Physical vertical span of the lens element.",
        ),
        "lens_type": ParameterRequirement(
            id="req_lens_type",
            name="lens_type",
            dimension=PhysicalDimension.CATEGORICAL,
            required=False,
            allowed_categories=["convex", "concave", "converging", "diverging"],
            prompt_question="Lens curvature type.",
            prompt_question_bn="লেন্সটি উত্তল (convex) নাকি অবতল (concave)?",
        ),
    },
    allowed_policies=["policy_standard_lens_aperture"],
    parameter_aliases={
        "focal_length": "focal_length_px",
        "focalLength": "focal_length_px",
        "f": "focal_length_px",
        "aperture": "aperture_height_px",
        "aperture_height": "aperture_height_px",
        "apertureHeight": "aperture_height_px",
        "optical_center": "lens_center",
        "center": "lens_center",
    },
    notes="Gaussian 2D thin lens ray-tracing engine (1/f = 1/v - 1/u).",
)

SPHERICAL_MIRROR_SPEC = ModelRequirementSpec(
    domain="optics",
    subtype="spherical_mirror",
    required_entities=["mirror"],
    required_geometry=["pole"],
    parameters={
        "pole": ParameterRequirement(
            id="req_mirror_pole",
            name="pole",
            dimension=PhysicalDimension.POINT_2D,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Mirror vertex pole position (source_px).",
        ),
        "focal_length_px": ParameterRequirement(
            id="req_mirror_focal_length_px",
            name="focal_length_px",
            dimension=PhysicalDimension.PIXELS,
            required=True,
            canonical_unit="px",
            min_value=1.0,
            can_derive_from_geometry=True,
            prompt_question="Mirror focal length in source pixels.",
            prompt_question_bn="দর্পণের ফোকাস দূরত্ব f (পিক্সেলে) কত?",
        ),
        "concavity": ParameterRequirement(
            id="req_mirror_concavity",
            name="concavity",
            dimension=PhysicalDimension.CATEGORICAL,
            required=True,
            allowed_categories=["concave", "convex", "plane"],
            prompt_question="Mirror concavity.",
            prompt_question_bn="দর্পণটি অবতল (concave), উত্তল (convex), নাকি সমতল (plane)?",
        ),
        "aperture_height_px": ParameterRequirement(
            id="req_mirror_aperture_height_px",
            name="aperture_height_px",
            dimension=PhysicalDimension.PIXELS,
            required=True,
            canonical_unit="px",
            min_value=10.0,
            can_derive_from_geometry=True,
            default_policy_id="policy_standard_mirror_aperture",
            prompt_question="Mirror aperture height in source pixels.",
        ),
    },
    allowed_policies=["policy_standard_mirror_aperture"],
    parameter_aliases={
        "focal_length": "focal_length_px",
        "focalLength": "focal_length_px",
        "f": "focal_length_px",
        "aperture": "aperture_height_px",
        "aperture_height": "aperture_height_px",
        "mirror_type": "concavity",
        "mirrorType": "concavity",
        "vertex": "pole",
    },
    notes="Spherical concave/convex mirror reflection engine (1/f = 1/u + 1/v).",
)

INTERFACE_REFRACTION_SPEC = ModelRequirementSpec(
    domain="optics",
    subtype="interface_refraction",
    required_entities=["interface_boundary"],
    required_geometry=["boundary_y", "normal_x"],
    parameters={
        "boundary_y": ParameterRequirement(
            id="req_refraction_boundary_y",
            name="boundary_y",
            dimension=PhysicalDimension.PIXELS,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Interface horizontal boundary y position.",
        ),
        "normal_x": ParameterRequirement(
            id="req_refraction_normal_x",
            name="normal_x",
            dimension=PhysicalDimension.PIXELS,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Interface normal vertical line x position.",
        ),
        "n1": ParameterRequirement(
            id="req_refraction_n1",
            name="n1",
            dimension=PhysicalDimension.REFRACTIVE_INDEX,
            required=True,
            min_value=1.0,
            default_policy_id="policy_air_refractive_index",
            prompt_question="Medium 1 refractive index n₁.",
            prompt_question_bn="১ম মাধ্যমের প্রতিসরাঙ্ক n₁ কত?",
            help_text="Incident medium refractive index (e.g. 1.0 for air).",
        ),
        "n2": ParameterRequirement(
            id="req_refraction_n2",
            name="n2",
            dimension=PhysicalDimension.REFRACTIVE_INDEX,
            required=True,
            min_value=1.0,
            prompt_question="Medium 2 refractive index n₂.",
            prompt_question_bn="২য় মাধ্যমের প্রতিসরাঙ্ক n₂ কত?",
            help_text="Refracting medium refractive index (e.g. 1.333 for water, 1.52 for glass).",
        ),
        "theta1": ParameterRequirement(
            id="req_refraction_theta1",
            name="theta1",
            dimension=PhysicalDimension.ANGLE,
            required=False,
            allowed_units=["deg", "degree", "°", "rad"],
            canonical_unit="deg",
            min_value=0.0,
            max_value=90.0,
            can_derive_from_geometry=True,
            prompt_question="Incident angle θ₁ relative to normal.",
            prompt_question_bn="আপতন কোণ θ₁ এর মান কত?",
        ),
        "source_position": ParameterRequirement(
            id="req_refraction_source_pos",
            name="source_position",
            dimension=PhysicalDimension.POINT_2D,
            required=False,
            can_derive_from_geometry=True,
            prompt_question="Light ray source origin coordinate.",
        ),
    },
    one_of_requirements=[["theta1", "source_position"]],
    allowed_policies=["policy_air_refractive_index", "policy_water_refractive_index", "policy_crown_glass_refractive_index"],
    parameter_aliases={
        "boundaryY": "boundary_y",
        "normalX": "normal_x",
        "refractive_index_1": "n1",
        "refractive_index_2": "n2",
        "refractive_index": "n1",
        "incident_angle": "theta1",
        "beam_angle": "theta1",
        "angle": "theta1",
        "sourcePosition": "source_position",
        "source_pos": "source_position",
    },
    notes="Snell's Law interface refraction, critical angle, and TIR solver.",
)

PRISM_SPEC = ModelRequirementSpec(
    domain="optics",
    subtype="prism",
    required_entities=["prism_body"],
    required_geometry=["vertices", "ray_origin", "ray_direction"],
    parameters={
        "vertices": ParameterRequirement(
            id="req_prism_vertices",
            name="vertices",
            dimension=PhysicalDimension.POLYGON_POINTS,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Polygon vertices of the optical prism.",
        ),
        "n": ParameterRequirement(
            id="req_prism_n",
            name="n",
            dimension=PhysicalDimension.REFRACTIVE_INDEX,
            required=True,
            min_value=1.0,
            default_policy_id="policy_crown_glass_refractive_index",
            prompt_question="Prism material refractive index n.",
            prompt_question_bn="প্রিজমের প্রতিসরাঙ্ক n কত?",
        ),
        "apex_angle_deg": ParameterRequirement(
            id="req_prism_apex_angle",
            name="apex_angle_deg",
            dimension=PhysicalDimension.ANGLE,
            required=True,
            allowed_units=["deg", "degree", "°"],
            canonical_unit="deg",
            min_value=1.0,
            max_value=179.0,
            can_derive_from_geometry=True,
            prompt_question="Prism apex angle A.",
            prompt_question_bn="প্রিজম কোণ A এর মান কত?",
        ),
        "ray_origin": ParameterRequirement(
            id="req_prism_ray_origin",
            name="ray_origin",
            dimension=PhysicalDimension.POINT_2D,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Incident ray start coordinate.",
        ),
        "ray_direction": ParameterRequirement(
            id="req_prism_ray_direction",
            name="ray_direction",
            dimension=PhysicalDimension.POINT_2D,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Incident ray direction vector.",
        ),
    },
    allowed_policies=["policy_crown_glass_refractive_index"],
    parameter_aliases={
        "apex_angle": "apex_angle_deg",
        "apexAngle": "apex_angle_deg",
        "refractive_index": "n",
        "refractiveIndex": "n",
        "rayOrigin": "ray_origin",
        "rayDirection": "ray_direction",
        "prismVertices": "vertices",
    },
    notes="Triangular/polygonal prism refraction with angle of deviation δ.",
)

CIRCUITS_DC_LINEAR_SPEC = ModelRequirementSpec(
    domain="circuits",
    subtype="dc_linear",
    required_entities=["resistor"],
    required_geometry=[],
    parameters={
        "nodes": ParameterRequirement(
            id="req_circuits_nodes",
            name="nodes",
            dimension=PhysicalDimension.TOPOLOGY_NODES,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Circuit graph node topology.",
        ),
        "components": ParameterRequirement(
            id="req_circuits_components",
            name="components",
            dimension=PhysicalDimension.TOPOLOGY_COMPONENTS,
            required=True,
            can_derive_from_geometry=True,
            prompt_question="Circuit component specifications (resistors, sources).",
        ),
    },
    notes="Modified Nodal Analysis (MNA) matrix solver for DC resistor networks.",
)

# Registry mapping (domain, subtype) to ModelRequirementSpec
REQUIREMENT_REGISTRY: Dict[str, ModelRequirementSpec] = {
    "mechanics/pendulum": PENDULUM_SPEC,
    "mechanics/projectile": PROJECTILE_SPEC,
    "optics/thin_lens": THIN_LENS_SPEC,
    "optics/concave_lens": THIN_LENS_SPEC,
    "optics/mirror": SPHERICAL_MIRROR_SPEC,
    "optics/spherical_mirror": SPHERICAL_MIRROR_SPEC,
    "optics/interface_refraction": INTERFACE_REFRACTION_SPEC,
    "optics/prism": PRISM_SPEC,
    "circuits/dc_linear": CIRCUITS_DC_LINEAR_SPEC,
}


class RequirementRegistry:
    """Registry for querying ModelRequirementSpec contracts."""

    @classmethod
    def get_spec(cls, subtype: Optional[str], domain: Optional[str] = None) -> Optional[ModelRequirementSpec]:
        """Lookup ModelRequirementSpec by subtype and optional domain."""
        if not subtype:
            return None
        sub = subtype.lower()
        if domain:
            dom = domain.lower()
            key = f"{dom}/{sub}"
            if key in REQUIREMENT_REGISTRY:
                return REQUIREMENT_REGISTRY[key]
        for key, spec in REQUIREMENT_REGISTRY.items():
            if key.endswith(f"/{sub}") or key == sub:
                return spec
        return None

    @classmethod
    def canonicalize_parameter(cls, subtype: Optional[str], param_name: str, domain: Optional[str] = None) -> str:
        spec = cls.get_spec(subtype, domain=domain)
        if spec:
            return spec.canonicalize_parameter(param_name)
        return param_name


def get_model_spec(domain: Optional[str], subtype: Optional[str]) -> Optional[ModelRequirementSpec]:
    """Retrieve the requirement spec for a (domain, subtype) pair."""
    return RequirementRegistry.get_spec(subtype=subtype, domain=domain)


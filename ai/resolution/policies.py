"""PR-07 Explicit Default Policy Registry.

Enforces zero silent fabrication:
  - Every default is named, documented, domain/subtype scoped, and versioned.
  - Applying a policy explicitly stamps parameter provenance as 'policy_default'
    with policy_id, policy_version, and user confirmation metadata.
  - Removing a policy removes the resolved value and re-triggers missing blockers.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from shared.schemas.ingestion import BookIR, PhysicalValue, ProvenanceRecord
from shared.schemas.resolution import ResolutionSource


@dataclass
class ResolutionPolicy:
    """An explicit, auditable modelling assumption or default policy."""
    id: str
    name: str
    description: str
    domain: str
    target_subtype: Optional[str]
    target_parameter: str
    value: Any
    unit: Optional[str]
    version: str = "1.0"
    requires_user_opt_in: bool = True
    educational_rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def policy_id(self) -> str:
        return self.id

    @property
    def parameter_name(self) -> str:
        return self.target_parameter

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "policyId": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "targetSubtype": self.target_subtype,
            "targetParameter": self.target_parameter,
            "parameterName": self.target_parameter,
            "value": self.value,
            "unit": self.unit,
            "version": self.version,
            "requiresUserOptIn": self.requires_user_opt_in,
            "educationalRationale": self.educational_rationale,
            "metadata": self.metadata,
        }

    def to_physical_value(self, user_accepted: bool = True) -> PhysicalValue:
        """Create a provenance-carrying PhysicalValue from this policy."""
        prov = ProvenanceRecord(
            source=ResolutionSource.POLICY_DEFAULT.value,
            confidence=0.95,
            notes=f"Explicit default policy applied: {self.name} (v{self.version}).",
            policy_id=self.id,
            policy_version=self.version,
            user_accepted=user_accepted,
        )
        return PhysicalValue(
            value=self.value,
            unit=self.unit,
            status="assumed",
            provenance=prov,
        )


class PolicyRegistry:
    """Registry managing standard physical modelling default policies."""

    def __init__(self):
        self._policies: Dict[str, ResolutionPolicy] = {}
        self._register_default_policies()

    def register(self, policy: ResolutionPolicy) -> None:
        self._policies[policy.id] = policy

    def get(self, policy_id: str) -> Optional[ResolutionPolicy]:
        return self._policies.get(policy_id)

    def list_all(self) -> List[ResolutionPolicy]:
        return list(self._policies.values())

    def find_policies_for_parameter(
        self,
        domain: Optional[str],
        subtype: Optional[str],
        parameter_name: str,
    ) -> List[ResolutionPolicy]:
        """Find matching policies for a specific domain, subtype, and parameter."""
        res = []
        d_lower = domain.lower() if domain else None
        sub_lower = subtype.lower() if subtype else None

        for p in self._policies.values():
            if d_lower and p.domain.lower() != d_lower:
                continue
            if p.target_parameter != parameter_name:
                continue
            if p.target_subtype is not None and sub_lower is not None:
                if p.target_subtype.lower() != sub_lower:
                    continue
            res.append(p)
        return res

    @classmethod
    def get_policy(cls, policy_id: str) -> Optional[ResolutionPolicy]:
        return POLICY_REGISTRY.get(policy_id)

    @classmethod
    def find_policy(
        cls,
        subtype: Optional[str],
        parameter_name: str,
        domain: Optional[str] = None,
    ) -> Optional[ResolutionPolicy]:
        matches = POLICY_REGISTRY.find_policies_for_parameter(
            domain=domain,
            subtype=subtype,
            parameter_name=parameter_name,
        )
        return matches[0] if matches else None

    @classmethod
    def get_policies_for_subtype(
        cls,
        subtype: Optional[str],
        domain: Optional[str] = None,
    ) -> List[ResolutionPolicy]:
        sub_lower = subtype.lower() if subtype else None
        d_lower = domain.lower() if domain else None
        res = []
        for p in POLICY_REGISTRY.list_all():
            if d_lower and p.domain.lower() != d_lower:
                continue
            if p.target_subtype is None or (sub_lower and p.target_subtype.lower() == sub_lower):
                res.append(p)
        return res

    def _register_default_policies(self) -> None:
        # 1. Earth Gravity Policy
        self.register(
            ResolutionPolicy(
                id="policy_earth_gravity",
                name="Standard Earth Gravity",
                description="Standard terrestrial acceleration due to gravity (g = 9.80665 m/s² ~ 9.8 m/s²).",
                domain="mechanics",
                target_subtype=None,
                target_parameter="gravity",
                value=9.80665,
                unit="m/s²",
                educational_rationale=(
                    "Standard terrestrial gravitational acceleration specified in NCTB curriculum "
                    "for mechanics exercises unless explicitly specified otherwise."
                ),
            )
        )

        # 2. Zero Damping Policy
        self.register(
            ResolutionPolicy(
                id="policy_zero_damping",
                name="Ideal Undamped Oscillation",
                description="Neglect atmospheric drag and pivot mechanical friction (damping = 0.0 1/s).",
                domain="mechanics",
                target_subtype="pendulum",
                target_parameter="damping",
                value=0.0,
                unit="1/s",
                educational_rationale=(
                    "Ideal simple harmonic motion (SHM) simple pendulum assumption in textbook theory."
                ),
            )
        )

        # 3. Standard Mass Policy (Unit Mass)
        self.register(
            ResolutionPolicy(
                id="policy_standard_mass",
                name="Standard Unit Mass",
                description="Assign 1.0 kg unit bob mass (does not alter ideal pendulum period T = 2π√(L/g)).",
                domain="mechanics",
                target_subtype="pendulum",
                target_parameter="mass",
                value=1.0,
                unit="kg",
                educational_rationale=(
                    "In ideal simple pendulums, period is strictly independent of bob mass. "
                    "A unit mass allows dynamic simulation while preserving all analytical dynamics."
                ),
            )
        )

        # 4. Standard Air Medium Policy
        self.register(
            ResolutionPolicy(
                id="policy_air_refractive_index",
                name="Standard Air Refractive Index",
                description="Refractive index of air at standard temperature and pressure (n = 1.0003 ≈ 1.00).",
                domain="optics",
                target_subtype=None,
                target_parameter="n1",
                value=1.0003,
                unit=None,
                educational_rationale="Air is the default ambient medium in standard optical setups.",
            )
        )

        # 5. Water Refractive Index Policy
        self.register(
            ResolutionPolicy(
                id="policy_water_refractive_index",
                name="Water Medium Refractive Index",
                description="Refractive index of pure liquid water (n = 1.333).",
                domain="optics",
                target_subtype=None,
                target_parameter="n2",
                value=1.333,
                unit=None,
                educational_rationale="Standard NCTB textbook value for water refraction problems.",
            )
        )

        # 6. Crown Glass Refractive Index Policy
        self.register(
            ResolutionPolicy(
                id="policy_crown_glass_refractive_index",
                name="Crown Glass Refractive Index",
                description="Refractive index of standard optical crown glass (n = 1.52).",
                domain="optics",
                target_subtype=None,
                target_parameter="n",
                value=1.52,
                unit=None,
                educational_rationale="Standard refractive index for optical lenses and prisms.",
            )
        )

        # 7. Standard Lens Aperture Policy
        self.register(
            ResolutionPolicy(
                id="policy_standard_lens_aperture",
                name="Standard Lens Aperture Height",
                description="Explicit visual lens aperture height (200.0 source pixels).",
                domain="optics",
                target_subtype="thin_lens",
                target_parameter="aperture_height_px",
                value=200.0,
                unit="px",
                educational_rationale="Standard vertical aperture extent for ray-tracing display.",
            )
        )

        # 8. Standard Mirror Aperture Policy
        self.register(
            ResolutionPolicy(
                id="policy_normalized_lens_focal_ratio",
                name="Normalized Thin Lens Focal Ratio",
                description="Use half the observed lens aperture as a normalized display focal length when no focal evidence exists.",
                domain="optics",
                target_subtype="thin_lens",
                target_parameter="focal_length_px",
                value=0.5,
                unit="aperture_ratio",
                educational_rationale="A disclosed demonstration model; the source diagram does not specify its optical power.",
            )
        )

        # 9. Standard Mirror Aperture Policy
        for policy_id, target, ratio, description in (
            ("policy_normalized_lens_object_distance", "objectDistance", 2.0,
             "Place an exploration object two observed focal lengths left of the measured lens center when no object is printed."),
            ("policy_normalized_lens_object_height", "object_height_px", 0.35,
             "Use 35% of the measured lens aperture for an exploration object not printed in the diagram."),
        ):
            self.register(ResolutionPolicy(
                id=policy_id, name="Normalized Thin Lens Exploration Object",
                description=description, domain="optics", target_subtype="thin_lens",
                target_parameter=target, value=ratio, unit="ratio",
                educational_rationale="This is a disclosed simulation setup, not an observed source-image object.",
            ))

        # 10. Standard Mirror Aperture Policy
        self.register(
            ResolutionPolicy(
                id="policy_normalized_prism_incident_ray",
                name="Normalized Prism Incident Ray",
                description="Launch a horizontal exploration ray toward the observed left prism face when no incident ray is printed.",
                domain="optics", target_subtype="prism", target_parameter="ray_origin",
                value="left_face_horizontal", unit=None,
                educational_rationale="The ray is a disclosed simulation setup based on the measured prism outline, not a source-image observation.",
            )
        )

        for policy_id, target, ratio, description in (
            ("policy_normalized_mirror_object_distance", "objectDistance", 2.0,
             "Place an exploration object two observed focal lengths from the measured mirror pole when no object is printed."),
            ("policy_normalized_mirror_object_height", "object_height_px", 0.35,
             "Use 35% of the measured mirror aperture for an exploration object not printed in the diagram."),
        ):
            self.register(ResolutionPolicy(
                id=policy_id, name="Normalized Spherical Mirror Exploration Object",
                description=description, domain="optics", target_subtype="spherical_mirror",
                target_parameter=target, value=ratio, unit="ratio",
                educational_rationale="This is a disclosed simulation setup, not an observed source-image object.",
            ))

        # 10. Standard Mirror Aperture Policy
        self.register(
            ResolutionPolicy(
                id="policy_standard_mirror_aperture",
                name="Standard Mirror Aperture Height",
                description="Explicit visual mirror aperture height (200.0 source pixels).",
                domain="optics",
                target_subtype="spherical_mirror",
                target_parameter="aperture_height_px",
                value=200.0,
                unit="px",
                educational_rationale="Standard visual aperture extent for spherical mirror reflection.",
            )
        )

        # 9. Standard Projectile Ball Radius Policy
        self.register(
            ResolutionPolicy(
                id="policy_standard_ball_radius",
                name="Standard Projectile Visual Radius",
                description="Explicit projectile visual radius (15.0 source pixels).",
                domain="mechanics",
                target_subtype="projectile",
                target_parameter="ball_radius_px",
                value=15.0,
                unit="px",
                educational_rationale="Standard visual display radius for projectile marker on textbook diagrams.",
            )
        )

        # 10. Standard Projectile Display Scale Policy
        self.register(
            ResolutionPolicy(
                id="policy_standard_projectile_scale",
                name="Standard Display Scale Calibration",
                description="Standard diagram display scale calibration (25.0 px/m).",
                domain="mechanics",
                target_subtype="projectile",
                target_parameter="pixels_per_meter",
                value=25.0,
                unit="px/m",
                educational_rationale="Standard diagram display scale ensuring full parabolic trajectory fits diagram canvas.",
            )
        )

        # 11. Prism Apex Angle Policy
        self.register(
            ResolutionPolicy(
                id="policy_prism_apex_angle",
                name="Standard Equilateral Prism Apex Angle",
                description="Standard 60.0° apex angle for equilateral optical prism.",
                domain="optics",
                target_subtype="prism",
                target_parameter="apex_angle_deg",
                value=60.0,
                unit="deg",
                educational_rationale="Standard equilateral 60° triangular prism used in secondary physics curricula.",
            )
        )

        # 12. Spherical Mirror Concavity Policy
        self.register(
            ResolutionPolicy(
                id="policy_mirror_concave",
                name="Standard Concave Spherical Mirror",
                description="Default to converging concave spherical mirror curvature.",
                domain="optics",
                target_subtype="spherical_mirror",
                target_parameter="concavity",
                value="concave",
                unit=None,
                educational_rationale="Standard introductory optics reflection studies focus on concave converging mirrors.",
            )
        )

        # 13. Standard DC Voltage Source Policy
        self.register(
            ResolutionPolicy(
                id="policy_standard_dc_voltage",
                name="Standard DC Source Voltage",
                description="Standard 10.0 V DC bench power supply voltage.",
                domain="circuits",
                target_subtype="dc_linear",
                target_parameter="source_voltage",
                value=10.0,
                unit="V",
                educational_rationale="Standard 10V bench voltage source for introductory DC circuit network analysis.",
            )
        )

        # 14. Standard Resistor Value Policy
        self.register(
            ResolutionPolicy(
                id="policy_standard_dc_resistance",
                name="Standard Load Resistor Value",
                description="Standard 100.0 Ω load resistance.",
                domain="circuits",
                target_subtype="dc_linear",
                target_parameter="resistance",
                value=100.0,
                unit="Ω",
                educational_rationale="Standard 100 Ohm load resistor for manageable branch currents.",
            )
        )

        # 15. Standard Pendulum Length Policy
        self.register(
            ResolutionPolicy(
                id="policy_standard_pendulum_length",
                name="Standard Pendulum String Length",
                description="Standard 1.0 m simple pendulum string length.",
                domain="mechanics",
                target_subtype="pendulum",
                target_parameter="length",
                value=1.0,
                unit="m",
                educational_rationale="Standard seconds pendulum unit length (L = 1.0 m produces T ≈ 2.0 s).",
            )
        )

        # 16. Standard Projectile Launch Speed Policy
        self.register(
            ResolutionPolicy(
                id="policy_standard_projectile_speed",
                name="Standard Initial Velocity",
                description="Standard 20.0 m/s initial launch speed.",
                domain="mechanics",
                target_subtype="projectile",
                target_parameter="launch_speed",
                value=20.0,
                unit="m/s",
                educational_rationale="Standard introductory textbook launch velocity.",
            )
        )

        # 17. Standard Projectile Launch Angle Policy
        self.register(
            ResolutionPolicy(
                id="policy_standard_projectile_angle",
                name="Standard Launch Angle",
                description="Standard 45.0° launch angle for maximum range.",
                domain="mechanics",
                target_subtype="projectile",
                target_parameter="launch_angle_deg",
                value=45.0,
                unit="deg",
                educational_rationale="Standard maximum horizontal range 45° launch angle.",
            )
        )


POLICY_REGISTRY = PolicyRegistry()

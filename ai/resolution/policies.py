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


POLICY_REGISTRY = PolicyRegistry()

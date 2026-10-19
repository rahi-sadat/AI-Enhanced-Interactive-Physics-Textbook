"""PR-06 Entity Grounder Registry.

Registers and dispatches subtype-specific entity grounders for all 7 supported
PhysicsCompiler domains and subtypes.
"""
from __future__ import annotations

from typing import List, Optional

from ai.evidence.grounding.base import EntityGrounder
from ai.evidence.grounding.circuits import CircuitGrounder
from ai.evidence.grounding.pendulum import PendulumGrounder
from ai.evidence.grounding.prism import PrismGrounder
from ai.evidence.grounding.projectile import ProjectileGrounder
from ai.evidence.grounding.refraction import InterfaceRefractionGrounder
from ai.evidence.grounding.spherical_mirror import SphericalMirrorGrounder
from ai.evidence.grounding.thin_lens import ThinLensGrounder


class GrounderRegistry:
    """Registry maintaining active subtype-specific entity grounders."""

    def __init__(self):
        self._grounders: List[EntityGrounder] = []
        # Register implementations for all 7 supported subtypes
        self.register(PendulumGrounder())
        self.register(ProjectileGrounder())
        self.register(ThinLensGrounder())
        self.register(SphericalMirrorGrounder())
        self.register(InterfaceRefractionGrounder())
        self.register(PrismGrounder())
        self.register(CircuitGrounder())

    def register(self, grounder: EntityGrounder) -> None:
        self._grounders.append(grounder)

    def find_grounder(self, domain: Optional[str], subtype: Optional[str]) -> Optional[EntityGrounder]:
        if not domain or not subtype:
            return None
        for g in self._grounders:
            if g.supports(domain, subtype):
                return g
        return None

    def list_supported_capabilities(self) -> List[str]:
        """Return list of supported domain/subtype pairings."""
        caps = []
        for g in self._grounders:
            caps.append(f"{g.domain}/{g.subtype}")
        return sorted(list(set(caps)))


# Global registry singleton
_DEFAULT_REGISTRY = GrounderRegistry()


def get_default_grounder_registry() -> GrounderRegistry:
    return _DEFAULT_REGISTRY

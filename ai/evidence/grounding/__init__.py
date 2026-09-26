"""PR-06 Grounding Package."""
from .base import EntityGrounder, GroundingOutcome
from .pendulum import PendulumGrounder
from .projectile import ProjectileGrounder
from .thin_lens import ThinLensGrounder
from .spherical_mirror import SphericalMirrorGrounder
from .refraction import InterfaceRefractionGrounder
from .prism import PrismGrounder
from .circuits import CircuitGrounder
from .registry import GrounderRegistry, get_default_grounder_registry
from .physical_value_parser import parse_physical_value_candidate, normalize_ocr_text

__all__ = [
    "EntityGrounder",
    "GroundingOutcome",
    "PendulumGrounder",
    "ProjectileGrounder",
    "ThinLensGrounder",
    "SphericalMirrorGrounder",
    "InterfaceRefractionGrounder",
    "PrismGrounder",
    "CircuitGrounder",
    "GrounderRegistry",
    "get_default_grounder_registry",
    "parse_physical_value_candidate",
    "normalize_ocr_text",
]

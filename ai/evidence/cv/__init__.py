"""PR-06 Classical CV Utilities Package."""
from .preprocessing import preprocess_diagram, mask_out_text_regions, preprocess_for_geometry
from .geometry_helpers import (
    distance_pt,
    point_to_segment_distance,
    fit_circle_subpixel,
    fit_line_subpixel,
    merge_collinear_lines,
    line_intersection,
)
from .pendulum_cv import PendulumCVCandidateExtractor
from .projectile_cv import ProjectileCVCandidateExtractor
from .thin_lens_cv import ThinLensCVCandidateExtractor
from .spherical_mirror_cv import SphericalMirrorCVCandidateExtractor
from .refraction_cv import InterfaceRefractionCVCandidateExtractor
from .prism_cv import PrismCVCandidateExtractor
from .circuits_cv import CircuitCVCandidateExtractor

__all__ = [
    "preprocess_diagram",
    "mask_out_text_regions",
    "preprocess_for_geometry",
    "distance_pt",
    "point_to_segment_distance",
    "fit_circle_subpixel",
    "fit_line_subpixel",
    "merge_collinear_lines",
    "line_intersection",
    "PendulumCVCandidateExtractor",
    "ProjectileCVCandidateExtractor",
    "ThinLensCVCandidateExtractor",
    "SphericalMirrorCVCandidateExtractor",
    "InterfaceRefractionCVCandidateExtractor",
    "PrismCVCandidateExtractor",
    "CircuitCVCandidateExtractor",
]

"""Unit tests for VisualRequirementSpec and VisualRequirementRegistry (Phase 4)."""
import pytest
from ai.resolution.visual_requirements import (
    VisualRequirementRegistry,
    VisualRequirementSpec,
    VisualElement,
    VisualElementKind,
    PENDULUM_VISUAL_SPEC,
    PROJECTILE_VISUAL_SPEC,
    THIN_LENS_VISUAL_SPEC,
    CIRCUIT_VISUAL_SPEC,
)


def test_visual_requirement_registry_all_domains():
    """Verify registry returns specifications for all supported domains/subtypes."""
    expected = [
        ("mechanics", "pendulum"),
        ("mechanics", "projectile"),
        ("optics", "thin_lens"),
        ("optics", "spherical_mirror"),
        ("optics", "interface_refraction"),
        ("optics", "prism"),
        ("circuits", "dc_linear"),
    ]
    for domain, subtype in expected:
        spec = VisualRequirementRegistry.get_spec(subtype, domain)
        assert spec is not None, f"Missing spec for {domain}/{subtype}"
        assert spec.domain == domain
        assert spec.subtype == subtype
        assert len(spec.observable_elements) > 0


def test_visual_requirement_fallback_lookup():
    """Verify subtype lookup works without domain parameter."""
    spec = VisualRequirementRegistry.get_spec("pendulum")
    assert spec is not None
    assert spec.subtype == "pendulum"


def test_visual_requirement_case_insensitive():
    """Verify registry lookups are case-insensitive."""
    spec = VisualRequirementRegistry.get_spec("THIN_LENS", "OPTICS")
    assert spec is not None
    assert spec.subtype == "thin_lens"


def test_visual_requirement_unknown_returns_none():
    """Verify unknown subtypes return None."""
    assert VisualRequirementRegistry.get_spec("unknown_subtype") is None
    assert VisualRequirementRegistry.get_spec(None) is None


def test_pendulum_observable_elements():
    """Verify pendulum visual requirements include pivot, bob_center, string, and dynamic bob."""
    spec = PENDULUM_VISUAL_SPEC
    elem_ids = {e.id for e in spec.observable_elements}
    assert "pivot" in elem_ids
    assert "bob_center" in elem_ids
    assert "string" in elem_ids
    assert "bob_mask" in spec.dynamic_elements


def test_thin_lens_observable_elements():
    """Verify thin lens visual requirements include axis, lens, object, rays."""
    spec = THIN_LENS_VISUAL_SPEC
    elem_ids = {e.id for e in spec.observable_elements}
    assert "lens_center" in elem_ids
    assert "optical_axis" in elem_ids
    assert "object_base" in elem_ids
    assert "ray_parallel" in elem_ids
    assert "object_arrow" in spec.dynamic_elements


def test_circuit_exact_match_elements():
    """Verify circuit visual requirements declare wire skeleton as exact match."""
    spec = CIRCUIT_VISUAL_SPEC
    assert "wire_skeleton" in spec.exact_match_elements
    elem = spec.get_element("wire_skeleton")
    assert elem is not None
    assert elem.kind == VisualElementKind.TOPOLOGY

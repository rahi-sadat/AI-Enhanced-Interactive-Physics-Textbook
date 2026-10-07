"""PR-07 Acceptance Tests: All 7 Supported Physics Domains / Subtypes.

Verifies the complete PR-07 pipeline for every supported solver:
  1. mechanics/pendulum
  2. mechanics/projectile
  3. optics/thin_lens
  4. optics/spherical_mirror
  5. optics/interface_refraction
  6. optics/prism
  7. circuits/dc_linear

Flow for each:
  Grounded BookIR (NEEDS_REVIEW)
      ↓
  ResolutionAnalyzer detects missing requirements & blockers
      ↓
  Explicit user values & default policies applied via ResolutionEngine
      ↓
  ReadinessEvaluator confirms READY_TO_COMPILE invariant
      ↓
  PhysicsCompiler produces runnable Canonical PhysicsScene (status: READY)
"""
import pytest
from ai.resolution.analyzer import ResolutionAnalyzer
from ai.resolution.engine import ResolutionEngine
from ai.resolution.evaluator import ReadinessEvaluator
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from shared.schemas.ingestion import BookIR, BookEntity, BookIRStatus, ProvenanceRecord


class TestAllDomainsResolutionAndCompilation:
    """End-to-end resolution acceptance across all 7 supported physics subtypes."""

    def test_domain_pendulum(self):
        b = BookIR(
            source_asset_id="asset_pendulum",
            figure_id="fig_pendulum",
            domain="mechanics",
            subtype="pendulum",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_p", type="pivot", position_source_px={"x": 300, "y": 100}),
                BookEntity(id="e_b", type="bob", position_source_px={"x": 300, "y": 500}),
                BookEntity(id="e_s", type="string", position_source_px={"x": 300, "y": 100}, geometry={"effective_length_px": 400}),
            ],
            geometry={
                "pivot": {"x": 300, "y": 100},
                "bob_center": {"x": 300, "y": 500},
                "string_length_px": 400.0,
                "bob_radius_px": 20.0,
                "width": 800.0,
                "height": 600.0,
            },
            parameters={},
        )
        # Initial check: missing compile requirements
        rev = ResolutionAnalyzer.analyze(b)
        assert rev.ready_to_compile is False

        # Apply resolutions
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 0.8,
            "canonicalUnit": "m",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_policy(b, "policy_earth_gravity")
        ResolutionEngine.apply_policy(b, "policy_standard_mass")
        ResolutionEngine.apply_policy(b, "policy_zero_damping")

        assert b.status == BookIRStatus.READY_TO_COMPILE
        compiler = PhysicsCompiler()
        res = compiler.compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["subtype"] == "pendulum"

    def test_domain_projectile(self):
        b = BookIR(
            source_asset_id="asset_proj",
            figure_id="fig_proj",
            domain="mechanics",
            subtype="projectile",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_cannon", type="launch_source", position_source_px={"x": 100, "y": 500}),
                BookEntity(id="e_ball", type="projectile_body", position_source_px={"x": 100, "y": 500}),
            ],
            geometry={
                "launch_source_px": {"x": 100, "y": 500},
                "ball_radius_px": 10.0,
                "width": 1000.0,
                "height": 600.0,
            },
            parameters={},
        )
        rev = ResolutionAnalyzer.analyze(b)
        assert rev.ready_to_compile is False

        # Resolve projectile speed, angle, calibration, gravity
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "launch_speed",
            "resolvedValue": 25.0,
            "canonicalUnit": "m/s",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "launch_angle_deg",
            "resolvedValue": 45.0,
            "canonicalUnit": "deg",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "pixels_per_meter",
            "resolvedValue": 50.0,
            "canonicalUnit": "px/m",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_policy(b, "policy_earth_gravity")

        assert b.status == BookIRStatus.READY_TO_COMPILE
        res = PhysicsCompiler().compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["subtype"] == "projectile"

    def test_domain_thin_lens(self):
        b = BookIR(
            source_asset_id="asset_lens",
            figure_id="fig_lens",
            domain="optics",
            subtype="thin_lens",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_lens", type="lens", position_source_px={"x": 400, "y": 300}),
            ],
            geometry={
                "lens_center": {"x": 400, "y": 300},
                "width": 800.0,
                "height": 600.0,
            },
            parameters={},
        )
        # Missing focal length and aperture
        rev = ResolutionAnalyzer.analyze(b)
        assert rev.ready_to_compile is False

        ResolutionEngine.apply_resolution(b, {
            "parameterName": "focal_length_px",
            "resolvedValue": 150.0,
            "canonicalUnit": "px",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_policy(b, "policy_standard_lens_aperture")

        assert b.status == BookIRStatus.READY_TO_COMPILE
        res = PhysicsCompiler().compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["subtype"] == "thin_lens"

    def test_domain_spherical_mirror(self):
        b = BookIR(
            source_asset_id="asset_mirror",
            figure_id="fig_mirror",
            domain="optics",
            subtype="spherical_mirror",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_m", type="mirror", position_source_px={"x": 500, "y": 300}),
            ],
            geometry={
                "pole": {"x": 500, "y": 300},
                "width": 800.0,
                "height": 600.0,
            },
            parameters={},
        )
        rev = ResolutionAnalyzer.analyze(b)
        assert rev.ready_to_compile is False

        ResolutionEngine.apply_resolution(b, {
            "parameterName": "focal_length_px",
            "resolvedValue": 120.0,
            "canonicalUnit": "px",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "concavity",
            "resolvedValue": "concave",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_policy(b, "policy_standard_mirror_aperture")

        assert b.status == BookIRStatus.READY_TO_COMPILE
        res = PhysicsCompiler().compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["subtype"] == "spherical_mirror"

    def test_domain_interface_refraction(self):
        b = BookIR(
            source_asset_id="asset_refr",
            figure_id="fig_refr",
            domain="optics",
            subtype="interface_refraction",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_boundary", type="interface_boundary", position_source_px={"x": 400, "y": 300}),
            ],
            geometry={
                "boundary_y": 300.0,
                "normal_x": 400.0,
                "source_position": {"x": 200, "y": 100},
                "width": 800.0,
                "height": 600.0,
            },
            parameters={},
        )
        rev = ResolutionAnalyzer.analyze(b)
        assert rev.ready_to_compile is False

        # Apply policies for air (medium 1) and water (medium 2)
        ResolutionEngine.apply_policy(b, "policy_air_refractive_index")
        ResolutionEngine.apply_policy(b, "policy_water_refractive_index")

        assert b.status == BookIRStatus.READY_TO_COMPILE
        res = PhysicsCompiler().compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["subtype"] == "interface_refraction"

    def test_domain_prism(self):
        b = BookIR(
            source_asset_id="asset_prism",
            figure_id="fig_prism",
            domain="optics",
            subtype="prism",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_prism", type="prism", position_source_px={"x": 400, "y": 300}),
            ],
            geometry={
                "vertices": [{"x": 300, "y": 450}, {"x": 400, "y": 200}, {"x": 500, "y": 450}],
                "apex_angle_deg": 60.0,
                "rayOrigin": {"x": 200, "y": 350},
                "rayDirection": {"x": 1.0, "y": 0.0},
                "width": 800.0,
                "height": 600.0,
            },
            parameters={},
        )
        rev = ResolutionAnalyzer.analyze(b)
        assert rev.ready_to_compile is False

        # Apply crown glass refractive index policy
        ResolutionEngine.apply_policy(b, "policy_crown_glass_refractive_index")

        assert b.status == BookIRStatus.READY_TO_COMPILE
        res = PhysicsCompiler().compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["subtype"] == "prism"

    def test_domain_circuits_dc_linear(self):
        b = BookIR(
            source_asset_id="asset_circ",
            figure_id="fig_circ",
            domain="circuits",
            subtype="dc_linear",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_r1", type="resistor", position_source_px={"x": 300, "y": 200}),
                BookEntity(id="e_v1", type="voltage_source", position_source_px={"x": 150, "y": 200}),
            ],
            geometry={
                "width": 600.0,
                "height": 400.0,
            },
            parameters={
                "nodes": ["0", "1"],
                "components": [
                    {"id": "V1", "type": "voltage_source", "nodes": ["1", "0"], "value": 12.0, "unit": "V"},
                    {"id": "R1", "type": "resistor", "nodes": ["1", "0"], "value": 1000.0, "unit": "ohm"},
                ],
            },
            parameter_provenance={
                "nodes": ProvenanceRecord(source="observed_visual", notes="Extracted from circuit schematic graph."),
                "components": ProvenanceRecord(source="observed_visual", notes="Extracted from circuit schematic components."),
            },
        )
        # All required topology components and nodes already exist in grounded parameters
        rev = ReadinessEvaluator.evaluate(b, mutate_status=True)
        assert rev.ready is True
        assert b.status == BookIRStatus.READY_TO_COMPILE

        res = PhysicsCompiler().compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["domain"] == "circuits"
        assert res.scene["subtype"] == "dc_linear"

    def test_projectile_with_zero_values_compiles_successfully(self):
        """Verify 0.0 is accepted for launch_speed (drop from rest), launch_angle_deg (horizontal throw), and zero gravity."""
        b = BookIR(
            source_asset_id="asset_proj_zero",
            figure_id="fig_proj_zero",
            domain="mechanics",
            subtype="projectile",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_source", type="launch_source", position_source_px={"x": 50, "y": 50}),
                BookEntity(id="e_ball", type="projectile_body", position_source_px={"x": 50, "y": 50}),
            ],
            geometry={
                "launch_source_px": {"x": 50, "y": 50},
                "ball_radius_px": 8.0,
                "width": 800.0,
                "height": 600.0,
            },
            parameters={},
        )
        # Drop from rest (speed = 0 m/s), horizontal angle (0 deg), zero-g environment (gravity = 0 m/s2)
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "launch_speed",
            "resolvedValue": 0.0,
            "canonicalUnit": "m/s",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "launch_angle_deg",
            "resolvedValue": 0.0,
            "canonicalUnit": "deg",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "gravity",
            "resolvedValue": 0.0,
            "canonicalUnit": "m/s²",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "pixels_per_meter",
            "resolvedValue": 80.0,
            "canonicalUnit": "px/m",
            "resolutionSource": "user_supplied",
        })
        assert b.status == BookIRStatus.READY_TO_COMPILE
        res = PhysicsCompiler().compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["parameters"]["speed"]["value"] == 0.0
        assert res.scene["parameters"]["angle"]["value"] == 0.0
        assert res.scene["environment"]["gravity"] == 0.0

    def test_pendulum_with_zero_damping_and_zero_gravity_compiles(self):
        """Verify pendulum compiles cleanly with explicit 0.0 damping (frictionless) and 0.0 gravity."""
        b = BookIR(
            source_asset_id="asset_pendulum_zero",
            figure_id="fig_pendulum_zero",
            domain="mechanics",
            subtype="pendulum",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_p", type="pivot", position_source_px={"x": 200, "y": 100}),
                BookEntity(id="e_b", type="bob", position_source_px={"x": 200, "y": 400}),
                BookEntity(id="e_s", type="string", position_source_px={"x": 200, "y": 100}, geometry={"effective_length_px": 300}),
            ],
            geometry={
                "pivot": {"x": 200, "y": 100},
                "bob_center": {"x": 200, "y": 400},
                "string_length_px": 300.0,
                "bob_radius_px": 15.0,
                "width": 600.0,
                "height": 600.0,
            },
            parameters={},
        )
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 1.2,
            "canonicalUnit": "m",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "mass",
            "resolvedValue": 0.5,
            "canonicalUnit": "kg",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "gravity",
            "resolvedValue": 0.0,
            "canonicalUnit": "m/s²",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_policy(b, "policy_zero_damping")
        assert b.status == BookIRStatus.READY_TO_COMPILE
        res = PhysicsCompiler().compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["parameters"]["damping"]["value"] == 0.0
        assert res.scene["parameters"]["gravity"]["value"] == 0.0

    def test_interface_refraction_normal_incidence_and_zero_coordinates_compiles(self):
        """Verify interface refraction compiles with normal incidence theta1 = 0.0 deg and coordinate 0.0."""
        b = BookIR(
            source_asset_id="asset_refr_zero",
            figure_id="fig_refr_zero",
            domain="optics",
            subtype="interface_refraction",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_boundary", type="interface_boundary", position_source_px={"x": 0.0, "y": 0.0}),
            ],
            geometry={
                "boundary_y": 0.0,
                "normal_x": 0.0,
                "source_position": {"x": 0.0, "y": -50.0},
                "width": 500.0,
                "height": 500.0,
            },
            parameters={
                "theta1": 0.0,
            },
            parameter_provenance={
                "theta1": ProvenanceRecord(source="observed_visual", notes="Normal ray incidence 0.0 deg"),
            },
        )
        ResolutionEngine.apply_policy(b, "policy_air_refractive_index")
        ResolutionEngine.apply_policy(b, "policy_water_refractive_index")
        assert b.status == BookIRStatus.READY_TO_COMPILE
        res = PhysicsCompiler().compile(b)
        assert res.status == "READY"
        assert res.scene is not None
        assert res.scene["parameters"]["theta1"]["value"] == 0.0
        assert res.scene["geometry"]["boundaryY"] == 0.0
        assert res.scene["geometry"]["normalX"] == 0.0

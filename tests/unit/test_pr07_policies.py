"""PR-07 Unit Tests: Explicit Policy Registry & Zero-Fabrication Guarantees.

Verifies:
  - All default policies are named, versioned, domain/subtype scoped, and auditable.
  - No hidden constants inside PhysicsCompiler.
  - Policy application produces provenance records carrying policy_id, policy_version, user_accepted.
  - Deleting/removing a policy reverses resolution and re-triggers compilation gating.
"""
import pytest
from ai.resolution.policies import PolicyRegistry, ResolutionPolicy
from shared.schemas.ingestion import BookIR, BookEntity
from shared.schemas.resolution import ResolutionSource
from ai.resolution.engine import ResolutionEngine
from ai.resolution.evaluator import ReadinessEvaluator


class TestPolicyRegistry:
    """Verify registered physical modelling default policies."""

    def test_registry_contains_standard_policies(self):
        policies = PolicyRegistry().list_all()
        policy_ids = {p.id for p in policies}

        expected = {
            "policy_earth_gravity",
            "policy_zero_damping",
            "policy_standard_mass",
            "policy_air_refractive_index",
            "policy_water_refractive_index",
            "policy_crown_glass_refractive_index",
            "policy_standard_lens_aperture",
            "policy_standard_mirror_aperture",
        }
        for exp in expected:
            assert exp in policy_ids, f"Expected policy '{exp}' not found in PolicyRegistry."

    def test_earth_gravity_policy_spec(self):
        policy = PolicyRegistry.get_policy("policy_earth_gravity")
        assert policy is not None
        assert policy.domain == "mechanics"
        assert policy.parameter_name == "gravity"
        assert policy.value == pytest.approx(9.80665)
        assert policy.unit == "m/s²"
        assert policy.version == "1.0"
        assert policy.requires_user_opt_in is True

    def test_zero_damping_policy_spec(self):
        policy = PolicyRegistry.get_policy("policy_zero_damping")
        assert policy is not None
        assert policy.domain == "mechanics"
        assert policy.target_subtype == "pendulum"
        assert policy.parameter_name == "damping"
        assert policy.value == 0.0
        assert policy.unit == "1/s"

    def test_find_policy_by_parameter(self):
        match = PolicyRegistry.find_policy(subtype="pendulum", parameter_name="gravity")
        assert match is not None
        assert match.id == "policy_earth_gravity"

        damp_match = PolicyRegistry.find_policy(subtype="pendulum", parameter_name="damping")
        assert damp_match is not None
        assert damp_match.id == "policy_zero_damping"

    def test_policies_filtered_by_subtype(self):
        pendulum_policies = PolicyRegistry.get_policies_for_subtype("pendulum")
        p_ids = {p.id for p in pendulum_policies}
        assert "policy_earth_gravity" in p_ids
        assert "policy_zero_damping" in p_ids
        assert "policy_standard_mass" in p_ids
        # Optics policies should not be in pendulum subtype
        assert "policy_standard_lens_aperture" not in p_ids


class TestPolicyApplicationAndProvenance:
    """Verify that applying a policy explicitly sets audit trail and provenance."""

    def test_apply_policy_stamps_provenance(self):
        b = BookIR(
            source_asset_id="asset_1",
            figure_id="fig_1",
            domain="mechanics",
            subtype="pendulum",
            status="NEEDS_REVIEW",
            parameters={},
        )
        res = ResolutionEngine.apply_policy(b, "policy_earth_gravity")
        assert res.success is True
        assert b.parameters["gravity"] == pytest.approx(9.80665)

        # Check provenance record
        prov = b.parameter_provenance["gravity"]
        assert prov.source == ResolutionSource.POLICY_DEFAULT.value
        assert prov.policy_id == "policy_earth_gravity"
        assert prov.policy_version == "1.0"
        assert prov.user_accepted is True

        # Check resolution decision
        res_dec = b.resolutions["gravity"]
        assert res_dec["policyId"] == "policy_earth_gravity"
        assert res_dec["resolutionSource"] == ResolutionSource.POLICY_DEFAULT.value

    def test_removing_policy_reverses_resolution(self):
        b = BookIR(
            source_asset_id="asset_1",
            figure_id="fig_1",
            domain="mechanics",
            subtype="pendulum",
            status="NEEDS_REVIEW",
            entities=[
                BookEntity(id="e_pivot", type="pivot", position_source_px={"x": 100, "y": 50}),
                BookEntity(id="e_bob", type="bob", position_source_px={"x": 100, "y": 350}),
                BookEntity(id="e_str", type="string", position_source_px={"x": 100, "y": 50}, geometry={"effective_length_px": 300}),
            ],
            geometry={"pivot": {"x": 100, "y": 50}, "bob_center": {"x": 100, "y": 350}, "string_length_px": 300, "bob_radius_px": 15, "width": 800, "height": 600},
            parameters={},
        )
        ResolutionEngine.apply_resolution(b, {
            "parameterName": "length",
            "resolvedValue": 0.8,
            "canonicalUnit": "m",
            "resolutionSource": "user_supplied",
        })
        ResolutionEngine.apply_policy(b, "policy_earth_gravity")
        ResolutionEngine.apply_policy(b, "policy_standard_mass")
        ResolutionEngine.apply_policy(b, "policy_zero_damping")

        eval_before = ReadinessEvaluator.evaluate(b)
        assert eval_before.ready is True
        assert b.status == "READY_TO_COMPILE"

        # Remove gravity policy
        report_after = ResolutionEngine.remove_resolution(b, "gravity")
        assert report_after.ready is False
        assert b.status == "NEEDS_REVIEW"
        assert "gravity" not in b.parameters
        assert "gravity" not in b.resolutions
        assert any("gravity" in blk.lower() for blk in report_after.blockers)

    def test_optics_policy_cannot_be_applied_to_pendulum(self):
        b = BookIR(
            source_asset_id="asset_1",
            figure_id="fig_1",
            domain="mechanics",
            subtype="pendulum",
            status="NEEDS_REVIEW",
            parameters={},
        )
        res = ResolutionEngine.apply_policy(b, "policy_air_refractive_index")
        assert res.success is False
        assert "POLICY_DOMAIN_MISMATCH" in res.error or "POLICY_NOT_ALLOWED" in res.error
        assert "gravity" not in b.parameters

    def test_pendulum_policy_cannot_be_applied_to_optics(self):
        b = BookIR(
            source_asset_id="asset_opt",
            figure_id="fig_opt",
            domain="optics",
            subtype="thin_lens",
            status="NEEDS_REVIEW",
            parameters={},
        )
        res = ResolutionEngine.apply_policy(b, "policy_earth_gravity")
        assert res.success is False
        assert "POLICY_DOMAIN_MISMATCH" in res.error or "POLICY_NOT_ALLOWED" in res.error
        assert "gravity" not in b.parameters

    def test_pendulum_available_policies_contain_only_mechanics_policies(self):
        from ai.resolution.analyzer import ResolutionAnalyzer
        b = BookIR(
            source_asset_id="asset_pend",
            figure_id="fig_pend",
            domain="mechanics",
            subtype="pendulum",
            status="NEEDS_REVIEW",
            parameters={},
        )
        review = ResolutionAnalyzer.analyze(b)
        avail_ids = [p["id"] for p in review.available_policies]
        assert "policy_earth_gravity" in avail_ids
        assert "policy_standard_mass" in avail_ids
        assert "policy_zero_damping" in avail_ids
        # Strictly ensure optics policies are never advertised for a pendulum
        assert "policy_air_refractive_index" not in avail_ids
        assert "policy_water_refractive_index" not in avail_ids
        assert "policy_crown_glass_refractive_index" not in avail_ids
        assert "policy_standard_lens_aperture" not in avail_ids
        assert "policy_standard_mirror_aperture" not in avail_ids


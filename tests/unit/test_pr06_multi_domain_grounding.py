"""PR-06 Unit Tests — Multi-Domain Grounding Coverage & Strict Anti-Fabrication Invariants.

Tests:
  - Coverage for all 7 supported PhysicsCompiler subtypes:
      * mechanics/pendulum
      * mechanics/projectile
      * optics/thin_lens
      * optics/spherical_mirror
      * optics/interface_refraction
      * optics/prism
      * circuits/dc_linear
  - Invariant: Zero Parameter Fabrication:
      * Projectile arrow pixel length NEVER fabricated into velocity (m/s).
      * Thin lens distance to 'F' NEVER fabricated into focal length (m).
      * Mirror arc curvature NEVER fabricated into radius of curvature.
      * Refraction refractive index NEVER fabricated.
      * Prism apex angle NEVER defaulted to 60°.
      * Circuit visual proximity NEVER converted to electrical connectivity.
      * Unsupported mechanics NEVER mapped to runnable scenes.
"""
from __future__ import annotations

import unittest
from typing import Dict, Any

from shared.schemas.evidence import (
    ExtractionStatus,
    GroundingState,
    OCRExtractionResult,
    OCRToken,
    SourceBBox,
    SourcePoint,
    SourceLine,
)
from shared.schemas.ingestion import (
    BookEntity,
    BookIR,
    BookIRStatus,
    PhysicalValue,
)
from ai.evidence.grounding import (
    CircuitGrounder,
    GrounderRegistry,
    InterfaceRefractionGrounder,
    PendulumGrounder,
    PrismGrounder,
    ProjectileGrounder,
    SphericalMirrorGrounder,
    ThinLensGrounder,
    get_default_grounder_registry,
)
from ai.scene_compiler.physics_compiler import PhysicsCompiler


class TestPR06MultiDomainGrounding(unittest.TestCase):
    """Test suite for all 7 domain grounders and compiler anti-fabrication safety."""

    def setUp(self):
        self.registry = get_default_grounder_registry()
        self.compiler = PhysicsCompiler()

    def test_registry_covers_all_seven_subtypes(self):
        """Registry must list all 7 supported domain/subtype capabilities."""
        caps = self.registry.list_supported_capabilities()
        expected = [
            "circuits/dc_linear",
            "mechanics/pendulum",
            "mechanics/projectile",
            "optics/interface_refraction",
            "optics/prism",
            "optics/spherical_mirror",
            "optics/thin_lens",
        ]
        for exp in expected:
            self.assertIn(exp, caps)

    def test_pendulum_grounder_supports_and_grounds(self):
        """Pendulum grounder must ground bob and pivot without fabricating string length."""
        grounder = self.registry.find_grounder("mechanics", "pendulum")
        self.assertIsNotNone(grounder)
        self.assertTrue(isinstance(grounder, PendulumGrounder))

        book_ir = BookIR(
            domain="mechanics",
            subtype="pendulum",
            status=BookIRStatus.NEEDS_REVIEW,
            entities=[
                BookEntity(id="bob_1", type="bob"),
                BookEntity(id="pivot_1", type="pivot"),
            ],
            parameters={},  # No length parameter
        )
        cv_candidates = {
            "best_proposal": {
                "bob": {"center": SourcePoint(100.0, 200.0), "bounds": SourceBBox(90, 190, 20, 20)},
                "pivot": {"point": SourcePoint(100.0, 50.0)},
            }
        }
        outcome = grounder.ground(book_ir, cv_candidates, None, None, 400, 400)
        # Check compiler: missing length must keep NEEDS_REVIEW, never READY
        comp_res = self.compiler.compile(outcome.grounded_book_ir)
        self.assertEqual(comp_res.status, "NEEDS_REVIEW")
        self.assertIsNone(comp_res.scene)

    def test_projectile_grounder_anti_fabrication(self):
        """Arrow pixel length must NEVER become velocity magnitude (m/s)."""
        grounder = self.registry.find_grounder("mechanics", "projectile")
        self.assertIsNotNone(grounder)
        self.assertTrue(isinstance(grounder, ProjectileGrounder))

        book_ir = BookIR(
            domain="mechanics",
            subtype="projectile",
            status=BookIRStatus.NEEDS_REVIEW,
            entities=[
                BookEntity(id="p1", type="projectile_body"),
                BookEntity(id="v1", type="velocity_vector"),
            ],
            parameters={},
        )
        # Long velocity arrow (length = 250 px)
        cv_candidates = {
            "launch_point": SourcePoint(50.0, 300.0),
            "velocity_vector": {"p1": (50.0, 300.0), "p2": (250.0, 150.0), "length_px": 250.0},
        }
        outcome = grounder.ground(book_ir, cv_candidates, None, None, 500, 500)
        # Must NOT invent launch_speed = 250 m/s
        params = outcome.grounded_book_ir.parameters
        self.assertNotIn("launch_speed", params)
        # Compiler must reject as NEEDS_REVIEW
        comp_res = self.compiler.compile(outcome.grounded_book_ir)
        self.assertEqual(comp_res.status, "NEEDS_REVIEW")
        self.assertIsNone(comp_res.scene)

    def test_thin_lens_grounder_anti_fabrication(self):
        """Distance between lens and printed 'F' must NEVER be converted to meters."""
        grounder = self.registry.find_grounder("optics", "thin_lens")
        self.assertIsNotNone(grounder)
        self.assertTrue(isinstance(grounder, ThinLensGrounder))

        book_ir = BookIR(
            domain="optics",
            subtype="thin_lens",
            status=BookIRStatus.NEEDS_REVIEW,
            entities=[
                BookEntity(id="lens_1", type="lens"),
                BookEntity(id="f_pt", type="focal_point"),
            ],
            parameters={},
        )
        cv_candidates = {
            "lens_axis": {"x": 200.0},
            "principal_axis": {"y": 150.0},
            "f_markers": [SourcePoint(280.0, 150.0)],  # 80 px away
        }
        outcome = grounder.ground(book_ir, cv_candidates, None, None, 400, 300)
        # Physical focal length parameter must not be fabricated from 80 px
        self.assertNotIn("focal_length", outcome.grounded_book_ir.parameters)
        comp_res = self.compiler.compile(outcome.grounded_book_ir)
        self.assertEqual(comp_res.status, "NEEDS_REVIEW")
        self.assertIsNone(comp_res.scene)

    def test_spherical_mirror_grounder_anti_fabrication(self):
        """Mirror arc curvature must NEVER become physical radius of curvature."""
        grounder = self.registry.find_grounder("optics", "spherical_mirror")
        self.assertIsNotNone(grounder)
        self.assertTrue(isinstance(grounder, SphericalMirrorGrounder))

        book_ir = BookIR(
            domain="optics",
            subtype="spherical_mirror",
            status=BookIRStatus.NEEDS_REVIEW,
            entities=[BookEntity(id="m1", type="mirror_surface")],
            parameters={},
        )
        cv_candidates = {
            "pole": SourcePoint(100.0, 150.0),
            "estimated_radius_px": 120.0,
        }
        outcome = grounder.ground(book_ir, cv_candidates, None, None, 400, 300)
        self.assertNotIn("radius_of_curvature", outcome.grounded_book_ir.parameters)
        comp_res = self.compiler.compile(outcome.grounded_book_ir)
        self.assertEqual(comp_res.status, "NEEDS_REVIEW")
        self.assertIsNone(comp_res.scene)

    def test_refraction_grounder_anti_fabrication(self):
        """Interface refraction must NEVER fabricate refractive index n2."""
        grounder = self.registry.find_grounder("optics", "interface_refraction")
        self.assertIsNotNone(grounder)
        self.assertTrue(isinstance(grounder, InterfaceRefractionGrounder))

        book_ir = BookIR(
            domain="optics",
            subtype="interface_refraction",
            status=BookIRStatus.NEEDS_REVIEW,
            entities=[
                BookEntity(id="interface_1", type="interface"),
                BookEntity(id="ray_in", type="incident_ray"),
            ],
            parameters={},
        )
        cv_candidates = {
            "interface_line": {"y": 150.0},
            "incidence_point": SourcePoint(200.0, 150.0),
        }
        outcome = grounder.ground(book_ir, cv_candidates, None, None, 400, 300)
        self.assertNotIn("n2", outcome.grounded_book_ir.parameters)
        comp_res = self.compiler.compile(outcome.grounded_book_ir)
        self.assertEqual(comp_res.status, "NEEDS_REVIEW")
        self.assertIsNone(comp_res.scene)

    def test_prism_grounder_anti_fabrication(self):
        """Prism apex angle must NEVER default to 60° without evidence."""
        grounder = self.registry.find_grounder("optics", "prism")
        self.assertIsNotNone(grounder)
        self.assertTrue(isinstance(grounder, PrismGrounder))

        book_ir = BookIR(
            domain="optics",
            subtype="prism",
            status=BookIRStatus.NEEDS_REVIEW,
            entities=[BookEntity(id="prism_1", type="prism_body")],
            parameters={},
        )
        cv_candidates = {
            "apex_point": SourcePoint(200.0, 50.0),
        }
        outcome = grounder.ground(book_ir, cv_candidates, None, None, 400, 300)
        self.assertNotIn("apex_angle", outcome.grounded_book_ir.parameters)
        comp_res = self.compiler.compile(outcome.grounded_book_ir)
        self.assertEqual(comp_res.status, "NEEDS_REVIEW")
        self.assertIsNone(comp_res.scene)

    def test_circuits_grounder_anti_fabrication(self):
        """Visual proximity is NOT connectivity: missing wire path keeps circuit open/needs review."""
        grounder = self.registry.find_grounder("circuits", "dc_linear")
        self.assertIsNotNone(grounder)
        self.assertTrue(isinstance(grounder, CircuitGrounder))

        book_ir = BookIR(
            domain="circuits",
            subtype="dc_linear",
            status=BookIRStatus.NEEDS_REVIEW,
            entities=[
                BookEntity(id="r1", type="resistor"),
                BookEntity(id="v1", type="voltage_source"),
            ],
            parameters={},
        )
        # Components placed next to each other, but ZERO wire continuity
        cv_candidates = {
            "components": [
                {"id": "c1", "type": "resistor", "box": SourceBBox(100, 100, 50, 20)},
                {"id": "c2", "type": "voltage_source", "box": SourceBBox(110, 100, 50, 20)},
            ],
            "wire_paths": [],  # No connecting wires!
        }
        outcome = grounder.ground(book_ir, cv_candidates, None, None, 400, 300)
        # Circuit topology must NOT invent connection
        comp_res = self.compiler.compile(outcome.grounded_book_ir)
        self.assertEqual(comp_res.status, "NEEDS_REVIEW")
        self.assertIsNone(comp_res.scene)

    def test_circuits_grounder_authentic_e2e(self):
        """Valid wire continuity and authentic OCR tokens compile to runnable PhysicsScene."""
        grounder = self.registry.find_grounder("circuits", "dc_linear")
        self.assertIsNotNone(grounder)

        book_ir = BookIR(
            source_asset_id="asset_real_circ",
            figure_id="fig_real_circ",
            domain="circuits",
            subtype="dc_linear",
            status=BookIRStatus.NEEDS_REVIEW,
            entities=[
                BookEntity(id="r1", type="resistor"),
                BookEntity(id="v1", type="voltage_source"),
            ],
            parameters={},
        )
        # 2 components with real connecting wires (loop)
        cv_candidates = {
            "components": [
                {"id": "R1", "type": "resistor", "bbox": SourceBBox(300, 100, 50, 20), "center": SourcePoint(325, 110)},
                {"id": "V1", "type": "voltage_source", "bbox": SourceBBox(100, 100, 50, 20), "center": SourcePoint(125, 110)},
            ],
            "wires": [
                SourceLine(start=SourcePoint(100, 100), end=SourcePoint(350, 100)),
                SourceLine(start=SourcePoint(100, 200), end=SourcePoint(350, 200)),
            ],
            "rails_y": [100, 200],
            "branches_x": [100, 350],
        }
        ocr_result = OCRExtractionResult(
            status=ExtractionStatus.SUCCESS,
            tokens=[
                OCRToken(id="t1", raw_text="R1", confidence=0.95, bbox_source_px=SourceBBox(310, 80, 30, 15)),
                OCRToken(id="t2", raw_text="100Ω", confidence=0.95, bbox_source_px=SourceBBox(310, 125, 40, 15)),
                OCRToken(id="t3", raw_text="12 V", confidence=0.95, bbox_source_px=SourceBBox(110, 80, 35, 15)),
            ],
            provider="mock_ocr",
        )

        outcome = grounder.ground(book_ir, cv_candidates, ocr_result, source_width=500, source_height=400)
        grounded_ir = outcome.grounded_book_ir
        self.assertEqual(grounded_ir.status, BookIRStatus.READY_TO_COMPILE)
        self.assertIn("R1_resistance", grounded_ir.parameters)
        self.assertEqual(grounded_ir.parameters["R1_resistance"].value, 100.0)

        comp_res = self.compiler.compile(grounded_ir)
        self.assertEqual(comp_res.status, "READY")
        self.assertIsNotNone(comp_res.scene)
        self.assertEqual(comp_res.scene["domain"], "circuits")
        self.assertEqual(comp_res.scene["subtype"], "dc_linear")
        self.assertEqual(len(comp_res.scene["circuit"]["components"]), 2)

    def test_unsupported_mechanics_rejected(self):
        """Unsupported mechanics (e.g. spring, pulley, incline) must remain UNSUPPORTED with scene=null."""
        for unsupported_sub in ["spring", "pulley", "inclined_plane", "atwood_machine"]:
            book_ir = BookIR(
                domain="mechanics",
                subtype=unsupported_sub,
                status=BookIRStatus.UNSUPPORTED,
                entities=[],
            )
            grounder = self.registry.find_grounder("mechanics", unsupported_sub)
            self.assertIsNone(grounder, f"Unsupported subtype {unsupported_sub} must have no active grounder")
            comp_res = self.compiler.compile(book_ir)
            self.assertEqual(comp_res.status, "UNSUPPORTED")
            self.assertIsNone(comp_res.scene)


if __name__ == "__main__":
    unittest.main()

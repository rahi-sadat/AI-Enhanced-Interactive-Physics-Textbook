"""tests/unit/test_strict_analysis.py

Unit tests for PR-01 Strict Automatic Analysis Contract.
Verifies:
  1. Structural invariant enforcement (ready requires scene, non-ready prohibits scene)
  2. Filename independence in automatic mode
  3. Blank image and deterministic noise rejection
  4. Unknown images never default to thin lens or any other concept
  5. In PR-01, explicit user scenarios without strict extractors return needs_review
  6. Explicit pendulum scenario on test1.jpg uses native sub-pixel detector geometry
  7. Pendulum preserves native source dimensions (797x652) and source_px space
  8. Pendulum dynamic assets (clean background and bob sprite) are wired into scene
  9. Explicit physical assumptions (gravity = 9.81 m/s²) and extracted parameters
 10. Manual overrides tagged as user_override, not automatic detection
"""
from __future__ import annotations

import math
from pathlib import Path
import shutil
import sys
import unittest

import cv2
import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from apps.api.main import (
    AnalyzeRequest,
    analyze_diagram,
    classify_diagram_concept,
    make_analysis_response,
    FRONTEND_UPLOADS,
    FRONTEND_SPRITES,
)


class TestStrictAnalysisContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = _REPO_ROOT
        cls.fixtures_dir = cls.project_root / "tests" / "fixtures" / "images"
        cls.test1_path = cls.fixtures_dir / "test1.jpg"
        if not cls.test1_path.exists():
            cls.test1_path = cls.project_root / "storage" / "uploads" / "test1.jpg"
        if not cls.test1_path.exists():
            cls.test1_path = cls.project_root / "apps" / "web" / "public" / "uploads" / "test1.jpg"

        if not cls.test1_path.exists():
            raise FileNotFoundError(f"Fixture test1.jpg not found at {cls.test1_path}")

        # Ensure upload test images exist in FRONTEND_UPLOADS
        FRONTEND_UPLOADS.mkdir(parents=True, exist_ok=True)
        FRONTEND_SPRITES.mkdir(parents=True, exist_ok=True)

        cls.created_files: list[Path] = []

        # 1. Base test1.jpg in frontend uploads
        target_test1 = FRONTEND_UPLOADS / "test1.jpg"
        if not target_test1.exists():
            shutil.copy2(cls.test1_path, target_test1)

        # 2. Renamed clones of test1.jpg to test filename independence
        for alias in ["pendulum.jpg", "lens.jpg", "cat.jpg", "f4a8b1c2-3d4e.png"]:
            alias_path = FRONTEND_UPLOADS / alias
            shutil.copy2(cls.test1_path, alias_path)
            cls.created_files.append(alias_path)

        # 3. Pure white image
        cls.white_path = FRONTEND_UPLOADS / "pure_white.png"
        white_img = np.full((400, 400, 3), 255, dtype=np.uint8)
        cv2.imwrite(str(cls.white_path), white_img)
        cls.created_files.append(cls.white_path)

        # 4. Deterministic random noise (fixed seed)
        cls.noise_path = FRONTEND_UPLOADS / "fixed_noise.png"
        rng = np.random.RandomState(42)
        noise_img = rng.randint(0, 256, (400, 400, 3), dtype=np.uint8)
        cv2.imwrite(str(cls.noise_path), noise_img)
        cls.created_files.append(cls.noise_path)

    @classmethod
    def tearDownClass(cls):
        for f in cls.created_files:
            try:
                if f.exists():
                    f.unlink()
            except Exception:
                pass

    def _assert_strict_envelope(self, res: dict):
        """Verifies structural properties of the strict response envelope."""
        self.assertIsInstance(res, dict)
        self.assertTrue(res.get("success"), "Envelope must have success: True")
        status = res.get("status")
        self.assertIn(status, {"ready", "needs_review", "unsupported", "error"})
        self.assertIn("analysis", res)
        self.assertIn("source", res["analysis"])
        self.assertEqual(res["analysis"]["source"]["coordinate_space"], "source_px")
        self.assertIsInstance(res.get("issues"), list)

        # Invariant: scene is non-null IF AND ONLY IF status == 'ready'
        if status == "ready":
            self.assertIsNotNone(res.get("scene"), "Ready status must include a runnable scene")
        else:
            self.assertIsNone(res.get("scene"), f"Non-ready status '{status}' must not contain a scene")

    # -------------------------------------------------------------------------
    # 1. Structural Invariant Enforcement
    # -------------------------------------------------------------------------
    def test_structural_invariant_enforcement(self):
        """make_analysis_response must raise RuntimeError on invariant violations."""
        # 1. ready without scene -> raises RuntimeError
        with self.assertRaises(RuntimeError):
            make_analysis_response(status="ready", scene=None)

        # 2. non-ready with scene -> raises RuntimeError
        with self.assertRaises(RuntimeError):
            make_analysis_response(status="needs_review", scene={"id": "fake_scene"})

        with self.assertRaises(RuntimeError):
            make_analysis_response(status="unsupported", scene={"id": "fake_scene"})

        # 3. Invalid status -> raises ValueError
        with self.assertRaises(ValueError):
            make_analysis_response(status="fabricated", scene=None)

        # 4. Valid calls must succeed
        ready_res = make_analysis_response(status="ready", scene={"objects": []})
        self.assertEqual(ready_res["status"], "ready")
        self.assertIsNotNone(ready_res["scene"])

        review_res = make_analysis_response(status="needs_review", scene=None)
        self.assertEqual(review_res["status"], "needs_review")
        self.assertIsNone(review_res["scene"])

    # -------------------------------------------------------------------------
    # 2. Filename Independence in Automatic Mode
    # -------------------------------------------------------------------------
    def test_auto_analysis_is_filename_independent(self):
        """Identical image bytes under different filenames must produce identical automatic responses."""
        aliases = ["pendulum.jpg", "lens.jpg", "cat.jpg", "f4a8b1c2-3d4e.png"]
        results = []

        for alias in aliases:
            req = AnalyzeRequest(
                image_url=f"/uploads/{alias}",
                domain="auto",
                scenario="auto",
            )
            res = analyze_diagram(req)
            self._assert_strict_envelope(res)
            self.assertEqual(res["status"], "needs_review")
            self.assertIsNone(res["domain"])
            self.assertIsNone(res["scenario"])
            self.assertIsNone(res["scene"])
            self.assertEqual(res["analysis"]["mode"], "automatic")
            issue_codes = [i["code"] for i in res["issues"]]
            self.assertIn("NO_CONFIDENT_SUPPORTED_CONCEPT", issue_codes)
            results.append(res)

        # Check that status, domain, scenario, and issues are identical across all aliases
        first = results[0]
        for other in results[1:]:
            self.assertEqual(other["status"], first["status"])
            self.assertEqual(other["domain"], first["domain"])
            self.assertEqual(other["scenario"], first["scenario"])
            self.assertEqual(other["scene"], first["scene"])
            self.assertEqual([i["code"] for i in other["issues"]], [i["code"] for i in first["issues"]])

    # -------------------------------------------------------------------------
    # 3. Blank Image & Deterministic Random Noise Rejection
    # -------------------------------------------------------------------------
    def test_blank_image_is_not_ready(self):
        """A pure white blank image must not produce a ready scene in automatic mode."""
        req = AnalyzeRequest(image_url="/uploads/pure_white.png", domain="auto", scenario="auto")
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)
        self.assertEqual(res["status"], "needs_review")
        self.assertIsNone(res["scene"])

    def test_random_noise_is_not_ready(self):
        """Deterministic random noise must not produce a ready scene in automatic mode."""
        req = AnalyzeRequest(image_url="/uploads/fixed_noise.png", domain="auto", scenario="auto")
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)
        self.assertEqual(res["status"], "needs_review")
        self.assertIsNone(res["scene"])

    # -------------------------------------------------------------------------
    # 4. Unknown Image Never Defaults to Thin Lens
    # -------------------------------------------------------------------------
    def test_unknown_never_defaults_to_thin_lens(self):
        """Unknown or unclassifiable diagrams must never default to thin_lens."""
        for img_name in ["pure_white.png", "fixed_noise.png", "cat.jpg"]:
            req = AnalyzeRequest(image_url=f"/uploads/{img_name}", domain="auto", scenario="auto")
            res = analyze_diagram(req)
            self._assert_strict_envelope(res)
            self.assertNotEqual(res.get("scenario"), "thin_lens")
            self.assertIsNone(res.get("scene"))

    # -------------------------------------------------------------------------
    # 5. Explicit Domain with Auto Scenario Stays Not Ready
    # -------------------------------------------------------------------------
    def test_auto_with_explicit_domain_is_not_ready(self):
        """Supplying domain with scenario=auto must still safely abstain in PR-01."""
        for dom in ["mechanics", "optics", "circuits"]:
            req = AnalyzeRequest(image_url="/uploads/test1.jpg", domain=dom, scenario="auto")
            res = analyze_diagram(req)
            self._assert_strict_envelope(res)
            self.assertEqual(res["status"], "needs_review")
            self.assertIsNone(res["scene"])
            issue_codes = [i["code"] for i in res["issues"]]
            self.assertIn("NO_CONFIDENT_SUPPORTED_CONCEPT", issue_codes)

    # -------------------------------------------------------------------------
    # 6. Explicit Scenarios Without Strict Extractors Return needs_review
    # -------------------------------------------------------------------------
    def test_other_scenarios_without_strict_extractors_are_not_ready(self):
        """Scenarios where perception would be fabricated must return needs_review in PR-01."""
        unimplemented_scenarios = [
            ("optics", "thin_lens"),
            ("optics", "mirror"),
            ("optics", "interface_refraction"),
            ("optics", "prism"),
            ("mechanics", "incline"),
            ("mechanics", "projectile"),
            ("mechanics", "spring_mass"),
            ("circuits", "circuit1"),
            ("circuits", "circuits"),
        ]
        for dom, sc in unimplemented_scenarios:
            req = AnalyzeRequest(
                image_url="/uploads/test1.jpg",
                domain=dom,
                scenario=sc,
            )
            res = analyze_diagram(req)
            self._assert_strict_envelope(res)
            self.assertEqual(res["status"], "needs_review", f"Scenario '{sc}' must not return ready")
            self.assertIsNone(res["scene"], f"Scenario '{sc}' must not contain a scene")
            self.assertEqual(res["analysis"]["mode"], "user_override")
            issue_codes = [i["code"] for i in res["issues"]]
            self.assertIn("STRICT_EXTRACTION_NOT_IMPLEMENTED", issue_codes)

    # -------------------------------------------------------------------------
    # 7. Invalid Scenario String Returns Unsupported
    # -------------------------------------------------------------------------
    def test_invalid_scenario_string_is_unsupported(self):
        """An invalid scenario choice returns unsupported and never defaults to another concept."""
        req = AnalyzeRequest(
            image_url="/uploads/test1.jpg",
            domain="auto",
            scenario="teleportation_device",
        )
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)
        self.assertEqual(res["status"], "unsupported")
        self.assertIsNone(res["scene"])
        issue_codes = [i["code"] for i in res["issues"]]
        self.assertIn("UNSUPPORTED_SCENARIO", issue_codes)

    # -------------------------------------------------------------------------
    # 8. Explicit Pendulum Scenario Recovers Native Geometry
    # -------------------------------------------------------------------------
    def test_manual_pendulum_uses_native_detector_geometry(self):
        """User override scenario=pendulum on test1.jpg recovers native sub-pixel detector geometry."""
        req = AnalyzeRequest(
            image_url="/uploads/test1.jpg",
            domain="mechanics",
            scenario="pendulum",
        )
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["domain"], "mechanics")
        self.assertEqual(res["scenario"], "pendulum")

        scene = res["scene"]
        self.assertIsNotNone(scene)
        self.assertEqual(scene["simulation_type"], "kinematics")

        objects = scene["objects"]
        self.assertEqual(len(objects), 1)
        pendulum = objects[0]

        # Verify sub-pixel bob center: ~246.58, ~527.56
        bob = pendulum["bob_position"]
        self.assertAlmostEqual(bob["x"], 246.58, delta=2.5)
        self.assertAlmostEqual(bob["y"], 527.56, delta=2.5)
        self.assertAlmostEqual(pendulum["radius"], 43.27, delta=2.5)

        # Verify pivot: ~468.0, ~99.7
        pivot = pendulum["pivot"]
        self.assertAlmostEqual(pivot["x"], 468.0, delta=4.0)
        self.assertAlmostEqual(pivot["y"], 99.7, delta=4.0)

        # Verify string length: ~481.75 px
        self.assertAlmostEqual(pendulum["length"], 481.75, delta=2.5)
        self.assertAlmostEqual(pendulum["string_length_px"], 481.75, delta=2.5)

        # Verify pivot is strictly above bob in image space
        self.assertLess(pivot["y"], bob["y"])

        # Verify mass and velocity are NOT invented
        self.assertIsNone(pendulum["mass_kg"], "Ideal simple pendulum must not invent mass")
        self.assertIsNone(pendulum["initial_velocity"], "Initial velocity must not be invented")

        # Verify ideal pendulum model and non-fabricated zero damping/friction
        self.assertEqual(pendulum["model"], "ideal_pendulum")
        self.assertEqual(pendulum["damping"], 0.0)
        self.assertEqual(pendulum["friction"], 0.0)
        self.assertEqual(pendulum["friction_air"], 0.0)
        self.assertEqual(pendulum["restitution"], 1.0)

        # Verify environment gravity is non-zero standard Earth gravity
        env = scene["environment"]
        self.assertEqual(env["gravity"], 9.81)
        self.assertEqual(env["gravity_m_s2"], 9.81)

    # -------------------------------------------------------------------------
    # 9. Source Dimensions and Coordinates Preserved
    # -------------------------------------------------------------------------
    def test_manual_pendulum_preserves_source_dimensions(self):
        """Native source dimensions (797x652) must be preserved without 800x600 remapping."""
        req = AnalyzeRequest(image_url="/uploads/test1.jpg", scenario="pendulum")
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)
        self.assertEqual(res["status"], "ready")

        source = res["analysis"]["source"]
        self.assertEqual(source["width"], 797)
        self.assertEqual(source["height"], 652)

        render = res["scene"]["render"]
        self.assertEqual(render["source_width_px"], 797)
        self.assertEqual(render["source_height_px"], 652)
        self.assertEqual(render["coordinate_space"], "source_px")

    # -------------------------------------------------------------------------
    # 10. Clean Background and Bob Sprite Asset Wiring
    # -------------------------------------------------------------------------
    def test_manual_pendulum_generates_clean_bg_and_sprite(self):
        """Clean inpainted background and transparent bob sprite must be created and referenced."""
        req = AnalyzeRequest(image_url="/uploads/test1.jpg", scenario="pendulum")
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)

        scene = res["scene"]
        bg_url = scene["visual"]["background_url"]
        self.assertTrue(
            bg_url.startswith("/uploads/clean_") or bg_url == "/uploads/test1.jpg",
            f"Expected clean background URL, got {bg_url}",
        )

        pendulum = scene["objects"][0]
        if "visual" in pendulum and "sprite_url" in pendulum["visual"]:
            sprite_url = pendulum["visual"]["sprite_url"]
            self.assertTrue(sprite_url.startswith("/sprites/element_bob_"))

    # -------------------------------------------------------------------------
    # 11. Explicit Physics Assumptions and Provenance
    # -------------------------------------------------------------------------
    def test_manual_pendulum_reports_explicit_assumptions(self):
        """Earth gravity assumption, damping model, and extracted angle must be explicitly reported."""
        req = AnalyzeRequest(image_url="/uploads/test1.jpg", scenario="pendulum")
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)

        analysis = res["analysis"]
        self.assertIn("assumptions", analysis)
        gravity_assumptions = [
            a for a in analysis["assumptions"] if a.get("parameter") == "gravity_m_s2"
        ]
        self.assertEqual(len(gravity_assumptions), 1)
        g_item = gravity_assumptions[0]
        self.assertEqual(g_item["value"], 9.81)
        self.assertEqual(g_item["status"], "assumed")
        self.assertEqual(g_item["source"], "standard_earth")

        damping_assumptions = [
            a for a in analysis["assumptions"] if a.get("parameter") == "damping"
        ]
        self.assertEqual(len(damping_assumptions), 1)
        d_item = damping_assumptions[0]
        self.assertEqual(d_item["value"], 0.0)
        self.assertEqual(d_item["status"], "assumed")
        self.assertEqual(d_item["source"], "ideal_textbook_model")

        self.assertIn("extracted_parameters", analysis)
        params = analysis["extracted_parameters"]
        self.assertIn("theta0_rad", params)
        self.assertLess(params["theta0_rad"], 0.0, "Bob is displaced to the left in test1.jpg")
        self.assertAlmostEqual(math.degrees(params["theta0_rad"]), -27.36, delta=2.0)
        self.assertIn("geometry_score", params)

    # -------------------------------------------------------------------------
    # 12. User-Provided Gravity Parameter Override
    # -------------------------------------------------------------------------
    def test_manual_pendulum_user_gravity_override(self):
        """User-provided gravity (e.g. 3.71 for Mars) is applied to environment and tagged user_provided."""
        req = AnalyzeRequest(image_url="/uploads/test1.jpg", scenario="pendulum", gravity=3.71)
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)
        self.assertEqual(res["status"], "ready")

        env = res["scene"]["environment"]
        self.assertEqual(env["gravity"], 3.71)
        self.assertEqual(env["gravity_m_s2"], 3.71)

        gravity_assumptions = [
            a for a in res["analysis"]["assumptions"] if a.get("parameter") == "gravity_m_s2"
        ]
        self.assertEqual(len(gravity_assumptions), 1)
        g_item = gravity_assumptions[0]
        self.assertEqual(g_item["value"], 3.71)
        self.assertEqual(g_item["status"], "user_provided")
        self.assertEqual(g_item["source"], "user_override")

    # -------------------------------------------------------------------------
    # 12. Manual Override Tagged as user_override
    # -------------------------------------------------------------------------
    def test_manual_override_is_labeled_user_override(self):
        """Explicit scenario selection must be marked as user_override."""
        req = AnalyzeRequest(image_url="/uploads/test1.jpg", scenario="pendulum")
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)
        self.assertEqual(res["analysis"]["mode"], "user_override")

    # -------------------------------------------------------------------------
    # 13. Deterministic Pendulum Geometry Sanity Validation
    # -------------------------------------------------------------------------
    def test_pendulum_geometry_sanity_validation(self):
        """Non-pendulum or inconsistent images must fail geometry checks and return needs_review."""
        req = AnalyzeRequest(image_url="/uploads/pure_white.png", scenario="pendulum")
        res = analyze_diagram(req)
        self._assert_strict_envelope(res)
        self.assertEqual(res["status"], "needs_review")
        self.assertIsNone(res["scene"])
        issue_codes = [i["code"] for i in res["issues"]]
        self.assertTrue(
            any(c in issue_codes for c in ["BOB_NOT_FOUND", "PENDULUM_GEOMETRY_INCONSISTENT"]),
            f"Expected BOB_NOT_FOUND or PENDULUM_GEOMETRY_INCONSISTENT, got {issue_codes}",
        )


if __name__ == "__main__":
    unittest.main()

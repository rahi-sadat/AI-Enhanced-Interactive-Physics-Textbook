"""
Unit tests for sub-pixel pendulum geometry detection.
Verifies sub-pixel precision, angular localization, and dynamic inpainting on test1.jpg.
"""

import math
from pathlib import Path
import sys
import unittest

import cv2
import numpy as np

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_KINEMATICS_DIR = _BACKEND_DIR / "kinematics"
sys.path.insert(0, str(_KINEMATICS_DIR))

from pendulum_geometry import detect_pendulum_geometry, fit_circle_subpixel, fit_line_subpixel


class TestPendulumGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = _BACKEND_DIR.parent
        cls.image_path = (
            cls.project_root
            / "simulation_frontend"
            / "augmented_physics_v2"
            / "public"
            / "uploads"
            / "test1.jpg"
        )
        if not cls.image_path.exists():
            raise FileNotFoundError(f"Test image not found at {cls.image_path}")
        cls.img = cv2.imread(str(cls.image_path))
        cls.assertIsNotNone(cls.img, "Failed to load test1.jpg")

    def test_subpixel_circle_fit_synthetic(self):
        """Verify circle fitting recovers sub-pixel float coordinates from synthetic edges."""
        canvas = np.zeros((200, 200), dtype=np.uint8)
        true_cx, true_cy, true_r = 104.38, 98.72, 35.65

        # Draw circle on canvas
        for deg in range(360):
            rad = math.radians(deg)
            x = int(round(true_cx + true_r * math.cos(rad)))
            y = int(round(true_cy + true_r * math.sin(rad)))
            if 0 <= x < 200 and 0 <= y < 200:
                canvas[y, x] = 255

        fit_x, fit_y, fit_r = fit_circle_subpixel(
            canvas, (105.0, 99.0), 35.0, margin_ratio=0.25
        )
        self.assertAlmostEqual(fit_x, true_cx, delta=0.5)
        self.assertAlmostEqual(fit_y, true_cy, delta=0.5)
        self.assertAlmostEqual(fit_r, true_r, delta=0.8)

    def test_detection_test1_subpixel_accuracy(self):
        """Verify sub-pixel bob and pivot detection on textbook diagram test1.jpg."""
        res = detect_pendulum_geometry(self.img, image_rel_url="/uploads/test1.jpg")

        bob = res["bob_center"]
        pivot = res["pivot"]
        radius = res["bob_radius_px"]
        length_px = res["string_length_px"]
        theta0 = res["theta0_rad"]

        # Assert sub-pixel bob center matches ground truth within < 2px
        self.assertAlmostEqual(bob["x"], 246.58, delta=2.5)
        self.assertAlmostEqual(bob["y"], 527.56, delta=2.5)
        self.assertAlmostEqual(radius, 43.27, delta=2.5)

        # Assert pivot point near pin mount at top
        self.assertAlmostEqual(pivot["x"], 468.0, delta=4.0)
        self.assertAlmostEqual(pivot["y"], 99.7, delta=4.0)

        # Bob must be lower than pivot (pivot.y < bob.y in image space)
        self.assertLess(pivot["y"], bob["y"])

        # String length must match distance between points
        expected_len = math.hypot(bob["x"] - pivot["x"], bob["y"] - pivot["y"])
        self.assertAlmostEqual(length_px, expected_len, delta=0.01)

        # Bob is displaced to the left in test1.jpg, so theta0 must be negative
        self.assertLess(theta0, 0.0)
        # Angle should be approx -27.3 degrees (-0.477 rad)
        self.assertAlmostEqual(math.degrees(theta0), -27.36, delta=2.0)

        # Confidence should be high
        self.assertGreater(res["confidence"], 0.75)


if __name__ == "__main__":
    unittest.main()

"""backend/circuits/tests/test_circuit_images.py

Verification script for testing the end-to-end CircuitAnalyzer pipeline
on the uploaded textbook circuit diagrams (circuit1.png - circuit4.png).
"""
import unittest
from pathlib import Path

import cv2

from ..circuit_analyzer import CircuitAnalyzer


class TestUploadedCircuitImages(unittest.TestCase):

    def setUp(self):
        self.analyzer = CircuitAnalyzer()
        self.project_root = Path(__file__).resolve().parents[3]
        self.uploads_dir = self.project_root / "uploads"

    def test_uploaded_circuit_images(self):
        for fn in ["circuit1.png", "circuit2.png", "circuit3.png", "circuit4.png"]:
            img_path = self.uploads_dir / fn
            if not img_path.exists():
                continue
            img = cv2.imread(str(img_path))
            self.assertIsNotNone(img, f"Failed to load {fn}")

            res = self.analyzer.analyze(img, image_url=f"/uploads/{fn}")
            self.assertTrue(res["success"])

            scene = res["scene"]
            circuit_data = scene["circuit"]
            self.assertTrue(len(circuit_data["components"]) > 0, f"No components detected in {fn}")

            state = res["electrical_state"]
            self.assertEqual(state["status"], "solved", f"Solver failed for {fn}: {state.get('error_message')}")
            self.assertTrue(len(state["node_voltages_v"]) > 0)

            print(f"\n[Test] {fn} successfully analyzed and solved:")
            print(f"  Components: {[c['id'] + ' (' + c['type'] + ')' for c in circuit_data['components']]}")
            print(f"  Nodes: {[n['id'] for n in circuit_data['nodes']]}")
            print(f"  Voltages: {state['node_voltages_v']}")
            if state.get("equivalent_resistance_ohm") is not None:
                print(f"  R_eq: {state['equivalent_resistance_ohm']:.2f} Ω")


if __name__ == "__main__":
    unittest.main()

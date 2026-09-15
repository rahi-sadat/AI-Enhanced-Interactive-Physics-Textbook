"""backend/circuits/circuit_analyzer.py

High-level orchestrator for the Circuits domain backend.
Coordinates perception, parameter extraction, topological graph construction,
MNA solving, and equation derivation.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import cv2
import numpy as np

from .models import CircuitScene
from .parameters.circuit_ocr import HeuristicCircuitOCR
from .parameters.parameter_binder import bind_parameters_to_components
from .perception.component_detector import ComponentDetector
from .perception.junction_detector import JunctionDetector
from .perception.polarity_detector import PolarityDetector
from .perception.region_detector import detect_circuit_region
from .perception.text_detector import TextDetector
from .perception.wire_detector import WireDetector
from .scene.circuit_scene_builder import CircuitSceneBuilder
from .solver.equation_generator import generate_equations
from .solver.mna_solver import MNASolver
from .topology.topology_builder import build_topology
from .topology.topology_validator import validate_topology


class CircuitAnalyzer:
    """End-to-end circuit perception and simulation analyzer."""

    def __init__(self) -> None:
        self.text_detector = TextDetector()
        self.component_detector = ComponentDetector()
        self.polarity_detector = PolarityDetector()
        self.wire_detector = WireDetector()
        self.junction_detector = JunctionDetector()

    def analyze(
        self,
        image_bgr: np.ndarray,
        image_url: str = "",
        precision_mode: bool = True,
        manual_annotations: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Runs the complete perception and MNA analysis pipeline on an uploaded diagram image."""
        h, w = image_bgr.shape[:2]

        # 1. Detect diagram region (keeps source_px transform)
        cropped_img, crop_transform = detect_circuit_region(image_bgr)

        # 2. Text detection and masking
        text_mask, text_fragments = self.text_detector.detect(image_bgr)

        # 3. Component symbol detection
        components = self.component_detector.detect(image_bgr, text_mask=text_mask)

        # 4. Polarity assignment for sources
        for comp in components:
            if comp.type in ("voltage_source", "battery", "cell", "current_source"):
                self.polarity_detector.assign_polarity(comp)

        # 5. Wire skeleton and polyline extraction
        wires = self.wire_detector.detect(image_bgr, text_mask=text_mask)

        # 6. Junction classification
        junctions = self.junction_detector.detect(image_bgr, wires)
        ambiguities = [j.to_dict() for j in junctions if j.requires_confirmation]

        # 7. Topological graph construction (terminals + wires -> nodes)
        nodes, ref_node = build_topology(components, wires, image_width=w, image_height=h)

        # 8. Parameter binding (match OCR text values to candidate components)
        components = bind_parameters_to_components(components, text_fragments, image_width=w, image_height=h)

        # 9. Build canonical CircuitScene v3
        builder = CircuitSceneBuilder(source_width=w, source_height=h, background_url=image_url)
        scene = builder.build_scene(
            components=components,
            wires=wires,
            nodes=nodes,
            reference_node=ref_node,
            ambiguities=ambiguities,
        )

        # 10. Topology validation
        val_report = validate_topology(scene)

        # 11. MNA Electrical Solve
        mna = MNASolver(scene)
        state = mna.solve_dc()

        # 12. Equation derivation for AI Tutor
        equations = generate_equations(scene, state)

        return {
            "success": True,
            "scene": scene.to_dict(),
            "validation": val_report.to_dict(),
            "electrical_state": state.to_dict(),
            "equations": equations,
        }

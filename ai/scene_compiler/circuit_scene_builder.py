"""backend/circuits/scene/circuit_scene_builder.py

Builds Canonical CircuitScene v3 JSON from verified components, wires, and topological nodes.
Strictly adheres to source_px coordinate authority.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from engine.core.provenance import CircuitConfidence
except (ImportError, ValueError):
    try:
        from backend.core.provenance import CircuitConfidence
    except (ImportError, ValueError):
        from core.provenance import CircuitConfidence

try:
    from shared.schemas.circuit_models import CircuitScene, Component, Node, Wire
except (ImportError, ValueError):
    from ..models import CircuitScene, Component, Node, Wire


class CircuitSceneBuilder:
    """Constructs canonical CircuitScene data structures."""

    def __init__(self, source_width: int, source_height: int, background_url: str = "") -> None:
        self.source_width = source_width
        self.source_height = source_height
        self.background_url = background_url

    def build_scene(
        self,
        components: list[Component],
        wires: list[Wire],
        nodes: list[Node],
        reference_node: str = "N0",
        ambiguities: Optional[list[dict[str, Any]]] = None,
        confidence: Optional[CircuitConfidence] = None,
        subtype: str = "dc_linear",
    ) -> CircuitScene:
        """Create and return a canonical CircuitScene."""
        conf_dict = confidence.to_dict() if confidence else {
            "component_detection": 0.98,
            "terminal_detection": 0.96,
            "wire_extraction": 0.95,
            "topology": 0.92,
            "parameter_binding": 0.96,
            "overall": 0.92,
        }

        return CircuitScene(
            schema_version="3.0",
            domain="circuits",
            subtype=subtype,
            engine="mna",
            source_width=self.source_width,
            source_height=self.source_height,
            background_url=self.background_url,
            reference_node=reference_node,
            nodes=nodes,
            components=components,
            wires=wires,
            ambiguities=ambiguities or [],
            confidence=conf_dict,
            metadata={"generator": "AugmentedPhysics Circuit Engine v3"},
        )

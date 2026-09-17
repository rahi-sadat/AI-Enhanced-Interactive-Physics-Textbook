"""backend/circuits/parameters/parameter_binder.py

Associates extracted text fragments (e.g., "10 Ω", "12V", "R1 = 20 Ω")
with the correct visual components using multi-signal spatial-semantic scoring:
  Score = w_d * S_distance + w_t * S_type + w_o * S_orientation + w_l * S_label
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

try:
    from engine.circuits.circuit_registry import get_component_spec
except (ImportError, ValueError):
    from ..circuit_registry import get_component_spec

try:
    from shared.schemas.circuit_models import Component, Parameter
except (ImportError, ValueError):
    from ..models import Component, Parameter
from .value_parser import parse_circuit_parameter


@dataclass
class TextFragment:
    text: str
    center_x: float
    center_y: float
    bbox: list[float]  # [x1, y1, x2, y2]
    confidence: float = 0.95


def bind_parameters_to_components(
    components: list[Component],
    text_fragments: list[TextFragment],
    image_width: int = 800,
    image_height: int = 600,
) -> list[Component]:
    """Binds text parameter fragments to the most compatible component."""
    diag = math.hypot(image_width, image_height)

    for frag in text_fragments:
        parsed_param = parse_circuit_parameter(frag.text)
        if not parsed_param or parsed_param.value is None:
            continue

        best_comp: Optional[Component] = None
        best_score = -1.0

        for comp in components:
            spec = get_component_spec(comp.type)
            if not spec:
                continue

            target_param_name = spec["parameter"]
            if not target_param_name:
                continue

            # 1. Unit compatibility score (S_type): strictly 0.0 if incompatible!
            unit_family = spec["unit_family"]
            unit_score = 0.0
            if unit_family == "resistance" and parsed_param.unit == "ohm":
                unit_score = 1.0
            elif unit_family == "voltage" and parsed_param.unit == "V":
                unit_score = 1.0
            elif unit_family == "current" and parsed_param.unit == "A":
                unit_score = 1.0
            elif unit_family == "capacitance" and parsed_param.unit == "F":
                unit_score = 1.0

            if unit_score == 0.0:
                continue  # Never bind ohm to battery or volt to resistor!

            # 2. Distance score (S_distance): normalized exponential decay
            bx1, by1, bx2, by2 = comp.bbox_source_px
            comp_cx = (bx1 + bx2) / 2.0
            comp_cy = (by1 + by2) / 2.0
            dist = math.hypot(frag.center_x - comp_cx, frag.center_y - comp_cy)
            dist_score = max(0.0, 1.0 - (dist / (diag * 0.35)))

            # 3. Label matching score (S_label): e.g. "R1" in "R1 = 10 Ω"
            label_score = 0.0
            if comp.id.lower() in frag.text.lower():
                label_score = 1.0

            # Composite weighted score: S = 0.45*dist + 0.35*unit + 0.20*label
            total_score = 0.45 * dist_score + 0.35 * unit_score + 0.20 * label_score

            if total_score > best_score and total_score > 0.40:
                best_score = total_score
                best_comp = comp

        if best_comp is not None:
            spec = get_component_spec(best_comp.type)
            p_name = spec["parameter"]
            # Bind parameter with spatial bbox and confidence
            parsed_param.confidence = min(0.99, round(best_score, 4))
            parsed_param.bbox_source_px = frag.bbox
            best_comp.parameters[p_name] = parsed_param

    return components

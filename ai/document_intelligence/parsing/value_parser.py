"""backend/circuits/parameters/value_parser.py

Extracts and validates physical parameters from raw OCR/VLM text fragments.
Maps units to the corresponding component property family (resistance, voltage, current, capacitance).
"""
from __future__ import annotations

from typing import Optional

try:
    from engine.core.parameter_resolver import parse_si
except (ImportError, ValueError):
    try:
        from backend.core.parameter_resolver import parse_si
    except (ImportError, ValueError):
        from core.parameter_resolver import parse_si

try:
    from shared.schemas.circuit_models import Parameter
except (ImportError, ValueError):
    from ..models import Parameter


def parse_circuit_parameter(text: str, expected_family: Optional[str] = None) -> Optional[Parameter]:
    """Parse text into a circuit Parameter dataclass.
    
    Examples:
        "10 Ω"   -> Parameter(value=10.0, unit="ohm", source="ocr")
        "2.2 kΩ" -> Parameter(value=2200.0, unit="ohm", source="ocr")
        "12V"    -> Parameter(value=12.0, unit="V", source="ocr")
        "5 mA"   -> Parameter(value=0.005, unit="A", source="ocr")
        "470uF"  -> Parameter(value=0.00047, unit="F", source="ocr")
    """
    default_unit = None
    if expected_family == "resistance":
        default_unit = "ohm"
    elif expected_family == "voltage":
        default_unit = "V"
    elif expected_family == "current":
        default_unit = "A"
    elif expected_family == "capacitance":
        default_unit = "F"

    res = parse_si(text, default_unit=default_unit)
    if not res:
        return None

    return Parameter(
        value=res["value"],
        unit=res["unit"],
        source="ocr",
        confidence=0.95,
        raw_text=text,
    )

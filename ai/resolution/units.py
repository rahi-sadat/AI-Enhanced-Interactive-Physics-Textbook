"""PR-07 Safe Unit Engine and Dimensional Normalizer.

Provides strict, deterministic unit parsing, dimensional validation, and SI normalization
for user inputs, policy defaults, and OCR candidates.
Zero eval, zero parameter fabrication, finite float guarantees.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Set


@dataclass(frozen=True)
class UnitDefinition:
    symbol: str
    dimension: str
    scale_to_canonical: float  # Multiplier to reach canonical unit for dimension
    canonical_symbol: str


# Canonical units per dimension:
# length: "m"
# mass: "kg"
# time: "s"
# acceleration: "m/s²"
# velocity: "m/s"
# angle: "deg" (standard for diagram ray/pendulum orientation)
# voltage: "V"
# current: "A"
# resistance: "ohm"
# dimensionless / refractive_index: ""

CANONICAL_UNITS: Dict[str, str] = {
    "length": "m",
    "mass": "kg",
    "time": "s",
    "acceleration": "m/s²",
    "velocity": "m/s",
    "angle": "deg",
    "voltage": "V",
    "current": "A",
    "resistance": "ohm",
    "capacitance": "F",
    "damping": "1/s",
    "frequency": "Hz",
    "pixels": "px",
    "pixels_per_meter": "px/m",
    "scale": "px/m",
    "categorical": "",
    "dimensionless": "",
    "refractive_index": "",
}

# Unit tables mapping normalized symbol -> UnitDefinition
# Case-sensitive mapping for critical distinctions like mΩ (milliohm) vs MΩ (megaohm)
UNIT_TABLE: Dict[str, UnitDefinition] = {
    # Length (canonical: m)
    "m": UnitDefinition("m", "length", 1.0, "m"),
    "meter": UnitDefinition("meter", "length", 1.0, "m"),
    "meters": UnitDefinition("meters", "length", 1.0, "m"),
    "cm": UnitDefinition("cm", "length", 0.01, "m"),
    "centimeter": UnitDefinition("centimeter", "length", 0.01, "m"),
    "centimeters": UnitDefinition("centimeters", "length", 0.01, "m"),
    "mm": UnitDefinition("mm", "length", 0.001, "m"),
    "millimeter": UnitDefinition("millimeter", "length", 0.001, "m"),
    "millimeters": UnitDefinition("millimeters", "length", 0.001, "m"),
    "km": UnitDefinition("km", "length", 1000.0, "m"),
    "kilometer": UnitDefinition("kilometer", "length", 1000.0, "m"),
    "in": UnitDefinition("in", "length", 0.0254, "m"),
    "inch": UnitDefinition("inch", "length", 0.0254, "m"),
    "inches": UnitDefinition("inches", "length", 0.0254, "m"),
    "ft": UnitDefinition("ft", "length", 0.3048, "m"),
    "feet": UnitDefinition("feet", "length", 0.3048, "m"),
    "সেমি": UnitDefinition("সেমি", "length", 0.01, "m"),
    "মিটার": UnitDefinition("মিটার", "length", 1.0, "m"),

    # Mass (canonical: kg)
    "kg": UnitDefinition("kg", "mass", 1.0, "kg"),
    "kilogram": UnitDefinition("kilogram", "mass", 1.0, "kg"),
    "kilograms": UnitDefinition("kilograms", "mass", 1.0, "kg"),
    "g": UnitDefinition("g", "mass", 0.001, "kg"),
    "gram": UnitDefinition("gram", "mass", 0.001, "kg"),
    "grams": UnitDefinition("grams", "mass", 0.001, "kg"),
    "mg": UnitDefinition("mg", "mass", 1e-6, "kg"),
    "milligram": UnitDefinition("milligram", "mass", 1e-6, "kg"),
    "কেজি": UnitDefinition("কেজি", "mass", 1.0, "kg"),
    "গ্রাম": UnitDefinition("গ্রাম", "mass", 0.001, "kg"),

    # Time (canonical: s)
    "s": UnitDefinition("s", "time", 1.0, "s"),
    "sec": UnitDefinition("sec", "time", 1.0, "s"),
    "second": UnitDefinition("second", "time", 1.0, "s"),
    "seconds": UnitDefinition("seconds", "time", 1.0, "s"),
    "ms": UnitDefinition("ms", "time", 0.001, "s"),
    "millisecond": UnitDefinition("millisecond", "time", 0.001, "s"),
    "milliseconds": UnitDefinition("milliseconds", "time", 0.001, "s"),
    "min": UnitDefinition("min", "time", 60.0, "s"),
    "minute": UnitDefinition("minute", "time", 60.0, "s"),
    "minutes": UnitDefinition("minutes", "time", 60.0, "s"),
    "h": UnitDefinition("h", "time", 3600.0, "s"),
    "hr": UnitDefinition("hr", "time", 3600.0, "s"),
    "hour": UnitDefinition("hour", "time", 3600.0, "s"),
    "hours": UnitDefinition("hours", "time", 3600.0, "s"),

    # Damping & Frequency (canonical: 1/s, Hz)
    "1/s": UnitDefinition("1/s", "damping", 1.0, "1/s"),
    "s^-1": UnitDefinition("s^-1", "damping", 1.0, "1/s"),
    "s_inv": UnitDefinition("s_inv", "damping", 1.0, "1/s"),
    "hz": UnitDefinition("hz", "frequency", 1.0, "Hz"),
    "Hz": UnitDefinition("Hz", "frequency", 1.0, "Hz"),
    "rad/s": UnitDefinition("rad/s", "angular_frequency", 1.0, "rad/s"),

    # Acceleration (canonical: m/s²)
    "m/s²": UnitDefinition("m/s²", "acceleration", 1.0, "m/s²"),
    "m/s^2": UnitDefinition("m/s^2", "acceleration", 1.0, "m/s²"),
    "m/s2": UnitDefinition("m/s2", "acceleration", 1.0, "m/s²"),
    "cm/s²": UnitDefinition("cm/s²", "acceleration", 0.01, "m/s²"),
    "cm/s^2": UnitDefinition("cm/s^2", "acceleration", 0.01, "m/s²"),
    "cm/s2": UnitDefinition("cm/s2", "acceleration", 0.01, "m/s²"),

    # Velocity (canonical: m/s)
    "m/s": UnitDefinition("m/s", "velocity", 1.0, "m/s"),
    "km/h": UnitDefinition("km/h", "velocity", 1.0 / 3.6, "m/s"),
    "cm/s": UnitDefinition("cm/s", "velocity", 0.01, "m/s"),

    # Angle (canonical: deg)
    "deg": UnitDefinition("deg", "angle", 1.0, "deg"),
    "degree": UnitDefinition("degree", "angle", 1.0, "deg"),
    "degrees": UnitDefinition("degrees", "angle", 1.0, "deg"),
    "°": UnitDefinition("°", "angle", 1.0, "deg"),
    "rad": UnitDefinition("rad", "angle", 180.0 / math.pi, "deg"),
    "radian": UnitDefinition("radian", "angle", 180.0 / math.pi, "deg"),
    "radians": UnitDefinition("radians", "angle", 180.0 / math.pi, "deg"),
    "ডিগ্রি": UnitDefinition("ডিগ্রি", "angle", 1.0, "deg"),
    "ডিগ্রী": UnitDefinition("ডিগ্রী", "angle", 1.0, "deg"),

    # Voltage (canonical: V)
    "V": UnitDefinition("V", "voltage", 1.0, "V"),
    "v": UnitDefinition("v", "voltage", 1.0, "V"),
    "volt": UnitDefinition("volt", "voltage", 1.0, "V"),
    "volts": UnitDefinition("volts", "voltage", 1.0, "V"),
    "mV": UnitDefinition("mV", "voltage", 0.001, "V"),
    "mv": UnitDefinition("mv", "voltage", 0.001, "V"),
    "kV": UnitDefinition("kV", "voltage", 1000.0, "V"),
    "kv": UnitDefinition("kv", "voltage", 1000.0, "V"),
    "ভোল্ট": UnitDefinition("ভোল্ট", "voltage", 1.0, "V"),

    # Current (canonical: A)
    "A": UnitDefinition("A", "current", 1.0, "A"),
    "a": UnitDefinition("a", "current", 1.0, "A"),
    "amp": UnitDefinition("amp", "current", 1.0, "A"),
    "amps": UnitDefinition("amps", "current", 1.0, "A"),
    "ampere": UnitDefinition("ampere", "current", 1.0, "A"),
    "amperes": UnitDefinition("amperes", "current", 1.0, "A"),
    "mA": UnitDefinition("mA", "current", 0.001, "A"),
    "ma": UnitDefinition("ma", "current", 0.001, "A"),
    "uA": UnitDefinition("uA", "current", 1e-6, "A"),
    "µA": UnitDefinition("µA", "current", 1e-6, "A"),
    "μA": UnitDefinition("μA", "current", 1e-6, "A"),
    "kA": UnitDefinition("kA", "current", 1000.0, "A"),
    "অ্যাম্পিয়ার": UnitDefinition("অ্যাম্পিয়ার", "current", 1.0, "A"),

    # Resistance (canonical: ohm)
    "ohm": UnitDefinition("ohm", "resistance", 1.0, "ohm"),
    "ohms": UnitDefinition("ohms", "resistance", 1.0, "ohm"),
    "Ω": UnitDefinition("Ω", "resistance", 1.0, "ohm"),
    "kΩ": UnitDefinition("kΩ", "resistance", 1000.0, "ohm"),
    "kohm": UnitDefinition("kohm", "resistance", 1000.0, "ohm"),
    "kohms": UnitDefinition("kohms", "resistance", 1000.0, "ohm"),
    "KΩ": UnitDefinition("KΩ", "resistance", 1000.0, "ohm"),
    "MΩ": UnitDefinition("MΩ", "resistance", 1e6, "ohm"),
    "Mohm": UnitDefinition("Mohm", "resistance", 1e6, "ohm"),
    "Mohms": UnitDefinition("Mohms", "resistance", 1e6, "ohm"),
    "mΩ": UnitDefinition("mΩ", "resistance", 1e-3, "ohm"),
    "mohm": UnitDefinition("mohm", "resistance", 1e-3, "ohm"),
    "ওহম": UnitDefinition("ওহম", "resistance", 1.0, "ohm"),

    # Capacitance (canonical: F)
    "F": UnitDefinition("F", "capacitance", 1.0, "F"),
    "farad": UnitDefinition("farad", "capacitance", 1.0, "F"),
    "uF": UnitDefinition("uF", "capacitance", 1e-6, "F"),
    "µF": UnitDefinition("µF", "capacitance", 1e-6, "F"),
    "μF": UnitDefinition("μF", "capacitance", 1e-6, "F"),
    "nF": UnitDefinition("nF", "capacitance", 1e-9, "F"),
    "pF": UnitDefinition("pF", "capacitance", 1e-12, "F"),

    # Pixels & Calibration Scale
    "px": UnitDefinition("px", "pixels", 1.0, "px"),
    "pixel": UnitDefinition("pixel", "pixels", 1.0, "px"),
    "pixels": UnitDefinition("pixels", "pixels", 1.0, "px"),
    "px/m": UnitDefinition("px/m", "pixels_per_meter", 1.0, "px/m"),
    "pixel/m": UnitDefinition("pixel/m", "pixels_per_meter", 1.0, "px/m"),
    "pixels/m": UnitDefinition("pixels/m", "pixels_per_meter", 1.0, "px/m"),

    # Dimensionless
    "": UnitDefinition("", "dimensionless", 1.0, ""),
    "none": UnitDefinition("none", "dimensionless", 1.0, ""),
    "dimensionless": UnitDefinition("dimensionless", "dimensionless", 1.0, ""),
}


@dataclass(frozen=True)
class ParsedQuantity:
    success: bool
    raw_input: str
    numeric_value: Optional[float] = None
    canonical_value: Optional[float] = None
    entered_unit: Optional[str] = None
    canonical_unit: Optional[str] = None
    dimension: Optional[str] = None
    error: Optional[str] = None


class UnitEngine:
    """Strict, deterministic physical unit and quantity parser."""

    _QUANTITY_RE = re.compile(
        r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(.*?)\s*$"
    )

    @classmethod
    def lookup_unit(cls, unit_str: str) -> Optional[UnitDefinition]:
        """Look up unit definition preserving case first, falling back to lower case."""
        if not unit_str:
            return UNIT_TABLE[""]
        
        trimmed = unit_str.strip()
        if trimmed in UNIT_TABLE:
            return UNIT_TABLE[trimmed]
        
        lower = trimmed.lower()
        if lower in UNIT_TABLE:
            return UNIT_TABLE[lower]
        
        return None

    @classmethod
    def parse_quantity(
        cls,
        value_input: object,
        unit_input: Optional[str] = None,
        expected_dimension: Optional[str] = None,
    ) -> ParsedQuantity:
        """Parse raw user input or parameter value into a normalized physical quantity.

        Args:
            value_input: number or string (e.g., 0.8, "80 cm", "12V", "9.80665 m/s²")
            unit_input: optional explicit unit string if separate
            expected_dimension: expected physical dimension (e.g. 'length', 'resistance')
        """
        raw_str = str(value_input).strip() if value_input is not None else ""
        if not raw_str:
            return ParsedQuantity(
                success=False,
                raw_input=str(value_input),
                error="Empty input value provided.",
            )

        # Check for categorical/string dimensions (e.g. concavity, lens_type, materials)
        if (
            expected_dimension in ("categorical", "string")
            or raw_str.lower() in ("concave", "convex", "plane", "converging", "diverging")
        ):
            return ParsedQuantity(
                success=True,
                raw_input=raw_str,
                numeric_value=None,
                canonical_value=raw_str.lower(),
                entered_unit="",
                canonical_unit="",
                dimension="categorical",
            )

        numeric_val: Optional[float] = None
        unit_str: str = (unit_input or "").strip()

        # If numeric input passed directly
        if isinstance(value_input, (int, float)) and not isinstance(value_input, bool):
            numeric_val = float(value_input)
        else:
            # Parse regex
            match = cls._QUANTITY_RE.match(raw_str)
            if match:
                num_part, embedded_unit = match.groups()
                try:
                    numeric_val = float(num_part)
                except ValueError:
                    return ParsedQuantity(
                        success=False,
                        raw_input=raw_str,
                        error=f"Cannot parse '{num_part}' as a valid number.",
                    )
                if embedded_unit:
                    if unit_str and unit_str.lower() != embedded_unit.lower():
                        return ParsedQuantity(
                            success=False,
                            raw_input=raw_str,
                            error=f"Conflicting units specified: embedded '{embedded_unit}' vs explicit '{unit_str}'.",
                        )
                    unit_str = embedded_unit
            else:
                # Could be pure number string with complex formatting
                try:
                    numeric_val = float(raw_str)
                except ValueError:
                    return ParsedQuantity(
                        success=False,
                        raw_input=raw_str,
                        error=f"Unrecognized quantity format: '{raw_str}'.",
                    )

        # Check for NaN or Inf
        if numeric_val is None or not math.isfinite(numeric_val):
            return ParsedQuantity(
                success=False,
                raw_input=raw_str,
                error=f"Invalid non-finite number: {numeric_val}",
            )

        # Dimension and unit resolution
        unit_def = cls.lookup_unit(unit_str)
        if unit_def is None and unit_str != "":
            return ParsedQuantity(
                success=False,
                raw_input=raw_str,
                numeric_value=numeric_val,
                entered_unit=unit_str,
                error=f"Unsupported unit: '{unit_str}'.",
            )

        dimension = unit_def.dimension if unit_def else (expected_dimension or "dimensionless")
        
        # If no unit specified but expected_dimension given, default unit to expected canonical
        if not unit_str and expected_dimension:
            canonical = CANONICAL_UNITS.get(expected_dimension, "")
            unit_def = cls.lookup_unit(canonical)
            dimension = expected_dimension
            unit_str = canonical

        if expected_dimension and dimension != expected_dimension and dimension != "dimensionless":
            return ParsedQuantity(
                success=False,
                raw_input=raw_str,
                numeric_value=numeric_val,
                entered_unit=unit_str,
                dimension=dimension,
                error=f"Dimension mismatch: expected '{expected_dimension}', got '{dimension}' (unit '{unit_str}').",
            )

        scale = unit_def.scale_to_canonical if unit_def else 1.0
        canonical_sym = unit_def.canonical_symbol if unit_def else (CANONICAL_UNITS.get(dimension, ""))
        canonical_val = numeric_val * scale

        if not math.isfinite(canonical_val):
            return ParsedQuantity(
                success=False,
                raw_input=raw_str,
                error="Normalized quantity resulted in non-finite value.",
            )

        return ParsedQuantity(
            success=True,
            raw_input=raw_str,
            numeric_value=numeric_val,
            canonical_value=canonical_val,
            entered_unit=unit_str,
            canonical_unit=canonical_sym,
            dimension=dimension,
        )

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert a numeric value between compatible units."""
        u_from = cls.lookup_unit(from_unit)
        u_to = cls.lookup_unit(to_unit)
        if not u_from or not u_to:
            return None
        if u_from.dimension != u_to.dimension:
            return None
        # Convert from -> canonical -> to
        canonical = value * u_from.scale_to_canonical
        converted = canonical / u_to.scale_to_canonical
        return converted if math.isfinite(converted) else None

    @classmethod
    def validate_range(
        cls,
        value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        must_be_positive: bool = False,
        allow_zero: bool = False,
        param_name: str = "value",
    ) -> Optional[str]:
        """Validate numeric range constraints."""
        if not isinstance(value, (int, float)):
            return None
        if not math.isfinite(value):
            return f"{param_name} must be a finite number."
        if must_be_positive and not allow_zero and value <= 0:
            return f"{param_name} must be strictly positive (> 0), got {value}."
        if must_be_positive and allow_zero and value < 0:
            return f"{param_name} must be non-negative (>= 0), got {value}."
        if min_value is not None and value < min_value:
            return f"{param_name} must be >= {min_value}, got {value}."
        if max_value is not None and value > max_value:
            return f"{param_name} must be <= {max_value}, got {value}."
        return None

"""backend/core/parameter_resolver.py

Robust SI unit and prefix resolver shared across physics domains.
Supports resistance (ohm, Ω), voltage (V), current (A), capacitance (F), and inductance (H).
Preserves case-sensitivity for SI prefixes:
  - m = 1e-3 (milli)
  - M = 1e6  (mega)
  - k/K = 1e3 (kilo)
  - u/µ/μ = 1e-6 (micro)
  - n = 1e-9 (nano)
  - p = 1e-12 (pico)
"""
from __future__ import annotations

import re
from typing import Optional, TypedDict


class ParsedSI(TypedDict):
    value: float
    unit: str
    prefix: str
    multiplier: float
    raw: str


PREFIX_MULTIPLIERS = {
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "µ": 1e-6,
    "μ": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "K": 1e3,
    "M": 1e6,
    "G": 1e9,
}

UNIT_CANONICAL = {
    "ohm": "ohm",
    "ohms": "ohm",
    "ω": "ohm",
    "Ω": "ohm",
    "Ω": "ohm",
    "v": "V",
    "volt": "V",
    "volts": "V",
    "a": "A",
    "amp": "A",
    "amps": "A",
    "ampere": "A",
    "f": "F",
    "farad": "F",
    "h": "H",
    "henry": "H",
    "w": "W",
    "watt": "W",
}


def parse_si(text: str, default_unit: Optional[str] = None) -> Optional[ParsedSI]:
    """Parse text representation of an SI value into a float and canonical unit.
    
    Examples:
        '2.2 kΩ' -> {'value': 2200.0, 'unit': 'ohm', ...}
        '12V'    -> {'value': 12.0, 'unit': 'V', ...}
        '5 mA'   -> {'value': 0.005, 'unit': 'A', ...}
        '100MΩ'  -> {'value': 1e8, 'unit': 'ohm', ...}
        '4.7 uF' -> {'value': 4.7e-6, 'unit': 'F', ...}
    """
    if not text or not isinstance(text, str):
        return None

    cleaned = text.strip().replace(",", ".")

    # Match: optional +/- , float number , optional prefix , optional unit
    # Note: prefix is case-sensitive for m vs M
    pattern = (
        r"^([+-]?\d*(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*"
        r"([pnuµμmkKMG]?)\s*"
        r"(Ω|Ω|ohm|ohms|V|v|volt|volts|A|a|amp|amps|ampere|F|f|farad|H|h|henry|W|w|watt)?$"
    )

    match = re.match(pattern, cleaned)
    if not match:
        # Fallback search within text if mixed with words (e.g. "R1 = 10 Ω")
        search_pattern = (
            r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*"
            r"([pnuµμmkKMG]?)\s*"
            r"(Ω|Ω|ohm|ohms|V|volt|volts|A|amp|amps|F|farad|H|henry|W|watt)"
        )
        match = re.search(search_pattern, cleaned)
        if not match:
            return None

    val_str = match.group(1)
    prefix_str = match.group(2) or ""
    unit_str = match.group(3) or default_unit or ""

    if not val_str or val_str in ("+", "-"):
        return None

    try:
        raw_num = float(val_str)
    except ValueError:
        return None

    multiplier = PREFIX_MULTIPLIERS.get(prefix_str, 1.0)
    canonical_unit = (
        UNIT_CANONICAL.get(unit_str)
        or UNIT_CANONICAL.get(unit_str.lower())
        or (default_unit or "")
    )

    return {
        "value": raw_num * multiplier,
        "unit": canonical_unit,
        "prefix": prefix_str,
        "multiplier": multiplier,
        "raw": text,
    }


def format_si(value: float, unit: str, sig_figs: int = 3) -> str:
    """Format a numerical value into appropriate engineering SI notation.
    
    Examples:
        0.005, 'A' -> '5.00 mA'
        15000, 'ohm' -> '15.0 kΩ'
        12.0, 'V' -> '12.0 V'
    """
    if value == 0:
        unit_display = "Ω" if unit.lower() in ("ohm", "Ω") else unit
        return f"0 {unit_display}"

    abs_val = abs(value)
    sign = "-" if value < 0 else ""

    if abs_val >= 1e9:
        scaled, pfx = abs_val / 1e9, "G"
    elif abs_val >= 1e6:
        scaled, pfx = abs_val / 1e6, "M"
    elif abs_val >= 1e3:
        scaled, pfx = abs_val / 1e3, "k"
    elif abs_val >= 1:
        scaled, pfx = abs_val, ""
    elif abs_val >= 1e-3:
        scaled, pfx = abs_val * 1e3, "m"
    elif abs_val >= 1e-6:
        scaled, pfx = abs_val * 1e6, "μ"
    elif abs_val >= 1e-9:
        scaled, pfx = abs_val * 1e9, "n"
    else:
        scaled, pfx = abs_val * 1e12, "p"

    unit_display = "Ω" if unit.lower() in ("ohm", "Ω") else unit
    return f"{sign}{scaled:.{sig_figs}g} {pfx}{unit_display}".strip()

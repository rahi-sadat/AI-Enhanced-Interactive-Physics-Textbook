"""PR-06 Physical Value Parser and OCR Normalization.

Extracts physical value candidates from OCR tokens without parameter fabrication.
Preserves raw OCR text separately from normalized candidates.
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from shared.schemas.evidence import OCRToken, ParsedPhysicalValueCandidate

# Common OCR character confusions in technical diagrams
OCR_REPLACEMENTS = [
    (r"(?<=\d)[oO](?=\s*(?:Ω|ohm|V|A|m|s|g|kg|cm|Hz|hz))", "0"),   # "1O Ω" -> "10 Ω"
    (r"(?<=\s)[oO](?=\d)", "0"),                                   # "O5 m" -> "05 m"
    (r"^[oO](?=\d)", "0"),
    (r"(?<=\d)[lI](?=\d)", "1"),                                   # "1l5 V" -> "115 V"
    (r"^[lI](?=\d)", "1"),
]

# Canonical Unit Normalization Mapping
UNIT_MAP = {
    # Length
    "m": ("m", "length", 1.0),
    "meter": ("m", "length", 1.0),
    "meters": ("m", "length", 1.0),
    "cm": ("cm", "length", 0.01),
    "centimeter": ("cm", "length", 0.01),
    "centimeters": ("cm", "length", 0.01),
    "mm": ("mm", "length", 0.001),
    "millimeter": ("mm", "length", 0.001),
    "km": ("km", "length", 1000.0),

    # Angle
    "°": ("°", "angle", 1.0),
    "deg": ("°", "angle", 1.0),
    "degree": ("°", "angle", 1.0),
    "degrees": ("°", "angle", 1.0),
    "rad": ("rad", "angle", 1.0),
    "radian": ("rad", "angle", 1.0),
    "radians": ("rad", "angle", 1.0),

    # Mass
    "kg": ("kg", "mass", 1.0),
    "kilogram": ("kg", "mass", 1.0),
    "kilograms": ("kg", "mass", 1.0),
    "g": ("g", "mass", 0.001),
    "gram": ("g", "mass", 0.001),
    "grams": ("g", "mass", 0.001),

    # Time
    "s": ("s", "time", 1.0),
    "sec": ("s", "time", 1.0),
    "second": ("s", "time", 1.0),
    "seconds": ("s", "time", 1.0),

    # Voltage
    "v": ("V", "voltage", 1.0),
    "volt": ("V", "voltage", 1.0),
    "volts": ("V", "voltage", 1.0),
    "mv": ("mV", "voltage", 0.001),
    "kv": ("kV", "voltage", 1000.0),

    # Resistance
    "ω": ("ohm", "resistance", 1.0),
    "ohm": ("ohm", "resistance", 1.0),
    "ohms": ("ohm", "resistance", 1.0),
    "kω": ("kohm", "resistance", 1000.0),
    "kohm": ("kohm", "resistance", 1000.0),
    "kΩ": ("kohm", "resistance", 1000.0),
    "mω": ("Mohm", "resistance", 1e6),
    "mohm": ("Mohm", "resistance", 1e6),
    "mΩ": ("Mohm", "resistance", 1e6),

    # Capacitance
    "f": ("F", "capacitance", 1.0),
    "farad": ("F", "capacitance", 1.0),
    "uf": ("uF", "capacitance", 1e-6),
    "µf": ("uF", "capacitance", 1e-6),
    "μf": ("uF", "capacitance", 1e-6),
    "pf": ("pF", "capacitance", 1e-12),
    "nf": ("nF", "capacitance", 1e-9),

    # Current
    "a": ("A", "current", 1.0),
    "amp": ("A", "current", 1.0),
    "amps": ("A", "current", 1.0),
    "ma": ("mA", "current", 0.001),
    "ua": ("uA", "current", 1e-6),
    "µa": ("uA", "current", 1e-6),
    "μa": ("uA", "current", 1e-6),

    # Velocity & Acceleration
    "m/s": ("m/s", "velocity", 1.0),
    "km/h": ("km/h", "velocity", 1.0 / 3.6),
    "m/s²": ("m/s²", "acceleration", 1.0),
    "m/s^2": ("m/s²", "acceleration", 1.0),
    "m/s2": ("m/s²", "acceleration", 1.0),

    # Bangla Units
    "সেমি": ("cm", "length", 0.01),
    "মিটার": ("m", "length", 1.0),
    "ভোল্ট": ("V", "voltage", 1.0),
    "ওহম": ("ohm", "resistance", 1.0),
    "অ্যাম্পিয়ার": ("A", "current", 1.0),
    "গ্রাম": ("g", "mass", 0.001),
    "কেজি": ("kg", "mass", 1.0),
    "ডিগ্রী": ("deg", "angle", 1.0),
    "ডিগ্রি": ("deg", "angle", 1.0),
}

# Standalone Physics Symbols (Latin & Greek)
STANDALONE_SYMBOLS = {
    "l": ("length_symbol", "L"),
    "m": ("mass_symbol", "m"),
    "g": ("gravity_symbol", "g"),
    "θ": ("angle_symbol", "θ"),
    "theta": ("angle_symbol", "θ"),
    "α": ("angle_symbol", "α"),
    "alpha": ("angle_symbol", "α"),
    "β": ("angle_symbol", "β"),
    "beta": ("angle_symbol", "β"),
    "Δ": ("delta_symbol", "Δ"),
    "delta": ("delta_symbol", "Δ"),
    "t": ("period_or_tension_symbol", "T"),
    "f": ("focal_or_force_symbol", "F"),
    "2f": ("two_f_symbol", "2F"),
    "c": ("center_of_curvature_symbol", "C"),
    "r": ("resistance_symbol", "R"),
    "r1": ("resistor_label", "R1"),
    "r2": ("resistor_label", "R2"),
    "r3": ("resistor_label", "R3"),
    "v": ("voltage_or_velocity_symbol", "V"),
    "v1": ("voltage_source_label", "V1"),
    "u": ("initial_velocity_symbol", "u"),
    "a": ("acceleration_symbol", "a"),
    "λ": ("wavelength_symbol", "λ"),
    "lambda": ("wavelength_symbol", "λ"),
    "μ": ("friction_or_micro_symbol", "μ"),
    "mu": ("friction_or_micro_symbol", "μ"),
    "ω": ("angular_velocity_symbol", "ω"),
    "omega": ("angular_velocity_symbol", "ω"),
    "ρ": ("density_or_resistivity_symbol", "ρ"),
    "rho": ("density_or_resistivity_symbol", "ρ"),
    "π": ("pi_symbol", "π"),
    "pi": ("pi_symbol", "π"),
    "φ": ("phi_symbol", "φ"),
    "ϕ": ("phi_symbol", "ϕ"),
    "phi": ("phi_symbol", "φ"),
    "Ω": ("resistance_symbol", "Ω"),
    "ohm": ("resistance_symbol", "Ω"),
}

BENGALI_DIGITS_TABLE = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def bengali_digits_to_ascii(text: str) -> str:
    """Convert Bengali numerals (০-৯) to ASCII digits (0-9)."""
    return text.translate(BENGALI_DIGITS_TABLE)


def normalize_ocr_text(raw_text: str) -> str:
    """Produce a normalized text candidate with Bengali numeral translation and OCR cleanup."""
    text = raw_text.strip()
    # Translate Bengali digits
    text = text.translate(BENGALI_DIGITS_TABLE)
    for pattern, repl in OCR_REPLACEMENTS:
        text = re.sub(pattern, repl, text)
    return text


def parse_physical_value_candidate(token: OCRToken) -> List[ParsedPhysicalValueCandidate]:
    """Parse an OCR token into zero, one, or more physical value candidates.

    Handles:
      1. Quantity expressions: "20 cm", "45°", "12 V", "10 Ω", "1.5 m/s", "g = 9.8 m/s²", "২০ সেমি"
      2. Variable declarations: "L = 50 cm", "m = 250 g", "θ = 30°", "R1 = 2 kΩ", "n = 1.50"
      3. Standalone symbols: "L", "m", "g", "θ", "T", "F", "2F", "R1", "u", "v"
      4. Alternative interpretations from candidateAlternatives
    """
    candidates: List[ParsedPhysicalValueCandidate] = []
    raw = token.raw_text.strip()
    normalized = normalize_ocr_text(raw)
    token.normalized_text = normalized

    clean_lower = normalized.lower().replace(" ", "")

    # 1. Check for standalone symbols (no numbers)
    if clean_lower in STANDALONE_SYMBOLS:
        cat, standard_sym = STANDALONE_SYMBOLS[clean_lower]
        candidates.append(
            ParsedPhysicalValueCandidate(
                raw_text=raw,
                numeric_value=None,  # STRICT: No fabricated value
                raw_unit=None,
                canonical_unit=None,
                quantity_candidate=cat,
                source_ocr_token_id=token.id,
                confidence=token.confidence,
            )
        )
        return candidates

    # 2. Pattern: [Symbol =] Number [Unit]
    # Examples: "20 cm", "L = 20 cm", "θ = 30°", "12V", "10 Ω", "45 deg", "২০ সেমি", "R1 = 2 kΩ", "n = 1.50"
    pattern = re.compile(
        r"(?:([A-Za-zθΘ\u0980-\u09FF][A-Za-z0-9_θΘ\u0980-\u09FF]*)\s*=\s*)?([+-]?\d+(?:\.\d+)?)\s*([°ΩωμµuA-Za-z/\^²2\u0980-\u09FF\.]+)?",
        re.UNICODE,
    )

    for match in pattern.finditer(normalized):
        symbol_prefix, num_str, unit_str = match.groups()
        try:
            num_val = float(num_str)
        except (ValueError, TypeError):
            continue

        raw_unit = unit_str.strip() if unit_str else None
        canonical_unit = None
        quantity_type = None

        # Section 13: Strict Candidate Filtering - Reject caption and non-physics words
        if raw_unit:
            raw_unit_lower = raw_unit.lower()
            if raw_unit_lower in ("simple", "pendulum", "figure", "fig", "chapter", "example", "page", "diagram", "table", "part"):
                continue
            unit_key = raw_unit_lower
            if unit_key in UNIT_MAP:
                canonical_unit, quantity_type, _ = UNIT_MAP[unit_key]
            elif raw_unit in ("°", "deg", "degree"):
                canonical_unit = "°"
                quantity_type = "angle"
            elif raw_unit in ("Ω", "ω", "ohm", "ohms"):
                canonical_unit = "ohm"
                quantity_type = "resistance"

        # If symbol prefix exists, refine quantity type
        if symbol_prefix:
            sym_key = symbol_prefix.lower()
            if sym_key == "l" and quantity_type is None:
                quantity_type = "length"
            elif sym_key == "m" and quantity_type is None:
                quantity_type = "mass"
            elif sym_key in ("θ", "theta", "angle") and quantity_type is None:
                quantity_type = "angle"
            elif sym_key in ("a", "apex") and raw_unit in ("°", "deg", "degree") and quantity_type is None:
                quantity_type = "angle"
            elif sym_key in ("i", "r") and raw_unit in ("°", "deg", "degree") and quantity_type is None:
                quantity_type = "angle"
            elif sym_key == "g" and quantity_type is None:
                quantity_type = "acceleration"
            elif sym_key in ("v", "v1", "v_source") and (quantity_type is None or quantity_type == "voltage"):
                quantity_type = "voltage"
            elif sym_key in ("u", "v0") and (quantity_type is None or quantity_type == "velocity"):
                quantity_type = "velocity"
            elif sym_key.startswith("r") and (quantity_type is None or quantity_type == "resistance"):
                quantity_type = "resistance"
            elif sym_key in ("i", "i1") and (quantity_type is None or quantity_type == "current"):
                quantity_type = "current"
            elif sym_key in ("n", "n1", "n2"):
                quantity_type = "refractive_index"
            elif sym_key == "f" and (quantity_type is None or quantity_type == "length"):
                quantity_type = "focal_length"

        # Strict requirement: Must have recognized physics unit OR recognized symbol assignment
        if not symbol_prefix:
            if canonical_unit is None and raw_unit not in ("°", "deg", "degree", "Ω", "ω"):
                # Bare number with no physics unit (e.g. caption number "1") -> reject
                continue
        else:
            if quantity_type is None and canonical_unit is None:
                continue

        # Reject caption patterns such as "Fig. 1", "Chapter 2"
        if re.match(r"^(?:fig\.?|figure|chap\.?|chapter|example|page)\s*\d+$", normalized, re.IGNORECASE):
            continue

        candidates.append(
            ParsedPhysicalValueCandidate(
                raw_text=match.group(0),
                numeric_value=num_val,
                raw_unit=raw_unit,
                canonical_unit=canonical_unit,
                quantity_candidate=quantity_type,
                source_ocr_token_id=token.id,
                confidence=token.confidence,
            )
        )

    # 3. Also parse candidates from candidate_alternatives (e.g. confusable disambiguation)
    if hasattr(token, "candidate_alternatives") and token.candidate_alternatives:
        for alt in token.candidate_alternatives:
            alt_text = alt.get("text", "")
            if alt_text and alt_text != raw and alt_text != normalized:
                alt_norm = normalize_ocr_text(alt_text)
                for match in pattern.finditer(alt_norm):
                    _, n_str, u_str = match.groups()
                    try:
                        n_val = float(n_str)
                    except (ValueError, TypeError):
                        continue
                    r_unit = u_str.strip() if u_str else None
                    c_unit = None
                    q_type = None
                    if r_unit:
                        u_key = r_unit.lower()
                        if u_key in UNIT_MAP:
                            c_unit, q_type, _ = UNIT_MAP[u_key]
                        elif r_unit in ("Ω", "ω"):
                            c_unit = "ohm"
                            q_type = "resistance"
                    candidates.append(
                        ParsedPhysicalValueCandidate(
                            raw_text=alt_text,
                            numeric_value=n_val,
                            raw_unit=r_unit,
                            canonical_unit=c_unit,
                            quantity_candidate=q_type,
                            source_ocr_token_id=token.id,
                            confidence=round(token.confidence * 0.90, 3),
                        )
                    )

    return candidates

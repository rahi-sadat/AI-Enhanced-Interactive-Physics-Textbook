"""PR-06 Greek & Physics Symbol Recognition and Confusable Disambiguation.

Provides specialized candidate generation for isolated physics symbols and Greek letters:
  θ, α, β, γ, λ, μ, ω, Ω, φ, ρ, σ, τ, π, Δ, Σ, L, m, g, T, F, C, R, V, I, u, v, R1, R2

Implements deterministic confusable mapping and alternative candidate retention:
  - O ↔ 0 ↔ Ω
  - 8 ↔ θ
  - u ↔ μ
  - v ↔ ν
  - p ↔ ρ
  - w ↔ ω
  - A ↔ Δ
  - 1 ↔ l ↔ I
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from shared.schemas.evidence import OCRToken

logger = logging.getLogger(__name__)

# Canonical physics symbol sets
GREEK_PHYSICS_SYMBOLS = {
    "θ": "theta",
    "α": "alpha",
    "β": "beta",
    "γ": "gamma",
    "λ": "lambda",
    "μ": "mu",
    "ω": "omega",
    "Ω": "ohm",
    "φ": "phi",
    "ρ": "rho",
    "σ": "sigma",
    "τ": "tau",
    "π": "pi",
    "Δ": "delta",
    "Σ": "sigma_sum",
}

# Known OCR misrecognitions and confusables
CONFUSABLE_MAP: Dict[str, List[Dict[str, Any]]] = {
    "8": [{"char": "θ", "script": "greek", "name": "theta", "priors": 0.85}],
    "O": [
        {"char": "Ω", "script": "greek", "name": "ohm", "priors": 0.80},
        {"char": "0", "script": "numeric", "name": "zero", "priors": 0.90},
    ],
    "o": [
        {"char": "Ω", "script": "greek", "name": "ohm", "priors": 0.70},
        {"char": "θ", "script": "greek", "name": "theta", "priors": 0.65},
    ],
    "0": [
        {"char": "O", "script": "latin", "name": "capital_o", "priors": 0.75},
        {"char": "Ω", "script": "greek", "name": "ohm", "priors": 0.75},
        {"char": "θ", "script": "greek", "name": "theta", "priors": 0.70},
    ],
    "u": [{"char": "μ", "script": "greek", "name": "micro", "priors": 0.85}],
    "v": [{"char": "ν", "script": "greek", "name": "nu", "priors": 0.70}],
    "w": [{"char": "ω", "script": "greek", "name": "omega_lower", "priors": 0.85}],
    "p": [{"char": "ρ", "script": "greek", "name": "rho", "priors": 0.75}],
    "A": [{"char": "Δ", "script": "greek", "name": "delta", "priors": 0.80}],
    "l": [
        {"char": "1", "script": "numeric", "name": "one", "priors": 0.90},
        {"char": "I", "script": "latin", "name": "current_i", "priors": 0.80},
    ],
    "I": [
        {"char": "1", "script": "numeric", "name": "one", "priors": 0.85},
        {"char": "l", "script": "latin", "name": "length_l", "priors": 0.80},
    ],
}


def generate_symbol_alternatives(raw_text: str, base_confidence: Optional[float] = None) -> List[Dict[str, Any]]:
    """Generate alternative interpretations for physics symbols and confusables."""
    cleaned = raw_text.strip()
    alternatives: List[Dict[str, Any]] = []

    # 1. Exact Greek symbol match
    if cleaned in GREEK_PHYSICS_SYMBOLS:
        alternatives.append({
            "text": cleaned,
            "script": "greek",
            "name": GREEK_PHYSICS_SYMBOLS[cleaned],
            "confidence": base_confidence or 0.95,
            "provider": "symbol_engine",
        })
        return alternatives

    # 2. Check confusables table for exact match
    if cleaned in CONFUSABLE_MAP:
        for conf in CONFUSABLE_MAP[cleaned]:
            scaled_conf = (base_confidence or 0.80) * conf["priors"]
            alternatives.append({
                "text": conf["char"],
                "script": conf["script"],
                "name": conf["name"],
                "confidence": round(scaled_conf, 3),
                "provider": "confusable_resolver",
            })

    # 3. Check for equation prefix confusables: e.g. "8 = 30°" -> "θ = 30°", "u = 0.2" -> "μ = 0.2"
    import re
    eq_match = re.match(r"^([A-Za-z0-9])\s*=\s*(.*)", cleaned)
    if eq_match:
        var_sym, rest = eq_match.group(1), eq_match.group(2)
        if var_sym in CONFUSABLE_MAP:
            for conf in CONFUSABLE_MAP[var_sym]:
                alt_eq = f"{conf['char']} = {rest}"
                scaled_conf = (base_confidence or 0.80) * conf["priors"]
                alternatives.append({
                    "text": alt_eq,
                    "script": conf["script"],
                    "name": f"confusable_var_{conf['name']}",
                    "confidence": round(scaled_conf, 3),
                    "provider": "equation_symbol_resolver",
                })

    # 4. Check for trailing ohm / unit pattern like "10 O" or "10 0" -> candidate "10 Ω"
    parts = cleaned.split()
    if len(parts) == 2 and parts[0].replace(".", "").isdigit():
        num, unit_part = parts[0], parts[1]
        if unit_part in ("O", "0", "o", "ohm", "ohms"):
            alternatives.append({
                "text": f"{num} Ω",
                "script": "mixed",
                "name": "resistance_value",
                "confidence": 0.92,
                "provider": "physics_unit_confusable",
            })
        elif unit_part.lower() in ("v", "volt", "volts"):
            alternatives.append({
                "text": f"{num} V",
                "script": "mixed",
                "name": "voltage_value",
                "confidence": 0.95,
                "provider": "physics_unit_confusable",
            })
        elif unit_part.lower() in ("a", "amp", "amps"):
            alternatives.append({
                "text": f"{num} A",
                "script": "mixed",
                "name": "current_value",
                "confidence": 0.95,
                "provider": "physics_unit_confusable",
            })

    return alternatives


def detect_symbol_in_token(text: str) -> Optional[str]:
    """Detect if text contains a known Greek physics symbol."""
    for sym, name in GREEK_PHYSICS_SYMBOLS.items():
        if sym in text:
            return name
    return None


class PhysicsSymbolCandidateResolver:
    """Specialized resolver enriching OCR tokens with physics symbol candidates and confusables.

    NOTE: This component does NOT perform pixel-level OCR recognition. It is a deterministic
    candidate generator and confusable resolver (θ ↔ 8, Ω ↔ O ↔ 0, μ ↔ u, etc.).
    """

    def __init__(self):
        self.name = "physics_symbol_resolver"

    def available(self) -> bool:
        return True

    def enrich_token(self, token: OCRToken) -> OCRToken:
        """Enrich an existing OCRToken with symbol alternatives and script detection."""
        alts = generate_symbol_alternatives(token.raw_text, token.confidence)
        if alts:
            token.candidate_alternatives.extend(alts)

            # If the primary text was an isolated Greek symbol, update script candidate
            if token.raw_text.strip() in GREEK_PHYSICS_SYMBOLS:
                token.script_candidate = "greek"
                token.language_candidate = "el"
                token.normalized_text = token.raw_text.strip()

        return token


# Aliases for backward compatibility
GreekConfusableResolver = PhysicsSymbolCandidateResolver
GreekSymbolOCRProvider = PhysicsSymbolCandidateResolver

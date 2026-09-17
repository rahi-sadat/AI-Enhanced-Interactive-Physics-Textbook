"""backend/circuits/solver/equation_generator.py

Generates symbolic and step-by-step mathematical proofs directly from the electrical state.
Grounds educational explanations and the Bangla AI tutor in verified physics facts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from engine.core.parameter_resolver import format_si
except (ImportError, ValueError):
    try:
        from backend.core.parameter_resolver import format_si
    except (ImportError, ValueError):
        from core.parameter_resolver import format_si
from ..models import CircuitScene
from .mna_solver import ElectricalState


@dataclass
class DerivationStep:
    law: str
    symbolic: str
    substitution: str
    result: str
    bangla_explanation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "law": self.law,
            "symbolic": self.symbolic,
            "substitution": self.substitution,
            "result": self.result,
            "bangla_explanation": self.bangla_explanation,
        }


def generate_equations(scene: CircuitScene, state: ElectricalState) -> list[dict[str, str]]:
    """Derive step-by-step educational circuit formulas from the solved state."""
    steps: list[DerivationStep] = []

    if state.status != "solved":
        return []

    # 1. Total / Equivalent Resistance Step (if single voltage source)
    v_sources = [c for c in scene.components if c.type in ("voltage_source", "battery", "cell")]
    resistors = [c for c in scene.components if c.type in ("resistor", "bulb")]

    if len(v_sources) == 1 and state.equivalent_resistance_ohm is not None:
        vs = v_sources[0]
        v_val = vs.parameters.get("voltage_v", None)
        v_num = v_val.value if v_val and v_val.value is not None else 12.0
        vs_state = state.components.get(vs.id)
        i_tot = abs(vs_state.current_a) if vs_state else (v_num / state.equivalent_resistance_ohm)

        r_eq_str = format_si(state.equivalent_resistance_ohm, "ohm")
        v_str = format_si(v_num, "V")
        i_str = format_si(i_tot, "A")

        steps.append(
            DerivationStep(
                law="equivalent_resistance",
                symbolic="R_eq = V_total / I_total",
                substitution=f"R_eq = {v_str} / {i_str}",
                result=f"R_eq = {r_eq_str}",
                bangla_explanation=f"বর্তনীর মোট তুল্য রোধ (Equivalent Resistance) হলো {r_eq_str}।",
            )
        )

        steps.append(
            DerivationStep(
                law="ohms_law_total",
                symbolic="I_total = V_total / R_eq",
                substitution=f"I_total = {v_str} / {r_eq_str}",
                result=f"I_total = {i_str}",
                bangla_explanation=f"ওহমের সূত্র অনুযায়ী বর্তনীর মূল তড়িৎপ্রবাহ I = {i_str}।",
            )
        )

    # 2. Individual Resistor Ohm's Law and Power Dissipation
    for res in resistors:
        r_state = state.components.get(res.id)
        if not r_state:
            continue
        r_param = res.parameters.get("resistance_ohm")
        r_val = r_param.value if r_param and r_param.value is not None else 100.0

        v_comp = abs(r_state.voltage_v)
        i_comp = abs(r_state.current_a)
        p_comp = r_state.power_w

        v_str = format_si(v_comp, "V")
        i_str = format_si(i_comp, "A")
        r_str = format_si(r_val, "ohm")
        p_str = format_si(p_comp, "W")

        steps.append(
            DerivationStep(
                law=f"ohms_law_{res.id}",
                symbolic=f"V_{{{res.id}}} = I_{{{res.id}}} * {res.id}",
                substitution=f"V_{{{res.id}}} = {i_str} * {r_str}",
                result=f"V_{{{res.id}}} = {v_str}",
                bangla_explanation=f"{res.id} রোধের দুই প্রান্তের বিভব পার্থক্য (Voltage Drop) হলো {v_str}।",
            )
        )

        steps.append(
            DerivationStep(
                law=f"joule_heating_{res.id}",
                symbolic=f"P_{{{res.id}}} = V_{{{res.id}}} * I_{{{res.id}}} = I^2 * R",
                substitution=f"P_{{{res.id}}} = {v_str} * {i_str}",
                result=f"P_{{{res.id}}} = {p_str}",
                bangla_explanation=f"{res.id}-এ ব্যায়িত তড়িৎ ক্ষমতা (Power Dissipation) হলো {p_str}।",
            )
        )

    # 3. Kirchhoff's Current Law (KCL) at Junctions with >= 3 connected branches
    for node in scene.nodes:
        if len(node.terminal_ids) >= 3:
            nid = node.id
            current_terms = []
            for comp in scene.components:
                c_state = state.components.get(comp.id)
                if not c_state:
                    continue
                if comp.type in ("resistor", "bulb"):
                    na = comp.terminals[0].node
                    nb = comp.terminals[1].node
                    if na == nid:
                        current_terms.append(f"-{format_si(c_state.current_a, 'A')} ({comp.id})")
                    elif nb == nid:
                        current_terms.append(f"+{format_si(c_state.current_a, 'A')} ({comp.id})")

            if current_terms:
                kcl_sub = " + ".join(current_terms).replace("+ -", "- ")
                residual = state.kcl_residuals.get(nid, 0.0)
                res_str = format_si(abs(residual), "A")
                steps.append(
                    DerivationStep(
                        law=f"kcl_{nid}",
                        symbolic=f"\\sum I_{{in}} = \\sum I_{{out}} \\implies \\sum I_{{node {nid}}} = 0",
                        substitution=f"{kcl_sub} = {res_str}",
                        result="KCL Balanced (0 A)" if abs(residual) < 1e-6 else f"Residual: {res_str}",
                        bangla_explanation=f"জাংশন {nid}-এ কার্শফের প্রথম সূত্র (KCL) রক্ষিত হয়েছে: মোট অন্তর্মুখী প্রবাহ = মোট বহির্মুখী প্রবাহ।",
                    )
                )

    return [s.to_dict() for s in steps]

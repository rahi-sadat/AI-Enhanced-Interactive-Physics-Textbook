"""backend/circuits/solver/mna_solver.py

Authoritative Modified Nodal Analysis (MNA) solver in Python using NumPy.
Solves Ax = z for linear DC networks:
  - Node voltages (V)
  - Branch currents (I)
  - Component power dissipation (P)
  - Kirchhoff's Current Law (KCL) verification
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..models import CircuitScene, Component, Node


@dataclass
class ComponentState:
    id: str
    type: str
    voltage_v: float
    current_a: float
    power_w: float
    terminals: list[str]
    notes: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "voltage_v": round(self.voltage_v, 6),
            "current_a": round(self.current_a, 6),
            "power_w": round(self.power_w, 6),
            "terminals": self.terminals,
        }
        if self.notes:
            d["notes"] = self.notes
        return d


@dataclass
class ElectricalState:
    status: str  # "solved", "unsolved", "singular"
    reference_node: str
    node_voltages: dict[str, float]
    components: dict[str, ComponentState]
    kcl_residuals: dict[str, float] = field(default_factory=dict)
    equivalent_resistance_ohm: Optional[float] = None
    total_power_w: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reference_node": self.reference_node,
            "node_voltages_v": {k: round(v, 6) for k, v in self.node_voltages.items()},
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "kcl_residuals_a": {k: round(v, 9) for k, v in self.kcl_residuals.items()},
            "equivalent_resistance_ohm": (
                round(self.equivalent_resistance_ohm, 6)
                if self.equivalent_resistance_ohm is not None
                else None
            ),
            "total_power_w": round(self.total_power_w, 6),
            "error_message": self.error_message,
        }


class MNASolver:
    """Modified Nodal Analysis linear circuit solver."""

    def __init__(self, scene: CircuitScene) -> None:
        self.scene = scene

    def solve_dc(self) -> ElectricalState:
        """Solve DC operating point using Modified Nodal Analysis (Ax = z)."""
        scene = self.scene
        circuit_nodes = scene.nodes
        components = scene.components

        if not circuit_nodes or not components:
            return ElectricalState(
                status="unsolved",
                reference_node="N0",
                node_voltages={},
                components={},
                error_message="Empty circuit scene.",
            )

        # 1. Determine reference node (ground = 0 V)
        ref_nodes = [n.id for n in circuit_nodes if n.reference]
        ref_node = ref_nodes[0] if ref_nodes else scene.reference_node
        if ref_node not in [n.id for n in circuit_nodes]:
            ref_node = circuit_nodes[0].id

        # Non-reference nodes
        non_ref_nodes = [n.id for n in circuit_nodes if n.id != ref_node]
        node_idx = {nid: i for i, nid in enumerate(non_ref_nodes)}
        n = len(non_ref_nodes)

        # 2. Identify auxiliary variables (voltage sources, closed switches, ammeters)
        # An open switch is treated as open circuit (no branch).
        # A closed switch is stamped as a 0-V voltage source.
        # An ammeter is stamped as a 0-V voltage source.
        # A voltmeter is high impedance (probe only).
        aux_components: list[Component] = []
        for comp in components:
            ctype = comp.type
            if ctype in ("voltage_source", "battery", "cell"):
                aux_components.append(comp)
            elif ctype == "ammeter":
                aux_components.append(comp)
            elif ctype == "switch":
                # Check switch state; default to closed if not specified
                is_closed = comp.state != "open"
                if is_closed:
                    aux_components.append(comp)

        m = len(aux_components)
        source_idx = {comp.id: i for i, comp in enumerate(aux_components)}

        dim = n + m
        if dim == 0:
            return ElectricalState(
                status="solved",
                reference_node=ref_node,
                node_voltages={ref_node: 0.0},
                components={},
            )

        A = np.zeros((dim, dim), dtype=np.float64)
        z = np.zeros(dim, dtype=np.float64)

        # 3. Stamp components into MNA matrix
        for comp in components:
            ctype = comp.type
            terms = comp.terminals
            if len(terms) < 2 and ctype != "ground":
                continue

            # Nodes for terminals
            na = terms[0].node
            nb = terms[1].node if len(terms) > 1 else None

            # 3a. Resistors & Bulbs
            if ctype in ("resistor", "bulb"):
                r_param = comp.parameters.get("resistance_ohm")
                r_val = r_param.value if r_param and r_param.value is not None else 100.0
                if r_val <= 0:
                    r_val = 1e-6  # safeguard against div by zero

                g = 1.0 / r_val
                if na != ref_node and na in node_idx:
                    ia = node_idx[na]
                    A[ia, ia] += g
                if nb != ref_node and nb in node_idx:
                    ib = node_idx[nb]
                    A[ib, ib] += g
                if na != ref_node and nb != ref_node and na in node_idx and nb in node_idx:
                    ia = node_idx[na]
                    ib = node_idx[nb]
                    A[ia, ib] -= g
                    A[ib, ia] -= g

            # 3b. Voltage sources, closed switches, and ammeters
            elif comp.id in source_idx:
                k = n + source_idx[comp.id]
                val = 0.0
                if ctype in ("voltage_source", "battery", "cell"):
                    v_param = comp.parameters.get("voltage_v")
                    val = v_param.value if v_param and v_param.value is not None else 12.0
                elif ctype in ("ammeter", "switch"):
                    val = 0.0

                # Convention: Terminal 0 is positive (+), Terminal 1 is negative (-)
                # Current leaves positive terminal: V_pos - V_neg = val
                if na != ref_node and na in node_idx:
                    ia = node_idx[na]
                    A[ia, k] += 1.0
                    A[k, ia] += 1.0
                if nb != ref_node and nb in node_idx:
                    ib = node_idx[nb]
                    A[ib, k] -= 1.0
                    A[k, ib] -= 1.0

                z[k] += val

            # 3c. Current sources
            elif ctype == "current_source":
                i_param = comp.parameters.get("current_a")
                i_val = i_param.value if i_param and i_param.value is not None else 1.0
                # Current flows from terminal 0 to terminal 1
                if na != ref_node and na in node_idx:
                    z[node_idx[na]] -= i_val
                if nb != ref_node and nb in node_idx:
                    z[node_idx[nb]] += i_val

            # 3d. Capacitors in DC steady-state act as open circuits (no conductance)

        # 4. Solve the linear system Ax = z
        try:
            x = np.linalg.solve(A, z)
        except np.linalg.LinAlgError:
            # Try pseudo-inverse for singular/unconnected floating segments
            try:
                x = np.linalg.lstsq(A, z, rcond=1e-10)[0]
            except Exception as e:
                return ElectricalState(
                    status="singular",
                    reference_node=ref_node,
                    node_voltages={n.id: 0.0 for n in circuit_nodes},
                    components={},
                    error_message=f"Singular MNA matrix: {e}",
                )

        # 5. Extract node voltages
        voltages: dict[str, float] = {ref_node: 0.0}
        for nid, idx in node_idx.items():
            voltages[nid] = float(x[idx])

        # 6. Extract component branch currents and powers
        comp_states: dict[str, ComponentState] = {}
        total_power = 0.0

        for comp in components:
            ctype = comp.type
            terms = comp.terminals
            term_ids = [t.id for t in terms]
            na = terms[0].node if len(terms) > 0 else ref_node
            nb = terms[1].node if len(terms) > 1 else ref_node

            va = voltages.get(na, 0.0)
            vb = voltages.get(nb, 0.0)
            v_drop = va - vb

            if ctype in ("resistor", "bulb"):
                r_param = comp.parameters.get("resistance_ohm")
                r_val = r_param.value if r_param and r_param.value is not None else 100.0
                i_branch = v_drop / r_val if r_val > 0 else 0.0
                p_branch = abs(v_drop * i_branch)
                total_power += p_branch
                comp_states[comp.id] = ComponentState(
                    id=comp.id,
                    type=ctype,
                    voltage_v=v_drop,
                    current_a=i_branch,
                    power_w=p_branch,
                    terminals=term_ids,
                )

            elif comp.id in source_idx:
                k = n + source_idx[comp.id]
                # Current exiting positive terminal (from na to nb)
                i_source = float(x[k])
                p_source = abs(v_drop * i_source)
                notes = None
                if ctype == "ammeter":
                    notes = f"Ammeter reading: {abs(i_source):.4f} A"
                elif ctype == "switch":
                    notes = f"Switch closed (I = {abs(i_source):.4f} A)"

                comp_states[comp.id] = ComponentState(
                    id=comp.id,
                    type=ctype,
                    voltage_v=v_drop,
                    current_a=i_source,
                    power_w=p_source,
                    terminals=term_ids,
                    notes=notes,
                )

            elif ctype == "switch" and comp.state == "open":
                comp_states[comp.id] = ComponentState(
                    id=comp.id,
                    type=ctype,
                    voltage_v=v_drop,
                    current_a=0.0,
                    power_w=0.0,
                    terminals=term_ids,
                    notes="Switch open (I = 0 A)",
                )

            elif ctype == "voltmeter":
                comp_states[comp.id] = ComponentState(
                    id=comp.id,
                    type=ctype,
                    voltage_v=v_drop,
                    current_a=0.0,
                    power_w=0.0,
                    terminals=term_ids,
                    notes=f"Voltmeter probe: {abs(v_drop):.4f} V",
                )

            elif ctype == "capacitor":
                # In DC steady-state, I = 0, V = v_drop
                comp_states[comp.id] = ComponentState(
                    id=comp.id,
                    type=ctype,
                    voltage_v=v_drop,
                    current_a=0.0,
                    power_w=0.0,
                    terminals=term_ids,
                    notes="DC steady-state (I = 0 A)",
                )

        # 7. Compute KCL residuals at each node
        kcl_residuals: dict[str, float] = {}
        for node in circuit_nodes:
            nid = node.id
            sum_i = 0.0
            for comp in components:
                if comp.id not in comp_states:
                    continue
                state = comp_states[comp.id]
                if comp.type in ("resistor", "bulb"):
                    na = comp.terminals[0].node
                    nb = comp.terminals[1].node
                    if na == nid:
                        sum_i -= state.current_a  # leaves na
                    elif nb == nid:
                        sum_i += state.current_a  # enters nb
                elif comp.id in source_idx:
                    na = comp.terminals[0].node
                    nb = comp.terminals[1].node
                    if na == nid:
                        sum_i -= state.current_a  # leaves positive terminal
                    elif nb == nid:
                        sum_i += state.current_a  # enters negative terminal
            kcl_residuals[nid] = sum_i

        # 8. Equivalent resistance (if single voltage source present)
        v_sources = [c for c in components if c.type in ("voltage_source", "battery", "cell")]
        r_eq = None
        if len(v_sources) == 1:
            vs_state = comp_states.get(v_sources[0].id)
            if vs_state and abs(vs_state.current_a) > 1e-12:
                r_eq = abs(vs_state.voltage_v / vs_state.current_a)

        return ElectricalState(
            status="solved",
            reference_node=ref_node,
            node_voltages=voltages,
            components=comp_states,
            kcl_residuals=kcl_residuals,
            equivalent_resistance_ohm=r_eq,
            total_power_w=total_power,
        )

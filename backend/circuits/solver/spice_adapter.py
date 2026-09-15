"""backend/circuits/solver/spice_adapter.py

Sanitized, injection-proof SPICE netlist generator and ngspice subprocess adapter.
Provides independent cross-validation against ngspice 47 when present,
with safe fallback when ngspice is not installed on the host.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from ..models import CircuitScene


def sanitize_id(identifier: str) -> str:
    """Validate and sanitize component or node identifiers to prevent SPICE command injection."""
    if not identifier:
        return "UNKNOWN"
    clean = re.sub(r"[^A-Za-z0-9_]", "_", str(identifier))
    if not clean or clean[0].isdigit():
        clean = "X_" + clean
    return clean


def sanitize_node(node_id: str, reference_node: str = "N0") -> str:
    """Map reference node to SPICE standard '0' (ground), and sanitize other node names."""
    if node_id == reference_node or node_id in ("0", "GND", "ground"):
        return "0"
    return sanitize_id(node_id)


class SpiceAdapter:
    """Generates standard SPICE netlists and runs sandboxed ngspice verification."""

    @classmethod
    def is_available(cls) -> bool:
        """Check if ngspice is installed and accessible on system PATH."""
        return shutil.which("ngspice") is not None

    @classmethod
    def build_netlist(cls, scene: CircuitScene) -> str:
        """Serialize a structured CircuitScene into a standard SPICE netlist."""
        ref_node = scene.reference_node
        lines = [
            "* AugmentedPhysics Canonical CircuitScene v3 SPICE Netlist",
            f"* Domain: {scene.domain} | Subtype: {scene.subtype}",
        ]

        # Resistors, sources, meters
        for comp in scene.components:
            ctype = comp.type
            cid = sanitize_id(comp.id)
            terms = comp.terminals
            if len(terms) < 2:
                continue

            n1 = sanitize_node(terms[0].node or ref_node, ref_node)
            n2 = sanitize_node(terms[1].node or ref_node, ref_node)

            if ctype in ("resistor", "bulb"):
                # Prefix with R
                r_name = cid if cid.startswith("R") else f"R_{cid}"
                r_param = comp.parameters.get("resistance_ohm")
                r_val = r_param.value if r_param and r_param.value is not None else 100.0
                lines.append(f"{r_name} {n1} {n2} {float(r_val):.6g}")

            elif ctype in ("voltage_source", "battery", "cell"):
                # Prefix with V
                v_name = cid if cid.startswith("V") else f"V_{cid}"
                v_param = comp.parameters.get("voltage_v")
                v_val = v_param.value if v_param and v_param.value is not None else 12.0
                lines.append(f"{v_name} {n1} {n2} DC {float(v_val):.6g}")

            elif ctype == "current_source":
                i_name = cid if cid.startswith("I") else f"I_{cid}"
                i_param = comp.parameters.get("current_a")
                i_val = i_param.value if i_param and i_param.value is not None else 1.0
                lines.append(f"{i_name} {n1} {n2} DC {float(i_val):.6g}")

            elif ctype == "ammeter":
                # Ammeter is a 0-V voltage source in SPICE
                v_name = cid if cid.startswith("V") else f"V_AM_{cid}"
                lines.append(f"{v_name} {n1} {n2} DC 0.0")

            elif ctype == "switch":
                if comp.state != "open":
                    s_name = cid if cid.startswith("V") else f"V_SW_{cid}"
                    lines.append(f"{s_name} {n1} {n2} DC 0.0")
                # Open switch is omitted (infinite resistance)

            elif ctype == "capacitor":
                c_name = cid if cid.startswith("C") else f"C_{cid}"
                c_param = comp.parameters.get("capacitance_f")
                c_val = c_param.value if c_param and c_param.value is not None else 1e-6
                lines.append(f"{c_name} {n1} {n2} {float(c_val):.6g}")

        lines.extend([
            ".op",
            ".end",
        ])
        return "\n".join(lines) + "\n"

    @classmethod
    def run_simulation(cls, netlist: str) -> dict[str, Any]:
        """Execute sandboxed ngspice subprocess on generated netlist."""
        if not cls.is_available():
            return {
                "available": False,
                "status": "skipped",
                "reason": "ngspice executable not found on system PATH",
                "netlist": netlist,
            }

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cir_file = tmp_path / "circuit.cir"
            out_file = tmp_path / "ngspice.out"
            cir_file.write_text(netlist, encoding="utf-8")

            try:
                # Run ngspice safely in batch mode (-b)
                proc = subprocess.run(
                    ["ngspice", "-b", "-r", str(out_file), str(cir_file)],
                    shell=False,
                    timeout=5,
                    capture_output=True,
                    text=True,
                )
                output_log = proc.stdout + "\n" + proc.stderr
                return {
                    "available": True,
                    "status": "success" if proc.returncode == 0 else "error",
                    "returncode": proc.returncode,
                    "log": output_log,
                    "netlist": netlist,
                }
            except subprocess.TimeoutExpired:
                return {
                    "available": True,
                    "status": "timeout",
                    "reason": "Simulation timed out after 5.0s",
                    "netlist": netlist,
                }
            except Exception as e:
                return {
                    "available": True,
                    "status": "error",
                    "reason": str(e),
                    "netlist": netlist,
                }

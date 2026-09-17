"""backend/circuits/topology/topology_validator.py

Validates circuit topology before attempting matrix solving.
Returns structured diagnostics and repair suggestions instead of raw LinAlgError exceptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ..circuit_registry import get_component_spec
from ..models import CircuitScene, Component


class DiagnosticSeverity(str, Enum):
    BLOCKING = "blocking"    # Cannot solve electrically
    WARNING = "warning"      # Solvable, but likely anomalous
    INFO = "info"            # Educational note


@dataclass
class Diagnostic:
    code: str
    severity: DiagnosticSeverity
    entity_id: Optional[str]
    message: str
    action: Optional[str] = None
    position_source_px: Optional[list[float]] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
        }
        if self.entity_id:
            d["entity_id"] = self.entity_id
        if self.action:
            d["action"] = self.action
        if self.position_source_px:
            d["position_source_px"] = self.position_source_px
        return d


@dataclass
class ValidationReport:
    valid: bool
    mode: str
    diagnostics: list[Diagnostic]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "mode": self.mode,
            "diagnostics": [d.to_dict() for d in self.diagnostics],
        }


def validate_topology(scene: CircuitScene) -> ValidationReport:
    """Validate electrical consistency and connectivity of a CircuitScene."""
    diagnostics: list[Diagnostic] = []

    # 1. Check for presence of elements
    if not scene.components:
        diagnostics.append(
            Diagnostic(
                code="NO_COMPONENTS",
                severity=DiagnosticSeverity.BLOCKING,
                entity_id=None,
                message="No components detected in circuit schematic.",
                action="add_components",
            )
        )
        return ValidationReport(valid=False, mode="assisted", diagnostics=diagnostics)

    # 2. Check for at least one power source (voltage_source, battery, cell, current_source)
    source_types = {"voltage_source", "battery", "cell", "current_source"}
    sources = [c for c in scene.components if c.type in source_types]
    if not sources:
        diagnostics.append(
            Diagnostic(
                code="MISSING_ENERGY_SOURCE",
                severity=DiagnosticSeverity.BLOCKING,
                entity_id=None,
                message="Circuit contains no active DC voltage or current source.",
                action="add_voltage_source",
            )
        )

    # 3. Node mapping analysis
    node_to_terminals: Dict[str, List[str]] = {}
    terminal_to_node: Dict[str, str] = {}
    for comp in scene.components:
        for term in comp.terminals:
            t_node = term.node
            if t_node:
                node_to_terminals.setdefault(t_node, []).append(term.id)
                terminal_to_node[term.id] = t_node
            else:
                diagnostics.append(
                    Diagnostic(
                        code="FLOATING_TERMINAL",
                        severity=DiagnosticSeverity.BLOCKING,
                        entity_id=comp.id,
                        message=f"Terminal {term.id} of {comp.id} is not connected to any electrical node.",
                        action="connect_terminal",
                        position_source_px=term.position.to_list(),
                    )
                )

    # 4. Check component parameters and connections
    for comp in scene.components:
        spec = get_component_spec(comp.type)
        param_name = spec["parameter"] if spec else None

        # Value validity
        if param_name and param_name in comp.parameters:
            param = comp.parameters[param_name]
            if param.value is None:
                diagnostics.append(
                    Diagnostic(
                        code="MISSING_PARAMETER",
                        severity=DiagnosticSeverity.BLOCKING,
                        entity_id=comp.id,
                        message=f"{comp.id} ({comp.type}) has no numerical value assigned.",
                        action="assign_value",
                    )
                )
            elif comp.type in ("resistor", "bulb") and param.value <= 0:
                diagnostics.append(
                    Diagnostic(
                        code="INVALID_RESISTANCE",
                        severity=DiagnosticSeverity.BLOCKING,
                        entity_id=comp.id,
                        message=f"{comp.id} resistance must be strictly positive (got {param.value}).",
                        action="correct_value",
                    )
                )

        # Check for shorted components (both terminals connected to same node)
        if len(comp.terminals) == 2:
            t1, t2 = comp.terminals[0], comp.terminals[1]
            if t1.node and t2.node and t1.node == t2.node:
                if comp.type in source_types:
                    diagnostics.append(
                        Diagnostic(
                            code="SHORTED_VOLTAGE_SOURCE",
                            severity=DiagnosticSeverity.BLOCKING,
                            entity_id=comp.id,
                            message=f"Voltage source {comp.id} is short-circuited (both terminals on {t1.node})!",
                            action="isolate_source",
                        )
                    )
                elif comp.type in ("resistor", "bulb"):
                    diagnostics.append(
                        Diagnostic(
                            code="SHORTED_RESISTOR",
                            severity=DiagnosticSeverity.WARNING,
                            entity_id=comp.id,
                            message=f"Resistor {comp.id} is shorted out and will carry no current.",
                        )
                    )

    # 5. Check for isolated nodes (nodes with only 1 terminal connected)
    for node_id, term_ids in node_to_terminals.items():
        if len(term_ids) < 2:
            diagnostics.append(
                Diagnostic(
                    code="DEAD_END_NODE",
                    severity=DiagnosticSeverity.WARNING,
                    entity_id=node_id,
                    message=f"Node {node_id} has only one terminal attached ({term_ids[0]}); no loop can close through it.",
                )
            )

    # 6. Check for unresolved crossings / ambiguities
    for amb in scene.ambiguities:
        if amb.get("requires_confirmation"):
            diagnostics.append(
                Diagnostic(
                    code="AMBIGUOUS_CROSSING",
                    severity=DiagnosticSeverity.BLOCKING,
                    entity_id=amb.get("id"),
                    message=f"Wire crossing {amb.get('id')} has ambiguous connectivity.",
                    action="confirm_junction",
                    position_source_px=amb.get("position_source_px"),
                )
            )

    has_blocking = any(d.severity == DiagnosticSeverity.BLOCKING for d in diagnostics)
    valid = not has_blocking
    mode = "precision" if valid and not scene.ambiguities else "assisted"

    return ValidationReport(valid=valid, mode=mode, diagnostics=diagnostics)

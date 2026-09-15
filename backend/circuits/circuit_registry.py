"""backend/circuits/circuit_registry.py

Registry of standard electrical components for perception, topology, and MNA solving.
Prevents ad-hoc if/elif chains across the codebase.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, TypedDict


class ComponentSpec(TypedDict):
    terminal_count: int
    parameter: Optional[str]
    unit_family: Optional[str]
    default_unit: str
    solver_type: str
    polarized: bool
    description: str


COMPONENT_REGISTRY: Dict[str, ComponentSpec] = {
    "resistor": {
        "terminal_count": 2,
        "parameter": "resistance_ohm",
        "unit_family": "resistance",
        "default_unit": "ohm",
        "solver_type": "resistor",
        "polarized": False,
        "description": "Linear two-terminal electrical resistor",
    },
    "voltage_source": {
        "terminal_count": 2,
        "parameter": "voltage_v",
        "unit_family": "voltage",
        "default_unit": "V",
        "solver_type": "voltage_source",
        "polarized": True,
        "description": "Ideal independent DC voltage source",
    },
    "battery": {
        "terminal_count": 2,
        "parameter": "voltage_v",
        "unit_family": "voltage",
        "default_unit": "V",
        "solver_type": "voltage_source",
        "polarized": True,
        "description": "DC chemical cell or multi-cell battery",
    },
    "cell": {
        "terminal_count": 2,
        "parameter": "voltage_v",
        "unit_family": "voltage",
        "default_unit": "V",
        "solver_type": "voltage_source",
        "polarized": True,
        "description": "Single DC electric cell",
    },
    "current_source": {
        "terminal_count": 2,
        "parameter": "current_a",
        "unit_family": "current",
        "default_unit": "A",
        "solver_type": "current_source",
        "polarized": True,
        "description": "Ideal independent DC current source",
    },
    "switch": {
        "terminal_count": 2,
        "parameter": None,
        "unit_family": None,
        "default_unit": "",
        "solver_type": "switch",
        "polarized": False,
        "description": "Ideal SPST mechanical switch",
    },
    "ammeter": {
        "terminal_count": 2,
        "parameter": None,
        "unit_family": "current",
        "default_unit": "A",
        "solver_type": "ammeter",
        "polarized": True,
        "description": "Ideal zero-resistance current measurement meter",
    },
    "voltmeter": {
        "terminal_count": 2,
        "parameter": None,
        "unit_family": "voltage",
        "default_unit": "V",
        "solver_type": "probe",
        "polarized": True,
        "description": "Ideal infinite-resistance voltage measurement probe",
    },
    "bulb": {
        "terminal_count": 2,
        "parameter": "resistance_ohm",
        "unit_family": "resistance",
        "default_unit": "ohm",
        "solver_type": "resistor",
        "polarized": False,
        "description": "Incandescent lamp modeled as ideal resistive branch",
    },
    "capacitor": {
        "terminal_count": 2,
        "parameter": "capacitance_f",
        "unit_family": "capacitance",
        "default_unit": "F",
        "solver_type": "capacitor",
        "polarized": False,
        "description": "Two-plate capacitor for DC steady-state or transient analysis",
    },
    "ground": {
        "terminal_count": 1,
        "parameter": None,
        "unit_family": None,
        "default_unit": "",
        "solver_type": "ground",
        "polarized": False,
        "description": "Explicit 0V electrical earth/reference symbol",
    },
}


def get_component_spec(component_type: str) -> Optional[ComponentSpec]:
    """Retrieve specifications for a given component type."""
    return COMPONENT_REGISTRY.get(component_type.lower())


def is_polarized(component_type: str) -> bool:
    """Check if component requires explicit polarity assignment."""
    spec = get_component_spec(component_type)
    return spec["polarized"] if spec else False

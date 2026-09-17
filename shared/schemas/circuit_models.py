"""backend/circuits/models.py

Typed dataclass models for the Canonical CircuitScene v3 schema.
Separates topological connectivity and electrical state from spatial pixels,
while keeping source_px coordinates authoritative for embedded rendering.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Point:
    x: float
    y: float

    def to_list(self) -> list[float]:
        return [round(self.x, 3), round(self.y, 3)]

    def to_dict(self) -> dict[str, float]:
        return {"x": round(self.x, 3), "y": round(self.y, 3)}

    @classmethod
    def from_data(cls, data: Any) -> Point:
        if isinstance(data, (list, tuple)) and len(data) >= 2:
            return cls(float(data[0]), float(data[1]))
        if isinstance(data, dict):
            return cls(float(data.get("x", 0)), float(data.get("y", 0)))
        return cls(0.0, 0.0)


@dataclass
class Parameter:
    value: Optional[float]
    unit: str
    source: str = "manual"
    confidence: float = 1.0
    raw_text: Optional[str] = None
    bbox_source_px: Optional[list[float]] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "confidence": round(self.confidence, 4),
        }
        if self.raw_text:
            d["raw_text"] = self.raw_text
        if self.bbox_source_px:
            d["bbox_source_px"] = self.bbox_source_px
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any], default_unit: str = "") -> Parameter:
        return cls(
            value=float(d["value"]) if d.get("value") is not None else None,
            unit=d.get("unit", default_unit),
            source=d.get("source", "manual"),
            confidence=float(d.get("confidence", 1.0)),
            raw_text=d.get("raw_text"),
            bbox_source_px=d.get("bbox_source_px"),
        )


@dataclass
class Terminal:
    id: str
    position: Point
    node: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "source_px": self.position.to_list(),
            "confidence": round(self.confidence, 4),
        }
        if self.node:
            d["node"] = self.node
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Terminal:
        pos_data = d.get("source_px") or d.get("position") or [0, 0]
        return cls(
            id=d["id"],
            position=Point.from_data(pos_data),
            node=d.get("node"),
            confidence=float(d.get("confidence", 1.0)),
        )


@dataclass
class Component:
    id: str
    type: str  # resistor, voltage_source, switch, ammeter, voltmeter, bulb, capacitor
    terminals: list[Terminal]
    bbox_source_px: list[float]
    parameters: dict[str, Parameter] = field(default_factory=dict)
    state: Optional[str] = None  # e.g., "open" or "closed" for switch
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "terminals": [t.to_dict() for t in self.terminals],
            "bbox_source_px": self.bbox_source_px,
            "parameters": {k: v.to_dict() for k, v in self.parameters.items()},
            "confidence": round(self.confidence, 4),
        }
        if self.state is not None:
            d["state"] = self.state
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Component:
        terms = [Terminal.from_dict(t) for t in d.get("terminals", [])]
        params = {}
        for k, v in d.get("parameters", {}).items():
            if isinstance(v, dict):
                params[k] = Parameter.from_dict(v)
            elif isinstance(v, (int, float)):
                params[k] = Parameter(value=float(v), unit="")
        return cls(
            id=d["id"],
            type=d["type"],
            terminals=terms,
            bbox_source_px=d.get("bbox_source_px", [0, 0, 0, 0]),
            parameters=params,
            state=d.get("state"),
            confidence=float(d.get("confidence", 1.0)),
        )


@dataclass
class Wire:
    id: str
    polyline_source_px: list[Point]
    confidence: float = 1.0
    connected_nodes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "polyline_source_px": [p.to_list() for p in self.polyline_source_px],
            "confidence": round(self.confidence, 4),
            "connected_nodes": self.connected_nodes,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Wire:
        pts = [Point.from_data(p) for p in d.get("polyline_source_px", [])]
        return cls(
            id=d["id"],
            polyline_source_px=pts,
            confidence=float(d.get("confidence", 1.0)),
            connected_nodes=d.get("connected_nodes", []),
        )


@dataclass
class Node:
    id: str
    terminal_ids: list[str] = field(default_factory=list)
    reference: bool = False
    label: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "terminal_ids": self.terminal_ids,
        }
        if self.reference:
            d["reference"] = True
        if self.label:
            d["label"] = self.label
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Node:
        return cls(
            id=d["id"],
            terminal_ids=d.get("terminal_ids", []),
            reference=bool(d.get("reference", False)),
            label=d.get("label"),
        )


@dataclass
class CircuitScene:
    schema_version: str = "3.0"
    domain: str = "circuits"
    subtype: str = "dc_linear"
    engine: str = "mna"
    source_width: int = 800
    source_height: int = 600
    background_url: str = ""
    reference_node: str = "N0"
    nodes: list[Node] = field(default_factory=list)
    components: list[Component] = field(default_factory=list)
    wires: list[Wire] = field(default_factory=list)
    ambiguities: list[dict[str, Any]] = field(default_factory=list)
    confidence: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "simulation": {
                "domain": self.domain,
                "subtype": self.subtype,
                "engine": self.engine,
            },
            "geometry": {
                "space": "source_px",
                "source_width": self.source_width,
                "source_height": self.source_height,
            },
            "visual": {
                "background_url": self.background_url,
            },
            "circuit": {
                "reference_node": self.reference_node,
                "nodes": [n.to_dict() for n in self.nodes],
                "components": [c.to_dict() for c in self.components],
                "wires": [w.to_dict() for w in self.wires],
            },
            "ambiguities": self.ambiguities,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CircuitScene:
        sim = data.get("simulation", {})
        geom = data.get("geometry", {})
        vis = data.get("visual", {})
        ckt = data.get("circuit", {})

        nodes = [Node.from_dict(n) for n in ckt.get("nodes", [])]
        comps = [Component.from_dict(c) for c in ckt.get("components", [])]
        wires = [Wire.from_dict(w) for w in ckt.get("wires", [])]

        return cls(
            schema_version=data.get("schema_version", "3.0"),
            domain=sim.get("domain", "circuits"),
            subtype=sim.get("subtype", "dc_linear"),
            engine=sim.get("engine", "mna"),
            source_width=int(geom.get("source_width", 800)),
            source_height=int(geom.get("source_height", 600)),
            background_url=vis.get("background_url", ""),
            reference_node=ckt.get("reference_node", "N0"),
            nodes=nodes,
            components=comps,
            wires=wires,
            ambiguities=data.get("ambiguities", []),
            confidence=data.get("confidence", {}),
            metadata=data.get("metadata", {}),
        )

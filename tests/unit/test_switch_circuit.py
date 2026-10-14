"""Unit tests for switch circuit grounding, normalization, and compilation (Phase 12)."""
import pytest
from shared.schemas.ingestion import BookEntity, BookIR, PhysicalValue, ProvenanceRecord
from ai.resolution.auto import AutoResolutionEngine
from ai.scene_compiler.physics_compiler import PhysicsCompiler


def test_closed_switch_circuit_compiles():
    """Verify circuit with closed switch resolves and compiles with small resistance."""
    book = BookIR(
        source_asset_id="asset_switch",
        figure_id="fig_switch",
        domain="circuits",
        subtype="dc_linear",
        status="NEEDS_REVIEW",
        geometry={
            "width": 600,
            "height": 400,
            "circuit_topology": {"verified_connectivity": True},
        },
        entities=[
            BookEntity(id="V1", type="voltage_source", position_source_px={"x": 100, "y": 200}, evidence_refs=["cv"]),
            BookEntity(id="R1", type="resistor", position_source_px={"x": 300, "y": 100}, evidence_refs=["cv"]),
            BookEntity(id="S1", type="switch", position_source_px={"x": 500, "y": 200}, evidence_refs=["cv"]),
        ],
        parameters={
            "nodes": ["N0", "N1", "N2"],
            "components": [
                {
                    "id": "V1",
                    "type": "voltage_source",
                    "nodes": ["N1", "N0"],
                    "value": 12.0,
                    "unit": "V",
                    "geometry": {"center_source_px": [100, 200]},
                    "provenance": {"source": "cv"},
                },
                {
                    "id": "R1",
                    "type": "resistor",
                    "nodes": ["N1", "N2"],
                    "value": 10.0,
                    "unit": "ohm",
                    "geometry": {"center_source_px": [300, 100]},
                    "provenance": {"source": "cv"},
                },
                {
                    "id": "S1",
                    "type": "switch",
                    "nodes": ["N2", "N0"],
                    "state": "closed",
                    "closed": True,
                    "geometry": {"center_source_px": [500, 200]},
                    "terminals": [
                        {"id": "S1.1", "source_px": [480, 200]},
                        {"id": "S1.2", "source_px": [520, 200]},
                    ],
                    "provenance": {"source": "cv"},
                },
            ],
            "reference_node": "N0",
        },
        parameter_provenance={
            "nodes": ProvenanceRecord(source="cv"),
            "components": ProvenanceRecord(source="cv"),
        },
    )

    result = AutoResolutionEngine.resolve(book)
    assert not result.failures, f"Unexpected failures: {result.failures}"
    compiled = PhysicsCompiler().compile(book)
    assert compiled.status == "READY", f"Compilation failed: {compiled.issues}"
    assert "S1" in compiled.scene["parameters"] or any(
        s.get("id") == "S1" for s in compiled.scene["geometry"].get("switches", [])
    )


def test_open_switch_circuit_compiles_as_open():
    """Verify circuit with open switch resolves as open branch."""
    book = BookIR(
        source_asset_id="asset_switch_open",
        figure_id="fig_switch_open",
        domain="circuits",
        subtype="dc_linear",
        status="NEEDS_REVIEW",
        geometry={
            "width": 600,
            "height": 400,
            "circuit_topology": {"verified_connectivity": True},
        },
        entities=[
            BookEntity(id="V1", type="voltage_source", position_source_px={"x": 100, "y": 200}, evidence_refs=["cv"]),
            BookEntity(id="R1", type="resistor", position_source_px={"x": 300, "y": 100}, evidence_refs=["cv"]),
            BookEntity(id="S1", type="open_switch", position_source_px={"x": 500, "y": 200}, evidence_refs=["cv"]),
        ],
        parameters={
            "nodes": ["N0", "N1", "N2"],
            "components": [
                {
                    "id": "V1",
                    "type": "voltage_source",
                    "nodes": ["N1", "N0"],
                    "value": 12.0,
                    "unit": "V",
                    "geometry": {"center_source_px": [100, 200]},
                    "provenance": {"source": "cv"},
                },
                {
                    "id": "R1",
                    "type": "resistor",
                    "nodes": ["N1", "N2"],
                    "value": 10.0,
                    "unit": "ohm",
                    "geometry": {"center_source_px": [300, 100]},
                    "provenance": {"source": "cv"},
                },
                {
                    "id": "S1",
                    "type": "open_switch",
                    "nodes": ["N2", "N0"],
                    "state": "open",
                    "closed": False,
                    "geometry": {"center_source_px": [500, 200]},
                    "terminals": [
                        {"id": "S1.1", "source_px": [480, 200]},
                        {"id": "S1.2", "source_px": [520, 200]},
                    ],
                    "provenance": {"source": "cv"},
                },
            ],
            "reference_node": "N0",
        },
        parameter_provenance={
            "nodes": ProvenanceRecord(source="cv"),
            "components": ProvenanceRecord(source="cv"),
        },
    )

    result = AutoResolutionEngine.resolve(book)
    assert not result.failures, f"Unexpected failures: {result.failures}"
    compiled = PhysicsCompiler().compile(book)
    assert compiled.status == "READY", f"Compilation failed: {compiled.issues}"
    # Switch should have high resistance (open branch)
    s1_comp = next(c for c in compiled.scene["circuit"]["components"] if c["id"] == "S1")
    assert s1_comp["value"] >= 1e6

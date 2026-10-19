"""Regression checks for automatic resolution and circuit compilation gates."""

import json
import math

from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.resolution.engine import ResolutionEngine
from ai.resolution.evaluator import ReadinessEvaluator
from shared.schemas.ingestion import BookEntity, BookIR, BookIRStatus, PhysicalValue, ProvenanceRecord


def test_review_overriding_ocr_value_keeps_json_serializable_provenance():
    book_ir = BookIR(
        source_asset_id="asset-1", figure_id="figure-1", domain="optics",
        subtype="interface_refraction", status=BookIRStatus.NEEDS_REVIEW,
        parameters={"n1": PhysicalValue(value=1.0, unit="dimensionless", status="observed",
                                         provenance=ProvenanceRecord(source="ocr"))},
    )

    result = ResolutionEngine.apply_resolution(book_ir, {
        "parameterName": "n1", "resolvedValue": 1.0, "canonicalUnit": "",
        "resolutionSource": "user_supplied",
    })

    assert result.success
    json.dumps(book_ir.resolutions["n1"])
    json.dumps(book_ir.parameter_provenance["n1"].to_dict())


def test_readiness_preserves_unsupported_classification_status():
    book_ir = BookIR(
        source_asset_id="asset-1", figure_id="figure-1", domain=None,
        subtype=None, status=BookIRStatus.UNSUPPORTED, isPhysics=True,
        provenance={"classification": "unsupported_physics"},
    )

    report = ReadinessEvaluator.evaluate(book_ir, mutate_status=True)

    assert not report.ready
    assert book_ir.status == BookIRStatus.UNSUPPORTED


def test_auto_resolve_does_not_accept_ocr_candidates_or_opt_in_policies():
    book_ir = BookIR(
        source_asset_id="asset-1",
        figure_id="figure-1",
        domain="mechanics",
        subtype="pendulum",
        status=BookIRStatus.NEEDS_REVIEW,
        provenance={
            "candidate_parameters": [
                {"numericValue": 0.8, "quantityCandidate": "length", "confidence": 0.95}
            ]
        },
    )

    result = ResolutionEngine.auto_resolve(book_ir)

    assert not result.ready
    assert "length" not in book_ir.parameters
    assert "gravity" not in book_ir.parameters
    assert "mass" not in book_ir.parameters
    assert "damping" not in book_ir.parameters
    assert not book_ir.resolutions


def test_compiler_rejects_resistor_only_circuit_even_if_marked_ready():
    book_ir = BookIR(
        source_asset_id="asset-1",
        figure_id="figure-1",
        domain="circuits",
        subtype="dc_linear",
        status=BookIRStatus.READY_TO_COMPILE,
        entities=[BookEntity(id="R1", type="resistor", position_source_px={"x": 40, "y": 40})],
        geometry={"width": 100, "height": 100},
        parameters={
            "nodes": [{"id": "N1"}, {"id": "N2"}],
            "components": [{"id": "R1", "type": "resistor", "nodes": ["N1", "N2"], "value": 10.0, "unit": "ohm"}],
        },
        parameter_provenance={
            "nodes": ProvenanceRecord(source="cv"),
            "components": ProvenanceRecord(source="cv"),
        },
    )

    result = PhysicsCompiler().compile(book_ir)

    readiness = ReadinessEvaluator.evaluate(book_ir)
    assert not readiness.ready
    assert any("voltage source" in blocker for blocker in readiness.blockers)

    assert result.status == "NEEDS_REVIEW"
    assert result.scene is None
    assert any(issue["code"] == "MISSING_CIRCUIT_SOURCE" for issue in result.issues)


def test_projectile_readiness_requires_grounded_scale_and_radius():
    book_ir = BookIR(
        source_asset_id="asset-1",
        figure_id="figure-1",
        domain="mechanics",
        subtype="projectile",
        status=BookIRStatus.NEEDS_REVIEW,
        entities=[BookEntity(id="ball", type="projectile_body", position_source_px={"x": 20, "y": 50})],
        geometry={"width": 100, "height": 100, "launch_position": {"x": 20, "y": 50}},
        parameters={
            "launch_position": {"x": 20, "y": 50},
            "launch_speed": 10.0,
            "launch_angle_deg": 45.0,
            "gravity": 9.80665,
        },
        parameter_provenance={
            key: ProvenanceRecord(source="ocr")
            for key in ("launch_position", "launch_speed", "launch_angle_deg", "gravity")
        },
    )

    report = ReadinessEvaluator.evaluate(book_ir)

    assert not report.ready
    assert "pixels_per_meter" in report.missing_requirements
    assert "ball_radius_px" in report.missing_requirements


def _ready_pendulum():
    book_ir = BookIR(
        source_asset_id="asset-1",
        figure_id="figure-1",
        domain="mechanics",
        subtype="pendulum",
        status=BookIRStatus.NEEDS_REVIEW,
        entities=[
            BookEntity(id="pivot", type="pivot", position_source_px={"x": 50, "y": 10}),
            BookEntity(id="bob", type="bob", position_source_px={"x": 50, "y": 90}),
            BookEntity(id="string", type="string", position_source_px={"x": 50, "y": 10}),
        ],
        geometry={
            "pivot": {"x": 50, "y": 10},
            "bob_center": {"x": 50, "y": 90},
            "string_length_px": 80.0,
            "bob_radius_px": 5.0,
            "width": 100.0,
            "height": 100.0,
        },
    )
    ResolutionEngine.apply_resolution(book_ir, {
        "parameterName": "length",
        "resolvedValue": 0.8,
        "canonicalUnit": "m",
        "resolutionSource": "user_supplied",
    })
    for policy in ("policy_earth_gravity", "policy_standard_mass", "policy_zero_damping"):
        ResolutionEngine.apply_policy(book_ir, policy)

    assert book_ir.status == BookIRStatus.READY_TO_COMPILE
    assert PhysicsCompiler().compile(book_ir).status == "READY"
    return book_ir


def test_compiler_rechecks_provenance_after_ready_status_becomes_stale():
    book_ir = _ready_pendulum()

    # The value remains numerically usable, but its evidence is gone. The
    # stored status must not authorize compilation after this change.
    book_ir.resolutions.pop("length", None)
    book_ir.parameter_provenance.pop("length", None)
    assert not ReadinessEvaluator.evaluate(book_ir).ready

    result = PhysicsCompiler().compile(book_ir)
    assert result.status == "NEEDS_REVIEW"
    assert result.scene is None
    assert any(issue["code"] == "READINESS_REVOKED" for issue in result.issues)


def test_conflicting_parameter_and_resolution_block_compilation():
    book_ir = _ready_pendulum()
    book_ir.parameters["length"] = 1.2

    report = ReadinessEvaluator.evaluate(book_ir)
    assert not report.ready
    assert any("conflicts with its recorded resolution" in reason for reason in report.blockers)
    result = PhysicsCompiler().compile(book_ir)
    assert result.status == "NEEDS_REVIEW"
    assert result.scene is None


def test_unaccepted_opt_in_policy_blocks_compilation():
    book_ir = _ready_pendulum()
    book_ir.resolutions["mass"]["userAccepted"] = False

    report = ReadinessEvaluator.evaluate(book_ir)
    assert not report.ready
    assert any("lacks a valid, accepted policy" in reason for reason in report.blockers)
    result = PhysicsCompiler().compile(book_ir)
    assert result.status == "NEEDS_REVIEW"
    assert result.scene is None


def test_lens_object_without_grounded_height_cannot_be_fabricated():
    book_ir = BookIR(
        source_asset_id="asset-lens",
        figure_id="figure-lens",
        domain="optics",
        subtype="thin_lens",
        status=BookIRStatus.READY_TO_COMPILE,
        entities=[
            BookEntity(id="lens", type="lens", position_source_px={"x": 100, "y": 100}),
            BookEntity(id="object", type="optical_object", position_source_px={"x": 40, "y": 100}),
        ],
        geometry={"lens_center": {"x": 100, "y": 100}, "aperture_height_px": 80, "width": 200, "height": 200},
        parameters={"focal_length_px": 60},
        parameter_provenance={"focal_length_px": ProvenanceRecord(source="author_override")},
    )
    result = PhysicsCompiler().compile(book_ir)
    assert result.status == "NEEDS_REVIEW"
    assert result.scene is None
    assert any(issue["code"] == "MISSING_OBJECT_HEIGHT_PX" for issue in result.issues)


def _ready_refraction():
    return BookIR(
        source_asset_id="asset-refraction",
        figure_id="figure-refraction",
        domain="optics",
        subtype="interface_refraction",
        status=BookIRStatus.READY_TO_COMPILE,
        entities=[BookEntity(id="boundary", type="interface_boundary", position_source_px={"x": 100, "y": 100})],
        geometry={"boundary_y": 100, "normal_x": 100, "source_position": {"x": 50, "y": 50}, "width": 200, "height": 200},
        parameters={"n1": 1.0, "n2": 1.5},
        parameter_provenance={
            "n1": ProvenanceRecord(source="author_override"),
            "n2": ProvenanceRecord(source="author_override"),
        },
    )


def test_refraction_rejects_dimensioned_refractive_index():
    book_ir = _ready_refraction()
    book_ir.parameters["n2"] = {"value": 1.5, "unit": "kg"}
    assert not ReadinessEvaluator.evaluate(book_ir).ready
    result = PhysicsCompiler().compile(book_ir)
    assert result.status == "NEEDS_REVIEW"
    assert result.scene is None


def test_refraction_converts_radian_incident_angle_to_degrees():
    book_ir = _ready_refraction()
    book_ir.parameters["theta1"] = {"value": math.pi / 6, "unit": "rad"}
    book_ir.parameter_provenance["theta1"] = ProvenanceRecord(source="author_override")
    result = PhysicsCompiler().compile(book_ir)
    assert result.status == "READY", result.issues
    assert math.isclose(result.scene["parameters"]["theta1"]["value"], 30.0)


def test_compiled_scene_preserves_reviewed_parameter_sources():
    result = PhysicsCompiler().compile(_ready_pendulum())
    assert result.status == "READY", result.issues
    assert result.scene["parameters"]["length"]["provenance"] == "user_supplied"
    assert result.scene["parameters"]["mass"]["provenance"] == "policy_default"
    assert result.scene["parameters"]["mass"]["evidenceProvenance"]["userAccepted"] is True


def _ready_circuit():
    return BookIR(
        source_asset_id="asset-circuit",
        figure_id="figure-circuit",
        domain="circuits",
        subtype="dc_linear",
        status=BookIRStatus.READY_TO_COMPILE,
        entities=[BookEntity(id="R1", type="resistor", position_source_px={"x": 50, "y": 50}),
                  BookEntity(id="V1", type="voltage_source", position_source_px={"x": 20, "y": 50})],
        geometry={"width": 100, "height": 100},
        parameters={
            "nodes": ["N0", "N1"],
            "reference_node": "N0",
            "components": [
                {"id": "V1", "type": "voltage_source", "nodes": ["N1", "N0"], "value": 12.0, "unit": "V",
                 "terminals": [{"id":"V1.t1","node":"N1"},{"id":"V1.t2","node":"N0"}]},
                {"id": "R1", "type": "resistor", "nodes": ["N1", "N0"], "value": 1.0, "unit": "kΩ",
                 "terminals": [{"id":"R1.t1","node":"N1"},{"id":"R1.t2","node":"N0"}]},
            ],
        },
        parameter_provenance={
            "nodes": ProvenanceRecord(source="author_override"),
            "components": ProvenanceRecord(source="author_override"),
        },
    )


def test_circuit_component_units_are_normalized_without_mutating_book_evidence():
    book_ir = _ready_circuit()
    result = PhysicsCompiler().compile(book_ir)
    assert result.status == "READY", result.issues
    resistor = next(c for c in result.scene["circuit"]["components"] if c["id"] == "R1")
    assert resistor["value"] == 1000.0
    assert resistor["unit"] == "ohm"
    assert book_ir.parameters["components"][1]["value"] == 1.0
    assert book_ir.parameters["components"][1]["unit"] == "kΩ"


def test_circuit_rejects_source_with_resistance_unit():
    book_ir = _ready_circuit()
    book_ir.parameters["components"][0]["unit"] = "ohm"
    result = PhysicsCompiler().compile(book_ir)
    assert result.status == "NEEDS_REVIEW"
    assert result.scene is None
    assert any(issue["code"] == "INCOMPATIBLE_CIRCUIT_UNIT" for issue in result.issues)


def test_circuit_switch_semantics_block_unverified_graph():
    book_ir = _ready_circuit()
    book_ir.entities.append(BookEntity(id="S1", type="switch"))
    result = PhysicsCompiler().compile(book_ir)
    assert result.status == "NEEDS_REVIEW"
    assert result.scene is None
    assert not ReadinessEvaluator.evaluate(book_ir).ready

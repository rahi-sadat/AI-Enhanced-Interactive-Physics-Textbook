"""Automatic policies must never replace missing pixels with a known fixture."""
from ai.resolution.auto import AutoResolutionEngine
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from shared.schemas.ingestion import BookEntity, BookIR, PhysicalValue, ProvenanceRecord


def _book(geometry):
    return BookIR(
        source_asset_id="asset_unknown_filename",
        figure_id="figure_1",
        domain="mechanics",
        subtype="pendulum",
        status="NEEDS_REVIEW",
        geometry=geometry,
    )


def test_missing_landmarks_cannot_be_auto_resolved():
    book = _book({"width": 800, "height": 600})
    result = AutoResolutionEngine.resolve(book)
    assert result.assumptions == []
    assert result.failures[0]["code"] == "GEOMETRY_NOT_FOUND"
    assert book.entities == []
    assert book.parameters == {}
    assert book.status == "NEEDS_REVIEW"


def test_grounded_pendulum_receives_only_named_model_policies():
    geometry = {
        "width": 800, "height": 600,
        "pivot": {"x": 250, "y": 80},
        "bob_center": {"x": 300, "y": 480},
        "string_length_px": 403.1,
        "bob_radius_px": 20,
    }
    book = _book(geometry.copy())
    result = AutoResolutionEngine.resolve(book)
    assert {a["parameter"] for a in result.assumptions} == {"gravity", "damping", "mass", "length"}
    assert all(a["policyId"] and a["policyVersion"] and a["provenance"] == "auto_policy" for a in result.assumptions)
    assert all(not r["userAccepted"] for r in book.resolutions.values())
    assert book.geometry == geometry
    assert book.entities == []


def test_cv_parameter_landmarks_are_accepted_without_fabricating_geometry():
    book = _book({"width": 800, "height": 600})
    book.parameters = {
        "pivot": {"x": 250, "y": 80, "provenance": {"source": "cv"}},
        "bob_position": {"x": 300, "y": 480, "provenance": {"source": "cv"}},
        "string_length_px": {"value": 403.1, "provenance": {"source": "cv"}},
        "bob_radius_px": {"value": 20, "provenance": {"source": "cv"}},
    }
    result = AutoResolutionEngine.resolve(book)
    assert not result.failures
    assert len(result.assumptions) == 4
    assert book.geometry == {"width": 800, "height": 600}


def test_out_of_bounds_landmark_cannot_be_policy_resolved():
    book = _book({"width": 800, "height": 600,
                  "pivot": {"x": 900, "y": 80}, "bob_center": {"x": 300, "y": 480},
                  "string_length_px": 403.1, "bob_radius_px": 20})
    result = AutoResolutionEngine.resolve(book)
    assert result.failures[0]["code"] == "REGISTRATION_MISMATCH"
    assert result.assumptions == []


def test_unlabelled_grounded_circuit_gets_normalized_values_only():
    book = BookIR(source_asset_id="asset_circuit", figure_id="figure_1",
                  domain="circuits", subtype="dc_linear", status="NEEDS_REVIEW",
                  geometry={"width": 500, "height": 400,
                            "circuit_topology": {"verified_connectivity": True, "node_count": 2}},
                  entities=[BookEntity(id="r1", type="resistor", position_source_px={"x": 200, "y": 100})],
                  parameters={"nodes": [{"id": "N0"}, {"id": "N1"}],
                              "components": [
                                  {"id": "V1", "type": "voltage_source", "nodes": ["N0", "N1"],
                                   "geometry": {"center_source_px": [100, 200]}, "value": None},
                                  {"id": "R1", "type": "resistor", "nodes": ["N1", "N0"],
                                   "geometry": {"center_source_px": [300, 200]}, "value": None},
                              ]},
                  parameter_provenance={"nodes": {"source": "cv"},
                                        "components": {"source": "cv"}})
    result = AutoResolutionEngine.resolve(book)
    assert not result.failures
    assert {a["parameter"] for a in result.assumptions} == {"V1", "R1"}
    assert [comp["value"] for comp in book.parameters["components"]] == [10, 100]
    assert all(comp["provenance"]["source"] == "auto_policy" for comp in book.parameters["components"])
    compiled = PhysicsCompiler().compile(book)
    assert compiled.status == "READY", compiled.issues
    assert compiled.scene["parameters"]["V1"]["provenance"] == "auto_policy"


def test_circuit_without_grounded_topology_stays_unresolved():
    book = BookIR(source_asset_id="asset_circuit", figure_id="figure_1",
                  domain="circuits", subtype="dc_linear", status="NEEDS_REVIEW",
                  geometry={"width": 500, "height": 400,
                            "circuit_topology": {"verified_connectivity": False}},
                  parameters={"nodes": [], "components": []})
    result = AutoResolutionEngine.resolve(book)
    assert result.failures[0]["code"] == "TOPOLOGY_INVALID"
    assert result.assumptions == []
    assert book.parameters["components"] == []


def test_compiled_scene_exposes_automatic_assumptions():
    book = _book({"width": 800, "height": 600,
                  "pivot": {"x": 250, "y": 80}, "bob_center": {"x": 300, "y": 480},
                  "string_length_px": 403.1, "bob_radius_px": 20})
    book.entities = [
        BookEntity(id="pivot", type="pivot", position_source_px={"x": 250, "y": 80}, evidence_refs=["cv"]),
        BookEntity(id="bob", type="bob", position_source_px={"x": 300, "y": 480}, evidence_refs=["cv"]),
        BookEntity(id="string", type="string", position_source_px={"x": 250, "y": 80}, evidence_refs=["cv"]),
    ]
    book.parameters = {
        "pivot": {"x": 250, "y": 80, "provenance": {"source": "cv"}},
        "bob_position": {"x": 300, "y": 480, "provenance": {"source": "cv"}},
        "string_length_px": {"value": 403.1, "unit": "px", "provenance": {"source": "cv"}},
        "bob_radius_px": {"value": 20, "unit": "px", "provenance": {"source": "cv"}},
    }
    AutoResolutionEngine.resolve(book)
    compiled = PhysicsCompiler().compile(book)
    assert compiled.status == "READY", compiled.issues
    assert len(compiled.scene["assumptions"]) == 4
    assert compiled.scene["parameters"]["gravity"]["provenance"] == "auto_policy"


def test_refraction_incident_angle_is_derived_only_from_observed_values():
    observed = lambda value, ref: PhysicalValue(
        value=value, unit="deg" if ref == "angle" else "dimensionless",
        status="observed", provenance=ProvenanceRecord(source="ocr", evidence_refs=[ref]),
    )
    book = BookIR(source_asset_id="random_name", figure_id="figure_1",
                  domain="optics", subtype="interface_refraction", status="NEEDS_REVIEW",
                  geometry={"width": 393, "height": 328, "boundary_y": 150, "normal_x": 190},
                  entities=[BookEntity(id="boundary", type="interface_boundary",
                                       position_source_px={"x": 190, "y": 150}, evidence_refs=["cv"])],
                  parameters={"n1": observed(1.5, "n1"), "n2": observed(1.0, "n2"),
                              "refracted_angle": observed(30.0, "angle")},
                  parameter_provenance={"boundary_y": ProvenanceRecord(source="diagram_measurement", evidence_refs=["cv"]),
                                        "normal_x": ProvenanceRecord(source="diagram_measurement", evidence_refs=["cv"])})
    AutoResolutionEngine.resolve(book)
    angle = book.parameters["incident_angle"]
    assert abs(angle.value - 19.4712206345) < 1e-6
    assert angle.provenance.source == "derived"
    assert set(angle.provenance.evidence_refs) == {"n1", "n2", "angle"}
    compiled = PhysicsCompiler().compile(book)
    assert compiled.status == "READY", compiled.issues
    assert compiled.scene["parameters"]["theta1"]["provenance"] == "derived"


def test_prism_policy_needs_observed_polygon():
    book = BookIR(source_asset_id="neutral.png", figure_id="figure_1",
                  domain="optics", subtype="prism", status="NEEDS_REVIEW",
                  geometry={"width": 500, "height": 400,
                            "vertices": [{"x": 250, "y": 50}, {"x": 120, "y": 300}, {"x": 380, "y": 300}]},
                  entities=[BookEntity(id="prism", type="prism_body")])
    result = AutoResolutionEngine.resolve(book)
    assert "ray_origin" not in book.geometry
    assert not any(item["parameter"] == "ray_origin" for item in result.assumptions)


def test_lens_without_printed_object_has_a_disclosed_runtime_object():
    book = BookIR(source_asset_id="neutral.png", figure_id="figure_1",
                  domain="optics", subtype="thin_lens", status="NEEDS_REVIEW",
                  geometry={"width": 900, "height": 450,
                            "lens_center": {"x": 450, "y": 225}},
                  entities=[BookEntity(id="lens", type="lens",
                                       position_source_px={"x": 450, "y": 225}, evidence_refs=["cv"])],
                  parameters={"aperture_height_px": PhysicalValue(
                      value=300, unit="px", status="observed",
                      provenance=ProvenanceRecord(source="diagram_measurement", evidence_refs=["cv"])),
                              "lens_center": {"x": 450, "y": 225,
                                              "provenance": {"source": "diagram_measurement"}}})
    result = AutoResolutionEngine.resolve(book)
    compiled = PhysicsCompiler().compile(book)
    assert compiled.status == "READY", compiled.issues
    assert {item["parameter"] for item in result.assumptions} == {
        "focal_length_px", "objectDistance", "object_height_px",
    }
    assert compiled.scene["parameters"]["objectDistance"]["provenance"] == "auto_policy"
    assert compiled.scene["parameters"]["objectHeight"]["provenance"] == "auto_policy"

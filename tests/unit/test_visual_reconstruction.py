"""Offline contracts for native-image reconstruction, independent of solver readiness."""
from copy import deepcopy
import json

import pytest

from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.resolution.engine import ResolutionEngine
from ai.resolution.evaluator import ReadinessEvaluator
from shared.schemas.evidence import (
    EvidenceMethod, EvidenceRecord, MaskArtifact, SourceBBox, SourceLine,
    SourcePoint, SourcePolygon,
)
from shared.schemas.ingestion import BookEntity, BookIR, BookIRStatus
from shared.schemas.visual_reconstruction import (
    DynamicVisualAsset, ObservedGeometry, RegistrationMetric, RegistrationReport,
    RegistrationStatus, VisualConstraint, VisualReadiness, VisualReconstruction,
)


def _complete_reconstruction():
    observed = ObservedGeometry(
        source_width=800, source_height=600,
        landmarks={"pivot": SourcePoint(200, 100), "bob": SourcePoint(200, 500)},
        lines={"string": SourceLine(SourcePoint(200, 100), SourcePoint(200, 480))},
        curves={"arc": [SourcePoint(180, 499), SourcePoint(200, 500), SourcePoint(220, 499)]},
        masks={"bob_mask": MaskArtifact(
            id="bob_mask", source_asset_id="asset", figure_id="figure",
            source_width=800, source_height=600,
            bbox_source_px=SourceBBox(180, 480, 40, 40),
            centroid_source_px=SourcePoint(200, 500), area_px=1200,
            rle_counts="encoded-mask-reference", confidence=0.9,
            polygon_approx=SourcePolygon([
                SourcePoint(180, 480), SourcePoint(220, 480), SourcePoint(200, 520),
            ]), prompt_provenance={"source": "classical_cv", "evidenceRefs": ["ev_cv"]},
        )},
        text_anchors={"length_label": SourcePoint(240, 300)},
        topology={"terminal_a": ["terminal_b"], "terminal_b": ["terminal_a"]},
        evidence_refs={
            "pivot": ["ev_cv"], "bob": ["ev_cv", "ev_seg"], "string": ["ev_cv"],
            "arc": ["ev_cv"], "bob_mask": ["ev_seg"], "length_label": ["ev_ocr"],
            "terminal_a": ["ev_cv"], "terminal_b": ["ev_cv"],
        },
    )
    constraints = [
        VisualConstraint("c_pivot", "landmark", ["pivot"], evidence_refs=["ev_cv"]),
        VisualConstraint("c_string", "line", ["string"], evidence_refs=["ev_cv"]),
        VisualConstraint("c_arc", "curve", ["arc"], evidence_refs=["ev_cv"]),
        VisualConstraint("c_mask", "mask", ["bob_mask"], evidence_refs=["ev_seg"]),
        VisualConstraint("c_text", "text_anchor", ["length_label"], evidence_refs=["ev_ocr"]),
        VisualConstraint("c_topology", "topology", ["terminal_a", "terminal_b"], evidence_refs=["ev_cv"]),
    ]
    metrics = [
        RegistrationMetric("c_pivot", "radial_error", 0.2, "source_px", True, 1),
        RegistrationMetric("c_string", "line_distance", 0.3, "source_px", True, 20),
        RegistrationMetric("c_arc", "curve_distance", 0.4, "source_px", True, 30),
        RegistrationMetric("c_mask", "mask_iou", 0.95, "ratio", True, 1200),
        RegistrationMetric("c_text", "anchor_error", 0.2, "source_px", True, 1),
        RegistrationMetric("c_topology", "topology_match", True, "boolean", True, 2),
    ]
    return VisualReconstruction(
        observed_geometry=observed, constraints=constraints,
        dynamic_visuals=[DynamicVisualAsset(
            entity_id="e_bob", source_bbox=SourceBBox(180, 480, 40, 40),
            anchor_source_px=SourcePoint(200, 500), transform_origin=SourcePoint(200, 100),
            source_mask_url="/generated/bob-mask.png", sprite_url="/generated/bob.png",
            restoration_mask_url="/generated/restoration-mask.png",
            clean_background_url="/generated/background.png",
            restoration_patch_url="/generated/patch.png",
            restoration_bbox=SourceBBox(175, 475, 50, 50),
            extraction_confidence=0.9, evidence_refs=["ev_seg"],
        )],
        registration=RegistrationReport(
            status=RegistrationStatus.PASSED, mean_error_px=0.3, p95_error_px=0.5,
            landmark_errors={"pivot": 0.2}, curve_errors={"arc": 0.4},
            mask_iou=0.95, topology_match=True, confidence=0.92, metrics=metrics,
        ),
        visual_readiness=VisualReadiness.PHYSICS_VERIFIED,
        physics_evidence_refs=["ev_length"],
    )


def _book_with_reconstruction(reconstruction=None):
    return BookIR(
        source_asset_id="asset", figure_id="figure", domain="mechanics", subtype="pendulum",
        entities=[BookEntity(id="e_bob", type="bob")],
        geometry={"width": 800, "height": 600},
        evidence={
            key: EvidenceRecord(key, method, source_asset_id="asset", figure_id="figure")
            for key, method in {
                "ev_cv": EvidenceMethod.CLASSICAL_CV, "ev_seg": EvidenceMethod.SEGMENTATION,
                "ev_ocr": EvidenceMethod.OCR, "ev_length": EvidenceMethod.MANUAL,
            }.items()
        },
        parameters={"length": {"value": 0.8, "unit": "m", "provenance": {"source": "author_override"}}},
        parameter_provenance={"length": {"source": "author_override", "evidenceRefs": ["ev_length"]}},
        visual_reconstruction=reconstruction or _complete_reconstruction(),
    )


def test_complete_bookir_json_roundtrip_preserves_typed_visuals_and_provenance():
    book = _book_with_reconstruction()
    encoded = book.to_dict()
    restored = BookIR.from_dict(json.loads(json.dumps(encoded, allow_nan=False)))
    assert restored.to_dict() == encoded
    visual = restored.visual_reconstruction
    assert isinstance(visual, VisualReconstruction)
    assert isinstance(visual.observed_geometry.landmarks["pivot"], SourcePoint)
    assert isinstance(visual.observed_geometry.lines["string"], SourceLine)
    assert isinstance(visual.observed_geometry.masks["bob_mask"], MaskArtifact)
    assert isinstance(visual.observed_geometry.masks["bob_mask"].polygon_approx, SourcePolygon)
    assert isinstance(visual.dynamic_visuals[0], DynamicVisualAsset)
    assert isinstance(visual.registration.metrics[0], RegistrationMetric)
    assert visual.visual_readiness is VisualReadiness.PHYSICS_VERIFIED
    assert restored.parameters == book.parameters
    assert restored.parameter_provenance == book.parameter_provenance
    # Serialization must not leak live reconstruction collections to API callers.
    encoded["visualReconstruction"]["observedGeometry"]["landmarks"]["pivot"]["x"] = 0
    assert book.visual_reconstruction.observed_geometry.landmarks["pivot"].x == 200
    encoded["visualReconstruction"]["observedGeometry"]["masks"]["bob_mask"]["promptProvenance"]["evidenceRefs"].append("external")
    assert book.visual_reconstruction.observed_geometry.masks["bob_mask"].prompt_provenance["evidenceRefs"] == ["ev_cv"]


def test_legacy_bookir_has_no_new_field_or_readiness_claim():
    book = BookIR(parameters={"mass": {"value": None, "provenance": {"source": "inferred"}}})
    encoded = book.to_dict()
    assert "visualReconstruction" not in encoded
    restored = BookIR.from_dict(json.loads(json.dumps(encoded)))
    assert restored.visual_reconstruction is None
    assert restored.to_dict() == encoded
    assert restored.status == BookIRStatus.UNRESOLVED


def test_unevaluated_registration_does_not_fabricate_zero_error_or_confidence():
    visual = VisualReconstruction(ObservedGeometry(800, 600))
    report = visual.to_dict()["registration"]
    assert visual.visual_readiness is VisualReadiness.NOT_EVALUATED
    assert report["status"] == "NOT_EVALUATED"
    assert report["meanErrorPx"] is None and report["p95ErrorPx"] is None
    assert report["maskIou"] is None and report["topologyMatch"] is None
    assert report["confidence"] == 0 and report["metrics"] == []


@pytest.mark.parametrize("coordinate_space", ["world", "local", "viewport_px", "css_px", "normalized"])
def test_observations_reject_other_coordinate_spaces(coordinate_space):
    with pytest.raises(ValueError):
        ObservedGeometry(800, 600, coordinate_space=coordinate_space)


@pytest.mark.parametrize("value", [True, 0, -1, 800.0, "800", float("nan"), float("inf")])
def test_native_dimensions_are_positive_json_integers(value):
    with pytest.raises(ValueError):
        ObservedGeometry(value, 600)


@pytest.mark.parametrize("value", [True, "200", float("nan"), float("inf"), float("-inf"), -1, 801])
def test_invalid_or_outside_image_points_are_rejected(value):
    with pytest.raises((ValueError, TypeError)):
        ObservedGeometry(800, 600, landmarks={"pivot": {"x": value, "y": 100}})


def test_observed_line_and_curve_require_real_samples():
    with pytest.raises(ValueError):
        ObservedGeometry(800, 600, lines={"line": SourceLine(SourcePoint(10, 10), SourcePoint(10, 10))})
    with pytest.raises(ValueError):
        ObservedGeometry(800, 600, curves={"curve": [SourcePoint(10, 10)]})


def test_mask_must_match_its_id_dimensions_and_source_bounds():
    for change in ({"id": "wrong"}, {"sourceWidth": 400}, {"bboxSourcePx": {"x": 790, "y": 480, "width": 40, "height": 40}}):
        payload = _complete_reconstruction().to_dict()
        payload["observedGeometry"]["masks"]["bob_mask"].update(change)
        with pytest.raises(ValueError):
            VisualReconstruction.from_dict(payload)


@pytest.mark.parametrize("field,value", [
    ("rleCounts", [10, 20]), ("rleCounts", True), ("promptProvenance", ["ev_cv"]),
    ("promptProvenance", None),
])
def test_mask_encoding_and_prompt_provenance_have_explicit_wire_types(field, value):
    payload = _complete_reconstruction().to_dict()
    payload["observedGeometry"]["masks"]["bob_mask"][field] = value
    with pytest.raises(ValueError):
        VisualReconstruction.from_dict(payload)


def test_mask_polygon_cannot_silently_drop_unknown_geometry_fields():
    payload = _complete_reconstruction().to_dict()
    payload["observedGeometry"]["masks"]["bob_mask"]["polygonApprox"]["coordinateSpace"] = "css_px"
    with pytest.raises(ValueError):
        VisualReconstruction.from_dict(payload)


@pytest.mark.parametrize("topology", [
    {"a": ["b"]}, {"a": ["b"], "b": []}, {"a": ["a"]}, {"a": ["b", "b"], "b": ["a"]},
])
def test_topology_rejects_dangling_asymmetric_self_and_duplicate_edges(topology):
    with pytest.raises(ValueError):
        ObservedGeometry(800, 600, topology=topology)


def test_constraints_and_residuals_reject_missing_or_wrong_feature_references():
    for observed_ref in ("missing", "arc"):
        payload = _complete_reconstruction().to_dict()
        payload["constraints"][0]["observedRefs"] = [observed_ref]
        with pytest.raises(ValueError):
            VisualReconstruction.from_dict(payload)
    payload = _complete_reconstruction().to_dict()
    payload["registration"]["landmarkErrors"]["missing"] = 0.1
    with pytest.raises(ValueError):
        VisualReconstruction.from_dict(payload)


def test_dynamic_asset_requires_declared_entity_and_bounded_source_geometry():
    visual = _complete_reconstruction()
    visual.dynamic_visuals[0].entity_id = "missing"
    with pytest.raises(ValueError):
        _book_with_reconstruction(visual)
    payload = _complete_reconstruction().to_dict()
    payload["dynamicVisuals"][0]["anchorSourcePx"] = {"x": 900, "y": 100}
    with pytest.raises(ValueError):
        VisualReconstruction.from_dict(payload)


def test_partial_dynamic_asset_is_valid_but_restoration_patch_needs_placement():
    asset = DynamicVisualAsset("e_bob", SourceBBox(180, 480, 40, 40), SourcePoint(200, 500), SourcePoint(200, 100))
    assert asset.sprite_url is None and asset.clean_background_url is None
    asset.restoration_patch_url = "/generated/patch.png"
    with pytest.raises(ValueError):
        asset.to_dict()


@pytest.mark.parametrize("field,value", [
    ("mean_error_px", -1), ("p95_error_px", float("nan")), ("mask_iou", 1.01),
    ("confidence", float("inf")), ("confidence", True), ("confidence", -0.1),
    ("topology_match", "true"),
])
def test_registration_rejects_invalid_measurements(field, value):
    with pytest.raises(ValueError):
        RegistrationReport(**{field: value})


@pytest.mark.parametrize("measurements", [
    {"mean_error_px": 0}, {"p95_error_px": 0}, {"mask_iou": 1},
    {"topology_match": True}, {"confidence": 0.5}, {"landmark_errors": {"pivot": 0}},
    {"metrics": [RegistrationMetric("c", "error", 0, "source_px", True, 1)]},
])
def test_not_evaluated_status_cannot_claim_measured_results(measurements):
    with pytest.raises(ValueError):
        RegistrationReport(**measurements)


@pytest.mark.parametrize("field", ["landmark_errors", "curve_errors"])
def test_per_feature_residuals_cannot_claim_null_measurements(field):
    with pytest.raises(ValueError):
        RegistrationReport(status=RegistrationStatus.NEEDS_REVIEW, **{field: {"feature": None}})


@pytest.mark.parametrize("overrides", [
    {"value": True}, {"value": float("inf")}, {"unit": "css_px"},
    {"passed": "true"}, {"sample_count": 0}, {"sample_count": True},
    {"unit": "ratio", "value": 1.1}, {"unit": "boolean", "value": 1},
])
def test_registration_metrics_reject_unmeasured_or_mistyped_values(overrides):
    args = dict(constraint_id="c_pivot", name="error", value=0.2, unit="source_px", passed=True, sample_count=1)
    with pytest.raises(ValueError):
        RegistrationMetric(**{**args, **overrides})


def test_metric_name_and_constraint_id_are_independent_identifiers():
    metric = RegistrationMetric("landmark_error", "landmark_error", 0.2, "source_px", True, 1)
    assert RegistrationMetric.from_dict(metric.to_dict()) == metric


def test_passed_registration_requires_metrics_and_all_required_constraints():
    with pytest.raises(ValueError):
        RegistrationReport(status=RegistrationStatus.PASSED)
    payload = _complete_reconstruction().to_dict()
    payload["registration"]["metrics"].pop()
    with pytest.raises(ValueError):
        VisualReconstruction.from_dict(payload)


@pytest.mark.parametrize("change", ["failed_metric", "blocker", "wrong_constraint", "duplicate_metric", "topology_failure"])
def test_registration_cannot_pass_with_inconsistent_evidence(change):
    payload = _complete_reconstruction().to_dict()
    report = payload["registration"]
    if change == "failed_metric":
        report["metrics"][0]["passed"] = False
    elif change == "blocker":
        report["blockers"] = ["ambiguous pivot"]
    elif change == "wrong_constraint":
        report["metrics"][0]["constraintId"] = "missing"
    elif change == "duplicate_metric":
        report["metrics"].append(deepcopy(report["metrics"][0]))
    else:
        report["topologyMatch"] = False
    with pytest.raises(ValueError):
        VisualReconstruction.from_dict(payload)


@pytest.mark.parametrize("readiness", [VisualReadiness.AUTO_VISUAL, VisualReadiness.PHYSICS_VERIFIED])
def test_visual_readiness_requires_registration(readiness):
    with pytest.raises(ValueError):
        VisualReconstruction(ObservedGeometry(800, 600), visual_readiness=readiness, physics_evidence_refs=["ev_length"])


def test_auto_visual_does_not_require_or_invent_absolute_physical_evidence():
    payload = _complete_reconstruction().to_dict()
    payload["visualReadiness"] = "AUTO_VISUAL"
    payload["physicsEvidenceRefs"] = []
    visual = VisualReconstruction.from_dict(payload)
    assert visual.visual_readiness is VisualReadiness.AUTO_VISUAL
    assert visual.physics_evidence_refs == []
    payload["visualReadiness"] = "PHYSICS_VERIFIED"
    with pytest.raises(ValueError):
        VisualReconstruction.from_dict(payload)


def test_unknown_fields_and_mutated_invalid_geometry_fail_at_serialization():
    payload = _complete_reconstruction().to_dict()
    payload["observedGeometry"]["viewportWidth"] = 900
    with pytest.raises(ValueError):
        VisualReconstruction.from_dict(payload)
    book = _book_with_reconstruction()
    book.visual_reconstruction.observed_geometry.landmarks["pivot"].x = float("nan")
    with pytest.raises(ValueError):
        book.to_dict()


@pytest.mark.parametrize("container,dimensions", [
    ("geometry", {"width": 400, "height": 600}),
    ("geometry", {"source_width": 400, "source_height": 600}),
    ("provenance", {"source_width": 800, "source_height": 300}),
    ("parameters", {"source_width": {"value": 400, "unit": "px"}}),
])
def test_bookir_rejects_reconstruction_from_a_different_image_size(container, dimensions):
    payload = _book_with_reconstruction().to_dict()
    payload[container] = dimensions
    with pytest.raises(ValueError):
        BookIR.from_dict(payload)


def test_physical_width_and_height_parameters_do_not_override_source_dimensions():
    payload = _book_with_reconstruction().to_dict()
    physical_dimensions = {
        "width": {"value": 0.4, "unit": "m", "provenance": {"source": "observed_ocr"}},
        "height": {"value": 30, "unit": "cm", "provenance": {"source": "author_override"}},
    }
    payload["parameters"].update(physical_dimensions)
    restored = BookIR.from_dict(payload)
    assert restored.visual_reconstruction.observed_geometry.source_width == 800
    assert restored.visual_reconstruction.observed_geometry.source_height == 600
    for key, value in physical_dimensions.items():
        assert restored.to_dict()["parameters"][key] == value


@pytest.mark.parametrize("field,value", [("sourceAssetId", "different_asset"), ("figureId", "different_figure")])
def test_bookir_masks_must_belong_to_its_source_asset_and_figure(field, value):
    payload = _book_with_reconstruction().to_dict()
    payload["visualReconstruction"]["observedGeometry"]["masks"]["bob_mask"][field] = value
    with pytest.raises(ValueError):
        BookIR.from_dict(payload)


@pytest.mark.parametrize("field,value", [("sourceAssetId", "different_asset"), ("figureId", "different_figure")])
@pytest.mark.parametrize("evidence_id", ["ev_cv", "ev_length"])
def test_referenced_evidence_cannot_come_from_a_different_source_or_figure(field, value, evidence_id):
    payload = _book_with_reconstruction().to_dict()
    payload["evidence"][evidence_id][field] = value
    with pytest.raises(ValueError):
        BookIR.from_dict(payload)


def test_bookir_rejects_dangling_and_vlm_only_observed_evidence():
    for change in ("missing", "vlm"):
        payload = _book_with_reconstruction().to_dict()
        if change == "missing":
            del payload["evidence"]["ev_cv"]
        else:
            payload["evidence"]["ev_cv"]["method"] = "vlm"
        with pytest.raises(ValueError):
            BookIR.from_dict(payload)


def test_solver_ready_scene_is_not_automatically_visually_ready():
    book = BookIR(
        source_asset_id="asset", figure_id="figure", domain="mechanics", subtype="pendulum",
        entities=[
            BookEntity(id="pivot", type="pivot", position_source_px={"x": 200, "y": 100}),
            BookEntity(id="bob", type="bob", position_source_px={"x": 200, "y": 500}),
            BookEntity(id="string", type="string", position_source_px={"x": 200, "y": 100}, geometry={"effective_length_px": 400}),
        ],
        geometry={"width": 800, "height": 600, "pivot": {"x": 200, "y": 100},
                  "bob_center": {"x": 200, "y": 500}, "string_length_px": 400, "bob_radius_px": 20},
        visual_reconstruction=VisualReconstruction(ObservedGeometry(800, 600)),
    )
    ResolutionEngine.apply_resolution(book, {
        "parameterName": "length", "resolvedValue": 0.8,
        "canonicalUnit": "m", "resolutionSource": "user_supplied",
    })
    for policy in ("policy_earth_gravity", "policy_standard_mass", "policy_zero_damping"):
        ResolutionEngine.apply_policy(book, policy)
    assert ReadinessEvaluator.evaluate(book, mutate_status=True).ready
    evidence_before = deepcopy(book.to_dict())
    result = PhysicsCompiler().compile(book)
    assert result.status == "READY", result.issues
    assert book.status == BookIRStatus.READY_TO_COMPILE
    assert book.visual_reconstruction.visual_readiness is VisualReadiness.NOT_EVALUATED
    assert book.visual_reconstruction.registration.status is RegistrationStatus.NOT_EVALUATED
    assert book.to_dict() == evidence_before

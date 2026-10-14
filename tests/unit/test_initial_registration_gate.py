"""Offline registration safety: measured agreement is independent of solver readiness."""
from copy import deepcopy
import json

import numpy as np
import pytest

from ai.registration import InitialRegistrationGate, PredictedGeometry, RegistrationThresholds
from shared.schemas.evidence import EvidenceMethod, EvidenceRecord, MaskArtifact, SourceBBox, SourceLine, SourcePoint
from shared.schemas.ingestion import BookIR, BookIRStatus
from shared.schemas.visual_reconstruction import (
    ObservedGeometry, RegistrationReport, RegistrationStatus, VisualConstraint,
    VisualReadiness, VisualReconstruction,
)


def case(*, all_features=False):
    """Synthetic contract geometry, not fixture annotations or a physics model."""
    observed = ObservedGeometry(160, 120, landmarks={"bob": SourcePoint(40, 80)},
                                evidence_refs={"bob": ["cv"]})
    constraints = [VisualConstraint("bob_check", "landmark", ["bob"])]
    rasters = {}
    if all_features:
        observed.lines["string"] = SourceLine(SourcePoint(40, 20), SourcePoint(40, 80))
        observed.curves["path"] = [SourcePoint(10, 90), SourcePoint(40, 100), SourcePoint(90, 110)]
        observed.text_anchors["label"] = SourcePoint(100, 20)
        observed.topology = {"a": ["b"], "b": ["a"]}
        observed.masks["bob_mask"] = MaskArtifact(
            "bob_mask", source_asset_id="source", figure_id="figure", source_width=160, source_height=120,
            bbox_source_px=SourceBBox(35, 75, 10, 10), area_px=64, confidence=0.93,
        )
        rasters["bob_mask"] = np.zeros((120, 160), dtype=bool)
        rasters["bob_mask"][76:84, 36:44] = True
        for feature, kind in (("string", "line"), ("path", "curve"), ("label", "text_anchor"), ("bob_mask", "mask")):
            constraints.append(VisualConstraint(f"{feature}_check", kind, [feature]))
            observed.evidence_refs[feature] = ["cv"]
        constraints.append(VisualConstraint("topology_check", "topology", ["a", "b"]))
        observed.evidence_refs.update({"a": ["cv"], "b": ["cv"]})
    book = BookIR(
        source_asset_id="source", figure_id="figure", domain="mechanics", subtype="pendulum",
        status=BookIRStatus.NEEDS_REVIEW, geometry={"width": 160, "height": 120},
        evidence={"cv": EvidenceRecord("cv", EvidenceMethod.CLASSICAL_CV, source_asset_id="source",
                                       figure_id="figure", confidence=0.93)},
        visual_reconstruction=VisualReconstruction(observed, constraints=constraints),
    )
    prediction = PredictedGeometry(
        "source", "figure", 160, 120, "mechanics", "pendulum",
        landmarks=deepcopy(observed.landmarks), lines=deepcopy(observed.lines), curves=deepcopy(observed.curves),
        text_anchors=deepcopy(observed.text_anchors), topology=deepcopy(observed.topology), masks=deepcopy(rasters),
    )
    return book, prediction, rasters


def test_all_primitive_kinds_pass_with_measured_metrics_and_no_input_mutation():
    book, prediction, rasters = case(all_features=True)
    before = json.dumps(book.to_dict(), sort_keys=True)
    report = InitialRegistrationGate().evaluate(book, prediction, observed_masks=rasters)
    assert report.status == RegistrationStatus.PASSED, report.blockers
    assert len(report.metrics) == 8
    assert report.mean_error_px == pytest.approx(0, abs=1e-10)
    assert report.p95_error_px == pytest.approx(0, abs=1e-10)
    assert report.mask_iou == 1 and report.topology_match is True
    assert report.confidence == 0.93
    assert json.dumps(book.to_dict(), sort_keys=True) == before
    assert book.status == BookIRStatus.NEEDS_REVIEW
    assert book.visual_reconstruction.visual_readiness == VisualReadiness.NOT_EVALUATED
    assert np.array_equal(prediction.masks["bob_mask"], rasters["bob_mask"])
    json.dumps(report.to_dict(), allow_nan=False)


@pytest.mark.parametrize("offset,status", [(0, "PASSED"), (3, "PASSED"), (3.01, "NEEDS_REVIEW"),
                                           (5, "NEEDS_REVIEW"), (5.01, "FAILED"), (200, "FAILED")])
def test_landmark_bounds_are_native_pixel_residuals(offset, status):
    book, prediction, _ = case()
    prediction.landmarks["bob"].x += offset
    report = InitialRegistrationGate().evaluate(book, prediction)
    assert report.status.value == status
    assert report.landmark_errors["bob"] == pytest.approx(offset)


def test_thresholds_are_configurable_without_scaling_source_geometry():
    book, prediction, _ = case()
    prediction.landmarks["bob"].x += 4
    policy = RegistrationThresholds(landmark_preferred_px=4, landmark_warning_px=6)
    assert InitialRegistrationGate(policy).evaluate(book, prediction).status == RegistrationStatus.PASSED
    assert book.visual_reconstruction.observed_geometry.landmarks["bob"].x == 40


@pytest.mark.parametrize("changes", [{"line_mean_px": True}, {"curve_p95_px": float("nan")},
    {"minimum_mask_iou": 0}, {"minimum_evidence_confidence": 1.1}, {"max_samples": 1},
    {"sample_spacing_px": 0}, {"landmark_preferred_px": 6, "landmark_warning_px": 5}])
def test_invalid_thresholds_are_rejected(changes):
    with pytest.raises(ValueError):
        RegistrationThresholds(**changes)


@pytest.mark.parametrize("field,value", [("source_asset_id", "other"), ("figure_id", "other"),
    ("source_width", 320), ("source_height", True), ("coordinate_space", "css_px"),
    ("time_s", 1e-12), ("time_s", False), ("time_s", float("nan")), ("subtype", "projectile")])
def test_incompatible_prediction_context_cannot_pass(field, value):
    book, prediction, _ = case()
    setattr(prediction, field, value)
    report = InitialRegistrationGate().evaluate(book, prediction)
    assert report.status == RegistrationStatus.NEEDS_REVIEW and not report.metrics
    assert report.mean_error_px is None and report.confidence == 0


@pytest.mark.parametrize("change", ["missing_feature", "no_constraints", "missing_evidence", "uncovered", "extra_prediction"])
def test_partial_input_cannot_be_mistaken_for_zero_error_success(change):
    book, prediction, _ = case()
    if change == "missing_feature":
        prediction.landmarks.clear()
    elif change == "no_constraints":
        book.visual_reconstruction.constraints.clear()
    elif change == "missing_evidence":
        book.visual_reconstruction.observed_geometry.evidence_refs.clear()
    elif change == "uncovered":
        book.visual_reconstruction.observed_geometry.landmarks["pivot"] = SourcePoint(40, 20)
    else:
        prediction.lines["invented_ray"] = SourceLine(SourcePoint(1, 1), SourcePoint(100, 1))
    report = InitialRegistrationGate().evaluate(book, prediction)
    assert report.status == RegistrationStatus.NEEDS_REVIEW, report
    assert report.confidence == 0


@pytest.mark.parametrize("value", [None, 0.79, True, float("nan"), float("inf"), -1, 1.1])
def test_untrusted_evidence_confidence_cannot_authorize_visual_agreement(value):
    book, prediction, _ = case()
    book.evidence["cv"].confidence = value
    report = InitialRegistrationGate().evaluate(book, prediction)
    assert report.status == RegistrationStatus.NEEDS_REVIEW
    assert report.confidence < 0.8


def test_perfect_agreement_does_not_create_ground_truth_confidence():
    book, prediction, _ = case()
    book.evidence["cv"].confidence = 1.0
    assert InitialRegistrationGate().evaluate(book, prediction).confidence == 0.99


@pytest.mark.parametrize("change", ["vlm", "cross_source", "viewport", "unsupported", "unresolved", "missing_visuals", "non_physics"])
def test_ungrounded_or_incompatible_book_ir_abstains(change):
    book, prediction, _ = case()
    if change == "vlm":
        book.evidence["cv"].method = EvidenceMethod.VLM
    elif change == "cross_source":
        book.evidence["cv"].source_asset_id = "different"
    elif change == "viewport":
        book.evidence["cv"].coordinate_space = "css_px"
    elif change == "unsupported":
        book.subtype = "ramp"
    elif change == "unresolved":
        book.status = BookIRStatus.UNRESOLVED
    elif change == "non_physics":
        book.provenance["classification"] = "non_physics"
    else:
        book.visual_reconstruction = None
    assert InitialRegistrationGate().evaluate(book, prediction).status == RegistrationStatus.NEEDS_REVIEW


def test_stale_pass_is_recomputed_and_does_not_mutate_cached_report():
    book, prediction, _ = case()
    gate = InitialRegistrationGate()
    book.visual_reconstruction.registration = gate.evaluate(book, prediction)
    book.visual_reconstruction.visual_readiness = VisualReadiness.AUTO_VISUAL
    # Stale metric even refers to a removed constraint: it must not poison a new evaluation.
    book.visual_reconstruction.registration.metrics[0].constraint_id = "old_constraint"
    prediction.landmarks["bob"].x += 20
    report = gate.evaluate(book, prediction)
    assert report.status == RegistrationStatus.FAILED
    assert report.landmark_errors["bob"] == 20
    assert book.visual_reconstruction.registration.status == RegistrationStatus.PASSED
    assert book.visual_reconstruction.registration.metrics[0].constraint_id == "old_constraint"


def test_line_shortening_and_wrong_curve_fail_even_with_correct_bob_landmark():
    book, prediction, rasters = case(all_features=True)
    prediction.lines["string"].end = SourcePoint(40, 25)
    prediction.curves["path"] = [SourcePoint(10, 90), SourcePoint(90, 90)]
    report = InitialRegistrationGate().evaluate(book, prediction, observed_masks=rasters)
    assert report.status == RegistrationStatus.FAILED
    assert report.landmark_errors["bob"] == 0
    assert any("PATH_MISMATCH" in blocker for blocker in report.blockers)
    assert report.curve_errors["path"] > 5


def test_path_sampling_budget_abstains_instead_of_silently_downsampling():
    book, prediction, rasters = case(all_features=True)
    report = InitialRegistrationGate(RegistrationThresholds(max_samples=2)).evaluate(book, prediction, observed_masks=rasters)
    assert report.status == RegistrationStatus.NEEDS_REVIEW
    assert any("UNMEASURABLE_FEATURE" in blocker for blocker in report.blockers)


def test_mask_iou_measures_pixels_not_matching_metadata_boxes():
    book, prediction, rasters = case(all_features=True)
    prediction.masks["bob_mask"] = np.zeros((120, 160), dtype=bool)
    prediction.masks["bob_mask"][80:88, 40:48] = True
    report = InitialRegistrationGate().evaluate(book, prediction, observed_masks=rasters)
    assert report.status == RegistrationStatus.FAILED
    assert report.mask_iou == pytest.approx(16 / 112)


@pytest.mark.parametrize("change", ["missing", "scaled", "nonbinary", "empty", "grayscale"])
def test_missing_or_invalid_mask_pixels_do_not_use_bbox_fallback(change):
    book, prediction, rasters = case(all_features=True)
    if change == "missing":
        rasters.clear()
    elif change == "scaled":
        rasters["bob_mask"] = np.ones((60, 80), dtype=bool)
    elif change == "nonbinary":
        rasters["bob_mask"] = rasters["bob_mask"].astype(float) * float("nan")
    elif change == "grayscale":
        rasters["bob_mask"] = rasters["bob_mask"].astype(float) * 0.5
    else:
        rasters["bob_mask"][:] = False
        prediction.masks["bob_mask"][:] = False
    report = InitialRegistrationGate().evaluate(book, prediction, observed_masks=rasters)
    assert report.status == RegistrationStatus.NEEDS_REVIEW
    assert report.mask_iou is None


def test_float_binary_masks_are_valid_without_bitwise_array_operations():
    book, prediction, rasters = case(all_features=True)
    prediction.masks["bob_mask"] = prediction.masks["bob_mask"].astype(float)
    rasters["bob_mask"] = rasters["bob_mask"].astype(float)
    assert InitialRegistrationGate().evaluate(book, prediction, observed_masks=rasters).status == RegistrationStatus.PASSED


def test_an_empty_observed_mask_is_missing_evidence_not_a_measured_mismatch():
    book, prediction, rasters = case(all_features=True)
    rasters["bob_mask"][:] = False
    report = InitialRegistrationGate().evaluate(book, prediction, observed_masks=rasters)
    assert report.status == RegistrationStatus.NEEDS_REVIEW and report.mask_iou is None


def test_exact_topology_is_required_even_when_all_positions_match():
    book, prediction, rasters = case(all_features=True)
    prediction.topology = {"a": [], "b": []}
    report = InitialRegistrationGate().evaluate(book, prediction, observed_masks=rasters)
    assert report.status == RegistrationStatus.FAILED and report.topology_match is False
    assert report.mean_error_px == pytest.approx(0, abs=1e-10)


def test_predicted_extra_topology_cannot_hide_without_observed_graph():
    book, prediction, _ = case()
    prediction.topology = {"invented": []}
    assert InitialRegistrationGate().evaluate(book, prediction).status == RegistrationStatus.NEEDS_REVIEW


def test_empty_observation_set_has_no_measured_zero_errors():
    book, prediction, _ = case()
    book.visual_reconstruction = VisualReconstruction(ObservedGeometry(160, 120))
    prediction.landmarks.clear()
    report = InitialRegistrationGate().evaluate(book, prediction)
    assert report.status == RegistrationStatus.NEEDS_REVIEW
    assert report.mean_error_px is None and report.p95_error_px is None


def test_no_mask_or_topology_observation_leaves_metrics_unknown():
    book, prediction, _ = case()
    report = InitialRegistrationGate().evaluate(book, prediction)
    assert report.status == RegistrationStatus.PASSED
    assert report.mask_iou is None and report.topology_match is None

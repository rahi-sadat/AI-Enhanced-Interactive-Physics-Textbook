"""Fail-closed comparison of grounded observations and independent t=0 geometry.

The gate returns a fresh RegistrationReport. It neither mutates BookIR nor trusts
stored registration/readiness. PASSED is visual agreement for the supplied
observation set, not SI verification or proof that perception found every mark.
"""
from __future__ import annotations

import math
from copy import deepcopy

import numpy as np

from shared.schemas.ingestion import BookIR, BookIRStatus
from shared.schemas.semantic import DOMAIN_SUBTYPES
from shared.schemas.visual_reconstruction import (
    RegistrationMetric, RegistrationReport, RegistrationStatus,
    VisualReadiness, VisualReconstruction,
)
from .base import PredictedGeometry, RegistrationThresholds
from .metrics import (
    distance_summary, mask_iou, point_error_px, polyline_distances_px, topology_matches,
)


class InitialRegistrationGate:
    def __init__(self, thresholds=None):
        self.thresholds = thresholds if thresholds is not None else RegistrationThresholds()
        if not isinstance(self.thresholds, RegistrationThresholds):
            raise ValueError("Expected RegistrationThresholds")

    def evaluate(self, book_ir, prediction, *, observed_masks=None):
        """Evaluate all declared observations; missing/invalid evidence needs review.

        Feature correspondence is explicit by ID: no nearest-neighbor matching,
        source-image rescaling, implicit topology, or physics defaults. Optional
        constraints are also checked when supplied: their designation cannot hide
        a known visual mismatch. Missing observations cannot establish a pass.
        Pixel residuals are summarized independently from mask/topology scores.
        """
        try:
            book = self._observation_snapshot(book_ir)
            predicted = deepcopy(prediction)
            if not isinstance(predicted, PredictedGeometry):
                raise ValueError("An independent PredictedGeometry is required")
            predicted.validate_context(book)
            if observed_masks is not None and not isinstance(observed_masks, dict):
                raise ValueError("Observed masks must be a named raster map")
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
            return RegistrationReport(status=RegistrationStatus.NEEDS_REVIEW,
                                      blockers=[f"INVALID_REGISTRATION_INPUT: {error}"])

        visual = book.visual_reconstruction
        observed = visual.observed_geometry
        report = RegistrationReport(status=RegistrationStatus.NEEDS_REVIEW)
        errors_px, confidences, ious = [], [], []
        failed = False
        groups = {"landmark": "landmarks", "line": "lines", "curve": "curves",
                  "text_anchor": "text_anchors", "mask": "masks", "topology": "topology"}
        covered = {name: set() for name in groups.values()}

        for constraint in visual.constraints:
            group_name = groups[constraint.kind]
            observed_group = getattr(observed, group_name)
            predicted_group = getattr(predicted, group_name)
            covered[group_name].update(constraint.observed_refs)
            for feature_id in constraint.observed_refs:
                refs = observed.evidence_refs.get(feature_id, [])
                confidence, problem = self._evidence_confidence(book, refs)
                confidences.append(confidence)
                if problem:
                    report.blockers.append(f"UNGROUNDED_FEATURE: {feature_id}: {problem}")
                if confidence < self.thresholds.minimum_evidence_confidence:
                    report.blockers.append(f"LOW_EVIDENCE_CONFIDENCE: {feature_id}")
                if feature_id not in predicted_group:
                    report.blockers.append(f"MISSING_PREDICTION: {constraint.kind}/{feature_id}")
                    continue
                # Topology compares the whole graph once per constraint, never a
                # subgraph that could hide an extra branch/junction elsewhere.
                if constraint.kind == "topology":
                    continue
                try:
                    if constraint.kind in ("landmark", "text_anchor"):
                        error = point_error_px(observed_group[feature_id], predicted_group[feature_id])
                        passed = error <= self.thresholds.landmark_preferred_px
                        self._metric(report, constraint.id, f"{feature_id}:distance", error, "source_px", passed, 1)
                        errors_px.append(error)
                        if constraint.kind == "landmark":
                            report.landmark_errors[feature_id] = error
                        if not passed:
                            if error <= self.thresholds.landmark_warning_px:
                                report.blockers.append(f"LANDMARK_WARNING: {feature_id}")
                            else:
                                failed = True
                                report.blockers.append(f"LANDMARK_MISMATCH: {feature_id}")
                    elif constraint.kind in ("line", "curve"):
                        actual, expected = observed_group[feature_id], predicted_group[feature_id]
                        if constraint.kind == "line":
                            actual, expected = [actual.start, actual.end], [expected.start, expected.end]
                        distances = polyline_distances_px(
                            actual, expected, sample_spacing_px=self.thresholds.sample_spacing_px,
                            max_samples=self.thresholds.max_samples,
                        )
                        mean, p95 = distance_summary(distances)
                        mean_limit = getattr(self.thresholds, f"{constraint.kind}_mean_px")
                        p95_limit = getattr(self.thresholds, f"{constraint.kind}_p95_px")
                        self._metric(report, constraint.id, f"{feature_id}:mean", mean, "source_px", mean <= mean_limit, len(distances))
                        self._metric(report, constraint.id, f"{feature_id}:p95", p95, "source_px", p95 <= p95_limit, len(distances))
                        errors_px.extend(distances)
                        if constraint.kind == "curve":
                            report.curve_errors[feature_id] = p95
                        if mean > mean_limit or p95 > p95_limit:
                            failed = True
                            report.blockers.append(f"PATH_MISMATCH: {feature_id}")
                    elif constraint.kind == "mask":
                        raster = (observed_masks or {}).get(feature_id)
                        predicted_raster = predicted_group[feature_id]
                        shape = (observed.source_height, observed.source_width)
                        if not isinstance(raster, np.ndarray) or not isinstance(predicted_raster, np.ndarray):
                            raise ValueError("Both observed and predicted mask rasters are required")
                        if raster.shape != shape or predicted_raster.shape != shape:
                            raise ValueError("Mask rasters must match full native source dimensions")
                        if not np.any(raster):
                            raise ValueError("Observed mask contains no foreground evidence")
                        iou = mask_iou(raster, predicted_raster)
                        ious.append(iou)
                        passed = iou >= self.thresholds.minimum_mask_iou
                        self._metric(report, constraint.id, f"{feature_id}:iou", iou, "ratio", passed,
                                     int(np.count_nonzero(np.logical_or(raster, predicted_raster))))
                        if not passed:
                            failed = True
                            report.blockers.append(f"MASK_MISMATCH: {feature_id}")
                except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
                    report.blockers.append(f"UNMEASURABLE_FEATURE: {feature_id}: {error}")
            if constraint.kind == "topology":
                try:
                    matches = topology_matches(observed.topology, predicted.topology)
                    self._metric(report, constraint.id, "topology_match", matches, "boolean", matches, len(observed.topology))
                    report.topology_match = matches
                    if not matches:
                        failed = True
                        report.blockers.append("TOPOLOGY_MISMATCH: exact connectivity is required")
                except (ValueError, TypeError, KeyError, AttributeError) as error:
                    report.blockers.append(f"UNMEASURABLE_TOPOLOGY: {error}")

        for group in groups.values():
            missing = set(getattr(observed, group)) - covered[group]
            if missing:
                report.blockers.append(f"UNCHECKED_OBSERVATIONS: {group}/{','.join(sorted(missing))}")
            unexpected = set(getattr(predicted, group)) - set(getattr(observed, group))
            if unexpected:
                report.blockers.append(f"UNMATCHED_PREDICTIONS: {group}/{','.join(sorted(unexpected))}")
        if not report.metrics:
            report.blockers.append("NO_MEASURED_CONSTRAINTS")
        if errors_px:
            report.mean_error_px, report.p95_error_px = distance_summary(errors_px)
        if ious:
            report.mask_iou = min(ious)
        # Confidence is an evidence bottleneck, not a fabricated probability from
        # residual magnitude. Exact metric agreement does not mean ground truth.
        incomplete = any(blocker.startswith(("MISSING_", "UNCHECKED_", "UNMATCHED_", "UNMEASURABLE_", "NO_MEASURED"))
                         for blocker in report.blockers)
        report.confidence = min([0.99, *confidences]) if confidences and not incomplete else 0.0
        report.blockers = list(dict.fromkeys(report.blockers))
        report.status = (RegistrationStatus.FAILED if failed else
                         RegistrationStatus.NEEDS_REVIEW if report.blockers else RegistrationStatus.PASSED)
        report.__post_init__()
        return report

    @staticmethod
    def _metric(report, constraint_id, name, value, unit, passed, sample_count):
        report.metrics.append(RegistrationMetric(constraint_id, name, value, unit, passed, sample_count))

    @staticmethod
    def _observation_snapshot(book_ir):
        if not isinstance(book_ir, BookIR):
            raise ValueError("Expected grounded BookIR")
        book = deepcopy(book_ir)
        visual = book.visual_reconstruction
        if visual is None:
            raise ValueError("Source observations are missing")
        # Discard cached/client supplied claims BEFORE validation: stale metrics
        # must neither authorize this candidate nor poison a fresh evaluation.
        if isinstance(visual, dict):
            visual["registration"] = RegistrationReport().to_dict()
            visual["visualReadiness"] = VisualReadiness.NOT_EVALUATED.value
            visual = VisualReconstruction.from_dict(visual)
            book.visual_reconstruction = visual
        else:
            if not isinstance(visual, VisualReconstruction):
                raise ValueError("Invalid reconstruction record")
            visual.registration = RegistrationReport()
            visual.visual_readiness = VisualReadiness.NOT_EVALUATED
        if book.isPhysics is not True or book.subtype not in DOMAIN_SUBTYPES.get(book.domain, set()):
            raise ValueError("Registration requires a supported physics model")
        if book.status not in (BookIRStatus.NEEDS_REVIEW, BookIRStatus.READY_TO_COMPILE):
            raise ValueError("BookIR is unresolved, unsupported, or has an unknown status")
        if book.provenance.get("classification", "supported") != "supported":
            raise ValueError("Source classification does not support a physics model")
        book.to_dict()
        return book

    @staticmethod
    def _evidence_confidence(book, refs):
        if not refs:
            return 0.0, "Measured source evidence references are required"
        confidences = []
        for ref in refs:
            record = book.evidence[ref]
            record = record.to_dict() if hasattr(record, "to_dict") else record
            if record.get("method") not in {"classical_cv", "segmentation", "ocr", "manual", "fused"}:
                return 0.0, "Evidence must originate from CV, segmentation, OCR, or human grounding"
            if record.get("coordinateSpace", record.get("coordinate_space", "source_px")) != "source_px":
                return 0.0, "Evidence does not use native source pixels"
            value = record.get("confidence", 0.0)
            if value is None:
                value = 0.0
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
                return 0.0, "Evidence confidence must be finite and within [0, 1]"
            confidences.append(value)
        return min(confidences), None

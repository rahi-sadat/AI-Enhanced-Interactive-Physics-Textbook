"""Independent numerical checks for source-image registration metrics."""
import numpy as np
import pytest

from ai.registration.metrics import distance_summary, mask_iou, point_error_px, polyline_distances_px, topology_matches
from shared.schemas.evidence import SourcePoint


def path(*pairs):
    return [SourcePoint(*pair) for pair in pairs]


def test_point_error_is_euclidean_in_source_pixels():
    assert point_error_px(SourcePoint(10, 10), SourcePoint(13, 14)) == 5


def test_percentile_is_linear_interpolation_and_summary_excludes_no_samples():
    assert distance_summary([0, 10]) == (5, 9.5)
    with pytest.raises(ValueError):
        distance_summary([])


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), -1])
def test_summary_rejects_invalid_distances(value):
    with pytest.raises(ValueError):
        distance_summary([value])


def test_parallel_lines_have_constant_distance():
    distances = polyline_distances_px(path((0, 0), (10, 0)), path((0, 4), (10, 4)))
    assert len(distances) == 22
    assert distance_summary(distances) == pytest.approx((4, 4))


def test_reversal_and_vertex_density_do_not_create_errors():
    first = path((0, 0), (10, 0), (10, 10))
    second = path((10, 10), (10, 5), (10, 0), (5, 0), (5, 0), (0, 0))
    assert max(polyline_distances_px(first, second)) == pytest.approx(0, abs=1e-12)


def test_shortened_path_is_penalized_from_observed_to_predicted_direction():
    distances = polyline_distances_px(path((0, 0), (100, 0)), path((0, 0), (10, 0)))
    mean, p95 = distance_summary(distances)
    assert mean > 30 and p95 > 80


def test_segment_distance_does_not_depend_on_matching_vertex_indices():
    first = path((0, 0), (10, 0))
    second = path((0, 2), (3, 2), (8, 2), (10, 2))
    assert distance_summary(polyline_distances_px(first, second)) == pytest.approx((2, 2))


@pytest.mark.parametrize("points", [[], path((1, 1)), path((1, 1), (1, 1)), path((True, 1), (2, 1))])
def test_unmeasurable_paths_are_rejected(points):
    with pytest.raises(ValueError):
        polyline_distances_px(points, path((0, 0), (2, 0)))


def test_sampling_budget_is_not_silently_relaxed():
    with pytest.raises(ValueError, match="max_samples"):
        polyline_distances_px(path((0, 0), (100, 0)), path((0, 0), (100, 0)), max_samples=50)


def test_masks_with_same_bbox_can_have_different_iou():
    first = np.eye(3, dtype=bool)
    second = np.fliplr(first)
    assert mask_iou(first, second) == pytest.approx(1 / 5)
    assert mask_iou(first.astype(np.uint8) * 255, first.astype(float)) == 1


@pytest.mark.parametrize("mask", [np.zeros((2, 2)), np.ones((0, 2)), np.ones((2, 2)) * 0.5,
                                   np.ones((2, 2)) * np.nan, np.ones((2, 2, 1))])
def test_mask_absence_or_nonbinary_data_cannot_claim_perfect_match(mask):
    with pytest.raises(ValueError):
        mask_iou(mask, mask)


def test_empty_prediction_mask_is_a_measured_mismatch():
    assert mask_iou(np.eye(2), np.zeros((2, 2))) == 0


def test_topology_requires_exact_nodes_and_connections_not_graph_isomorphism():
    crossing = {"left": ["right"], "right": ["left"], "top": ["bottom"], "bottom": ["top"]}
    junction = {"left": ["center"], "right": ["center"], "top": ["center"],
                "bottom": ["center"], "center": ["left", "right", "top", "bottom"]}
    assert topology_matches(crossing, crossing)
    assert not topology_matches(crossing, junction)
    assert not topology_matches({"a": ["b"], "b": ["a"]}, {"x": ["y"], "y": ["x"]})


@pytest.mark.parametrize("graph", [{}, {"a": ["b"]}, {"a": ["b"], "b": []}, {"a": ["a"]}])
def test_missing_and_invalid_topology_is_not_a_match(graph):
    with pytest.raises(ValueError):
        topology_matches(graph, graph)

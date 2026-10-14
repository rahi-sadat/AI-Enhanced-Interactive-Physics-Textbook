"""Geometry-only registration metrics in native source pixels."""
from __future__ import annotations

import math

import numpy as np

from shared.schemas.evidence import SourcePoint


def _point(point):
    if not isinstance(point, SourcePoint):
        raise ValueError("Expected SourcePoint")
    for value in (point.x, point.y):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("Source coordinates must be finite JSON numbers")
    return point


def point_error_px(observed, predicted):
    first, second = _point(observed), _point(predicted)
    distance = math.hypot(first.x - second.x, first.y - second.y)
    if not math.isfinite(distance):
        raise ValueError("Point distance exceeds numerical range")
    return distance


def distance_summary(distances):
    """Mean and p95 with linear interpolation between ordered sample ranks."""
    if not isinstance(distances, list) or not distances:
        raise ValueError("Distance summary requires measured samples")
    for value in distances:
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("Distances must be finite nonnegative numbers")
    ordered = sorted(distances)
    rank = 0.95 * (len(ordered) - 1)
    lower = int(math.floor(rank))
    upper = int(math.ceil(rank))
    p95 = ordered[lower] + (rank - lower) * (ordered[upper] - ordered[lower])
    # Divide before summing to avoid overflow for finite but very large samples.
    mean = math.fsum(value / len(ordered) for value in ordered)
    return mean, p95


def _sample_path(points, spacing, cap):
    if not isinstance(points, list) or len(points) < 2 or len(points) > cap:
        raise ValueError("A path needs 2..max_samples source points")
    vertices = np.array([(_point(p).x, p.y) for p in points], dtype=float)
    delta = np.diff(vertices, axis=0)
    lengths = np.hypot(delta[:, 0], delta[:, 1])
    if not np.isfinite(lengths).all():
        raise ValueError("Path length exceeds numerical range")
    # Repeated vertices have no arc length and must not overweight a region.
    keep = np.concatenate(([True], lengths > 0))
    vertices = vertices[keep]
    if len(vertices) < 2:
        raise ValueError("A path must contain a nonzero segment")
    delta = np.diff(vertices, axis=0)
    lengths = np.hypot(delta[:, 0], delta[:, 1])
    cumulative = np.concatenate(([0.0], np.cumsum(lengths)))
    total = float(cumulative[-1])
    if not math.isfinite(total) or total > (cap - 1) * spacing:
        raise ValueError("Path sampling exceeds max_samples; no silent downsampling")
    count = max(2, math.ceil(total / spacing) + 1)
    locations = np.linspace(0, total, count)
    samples = np.column_stack([np.interp(locations, cumulative, vertices[:, axis]) for axis in (0, 1)])
    return vertices, samples


def _distances_to_segments(samples, vertices):
    """Continuous opposite-segment distance with bounded O(samples) workspace."""
    best = np.full(len(samples), np.inf)
    for start, end in zip(vertices[:-1], vertices[1:]):
        vector = end - start
        length = float(np.hypot(vector[0], vector[1]))
        direction = vector / length
        relative = samples - start
        along = np.clip(relative @ direction, 0, length)
        perpendicular = relative - along[:, None] * direction
        best = np.minimum(best, np.hypot(perpendicular[:, 0], perpendicular[:, 1]))
    if not np.isfinite(best).all():
        raise ValueError("Path distances exceed numerical range")
    return best.tolist()


def polyline_distances_px(observed, predicted, *, sample_spacing_px=1.0, max_samples=10000):
    """Symmetric sampled point-to-continuous-polyline distances.

    Samples include endpoints and are spaced uniformly in arc length, at most
    sample_spacing_px apart on EACH path. Distances from both directions are
    pooled (length-weighted by sampling), so a shortened prediction cannot pass
    merely by lying somewhere on the observed path. This is not a Hausdorff
    bound, a curve-order check, or an exact continuous integral.
    """
    if type(sample_spacing_px) not in (int, float) or not math.isfinite(sample_spacing_px) or sample_spacing_px <= 0:
        raise ValueError("Sample spacing must be positive and finite")
    if type(max_samples) is not int or max_samples < 2:
        raise ValueError("max_samples must be an integer >= 2")
    observed_vertices, observed_samples = _sample_path(observed, sample_spacing_px, max_samples)
    predicted_vertices, predicted_samples = _sample_path(predicted, sample_spacing_px, max_samples)
    return (_distances_to_segments(observed_samples, predicted_vertices)
            + _distances_to_segments(predicted_samples, observed_vertices))


def _binary_mask(mask):
    if not isinstance(mask, np.ndarray) or mask.ndim != 2 or not mask.size:
        raise ValueError("Expected a nonempty 2D mask array")
    if mask.dtype.kind not in "buif" or not np.isfinite(mask).all():
        raise ValueError("Mask pixels must be finite binary values")
    if not np.isin(mask, [0, 1, 255]).all():
        raise ValueError("Mask pixels must be binary (0/1 or 0/255)")
    return mask != 0


def mask_iou(observed, predicted):
    actual, expected = _binary_mask(observed), _binary_mask(predicted)
    if actual.shape != expected.shape:
        raise ValueError("Mask dimensions differ")
    union = int(np.count_nonzero(actual | expected))
    if not union:
        raise ValueError("Empty masks cannot establish measured agreement")
    return float(np.count_nonzero(actual & expected) / union)


def _graph(graph):
    if not isinstance(graph, dict) or any(not isinstance(node, str) or not node for node in graph):
        raise ValueError("Topology must be a named adjacency map")
    for node, neighbors in graph.items():
        if not isinstance(neighbors, list) or any(not isinstance(n, str) or n not in graph for n in neighbors):
            raise ValueError("Topology neighbors must reference declared nodes")
        if len(neighbors) != len(set(neighbors)) or node in neighbors:
            raise ValueError("Topology has duplicate or self connections")
    if any(node not in graph[neighbor] for node, neighbors in graph.items() for neighbor in neighbors):
        raise ValueError("Topology adjacency must be symmetric")
    return {node: frozenset(neighbors) for node, neighbors in graph.items()}


def topology_matches(observed, predicted):
    actual, expected = _graph(observed), _graph(predicted)
    if not actual:
        raise ValueError("Missing observed topology cannot establish agreement")
    return actual == expected

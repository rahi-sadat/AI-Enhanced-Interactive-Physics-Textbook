from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, List, Sequence, Tuple

import cv2
import numpy as np


@dataclass
class CandidateMetrics:
    index: int
    sam_iou_score: float
    stability_score: float
    prompt_consistency: float
    connectedness_score: float
    overlap_penalty: float
    area_fraction: float
    composite_score: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CandidateChoice:
    selected_index: int
    selected_mask: np.ndarray
    selected_logit: np.ndarray
    metrics: List[CandidateMetrics]
    quality_margin: float
    needs_refinement: bool
    reasons: List[str]


def _resize_logits_if_needed(logit: np.ndarray) -> np.ndarray:
    arr = np.asarray(logit, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError(f"Expected a 2D logit map, got {arr.shape}")
    return arr


def stability_score(logit: np.ndarray, offset: float = 1.0) -> float:
    """SAM-style stability score using two nearby mask thresholds.

    A stable candidate should change little if the logit threshold is moved up/down.
    This is a useful second opinion to the model's predicted-IoU score.
    """
    arr = _resize_logits_if_needed(logit)
    high = arr > offset
    low = arr > -offset
    union = int(np.count_nonzero(low))
    if union == 0:
        return 0.0
    intersection = int(np.count_nonzero(high))
    return float(intersection / union)


def prompt_consistency(
    mask: np.ndarray,
    point_coords: np.ndarray,
    point_labels: np.ndarray,
) -> float:
    """Fraction of positive/negative prompts satisfied by a mask."""
    mask_bool = np.asarray(mask).astype(bool)
    h, w = mask_bool.shape
    if len(point_coords) == 0:
        return 1.0

    hits = 0.0
    total = 0.0
    for (x, y), label in zip(point_coords, point_labels):
        ix = int(np.clip(round(float(x)), 0, w - 1))
        iy = int(np.clip(round(float(y)), 0, h - 1))
        inside = bool(mask_bool[iy, ix])
        expected_inside = int(label) == 1
        hits += 1.0 if inside == expected_inside else 0.0
        total += 1.0
    return float(hits / max(total, 1.0))


def connectedness_score(mask: np.ndarray) -> float:
    """How much of the mask belongs to its largest connected component."""
    binary = np.asarray(mask).astype(np.uint8)
    total = int(binary.sum())
    if total == 0:
        return 0.0
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if count <= 1:
        return 0.0
    largest = int(stats[1:, cv2.CC_STAT_AREA].max())
    return float(largest / total)


def max_overlap_iou(mask: np.ndarray, accepted_masks: Sequence[np.ndarray]) -> float:
    if not accepted_masks:
        return 0.0
    current = np.asarray(mask).astype(bool)
    best = 0.0
    for previous in accepted_masks:
        previous_bool = np.asarray(previous).astype(bool)
        intersection = int(np.logical_and(current, previous_bool).sum())
        union = int(np.logical_or(current, previous_bool).sum())
        iou = float(intersection / union) if union else 0.0
        best = max(best, iou)
    return best


def clean_mask_using_prompts(
    mask: np.ndarray,
    point_coords: np.ndarray,
    point_labels: np.ndarray,
    min_component_area: int = 20,
) -> np.ndarray:
    """Remove detached garbage while preserving components selected by positive clicks.

    If one or more positive clicks are inside connected components, those components are
    kept. Otherwise the largest component is kept. Tiny holes are filled conservatively.
    """
    binary = np.asarray(mask).astype(np.uint8)
    h, w = binary.shape
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if count <= 1:
        return binary.astype(bool)

    keep_labels = set()
    for (x, y), label in zip(point_coords, point_labels):
        if int(label) != 1:
            continue
        ix = int(np.clip(round(float(x)), 0, w - 1))
        iy = int(np.clip(round(float(y)), 0, h - 1))
        component = int(labels[iy, ix])
        if component > 0 and int(stats[component, cv2.CC_STAT_AREA]) >= min_component_area:
            keep_labels.add(component)

    if not keep_labels:
        largest_label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        keep_labels.add(largest_label)

    cleaned = np.isin(labels, list(keep_labels)).astype(np.uint8)

    # Fill enclosed holes but do not aggressively smooth boundaries.
    flood = cleaned.copy()
    flood_pad = cv2.copyMakeBorder(flood, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    ffmask = np.zeros((flood_pad.shape[0] + 2, flood_pad.shape[1] + 2), dtype=np.uint8)
    cv2.floodFill(flood_pad, ffmask, (0, 0), 1)
    outside = flood_pad[1:-1, 1:-1]
    holes = (outside == 0) & (cleaned == 0)
    cleaned[holes] = 1
    return cleaned.astype(bool)


def choose_candidate(
    masks: np.ndarray,
    sam_scores: np.ndarray,
    logits: np.ndarray,
    point_coords: np.ndarray,
    point_labels: np.ndarray,
    accepted_masks: Sequence[np.ndarray] | None = None,
    min_quality: float = 0.72,
    min_margin: float = 0.035,
) -> CandidateChoice:
    """Re-rank SAM2 candidates without assuming a physics shape.

    The composite uses model confidence + mask stability + prompt correctness +
    connectedness and penalizes near-duplicate overlap with already accepted objects.
    It intentionally does NOT prefer circles, rectangles, balls, slopes, etc.
    """
    accepted_masks = list(accepted_masks or [])
    masks = np.asarray(masks).astype(bool)
    sam_scores = np.asarray(sam_scores, dtype=np.float32).reshape(-1)
    logits = np.asarray(logits, dtype=np.float32)

    if masks.ndim != 3:
        raise ValueError(f"Expected masks shaped [N,H,W], got {masks.shape}")
    if logits.ndim != 3:
        raise ValueError(f"Expected logits shaped [N,h,w], got {logits.shape}")

    metrics: List[CandidateMetrics] = []
    image_area = float(masks.shape[1] * masks.shape[2])

    for idx in range(masks.shape[0]):
        mask = masks[idx]
        iou_score = float(np.clip(sam_scores[idx], 0.0, 1.0))
        stable = stability_score(logits[idx])
        prompt_ok = prompt_consistency(mask, point_coords, point_labels)
        connected = connectedness_score(mask)
        overlap = max_overlap_iou(mask, accepted_masks)
        area_fraction = float(mask.sum() / max(image_area, 1.0))

        # Generic sanity penalty only for pathological almost-empty / almost-full masks.
        area_penalty = 0.0
        if area_fraction < 1e-6:
            area_penalty = 0.40
        elif area_fraction > 0.985:
            area_penalty = 0.30

        composite = (
            0.43 * iou_score
            + 0.27 * stable
            + 0.22 * prompt_ok
            + 0.08 * connected
            - 0.18 * overlap
            - area_penalty
        )
        composite = float(np.clip(composite, 0.0, 1.0))

        metrics.append(
            CandidateMetrics(
                index=idx,
                sam_iou_score=iou_score,
                stability_score=stable,
                prompt_consistency=prompt_ok,
                connectedness_score=connected,
                overlap_penalty=overlap,
                area_fraction=area_fraction,
                composite_score=composite,
            )
        )

    ranked = sorted(metrics, key=lambda m: m.composite_score, reverse=True)
    best = ranked[0]
    second_score = ranked[1].composite_score if len(ranked) > 1 else 0.0
    margin = float(best.composite_score - second_score)

    reasons: List[str] = []
    if best.composite_score < min_quality:
        reasons.append("low composite mask quality")
    if len(ranked) > 1 and margin < min_margin:
        reasons.append("top candidates are too close")
    if best.prompt_consistency < 1.0:
        reasons.append("candidate violates a positive/negative prompt")
    if best.stability_score < 0.82:
        reasons.append("candidate is unstable to threshold changes")
    if best.overlap_penalty > 0.80:
        reasons.append("candidate strongly overlaps an accepted object")

    selected_mask = clean_mask_using_prompts(
        masks[best.index],
        point_coords=point_coords,
        point_labels=point_labels,
    )

    return CandidateChoice(
        selected_index=best.index,
        selected_mask=selected_mask,
        selected_logit=logits[best.index],
        metrics=metrics,
        quality_margin=margin,
        needs_refinement=bool(reasons),
        reasons=reasons,
    )

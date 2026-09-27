"""PR-06 SAM 2 Segmentation Provider Implementation.

Provides promptable segmentation for physics entities (e.g. bob, lens, prism)
using Segment Anything 2 (SAM 2 / SAM 2.1).

Rules:
  - Lazy initialization: models are NEVER loaded at global import time.
  - Safe import handling: resolves sys.path to prevent repository shadowing.
  - Returns compact mask artifacts with source-pixel centroids, boundaries, and areas.
  - If checkpoint or SAM 2 is missing, returns ExtractionStatus.UNAVAILABLE without crashing.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from shared.schemas.evidence import (
    ExtractionStatus,
    MaskArtifact,
    SegmentationResult,
    SourceBBox,
    SourcePoint,
    SourcePolygon,
)
from ai.evidence.segmentation.base import SegmentationPrompt

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


class SAM2SegmentationProvider:
    """Promptable segmentation provider using SAM 2 / SAM 2.1."""

    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        config_path: str = "configs/sam2.1/sam2.1_hiera_t.yaml",
        device: Optional[str] = None,
    ):
        self.checkpoint_path = checkpoint_path or str(
            _PROJECT_ROOT / "checkpoints" / "sam2.1_hiera_tiny.pt"
        )
        self.config_path = config_path
        self.device = device  # auto-detected if None
        self._predictor = None
        self._model = None

    @property
    def name(self) -> str:
        return "sam2.1"

    def available(self) -> bool:
        """Check whether SAM 2 package and checkpoint file exist."""
        if not Path(self.checkpoint_path).exists():
            return False
        try:
            self._ensure_sam2_on_path()
            import sam2
            return True
        except Exception:
            return False

    def _ensure_sam2_on_path(self):
        """Ensure sam2 directory is at sys.path[0] to prevent repo parent shadowing."""
        sam2_dir = _PROJECT_ROOT / "sam2"
        if sam2_dir.exists() and str(sam2_dir) not in sys.path:
            sys.path.insert(0, str(sam2_dir))

    def _get_predictor(self):
        """Lazily initialize SAM 2 model and predictor."""
        if self._predictor is None:
            self._ensure_sam2_on_path()
            try:
                import torch
                from sam2.build_sam import build_sam2
                from sam2.sam2_image_predictor import SAM2ImagePredictor
            except ImportError as e:
                raise RuntimeError(f"SAM 2 dependencies could not be imported: {e}")

            if not Path(self.checkpoint_path).exists():
                raise FileNotFoundError(f"SAM 2 checkpoint missing at: {self.checkpoint_path}")

            dev = self.device
            if dev is None:
                dev = "cuda" if torch.cuda.is_available() else "cpu"

            logger.info("[SAM2SegmentationProvider] Loading model on %s from %s...", dev, self.checkpoint_path)
            self._model = build_sam2(self.config_path, self.checkpoint_path, device=dev)
            self._predictor = SAM2ImagePredictor(self._model)

        return self._predictor

    def segment(
        self,
        image_bgr: np.ndarray,
        prompt: SegmentationPrompt,
        *,
        source_width: int,
        source_height: int,
        entity_id: Optional[str] = None,
    ) -> SegmentationResult:
        if not self.available():
            return SegmentationResult(
                status=ExtractionStatus.UNAVAILABLE,
                masks=[],
                provider=self.name,
                model="sam2.1_hiera_tiny",
                error=f"SAM 2 checkpoint missing or package not installed (checked {self.checkpoint_path}).",
            )

        start_time = time.perf_counter()

        try:
            predictor = self._get_predictor()

            # Convert BGR to RGB for SAM 2
            img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            predictor.set_image(img_rgb)

            # Build prompts
            point_coords = None
            point_labels = None
            if prompt.points:
                point_coords = np.array(prompt.points, dtype=np.float32)
                point_labels = np.array(
                    prompt.labels if prompt.labels else [1] * len(prompt.points),
                    dtype=np.int32,
                )

            box_coord = None
            if prompt.box is not None:
                box_coord = np.array(
                    [
                        prompt.box.x,
                        prompt.box.y,
                        prompt.box.x + prompt.box.width,
                        prompt.box.y + prompt.box.height,
                    ],
                    dtype=np.float32,
                )

            # Run predictor
            masks, scores, _ = predictor.predict(
                point_coords=point_coords,
                point_labels=point_labels,
                box=box_coord,
                multimask_output=True,
            )

        except Exception as e:
            logger.error("[SAM2SegmentationProvider] Segmentation failed: %s", e)
            return SegmentationResult(
                status=ExtractionStatus.ERROR,
                masks=[],
                provider=self.name,
                model="sam2.1_hiera_tiny",
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
                error=f"SAM 2 execution error: {e}",
            )

        if masks is None or len(masks) == 0:
            return SegmentationResult(
                status=ExtractionStatus.NO_EVIDENCE,
                masks=[],
                provider=self.name,
                model="sam2.1_hiera_tiny",
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        # Select highest scoring mask
        best_idx = int(np.argmax(scores))
        best_mask = masks[best_idx].astype(bool)
        best_score = float(scores[best_idx])
        area = float(np.sum(best_mask))

        if area <= 0:
            return SegmentationResult(
                status=ExtractionStatus.NO_EVIDENCE,
                masks=[],
                provider=self.name,
                model="sam2.1_hiera_tiny",
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        # Compute centroid and bbox
        mask_u8 = best_mask.astype(np.uint8) * 255
        moments = cv2.moments(mask_u8)
        if moments["m00"] > 0:
            cx = float(moments["m10"] / moments["m00"])
            cy = float(moments["m01"] / moments["m00"])
        else:
            # Fallback to mean of active indices
            ys, xs = np.where(best_mask)
            cx, cy = float(np.mean(xs)), float(np.mean(ys))

        centroid = SourcePoint(x=cx, y=cy)

        # Bounding box
        ys, xs = np.where(best_mask)
        min_x, max_x = float(np.min(xs)), float(np.max(xs))
        min_y, max_y = float(np.min(ys)), float(np.max(ys))
        bbox = SourceBBox(
            x=min_x,
            y=min_y,
            width=max(1e-3, max_x - min_x),
            height=max(1e-3, max_y - min_y),
        )

        # Approximate polygon boundary
        contours, _ = cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polygon = None
        if contours:
            largest_cnt = max(contours, key=cv2.contourArea)
            # Simplify polygon (epsilon ~ 1.5% perimeter)
            epsilon = 0.015 * cv2.arcLength(largest_cnt, True)
            approx = cv2.approxPolyDP(largest_cnt, epsilon, True)
            if len(approx) >= 3:
                poly_pts = [SourcePoint(x=float(p[0][0]), y=float(p[0][1])) for p in approx]
                polygon = SourcePolygon(points=poly_pts)

        mask_id = f"mask_{entity_id or 'obj'}_{int(time.time()*1000)%100000}"

        artifact = MaskArtifact(
            id=mask_id,
            source_width=source_width,
            source_height=source_height,
            bbox_source_px=bbox,
            centroid_source_px=centroid,
            area_px=area,
            polygon_approx=polygon,
            confidence=best_score,
            provider=self.name,
            model="sam2.1_hiera_tiny",
            prompt_provenance={
                "has_box": prompt.box is not None,
                "has_points": len(prompt.points) > 0,
            },
            verified=False,
        )

        latency = (time.perf_counter() - start_time) * 1000.0
        return SegmentationResult(
            status=ExtractionStatus.SUCCESS,
            masks=[artifact],
            provider=self.name,
            model="sam2.1_hiera_tiny",
            latency_ms=latency,
        )

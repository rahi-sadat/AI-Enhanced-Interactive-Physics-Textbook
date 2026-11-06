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
import hashlib
import json
import threading
import importlib
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

# Global singletons for model caching across pipeline calls
_CACHED_SAM2_MODEL = None
_CACHED_SAM2_PREDICTOR = None
_CACHED_SAM2_KEY = None
_CACHED_IMAGE_SIG = None
_PREDICTOR_LOCK = threading.RLock()
_INITIALIZATION_FAILURES = {}


class SAM2InitializationError(RuntimeError):
    def __init__(self, state, message):
        super().__init__(message)
        self.state = state


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
        self._diagnostics = {"state": "NOT_INITIALIZED"}

    @property
    def device_name(self) -> str:
        if self.device:
            return self.device
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    @property
    def name(self) -> str:
        return "sam2.1"

    def available(self) -> bool:
        """Ready means the configured checkpoint has actually initialized."""
        try:
            self._get_predictor()
            return True
        except SAM2InitializationError:
            return False

    def readiness(self):
        self.available()
        return dict(self._diagnostics)

    def _load_runtime(self):
        """Import the actual architecture explicitly so Hydra cannot hide its cause."""
        self._ensure_sam2_on_path()
        try:
            torch = importlib.import_module("torch")
            sam = importlib.import_module("sam2")
            importlib.import_module("sam2.modeling.backbones.hieradet").Hiera
            builder = importlib.import_module("sam2.build_sam").build_sam2
            predictor_class = importlib.import_module("sam2.sam2_image_predictor").SAM2ImagePredictor
        except ModuleNotFoundError as exc:
            raise SAM2InitializationError("MISSING_DEPENDENCY", str(exc)) from exc
        except Exception as exc:
            raise SAM2InitializationError("IMPORT_FAILURE", str(exc)) from exc
        self._diagnostics.update(sam2_file=sam.__file__, torch_version=torch.__version__,
                                 architecture="sam2.modeling.backbones.hieradet.Hiera")
        return builder, predictor_class

    def _ensure_sam2_on_path(self):
        """Ensure sam2 directory is at sys.path[0] to prevent repo parent shadowing."""
        sam2_dir = _PROJECT_ROOT / "sam2"
        if sam2_dir.exists() and str(sam2_dir) not in sys.path:
            sys.path.insert(0, str(sam2_dir))

    def _get_predictor(self):
        """Lazily initialize SAM 2 model and predictor with singleton caching."""
        global _CACHED_SAM2_MODEL, _CACHED_SAM2_PREDICTOR, _CACHED_SAM2_KEY, _CACHED_IMAGE_SIG
        # A new checkpoint/config file (including a previously missing one)
        # invalidates both success and failure caches. No per-component retries.
        def identity(path):
            p = Path(path).resolve()
            stat = p.stat() if p.is_file() else None
            return str(p), (stat.st_size, stat.st_mtime_ns) if stat else None
        config_file = _PROJECT_ROOT / "sam2" / "sam2" / self.config_path
        key = (identity(self.checkpoint_path), self.config_path, identity(config_file), self.device_name)
        with _PREDICTOR_LOCK:
            self._diagnostics.update(checkpoint=str(Path(self.checkpoint_path).resolve()),
                                     config=self.config_path, device=self.device_name)
            if key in _INITIALIZATION_FAILURES:
                self._diagnostics.update(_INITIALIZATION_FAILURES[key])
                raise SAM2InitializationError(self._diagnostics['state'], self._diagnostics['error'])
            if _CACHED_SAM2_PREDICTOR is not None and _CACHED_SAM2_KEY == key:
                self._model, self._predictor = _CACHED_SAM2_MODEL, _CACHED_SAM2_PREDICTOR
                self._diagnostics.update(state="READY", error=None)
                return self._predictor
            try:
                if not Path(self.checkpoint_path).is_file():
                    raise SAM2InitializationError("MISSING_CHECKPOINT", f"SAM2 checkpoint missing: {self.checkpoint_path}")
                build_sam2, predictor_class = self._load_runtime()
                self._model = build_sam2(self.config_path, self.checkpoint_path, device=self.device_name)
                self._predictor = predictor_class(self._model)
            except Exception as exc:
                state = getattr(exc, 'state', None)
                if state is None:
                    state = ("CONFIGURATION_FAILURE" if type(exc).__module__.startswith(('hydra', 'omegaconf'))
                             else "MODEL_INITIALIZATION_FAILURE")
                self._diagnostics.update(state=state, error=f"{type(exc).__name__}: {exc}")
                _INITIALIZATION_FAILURES[key] = dict(self._diagnostics)
                self._model = self._predictor = None
                raise SAM2InitializationError(state, self._diagnostics['error']) from exc
            _CACHED_SAM2_MODEL = self._model
            _CACHED_SAM2_PREDICTOR = self._predictor
            _CACHED_SAM2_KEY = key
            _CACHED_IMAGE_SIG = None
            self._diagnostics.update(state="READY", error=None)
            return self._predictor

    def segment(
        self, image_bgr, prompt, *, source_width, source_height, entity_id=None,
    ) -> SegmentationResult:
        # Shared predictors store mutable image embeddings. Keep set_image and
        # predict atomic across concurrently offloaded FastAPI requests.
        with _PREDICTOR_LOCK:
            return self._segment_locked(image_bgr, prompt, source_width=source_width,
                                        source_height=source_height, entity_id=entity_id)

    def _segment_locked(
        self,
        image_bgr: np.ndarray,
        prompt: SegmentationPrompt,
        *,
        source_width: int,
        source_height: int,
        entity_id: Optional[str] = None,
    ) -> SegmentationResult:
        global _CACHED_IMAGE_SIG
        if not self.available():
            return SegmentationResult(
                status=ExtractionStatus.UNAVAILABLE,
                masks=[],
                provider=self.name,
                model="sam2.1_hiera_tiny",
                error=f"{self._diagnostics['state']}: {self._diagnostics.get('error')}",
            )

        start_time = time.perf_counter()

        try:
            if image_bgr.shape[:2] != (source_height, source_width):
                raise ValueError("SAM2 input does not match the native source frame")
            predictor = self._get_predictor()

            # Reuse image embedding if identical image array is already loaded in predictor
            current_sig = (id(predictor),image_bgr.shape,hashlib.sha256(image_bgr.tobytes()).digest())
            if _CACHED_IMAGE_SIG != current_sig:
                img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                predictor.set_image(img_rgb)
                _CACHED_IMAGE_SIG = current_sig

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
            _CACHED_IMAGE_SIG = None
            self._diagnostics.update(state="INFERENCE_FAILURE", error=str(e))
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

        # Reject malformed candidates before ranking; a high score alone does
        # not establish valid pixels or the correct source frame.
        valid = [i for i, (mask, score) in enumerate(zip(masks, scores))
                 if mask.shape == (source_height, source_width)
                 and np.isfinite(mask).all() and np.isfinite(score) and 0 <= score <= 1
                 and np.any(mask)]
        if not valid:
            return SegmentationResult(status=ExtractionStatus.NO_EVIDENCE, masks=[], provider=self.name,
                model="sam2.1_hiera_tiny", error="No valid finite mask in the native source frame.",
                latency_ms=(time.perf_counter() - start_time) * 1000)
        best_idx = max(valid, key=lambda i: scores[i])
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
            rle_counts=json.dumps(_encode_mask_runs(best_mask)),
            polygon_approx=polygon,
            confidence=min(best_score, .95),
            provider=self.name,
            model="sam2.1_hiera_tiny",
            prompt_provenance={
                "has_box": prompt.box is not None,
                "has_points": len(prompt.points) > 0,
                "entity_candidate_id": entity_id,
                "source_bbox": prompt.box.to_dict() if prompt.box else None,
                "prompt_points": prompt.points,
                "prompt_labels": prompt.labels,
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


def _encode_mask_runs(mask):
    """Row-major alternating background/foreground counts, beginning with background."""
    flat = mask.ravel().astype(np.uint8)
    changes = np.flatnonzero(np.diff(flat)) + 1
    counts = np.diff(np.r_[0, changes, len(flat)]).tolist()
    return ([0] if len(flat) and flat[0] else []) + counts

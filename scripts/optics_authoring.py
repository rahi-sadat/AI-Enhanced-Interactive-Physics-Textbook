"""Interactive optics diagram authoring session with SAM 2.

Follows the same AuthoringSession pattern from
backend/kinematics/build_kinematics_scene.py, but with optics-specific:
  - Semantic buttons:  Lens, Object, Prism, Mirror, Screen
  - Annotation mode:   Click to place F / 2F points
  - Post-export:       Optional manual value entry (focal length in cm)

Workflow:
  1.  Click to segment optical elements (same SAM pipeline).
  2.  Label each element (Lens, Object, Prism, etc.).
  3.  Switch to annotation mode → click to place F / 2F points.
  4.  Optional: enter physical values via terminal prompt.
  5.  Export optics PhysicsScene v2.1.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional, Tuple

_BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BACKEND_DIR / "core"))

import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import torch

from geometry_utils import extract_geometry
from mask_quality import CandidateChoice, choose_candidate
from sprite_utils import save_rgba_sprite

try:
    from .optics_registry import OPTICS_SHORTCUTS, default_role
    from .optics_geometry import (
        extract_lens_geometry,
        extract_arrow_geometry,
        extract_prism_geometry,
        extract_mirror_geometry,
        detect_optical_axis,
    )
    from .optics_text import (
        create_manual_label,
        classify_focal_points,
        infer_pixel_scale,
        DetectedLabel,
        FocalPointSet,
    )
except ImportError:
    from optics_registry import OPTICS_SHORTCUTS, default_role
    from optics_geometry import (
        extract_lens_geometry,
        extract_arrow_geometry,
        extract_prism_geometry,
        extract_mirror_geometry,
        detect_optical_axis,
    )
    from optics_text import (
        create_manual_label,
        classify_focal_points,
        infer_pixel_scale,
        DetectedLabel,
        FocalPointSet,
    )



# ---------------------------------------------------------------------------
# Visualisation helpers (reused from kinematics)
# ---------------------------------------------------------------------------

def _rgba_overlay(mask: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    overlay = np.zeros((*mask.shape, 4), dtype=np.float32)
    overlay[..., 0] = 0.15    # R — slight blue-green tint
    overlay[..., 1] = 0.6     # G
    overlay[..., 2] = 1.0     # B
    overlay[..., 3] = np.asarray(mask).astype(np.float32) * alpha
    return overlay


def _save_mask(mask: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), np.asarray(mask).astype(np.uint8) * 255)


# ---------------------------------------------------------------------------
# Authoring session modes
# ---------------------------------------------------------------------------
MODE_SEGMENT = "segment"           # Normal SAM click-to-segment
MODE_MARK_FOCAL = "mark_focal"     # Click to place F / 2F points
MODE_MARK_AXIS = "mark_axis"       # Click to define optical axis endpoints


class OpticsAuthoringSession:
    """Single-window human-in-the-loop segmentation for optics diagrams.

    The GUI has three modes:
      segment    – Left/Right click to add positive/negative SAM prompts.
      mark_focal – Left click to place F / 2F annotation points.
      mark_axis  – Left click to define optical axis endpoints.

    Keyboard shortcuts mirror the kinematics session with optics labels.
    """

    def __init__(
        self,
        predictor,
        image_rgb: np.ndarray,
        builder,
        debug_dir: Path,
    ) -> None:
        self.predictor = predictor
        self.image_rgb = image_rgb
        self.builder = builder
        self.debug_dir = debug_dir

        # Segmentation state
        self.accepted_masks: List[np.ndarray] = []
        self.current_points: List[Tuple[float, float]] = []
        self.current_labels: List[int] = []
        self.current_choice: Optional[CandidateChoice] = None
        self.current_raw_masks: Optional[np.ndarray] = None
        self.current_raw_scores: Optional[np.ndarray] = None
        self.current_role = "unknown"
        self.current_semantic_label = "unknown"

        # Annotation state
        self.mode = MODE_SEGMENT
        self.focal_labels: List[DetectedLabel] = []
        self.focal_label_type = "F"          # "F" or "2F" — toggled by user
        self.axis_points: List[Tuple[float, float]] = []

        # Session lifecycle
        self.done = False
        self.auto_simulate = False

        # ── Matplotlib GUI ──
        self.fig, self.ax = plt.subplots(figsize=(15, 9))
        plt.subplots_adjust(bottom=0.22)
        self.ax.imshow(self.image_rgb)
        self.ax.axis("off")
        self.mask_artist = self.ax.imshow(
            np.zeros((*self.image_rgb.shape[:2], 4), dtype=np.float32)
        )
        self.accepted_artists = []
        self.annotation_artists = []
        self.prompt_artist = self.ax.scatter([], [], s=90)

        self.help_ax = self.fig.add_axes([0.03, 0.01, 0.55, 0.16])
        self.help_ax.axis("off")
        self.help_text = self.help_ax.text(0.0, 0.5, "", fontsize=9, va="center", family="monospace")

        # Row 1: Semantic labels
        btn_specs_row1 = [
            (0.60, "Lens (1)",   "#dbeafe", "#93c5fd", "convex_lens",    "static"),
            (0.68, "Object (2)", "#fce7f3", "#f9a8d4", "object_arrow",   "dynamic"),
            (0.76, "Prism (3)",  "#fef3c7", "#fde68a", "prism",          "static"),
            (0.84, "Mirror (4)", "#e0e7ff", "#c7d2fe", "concave_mirror", "static"),
            (0.92, "Screen (5)", "#e2e8f0", "#cbd5e1", "screen",         "dynamic"),
        ]
        self._label_buttons = []
        for x, text, color, hover, label, role in btn_specs_row1:
            ax_btn = self.fig.add_axes([x, 0.14, 0.07, 0.04])
            btn = Button(ax_btn, text, color=color, hovercolor=hover)
            btn.on_clicked(lambda _ev, lb=label, rl=role: self._set_semantic(lb, rl))
            self._label_buttons.append((ax_btn, btn))

        # Row 2: Roles + Actions
        btn_specs_row2 = [
            (0.60, "Dyn (D)",     "#e0f2fe", "#bae6fd"),
            (0.68, "Stat (S)",    "#fef3c7", "#fde68a"),
            (0.76, "Accept (↵)",  "#dcfce7", "#bbf7d0"),
            (0.84, "Export (Q)",  "#f1f5f9", "#e2e8f0"),
        ]
        self._action_buttons = []
        actions = [
            lambda _ev: self._set_role("dynamic"),
            lambda _ev: self._set_role("static"),
            lambda _ev: self._accept(),
            lambda _ev: self._finish(),
        ]
        for (x, text, color, hover), action in zip(btn_specs_row2, actions):
            ax_btn = self.fig.add_axes([x, 0.09, 0.07, 0.04])
            btn = Button(ax_btn, text, color=color, hovercolor=hover)
            btn.on_clicked(action)
            self._action_buttons.append((ax_btn, btn))

        # Row 3: Annotation mode + Simulate
        ax_focal = self.fig.add_axes([0.60, 0.04, 0.10, 0.04])
        self.btn_focal = Button(ax_focal, "Mark F/2F", color="#fef08a", hovercolor="#fde047")
        self.btn_focal.on_clicked(lambda _ev: self._toggle_focal_mode())

        ax_sim = self.fig.add_axes([0.72, 0.04, 0.27, 0.04])
        self.btn_sim = Button(ax_sim, "▶ SIMULATE (Finish & Run Frontend)", color="#4ade80", hovercolor="#22c55e")
        self.btn_sim.on_clicked(lambda _ev: self._finish_and_simulate())

        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self._update_status()

    # ------------------------------------------------------------------
    # Semantic / role setters
    # ------------------------------------------------------------------

    def _set_role(self, role: str) -> None:
        self.current_role = role
        self._update_status()

    def _set_semantic(self, label: str, default_role_val: str | None = None) -> None:
        self.current_semantic_label = label
        if default_role_val and self.current_role == "unknown":
            self.current_role = default_role_val
        self._update_status()

    # ------------------------------------------------------------------
    # Mode switching
    # ------------------------------------------------------------------

    def _toggle_focal_mode(self) -> None:
        if self.mode == MODE_SEGMENT:
            self.mode = MODE_MARK_FOCAL
            self.focal_label_type = "F"
        elif self.mode == MODE_MARK_FOCAL and self.focal_label_type == "F":
            self.focal_label_type = "2F"
        elif self.mode == MODE_MARK_FOCAL and self.focal_label_type == "2F":
            self.mode = MODE_SEGMENT
        self._update_status()

    # ------------------------------------------------------------------
    # Status display
    # ------------------------------------------------------------------

    def _update_status(self) -> None:
        if self.mode == MODE_MARK_FOCAL:
            mode_str = f"ANNOTATION: Click to place {self.focal_label_type} points"
        elif self.mode == MODE_MARK_AXIS:
            mode_str = "ANNOTATION: Click 2 points to define optical axis"
        else:
            mode_str = "SEGMENT"

        if self.current_choice is None:
            quality = "no active mask"
        else:
            m = next(
                m for m in self.current_choice.metrics
                if m.index == self.current_choice.selected_index
            )
            quality = f"quality={m.composite_score:.3f}"
            if self.current_choice.needs_refinement:
                quality += " | refine: " + ", ".join(self.current_choice.reasons)

        focal_count = len(self.focal_labels)
        self.ax.set_title(
            f"Optics Authoring | mode={mode_str} | "
            f"role={self.current_role.upper()} | label={self.current_semantic_label.upper()} | "
            f"F/2F points={focal_count} | {quality}",
            fontsize=11,
        )

        self.help_text.set_text(
            "SEGMENT MODE:\n"
            "  LEFT click = positive (+)   RIGHT click = negative (-)\n"
            "  1=Lens 2=Object 3=Prism 4=Mirror 5=Screen | D=Dyn S=Stat\n"
            "  ENTER = accept   R = reset   Q = export   F = toggle F/2F mode\n"
            "ANNOTATION MODE:  Click to place F or 2F, press F to toggle / exit"
        )
        self.fig.canvas.draw_idle()

    # ------------------------------------------------------------------
    # Prompt and prediction
    # ------------------------------------------------------------------

    def _update_prompts(self) -> None:
        if not self.current_points:
            self.prompt_artist.set_offsets(np.empty((0, 2)))
            return
        pts = np.asarray(self.current_points, dtype=np.float32)
        colors = ["lime" if label == 1 else "red" for label in self.current_labels]
        self.prompt_artist.remove()
        self.prompt_artist = self.ax.scatter(
            pts[:, 0], pts[:, 1], s=100, c=colors, marker="x", linewidths=2
        )

    def _predict(self) -> None:
        if not self.current_points:
            self.current_choice = None
            self.mask_artist.set_data(
                np.zeros((*self.image_rgb.shape[:2], 4), dtype=np.float32)
            )
            self._update_prompts()
            self._update_status()
            return

        points = np.asarray(self.current_points, dtype=np.float32)
        labels = np.asarray(self.current_labels, dtype=np.int32)

        device_type = self.predictor.model.device.type
        ctx = (
            torch.autocast(device_type=device_type, dtype=torch.bfloat16)
            if device_type != "cpu"
            else torch.inference_mode()
        )
        with torch.inference_mode(), ctx:
            masks, scores, logits = self.predictor.predict(
                point_coords=points,
                point_labels=labels,
                multimask_output=True,
            )
        masks = np.asarray(masks).astype(bool)
        scores = np.asarray(scores, dtype=np.float32).reshape(-1)
        logits = np.asarray(logits, dtype=np.float32)

        choice = choose_candidate(
            masks=masks,
            sam_scores=scores,
            logits=logits,
            point_coords=points,
            point_labels=labels,
            accepted_masks=self.accepted_masks,
        )
        self.current_choice = choice
        self.current_raw_masks = masks
        self.current_raw_scores = scores
        self.mask_artist.set_data(_rgba_overlay(choice.selected_mask))
        self._update_prompts()
        self._update_status()

    # ------------------------------------------------------------------
    # Click handler
    # ------------------------------------------------------------------

    def on_click(self, event) -> None:
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        # ── Annotation mode: place F / 2F ──
        if self.mode == MODE_MARK_FOCAL and event.button == 1:
            x, y = float(event.xdata), float(event.ydata)
            label = create_manual_label(self.focal_label_type, x, y)
            self.focal_labels.append(label)

            color = "#fbbf24" if self.focal_label_type == "F" else "#f97316"
            self.ax.plot(x, y, "D", color=color, markersize=10, markeredgecolor="black")
            self.ax.text(
                x + 8, y - 8, self.focal_label_type,
                fontsize=10, fontweight="bold", color=color,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8),
            )
            self.fig.canvas.draw_idle()
            print(f"Placed {self.focal_label_type} at ({x:.1f}, {y:.1f})")
            self._update_status()
            return

        # ── Segment mode ──
        if self.mode == MODE_SEGMENT:
            if event.button == 1:
                label = 1
            elif event.button == 3:
                if not self.current_points:
                    return
                label = 0
            else:
                return
            self.current_points.append((float(event.xdata), float(event.ydata)))
            self.current_labels.append(label)
            self._predict()

    # ------------------------------------------------------------------
    # Accept / Reset / Finish
    # ------------------------------------------------------------------

    def _reset_current(self) -> None:
        self.current_points = []
        self.current_labels = []
        self.current_choice = None
        self.current_raw_masks = None
        self.current_raw_scores = None
        self.mask_artist.set_data(
            np.zeros((*self.image_rgb.shape[:2], 4), dtype=np.float32)
        )
        self._update_prompts()
        self._update_status()

    def _accept(self) -> None:
        if self.current_choice is None or not self.current_points:
            print("Nothing to accept yet.")
            return

        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        object_number = len(self.accepted_masks) + 1
        element_id = f"element_{object_number:03d}"
        mask = self.current_choice.selected_mask
        geometry = extract_geometry(mask)

        # Debug artifacts
        mask_file = self.debug_dir / f"{element_id}_mask.png"
        quality_file = self.debug_dir / f"{element_id}_quality.json"
        sprite_file = self.debug_dir / f"{element_id}_sprite.png"

        _save_mask(mask, mask_file)

        sprite_info = None
        try:
            sprite_res = save_rgba_sprite(self.image_rgb, mask, sprite_file)
            sprite_info = {
                "sprite_path": os.path.relpath(sprite_file, PROJECT_ROOT).replace("\\", "/"),
                "width": sprite_res["width"],
                "height": sprite_res["height"],
                "sprite_url": f"/sprites/{element_id}.png",
            }
        except Exception as e:
            print(f"Warning: could not create sprite for {element_id}: {e}")

        # Quality metrics
        sel_m = next(
            m for m in self.current_choice.metrics
            if m.index == self.current_choice.selected_index
        )
        quality = {
            "selected_internal_candidate": self.current_choice.selected_index,
            "composite_score": sel_m.composite_score,
            "sam_predicted_iou": sel_m.sam_iou_score,
            "stability_score": sel_m.stability_score,
            "prompt_consistency": sel_m.prompt_consistency,
            "connectedness_score": sel_m.connectedness_score,
            "quality_margin": self.current_choice.quality_margin,
            "needed_refinement_at_accept": self.current_choice.needs_refinement,
            "reasons": self.current_choice.reasons,
        }
        quality_file.parent.mkdir(parents=True, exist_ok=True)
        quality_file.write_text(json.dumps(quality, indent=2), encoding="utf-8")

        mask_rel = os.path.relpath(mask_file, PROJECT_ROOT).replace("\\", "/")
        h, w = self.image_rgb.shape[:2]

        # ── Domain-specific element addition ──
        sem = self.current_semantic_label
        if sem in ("convex_lens", "concave_lens"):
            optics_geo = extract_lens_geometry(mask, (h, w)).to_dict()
            self.builder.add_lens(
                geometry, optics_geo, self.current_role,
                self.current_points, self.current_labels,
                quality, mask_rel, sem, sprite_info,
            )
        elif sem == "object_arrow":
            # Try to use the lens center y as the axis reference
            axis_y = None
            for el in self.builder.elements:
                oc = el.get("optics", {}).get("optical_center")
                if oc:
                    axis_y = oc.get("y")
                    break
            arrow_geo = extract_arrow_geometry(mask, (h, w), axis_y).to_dict()
            self.builder.add_optical_object(
                geometry, arrow_geo, self.current_role,
                self.current_points, self.current_labels,
                quality, mask_rel, sem, sprite_info,
            )
        elif sem == "prism":
            prism_geo = extract_prism_geometry(mask).to_dict()
            self.builder.add_prism(
                geometry, prism_geo, self.current_role,
                self.current_points, self.current_labels,
                quality, mask_rel, None, sprite_info,
            )
        elif sem in ("concave_mirror", "convex_mirror", "plane_mirror"):
            mirror_geo = extract_mirror_geometry(mask).to_dict()
            self.builder.add_mirror(
                geometry, mirror_geo, self.current_role,
                self.current_points, self.current_labels,
                quality, mask_rel, sem, sprite_info,
            )
        else:
            self.builder.add_generic_element(
                geometry, self.current_role,
                self.current_points, self.current_labels,
                quality, mask_rel, sem if sem != "unknown" else None, sprite_info,
            )

        # Visual feedback: draw accepted contour
        contour = np.asarray(
            [[p["x"], p["y"]] for p in geometry.polygon_px], dtype=np.float32
        )
        if len(contour) >= 2:
            closed = np.vstack([contour, contour[0]])
            artist, = self.ax.plot(closed[:, 0], closed[:, 1], linewidth=1.5, color="#60a5fa")
            self.accepted_artists.append(artist)

        self.accepted_masks.append(mask.copy())
        print(
            f"Accepted {element_id}: role={self.current_role}, "
            f"label={sem}, quality={sel_m.composite_score:.3f}"
        )
        self.current_semantic_label = "unknown"
        self._reset_current()

    def _finish(self) -> None:
        self.done = True
        self.auto_simulate = False
        plt.close(self.fig)

    def _finish_and_simulate(self) -> None:
        if self.current_choice is not None and self.current_points:
            self._accept()
        self.done = True
        self.auto_simulate = True
        plt.close(self.fig)

    # ------------------------------------------------------------------
    # Keyboard handler
    # ------------------------------------------------------------------

    def on_key(self, event) -> None:
        key = (event.key or "").lower()

        # Toggle focal annotation mode
        if key == "f":
            self._toggle_focal_mode()
            return

        # Optics semantic shortcuts
        if key in OPTICS_SHORTCUTS:
            label, role = OPTICS_SHORTCUTS[key]
            self._set_semantic(label, role)
            return

        if key == "d":
            self._set_role("dynamic")
        elif key == "s":
            self._set_role("static")
        elif key == "u":
            self._set_role("unknown")
        elif key in {"enter", "return"}:
            self._accept()
            return
        elif key in {"r", "x"}:
            self._reset_current()
            return
        elif key == "q":
            self._finish()
            return
        self._update_status()

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Launch the interactive Matplotlib window."""
        plt.show()

    def get_focal_data(self, optical_center_x: float) -> FocalPointSet:
        """Classify the placed focal labels and return structured data."""
        return classify_focal_points(self.focal_labels, optical_center_x)

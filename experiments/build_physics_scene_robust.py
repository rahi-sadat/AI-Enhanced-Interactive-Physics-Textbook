from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict
from pathlib import Path
from typing import List, Tuple

import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import shutil
import subprocess
import torch
import webbrowser

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

from geometry_utils import extract_geometry
from mask_quality import CandidateChoice, choose_candidate
from scene_builder import SceneBuilder, export_matterjs_compat
from sprite_utils import save_rgba_sprite


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = PROJECT_ROOT / "images" / "multi_balls_test.jpg"
DEFAULT_FULL_JSON = PROJECT_ROOT / "physics_scene_full.json"
DEFAULT_MATTER_JSON = PROJECT_ROOT / "physics_scene.json"
DEFAULT_DEBUG_DIR = PROJECT_ROOT / "outputs" / "scene_pipeline_debug"

CHECKPOINT_CONFIGS = {
    "sam2.1_hiera_tiny.pt": "configs/sam2.1/sam2.1_hiera_t.yaml",
    "sam2.1_hiera_small.pt": "configs/sam2.1/sam2.1_hiera_s.yaml",
    "sam2.1_hiera_base_plus.pt": "configs/sam2.1/sam2.1_hiera_b+.yaml",
    "sam2.1_hiera_large.pt": "configs/sam2.1/sam2.1_hiera_l.yaml",
    "sam2_hiera_tiny.pt": "configs/sam2/sam2_hiera_t.yaml",
    "sam2_hiera_small.pt": "configs/sam2/sam2_hiera_s.yaml",
    "sam2_hiera_base_plus.pt": "configs/sam2/sam2_hiera_b+.yaml",
    "sam2_hiera_large.pt": "configs/sam2/sam2_hiera_l.yaml",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Robust SAM2 authoring: click -> quality re-ranking -> visual confirmation / "
            "positive-negative refinement -> geometry -> generic scene JSON + Matter.js adapter"
        )
    )
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--full-json", type=Path, default=DEFAULT_FULL_JSON)
    parser.add_argument("--matter-json", type=Path, default=DEFAULT_MATTER_JSON)
    parser.add_argument("--debug-dir", type=Path, default=DEFAULT_DEBUG_DIR)
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument("--model-cfg", type=str, default=None)
    parser.add_argument("--canvas-width", type=int, default=800)
    parser.add_argument("--canvas-height", type=int, default=600)
    return parser.parse_args()


def discover_from_working_verifier() -> Tuple[Path, str] | None:
    verifier = PROJECT_ROOT / "experiments" / "verify_multiple_objects.py"
    if not verifier.exists():
        return None
    text = verifier.read_text(encoding="utf-8", errors="ignore")
    cfg_matches = re.findall(r"[\"'](configs[\\/][^\"']+?\.yaml)[\"']", text)
    ckpt_matches = re.findall(r"[\"']([^\"']+?\.(?:pt|pth))[\"']", text, flags=re.IGNORECASE)
    for ckpt_text in ckpt_matches:
        normalized = ckpt_text.replace("\\", os.sep).replace("/", os.sep)
        candidate = Path(normalized)
        if not candidate.is_absolute():
            candidate = (PROJECT_ROOT / candidate).resolve()
        if candidate.exists():
            if cfg_matches:
                return candidate, cfg_matches[0].replace("\\", "/")
            if candidate.name in CHECKPOINT_CONFIGS:
                return candidate, CHECKPOINT_CONFIGS[candidate.name]
    return None


def discover_checkpoint(checkpoint_arg: Path | None) -> Tuple[Path, str]:
    if checkpoint_arg is not None:
        checkpoint = checkpoint_arg.resolve()
        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)
        cfg = CHECKPOINT_CONFIGS.get(checkpoint.name)
        if cfg:
            return checkpoint, cfg
        working = discover_from_working_verifier()
        if working and working[0] == checkpoint:
            return working
        raise RuntimeError("Pass --model-cfg using the config from verify_multiple_objects.py")

    working = discover_from_working_verifier()
    if working:
        return working

    checkpoint_dir = PROJECT_ROOT / "checkpoints"
    priority = [
        "sam2.1_hiera_small.pt",
        "sam2.1_hiera_tiny.pt",
        "sam2_hiera_small.pt",
        "sam2_hiera_tiny.pt",
        "sam2.1_hiera_base_plus.pt",
        "sam2_hiera_base_plus.pt",
        "sam2.1_hiera_large.pt",
        "sam2_hiera_large.pt",
    ]
    for name in priority:
        path = checkpoint_dir / name
        if path.exists():
            return path, CHECKPOINT_CONFIGS[name]
    raise FileNotFoundError("Could not discover the checkpoint already used by your verifier.")


def load_predictor(checkpoint: Path, model_cfg: str, device: str) -> SAM2ImagePredictor:
    model = build_sam2(model_cfg, str(checkpoint), device=device)
    model.eval()
    return SAM2ImagePredictor(model)


def rgba_mask(mask: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    overlay = np.zeros((*mask.shape, 4), dtype=np.float32)
    overlay[..., 1] = 1.0
    overlay[..., 2] = 0.15
    overlay[..., 3] = np.asarray(mask).astype(np.float32) * alpha
    return overlay


def save_mask(mask: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), np.asarray(mask).astype(np.uint8) * 255)


def save_debug_candidates(
    image_rgb: np.ndarray,
    masks: np.ndarray,
    scores: np.ndarray,
    choice: CandidateChoice,
    path: Path,
) -> None:
    n = len(masks)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]
    metrics_by_index = {m.index: m for m in choice.metrics}
    for idx, ax in enumerate(axes):
        ax.imshow(image_rgb)
        ax.imshow(rgba_mask(masks[idx]))
        m = metrics_by_index[idx]
        selected = "SELECTED" if idx == choice.selected_index else ""
        ax.set_title(
            f"candidate {idx} {selected}\n"
            f"SAM={scores[idx]:.3f} composite={m.composite_score:.3f}\n"
            f"stable={m.stability_score:.3f} prompt={m.prompt_consistency:.2f}"
        )
        ax.axis("off")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


class AuthoringSession:
    """Single-window human-in-the-loop segmentation.

    No Candidate 0/1/2 decision is exposed to the user. The system proposes the best
    candidate, but the final mask is confirmed visually. If wrong, the user adds a
    positive click on missing content or a negative click on unwanted content.
    """

    def __init__(
        self,
        predictor: SAM2ImagePredictor,
        image_rgb: np.ndarray,
        builder: SceneBuilder,
        debug_dir: Path,
    ) -> None:
        self.predictor = predictor
        self.image_rgb = image_rgb
        self.builder = builder
        self.debug_dir = debug_dir

        self.accepted_masks: List[np.ndarray] = []
        self.current_points: List[Tuple[float, float]] = []
        self.current_labels: List[int] = []
        self.current_choice: CandidateChoice | None = None
        self.current_raw_masks: np.ndarray | None = None
        self.current_raw_scores: np.ndarray | None = None
        self.current_role = "unknown"
        self.current_semantic_label = "unknown"
        self.done = False
        self.auto_simulate = False

        self.fig, self.ax = plt.subplots(figsize=(15, 9))
        plt.subplots_adjust(bottom=0.20)
        self.ax.imshow(self.image_rgb)
        self.ax.axis("off")
        self.mask_artist = self.ax.imshow(
            np.zeros((*self.image_rgb.shape[:2], 4), dtype=np.float32)
        )
        self.accepted_artists = []
        self.prompt_artist = self.ax.scatter([], [], s=90)

        self.help_ax = self.fig.add_axes([0.05, 0.01, 0.55, 0.14])
        self.help_ax.axis("off")
        self.help_text = self.help_ax.text(0.0, 0.5, "", fontsize=9.5, va="center")

        # Row 1: Quick Semantic Labels
        self.btn_ball_ax = self.fig.add_axes([0.62, 0.12, 0.07, 0.045])
        self.btn_ball = Button(self.btn_ball_ax, "Ball (1)", color="#e0f2fe", hovercolor="#bae6fd")
        self.btn_ball.on_clicked(lambda event: self._set_semantic("ball", "dynamic"))

        self.btn_track_ax = self.fig.add_axes([0.70, 0.12, 0.07, 0.045])
        self.btn_track = Button(self.btn_track_ax, "Track (2)", color="#fef3c7", hovercolor="#fde68a")
        self.btn_track.on_clicked(lambda event: self._set_semantic("track", "static"))

        self.btn_spring_ax = self.fig.add_axes([0.78, 0.12, 0.08, 0.045])
        self.btn_spring = Button(self.btn_spring_ax, "Spring (3)", color="#fef08a", hovercolor="#fde047")
        self.btn_spring.on_clicked(lambda event: self._set_semantic("spring", "static"))

        self.btn_wall_ax = self.fig.add_axes([0.87, 0.12, 0.07, 0.045])
        self.btn_wall = Button(self.btn_wall_ax, "Wall (4)", color="#e2e8f0", hovercolor="#cbd5e1")
        self.btn_wall.on_clicked(lambda event: self._set_semantic("wall", "static"))

        # Row 2: Roles and Actions
        self.btn_dyn_ax = self.fig.add_axes([0.62, 0.065, 0.07, 0.045])
        self.btn_dyn = Button(self.btn_dyn_ax, "Dyn (D)", color="#e0f2fe", hovercolor="#bae6fd")
        self.btn_dyn.on_clicked(lambda event: self._set_role("dynamic"))

        self.btn_stat_ax = self.fig.add_axes([0.70, 0.065, 0.07, 0.045])
        self.btn_stat = Button(self.btn_stat_ax, "Stat (S)", color="#fef3c7", hovercolor="#fde68a")
        self.btn_stat.on_clicked(lambda event: self._set_role("static"))

        self.btn_accept_ax = self.fig.add_axes([0.78, 0.065, 0.08, 0.045])
        self.btn_accept = Button(self.btn_accept_ax, "Accept (↵)", color="#dcfce7", hovercolor="#bbf7d0")
        self.btn_accept.on_clicked(lambda event: self._accept())

        self.btn_quit_ax = self.fig.add_axes([0.87, 0.065, 0.07, 0.045])
        self.btn_quit = Button(self.btn_quit_ax, "Export (Q)", color="#f1f5f9", hovercolor="#e2e8f0")
        self.btn_quit.on_clicked(lambda event: self._finish())

        # Row 3: Big Simulate Button
        self.btn_sim_ax = self.fig.add_axes([0.62, 0.015, 0.32, 0.045])
        self.btn_sim = Button(self.btn_sim_ax, "▶ SIMULATE (Finish & Run Frontend)", color="#4ade80", hovercolor="#22c55e")
        self.btn_sim.on_clicked(lambda event: self._finish_and_simulate())

        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self._update_status()

    def _set_role(self, role: str) -> None:
        self.current_role = role
        self._update_status()

    def _set_semantic(self, label: str, default_role: str | None = None) -> None:
        self.current_semantic_label = label
        if default_role and self.current_role == "unknown":
            self.current_role = default_role
        self._update_status()

    def _finish(self) -> None:
        self.done = True
        self.auto_simulate = False
        plt.close(self.fig)

    def _finish_and_simulate(self) -> None:
        if self.current_choice is not None and self.current_points:
            # If an unaccepted object is on screen, accept it first
            self._accept()
        self.done = True
        self.auto_simulate = True
        plt.close(self.fig)

    def _update_status(self) -> None:
        if self.current_choice is None:
            quality = "no active mask"
        else:
            selected_metrics = next(
                m for m in self.current_choice.metrics if m.index == self.current_choice.selected_index
            )
            quality = f"quality={selected_metrics.composite_score:.3f}"
            if self.current_choice.needs_refinement:
                quality += " | refine recommended: " + ", ".join(self.current_choice.reasons)
            else:
                quality += " | looks stable"

        self.ax.set_title(
            f"SAM2 Physics Scene Authoring | role={self.current_role.upper()} | label={self.current_semantic_label.upper()} | {quality}",
            fontsize=12,
        )
        self.help_text.set_text(
            "LEFT click = positive (+)   RIGHT click = negative (-)\n"
            "Roles: D = dynamic   S = static   U = unknown\n"
            "Labels: 1 = ball   2 = track   3 = spring   4 = wall\n"
            "ENTER = accept   R = reset current   Q = finish"
        )
        self.fig.canvas.draw_idle()

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
            self.mask_artist.set_data(np.zeros((*self.image_rgb.shape[:2], 4), dtype=np.float32))
            self._update_prompts()
            self._update_status()
            return

        points = np.asarray(self.current_points, dtype=np.float32)
        labels = np.asarray(self.current_labels, dtype=np.int32)

        device_type = self.predictor.model.device.type
        with torch.inference_mode(), torch.autocast(device_type=device_type, dtype=torch.bfloat16) if device_type != "cpu" else torch.inference_mode():
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
        self.mask_artist.set_data(rgba_mask(choice.selected_mask))
        self._update_prompts()
        self._update_status()

    def on_click(self, event) -> None:
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
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

    def _reset_current(self) -> None:
        self.current_points = []
        self.current_labels = []
        self.current_choice = None
        self.current_raw_masks = None
        self.current_raw_scores = None
        self.mask_artist.set_data(np.zeros((*self.image_rgb.shape[:2], 4), dtype=np.float32))
        self._update_prompts()
        self._update_status()

    def _accept(self) -> None:
        if self.current_choice is None or not self.current_points:
            print("Nothing to accept yet.")
            return

        object_number = len(self.accepted_masks) + 1
        element_id = f"element_{object_number:03d}"
        mask = self.current_choice.selected_mask
        geometry = extract_geometry(mask)

        mask_file = self.debug_dir / f"{element_id}_mask.png"
        candidate_file = self.debug_dir / f"{element_id}_candidates.png"
        quality_file = self.debug_dir / f"{element_id}_quality.json"
        sprite_file = self.debug_dir / f"{element_id}_sprite.png"

        save_mask(mask, mask_file)
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

        if self.current_raw_masks is not None and self.current_raw_scores is not None:
            save_debug_candidates(
                self.image_rgb,
                self.current_raw_masks,
                self.current_raw_scores,
                self.current_choice,
                candidate_file,
            )

        selected_metrics = next(
            m for m in self.current_choice.metrics if m.index == self.current_choice.selected_index
        )
        quality = {
            "selected_internal_candidate": self.current_choice.selected_index,
            "composite_score": selected_metrics.composite_score,
            "sam_predicted_iou": selected_metrics.sam_iou_score,
            "stability_score": selected_metrics.stability_score,
            "prompt_consistency": selected_metrics.prompt_consistency,
            "connectedness_score": selected_metrics.connectedness_score,
            "quality_margin": self.current_choice.quality_margin,
            "needed_refinement_at_accept": self.current_choice.needs_refinement,
            "reasons": self.current_choice.reasons,
            "all_internal_candidates": [m.to_dict() for m in self.current_choice.metrics],
        }
        quality_file.parent.mkdir(parents=True, exist_ok=True)
        quality_file.write_text(json.dumps(quality, indent=2), encoding="utf-8")

        self.builder.add_element(
            geometry=geometry,
            author_role=self.current_role,
            prompt_points=self.current_points,
            prompt_labels=self.current_labels,
            quality=quality,
            mask_path=os.path.relpath(mask_file, PROJECT_ROOT).replace("\\", "/"),
            semantic_label=self.current_semantic_label if self.current_semantic_label != "unknown" else None,
            sprite_info=sprite_info,
        )

        # Draw a permanent outline for already accepted elements.
        contour = np.asarray(
            [[p["x"], p["y"]] for p in geometry.polygon_px], dtype=np.float32
        )
        if len(contour) >= 2:
            closed = np.vstack([contour, contour[0]])
            artist, = self.ax.plot(closed[:, 0], closed[:, 1], linewidth=1.5)
            self.accepted_artists.append(artist)

        self.accepted_masks.append(mask.copy())
        print(
            f"Accepted element {object_number}: role={self.current_role}, "
            f"label={self.current_semantic_label}, "
            f"quality={selected_metrics.composite_score:.3f}, "
            f"refinement_clicks={max(0, len(self.current_points)-1)}"
        )
        self.current_semantic_label = "unknown"
        self._reset_current()

    def on_key(self, event) -> None:
        key = (event.key or "").lower()
        if key == "1":
            self._set_semantic("ball", "dynamic")
            return
        elif key == "2":
            self._set_semantic("track", "static")
            return
        elif key == "3":
            self._set_semantic("spring", "static")
            return
        elif key == "4":
            self._set_semantic("wall", "static")
            return
        elif key == "d":
            self.current_role = "dynamic"
        elif key == "s":
            self.current_role = "static"
        elif key == "u":
            self.current_role = "unknown"
        elif key in {"enter", "return"}:
            self._accept()
            return
        elif key == "r":
            self._reset_current()
            return
        elif key == "x":
            self._reset_current()
            return
        elif key == "q":
            self.done = True
            plt.close(self.fig)
            return
        self._update_status()

    def run(self) -> None:
        plt.show()


def main() -> None:
    args = parse_args()
    image_path = args.image.resolve()
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    checkpoint, inferred_cfg = discover_checkpoint(args.checkpoint)
    model_cfg = args.model_cfg or inferred_cfg
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("=" * 68)
    print("ROBUST SAM2 -> GENERIC PHYSICS SCENE")
    print("=" * 68)
    print(f"Device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Image: {image_path}")
    print(f"Checkpoint: {checkpoint}")
    print(f"Config: {model_cfg}")

    image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise RuntimeError(f"OpenCV could not read {image_path}")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w = image_rgb.shape[:2]

    predictor = load_predictor(checkpoint, model_cfg, device)
    print("Encoding image once...")
    with torch.inference_mode(), torch.autocast(device_type=device, dtype=torch.bfloat16) if device != "cpu" else torch.inference_mode():
        predictor.set_image(image_rgb)
    print("Ready.")

    debug_dir = args.debug_dir.resolve()
    debug_dir.mkdir(parents=True, exist_ok=True)
    builder = SceneBuilder(
        image_path=image_path,
        image_width=w,
        image_height=h,
        target_width=args.canvas_width,
        target_height=args.canvas_height,
    )

    session = AuthoringSession(predictor, image_rgb, builder, debug_dir)
    session.run()

    full_path = args.full_json.resolve()
    matter_path = args.matter_json.resolve()
    full_scene = builder.write(full_path)
    compat_scene = export_matterjs_compat(full_scene, matter_path, background_url="/physics_scene.png")

    # Seamless deployment to frontend public folder
    frontend_dir = PROJECT_ROOT / "simulation_frontend" / "physics simulation"
    frontend_public = frontend_dir / "public"
    if frontend_public.exists():
        shutil.copy2(matter_path, frontend_public / "physics_scene.json")
        shutil.copy2(matter_path, frontend_dir / "physics_scene.json")
        shutil.copy2(image_path, frontend_public / "physics_scene.png")
        shutil.copy2(image_path, frontend_dir / "physics_scene.png")

        frontend_sprites = frontend_public / "sprites"
        frontend_sprites.mkdir(parents=True, exist_ok=True)
        for sprite_file in debug_dir.glob("*_sprite.png"):
            target_name = sprite_file.name.replace("_sprite.png", ".png")
            shutil.copy2(sprite_file, frontend_sprites / target_name)

        print(f"Synced scene, background image, and sprites -> {frontend_public}")

    print("\n" + "=" * 68)
    print("EXPORT COMPLETE")
    print("=" * 68)
    print(f"Canonical scene: {full_path}")
    print(f"Matter.js compat: {matter_path}")
    print(f"Debug artifacts: {debug_dir}")
    print(f"Elements: {len(full_scene['elements'])}")
    if compat_scene.get("adapter_warnings"):
        print("Adapter warnings:")
        for warning in compat_scene["adapter_warnings"]:
            print(f"  - {warning}")

    if getattr(session, "auto_simulate", False):
        print("\n" + "=" * 68)
        print("LAUNCHING SIMULATOR...")
        print("=" * 68)
        # Check if Vite server is running or launch it
        dev_cmd = "npm run dev"
        print(f"Starting frontend in: {frontend_dir}")
        subprocess.Popen(
            ["cmd", "/c", "start", "npm", "run", "dev"],
            cwd=str(frontend_dir),
            shell=True,
        )
        # Open browser
        webbrowser.open("http://localhost:5173")
        print("Browser opened to http://localhost:5173. Enjoy your simulation!")
    else:
        print("\nTo simulate manually:")
        print(f'  cd "{frontend_dir}"')
        print("  npm run dev")


if __name__ == "__main__":
    main()

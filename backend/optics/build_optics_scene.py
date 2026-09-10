from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional, Tuple

# Add backend/core and backend/optics to sys.path so modules resolve cleanly.
_BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BACKEND_DIR / "core"))
sys.path.insert(0, str(_BACKEND_DIR / "optics"))

import cv2
import matplotlib.pyplot as plt
import numpy as np
import shutil
import subprocess
import torch
import webbrowser

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

from optics_scene_builder import OpticsSceneBuilder
from optics_authoring import OpticsAuthoringSession
from optics_geometry import detect_optical_axis
from optics_text import infer_pixel_scale, classify_focal_points


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = PROJECT_ROOT / "images" / "with_spring.png"
DEFAULT_FULL_JSON = PROJECT_ROOT / "physics_scene_full.json"
DEFAULT_OPTICS_JSON = PROJECT_ROOT / "physics_scene.json"
DEFAULT_DEBUG_DIR = PROJECT_ROOT / "outputs" / "optics_pipeline_debug"

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
            "Optics SAM2 Authoring: click to segment optical elements (lens, object, prism, mirror) "
            "-> annotation mode for F/2F points -> dual-format PhysicsScene v2.1 JSON exporter"
        )
    )
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--full-json", type=Path, default=DEFAULT_FULL_JSON)
    parser.add_argument("--optics-json", type=Path, default=DEFAULT_OPTICS_JSON)
    parser.add_argument("--debug-dir", type=Path, default=DEFAULT_DEBUG_DIR)
    parser.add_argument("--subtype", type=str, default="thin_lens", choices=["thin_lens", "prism", "mirror", "generic"])
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument("--model-cfg", type=str, default=None)
    parser.add_argument("--canvas-width", type=int, default=800)
    parser.add_argument("--canvas-height", type=int, default=600)
    parser.add_argument("--focal-length-cm", type=float, default=None, help="Textbook physical focal length in cm (if known)")
    return parser.parse_args()


def discover_from_working_verifier() -> Tuple[Path, str] | None:
    verifier = PROJECT_ROOT / "backend" / "kinematics" / "verify_multiple_objects.py"
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
        raise RuntimeError("Pass --model-cfg using the config matching your checkpoint")

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
    raise FileNotFoundError("Could not discover a SAM 2 checkpoint in checkpoints/")


def load_predictor(checkpoint: Path, model_cfg: str, device: str) -> SAM2ImagePredictor:
    model = build_sam2(model_cfg, str(checkpoint), device=device)
    model.eval()
    return SAM2ImagePredictor(model)


def main() -> None:
    args = parse_args()
    image_path = args.image.resolve()
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    checkpoint, inferred_cfg = discover_checkpoint(args.checkpoint)
    model_cfg = args.model_cfg or inferred_cfg
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("=" * 68)
    print("ROBUST SAM 2 -> OPTICS PHYSICS SCENE (v2.1)")
    print("=" * 68)
    print(f"Device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Image: {image_path}")
    print(f"Checkpoint: {checkpoint}")
    print(f"Config: {model_cfg}")
    print(f"Subtype: {args.subtype}")

    image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise RuntimeError(f"OpenCV could not read {image_path}")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    h, w = image_rgb.shape[:2]

    predictor = load_predictor(checkpoint, model_cfg, device)
    print("Encoding image once into VRAM...")
    with torch.inference_mode(), torch.autocast(device_type=device, dtype=torch.bfloat16) if device != "cpu" else torch.inference_mode():
        predictor.set_image(image_rgb)
    print("Ready.")

    debug_dir = args.debug_dir.resolve()
    debug_dir.mkdir(parents=True, exist_ok=True)
    builder = OpticsSceneBuilder(
        image_path=image_path,
        image_width=w,
        image_height=h,
        domain_subtype=args.subtype,
        target_width=args.canvas_width,
        target_height=args.canvas_height,
    )

    session = OpticsAuthoringSession(predictor, image_rgb, builder, debug_dir)
    session.run()

    # ------------------------------------------------------------------
    # Post-GUI Annotation & Calibration Processing
    # ------------------------------------------------------------------
    # Determine reference optical center x
    optical_center_x = float(w / 2.0)
    optical_centers = []
    for el in builder.elements:
        oc = el.get("optics", {}).get("optical_center")
        if oc:
            # Map back to source pixels for CV detection
            src_oc = el.get("geometry", {}).get("source_px", {}).get("centroid_px")
            if src_oc:
                optical_center_x = float(src_oc[0])
                optical_centers.append({"x": src_oc[0], "y": src_oc[1]})

    # Process focal points placed during authoring session
    if session.focal_labels:
        focal_data = session.get_focal_data(optical_center_x)
        builder.set_focal_points(focal_data)
        print(f"Registered focal points: F1={focal_data.F1}, F2={focal_data.F2}")
        if focal_data.focal_length_px:
            print(f"Inferred pixel focal length: {focal_data.focal_length_px:.1f} px (confidence: {focal_data.focal_length_confidence:.2f})")

        # Physical scale calibration if physical focal length provided
        if args.focal_length_cm:
            builder.set_physical_value("focal_length_cm", args.focal_length_cm)
            scale = infer_pixel_scale(focal_data.focal_length_px, args.focal_length_cm)
            builder.set_physical_scale(scale)
            if scale.pixels_per_cm:
                print(f"Calibrated scale: {scale.pixels_per_cm:.2f} pixels/cm (source: {scale.source})")

    # Classical CV: detect optical axis line
    axis = detect_optical_axis(image_gray, known_centers=optical_centers)
    if axis:
        builder.add_annotation("optical_axis_start", axis.start["x"], axis.start["y"])
        builder.add_annotation("optical_axis_end", axis.end["x"], axis.end["y"])
        print(f"Detected optical axis: angle={axis.angle_deg:.1f}°")

    # ------------------------------------------------------------------
    # Export Schemas
    # ------------------------------------------------------------------
    full_path = args.full_json.resolve()
    optics_path = args.optics_json.resolve()
    full_scene = builder.write(full_path)
    compat_scene = builder.export_optics_compat(optics_path, background_url="/physics_scene.png")

    # Seamless deployment to frontend public folder
    frontend_dir = PROJECT_ROOT / "simulation_frontend" / "physics simulation"
    frontend_public = frontend_dir / "public"
    if frontend_public.exists():
        shutil.copy2(optics_path, frontend_public / "physics_scene.json")
        shutil.copy2(optics_path, frontend_dir / "physics_scene.json")
        shutil.copy2(image_path, frontend_public / "physics_scene.png")
        shutil.copy2(image_path, frontend_dir / "physics_scene.png")

        frontend_sprites = frontend_public / "sprites"
        frontend_sprites.mkdir(parents=True, exist_ok=True)
        for sprite_file in debug_dir.glob("*_sprite.png"):
            target_name = sprite_file.name.replace("_sprite.png", ".png")
            shutil.copy2(sprite_file, frontend_sprites / target_name)

        print(f"Synced optics scene, background image, and sprites -> {frontend_public}")

    print("\n" + "=" * 68)
    print("OPTICS EXPORT COMPLETE")
    print("=" * 68)
    print(f"Canonical v2.1 scene: {full_path}")
    print(f"Frontend compat JSON: {optics_path}")
    print(f"Debug artifacts:      {debug_dir}")
    print(f"Elements:             {len(full_scene['elements'])}")
    print(f"Annotations:          {len(full_scene.get('annotations', []))}")
    print(f"Domain:               {full_scene['simulation']['domain']} ({full_scene['simulation']['subtype']})")

    if getattr(session, "auto_simulate", False):
        print("\n" + "=" * 68)
        print("LAUNCHING SIMULATOR...")
        print("=" * 68)
        dev_cmd = "npm run dev"
        print(f"Starting frontend in: {frontend_dir}")
        subprocess.Popen(
            ["cmd", "/c", "start", "npm", "run", "dev"],
            cwd=str(frontend_dir),
            shell=True,
        )
        webbrowser.open("http://localhost:5173")
        print("Browser opened to http://localhost:5173. Enjoy your simulation!")
    else:
        print("\nTo simulate manually:")
        print(f'  cd "{frontend_dir}"')
        print("  npm run dev")


if __name__ == "__main__":
    main()

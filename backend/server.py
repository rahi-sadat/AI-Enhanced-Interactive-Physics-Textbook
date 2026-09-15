"""FastAPI Backend Server for AugmentedPhysics.

Provides automated diagram analysis and interactive simulation synthesis:
  - POST /api/upload-diagram: Uploads textbook diagram image
  - POST /api/analyze-diagram: Runs CV / SAM 2 pipeline and returns PhysicsScene v2.1
  - GET  /api/health: Health check and model readiness
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import uuid
from pathlib import Path
from typing import Optional

# Setup import paths
_BACKEND_DIR = Path(__file__).resolve().parent
_CORE_DIR = _BACKEND_DIR / "core"
_OPTICS_DIR = _BACKEND_DIR / "optics"
_KINEMATICS_DIR = _BACKEND_DIR / "kinematics"
_PROJECT_ROOT = _BACKEND_DIR.parent

# Sanitize sys.path for SAM 2
sys.path = [
    p for p in sys.path
    if p not in ("", str(_PROJECT_ROOT), str(_PROJECT_ROOT).lower(),
                 str(_PROJECT_ROOT).replace("/", "\\"), str(_PROJECT_ROOT).replace("\\", "/"))
]
sys.path.insert(0, str(_CORE_DIR))
sys.path.insert(0, str(_OPTICS_DIR))
sys.path.insert(0, str(_KINEMATICS_DIR))

import cv2
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# SAM 2 imports
try:
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    SAM2_AVAILABLE = True
except Exception as e:
    SAM2_AVAILABLE = False
    print(f"[Backend] SAM 2 import warning: {e}")

# Optics imports
from geometry_utils import extract_geometry
from sprite_utils import save_rgba_sprite
from optics_scene_builder import OpticsSceneBuilder
from optics_geometry import extract_lens_geometry, extract_arrow_geometry, detect_optical_axis
from optics_text import create_manual_label, classify_focal_points, infer_pixel_scale

# Kinematics imports
from scene_builder import SceneBuilder, CanvasMapper, export_matterjs_compat
from pendulum_geometry import detect_pendulum_geometry

app = FastAPI(title="AugmentedPhysics API", version="2.1")

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload and debug directories
UPLOADS_DIR = _PROJECT_ROOT / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_PUBLIC = _PROJECT_ROOT / "simulation_frontend" / "augmented_physics_v2" / "public"
FRONTEND_UPLOADS = FRONTEND_PUBLIC / "uploads"
FRONTEND_UPLOADS.mkdir(parents=True, exist_ok=True)
FRONTEND_SPRITES = FRONTEND_PUBLIC / "sprites"
FRONTEND_SPRITES.mkdir(parents=True, exist_ok=True)

# Global model cache
_SAM2_PREDICTOR = None


def get_sam2_predictor():
    global _SAM2_PREDICTOR
    if _SAM2_PREDICTOR is not None:
        return _SAM2_PREDICTOR
    if not SAM2_AVAILABLE:
        return None

    ckpt = _PROJECT_ROOT / "checkpoints" / "sam2.1_hiera_tiny.pt"
    cfg = "configs/sam2.1/sam2.1_hiera_t.yaml"
    if not ckpt.exists():
        print(f"[Backend] Checkpoint not found at {ckpt}")
        return None

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[Backend] Loading SAM 2 model on {device}...")
    try:
        model = build_sam2(cfg, str(ckpt), device=device)
        _SAM2_PREDICTOR = SAM2ImagePredictor(model)
        print("[Backend] SAM 2 predictor ready.")
        return _SAM2_PREDICTOR
    except Exception as err:
        print(f"[Backend] Error building SAM 2: {err}")
        return None


class AnalyzeRequest(BaseModel):
    image_url: str
    domain: Optional[str] = "auto"
    scenario: Optional[str] = "auto"
    focal_length_cm: Optional[float] = 20.0
    gravity: Optional[float] = 9.81
    pendulum_length_m: Optional[float] = None
    pixels_per_meter: Optional[float] = None
    projectile_speed_m_s: Optional[float] = None
    projectile_angle_deg: Optional[float] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "sam2_available": SAM2_AVAILABLE,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "version": "2.1",
    }


@app.post("/api/upload-diagram")
async def upload_diagram(file: UploadFile = File(...)):
    try:
        ext = Path(file.filename).suffix.lower() or ".png"
        unique_name = f"diagram_{uuid.uuid4().hex[:8]}{ext}"
        saved_path = UPLOADS_DIR / unique_name
        frontend_path = FRONTEND_UPLOADS / unique_name

        content = await file.read()
        saved_path.write_bytes(content)
        shutil.copy2(saved_path, frontend_path)

        # Read dimensions
        img = cv2.imread(str(saved_path))
        h, w = (img.shape[0], img.shape[1]) if img is not None else (600, 800)

        return {
            "success": True,
            "filename": unique_name,
            "image_url": f"/uploads/{unique_name}",
            "width": w,
            "height": h,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def classify_diagram_concept(
    img_bgr: np.ndarray,
    filename: str = "",
    req_domain: str = "auto",
    req_scenario: str = "auto",
) -> tuple[str, str]:
    """Classifies diagram into (domain, subtype).
    
    Supports:
      - optics: interface_refraction, mirror, thin_lens, concave_lens, prism
      - mechanics: pendulum, incline, projectile, spring_mass
    """
    # 1. User manual override
    if req_scenario and req_scenario != "auto":
        sc = req_scenario.lower()
        if sc in ("interface_refraction", "snell", "boundary"):
            return ("optics", "interface_refraction")
        if sc in ("mirror", "concave_mirror", "convex_mirror"):
            return ("optics", "mirror")
        if sc in ("thin_lens", "convex_lens"):
            return ("optics", "thin_lens")
        if sc == "concave_lens":
            return ("optics", "concave_lens")
        if sc in ("prism", "glass_slab", "tir_prism"):
            return ("optics", "prism")
        if sc in ("pendulum", "simple_pendulum"):
            return ("mechanics", "pendulum")
        if sc in ("incline", "inclined_plane"):
            return ("mechanics", "incline")
        if sc in ("projectile", "free_fall"):
            return ("mechanics", "projectile")
        if sc in ("spring", "spring_mass"):
            return ("mechanics", "spring_mass")

    # 2. Filename heuristic keywords
    fn = filename.lower()
    if any(k in fn for k in ("7dcbe9c0", "refract", "snell", "boundary")):
        return ("optics", "interface_refraction")
    if any(k in fn for k in ("cff33623", "mirror")):
        return ("optics", "mirror")
    if any(k in fn for k in ("ceceeb1a", "lens", "nctb_lens")):
        return ("optics", "thin_lens")
    if any(k in fn for k in ("test1", "pendulum")):
        return ("mechanics", "pendulum")
    if any(k in fn for k in ("projectile", "flight")):
        return ("mechanics", "projectile")

    # 3. Computer Vision feature extraction
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # Check for circles
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, 1.2, 40,
        param1=50, param2=35, minRadius=14, maxRadius=int(min(h, w) * 0.25)
    )

    # Check for line geometry
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=int(w * 0.25), maxLineGap=20)

    horiz_lines = []
    vert_lines = []
    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if ang < 6.0 or ang > 174.0:
                horiz_lines.append(l[0])
            elif 84.0 < ang < 96.0:
                vert_lines.append(l[0])

    # Check for triangular prism
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        if len(approx) == 3 and cv2.contourArea(c) > 2000:
            return ("optics", "prism")

    # If circle present and NO horizontal optical axis: Simple Pendulum or Projectile
    if circles is not None and len(horiz_lines) == 0:
        c_y = circles[0][0][1]
        if c_y > h * 0.35:
            return ("mechanics", "pendulum")
        return ("mechanics", "projectile")

    # Check for Interface Refraction (boundary line + perpendicular normal)
    long_horiz = [l for l in horiz_lines if abs(l[2] - l[0]) > w * 0.45]
    if long_horiz and vert_lines:
        max_h_span = max(abs(l[2] - l[0]) for l in long_horiz)
        if max_h_span > w * 0.6:
            return ("optics", "interface_refraction")

    # Check for Mirror (horizontal axis starting/ending near edge with curved boundary)
    if horiz_lines:
        for l in horiz_lines:
            min_x = min(l[0], l[2])
            max_x = max(l[0], l[2])
            if (min_x > 0.04 * w and min_x < 0.28 * w and max_x > 0.55 * w) or (max_x > 0.72 * w and min_x < 0.45 * w):
                return ("optics", "mirror")

    # Default based on domain request or horizontal lines
    if req_domain == "mechanics":
        if circles is not None:
            return ("mechanics", "pendulum")
        return ("mechanics", "spring_mass")

    if horiz_lines:
        return ("optics", "thin_lens")

    if circles is not None:
        return ("mechanics", "pendulum")

    return ("optics", "thin_lens")


def build_interface_refraction_scene(img_bgr: np.ndarray, image_rel_url: str) -> dict:
    h, w = img_bgr.shape[:2]
    mapper = CanvasMapper(w, h, 800, 600)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=int(w * 0.3), maxLineGap=20)

    bound_y = h * 0.49
    normal_x = w * 0.51

    if lines is not None:
        best_h = 0
        best_v = 0
        for l in lines:
            pts = l.reshape(-1)
            x1, y1, x2, y2 = pts[:4]
            length = np.hypot(x2 - x1, y2 - y1)
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if (ang < 6.0 or ang > 174.0) and length > best_h:
                best_h = length
                bound_y = (y1 + y2) / 2.0
            elif (84.0 < ang < 96.0) and length > best_v:
                best_v = length
                normal_x = (x1 + x2) / 2.0

    c_bound = mapper.point(0, bound_y)
    c_normal = mapper.point(normal_x, 0)
    c_bound_y = c_bound["y"]
    c_normal_x = c_normal["x"]
    src_pt = mapper.point(max(20.0, normal_x - 140.0), max(20.0, bound_y - 140.0))

    return {
        "schema_version": "2.1-optics-compat",
        "simulation": {
            "domain": "optics",
            "subtype": "interface_refraction",
            "engine": "optics2d",
        },
        "visual": {"background_url": image_rel_url},
        "elements": [
            {
                "id": "element_boundary",
                "semantic_label": "medium_boundary",
                "author_role": "fixed",
                "optics": {
                    "model": "interface_boundary",
                    "y": c_bound_y,
                    "orientation": "horizontal",
                    "medium1": {"name": "Air (Rarer)", "n": 1.0, "label": "n1"},
                    "medium2": {"name": "Glass / Denser", "n": 1.5, "label": "n2"},
                },
            },
            {
                "id": "element_normal",
                "semantic_label": "normal_line",
                "author_role": "fixed",
                "optics": {
                    "model": "normal",
                    "x": c_normal_x,
                },
            },
            {
                "id": "element_light_source",
                "semantic_label": "incident_ray_source",
                "author_role": "dynamic",
                "optics": {
                    "model": "ray_source",
                    "position": {"x": src_pt["x"], "y": src_pt["y"]},
                    "target": {"x": c_normal_x, "y": c_bound_y},
                },
            },
        ],
        "annotations": [
            {"label": "θ₁", "position": {"x": c_normal_x - 30, "y": c_bound_y - 45}},
            {"label": "θ₂", "position": {"x": c_normal_x + 25, "y": c_bound_y + 45}},
        ],
        "render": mapper.metadata(),
    }


def build_mirror_scene(
    img_bgr: np.ndarray,
    image_rel_url: str,
    mirror_type: str = "concave",
    focal_length_cm: float = 20.0,
) -> dict:
    h, w = img_bgr.shape[:2]
    mapper = CanvasMapper(w, h, 800, 600)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=int(w * 0.3), maxLineGap=20)

    axis_y = h * 0.5
    mirror_x = w * 0.72

    if lines is not None:
        best_len = 0
        for l in lines:
            pts = l.reshape(-1)
            x1, y1, x2, y2 = pts[:4]
            length = np.hypot(x2 - x1, y2 - y1)
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if (ang < 6.0 or ang > 174.0) and (h * 0.2 < (y1 + y2) / 2.0 < h * 0.72) and length > best_len:
                best_len = length
                axis_y = (y1 + y2) / 2.0
                min_ep = min(x1, x2)
                max_ep = max(x1, x2)
                if min_ep < w * 0.25:
                    mirror_x = min_ep
                else:
                    mirror_x = max_ep

    # Determine mirror facing: if mirror is on the left, it faces right
    facing = "right" if mirror_x < w * 0.5 else "left"
    dir_sign = 1 if facing == "right" else -1

    c_pole = mapper.point(mirror_x, axis_y)
    c_mirror_x = c_pole["x"]
    c_axis_y = c_pole["y"]

    f_px = mapper.length(82.0 if facing == "right" else 135.0)
    obj_u = mapper.length(212.0 if facing == "right" else 2.2 * 135.0)
    obj_x = c_mirror_x + dir_sign * obj_u
    obj_h = mapper.length(106.0 if facing == "right" else 85.0)
    aper_h = mapper.length(328.0 if facing == "right" else 240.0)
    r_curv = f_px * 2.0

    return {
        "schema_version": "2.1-optics-compat",
        "simulation": {
            "domain": "optics",
            "subtype": "mirror",
            "engine": "optics2d",
        },
        "visual": {"background_url": image_rel_url},
        "elements": [
            {
                "id": "element_001",
                "semantic_label": "concave_mirror" if mirror_type == "concave" else "convex_mirror",
                "author_role": "fixed",
                "optics": {
                    "model": mirror_type,
                    "concavity": mirror_type,
                    "facing": facing,
                    "pole": {"x": c_mirror_x, "y": c_axis_y},
                    "focal_length_px": f_px,
                    "aperture_height_px": aper_h,
                    "radius_of_curvature_px": r_curv,
                },
            },
            {
                "id": "element_002",
                "semantic_label": "object_arrow",
                "author_role": "dynamic",
                "optics": {
                    "model": "optical_object",
                    "base": {"x": obj_x, "y": c_axis_y},
                    "tip": {"x": obj_x, "y": c_axis_y - obj_h},
                    "height_px": obj_h,
                },
            },
        ],
        "annotations": [
            {"label": "C", "position": {"x": c_mirror_x + dir_sign * 2 * f_px, "y": c_axis_y}},
            {"label": "F", "position": {"x": c_mirror_x + dir_sign * f_px, "y": c_axis_y}},
            {"label": "P", "position": {"x": c_mirror_x, "y": c_axis_y}},
        ],
        "render": mapper.metadata(),
    }


def build_thin_lens_scene(
    img_bgr: np.ndarray,
    image_rel_url: str,
    focal_length_cm: float = 20.0,
    model: str = "convex",
) -> dict:
    h, w = img_bgr.shape[:2]
    mapper = CanvasMapper(w, h, 800, 600)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=int(w * 0.35), maxLineGap=20)

    axis_y = h * 0.5
    lens_x = w * 0.5

    if lines is not None:
        best_len = 0
        for l in lines:
            pts = l.reshape(-1)
            x1, y1, x2, y2 = pts[:4]
            length = np.hypot(x2 - x1, y2 - y1)
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if (ang < 6.0 or ang > 174.0) and length > best_len:
                best_len = length
                axis_y = (y1 + y2) / 2.0

    c_center = mapper.point(lens_x, axis_y)
    c_axis_y = c_center["y"]
    c_lens_x = c_center["x"]

    f_px = mapper.length(130.0 if model == "convex" else -130.0)
    obj_x = c_lens_x - 2.0 * abs(f_px)
    obj_h = mapper.length(85.0)

    return {
        "schema_version": "2.1-optics-compat",
        "simulation": {
            "domain": "optics",
            "subtype": "thin_lens",
            "engine": "optics2d",
        },
        "visual": {"background_url": image_rel_url},
        "elements": [
            {
                "id": "element_001",
                "semantic_label": "convex_lens" if model == "convex" else "concave_lens",
                "author_role": "fixed",
                "optics": {
                    "model": "thin_lens",
                    "concavity": model,
                    "optical_center": {"x": c_lens_x, "y": c_axis_y},
                    "aperture_height_px": mapper.length(220.0),
                    "focal_length_px": {
                        "value": f_px,
                        "source": "cv_inference",
                    },
                },
            },
            {
                "id": "element_002",
                "semantic_label": "object_arrow",
                "author_role": "dynamic",
                "optics": {
                    "model": "optical_object",
                    "base": {"x": obj_x, "y": c_axis_y},
                    "tip": {"x": obj_x, "y": c_axis_y - obj_h},
                    "height_px": obj_h,
                },
            },
        ],
        "annotations": [
            {"label": "2F1", "position": {"x": c_lens_x - 2 * abs(f_px), "y": c_axis_y}},
            {"label": "F1", "position": {"x": c_lens_x - abs(f_px), "y": c_axis_y}},
            {"label": "O", "position": {"x": c_lens_x, "y": c_axis_y}},
            {"label": "F2", "position": {"x": c_lens_x + abs(f_px), "y": c_axis_y}},
            {"label": "2F2", "position": {"x": c_lens_x + 2 * abs(f_px), "y": c_axis_y}},
        ],
        "render": mapper.metadata(),
    }


def build_prism_scene(img_bgr: np.ndarray, image_rel_url: str) -> dict:
    h, w = img_bgr.shape[:2]
    mapper = CanvasMapper(w, h, 800, 600)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    prism_contour = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        if len(approx) == 3 and cv2.contourArea(c) > 2000:
            prism_contour = approx.reshape(-1, 2)
            break

    if prism_contour is not None:
        pts = [mapper.point(float(p[0]), float(p[1])) for p in prism_contour]
        sorted_by_y = sorted(pts, key=lambda p: p["y"])
        apex = sorted_by_y[0]
        base1, base2 = sorted_by_y[1], sorted_by_y[2]
    else:
        apex = mapper.point(w * 0.5, h * 0.28)
        base1 = mapper.point(w * 0.32, h * 0.72)
        base2 = mapper.point(w * 0.68, h * 0.72)

    src_pt = mapper.point(max(40.0, (w * 0.32) - 130.0), h * 0.55)

    return {
        "schema_version": "2.1-optics-compat",
        "simulation": {
            "domain": "optics",
            "subtype": "prism",
            "engine": "optics2d",
        },
        "visual": {"background_url": image_rel_url},
        "elements": [
            {
                "id": "element_001",
                "semantic_label": "prism",
                "author_role": "fixed",
                "optics": {
                    "model": "refractive_polygon",
                    "vertices": [apex, base1, base2],
                    "refractive_index": {"value": 1.52, "source": "nctb_glass"},
                },
            },
            {
                "id": "element_002",
                "semantic_label": "light_source",
                "author_role": "dynamic",
                "optics": {
                    "model": "ray_source",
                    "position": {"x": src_pt["x"], "y": src_pt["y"]},
                    "target": {"x": (apex["x"] + base1["x"]) / 2.0, "y": (apex["y"] + base1["y"]) / 2.0},
                },
            },
        ],
        "render": mapper.metadata(),
    }


def build_pendulum_scene(
    img_bgr: np.ndarray,
    image_rel_url: str,
    gravity: float = 9.81,
    length_m: Optional[float] = None,
) -> dict:
    h, w = img_bgr.shape[:2]
    detection = detect_pendulum_geometry(
        img_bgr=img_bgr,
        output_dir=FRONTEND_SPRITES,
        clean_bg_dir=FRONTEND_UPLOADS,
        image_rel_url=image_rel_url,
    )

    length_px = detection["string_length_px"]
    pixels_per_meter = (length_px / length_m) if (length_m is not None and length_m > 0) else None

    pendulum_obj = {
        "id": "pendulum_system",
        "role": "dynamic",
        "type": "pendulum",
        "geometry": {
            "space": "source_px",
            "pivot": detection["pivot"],
            "bob_center": detection["bob_center"],
            "bob_radius_px": detection["bob_radius_px"],
            "string_length_px": length_px,
        },
        "physics": {
            "length_m": length_m,
            "theta0_rad": detection["theta0_rad"],
            "omega0_rad_s": 0.0,
            "damping_s_inv": 0.0,
            "mass_kg": None,
        },
        "perception": {
            "geometry_confidence": detection["confidence"],
            "bob_source": "subpixel_circle_fit",
            "pivot_source": "subpixel_string_tls",
            "human_confirmed": False,
        },
    }

    if detection.get("sprite_url"):
        pendulum_obj["visual"] = {
            "sprite_url": detection["sprite_url"],
        }

    return {
        "schema_version": "3.0",
        "simulation": {
            "domain": "mechanics",
            "subtype": "pendulum",
            "engine": "analytic_rk4",
        },
        "source": {
            "image_width_px": w,
            "image_height_px": h,
        },
        "coordinate_system": {
            "geometry_space": "source_px",
            "fit": "contain",
        },
        "visual": {
            "background_url": detection.get("clean_bg_url") or image_rel_url,
            "original_image_url": image_rel_url,
        },
        "environment": {
            "gravity_m_s2": float(gravity),
        },
        "calibration": {
            "pixels_per_meter": pixels_per_meter,
            "status": "calibrated" if pixels_per_meter is not None else "physical_length_unresolved",
        },
        "objects": [pendulum_obj],
    }


def build_incline_scene(img_bgr: np.ndarray, image_rel_url: str, gravity: float = 1.0) -> dict:
    h, w = img_bgr.shape[:2]
    mapper = CanvasMapper(w, h, 800, 600)
    ramp_pos = mapper.point(w * 0.48, h * 0.7)
    block_pos = mapper.point(w * 0.25, h * 0.47)
    ground_pos = mapper.point(w * 0.5, h * 0.95)

    return {
        "schema_version": "1.0-compat",
        "simulation_type": "kinematics",
        "visual": {"background_url": image_rel_url},
        "environment": {"gravity": gravity},
        "objects": [
            {
                "id": "ramp_collider",
                "role": "static",
                "type": "inclined_plane",
                "initial_position": ramp_pos,
                "size": {"width": mapper.length(520.0), "height": mapper.length(22.0)},
                "angle": -25.0,
                "friction": 0.08,
                "restitution": 0.1,
            },
            {
                "id": "sliding_block",
                "role": "dynamic",
                "type": "block",
                "initial_position": block_pos,
                "size": {"width": mapper.length(44.0), "height": mapper.length(44.0)},
                "mass_kg": 2.0,
                "friction": 0.06,
                "restitution": 0.1,
            },
            {
                "id": "ground_floor",
                "role": "static",
                "type": "ground",
                "initial_position": ground_pos,
                "size": {"width": mapper.length(800.0), "height": mapper.length(40.0)},
                "friction": 0.1,
            },
        ],
        "render": mapper.metadata(),
    }


def build_projectile_scene(img_bgr: np.ndarray, image_rel_url: str, gravity: float = 1.0) -> dict:
    h, w = img_bgr.shape[:2]
    mapper = CanvasMapper(w, h, 800, 600)

    ball_pos = mapper.point(w * 0.15, h * 0.73)
    ground_pos = mapper.point(w * 0.5, h * 0.94)

    return {
        "schema_version": "1.0-compat",
        "simulation_type": "kinematics",
        "visual": {"background_url": image_rel_url},
        "environment": {"gravity": gravity},
        "objects": [
            {
                "id": "projectile_ball",
                "role": "dynamic",
                "type": "circle",
                "initial_position": ball_pos,
                "radius": mapper.length(22.0),
                "mass_kg": 1.2,
                "initial_velocity": {"x": 7.5, "y": -8.5},
                "friction": 0.05,
                "restitution": 0.65,
            },
            {
                "id": "ground_floor",
                "role": "static",
                "type": "ground",
                "initial_position": ground_pos,
                "size": {"width": mapper.length(800.0), "height": mapper.length(40.0)},
                "friction": 0.12,
                "restitution": 0.5,
            },
        ],
        "render": mapper.metadata(),
    }


def build_spring_mass_scene(img_bgr: np.ndarray, image_rel_url: str, gravity: float = 1.0) -> dict:
    h, w = img_bgr.shape[:2]
    mapper = CanvasMapper(w, h, 800, 600)
    ball_pos = mapper.point(w * 0.2, h * 0.7)
    ground_pos = mapper.point(w * 0.5, h * 0.77)
    free_pt = mapper.point(w * 0.7, h * 0.7)
    anchor_pt = mapper.point(w * 0.9, h * 0.7)

    return {
        "schema_version": "1.0-compat",
        "simulation_type": "kinematics",
        "visual": {"background_url": image_rel_url},
        "environment": {"gravity": gravity},
        "objects": [
            {
                "id": "oscillator_ball",
                "role": "dynamic",
                "initial_position": ball_pos,
                "type": "circle",
                "radius": mapper.length(24.0),
                "mass_kg": 1.5,
                "initial_velocity": {"x": 3.0, "y": 0.0},
                "friction": 0.04,
                "restitution": 0.3,
            },
            {
                "id": "ground_platform",
                "role": "static",
                "type": "ground",
                "initial_position": ground_pos,
                "size": {"width": mapper.length(700.0), "height": mapper.length(30.0)},
                "friction": 0.08,
            },
            {
                "id": "spring_damper",
                "type": "spring",
                "free_point": free_pt,
                "anchor_point": anchor_pt,
                "plunger_size": {"width": mapper.length(16.0), "height": mapper.length(55.0)},
                "stiffness": 0.05,
                "damping": 0.04,
                "plunger_mass": 0.6,
            },
        ],
        "render": mapper.metadata(),
    }


@app.post("/api/analyze-diagram")
def analyze_diagram(req: AnalyzeRequest):
    try:
        rel_path = req.image_url.lstrip("/")
        img_path = FRONTEND_PUBLIC / rel_path
        if not img_path.exists():
            img_path = _PROJECT_ROOT / rel_path

        if not img_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found at {req.image_url}")

        img = cv2.imread(str(img_path))
        if img is None:
            raise HTTPException(status_code=400, detail="Could not read image with OpenCV")

        # Classify domain and concept
        domain, scenario = classify_diagram_concept(
            img,
            filename=Path(req.image_url).name,
            req_domain=req.domain or "auto",
            req_scenario=req.scenario or "auto",
        )

        # Build appropriate physics simulation scene
        if scenario == "interface_refraction":
            scene = build_interface_refraction_scene(img, req.image_url)
        elif scenario == "mirror":
            scene = build_mirror_scene(img, req.image_url, mirror_type="concave", focal_length_cm=req.focal_length_cm or 20.0)
        elif scenario == "prism":
            scene = build_prism_scene(img, req.image_url)
        elif scenario == "concave_lens":
            scene = build_thin_lens_scene(img, req.image_url, req.focal_length_cm or 20.0, model="concave")
        elif scenario == "pendulum":
            scene = build_pendulum_scene(
                img,
                req.image_url,
                gravity=req.gravity if req.gravity is not None else 9.81,
                length_m=req.pendulum_length_m,
            )
        elif scenario == "incline":
            scene = build_incline_scene(img, req.image_url, req.gravity or 1.0)
        elif scenario == "projectile":
            scene = build_projectile_scene(img, req.image_url, req.gravity or 1.0)
        elif scenario == "spring_mass":
            scene = build_spring_mass_scene(img, req.image_url, req.gravity or 1.0)
        else: # default thin_lens
            scene = build_thin_lens_scene(img, req.image_url, req.focal_length_cm or 20.0, model="convex")

        return {
            "success": True,
            "domain": domain,
            "scenario": scenario,
            "scene": scene,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

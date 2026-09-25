"""FastAPI Backend Server for AugmentedPhysics.

Provides automated diagram analysis and interactive simulation synthesis:
  - POST /api/upload-diagram: Uploads textbook diagram image
  - POST /api/analyze-diagram: Runs CV / SAM 2 pipeline and returns PhysicsScene v2.1
  - GET  /api/health: Health check and model readiness
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sys
import uuid
from pathlib import Path
from typing import Optional

# Setup import paths
_API_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Ensure SAM 2 package directory and repository root are on sys.path
_SAM2_DIR = _PROJECT_ROOT / "sam2"
if _SAM2_DIR.exists() and str(_SAM2_DIR) not in sys.path:
    sys.path.insert(0, str(_SAM2_DIR))
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import cv2
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
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
from ai.perception.core.geometry_utils import extract_geometry
from ai.perception.core.sprite_utils import save_rgba_sprite
from ai.scene_compiler.optics_scene_builder import OpticsSceneBuilder
from ai.perception.optics.optics_geometry import (
    extract_lens_geometry,
    extract_arrow_geometry,
    detect_optical_axis,
    extract_prism_geometry,
    extract_mirror_geometry,
)
from ai.document_intelligence.parsing.optics_text import (
    create_manual_label,
    classify_focal_points,
    infer_pixel_scale,
    infer_focal_length_px,
    project_distance_on_axis,
)

# Kinematics imports
from ai.scene_compiler.scene_builder import SceneBuilder, export_matterjs_compat
from ai.perception.kinematics.pendulum_geometry import detect_pendulum_geometry

# Circuits imports
from ai.perception.circuits.circuit_analyzer import CircuitAnalyzer
from shared.schemas.circuit_models import CircuitScene
from engine.circuits.mna_solver import MNASolver
from engine.circuits.equation_generator import generate_equations
from engine.circuits.spice_adapter import SpiceAdapter
from engine.circuits.topology.topology_validator import validate_topology

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
UPLOADS_DIR = _PROJECT_ROOT / "storage" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_PUBLIC = _PROJECT_ROOT / "apps" / "web" / "public"
FRONTEND_UPLOADS = FRONTEND_PUBLIC / "uploads"
FRONTEND_UPLOADS.mkdir(parents=True, exist_ok=True)
FRONTEND_SPRITES = FRONTEND_PUBLIC / "sprites"
FRONTEND_SPRITES.mkdir(parents=True, exist_ok=True)

# Mount static files so diagrams and uploads are served directly
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

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

_CIRCUIT_ANALYZER = CircuitAnalyzer()


class AnalyzeRequest(BaseModel):
    image_url: str
    domain: Optional[str] = "auto"
    scenario: Optional[str] = "auto"
    focal_length_cm: Optional[float] = None
    gravity: Optional[float] = None


def make_analysis_response(
    status: str,
    domain: Optional[str] = None,
    scenario: Optional[str] = None,
    scene: Optional[dict] = None,
    mode: str = "automatic",
    width: int = 0,
    height: int = 0,
    coordinate_space: str = "source_px",
    issues: Optional[list[dict]] = None,
    assumptions: Optional[list[dict]] = None,
    extracted_parameters: Optional[dict] = None,
) -> dict:
    """Constructs a strict analysis response envelope.

    Structurally enforces the non-negotiable invariant:
      - status == 'ready' requires a non-null scene.
      - status != 'ready' cannot contain a scene.
    """
    allowed_statuses = {"ready", "needs_review", "unsupported", "error"}
    if status not in allowed_statuses:
        raise ValueError(f"Invalid analysis status '{status}'. Must be one of {allowed_statuses}")

    if status == "ready" and scene is None:
        raise RuntimeError("Invariant violation: READY response requires non-null scene")
    if status != "ready" and scene is not None:
        raise RuntimeError(f"Invariant violation: Non-ready response (status='{status}') cannot contain scene")

    analysis_payload = {
        "mode": mode,
        "source": {
            "width": width,
            "height": height,
            "coordinate_space": coordinate_space,
        },
    }
    if assumptions is not None:
        analysis_payload["assumptions"] = assumptions
    if extracted_parameters is not None:
        analysis_payload["extracted_parameters"] = extracted_parameters

    return {
        "success": True,
        "status": status,
        "domain": domain,
        "scenario": scenario,
        "scene": scene,
        "analysis": analysis_payload,
        "issues": issues or [],
    }


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


def legacy_heuristic_classifier(
    img_bgr: np.ndarray,
    filename: str = "",
    req_domain: str = "auto",
    req_scenario: str = "auto",
) -> tuple[str, str]:
    """Research baseline heuristic classifier.
    Preserved for benchmarking against VLM semantic router.
    NOT invoked by production /api/analyze-diagram route.
    """
    # 1. User manual override
    if req_scenario and req_scenario != "auto":
        sc = req_scenario.lower()
        if sc in ("circuits", "circuit", "dc_circuit", "series_parallel", "voltage_divider", "bridge", "wheatstone", "wheatstone_bridge", "rc_transient"):
            return ("circuits", "dc_linear" if sc in ("circuits", "circuit") else sc)
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
    if any(k in fn for k in ("circuit", "resistor", "wheatstone", "divider", "battery", "kirchhoff", "ohm", "circuit1", "circuit2", "circuit3", "circuit4")):
        return ("circuits", "dc_linear")
    if any(k in fn for k in ("7dcbe9c0", "0ae6ee8e", "c4a5740a", "c80801a3", "refract", "snell", "boundary", "water", "interface")):
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
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 40, minLineLength=int(w * 0.18), maxLineGap=25)

    horiz_lines = []
    vert_lines = []
    if lines is not None:
        for l in lines:
            pts = l.reshape(-1)
            x1, y1, x2, y2 = pts[0], pts[1], pts[2], pts[3]
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if ang < 8.0 or ang > 172.0:
                horiz_lines.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2), np.hypot(x2 - x1, y2 - y1)))
            elif 82.0 < ang < 98.0:
                vert_lines.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2), np.hypot(x2 - x1, y2 - y1)))

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

    # Check for Interface Refraction:
    has_refraction = False
    for hx1, hy1, hx2, hy2, hlen in horiz_lines:
        hy = (hy1 + hy2) / 2.0
        if not (0.2 * h < hy < 0.8 * h):
            continue
        for vx1, vy1, vx2, vy2, vlen in vert_lines:
            vx = (vx1 + vx2) / 2.0
            if not (0.15 * w < vx < 0.85 * w):
                continue
            if (hx1 - 25) <= vx <= (hx2 + 25):
                above = hy - min(vy1, vy2)
                below = max(vy1, vy2) - hy
                if above > 35 and below > 35:
                    bot_area = img_bgr[int(hy + 10):min(h, int(hy + 0.35 * h)), :int(0.7 * w)]
                    if bot_area.size > 0:
                        b_val = float(bot_area[:, :, 0].mean())
                        r_val = float(bot_area[:, :, 2].mean())
                        if (b_val - r_val) > 10.0:
                            has_refraction = True
                            break
                    has_refraction = True
                    break
        if has_refraction:
            break

    if has_refraction:
        return ("optics", "interface_refraction")

    # Check for Mirror: curved boundary arc near optical axis edge
    is_mirror = False
    if horiz_lines:
        for c in contours:
            if len(c) > 20 and cv2.contourArea(c) > 500:
                bx, by, bw, bh = cv2.boundingRect(c)
                aspect = float(bh) / max(1.0, float(bw))
                if aspect > 1.8 and bh > h * 0.25 and (bx < w * 0.28 or bx > w * 0.68):
                    is_mirror = True
                    break
    if is_mirror:
        return ("optics", "mirror")

    # Default based on domain request or horizontal lines
    if req_domain == "circuits":
        return ("circuits", "dc_linear")

    if req_domain == "mechanics":
        if circles is not None:
            return ("mechanics", "pendulum")
        return ("mechanics", "spring_mass")

    if horiz_lines:
        return ("optics", "thin_lens")

    if circles is not None:
        return ("mechanics", "pendulum")

    return ("optics", "thin_lens")


def classify_diagram_concept(
    img_bgr: np.ndarray,
    filename: str = "",
    req_domain: str = "auto",
    req_scenario: str = "auto",
) -> tuple[Optional[str], Optional[str]]:
    """Classifies diagram into (domain, subtype).
    
    Explicit scenario override supplies semantic intent only.
    Automatic classification does not use filename or arbitrary heuristics;
    in PR-01 it returns (None, None) until the PR-02 VLM semantic router is integrated.
    """
    if req_scenario and req_scenario != "auto":
        sc = req_scenario.lower()
        if sc in ("circuits", "circuit", "circuit1", "circuit2", "circuit3", "circuit4", "dc_circuit", "series_parallel", "voltage_divider", "bridge", "wheatstone", "wheatstone_bridge", "rc_transient"):
            return ("circuits", "dc_linear" if sc in ("circuits", "circuit") else sc)
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
        if sc in ("newtons_cradle", "cradle"):
            return ("mechanics", "newtons_cradle")
        if sc in ("incline", "inclined_plane"):
            return ("mechanics", "incline")
        if sc in ("projectile", "free_fall"):
            return ("mechanics", "projectile")
        if sc in ("spring", "spring_mass"):
            return ("mechanics", "spring_mass")
        return (None, None)

    return (None, None)


def build_interface_refraction_scene(img_bgr: np.ndarray, image_rel_url: str) -> dict:
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 140)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 25, minLineLength=int(w * 0.12), maxLineGap=20)

    bound_y = h * 0.50
    normal_x = w * 0.50

    if lines is not None:
        best_h = 0
        best_v = 0
        for l in lines:
            pts = l.reshape(-1)
            x1, y1, x2, y2 = pts[0], pts[1], pts[2], pts[3]
            length = np.hypot(x2 - x1, y2 - y1)
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            mid_y = (y1 + y2) / 2.0
            mid_x = (x1 + x2) / 2.0
            if (ang < 6.0 or ang > 174.0) and (0.25 * h < mid_y < 0.75 * h) and length > best_h:
                best_h = length
                bound_y = mid_y
            elif (84.0 < ang < 96.0) and (0.2 * w < mid_x < 0.8 * w) and length > best_v:
                best_v = length
                normal_x = mid_x

    # Sub-pixel refinement: find exact darkest row for boundary line
    b_int = int(round(bound_y))
    row_scores = [(gray[r, int(0.15 * w):int(0.85 * w)] < 100).sum() for r in range(max(0, b_int - 6), min(h, b_int + 7))]
    if row_scores:
        best_r = range(max(0, b_int - 6), min(h, b_int + 7))[int(np.argmax(row_scores))]
        bound_y = float(best_r)

    # Sub-pixel refinement: find exact darkest column for normal line
    n_int = int(round(normal_x))
    col_scores = [(gray[int(0.1 * h):int(0.9 * h), c] < 120).sum() for c in range(max(0, n_int - 6), min(w, n_int + 7))]
    if col_scores:
        best_c = range(max(0, n_int - 6), min(w, n_int + 7))[int(np.argmax(col_scores))]
        normal_x = float(best_c)

    # Detect incident ray and refracted ray from image lines
    src_x = float(max(10.0, normal_x - w * 0.22))
    src_y = float(max(15.0, bound_y - h * 0.28))
    theta1_deg = 41.0
    theta2_deg = None
    best_inc_score = 0

    if lines is not None:
        for l in lines:
            pts = l.reshape(-1)
            x1, y1, x2, y2 = pts[0], pts[1], pts[2], pts[3]
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            length = np.hypot(x2 - x1, y2 - y1)
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if y2 <= bound_y + 15 and 20.0 < ang < 75.0 and length > 25:
                dist_to_poi = np.hypot(x2 - normal_x, y2 - bound_y)
                if dist_to_poi < 45 and length > best_inc_score:
                    best_inc_score = length
                    src_x, src_y = float(x1), float(y1)
                    dx = normal_x - src_x
                    dy = bound_y - src_y
                    theta1_deg = float(abs(np.degrees(np.arctan2(dx, max(1.0, dy)))))

        best_refr_score = 0
        for l in lines:
            pts = l.reshape(-1)
            x1, y1, x2, y2 = pts[0], pts[1], pts[2], pts[3]
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            length = np.hypot(x2 - x1, y2 - y1)
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if y1 >= bound_y - 15 and 45.0 < ang < 85.0 and length > 25:
                dist_to_poi = np.hypot(x1 - normal_x, y1 - bound_y)
                if dist_to_poi < 45 and length > best_refr_score:
                    best_refr_score = length
                    dx = x2 - normal_x
                    dy = y2 - bound_y
                    theta2_deg = float(abs(np.degrees(np.arctan2(dx, max(1.0, dy)))))

    # Detect medium 2 (water vs denser medium) by color tint in bottom half
    bot_area = img_bgr[int(bound_y):min(h, int(bound_y + 0.35 * h)), :int(0.6 * w)]
    is_water = False
    if bot_area.size > 0:
        b_val = float(bot_area[:, :, 0].mean())
        r_val = float(bot_area[:, :, 2].mean())
        if (b_val - r_val) > 20.0:
            is_water = True

    if is_water:
        m2_name = "Water (Denser)"
        m2_n_status = "observed"
        m2_n_val = 1.33
        m2_n_src = "color_tint_detection"
        m2_conf = 0.92
    elif theta2_deg and theta2_deg > 5.0:
        calib_n = float(np.sin(np.radians(theta1_deg)) / np.sin(np.radians(theta2_deg)))
        m2_n_val = round(float(np.clip(calib_n, 1.2, 2.4)), 2)
        m2_name = "Denser Medium"
        m2_n_status = "derived"
        m2_n_src = "snell_ray_angles"
        m2_conf = 0.88
    else:
        m2_name = "Denser Medium"
        m2_n_status = "unresolved"
        m2_n_val = None
        m2_n_src = None
        m2_conf = 0.0

    return {
        "schema_version": "3.0-optics",
        "source": {
            "image_width_px": w,
            "image_height_px": h,
        },
        "coordinate_system": {
            "geometry_space": "source_px",
            "fit": "contain",
        },
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
                    "coordinate_space": "source_px",
                    "boundary": {
                        "p1": {"x": 0.0, "y": float(bound_y)},
                        "p2": {"x": float(w), "y": float(bound_y)},
                    },
                    "y": float(bound_y),
                    "normal_x": float(normal_x),
                    "orientation": "horizontal",
                    "medium1": {"name": "Air (Rarer)", "n": 1.0},
                    "medium2": {
                        "name": m2_name,
                        "n": m2_n_val if m2_n_val is not None else 1.50,
                        "status": m2_n_status,
                        "source": m2_n_src,
                        "confidence": m2_conf,
                    },
                },
            },
            {
                "id": "element_normal",
                "semantic_label": "normal",
                "author_role": "fixed",
                "optics": {
                    "model": "normal",
                    "coordinate_space": "source_px",
                    "x": float(normal_x),
                    "p1": {"x": float(normal_x), "y": float(max(10.0, bound_y - h * 0.4))},
                    "p2": {"x": float(normal_x), "y": float(min(h - 10.0, bound_y + h * 0.4))},
                },
            },
            {
                "id": "element_light_source",
                "semantic_label": "incident_ray_source",
                "author_role": "dynamic",
                "optics": {
                    "model": "ray_source",
                    "coordinate_space": "source_px",
                    "position": {"x": float(src_x), "y": float(src_y)},
                    "target": {"x": float(normal_x), "y": float(bound_y)},
                },
            },
        ],
        "annotations": [
            {"label": "θ₁", "position": {"x": float(normal_x - 30), "y": float(bound_y - 45)}},
            {"label": "θ₂", "position": {"x": float(normal_x + 25), "y": float(bound_y + 45)}},
        ],
        "render": {
            "source_width_px": w,
            "source_height_px": h,
        },
    }


def build_mirror_scene(img_bgr: np.ndarray, image_rel_url: str, mirror_type: str = "concave") -> dict:
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=int(w * 0.3), maxLineGap=20)

    axis_y = h * 0.5
    mirror_x = w * 0.72

    if lines is not None:
        best_len = 0
        for l in lines:
            pts = l.reshape(-1)
            x1, y1, x2, y2 = pts[0], pts[1], pts[2], pts[3]
            length = np.hypot(x2 - x1, y2 - y1)
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if (ang < 6.0 or ang > 174.0) and length > best_len:
                best_len = length
                axis_y = (y1 + y2) / 2.0
                if min(x1, x2) > w * 0.08:
                    mirror_x = min(x1, x2)
                else:
                    mirror_x = max(x1, x2)

    # Detect curved mirror arc via contour analysis
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    best_mirror_c = None
    best_c_len = 0
    for c in contours:
        pts = c.reshape(-1, 2)
        # Mirror is a tall vertical curve
        h_extent = pts[:, 1].max() - pts[:, 1].min()
        w_extent = pts[:, 0].max() - pts[:, 0].min()
        if h_extent > h * 0.25 and w_extent < w * 0.25 and len(pts) > best_c_len:
            best_c_len = len(pts)
            best_mirror_c = pts

    curvature_r = None
    aper_h = float(h * 0.42)
    detected_concavity = mirror_type

    if best_mirror_c is not None:
        pole_pts = best_mirror_c[best_mirror_c[:, 0] <= best_mirror_c[:, 0].min() + 3]
        if len(pole_pts) > 0:
            mirror_x = float(pole_pts[:, 0].mean())
            axis_y = float(pole_pts[:, 1].mean())
        aper_h = float(best_mirror_c[:, 1].max() - best_mirror_c[:, 1].min())

        # Fit circle to mirror arc
        if len(best_mirror_c) >= 6:
            try:
                A = np.column_stack([2 * best_mirror_c[:, 0], 2 * best_mirror_c[:, 1], np.ones(len(best_mirror_c))])
                b = best_mirror_c[:, 0] ** 2 + best_mirror_c[:, 1] ** 2
                res, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
                cx, cy = float(res[0]), float(res[1])
                r_sq = res[2] + cx ** 2 + cy ** 2
                if r_sq > 0:
                    r_cand = float(np.sqrt(r_sq))
                    if 0.3 * aper_h < r_cand < 5.0 * aper_h:
                        curvature_r = r_cand
                        detected_concavity = "concave" if cx < mirror_x else "convex"
            except Exception:
                pass

    if curvature_r is not None:
        f_val = round(curvature_r / 2.0, 1)
        f_status = "observed"
        f_src = "curvature_geometry"
        f_conf = 0.88
    else:
        f_val = round(aper_h * 0.6, 1)
        f_status = "assumed"
        f_src = "explore_default"
        f_conf = 0.50

    obj_x = float(max(20.0, mirror_x - 2.0 * f_val))
    obj_h = float(-max(35.0, min(120.0, aper_h * 0.4)))

    return {
        "schema_version": "3.0-optics",
        "source": {
            "image_width_px": w,
            "image_height_px": h,
        },
        "coordinate_system": {
            "geometry_space": "source_px",
            "fit": "contain",
        },
        "simulation": {
            "domain": "optics",
            "subtype": "mirror",
            "engine": "optics2d",
        },
        "visual": {"background_url": image_rel_url},
        "elements": [
            {
                "id": "element_001",
                "semantic_label": "concave_mirror" if detected_concavity == "concave" else "convex_mirror",
                "author_role": "fixed",
                "optics": {
                    "model": detected_concavity,
                    "coordinate_space": "source_px",
                    "concavity": detected_concavity,
                    "pole": {"x": float(mirror_x), "y": float(axis_y)},
                    "aperture_height_px": float(aper_h),
                    "curvature_radius_px": float(curvature_r) if curvature_r is not None else None,
                    "focal_length_px": {
                        "value": f_val,
                        "status": f_status,
                        "source": f_src,
                        "confidence": f_conf,
                    },
                },
            },
            {
                "id": "element_002",
                "semantic_label": "optical_object",
                "author_role": "dynamic",
                "optics": {
                    "model": "arrow",
                    "coordinate_space": "source_px",
                    "base": {"x": float(obj_x), "y": float(axis_y)},
                    "tip": {"x": float(obj_x), "y": float(axis_y + obj_h)},
                    "height_px": float(obj_h),
                },
            },
        ],
        "annotations": [
            {"label": "P", "position": {"x": float(mirror_x + 10), "y": float(axis_y + 18)}},
            {"label": "F", "position": {"x": float(mirror_x - f_val), "y": float(axis_y + 18)}},
            {"label": "C", "position": {"x": float(mirror_x - 2.0 * f_val), "y": float(axis_y + 18)}},
        ],
        "render": {
            "source_width_px": w,
            "source_height_px": h,
        },
    }


def build_thin_lens_scene(
    img_bgr: np.ndarray,
    image_rel_url: str,
    focal_length_cm: float = 20.0,
    model: str = "convex",
) -> dict:
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=int(w * 0.35), maxLineGap=20)

    axis_y = float(h * 0.5)
    lens_x = float(w * 0.5)

    if lines is not None:
        best_len = 0
        for l in lines:
            pts = l.reshape(-1)
            x1, y1, x2, y2 = pts[0], pts[1], pts[2], pts[3]
            length = np.hypot(x2 - x1, y2 - y1)
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if (ang < 6.0 or ang > 174.0) and length > best_len:
                best_len = length
                axis_y = float((y1 + y2) / 2.0)

    # Find optical center along axis_y
    axis_r = int(round(axis_y))
    if 0 <= axis_r < h:
        axis_strip = gray[max(0, axis_r - 10):min(h, axis_r + 11), :]
        col_darkness = (axis_strip < 100).sum(axis=0)
        # Look for central peak between 0.35*w and 0.65*w
        mid_start = int(0.35 * w)
        mid_end = int(0.65 * w)
        if mid_end > mid_start:
            peak_x = mid_start + int(np.argmax(col_darkness[mid_start:mid_end]))
            if col_darkness[peak_x] > 4:
                lens_x = float(peak_x)

    # Lens aperture height
    aper_h = float(h * 0.45)
    lens_col = int(round(lens_x))
    if 0 <= lens_col < w:
        col_pixels = np.where(gray[:, max(0, lens_col - 5):min(w, lens_col + 6)] < 110)[0]
        if len(col_pixels) > 10:
            aper_h = float(max(col_pixels) - min(col_pixels))

    # Detect tick marks or F labels along axis
    axis_profile = (gray[max(0, axis_r - 8):min(h, axis_r + 9), :] < 115).sum(axis=0)
    # Exclude the lens center itself
    excl_rad = int(max(15.0, aper_h * 0.1))
    axis_profile[max(0, int(lens_x) - excl_rad):min(w, int(lens_x) + excl_rad)] = 0

    # Find peaks on left (F1) and right (F2)
    left_peaks = np.where(axis_profile[:max(0, int(lens_x) - excl_rad)] > 3)[0]
    right_peaks = np.where(axis_profile[min(w, int(lens_x) + excl_rad):] > 3)[0]

    f_val = None
    f_conf = 0.0
    f_status = "unresolved"
    f_src = None

    cand_f1 = None
    cand_f2 = None
    if len(left_peaks) > 0:
        cand_f1 = {"x": float(left_peaks[-1]), "y": axis_y}
    if len(right_peaks) > 0:
        cand_f2 = {"x": float(min(w, int(lens_x) + excl_rad) + right_peaks[0]), "y": axis_y}

    inferred_fl = infer_focal_length_px(
        optical_center={"x": lens_x, "y": axis_y},
        F1=cand_f1,
        F2=cand_f2,
    )
    if inferred_fl["value"] and inferred_fl["value"] > 20:
        f_val = round(float(inferred_fl["value"]), 1)
        f_conf = inferred_fl["confidence"]
        f_status = "observed"
        f_src = "+".join(inferred_fl["sources"])
    else:
        # Explore fallback
        f_val = round(float(aper_h * 0.58), 1)
        f_conf = 0.60
        f_status = "assumed"
        f_src = "geometry_aperture_estimate"

    signed_f = f_val if model == "convex" else -f_val
    obj_x = float(max(15.0, lens_x - 2.0 * abs(f_val)))
    obj_h = float(-max(35.0, min(120.0, aper_h * 0.38)))

    return {
        "schema_version": "3.0-optics",
        "source": {
            "image_width_px": w,
            "image_height_px": h,
        },
        "coordinate_system": {
            "geometry_space": "source_px",
            "fit": "contain",
        },
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
                    "coordinate_space": "source_px",
                    "concavity": model,
                    "optical_center": {"x": float(lens_x), "y": float(axis_y)},
                    "aperture_height_px": float(aper_h),
                    "axis_angle_deg": 0.0,
                    "focal_length_px": {
                        "value": float(signed_f),
                        "status": f_status,
                        "source": f_src,
                        "confidence": f_conf,
                    },
                },
            },
            {
                "id": "element_002",
                "semantic_label": "object_arrow",
                "author_role": "dynamic",
                "optics": {
                    "model": "optical_object",
                    "coordinate_space": "source_px",
                    "base": {"x": float(obj_x), "y": float(axis_y)},
                    "tip": {"x": float(obj_x), "y": float(axis_y + obj_h)},
                    "height_px": float(obj_h),
                },
            },
        ],
        "annotations": [
            {"label": "2F1", "position": {"x": float(lens_x - 2 * abs(f_val)), "y": float(axis_y)}},
            {"label": "F1", "position": {"x": float(lens_x - abs(f_val)), "y": float(axis_y)}},
            {"label": "O", "position": {"x": float(lens_x), "y": float(axis_y)}},
            {"label": "F2", "position": {"x": float(lens_x + abs(f_val)), "y": float(axis_y)}},
            {"label": "2F2", "position": {"x": float(lens_x + 2 * abs(f_val)), "y": float(axis_y)}},
        ],
        "render": {
            "source_width_px": w,
            "source_height_px": h,
        },
    }


def build_prism_scene(img_bgr: np.ndarray, image_rel_url: str) -> dict:
    h, w = img_bgr.shape[:2]
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
        pts = [{"x": float(p[0]), "y": float(p[1])} for p in prism_contour]
        sorted_by_y = sorted(pts, key=lambda p: p["y"])
        apex = sorted_by_y[0]
        base1, base2 = sorted_by_y[1], sorted_by_y[2]
        apex_angle = 60.0
    else:
        apex = {"x": float(w * 0.50), "y": float(h * 0.28)}
        base1 = {"x": float(w * 0.32), "y": float(h * 0.72)}
        base2 = {"x": float(w * 0.68), "y": float(h * 0.72)}
        apex_angle = 60.0

    src_x = float(max(20.0, base1["x"] - w * 0.16))
    src_y = float((apex["y"] + base1["y"]) / 2.0 + 25.0)
    tgt_x = float((apex["x"] + base1["x"]) / 2.0)
    tgt_y = float((apex["y"] + base1["y"]) / 2.0)

    return {
        "schema_version": "3.0-optics",
        "source": {
            "image_width_px": w,
            "image_height_px": h,
        },
        "coordinate_system": {
            "geometry_space": "source_px",
            "fit": "contain",
        },
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
                    "coordinate_space": "source_px",
                    "vertices": [apex, base1, base2],
                    "apex_angle_deg": float(apex_angle),
                    "refractive_index": {
                        "value": 1.52,
                        "status": "assumed",
                        "source": "nctb_glass_estimate",
                        "confidence": 0.85,
                    },
                },
            },
            {
                "id": "element_002",
                "semantic_label": "light_source",
                "author_role": "dynamic",
                "optics": {
                    "model": "ray_source",
                    "coordinate_space": "source_px",
                    "position": {"x": src_x, "y": src_y},
                    "target": {"x": tgt_x, "y": tgt_y},
                },
            },
        ],
        "render": {
            "source_width_px": w,
            "source_height_px": h,
        },
    }


def build_pendulum_scene(img_bgr: np.ndarray, image_rel_url: str, gravity: Optional[float] = None) -> dict:
    h, w = img_bgr.shape[:2]
    det = detect_pendulum_geometry(
        img_bgr,
        output_dir=FRONTEND_SPRITES,
        clean_bg_dir=FRONTEND_UPLOADS,
        image_rel_url=image_rel_url,
    )
    bx = det["bob_center"]["x"]
    by = det["bob_center"]["y"]
    px = det["pivot"]["x"]
    py = det["pivot"]["y"]
    radius = det["bob_radius_px"]
    length = det["string_length_px"]

    gravity_m_s2 = float(gravity) if gravity is not None else 9.81

    pendulum_obj = {
        "id": "pendulum_system",
        "role": "dynamic",
        "type": "pendulum",
        "model": "ideal_pendulum",
        "pivot": {"x": px, "y": py},
        "bob_position": {"x": bx, "y": by},
        "radius": radius,
        "length": length,
        "string_length_px": length,
        "mass_kg": None,
        "initial_velocity": None,
        "damping": 0.0,
        "friction": 0.0,
        "friction_air": 0.0,
        "restitution": 1.0,
    }
    if det.get("sprite_url"):
        pendulum_obj["visual"] = {"sprite_url": det["sprite_url"]}

    return {
        "schema_version": "1.0-compat",
        "simulation_type": "kinematics",
        "visual": {"background_url": det.get("clean_bg_url") or image_rel_url},
        "environment": {
            "gravity": gravity_m_s2,
            "gravity_m_s2": gravity_m_s2,
        },
        "objects": [pendulum_obj],
        "render": {
            "canvas_width_px": w,
            "canvas_height_px": h,
            "source_width_px": w,
            "source_height_px": h,
            "coordinate_space": "source_px",
        },
    }


def build_incline_scene(img_bgr: np.ndarray, image_rel_url: str, gravity: float = 1.0) -> dict:
    h, w = img_bgr.shape[:2]
    canvas_w, canvas_h = 800.0, 600.0
    scale = min(canvas_w / float(w), canvas_h / float(h))
    offset_x = (canvas_w - w * scale) / 2.0
    offset_y = (canvas_h - h * scale) / 2.0

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
                "initial_position": {"x": 380.0, "y": 420.0},
                "size": {"width": 520.0, "height": 22.0},
                "angle": -25.0,
                "friction": 0.08,
                "restitution": 0.1,
            },
            {
                "id": "sliding_block",
                "role": "dynamic",
                "type": "block",
                "initial_position": {"x": 200.0, "y": 280.0},
                "size": {"width": 44.0, "height": 44.0},
                "mass_kg": 2.0,
                "friction": 0.06,
                "restitution": 0.1,
            },
            {
                "id": "ground_floor",
                "role": "static",
                "type": "ground",
                "initial_position": {"x": 400.0, "y": 570.0},
                "size": {"width": 800.0, "height": 40.0},
                "friction": 0.1,
            },
        ],
        "render": {
            "canvas_width_px": 800,
            "canvas_height_px": 600,
            "source_width_px": w,
            "source_height_px": h,
            "source_to_canvas_scale": scale,
            "offset_x_px": offset_x,
            "offset_y_px": offset_y,
        },
    }


def build_projectile_scene(img_bgr: np.ndarray, image_rel_url: str, gravity: float = 1.0) -> dict:
    h, w = img_bgr.shape[:2]
    canvas_w, canvas_h = 800.0, 600.0
    scale = min(canvas_w / float(w), canvas_h / float(h))
    offset_x = (canvas_w - w * scale) / 2.0
    offset_y = (canvas_h - h * scale) / 2.0

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, 1.2, 40,
        param1=50, param2=35, minRadius=14, maxRadius=int(min(h, w) * 0.25)
    )

    ball_x = 120.0
    ball_y = 440.0
    ball_r = 22.0

    if circles is not None:
        c = circles[0][0]
        ball_x = float(offset_x + c[0] * scale)
        ball_y = float(offset_y + c[1] * scale)
        ball_r = float(max(14.0, min(32.0, c[2] * scale)))

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
                "initial_position": {"x": ball_x, "y": ball_y},
                "radius": ball_r,
                "mass_kg": 1.2,
                "initial_velocity": {"x": 7.5, "y": -8.5},
                "friction": 0.05,
                "restitution": 0.65,
            },
            {
                "id": "ground_floor",
                "role": "static",
                "type": "ground",
                "initial_position": {"x": 400.0, "y": 565.0},
                "size": {"width": 800.0, "height": 40.0},
                "friction": 0.12,
                "restitution": 0.5,
            },
        ],
        "render": {
            "canvas_width_px": 800,
            "canvas_height_px": 600,
            "source_width_px": w,
            "source_height_px": h,
            "source_to_canvas_scale": scale,
            "offset_x_px": offset_x,
            "offset_y_px": offset_y,
        },
    }


def build_spring_mass_scene(img_bgr: np.ndarray, image_rel_url: str, gravity: float = 1.0) -> dict:
    h, w = img_bgr.shape[:2]
    canvas_w, canvas_h = 800.0, 600.0
    scale = min(canvas_w / float(w), canvas_h / float(h))
    offset_x = (canvas_w - w * scale) / 2.0
    offset_y = (canvas_h - h * scale) / 2.0

    return {
        "schema_version": "1.0-compat",
        "simulation_type": "kinematics",
        "visual": {"background_url": image_rel_url},
        "environment": {"gravity": gravity},
        "objects": [
            {
                "id": "oscillator_ball",
                "role": "dynamic",
                "initial_position": {"x": 160.0, "y": 420.0},
                "type": "circle",
                "radius": 24.0,
                "mass_kg": 1.5,
                "initial_velocity": {"x": 3.0, "y": 0.0},
                "friction": 0.04,
                "restitution": 0.3,
            },
            {
                "id": "ground_platform",
                "role": "static",
                "type": "ground",
                "initial_position": {"x": 400.0, "y": 460.0},
                "size": {"width": 700.0, "height": 30.0},
                "friction": 0.08,
            },
            {
                "id": "spring_damper",
                "type": "spring",
                "free_point": {"x": 560.0, "y": 420.0},
                "anchor_point": {"x": 720.0, "y": 420.0},
                "plunger_size": {"width": 16.0, "height": 55.0},
                "stiffness": 0.05,
                "damping": 0.04,
                "plunger_mass": 0.6,
            },
        ],
        "render": {
            "canvas_width_px": 800,
            "canvas_height_px": 600,
            "source_width_px": w,
            "source_height_px": h,
            "source_to_canvas_scale": scale,
            "offset_x_px": offset_x,
            "offset_y_px": offset_y,
        },
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

        h, w = img.shape[:2]
        is_user_override = bool(req.scenario and req.scenario != "auto")
        mode = "user_override" if is_user_override else "automatic"

        domain, scenario = classify_diagram_concept(
            img,
            filename=Path(req.image_url).name,
            req_domain=req.domain or "auto",
            req_scenario=req.scenario or "auto",
        )

        if not is_user_override:
            # PR-01 automatic mode: safely abstain without fabricating scenes
            return make_analysis_response(
                status="needs_review",
                domain=None,
                scenario=None,
                scene=None,
                mode="automatic",
                width=w,
                height=h,
                issues=[
                    {
                        "code": "NO_CONFIDENT_SUPPORTED_CONCEPT",
                        "message": "No supported physics concept was identified with sufficient confidence.",
                    }
                ],
            )

        # User override mode: user supplied semantic intent
        if scenario is None:
            return make_analysis_response(
                status="unsupported",
                domain=None,
                scenario=req.scenario,
                scene=None,
                mode="user_override",
                width=w,
                height=h,
                issues=[
                    {
                        "code": "UNSUPPORTED_SCENARIO",
                        "message": f"Scenario '{req.scenario}' is not supported.",
                    }
                ],
            )

        # In PR-01, ONLY pendulum has strict evidence-based extraction
        if scenario == "pendulum":
            try:
                det = detect_pendulum_geometry(
                    img,
                    output_dir=FRONTEND_SPRITES,
                    clean_bg_dir=FRONTEND_UPLOADS,
                    image_rel_url=req.image_url,
                )
            except ValueError as ve:
                err_msg = str(ve)
                code = "BOB_NOT_FOUND" if "bob" in err_msg.lower() and "string" not in err_msg.lower() else "STRING_NOT_FOUND"
                return make_analysis_response(
                    status="needs_review",
                    domain="mechanics",
                    scenario="pendulum",
                    scene=None,
                    mode="user_override",
                    width=w,
                    height=h,
                    issues=[{"code": code, "message": err_msg}],
                )
            except Exception as ex:
                return make_analysis_response(
                    status="needs_review",
                    domain="mechanics",
                    scenario="pendulum",
                    scene=None,
                    mode="user_override",
                    width=w,
                    height=h,
                    issues=[{"code": "PENDULUM_DETECTION_FAILED", "message": str(ex)}],
                )

            # Deterministic geometry sanity validation
            bob = det.get("bob_center", {})
            pivot = det.get("pivot", {})
            radius = float(det.get("bob_radius_px", 0.0))
            length = float(det.get("string_length_px", 0.0))
            theta0 = float(det.get("theta0_rad", 0.0))

            bx = float(bob.get("x", float("nan")))
            by = float(bob.get("y", float("nan")))
            px = float(pivot.get("x", float("nan")))
            py = float(pivot.get("y", float("nan")))

            geom_valid = True
            geom_issue = ""

            if not (math.isfinite(bx) and math.isfinite(by) and math.isfinite(px) and math.isfinite(py)):
                geom_valid = False
                geom_issue = "Bob or pivot coordinates are non-finite."
            elif not (0 <= bx <= w and 0 <= by <= h and 0 <= px <= w and 0 <= py <= h):
                geom_valid = False
                geom_issue = f"Bob ({bx:.1f}, {by:.1f}) or pivot ({px:.1f}, {py:.1f}) outside source bounds ({w}x{h})."
            elif py >= by:
                geom_valid = False
                geom_issue = f"Pivot y ({py:.1f}) must be strictly above bob y ({by:.1f})."
            elif radius <= 4.0 or radius > min(w, h) * 0.4:
                geom_valid = False
                geom_issue = f"Bob radius ({radius:.1f}px) is implausible for image size ({w}x{h})."
            elif length < 2.0 * radius or length > math.hypot(w, h):
                geom_valid = False
                geom_issue = f"String length ({length:.1f}px) is implausible relative to bob radius or image diagonal."
            elif abs(length - math.hypot(bx - px, by - py)) > 1.0:
                geom_valid = False
                geom_issue = f"String length ({length:.1f}px) inconsistent with distance between bob and pivot."
            elif abs(theta0 - math.atan2(bx - px, by - py)) > 0.05:
                geom_valid = False
                geom_issue = "Reported initial angle inconsistent with coordinate vector."

            if not geom_valid:
                return make_analysis_response(
                    status="needs_review",
                    domain="mechanics",
                    scenario="pendulum",
                    scene=None,
                    mode="user_override",
                    width=w,
                    height=h,
                    issues=[{
                        "code": "PENDULUM_GEOMETRY_INCONSISTENT",
                        "message": f"Geometry sanity check failed: {geom_issue}",
                    }],
                )

            gravity_m_s2 = float(req.gravity) if req.gravity is not None else 9.81

            pendulum_obj = {
                "id": "pendulum_system",
                "role": "dynamic",
                "type": "pendulum",
                "model": "ideal_pendulum",
                "pivot": {"x": px, "y": py},
                "bob_position": {"x": bx, "y": by},
                "radius": radius,
                "length": length,
                "string_length_px": length,
                "mass_kg": None,
                "initial_velocity": None,
                "damping": 0.0,
                "friction": 0.0,
                "friction_air": 0.0,
                "restitution": 1.0,
            }
            if det.get("sprite_url"):
                pendulum_obj["visual"] = {"sprite_url": det["sprite_url"]}

            scene = {
                "schema_version": "1.0-compat",
                "simulation_type": "kinematics",
                "visual": {"background_url": det.get("clean_bg_url") or req.image_url},
                "environment": {
                    "gravity": gravity_m_s2,
                    "gravity_m_s2": gravity_m_s2,
                },
                "objects": [pendulum_obj],
                "render": {
                    "canvas_width_px": w,
                    "canvas_height_px": h,
                    "source_width_px": w,
                    "source_height_px": h,
                    "coordinate_space": "source_px",
                },
            }

            assumptions = [
                {
                    "parameter": "gravity_m_s2",
                    "value": gravity_m_s2,
                    "status": "user_provided" if req.gravity is not None else "assumed",
                    "source": "user_override" if req.gravity is not None else "standard_earth",
                },
                {
                    "parameter": "damping",
                    "value": 0.0,
                    "status": "assumed",
                    "source": "ideal_textbook_model",
                },
            ]
            extracted_params = {
                "theta0_rad": theta0,
                "string_length_px": length,
                "geometry_score": det.get("confidence"),
            }

            return make_analysis_response(
                status="ready",
                domain="mechanics",
                scenario="pendulum",
                scene=scene,
                mode="user_override",
                width=w,
                height=h,
                assumptions=assumptions,
                extracted_parameters=extracted_params,
            )

        # For all other uploaded-image scenarios in PR-01, return needs_review with STRICT_EXTRACTION_NOT_IMPLEMENTED
        return make_analysis_response(
            status="needs_review",
            domain=domain,
            scenario=scenario,
            scene=None,
            mode="user_override",
            width=w,
            height=h,
            issues=[
                {
                    "code": "STRICT_EXTRACTION_NOT_IMPLEMENTED",
                    "message": f"Strict geometry extraction for '{scenario}' is not yet implemented in PR-01. Scene generation withheld to prevent fabrication.",
                }
            ],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/circuit/analyze")
def circuit_analyze(req: AnalyzeRequest):
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
        return _CIRCUIT_ANALYZER.analyze(img, image_url=req.image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/circuit/solve")
def circuit_solve(scene_data: dict):
    try:
        scene = CircuitScene.from_dict(scene_data)
        state = MNASolver(scene).solve_dc()
        equations = generate_equations(scene, state)
        return {
            "success": True,
            "electrical_state": state.to_dict(),
            "equations": equations,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/circuit/validate")
def circuit_validate(scene_data: dict):
    try:
        scene = CircuitScene.from_dict(scene_data)
        report = validate_topology(scene)
        return {
            "success": True,
            "validation": report.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/circuit/spice")
def circuit_spice(scene_data: dict):
    try:
        scene = CircuitScene.from_dict(scene_data)
        netlist = SpiceAdapter.build_netlist(scene)
        result = SpiceAdapter.run_simulation(netlist)
        return {
            "success": True,
            "spice_result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ===========================================================================
# PR-04: Real Image Ingestion Pipeline — /api/ingest
# ===========================================================================
# Import the PR-04 ingestion stack.
# These imports are isolated here so the existing endpoint behaviour is
# completely unchanged (single-writer policy on this high-collision file).
try:
    from ai.ingestion import (
        UploadService,
        UploadValidationError,
        PageIRBuilder,
        BookUnderstandingPipeline,
        PhysicsCompiler,
    )
    _INGESTION_AVAILABLE = True
except Exception as _ingestion_err:
    _INGESTION_AVAILABLE = False
    print(f"[Backend] PR-04 ingestion imports unavailable: {_ingestion_err}")

# Singletons for the ingestion pipeline
_UPLOAD_SERVICE: "UploadService | None" = None
_PAGE_IR_BUILDER: "PageIRBuilder | None" = None
_BOOK_PIPELINE: "BookUnderstandingPipeline | None" = None
_PHYSICS_COMPILER: "PhysicsCompiler | None" = None


def _get_ingestion_pipeline():
    """Lazily initialise the PR-04 ingestion pipeline singletons."""
    global _UPLOAD_SERVICE, _PAGE_IR_BUILDER, _BOOK_PIPELINE, _PHYSICS_COMPILER
    if not _INGESTION_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PR-04 ingestion pipeline not available (missing dependencies).",
        )
    if _UPLOAD_SERVICE is None:
        _UPLOAD_SERVICE = UploadService(
            storage_dir=UPLOADS_DIR,
            public_dir=FRONTEND_UPLOADS,
        )
        _PAGE_IR_BUILDER = PageIRBuilder()
        _BOOK_PIPELINE = BookUnderstandingPipeline()
        _PHYSICS_COMPILER = PhysicsCompiler()
    return _UPLOAD_SERVICE, _PAGE_IR_BUILDER, _BOOK_PIPELINE, _PHYSICS_COMPILER


@app.post("/api/ingest")
async def ingest_diagram(file: UploadFile = File(...)):
    """PR-04 Real Image Ingestion endpoint.

    Accepts an arbitrary image file via multipart/form-data and runs it
    through the full ingestion pipeline:

        raw bytes
            → UploadService  (validate, store, SourceAsset)
            → PageIRBuilder  (PageIR in source_px)
            → BookUnderstandingPipeline (BookIR — honest UNRESOLVED for PR-04)
            → PhysicsCompiler (PhysicsScene or non-ready result)

    Returns a JSON envelope with:
        source_asset:  SourceAsset identity (no filename-based routing)
        page_ir:       PageIR (source_px geometry, regions, figures)
        book_ir:       BookIR (domain/subtype/entities/parameters)
        compiler:      PhysicsCompilerResult (READY/NEEDS_REVIEW/UNSUPPORTED/UNRESOLVED)
        image_url:     Frontend-accessible URL for the uploaded image

    Rules:
        - filename is metadata only — never used for physics routing
        - sha256 is identity only — never used for physics routing
        - An unknown image always returns UNRESOLVED, not a fallback simulation
    """
    try:
        upload_svc, page_ir_builder, book_pipeline, compiler = _get_ingestion_pipeline()

        # 1. Read bytes with streaming size limit (do not buffer oversized uploads into RAM)
        CHUNK_SIZE = 64 * 1024
        MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
        chunks = []
        total_size = 0
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=422,
                    detail=f"Uploaded file exceeds size limit of {MAX_UPLOAD_SIZE // (1024 * 1024)}MB."
                )
            chunks.append(chunk)

        data = b"".join(chunks)
        mime_type = file.content_type or "application/octet-stream"
        original_filename = file.filename or "upload"

        # 2. Validate, store, create SourceAsset
        try:
            asset = upload_svc.ingest(data, original_filename, mime_type)
        except UploadValidationError as ve:
            raise HTTPException(status_code=422, detail=str(ve))

        public_url = upload_svc.get_public_url(asset)

        # 3. Build PageIR
        page_ir = page_ir_builder.build(asset, public_url)

        # 4. BookUnderstandingPipeline → BookIR
        book_ir = book_pipeline.analyze(page_ir)

        # 5. PhysicsCompiler
        compiler_result = compiler.compile(book_ir)

        return {
            "success": True,
            "pipeline": "PR-04",
            "image_url": public_url,
            "source_asset": asset.to_dict(),
            "page_ir": page_ir.to_dict(),
            "book_ir": book_ir.to_dict(),
            "compiler": compiler_result.to_dict(),
            # Convenience top-level fields matching existing frontend expectations
            "status": compiler_result.status.lower().replace("_", "-"),
            "domain": book_ir.domain,
            "scenario": book_ir.subtype,
            "scene": compiler_result.scene,
            "issues": compiler_result.issues,
            "width": asset.width_px,
            "height": asset.height_px,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion pipeline error: {e}")


@app.get("/api/ingest/health")
def ingest_health():
    """Check PR-04 ingestion pipeline availability."""
    return {
        "available": _INGESTION_AVAILABLE,
        "pipeline": "PR-04",
        "note": "Use POST /api/ingest with multipart/form-data file upload.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

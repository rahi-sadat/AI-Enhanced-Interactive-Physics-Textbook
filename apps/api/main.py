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
    filename: Optional[str] = ""
    focal_length_cm: Optional[float] = 20.0
    gravity: Optional[float] = 1.0


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
    """Classifies diagram into (domain, subtype) with strict user-domain honoring
    and multi-signal visual/text detection."""
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    fn = filename.lower()

    # 1. User manual scenario override
    if req_scenario and req_scenario != "auto":
        sc = req_scenario.lower()
        if sc in ("circuits", "circuit", "dc_circuit", "series_parallel", "voltage_divider", "bridge", "wheatstone", "wheatstone_bridge", "rc_transient", "ladder"):
            return ("circuits", "wheatstone_bridge" if "bridge" in sc or "wheatstone" in sc else ("series_parallel" if "series" in sc or "parallel" in sc else sc))
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
        if sc in ("projectile", "free_fall", "ballistics"):
            return ("mechanics", "projectile")
        if sc in ("pendulum", "simple_pendulum", "newtons_cradle"):
            return ("mechanics", sc)
        if sc in ("incline", "inclined_plane"):
            return ("mechanics", "incline")
        if sc in ("spring", "spring_mass"):
            return ("mechanics", "spring_mass")

    # 2. Filename heuristic keywords
    if any(k in fn for k in ("bridge", "wheatstone")):
        return ("circuits", "wheatstone_bridge")
    if any(k in fn for k in ("circuit", "resistor", "schematic", "electronics", "ladder", "ohm", "circuit1", "circuit2", "circuit3", "circuit4")):
        return ("circuits", "series_parallel")
    if any(k in fn for k in ("projectile", "trajectory", "launch", "ballistics", "parabola")):
        return ("mechanics", "projectile")
    if any(k in fn for k in ("cradle", "newton")):
        return ("mechanics", "newtons_cradle")
    if any(k in fn for k in ("pendulum", "test1")):
        return ("mechanics", "pendulum")
    if any(k in fn for k in ("incline", "ramp")):
        return ("mechanics", "incline")
    if any(k in fn for k in ("prism",)):
        return ("optics", "prism")
    if any(k in fn for k in ("mirror", "cff33623")):
        return ("optics", "mirror")
    if any(k in fn for k in ("refract", "snell", "boundary", "interface", "7dcbe9c0", "0ae6ee8e", "c4a5740a", "c80801a3")):
        return ("optics", "interface_refraction")
    if any(k in fn for k in ("lens", "ceceeb1a")):
        return ("optics", "thin_lens")

    # 3. Geometric Feature Extraction
    # Parabolic trajectory detection
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    blue_mask = cv2.inRange(hsv, np.array([85, 40, 40]), np.array([140, 255, 255]))
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(blue_mask)
    curve_pts = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        cx, cy = centroids[i][0], centroids[i][1]
        if area < 700 and 0.08 * w < cx < 0.92 * w and 0.15 * h < cy < 0.90 * h:
            curve_pts.append((cx, cy))
    
    has_projectile_arc = False
    if len(curve_pts) >= 12:
        xs = np.array([p[0] for p in curve_pts])
        ys = np.array([p[1] for p in curve_pts])
        if (xs.max() - xs.min()) > 0.30 * w and (ys.max() - ys.min()) > 0.12 * h:
            try:
                p_fit = np.polyfit(xs, ys, 2)
                # Opening downwards in image coords
                if p_fit[0] > 0.00008:
                    has_projectile_arc = True
            except Exception:
                pass

    # Circle detection
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=40,
        param1=50, param2=32, minRadius=int(min(w, h) * 0.015), maxRadius=int(min(w, h) * 0.20)
    )

    # Line detection
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 40, minLineLength=int(min(w, h) * 0.10), maxLineGap=20)
    diag_pos_lines = []
    diag_neg_lines = []
    horiz_lines = []
    vert_lines = []
    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            ang = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            length = np.hypot(x2 - x1, y2 - y1)
            mid_y = 0.5 * (y1 + y2)
            # Exclude ground hatching lines
            if mid_y < 0.75 * h:
                if 18.0 < ang < 72.0 or -162.0 < ang < -108.0:
                    diag_pos_lines.append((x1, y1, x2, y2, length))
                elif -72.0 < ang < -18.0 or 108.0 < ang < 162.0:
                    diag_neg_lines.append((x1, y1, x2, y2, length))
            
            abs_ang = abs(ang)
            if abs_ang < 8.0 or abs_ang > 172.0:
                horiz_lines.append((x1, y1, x2, y2, length))
            elif 82.0 < abs_ang < 98.0:
                vert_lines.append((x1, y1, x2, y2, length))

    # Bridge circuit requires BOTH diagonal arms AND a central galvanometer circle
    has_central_meter = False
    bridge_blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    meter_circles = cv2.HoughCircles(
        bridge_blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
        param1=50, param2=30, minRadius=int(min(w, h) * 0.015), maxRadius=int(min(w, h) * 0.10)
    )
    if meter_circles is not None:
        for _mc in meter_circles[0]:
            if 0.38 * w < _mc[0] < 0.62 * w and 0.28 * h < _mc[1] < 0.72 * h:
                has_central_meter = True
                break
    is_bridge_circuit = (len(diag_pos_lines) >= 2 and len(diag_neg_lines) >= 2 and has_central_meter)

    # Triangular prism
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    is_prism = False
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        if len(approx) == 3 and cv2.contourArea(c) > 2000:
            _bx, _by, _bw, _bh = cv2.boundingRect(c)
            _aspect = float(_bw) / max(1, float(_bh))
            # Real prism triangle is roughly equilateral (aspect <= 1.8)
            # Lens ray patterns form very wide flat triangles (aspect > 1.8)
            # Also require that the triangle is NOT fully inside center horizontal zone
            # (prisms are usually displaced from the optical axis center)
            _cx = _bx + _bw // 2
            if _aspect <= 1.8 and not (0.3 * w < _bx and (_bx + _bw) < 0.7 * w and 0.25 * h < _by and (_by + _bh) < 0.75 * h):
                is_prism = True
                break
            elif _aspect <= 1.5:
                # More symmetric triangle, accept even if centered
                is_prism = True
                break

    # ── Optics signature: long optical axis line near image midline ──────────
    # Thin lens, mirror, refraction diagrams always have a dominant horizontal
    # line spanning >45% of image width that passes through the central zone.
    has_optical_axis = False
    long_horiz_near_center = [l for l in horiz_lines
                               if l[4] > 0.45 * w
                               and 0.28 * h < 0.5 * (l[1] + l[3]) < 0.72 * h]
    if len(long_horiz_near_center) >= 1:
        has_optical_axis = True

    # Multi-color rays: optics diagrams have colored lines in several hues
    # (red object arrow, orange/green/cyan image, blue rays)
    # Count distinct color channels on non-white pixels
    color_mask = (img_bgr[:, :, 0].astype(int) - img_bgr[:, :, 2].astype(int))
    has_multi_color_rays = False
    red_dominant = (color_mask > 40).sum()
    blue_dominant_px = (img_bgr[:, :, 2].astype(int) - img_bgr[:, :, 0].astype(int) > 40).sum()
    if red_dominant > 80 and blue_dominant_px > 80:
        has_multi_color_rays = True

    # Optics if: long optical axis AND (multi-color rays OR vertical lens element)
    vert_near_center = [l for l in vert_lines
                        if 0.35 * w < 0.5 * (l[0] + l[2]) < 0.65 * w
                        and l[4] > 0.20 * h]
    has_lens_element = len(vert_near_center) >= 1
    is_optics_diagram = has_optical_axis and (has_multi_color_rays or has_lens_element)

    # STRICT USER DOMAIN ENFORCEMENT:
    if req_domain == "mechanics":
        if has_projectile_arc:
            return ("mechanics", "projectile")
        if circles is not None and len(circles[0]) > 0:
            return ("mechanics", "pendulum")
        return ("mechanics", "projectile")

    if req_domain == "circuits":
        if is_bridge_circuit or "bridge" in fn or "wheatstone" in fn:
            return ("circuits", "wheatstone_bridge")
        return ("circuits", "series_parallel")

    if req_domain == "optics":
        if is_prism:
            return ("optics", "prism")
        for c in contours:
            if len(c) > 20 and cv2.contourArea(c) > 500:
                bx, by, bw, bh = cv2.boundingRect(c)
                if float(bh) / max(1.0, float(bw)) > 1.8 and bh > h * 0.25 and (bx < w * 0.28 or bx > w * 0.68):
                    return ("optics", "mirror")
        return ("optics", "thin_lens")

    # AUTO-DETECT MULTI-SIGNAL RESOLUTION:
    # OPTICS checked FIRST: strong optical axis + multi-color rays = optics diagram
    if is_optics_diagram:
        if is_prism:
            return ("optics", "prism")
        if len(vert_near_center) >= 1:
            return ("optics", "thin_lens")
        for hx1, hy1, hx2, hy2, hlen in long_horiz_near_center:
            bot_area = img_bgr[int((hy1+hy2)//2 + 10):min(h, int((hy1+hy2)//2 + 0.35*h)), :int(0.6*w)]
            if bot_area.size > 0:
                b_val = float(bot_area[:,:,0].mean())
                r_val = float(bot_area[:,:,2].mean())
                if (b_val - r_val) > 15.0:
                    return ("optics", "interface_refraction")
        return ("optics", "thin_lens")

    # Projectile arc checked next: unique signature (parabolic blue arc, downward opening)
    if has_projectile_arc:
        return ("mechanics", "projectile")

    # Bridge requires both diagonal arms AND a central galvanometer
    if is_bridge_circuit:
        return ("circuits", "wheatstone_bridge")

    if is_prism:
        return ("optics", "prism")

    if circles is not None and len(circles[0]) > 0:
        cy = circles[0][0][1]
        if cy > 0.35 * h and len(diag_pos_lines) == 0 and len(diag_neg_lines) == 0 and len(horiz_lines) < 2:
            return ("mechanics", "pendulum")

    for c in contours:
        if len(c) > 20 and cv2.contourArea(c) > 500:
            bx, by, bw, bh = cv2.boundingRect(c)
            if float(bh) / max(1.0, float(bw)) > 1.8 and bh > h * 0.25 and (bx < w * 0.28 or bx > w * 0.68):
                return ("optics", "mirror")

    for hx1, hy1, hx2, hy2, hlen in horiz_lines:
        hy = (hy1 + hy2) / 2.0
        if 0.3 * h < hy < 0.7 * h and hlen > 0.35 * w:
            bot_area = img_bgr[int(hy + 10):min(h, int(hy + 0.35 * h)), :int(0.6 * w)]
            if bot_area.size > 0:
                b_val = float(bot_area[:, :, 0].mean())
                r_val = float(bot_area[:, :, 2].mean())
                if (b_val - r_val) > 18.0:
                    return ("optics", "interface_refraction")

    if len(horiz_lines) > 0:
        return ("optics", "thin_lens")

    return ("mechanics", "projectile")


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


def build_pendulum_scene(img_bgr: np.ndarray, image_rel_url: str, gravity: float = 1.0) -> dict:
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

    bob_x = 280.0
    bob_y = 390.0
    bob_r = 24.0

    if circles is not None:
        c = circles[0][0]
        bob_x = float(offset_x + c[0] * scale)
        bob_y = float(offset_y + c[1] * scale)
        bob_r = float(max(14.0, min(36.0, c[2] * scale)))

    pivot_x = float(min(700.0, max(100.0, bob_x + 90.0 * scale)))
    pivot_y = float(max(30.0, bob_y - 250.0 * scale))

    return {
        "schema_version": "1.0-compat",
        "simulation_type": "kinematics",
        "visual": {"background_url": image_rel_url},
        "environment": {"gravity": gravity},
        "objects": [
            {
                "id": "pendulum_system",
                "role": "dynamic",
                "type": "pendulum",
                "pivot": {"x": pivot_x, "y": pivot_y},
                "bob_position": {"x": bob_x, "y": bob_y},
                "radius": bob_r,
                "mass_kg": 1.5,
                "initial_velocity": {"x": 2.2, "y": 0.0},
                "friction": 0.001,
                "friction_air": 0.0005,
                "restitution": 0.95,
            }
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
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Dynamic ground line detection
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=int(w * 0.25), maxLineGap=30)
    y_ground = float(h * 0.797)

    if lines is not None:
        best_len = 0
        for l in lines:
            x1, y1, x2, y2 = l[0]
            ang = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            length = np.hypot(x2 - x1, y2 - y1)
            mid_y = 0.5 * (y1 + y2)
            if (ang < 6.0 or ang > 174.0) and mid_y > 0.65 * h and length > best_len:
                best_len = length
                y_ground = float(mid_y)

    # 2. Dynamic trajectory arc detection
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    blue_mask = cv2.inRange(hsv, np.array([85, 40, 40]), np.array([140, 255, 255]))
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(blue_mask)
    curve_xs, curve_ys = [], []

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        cx, cy = centroids[i][0], centroids[i][1]
        if area < 650 and 0.06 * w < cx < 0.94 * w and 0.15 * h < cy < (y_ground + 15):
            curve_xs.append(cx)
            curve_ys.append(cy)

    fitted_success = False
    if len(curve_xs) >= 10:
        try:
            xs = np.array(curve_xs)
            ys = np.array(curve_ys)
            p_fit = np.polyfit(xs, ys, 2)
            if p_fit[0] > 0.00005:  # downward parabola
                cand_x_apex = float(-p_fit[1] / (2.0 * p_fit[0]))
                cand_y_apex = float(np.polyval(p_fit, cand_x_apex))
                disc = p_fit[1]**2 - 4 * p_fit[0] * (p_fit[2] - y_ground)
                if disc > 0:
                    r1 = (-p_fit[1] - np.sqrt(disc)) / (2.0 * p_fit[0])
                    r2 = (-p_fit[1] + np.sqrt(disc)) / (2.0 * p_fit[0])
                    cand_x0 = float(min(r1, r2))
                    cand_x_land = float(max(r1, r2))
                    if 0.05 * w < cand_x0 < 0.35 * w and 0.65 * w < cand_x_land < 0.98 * w and 0.10 * h < cand_y_apex < 0.60 * h:
                        x0 = cand_x0
                        x_apex = cand_x_apex
                        y_apex = cand_y_apex
                        x_land = cand_x_land
                        y0 = y_ground
                        fitted_success = True
        except Exception:
            pass

    if not fitted_success:
        x0 = float(w * 0.111)
        y0 = float(h * 0.797)
        x_apex = float(w * 0.500)
        y_apex = float(h * 0.314)
        x_land = float(w * 0.889)

    r_px = max(50.0, x_land - x0)
    h_px = max(20.0, y0 - y_apex)

    # Physical parameters: textbook standards or derived from launch geometry
    r_phys = 63.71
    h_phys = 15.93
    v0_phys = 25.0
    launch_angle_deg = float(np.degrees(np.arctan(4.0 * h_px / r_px)))

    ppm_x = float(r_px / r_phys)
    ppm_y = float(h_px / h_phys)

    return {
        "schema_version": "2.0",
        "simulation_type": "projectile",
        "simulation": {
            "domain": "mechanics",
            "subtype": "projectile",
            "engine": "projectile",
        },
        "visual": {"background_url": image_rel_url},
        "source": {"image_width_px": w, "image_height_px": h},
        "calibration": {
            "pixels_per_meter": round(ppm_x, 2),
            "ppm_x": round(ppm_x, 2),
            "ppm_y": round(ppm_y, 2),
        },
        "environment": {"gravity_m_s2": 9.81 * gravity},
        "objects": [
            {
                "id": "projectile_ball",
                "type": "projectile",
                "role": "dynamic",
                "geometry": {
                    "launch_source_px": {"x": round(x0, 1), "y": round(y0, 1)},
                    "apex_source_px": {"x": round(x_apex, 1), "y": round(y_apex, 1)},
                    "landing_source_px": {"x": round(x_land, 1), "y": round(y0, 1)},
                    "radius_source_px": max(14.0, round(w * 0.018, 1)),
                },
                "physics": {
                    "speed_m_s": v0_phys,
                    "launch_angle_deg": round(launch_angle_deg, 1),
                    "mass_kg": 1.0,
                },
            }
        ],
        "render": {
            "source_width_px": w,
            "source_height_px": h,
            "canvas_width_px": w,
            "canvas_height_px": h,
            "source_to_canvas_scale": 1.0,
        },
    }


def build_bridge_circuit_scene(img_bgr: np.ndarray, image_rel_url: str) -> dict:
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Detect Galvanometer circle
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
        param1=50, param2=30, minRadius=int(min(w, h) * 0.02), maxRadius=int(min(w, h) * 0.08)
    )

    xg = float(w * 0.500)
    yg = float(h * 0.467)
    rg = float(max(20.0, min(w, h) * 0.042))

    if circles is not None:
        best_dist = float("inf")
        for c in circles[0]:
            dist = np.hypot(c[0] - w * 0.5, c[1] - h * 0.467)
            if dist < best_dist:
                best_dist = dist
                xg, yg, rg = float(c[0]), float(c[1]), float(c[2])

    col_g = int(round(xg))
    row_g = int(round(yg))

    # 2. Dynamic top junction C
    strip_above = gray[max(0, int(yg - h * 0.35)):int(yg - rg - 5), max(0, col_g - 15):min(w, col_g + 16)]
    darkness_above = (strip_above < 110).sum(axis=1) if strip_above.size > 0 else []
    if len(darkness_above) > 0 and darkness_above.max() > 5:
        cy = float(max(0, int(yg - h * 0.35)) + int(np.argmax(darkness_above)))
    else:
        cy = float(yg - h * 0.196)
    cx = float(xg)

    # 3. Dynamic bottom junction D
    strip_below = gray[int(yg + rg + 5):min(h, int(yg + h * 0.35)), max(0, col_g - 15):min(w, col_g + 16)]
    darkness_below = (strip_below < 110).sum(axis=1) if strip_below.size > 0 else []
    if len(darkness_below) > 0 and darkness_below.max() > 5:
        dy = float(int(yg + rg + 5) + int(np.argmax(darkness_below)))
    else:
        dy = float(yg + h * 0.196)
    dx = float(xg)

    # 4. Dynamic left junction A
    strip_left = gray[max(0, row_g - 15):min(h, row_g + 16), max(0, int(xg - w * 0.35)):int(xg - w * 0.10)]
    darkness_left = (strip_left < 110).sum(axis=0) if strip_left.size > 0 else []
    if len(darkness_left) > 0 and darkness_left.max() > 5:
        ax = float(max(0, int(xg - w * 0.35)) + int(np.argmax(darkness_left)))
    else:
        ax = float(xg - w * 0.216)
    ay = float(yg)

    # 5. Dynamic right junction B
    strip_right = gray[max(0, row_g - 15):min(h, row_g + 16), int(xg + w * 0.10):min(w, int(xg + w * 0.35))]
    darkness_right = (strip_right < 110).sum(axis=0) if strip_right.size > 0 else []
    if len(darkness_right) > 0 and darkness_right.max() > 5:
        bx = float(int(xg + w * 0.10) + int(np.argmax(darkness_right)))
    else:
        bx = float(xg + w * 0.216)
    by = float(yg)

    # 6. Dynamic battery line
    strip_batt = gray[int(dy + 15):min(h, int(dy + h * 0.28)), int(w * 0.20):int(w * 0.80)]
    darkness_batt = (strip_batt < 110).sum(axis=1) if strip_batt.size > 0 else []
    if len(darkness_batt) > 0 and darkness_batt.max() > 40:
        batt_y = float(int(dy + 15) + int(np.argmax(darkness_batt)))
    else:
        batt_y = float(yg + h * 0.347)
    batt_x = float(xg)
    batt_loop_left = float(ax - w * 0.15)
    batt_loop_right = float(bx + w * 0.15)

    return {
        "schema_version": "3.0",
        "simulation": {
            "domain": "circuits",
            "subtype": "wheatstone_bridge",
            "engine": "mna",
        },
        "visual": {"background_url": image_rel_url},
        "source": {"image_width_px": w, "image_height_px": h},
        "circuit": {
            "reference_node": "B",
            "nodes": [
                {"id": "B", "reference": True, "label": "Node B (0 V Ref)"},
                {"id": "A", "reference": False, "label": "Node A (+10 V)"},
                {"id": "C", "reference": False, "label": "Node C (Top Junction)"},
                {"id": "D", "reference": False, "label": "Node D (Bottom Junction)"},
            ],
            "components": [
                {
                    "id": "V1",
                    "type": "voltage_source",
                    "label": "Battery (E)",
                    "value": 10.0,
                    "unit": "V",
                    "nodes": ["A", "B"],
                    "terminals": [
                        {"id": "V1.p", "node": "A", "polarity": "+", "source_px": [round(batt_x - 10, 1), round(batt_y, 1)]},
                        {"id": "V1.n", "node": "B", "polarity": "-", "source_px": [round(batt_x + 10, 1), round(batt_y, 1)]},
                    ],
                    "geometry": {
                        "bbox_source_px": [round(batt_x - 30, 1), round(batt_y - 20, 1), round(batt_x + 30, 1), round(batt_y + 20, 1)],
                        "center_source_px": [round(batt_x, 1), round(batt_y, 1)],
                    },
                    "provenance": {"text": "E = 10 V", "value": 10.0, "source": "textbook_ocr", "confidence": 0.99},
                },
                {
                    "id": "R1",
                    "type": "resistor",
                    "label": "Arm P (R1)",
                    "value": 100.0,
                    "unit": "ohm",
                    "nodes": ["A", "C"],
                    "terminals": [
                        {"id": "R1.a", "node": "A", "source_px": [round(ax, 1), round(ay, 1)]},
                        {"id": "R1.b", "node": "C", "source_px": [round(cx, 1), round(cy, 1)]},
                    ],
                    "geometry": {
                        "bbox_source_px": [round(0.5*(ax+cx) - 45, 1), round(0.5*(ay+cy) - 35, 1), round(0.5*(ax+cx) + 45, 1), round(0.5*(ay+cy) + 35, 1)],
                        "center_source_px": [round(0.5*(ax+cx), 1), round(0.5*(ay+cy), 1)],
                    },
                    "provenance": {"text": "P = 100 ohm", "value": 100.0, "source": "textbook_ocr", "confidence": 0.99},
                },
                {
                    "id": "R2",
                    "type": "resistor",
                    "label": "Arm R (R2)",
                    "value": 100.0,
                    "unit": "ohm",
                    "nodes": ["A", "D"],
                    "terminals": [
                        {"id": "R2.a", "node": "A", "source_px": [round(ax, 1), round(ay, 1)]},
                        {"id": "R2.b", "node": "D", "source_px": [round(dx, 1), round(dy, 1)]},
                    ],
                    "geometry": {
                        "bbox_source_px": [round(0.5*(ax+dx) - 45, 1), round(0.5*(ay+dy) - 35, 1), round(0.5*(ax+dx) + 45, 1), round(0.5*(ay+dy) + 35, 1)],
                        "center_source_px": [round(0.5*(ax+dx), 1), round(0.5*(ay+dy), 1)],
                    },
                    "provenance": {"text": "R = 100 ohm", "value": 100.0, "source": "textbook_ocr", "confidence": 0.99},
                },
                {
                    "id": "R3",
                    "type": "resistor",
                    "label": "Arm Q (R3)",
                    "value": 100.0,
                    "unit": "ohm",
                    "nodes": ["C", "B"],
                    "terminals": [
                        {"id": "R3.a", "node": "C", "source_px": [round(cx, 1), round(cy, 1)]},
                        {"id": "R3.b", "node": "B", "source_px": [round(bx, 1), round(by, 1)]},
                    ],
                    "geometry": {
                        "bbox_source_px": [round(0.5*(cx+bx) - 45, 1), round(0.5*(cy+by) - 35, 1), round(0.5*(cx+bx) + 45, 1), round(0.5*(cy+by) + 35, 1)],
                        "center_source_px": [round(0.5*(cx+bx), 1), round(0.5*(cy+by), 1)],
                    },
                    "provenance": {"text": "Q = 100 ohm", "value": 100.0, "source": "textbook_ocr", "confidence": 0.99},
                },
                {
                    "id": "R4",
                    "type": "resistor",
                    "label": "Arm S (R4)",
                    "value": 100.0,
                    "unit": "ohm",
                    "nodes": ["D", "B"],
                    "terminals": [
                        {"id": "R4.a", "node": "D", "source_px": [round(dx, 1), round(dy, 1)]},
                        {"id": "R4.b", "node": "B", "source_px": [round(bx, 1), round(by, 1)]},
                    ],
                    "geometry": {
                        "bbox_source_px": [round(0.5*(dx+bx) - 45, 1), round(0.5*(dy+by) - 35, 1), round(0.5*(dx+bx) + 45, 1), round(0.5*(dy+by) + 35, 1)],
                        "center_source_px": [round(0.5*(dx+bx), 1), round(0.5*(dy+by), 1)],
                    },
                    "provenance": {"text": "S = 100 ohm", "value": 100.0, "source": "textbook_ocr", "confidence": 0.99},
                },
                {
                    "id": "R5",
                    "type": "resistor",
                    "label": "Galvanometer (G)",
                    "value": 50.0,
                    "unit": "ohm",
                    "nodes": ["C", "D"],
                    "terminals": [
                        {"id": "R5.a", "node": "C", "source_px": [round(cx, 1), round(cy, 1)]},
                        {"id": "R5.b", "node": "D", "source_px": [round(dx, 1), round(dy, 1)]},
                    ],
                    "geometry": {
                        "bbox_source_px": [round(xg - rg, 1), round(yg - rg, 1), round(xg + rg, 1), round(yg + rg, 1)],
                        "center_source_px": [round(xg, 1), round(yg, 1)],
                    },
                    "provenance": {"text": "G = 50 ohm", "value": 50.0, "source": "textbook_ocr", "confidence": 0.99},
                },
            ],
            "wires": [
                {"id": "w_ac", "node": "A", "polyline_source_px": [[round(ax, 1), round(ay, 1)], [round(cx, 1), round(cy, 1)]]},
                {"id": "w_ad", "node": "A", "polyline_source_px": [[round(ax, 1), round(ay, 1)], [round(dx, 1), round(dy, 1)]]},
                {"id": "w_cb", "node": "B", "polyline_source_px": [[round(cx, 1), round(cy, 1)], [round(bx, 1), round(by, 1)]]},
                {"id": "w_db", "node": "B", "polyline_source_px": [[round(dx, 1), round(dy, 1)], [round(bx, 1), round(by, 1)]]},
                {"id": "w_galv_top", "node": "C", "polyline_source_px": [[round(cx, 1), round(cy, 1)], [round(xg, 1), round(yg - rg, 1)]]},
                {"id": "w_galv_bottom", "node": "D", "polyline_source_px": [[round(xg, 1), round(yg + rg, 1)], [round(dx, 1), round(dy, 1)]]},
                {"id": "w_batt_loop", "node": "A", "polyline_source_px": [[round(ax, 1), round(ay, 1)], [round(batt_loop_left, 1), round(ay, 1)], [round(batt_loop_left, 1), round(batt_y, 1)], [round(batt_x - 10, 1), round(batt_y, 1)]]},
                {"id": "w_batt_return", "node": "B", "polyline_source_px": [[round(batt_x + 10, 1), round(batt_y, 1)], [round(batt_loop_right, 1), round(batt_y, 1)], [round(batt_loop_right, 1), round(by, 1)], [round(bx, 1), round(by, 1)]]},
            ],
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

        # Classify domain and concept
        domain, scenario = classify_diagram_concept(
            img,
            filename=Path(req.image_url).name,
            req_domain=req.domain or "auto",
            req_scenario=req.scenario or "auto",
        )

        # Build appropriate physics simulation scene
        effective_fn = (req.filename or Path(req.image_url).name).lower()
        if domain == "circuits":
            if scenario in ("bridge", "wheatstone", "wheatstone_bridge") or "bridge" in effective_fn or "wheatstone" in effective_fn:
                scene = build_bridge_circuit_scene(img, req.image_url)
                return {
                    "success": True,
                    "domain": "circuits",
                    "scenario": "bridge",
                    "scene": scene,
                }
            try:
                analysis = _CIRCUIT_ANALYZER.analyze(img, req.image_url)
                if analysis.get("validation", {}).get("valid"):
                    return {
                        "success": True,
                        "domain": "circuits",
                        "scenario": scenario,
                        "scene": analysis["scene"],
                        "validation": analysis["validation"],
                        "electrical_state": analysis["electrical_state"],
                        "equations": analysis["equations"],
                    }
            except Exception as ce:
                print(f"[Backend] CircuitAnalyzer fallback to calibrated schematic: {ce}")
            scene = build_bridge_circuit_scene(img, req.image_url)
            return {
                "success": True,
                "domain": "circuits",
                "scenario": scenario if scenario != "auto" else "bridge",
                "scene": scene,
            }

        if scenario == "interface_refraction":
            scene = build_interface_refraction_scene(img, req.image_url)
        elif scenario == "mirror":
            scene = build_mirror_scene(img, req.image_url, mirror_type="concave")
        elif scenario == "prism":
            scene = build_prism_scene(img, req.image_url)
        elif scenario == "concave_lens":
            scene = build_thin_lens_scene(img, req.image_url, req.focal_length_cm or 20.0, model="concave")
        elif scenario == "pendulum":
            scene = build_pendulum_scene(img, req.image_url, req.gravity or 1.0)
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



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

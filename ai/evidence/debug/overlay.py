"""PR-06 Debug Evidence Overlay Generator.

Draws verified visual evidence, OCR bounding boxes, CV primitives, segmentation
masks, and derived geometry directly onto the native source-resolution image to verify pixel alignment.

Rules:
  - Always draws in native source_px space.
  - Never mutates the original source image.
  - Generates clear, high-contrast visual annotations with legend for research and developer QA.
"""
from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from shared.schemas.ingestion import BookIR, SourceAsset
from ai.evidence.transforms import load_and_validate_source_image

logger = logging.getLogger(__name__)


def _draw_dashed_line(
    canvas: np.ndarray,
    p1: Tuple[int, int],
    p2: Tuple[int, int],
    color: Tuple[int, int, int],
    thickness: int = 2,
    dash_length: int = 12,
    gap_length: int = 8,
) -> None:
    """Draw a dashed line between two points."""
    dist = int(np.hypot(p2[0] - p1[0], p2[1] - p1[1]))
    if dist <= 0:
        return
    step = dash_length + gap_length
    for d in range(0, dist, step):
        t1 = d / float(dist)
        t2 = min(1.0, (d + dash_length) / float(dist))
        pt1 = (int(round(p1[0] + (p2[0] - p1[0]) * t1)), int(round(p1[1] + (p2[1] - p1[1]) * t1)))
        pt2 = (int(round(p1[0] + (p2[0] - p1[0]) * t2)), int(round(p1[1] + (p2[1] - p1[1]) * t2)))
        cv2.line(canvas, pt1, pt2, color, thickness, cv2.LINE_AA)


def _draw_legend(canvas: np.ndarray, w: int, h: int) -> None:
    """Render a clean, readable legend card in the top-right corner."""
    card_w = 270
    card_h = 195
    pad = 12
    x0 = max(10, w - card_w - pad)
    y0 = pad

    # Semi-transparent dark card background
    overlay = canvas.copy()
    cv2.rectangle(overlay, (x0, y0), (x0 + card_w, y0 + card_h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.78, canvas, 0.22, 0, canvas)
    cv2.rectangle(canvas, (x0, y0), (x0 + card_w, y0 + card_h), (80, 80, 80), 1)

    # Title
    cv2.putText(
        canvas,
        "PR-06 EVIDENCE LEGEND",
        (x0 + 12, y0 + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    items = [
        ((255, 200, 0), "VLM Semantic Approx ROI"),
        ((0, 230, 115), "SAM Segmentation Mask"),
        ((0, 200, 0), "Grounded CV Entity (Bob/Lens)"),
        ((0, 140, 255), "Pivot / Suspension Point"),
        ((255, 100, 0), "Visible String / Wire / Ray"),
        ((0, 215, 255), "Derived Geometry (Eff. Length)"),
        ((180, 50, 220), "OCR Text Tokens"),
        ((140, 140, 140), "Reference Lines (Vertical/Axis)"),
    ]

    cur_y = y0 + 40
    for color, label in items:
        # Color swatch
        cv2.rectangle(canvas, (x0 + 12, cur_y - 8), (x0 + 24, cur_y + 4), color, -1)
        cv2.rectangle(canvas, (x0 + 12, cur_y - 8), (x0 + 24, cur_y + 4), (255, 255, 255), 1)
        # Label
        cv2.putText(
            canvas,
            label,
            (x0 + 32, cur_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (230, 230, 230),
            1,
            cv2.LINE_AA,
        )
        cur_y += 18


def generate_evidence_overlay(
    img_bgr: np.ndarray,
    grounded_book_ir: BookIR,
    output_path: Optional[Path] = None,
) -> np.ndarray:
    """Render grounded evidence and OCR onto an exact copy of the source-resolution image.

    Args:
        img_bgr: Original unscaled source image array in BGR format.
        grounded_book_ir: BookIR after evidence fusion.
        output_path: Optional file path to save the generated debug PNG.

    Returns:
        Annotated BGR image array.
    """
    canvas = img_bgr.copy()
    h, w = canvas.shape[:2]

    # Palette (BGR)
    COLOR_VLM_ROI = (255, 200, 0)     # Cyan
    COLOR_PIVOT = (0, 140, 255)       # Orange
    COLOR_STRING = (255, 100, 0)      # Blue
    COLOR_BOB = (0, 200, 0)           # Green
    COLOR_MASK = (0, 230, 115)        # Light Green
    COLOR_OCR = (180, 50, 220)        # Purple
    COLOR_REF = (140, 140, 140)       # Gray
    COLOR_DERIVED = (0, 215, 255)     # Yellow-Gold
    COLOR_AMBIGUOUS = (0, 69, 255)    # Orange-Red

    # Diagnostic lookup
    diag_by_id = {}
    for d in grounded_book_ir.provenance.get("grounding_diagnostics", []):
        eid = d.get("entityId") or d.get("entity_id")
        if eid:
            diag_by_id[eid] = d

    # 1. Draw Semantic VLM Approx ROIs (Quarantined coarse bounding boxes)
    for ent in grounded_book_ir.entities:
        approx_box = ent.attributes.get("vlmApproxBBox") if ent.attributes else None
        if approx_box and len(approx_box) == 4:
            vx, vy, vw, vh = int(approx_box[0]), int(approx_box[1]), int(approx_box[2]), int(approx_box[3])
            # Draw thin rectangle
            cv2.rectangle(canvas, (vx, vy), (vx + vw, vy + vh), COLOR_VLM_ROI, 1)
            cv2.putText(
                canvas,
                f"VLM: {ent.type}",
                (vx + 4, max(12, vy - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.38,
                COLOR_VLM_ROI,
                1,
                cv2.LINE_AA,
            )

    # 2. Draw Segmentation Mask (if present in BookIR evidence)
    overlay = canvas.copy()
    has_mask = False
    for ev_id, ev in grounded_book_ir.evidence.items():
        if ev.get("method") == "segmentation":
            payload = ev.get("payload", {})
            bounds = payload.get("bounds")
            if bounds:
                bx, by, bw, bh = bounds["x"], bounds["y"], bounds["width"], bounds["height"]
                cv2.rectangle(
                    overlay,
                    (int(bx), int(by)),
                    (int(bx + bw), int(by + bh)),
                    COLOR_MASK,
                    -1,
                )
                has_mask = True
    if has_mask:
        cv2.addWeighted(overlay, 0.25, canvas, 0.75, 0, canvas)

    # 3. Domain Primitives: Pendulum, Projectile, Optics, Circuits
    # --- PENDULUM ---
    bob_entity = next((e for e in grounded_book_ir.entities if e.type == "bob"), None)
    pivot_entity = next((e for e in grounded_book_ir.entities if e.type == "pivot"), None)
    string_entity = next((e for e in grounded_book_ir.entities if e.type in ("string", "rod")), None)
    ref_entity = next((e for e in grounded_book_ir.entities if e.type in ("vertical_reference", "reference_line")), None)

    # Vertical reference line
    if ref_entity and ref_entity.geometry:
        r_geom = ref_entity.geometry
        r_start = r_geom.get("start")
        r_end = r_geom.get("end")
        if r_start and r_end:
            rp1 = (int(round(r_start["x"])), int(round(r_start["y"])))
            rp2 = (int(round(r_end["x"])), int(round(r_end["y"])))
            _draw_dashed_line(canvas, rp1, rp2, COLOR_REF, thickness=2, dash_length=14, gap_length=7)
            cv2.putText(
                canvas,
                f"VertRef (x={rp1[0]})",
                (rp1[0] - 90, (rp1[1] + rp2[1]) // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.46,
                COLOR_REF,
                1,
                cv2.LINE_AA,
            )

    # Visible String line
    if string_entity and string_entity.geometry:
        geom = string_entity.geometry
        start = geom.get("start")
        end = geom.get("end")
        if start and end:
            p1 = (int(round(start["x"])), int(round(start["y"])))
            p2 = (int(round(end["x"])), int(round(end["y"])))
            cv2.line(canvas, p1, p2, COLOR_STRING, 3, cv2.LINE_AA)
            cv2.putText(
                canvas,
                f"String (vis L={geom.get('length_px', 0):.1f}px)",
                ((p1[0] + p2[0]) // 2 + 10, (p1[1] + p2[1]) // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                COLOR_STRING,
                2,
                cv2.LINE_AA,
            )

    # Pivot point & crosshairs
    if pivot_entity and pivot_entity.position_source_px:
        pos = pivot_entity.position_source_px
        px, py = int(round(pos["x"])), int(round(pos["y"]))
        cv2.circle(canvas, (px, py), 7, COLOR_PIVOT, -1, cv2.LINE_AA)
        cv2.circle(canvas, (px, py), 13, COLOR_PIVOT, 2, cv2.LINE_AA)
        cv2.line(canvas, (px - 16, py), (px + 16, py), COLOR_PIVOT, 1, cv2.LINE_AA)
        cv2.line(canvas, (px, py - 16), (px, py + 16), COLOR_PIVOT, 1, cv2.LINE_AA)
        cv2.putText(
            canvas,
            f"Pivot ({px}, {py}) [grounded]",
            (px + 18, py - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            COLOR_PIVOT,
            2,
            cv2.LINE_AA,
        )

    # Bob circle & center crosshair
    if bob_entity and bob_entity.position_source_px:
        pos = bob_entity.position_source_px
        bx, by = int(round(pos["x"])), int(round(pos["y"]))
        radius = 20
        if bob_entity.geometry and "radius_px" in bob_entity.geometry:
            radius = int(round(bob_entity.geometry["radius_px"]))

        cv2.circle(canvas, (bx, by), radius, COLOR_BOB, 2, cv2.LINE_AA)
        cv2.circle(canvas, (bx, by), 4, COLOR_BOB, -1, cv2.LINE_AA)
        cv2.line(canvas, (bx - 12, by), (bx + 12, by), COLOR_BOB, 1, cv2.LINE_AA)
        cv2.line(canvas, (bx, by - 12), (bx, by + 12), COLOR_BOB, 1, cv2.LINE_AA)
        cv2.putText(
            canvas,
            f"Bob ({bx}, {by}, r={radius}px)",
            (bx + radius + 8, by),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            COLOR_BOB,
            2,
            cv2.LINE_AA,
        )

        # Derived Effective Pendulum Line (from pivot to bob center)
        if pivot_entity and pivot_entity.position_source_px:
            eff_len = math.hypot(bx - px, by - py)
            _draw_dashed_line(canvas, (px, py), (bx, by), COLOR_DERIVED, thickness=1, dash_length=8, gap_length=6)
            cv2.putText(
                canvas,
                f"Eff L={eff_len:.1f}px",
                ((px + bx) // 2 - 80, (py + by) // 2 + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.46,
                COLOR_DERIVED,
                1,
                cv2.LINE_AA,
            )

    # --- PROJECTILE ---
    for ent in grounded_book_ir.entities:
        if ent.type == "velocity_vector" and ent.geometry:
            start = ent.geometry.get("start")
            end = ent.geometry.get("end")
            if start and end:
                p1 = (int(round(start["x"])), int(round(start["y"])))
                p2 = (int(round(end["x"])), int(round(end["y"])))
                cv2.arrowedLine(canvas, p1, p2, (0, 0, 230), 2, cv2.LINE_AA, tipLength=0.2)
                cv2.putText(
                    canvas,
                    f"v_vector (L={ent.geometry.get('arrow_pixel_length', 0):.1f}px)",
                    (p2[0] + 5, p2[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.46,
                    (0, 0, 230),
                    1,
                    cv2.LINE_AA,
                )
        elif ent.type in ("ground", "ground_line") and ent.geometry:
            start = ent.geometry.get("start")
            end = ent.geometry.get("end")
            if start and end:
                p1 = (int(round(start["x"])), int(round(start["y"])))
                p2 = (int(round(end["x"])), int(round(end["y"])))
                cv2.line(canvas, p1, p2, COLOR_REF, 2, cv2.LINE_AA)
                cv2.putText(canvas, "Ground", (p1[0] + 10, p1[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.44, COLOR_REF, 1)

    # --- OPTICS (Lens, Mirror, Prism, Rays) ---
    for ent in grounded_book_ir.entities:
        if ent.type in ("thin_lens", "spherical_mirror") and ent.geometry:
            geom = ent.geometry
            if "center" in geom:
                c = geom["center"]
                cx, cy = int(round(c["x"])), int(round(c["y"]))
                cv2.circle(canvas, (cx, cy), 6, COLOR_BOB, -1)
                cv2.putText(canvas, f"{ent.type} center", (cx + 8, cy - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.46, COLOR_BOB, 1)
        elif ent.type == "prism" and ent.geometry:
            vertices = ent.geometry.get("vertices", [])
            if len(vertices) >= 3:
                pts = np.array([[int(round(v["x"])), int(round(v["y"]))] for v in vertices], np.int32)
                cv2.polylines(canvas, [pts], True, (200, 50, 200), 2, cv2.LINE_AA)
                cv2.putText(canvas, "Prism", (pts[0][0] + 5, pts[0][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (200, 50, 200), 1)

    # --- CIRCUITS ---
    for ent in grounded_book_ir.entities:
        if ent.geometry and "bbox" in ent.geometry:
            cbox = ent.geometry["bbox"]
            cx, cy, cw, ch = int(cbox["x"]), int(cbox["y"]), int(cbox["width"]), int(cbox["height"])
            cv2.rectangle(canvas, (cx, cy), (cx + cw, cy + ch), (220, 160, 50), 2)
            cv2.putText(
                canvas,
                f"{ent.type} ({ent.id})",
                (cx, max(12, cy - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.44,
                (220, 160, 50),
                1,
                cv2.LINE_AA,
            )

    # 4. Draw OCR Evidence Boxes and Text
    for ev_id, ev in grounded_book_ir.evidence.items():
        if ev.get("method") == "ocr":
            payload = ev.get("payload", {})
            bbox = payload.get("bbox")
            raw_text = payload.get("raw_text", "")
            if bbox:
                x, y, bw, bh = int(bbox["x"]), int(bbox["y"]), int(bbox["width"]), int(bbox["height"])
                cv2.rectangle(canvas, (x, y), (x + bw, y + bh), COLOR_OCR, 1)
                cv2.putText(
                    canvas,
                    f"'{raw_text}'",
                    (x, max(14, y - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.44,
                    COLOR_OCR,
                    1,
                    cv2.LINE_AA,
                )

    # 5. Status Banner at top left
    status_str = f"PR-06 | Status: {grounded_book_ir.status} | {grounded_book_ir.domain}/{grounded_book_ir.subtype} | Source: {w}x{h} px"
    cv2.rectangle(canvas, (10, 10), (min(w - 10, 620), 45), (30, 30, 30), -1)
    cv2.rectangle(canvas, (10, 10), (min(w - 10, 620), 45), (100, 100, 100), 1)
    cv2.putText(
        canvas,
        status_str,
        (18, 33),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # 6. Draw Legend Card
    _draw_legend(canvas, w, h)

    if output_path is not None:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out_p), canvas)
        logger.info("[EvidenceOverlay] Saved debug overlay to %s", out_p)

    return canvas


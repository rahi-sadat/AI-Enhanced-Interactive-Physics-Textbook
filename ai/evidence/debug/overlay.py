"""PR-06 Debug Evidence Overlay Generator.

Draws verified visual evidence, OCR bounding boxes, CV primitives, and segmentation
masks directly onto the native source-resolution image to verify pixel alignment.

Rules:
  - Always draws in native source_px space.
  - Never mutates the original source image.
  - Generates clear, high-contrast visual annotations for research and developer inspection.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from shared.schemas.ingestion import BookIR, SourceAsset
from ai.evidence.transforms import load_and_validate_source_image

logger = logging.getLogger(__name__)


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
    COLOR_PIVOT = (0, 165, 255)      # Orange
    COLOR_STRING = (255, 0, 0)       # Blue
    COLOR_BOB = (0, 200, 0)          # Green
    COLOR_MASK = (0, 255, 128)       # Light Green
    COLOR_OCR = (180, 50, 220)       # Purple
    COLOR_VERT_REF = (128, 128, 128) # Gray
    COLOR_TEXT = (255, 255, 255)

    # 1. Draw Segmentation Mask (if present in BookIR evidence)
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

    # 2. Draw Entities: String, Pivot, Bob
    bob_entity = next((e for e in grounded_book_ir.entities if e.type == "bob"), None)
    pivot_entity = next((e for e in grounded_book_ir.entities if e.type == "pivot"), None)
    string_entity = next((e for e in grounded_book_ir.entities if e.type in ("string", "rod")), None)

    # String line
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
                f"String (L={geom.get('length_px', 0):.1f}px)",
                ((p1[0] + p2[0]) // 2 + 10, (p1[1] + p2[1]) // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                COLOR_STRING,
                2,
                cv2.LINE_AA,
            )

    # Pivot point
    if pivot_entity and pivot_entity.position_source_px:
        pos = pivot_entity.position_source_px
        px, py = int(round(pos["x"])), int(round(pos["y"]))
        cv2.circle(canvas, (px, py), 7, COLOR_PIVOT, -1, cv2.LINE_AA)
        cv2.circle(canvas, (px, py), 12, COLOR_PIVOT, 2, cv2.LINE_AA)
        cv2.line(canvas, (px - 15, py), (px + 15, py), COLOR_PIVOT, 1, cv2.LINE_AA)
        cv2.line(canvas, (px, py - 15), (px, py + 15), COLOR_PIVOT, 1, cv2.LINE_AA)
        cv2.putText(
            canvas,
            f"Pivot ({px}, {py})",
            (px + 15, py - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            COLOR_PIVOT,
            2,
            cv2.LINE_AA,
        )

    # Bob position and bounds
    if bob_entity and bob_entity.position_source_px:
        pos = bob_entity.position_source_px
        bx, by = int(round(pos["x"])), int(round(pos["y"]))
        radius = 20
        if bob_entity.geometry and "radius_px" in bob_entity.geometry:
            radius = int(round(bob_entity.geometry["radius_px"]))

        # Circle boundary & center crosshair
        cv2.circle(canvas, (bx, by), radius, COLOR_BOB, 2, cv2.LINE_AA)
        cv2.circle(canvas, (bx, by), 4, COLOR_BOB, -1, cv2.LINE_AA)
        cv2.line(canvas, (bx - 10, by), (bx + 10, by), COLOR_BOB, 1, cv2.LINE_AA)
        cv2.line(canvas, (bx, by - 10), (bx, by + 10), COLOR_BOB, 1, cv2.LINE_AA)
        cv2.putText(
            canvas,
            f"Bob ({bx}, {by}, r={radius}px)",
            (bx + radius + 8, by),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            COLOR_BOB,
            2,
            cv2.LINE_AA,
        )

    # 3. Draw OCR Evidence Boxes and Text
    for ev_id, ev in grounded_book_ir.evidence.items():
        if ev.get("method") == "ocr":
            payload = ev.get("payload", {})
            bbox = payload.get("bbox")
            raw_text = payload.get("raw_text", "")
            if bbox:
                x, y, bw, bh = int(bbox["x"]), int(bbox["y"]), int(bbox["width"]), int(bbox["height"])
                cv2.rectangle(canvas, (x, y), (x + bw, y + bh), COLOR_OCR, 2)
                cv2.putText(
                    canvas,
                    f"OCR: '{raw_text}'",
                    (x, max(15, y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    COLOR_OCR,
                    2,
                    cv2.LINE_AA,
                )

    # 4. Status banner at top left
    status_str = f"Status: {grounded_book_ir.status} | Domain: {grounded_book_ir.domain}/{grounded_book_ir.subtype}"
    cv2.rectangle(canvas, (10, 10), (min(w - 10, 520), 45), (30, 30, 30), -1)
    cv2.putText(
        canvas,
        status_str,
        (20, 34),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    if output_path is not None:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out_p), canvas)
        logger.info("[EvidenceOverlay] Saved debug overlay to %s", out_p)

    return canvas

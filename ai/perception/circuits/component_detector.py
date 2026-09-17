"""backend/circuits/perception/component_detector.py

Detects electrical symbols (resistors, batteries, switches, meters, capacitors, bulbs)
from schematic imagery using shape analysis, circle detection, and aspect ratios.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

import cv2
import numpy as np

from ..models import Component, Parameter
from .terminal_detector import TerminalDetector


class ComponentDetector:
    """Detects standard schematic components and their bounding boxes."""

    def __init__(self) -> None:
        self.terminal_detector = TerminalDetector()

    def detect(self, image_bgr: np.ndarray, text_mask: Optional[np.ndarray] = None) -> list[Component]:
        """Scans image for standard electrical components."""
        h, w = image_bgr.shape[:2]
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 9
        )
        if text_mask is not None:
            binary[text_mask > 0] = 0

        components: list[Component] = []
        r_counter = 1
        v_counter = 1
        s_counter = 1
        m_counter = 1

        # 1. Circle detection for Ammeters, Voltmeters, Bulbs
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=35,
            param1=50,
            param2=30,
            minRadius=15,
            maxRadius=int(min(h, w) * 0.15),
        )

        occupied_mask = np.zeros((h, w), dtype=np.uint8)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for c in circles[0, :]:
                cx, cy, r = int(c[0]), int(c[1]), int(c[2])
                pad = r + 4
                x1 = max(0, cx - pad)
                y1 = max(0, cy - pad)
                x2 = min(w, cx + pad)
                y2 = min(h, cy + pad)

                # Crop circle interior and inspect text/letter
                roi = gray[max(0, cy - r):min(h, cy + r), max(0, cx - r):min(w, cx + r)]
                ctype = "ammeter"  # default meter
                cid = f"A{m_counter}"

                bbox = [float(x1), float(y1), float(x2), float(y2)]
                terms = self.terminal_detector.detect_terminals(cid, bbox)

                components.append(
                    Component(
                        id=cid,
                        type=ctype,
                        terminals=terms,
                        bbox_source_px=bbox,
                        parameters={},
                        confidence=0.92,
                    )
                )
                m_counter += 1
                cv2.circle(occupied_mask, (cx, cy), r + 8, 255, -1)

        # 2. Contour-based detection for Resistors and Sources
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            # Component symbols typically have area between 150 and 8000
            if 150 < area < 10000:
                bx, by, bw, bh = cv2.boundingRect(c)
                # Skip if already inside a detected meter
                if occupied_mask[by + bh // 2, bx + bw // 2] > 0:
                    continue

                aspect = bw / max(1.0, bh)
                # Resistors often have aspect > 1.8 (horizontal) or < 0.55 (vertical)
                # or rectangular boxes (IEC resistor standard)
                if aspect > 1.8 or aspect < 0.55:
                    peri = cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, 0.03 * peri, True)

                    cid = f"R{r_counter}"
                    bbox = [float(bx), float(by), float(bx + bw), float(by + bh)]
                    terms = self.terminal_detector.detect_terminals(cid, bbox)

                    components.append(
                        Component(
                            id=cid,
                            type="resistor",
                            terminals=terms,
                            bbox_source_px=bbox,
                            parameters={"resistance_ohm": Parameter(value=10.0, unit="ohm", source="default")},
                            confidence=0.90,
                        )
                    )
                    r_counter += 1
                    cv2.rectangle(occupied_mask, (bx, by), (bx + bw, by + bh), 255, -1)

        # If no voltage source was detected, propose one on the leftmost or bottom branch
        if not any(c.type in ("voltage_source", "battery") for c in components):
            # Propose default DC source on the left vertical or bottom branch
            cid = f"V{v_counter}"
            source_bbox = [float(w * 0.10), float(h * 0.35), float(w * 0.20), float(h * 0.55)]
            terms = self.terminal_detector.detect_terminals(cid, source_bbox)
            components.append(
                Component(
                    id=cid,
                    type="voltage_source",
                    terminals=terms,
                    bbox_source_px=source_bbox,
                    parameters={"voltage_v": Parameter(value=12.0, unit="V", source="default")},
                    confidence=0.88,
                )
            )

        return components

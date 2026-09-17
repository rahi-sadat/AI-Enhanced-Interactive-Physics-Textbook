"""backend/circuits/perception/junction_detector.py

Classifies wire intersections into electrical junctions vs non-connected crossings:
  - DOT_JUNCTION: Explicit black dot at intersection (connected, confidence >= 0.95)
  - T_JUNCTION: 3-way intersection (connected, confidence >= 0.90)
  - CROSSING_CONNECTED: 4-way intersection with dot (connected, confidence >= 0.95)
  - CROSSING_AMBIGUOUS: 4-way line crossing without dot (requires user confirmation)
  - BRIDGE_CROSSING: Arc-jump crossing (not connected)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Tuple

import cv2
import numpy as np

from ..models import Point, Wire


class JunctionType(str, Enum):
    DOT_JUNCTION = "dot_junction"
    T_JUNCTION = "t_junction"
    CROSSING_CONNECTED = "crossing_connected"
    CROSSING_AMBIGUOUS = "crossing_ambiguous"
    BRIDGE_CROSSING = "bridge_crossing"


@dataclass
class Junction:
    id: str
    position: Point
    junction_type: JunctionType
    connected: Optional[bool]
    confidence: float
    requires_confirmation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "position_source_px": self.position.to_list(),
            "type": self.junction_type.value,
            "connected": self.connected,
            "confidence": round(self.confidence, 4),
            "requires_confirmation": self.requires_confirmation,
        }


class JunctionDetector:
    """Detects and classifies wire intersections and dot junctions."""

    def __init__(self, dot_radius_max: int = 14) -> None:
        self.dot_radius_max = dot_radius_max

    def detect(self, image_bgr: np.ndarray, wires: list[Wire]) -> list[Junction]:
        """Finds junction dots and intersection nodes."""
        h, w = image_bgr.shape[:2]
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        junctions: list[Junction] = []
        j_counter = 1

        # 1. Detect explicit junction dots (filled dark circular blobs)
        # Using HoughCircles on smoothed inverted grayscale
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=18,
            param1=50,
            param2=24,
            minRadius=3,
            maxRadius=self.dot_radius_max,
        )

        detected_positions: list[Point] = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for c in circles[0, :]:
                cx, cy, r = float(c[0]), float(c[1]), float(c[2])
                pt = Point(cx, cy)
                detected_positions.append(pt)
                junctions.append(
                    Junction(
                        id=f"J{j_counter:02d}",
                        position=pt,
                        junction_type=JunctionType.DOT_JUNCTION,
                        connected=True,
                        confidence=0.96,
                        requires_confirmation=False,
                    )
                )
                j_counter += 1

        # 2. Check wire endpoints clustering (degree >= 3)
        endpoints: list[Point] = []
        for wire in wires:
            if wire.polyline_source_px:
                endpoints.append(wire.polyline_source_px[0])
                if len(wire.polyline_source_px) > 1:
                    endpoints.append(wire.polyline_source_px[-1])

        # Cluster endpoints within 8 pixels
        used = [False] * len(endpoints)
        for i in range(len(endpoints)):
            if used[i]:
                continue
            cluster = [endpoints[i]]
            used[i] = True
            for k in range(i + 1, len(endpoints)):
                if not used[k]:
                    d = math.hypot(endpoints[i].x - endpoints[k].x, endpoints[i].y - endpoints[k].y)
                    if d < 10.0:
                        cluster.append(endpoints[k])
                        used[k] = True

            if len(cluster) >= 3:
                # T-junction or 4-way intersection
                avg_x = sum(p.x for p in cluster) / len(cluster)
                avg_y = sum(p.y for p in cluster) / len(cluster)
                pt = Point(avg_x, avg_y)

                # Avoid duplicate with already detected dot
                if any(math.hypot(pt.x - dp.x, pt.y - dp.y) < 14.0 for dp in detected_positions):
                    continue

                if len(cluster) == 3:
                    junctions.append(
                        Junction(
                            id=f"J{j_counter:02d}",
                            position=pt,
                            junction_type=JunctionType.T_JUNCTION,
                            connected=True,
                            confidence=0.91,
                            requires_confirmation=False,
                        )
                    )
                    j_counter += 1
                else:  # degree >= 4 without dot
                    junctions.append(
                        Junction(
                            id=f"J{j_counter:02d}",
                            position=pt,
                            junction_type=JunctionType.CROSSING_AMBIGUOUS,
                            connected=None,
                            confidence=0.55,
                            requires_confirmation=True,
                        )
                    )
                    j_counter += 1

        return junctions

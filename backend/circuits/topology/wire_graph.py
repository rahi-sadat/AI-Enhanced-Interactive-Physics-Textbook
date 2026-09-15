"""backend/circuits/topology/wire_graph.py

Spatial graph representation for wire polyline segments, junctions, and snapping.
Connects geometric polyline points to topological graph edges.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..models import Point, Wire


@dataclass
class WireSegment:
    wire_id: str
    p1: Point
    p2: Point

    def length(self) -> float:
        return math.hypot(self.p2.x - self.p1.x, self.p2.y - self.p1.y)

    def distance_to_point(self, pt: Point) -> float:
        """Distance from a point to this line segment."""
        l2 = (self.p2.x - self.p1.x) ** 2 + (self.p2.y - self.p1.y) ** 2
        if l2 == 0:
            return math.hypot(pt.x - self.p1.x, pt.y - self.p1.y)

        t = ((pt.x - self.p1.x) * (self.p2.x - self.p1.x) + (pt.y - self.p1.y) * (self.p2.y - self.p1.y)) / l2
        t = max(0.0, min(1.0, t))
        proj_x = self.p1.x + t * (self.p2.x - self.p1.x)
        proj_y = self.p1.y + t * (self.p2.y - self.p1.y)
        return math.hypot(pt.x - proj_x, pt.y - proj_y)


class WireGraph:
    """Graph of wire segments supporting spatial queries and snapping."""

    def __init__(self, wires: list[Wire]) -> None:
        self.wires = wires
        self.segments: list[WireSegment] = []
        self._build_segments()

    def _build_segments(self) -> None:
        for wire in self.wires:
            pts = wire.polyline_source_px
            for i in range(len(pts) - 1):
                self.segments.append(WireSegment(wire_id=wire.id, p1=pts[i], p2=pts[i + 1]))

    def find_nearest_endpoint(self, pt: Point, max_dist: float) -> Optional[Tuple[str, Point, float]]:
        """Find the nearest wire endpoint within max_dist.
        Returns (wire_id, endpoint, distance) or None.
        """
        best: Optional[Tuple[str, Point, float]] = None
        best_dist = max_dist

        for wire in self.wires:
            if not wire.polyline_source_px:
                continue
            endpoints = [wire.polyline_source_px[0], wire.polyline_source_px[-1]]
            for ep in endpoints:
                d = math.hypot(pt.x - ep.x, pt.y - ep.y)
                if d < best_dist:
                    best_dist = d
                    best = (wire.id, ep, d)

        return best

    def find_nearest_segment(self, pt: Point, max_dist: float) -> Optional[Tuple[WireSegment, float]]:
        """Find nearest wire segment within max_dist."""
        best: Optional[Tuple[WireSegment, float]] = None
        best_dist = max_dist

        for seg in self.segments:
            d = seg.distance_to_point(pt)
            if d < best_dist:
                best_dist = d
                best = (seg, d)

        return best

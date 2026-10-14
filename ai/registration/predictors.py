"""Domain-specific predicted geometry producers (Phase 5).

Each adapter takes candidate model parameters and produces a PredictedGeometry
at t=0 for comparison against observed source geometry. These are the bridge
between physics models and the InitialRegistrationGate.

No physics equations live here — the adapters call existing solver modules
to generate predicted positions/paths, then format them for the gate.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from shared.schemas.evidence import SourceLine, SourcePoint
from ai.registration.base import PredictedGeometry


class PendulumGeometryPredictor:
    """Predict pendulum geometry at t=0 from model parameters."""

    @staticmethod
    def predict(
        *,
        source_asset_id: str,
        figure_id: str,
        source_width: int,
        source_height: int,
        pivot: Dict[str, float],
        bob_center: Dict[str, float],
        string_length_px: float,
        bob_radius_px: float,
        **kwargs,
    ) -> PredictedGeometry:
        pivot_pt = SourcePoint(x=pivot["x"], y=pivot["y"])
        bob_pt = SourcePoint(x=bob_center["x"], y=bob_center["y"])

        # Predicted string endpoint at bob surface (along pivot->bob direction)
        dx = bob_pt.x - pivot_pt.x
        dy = bob_pt.y - pivot_pt.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            # String ends at bob circumference
            string_end_x = bob_pt.x - (dx / dist) * bob_radius_px
            string_end_y = bob_pt.y - (dy / dist) * bob_radius_px
        else:
            string_end_x, string_end_y = bob_pt.x, bob_pt.y

        return PredictedGeometry(
            source_asset_id=source_asset_id,
            figure_id=figure_id,
            source_width=source_width,
            source_height=source_height,
            domain="mechanics",
            subtype="pendulum",
            landmarks={
                "pivot": pivot_pt,
                "bob_center": bob_pt,
            },
            lines={
                "string": SourceLine(
                    start=pivot_pt,
                    end=SourcePoint(x=string_end_x, y=string_end_y),
                ),
            },
        )


class ThinLensGeometryPredictor:
    """Predict thin lens ray geometry at t=0 from model parameters."""

    @staticmethod
    def predict(
        *,
        source_asset_id: str,
        figure_id: str,
        source_width: int,
        source_height: int,
        lens_center: Dict[str, float],
        focal_length_px: float,
        object_x: Optional[float] = None,
        object_height_px: Optional[float] = None,
        axis_y: Optional[float] = None,
        **kwargs,
    ) -> PredictedGeometry:
        cx = lens_center["x"]
        cy = lens_center["y"]
        f = focal_length_px
        ay = axis_y if axis_y is not None else cy

        landmarks = {
            "lens_center": SourcePoint(x=cx, y=ay),
            "focal_F1": SourcePoint(x=cx - f, y=ay),
            "focal_F2": SourcePoint(x=cx + f, y=ay),
        }

        lines = {}
        curves = {}

        # Predict object and image positions using thin lens equation
        if object_x is not None and object_height_px is not None:
            u = cx - object_x  # object distance (positive = left of lens)
            if abs(u) > 1e-6 and abs(u - f) > 1e-6:
                v = (u * f) / (u - f)  # image distance
                magnification = -v / u
                image_x = cx + v
                image_height = object_height_px * magnification

                # Object landmarks
                obj_base = SourcePoint(x=object_x, y=ay)
                obj_tip = SourcePoint(x=object_x, y=ay - object_height_px)
                landmarks["object_base"] = obj_base
                landmarks["object_tip"] = obj_tip

                # Image landmarks
                img_base = SourcePoint(x=image_x, y=ay)
                img_tip = SourcePoint(x=image_x, y=ay - image_height)
                landmarks["image_base"] = img_base
                landmarks["image_tip"] = img_tip

                # Principal rays
                # Ray 1: parallel to axis -> through F2
                lines["ray_parallel"] = SourceLine(
                    start=obj_tip,
                    end=SourcePoint(x=cx, y=ay - object_height_px),
                )
                # Ray 2: through F1 -> parallel to axis after lens
                lines["ray_focal"] = SourceLine(
                    start=obj_tip,
                    end=SourcePoint(x=cx, y=ay - object_height_px + (object_height_px * f / u)),
                )

        return PredictedGeometry(
            source_asset_id=source_asset_id,
            figure_id=figure_id,
            source_width=source_width,
            source_height=source_height,
            domain="optics",
            subtype="thin_lens",
            landmarks=landmarks,
            lines=lines,
            curves=curves,
        )


class CircuitGeometryPredictor:
    """Predict circuit topology at t=0 from component graph."""

    @staticmethod
    def predict(
        *,
        source_asset_id: str,
        figure_id: str,
        source_width: int,
        source_height: int,
        topology: Dict[str, List[str]],
        component_centers: Optional[Dict[str, SourcePoint]] = None,
        **kwargs,
    ) -> PredictedGeometry:
        landmarks = {}
        if component_centers:
            landmarks = dict(component_centers)

        return PredictedGeometry(
            source_asset_id=source_asset_id,
            figure_id=figure_id,
            source_width=source_width,
            source_height=source_height,
            domain="circuits",
            subtype="dc_linear",
            landmarks=landmarks,
            topology=topology,
        )


class ProjectileGeometryPredictor:
    """Predict projectile trajectory at t=0 from launch parameters."""

    @staticmethod
    def predict(
        *,
        source_asset_id: str,
        figure_id: str,
        source_width: int,
        source_height: int,
        launch_position: Dict[str, float],
        launch_angle_deg: float,
        pixels_per_meter: float = 25.0,
        launch_speed: float = 20.0,
        gravity: float = 9.80665,
        **kwargs,
    ) -> PredictedGeometry:
        lx = launch_position["x"]
        ly = launch_position["y"]
        angle_rad = math.radians(launch_angle_deg)
        vx = launch_speed * math.cos(angle_rad)
        vy = launch_speed * math.sin(angle_rad)

        landmarks = {"launch_position": SourcePoint(x=lx, y=ly)}
        curves = {}

        # Generate trajectory points in source_px
        if abs(vx) > 1e-6 and gravity > 0:
            # Total flight time
            t_flight = 2 * vy / gravity
            if t_flight > 0:
                n_points = min(200, max(20, int(t_flight * 50)))
                trajectory = []
                for i in range(n_points + 1):
                    t = t_flight * i / n_points
                    px = lx + vx * t * pixels_per_meter
                    # Note: y-axis is inverted in source_px (down is positive)
                    py = ly - (vy * t - 0.5 * gravity * t * t) * pixels_per_meter
                    if 0 <= px <= source_width and 0 <= py <= source_height:
                        trajectory.append(SourcePoint(x=px, y=py))
                if len(trajectory) >= 2:
                    curves["trajectory"] = trajectory

        return PredictedGeometry(
            source_asset_id=source_asset_id,
            figure_id=figure_id,
            source_width=source_width,
            source_height=source_height,
            domain="mechanics",
            subtype="projectile",
            landmarks=landmarks,
            curves=curves,
        )


class RefractionGeometryPredictor:
    """Predict refraction ray geometry at t=0."""

    @staticmethod
    def predict(
        *,
        source_asset_id: str,
        figure_id: str,
        source_width: int,
        source_height: int,
        boundary_y: float,
        normal_x: float,
        n1: float = 1.0,
        n2: float = 1.5,
        incident_angle_deg: Optional[float] = None,
        source_position: Optional[Dict[str, float]] = None,
        **kwargs,
    ) -> PredictedGeometry:
        incidence_pt = SourcePoint(x=normal_x, y=boundary_y)
        landmarks = {"incidence_point": incidence_pt}
        lines = {}

        theta1 = None
        if incident_angle_deg is not None:
            theta1 = incident_angle_deg
        elif source_position is not None:
            dx = normal_x - source_position["x"]
            dy = boundary_y - source_position["y"]
            if abs(dy) > 1e-6:
                theta1 = math.degrees(math.atan2(abs(dx), abs(dy)))
            landmarks["source_position"] = SourcePoint(**source_position)

        if theta1 is not None and 0 <= theta1 < 90:
            # Snell's law
            sin_theta2 = n1 * math.sin(math.radians(theta1)) / n2
            if abs(sin_theta2) <= 1.0:
                theta2 = math.degrees(math.asin(sin_theta2))

                # Incident ray (above boundary, going down)
                ray_len = min(source_width, source_height) * 0.3
                inc_dx = ray_len * math.sin(math.radians(theta1))
                inc_dy = ray_len * math.cos(math.radians(theta1))
                inc_start = SourcePoint(x=normal_x - inc_dx, y=boundary_y - inc_dy)
                lines["incident_ray"] = SourceLine(start=inc_start, end=incidence_pt)

                # Refracted ray (below boundary, going down)
                ref_dx = ray_len * math.sin(math.radians(theta2))
                ref_dy = ray_len * math.cos(math.radians(theta2))
                ref_end = SourcePoint(x=normal_x + ref_dx, y=boundary_y + ref_dy)
                lines["refracted_ray"] = SourceLine(start=incidence_pt, end=ref_end)

                # Normal line
                lines["normal"] = SourceLine(
                    start=SourcePoint(x=normal_x, y=max(0, boundary_y - ray_len * 0.8)),
                    end=SourcePoint(x=normal_x, y=min(source_height, boundary_y + ray_len * 0.8)),
                )

                # Boundary line
                lines["boundary"] = SourceLine(
                    start=SourcePoint(x=0, y=boundary_y),
                    end=SourcePoint(x=float(source_width), y=boundary_y),
                )

        return PredictedGeometry(
            source_asset_id=source_asset_id,
            figure_id=figure_id,
            source_width=source_width,
            source_height=source_height,
            domain="optics",
            subtype="interface_refraction",
            landmarks=landmarks,
            lines=lines,
        )


class PrismGeometryPredictor:
    """Predict prism ray geometry at t=0."""

    @staticmethod
    def predict(
        *,
        source_asset_id: str,
        figure_id: str,
        source_width: int,
        source_height: int,
        vertices: List[Dict[str, float]],
        ray_origin: Optional[Dict[str, float]] = None,
        ray_direction: Optional[Dict[str, float]] = None,
        n: float = 1.52,
        apex_angle_deg: float = 60.0,
        **kwargs,
    ) -> PredictedGeometry:
        landmarks = {}
        curves = {}
        lines = {}

        # Prism polygon as curve
        if vertices and len(vertices) >= 3:
            prism_pts = [SourcePoint(x=v["x"], y=v["y"]) for v in vertices]
            # Close the polygon
            prism_pts.append(prism_pts[0])
            curves["prism_polygon"] = prism_pts

            # Vertex landmarks
            for i, v in enumerate(vertices):
                landmarks[f"vertex_{i}"] = SourcePoint(x=v["x"], y=v["y"])

        if ray_origin is not None:
            landmarks["ray_origin"] = SourcePoint(**ray_origin)

        return PredictedGeometry(
            source_asset_id=source_asset_id,
            figure_id=figure_id,
            source_width=source_width,
            source_height=source_height,
            domain="optics",
            subtype="prism",
            landmarks=landmarks,
            lines=lines,
            curves=curves,
        )


# Registry of domain-specific predictors
GEOMETRY_PREDICTORS = {
    "mechanics/pendulum": PendulumGeometryPredictor,
    "mechanics/projectile": ProjectileGeometryPredictor,
    "optics/thin_lens": ThinLensGeometryPredictor,
    "optics/spherical_mirror": ThinLensGeometryPredictor,  # Same philosophy
    "optics/interface_refraction": RefractionGeometryPredictor,
    "optics/prism": PrismGeometryPredictor,
    "circuits/dc_linear": CircuitGeometryPredictor,
}


def get_predictor(domain: str, subtype: str):
    """Get the geometry predictor for a given domain/subtype."""
    key = f"{domain}/{subtype}"
    return GEOMETRY_PREDICTORS.get(key)

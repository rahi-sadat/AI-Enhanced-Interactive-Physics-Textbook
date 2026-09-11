from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from geometry_utils import GeometryBundle


@dataclass
class CanvasMapper:
    source_width: int
    source_height: int
    target_width: int = 800
    target_height: int = 600

    def __post_init__(self) -> None:
        self.scale = min(
            self.target_width / self.source_width,
            self.target_height / self.source_height,
        )
        rendered_w = self.source_width * self.scale
        rendered_h = self.source_height * self.scale
        self.offset_x = (self.target_width - rendered_w) / 2.0
        self.offset_y = (self.target_height - rendered_h) / 2.0

    def point(self, x: float, y: float) -> Dict[str, float]:
        return {
            "x": float(x * self.scale + self.offset_x),
            "y": float(y * self.scale + self.offset_y),
        }

    def length(self, value: float) -> float:
        return float(value * self.scale)

    def vertices(self, points: Iterable[Dict[str, float]]) -> List[Dict[str, float]]:
        return [self.point(p["x"], p["y"]) for p in points]

    def metadata(self) -> dict:
        return {
            "canvas_width_px": self.target_width,
            "canvas_height_px": self.target_height,
            "source_to_canvas_scale": self.scale,
            "offset_x_px": self.offset_x,
            "offset_y_px": self.offset_y,
            "preserve_aspect_ratio": True,
        }


class SceneBuilder:
    """Build a domain-neutral scene first; do not let Matter.js define perception."""

    def __init__(
        self,
        image_path: Path,
        image_width: int,
        image_height: int,
        target_width: int = 800,
        target_height: int = 600,
    ) -> None:
        self.image_path = Path(image_path)
        self.mapper = CanvasMapper(image_width, image_height, target_width, target_height)
        self.elements: List[dict] = []
        self.warnings: List[str] = []

    def add_element(
        self,
        geometry: GeometryBundle,
        author_role: str,
        prompt_points: Sequence[Tuple[float, float]],
        prompt_labels: Sequence[int],
        quality: dict,
        mask_path: str,
        semantic_label: str | None = None,
        sprite_info: dict | None = None,
    ) -> dict:
        element_id = f"element_{len(self.elements) + 1:03d}"
        cx, cy = geometry.centroid_px

        element = {
            "id": element_id,
            "kind": "segmented_region",
            "semantic_label": semantic_label,
            "author_role": author_role,
            "geometry": {
                "source_px": geometry.to_dict(),
                "render": {
                    "centroid": self.mapper.point(cx, cy),
                    "polygon": self.mapper.vertices(geometry.polygon_px),
                    "convex_collision_polygon": self.mapper.vertices(
                        geometry.convex_collision_polygon_px
                    ),
                    "skeleton_polyline": self.mapper.vertices(geometry.skeleton_polyline_px),
                    "oriented_bbox": {
                        "center": self.mapper.point(cx, cy),
                        "width": self.mapper.length(geometry.oriented_bbox_px["width"]),
                        "height": self.mapper.length(geometry.oriented_bbox_px["height"]),
                        "angle_deg": geometry.oriented_bbox_px["angle_deg"],
                    },
                    "circle_fit": {
                        "center": self.mapper.point(
                            geometry.circle_fit_px["center_x"],
                            geometry.circle_fit_px["center_y"],
                        ),
                        "equivalent_radius": self.mapper.length(
                            geometry.circle_fit_px["equivalent_radius"]
                        ),
                        "enclosing_radius": self.mapper.length(
                            geometry.circle_fit_px["enclosing_radius"]
                        ),
                    },
                },
            },
            "visual": {
                "mask_path": mask_path,
                "sprite_path": sprite_info.get("sprite_path") if sprite_info else None,
                "sprite_width_px": sprite_info.get("width") if sprite_info else None,
                "sprite_height_px": sprite_info.get("height") if sprite_info else None,
                "sprite_url": sprite_info.get("sprite_url") if sprite_info else None,
            },
            "physics": {
                # These are intentionally unresolved here. Segmentation cannot infer them.
                "body_mode": author_role if author_role in {"dynamic", "static"} else "unknown",
                "mass_kg": None,
                "friction": None,
                "restitution": None,
                "initial_velocity_m_s": None,
                "initial_angular_velocity_rad_s": None,
            },
            "perception": {
                "segmenter": "sam2",
                "prompt": {
                    "points_source_px": [
                        {"x": float(x), "y": float(y), "label": int(label)}
                        for (x, y), label in zip(prompt_points, prompt_labels)
                    ]
                },
                "mask_quality": quality,
                "human_confirmed_mask": True,
            },
        }
        self.elements.append(element)
        return element

    def build(self) -> dict:
        return {
            "schema_version": "2.0",
            "scene_type": "physics_diagram",
            "source": {
                "image": self.image_path.as_posix(),
                "image_width_px": self.mapper.source_width,
                "image_height_px": self.mapper.source_height,
            },
            "coordinate_system": {
                "source": {
                    "origin": "top_left",
                    "x_direction": "right",
                    "y_direction": "down",
                    "unit": "px",
                },
                "render": self.mapper.metadata(),
                "physical_scale": {
                    "pixels_per_meter": None,
                    "status": "unresolved_until_text_or_known_length_is_bound",
                },
            },
            "simulation": {
                "domain": "unknown",
                "engine": "auto",
                "supported_domain_candidates": [
                    "kinematics",
                    "dynamics",
                    "collisions",
                    "springs_constraints",
                    "pendulum",
                    "optics",
                    "circuits",
                    "animation_path",
                    "generic",
                ],
            },
            "environment": {
                "gravity_m_s2": None,
                "gravity_direction": None,
            },
            "elements": self.elements,
            "relations": [],
            "parameters": [],
            "bindings": [],
            "warnings": self.warnings,
        }

    def write(self, output_path: Path) -> dict:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        scene = self.build()
        output_path.write_text(json.dumps(scene, indent=2), encoding="utf-8")
        return scene


def _looks_circle(geometry: dict) -> bool:
    hints = geometry["source_px"]["shape_hints"]
    return hints["circularity"] >= 0.78 and hints["circle_fill_ratio"] >= 0.72


def _looks_long_rectangle(geometry: dict) -> bool:
    hints = geometry["source_px"]["shape_hints"]
    return hints["aspect_ratio"] >= 3.0 and hints["rectangularity"] >= 0.65


def _looks_spring(geometry: dict) -> bool:
    hints = geometry["source_px"]["shape_hints"]
    bbox = geometry["source_px"]["oriented_bbox_px"]
    aspect = bbox["width"] / max(1.0, bbox["height"])
    return 1.4 <= aspect <= 3.5 and hints["circularity"] < 0.45 and hints["circle_fill_ratio"] < 0.45


def export_matterjs_compat(
    scene_v2: dict,
    output_path: Path,
    background_url: str | None = "/physics_scene.png",
) -> dict:
    """Temporary adapter for the friend's existing JSON loader.

    The canonical v2 scene remains generic. This adapter only exports elements whose
    body mode is already known as dynamic/static. Unknown semantics are not invented.
    """
    render_meta = scene_v2["coordinate_system"]["render"]
    objects = []
    warnings = []

    for element in scene_v2["elements"]:
        semantic_label = element.get("semantic_label")
        role = element["physics"]["body_mode"]
        visual_info = element.get("visual", {})
        sprite_url = visual_info.get("sprite_url")
        sprite_w = visual_info.get("sprite_width_px")
        sprite_h = visual_info.get("sprite_height_px")

        geometry = element["geometry"]
        center = geometry["render"]["centroid"]

        # ----------------------------------------------------
        # 1. SPECIAL CASE: SPRING
        # (Accept if marked 'spring', OR if labeled unknown but looks like a spring)
        # ----------------------------------------------------
        if semantic_label == "spring" or (role == "unknown" and _looks_spring(geometry)):
            box = geometry["render"]["oriented_bbox"]
            box_center = box["center"]
            width = box["width"]
            height = box["height"]

            free_x = box_center["x"] - width / 2.0
            anchor_x = box_center["x"] + width / 2.0

            objects.append({
                "id": element["id"],
                "type": "spring",
                "free_point": {
                    "x": free_x,
                    "y": box_center["y"],
                },
                "anchor_point": {
                    "x": anchor_x,
                    "y": box_center["y"],
                },
                "plunger_size": {
                    "width": 12.0,
                    "height": max(40.0, height + 10.0),
                },
                "stiffness": 0.04,
                "damping": 0.05,
                "plunger_mass": 0.5,
            })
            continue

        # For normal rigid bodies, require known dynamic or static role
        if role not in {"dynamic", "static"}:
            warnings.append(f"Skipped {element['id']}: body mode unresolved")
            continue

        obj = {
            "id": element["id"],
            "role": role,
            "initial_position": center,
        }

        # ----------------------------------------------------
        # 2. SPECIAL CASE: TRACK / CURVED RAMP
        # (Preserve full polygon contour as an invisible static collider)
        # ----------------------------------------------------
        if semantic_label == "track" or (role == "static" and not _looks_circle(geometry) and not _looks_long_rectangle(geometry)):
            obj["type"] = "polygon"
            obj["vertices"] = geometry["render"]["polygon"]
            obj["friction"] = 0.10
            obj["restitution"] = 0.02
            # Invisible collider so underlying textbook diagram is visible directly
            obj["render"] = {"visible": False}
            objects.append(obj)
            continue

        # ----------------------------------------------------
        # 3. BALL / DYNAMIC CIRCLE (Rolling + Sprite attachment)
        # ----------------------------------------------------
        if semantic_label == "ball" or _looks_circle(geometry):
            obj["type"] = "circle"
            radius = geometry["render"]["circle_fit"]["equivalent_radius"]
            obj["radius"] = radius
            if role == "dynamic":
                obj["mass_kg"] = 1.0
                # Gentle push to trigger natural rolling down the curvature
                obj["initial_velocity"] = {"x": 0.35, "y": 0.0}
                obj["friction"] = 0.08
                obj["restitution"] = 0.05
            
            if sprite_url and sprite_w and sprite_h:
                target_diam = 2.0 * radius
                obj["visual"] = {
                    "sprite_url": sprite_url,
                    "x_scale": float(target_diam / sprite_w),
                    "y_scale": float(target_diam / sprite_h),
                }
            objects.append(obj)
            continue

        if role == "dynamic":
            obj["mass_kg"] = 1.0
            obj["initial_velocity"] = {"x": 0.0, "y": 0.0}

        if role == "static":
            # Other static objects like ground/walls act as invisible colliders over diagram
            obj["render"] = {"visible": False}

        if role == "static" and _looks_long_rectangle(geometry):
            angle = float(geometry["render"]["oriented_bbox"]["angle_deg"])
            obj["type"] = "ground" if abs(angle) <= 7.0 else "inclined_plane"
            obj["size"] = {
                "width": geometry["render"]["oriented_bbox"]["width"],
                "height": max(4.0, geometry["render"]["oriented_bbox"]["height"]),
            }
            if obj["type"] == "inclined_plane":
                obj["angle"] = angle
        else:
            obj["type"] = "polygon"
            obj["vertices"] = geometry["render"]["convex_collision_polygon"]

        if role == "dynamic" and sprite_url and sprite_w and sprite_h:
            box = geometry["render"]["oriented_bbox"]
            obj["visual"] = {
                "sprite_url": sprite_url,
                "x_scale": float(box["width"] / sprite_w),
                "y_scale": float(box["height"] / sprite_h),
            }

        objects.append(obj)

    compat = {
        "schema_version": "1.0-compat",
        "simulation_type": "kinematics",
        "visual": {
            "background_url": background_url,
        },
        "environment": {"gravity": 1.0},
        "objects": objects,
        "adapter_warnings": warnings,
        "source_schema_version": scene_v2.get("schema_version"),
        "render": render_meta,
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(compat, indent=2), encoding="utf-8")
    return compat

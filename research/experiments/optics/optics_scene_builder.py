"""
experiments/optics/optics_scene_builder.py
Generates the canonical PhysicsScene (schema_version 2.0) for optics diagrams.
Preserves perception facts, uncertainty, and provenance.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional


class OpticsSceneBuilder:
    def __init__(
        self,
        image_path: Optional[Path | str],
        image_width: int = 800,
        image_height: int = 600,
        canvas_width: int = 800,
        canvas_height: int = 600,
        subtype: str = "thin_lens",
    ):
        self.image_path = str(image_path) if image_path else None
        self.image_width = image_width
        self.image_height = image_height
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.subtype = subtype

        self.elements: List[dict] = []
        self.annotations: List[dict] = []
        self.calibration: Optional[dict] = None
        self.provenance_records: Dict[str, dict] = {}

    def set_calibration(self, calib: Optional[dict]) -> None:
        self.calibration = calib

    def add_lens(
        self,
        optical_center: Dict[str, float],
        aperture_height_px: float,
        focal_length_px: float | dict,
        element_id: str = "lens_001",
        semantic_label: str = "convex_lens",
        focal_length_cm: Optional[float | dict] = None,
    ) -> dict:
        optics_data = {
            "model": "thin_lens",
            "focal_length_px": focal_length_px,
        }
        if focal_length_cm is not None:
            optics_data["focal_length_cm"] = focal_length_cm

        element = {
            "id": element_id,
            "semantic_label": semantic_label,
            "author_role": "static",
            "geometry": {
                "optical_center": {
                    "x": round(optical_center["x"], 1),
                    "y": round(optical_center["y"], 1),
                },
                "aperture_height_px": round(aperture_height_px, 1),
            },
            "optics": optics_data,
        }
        self.elements.append(element)
        return element

    def add_object_arrow(
        self,
        position: Dict[str, float],
        height_px: float,
        element_id: str = "object_001",
        semantic_label: str = "object_arrow",
        sprite_url: Optional[str] = None,
    ) -> dict:
        element = {
            "id": element_id,
            "semantic_label": semantic_label,
            "author_role": "dynamic",
            "geometry": {
                "position": {
                    "x": round(position["x"], 1),
                    "y": round(position["y"], 1),
                },
                "height_px": round(height_px, 1),
            },
        }
        if sprite_url:
            element["visual"] = {"sprite_url": sprite_url}

        self.elements.append(element)
        return element

    def add_prism(
        self,
        vertices: List[Dict[str, float]],
        refractive_index: float | dict = 1.52,
        element_id: str = "prism_001",
    ) -> dict:
        element = {
            "id": element_id,
            "semantic_label": "prism",
            "author_role": "static",
            "geometry": {
                "vertices": [{"x": round(v["x"], 1), "y": round(v["y"], 1)} for v in vertices],
            },
            "optics": {
                "refractive_index": refractive_index,
            },
        }
        self.elements.append(element)
        return element

    def add_annotations(self, annotations: List[dict]) -> None:
        for ann in annotations:
            self.annotations.append({
                "label": ann.get("label", ""),
                "position": {
                    "x": round(ann["position"]["x"], 1),
                    "y": round(ann["position"]["y"], 1),
                },
            })

    def build_scene(self) -> dict:
        scale = min(self.canvas_width / self.image_width, self.canvas_height / self.image_height)

        scene = {
            "schema_version": "2.0",
            "scene_type": "physics_diagram",
            "source": {
                "image": self.image_path,
                "image_width_px": self.image_width,
                "image_height_px": self.image_height,
            },
            "coordinate_system": {
                "render": {
                    "canvas_width_px": self.canvas_width,
                    "canvas_height_px": self.canvas_height,
                    "source_to_canvas_scale": round(scale, 4),
                },
            },
            "simulation": {
                "domain": "optics",
                "subtype": self.subtype,
                "engine": "optics2d",
            },
            "visual": {
                "background_url": self.image_path,
            },
            "elements": self.elements,
            "annotations": self.annotations,
        }

        if self.calibration:
            scene["coordinate_system"]["calibration"] = {
                "pixels_per_cm": self.calibration,
            }

        return scene

    def export_json(self, output_path: Path | str, indent: int = 2) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        scene = self.build_scene()
        with open(out, "w", encoding="utf-8") as f:
            json.dump(scene, f, indent=indent)
        return out

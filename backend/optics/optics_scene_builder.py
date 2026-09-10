"""Optics PhysicsScene v2.1 builder.

Extends the core SceneBuilder pattern for optics diagrams. Produces a
PhysicsScene with simulation.domain = "optics" and optics-specific element
blocks, while reusing CanvasMapper for coordinate mapping.

Key differences from the mechanics SceneBuilder:
  - Elements carry an .optics block with model-specific parameters.
  - An .annotations array stores F, 2F, O label positions.
  - physical_scale tracks pixel-to-cm calibration with provenance.
  - export_optics_compat() produces frontend-consumable optics JSON.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# Ensure backend/core is on the path.
_BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BACKEND_DIR / "core"))

from geometry_utils import GeometryBundle                 # noqa: E402
from scene_builder import CanvasMapper                    # noqa: E402
try:
    from .optics_text import FocalPointSet, PixelScale
    from .optics_registry import get_preset
except ImportError:
    from optics_text import FocalPointSet, PixelScale
    from optics_registry import get_preset



class OpticsSceneBuilder:
    """Builds PhysicsScene v2.1 for optics diagrams.

    Mirrors SceneBuilder's interface but adds:
      - simulation.domain = "optics", simulation.subtype, simulation.engine
      - elements carry .optics block with model-specific parameters
      - annotations array for F / 2F / O labels with positions
      - physical_scale with provenance tracking
    """

    def __init__(
        self,
        image_path: Path,
        image_width: int,
        image_height: int,
        domain_subtype: str = "thin_lens",
        target_width: int = 800,
        target_height: int = 600,
    ) -> None:
        self.image_path = Path(image_path)
        self.mapper = CanvasMapper(image_width, image_height, target_width, target_height)
        self.domain_subtype = domain_subtype
        self.elements: List[dict] = []
        self.annotations: List[dict] = []
        self.warnings: List[str] = []
        self.focal_data: Optional[FocalPointSet] = None
        self.pixel_scale: PixelScale = PixelScale()
        self.physical_values: Dict[str, Optional[float]] = {}

    # ------------------------------------------------------------------
    # Add elements
    # ------------------------------------------------------------------

    def _base_element(
        self,
        geometry: GeometryBundle,
        author_role: str,
        prompt_points: Sequence[Tuple[float, float]],
        prompt_labels: Sequence[int],
        quality: dict,
        mask_path: str,
        semantic_label: str,
        sprite_info: Optional[dict] = None,
    ) -> dict:
        """Construct the shared element skeleton (same structure as mechanics)."""
        element_id = f"element_{len(self.elements) + 1:03d}"
        cx, cy = geometry.centroid_px

        return {
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

    def add_lens(
        self,
        geometry: GeometryBundle,
        optics_geometry: dict,
        author_role: str,
        prompt_points: Sequence[Tuple[float, float]],
        prompt_labels: Sequence[int],
        quality: dict,
        mask_path: str,
        semantic_label: str = "convex_lens",
        sprite_info: Optional[dict] = None,
    ) -> dict:
        """Add a lens element with optical parameters."""
        element = self._base_element(
            geometry, author_role, prompt_points, prompt_labels,
            quality, mask_path, semantic_label, sprite_info,
        )

        oc = optics_geometry.get("optical_center", {})
        render_oc = self.mapper.point(oc.get("x", 0), oc.get("y", 0))

        element["optics"] = {
            "model": "thin_lens",
            "optical_center": render_oc,
            "aperture_height_px": self.mapper.length(
                optics_geometry.get("aperture_height_px", 0)
            ),
            "focal_length_px": None,  # Set later via set_focal_points()
        }

        self.elements.append(element)
        return element

    def add_optical_object(
        self,
        geometry: GeometryBundle,
        arrow_geometry: dict,
        author_role: str,
        prompt_points: Sequence[Tuple[float, float]],
        prompt_labels: Sequence[int],
        quality: dict,
        mask_path: str,
        semantic_label: str = "object_arrow",
        sprite_info: Optional[dict] = None,
    ) -> dict:
        """Add an optical object (arrow, candle, tree) with base/tip geometry."""
        element = self._base_element(
            geometry, author_role, prompt_points, prompt_labels,
            quality, mask_path, semantic_label, sprite_info,
        )

        base = arrow_geometry.get("base", {})
        tip = arrow_geometry.get("tip", {})
        render_base = self.mapper.point(base.get("x", 0), base.get("y", 0))
        render_tip = self.mapper.point(tip.get("x", 0), tip.get("y", 0))

        element["optics"] = {
            "model": "optical_object",
            "base": render_base,
            "tip": render_tip,
            "height_px": abs(render_tip["y"] - render_base["y"]),
        }

        self.elements.append(element)
        return element

    def add_prism(
        self,
        geometry: GeometryBundle,
        prism_geometry: dict,
        author_role: str,
        prompt_points: Sequence[Tuple[float, float]],
        prompt_labels: Sequence[int],
        quality: dict,
        mask_path: str,
        refractive_index: Optional[float] = None,
        sprite_info: Optional[dict] = None,
    ) -> dict:
        """Add a prism element with vertices and refractive index."""
        element = self._base_element(
            geometry, author_role, prompt_points, prompt_labels,
            quality, mask_path, "prism", sprite_info,
        )

        raw_verts = prism_geometry.get("vertices", [])
        render_verts = self.mapper.vertices(raw_verts)

        element["optics"] = {
            "model": "refractive_polygon",
            "vertices": render_verts,
            "apex_angle_deg": prism_geometry.get("apex_angle_deg"),
            "refractive_index": {
                "value": refractive_index,
                "source": "author_manual" if refractive_index is not None else None,
                "status": "resolved" if refractive_index is not None else "unresolved",
            },
        }

        self.elements.append(element)
        return element

    def add_mirror(
        self,
        geometry: GeometryBundle,
        mirror_geometry: dict,
        author_role: str,
        prompt_points: Sequence[Tuple[float, float]],
        prompt_labels: Sequence[int],
        quality: dict,
        mask_path: str,
        semantic_label: str = "concave_mirror",
        sprite_info: Optional[dict] = None,
    ) -> dict:
        """Add a mirror element with curvature parameters."""
        element = self._base_element(
            geometry, author_role, prompt_points, prompt_labels,
            quality, mask_path, semantic_label, sprite_info,
        )

        pole = mirror_geometry.get("pole", {})
        render_pole = self.mapper.point(pole.get("x", 0), pole.get("y", 0))

        cur_r = mirror_geometry.get("curvature_radius_px")

        element["optics"] = {
            "model": "spherical_mirror",
            "pole": render_pole,
            "aperture_height_px": self.mapper.length(
                mirror_geometry.get("aperture_height_px", 0)
            ),
            "curvature_radius_px": self.mapper.length(cur_r) if cur_r else None,
            "concavity": mirror_geometry.get("concavity", "unknown"),
            "focal_length_px": self.mapper.length(cur_r / 2.0) if cur_r else None,
        }

        self.elements.append(element)
        return element

    def add_generic_element(
        self,
        geometry: GeometryBundle,
        author_role: str,
        prompt_points: Sequence[Tuple[float, float]],
        prompt_labels: Sequence[int],
        quality: dict,
        mask_path: str,
        semantic_label: Optional[str] = None,
        sprite_info: Optional[dict] = None,
    ) -> dict:
        """Add a non-specialised optical element (screen, light source, etc.)."""
        element = self._base_element(
            geometry, author_role, prompt_points, prompt_labels,
            quality, mask_path, semantic_label or "unknown", sprite_info,
        )

        preset = get_preset(semantic_label) if semantic_label else None
        element["optics"] = {
            "model": preset["physics_type"] if preset else "generic",
        }

        self.elements.append(element)
        return element

    # ------------------------------------------------------------------
    # Annotations & calibration
    # ------------------------------------------------------------------

    def set_focal_points(self, focal_data: FocalPointSet) -> None:
        """Register F / 2F annotation positions from optics_text results."""
        self.focal_data = focal_data

        # Build annotations list
        label_map = [
            ("F1", focal_data.F1),
            ("F2", focal_data.F2),
            ("2F1", focal_data.TwoF1),
            ("2F2", focal_data.TwoF2),
        ]
        for label_text, pos in label_map:
            if pos is not None:
                self.annotations.append({
                    "label": label_text,
                    "position": self.mapper.point(pos["x"], pos["y"]),
                    "source_position": pos,
                })

        # Propagate focal length to lens elements
        if focal_data.focal_length_px is not None:
            render_fl = self.mapper.length(focal_data.focal_length_px)
            for el in self.elements:
                if el.get("optics", {}).get("model") == "thin_lens":
                    el["optics"]["focal_length_px"] = {
                        "value": render_fl,
                        "source": focal_data.focal_length_source,
                        "confidence": focal_data.focal_length_confidence,
                    }

    def set_physical_scale(self, scale: PixelScale) -> None:
        """Set pixel-to-physical calibration."""
        self.pixel_scale = scale

    def set_physical_value(self, key: str, value: Optional[float]) -> None:
        """Store a manually-entered physical value (e.g. focal_length_cm)."""
        self.physical_values[key] = value

    def add_annotation(self, label: str, x: float, y: float) -> None:
        """Add a custom annotation point (e.g. 'O' for optical center)."""
        self.annotations.append({
            "label": label,
            "position": self.mapper.point(x, y),
            "source_position": {"x": x, "y": y},
        })

    # ------------------------------------------------------------------
    # Build & export
    # ------------------------------------------------------------------

    def build(self) -> dict:
        """Build the complete PhysicsScene v2.1 dict."""
        physical_scale_dict = self.pixel_scale.to_dict() if self.pixel_scale else {
            "pixels_per_cm": None,
            "status": "unresolved",
        }

        return {
            "schema_version": "2.1",
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
                "physical_scale": physical_scale_dict,
            },
            "simulation": {
                "domain": "optics",
                "subtype": self.domain_subtype,
                "engine": "optics2d",
            },
            "elements": self.elements,
            "annotations": self.annotations,
            "physical_values": {
                k: {"value": v, "source": "author_manual"}
                for k, v in self.physical_values.items()
                if v is not None
            },
            "relations": [],
            "bindings": [],
            "warnings": self.warnings,
        }

    def write(self, output_path: Path) -> dict:
        """Write PhysicsScene v2.1 JSON to disk."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        scene = self.build()
        output_path.write_text(json.dumps(scene, indent=2), encoding="utf-8")
        return scene

    def export_optics_compat(
        self,
        output_path: Path,
        background_url: Optional[str] = "/physics_scene.png",
    ) -> dict:
        """Export frontend-compatible optics scene JSON.

        Analogous to export_matterjs_compat() but for domain=optics:
          - Resolves focal_length_px from annotations or explicit value
          - Computes object position relative to lens center
          - Sets sensible defaults with provenance flags
        """
        scene = self.build()
        render_meta = scene["coordinate_system"]["render"]

        compat = {
            "schema_version": "2.1-optics-compat",
            "simulation": scene["simulation"],
            "visual": {
                "background_url": background_url,
            },
            "elements": scene["elements"],
            "annotations": scene["annotations"],
            "physical_values": scene.get("physical_values", {}),
            "physical_scale": scene["coordinate_system"]["physical_scale"],
            "render": render_meta,
            "warnings": self.warnings,
            "source_schema_version": "2.1",
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(compat, indent=2), encoding="utf-8")
        return compat

"""
Unit tests for AugmentedPhysics Optics Precision backend modules:
- optics_text.py: project_distance_on_axis, infer_focal_length_px
- optics_scene_builder.py: source_px coordinate systems and provenance records
- server.py: build_*_scene builders retaining source dimensions and provenance
"""
import math
import sys
import os

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from ai.document_intelligence.parsing.optics_text import (
        project_distance_on_axis,
        infer_focal_length_px,
        classify_focal_points,
        FocalPointSet,
    )
    from ai.scene_compiler.optics_scene_builder import OpticsSceneBuilder
    from apps.api.main import (
        build_thin_lens_scene,
        build_mirror_scene,
        build_prism_scene,
        build_interface_refraction_scene,
    )
except ImportError:
    from backend.optics.optics_text import (
        project_distance_on_axis,
        infer_focal_length_px,
        classify_focal_points,
        FocalPointSet,
    )
    from backend.optics.optics_scene_builder import OpticsSceneBuilder
    from backend.server import (
        build_thin_lens_scene,
        build_mirror_scene,
        build_prism_scene,
        build_interface_refraction_scene,
    )


def test_project_distance_on_axis():
    print("Testing project_distance_on_axis...")
    # Horizontal axis (0 deg)
    origin = {"x": 400.0, "y": 300.0}
    pt = {"x": 550.0, "y": 300.0}
    d = project_distance_on_axis(pt, origin, 0.0)
    assert abs(d - 150.0) < 1e-4, f"Expected 150, got {d}"

    # Diagonal axis (45 deg)
    pt_diag = {"x": 400.0 + 100.0 * math.cos(math.pi / 4), "y": 300.0 + 100.0 * math.sin(math.pi / 4)}
    d_diag = project_distance_on_axis(pt_diag, origin, 45.0)
    assert abs(d_diag - 100.0) < 1e-4, f"Expected 100, got {d_diag}"
    print("  [OK] project_distance_on_axis passed")


def test_infer_focal_length_px():
    print("Testing infer_focal_length_px...")
    origin = {"x": 400.0, "y": 300.0}
    F1 = {"x": 250.0, "y": 300.0}       # d = 150
    F2 = {"x": 550.0, "y": 300.0}       # d = 150
    TwoF1 = {"x": 100.0, "y": 300.0}    # d = 300 -> f = 150
    TwoF2 = {"x": 700.0, "y": 300.0}    # d = 300 -> f = 150

    res = infer_focal_length_px(origin, F1, F2, TwoF1, TwoF2, axis_angle_deg=0.0)
    assert res is not None, "Expected valid result"
    assert abs(res["focal_length_px"] - 150.0) < 1e-4, f"Expected 150, got {res['focal_length_px']}"
    assert res["status"] in ("observed", "derived"), f"Expected observed or derived, got {res['status']}"
    assert res["confidence"] >= 0.9, f"Expected high confidence, got {res['confidence']}"
    assert res["uncertainty"] == 0.0, f"Expected 0 uncertainty for perfect match, got {res['uncertainty']}"
    print("  [OK] infer_focal_length_px perfect symmetry passed")

    # Partial points test (only F1 and TwoF1 with slight measurement noise)
    res_partial = infer_focal_length_px(origin, F1={"x": 248.0, "y": 300.0}, TwoF1={"x": 102.0, "y": 300.0})
    assert res_partial is not None
    assert abs(res_partial["focal_length_px"] - 150.5) < 2.0
    assert res_partial["uncertainty"] > 0.0
    print("  [OK] infer_focal_length_px partial noisy passed")


def test_optics_scene_builder():
    print("Testing OpticsSceneBuilder source_px and provenance...")
    builder = OpticsSceneBuilder("test.png", 1024, 768)
    
    # Test setting focal points from FocalPointSet
    focal_data = FocalPointSet(
        focal_length_px=150.0,
        focal_length_source="annotations",
        focal_length_confidence=0.95,
        F1={"x": 362.0, "y": 384.0},
        F2={"x": 662.0, "y": 384.0},
        TwoF1={"x": 212.0, "y": 384.0},
        TwoF2={"x": 812.0, "y": 384.0},
    )
    builder.set_focal_points(focal_data)
    builder.add_annotation("O", 512.0, 384.0)

    scene = builder.build()
    assert scene["schema_version"] == "2.1"
    assert scene["source"]["image_width_px"] == 1024
    assert scene["source"]["image_height_px"] == 768
    assert len(scene["annotations"]) == 5  # F1, F2, 2F1, 2F2, O

    # Verify source_position in annotations retains exact source pixels
    ann_map = {a["label"]: a for a in scene["annotations"]}
    assert ann_map["F1"]["source_position"]["x"] == 362.0
    assert ann_map["F2"]["source_position"]["x"] == 662.0
    assert ann_map["O"]["source_position"]["x"] == 512.0
    print("  [OK] OpticsSceneBuilder passed")


def test_server_scene_builders():
    print("Testing server.py build_*_scene functions...")
    import numpy as np
    # White textbook page
    img_bgr = np.full((900, 1200, 3), 255, dtype=np.uint8)
    # Draw optical axis line across y=450
    img_bgr[449:452, :] = 0
    # Draw lens line along x=600, y in [250, 650]
    img_bgr[250:650, 598:603] = 0
    image_rel_url = "/uploads/test.png"

    # 1. Thin lens
    lens_scene = build_thin_lens_scene(img_bgr, image_rel_url, focal_length_cm=20.0, model="convex")
    assert lens_scene["schema_version"] == "3.0-optics"
    assert lens_scene["coordinate_system"]["geometry_space"] == "source_px"
    assert lens_scene["render"]["source_width_px"] == 1200
    assert lens_scene["render"]["source_height_px"] == 900

    lens_elem = next(e for e in lens_scene["elements"] if e["optics"]["model"] == "thin_lens")
    assert lens_elem["optics"]["coordinate_space"] == "source_px"
    print("Detected lens optical center:", lens_elem["optics"]["optical_center"])
    assert abs(lens_elem["optics"]["optical_center"]["x"] - 600.0) <= 2.0

    # 2. Mirror
    mirror_scene = build_mirror_scene(img_bgr, image_rel_url, mirror_type="concave")
    assert mirror_scene["schema_version"] == "3.0-optics"
    assert mirror_scene["coordinate_system"]["geometry_space"] == "source_px"
    assert mirror_scene["render"]["source_width_px"] == 1200
    mirror_elem = next(e for e in mirror_scene["elements"] if e["optics"]["model"] in ("concave", "convex"))
    assert mirror_elem["optics"]["coordinate_space"] == "source_px"

    # 3. Prism
    prism_scene = build_prism_scene(img_bgr, image_rel_url)
    assert prism_scene["schema_version"] == "3.0-optics"
    assert prism_scene["coordinate_system"]["geometry_space"] == "source_px"
    assert prism_scene["render"]["source_width_px"] == 1200
    prism_elem = next(e for e in prism_scene["elements"] if e["optics"]["model"] == "refractive_polygon")
    assert len(prism_elem["optics"]["vertices"]) == 3
    assert prism_elem["optics"]["refractive_index"]["value"] == 1.52

    # 4. Interface refraction
    interface_scene = build_interface_refraction_scene(img_bgr, image_rel_url)
    assert interface_scene["schema_version"] == "3.0-optics"
    assert interface_scene["coordinate_system"]["geometry_space"] == "source_px"
    assert interface_scene["render"]["source_width_px"] == 1200
    interface_elem = next(e for e in interface_scene["elements"] if e["optics"]["model"] == "interface_boundary")
    assert interface_elem["optics"]["boundary"]["p1"]["x"] == 0.0
    assert interface_elem["optics"]["boundary"]["p2"]["x"] == 1200.0

    print("  [OK] server.py scene builders passed")


if __name__ == "__main__":
    test_project_distance_on_axis()
    test_infer_focal_length_px()
    test_optics_scene_builder()
    test_server_scene_builders()
    print("\n==============================================")
    print("  ALL BACKEND OPTICS PRECISION TESTS PASSED!  ")
    print("==============================================")

"""Offline pixel-variation benchmark of grounding through scene compilation.

Semantic labels are injected through MockVisionProvider. Reported success is
conditional on the correct subtype being supplied; classification is unmeasured.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
from sys import path as sys_path
if str(ROOT) not in sys_path:
    sys_path.insert(0, str(ROOT))

from scripts.benchmark_phase2 import run_case
from engine.circuits.mna_solver import MNASolver
from shared.schemas.circuit_models import CircuitScene, Component, Node, Parameter, Point, Terminal


def circuit_metrics(scene: dict) -> dict:
    graph = scene.get("circuit") or {}
    components = graph.get("components") or []
    nodes = graph.get("nodes") or []
    signature = []
    for first_index, first in enumerate(components):
        for second in components[first_index + 1:]:
            if first.get("nodes") and second.get("nodes"):
                shared = len(set(first["nodes"]) & set(second["nodes"]))
                a, b = sorted((first["id"], second["id"]))
                signature.append((a, b, shared))
    signature.sort()
    typed = []
    for item in components:
        kind = item.get("type")
        unit_key = "voltage_v" if kind in {"voltage_source", "battery", "dc_source"} else "resistance_ohm"
        raw_terms = item.get("terminals") or []
        terms = [Terminal(id=term.get("id", f"{item['id']}.t{index}"),
                          position=Point(*term.get("source_px", [0, 0])),
                          node=term.get("node"))
                 for index, term in enumerate(raw_terms)]
        box = (item.get("geometry") or {}).get("bbox_source_px") or [0, 0, 0, 0]
        typed.append(Component(id=item["id"], type="voltage_source" if kind in {"battery", "dc_source"} else kind,
                               terminals=terms, bbox_source_px=box,
                               parameters={unit_key: Parameter(value=float(item["value"]),
                                                               unit="V" if unit_key == "voltage_v" else "ohm")}))
    dimensions = scene.get("coordinateSpace") or {}
    circuit = CircuitScene(source_width=int(dimensions["width"]),
                           source_height=int(dimensions["height"]),
                           reference_node=graph.get("reference_node") or nodes[0]["id"],
                           nodes=[Node(id=node["id"], reference=node["id"] == graph.get("reference_node"))
                                  for node in nodes], components=typed)
    state = MNASolver(circuit).solve_dc()
    finite = all(np.isfinite(value) for value in state.node_voltages.values())
    residual = max((abs(value) for value in state.kcl_residuals.values()), default=0.0)
    return {"components": len(components), "nodes": len(nodes),
            "connectivity_signature": signature, "solver_status": state.status,
            "finite_node_voltages": bool(finite), "max_kcl_residual_a": residual}


def variants(image: np.ndarray):
    height, width = image.shape[:2]
    for scale in (0.75, 1.5):
        resized = cv2.resize(image, (round(width * scale), round(height * scale)),
                             interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
        yield f"scale_{scale}", resized, scale, scale, 0, 0
    pad_x, pad_y = max(8, round(width * 0.08)), max(8, round(height * 0.08))
    padded = cv2.copyMakeBorder(image, pad_y, pad_y, pad_x, pad_x,
                                cv2.BORDER_CONSTANT, value=(255, 255, 255))
    yield "padding_8pct", padded, 1, 1, pad_x, pad_y
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    contrast = cv2.convertScaleAbs(gray, alpha=0.75, beta=35)
    yield "reduced_contrast", cv2.cvtColor(contrast, cv2.COLOR_GRAY2BGR), 1, 1, 0, 0
    yield "grayscale", cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), 1, 1, 0, 0
    yield "mild_blur", cv2.GaussianBlur(image, (3, 3), 0.7), 1, 1, 0, 0
    rng = np.random.default_rng(2026)
    noise = rng.normal(0, 3.0, image.shape).astype(np.float32)
    noisy = np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    yield "mild_noise", noisy, 1, 1, 0, 0
    encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 75])[1]
    yield "jpeg_75", cv2.imdecode(encoded, cv2.IMREAD_COLOR), 1, 1, 0, 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path,
                        default=ROOT / "tests/fixtures/unseen/phase2_manifest.json")
    parser.add_argument("--case", action="append", dest="case_ids",
                        help="Limit to a fixture ID; repeat for multiple cases.")
    parser.add_argument("--variant", action="append", dest="variant_ids",
                        help="Limit to a named pixel transform; repeat for multiple transforms.")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "storage/generated/variation_benchmark.json")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    selected = [case for case in manifest["cases"]
                if case.get("classification", "supported") == "supported"
                and (not args.case_ids or case["id"] in args.case_ids)]
    rows = []
    with tempfile.TemporaryDirectory(prefix="physics_variations_") as temp_name:
        temp = Path(temp_name)
        for case in selected:
            image = cv2.imread(str(args.manifest.parent / case["path"]))
            if image is None:
                rows.append({"id": case["id"], "error": "IMAGE_DECODE_FAILED"})
                continue
            for variant_id, pixels, sx, sy, dx, dy in variants(image):
                if args.variant_ids and variant_id not in args.variant_ids:
                    continue
                name = f"{case['id']}_{variant_id}.png"
                cv2.imwrite(str(temp / name), pixels)
                transformed = dict(case)
                transformed.pop("review", None)
                transformed["id"] = f"{case['id']}:{variant_id}"
                transformed["path"] = name
                transformed["expected_points"] = {
                    key: {**point, "x": point["x"] * sx + dx,
                          "y": point["y"] * sy + dy,
                          "tolerance_px": point["tolerance_px"] * max(sx, sy)}
                    for key, point in case.get("expected_points", {}).items()
                }
                try:
                    result = run_case(transformed, temp)
                    errors = [check["error_px"] for check in result["point_checks"].values()
                              if check["error_px"] is not None]
                    row = {
                        "id": transformed["id"], "subtype": case["subtype"],
                        "variant": variant_id, "automatic_success": result["scene_created"],
                        "geometry_success": (all(check["pass"] for check in result["point_checks"].values())
                                             if result["point_checks"] else None),
                        "mean_landmark_error_px": sum(errors) / len(errors) if errors else None,
                        "max_landmark_error_px": max(errors) if errors else None,
                        "compiler_status": result["compiler_status"],
                        "issue_codes": result["issue_codes"],
                        "automatic_failures": result["automatic_failures"],
                        "backend_blockers": result["backend_blockers"],
                        "missing_requirements": result["missing_requirements"],
                        "grounded_parameter_names": result["grounded_parameter_names"],
                        "point_checks": result["point_checks"],
                        "parameter_checks": result["parameter_checks"],
                    }
                    if case["subtype"] == "dc_linear" and result["auto_scene"] is not None:
                        try:
                            row["circuit_metrics"] = circuit_metrics(result["auto_scene"])
                        except Exception as error:
                            row["circuit_metrics"] = {"error": type(error).__name__}
                    rows.append(row)
                except Exception as error:
                    rows.append({"id": transformed["id"], "subtype": case["subtype"],
                                 "variant": variant_id, "automatic_success": False,
                                 "error": type(error).__name__})
                print(f"Completed {transformed['id']}: {rows[-1].get('compiler_status', rows[-1].get('error'))}", flush=True)
    by_subtype = defaultdict(lambda: {"variants": 0, "automatic_successes": 0,
                                      "geometry_checks": 0, "geometry_successes": 0})
    for row in rows:
        if "subtype" not in row:
            continue
        group = by_subtype[row["subtype"]]
        group["variants"] += 1
        group["automatic_successes"] += int(row.get("automatic_success", False))
        if row.get("geometry_success") is not None:
            group["geometry_checks"] += 1
            group["geometry_successes"] += int(row["geometry_success"])
    report = {"semantic_mode": "MockVisionProvider with expected subtype",
              "classification_accuracy": None,
              "summary": dict(by_subtype), "cases": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Details: {args.output}")


if __name__ == "__main__":
    main()

"""Offline generated-layout circuit perception benchmark (mock semantics).

Draws neutral-name schematics from topology descriptions. The production
pipeline receives only pixels; no component coordinates or graph are injected.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
import sys

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research.benchmarks.variation_benchmark import ROOT, circuit_metrics
from scripts.benchmark_phase2 import run_case


def draw_component(image, start, end, label, value):
    x1, y1 = start
    x2, y2 = end
    if y1 == y2:
        mid = (x1 + x2) // 2
        xs = np.linspace(mid - 38, mid + 38, 9).astype(int)
        points = [(int(x), y1 + (12 if i % 2 else -12)) for i, x in enumerate(xs)]
        cv2.line(image, (x1, y1), (int(xs[0]), y1), (15, 20, 25), 3)
        cv2.polylines(image, [np.array(points)], False, (15, 20, 25), 3)
        cv2.line(image, (int(xs[-1]), y1), (x2, y1), (15, 20, 25), 3)
        cv2.putText(image, label, (mid - 28, y1 - 48), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (15, 20, 25), 2)
        cv2.putText(image, f"{value} ohm", (mid - 50, y1 - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (15, 20, 25), 2)
    else:
        mid = (y1 + y2) // 2
        ys = np.linspace(mid - 38, mid + 38, 9).astype(int)
        points = [(x1 + (12 if i % 2 else -12), int(y)) for i, y in enumerate(ys)]
        cv2.line(image, (x1, y1), (x1, int(ys[0])), (15, 20, 25), 3)
        cv2.polylines(image, [np.array(points)], False, (15, 20, 25), 3)
        cv2.line(image, (x1, int(ys[-1])), (x1, y2), (15, 20, 25), 3)
        cv2.putText(image, label, (x1 + 28, mid - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (15, 20, 25), 2)
        cv2.putText(image, f"{value} ohm", (x1 + 28, mid + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (15, 20, 25), 2)


def make_layout(kind: str) -> np.ndarray:
    image = np.full((768, 1024, 3), 255, dtype=np.uint8)
    left, right, top, bottom = 180, 820, 160, 610
    color = (15, 20, 25)
    # Source bars interrupt the left vertical wire.
    cv2.line(image, (left, top), (left, 354), color, 3)
    cv2.line(image, (left, 420), (left, bottom), color, 3)
    cv2.line(image, (left - 36, 354), (left + 36, 354), color, 3)
    cv2.line(image, (left - 22, 381), (left + 22, 381), color, 3)
    cv2.line(image, (left - 36, 408), (left + 36, 408), color, 3)
    cv2.putText(image, "12 V", (46, 392), cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)

    if kind == "series":
        draw_component(image, (left, top), (right, top), "R1", 50)
        draw_component(image, (right, top), (right, bottom), "R2", 100)
        cv2.line(image, (left, bottom), (right, bottom), color, 3)
    elif kind == "parallel":
        cv2.line(image, (left, top), (right, top), color, 3)
        cv2.line(image, (left, bottom), (right, bottom), color, 3)
        draw_component(image, (500, top), (500, bottom), "R1", 50)
        draw_component(image, (right, top), (right, bottom), "R2", 100)
    elif kind == "multi_branch":
        draw_component(image, (left, top), (500, top), "R1", 50)
        cv2.line(image, (500, top), (right, top), color, 3)
        draw_component(image, (500, top), (500, bottom), "R2", 150)
        draw_component(image, (right, top), (right, bottom), "R3", 300)
        draw_component(image, (left, bottom), (500, bottom), "R4", 100)
        cv2.line(image, (500, bottom), (right, bottom), color, 3)
    elif kind == "bridge":
        middle = (top + bottom) // 2
        cv2.line(image, (left, top), (right, top), color, 3)
        cv2.line(image, (left, bottom), (right, bottom), color, 3)
        draw_component(image, (500, top), (500, middle), "R1", 50)
        draw_component(image, (500, middle), (500, bottom), "R2", 100)
        draw_component(image, (right, top), (right, middle), "R3", 150)
        draw_component(image, (right, middle), (right, bottom), "R4", 300)
        draw_component(image, (500, middle), (right, middle), "R5", 200)
    else:
        raise ValueError(kind)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", choices=("series", "parallel", "multi_branch", "bridge"),
                        action="append", dest="layouts")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "storage/generated/circuit_layout_benchmark.json")
    args = parser.parse_args()
    rows = []
    with tempfile.TemporaryDirectory(prefix="neutral_circuit_layout_") as name:
        root = Path(name)
        for index, kind in enumerate(args.layouts or ("series", "parallel", "multi_branch", "bridge")):
            path = f"neutral_{index + 7}.png"
            cv2.imwrite(str(root / path), make_layout(kind))
            case = {"id": kind, "path": path, "origin": "generated_layout",
                    "classification": "supported", "domain": "circuits", "subtype": "dc_linear",
                    "roles": ["resistor", "voltage_source"], "expected_scene": "ready"}
            result = run_case(case, root)
            scene = result.get("auto_scene")
            row = {"layout": kind, "automatic_success": bool(scene),
                   "issue_codes": result["issue_codes"],
                   "automatic_failures": result["automatic_failures"]}
            if scene:
                try:
                    row["circuit_metrics"] = circuit_metrics(scene)
                    expected = {"series": (3, 3), "parallel": (3, 2),
                                "multi_branch": (5, 4), "bridge": (6, 4)}[kind]
                    metrics = row["circuit_metrics"]
                    row["graph_valid"] = (
                        (metrics["components"], metrics["nodes"]) == expected
                        and metrics["solver_status"] == "solved"
                        and metrics["finite_node_voltages"]
                        and metrics["max_kcl_residual_a"] < 1e-6
                    )
                except Exception as error:
                    row["circuit_metrics"] = {"error": type(error).__name__}
                    row["graph_valid"] = False
            rows.append(row)
            print(f"{kind}: {result['compiler_status']}", flush=True)
    output = args.output
    output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Details: {output}")


if __name__ == "__main__":
    main()

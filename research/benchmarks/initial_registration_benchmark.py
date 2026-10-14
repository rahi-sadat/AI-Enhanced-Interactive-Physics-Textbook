"""Offline real-image pendulum CV -> canonical runtime t=0 -> registration.

This bounded benchmark measures consistency with CV observations, not independent
ground-truth perception accuracy or rendered sprite pixels. Its bridge calls the
existing runtime kernel and source-position renderer method without reimplementing
physics. Deliberately changed-angle/missing/dimension cases are negative controls.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.ingestion.BookUnderstandingPipeline import BookUnderstandingPipeline
from ai.ingestion.PageIRBuilder import PageIRBuilder
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.mock_provider import MockVisionProvider
from ai.registration import InitialRegistrationGate, PredictedGeometry
from ai.resolution.auto import AutoResolutionEngine
from scripts.benchmark_phase2 import evidence_pipeline
from shared.schemas.evidence import SourcePoint, SourceLine
from shared.schemas.ingestion import BookIR, SourceAsset
from shared.schemas.semantic import SemanticAnalysisResult, SemanticConfidence, SemanticEntity
from shared.schemas.visual_reconstruction import ObservedGeometry, VisualConstraint, VisualReconstruction


def prepare_case(case, fixture_root):
    if case["subtype"] != "pendulum":
        raise ValueError("This benchmark currently has a pendulum prediction bridge only")
    path = fixture_root / case["path"]
    raw = path.read_bytes()
    pixels = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
    if pixels is None:
        raise ValueError("Fixture image could not be decoded")
    height, width = pixels.shape[:2]
    digest = hashlib.sha256(raw).hexdigest()
    asset = SourceAsset(
        id=f"registration_{digest[:12]}", mime_type="image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png",
        original_filename="neutral_upload", byte_size=len(raw), width_px=width, height_px=height,
        sha256=digest, storage_path=str(path.resolve()),
    )
    semantic = SemanticAnalysisResult(
        classification="supported", is_physics=True, domain=case["domain"], subtype=case["subtype"],
        confidence=SemanticConfidence(is_physics=0.9, domain=0.88, subtype=0.85, overall=0.85),
        entities=[SemanticEntity(temporary_id=f"entity_{i}", role=role, confidence=0.85)
                  for i, role in enumerate(case["roles"])],
    )
    page = PageIRBuilder().build(asset, "/benchmark/neutral_upload")
    book = BookUnderstandingPipeline(PhysicsVisionAnalyzer(MockVisionProvider(default_result=semantic))).analyze(page, asset=asset)
    grounded = evidence_pipeline().extract_and_fuse(asset=asset, page_ir=page, book_ir=book)
    # Capture real grounded observations BEFORE automatic assumptions/compilation.
    entities = {entity.type: entity for entity in grounded.entities}
    pivot, bob = entities["pivot"], entities["bob"]
    string = entities.get("string") or entities.get("rod")
    if string is None or not pivot.position_source_px or not bob.position_source_px:
        raise ValueError("Pivot/bob/string did not ground; no fallback observations allowed")
    visible = string.geometry["visible_string"]
    point = lambda value: SourcePoint(value["x"], value["y"])
    observed = ObservedGeometry(
        width, height,
        landmarks={"pivot": point(pivot.position_source_px), "bob": point(bob.position_source_px)},
        lines={"string": SourceLine(point(visible["start"]), point(visible["end"]))},
        evidence_refs={"pivot": list(dict.fromkeys(pivot.evidence_refs)),
                       "bob": list(dict.fromkeys(bob.evidence_refs)),
                       "string": list(dict.fromkeys(string.evidence_refs))},
    )
    auto = AutoResolutionEngine.resolve(grounded)
    compiled = PhysicsCompiler().compile(grounded)
    if compiled.scene is None:
        raise ValueError(f"No canonical scene: {compiled.status}; {compiled.issues}")
    grounded.visual_reconstruction = VisualReconstruction(
        observed, constraints=[VisualConstraint("pivot_check", "landmark", ["pivot"]),
                               VisualConstraint("bob_check", "landmark", ["bob"]),
                               VisualConstraint("string_check", "line", ["string"])],
    )
    return {"id": case["id"], "book_ir": grounded.to_dict(), "scene": compiled.scene,
            "compiler_status": compiled.status, "automatic_assumptions": auto.assumptions}


def evaluate_case(prepared, runtime):
    grounded = BookIR.from_dict(prepared["book_ir"])
    observed = grounded.visual_reconstruction.observed_geometry
    width, height = observed.source_width, observed.source_height
    point = lambda value: SourcePoint(value["x"], value["y"])
    original = json.dumps(grounded.to_dict(), sort_keys=True)

    def prediction(data):
        return PredictedGeometry(
            grounded.source_asset_id, grounded.figure_id, width, height, grounded.domain, grounded.subtype,
            time_s=data["time_s"], landmarks={key: point(value) for key, value in data["landmarks"].items()},
            lines={key: SourceLine(point(value["start"]), point(value["end"])) for key, value in data["lines"].items()},
        )

    gate = InitialRegistrationGate()
    initial = prediction(runtime["initial"])
    reports = {"initial": gate.evaluate(grounded, initial),
               "angle_plus_30_degrees": gate.evaluate(grounded, prediction(runtime["perturbed"]))}
    missing = deepcopy(initial)
    del missing.landmarks["bob"]
    reports["missing_bob_prediction"] = gate.evaluate(grounded, missing)
    scaled = deepcopy(initial)
    scaled.source_width *= 2
    reports["wrong_source_dimensions"] = gate.evaluate(grounded, scaled)
    assert reports["angle_plus_30_degrees"].status.value == "FAILED", "Changed runtime angle escaped registration"
    assert reports["missing_bob_prediction"].status.value != "PASSED"
    assert reports["wrong_source_dimensions"].status.value == "NEEDS_REVIEW"
    assert json.dumps(grounded.to_dict(), sort_keys=True) == original, "Gate mutated grounded BookIR"
    return {"id": prepared["id"], "source_width": width, "source_height": height,
            "compiler_status": prepared["compiler_status"], "observed_geometry": observed.to_dict(),
            "runtime_predictions": runtime, "automatic_assumptions": prepared["automatic_assumptions"],
            "thresholds": gate.thresholds.to_dict(), "reports": {key: value.to_dict() for key, value in reports.items()},
            "limitations": "CV observations, not independent annotations; pivot/bob/visible string only, no masks or raster rendering"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", dest="cases")
    parser.add_argument("--node", default="node")
    parser.add_argument("--prepare-only", action="store_true", help="Export one grounded case and scene for a separate Node process")
    parser.add_argument("--prepared", type=Path, help="Previously exported case (avoids rerunning CV)")
    parser.add_argument("--predictions", type=Path, help="Node bridge output for --prepared")
    parser.add_argument("--output", type=Path, default=ROOT / "storage/generated/phase2_initial_registration.json")
    args = parser.parse_args()
    def offline_only(*args, **kwargs):
        raise RuntimeError("Network disabled for offline registration benchmark")
    socket.socket.connect = offline_only
    manifest = ROOT / "tests/fixtures/unseen/phase2_manifest.json"
    catalog = {case["id"]: case for case in json.loads(manifest.read_text())["cases"]}
    names = args.cases or ["pendulum_sketch"]
    if args.prepare_only and (len(names) != 1 or args.prepared or args.predictions):
        parser.error("--prepare-only exports exactly one fresh case")
    if bool(args.prepared) != bool(args.predictions):
        parser.error("--prepared and --predictions must be supplied together")
    if args.prepare_only:
        prepared = prepare_case(catalog[names[0]], manifest.parent)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(prepared, indent=2, allow_nan=False), encoding="utf-8")
        print(f"Prepared case: {args.output}")
        return
    if args.prepared:
        rows = [evaluate_case(json.loads(args.prepared.read_text(encoding="utf-8-sig")),
                              json.loads(args.predictions.read_text(encoding="utf-8-sig")))]
    else:
        rows = []
        for name in names:
            prepared = prepare_case(catalog[name], manifest.parent)
            result = subprocess.run(
                [args.node, "research/benchmarks/pendulum_initial_prediction.mjs"],
                input=json.dumps(prepared["scene"]), capture_output=True, text=True, check=True, timeout=45, cwd=ROOT,
            )
            rows.append(evaluate_case(prepared, json.loads(result.stdout)))
    report = {"semantic_mode": "MockVisionProvider; no classification accuracy measured",
              "prediction_mode": "canonical PhysicsRuntime kernel + existing PendulumSimulation source-position method, unstepped t=0",
              "cases": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    for row in rows:
        print(json.dumps({"id": row["id"], "statuses": {key: value["status"] for key, value in row["reports"].items()},
                          "initial_landmark_errors": row["reports"]["initial"]["landmarkErrors"]}))
    print(f"Details: {args.output}")


if __name__ == "__main__":
    main()

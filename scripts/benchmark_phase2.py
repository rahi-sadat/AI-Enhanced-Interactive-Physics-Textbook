"""Run an offline image-to-compilation safety benchmark over local fixtures.

Semantic labels are injected through MockVisionProvider. This measures the
grounding/readiness/compilation path, not VLM classification accuracy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.evidence.pipeline import EvidenceExtractionPipeline
from ai.ingestion.BookUnderstandingPipeline import BookUnderstandingPipeline
from ai.ingestion.PageIRBuilder import PageIRBuilder
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.mock_provider import MockVisionProvider
from ai.resolution import ReadinessEvaluator, ResolutionAnalyzer, ResolutionEngine
from ai.resolution.auto import AutoResolutionEngine
from shared.schemas.ingestion import SourceAsset
from shared.schemas.semantic import SemanticAnalysisResult, SemanticConfidence, SemanticEntity


_EVIDENCE_PIPELINE = None


def evidence_pipeline():
    global _EVIDENCE_PIPELINE
    if _EVIDENCE_PIPELINE is None:
        _EVIDENCE_PIPELINE = EvidenceExtractionPipeline()
    return _EVIDENCE_PIPELINE


def scalar(value):
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return getattr(value, "value", value)


def non_json_path(value, path="scene"):
    if isinstance(value, dict):
        for key, item in value.items():
            found = non_json_path(item, f"{path}.{key}")
            if found:
                return found
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            found = non_json_path(item, f"{path}[{index}]")
            if found:
                return found
    else:
        try:
            json.dumps(value)
        except (TypeError, ValueError):
            return f"{path}: {type(value).__name__}"
    return None


def run_case(case: dict, fixture_root: Path) -> dict:
    path = fixture_root / case["path"]
    raw = path.read_bytes()
    image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot decode {path}")
    height, width = image.shape[:2]
    digest = hashlib.sha256(raw).hexdigest()
    asset = SourceAsset(
        id=f"benchmark_{digest[:12]}", sha256=digest, original_filename=path.name,
        mime_type="image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png",
        byte_size=len(raw), width_px=width, height_px=height, storage_path=str(path.resolve()),
    )
    classification = case.get("classification", "supported")
    supported = classification == "supported"
    semantic = SemanticAnalysisResult(
        classification=classification, is_physics=case.get("is_physics", True),
        domain=case.get("domain"), subtype=case.get("subtype"),
        confidence=SemanticConfidence(overall=0.85 if supported else 0.0,
                                      is_physics=0.9, domain=0.88 if supported else 0.0,
                                      subtype=0.85 if supported else 0.0),
        entities=[SemanticEntity(temporary_id=f"entity_{i}", role=role, confidence=0.85)
                  for i, role in enumerate(case["roles"])],
    )
    started = time.perf_counter()
    page_ir = PageIRBuilder().build(asset, f"/benchmark/{path.name}")
    book_ir = BookUnderstandingPipeline(
        analyzer=PhysicsVisionAnalyzer(provider=MockVisionProvider(default_result=semantic))
    ).analyze(page_ir, asset=asset)
    grounded = evidence_pipeline().extract_and_fuse(asset=asset, page_ir=page_ir, book_ir=book_ir)
    auto_result = AutoResolutionEngine.resolve(grounded)
    compile_result = PhysicsCompiler().compile(grounded)
    review_state = ResolutionAnalyzer.analyze(grounded) if classification == "supported" else None
    backend_readiness = ReadinessEvaluator.evaluate(grounded) if classification == "supported" else None
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)

    parameter_checks = {}
    for name, expectation in case.get("expected_parameters", {}).items():
        found = scalar((grounded.parameters or {}).get(name))
        try:
            error = abs(float(found) - expectation["value"])
            passed = error <= expectation["tolerance"]
        except (TypeError, ValueError):
            error, passed = None, False
        parameter_checks[name] = {"observed": found, "expected": expectation["value"],
                                  "unit": expectation.get("unit"),
                                  "tolerance": expectation["tolerance"], "absolute_error": error,
                                  "pass": passed}

    point_checks = {}
    for name, expectation in case.get("expected_points", {}).items():
        found = scalar((grounded.parameters or {}).get(name))
        try:
            error = math.hypot(float(found["x"]) - expectation["x"],
                               float(found["y"]) - expectation["y"])
            passed = error <= expectation["tolerance_px"]
        except (TypeError, ValueError, KeyError):
            error, passed = None, False
        point_checks[name] = {"observed": found, "expected": {"x": expectation["x"],
                                                              "y": expectation["y"]},
                              "tolerance_px": expectation["tolerance_px"],
                              "error_px": error, "pass": passed}

    expected_scene = case["expected_scene"]
    false_ready = expected_scene == "null" and compile_result.scene is not None
    false_abstain = expected_scene == "ready" and compile_result.scene is None
    auto_serialization_error = non_json_path(compile_result.scene) if compile_result.scene is not None else None
    row = {
        "id": case["id"], "path": case["path"], "origin": case["origin"],
        "classification": classification, "domain": case.get("domain"),
        "subtype": case.get("subtype"), "sha256": digest,
        "width": width, "height": height, "semantic_mode": "mock_expected_label",
        "book_ir_status": grounded.status, "compiler_status": compile_result.status,
        "scene_created": compile_result.scene is not None, "false_ready": false_ready,
        "false_abstain": false_abstain,
        "auto_scene_serializable": compile_result.scene is not None and auto_serialization_error is None,
        "auto_scene_serialization_error": auto_serialization_error,
        "auto_scene": compile_result.scene if compile_result.scene is not None and auto_serialization_error is None else None,
        "grounded_parameter_names": sorted((grounded.parameters or {}).keys()),
        "evidence_records": len(grounded.evidence or {}),
        "parameter_checks": parameter_checks, "point_checks": point_checks,
        "latency_ms": elapsed_ms,
        "issue_codes": [issue.get("code") for issue in compile_result.issues],
        "automatic_assumptions": auto_result.assumptions,
        "automatic_failures": auto_result.failures,
        "missing_requirements": sorted(review_state.missing_requirements) if review_state else [],
        "blockers_count": review_state.blockers_count if review_state else 0,
        "analysis_ready": review_state.ready_to_compile if review_state else None,
        "backend_ready": backend_readiness.ready if backend_readiness else None,
        "readiness_disagreement": (review_state.ready_to_compile != backend_readiness.ready)
        if review_state and backend_readiness else False,
        "backend_blockers": backend_readiness.blockers if backend_readiness else [],
    }
    if circuit_spec := case.get("expected_circuit"):
        circuit = (compile_result.scene or {}).get("circuit") or {}
        components = {component.get("id"): component
                      for component in circuit.get("components", []) if isinstance(component, dict)}
        type_checks = {cid: components.get(cid, {}).get("type") == kind
                       for cid, kind in circuit_spec.get("component_types", {}).items()}
        parallel_checks = {}
        for pair in circuit_spec.get("parallel_pairs", []):
            first, second = (components.get(cid, {}) for cid in pair)
            parallel_checks["/".join(pair)] = (
                len(first.get("nodes", [])) == 2
                and len(second.get("nodes", [])) == 2
                and set(first["nodes"]) == set(second["nodes"])
            )
        row["circuit_graph_checks"] = {"component_types": type_checks,
                                       "parallel_pairs": parallel_checks}
    if review := case.get("review"):
        resolution_errors = []
        for spec in review.get("supplied_parameters", []):
            result = ResolutionEngine.apply_resolution(grounded, spec)
            if not result.success:
                resolution_errors.append(f"parameter {spec['parameterName']}: {result}")
        for policy_id in review.get("accepted_policies", []):
            result = ResolutionEngine.apply_policy(grounded, policy_id)
            if not result.success:
                resolution_errors.append(f"policy {policy_id}: {result}")
        readiness = ReadinessEvaluator.evaluate(grounded, mutate_status=True)
        reviewed_compile = PhysicsCompiler().compile(grounded)
        scene = reviewed_compile.scene
        serialization_error = non_json_path(scene) if scene is not None else None
        scene_checks = {}
        for name, expected in review.get("expected_scene_parameters", {}).items():
            found = scalar((scene or {}).get("parameters", {}).get(name))
            scene_checks[name] = {"observed": found, "expected": expected,
                                  "pass": isinstance(found, (int, float)) and abs(found - expected) < 1e-9}
        row["review"] = {
            "resolution_errors": resolution_errors, "ready": readiness.ready,
            "compiler_status": reviewed_compile.status, "scene_created": scene is not None,
            "scene_serializable": scene is not None and serialization_error is None,
            "scene_serialization_error": serialization_error,
            "scene_parameter_checks": scene_checks,
            "scene": scene if serialization_error is None else None,
        }
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path,
                        default=ROOT / "tests/fixtures/unseen/phase2_manifest.json")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "storage/generated/phase2_benchmark.json")
    parser.add_argument("--case", action="append", dest="case_ids",
                        help="Run only the named manifest case (repeatable).")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    fixture_root = args.manifest.parent
    selected = [case for case in manifest["cases"]
                if not args.case_ids or case["id"] in args.case_ids]
    if args.case_ids and len(selected) != len(set(args.case_ids)):
        parser.error("One or more --case identifiers were not found in the manifest")
    rows = [run_case(case, fixture_root) for case in selected]
    by_subtype = defaultdict(lambda: {"cases": 0, "false_ready": 0, "false_abstain": 0,
                                      "automatic_ready": 0, "parameter_checks": 0,
                                      "parameter_checks_passed": 0, "point_checks": 0,
                                      "point_checks_passed": 0})
    for row in rows:
        group = by_subtype[row["subtype"] or row["classification"]]
        group["cases"] += 1
        group["false_ready"] += int(row["false_ready"])
        group["false_abstain"] += int(row["false_abstain"])
        group["automatic_ready"] += int(row["scene_created"] and row["auto_scene_serializable"])
        group["parameter_checks"] += len(row["parameter_checks"])
        group["parameter_checks_passed"] += sum(int(check["pass"]) for check in row["parameter_checks"].values())
        group["point_checks"] += len(row["point_checks"])
        group["point_checks_passed"] += sum(int(check["pass"]) for check in row["point_checks"].values())
    reviewed = [row["review"] for row in rows if "review" in row]
    review_failures = sum(int(bool(item["resolution_errors"]) or not item["ready"] or
                              not item["scene_created"] or not item["scene_serializable"] or
                              not all(check["pass"] for check in item["scene_parameter_checks"].values()))
                          for item in reviewed)
    summary = {"cases": len(rows), "false_ready": sum(int(row["false_ready"]) for row in rows),
               "false_abstain": sum(int(row["false_abstain"]) for row in rows),
               "automatic_ready": sum(int(row["scene_created"] and row["auto_scene_serializable"]) for row in rows),
               "readiness_disagreements": sum(int(row["readiness_disagreement"]) for row in rows),
               "parameter_checks": sum(len(row["parameter_checks"]) for row in rows),
               "parameter_checks_passed": sum(sum(int(check["pass"]) for check in row["parameter_checks"].values()) for row in rows),
               "point_checks": sum(len(row["point_checks"]) for row in rows),
               "point_checks_passed": sum(sum(int(check["pass"]) for check in row["point_checks"].values()) for row in rows),
               "circuit_graph_checks": sum(len(checks) for row in rows for checks in row.get("circuit_graph_checks", {}).values()),
               "circuit_graph_checks_passed": sum(sum(int(passed) for passed in checks.values())
                                                  for row in rows for checks in row.get("circuit_graph_checks", {}).values()),
               "reviewed_cases": len(reviewed), "reviewed_successes": len(reviewed) - review_failures,
               "by_subtype": dict(by_subtype), "classification_accuracy": None,
               "classification_note": "MockVisionProvider was supplied the expected subtype for each case."}
    result = {"manifest_version": manifest["version"], "summary": summary, "cases": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Details: {args.output}")
    graph_failures = any(not all(checks.values())
                         for row in rows for checks in row.get("circuit_graph_checks", {}).values())
    return 1 if (summary["false_ready"] or summary["false_abstain"] or review_failures or graph_failures
                 or any(row["scene_created"] and not row["auto_scene_serializable"] for row in rows)) else 0


if __name__ == "__main__":
    raise SystemExit(main())

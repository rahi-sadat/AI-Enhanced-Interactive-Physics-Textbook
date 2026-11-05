"""Opt-in live semantic audit of user-provided diagrams.

Run directly with ``python tests/acceptance/test_phase5_live_semantics.py``.
Pytest collection skips this module. No key or raw provider response is logged.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

if __name__ != "__main__":
    import pytest
    pytest.skip("Live API audit runs only as an explicit script", allow_module_level=True)

from ai.ingestion.PageIRBuilder import PageIRBuilder
from ai.ingestion.BookUnderstandingPipeline import BookUnderstandingPipeline
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.ingestion.vision.gemini_provider import GeminiVisionProvider
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.mock_provider import MockVisionProvider
from ai.evidence.pipeline import EvidenceExtractionPipeline
from ai.resolution.auto import AutoResolutionEngine
from shared.schemas.ingestion import SourceAsset


load_dotenv(ROOT / ".env")
if not os.getenv("GEMINI_API_KEY"):
    raise SystemExit("GEMINI_API_KEY is not configured; live audit was not run")

manifest = json.loads((ROOT / "tests/fixtures/unseen/phase2_manifest.json").read_text(encoding="utf-8"))
cases = [case for case in manifest["cases"] if case.get("origin") == "user_provided_2026-10-11"]
assert len(cases) == 7, "Expected seven user-provided acceptance images"
provider = GeminiVisionProvider()
results = []
for case in cases:
    image_path = ROOT / "tests/fixtures/unseen" / case["path"]
    raw = image_path.read_bytes()
    with Image.open(image_path) as image:
        width, height = image.size
    asset = SourceAsset(
        id=f"live_{hashlib.sha256(raw).hexdigest()[:12]}",
        sha256=hashlib.sha256(raw).hexdigest(),
        original_filename=image_path.name,
        mime_type="image/jpeg" if image_path.suffix.lower() in {".jpg", ".jpeg"} else "image/png",
        byte_size=len(raw), width_px=width, height_px=height,
        storage_path=str(image_path),
    )
    page = PageIRBuilder().build(asset, f"/acceptance/{image_path.name}")
    row = {"id": case["id"], "path": case["path"], "expected_domain": case["domain"],
           "expected_subtype": case["subtype"]}
    try:
        result = provider.analyze_diagram(raw, asset.mime_type, page)
        row.update({
            "classification": result.classification,
            "is_physics": result.is_physics,
            "domain": result.domain,
            "subtype": result.subtype,
            "model": result.model,
            "latency_ms": result.latency_ms,
            "fallback_used": result.fallback_used,
            "role_names": [entity.role for entity in result.entities],
            "correct_pair": result.domain == case["domain"] and result.subtype == case["subtype"],
        })
        # Reuse this actual live semantic result locally; no second external call.
        book_ir = BookUnderstandingPipeline(
            analyzer=PhysicsVisionAnalyzer(provider=MockVisionProvider(default_result=result))
        ).analyze(page, asset=asset)
        grounded = EvidenceExtractionPipeline().extract_and_fuse(
            asset=asset, page_ir=page, book_ir=book_ir
        )
        auto_result = AutoResolutionEngine.resolve(grounded)
        compiled = PhysicsCompiler().compile(grounded)
        row.update({
            "book_ir_status": grounded.status,
            "compiler_status": compiled.status,
            "scene_created": compiled.scene is not None,
            "auto_scene": compiled.scene,
            "automatic_failures": auto_result.failures,
            "automatic_assumptions": auto_result.assumptions,
            "issue_codes": [issue.get("code") for issue in compiled.issues],
        })
    except Exception as exc:
        # Exception text may contain provider request details; record only the class.
        row.update({"error_type": type(exc).__name__, "correct_pair": False})
    results.append(row)
    print(f"{row['id']}: {row.get('domain')}/{row.get('subtype')} "
          f"correct={row['correct_pair']} error={row.get('error_type', 'none')}", flush=True)

summary = {"cases": len(results), "correct_pairs": sum(row.get("correct_pair", False) for row in results),
           "errors": sum("error_type" in row for row in results),
           "automatic_successes": sum(row.get("scene_created", False) for row in results)}
output = ROOT / "storage/generated/phase5_live_semantics.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({"summary": summary, "cases": results}, indent=2), encoding="utf-8")
print(json.dumps(summary))

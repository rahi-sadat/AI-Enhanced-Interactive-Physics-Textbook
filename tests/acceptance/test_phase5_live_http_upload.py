"""Opt-in live HTTP upload acceptance for explicitly selected diagrams.

Run directly with Python. Pytest collection skips this module. Uploaded files
use neutral names; generated assets and results remain under ignored storage.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

if __name__ != "__main__":
    import pytest
    pytest.skip("Live Gemini HTTP audit runs only as an explicit script", allow_module_level=True)

load_dotenv(ROOT / ".env")
if not os.getenv("GEMINI_API_KEY"):
    raise SystemExit("GEMINI_API_KEY is not configured; live HTTP audit was not run")
os.environ.pop("USE_MOCK_VISION", None)

from apps.api.main import app  # noqa: E402

manifest = json.loads((ROOT / "tests/fixtures/unseen/phase2_manifest.json").read_text(encoding="utf-8"))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--case", action="append", dest="case_ids",
                    help="Explicit manifest case ID; repeat to select multiple images")
parser.add_argument("--output", type=Path,
                    default=ROOT / "storage/generated/phase5_live_http_upload.json")
args = parser.parse_args()
cases = [case for case in manifest["cases"]
         if case["id"] in args.case_ids] if args.case_ids else [
             case for case in manifest["cases"] if case.get("origin") == "user_provided_2026-10-11"
         ]
if args.case_ids:
    assert {case["id"] for case in cases} == set(args.case_ids), "Unknown requested case"
else:
    assert len(cases) == 7
rows = []
with TestClient(app) as client:
    for index, case in enumerate(cases, 1):
        image_path = ROOT / "tests/fixtures/unseen" / case["path"]
        raw = image_path.read_bytes()
        with Image.open(image_path) as image:
            width, height = image.size
        mime = "image/jpeg" if image_path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
        row = {"id": case["id"], "path": case["path"],
               "expected_domain": case["domain"], "expected_subtype": case["subtype"]}
        try:
            response = client.post("/api/ingest", files={"file": (f"neutral_{index:02d}{image_path.suffix}", raw, mime)})
            row["http_status"] = response.status_code
            if response.status_code == 200:
                body = response.json()
                asset = body.get("source_asset") or {}
                page = body.get("page_ir") or {}
                book = body.get("book_ir") or {}
                scene = body.get("scene")
                row.update({
                    "domain": book.get("domain"), "subtype": book.get("subtype"),
                    "correct_pair": book.get("domain") == case["domain"] and book.get("subtype") == case["subtype"],
                    "compiler_status": (body.get("compiler") or {}).get("status"),
                    "scene_created": scene is not None,
                    "auto_scene": scene,
                    "source_width": asset.get("width_px"), "source_height": asset.get("height_px"),
                    "page_width": (page.get("source") or {}).get("width_px"),
                    "page_height": (page.get("source") or {}).get("height_px"),
                    "dimension_match": (
                        asset.get("width_px") == width and asset.get("height_px") == height
                        and (page.get("source") or {}).get("width_px") == width
                        and (page.get("source") or {}).get("height_px") == height
                        and (book.get("geometry") or {}).get("width") == width
                        and (book.get("geometry") or {}).get("height") == height
                        and (scene is None or (
                            (scene.get("coordinateSpace") or {}).get("width") == width
                            and (scene.get("coordinateSpace") or {}).get("height") == height
                        ))
                    ),
                    "assumptions": body.get("assumptions") or [],
                    "failure_category": body.get("failure_category"),
                    "issue_codes": [issue.get("code") for issue in body.get("issues") or []],
                    "auto_failures": body.get("auto_failures") or [],
                    "review_blockers": ((body.get("debugTrace") or {}).get("readiness") or {}).get("blockers") or [],
                })
                if scene is None:
                    row["debug_book_ir"] = book
            else:
                row["error_type"] = "HTTP_ERROR"
        except Exception as error:
            row["error_type"] = type(error).__name__
        rows.append(row)
        print(f"{row['id']}: HTTP {row.get('http_status', 'error')} "
              f"{row.get('domain')}/{row.get('subtype')} scene={row.get('scene_created')}", flush=True)

summary = {"cases": len(rows), "correct_pairs": sum(bool(r.get("correct_pair")) for r in rows),
           "http_successes": sum(r.get("http_status") == 200 for r in rows),
           "automatic_scenes": sum(bool(r.get("scene_created")) for r in rows),
           "dimension_matches": sum(bool(r.get("dimension_match")) for r in rows)}
output = args.output
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({"summary": summary, "cases": rows}, indent=2), encoding="utf-8")
print(json.dumps(summary))

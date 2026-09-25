import hashlib
import json
import sys
import time
from pathlib import Path
import httpx

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TEST_CASES = [
    {
        "source": "tests/fixtures/unseen/mechanics/pendulum_sketch_raw.png",
        "target_filename": "x17.jpg",
        "mime": "image/jpeg",
        "expected_concept": "mechanics / pendulum",
    },
    {
        "source": "storage/uploads/sample_test_diagrams/projectile_test_diagram.png",
        "target_filename": "a91.png",
        "mime": "image/png",
        "expected_concept": "mechanics / projectile",
    },
    {
        "source": "tests/fixtures/unseen/optics/lens_diagram_exercise.png",
        "target_filename": "photo42.png",
        "mime": "image/png",
        "expected_concept": "optics / thin_lens",
    },
    {
        "source": "tests/fixtures/unseen/optics/concave_mirror_diagram.png",
        "target_filename": "scan77.jpg",
        "mime": "image/jpeg",
        "expected_concept": "optics / spherical_mirror",
    },
    {
        "source": "tests/fixtures/unseen/circuits/resistor_network_handdrawn.png",
        "target_filename": "q123.png",
        "mime": "image/png",
        "expected_concept": "circuits / dc_linear",
    },
    {
        "source": "tests/fixtures/unseen/unrelated/landscape_photo.jpg",
        "target_filename": "random_photo.jpg",
        "mime": "image/jpeg",
        "expected_concept": "non_physics",
    },
    {
        "source": "tests/fixtures/unseen/unsupported/wave_interference.png",
        "target_filename": "wave_interfere.png",
        "mime": "image/png",
        "expected_concept": "unsupported_physics",
    },
]

BASE_URL = "http://127.0.0.1:8000/api/ingest"

print("=" * 80)
print("PR-05 MANDATORY REAL GEMINI ACCEPTANCE TEST SUITE")
print("=" * 80)

results = []

for idx, tc in enumerate(TEST_CASES):
    src_path = Path(tc["source"])
    if not src_path.exists():
        print(f"ERROR: Source file not found: {src_path}")
        continue

    data = src_path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    filename = tc["target_filename"]
    mime = tc["mime"]

    print(f"\n[{idx + 1}/{len(TEST_CASES)}] Testing: {filename} (from {src_path.name})")
    print(f"  Target Concept: {tc['expected_concept']}")
    print(f"  SHA-256: {sha256[:16]}... ({len(data)} bytes)")

    # Send multipart upload with retries on rate limits
    max_http_retries = 3
    resp_json = None
    for attempt in range(max_http_retries):
        try:
            with httpx.Client(timeout=60.0) as client:
                files = {"file": (filename, data, mime)}
                resp = client.post(BASE_URL, files=files)
                if resp.status_code == 200:
                    resp_json = resp.json()
                    break
                else:
                    print(f"  HTTP {resp.status_code}: {resp.text[:150]}")
                    time.sleep(5)
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            time.sleep(5)

    if not resp_json:
        print(f"  FAILED to get successful 200 response for {filename}")
        continue

    # Extract required verification fields
    sa = resp_json.get("source_asset", {})
    bi = resp_json.get("book_ir", {})
    prov = bi.get("provenance", {})
    cr = resp_json.get("compiler", {})
    conf = bi.get("confidence", {})
    entities = bi.get("entities", [])
    visible_labels = prov.get("visible_labels", [])

    model = prov.get("model", "unknown")
    classification = prov.get("classification", "unknown")
    domain = bi.get("domain")
    subtype = bi.get("subtype")
    book_status = bi.get("status")
    compiler_status = cr.get("status")
    scene = cr.get("scene")

    entity_roles = [f"{e.get('id')}:{e.get('type')}" for e in entities]
    label_texts = [f"'{l.get('text')}'" for l in visible_labels]

    report_row = {
        "filename": filename,
        "sha256": sha256[:16] + "...",
        "model": model,
        "classification": classification,
        "domain": domain,
        "subtype": subtype,
        "confidence": conf,
        "entity_roles": entity_roles,
        "visible_labels": label_texts,
        "book_status": book_status,
        "compiler_status": compiler_status,
        "scene": scene,
        "expected": tc["expected_concept"],
    }
    results.append(report_row)

    print(f"  -> Model: {model}")
    print(f"  -> Classification: {classification}")
    print(f"  -> Domain: {domain}")
    print(f"  -> Subtype: {subtype}")
    print(f"  -> Confidence: isPhysics={conf.get('isPhysics')}, domain={conf.get('domain')}, subtype={conf.get('subtype')}")
    print(f"  -> Entity Roles: {entity_roles}")
    print(f"  -> Visible Labels: {label_texts}")
    print(f"  -> BookIR Status: {book_status}")
    print(f"  -> Compiler Status: {compiler_status}")
    print(f"  -> Compiler Scene: {scene} (Zero fabrication enforced: {scene is None})")

    # Safety delay between live calls to honor rate limits
    if idx < len(TEST_CASES) - 1:
        time.sleep(4)

print("\n" + "=" * 80)
print("FINAL ACCEPTANCE SUMMARY TABLE")
print("=" * 80)
print(f"{'Filename':<16} | {'Class':<12} | {'Domain':<10} | {'Subtype':<18} | {'BookIR':<12} | {'Scene':<6}")
print("-" * 80)
for r in results:
    scene_str = "null" if r["scene"] is None else "FABRICATED!"
    print(f"{r['filename']:<16} | {str(r['classification']):<12} | {str(r['domain']):<10} | {str(r['subtype']):<18} | {str(r['book_status']):<12} | {scene_str:<6}")

with open("live_acceptance_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nWrote live_acceptance_results.json")

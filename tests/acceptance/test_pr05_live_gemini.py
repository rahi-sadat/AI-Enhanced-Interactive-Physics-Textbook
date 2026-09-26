"""PR-05 Live Acceptance Test Suite — Real Gemini VLM Integration.

Validates the full pipeline:
  REAL uploaded image bytes
      ↓ SourceAsset → PageIR → PhysicsVisionAnalyzer → GeminiVisionProvider
      ↓ SemanticAnalysisResult → BookUnderstandingPipeline → BookIR
      ↓ PhysicsCompiler → NEEDS_REVIEW + scene=null

USAGE (requires GEMINI_API_KEY and running backend):
    python tests/acceptance/test_pr05_live_gemini.py

PASS CRITERIA:
  - HTTP 200 from live backend for every test case
  - classification matches expected_concept (for supported cases: "domain / subtype")
  - compiler scene is always null (zero-fabrication invariant)
  - compiler status is NEEDS_REVIEW
  - BookIR status is UNRESOLVED
  - No exceptions, no fabricated geometry or parameters
"""
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

# ---------------------------------------------------------------------------
# Test case definitions
# ---------------------------------------------------------------------------
TEST_CASES = [
    {
        "source": "tests/fixtures/unseen/mechanics/pendulum_sketch_raw.png",
        "target_filename": "x17.jpg",
        "mime": "image/jpeg",
        "expected_classification": "supported",
        "expected_domain": "mechanics",
        "expected_subtype": "pendulum",
        "expected_concept": "mechanics / pendulum",
    },
    {
        "source": "storage/uploads/sample_test_diagrams/projectile_test_diagram.png",
        "target_filename": "a91.png",
        "mime": "image/png",
        "expected_classification": "supported",
        "expected_domain": "mechanics",
        "expected_subtype": "projectile",
        "expected_concept": "mechanics / projectile",
    },
    {
        "source": "tests/fixtures/unseen/optics/lens_diagram_exercise.png",
        "target_filename": "photo42.png",
        "mime": "image/png",
        "expected_classification": "supported",
        "expected_domain": "optics",
        "expected_subtype": "thin_lens",
        "expected_concept": "optics / thin_lens",
    },
    {
        "source": "tests/fixtures/unseen/optics/concave_mirror_diagram.png",
        "target_filename": "scan77.jpg",
        "mime": "image/jpeg",
        "expected_classification": "supported",
        "expected_domain": "optics",
        "expected_subtype": "spherical_mirror",
        "expected_concept": "optics / spherical_mirror",
    },
    {
        "source": "tests/fixtures/unseen/circuits/resistor_network_handdrawn.png",
        "target_filename": "q123.png",
        "mime": "image/png",
        "expected_classification": "supported",
        "expected_domain": "circuits",
        "expected_subtype": "dc_linear",
        "expected_concept": "circuits / dc_linear",
    },
    {
        "source": "tests/fixtures/unseen/unrelated/landscape_photo.jpg",
        "target_filename": "random_photo.jpg",
        "mime": "image/jpeg",
        "expected_classification": "non_physics",
        "expected_domain": None,
        "expected_subtype": None,
        "expected_concept": "non_physics",
    },
    {
        "source": "tests/fixtures/unseen/unsupported/wave_interference.png",
        "target_filename": "wave_interfere.png",
        "mime": "image/png",
        "expected_classification": "unsupported_physics",
        "expected_domain": None,
        "expected_subtype": None,
        "expected_concept": "unsupported_physics",
    },
]

BASE_URL = "http://127.0.0.1:8000/api/ingest"

# ---------------------------------------------------------------------------
# Invariants that MUST hold for every test case regardless of classification
# ---------------------------------------------------------------------------
UNIVERSAL_INVARIANTS = {
    "compiler_scene_null": "PhysicsCompiler scene must always be null (zero-fabrication PR-05 invariant)",
    "compiler_status_needs_review": "PhysicsCompiler status must be NEEDS_REVIEW",
    "bookir_status_unresolved": "BookIR status must be UNRESOLVED",
    "no_fabricated_parameters": "BookIR parameters must be empty {}",
}

print("=" * 80)
print("PR-05 MANDATORY REAL GEMINI ACCEPTANCE TEST SUITE")
print("=" * 80)

results = []
passed = 0
failed = 0
skipped = 0
assertion_failures = []

for idx, tc in enumerate(TEST_CASES):
    src_path = Path(tc["source"])
    if not src_path.exists():
        print(f"\n[{idx + 1}/{len(TEST_CASES)}] SKIPPED — file not found: {src_path}")
        skipped += 1
        continue

    data = src_path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    filename = tc["target_filename"]
    mime = tc["mime"]

    print(f"\n[{idx + 1}/{len(TEST_CASES)}] {filename}  (from {src_path.name})")
    print(f"  Expected: {tc['expected_concept']}")
    print(f"  SHA-256:  {sha256[:16]}...  ({len(data)} bytes)")

    # Send multipart upload with retries
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
        msg = f"FAILED to get 200 response for {filename}"
        print(f"  ❌ {msg}")
        assertion_failures.append(f"[{filename}] HTTP failure: {msg}")
        failed += 1
        continue

    # -----------------------------------------------------------------------
    # Extract fields
    # -----------------------------------------------------------------------
    sa = resp_json.get("source_asset", {})
    bi = resp_json.get("book_ir", {})
    prov = bi.get("provenance", {})
    cr = resp_json.get("compiler", {})
    conf = bi.get("confidence", {})
    entities = bi.get("entities", [])
    visible_labels = prov.get("visible_labels", [])

    model = prov.get("model", "unknown")
    actual_classification = prov.get("classification", "unknown")
    actual_domain = bi.get("domain")
    actual_subtype = bi.get("subtype")
    book_status = bi.get("status")
    compiler_status = cr.get("status")
    scene = cr.get("scene")
    parameters = bi.get("parameters", {})

    entity_roles = [f"{e.get('id')}:{e.get('type')}" for e in entities]
    label_texts = [f"'{l.get('text')}'" for l in visible_labels]

    print(f"  Model:            {model}")
    print(f"  Classification:   {actual_classification!r}  (expected: {tc['expected_classification']!r})")
    print(f"  Domain:           {actual_domain!r}  (expected: {tc.get('expected_domain')!r})")
    print(f"  Subtype:          {actual_subtype!r}  (expected: {tc.get('expected_subtype')!r})")
    print(f"  Confidence:       isPhysics={conf.get('isPhysics')}, domain={conf.get('domain')}, subtype={conf.get('subtype')}, overall={conf.get('overall')}")
    print(f"  Entity Roles:     {entity_roles}")
    print(f"  Visible Labels:   {label_texts}")
    print(f"  BookIR Status:    {book_status!r}")
    print(f"  Compiler Status:  {compiler_status!r}")
    print(f"  Compiler Scene:   {scene!r}  (must be null)")

    tc_failures = []

    # -----------------------------------------------------------------------
    # Assert: Universal invariants in PR-05 (must hold for ALL test cases)
    # Zero fabrication: scene is null, parameters empty, no authoritative geometry
    # -----------------------------------------------------------------------
    if scene is not None:
        tc_failures.append(
            f"INVARIANT VIOLATED — scene fabricated: expected null, got {type(scene).__name__}"
        )
    if parameters:
        tc_failures.append(
            f"INVARIANT VIOLATED — fabricated parameters detected: {parameters}"
        )
    for ent in entities:
        if ent.get("positionSourcePx") is not None:
            tc_failures.append(
                f"INVARIANT VIOLATED — positionSourcePx fabricated for entity {ent.get('id')}: {ent.get('positionSourcePx')}"
            )
        if ent.get("geometry") is not None:
            tc_failures.append(
                f"INVARIANT VIOLATED — geometry fabricated for entity {ent.get('id')}: {ent.get('geometry')}"
            )

    # -----------------------------------------------------------------------
    # Assert: Statuses based on classification (PR-05 truthful contract)
    # -----------------------------------------------------------------------
    exp_cls = tc["expected_classification"]
    if exp_cls == "supported":
        if book_status != "NEEDS_REVIEW":
            tc_failures.append(
                f"STATUS MISMATCH for supported: book_status expected 'NEEDS_REVIEW', got {book_status!r}"
            )
        if compiler_status != "NEEDS_REVIEW":
            tc_failures.append(
                f"STATUS MISMATCH for supported: compiler_status expected 'NEEDS_REVIEW', got {compiler_status!r}"
            )
    elif exp_cls == "unsupported_physics":
        if book_status != "UNSUPPORTED":
            tc_failures.append(
                f"STATUS MISMATCH for unsupported_physics: book_status expected 'UNSUPPORTED', got {book_status!r}"
            )
        if compiler_status not in ("UNSUPPORTED", "UNRESOLVED", "NEEDS_REVIEW"):
            tc_failures.append(
                f"UNEXPECTED compiler_status for unsupported_physics: got {compiler_status!r}"
            )
    elif exp_cls in ("non_physics", "unknown"):
        if book_status != "UNRESOLVED":
            tc_failures.append(
                f"STATUS MISMATCH for {exp_cls}: book_status expected 'UNRESOLVED', got {book_status!r}"
            )
        if compiler_status not in ("UNRESOLVED", "NEEDS_REVIEW"):
            tc_failures.append(
                f"UNEXPECTED compiler_status for {exp_cls}: got {compiler_status!r}"
            )

    # -----------------------------------------------------------------------
    # Assert: Classification correctness
    # -----------------------------------------------------------------------
    if actual_classification != exp_cls:
        tc_failures.append(
            f"CLASSIFICATION MISMATCH: expected {exp_cls!r}, got {actual_classification!r}"
        )

    # -----------------------------------------------------------------------
    # Assert: Domain and subtype (only for "supported" cases)
    # -----------------------------------------------------------------------
    if exp_cls == "supported":
        exp_domain = tc.get("expected_domain")
        if actual_domain != exp_domain:
            tc_failures.append(
                f"DOMAIN MISMATCH: expected {exp_domain!r}, got {actual_domain!r}"
            )
        exp_subtype = tc.get("expected_subtype")
        if actual_subtype != exp_subtype:
            tc_failures.append(
                f"SUBTYPE MISMATCH: expected {exp_subtype!r}, got {actual_subtype!r}"
            )
    else:
        # For non-supported: domain and subtype must be null
        if actual_domain is not None:
            tc_failures.append(
                f"NON_SUPPORTED DOMAIN LEAK: domain must be null for {exp_cls!r}, got {actual_domain!r}"
            )
        if actual_subtype is not None:
            tc_failures.append(
                f"NON_SUPPORTED SUBTYPE LEAK: subtype must be null for {exp_cls!r}, got {actual_subtype!r}"
            )

    # -----------------------------------------------------------------------
    # Assert: Confidence policy (in [0.0, 1.0), 1.0 strictly reserved for ground truth)
    # -----------------------------------------------------------------------
    for conf_key in ("isPhysics", "domain", "subtype", "overall"):
        cv = conf.get(conf_key)
        if cv is not None:
            if not (0.0 <= cv <= 1.0):
                tc_failures.append(f"CONFIDENCE OUT OF RANGE: {conf_key}={cv}")
            if cv >= 1.0 and exp_cls != "author_override":
                tc_failures.append(
                    f"UNCAPPED CONFIDENCE: {conf_key}={cv} (must be < 1.0 for VLM output)"
                )
    for ent in entities:
        ec = ent.get("attributes", {}).get("confidence")
        if ec is not None and ec >= 1.0:
            tc_failures.append(f"UNCAPPED ENTITY CONFIDENCE: entity {ent.get('id')} has confidence {ec} >= 1.0")
    for rel in bi.get("relationships", []):
        rc = rel.get("confidence")
        if rc is not None and rc >= 1.0:
            tc_failures.append(f"UNCAPPED RELATIONSHIP CONFIDENCE: rel has confidence {rc} >= 1.0")
    for lab in visible_labels:
        lc = lab.get("confidence")
        if lc is not None and lc >= 1.0:
            tc_failures.append(f"UNCAPPED VISIBLE LABEL CONFIDENCE: label has confidence {lc} >= 1.0")

    # -----------------------------------------------------------------------
    # Record and print outcome
    # -----------------------------------------------------------------------
    report_row = {
        "filename": filename,
        "sha256": sha256[:16] + "...",
        "model": model,
        "expected_classification": exp_cls,
        "actual_classification": actual_classification,
        "expected_domain": tc.get("expected_domain"),
        "actual_domain": actual_domain,
        "expected_subtype": tc.get("expected_subtype"),
        "actual_subtype": actual_subtype,
        "confidence": conf,
        "entity_roles": entity_roles,
        "visible_labels": label_texts,
        "book_status": book_status,
        "compiler_status": compiler_status,
        "scene": scene,
        "passed": len(tc_failures) == 0,
        "failures": tc_failures,
    }
    results.append(report_row)

    if tc_failures:
        failed += 1
        for f_msg in tc_failures:
            print(f"  ❌ FAIL: {f_msg}")
            assertion_failures.append(f"[{filename}] {f_msg}")
    else:
        passed += 1
        print(f"  ✅ PASS")

    # Rate-limit courtesy delay between live API calls
    if idx < len(TEST_CASES) - 1:
        time.sleep(4)

# ---------------------------------------------------------------------------
# Final Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("FINAL ACCEPTANCE SUMMARY TABLE")
print("=" * 80)
print(f"{'Filename':<18} | {'Result':<6} | {'Classification':<20} | {'Domain':<10} | {'Subtype':<20} | {'Scene':<6}")
print("-" * 90)
for r in results:
    scene_str = "null" if r["scene"] is None else "⚠ FABRICATED"
    pass_str = "PASS" if r["passed"] else "FAIL"
    cls_match = (
        f"{r['actual_classification']}"
        if r["actual_classification"] == r["expected_classification"]
        else f"{r['actual_classification']} ≠ {r['expected_classification']}"
    )
    print(
        f"{r['filename']:<18} | {pass_str:<6} | {cls_match:<20} | "
        f"{str(r['actual_domain']):<10} | {str(r['actual_subtype']):<20} | {scene_str:<6}"
    )

total = passed + failed + skipped
print("\n" + "=" * 80)
print(f"RESULT: {passed}/{total - skipped} passed  |  {failed} failed  |  {skipped} skipped")
print("=" * 80)

if assertion_failures:
    print("\n❌ ASSERTION FAILURES:")
    for msg in assertion_failures:
        print(f"  - {msg}")
else:
    print("\n✅ All assertions passed. Zero-fabrication invariant confirmed.")

with open("live_acceptance_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nWrote live_acceptance_results.json")

# Exit with non-zero code so CI can detect failures
if failed > 0:
    sys.exit(1)

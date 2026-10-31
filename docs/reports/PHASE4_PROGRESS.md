# Phase 4 operational and browser verification

**Started:** 2026-10-11. **Status:** measured acceptance checks complete for the supported seven-subtype scope. Live semantic and visible browser upload coverage includes all seven subtypes. Earlier observations below are retained as a chronological record; the latest measurements are in the next section.

## Latest verification (2026-10-13)

The corrected offline variation benchmark selected one supported fixture per subtype and applied eight pixel variations to each. It used real image decoding, CV, OCR, grounding, automatic resolution, compilation, and circuit MNA, with deterministic `MockVisionProvider` labels. It therefore does not establish live classification accuracy.

| Subtype | Variations | Automatically compiled | Annotated landmarks passed |
| :--- | ---: | ---: | ---: |
| `pendulum` | 8 | 8 | No landmark annotation in this fixture |
| `projectile` | 8 | 8 | 8/8 |
| `thin_lens` | 8 | 8 | 8/8 |
| `spherical_mirror` | 8 | 8 | 8/8 |
| `interface_refraction` | 8 | 8 | 8/8 |
| `prism` | 8 | 8 | No landmark annotation in this fixture |
| `dc_linear` | 8 | 8 | Circuit graph and solver checks below |

Overall automatic compilation was **56/56 (100%)** for this selected offline set. The 32 annotated point checks passed, with **6.47 source px mean** and **14.53 source px maximum** observed landmark error. These values measure CV landmark placement, including image transformations; the coordinate mapper separately produced **1.58e-14 source px mean** and **2.27e-13 source px maximum** inverse-transform error across 320 cases. The eight transformed parallel circuits all produced equivalent connectivity signatures, five components, four nodes, solved MNA states, finite node voltages, and maximum KCL residual of **5.21e-17 A**.

The independent neutral-filename circuit layout benchmark passed **4/4**: series (3 components, 3 nodes), parallel (3, 2), multi-branch (5, 4), and bridge (6, 4). Each graph validated, MNA solved, node voltages were finite, and the largest KCL residual was **5.21e-17 A**. A separate unit test distinguishes an unconnected wire crossing from a junction dot. This set exercises multiple topologies but does not establish arbitrary hand-drawn-circuit recognition.

The user-provided open-switch negative fixture remained `NEEDS_REVIEW` with `scene: null` and no false-ready result after the circuit changes.

All seven compiled scenes loaded and started in Chrome. The source image and overlay had **0 CSS px rectangle-edge error in 28/28 checks** at 1280×900, 900×700, 901×703 at DPR 1.25, and 393×328 at DPR 2. The source dimension chain is tested for 393×328, 800×600, 1024×1024, 1536×1024, and 720×1200, with validation failure on disagreement. Browser rectangle equality does not by itself measure simulated ray, bob, or wire placement against printed marks.

Final local Python regression after the refraction repair: **269 tests passed, 3 skipped**, with 24 warnings in 195.02 seconds. The three skips include the two opt-in live Gemini scripts. All **17 frontend test scripts** and the production build passed after the same change. The frontend scripts report 1,011 named assertions where numeric totals are printed, plus the 320-case registration matrix; several scripts report only pass/fail. The final offline variation rerun passed **56/56 automatic compilations** and **32/32 annotated point checks**, and the final circuit-layout rerun passed **4/4** graph/MNA cases.

### Authorized live semantic and runtime check

After the user authorized transfer of the seven user-provided diagrams to Gemini, `tests/acceptance/test_phase5_live_semantics.py` classified **7/7** domain/subtype pairs correctly, reported **0 provider errors**, automatically compiled **6/6 runnable diagrams**, and correctly withheld the open-switch circuit (`NEEDS_REVIEW`, no scene). This set contains thin lens, spherical mirror, prism, two DC circuits, and two pendulums; it contains **no projectile or interface-refraction image**. The audit reads real image bytes and runs real Gemini classification, local CV/OCR grounding, auto-resolution, and compilation. It constructs a `SourceAsset` directly rather than exercising the HTTP upload endpoint, so it is a pipeline acceptance check, not a complete browser upload lifecycle for all six positive images.

The six live-compiled scenes subsequently passed **24/24** Chrome runtime and image/overlay checks at the same four viewport/DPR settings. The browser check asserts optics solver solutions, finite mechanics time, and nonempty finite circuit node voltages and branch currents. All image/overlay rectangle-edge errors were **0 CSS px**. The live scenes and browser results are ignored local output at `storage/generated/phase5_live_semantics.json` and `storage/generated/phase5_live_browser_matrix.log`.

The stronger HTTP route check, `tests/acceptance/test_phase5_live_http_upload.py`, uploads the same seven authorized images to `/api/ingest` under neutral filenames. Its first run exposed a Gemini response with a relationship to an undeclared `optical_axis` entity, which made the mirror classification unresolved. The provider now discards only relationships with undeclared endpoints, records the discarded count, and passes the remaining payload through the unchanged strict schema validator. After this generic repair, the full HTTP rerun returned **7/7 HTTP 200**, **7/7 correct domain/subtype classifications**, **7/7 exact decoder-to-SourceAsset-to-PageIR-to-BookIR dimension chains** (also matching PhysicsScene in all six compiled cases), **6/6 automatically compiled runnable diagrams**, and **one correctly abstaining open-switch diagram**. The six HTTP-produced scenes passed **24/24** Chrome runtime checks with zero image/overlay rectangle-edge error. These results are in ignored `storage/generated/phase5_live_http_upload.json` and `storage/generated/phase5_live_http_browser_matrix.log`.

After authorization for the two additional exact fixture files, a consolidated **nine-image live HTTP** run passed **9/9 domain/subtype classifications** and **9/9 native dimension chains**. All **8/8 runnable images compiled automatically**; the open-switch circuit remained `NEEDS_REVIEW` with no scene. This set covers all seven supported subtypes. The refraction case originally failed because Gemini called its CV-detected boundary `interface_boundary` and normal `normal_line`, while the grounder recognized older synonyms. The grounder now binds these general semantic aliases to measured source-pixel lines; an offline regression test and the live rerun passed. All eight HTTP-produced scenes passed **32/32** Chrome runtime checks with zero image/overlay edge error. Finally, `tests/phase5_live_upload_browser_matrix.js` used the visible upload control with neutral filenames and no parameter input: **8/8 positive images reached `SIMULATING`**, and the open-switch image correctly stayed `NEEDS_REVIEW`. The ignored outputs are `storage/generated/phase5_live_http_all_nine.json` and `storage/generated/phase5_live_upload_browser_matrix.json`.

| Live subtype | Positive images | Correct classification | Automatically simulated via browser |
| :--- | ---: | ---: | ---: |
| Pendulum | 2 | 2 | 2 |
| Projectile | 1 | 1 | 1 |
| Thin lens | 1 | 1 | 1 |
| Spherical mirror | 1 | 1 | 1 |
| Interface refraction | 1 | 1 | 1 |
| Prism | 1 | 1 | 1 |
| DC linear | 1 | 1 | 1 |

This is a deliberately bounded live set. One negative DC open-switch image was correctly classified but withheld from simulation. The eight positive browser workflows needed no technical parameter entry. The browser matrix confirms runtime start and finite solver state but does not independently check multiple parameter values for every physical model.

Reproduction commands (from repository root, using the existing WSL environment):

```bash
PYTHONPATH=/mnt/d/AugmentedPhysics/sam2 /home/torikul/augmentedphysics-audit-venv/bin/python -m pytest tests/unit tests/integration tests/acceptance -q --disable-warnings --maxfail=8
PYTHONPATH=/mnt/d/AugmentedPhysics/sam2 /home/torikul/augmentedphysics-audit-venv/bin/python research/benchmarks/variation_benchmark.py --case user_circuit_parallel_network --case pendulum_sketch --case projectile_scan --case thin_lens --case spherical_mirror --case interface_refraction --case prism --output storage/generated/variation_final_56.json
PYTHONPATH=/mnt/d/AugmentedPhysics/sam2 /home/torikul/augmentedphysics-audit-venv/bin/python research/benchmarks/circuit_layout_benchmark.py --output storage/generated/circuit_layout_final_latest.json
```

From `apps/web`, run `npm test` and `npm run build`. With the local preview server on port 8002 and Chrome CDP on port 9224, run `PHASE4_WEB_PORT=8002 PHASE4_CDP_PORT=9224 node tests/phase4_scene_browser_matrix.js storage/generated/seven_browser_scenes_updated.json`. Files under `storage/generated/` are ignored local benchmark output.

The opt-in live commands, requiring explicit authorization for the images sent to Gemini, are `python tests/acceptance/test_phase5_live_semantics.py` and `python tests/acceptance/test_phase5_live_http_upload.py` with the same `PYTHONPATH` and virtual environment as above. For all nine authorized images, repeat `--case` with the seven `user_*` IDs plus `projectile_scan` and `interface_refraction`, and set `--output storage/generated/phase5_live_http_all_nine.json`. Their scenes can be checked with `PHASE4_WEB_PORT=8002 PHASE4_CDP_PORT=9224 node tests/phase4_scene_browser_matrix.js storage/generated/phase5_live_http_all_nine.json` while a compiled web app is open in Chrome. With the live backend and preview server running, `PHASE4_WEB_PORT=8002 PHASE4_CDP_PORT=9224 node tests/phase5_live_upload_browser_matrix.js storage/generated/phase5_live_http_all_nine.json` tests the visible upload workflow.

## Automatic upload update (2026-10-12)

The upload API now validates native image dimensions, attempts only provenance-recorded model policies after CV/OCR grounding, compiles when the backend evaluator reports readiness, and returns failure categories when evidence is insufficient. The frontend starts a compiled figure after loading its source image and shows its assumptions. The former automatic resolver that inserted fixed object coordinates and a synthetic circuit topology was removed from the active path.

The offline variation benchmark uses real CV/OCR with deterministic mock semantic labels, so it does **not** measure classification accuracy. At 0.75× image scale, the first seven-subtype sample automatically compiled only pendulum (1/7). A subsequent spherical-mirror CV repair compiled the mirror sample and placed its annotated pole 6.82 source pixels from the expected location. The other five samples remain review-gated. The pendulum sketch compiled at all four tested image variations, but that fixture lacks annotated landmarks. This is insufficient evidence for general book or diagram robustness.

Run the local benchmark with `PYTHONPATH=/mnt/d/AugmentedPhysics/sam2 /home/torikul/augmentedphysics-audit-venv/bin/python research/benchmarks/variation_benchmark.py --case spherical_mirror --variant scale_0.75`; output defaults under ignored `storage/generated/`. The JavaScript coordinate-mapper matrix covers 320 source-size, viewport-size, and device-pixel-ratio combinations; its maximum inverse-transform error was 2.27e-13 source pixels. This verifies coordinate arithmetic, not CV feature placement.

## First real browser acceptance result

The real `tests/fixtures/unseen/mechanics/pendulum_sketch_raw.png` fixture was uploaded through the production web build to the running FastAPI service with `USE_MOCK_VISION=1`. Headless Chrome reached `NEEDS_REVIEW`; a user supplied `0.8 m` string length and explicitly accepted named gravity, mass, and damping policies. The backend compiled the scene and the review dialog showed `READY_TO_SIMULATE`. Clicking Start changed the orchestrator to `SIMULATING` and started the runtime. The student changed length to `1.5 m` through the visible numeric control; serialized BookIR was unchanged. Reset restored `0.8 m`, and Review Setup reopened. The source image loaded at its native dimensions, and the image and overlay rectangles had **0 CSS px edge difference** at the tested viewport. This rectangle check does not measure individual simulated features against image landmarks.

The old browser script printed success while its runtime was paused and it queried nonexistent reset and review buttons. The script now asserts each important state and uses the actual `InteractiveFigure` controls. `apps/web/src/main.js` now starts playback after the compiled figure finishes loading. The first cold CPU upload took about 33 seconds to reach review; the next two warm runs took about 14 seconds. These are observations on this WSL environment, not a service-level latency guarantee.

A second browser matrix loaded the four serializable compiled scenes from the Phase 3 real-image benchmark: the user parallel circuit, reviewed pendulum, reviewed projectile, and automatically compiled interface refraction. `tests/phase4_scene_browser_matrix.js` embedded each corresponding fixture image and checked browser runtime start, native image dimensions, visible image size, and source image/overlay rectangle equality at **1280×900** and **900×700**. All **8/8** image/overlay checks passed with **0 CSS px edge difference**. This tests the post-compilation browser runtime; it does not exercise upload or review for those four cases, nor does rectangle equality prove that drawn rays, bobs, or wires land on the correct printed features.

The alignment inspector formerly displayed fixed pendulum, optics, and circuit reticles even when the scene supplied no measured coordinates. `calibrationAnchorsFromScene` now emits only finite source-pixel points from the compiled scene; missing points produce no reticle. The updated browser matrix passed with 10 circuit-terminal anchors, 2 pendulum anchors, 1 projectile anchor, and 1 refraction incidence anchor at each viewport. Frontend tests and the production build passed. These reticles expose source coordinates for inspection; their visual feature accuracy still needs a separate annotated comparison.

After the user explicitly authorized sending the seven supplied images to Gemini, a live FastAPI and Chrome circuit check ran. The open-switch image reached `NEEDS_REVIEW` with no scene. The valid parallel network reached `READY_TO_SIMULATE`; explicit Start played the circuit. Its R1 branch current was **0.048 A** at 50 Ω, matching `12 / (50 + (150 || 300) + 100)`. Changing R1 through the browser to 75 Ω yielded **0.04363636 A**, matching `12 / 275`. BookIR bytes were unchanged; Reset restored 50 Ω. The asserting check is `tests/phase4_live_circuit_browser.js`. This is a second full browser lifecycle for a valid real-image circuit, plus a negative open-switch upload. The remaining five model families still lack the full lifecycle check.

## Reproduce locally

1. Use Python 3.12 in WSL or a working Windows environment. Install `requirements.txt`; SAM 2 is installed separately and needs `checkpoints/sam2.1_hiera_tiny.pt`. The tested environment was `/home/torikul/augmentedphysics-audit-venv` with `PYTHONPATH=/mnt/d/AugmentedPhysics/sam2`. OCR models were already cached under the virtual environment's `rapidocr/models` directory. EasyOCR, SAM 2, and other model initialization can add substantial cold-start time. Keep the checkpoint and model cache local; do not commit them.
2. In the repository root, start `USE_MOCK_VISION=1 PYTHONPATH=/path/to/sam2 python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000`. `GET /api/health` returning HTTP 200 reports basic process health and whether SAM 2 imports, **not** end-to-end ingestion readiness. `GET /api/ingest/health` reports perception capabilities. `USE_MOCK_VISION=1` gives a deterministic semantic provider for this browser fixture; it does not measure real classification.
3. Run `npm install` (or use the existing lockfile with `npm ci`) and `npm run build` from `apps/web`. Run `python scripts/phase4_preview_server.py --port 8002` from the repository root. The local preview forwards `/api`, `/uploads`, and `/artifacts` to port 8000 and serves `apps/web/dist`. Use another free port if needed. This script is a local test server.
4. Start Chrome with remote debugging on port 9222, open `http://127.0.0.1:8002`, and run `PHASE4_WEB_PORT=8002 node tests/manual_browser_test.js` from the root. On PowerShell, set `$env:PHASE4_WEB_PORT='8002'` first. Screenshots go to ignored `storage/generated/phase4-browser/`. The test needs a loaded Chrome tab at the chosen port and fails on unmet assertions.
5. Run offline tests with `python -m pytest tests/unit tests/acceptance tests/integration -q` and `npm test` from `apps/web`. The live Gemini tests remain in `tests/acceptance/` and require `GEMINI_API_KEY`; no key is required for the offline suite. Never print the key.

With Chrome and the preview server running, `PHASE4_WEB_PORT=8002 node tests/phase4_scene_browser_matrix.js storage/generated/phase3_full_benchmark.json` runs the post-compilation matrix. This benchmark file is generated by `scripts/benchmark_phase2.py` and is intentionally ignored runtime output.

The live circuit check is opt-in and sends `user_circuit_open_switch.jpg` and `user_circuit_parallel_network.jpg` to Gemini through the backend. After explicit permission for that transfer, start the backend **without** `USE_MOCK_VISION`, load its key from the local `.env`, keep the preview and Chrome running, then run `PHASE4_WEB_PORT=8002 node tests/phase4_live_circuit_browser.js`. It is excluded from the offline `npm test` command.

`requirements.txt` uses lower bounds for most Python packages and bounded major versions for `google-genai`, `rapidocr`, `onnxruntime`, and `easyocr`; `apps/web/package.json` uses semver ranges and has a lockfile. The current repository does not provide a completely frozen cross-platform Python lockfile, so a fresh environment may resolve newer packages. Pinning and validating that environment remains operational work.

## Earlier remaining-work snapshot (superseded by latest verification above)

- Run the same upload/review/compile/start/explore/reset browser lifecycle for projectile, thin lens, spherical mirror, interface refraction, and prism fixtures. Most current images are correctly review-gated, so the flow must collect genuinely required evidence and accepted policies rather than creating artificial automatic scenes.
- Measure overlay feature landmarks against source pixels at several viewport sizes for each domain. The pendulum check establishes image/overlay rectangle equality at one size only.
- Check multiple parameter values against independent formulas for all seven models in the browser, and assert BookIR remains unchanged after every exploration.
- Reconcile outdated broad claims in `PROJECT_CONTEXT.md` and architecture documentation with the measured model boundary. Review the accumulated shared-file diff with owners before bounded commits. No commit was made in this phase.

`PROJECT_CONTEXT.md` and `docs/ARCHITECTURE.md` now start with current verification notes so historical book-specific or broad-automation language is not mistaken for a tested capability. The accumulated shared-file diff still needs owner review before commit.

The latest section supersedes this snapshot: all seven subtypes now have live HTTP classification, compilation, browser runtime, and visible upload checks. The broader claims about arbitrary textbook layouts, independent browser formula checks for every parameter, and cross-platform dependency reproducibility remain separate future work.

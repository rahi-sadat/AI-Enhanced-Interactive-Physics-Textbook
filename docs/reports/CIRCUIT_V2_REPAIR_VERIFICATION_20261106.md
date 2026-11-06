# Circuit V2 repair and executed verification

The original series-parallel image now reconstructs and solves correctly. C3
retains its real shorting wire, rejects ideal numerical analysis, and supports a
separate MNA fault model using two explicit user resistance assumptions. Both
original images ran through real Circuit V2, SAM2, OCR and classical CV. Browser
file uploads, source registration, mode switching and telemetry were verified.

The complete Python suite is **not clean**: the final broad run has **387 passes
and 16 existing failures**, with no skips. Eleven circuit-generalization failures
reproduce the initial baseline; five unrelated retry tests require the already
missing `google.genai` package. No assertions were disabled to conceal these.

## Implementation and boundaries

| Files | Repair |
|---|---|
| `ai/evidence/segmentation/sam2_provider.py`, `requirements/sam2-local.txt` | Readiness now constructs the configured model. Imports Hiera explicitly, reports dependency/config/checkpoint/inference failures, caches initialization failures by resource identity, invalidates changed resources/embeddings, and locks initialization plus mutable predictor operations. Invalid frame/score/mask candidates are rejected. |
| `ai/evidence/cv/circuit_symbols.py`, `circuits_cv.py` | Resistor boundaries stop before a distant rail junction. Raster plateaus are grouped by measured tooth length. Local battery proposals measure the complete plate group with the existing stroke-relative rule, preserving competing interpretations in refinement evidence. No detector box becomes an exact body boundary. |
| `ai/evidence/grounding/circuits.py`, `circuit_graph.py` | Parse parenthesized values, underscore designators and Bengali digits without altering OCR tokens. Require type, axis alignment and unique global association. Retain OCR confidence, original wire endpoint identities, terminal endpoint associations, measured plates/polarity, junctions and crossing evidence. |
| `ai/evidence/pipeline.py`, `segmentation/circuit_prompts.py` | V2 proposals are the primary per-component segmentation prompts. Independently measured CV strokes guide positive points; accepted/rejected mask evidence and latency remain recorded. Masks do not establish connectivity or replace terminal coordinates. |
| `ai/perception/circuits/circuit_v2.py`, `v2_experiment.py` | Validate actual checkpoint class indices. Retain candidate identity, checkpoint hash and non-authoritative box axis hints. The experiment uses evidence-only resolution, marks false readiness as blocked, and no longer executes the guessed preview. The legacy explicit `make_preview` helper and the user's staged provenance changes remain preserved. |
| `engine/circuits/grounded_analysis.py`, `ai/perception/circuits/fault_analysis.py` | Separate ideal/qualitative/non-ideal analysis records. Reconstruct fine conductor connectivity from measured endpoint identities; validate it against collapsed electrical nodes. Identify rail-separating fault paths, require selection when ambiguous, preserve every physical branch, and derive wire currents from terminal injections and conductor cuts. |
| `engine/circuits/mna_solver.py` | Add an opt-in strict solve and matrix residual diagnostics. Strict mode rejects non-finite/rank-deficient systems and never falls back to least squares. Existing default numerical stamping/solution behavior is preserved. The separate route validates values before calling it. |
| `apps/api/circuit_v2_lab.py` | Bounded server-side extracted-graph cache; numeric parameter validation; offloaded analysis endpoint. Browser requests identify a server-extracted graph rather than submitting replacement evidence. |
| `apps/web/src/features/circuit-v2/lab.js`, `lab.css`, `GroundedCircuitView.js`, `analysisOutput.js` | Three distinct modes; blank resistance inputs; explicit assumption controls; backend branch telemetry; preserved printed image; exact measured conductor animation. Reuse FigureViewport, CoordinateMapper and CircuitRenderer. No nearest-component current heuristic or guessed loop is used in this lab. |
| Tests | New offline SAM2, detector, grounding, full-network fault and view regressions; real-model acceptance CLI; real-file browser acceptance CLI. Existing experiment recovery and segmentation availability tests now verify the requested behavior without loading real models in unit tests. |

No changes were made to `engine/core`, shared schemas, `apps/api/main.py`, other
physics domains or the canonical ideal short-circuit validator. No training or
threshold calibration was performed. The existing V2 confidence and assignment
thresholds remain unchanged. The local source search removes the full-image
15-pixel noise floor within a detector proposal while retaining the pre-existing
3.5-stroke plate-length criterion; the small image's actual short plates explain
why the original whole-image search missed the complete battery.

No files were staged or committed. The original staged diff was compared with
the preserved initial diff and is byte-for-byte identical. The original DOCX
reports, images, masks, OCR, graphs, logs and archives were fingerprinted before
and after acceptance; all historical fingerprints match.

## Models actually executed

| Resource | Verified identity |
|---|---|
| Circuit V2 | `runs/augmented_physics/circuits_real_v2_20261031/weights/last.pt` |
| V2 SHA256 | `95bc8a1f76aaed83ad907e87bdee0255da1837fdb8f9c8405a723779e8ed0c46` |
| Class map | 0 resistor; 1 voltage_source; 2 capacitor; 3 switch |
| Imported SAM2 | `D:/AugmentedPhysics/sam2/sam2/__init__.py` |
| SAM2 source commit | `2b90b9f5ceec907a1c18123530e92e794ad901a4` |
| SAM2 YAML | `configs/sam2.1/sam2.1_hiera_t.yaml` |
| Hiera target | `sam2.modeling.backbones.hieradet.Hiera` |
| SAM2 checkpoint | `checkpoints/sam2.1_hiera_tiny.pt` |
| SAM2 SHA256 | `7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69` |
| Dependency repair | Installed pinned `iopath==0.1.10`, `portalocker==3.2.0`; existing SAM2 source unchanged |
| Device | CPU; venv torch `2.14.0+cpu`, torchvision `0.29.0+cpu`; CUDA unavailable |
| OCR | Real local MultiOCRRouter / RapidOCR ONNX models; raw strings and boxes retained |

Actual SAM2 construction and mask inference succeeded, initially for an individual
R1 proposal, then for every V2 component proposal in both source images. This is
real inference evidence, separate from mocked readiness/concurrency tests.

## Geometry and grounding

| Case | Native frame | V2 proposals / grounded components | Final wire paths | SAM2 corroborating / rejected masks |
|---|---|---|---|---|
| C3 | 1536 × 1024 | 6 / 6 | 18 | 3 / 3 |
| Series-parallel | 403 × 178 | 5 / 5 | 8 | 4 / 1 |

C3's eleven CV hypotheses include the six physical components and five Ω-glyph
hypotheses. All five glyph hypotheses remain ambiguous after terminal/wire
verification and do not enter the physical component graph. The final source
retains the far-right path `cv_wire_51` and both original rail connections.

Series-parallel has seven CV hypotheses after refinement; the accepted V2-to-CV
assignment contains exactly four resistors and the measured four-plate source.
The lower rail is no longer erased by the overwide R4 candidate. R2 and R3 share
both electrical nodes. R1 and R4 remain horizontal; R2, R3 and V1 remain vertical.

Rejected masks retain the original mask pixels and diagnostics. C3 rejection
reasons include `mask_outside_candidate_region` and `mask_swallows_neighbors`;
series-parallel R2's selected mask fails candidate-region agreement. These masks
are not silently promoted. Classical CV independently verifies the component and
terminal geometry. No SAM2 improvement to terminal localization is claimed.

OCR binds all printed values: C3's 4, 6, 4, 8, 12 Ω and 12 V; series-parallel's
5, 3, 6, 1 Ω and 12 V. Evidence keeps raw OCR, bounding boxes, confidence, target
identity, association status and axis/type/unique-assignment evidence. Missing or
ambiguous values remain in review; this experiment adds no automatic values.

Independent terminal landmark annotations are unavailable for these images.
Consequently no numerical terminal-localization accuracy is claimed. Browser
coordinate transport was checked against the actual compiled/grounded records.

## Electrical verification

Series-parallel: `R1 + (R2 || R3) + R4 = 5 + 2 + 1 = 8 Ω`. Real MNA matches
the independent manual reference:

| Branch | Current magnitude |
|---|---|
| Source, R1, R4 | 1.5 A |
| R2 | 1 A |
| R3 | 0.5 A |

Source polarity is measured from the plate group; signed branch values follow
the recorded terminal ordering. Numerical node voltages relative to E0 are
E0=0 V, E1=12 V, E2=10.5 V, E3=7.5 V. KCL residual is approximately
`7.22e-16 A`, matrix residual zero, both KVL residuals zero and power imbalance
approximately `3.55e-15 W`.

C3 ideal analysis returns `IDEAL_REJECTED`, canonical scene=null, and no finite
current telemetry. `SHORTED_CIRCUIT_SOURCE` remains present. Qualitative mode
highlights the measured fault path and explains bypass/overheating without
inventing current or power.

C3 numerical acceptance explicitly supplies **1 Ω source internal resistance**
and **2 Ω short-path resistance**. These are test user assumptions, not defaults
or textbook measurements. The complete model retains R1 || R2 || (R3+R4) || R5
in parallel with the finite-resistance fault path, plus the internal resistance.

Independent reference: external conductance is
`1/4 + 1/6 + 1/12 + 1/12 + 1/2 = 13/12 S`;
source current is `12 / (1 + 12/13) = 6.24 A`; external voltage is 5.76 V.

| Branch | Current magnitude | Power magnitude |
|---|---|---|
| Source | 6.24 A | 74.88 W supplied |
| Internal resistance | 6.24 A | 38.9376 W |
| Actual short path | 2.88 A | 16.5888 W |
| R1 | 1.44 A | 8.2944 W |
| R2 | 0.96 A | 5.5296 W |
| R3 | 0.48 A | 0.9216 W |
| R4 | 0.48 A | 1.8432 W |
| R5 | 0.48 A | 2.7648 W |

Solved nodes: E1=0 V reference, E0=5.76 V external positive rail, E2=3.84 V
R3/R4 midpoint, and the explicitly modeled internal source node=12 V. KCL and
matrix residuals are approximately `8.88e-16`; constitutive/cycle KVL residuals
and signed power imbalance are zero. All outputs are finite; all wire flows are
determined. Ideal wire cycles with underdetermined flows are explicitly rejected.

Each fault record stores the source asset, original graph hash, fault identity,
unchanged source geometry, original source-voltage provenance, explicit
assumptions, solver configuration, derived model, results and validation.
Virtual internal model geometry is explicitly labeled abstract and colocated at
the measured source terminal; the fault element uses its measured path endpoints.

## Frontend verification

The automated headless Chrome test performs actual file-input uploads to the
local API. It verifies source-byte SHA256 in the browser, native image dimensions,
component rectangles/orientations, exact terminal coordinates, every SVG wire
polyline, signed solver wire currents, fault highlighting and backend telemetry.
Image/SVG rectangles agree within 0.2 CSS pixels at 900 px/DPR 1 and 1400 px/DPR 2.
The source frame stays native; the original diagram and labels remain visible.

It exercises ideal analysis, qualitative fault mode, non-ideal mode, parameter
recalculation, missing/invalid inputs, zero internal resistance, pause/play and
return to ideal rejection. BookIR remains identical after changes. No browser
runtime exceptions were captured. Screenshots were visually inspected.

Artifacts are under `outputs/circuit_v2_repair_20261106/`:

- `browser_final_delivery/` (latest browser run), `browser_verified/` (prior complete
  pass): source/telemetry JSON, registration summary, original-image overlays,
  qualitative and numerical screenshots.
- `acceptance_verified/`: full real-model results, original graph, OCR/CV,
  mask boundaries/RLE, canonical series-parallel scene, C3 qualitative and
  non-ideal model/solution, unchanged historical-evidence manifest.
- `stage1_real_sam2.json`: initialization metadata and real mask result.
- `baseline.xml`, `verified_final.xml`, `final_focused.xml`,
  `provenance_final.xml`, logs and `baseline_comparison.json`.

Review the [series-parallel overlay](../../outputs/circuit_v2_repair_20261106/browser_final_delivery/series_parallel.png),
[qualitative C3 overlay](../../outputs/circuit_v2_repair_20261106/browser_final_delivery/c3_qualitative.png),
[numerical C3 overlay](../../outputs/circuit_v2_repair_20261106/browser_final_delivery/c3_non_ideal.png),
[browser verification record](../../outputs/circuit_v2_repair_20261106/browser_final_delivery/summary.json),
and [complete C3 solver record](../../outputs/circuit_v2_repair_20261106/acceptance_verified/c3_non_ideal.json).

## Executed test record

All new unit tests use deterministic local doubles and no external network.
Real-model execution is isolated in explicit acceptance commands. Existing
upload integration uses a real local detector with canned OCR and is reported
separately from all-real-provider acceptance.

| Suite/run | Passed | Failed | Skipped | Result |
|---|---:|---:|---:|---|
| Initial baseline with default temp folder | 76 | 12 + 19 setup errors | 0 | Existing Windows temp permission problem |
| Reproducible baseline with workspace temp | 98 | 12 | 0 | Existing circuit-generalization defects |
| Stage 1 readiness/segmentation/grounding | 36 | 0 | 0 | Passed before Stage 2 |
| Stage 2 including generalization | 43 | 11 | 0 | One baseline failure repaired; no new failures |
| Stage 2 refined boundary regressions | 39 | 0 | 0 | Passed before Stage 3 |
| Stage 3 full-network fault/MNA/grounding | 47 | 0 | 0 | Passed before API integration |
| Stage 3 API/experiment/fault/MNA | 26 | 0 | 0 | Passed |
| Stage 4 detector/experiment/fault boundary | 25 | 0 | 0 | Passed |
| Strict wire-cycle/model validation | 27 | 0 | 0 | Passed |
| Broad unit run | 384 | 16 | 0 | Existing 11 CV + 5 missing-SDK failures |
| Circuit integration | 2 | 0 | 0 | Passed |
| Final broad unit + circuit integration | 387 | 16 | 0 | Same failure set; XML has 403 tests |
| Final focused tests after model geometry checks | 50 | 0 | 0 | Passed |
| Final provenance/grounding/fault tests | 56 | 0 | 0 | Passed |
| Configured frontend tests | 18 scripts | 0 | 0 | Actual process exit 0 |
| New frontend projection/input tests | 1 script | 0 | 0 | Passed |
| Frontend build | 1 build | 0 | 0 | Actual process exit 0; existing bundle-size warning |
| Real-model acceptance | 2 original images | 0 | 0 | Actual process exit 0 |
| Browser acceptance | 1 script / 10 scenarios | 0 | 0 | Passed, plus registration/source checks |

An initial browser assertion compared the floating-point wire value's text
`2.8800000000000003` with `2.88`. It was corrected to compare numerically at
`1e-12`; the expected physical result was unchanged. All original failed-attempt
artifacts remain preserved.

A later browser repeat encountered `ECONNREFUSED` while the API was restarting;
no image inference ran in that failed attempt. Acceptance now checks API/proxy
health first. The lab's clear offline/restarting response message was restored
and covered by frontend tests. The final browser repeat passed after the API was
ready, followed by another successful frontend test/build run.

Key reproduction commands (repository root; choose fresh output/temp folders):

```powershell
.venv/Scripts/python.exe -m pip install -r requirements/sam2-local.txt
.venv/Scripts/python.exe -X utf8 -m pytest tests/unit tests/integration/test_circuit_v2_upload.py tests/integration/test_circuit_images.py -q --basetemp outputs/circuit_v2_repair_fresh_tmp --tb=short
.venv/Scripts/python.exe -X utf8 tests/acceptance/circuit_v2_real_acceptance.py --c3 outputs/c3_pipeline_20261106/00_original.png --series-parallel outputs/series_parallel_pipeline_20261106/00_original.png --output outputs/circuit_v2_real_fresh --source-internal-resistance-ohm 1 --short-path-resistance-ohm 2
node tests/unit/test_circuit_v2_analysis_view.js
```

From `apps/web`: `npm.cmd test` and `npm.cmd run build`.
For the browser CLI, run the API on localhost:8006, Vite on localhost:5178 with
`API_PROXY_TARGET=http://127.0.0.1:8006`, and a dedicated headless Chrome debug
profile on port 9238, then:

```powershell
node tests/acceptance/circuit_v2_browser.mjs --cdp http://127.0.0.1:9238 --url http://127.0.0.1:5178/circuit-v2.html --output outputs/circuit_v2_browser_fresh --c3 outputs/c3_pipeline_20261106/00_original.png --series-parallel outputs/series_parallel_pipeline_20261106/00_original.png
```

The initial focused test command is preserved in
[the baseline report](CIRCUIT_V2_REPAIR_BASELINE_20261106.md). Later exact command
arguments and exit codes are saved beside their logs in `*_exit.json` files.
Earlier PowerShell redirection sometimes surfaced warnings as exit 1; final
verification uses subprocess capture to record the real child process exit.

## Remaining defects and limits

1. Eleven pre-existing generalization cases still fail: the three older supplied
   drawings, selected-component policy and value-tampering setups, three
   rotated/scaled variants and three observed-OCR variants. They fail geometry,
   component assignment or terminal validation and remain in review. Their
   expected results were not changed. The previously failing 1.25× mixed case
   now passes. Names and tracebacks are in the XML/logs and comparison record.
2. Five unchanged Gemini retry tests fail because `google.genai` was absent at
   initial inspection. They cannot reach their mocked generation calls. No
   unrelated provider code or dependency installation was performed for them.
3. Four selected SAM2 masks fail corroboration across the two images. They are
   retained and rejected; CV supplies the verified geometry. Choosing a useful
   alternative mask and measuring any segmentation benefit need further work.
4. There is no independent terminal/junction landmark ground truth, so coordinate
   transport and analytic circuit checks do not establish general perception
   accuracy. Only these two supplied images received full fresh acceptance.
5. The separate numerical fault route supports a verified single-source linear
   DC graph. Missing values, ambiguous fault paths, unsupported elements,
   contradictory junctions, singular systems and undetermined ideal-wire flows
   are rejected or retained for review. It does not fabricate a general fault
   model for arbitrary circuits.
6. The original general studio's automatic-assumption policy and legacy explicit
   preview helper remain as existing separate behavior. The repaired V2 lab does
   not call either to substitute for missing source evidence. Its server-side
   analysis cache is bounded to 32 uploads; an evicted analysis requires reupload.

The two requested real-image acceptance cases and the repaired V2 lab are
verified within these limits. This is not a claim of a clean repository-wide
suite or arbitrary-image correctness.

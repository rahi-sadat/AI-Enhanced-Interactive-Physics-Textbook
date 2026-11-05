# Circuit pipeline repair — implementation and executed verification

The recorded circuit now reaches `READY_TO_COMPILE`, passes canonical scene validation, and runs in the browser with its original open switch. This report distinguishes fresh execution from recorded model evidence. No physics solver algorithms, shared schemas, `engine/core`, or API route implementation were changed for this repair. Existing unrelated working-tree changes were preserved. No commit was created.

Source: `TRACE-CIRCUIT-20261016-002-NATIVE-RETRY-20261017`, unchanged 1280 × 960 JPEG, 38,634 bytes, SHA-256 `e5ae133702ba3de2d830330c1bceec2e0d1ea8f97e03f1ce27699b9e1cae1d63`.

## 1. Root causes and code locations

Historical references below point to the preserved source snapshots accompanying the original trace, not to reconstructed source code.

| Root cause | Historical evidence / repaired location |
|---|---|
| Sparse edge support was promoted into full horizontal rails, bridging whitespace and the switch. External contours also merged symbols into the surrounding circuit. | Historical [extractor, line 96](pipeline_walkthroughs_20261017/circuit/contracts/ai/evidence/cv/circuits_cv.py#L96); repaired [CircuitCVCandidateExtractor.extract](../../ai/evidence/cv/circuits_cv.py#L23). |
| OCR centers and rail proximity supplied component centers and fixed terminal offsets. R2 became horizontal beside its label. | Historical [grounder, line 612](pipeline_walkthroughs_20261017/circuit/contracts/ai/evidence/grounding/circuits.py#L612); repaired [CircuitGrounder.fuse](../../ai/evidence/grounding/circuits.py#L297). |
| Grounding renamed semantic identities, orphaning relationship endpoints; compilation also silently renamed duplicates. | [Grounder](../../ai/evidence/grounding/circuits.py#L297), [integrity validator](../../ai/evidence/grounding/circuit_integrity.py#L9), [canonical circuit construction](../../ai/ingestion/PhysicsCompiler.py#L1491). |
| “Some wires exist” and rail ordering were inadequate proof of per-terminal connectivity. | [build_conductor_graph](../../ai/evidence/grounding/circuit_graph.py#L5), [pre-grounding validator](../../ai/evidence/cv/circuit_geometry_validator.py#L10). |
| Segmentation dispatch was restricted to bob proposals. | [EvidenceExtractionPipeline.extract_and_fuse, circuit branch](../../ai/evidence/pipeline.py#L266). |
| A stale `canCompile` hint could override a newer negative review; an expected compilation refusal became UI ERROR. | [SimulationOrchestrator._evaluateAndAdvance](../../apps/web/src/features/simulations/core/SimulationOrchestrator.js#L460) and `compile`, line 516. |
| The circuit renderer replaced the observed open arm with a fixed angle. | [CircuitRenderer._renderSwitches](../../apps/web/src/features/simulations/circuits/CircuitRenderer.js#L247); adapter now carries measured arm geometry. |

## 2. Files changed and responsibility

- `ai/evidence/cv/circuits_cv.py`: native-frame extraction and symbol removal before conductor tracing.
- New `circuit_paths.py`, `circuit_symbols.py`, `circuit_geometry_validator.py`: continuous pixel paths, physical symbol hypotheses, and independent raster/terminal checks.
- `ai/evidence/cv/geometry_helpers.py`: duplicate-line suppression compares both endpoints; similar midpoints no longer discard independent extents.
- `ai/evidence/grounding/circuits.py`: replaces OCR/rail-based geometry with verified symbol assignment, stable identities, explicit diagnostics, and separate value/geometry provenance.
- New `circuit_graph.py`, `circuit_integrity.py`: conductor islands, terminal attachments, graph/reference validation, malformed-payload rejection.
- `ai/evidence/pipeline.py`, new `segmentation/circuit_prompts.py`, and `segmentation/sam2_provider.py`: circuit prompts, conservative mask checks, atomic predictor use, content-based embedding cache, retained mask pixels and prompt metadata.
- `ai/resolution/analyzer.py`, `ai/resolution/auto.py`, `ai/ingestion/PhysicsCompiler.py`: shared circuit checks at review and compilation; missing circuit values and switch state remain unresolved; duplicate IDs are rejected.
- `SimulationOrchestrator.js`: latest review governs advancement; gating refusals return to review.
- `CircuitAdapter.js`, `CircuitRenderer.js`: preserve measured switch-arm geometry and display provenance/labels correctly. MNA and circuit solution code are unchanged.
- `requirements.txt`: explicitly declares SciPy and scikit-image used by assignment and skeletonization.
- New `tests/unit/test_circuit_grounding_repair.py`: synthetic raster, recorded-source, graph, corruption, and mock segmentation regressions. Existing circuit fixture tests now declare valid semantic/terminal identities; the old unverified rail fixture now correctly expects review. `test_pr08_no_fabrication.js` covers stale readiness and gating refusal.
- New `tests/acceptance/circuit_repair_replay.py`, `circuit_repair_server.py`, `circuit_repair.html`, `circuit_repair_browser.mjs`: reproducible offline replay and browser acceptance. These are test infrastructure, not production routes.

## 3. Wire, component, and terminal algorithms

Native raster thresholding and skeletonization produce traced polylines. There is no gap closing or extrapolation across components. Thresholds use estimated stroke width and source diagonal. Short thinning spurs are pruned only at existing branches. Four-way crossings without a sufficiently large dot retain separate opposite conductors. A dot joins them. Bent and diagonal paths retain their bends.

Zigzag resistors require repeated alternating excursions along a monotonic axis and straight leads. Rectangular resistors require an enclosed quadrilateral with supported leads. Battery groups require parallel alternating plate lengths and external leads; plate lengths establish polarity. Switches require paired contact outlines plus an observed arm or supported closed bridge. Circular stroke checks handle contact interiors divided by leads.

Component regions are removed from the conductor mask before graph construction. Each terminal must attach to a nearby actual path endpoint with local raster support. Distances are bounded by stroke uncertainty and measured contact radius. OCR boxes suppress text and associate values; their centers never become physical coordinates.

Semantic-to-physical assignment is one-to-one, type constrained, and global. Nearly equivalent assignments stay unresolved. Visible designators are separate from stable semantic IDs. Geometry confidence is a conservative heuristic (0.9 after checks), not an empirically calibrated accuracy probability; stroke-width uncertainty remains attached.

## 4. SAM2 changes and execution status

Circuit symbols receive independent CV-derived boxes and positive points. Diagnostics retain candidate/source IDs, prompts, provider/model, status, masks, scores, area, centroid, and rejection reasons. Frame, bounds, area, neighboring-region spill, encoded mask extent, and coverage of measured symbol points are checked. Masks never establish connectivity or replace terminals. Retained corroborating masks explicitly say `localization_improved: false` and remain non-authoritative.

Predictor `set_image` and `predict` are protected together by a lock. Cache identity includes checkpoint/config/device and predictor identity; image embeddings use full pixel hashes. An offline mock test changes interior pixels while retaining allocation, dimensions, and corners, and verifies recomputation. Mask RLE round-trip is also tested.

**Actual SAM2 neural inference did not execute.** The replay explicitly uses `UnavailableSegmentationProvider`; no mask is fabricated. Conflict/unavailability tests and the predictor-cache test use mocks. Therefore no segmentation accuracy or localization improvement is claimed.

To enable real inference, install the repository's SAM2/PyTorch dependencies in the runtime environment and supply the configured checkpoint (default `checkpoints/sam2.1_hiera_tiny.pt`, config `configs/sam2.1/sam2.1_hiera_t.yaml`). Run the production pipeline with `SAM2SegmentationProvider`. Verify each `circuit_segmentation` record has actual execution status and returned mask pixels; `available()` alone is insufficient. Check mask rejection reasons before treating the run as useful evidence.

## 5. Pre-grounding gate and failure behavior

`CircuitGeometryValidator.validate` rejects paths outside the source, paths across component bodies, and paths lacking continuous pixel support. It checks symbol strokes against the original raster, terminal/body bounds, per-terminal endpoint attachments, battery polarity, and switch state.

Unsupported symbols remain `AMBIGUOUS`; rejected wires remain in diagnostics. Direct calls with arbitrary boxes/rail lists and no verification boundary produce no trusted components or nodes. Missing symbols, ambiguous assignments, broken conductor islands, missing values, and corrupt references produce `NEEDS_REVIEW` and `scene: null`. Automatic circuit resolution no longer fills missing resistance/voltage with 100 Ω/10 V. Explicit evidence or user resolution is required.

## 6. IDs, graph, and provenance

Original IDs `voltage_source_1`, `switch_1`, `resistor_1`, and `resistor_2` remain unchanged. All four original relationships resolve after serialization. Terminals use `<entity>.t1/t2`; each has measured source coordinates, a wire ID, and a declared node.

Nodes derive from shared traced endpoints, respecting crossing separation. Only conductor islands attached to physical terminals enter the electrical graph. Detached current arrows and caption strokes remain excluded. A conductor island with only one component terminal or a separate component network requires review.

Integrity checks cover duplicate/missing IDs, inconsistent relationship aliases, missing physical components, evidence references, component/terminal/wire/node references, source identity, finite source coordinates, reference node, and verification state. Malformed containers are rejected without attempting scene construction. Geometry provenance remains classical CV; emitted resistance/voltage parameters retain OCR provenance.

## 7. Stage 14 — actual before and after

| Recorded before repair | Fresh execution after repair |
|---|---|
| `components=[]`; 15 line segments | Four physical symbol proposals; 24 raster-supported paths before semantic graph filtering |
| `rails_y=[255,416,668]`, `branches_x=[231,992]` | Rail/branch template arrays empty and unused |
| Full x=231→992 span at y=416 across empty interior | No such interior span |
| Top full-span rail crossed open switch and resistor | Physical symbols removed from conductor tracing; open switch terminals remain distinct |
| External contour missed connected zigzags | Both zigzag resistors detected, including vertical R2 |

The final graph retains four measured conductor polylines. The other raw paths are detached ink, not electrical edges. Historical records are unchanged and hash-referenced in [before_manifest.json](../../storage/generated/circuit_repair_20261018/before_manifest.json).

## 8. Stages 16–17 — actual before and after

Before: R2 at `(1149,416)` with horizontal terminals; R1 at `(757,255)`; V1 at `(231,457)`; switch ungrounded; no nodes; renamed IDs left dangling relationships; `NEEDS_REVIEW`.

Fresh measured output (coordinates are source pixels):

| Stable identity | Center | Orientation | Terminal 1 → terminal 2 | Value/state | Nodes |
|---|---|---|---|---|---|
| voltage_source_1 | (232,466) | Vertical | (232,419) → (232,511.48) | 12 V, OCR | N2,N3 |
| switch_1 | (397.25,235.25) | Horizontal contacts | (444,255.5) → (350.5,255) | Open, CV | N4,N2 |
| resistor_1 | (762.5,255) | Horizontal | (843,255) → (682,255) | 10 Ω, OCR | N1,N4 |
| resistor_2 | (992.5,462) | Vertical | (991,542) → (991,382) | 20 Ω, OCR | N3,N1 |

The switch center describes the arm/contact region, not the midpoint between contacts. Terminal ordering follows detected geometry; current sign follows that ordering. Eight terminal attachments and four nodes are present. Semantic, geometry, topology, referential-integrity, and physics-readiness flags pass. Overall status is `READY_TO_COMPILE`.

## 9. Stage 24 and canonical validation

Historical Stage 24 was **NOT EXECUTED** because readiness failed. Fresh replay executes `PhysicsCompiler.compile`, the readiness gate, canonical construction, and `validate_canonical_scene`. Result: `READY`, `schemaVersion: "1.0"`, `domain: "circuits"`, `subtype: "dc_linear"`, no compiler issues. The actual JS runtime subsequently loads and solves that scene in Chrome.

See [scene.json](../../storage/generated/circuit_repair_20261018/scene.json), [book_ir.json](../../storage/generated/circuit_repair_20261018/book_ir.json), and [stage_diagnostics.json](../../storage/generated/circuit_repair_20261018/stage_diagnostics.json).

## 10. Observed solver and browser results

The browser test selected the real JPEG through a file input and sent multipart bytes through `SimulationApi`. The replay server ran the actual UploadService, PageIRBuilder, EvidenceExtractionPipeline, readiness evaluator, and compiler using recorded semantic/OCR responses. The real SimulationOrchestrator, InteractiveFigure, FigureViewport, CircuitRenderer, PhysicsRuntime, adapter, and solver executed.

| Interaction | Observed current magnitude |
|---|---|
| Initial open switch | 0 A |
| Pointer click closes switch, 12 V / (10 Ω + 20 Ω) | 0.4 A; total resistor power 4.8 W |
| R1 input changed to 20 Ω | 0.3 A |
| Reopen switch | 0 A |
| Reset | 0 A; R1 restored to 10 Ω; switch restored open |

Activation required a separate Start Simulation click; Play was also exercised. The rendered open arm exactly retained the compiled measured arm coordinates. Image and SVG bounds agreed within 0.1 CSS px at 900 px/DPR 1 and 1280 px/DPR 2; switch clicks worked at both. Serialized BookIR was unchanged after edits and reset. No browser runtime exceptions were captured.

This verifies coordinate transport/layout consistency, **not pixel-perfect detection accuracy**. Source hash and natural dimensions were checked. [Browser results](../../storage/generated/circuit_repair_20261018/browser_results.json) include voltages, currents, power, source identity, and layout measurements. [Browser screenshot](../../storage/generated/circuit_repair_20261018/13_browser_overlay_t0.png) and [actual t=0 crop](../../storage/generated/circuit_repair_20261018/12_compiled_scene_t0_on_source.png) were captured and visually inspected.

## 11. Tests, commands, and artifacts

Commands run from the repository root unless indicated:

```powershell
./.venv/Scripts/python.exe -X utf8 -m pytest tests/unit/test_circuit_grounding_repair.py -q -p no:cacheprovider
./.venv/Scripts/python.exe -X utf8 -m pytest tests/unit -q -p no:cacheprovider --ignore=tests/unit/test_strict_analysis.py
./.venv/Scripts/python.exe -X utf8 tests/acceptance/circuit_repair_replay.py
# apps/web:
npm.cmd test
npm.cmd run build
# Opt-in browser replay: start the replay server and Vite, plus a dedicated
# headless Chrome profile with remote debugging on localhost port 9223:
./.venv/Scripts/python.exe -X utf8 tests/acceptance/circuit_repair_server.py
node tests/acceptance/circuit_repair_browser.mjs
```

The circuit repair suite has **20 passing tests**. It covers series and parallel circuits; open/closed switches; rectangular/zigzag resistors; 90° rotation; 0.7× and 1.5× resolution; bent/diagonal wires; crossings with/without dots; broken conductors; forged geometry; malformed IDs/references; missing geometry; serialization; source/value provenance; unavailable/conflicting segmentation; content-based embedding invalidation; and the recorded source replay. Synthetic fixtures have explicit known geometry and are identified as synthetic.

The frontend test command passed all included suites, including optics, mechanics, coordinate mapping, canonical runtime, circuit solver, rendering, orchestration, and review. Production Vite build passed. Baseline Python run had 200 passes and eight environment-related failures; the final broad run has **220 passes and the same eight failures**, recorded in [circuit_final_pytest.txt](../../storage/generated/circuit_final_pytest.txt). Those eight failures concern missing RapidOCR/model dependencies, SAM2 availability, and five mocked Gemini retry tests whose SDK dependency is absent. `test_strict_analysis.py` cannot collect because importing the production API requires missing `torch`; it was explicitly excluded, not silently treated as passing.

Logs: [new circuit suite](../../storage/generated/circuit_new_tests.txt), [frontend suites](../../storage/generated/circuit_final_web.txt), [build](../../storage/generated/circuit_final_build.txt), [baseline](../../storage/generated/circuit_baseline_pytest.txt).

All thirteen requested image roles exist under `storage/generated/circuit_repair_20261018/`, from original/grayscale/edges through OCR, candidates, prompts, verification, terminals, graph, actual renderer crop, and browser screenshot. Artifact 08 clearly labels SAM2 unavailable and shows prompts only. `diagnostics.json` contains full outputs; `stage_diagnostics.json` identifies stages/functions, inputs, outputs, validations, rejections, uncertainty, coordinate frame, evidence, failure reasons, and downstream impact. Runtime outputs remain ignored and unstaged.

## 12. Limits and acceptance checkpoints

| Checkpoint | Result and practical limit |
|---|---|
| A — Stage 14 | Passed recorded-source and synthetic continuity/symbol checks; no rail template or switch bridging. |
| B — Pre-grounding | Passed rejection tests and CV-only fallback. Real SAM2 inference remains untested. |
| C — Grounding | All four recorded symbols, orientations, eight terminals, and three OCR values grounded. |
| D — Referential integrity | Stable IDs, resolved relationships/evidence, declared nodes, corruption/serialization tests passed. |
| E — Compilation | Readiness and canonical validation executed successfully; missing values and broken graphs fail safely. |
| F — Browser | Passed real file upload/core-service replay, overlay, switch, resistance edit, Play, resize/DPR, reset, and evidence immutability. |
| G — Generalization | Passed materially different synthetic layouts/styles/resolutions. Broad real-image corpus accuracy is not established. |

The acceptance server is an explicit offline replay harness; the full `apps/api/main.py` application and fresh Gemini/OCR/SAM inference were not run. No live provider performance claim is made. Arbitrary-angle symbols, circular source variants, handwritten/degraded scans, OCR collisions, bridge/hop notation, and dense circuits need further labeled evaluation; unsupported or ambiguous detections should require review. A non-dotted four-way crossing follows the non-connected convention; diagrams using a different convention need explicit review. There is no independently annotated landmark ground truth for the recorded JPEG. The screenshot and measurements support visual registration and consistent coordinate mapping, not a general accuracy percentage.

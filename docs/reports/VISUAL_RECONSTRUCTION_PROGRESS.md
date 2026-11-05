# Faithful visual reconstruction progress

> **2026-10-15 checkout correction:** This report below is historical. The working tree was reset to `f59652f` after reconstruction commit `56cc340`, so the recorded Phase 1–2 implementation is not currently present. The user redirected work to simulation failures; see [the active regression investigation](SIMULATION_REGRESSION_20261015.md). Do not proceed to the next phase or report the historical phase tests as validation of this checkout.

Started: 2026-10-13. Updated: 2026-10-14. **Phases 1–2 complete; Phase 3 next.** Scope: the user's new reconstruction plan, implemented one phase per task. This numbering is independent of the historical Phase 2–5 benchmark/browser reports.

## Phase tracker

| Phase | Scope | Status |
| :--- | :--- | :--- |
| 1 | Reusable visual reconstruction contract | Complete (2026-10-14) |
| 2 | Initial registration gate and centralized thresholds | Complete (2026-10-14) |
| 3 | Separate physics assumptions from fabricated visual geometry | Pending |
| 4 | Requirements based on observable visual elements | Pending |
| 5 | Physically valid candidate fitting and ranking | Pending |
| 6 | Pendulum source bob/string extraction and interaction | Pending |
| 7 | Projectile trajectory reconstruction and inverse fitting | Pending |
| 8 | Thin-lens reconstruction, fitting, and object interaction | Pending |
| 9 | Mirror reconstruction and fitting | Pending |
| 10 | Refraction reconstruction and Snell validation | Pending |
| 11 | Prism reconstruction and direct beam manipulation | Pending |
| 12 | Circuit visual wire paths and printed switch interaction | Pending |
| 13 | Generic source visual extraction/restoration | Pending |
| 14 | Faithful, debug, and educational rendering modes | Pending |
| 15 | Separate mapping error from visual residuals | Pending |
| 16 | Minimal image-based review | Pending |
| 17 | Visual metrics, reference cases, and unseen-image acceptance | Pending |

The architecture should first prove itself with pendulum, thin lens, and a switch circuit before expanding visual reconstruction to the remaining supported models. Passing unit tests at an early phase does not complete the overall plan. Regression tests run throughout; phase 17 is the broader visual acceptance milestone.

## Phase 1 implementation

The shared contract belongs beside the existing evidence and ingestion schemas because perception, resolution, and later compilation need the same representation. Existing source primitives are reused instead of introducing another coordinate system. No physics solver, runtime, API handler, detector, or renderer was changed.

Files:

- `shared/schemas/visual_reconstruction.py`: `ObservedGeometry`, `VisualConstraint`, `DynamicVisualAsset`, `RegistrationMetric`, `RegistrationReport`, `RegistrationStatus`, `VisualReadiness`, and versioned `VisualReconstruction`.
- `shared/schemas/ingestion.py`: optional `BookIR.visual_reconstruction` and camelCase `visualReconstruction` JSON round trips. Legacy payloads omit the optional key and retain their existing readiness.
- `shared/schemas/__init__.py`: public contract exports.
- `tests/unit/test_visual_reconstruction.py`: offline contract, provenance, compatibility, and rejection checks.
- `PROJECT_CONTEXT.md`, `docs/ARCHITECTURE.md`, and this report: current scope, limitations, and next phase.

`ObservedGeometry` contains native source dimensions, named landmarks/lines/curves/masks/text anchors, an undirected observed topology adjacency map, and evidence references. Curves are ordered sampled polylines. The topology describes observed terminal/junction connectivity; it does not replace the electrical solver graph.

`DynamicVisualAsset` records optional mask/sprite/background/restoration-patch URLs. Its bounding boxes, anchor, and transform origin all use absolute source pixels, including when the sprite is cropped. A restoration patch needs its own bounding box. Creating a record performs no extraction, image editing, or network access.

The contract rejects non-finite or boolean geometry/numeric metrics, non-source coordinate spaces, out-of-bounds observations, invalid confidence/IoU, inconsistent mask dimensions, undeclared feature/constraint/entity references, and incompatible native BookIR dimensions. Supplied evidence references must resolve in BookIR and cannot point to VLM-only semantic records. Metadata retains evidence references and mask prompt provenance through detached JSON serialization.

### Pipeline boundary

Before: semantic analysis → CV/OCR grounding → BookIR → existing parameter readiness → compiler → runtime.

After phase 1: the same execution path, with an optional validated reconstruction record that can survive BookIR serialization and resolution round trips. No second execution pipeline is introduced. Perception producers, predicted t=0 geometry, the registration gate, and canonical scene propagation are later work.

### Exact readiness semantics at this phase

- `NOT_EVALUATED` is the default. Mean/p95 errors, mask IoU, and topology match are unknown (`null`), not invented zero errors. An unevaluated report cannot contain measured results or nonzero confidence.
- A structurally `PASSED` report requires at least one measured metric, positive sample counts, all metric pass flags, no blockers, no known topology mismatch, and coverage of every required declared constraint.
- `AUTO_VISUAL` requires a passed registration report. It represents visual interaction only and does not authorize SI claims.
- `PHYSICS_VERIFIED` additionally requires physical evidence references. The schema checks reference integrity; future evaluators must determine model-specific sufficiency. Merely attaching references does not prove SI accuracy.
- No contract constructor calculates visual error, chooses thresholds, evaluates pixels, or upgrades `BookIR.status`. Existing `READY_TO_COMPILE` / compiler `READY` is still solver readiness, not proof of source-image reproduction.

The current review fallback remains unchanged. This phase does not enable visual review actions or suppress existing numeric review. Missing or failed reconstruction cannot claim either new visual readiness level. Phase 2 implements evaluation; phases 3–4 integrate automatic assumptions and visual requirements, and phase 16 implements minimal visual corrections.

### Validation

| Check | Measured result |
| :--- | :--- |
| Existing Python unit/integration/acceptance baseline | 269 passed, 3 skipped, 24 warnings (519.50 s) |
| Final reconstruction + readiness + semantic + all-domain focused regressions | 142 passed (5.51 s) |
| Final upload API integration tests | 8 passed, 1 existing Starlette warning (21.63 s) |
| Final `apps/web` JavaScript tests | All 17 scripts passed |
| Final production build | Passed; existing >500 kB bundle warning |
| Existing real-image variation benchmark | 6/6 positive variants compiled; 2/2 negative open-switch variants withheld |

These test sets overlap; their counts are not additive. The baseline covers the existing suite, while the final focused run includes the new contract and its latest fixes. The API check exercises real multipart uploads using `MockVisionProvider`. Python runs blanked Gemini/Google keys and blocked `socket.socket.connect`; OCR used local cached models. Three live/opt-in tests were skipped. No external VLM request was made.

The first unrestricted-thread Python/benchmark attempts exited without a result summary or Python traceback. Sequential reruns with `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, and `MKL_NUM_THREADS=1` completed the baseline. These incomplete attempts are not counted as passes or asserted product regressions. The baseline log is ignored local output at `storage/generated/phase1_contract_python_baseline_20261013.log`.

The final bounded variation benchmark used actual image decoding/CV/OCR and deterministic `MockVisionProvider` semantic labels. Classification accuracy is not measured. Each selected fixture was tested at 0.75× scale and with 8% padding:

| Fixture | Scaled result | Padded result | Available visual/physics measurements |
| :--- | :--- | :--- | :--- |
| `pendulum_sketch` | `READY` | `READY` | No annotated landmarks; compilation is not a bob/string registration measurement |
| `thin_lens` | `READY` | `READY` | Lens-center residuals 3.5795 px / 7.2801 px; old tolerances 15 px / 20 px |
| `user_circuit_parallel_network` | `READY` | `READY` | Both: 5 components, 4 nodes, identical connectivity signatures, finite solved voltages |
| `user_circuit_open_switch` | `NEEDS_REVIEW` | `NEEDS_REVIEW` | No scene; `TOPOLOGY_INVALID`, ungrounded switch state/connections |

Parallel-circuit maximum KCL residuals were 5.2042e-17 A and 4.8572e-17 A. Both thin-lens annotations pass the existing loose point tolerances, but neither is within the proposed preferred 3 px landmark bound; the padded lens also exceeds 5 px. These are detector-to-annotation errors, **not predicted t=0 renderer residuals**. The new registration gate was not implemented or measured in Phase 1. This bounded result must not be reported as general automation accuracy or as visual readiness.

Benchmark JSON and console output are ignored local files `storage/generated/phase1_contract_variation_20261014.json` and `.log`. No production regression was identified in these checks; the lens alignment and switch abstention remain known limitations assigned to later phases.

To reproduce the focused contract check in the existing WSL environment, start in `/mnt/d/AugmentedPhysics`:

```bash
GEMINI_API_KEY= GOOGLE_API_KEY= PYTHONPATH=/mnt/d/AugmentedPhysics/sam2 \
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
/home/torikul/augmentedphysics-audit-venv/bin/python - <<'PY'
import socket
import pytest

def offline_only(*args, **kwargs):
    raise RuntimeError("Network disabled for offline contracts")

socket.socket.connect = offline_only
raise SystemExit(pytest.main([
    "-q", "-p", "no:cacheprovider",
    "tests/unit/test_visual_reconstruction.py",
    "tests/unit/test_pr07_evaluator.py",
    "tests/unit/test_automatic_readiness_safety.py",
    "tests/unit/test_pr05_semantic_schemas.py",
    "tests/unit/test_auto_resolution_grounding.py",
    "tests/acceptance/test_pr07_all_domains.py",
]))
PY
```

For the API check, use `tests/integration/test_pr04_api_upload.py` in that same offline runner. The full baseline uses `tests/unit tests/integration tests/acceptance`. Run `npm test` and `npm run build` from `apps/web` (or `npm.cmd` in PowerShell).

To reproduce the benchmark with the same environment and network guard, replace the pytest call in that runner with:

```python
import runpy
import sys
sys.argv = [
    "research/benchmarks/variation_benchmark.py",
    "--case", "pendulum_sketch", "--case", "thin_lens",
    "--case", "user_circuit_parallel_network", "--case", "user_circuit_open_switch",
    "--variant", "scale_0.75", "--variant", "padding_8pct",
    "--output", "storage/generated/phase1_contract_variation_20261014.json",
]
runpy.run_path(sys.argv[0], run_name="__main__")
```

Manual scope: pendulum, lens, and switch uploads retain their existing behavior. No newly moving source sprite, fitted lens ray, or clickable printed switch is claimed in Phase 1. The contract round-trip test is the relevant inspection now; visible interaction acceptance belongs to the later domain phases.

### Scope and review

This task changes shared schemas because the requested Phase 1 contract crosses perception/resolution boundaries. The change is optional and additive, and the root agent is the sole production-schema writer. `.github/CODEOWNERS` names `@rahi-sadat` and `@THE-FOOL-T` for shared-schema review; this report is the concrete review handoff. No commit, push, or merge is included.

No filename/hash routing, fixture-specific coordinates, fabricated geometry, new physics domains, or changes to working equations were introduced. Coordinate values used in contract tests are synthetic test data only.

## Phase 2 implementation

`ai/registration/` adds the initial registration library on top of the Phase 1 contracts. `InitialRegistrationGate.evaluate(book_ir, prediction, observed_masks=...)` compares grounded BookIR observations with independently supplied `PredictedGeometry` at t=0 and returns a fresh `RegistrationReport`. The gate contains no physics equations, image-specific constants, candidate fitting, or network/image-file loading.

Central policy lives in `RegistrationThresholds`:

| Comparison | Default passing requirement | Other outcomes |
| :--- | :--- | :--- |
| Landmark/text anchor Euclidean distance | <= 3 source px | >3 through 5 px: review; >5 px: failed |
| Symmetric line/curve distance | Mean <=3 px AND p95 <=5 px | Either bound exceeded: failed |
| Raster mask IoU | >=0.85 | Below threshold: failed; absent/invalid source mask: review |
| Circuit topology | Exact labeled node/edge connectivity | Well-formed mismatch: failed; invalid graph: review |
| Supporting source evidence confidence | >=0.8 for every compared feature | Missing/invalid/low confidence: review |

The confidence value is the weakest supporting evidence confidence, capped at 0.99. It is not a calibrated statistical probability and is not invented from a zero mapping error. Incomplete comparison coverage yields zero registration confidence.

Correspondence uses explicit feature IDs. Every supplied observation must be covered by a constraint, including printed paths and masks; checking only one convenient landmark cannot approve an incomplete observation set. Predicted extras cannot silently disappear from the comparison. Topology is compared as a whole graph. Mask comparison requires real binary arrays at full native dimensions, never bbox overlap or URL presence. Pixel residual summaries exclude dimensionless IoU and topology booleans.

The gate deep-copies inputs and discards cached registration/readiness claims before evaluation. It checks source/figure identity, domain/subtype, native dimensions, coordinate space, t=0, and grounded evidence. It leaves BookIR parameters, provenance, solver status, and existing readiness untouched. A passed report is agreement for the **supplied observation set**; it does not prove that perception found every printed element, that a candidate is physically identifiable, or that its SI values are verified.

The active upload path has no general t=0 prediction producer yet. This phase therefore supplies the reusable gate and measured tests/benchmark, without fabricating predictions by copying observations or wiring a false automatic pass into ingestion. Model-specific adapters, visual-aware requirements, and automatic readiness integration remain later phases. Phase 3 will address physics versus visual assumptions next.

### Phase 2 files and validation

- `ai/registration/base.py`: prediction input and centralized thresholds.
- `ai/registration/metrics.py`: landmark, symmetric path, raster IoU, and topology comparisons.
- `ai/registration/evaluator.py` and `__init__.py`: gate and public exports.
- `tests/unit/test_initial_registration_gate.py` and `test_registration_metrics.py`: agreement, mismatches, missing evidence, malformed predictions, coverage, numerical bounds, and input immutability.
- `research/benchmarks/initial_registration_benchmark.py` and `pendulum_initial_prediction.mjs`: offline real-image CV observations versus the existing canonical pendulum runtime and source-position renderer method, with changed-angle/missing-prediction/dimension controls.

Validation on 2026-10-14:

| Check | Result |
| :--- | :--- |
| Gate, metric, and reconstruction contract tests | 170 passed |
| Full Python unit/integration/acceptance suite | 439 passed, 3 skipped; 376.07 seconds |
| Frontend regression suite | All 17 scripts passed |
| Frontend production build | Passed; existing large-chunk warning remains |

Python validation used deterministic mock semantic providers, blank API keys, a blocked network socket, cached local OCR models, and single-thread BLAS/OpenMP settings. The 24 full-suite warnings concern existing dependency deprecations and unavailable GPU pinning. Focused and full counts overlap. No working physics algorithm, production renderer, API handler, or Phase 1 schema was changed during Phase 2.

Local logs are ignored output under `storage/generated/`: `phase2_registration_python_20261014.log`, `phase2_registration_frontend_baseline_20261014.log`, and `phase2_registration_frontend_build_20261014.log`.

Reproduce Python checks using the offline runner above with `tests/unit/test_initial_registration_gate.py`, `tests/unit/test_registration_metrics.py`, and `tests/unit/test_visual_reconstruction.py`, or with `tests/unit tests/integration tests/acceptance` for the full suite. In a native environment with Python and Node on PATH, run `python research/benchmarks/initial_registration_benchmark.py`. In this split WSL/Windows environment, use the same offline WSL environment variables and Python executable to prepare observations:

```bash
/home/torikul/augmentedphysics-audit-venv/bin/python \
  research/benchmarks/initial_registration_benchmark.py \
  --prepare-only --output storage/generated/phase2_registration_prepared.json
```

Then run the runtime bridge from PowerShell at the repository root:

```powershell
node research/benchmarks/pendulum_initial_prediction.mjs storage/generated/phase2_registration_prepared.json |
  Out-File -Encoding utf8 storage/generated/phase2_registration_predictions.json
```

Finally, score from the same offline WSL Python environment:

```bash
/home/torikul/augmentedphysics-audit-venv/bin/python \
  research/benchmarks/initial_registration_benchmark.py \
  --prepared storage/generated/phase2_registration_prepared.json \
  --predictions storage/generated/phase2_registration_predictions.json
```

The benchmark itself blocks network connections and uses `MockVisionProvider`. Two initial attempts reached compilation but could not launch Node (absent WSL executable, then disabled Windows executable interoperability); they are not counted as benchmark passes. The staged invocation avoids both environment limitations without modifying production code.

### Phase 2 measured benchmark

The final staged run completed on `pendulum_sketch`. Observations were captured from classical CV before automatic resolution/compilation. Predictions came from the unstepped canonical `PhysicsRuntime` kernel and the existing `PendulumSimulation.getBobSourcePosition` method; the benchmark contains no replacement pendulum equations.

| Case | Gate result | Measured evidence |
| :--- | :--- | :--- |
| Original runtime t=0 | `PASSED` | Pivot 0 px; bob 0.00006763 px; string mean 1.1770 px, p95 1.7067 px; confidence 0.85 |
| Runtime initial angle increased by 30 degrees | `FAILED` | Bob 181.4529 px; string mean 85.6430 px, p95 163.2173 px |
| Bob prediction removed | `NEEDS_REVIEW` | Missing prediction; confidence 0 |
| Prediction source width doubled | `NEEDS_REVIEW` | Native-dimension mismatch; residuals unknown, confidence 0 |

All negative-control assertions and BookIR immutability checks passed. The complete result is ignored local output at `storage/generated/phase2_initial_registration.json`; staged inputs/predictions are also ignored runtime artifacts. Gate registration did not promote visual or physics readiness.

This is one bounded consistency check against CV observations used by compilation, **not independent ground-truth accuracy**. The supplied comparison covers pivot, bob center, and visible string only. It does not measure bob silhouettes, source sprites, canvas pixels, lens rays, or circuit wiring. Masks and topology have deterministic synthetic metric/gate tests, but no real-image registration claim here. The Phase 1 lens-center and open-switch limitations remain unresolved and assigned to later phases.

Phase 2 is complete at this library boundary. Phase 3 is next: distinguish permitted physical assumptions from invented visual geometry while preserving provenance. No Phase 3 implementation is included in this task.

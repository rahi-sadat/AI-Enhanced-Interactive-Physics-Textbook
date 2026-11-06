# Circuit v2: user-verified 99-image evaluation

The user confirmed that they manually checked, corrected and finished the CVAT
annotations. The saved job was exported on 2026-11-05 without changing its boxes,
labels or job state. The reference contains 99 original images and 916 boxes.

- CVAT task: https://app.cvat.ai/tasks/2740033
- CVAT job: https://app.cvat.ai/tasks/2740033/jobs/4698364
- Preserved export: `outputs/circuit_v2_verified_99_20261105/cvat_user_verified.zip`
- Image-by-image comparison: `outputs/circuit_v2_verified_99_20261105/report.html`
- Full metrics, source hashes and annotation audit are alongside that report.
- Six-class YOLO staging copies: `outputs/circuit_v2_verified_99_20261105/data/`.
  Names have frame prefixes to avoid collisions between originals sharing a stem.
  Image bytes are unchanged; native rotated rectangles remain in the original XML.

## Frozen model and method

Checkpoint: `runs/augmented_physics/circuits_real_v2_20261031/weights/last.pt`

SHA-256: `95bc8a1f76aaed83ad907e87bdee0255da1837fdb8f9c8405a723779e8ed0c46`

The comparison uses the previously saved post-NMS predictions at
`outputs/circuit_v2_test_20261103/predictions.json`. All 99 source hashes and image
dimensions were checked against those predictions, and the current checkpoint
hash was checked against the recorded inference manifest. No model was trained,
and no VLM or external API was used for this evaluation.

Precision, recall and F1 below use confidence >= 0.25, IoU >= 0.50 and class-aware,
descending-confidence one-to-one matching from installed Ultralytics 8.4.193.
AP uses saved detections at confidence >= 0.001 and the installed Ultralytics AP
calculation at IoU 0.50 through 0.95. These are cached-prediction metrics, rather
than a fresh `model.val` inference run.

The user's 38 rotated reference rectangles are converted to their enclosing
axis-aligned boxes for comparison with v2's axis-aligned predictions. Only the
derived evaluation labels undergo this conversion. The original XML, rotation,
polygon corners, image bytes and input fingerprints are retained separately.

## Component detection results

| Class | Reference boxes | TP | FP | FN | Precision | Recall | F1 | AP50 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| resistor | 739 | 686 | 11 | 53 | 98.42% | 92.83% | 95.54% | 95.16% |
| voltage_source | 138 | 123 | 22 | 15 | 84.83% | 89.13% | 86.93% | 84.23% |
| capacitor | 3 | 0 | 1 | 3 | 0.00% | 0.00% | 0.00% | 0.00% |
| switch | 20 | 7 | 11 | 13 | 38.89% | 35.00% | 36.84% | 23.27% |
| ammeter | 12 | 0 | 0 | 12 | — | 0.00% | 0.00% | 0.00% |
| voltmeter | 4 | 0 | 0 | 4 | — | 0.00% | 0.00% | 0.00% |

V2 has only four output classes: resistor, voltage source, capacitor and switch.
It cannot emit either meter class. Meter precision is undefined with no meter
predictions (stored as zero by the evaluator); their recall and AP are zero.
Adding CVAT labels does not add model capabilities. A future six-class training
run would be needed to learn those classes; no such run was started here.

| Evaluation scope | Micro precision | Micro recall | Micro F1 | Macro mAP50 | Macro mAP50–95 |
|---|---:|---:|---:|---:|---:|
| Four supported classes | 94.77% | 90.67% | 92.67% | 50.67% | 46.24% |
| All six reference classes | 94.77% | 89.08% | 91.84% | 33.78% | 30.83% |

The class imbalance makes aggregate micro scores look strong while capacitor,
switch and meter coverage remains weak. These annotations began as model-assisted
proposals before the user's manual corrections; this is not independent blind
annotation. Exact image identity checks do not establish source-level or
near-duplicate independence. Three capacitor references are too few for a broad
capacitor generalization claim.

## Simulation and failure visibility

The integrated experiment is available at
`http://127.0.0.1:5174/circuit-v2.html` while the local Vite and API servers run.
Upload a circuit and keep **Play experimental preview if compilation is blocked**
checked to see the detector-based preview. The page lists each stage, the first
blocker, affected entity IDs, OCR status and checkpoint identity. Full diagnostics
can be downloaded from the page.

The prior 99-image full pipeline audit with local OCR produced:

- 17 compiled scenes; all 17 passed the actual physics runtime loading/step check.
- 81 NEEDS_REVIEW and 1 UNRESOLVED result.
- First blockers: geometry validation 79, topology validation 2, detection 1.
- 99 experimental previews; all 99 passed the runtime loading/step check.
- Zero HTTP request failures.

Evidence: `outputs/circuit_v2_pipeline_99_with_ocr/summary.json` and
`runtime_results.json`. Those are the earlier pipeline audit, not a new 99-image
run against the human labels. CVAT boxes do not supply wire topology or values.

The experimental preview guesses a series loop, terminals and default values.
It may therefore be physically wrong even when playback succeeds. Its assumptions
remain separate from grounded BookIR and canonical compilation. The user-visible
warning and original compilation blockers remain present. This follow-up also
sets explicit experimental source and zero evidence confidence on guessed
parameters so the existing viewer cannot describe them as textbook evidence at
100% confidence. Physics solvers were unchanged.

## Validation and reproduction

- Complete reference, prediction, source dimension/hash and staged image checks passed.
- All 99 comparison image paths resolve; all 916 targets and 861 fixed-threshold
  predictions are accounted for; all 38 rotations remain in the native reference.
- Rotation conversion, empty sets, duplicate/wrong-class matching, unsupported
  meter matching, nonmutation and metric arithmetic checks passed.
- Preview separation and failed-grounding recovery tests: 2 passed with offline
  canned detector responses and MockVisionProvider. A workspace-local pytest
  base directory was used because the default Windows pytest temp directory was
  inaccessible.
- The web `npm test` suite passed; log:
  `outputs/v2_verified_web_tests_20261105.log`.
- Fresh browser check on `DC_015.png`: RUNNING preview over the source image,
  runtime/rendering passed, compilation blockers visible, and guessed parameter
  tooltips showed `experimental_preview` with 0% evidence confidence. API health
  and the experiment page both returned HTTP 200 afterward.
- The earlier full unit-suite run had 339 passes and 18 failures involving CV
  generalization, SAM2 availability and provider retry dependencies. This
  follow-up does not establish a clean full-suite result.

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_circuit_v2_verified.py --export "C:\Users\saher\Downloads\circuits_v2_99_user_verified_20261105.zip" --output outputs/circuit_v2_verified_99_new_run
.\.venv\Scripts\python.exe -m pytest tests/unit/test_circuit_v2_experiment.py --basetemp outputs/pytest_v2_new_run -q
```

Use a new output/base directory. The evaluator refuses to overwrite a previous
run. The CVAT export and generated runtime data remain local ignored artifacts.

# Team handoff: completed circuit evaluation and YOLO v2 training

Everything needed to inspect and continue the completed circuit work is versioned: source images, approved labels, raw CVAT export, v1/v2 checkpoints, optimizer-bearing intermediate checkpoints, predictions, metrics, plots, comparison gallery, scripts and reports. Historical physics investigation reports, regression tests and an archive of their raw evidence are included too. Training does not need to be repeated after pulling.

## Continue an existing checkout

From your checkout root, preserve local changes and pull normally:

```powershell
git status
git pull --ff-only
.\.venv\Scripts\python.exe scripts/verify_circuit_handoff.py
```

Keep your existing `.venv`, SAM2 installation, CUDA/PyTorch, checkpoints and personal `.env`. Do not run `setup_windows.ps1`, recreate an environment, replace CUDA, or retrain as a verification step. Environment directories and browser profiles are machine-specific; they are not transferred through Git. Personal API credentials remain local; all shared model/data/research files are included without credentials.

The verifier checks SHA-256 and size against `requirements/circuit-handoff-v2.json` using only Python's standard library. It covers the exact shared model/data/results payload, including all eight v2 checkpoints. A missing or changed file is an error, not silently redownloaded or overwritten.

If you want to rerender historical evaluation plots without inference/training, first prepare the ignored staging copies with current checkout paths. To access the earlier raw physics evidence, restore its archive:

```powershell
.\.venv\Scripts\python.exe scripts/verify_circuit_handoff.py --prepare-staging --restore-research
```

This copies existing data and restores completed observations; it does not redo model training, inference or live provider calls. Existing different local files are protected. Historical JSON manifests retain the original laptop's absolute paths as provenance; the helper generates new local data.yaml descriptors. The synthetic source YAML now resolves relative to its own location instead of assuming `D:/AugmentedPhysics`.

## What was completed

1. The existing Python 3.12.11 environment was retained. Missing dataset/detector packages were installed, including schemdraw 0.23, ultralytics 8.4.193 and the user-authorized CPU PyTorch 2.14.0 / torchvision 0.29.0. The original GPU environment snapshot is still available; the CPU inventory is separately recorded in `requirements/windows-py312-cpu-environment.json` and its lock file. These are observed snapshots, not instructions to bulk-replace a working environment.
2. The original YOLO26n detector was trained on 480 synthetic images, with 120 synthetic validation images. Its v1 best.pt is included in Git and retains its original hash.
3. Predictions were generated for all 59 real textbook screenshots at imgsz 960 and confidence 0.25.
4. All 59 were annotated in CVAT with four classes. The user explicitly reviewed and approved the annotations. Exact reference labels are now in `datasets/circuits_v1/real_v1/evaluation_v1/labels`; the unchanged raw export is included under `outputs/`. AI assistance and human approval are recorded, not hidden.
5. The frozen v1 model was evaluated: real mAP50 67.15%, mAP50–95 33.39%. At confidence 0.25 / matching IoU 0.50: 245 TP, 67 FP, 37 FN. All 59 comparison images, PR curves and confusion matrices are available.
6. The user then authorized using all 59 real diagrams for training and will provide a fresh test set later. V2 was fine-tuned for 30 epochs using those 59 images plus 120 synthetic training rehearsal examples. The first 10 backbone modules were frozen; the neck/head changed. CPU training took about 93 minutes. No production integration occurred.

## Current models and results

| Model | Path | Role |
|---|---|---|
| v1 | `runs/augmented_physics/circuits_synthetic_v1/weights/best.pt` | Synthetic-only baseline, preserved |
| v2 best | `runs/augmented_physics/circuits_real_v2_20261031/weights/best.pt` | Final-synthetic-validation checkpoint |
| v2 last | `runs/augmented_physics/circuits_real_v2_20261031/weights/last.pt` | Fixed 30-epoch candidate; model tensors match v2 best |
| Intermediate v2 | Same weights directory, `epoch0.pt` through `epoch25.pt` every five epochs | Optimizer-bearing recovery checkpoints; no need to restart from v1 |

The 59 real images are **training/regression data for v2**, despite the historical directory name `evaluation_v1`. V2's results on these images are training fit, not independent accuracy: mAP50 87.97%, mAP50–95 66.68%; fixed 0.25 / 0.50 matching gave 276 TP, 14 FP and 6 FN. Two of three switches remain missed at that threshold. Synthetic strict-localization mAP50–95 declined from the earlier v1 revalidation's 98.58% to 83.11%; keep both candidates and investigate this regression. Do not claim a universal improvement or deploy based on seen-image fit.

When the new real test set arrives, label it independently and evaluate both models under identical settings. Keep its book/page sources separate from these training images. YOLO boxes do not establish terminal geometry, electrical connectivity, numerical values or simulation readiness; preserve the existing CV/SAM2/OCR and review boundaries.

## Read already-completed results

- [V1 real evaluation report](reports/CIRCUIT_YOLO_REAL_EVALUATION_20261031.md).
- [All 59 v1 comparisons](../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparison_gallery.html).
- [V2 training report and failure examples](reports/CIRCUIT_YOLO_V2_FINETUNING_20261031.md).
- V2 outputs: `runs/augmented_physics/circuits_real_v2_20261031/seen_real_predictions/` and `seen_real_fit_validation/`.
- Training configuration, exact 179-image manifest, results.csv, training.log, before/after input hashes and progress.json are in the v2 run.
- Historical physics/CV investigations: `context.md`, the reports under `docs/reports/`, four `pipeline_walkthroughs_20261017` reports, and [archived evidence instructions](../research/handoff/20261031/ARCHIVE_README.md).

## Optional fresh prediction check

Existing predictions are already included. To run a new diagnostic pass on these seen training images:

```powershell
$projectPath = (Resolve-Path runs/augmented_physics).Path
$runName = 'friend_v2_' + (Get-Date -Format yyyyMMdd_HHmmss)
.\.venv\Scripts\yolo.exe detect predict model=runs/augmented_physics/circuits_real_v2_20261031/weights/best.pt source=datasets/circuits_v1/real_v1/evaluation_v1/images imgsz=960 conf=0.25 save=True save_txt=True save_conf=True device=cpu project="$projectPath" name=$runName
```

Use your existing GPU installation if desired by selecting its device. Nothing in this handoff requires changing PyTorch/CUDA. Verify imports first; install only genuinely missing packages. Keep the existing working OpenCV build rather than automatically installing a second cv2 wheel because of metadata-only dependency warnings.

## Validation and known limitations

- Web test chain: passed. Production build: passed, with existing bundle-size warnings.
- Current Python unit run with mock vision and no live provider key: **330 passed, 21 failed**. The same failures were observed before this publishing task. They include 13 circuit-generalization regressions, OCR/segmentation availability/benchmark issues and five Google SDK retry tests in this CPU environment. These are recorded limitations, not silently skipped or fixed through unrelated physics changes.
- Logs are archived under `research/handoff/20261031/validation/`. Historical reports may describe earlier checkout states or expectations; they do not override these current results.
- Both trained model states are finite, have the expected four classes, and v2 best/last tensors match. The frozen backbone matches v1 while trainable layers differ. All 1,364 original inputs were preserved during training; the old evaluation report was hash-checked separately.
- Publishing adds approved labels to their canonical directory and makes the synthetic descriptor portable. Older recorded fingerprint files remain historical observations; text line endings can differ across Git checkouts. New evaluations protect their own before/after inputs rather than demanding another machine's historical working-tree hashes.
- No credentials, virtual environments, browser account profiles, browser caches or duplicate dataset staging/cache files are required to resume this work. SAM2 foundation assets from the prior working setup remain local; the newly trained circuit weights are included directly in Git.

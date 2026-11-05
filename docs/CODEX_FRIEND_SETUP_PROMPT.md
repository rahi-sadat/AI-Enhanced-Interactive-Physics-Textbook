# Copy this prompt into Codex on the other laptop

## Current handoff — use this for an existing working checkout

```text
Continue the completed AugmentedPhysics work from origin/main. Read AGENTS.md
and docs/TEAM_HANDOFF_20261031.md. Preserve local changes and safely pull with
git pull --ff-only. Keep my existing .venv, SAM2 and PyTorch/CUDA; do not run
setup_windows.ps1, recreate environments or retrain as a setup check.

Run my existing .venv\Scripts\python.exe scripts/verify_circuit_handoff.py.
The approved annotations, v1/v2 weights, intermediate training checkpoints,
predictions, plots, comparison gallery and reports are already in Git. No new
model-assets transfer is needed for these circuit detectors. If raw historical
evidence or local evaluation staging is needed, use this verifier's
--restore-research and --prepare-staging flags; do not redo completed work.

All 59 real textbook images were used to train v2 after the original v1
evaluation. They are no longer an independent v2 test set. The next task is to
evaluate both models on the new, separately supplied real test set. Do not
integrate YOLO into production or silently treat training fit as test accuracy.
Read the documented switch weakness, localization regression and 21 existing
Python test failures before making claims. Keep my own API keys local.
```

## Historical fresh-machine setup prompt

The following is retained for an entirely new installation. It predates the
checked-in v1/v2 weights and approved real annotations. Use the current handoff
above for an existing environment; its data roles and asset locations take
precedence over the older instructions below.

```text
Set up this AugmentedPhysics checkout so it can run the same new dataset/YOLO
tools and the existing app as Rahi's laptop. Execute the setup and verification;
do not only describe commands.

1. Read AGENTS.md, PROJECT_CONTEXT.md, docs/ARCHITECTURE.md, and
   docs/WINDOWS_REPRODUCIBLE_SETUP.md. Inspect git status and preserve local work.
   Pull origin/main with --ff-only when safe. Never discard edits or reset files.

2. Inspect Windows, the Python launcher/interpreters, Node, and the GPU/driver.
   The reference is Python 3.13.5 x64, torch 2.14.0+cu130,
   torchvision 0.29.0+cu130, Ultralytics 8.4.193, and Schemdraw 0.23.
   Use requirements/windows-py313-environment.json and windows-py313.lock.txt
   as the complete observed snapshot. Do not use a legacy system Python 2.7.

3. Recreate the local .venv with Python 3.13; do not copy someone else's .venv.
   Preserve an existing incompatible .venv under a unique backup name before
   replacing it. Run:
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
   Resolve install failures using the pinned versions and official package
   indexes. The guide documents the existing EasyOCR/OpenCV metadata exception;
   do not silently upgrade dependencies or install a second conflicting cv2.
   Keep the existing app, physics algorithms, provenance and VLM configuration.

4. Run the setup again with -VerifyOnly. Confirm the Python path, pinned
   versions, key imports and CUDA operation. Report CPU-only operation honestly
   if there is no compatible NVIDIA GPU; use device=cpu for prediction.
   Never claim GPU parity when the hardware/driver is different.

5. Git intentionally excludes model weights. Locate the
   circuit_model_assets_20261031.zip supplied by Rahi; if it is missing, ask for
   its path and report the specific unavailable features. Restore with:
   .\.venv\Scripts\python.exe scripts/circuit_assets.py --restore '<actual ZIP path>'
   Then run the same script with --verify-only. Do not fabricate weights or
   substitute the 80-class pretrained checkpoint for the trained circuit model.

6. Run prediction using .\.venv\Scripts\yolo.exe and the restored
   runs/augmented_physics/circuits_synthetic_v1/weights/best.pt on the held-out
   datasets/circuits_v1/real_v1/evaluation_v1/images directory, with imgsz=960,
   conf=0.25, save=True, save_txt=True and save_conf=True. Resolve the project
   path to an absolute runs/augmented_physics path inside THIS checkout, and
   use a fresh run name. Inspect several actual overlays. Keep prediction
   labels separate from human ground truth. Do not retrain or tune on this set.

7. If training data is needed, use the generator/seed 20261030, inspect the
   twelve pilots, then generate 600 images as documented. Do not overwrite any
   existing dataset. For inference alone, regeneration and training are not
   required. Never launch the four-hour training job as an installation check.

8. Run the relevant offline tests and web build. Report known upstream test
   failures accurately, including the auto-resolution safety assertion and
   missing JS transient test; do not mask them. Configure my own .env only as
   needed for live provider features, without exposing or committing secrets.

Finish with the exact environment, GPU/CPU status, checks run, prediction output
paths, assets restored, app start commands, and any remaining limitations.
```

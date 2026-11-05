# Recreate the working Windows laptop environment

The reference machine uses Windows 11 x64, Python **3.13.5**, PyTorch
**2.14.0+cu130**, torchvision **0.29.0+cu130**, Ultralytics **8.4.193**, and
Schemdraw **0.23**. Its complete 93-package inventory is captured in
`requirements/windows-py313-environment.json`. The lock file pins all packages
except editable SAM-2, whose source checkout is pinned separately in that JSON.

`.venv` contains machine-specific interpreter paths and is recreated locally.
It is excluded from Git. This follows the
[Python virtual environment guidance](https://docs.python.org/3.13/library/venv.html).
CUDA operation additionally depends on the friend's GPU and NVIDIA driver;
identical Python packages cannot create GPU hardware or guarantee bit-identical
training on different machines. The CUDA wheels come from the
[official PyTorch index](https://download.pytorch.org/whl/cu130).

## Pull and set up

Install Python 3.13 x64 (prefer 3.13.5), Git, and Node.js 22.12 or later.
Run from the repository root after preserving any local edits:

```powershell
git pull --ff-only
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
```

The script creates `.venv` if absent, installs the pinned package snapshot,
clones/installs the matching SAM-2 revision, installs the web dependencies, and
verifies imports and an actual CUDA operation when CUDA is available. It uses
the virtual environment interpreter directly; activation and a global `yolo`
command are unnecessary. It never deletes an existing environment or resets a
changed SAM-2 checkout. If an existing `.venv` uses a different Python minor
version, preserve it under another name before creating the new Python 3.13 one.
`-SkipSam2` and `-SkipWeb` provide lighter optional setups.

Verify again without changing installed packages:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_windows.ps1 -VerifyOnly
```

The reference environment has one known packaging warning: EasyOCR declares
`opencv-python-headless`, while this GUI-capable installation uses
`opencv-python` to provide `cv2`. The snapshot intentionally reproduces the
observed environment using `--no-deps`, rather than installing two OpenCV
distributions over the same module. The verifier reports this exact warning
and rejects other missing/version-mismatched packages. This is a documented
metadata exception, not a claim that `pip check` is completely clean.

## Restore trained assets separately

Git includes the source, dependency snapshot, reports and the 59 curated real
evaluation PNGs. It excludes `.venv`, generated synthetic images, model weights,
run outputs, API credentials and caches. **A pull alone does not include the
trained detector.** Share `circuit_model_assets_20261031.zip` with the friend.
It contains the two trained circuit checkpoints, original YOLO26n checkpoint,
and SAM-2 tiny checkpoint, with a checked-in SHA-256 manifest.

```powershell
.\.venv\Scripts\python.exe scripts/circuit_assets.py --restore 'C:\path\to\circuit_model_assets_20261031.zip'
.\.venv\Scripts\python.exe scripts/circuit_assets.py --verify-only
```

Restoration verifies archive paths, sizes and hashes before writing, skips
identical existing weights, and refuses to overwrite different local weights.
The asset ZIP is generated on the author's machine with:

```powershell
.\.venv\Scripts\python.exe scripts/circuit_assets.py --export outputs/circuit_model_assets_20261031.zip
```

If the bundle is unavailable, report the missing trained files; do not substitute
the original 80-class pretrained checkpoint for the four-class circuit detector.
SAM-2 model code is recreated from its pinned public Git revision, not copied
from a machine-specific editable install path.

## Run the same circuit prediction

```powershell
$env:YOLO_CONFIG_DIR = Join-Path (Get-Location) 'outputs/yolo_settings'
$env:YOLO_OFFLINE = 'true'
$predictionProject = Join-Path (Get-Location) 'runs/augmented_physics'
.\.venv\Scripts\yolo.exe detect predict model=runs/augmented_physics/circuits_synthetic_v1/weights/best.pt source=datasets/circuits_v1/real_v1/evaluation_v1/images imgsz=960 conf=0.25 save=True save_txt=True save_conf=True project="$predictionProject" name=real_textbook_test_v1
```

Ultralytics chooses CUDA when available and CPU otherwise. An explicit
`device=cpu` is also available for a CPU-only laptop. Keep the project path
absolute: the tested package can nest relative project paths under `runs/detect`.
Existing run directories are preserved through automatic name increments.
Predicted labels belong under the run, separate from human evaluation labels.

## Regenerate the synthetic dataset if needed

See `docs/SYNTHETIC_CIRCUIT_DATASET.md` for the mandatory twelve-image pilot and
inspection before the complete 600-image run. The fixed seed is `20261030`.
Generation writes a data.yaml with the friend's actual repository path; do not
copy an author's absolute `D:/AugmentedPhysics` path to a different checkout.
The trained detector can perform inference without regenerating training data.
Do not retrain for 100 epochs merely to verify this setup.

## Run the platform and checks

Configure the friend's own `.env` from `.env.example` if needed. Never copy or
commit another user's API keys. Ordinary offline checks do not require Gemini:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_circuit_dataset_generator.py tests/unit/test_circuit_grounding_repair.py -q
.\.venv\Scripts\python.exe -m uvicorn apps.api.main:app --reload --port 8000
# In another PowerShell window:
npm.cmd --prefix apps/web run dev
```

The recent upstream checkout already has an auto-resolution safety-test failure
and an npm test entry for missing `tests/unit/test_circuit_transient.js`. Report
such failures explicitly rather than calling the entire repository green.
See `docs/reports/CIRCUIT_YOLO_BASELINE_20261031.md` for training and real-image
prediction results. The detector remains an offline experiment; it has not been
connected to the production ingestion or simulation pipeline.

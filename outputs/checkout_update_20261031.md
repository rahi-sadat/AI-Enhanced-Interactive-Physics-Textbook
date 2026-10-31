# AugmentedPhysics checkout update — 2026-10-31

> Follow-up completed: commit `1a572ba` supplied the verified trained best.pt. Prediction succeeded on all 59 images. See [the prediction report](circuit_prediction_20261031_1a572ba.md). The missing-weight and pending-prediction notes below describe the earlier state.

- Checkout: `D:\AugmentedPhysics`.
- Existing interpreter preserved: `D:\AugmentedPhysics\.venv\Scripts\python.exe` (Python 3.12.11).
- `git pull --ff-only origin main`: already up to date. Previous and final HEAD: `25f292069adcd29c6ab069ee9f80a6ad92d7e3b3` (125 commits). No commits newly pulled.
- Commit 119 is `7fd10bc`. Commits 120–125 were already present and were reviewed:
  - `5dcfe96`: synthetic circuit dataset generation.
  - `a2b69c3`: YOLO26n training and baseline report.
  - `8640aa7`: 59 held-out real evaluation images.
  - `7b74811`: Windows environment snapshot and setup tooling.
  - `e5c68f7`: standalone architecture/handoff report.
  - `25f2920`: versioned synthetic training dataset.
- Local tracked diff and full untracked-file status match the pre-install baseline. Nothing staged or committed.
- No previously installed distribution versions changed.
- SAM2, checkpoints, production physics/VLM configuration, evaluation images and human labels were untouched. No setup_windows.ps1, training, or dataset regeneration command was run.

## Newly installed packages

The two requested packages and only missing dependencies were installed with dependency resolution disabled, using snapshot pins. User subsequently authorized installing previously absent PyTorch. GPU inspection found AMD Radeon graphics and no NVIDIA driver; CPU builds match the snapshot's base PyTorch/torchvision releases. No CUDA/driver installation was performed. Existing NumPy, Pillow and headless OpenCV were preserved rather than downgraded/replaced.

| Package | Version |
| --- | --- |
| Jinja2 | 3.1.6 |
| MarkupSafe | 3.0.3 |
| PyYAML | 6.0.3 |
| charset-normalizer | 3.5.1 |
| contourpy | 1.3.3 |
| cycler | 0.12.1 |
| filelock | 3.32.3 |
| fonttools | 4.64.0 |
| fsspec | 2026.7.0 |
| kiwisolver | 1.5.1 |
| matplotlib | 3.11.1 |
| mpmath | 1.3.0 |
| nvidia-ml-py | 13.615.71 |
| polars | 2.1.0 |
| polars-runtime-32 | 2.1.0 |
| psutil | 7.2.2 |
| pyparsing | 3.3.2 |
| python-dateutil | 2.9.0.post0 |
| requests | 2.34.2 |
| schemdraw | 0.23 |
| setuptools | 78.1.0 |
| six | 1.17.0 |
| sympy | 1.14.0 |
| torch | 2.14.0+cpu |
| torchvision | 0.29.0+cpu |
| ultralytics | 8.4.193 |
| ultralytics-platform | 0.1.101 |
| ultralytics-thop | 2.2.3 |
| urllib3 | 2.8.0 |

## Verification

- Imports passed: schemdraw, matplotlib, ultralytics, torch, torchvision, cv2, polars.
- CPU tensor sum passed; torchvision NMS returned the expected retained index.
- `.venv\Scripts\yolo.exe version`: `8.4.193`.
- CUDA availability: false.
- `pip check` reports only `ultralytics 8.4.193 requires opencv-python, which is not installed.` Existing `opencv-python-headless==5.0.0.93` supplies working `cv2==5.0.0`; no second overlapping OpenCV distribution was installed. All other active package requirements are satisfied.
- `npm.cmd --prefix apps/web test`: passed.
- `.venv\Scripts\python.exe -m pytest tests/unit -q -p no:cacheprovider`: 330 passed, 21 failed in 99.38 seconds.
- Failures: 13 circuit generalization/grounding assertions; OCR benchmark, RapidOCR availability and SAM2 availability (one each); five mocked Gemini retry tests cannot import the absent Google SDK. These were reported without changing application code or installing unrelated platform dependencies. The initial full Python test collection was blocked by missing torch, so a fully passing pre-change Python baseline was not established.

## Trained weights and prediction

`runs/augmented_physics/circuits_synthetic_v1/weights/best.pt` is absent. User will obtain only this file from Rahi; no email was sent. No full model-assets archive was requested/restored.

Expected trained file from checked-in manifest: 5,496,133 bytes; SHA-256 `667371fa86a49cc88f4d50cc6256db26a42c7152c04344b59b976ad3eb0f5e0e`.

Prediction and visual inspection remain pending this file. No prediction output directory or predicted labels were produced. Human label directory still contains only `.gitkeep`.

After placing the trained file at its required location, run from this checkout (timestamp gives a fresh run name):

```powershell
$env:YOLO_CONFIG_DIR = 'D:\AugmentedPhysics\outputs\yolo_settings'
$env:YOLO_OFFLINE = 'true'
$runName = 'real_textbook_test_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
.\.venv\Scripts\yolo.exe detect predict model='D:\AugmentedPhysics\runs\augmented_physics\circuits_synthetic_v1\weights\best.pt' source='D:\AugmentedPhysics\datasets\circuits_v1\real_v1\evaluation_v1\images' imgsz=960 conf=0.25 save=True save_txt=True save_conf=True project='D:\AugmentedPhysics\runs\augmented_physics' name=$runName
```

Annotated images will be under `D:\AugmentedPhysics\runs\augmented_physics\<runName>\`; predictions with confidence under its `labels\` subdirectory. Inspect several annotated images after prediction. Do not copy prediction TXT files into human evaluation labels.


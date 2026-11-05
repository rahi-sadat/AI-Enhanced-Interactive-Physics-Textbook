# Circuit prediction completed — 2026-10-31

- Pulled one commit with `git pull --ff-only origin main`: `25f2920` → `1a572ba1119fdc705f8572a0dc9da8cbe909bb95` (commit 126), adding the trained best.pt and .gitignore exceptions. No application source changes.
- Model: `D:\AugmentedPhysics\runs\augmented_physics\circuits_synthetic_v1\weights\best.pt`.
- Model size: 5,496,133 bytes. SHA-256 matches checked-in manifest: `667371fa86a49cc88f4d50cc6256db26a42c7152c04344b59b976ad3eb0f5e0e`.
- Existing `.venv` used: Python 3.12.11, Ultralytics 8.4.193, torch 2.14.0+cpu. No new packages installed during this follow-up. Earlier dependency additions are in `checkout_update_20261031.md`.
- Device: CPU (AMD Ryzen 5 PRO 5675U). No training, dataset regeneration, environment replacement, SAM2 changes, CUDA/driver installation, or production configuration changes.

## Command executed successfully

```powershell
$env:YOLO_CONFIG_DIR = 'D:\AugmentedPhysics\outputs\yolo_settings'
$env:YOLO_OFFLINE = 'true'
$env:MPLBACKEND = 'Agg'
.\.venv\Scripts\yolo.exe detect predict model='D:\AugmentedPhysics\runs\augmented_physics\circuits_synthetic_v1\weights\best.pt' source='D:\AugmentedPhysics\datasets\circuits_v1\real_v1\evaluation_v1\images' imgsz=960 conf=0.25 save=True save_txt=True save_conf=True device=cpu project='D:\AugmentedPhysics\runs\augmented_physics' name=real_textbook_test_20261031_1a572ba
```

## Outputs and verification

- Annotated images: `D:\AugmentedPhysics\runs\augmented_physics\real_textbook_test_20261031_1a572ba\` — 59 JPGs.
- Predicted labels with confidence: `D:\AugmentedPhysics\runs\augmented_physics\real_textbook_test_20261031_1a572ba\labels\` — 59 TXT files.
- Predictions: 312 total — 187 resistors, 91 voltage sources, 23 capacitors, 11 switches. These are predicted counts, not verified correct counts.
- Every label row has six finite fields, class 0–3, normalized boxes within image bounds, and confidence in [0.25, 1]. All source image stems match the annotated-image and label-file stems.
- Four actual saved overlays inspected: `Screenshot 2026-10-30 232522.jpg`, `Screenshot 2026-10-30 235305.jpg`, `Screenshot 2026-10-30 234003.jpg`, `Screenshot 2026-10-31 000838.jpg`.
- Visual findings: horizontal resistors, voltage sources and capacitors detected in examples; angled resistors missed and resistor/text strokes falsely labeled as switches in other examples. Some rendered class captions overlap. No thresholds or outputs were adjusted.
- Exact local Git diff/status match the pre-pull baseline. All evaluation files, including human labels, have identical before/after SHA-256 hashes. Human labels still contain only `.gitkeep`; no model predictions were copied there.
- Prediction output directory is ignored by Git. Nothing staged or committed.
- Earlier validation: web test suite passed; Python unit suite had 330 passed and 21 failed (circuit grounding, unavailable OCR/SAM2/Google SDK); details in the environment report. These suites were not repeated because this pull only adds weights and ignore rules. This follow-up validates the actual checkpoint through full prediction and export inspection.

Real-image precision, recall and mAP cannot be established without human ground-truth annotations.

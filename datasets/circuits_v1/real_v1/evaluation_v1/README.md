# Held-out real circuit evaluation images

## Current role after the 2026-10-31 v2 training

The user reviewed and approved all 59 CVAT annotations. Their exact five-column
YOLO labels are now versioned in `labels/`, and the original CVAT export is
included in `outputs/circuits_real_eval_v1_cvat_draft_20261031.zip`.
After the v1 baseline evaluation, the user authorized training v2 on all 59
images and will supply a new test set later. These images are now training /
regression data for v2, not an independent v2 test set. See
`docs/TEAM_HANDOFF_20261031.md` before continuing work.

The following instructions describe the earlier, pre-annotation v1 evaluation.

The 59 PNG files in `images/` are user-selected textbook screenshots. They are
evaluation inputs, separate from the 480/120 synthetic training/validation split.
Keep original pixels and filenames. Bangla, English and mixed-language figures
can coexist. The detector has four classes; it does not perform OCR.

`labels/` is reserved for human-checked YOLO detection ground truth. It is
initially empty. Do not copy model predictions into it and call them ground truth.
Without human annotations, precision, recall and real-textbook mAP are unknown.

Example prediction from the repository root, after restoring the trained assets:

```powershell
$projectPath = Join-Path (Get-Location) 'runs/augmented_physics'
.\.venv\Scripts\yolo.exe detect predict model=runs/augmented_physics/circuits_synthetic_v1/weights/best.pt source=datasets/circuits_v1/real_v1/evaluation_v1/images imgsz=960 conf=0.25 save=True save_txt=True save_conf=True project="$projectPath" name=real_textbook_test_v1
```

An absolute project path avoids nesting the output below `runs/detect` in the
tested Ultralytics version. Prediction TXT files contain six fields:
`class_id x_center y_center width height confidence`; they belong under the run
directory. Human detection labels contain five fields, without confidence.

Classes: 0 resistor, 1 voltage_source, 2 capacitor, 3 switch.
Do not train or tune thresholds on this held-out set during final evaluation.

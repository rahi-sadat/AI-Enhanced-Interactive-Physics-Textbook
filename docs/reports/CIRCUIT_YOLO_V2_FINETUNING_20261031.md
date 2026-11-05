# YOLO26n v2 real-diagram fine-tuning — 2026-10-31

Training completed successfully: **all 59 user-approved textbook diagrams were used for 30 fine-tuning epochs**, together with 120 existing synthetic training images. The run took about 92.8 minutes on this laptop's CPU.

The user explicitly authorized repurposing these 59 diagrams for training and will provide a new test set later. This supersedes the earlier recommendation to retain them only as a test set. The [earlier evaluation report](CIRCUIT_YOLO_REAL_EVALUATION_20261031.md) remains an unchanged historical v1 baseline. These images are **no longer an independent test set for v2**.

## Model and training configuration

- Starting weights: `runs/augmented_physics/circuits_synthetic_v1/weights/best.pt`, preserved unchanged.
- New run: `runs/augmented_physics/circuits_real_v2_20261031`.
- Fixed-schedule v2 candidate: [weights/last.pt](../../runs/augmented_physics/circuits_real_v2_20261031/weights/last.pt).
- Native final-synthetic-validation checkpoint: [weights/best.pt](../../runs/augmented_physics/circuits_real_v2_20261031/weights/best.pt). It was not selected using an independent real validation set.
- Existing `.venv`: Python 3.12.11, torch 2.14.0+cpu, ultralytics 8.4.193. No environment or package replacement.
- 960-pixel training, batch 1 with nominal gradient accumulation to batch 8, AdamW, initial learning rate 0.0002, final LR factor 0.1, warmup 2 epochs, seed 20261031, workers 0.
- First 10 backbone modules frozen; neck and detection head fine-tuned. This is a pilot adaptation, not full-backbone training.
- Native on-the-fly augmentation included ±20° rotation, scale/translation, horizontal flips and brightness changes. Mosaic and mixup were disabled. Original image files and annotations were never transformed or overwritten.
- Synthetic rehearsal: 12 existing training images from each of 10 topology families, sampled deterministically. No synthetic dataset regeneration occurred.
- Training: 179 images / 977 boxes, including all 59 real images / 282 boxes.
- Validation: the original 120 synthetic validation images / 670 boxes, excluded from training. Validation ran at the final epoch; there was no real holdout, early stopping, or model selection on a new real test set.

Full settings and the exact selected image list are in [training_manifest.json](../../runs/augmented_physics/circuits_real_v2_20261031/training_manifest.json) and [data_manifest.json](../../runs/augmented_physics/circuits_real_v2_20261031/data_manifest.json).

## Results on the 59 real images: training fit only

Official validation used confidence floor 0.001 for PR/AP calculation. P/R are class-macro values at the standard maximum-mean-F1 point; they differ from fixed-confidence micro counts below.

| Class | Reference instances | Precision | Recall | AP50 | AP50–95 |
|---|---:|---:|---:|---:|---:|
| Resistor | 203 | 98.78% | 99.01% | 99.50% | 82.78% |
| Voltage source | 72 | 90.17% | 97.22% | 97.95% | 79.53% |
| Capacitor | 4 | 100.00% | 99.68% | 99.50% | 62.15% |
| Switch | 3 | 48.64% | 63.96% | 54.95% | 42.25% |
| Overall (class macro) | 282 | 84.40% | 89.97% | 87.97% | 66.68% |

At confidence ≥0.25 and same-class matching IoU ≥0.50, one-to-one in descending confidence order:

| Class | TP | FP | FN | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| Resistor | 201 | 3 | 2 | 98.53% | 99.01% |
| Voltage source | 70 | 7 | 2 | 90.91% | 97.22% |
| Capacitor | 4 | 0 | 0 | 100.00% | 100.00% |
| Switch | 1 | 4 | 2 | 20.00% | 33.33% |
| Overall (micro) | 276 | 14 | 6 | 95.17% | 97.87% |

For context, v1's earlier detections on these same images had 245 TP / 67 FP / 37 FN, mAP50 67.15%, and mAP50–95 33.39%. **That is a pre-training versus post-training-fit comparison, not a measured gain on unseen images.** Fine-tuning and inspection can produce memorization, especially with only 4 capacitors and 3 switches.

## Visual checks and remaining failures

All 59 new annotated prediction JPGs and confidence-bearing TXT files were saved in [seen_real_predictions](../../runs/augmented_physics/circuits_real_v2_20261031/seen_real_predictions).

Four saved overlays were inspected:

- [235305: diagonal resistors](<../../runs/augmented_physics/circuits_real_v2_20261031/seen_real_predictions/Screenshot 2026-10-30 235305.jpg>): all four diagonal resistors and the source are now TP; a false switch remains on printed resistance text. Counts: 5 TP / 1 FP / 0 FN, compared with v1's 1 / 1 / 4.
- [234003: bridge diagram](<../../runs/augmented_physics/circuits_real_v2_20261031/seen_real_predictions/Screenshot 2026-10-30 234003.jpg>): 6 TP / 4 FP / 1 FN, compared with 3 / 4 / 4 previously. Crowded labels and overlapping/partial predictions remain.
- [234647: open switch](<../../runs/augmented_physics/circuits_real_v2_20261031/seen_real_predictions/Screenshot 2026-10-30 234647.jpg>): the false capacitor on the cell is gone, but the open switch is still missed. Counts: 4 TP / 0 FP / 1 FN.
- [001508: battery grouping](<../../runs/augmented_physics/circuits_real_v2_20261031/seen_real_predictions/Screenshot 2026-10-31 001508.jpg>): the battery is now one correctly localized source, and all three resistors are TP. Counts: 4 TP / 0 FP / 0 FN, compared with 3 / 4 / 1 previously.

Per-image fixed-threshold counts are in [seen_real_fixed_conf025.json](../../runs/augmented_physics/circuits_real_v2_20261031/seen_real_fixed_conf025.json). PR curves, confusion matrices and label/prediction previews for the real training-fit pass are in [seen_real_fit_validation](../../runs/augmented_physics/circuits_real_v2_20261031/seen_real_fit_validation).

## Synthetic regression and limitations

| Synthetic validation | Precision | Recall | mAP50 | mAP50–95 |
|---|---:|---:|---:|---:|
| v1 prior CPU revalidation | 99.95% | 100.00% | 99.50% | 98.58% |
| v2 final synthetic validation | 99.73% | 99.86% | 99.47% | 83.11% |

Detection ranking at IoU 0.50 was largely retained, but strict localization performance fell substantially. The validation batching differs between the earlier standalone run and training's final validator, so this is not an exact same-configuration ablation. The magnitude of the drop is material and should not be hidden or attributed conclusively to a single cause. Changed box localization, augmentation, annotation conventions and adaptation are possible contributors; they were not isolated experimentally.

Keep v1 alongside this v2 candidate. Do not claim v2 is universally better or deploy it based on training fit. Switches remain weak even on seen images. A future improvement study should examine the localization regression, switch coverage, box conventions and the amount of synthetic rehearsal; additional data should include more real capacitors and switches, diagonal resistors, instruments, nodes and text negatives.

When the user supplies a new, book/page-disjoint real test set, evaluate both v1 and v2 with identical settings and report per-class counts, detection AP, localization errors and false positives. Detection scores alone still do not establish SAM2 mask quality, verified terminal/wire topology, OCR association, numerical parameters or simulation readiness. No production pipeline integration occurred.

## Preservation and reproduction

- All 1,364 fingerprinted original dataset, label, export, v1 checkpoint and previous prediction-label files matched their pre-training SHA-256 hashes.
- The historical real evaluation report was separately hash-checked and preserved.
- The reserved original human label directory still contains only `.gitkeep`; training labels were copied from the approved CVAT ZIP into the new run.
- No synthetic source images, original textbook pixels, human annotations, production physics/VLM settings, environment packages or unrelated tracked files were modified.
- `results.csv` confirms 30 completed epochs; `progress.json` and `training_report.json` report completion. Native intermediate resumable checkpoints were saved every five epochs.

Reproduce with a fresh name using the existing interpreter:

```powershell
.\.venv\Scripts\python.exe scripts/fine_tune_circuit_yolo_v2.py --name circuits_real_v2_reproduction --epochs 30 --seed 20261031
```

The training script refuses existing run directories. Raw run details are in [training_report.json](../../runs/augmented_physics/circuits_real_v2_20261031/training_report.json), [TRAINING_REPORT.md](../../runs/augmented_physics/circuits_real_v2_20261031/TRAINING_REPORT.md), `training.log`, `args.yaml`, `results.csv`, and the before/after input fingerprints under the run directory.

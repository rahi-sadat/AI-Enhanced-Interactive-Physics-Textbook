# YOLO v2 pilot fine-tuning — 2026-10-31

The user authorized repurposing all 59 reviewed real diagrams for training and will supply a new test set later.
The previous real evaluation report remains a historical pre-training baseline. These 59 images are no longer an independent v2 test set.

Completed 30 epochs from the existing synthetic v1 best.pt at 960 px, CPU, batch 1, nominal accumulated batch 8, AdamW lr0=0.0002.
First 10 backbone modules were frozen; neck and detection head were fine-tuned. Training used all 59 real images / 282 boxes plus 120 existing synthetic training images, stratified 12 per topology.
The original 120 synthetic validation images were excluded from training. Only final-epoch synthetic validation was used; no independent real test set is available.

| Dataset | Precision | Recall | mAP50 | mAP50–95 |
|---|---:|---:|---:|---:|
| Synthetic validation | 0.9973 | 0.9986 | 0.9947 | 0.8311 |
| Seen real images — training fit only | 0.8440 | 0.8997 | 0.8797 | 0.6668 |

Use `weights/last.pt` as the fixed-schedule v2 candidate; `weights/best.pt` is the native final-synthetic-validation checkpoint, not a claim of best real generalization.
Original images, CVAT ZIP, v1 model, synthetic source files, prediction labels and historical real evaluation report were preserved with SHA-256 checks.
No production integration or environment replacement was performed. Independent performance must be measured on the user's forthcoming book/page-disjoint test set.

Artifacts: `data_manifest.json`, `training_manifest.json`, `training.log`, `results.csv`, `progress.json`, `training_report.json`, `seen_real_fit_validation/`, `seen_real_predictions/`.

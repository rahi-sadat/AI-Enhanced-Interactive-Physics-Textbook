# Real circuit evaluation: CVAT annotation draft

> **Later status update (2026-10-31):** The user confirmed review and approval
> of all 59 annotations. The approved labels are now versioned under the real
> dataset's `labels/` directory. The v1 evaluation completed, then the user
> authorized using all 59 images for v2 training. They are now training/regression
> data for v2. See `docs/TEAM_HANDOFF_20261031.md`; the original draft provenance
> below and the raw export remain intact as historical records.

All 59 unchanged source images were inspected and annotated through the CVAT UI. This is an AI-assisted draft for human review, not verified human ground truth. No model predictions were imported as annotations.

- Project: https://app.cvat.ai/projects/459993
- Task: https://app.cvat.ai/tasks/2727411
- Job: https://app.cvat.ai/tasks/2727411/jobs/4681966
- Task name: `evaluation_v1 - 59 originals - AI-assisted draft - human review pending`
- Subset: `test`; job stage: `validation`; state: `new`, awaiting review.

## Export

`circuits_real_eval_v1_cvat_draft_20261031.zip` is the unchanged CVAT-exported **Ultralytics YOLO Detection 1.0** annotations-only archive.

- 59 label files, one for each source image; 282 bounding boxes.
- Class order: 0 `resistor` (203), 1 `voltage_source` (72), 2 `capacitor` (4), 3 `switch` (3).
- Archive size: 23,641 bytes.
- SHA-256: `d57826c7933b9515c8d408c7ed3ca9590eab4d3303156f0341a88e495d6608c8`.
- CRC integrity, exact class order, filename coverage, five-column YOLO rows, finite coordinates, positive box dimensions, and image bounds passed checks.
- Per-image counts and checks: `circuits_real_eval_v1_cvat_draft_20261031_audit.json`.

CVAT rejected the initial export with images because the account does not allow it. The annotations-only export succeeded without an upgrade. The ZIP contains `data.yaml`, `test.txt`, and `labels/test/*.txt`; original images remain at `datasets/circuits_v1/real_v1/evaluation_v1/images`. An unchanged upload archive is also available as `outputs/cvat_evaluation_v1_originals_59.zip`.

The raw CVAT `test.txt` uses `data/images/test/*.png`, while labels are under `labels/test/`. Keep this export intact for review. After human approval, prepare a separate validation directory with consistent image/label paths and an adjusted manifest before running YOLO validation. No precision, recall, or mAP has been computed from this draft.

## Annotation conventions and review

Boxes cover visible symbol bodies, excluding adjacent wires and printed values where practical. Both zigzag and rectangular resistors, diagonal components, cell/battery sources, capacitors, and switches were considered. Multi-cell batteries drawn as one source were grouped; distinct named sources were separated. Ammeter/voltmeter circles, nodes, probes, and wire junctions were not assigned to these four component classes. Printed internal resistance alone does not establish a drawn resistor symbol.

Human review should check every image, especially diagonal resistor bounds, cell/battery grouping, plug-key symbols, faint or overlapping strokes, and exclusions of measurement instruments. CVAT's UI may describe the drawing source as manual; these boxes were drawn by an AI assistant and remain unverified until reviewed by a person.

## Preservation and prior setup

Human evaluation labels still contain only `.gitkeep`. Original evaluation images and existing local Git changes were preserved. No training, synthetic dataset regeneration, production physics/VLM changes, or replacement of the environment or SAM2 was performed.

The original checkout/prediction task completed at commit `1a572ba` (commit 126), with `best.pt` present and manifest-verified. The existing `.venv` has schemdraw 0.23, ultralytics 8.4.193, and the subsequently authorized CPU PyTorch installation. See `checkout_update_20261031.md` for all 29 newly installed packages and test limitations, and `circuit_prediction_20261031_1a572ba.md` for prediction settings and inspected outputs. Prediction results remain in `runs/augmented_physics/real_textbook_test_20261031_1a572ba`.

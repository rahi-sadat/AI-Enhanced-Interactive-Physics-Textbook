# YOLO26n real textbook circuit evaluation — 2026-10-31

## Result and annotation provenance

Frozen best.pt achieved **67.15% mAP50 and 33.39% mAP50–95** on all 59 real screenshots (282 annotated instances). Overall class-macro precision was 62.08% and recall 61.39% at Ultralytics' common maximum-mean-F1 operating point.

The 59 CVAT annotations were drawn through the UI by an AI assistant, without importing model predictions. The original export remains named draft. The user explicitly confirmed in this session: **‘I reviewed and approved all 59 annotations.’** This report uses that approved export as the reference. Human approval is user-reported; no second independent annotator or inter-annotator agreement study was performed. These results measure real-image detection against that reference, not electrical graph or simulation accuracy.

## Input verification and preservation

- Source images: `datasets/circuits_v1/real_v1/evaluation_v1/images` — 59 unchanged PNGs.
- Reference: `outputs/circuits_real_eval_v1_cvat_draft_20261031.zip`; SHA-256 `d57826c7933b9515c8d408c7ed3ca9590eab4d3303156f0341a88e495d6608c8`.
- Checkpoint: `runs/augmented_physics/circuits_synthetic_v1/weights/best.pt`; SHA-256 `667371fa86a49cc88f4d50cc6256db26a42c7152c04344b59b976ad3eb0f5e0e`; matches checked-in asset manifest.
- Class IDs exactly match the checkpoint and synthetic data: 0 resistor, 1 voltage_source, 2 capacitor, 3 switch.
- Exactly one five-column reference TXT per source stem; no missing/extra files or duplicate rows. All decoded images, class IDs, finite normalized coordinates, positive dimensions and image-bound checks passed.
- CVAT's raw image-list prefix (`data/images/test`) differed from its label hierarchy (`labels/test`). Only a separate evaluation copy was given a consistent `images/test` / `labels/test` hierarchy and new data.yaml. Raw ZIP, originals, reserved human label directory, weights and previous prediction labels were unchanged.
- Synthetic validation used byte-identical copies of the existing 120 validation images and labels. All caches and generated outputs are inside the fresh evaluation run.
- No training, threshold optimization, dataset regeneration, package installation, production integration, physics algorithm changes or live VLM calls occurred.

## Method and definitions

Official Ultralytics 8.4.193 `YOLO(best.pt).val(...)` ran twice in the existing Python 3.12 .venv: real split=test and synthetic split=val. Both used imgsz=960, confidence floor=0.001, batch=4, CPU float32, workers=0, rect=True, augment=False, max_det=300 and NMS IoU argument=0.7. YOLO26n uses its native end-to-end head. The NMS argument is distinct from matching IoU. AP averages interpolated precision-recall area over confidence; mAP50–95 averages ten matching thresholds from 0.50 through 0.95. Low-confidence validation predictions are newly generated because the existing 0.25-filtered TXT files cannot provide complete PR curves or standard AP.

Official precision/recall are class-macro means at a common confidence selected from the mean-F1 curve (real 0.876877; synthetic 0.842843). This standard summary selection is descriptive, not a deployed threshold recommendation. AP and these P/R values must not be confused with fixed confidence=0.25 performance.

Separately, the 312 existing predictions at confidence≥0.25 were matched to references at same-class IoU≥0.50, one-to-one in descending confidence order. This follows the installed validator's class-aware policy. An unmatched prediction is FP and an unmatched reference is FN. A wrong class can contribute both one FP and one FN. Localization FP means unmatched same-class overlap 0.10≤IoU<0.50; it is a diagnostic subset of FP, not an extra error. Rounded six-field prediction exports and different rectangular batching may cause small differences from a fresh inference pass.

## Actual real-image validation metrics

| Class | Images containing class | Reference instances | Precision | Recall | AP50 | AP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| resistor | 58 | 203 | 100.00% | 76.10% | 91.62% | 56.19% |
| voltage_source | 58 | 72 | 83.91% | 69.44% | 77.39% | 38.55% |
| capacitor | 2 | 4 | 64.42% | 100.00% | 99.50% | 38.74% |
| switch | 3 | 3 | 0.00% | 0.00% | 0.08% | 0.06% |
| Overall (class macro) | 59 | 282 | 62.08% | 61.39% | 67.15% | 33.39% |

## Existing predictions at confidence 0.25 / matching IoU 0.50

| Class | Reference | Predictions | TP | FP | FN | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| resistor | 203 | 187 | 177 | 10 | 26 | 94.65% | 87.19% |
| voltage_source | 72 | 91 | 64 | 27 | 8 | 70.33% | 88.89% |
| capacitor | 4 | 23 | 4 | 19 | 0 | 17.39% | 100.00% |
| switch | 3 | 11 | 0 | 11 | 3 | 0.00% | 0.00% |
| Overall (micro) | 282 | 312 | 245 | 67 | 37 | 78.53% | 86.88% |

FP diagnostics: `{"background_or_unmatched": 43, "classification_error": 15, "localization_error": 9}`. The 15 classification-overlap FPs include extra wrong-class boxes on references already detected correctly; only two leftover cross-class pairs appear in the fixed confusion matrix (voltage source → capacitor). Do not add these diagnostic overlap counts to TP/FP/FN. These are heuristic box-level categories: low-IoU wrong-class fragments also fall under background_or_unmatched, so that category does not mean 43 detections on blank paper. Per-image rows and box IDs with IoUs are retained for every match and error.

All 312 TP flags across all 59 images were independently cross-checked against the installed Ultralytics `BaseValidator.match_predictions` using its own coordinate conversion and IoU function: exact agreement. Per-class/overall TP+FP=predictions and TP+FN=reference counts, including confusion-matrix margins, also passed.

### Failure examples

The following are measured examples ranked by FP+FN count. Each comparison shows original pixels, approved reference boxes, predictions, reference TP/FN and prediction FP categories. G/P indices link to the complete JSON diagnostics.

| Image | TP | FP | FN | Comparison |
|---|---:|---:|---:|---|
| Screenshot 2026-10-30 234003.png | 3 | 4 | 4 | [View](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-30 234003.png>) |
| Screenshot 2026-10-31 000005.png | 2 | 3 | 3 | [View](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-31 000005.png>) |
| Screenshot 2026-10-31 000634.png | 3 | 6 | 0 | [View](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-31 000634.png>) |
| Screenshot 2026-10-30 235305.png | 1 | 1 | 4 | [View](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-30 235305.png>) |
| Screenshot 2026-10-31 001508.png | 3 | 4 | 1 | [View](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-31 001508.png>) |
| Screenshot 2026-10-30 234517.png | 5 | 1 | 3 | [View](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-30 234517.png>) |
| Screenshot 2026-10-30 235428.png | 4 | 1 | 3 | [View](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-30 235428.png>) |
| Screenshot 2026-10-30 235951.png | 3 | 2 | 2 | [View](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-30 235951.png>) |

### Visually inspected failure evidence

- **Diagonal resistors, 235305:** all four diagonal resistors (G0/G2/G3/G4) are FN; the source is TP. A `15 Ω` text region is a false switch at confidence 0.425816. In **234003**, the four bridge resistors are missed while horizontal/vertical resistors are TP; three partial diagonal/text regions become switch FPs.
- **Additional angles, 235428:** all three diagonal resistors (G1/G2/G4) are FN, while four axis-aligned resistors are TP. Node label A is falsely detected as a resistor at confidence about 0.55. In **234517**, two angled resistors and a diagonal voltage source are missed. These are qualitative cases, not a labeled orientation-wide recall estimate.
- **Crowding and meters, 000005:** three compact horizontal resistors (G0/G1/G2) are missed too; this failure is not limited to diagonal symbols. Ammeter A becomes a voltage_source at confidence 0.97, and part of the `(0–5 A)` range text is another source FP. The actual cell is both correctly detected as a source and additionally labeled capacitor.
- **Capacitors, 000838:** all three real capacitor plate pairs are TP, with saved-prediction IoUs 0.6866, 0.6491 and 0.6259. The fourth real capacitor in 234759 is also TP (IoU 0.7324). All four are in just two images. Despite AP50=99.5%, the 0.25 operating point has 19 capacitor FPs and 17.39% precision; high ranking on four positives is not robust generalization. Official capacitor AP is zero at IoU≥0.75.
- **Switches / node negatives, 234647 and 000634:** the open switch G4 in 234647 is missed, while an extra capacitor box overlaps the correctly detected cell. In 000634, all three real targets are TP, yet four lettered node/circle regions become switch FPs (confidences 0.7604–0.9115), and both cells receive extra capacitor boxes. All three true switches in this set are FN at confidence 0.25.
- **Battery localization, 001508:** the single approved battery reference G0 is split into source boxes P3/P4 with confidences 0.844454/0.820727 and IoUs only 0.315196/0.273096. They are two localization FPs and one battery FN, despite visually finding individual plate groups. A separate capacitor FP and tiny wire-region resistor FP are also present. This illustrates why component grouping conventions matter.

The filename suffixes above refer to `Screenshot 2026-10-30 <suffix>.png` until midnight, and `Screenshot 2026-10-31 <suffix>.png` afterward; all full names and numbered boxes are in the gallery/JSON.

Low-confidence validation recovered 1 matched switch reference(s) below the old prediction threshold: `[{"image": "Screenshot 2026-10-30 232522.png", "gt_index": 2, "confidence": 0.00101691, "iou": 0.8144322499874751}]`. Very low-ranked switch matches explain the nonzero but near-zero switch AP; lowering the deployment threshold is not supported as a fix, given the high-confidence node/text false detections.

![Diagonal resistor failure](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-30 235305.png>)

![Battery localization failure](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparisons/Screenshot 2026-10-31 001508.png>)

### Component-level diagnosis

- **Resistors:** inspect diagonal branches, compact zigzags and IEC rectangles in the comparison gallery. Axis-aligned reference boxes do not encode orientation, so no numerical ‘angled resistor recall’ is claimed without an independently reviewed orientation subset. Standard class recall above includes all resistor orientations.
- **Voltage sources:** cell plates, multi-cell battery grouping and circular instruments can differ from generated source styles. The FP/IoU records separate localization and wrong-class overlap where the current annotations permit it.
- **Capacitors:** only four reference instances are present; plate-like battery strokes can produce false capacitor detections. Small-object box placement strongly affects AP at high IoU. Four examples cannot establish robust population accuracy.
- **Switches:** only three reference instances are present; plug-key and open-switch styles vary. Wire breaks, terminals and text strokes are relevant hard negatives. Do not infer coverage of switch variants from three objects.

## Synthetic versus real performance

| Dataset / source | Images | Instances | Precision | Recall | mAP50 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| Previous documented best-checkpoint synthetic baseline | 120 | 670 | 99.9512% | 100.0000% | 99.5000% | 98.0246% |
| Checkpoint embedded train_metrics (synthetic) | 120 | 670 | 99.95% | 100.00% | 99.50% | 97.97% |
| Synthetic revalidation, current CPU environment | 120 | 670 | 99.95% | 100.00% | 99.50% | 98.58% |
| Real textbook test, current CPU environment | 59 | 282 | 62.08% | 61.39% | 67.15% | 33.39% |

The directly comparable revalidation gap is **32.35 percentage points in mAP50 and 65.20 points in mAP50–95**. The historical documentation and checkpoint embedded summary differ slightly at strict IoUs; neither is silently substituted for the other. Current same-environment revalidation is the primary comparison. The historical GPU/precision/batch configuration and exact summary provenance differ; no definitive cause for their small difference is established.

Historical source: [checked-in synthetic baseline](<CIRCUIT_YOLO_BASELINE_20261031.md>); embedded checkpoint values: [checkpoint metadata and training history](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/checkpoint_metadata.json>).

| Class | Synthetic AP50 | Real AP50 | Synthetic AP50–95 | Real AP50–95 | AP50–95 gap (points) |
|---|---:|---:|---:|---:|---:|
| resistor | 99.50% | 91.62% | 99.48% | 56.19% | 43.29 |
| voltage_source | 99.50% | 77.39% | 98.92% | 38.55% | 60.37 |
| capacitor | 99.50% | 99.50% | 96.43% | 38.74% | 57.69 |
| switch | 99.50% | 0.08% | 99.50% | 0.06% | 99.44 |

The synthetic split comes from the same Schemdraw generator family as training, with controlled body boxes, symbol styles, text fonts and topology families. Real screenshots contain different print conventions, Bangla/English labels, diagonal branches, faint/blurred strokes, crowded symbols and measurement instruments absent from the four target classes. This is evidence of a domain gap, consistent with limited synthetic style/negative coverage. Class imbalance and annotation conventions also affect comparison. This observational evaluation does not isolate the causal contribution of each factor.

Metadata inspection provides concrete angle-coverage evidence: **all 1,159 training resistors are within 1.590° of a horizontal/vertical axis**; all 279 synthetic-validation resistors are within 1.595°. Neither split has a resistor more than 5° from those axes. Small whole-page scan rotations therefore did not supply the substantial diagonal resistor orientations seen in real bridge circuits. The installed checkpoint's training args also specify degrees=0.0 and shear=0.0.

## Plots and artifacts

- [All 59 visual comparisons](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/comparison_gallery.html>).
- [Per-class synthetic/real AP50–95 comparison](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/synthetic_vs_real_ap.png>).
- [Real AP versus matching IoU](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/real_ap_by_iou.png>).
- [Fixed 0.25 / 0.50 confusion matrix](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/confusion_matrix_conf025_iou050.png>): class-aware TP first, then leftover wrong-class pairs; rows=predicted, columns=reference; background holds FP/FN.
- [Ultralytics raw confusion matrix](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/real_validation/confusion_matrix.png>) and [normalized matrix](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/real_validation/confusion_matrix_normalized.png>): native class-agnostic matching IoU>0.45, confidence>0.001. These have different thresholds from the fixed-point analysis.
- [Real precision–recall curves](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/real_validation/BoxPR_curve.png>); [precision-confidence](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/real_validation/BoxP_curve.png>); [recall-confidence](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/real_validation/BoxR_curve.png>); [F1-confidence](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/real_validation/BoxF1_curve.png>).
- [Full real metrics](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/real_validation/metrics.json>); [full synthetic metrics](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/synthetic_validation/metrics.json>); [all per-box matches/errors](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/fixed_conf025_analysis.json>); [per-image error CSV](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/per_image_errors.csv>).
- [Matcher cross-check, low-confidence switch matches and angle-coverage evidence](<../../runs/augmented_physics/real_evaluation_20261031_1a572ba/analysis_verification.json>).
- Validation subdirectories include low-confidence predicted TXT files, confusion CSVs, lossless curve arrays and label/prediction batch previews.

## Limits, recommendation and next step

1. **Improve the dataset first; plan YOLO v2 fine-tuning afterward.** Collect a separate real training/development pool with diagonal resistors, IEC/ANSI variants, faint small capacitors, cells/batteries, open/closed/plug-key switches and hard negatives (A/V meters, text, nodes, wire gaps). Mix these with broader synthetic layouts and review symbol-body/battery-grouping conventions before training. Do not train or choose thresholds on these 59 test images.
2. This test set has already guided error analysis and future data choices. Retain its labels and original pixels for regression, but obtain a fresh book/page/source-disjoint final test set for an unbiased v2 claim. Near-duplicate pages or drawings should be grouped before splitting; byte hashes alone cannot detect semantic duplicates. Capacitor/switch sample sizes are particularly inadequate for broad claims; report per-class denominators.
3. **An offline experimental YOLO→SAM2/CV study can run in parallel after the data audit, without production changes.** Use frozen proposals as search regions, then evaluate mask quality, terminal endpoints, wire continuity, junction ambiguity, OCR association and graph correctness independently. Detection AP alone does not justify simulation readiness. Do not treat a class label, box, or confidence as a measured physical parameter or verified connection.
4. Preserve backend readiness/review gates and source-pixel provenance. No detector-to-MNA automatic path or student-facing integration is recommended on detection metrics alone. Require independent electrical-topology and parameter-grounding benchmarks before enabling such a path.
5. These are sample-level point estimates, without confidence intervals or inter-annotator reliability estimates. Reference generation was not a blinded annotation study. Source/book identifiers and independently verified orientation tags are absent. No calibrated confidence, OCR performance, SAM2 mask performance, topology correctness or physical simulation accuracy was measured.

## Reproduce

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_circuit_yolo_real.py --name real_evaluation_20261031_reproduction --report outputs/circuit_evaluation_reproduction.md --human-approved
```

Use a fresh run name. The script refuses existing runs and preserves the raw inputs, runs both frozen validations, creates all comparison figures, and generates this report. `--analyze-only` regenerates derived analysis/report from an existing run without inference. Human approval is required explicitly before an initial evaluation run.

Run: `runs/augmented_physics/real_evaluation_20261031_1a572ba`. Environment and settings: `execution_manifest.json`. Source SHA-256 snapshots: `input_fingerprints_before.json` / `input_fingerprints_after.json`. Code/package provenance: `evaluator_sha256` and `ultralytics_source_sha256` in the execution manifest. No unrelated source changes were required.

# Circuit detector baseline: synthetic training and real-image prediction

The 600-image Schemdraw dataset has 480 training and 120 validation images,
with 3,393 ground-truth objects: 1,438 resistors, 634 voltage sources,
798 capacitors and 523 switches. It has ten topology families (60 images each),
ten symbol styles and eleven image resolutions. Validation found zero duplicate
images or invalid annotations. Twelve annotated pilots were inspected first.

Pretrained YOLO26n was fine-tuned for all 100 epochs at imgsz=960, batch=8,
seed=20261030, on an RTX 3050 6GB laptop GPU. Ultralytics was 8.4.193 and
PyTorch 2.14.0+cu130. Windows paging-file exhaustion with multiprocessing was
resolved using workers=0. Image size and batch size were retained. The completed
run took 16,030 seconds of wall-clock time (about 4 h 27 min).
All 1,242 original synthetic dataset files matched their before/after hashes.

Best-checkpoint results on 120 **synthetic** validation images (670 objects):

| Class | Objects | Precision | Recall | mAP50 | mAP50–95 |
|---|---:|---:|---:|---:|---:|
| resistor | 279 | 0.999630 | 1.000000 | 0.995000 | 0.993576 |
| voltage_source | 128 | 0.999511 | 1.000000 | 0.995000 | 0.983242 |
| capacitor | 160 | 0.999648 | 1.000000 | 0.995000 | 0.950215 |
| switch | 103 | 0.999259 | 1.000000 | 0.995000 | 0.993951 |
| Overall | 670 | 0.999512 | 1.000000 | 0.995000 | 0.980246 |

The model outputs component class, confidence and symbol-body boxes. It does not
extract terminals, perform OCR, reconstruct electrical nodes or establish scene
readiness. Its integration into production recognition is future work.

## Held-out real textbook screenshots

The user supplied 59 PNGs, kept separate from training. Running the frozen
best.pt with imgsz=960 and conf=0.25 produced 59 annotated JPGs and 59 predicted
label files, containing 312 predictions: 187 resistors, 91 voltage sources,
23 capacitors and 11 switches. No image had zero predictions, and all exported
YOLO rows passed finite-coordinate/class/bounds checks.

These are **predicted counts**, not counts of verified correct detections.
Visual inspection found missed angled resistors and a false switch near
resistor/text strokes in `Screenshot 2026-10-30 235305.png`. Some horizontal
resistors, batteries and capacitors were detected in other examples. The real
ground-truth label directory is empty, so real-image precision/recall/mAP remain
unknown. The high synthetic validation score does not establish real-textbook
recognition accuracy.

## Reproduction and artifact locations

- Generator: `scripts/generate_circuit_dataset.py`.
- Training: `scripts/train_circuit_yolo.py` (defaults 100 epochs, 960, batch 8).
- Environment: `requirements/windows-py313.lock.txt` and the Windows setup guide.
- Trained weights: `runs/augmented_physics/circuits_synthetic_v1/weights/best.pt`
  and `last.pt`, distributed in the separately shared asset ZIP, not Git.
- Raw training reports, CSV, plots and twelve synthetic predictions remain in
  that ignored training-run directory.
- Real predictions and contact sheets remain under
  `runs/augmented_physics/real_textbook_test_v1/`.
- The 59 original held-out images are versioned under
  `datasets/circuits_v1/real_v1/evaluation_v1/images/`.

The original pre-pull CV/OCR stash is retained as a recovery copy. Integration
preserves newer capacitor detection and polarity checks; experimental relaxations
that bypassed continuous raster evidence or ambiguity rejection were not enabled.

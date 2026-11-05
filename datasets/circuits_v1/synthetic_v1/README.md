# Synthetic printed circuit dataset v1

600 synthetic PNG diagrams generated with Schemdraw; seed **20261030**.
80% train / 20% validation. Classes: 0 resistor, 1 voltage_source,
2 capacitor, 3 switch. Every diagram has 2–8 target components,
at least one resistor and at least one voltage source.

Regenerate from the repository root:

```powershell
python -m pip install -r scripts/requirements-circuit-dataset.txt
python scripts/generate_circuit_dataset.py --count 600 --seed 20261030 --output datasets/circuits_v1/synthetic_v1 --preview
python scripts/generate_circuit_dataset.py --output datasets/circuits_v1/synthetic_v1 --validate
```

Existing outputs are refused. `--overwrite` only replaces directories bearing
this generator's marker, and is restricted to descendants of the current directory.

## Annotation contract

YOLO labels contain symbol bodies only: ANSI/IEC resistor, cell/battery/DC
source, capacitor plates (flat/curved), switch blade and contact rings.
Wires and external printed text, including capacitor polarity marks, have
separate metadata and are excluded from target boxes. Intrinsic DC-source
signs inside its circle are part of that symbol.

Coordinates are continuous native `source_px`: origin top left, x right,
y down. Boxes use `[x_min,y_min,x_max,y_max]` with exclusive geometric
upper bounds; terminals/text positions are `[x,y]`. Values are canonical
ohm, V, F; switches have null numeric value/unit and an explicit state.
Values remain known in metadata even when omitted from the printed image;
`label_mode` and each component's `text` record what is actually visible.
Values have `synthetic_ground_truth` provenance and are never runtime evidence.

Each JSONL row records its image/label paths, dimensions, seed, PNG SHA-256,
topology, render affine, appearance, components, separate text boxes,
electrical nodes, explicit wire paths, junctions and terminal-node connections.
Terminal a/b are the native symbol-body attachment anchors; extended wire
leads are separate paths. Node membership is derived only from explicit wires.
Open switches have distinct nodes and an open blade; no wire spans the gap.
Polarized capacitors record their positive terminal; voltage sources record
positive terminal and battery cell count.

The body artist extents come from Schemdraw's native segments, excluding
automatic lead extensions, plus their measured physical stroke width.
The exact Matplotlib display-to-PNG affine maps body geometry, wires,
terminals, nodes and text. Minor scan rotation is rendered through this same
affine. Blur, scan noise and a JPEG encode/decode round trip are photometric
only. The final output is always PNG; no resizing or cropping follows labels.

`previews/annotated_samples/` shows colored boxes, orange terminal points
(a/b) and gray external text boxes. `contact_sheet.png` samples the dataset;
`previews/contact_sheets/` covers every image in pages of 60.
See `dataset_report.json` for actual counts, hashes and read-back validation.

All validation examples are synthetic and share the generator's style family.
Synthetic validation is not evidence of real-textbook recognition accuracy.
Collect a separate, held-out real printed textbook evaluation set before
assessing a trained detector. No YOLO model is trained here.

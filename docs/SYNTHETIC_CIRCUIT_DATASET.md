# Synthetic printed circuit dataset development

This offline tool generates training data independently of the recognition and
simulation applications. It imports no production modules and calls no external
AI, OCR, or image-generation service. It does not train a detector.

From the repository root, install the optional dataset requirements into your
development virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements-circuit-dataset.txt
```

Generate and **inspect the twelve pilots before the full run**:

```powershell
.\.venv\Scripts\python.exe scripts/generate_circuit_dataset.py --count 12 --seed 20261030 --output outputs/circuit_dataset_pilot_20261030 --preview
# Inspect previews/annotated_samples/ and previews/annotated_contact_sheet.png.
.\.venv\Scripts\python.exe scripts/generate_circuit_dataset.py --count 600 --seed 20261030 --output datasets/circuits_v1/synthetic_v1 --preview
.\.venv\Scripts\python.exe scripts/generate_circuit_dataset.py --output datasets/circuits_v1/synthetic_v1 --validate
.\.venv\Scripts\python.exe -m pytest tests/unit/test_circuit_dataset_generator.py -q
```

The interpreter can also be plain `python` when that environment is activated.
The implementation uses `scripts/`, the repository's existing CLI convention.
Generated dataset directories are Git-ignored. No existing fixtures are replaced.
Every run refuses an existing output directory unless `--overwrite` is explicit.
Even with that option, only a marked generator output below the current working
directory can be replaced. Validation is read-only and returns exit code 1 for
invalid data. Generation validates its output and also exits nonzero on failure.

The layout is `images/{train,val}`, `labels/{train,val}`, `metadata/{train,val}.jsonl`,
`previews/annotated_samples`, `previews/contact_sheet.png`, `data.yaml`,
`dataset_report.json`, and an automatically generated `README.md`.
`previews/contact_sheets/all_*.png` covers all images, sixty per page.
`--preview` saves 24 annotated individual previews; otherwise twelve are saved.

The fixed classes are 0 resistor (ANSI/IEC), 1 voltage_source (single cell,
two-cell battery, circular DC), 2 capacitor (flat or polarized flat/curved), and
3 switch (open/closed contacts). Ten topology families are scheduled evenly;
counts, branch lengths, component order, orientations, appearance and values
vary independently. Every sample has 2–8 objects, a resistor and a source.
The 600-image generation requires at least 300 instances of each class.
Splits are 80/20 and stratified by topology. Each image has its own seed and is
rendered once; no image is reused for augmented samples in the other split.
The global seed, accepted sample seeds and deterministic layout rejections are
recorded. Exact raster reproduction requires the pinned versions and bundled
DejaVu fonts; cross-platform floating-point rasterization may still differ.

Symbol-body annotation uses Schemdraw 0.23 native segments wrapped in a custom
`Element`, excluding `Element2Term`'s automatic lead extensions. Terminal a/b
come from the native segment endpoints. An explicit closed-switch blade joins
the centers of the native contact circles. Polarity marks are measured external
text, while intrinsic signs inside a circular DC source remain part of its body.
Bounding boxes union actual Matplotlib body artist extents with half the
physical stroke width (`linewidth_pt * dpi / 144`). This excludes external
wires and labels without arbitrary offsets. Read the
[official custom-element documentation](https://schemdraw.readthedocs.io/en/latest/usage/customizing.html)
and [segment API](https://schemdraw.readthedocs.io/en/latest/classes/segments.html)
for the interfaces used here.

Coordinates use continuous `source_px`, top-left origin, x right and y down.
An explicit affine maps drawing units through scan rotation into final pixels.
All body boxes, terminal anchors, text positions/boxes, wire endpoints and node
positions use the same transform. Blur, noise and JPEG encode/decode degradation
do not change coordinates; output files are PNG. There is no subsequent crop,
resize or image-space rotation. Text is measured from the actual font renderer
and rejected if it overlaps any body, wire or earlier text. Photometric blur
can produce a faint halo outside the geometric stroke box, as in ordinary
object-detection annotations; the box encloses the symbol's underlying geometry.

Each JSONL record includes final image dimensions, PNG hash, seed, appearance,
topology, label mode, affine, components, wires, nodes and explicit terminal-node
connections. Components contain IDs, class ID/name, pixel boxes, terminals,
physical values in ohm/V/F, display value, designator, measured external text,
symbol style, switch state and polarity where applicable. Values are tagged
`synthetic_ground_truth`; they remain recorded even when not printed. Switch
value/unit are null. The metadata is independent dataset ground truth, not
BookIR and not evidence for production compilation. Open switches connect to
two distinct conductor nodes and have no conductor crossing their open gap.

Validation reads every PNG, label and metadata row from disk. It checks counts,
splits, filename pairing, decode errors, exact YOLO/pixel box agreement, finite
coordinates, class mapping and minimum class counts, component counts and
required types, visibility of symbol ink, text/body separation, terminal raster
support, node references, wire attachments and independently reconstructed
conductor connectivity. SHA-256 checks both encoded files and decoded pixels,
detecting duplicate images and modified files. Independent raster regression
tests verify that measured boxes contain body ink in every symbol style and
four orientations, including scan rotation. Corruption tests demonstrate that
the validator rejects shifted boxes, broken terminals and missing labels.

All examples, including validation, are synthetic. This tool provides no evidence
of recognition accuracy on real textbooks. Use separate held-out real printed
textbook images to evaluate the eventual detector, OCR binding and graph recovery.
Handwriting, full-page layouts, camera perspective, occlusion and additional
component types are outside this first dataset.

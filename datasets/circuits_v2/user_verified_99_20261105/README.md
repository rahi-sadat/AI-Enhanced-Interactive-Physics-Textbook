# User verified circuit diagrams

This directory publishes the 99 diagrams manually checked and corrected by the
user in CVAT, including ammeter and voltmeter annotations. The saved reference
was exported on 5 November 2026 from task 2740033, job 4698364.

## Contents

- `images/test/`: 99 original image files, copied without changing their bytes.
- `labels/test/`: 99 matching five-column YOLO detection annotation files.
- `annotations.xml`: CVAT image annotations, including the 38 rotated rectangles.
- `annotation_manifest.json`: original-to-published filename mapping, SHA256
  hashes, image dimensions, class counts and review provenance.
- `data.yaml`: six-class evaluation configuration, with no training split.
- `.gitattributes`: preserves exact file bytes and hashes across platforms.

| Class ID | Label | Boxes |
|---|---|---:|
| 0 | resistor | 739 |
| 1 | voltage_source | 138 |
| 2 | capacitor | 3 |
| 3 | switch | 20 |
| 4 | ammeter | 12 |
| 5 | voltmeter | 4 |
| | Total | 916 |

## Annotation formats and provenance

Images and annotations are separate files; annotation boxes are not burned into
the image pixels. Each YOLO row is
`class_id x_center y_center width height`, normalized by the original image size.
The label filename stem matches its image filename stem.

Frame prefixes avoid collisions between images sharing an original filename
stem. The CVAT XML uses these same published filenames, so it can be imported
against the published images. Every original name is retained in the manifest.
The XML preserves all original boxes, attributes and rotations. Account owner,
assignee and bugtracker metadata is omitted from the public copy. The complete
original export remains in the local ignored output directory; its hash is
recorded in the manifest.

Standard YOLO detection labels do not represent rotation. Their 38 rotated
references use the enclosing axis-aligned boxes, clipped to the original image;
use `annotations.xml` when native rotated geometry is required.

## Dataset role

This is the user-reviewed reference used for the frozen v2 comparison. Publishing
it does not train a model. The current v2 checkpoint has four output classes and
cannot emit ammeter or voltmeter predictions. Those labels are retained here for
evaluation and future explicitly authorized six-class training.

Annotations began as model-assisted proposals before the user's corrections;
they are not independent blind annotations. Exact file identity does not prove
independence from related source images or near duplicates. Do not silently use
these evaluation images as training data and continue calling them held out.

When calling Ultralytics, pass the absolute path to this directory's `data.yaml`
(for example, resolve it with `pathlib.Path.resolve()`). Its image paths then
resolve relative to the YAML file. No machine-specific absolute paths, runtime
uploads, caches, checkpoints or prediction outputs are included.

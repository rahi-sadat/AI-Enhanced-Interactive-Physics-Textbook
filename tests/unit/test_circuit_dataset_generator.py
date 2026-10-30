"""Offline dataset geometry and corruption checks; optional dev dependency only."""
import hashlib
import json
import random

import numpy as np
import pytest

pytest.importorskip("schemdraw", reason="Install scripts/requirements-circuit-dataset.txt")

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from PIL import Image
import schemdraw

from scripts.generate_circuit_dataset import (
    CLASSES, TOPOLOGIES, artist_box, electrical_nodes, generate_dataset,
    make_layout, make_symbol, prepare_output, render_sample, validate_dataset,
)


STYLES = (
    ("resistor", "ansi_zigzag", None), ("resistor", "iec_rectangle", None),
    ("voltage_source", "cell_1", None), ("voltage_source", "battery_2", None),
    ("voltage_source", "dc_circle", None), ("capacitor", "parallel_plates", None),
    ("capacitor", "polarized_parallel", None), ("capacitor", "polarized_curved", None),
    ("switch", "open_contacts", "open"), ("switch", "closed_contacts", "closed"),
)


@pytest.mark.parametrize("kind,style,state", STYLES)
@pytest.mark.parametrize("angle", [1.3, 91.3, 181.3, 271.3])
def test_symbol_boxes_against_independent_raster(kind, style, state, angle):
    """Rasterize symbols alone: no wire or text can conceal an incorrect box."""
    for seed in range(50):
        symbol, info = make_symbol(kind, random.Random(seed), state)
        if info["symbol_style"] == style:
            break
    else:
        pytest.fail(f"Unreachable symbol style: {style}")
    fig = Figure(figsize=(3, 3), dpi=100, facecolor="white")
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5)
    ax.set_autoscale_on(False)
    old = set(ax.get_children())
    d = schemdraw.Drawing(show=False)
    d.config(lw=1.7)
    d.add(symbol.at((-.35, -.25)).theta(angle))
    d.draw(show=False, canvas=ax)
    artists = [a for a in ax.get_children() if a not in old]
    canvas.draw()
    box = artist_box(artists, canvas.get_renderer(), 300, 100)
    pixels = np.asarray(canvas.buffer_rgba())[:, :, :3]
    ys, xs = np.where(pixels.min(axis=2) < 128)
    assert len(xs) > 10
    ink_box = [xs.min(), ys.min(), xs.max()+1, ys.max()+1]
    # Ink occupies pixel cells; allow one cell for sampling at the geometric edge.
    assert box[0]-1 <= ink_box[0] <= box[0]+2
    assert box[1]-1 <= ink_box[1] <= box[1]+2
    assert box[2]-2 <= ink_box[2] <= box[2]+1
    assert box[3]-2 <= ink_box[3] <= box[3]+1
    assert not any(hasattr(a, "get_text") for a in artists)
    fig.clear()


def test_controlled_structure_and_graph_are_not_one_repeated_circuit():
    signatures, counts = set(), {kind: 0 for kind in CLASSES}
    families = set()
    for index in range(600):
        layout = make_layout(index, random.Random(20261030+index*1_000_003))
        families.add(layout.topology)
        assert 2 <= len(layout.components) <= 8
        kinds = [c["kind"] for c in layout.components]
        assert "resistor" in kinds and "voltage_source" in kinds
        nodes = electrical_nodes(layout)
        for c in layout.components:
            assert nodes[c["a"]] != nodes[c["b"]]
            counts[c["kind"]] += 1
        signatures.add(tuple((c["kind"], nodes[c["a"]], nodes[c["b"]]) for c in layout.components))
    assert families == set(TOPOLOGIES)
    assert len(signatures) >= 100
    assert min(counts.values()) >= 300


def test_seed_reproduces_pixels_metadata_and_scan_transform():
    seed = 20261030+3*1_000_003
    first, a = render_sample(3, seed)
    second, b = render_sample(3, seed)
    assert first.tobytes() == second.tobytes()
    assert a == b
    assert a["appearance"]["scan_rotation_deg"] != 0
    matrix = np.asarray(a["drawing_to_final_px"])
    assert np.isfinite(matrix).all()
    assert abs(np.linalg.det(matrix)) > 0
    layout = make_layout(3, random.Random(seed))
    raw_nodes = electrical_nodes(layout)
    # Compare recorded PNG coordinates with independently reconstructed layout
    # vertices; this catches a dropped scan rotation, y inversion or crop shift.
    for node in a["nodes"]:
        raw = sorted(p for p, nid in raw_nodes.items() if nid == node["id"])
        expected = [(matrix @ [*p, 1])[:2] for p in raw]
        assert np.allclose(node["positions_px"], expected, atol=1e-5)


@pytest.fixture(scope="module")
def pilot(tmp_path_factory):
    root = tmp_path_factory.mktemp("dataset")/"pilot"
    report = generate_dataset(12, 20261030, root, preview=True)
    assert report["validation_passed"], report["errors"]
    return root


def test_disk_readback_and_stratified_split(pilot):
    report = validate_dataset(pilot, 12)
    assert report["validation_passed"]
    assert (report["total_images"], report["train_images"], report["val_images"]) == (12, 10, 2)
    assert report["duplicate_count"] == report["invalid_annotation_count"] == 0
    assert set(report["class_counts"]) == set(CLASSES)
    assert len(list((pilot/"previews"/"annotated_samples").glob("*.png"))) == 12
    assert (pilot/"previews"/"annotated_contact_sheet.png").is_file()


def test_existing_and_unowned_directories_are_protected(pilot, tmp_path, monkeypatch):
    before = (pilot/"dataset_report.json").read_bytes()
    with pytest.raises(ValueError, match="already exists"):
        prepare_output(pilot)
    assert (pilot/"dataset_report.json").read_bytes() == before
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="restricted"):
        prepare_output(pilot, overwrite=True)  # pytest temp is outside cwd
    unrelated = tmp_path/"unrelated"
    unrelated.mkdir()
    keep = unrelated/"keep.txt"
    keep.write_text("existing work", encoding="utf-8")
    with pytest.raises(ValueError):
        prepare_output(unrelated, overwrite=True)
    assert keep.read_text(encoding="utf-8") == "existing work"


@pytest.mark.parametrize("corruption", ["yolo", "terminal", "metadata", "missing_label", "duplicate", "decode", "node", "class", "bbox", "value", "seed", "non_object"])
def test_validator_rejects_corrupted_data(pilot, corruption):
    """Change real outputs temporarily, restoring them even if an assertion fails."""
    manifest = pilot/"metadata"/"train.jsonl"
    original_manifest = manifest.read_bytes()
    records = [json.loads(line) for line in original_manifest.decode("utf-8").splitlines()]
    record = records[0]
    label = pilot/record["label_filename"]
    image = pilot/record["image_filename"]
    original_label, original_image = label.read_bytes(), image.read_bytes()
    expected = {
        "yolo": "yolo_annotation", "terminal": "terminal_coordinates",
        "metadata": "missing_metadata", "missing_label": "image_label_pairs",
        "duplicate": "duplicate_images", "decode": "image_decode", "node": "conductor_connectivity",
        "class": "component_class", "bbox": "pixel_bbox", "value": "physical_value",
        "seed": "metadata_record", "non_object": "metadata_json",
    }[corruption]
    try:
        if corruption == "yolo":
            label.write_text("0 1.5 .5 -.2 .1\n", encoding="utf-8")
        elif corruption == "terminal":
            record["components"][0]["terminals"]["a"] = [-100, -100]
        elif corruption == "metadata":
            records.pop()
        elif corruption == "missing_label":
            label.unlink()
        elif corruption == "duplicate":
            other = pilot/records[1]["image_filename"]
            image.write_bytes(other.read_bytes())
            with Image.open(other) as decoded:
                record["width"], record["height"] = decoded.size
            record["image_sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
        elif corruption == "decode":
            image.write_bytes(b"not an image")
        elif corruption == "node":
            record["nodes"][0]["positions_px"].append([10., 10.])
        elif corruption == "class":
            record["components"][0]["class_id"] = 7
        elif corruption == "bbox":
            record["components"][0]["bbox_xyxy_px"] = [1, 1, -5, 10]
        elif corruption == "value":
            record["components"][0]["value"] = float("nan")
        elif corruption == "seed":
            del record["generation_seed"]
        elif corruption == "non_object":
            records[0] = ["invalid row"]
        manifest.write_text("\n".join(json.dumps(r) for r in records)+"\n", encoding="utf-8")
        report = validate_dataset(pilot, 12)
        assert not report["validation_passed"]
        assert expected in {e["kind"] for e in report["errors"]}, report["errors"]
    finally:
        manifest.write_bytes(original_manifest)
        label.write_bytes(original_label)
        image.write_bytes(original_image)

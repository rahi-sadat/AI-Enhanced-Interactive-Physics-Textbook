"""Compare frozen v2 predictions with the user's saved, reviewed CVAT export.

Inputs are immutable. All six labels remain in the reference, including meter
classes absent from v2. This script does not train or invoke a vision provider.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
import math
import os
from pathlib import Path
import shutil
from types import SimpleNamespace
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = ["resistor", "voltage_source", "capacitor", "switch", "ammeter", "voltmeter"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def match_boxes(targets, predictions, thresholds):
    """Use the installed Ultralytics validator's class-aware one-to-one matching."""
    import numpy as np
    import torch
    from ultralytics.engine.validator import BaseValidator
    from ultralytics.utils.metrics import box_iou

    if not predictions or not targets:
        return np.zeros((len(predictions), len(thresholds)), dtype=bool)
    gt = torch.tensor([b["xyxy"] for b in targets], dtype=torch.float32)
    pred = torch.tensor([b["xyxy"] for b in predictions], dtype=torch.float32)
    return BaseValidator.match_predictions(
        SimpleNamespace(iouv=torch.tensor(thresholds, dtype=torch.float32)),
        torch.tensor([b["class_id"] for b in predictions]),
        torch.tensor([b["class_id"] for b in targets]), box_iou(gt, pred),
    ).numpy()


def scores(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return dict(tp=tp, fp=fp, fn=fn, precision=precision, recall=recall,
                f1=2 * precision * recall / (precision + recall) if precision + recall else 0.0)


def axis_aligned_reference(xyxy, rotation, width, height):
    """Derive the enclosing visible AABB, preserving CVAT rotation separately."""
    x1, y1, x2, y2 = xyxy
    cx, cy = (x1+x2)/2, (y1+y2)/2
    angle = math.radians(rotation)
    polygon = [[cx+(x-cx)*math.cos(angle)-(y-cy)*math.sin(angle),
                cy+(x-cx)*math.sin(angle)+(y-cy)*math.cos(angle)]
               for x, y in [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]]
    aabb = [max(0, min(p[0] for p in polygon)), max(0, min(p[1] for p in polygon)),
            min(width, max(p[0] for p in polygon)), min(height, max(p[1] for p in polygon))]
    return aabb, polygon


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, default=ROOT / "outputs/circuit_v2_test_20261103/predictions.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)  # Never replace a prior reference/run.
    os.environ["YOLO_CONFIG_DIR"] = str(out / "settings")
    os.environ["YOLO_OFFLINE"] = "true"
    os.environ["MPLBACKEND"] = "Agg"
    import numpy as np
    import ultralytics
    from ultralytics.utils.metrics import ap_per_class
    from PIL import Image, ImageOps

    manifest_path = args.predictions.parent / "execution_manifest.json"
    inference = json.loads(manifest_path.read_text(encoding="utf-8"))
    weights = Path(inference["weights"])
    assert sha(weights) == inference["weights_sha256"], "Frozen checkpoint changed"
    assert list(inference["classes"].values()) == NAMES[:4]
    inputs = {str(p.resolve()): sha(p) for p in (args.export, args.predictions, manifest_path, weights)}
    shutil.copyfile(args.export, out / "cvat_user_verified.zip")
    with zipfile.ZipFile(args.export) as z:
        assert z.testzip() is None, "Export CRC failure"
        xml = z.read("annotations.xml")
    (out / "annotations.xml").write_bytes(xml)
    root = ET.fromstring(xml)
    assert root.findtext("meta/job/id") == "4698364"
    assert {n.text for n in root.findall("meta/job/labels/label/name")} == set(NAMES)
    images = root.findall("image")
    assert len(images) == 99
    predictions = {p["filename"]: p for p in json.loads(args.predictions.read_text(encoding="utf-8"))}
    assert len(predictions) == 99 and set(predictions) == {i.get("name") for i in images}
    all_tp, all_conf, all_cls, all_gt = [], [], [], []
    counts, audit, details, rotated_count = Counter(), [], [], 0
    totals = {c: dict(instances=0, predictions=0, tp=0, fp=0, fn=0) for c in range(6)}
    (out / "data/images/test").mkdir(parents=True)
    (out / "data/labels/test").mkdir(parents=True)
    for image in images:
        name = image.get("name")
        staged_name = f"{int(image.get('id')):03d}__{name}"
        saved = predictions[name]
        source = Path(saved["source"])
        assert source.name == name and sha(source) == saved["sha256"], f"Source changed: {name}"
        inputs[str(source.resolve())] = sha(source)
        with Image.open(source) as im:
            size = ImageOps.exif_transpose(im).size
        w, h = int(image.get("width")), int(image.get("height"))
        assert size == (w, h) == (saved["width"], saved["height"]), name
        targets, rows = [], []
        for box in image:
            assert box.tag == "box", f"Unsupported shape {box.tag} in {name}"
            rotation = float(box.get("rotation", "0"))
            assert math.isfinite(rotation)
            rotated_count += rotation != 0
            c = NAMES.index(box.get("label"))
            x1, y1, x2, y2 = [float(box.get(k)) for k in ("xtl", "ytl", "xbr", "ybr")]
            assert all(np.isfinite([x1, y1, x2, y2])) and 0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h, name
            aabb, polygon = axis_aligned_reference([x1, y1, x2, y2], rotation, w, h)
            targets.append(dict(class_id=c, xyxy=aabb, cvat_xyxy=[x1,y1,x2,y2],
                                rotation=rotation, polygon=polygon))
            x1,y1,x2,y2 = aabb
            rows.append(f"{c} {(x1+x2)/(2*w):.10f} {(y1+y2)/(2*h):.10f} {(x2-x1)/w:.10f} {(y2-y1)/h:.10f}\n")
            counts[NAMES[c]] += 1
            totals[c]["instances"] += 1
        pred = [dict(class_id=b["class_id"], xyxy=b["xyxy_source_px"], confidence=b["confidence"])
                for b in sorted(saved["all_detections_conf0001"], key=lambda b: -b["confidence"])]
        assert all(0 <= b["class_id"] < 4 and .001 <= b["confidence"] <= 1 for b in pred)
        tp = match_boxes(targets, pred, np.linspace(.5, .95, 10))
        all_tp.append(tp)
        all_conf.extend(b["confidence"] for b in pred)
        all_cls.extend(b["class_id"] for b in pred)
        all_gt.extend(b["class_id"] for b in targets)
        fixed = [b for b in pred if b["confidence"] >= .25]
        fixed_tp = match_boxes(targets, fixed, [.5])[:, 0]
        local = dict(tp=int(fixed_tp.sum()), fp=len(fixed)-int(fixed_tp.sum()), fn=len(targets)-int(fixed_tp.sum()))
        for c in totals:
            nt = sum(b["class_id"] == c for b in targets)
            nc = sum(b["class_id"] == c for b in fixed)
            t = sum(bool(ok) and b["class_id"] == c for b, ok in zip(fixed, fixed_tp))
            totals[c]["predictions"] += nc
            for k, v in dict(tp=t, fp=nc-t, fn=nt-t).items():
                totals[c][k] += v
        details.append(dict(filename=name, staged_filename=staged_name, frame=int(image.get("id")), **local,
                            targets=targets, predictions=[dict(b, matched=bool(ok)) for b, ok in zip(fixed, fixed_tp)]))
        label_text = "".join(rows)
        (out / "data/labels/test" / (Path(staged_name).stem + ".txt")).write_text(label_text, encoding="utf-8")
        shutil.copyfile(source, out / "data/images/test" / staged_name)
        audit.append(dict(filename=name, staged_filename=staged_name, width=w, height=h, image_sha256=sha(source),
                          label_sha256=hashlib.sha256(label_text.encode()).hexdigest(), counts=dict(Counter(NAMES[b["class_id"]] for b in targets))))
    assert len({Path(a["staged_filename"]).stem for a in audit}) == 99, "YOLO filename stem collision"
    assert len(list((out / "data/labels/test").glob("*.txt"))) == 99
    assert all(sha(out / "data/images/test" / a["staged_filename"]) == a["image_sha256"] for a in audit)
    import yaml
    (out / "data/data.yaml").write_text(yaml.safe_dump(dict(path=(out / "data").as_posix(),
        train=None, val="images/test", test="images/test", names=dict(enumerate(NAMES))), sort_keys=False), encoding="utf-8")
    ap_result = ap_per_class(np.concatenate(all_tp), np.array(all_conf), np.array(all_cls), np.array(all_gt),
                            plot=True, save_dir=out, names=dict(enumerate(NAMES)))
    ap, class_ids = ap_result[5], ap_result[6]
    per_class = []
    for c in range(6):
        t = totals[c]
        idx = list(class_ids).index(c)
        per_class.append(dict(class_id=c, name=NAMES[c], supported_by_v2=c<4,
            instances=t["instances"], predictions=t["predictions"], **scores(t["tp"], t["fp"], t["fn"]),
            ap50=float(ap[idx, 0]), ap50_95=float(ap[idx].mean())))
    aggregates = {}
    for key, subset in [("supported_four_classes", per_class[:4]), ("all_six_classes", per_class)]:
        aggregates[key] = dict(**scores(*(sum(r[k] for r in subset) for k in ("tp", "fp", "fn"))),
            instances=sum(r["instances"] for r in subset),
            map50=float(np.mean([r["ap50"] for r in subset])), map50_95=float(np.mean([r["ap50_95"] for r in subset])))
    assert inputs == {p: sha(p) for p in inputs}, "An input changed during evaluation"
    assert sha(out / "cvat_user_verified.zip") == inputs[str(args.export.resolve())]
    result = dict(evaluated_at_utc=datetime.now(timezone.utc).isoformat(), images=99,
        annotation_boxes=sum(counts.values()), counts=dict(counts), per_class=per_class, **aggregates,
        checkpoint=str(weights), checkpoint_sha256=sha(weights), cvat_job=4698364, cvat_task=2740033,
        export_sha256=sha(args.export), cvat_updated=root.findtext("meta/job/updated"),
        rotated_reference_boxes=rotated_count,
        reference_conversion="Enclosing axis-aligned boxes of rotated CVAT rectangles, clipped to source image; original XML/rotation preserved",
        cvat_dumped=root.findtext("meta/dumped"), ultralytics=ultralytics.__version__,
        matching="Installed Ultralytics BaseValidator.match_predictions, class-aware one-to-one descending confidence",
        fixed_thresholds=dict(confidence=.25, iou=.5), ap_thresholds=dict(min_confidence=.001, iou="0.50:0.05:0.95"),
        prediction_manifest=inference, inputs_unchanged=True, external_api_calls=False, training=False,
        limitations=["User-confirmed manual review of model-assisted annotations; not independent blind annotation.",
            f"{rotated_count} rotated reference boxes are evaluated using their enclosing axis-aligned boxes, matching v2's output geometry. Native rotated XML is preserved.",
            "V2 has no ammeter or voltmeter output classes. Their recall and AP are zero; they remain in the six-class reference.",
            "AP is calculated from frozen post-NMS predictions, not a new validator inference pass.",
            "Component detection metrics do not measure topology, OCR, physical correctness, or simulation accuracy.",
            "99-image sample; exact byte/pixel overlap checks do not establish source-level independence."])
    write_json(out / "metrics.json", result)
    write_json(out / "annotation_audit.json", audit)
    write_json(out / "per_image.json", details)
    write_json(out / "input_fingerprints.json", inputs)
    report(out, result, details)
    print(json.dumps({k: result[k] for k in ("images", "annotation_boxes", "counts", "supported_four_classes", "all_six_classes")}, indent=2))


def report(out, result, details):
    fmt = lambda v: f"{100*v:.2f}%"
    lines = ["# Circuit v2 against user-verified CVAT annotations", "", "99 original images; saved CVAT job 4698364, task 2740033. The original export and source bytes are preserved.", "",
        "Precision/recall/F1 below use confidence ≥ 0.25 and class-aware IoU ≥ 0.50. AP uses frozen detections ≥ 0.001.", "",
        "| Class | Reference boxes | TP | FP | FN | Precision | Recall | F1 | AP50 | AP50–95 |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in result["per_class"]:
        lines.append(f"| {r['name']} | {r['instances']} | {r['tp']} | {r['fp']} | {r['fn']} | " + " | ".join(fmt(r[k]) for k in ("precision", "recall", "f1", "ap50", "ap50_95")) + " |")
    for label, key in [("Supported four classes", "supported_four_classes"), ("All six classes", "all_six_classes")]:
        r = result[key]
        lines.extend(["", f"{label}: micro precision {fmt(r['precision'])}, recall {fmt(r['recall'])}, F1 {fmt(r['f1'])}; macro mAP50 {fmt(r['map50'])}, mAP50–95 {fmt(r['map50_95'])}."])
    lines.extend(["", "Checkpoint: `" + result["checkpoint"] + "`", "", "SHA-256: `" + result["checkpoint_sha256"] + "`", "",
                  "## Limits", ""] + ["- " + x for x in result["limitations"]])
    lines.extend(["", "## Reproduce", "", "```powershell", ".\\.venv\\Scripts\\python.exe scripts/evaluate_circuit_v2_verified.py --export <saved-CVAT-zip> --output <new-output-directory>", "```", "", "Open report.html to inspect every image and toggle the verified reference and model predictions. Red predictions are unmatched false positives; green predictions match at IoU 0.50. Blue boxes show the complete reference."])
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    rows = []
    for row in sorted(details, key=lambda r: -(r["fp"]+r["fn"])):
        audit = next(a for a in json.loads((out / "annotation_audit.json").read_text()) if a["filename"] == row["filename"])
        shapes = []
        for kind, boxes in [("truth", row["targets"]), ("prediction", row["predictions"])]:
            for b in boxes:
                x1,y1,x2,y2 = b["xyxy"]
                color = "#0085ff" if kind == "truth" else ("#16803b" if b["matched"] else "#e12727")
                label = NAMES[b["class_id"]] + (f" {b['confidence']:.2f}" if kind == "prediction" else " verified")
                if kind == "truth":
                    points = " ".join(f"{x},{y}" for x,y in b["polygon"])
                    shapes.append(f'<polygon class="truth" points="{points}" fill="none" stroke="{color}" vector-effect="non-scaling-stroke"><title>{html.escape(label)}</title></polygon>')
                else:
                    shapes.append(f'<rect class="{kind}" x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" fill="none" stroke="{color}" vector-effect="non-scaling-stroke"><title>{html.escape(label)}</title></rect>')
        from urllib.parse import quote
        rows.append(f'<article data-errors="{row["fp"]+row["fn"]}"><h3>Frame {row["frame"]}: {html.escape(row["filename"])} — TP {row["tp"]}, FP {row["fp"]}, FN {row["fn"]}</h3><div class="image"><img src="data/images/test/{quote(row["staged_filename"])}"><svg viewBox="0 0 {audit["width"]} {audit["height"]}">{"".join(shapes)}</svg></div></article>')
    (out / "report.html").write_text('''<!doctype html><meta charset="utf-8"><title>Circuit v2 verified evaluation</title>
<style>body{font:16px system-ui;max-width:1100px;margin:32px auto;padding:0 20px;background:#f1f5f9;color:#17243b}article{background:white;padding:20px;margin:25px 0;border-radius:8px}.image{position:relative;max-width:100%}img{display:block;width:100%}svg{position:absolute;inset:0;width:100%;height:100%}rect,polygon{stroke-width:2}body.hide-truth .truth,body.hide-prediction .prediction{display:none}label{display:inline-block;margin:12px}</style>
<h1>V2 against your verified annotations</h1><p>99 images, six classes. Blue: verified reference. Green: matched model prediction. Red: unmatched prediction. Hover over boxes for labels. Sorted by total missed and extra predictions.</p>
<p>Confidence ≥ 0.25, IoU ≥ 0.50. Rotated reference rectangles are shown in their native orientation; metrics compare their enclosing axis-aligned boxes. V2 supports resistor, voltage_source, capacitor and switch; ammeter and voltmeter have no model output.</p>
<p><a href="REPORT.md">Metrics and limitations</a> · <a href="metrics.json">Full metrics</a></p>
<label><input type="checkbox" checked onchange="document.body.classList.toggle('hide-truth',!this.checked)">Verified reference</label>
<label><input type="checkbox" checked onchange="document.body.classList.toggle('hide-prediction',!this.checked)">Model predictions</label>
<label><input type="checkbox" onchange="for(const a of document.querySelectorAll('article'))a.hidden=this.checked&&a.dataset.errors==='0'">Only images with errors</label>
''' + "\n".join(rows), encoding="utf-8")


if __name__ == "__main__":
    main()

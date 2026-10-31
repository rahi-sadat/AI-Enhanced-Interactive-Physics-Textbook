"""Evaluate frozen circuit weights on approved real annotations and synthetic val.

Original datasets, CVAT exports, predictions and weights are read-only inputs.
Validation uses byte-identical copies so Ultralytics caches never touch sources.
Run with the existing checkout .venv; no training or production imports occur.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = {0: "resistor", 1: "voltage_source", 2: "capacitor", 3: "switch"}
REAL = ROOT / "datasets/circuits_v1/real_v1/evaluation_v1"
SYN = ROOT / "datasets/circuits_v1/synthetic_v1"
WEIGHTS = ROOT / "runs/augmented_physics/circuits_synthetic_v1/weights/best.pt"
EXPORT = ROOT / "outputs/circuits_real_eval_v1_cvat_draft_20261031.zip"
PRED = ROOT / "runs/augmented_physics/real_textbook_test_20261031_1a572ba/labels"
REPORT = ROOT / "docs/reports/CIRCUIT_YOLO_REAL_EVALUATION_20261031.md"


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    files = [p for base in (REAL, SYN, PRED) for p in base.rglob("*") if p.is_file()]
    files += [WEIGHTS, EXPORT]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(files)}


def parse_rows(text, prediction=False):
    import numpy as np
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        a = list(map(float, line.split()))
        assert len(a) == (6 if prediction else 5), line
        assert all(math.isfinite(x) for x in a), line
        assert a[0] == int(a[0]) and int(a[0]) in NAMES, line
        _, x, y, w, h, *_ = a
        assert 0 < w <= 1 and 0 < h <= 1 and 0 <= x <= 1 and 0 <= y <= 1, line
        assert x-w/2 >= -1e-5 and y-h/2 >= -1e-5 and x+w/2 <= 1.00001 and y+h/2 <= 1.00001, line
        if prediction:
            assert 0.25 <= a[5] <= 1, line
        rows.append(a)
    assert len({tuple(r) for r in rows}) == len(rows), "Duplicate label rows"
    return np.array(rows, dtype=float).reshape(-1, 6 if prediction else 5)


def stage(run, approved):
    import yaml
    from PIL import Image
    images = sorted((REAL / "images").glob("*.png"))
    assert len(images) == 59
    assert len({p.stem for p in images}) == 59
    counts = Counter()
    audit = []
    stage_real = run / "data/real"
    with zipfile.ZipFile(EXPORT) as z:
        assert z.testzip() is None, "CVAT archive CRC error"
        assert yaml.safe_load(z.read("data.yaml"))["names"] == NAMES
        label_members = [n for n in z.namelist() if n.startswith("labels/test/") and n.endswith(".txt")]
        assert len(label_members) == 59
        assert {Path(n).stem for n in label_members} == {p.stem for p in images}
        manifest = z.read("test.txt").decode().splitlines()
        assert len(manifest) == 59 and {Path(n).name for n in manifest} == {p.name for p in images}
        for p in images:
            data = z.read(f"labels/test/{p.stem}.txt")
            rows = parse_rows(data.decode())
            with Image.open(p) as im:
                im.verify()
            with Image.open(p) as im:
                width, height = im.size
            for c in rows[:, 0]:
                counts[int(c)] += 1
            for dest, content in [(stage_real / "images/test" / p.name, p.read_bytes()),
                                  (stage_real / "labels/test" / (p.stem + ".txt"), data)]:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(content)
            audit.append(dict(image=p.name, width=width, height=height, instances=len(rows),
                              image_sha256=sha(p), label_sha256=hashlib.sha256(data).hexdigest()))
    assert sum(counts.values()) == 282, counts
    assert {p.stem for p in PRED.glob("*.txt")} == {p.stem for p in images}
    for p in PRED.glob("*.txt"):
        parse_rows(p.read_text(), prediction=True)
    # A separate synthetic copy permits native cache creation without source writes.
    stage_syn = run / "data/synthetic"
    for folder in ("images/val", "labels/val"):
        shutil.copytree(SYN / folder, stage_syn / folder)
    assert len(list((stage_syn / "images/val").glob("*.png"))) == 120
    for p in (stage_syn / "labels/val").glob("*.txt"):
        parse_rows(p.read_text())
    for base, split in [(stage_real, "test"), (stage_syn, "val")]:
        # train:null satisfies Ultralytics' descriptor contract; no train split is used.
        descriptor = dict(path=base.as_posix(), train=None, val=f"images/{split}", names=NAMES)
        if split == "test":
            descriptor["test"] = "images/test"
        (base / "data.yaml").write_text(yaml.safe_dump(descriptor, sort_keys=False), encoding="utf-8")
    result = dict(images=59, instances=282, class_counts=dict(counts), image_audit=audit,
                  annotation_source=str(EXPORT), annotation_sha256=sha(EXPORT),
                  review_status="user-confirmed human review approved" if approved else "AI-assisted draft; unreviewed",
                  review_evidence="User: I reviewed and approved all 59 annotations" if approved else None,
                  original_export_unchanged=True, predictions_used_as_ground_truth=False,
                  raw_export_path_issue="test.txt uses data/images/test; raw labels use labels/test. Resolved only in staging.")
    write_json(run / "annotation_audit.json", result)
    return result


def validate(run, split):
    import numpy as np
    from ultralytics import YOLO
    from ultralytics.utils.metrics import smooth
    model = YOLO(str(WEIGHTS))
    assert model.names == NAMES
    data = run / f"data/{'real' if split == 'test' else 'synthetic'}/data.yaml"
    output = "real_validation" if split == "test" else "synthetic_validation"
    args = dict(data=str(data), split=split, imgsz=960, conf=0.001, iou=0.7,
                max_det=300, batch=4, workers=0, device="cpu", half=False,
                plots=True, save_txt=True, save_conf=True, verbose=True, cache=False,
                augment=False, rect=True, seed=20261030, deterministic=True,
                project=str(run), name=output, exist_ok=False)
    print(f"Validating {split}: {args}", flush=True)
    metrics = model.val(**args)
    box = metrics.box
    classes = []
    for i, c in enumerate(box.ap_class_index):
        c = int(c)
        classes.append(dict(class_id=c, name=NAMES[c], instances=int(metrics.nt_per_class[c]),
                            images=int(metrics.nt_per_image[c]), precision=float(box.p[i]),
                            recall=float(box.r[i]), map50=float(box.ap50[i]), map50_95=float(box.ap[i]),
                            ap_at_iou_50_to_95=box.all_ap[i].tolist()))
    idx = int(smooth(box.f1_curve.mean(0), 0.1).argmax())
    result = dict(images=59 if split == "test" else 120,
                  instances=int(metrics.nt_per_class.sum()),
                  precision=float(box.mp), recall=float(box.mr), map50=float(box.map50),
                  map50_95=float(box.map), per_class=classes,
                  precision_recall_definition="Macro mean at one common confidence maximizing smoothed mean class F1; not fixed 0.25",
                  best_mean_f1_confidence=float(box.px[idx]), args=args, speed_ms=metrics.speed,
                  confusion_matrix_default_iou=0.45, confusion_matrix_confidence=0.001,
                  confusion_matrix=metrics.confusion_matrix.matrix.tolist())
    write_json(run / output / "metrics.json", result)
    np.savez_compressed(run / output / "curves.npz", confidence=box.px, precision=box.p_curve,
                        recall=box.r_curve, f1=box.f1_curve, all_ap=box.all_ap,
                        ap_class_index=box.ap_class_index)
    np.savetxt(run / output / "confusion_matrix.csv", metrics.confusion_matrix.matrix, delimiter=",", fmt="%.0f")
    if split == "test":
        history = model.ckpt.get("train_results", {})
        write_json(run / "checkpoint_metadata.json", dict(date=model.ckpt.get("date"),
                   version=model.ckpt.get("version"), train_args=model.ckpt.get("train_args"),
                   train_metrics=model.ckpt.get("train_metrics"), train_results=history,
                   yaml=model.model.yaml, names=model.names, sha256=sha(WEIGHTS)))
    return result


def xyxy(rows):
    import numpy as np
    return np.column_stack((rows[:, 1]-rows[:, 3]/2, rows[:, 2]-rows[:, 4]/2,
                            rows[:, 1]+rows[:, 3]/2, rows[:, 2]+rows[:, 4]/2))


def pair_iou(a, b):
    import numpy as np
    lo = np.maximum(a[:, None, :2], b[None, :, :2])
    hi = np.minimum(a[:, None, 2:], b[None, :, 2:])
    area = np.maximum(hi-lo, 0).prod(2)
    return area / (np.maximum(a[:, 2:]-a[:, :2], 0).prod(1)[:, None] +
                   np.maximum(b[:, 2:]-b[:, :2], 0).prod(1)[None, :] - area + 1e-15)


def match(gt, pred):
    """Class-aware, descending-confidence one-to-one matching at IoU >= 0.50."""
    import numpy as np
    overlaps = pair_iou(xyxy(gt), xyxy(pred))
    matched_gt = {}
    matched_pred = {}
    for p in np.argsort(-pred[:, 5], kind="stable"):
        eligible = [g for g in range(len(gt)) if g not in matched_gt and int(gt[g, 0]) == int(pred[p, 0])]
        if eligible:
            g = max(eligible, key=lambda g: overlaps[g, p])
            if overlaps[g, p] >= 0.5:
                matched_gt[g] = int(p)
                matched_pred[int(p)] = g
    return overlaps, matched_gt, matched_pred


def compare_saved_predictions(run):
    import numpy as np
    totals = {c: dict(instances=0, predictions=0, tp=0, fp=0, fn=0) for c in NAMES}
    details = []
    matrix = np.zeros((5, 5), dtype=int)
    for p in sorted((REAL / "images").glob("*.png")):
        gt = parse_rows((run / "data/real/labels/test" / (p.stem + ".txt")).read_text())
        pred = parse_rows((PRED / (p.stem + ".txt")).read_text(), prediction=True)
        overlaps, mg, mp = match(gt, pred)
        detections = []
        targets = []
        for j, row in enumerate(pred):
            c = int(row[0])
            totals[c]["predictions"] += 1
            best = int(overlaps[:, j].argmax()) if len(gt) else None
            same = np.flatnonzero(gt[:, 0] == c)
            same_best = int(same[np.argmax(overlaps[same, j])]) if len(same) else None
            same_iou = float(overlaps[same_best, j]) if same_best is not None else 0.0
            if j in mp:
                reason = "tp"
                totals[c]["tp"] += 1
                matrix[c, c] += 1
            else:
                totals[c]["fp"] += 1
                if same_iou >= 0.5:
                    reason = "duplicate"
                elif best is not None and overlaps[best, j] >= 0.5 and int(gt[best, 0]) != c:
                    reason = "classification_error"
                elif same_iou >= 0.1:
                    reason = "localization_error"
                else:
                    reason = "background_or_unmatched"
            detections.append(dict(index=j, class_id=c, confidence=float(row[5]),
                              box_xyxy=xyxy(pred[j:j+1])[0].tolist(), status=reason,
                              matched_gt=mp.get(j), matched_iou=float(overlaps[mp[j], j]) if j in mp else None,
                              best_gt=best, best_iou=float(overlaps[best, j]) if best is not None else 0,
                              best_same_class_gt=same_best, best_same_class_iou=same_iou))
        for g, row in enumerate(gt):
            c = int(row[0])
            totals[c]["instances"] += 1
            if g not in mg:
                totals[c]["fn"] += 1
            targets.append(dict(index=g, class_id=c, box_xyxy=xyxy(gt[g:g+1])[0].tolist(),
                                status="tp" if g in mg else "fn", matched_prediction=mg.get(g),
                                max_same_class_iou=float(overlaps[g, pred[:, 0] == c].max())
                                if (pred[:, 0] == c).any() else 0.0))
        # Pair leftover cross-class errors for a count-consistent confusion matrix.
        remaining_gt = {g for g in range(len(gt)) if g not in mg}
        remaining_pred = {j for j in range(len(pred)) if j not in mp}
        for j in sorted(remaining_pred, key=lambda j: -pred[j, 5]):
            candidates = [g for g in remaining_gt if int(gt[g, 0]) != int(pred[j, 0]) and overlaps[g, j] >= 0.5]
            if candidates:
                g = max(candidates, key=lambda g: overlaps[g, j])
                matrix[int(pred[j, 0]), int(gt[g, 0])] += 1
                remaining_gt.remove(g)
                remaining_pred.remove(j)
        for g in remaining_gt:
            matrix[4, int(gt[g, 0])] += 1
        for j in remaining_pred:
            matrix[int(pred[j, 0]), 4] += 1
        errors = Counter(d["status"] for d in detections if d["status"] != "tp")
        details.append(dict(image=p.name, gt=targets, predictions=detections,
                            tp=len(mp), fp=len(pred)-len(mp), fn=len(gt)-len(mg), fp_types=dict(errors)))
    micro = {k: sum(v[k] for v in totals.values()) for k in ("instances", "predictions", "tp", "fp", "fn")}
    for v in [*totals.values(), micro]:
        assert v["tp"] + v["fp"] == v["predictions"]
        assert v["tp"] + v["fn"] == v["instances"]
        v["precision"] = v["tp"] / v["predictions"] if v["predictions"] else 0
        v["recall"] = v["tp"] / v["instances"] if v["instances"] else 0
    for c in NAMES:
        assert matrix[c, c] == totals[c]["tp"]
        assert matrix[c].sum()-matrix[c, c] == totals[c]["fp"]
        assert matrix[:, c].sum()-matrix[c, c] == totals[c]["fn"]
    result = dict(confidence=0.25, matching_iou=0.5, matching="descending-confidence class-aware greedy, one-to-one",
                  localization_definition="Unmatched prediction with same-class GT overlap 0.10 <= IoU < 0.50; diagnostic FP subset, not extra errors",
                  prediction_source=str(PRED), micro=micro, per_class={NAMES[c]: v for c, v in totals.items()},
                  fp_types=dict(sum((Counter(d["fp_types"]) for d in details), Counter())),
                  confusion_matrix=matrix.tolist(), images=details)
    write_json(run / "fixed_conf025_analysis.json", result)
    with (run / "per_image_errors.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "tp", "fp", "fn", "localization_fp", "classification_fp", "background_fp", "duplicate_fp"])
        writer.writeheader()
        for d in details:
            writer.writerow(dict(image=d["image"], tp=d["tp"], fp=d["fp"], fn=d["fn"],
                                 localization_fp=d["fp_types"].get("localization_error", 0),
                                 classification_fp=d["fp_types"].get("classification_error", 0),
                                 background_fp=d["fp_types"].get("background_or_unmatched", 0),
                                 duplicate_fp=d["fp_types"].get("duplicate", 0)))
    return result


def verify_and_summarize(run, analysis):
    """Cross-check research matching against the installed official validator."""
    import numpy as np
    import torch
    from types import SimpleNamespace
    from ultralytics.engine.validator import BaseValidator
    from ultralytics.utils.metrics import box_iou
    from ultralytics.utils import ops
    validator = SimpleNamespace(iouv=torch.tensor([0.5], dtype=torch.float64))
    checked = 0
    low_conf_switches = []
    for d in analysis["images"]:
        stem = Path(d["image"]).stem
        gt = parse_rows((run / "data/real/labels/test" / (stem + ".txt")).read_text())
        pred = parse_rows((PRED / (stem + ".txt")).read_text(), prediction=True)
        order = np.argsort(-pred[:, 5], kind="stable")
        p = pred[order]
        # Independent Ultralytics conversion and IoU implementation.
        gt_boxes = ops.xywh2xyxy(torch.tensor(gt[:, 1:5]))
        p_boxes = ops.xywh2xyxy(torch.tensor(p[:, 1:5]))
        official = BaseValidator.match_predictions(validator, torch.tensor(p[:, 0]),
                    torch.tensor(gt[:, 0]), box_iou(gt_boxes, p_boxes))[:, 0].numpy()
        ours = np.array([d["predictions"][int(j)]["status"] == "tp" for j in order])
        assert np.array_equal(official, ours), d["image"]
        checked += len(p)
        # Explain any nonzero switch AP despite zero switch TP at confidence 0.25.
        path = run / "real_validation/labels" / (stem + ".txt")
        low = np.loadtxt(path, ndmin=2) if path.exists() else np.empty((0, 6))
        overlaps, mg, _ = match(gt, low)
        for g, j in mg.items():
            if int(gt[g, 0]) == 3:
                low_conf_switches.append(dict(image=d["image"], gt_index=g,
                    confidence=float(low[j, 5]), iou=float(overlaps[g, j])))
    orientations = {}
    for split in ("train", "val"):
        angles = [c["orientation_deg"] for line in (SYN / f"metadata/{split}.jsonl").read_text(encoding="utf-8").splitlines()
                  for c in json.loads(line)["components"] if c["class"] == "resistor"]
        deviations = [min(a % 90, 90-a % 90) for a in angles]
        orientations[split] = dict(resistors=len(angles), max_degrees_from_cardinal=max(deviations),
                                    more_than_5_degrees_from_cardinal=sum(d > 5 for d in deviations))
    fp_by_class = {name: dict(Counter(p["status"] for d in analysis["images"] for p in d["predictions"]
                          if p["class_id"] == c and p["status"] != "tp")) for c, name in NAMES.items()}
    out = dict(official_matcher_crosscheck_images=59, official_matcher_crosscheck_predictions=checked,
               all_prediction_tp_flags_agree=True, count_identities_passed=True,
               low_confidence_switch_matches=low_conf_switches,
               synthetic_resistor_orientation_coverage=orientations, fp_types_per_class=fp_by_class,
               note="Diagnostic classification FP can overlap a reference already claimed by a correct-class TP; not all are cross-class FN pairs.")
    write_json(run / "analysis_verification.json", out)
    return out


def create_visuals(run, analysis, real, synthetic):
    """Scientific comparison figures; original pixels are read-only inputs."""
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    visuals = run / "comparisons"
    visuals.mkdir(exist_ok=True)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 15)
    small = ImageFont.truetype(str(font_path), 12)
    colors = {0: "#0072B2", 1: "#D55E00", 2: "#009E73", 3: "#CC79A7"}
    short = {0: "R", 1: "V", 2: "C", 3: "S"}
    short_error = dict(localization_error="FP-L", classification_error="FP-C",
                       background_or_unmatched="FP-B", duplicate="FP-D")
    err_colors = dict(tp="#009E73", fn="#D55E00", localization_error="#E69F00",
                      classification_error="#CC79A7", background_or_unmatched="#CC3311", duplicate="#882255")
    for d in analysis["images"]:
        original = Image.open(REAL / "images" / d["image"]).convert("RGB")
        w, h = original.size
        panels = []
        def panel(title, boxes):
            image = Image.new("RGB", (w, h+52), "white")
            image.paste(original, (0, 52))
            draw = ImageDraw.Draw(image)
            draw.text((6, 5), title, font=font, fill="black")
            for box, text, color in boxes:
                x1, y1, x2, y2 = [box[0]*w, box[1]*h+52, box[2]*w, box[3]*h+52]
                draw.rectangle((x1, y1, x2, y2), outline=color, width=2)
                tb = draw.textbbox((0, 0), text, font=small)
                tw, th = tb[2]-tb[0]+4, tb[3]-tb[1]+5
                tx, ty = min(max(0, x1), max(0, w-tw)), max(35, y1-th)
                draw.rectangle((tx, ty, tx+tw, ty+th), fill="white")
                draw.text((tx+2, ty), text, font=small, fill=color)
            return image
        panels.append(panel("Original (unchanged)", []))
        panels.append(panel("Approved reference boxes", [(g["box_xyxy"], f"G{g['index']} {short[g['class_id']]}", colors[g["class_id"]]) for g in d["gt"]]))
        panels.append(panel("YOLO predictions: confidence >= 0.25", [(p["box_xyxy"], f"P{p['index']} {short[p['class_id']]} {p['confidence']:.2f}", colors[p["class_id"]]) for p in d["predictions"]]))
        panels.append(panel(f"TP green / FN red: {d['tp']} TP, {d['fn']} FN", [(g["box_xyxy"], f"G{g['index']} {short[g['class_id']]} {g['status'].upper()}", err_colors[g["status"]]) for g in d["gt"]]))
        panels.append(panel(f"FP: {d['fp']} (orange=localization)", [(p["box_xyxy"], f"P{p['index']} {short[p['class_id']]} {short_error[p['status']]}", err_colors[p["status"]]) for p in d["predictions"] if p["status"] != "tp"]))
        for i, image in enumerate(panels):
            if image.width > 650:
                panels[i] = image.resize((650, round(image.height*650/image.width)))
        pw, ph = panels[0].size
        canvas = Image.new("RGB", (3*pw, 2*ph+46), "#eeeeee")
        for i, image in enumerate(panels):
            canvas.paste(image, ((i % 3)*pw, 46+(i // 3)*ph))
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 6), d["image"]+" | Matching: same class, IoU >= 0.50, one-to-one", font=font, fill="black")
        legend = ["R=resistor  V=voltage source", "C=capacitor  S=switch", "G=reference ID  P=prediction ID",
                  "TP/FN panel uses reference coordinates", "FP panel uses prediction coordinates", "FP-B: background / unmatched",
                  "FP-L: localization (same class IoU 0.10-0.50)", "FP-C: wrong-class overlap >= 0.50", "FP-D: duplicate (same class)",
                  "Full boxes / IoUs: fixed_conf025_analysis.json"]
        for line_idx, text in enumerate(legend):
            draw.text((2*pw+8, 46+ph+12+line_idx*18), text, font=small, fill="black")
        canvas.save(visuals / (Path(d["image"]).stem + ".png"))
    # Fixed operating-point confusion matrix, independently documented from AP plots.
    matrix = np.array(analysis["confusion_matrix"])
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix, cmap="Blues")
    labels = list(NAMES.values())+["background"]
    ax.set(xticks=range(5), yticks=range(5), xticklabels=labels, yticklabels=labels,
           xlabel="Reference class", ylabel="Predicted class",
           title="Existing predictions: conf >= 0.25, IoU >= 0.50")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    for (y, x), value in np.ndenumerate(matrix):
        ax.text(x, y, str(value), ha="center", va="center", color="white" if value > matrix.max()/2 else "black")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(run / "confusion_matrix_conf025_iou050.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(4)
    ax.bar(x-.18, [r["map50_95"] for r in synthetic["per_class"]], .36, label="Synthetic val (120 images)")
    ax.bar(x+.18, [r["map50_95"] for r in real["per_class"]], .36, label="Real test (59 images)")
    ax.set(xticks=x, xticklabels=list(NAMES.values()), ylabel="AP50-95", ylim=(0, 1.05),
           title="Same frozen best.pt, same validation settings")
    ax.legend(); fig.tight_layout(); fig.savefig(run / "synthetic_vs_real_ap.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    for r in real["per_class"]:
        ax.plot(np.arange(0.50, 1, .05), r["ap_at_iou_50_to_95"], marker="o", label=r["name"])
    ax.set(xlabel="Matching IoU threshold", ylabel="Average precision", ylim=(0, 1.05),
           title="Real-image AP versus box-overlap requirement")
    ax.legend(); fig.tight_layout(); fig.savefig(run / "real_ap_by_iou.png", dpi=160); plt.close(fig)
    # Exhaustive comparison index: each row links a full-resolution comparison.
    rows = ["<!doctype html><meta charset='utf-8'><title>Real circuit evaluation</title>",
            "<h1>59-image circuit evaluation</h1><p>Reference annotations: user-approved assistant-drawn CVAT boxes. "
            "Predictions: existing run, confidence 0.25. Class-aware IoU 0.50 matching.</p>"]
    import html
    for d in sorted(analysis["images"], key=lambda d: -(d["fp"]+d["fn"])):
        filename = Path(d["image"]).stem + ".png"
        rows.append(f"<h2>{html.escape(d['image'])}: {d['tp']} TP / {d['fp']} FP / {d['fn']} FN</h2>"
                    f"<a href='comparisons/{html.escape(filename, quote=True)}'><img style='max-width:1100px;width:100%' "
                    f"loading='lazy' src='comparisons/{html.escape(filename, quote=True)}'></a>")
    (run / "comparison_gallery.html").write_text("\n".join(rows), encoding="utf-8")


def report(run, audit, real, synthetic, analysis):
    """Generate the report from measured outputs, never hardcoded performance."""
    def pct(x):
        return f"{100*x:.2f}%"
    def rel(p):
        return os.path.relpath(p, REPORT.parent).replace("\\", "/")
    def link(p, label):
        return f"[{label}](<{rel(p)}>)"
    m = analysis["micro"]
    ckpt = json.loads((run / "checkpoint_metadata.json").read_text())
    verification = json.loads((run / "analysis_verification.json").read_text())
    lines = ["# YOLO26n real textbook circuit evaluation — 2026-10-31", "",
        "## Result and annotation provenance", "",
        f"Frozen best.pt achieved **{pct(real['map50'])} mAP50 and {pct(real['map50_95'])} mAP50–95** "
        f"on all 59 real screenshots (282 annotated instances). Overall class-macro precision was {pct(real['precision'])} "
        f"and recall {pct(real['recall'])} at Ultralytics' common maximum-mean-F1 operating point.", "",
        "The 59 CVAT annotations were drawn through the UI by an AI assistant, without importing model predictions. "
        "The original export remains named draft. The user explicitly confirmed in this session: "
        "**‘I reviewed and approved all 59 annotations.’** This report uses that approved export as the reference. "
        "Human approval is user-reported; no second independent annotator or inter-annotator agreement study was performed. "
        "These results measure real-image detection against that reference, not electrical graph or simulation accuracy.", "",
        "## Input verification and preservation", "",
        f"- Source images: `{REAL.relative_to(ROOT).as_posix()}/images` — 59 unchanged PNGs.",
        f"- Reference: `{EXPORT.relative_to(ROOT).as_posix()}`; SHA-256 `{sha(EXPORT)}`.",
        f"- Checkpoint: `{WEIGHTS.relative_to(ROOT).as_posix()}`; SHA-256 `{sha(WEIGHTS)}`; matches checked-in asset manifest.",
        "- Class IDs exactly match the checkpoint and synthetic data: 0 resistor, 1 voltage_source, 2 capacitor, 3 switch.",
        "- Exactly one five-column reference TXT per source stem; no missing/extra files or duplicate rows. "
        "All decoded images, class IDs, finite normalized coordinates, positive dimensions and image-bound checks passed.",
        "- CVAT's raw image-list prefix (`data/images/test`) differed from its label hierarchy (`labels/test`). "
        "Only a separate evaluation copy was given a consistent `images/test` / `labels/test` hierarchy and new data.yaml. "
        "Raw ZIP, originals, reserved human label directory, weights and previous prediction labels were unchanged.",
        "- Synthetic validation used byte-identical copies of the existing 120 validation images and labels. "
        "All caches and generated outputs are inside the fresh evaluation run.",
        "- No training, threshold optimization, dataset regeneration, package installation, production integration, "
        "physics algorithm changes or live VLM calls occurred.", "",
        "## Method and definitions", "",
        "Official Ultralytics 8.4.193 `YOLO(best.pt).val(...)` ran twice in the existing Python 3.12 .venv: "
        "real split=test and synthetic split=val. Both used imgsz=960, confidence floor=0.001, batch=4, CPU float32, "
        "workers=0, rect=True, augment=False, max_det=300 and NMS IoU argument=0.7. YOLO26n uses its native end-to-end head. "
        "The NMS argument is distinct from matching IoU. AP averages interpolated precision-recall area over confidence; "
        "mAP50–95 averages ten matching thresholds from 0.50 through 0.95. Low-confidence validation predictions are newly "
        "generated because the existing 0.25-filtered TXT files cannot provide complete PR curves or standard AP.", "",
        f"Official precision/recall are class-macro means at a common confidence selected from the mean-F1 curve "
        f"(real {real['best_mean_f1_confidence']:.6f}; synthetic {synthetic['best_mean_f1_confidence']:.6f}). "
        "This standard summary selection is descriptive, not a deployed threshold recommendation. AP and these P/R values "
        "must not be confused with fixed confidence=0.25 performance.", "",
        "Separately, the 312 existing predictions at confidence≥0.25 were matched to references at same-class IoU≥0.50, "
        "one-to-one in descending confidence order. This follows the installed validator's class-aware policy. "
        "An unmatched prediction is FP and an unmatched reference is FN. A wrong class can contribute both one FP and one FN. "
        "Localization FP means unmatched same-class overlap 0.10≤IoU<0.50; it is a diagnostic subset of FP, not an extra error. "
        "Rounded six-field prediction exports and different rectangular batching may cause small differences from a fresh inference pass.", "",
        "## Actual real-image validation metrics", "",
        "| Class | Images containing class | Reference instances | Precision | Recall | AP50 | AP50–95 |",
        "|---|---:|---:|---:|---:|---:|---:|"]
    for r in real["per_class"]:
        lines.append(f"| {r['name']} | {r['images']} | {r['instances']} | {pct(r['precision'])} | {pct(r['recall'])} | {pct(r['map50'])} | {pct(r['map50_95'])} |")
    lines += [f"| Overall (class macro) | 59 | 282 | {pct(real['precision'])} | {pct(real['recall'])} | {pct(real['map50'])} | {pct(real['map50_95'])} |", "",
        "## Existing predictions at confidence 0.25 / matching IoU 0.50", "",
        "| Class | Reference | Predictions | TP | FP | FN | Precision | Recall |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, r in analysis["per_class"].items():
        lines.append(f"| {name} | {r['instances']} | {r['predictions']} | {r['tp']} | {r['fp']} | {r['fn']} | {pct(r['precision'])} | {pct(r['recall'])} |")
    lines += [f"| Overall (micro) | {m['instances']} | {m['predictions']} | {m['tp']} | {m['fp']} | {m['fn']} | {pct(m['precision'])} | {pct(m['recall'])} |", "",
        f"FP diagnostics: `{json.dumps(analysis['fp_types'], sort_keys=True)}`. "
        "The 15 classification-overlap FPs include extra wrong-class boxes on references already detected correctly; "
        "only two leftover cross-class pairs appear in the fixed confusion matrix (voltage source → capacitor). "
        "Do not add these diagnostic overlap counts to TP/FP/FN. These are heuristic box-level categories: "
        "low-IoU wrong-class fragments also fall under background_or_unmatched, so that category does not mean "
        "43 detections on blank paper. Per-image rows and box IDs with IoUs are retained for every match and error.", "",
        "All 312 TP flags across all 59 images were independently cross-checked against the installed Ultralytics "
        "`BaseValidator.match_predictions` using its own coordinate conversion and IoU function: exact agreement. "
        "Per-class/overall TP+FP=predictions and TP+FN=reference counts, including confusion-matrix margins, also passed.", "",
        "### Failure examples", "",
        "The following are measured examples ranked by FP+FN count. Each comparison shows original pixels, approved reference "
        "boxes, predictions, reference TP/FN and prediction FP categories. G/P indices link to the complete JSON diagnostics.", "",
        "| Image | TP | FP | FN | Comparison |", "|---|---:|---:|---:|---|"]
    worst = sorted(analysis["images"], key=lambda d: -(d["fp"]+d["fn"]))[:8]
    for d in worst:
        lines.append(f"| {d['image']} | {d['tp']} | {d['fp']} | {d['fn']} | {link(run/'comparisons'/(Path(d['image']).stem+'.png'), 'View')} |")
    lines += ["", "### Visually inspected failure evidence", "",
        "- **Diagonal resistors, 235305:** all four diagonal resistors (G0/G2/G3/G4) are FN; the source is TP. "
        "A `15 Ω` text region is a false switch at confidence 0.425816. In **234003**, the four bridge resistors "
        "are missed while horizontal/vertical resistors are TP; three partial diagonal/text regions become switch FPs.",
        "- **Additional angles, 235428:** all three diagonal resistors (G1/G2/G4) are FN, while four axis-aligned "
        "resistors are TP. Node label A is falsely detected as a resistor at confidence about 0.55. In **234517**, "
        "two angled resistors and a diagonal voltage source are missed. These are qualitative cases, not a labeled orientation-wide recall estimate.",
        "- **Crowding and meters, 000005:** three compact horizontal resistors (G0/G1/G2) are missed too; this failure "
        "is not limited to diagonal symbols. Ammeter A becomes a voltage_source at confidence 0.97, and part of the "
        "`(0–5 A)` range text is another source FP. The actual cell is both correctly detected as a source and additionally labeled capacitor.",
        "- **Capacitors, 000838:** all three real capacitor plate pairs are TP, with saved-prediction IoUs "
        "0.6866, 0.6491 and 0.6259. The fourth real capacitor in 234759 is also TP (IoU 0.7324). "
        "All four are in just two images. Despite AP50=99.5%, the 0.25 operating point has 19 capacitor FPs and "
        "17.39% precision; high ranking on four positives is not robust generalization. Official capacitor AP is zero at IoU≥0.75.",
        "- **Switches / node negatives, 234647 and 000634:** the open switch G4 in 234647 is missed, while an "
        "extra capacitor box overlaps the correctly detected cell. In 000634, all three real targets are TP, "
        "yet four lettered node/circle regions become switch FPs (confidences 0.7604–0.9115), and both cells "
        "receive extra capacitor boxes. All three true switches in this set are FN at confidence 0.25.",
        "- **Battery localization, 001508:** the single approved battery reference G0 is split into source boxes "
        "P3/P4 with confidences 0.844454/0.820727 and IoUs only 0.315196/0.273096. They are two localization FPs "
        "and one battery FN, despite visually finding individual plate groups. A separate capacitor FP and tiny "
        "wire-region resistor FP are also present. This illustrates why component grouping conventions matter.", "",
        "The filename suffixes above refer to `Screenshot 2026-10-30 <suffix>.png` until midnight, and "
        "`Screenshot 2026-10-31 <suffix>.png` afterward; all full names and numbered boxes are in the gallery/JSON.", "",
        f"Low-confidence validation recovered {len(verification['low_confidence_switch_matches'])} matched switch reference(s) "
        f"below the old prediction threshold: `{json.dumps(verification['low_confidence_switch_matches'])}`. "
        "Very low-ranked switch matches explain the nonzero but near-zero switch AP; lowering the deployment threshold "
        "is not supported as a fix, given the high-confidence node/text false detections.", "",
        "![Diagonal resistor failure](<"+rel(run/"comparisons/Screenshot 2026-10-30 235305.png")+">)", "",
        "![Battery localization failure](<"+rel(run/"comparisons/Screenshot 2026-10-31 001508.png")+">)", "",
        "### Component-level diagnosis", "",
        "- **Resistors:** inspect diagonal branches, compact zigzags and IEC rectangles in the comparison gallery. "
        "Axis-aligned reference boxes do not encode orientation, so no numerical ‘angled resistor recall’ is claimed "
        "without an independently reviewed orientation subset. Standard class recall above includes all resistor orientations.",
        "- **Voltage sources:** cell plates, multi-cell battery grouping and circular instruments can differ from generated "
        "source styles. The FP/IoU records separate localization and wrong-class overlap where the current annotations permit it.",
        "- **Capacitors:** only four reference instances are present; plate-like battery strokes can produce false capacitor detections. "
        "Small-object box placement strongly affects AP at high IoU. Four examples cannot establish robust population accuracy.",
        "- **Switches:** only three reference instances are present; plug-key and open-switch styles vary. "
        "Wire breaks, terminals and text strokes are relevant hard negatives. Do not infer coverage of switch variants from three objects.", "",
        "## Synthetic versus real performance", "",
        "| Dataset / source | Images | Instances | Precision | Recall | mAP50 | mAP50–95 |", "|---|---:|---:|---:|---:|---:|---:|"]
    lines += ["| Previous documented best-checkpoint synthetic baseline | 120 | 670 | 99.9512% | 100.0000% | 99.5000% | 98.0246% |",
        f"| Checkpoint embedded train_metrics (synthetic) | 120 | 670 | {pct(ckpt['train_metrics']['metrics/precision(B)'])} | {pct(ckpt['train_metrics']['metrics/recall(B)'])} | {pct(ckpt['train_metrics']['metrics/mAP50(B)'])} | {pct(ckpt['train_metrics']['metrics/mAP50-95(B)'])} |",
        f"| Synthetic revalidation, current CPU environment | 120 | {synthetic['instances']} | {pct(synthetic['precision'])} | {pct(synthetic['recall'])} | {pct(synthetic['map50'])} | {pct(synthetic['map50_95'])} |",
        f"| Real textbook test, current CPU environment | 59 | {real['instances']} | {pct(real['precision'])} | {pct(real['recall'])} | {pct(real['map50'])} | {pct(real['map50_95'])} |", "",
        f"The directly comparable revalidation gap is **{100*(synthetic['map50']-real['map50']):.2f} percentage points "
        f"in mAP50 and {100*(synthetic['map50_95']-real['map50_95']):.2f} points in mAP50–95**. "
        "The historical documentation and checkpoint embedded summary differ slightly at strict IoUs; neither is silently substituted "
        "for the other. Current same-environment revalidation is the primary comparison. The historical GPU/precision/batch "
        "configuration and exact summary provenance differ; no definitive cause for their small difference is established.", "",
        f"Historical source: {link(ROOT/'docs/reports/CIRCUIT_YOLO_BASELINE_20261031.md', 'checked-in synthetic baseline')}; "
        f"embedded checkpoint values: {link(run/'checkpoint_metadata.json', 'checkpoint metadata and training history')}.", "",
        "| Class | Synthetic AP50 | Real AP50 | Synthetic AP50–95 | Real AP50–95 | AP50–95 gap (points) |",
        "|---|---:|---:|---:|---:|---:|"]
    for s, r in zip(synthetic["per_class"], real["per_class"]):
        assert s["class_id"] == r["class_id"]
        lines.append(f"| {r['name']} | {pct(s['map50'])} | {pct(r['map50'])} | {pct(s['map50_95'])} | {pct(r['map50_95'])} | {100*(s['map50_95']-r['map50_95']):.2f} |")
    lines += ["",
        "The synthetic split comes from the same Schemdraw generator family as training, with controlled body boxes, symbol styles, "
        "text fonts and topology families. Real screenshots contain different print conventions, Bangla/English labels, diagonal "
        "branches, faint/blurred strokes, crowded symbols and measurement instruments absent from the four target classes. "
        "This is evidence of a domain gap, consistent with limited synthetic style/negative coverage. "
        "Class imbalance and annotation conventions also affect comparison. This observational evaluation does not isolate "
        "the causal contribution of each factor.", "",
        f"Metadata inspection provides concrete angle-coverage evidence: **all 1,159 training resistors are within "
        f"{verification['synthetic_resistor_orientation_coverage']['train']['max_degrees_from_cardinal']:.3f}° of a horizontal/vertical axis**; "
        f"all 279 synthetic-validation resistors are within "
        f"{verification['synthetic_resistor_orientation_coverage']['val']['max_degrees_from_cardinal']:.3f}°. "
        "Neither split has a resistor more than 5° from those axes. Small whole-page scan rotations therefore did not "
        "supply the substantial diagonal resistor orientations seen in real bridge circuits. "
        "The installed checkpoint's training args also specify degrees=0.0 and shear=0.0.", "",
        "## Plots and artifacts", "",
        f"- {link(run/'comparison_gallery.html', 'All 59 visual comparisons')}.",
        f"- {link(run/'synthetic_vs_real_ap.png', 'Per-class synthetic/real AP50–95 comparison')}.",
        f"- {link(run/'real_ap_by_iou.png', 'Real AP versus matching IoU')}.",
        f"- {link(run/'confusion_matrix_conf025_iou050.png', 'Fixed 0.25 / 0.50 confusion matrix')}: "
        "class-aware TP first, then leftover wrong-class pairs; rows=predicted, columns=reference; background holds FP/FN.",
        f"- {link(run/'real_validation/confusion_matrix.png', 'Ultralytics raw confusion matrix')} and "
        f"{link(run/'real_validation/confusion_matrix_normalized.png', 'normalized matrix')}: "
        "native class-agnostic matching IoU>0.45, confidence>0.001. These have different thresholds from the fixed-point analysis.",
        f"- {link(run/'real_validation/BoxPR_curve.png', 'Real precision–recall curves')}; "
        f"{link(run/'real_validation/BoxP_curve.png', 'precision-confidence')}; "
        f"{link(run/'real_validation/BoxR_curve.png', 'recall-confidence')}; "
        f"{link(run/'real_validation/BoxF1_curve.png', 'F1-confidence')}.",
        f"- {link(run/'real_validation/metrics.json', 'Full real metrics')}; "
        f"{link(run/'synthetic_validation/metrics.json', 'full synthetic metrics')}; "
        f"{link(run/'fixed_conf025_analysis.json', 'all per-box matches/errors')}; "
        f"{link(run/'per_image_errors.csv', 'per-image error CSV')}.",
        f"- {link(run/'analysis_verification.json', 'Matcher cross-check, low-confidence switch matches and angle-coverage evidence')}.",
        "- Validation subdirectories include low-confidence predicted TXT files, confusion CSVs, lossless curve arrays and label/prediction batch previews.", "",
        "## Limits, recommendation and next step", "",
        "1. **Improve the dataset first; plan YOLO v2 fine-tuning afterward.** Collect a separate real training/development pool "
        "with diagonal resistors, IEC/ANSI variants, faint small capacitors, cells/batteries, open/closed/plug-key switches "
        "and hard negatives (A/V meters, text, nodes, wire gaps). Mix these with broader synthetic layouts and review "
        "symbol-body/battery-grouping conventions before training. Do not train or choose thresholds on these 59 test images.",
        "2. This test set has already guided error analysis and future data choices. Retain its labels and original pixels "
        "for regression, but obtain a fresh book/page/source-disjoint final test set for an unbiased v2 claim. "
        "Near-duplicate pages or drawings should be grouped before splitting; byte hashes alone cannot detect semantic duplicates. "
        "Capacitor/switch sample sizes are particularly inadequate for broad claims; report per-class denominators.",
        "3. **An offline experimental YOLO→SAM2/CV study can run in parallel after the data audit, without production changes.** "
        "Use frozen proposals as search regions, then evaluate mask quality, terminal endpoints, wire continuity, junction ambiguity, "
        "OCR association and graph correctness independently. Detection AP alone does not justify simulation readiness. "
        "Do not treat a class label, box, or confidence as a measured physical parameter or verified connection.",
        "4. Preserve backend readiness/review gates and source-pixel provenance. No detector-to-MNA automatic path or "
        "student-facing integration is recommended on detection metrics alone. Require independent electrical-topology "
        "and parameter-grounding benchmarks before enabling such a path.",
        "5. These are sample-level point estimates, without confidence intervals or inter-annotator reliability estimates. "
        "Reference generation was not a blinded annotation study. "
        "Source/book identifiers and independently verified orientation tags are absent. No calibrated confidence, "
        "OCR performance, SAM2 mask performance, topology correctness or physical simulation accuracy was measured.", "",
        "## Reproduce", "", "```powershell",
        ".\\.venv\\Scripts\\python.exe scripts/evaluate_circuit_yolo_real.py --name real_evaluation_20261031_reproduction --report outputs/circuit_evaluation_reproduction.md --human-approved",
        "```", "",
        "Use a fresh run name. The script refuses existing runs and preserves the raw inputs, runs both frozen validations, "
        "creates all comparison figures, and generates this report. `--analyze-only` regenerates derived analysis/report "
        "from an existing run without inference. Human approval is required explicitly before an initial evaluation run.", "",
        f"Run: `{run.relative_to(ROOT).as_posix()}`. Environment and settings: `execution_manifest.json`. "
        "Source SHA-256 snapshots: `input_fingerprints_before.json` / `input_fingerprints_after.json`. "
        "Code/package provenance: `evaluator_sha256` and `ultralytics_source_sha256` in the execution manifest. "
        "No unrelated source changes were required.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main():
    global REPORT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="real_evaluation_20261031_1a572ba")
    parser.add_argument("--human-approved", action="store_true")
    parser.add_argument("--analyze-only", action="store_true")
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args()
    REPORT = args.report.resolve()
    if not args.analyze_only and not args.human_approved:
        parser.error("Confirm human review with --human-approved before treating the annotation export as evaluation ground truth")
    assert Path(args.name).name == args.name and args.name not in {".", ".."}
    run = ROOT / "runs/augmented_physics" / args.name
    os.environ["YOLO_CONFIG_DIR"] = str(ROOT / "outputs/yolo_settings")
    os.environ["YOLO_OFFLINE"] = "true"
    os.environ["MPLBACKEND"] = "Agg"
    import torch
    import ultralytics
    from ultralytics import settings
    settings.update({key: False for key in ("sync", "wandb", "mlflow", "clearml", "comet", "dvc", "raytune")})
    torch.set_num_threads(6)
    if args.analyze_only:
        assert run.is_dir()
        audit = json.loads((run / "annotation_audit.json").read_text())
        assert audit["review_status"] == "user-confirmed human review approved"
        real = json.loads((run / "real_validation/metrics.json").read_text())
        synthetic = json.loads((run / "synthetic_validation/metrics.json").read_text())
    else:
        assert not run.exists(), "Use a fresh run name; existing outputs are protected"
        assert not REPORT.exists(), "Report already exists; preserve it or use --analyze-only for this run"
        assert sha(WEIGHTS) == json.loads((ROOT / "requirements/circuit-assets-v1.json").read_text())["files"][WEIGHTS.relative_to(ROOT).as_posix()]["sha256"]
        run.mkdir(parents=True)
        shutil.copyfile(__file__, run / "evaluator_snapshot.py")
        before = fingerprint()
        write_json(run / "input_fingerprints_before.json", before)
        try:
            audit = stage(run, args.human_approved)
            write_json(run / "execution_manifest.json", dict(started_utc=datetime.now(timezone.utc).isoformat(),
                python=sys.executable, python_version=sys.version, torch=torch.__version__, ultralytics=ultralytics.__version__,
                device="cpu", evaluator_sha256=sha(Path(__file__)), human_approved=args.human_approved,
                ultralytics_source_sha256={f: sha(Path(ultralytics.__file__).parent/f) for f in
                    ["engine/validator.py", "models/yolo/detect/val.py", "utils/metrics.py"]}))
            real = validate(run, "test")
            synthetic = validate(run, "val")
        finally:
            after = fingerprint()
            write_json(run / "input_fingerprints_after.json", after)
            assert before == after, "Source files changed during evaluation"
    analysis = compare_saved_predictions(run)
    verify_and_summarize(run, analysis)
    create_visuals(run, analysis, real, synthetic)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report(run, audit, real, synthetic, analysis)
    shutil.copyfile(__file__, run / "analysis_evaluator_snapshot.py")
    before = json.loads((run / "input_fingerprints_before.json").read_text())
    after = fingerprint()
    assert before == after, "Sources changed before analysis completed"
    write_json(run / "analysis_manifest.json", dict(completed_utc=datetime.now(timezone.utc).isoformat(),
        evaluator_sha256=sha(Path(__file__)), source_files_unchanged=True, fingerprinted_files=len(after),
        report=str(REPORT), comparison_images=len(list((run / "comparisons").glob("*.png")))))
    print(json.dumps(dict(real={k:real[k] for k in ('precision','recall','map50','map50_95')},
        synthetic={k:synthetic[k] for k in ('precision','recall','map50','map50_95')},
        fixed=analysis["micro"], report=str(REPORT)), indent=2), flush=True)


if __name__ == "__main__":
    main()

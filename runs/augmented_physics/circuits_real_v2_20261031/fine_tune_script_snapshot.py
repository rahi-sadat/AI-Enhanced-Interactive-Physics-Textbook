"""Fine-tune the frozen circuit detector with all 59 user-approved real images.

This explicitly repurposes the former real test set for training. A new real
test set is required for any subsequent generalization claim. Originals, raw
CVAT annotations, v1 weights and historical evaluation artifacts stay intact.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import shutil
import sys
import time
import traceback
import zipfile

from evaluate_circuit_yolo_real import ROOT, REAL, SYN, EXPORT, WEIGHTS, NAMES, parse_rows, sha, fingerprint, write_json


def prepare(run, seed):
    import yaml
    from PIL import Image
    audit = json.loads((ROOT / "runs/augmented_physics/real_evaluation_20261031_1a572ba/annotation_audit.json").read_text())
    assert audit["review_status"] == "user-confirmed human review approved"
    assert sha(EXPORT) == audit["annotation_sha256"]
    records, counts = [], {"real": Counter(), "synthetic": Counter(), "val_synthetic": Counter()}
    data = run / "data"
    def copy_pair(image, raw_label, split, prefix, domain):
        rows = parse_rows(raw_label.decode("utf-8"))
        with Image.open(image) as im:
            im.verify()
        stem = prefix + image.stem
        dest_image = data / "images" / split / (stem + image.suffix)
        dest_label = data / "labels" / split / (stem + ".txt")
        dest_image.parent.mkdir(parents=True, exist_ok=True)
        dest_label.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(image, dest_image)
        dest_label.write_bytes(raw_label)
        assert sha(dest_image) == sha(image)
        counts[domain].update(int(c) for c in rows[:, 0])
        records.append(dict(image=str(dest_image.relative_to(data)), source=str(image.relative_to(ROOT)),
                            source_sha256=sha(image), label_sha256=sha(dest_label), split=split,
                            domain=domain, instances=len(rows)))
    with zipfile.ZipFile(EXPORT) as z:
        assert z.testzip() is None and yaml.safe_load(z.read("data.yaml"))["names"] == NAMES
        images = sorted((REAL / "images").glob("*.png"))
        assert len(images) == 59
        assert {Path(n).stem for n in z.namelist() if n.startswith("labels/test/") and n.endswith(".txt")} == {p.stem for p in images}
        for image in images:
            copy_pair(image, z.read(f"labels/test/{image.stem}.txt"), "train", "real__", "real")
    # Existing synthetic training images only; never sample from synthetic val.
    groups = defaultdict(list)
    for line in (SYN / "metadata/train.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        assert row["split"] == "train"
        groups[row["topology"]].append(row)
    rng = random.Random(seed)
    assert len(groups) == 10
    for topology in sorted(groups):
        group = sorted(groups[topology], key=lambda r: r["image_filename"])
        rng.shuffle(group)
        for row in group[:12]:
            copy_pair(SYN / row["image_filename"], (SYN / row["label_filename"]).read_bytes(), "train", "syn__", "synthetic")
    for image in sorted((SYN / "images/val").glob("*.png")):
        copy_pair(image, (SYN / "labels/val" / (image.stem + ".txt")).read_bytes(), "val", "", "val_synthetic")
    training = [r for r in records if r["split"] == "train"]
    validation = [r for r in records if r["split"] == "val"]
    assert len(training) == 179 and len(validation) == 120
    assert sum(counts["real"].values()) == 282
    assert not ({r["source_sha256"] for r in training} & {r["source_sha256"] for r in validation})
    descriptor = dict(path=data.as_posix(), train="images/train", val="images/val", names=NAMES)
    (data / "data.yaml").write_text(yaml.safe_dump(descriptor, sort_keys=False), encoding="utf-8")
    manifest = dict(seed=seed, real_training_images=59, synthetic_training_images=120,
                    synthetic_validation_images=120, training_instances=sum(r["instances"] for r in training),
                    counts={domain: {NAMES[k]: v for k, v in c.items()} for domain, c in counts.items()},
                    annotation_review="User explicitly approved all 59 CVAT annotations in this session",
                    authorization="User requested training on these 59 real diagrams and will provide a new test set later",
                    real_data_role="training; no longer an independent test set for v2",
                    real_test_images=0, records=records)
    write_json(run / "data_manifest.json", manifest)
    return manifest


def metrics_json(metrics):
    rows = []
    for i, c in enumerate(metrics.box.ap_class_index):
        c = int(c)
        rows.append(dict(name=NAMES[c], instances=int(metrics.nt_per_class[c]), precision=float(metrics.box.p[i]),
                         recall=float(metrics.box.r[i]), map50=float(metrics.box.ap50[i]), map50_95=float(metrics.box.ap[i])))
    return dict(precision=float(metrics.box.mp), recall=float(metrics.box.mr), map50=float(metrics.box.map50),
                map50_95=float(metrics.box.map), per_class=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="circuits_real_v2_20261031")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20261031)
    args = parser.parse_args()
    assert Path(args.name).name == args.name and args.name not in {".", ".."}
    assert args.epochs > 0
    run = ROOT / "runs/augmented_physics" / args.name
    assert not run.exists(), "Existing runs are protected; use another name"
    os.environ["YOLO_CONFIG_DIR"] = str(ROOT / "outputs/yolo_settings")
    os.environ["YOLO_OFFLINE"] = "true"
    os.environ["MPLBACKEND"] = "Agg"
    os.environ["PYTHONUTF8"] = "1"
    run.mkdir(parents=True)
    shutil.copyfile(__file__, run / "fine_tune_script_snapshot.py")
    before = fingerprint()
    historical_report = ROOT / "docs/reports/CIRCUIT_YOLO_REAL_EVALUATION_20261031.md"
    historical_sha = sha(historical_report)
    write_json(run / "input_fingerprints_before.json", before)
    started = time.perf_counter()
    console = sys.stdout
    try:
        manifest = prepare(run, args.seed)
        # Staging a separate real scoring split avoids all writes to human inputs.
        score_data = run / "real_training_fit"
        with zipfile.ZipFile(EXPORT) as z:
            for image in sorted((REAL / "images").glob("*.png")):
                for folder in ["images/test", "labels/test"]:
                    (score_data / folder).mkdir(parents=True, exist_ok=True)
                shutil.copyfile(image, score_data / "images/test" / image.name)
                (score_data / "labels/test" / (image.stem + ".txt")).write_bytes(z.read(f"labels/test/{image.stem}.txt"))
        import yaml
        (score_data / "data.yaml").write_text(yaml.safe_dump(dict(path=score_data.as_posix(), train=None,
                val="images/test", test="images/test", names=NAMES), sort_keys=False), encoding="utf-8")
        import torch
        import ultralytics
        import psutil
        from ultralytics import YOLO, settings
        settings.update({k: False for k in ("sync", "wandb", "mlflow", "clearml", "comet", "dvc", "raytune")})
        torch.set_num_threads(4)
        train_args = dict(data=str(run / "data/data.yaml"), epochs=args.epochs, imgsz=960,
            batch=1, nbs=8, device="cpu", workers=0, optimizer="AdamW", lr0=0.0002,
            lrf=0.1, weight_decay=0.0005, warmup_epochs=2.0, patience=0,
            freeze=10, amp=False, cache=False, val=False, plots=True,
            mosaic=0.0, mixup=0.0, degrees=20.0, shear=0.0, translate=0.03, scale=0.15,
            fliplr=0.5, flipud=0.0, hsv_h=0.0, hsv_s=0.0, hsv_v=0.1,
            seed=args.seed, deterministic=True, resume=False, save=True, save_period=5,
            project=str(run.parent), name=run.name, exist_ok=True)
        write_json(run / "training_manifest.json", dict(started_utc=datetime.now(timezone.utc).isoformat(),
            python=sys.executable, torch=torch.__version__, ultralytics=ultralytics.__version__,
            starting_checkpoint=str(WEIGHTS), starting_checkpoint_sha256=sha(WEIGHTS),
            training_args=train_args, effective_nominal_batch=8, cuda_available=torch.cuda.is_available(),
            host_total_ram_bytes=psutil.virtual_memory().total,
            plan="30-epoch pilot by default; frozen first 10 backbone modules, train neck/head; all 59 real plus 120 synthetic rehearsal images",
            validation="Only final-epoch synthetic validation; no held-out real validation or early stopping/model selection on real test data"))
        model = YOLO(str(WEIGHTS))
        assert model.names == NAMES
        def epoch_done(trainer):
            if trainer.epoch >= trainer.epochs:
                return
            completed = trainer.epoch + 1
            seconds = time.perf_counter() - started
            progress = dict(status="training", epochs_completed=completed, epochs=args.epochs,
                elapsed_seconds=seconds, estimated_remaining_seconds=seconds/completed*(args.epochs-completed),
                losses={k: float(v) for k, v in trainer.label_loss_items(trainer.tloss).items()},
                available_ram_bytes=psutil.virtual_memory().available)
            write_json(run / "progress.json", progress)
            print(f"Epoch {completed}/{args.epochs}; elapsed {seconds/60:.1f} min; estimated remaining "
                  f"{progress['estimated_remaining_seconds']/60:.1f} min; loss {progress['losses']}", file=console, flush=True)
        model.add_callback("on_fit_epoch_end", epoch_done)
        write_json(run / "progress.json", dict(status="starting", epochs=args.epochs))
        with (run / "training.log").open("w", encoding="utf-8", buffering=1) as log:
            with redirect_stdout(log), redirect_stderr(log):
                model.train(**train_args)
                synthetic_metrics = metrics_json(model.metrics)
                # Last checkpoint is the fixed-schedule final model. Best is based only
                # on the final synthetic validation, not an independent real score.
                final = run / "weights/last.pt"
                assert final.is_file() and (run / "weights/best.pt").is_file()
                fitted = YOLO(str(final))
                fit = fitted.val(data=str(score_data / "data.yaml"), split="test", imgsz=960, conf=0.001,
                    device="cpu", batch=1, workers=0, plots=True, save_txt=True, save_conf=True,
                    project=str(run), name="seen_real_fit_validation", exist_ok=False)
                real_fit = metrics_json(fit)
                fitted.predict(source=str(REAL / "images"), imgsz=960, conf=0.25, device="cpu", batch=1,
                    save=True, save_txt=True, save_conf=True, project=str(run), name="seen_real_predictions", exist_ok=False)
        after = fingerprint()
        assert before == after and sha(historical_report) == historical_sha
        write_json(run / "input_fingerprints_after.json", after)
        summary = dict(status="complete", epochs=args.epochs, elapsed_seconds=time.perf_counter()-started,
                       weights_last=str(final), weights_best=str(run / "weights/best.pt"),
                       weights_last_sha256=sha(final), starting_checkpoint_unchanged=True, source_files_unchanged=True,
                       real_images_used_for_training=59, synthetic_rehearsal_images=120,
                       synthetic_validation=synthetic_metrics, seen_real_training_fit=real_fit,
                       independent_real_test_metrics=None,
                       warning="Scores on the 59 real diagrams are training fit, not unseen-image accuracy. Await a new independent real test set.")
        write_json(run / "training_report.json", summary)
        write_json(run / "progress.json", dict(status="complete", epochs_completed=args.epochs, elapsed_seconds=summary["elapsed_seconds"]))
        report = ["# YOLO v2 pilot fine-tuning — 2026-10-31", "",
            "The user authorized repurposing all 59 reviewed real diagrams for training and will supply a new test set later.",
            "The previous real evaluation report remains a historical pre-training baseline. These 59 images are no longer an independent v2 test set.", "",
            f"Completed {args.epochs} epochs from the existing synthetic v1 best.pt at 960 px, CPU, batch 1, nominal accumulated batch 8, AdamW lr0=0.0002.",
            "First 10 backbone modules were frozen; neck and detection head were fine-tuned. Training used all 59 real images / 282 boxes plus 120 existing synthetic training images, stratified 12 per topology.",
            "The original 120 synthetic validation images were excluded from training. Only final-epoch synthetic validation was used; no independent real test set is available.", "",
            "| Dataset | Precision | Recall | mAP50 | mAP50–95 |", "|---|---:|---:|---:|---:|"]
        for name, metrics in [("Synthetic validation", synthetic_metrics), ("Seen real images — training fit only", real_fit)]:
            report.append(f"| {name} | {metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['map50']:.4f} | {metrics['map50_95']:.4f} |")
        report += ["", "Use `weights/last.pt` as the fixed-schedule v2 candidate; `weights/best.pt` is the native final-synthetic-validation checkpoint, not a claim of best real generalization.",
            "Original images, CVAT ZIP, v1 model, synthetic source files, prediction labels and historical real evaluation report were preserved with SHA-256 checks.",
            "No production integration or environment replacement was performed. Independent performance must be measured on the user's forthcoming book/page-disjoint test set.", "",
            "Artifacts: `data_manifest.json`, `training_manifest.json`, `training.log`, `results.csv`, `progress.json`, `training_report.json`, `seen_real_fit_validation/`, `seen_real_predictions/`.", ""]
        (run / "TRAINING_REPORT.md").write_text("\n".join(report), encoding="utf-8")
        print(json.dumps(summary, indent=2), file=console, flush=True)
    except BaseException as exc:
        after = fingerprint()
        write_json(run / "input_fingerprints_after.json", after)
        write_json(run / "failure_report.json", dict(error=str(exc), traceback=traceback.format_exc(),
            elapsed_seconds=time.perf_counter()-started, sources_unchanged=before == after))
        write_json(run / "progress.json", dict(status="failed", error=str(exc)))
        raise


if __name__ == "__main__":
    main()

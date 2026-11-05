"""Train the synthetic-only circuit detector without writing into its dataset.

Uses the standard Ultralytics training API. The sole dataset adapter redirects
Ultralytics' label caches into the run directory; image/label processing is native.
Run with the repository .venv Python, not the machine's legacy system Python.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[1]
CLASSES = {0: "resistor", 1: "voltage_source", 2: "capacitor", 3: "switch"}


def fingerprint(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob("*")) if p.is_file()}


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT/"datasets/circuits_v1/synthetic_v1/data.yaml")
    parser.add_argument("--model", type=Path, default=ROOT/"checkpoints/yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--batch", type=int, choices=(8, 4), default=8)
    # Windows spawn loads a CUDA PyTorch copy in every worker. Avoid exhausting
    # the machine's paging-file commit limit; the GPU batch and image size stay fixed.
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20261030)
    parser.add_argument("--name", default="circuits_synthetic_v1")
    args = parser.parse_args(argv)
    dataset = args.data.resolve().parent
    project = ROOT/"runs/augmented_physics"
    run = project/args.name
    if run.exists():
        parser.error(f"Run already exists: {run}. Select a new --name; existing training is protected.")
    if not args.model.is_file():
        parser.error(f"Download the official pretrained checkpoint first: {args.model}")
    if not args.data.is_file():
        parser.error(f"Dataset YAML is missing: {args.data}")
    run.mkdir(parents=True)
    before = fingerprint(dataset)
    save_json(run/"dataset_fingerprint_before.json", before)
    started = time.perf_counter()
    started_utc = datetime.now(timezone.utc).isoformat()
    console = sys.stdout
    os.environ["YOLO_CONFIG_DIR"] = str(ROOT/"outputs/yolo_settings")
    os.environ["YOLO_OFFLINE"] = "true"
    os.environ["PYTHONUTF8"] = "1"
    os.environ["MPLBACKEND"] = "Agg"
    report = None
    try:
        with (run/"training.log").open("w", encoding="utf-8", buffering=1) as log:
            with redirect_stdout(log), redirect_stderr(log):
                import torch
                import ultralytics
                from ultralytics import YOLO, settings
                from ultralytics.data.dataset import YOLODataset

                if not torch.cuda.is_available():
                    raise RuntimeError("CUDA GPU is unavailable; refusing to silently train on CPU")
                settings.update({key: False for key in
                                 ("sync", "wandb", "mlflow", "clearml", "comet", "dvc", "raytune")})
                cache_loader = YOLODataset._load_or_scan_cache

                def local_cache(self, cache_path, cache_hash):
                    cache_path = Path(cache_path).resolve()
                    if cache_path.is_relative_to(dataset):
                        cache_path = run/"dataset_cache"/cache_path.relative_to(dataset)
                        cache_path.parent.mkdir(parents=True, exist_ok=True)
                    return cache_loader(self, cache_path, cache_hash)

                YOLODataset._load_or_scan_cache = local_cache
                model = YOLO(str(args.model.resolve()))
                initial_classes = len(model.names)
                batch_history = []

                def epoch_start(trainer):
                    if trainer.batch_size < 4:
                        raise RuntimeError("GPU needs a batch below 4; stopped to preserve the requested training settings")
                    if not batch_history or batch_history[-1] != trainer.batch_size:
                        batch_history.append(trainer.batch_size)
                    save_json(run/"progress.json", dict(status="training", epoch_started=trainer.epoch+1,
                              epochs=args.epochs, batch=trainer.batch_size, imgsz=trainer.args.imgsz,
                              elapsed_seconds=time.perf_counter()-started))

                def epoch_done(trainer):
                    # Ultralytics invokes this callback again for final best.pt
                    # evaluation after incrementing epoch past the training loop.
                    # That evaluation is reported below, not as epoch 101/100.
                    if trainer.epoch >= trainer.epochs:
                        return
                    metrics = {k: float(v) for k, v in trainer.metrics.items()}
                    progress = dict(status="training", epochs_completed=trainer.epoch+1,
                                    epochs=args.epochs, batch=trainer.batch_size,
                                    imgsz=trainer.args.imgsz, metrics=metrics,
                                    elapsed_seconds=time.perf_counter()-started)
                    save_json(run/"progress.json", progress)
                    print(f"Epoch {trainer.epoch+1}/{args.epochs}: batch={trainer.batch_size}, "
                          f"mAP50={metrics.get('metrics/mAP50(B)', 0):.4f}, "
                          f"mAP50-95={metrics.get('metrics/mAP50-95(B)', 0):.4f}, "
                          f"elapsed={progress['elapsed_seconds']/60:.1f} min", file=console, flush=True)

                model.add_callback("on_train_epoch_start", epoch_start)
                model.add_callback("on_fit_epoch_end", epoch_done)
                print(f"Training on {torch.cuda.get_device_name(0)}. Log: {run/'training.log'}", file=console, flush=True)
                model.train(data=str(args.data.resolve()), epochs=args.epochs, imgsz=args.imgsz,
                            batch=args.batch, device=0, project=str(project), name=args.name,
                            exist_ok=True, workers=args.workers, seed=args.seed, cache=False)
                metrics = model.metrics
                per_class = []
                for i, class_id in enumerate(metrics.box.ap_class_index):
                    class_id = int(class_id)
                    per_class.append(dict(class_id=class_id, name=CLASSES[class_id],
                        instances=int(metrics.nt_per_class[class_id]),
                        precision=float(metrics.box.p[i]), recall=float(metrics.box.r[i]),
                        map50=float(metrics.box.ap50[i]), map50_95=float(metrics.box.ap[i])))
                if model.names != CLASSES:
                    raise RuntimeError(f"Unexpected trained class mapping: {model.names}")
                with (run/"results.csv").open(encoding="utf-8") as source:
                    history = [{k.strip(): v for k, v in row.items()} for row in csv.DictReader(source)]
                epochs_completed = int(history[-1]["epoch"])
                if epochs_completed != args.epochs:
                    raise RuntimeError(f"Expected {args.epochs} epochs, completed {epochs_completed}")
                # The standard training API reloads best.pt before returning;
                # these metrics and example detections therefore use that model.
                val_images = sorted((dataset/"images/val").glob("*.png"))[:12]
                model.predict(source=[str(p) for p in val_images], imgsz=args.imgsz, device=0,
                              save=True, save_txt=True, save_conf=True,
                              project=str(run), name="validation_predictions", verbose=False)
                after = fingerprint(dataset)
                save_json(run/"dataset_fingerprint_after.json", after)
                if before != after:
                    raise RuntimeError("Dataset integrity changed during training; inspect fingerprints")
                report = dict(status="complete", started_utc=started_utc,
                    completed_utc=datetime.now(timezone.utc).isoformat(),
                    elapsed_seconds=time.perf_counter()-started,
                    environment=dict(python=sys.executable, ultralytics=ultralytics.__version__,
                        ultralytics_installation=str(Path(ultralytics.__file__).parent),
                        yolo_cli=str(ROOT/".venv/Scripts/yolo.exe"), torch=torch.__version__,
                        cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0)),
                    pretrained_checkpoint=str(args.model.resolve()), initial_pretrained_class_count=initial_classes,
                    best_checkpoint=str(run/"weights/best.pt"), last_checkpoint=str(run/"weights/last.pt"),
                    epochs_completed=epochs_completed, imgsz=args.imgsz, initial_batch=args.batch,
                    final_batch=model.trainer.batch_size, batch_history=batch_history,
                    seed=args.seed, workers=args.workers,
                    dataset=dict(root=str(dataset), train_images=480, validation_images=120,
                                 unchanged=True, fingerprinted_files=len(before),
                                 label_caches=str(run/"dataset_cache")),
                    metrics={k: float(v) for k, v in metrics.results_dict.items()},
                    per_class=per_class, inference_speed_ms=metrics.speed,
                    validation_example_images=len(val_images),
                    explanation="Fine-tuned pretrained YOLO26n to predict component classes, confidence scores and symbol-body bounding boxes.",
                    limitations=["Training and validation use only synthetic circuit images.",
                        "Synthetic validation metrics do not establish accuracy on real printed textbooks.",
                        "YOLO detection does not recover terminal coordinates, OCR values, electrical connections or simulation readiness.",
                        "This trained detector is not integrated into the production recognition pipeline."])
                save_json(run/"training_report.json", report)
                header = ["# YOLO26n synthetic circuit training report", "", report["explanation"], "",
                    f"Completed {epochs_completed} epochs at {args.imgsz}px on {report['environment']['gpu']}.",
                    f"Batch history: {batch_history}. Seed: {args.seed}. Workers: {args.workers}.",
                    "480 synthetic training images; 120 synthetic validation images. All original dataset files are unchanged.",
                    "", "| Class | Val objects | Precision | Recall | mAP50 | mAP50–95 |",
                    "|---|---:|---:|---:|---:|---:|"]
                for row in per_class:
                    header.append(f"| {row['name']} | {row['instances']} | {row['precision']:.4f} | {row['recall']:.4f} | {row['map50']:.4f} | {row['map50_95']:.4f} |")
                header += ["", "## Locations", "", f"- YOLO executable: `{report['environment']['yolo_cli']}`",
                    f"- Installed library: `{report['environment']['ultralytics_installation']}`",
                    f"- Pretrained starting weights: `{report['pretrained_checkpoint']}`",
                    f"- Best trained detector: `{report['best_checkpoint']}`",
                    f"- Final trained detector: `{report['last_checkpoint']}`",
                    "- `results.csv`, `results.png`, confusion matrices and validation plots: this run directory.",
                    "- `validation_predictions/`: twelve example predictions and predicted YOLO labels with confidence.",
                    "- `training.log`, `args.yaml`, `progress.json` and dataset fingerprints: this run directory.",
                    "", "## Scope and limits", ""] + [f"- {s}" for s in report["limitations"]]
                (run/"TRAINING_REPORT.md").write_text("\n".join(header)+"\n", encoding="utf-8")
                save_json(run/"progress.json", dict(status="complete", epochs_completed=epochs_completed,
                          metrics=report["metrics"], dataset_unchanged=True))
    except BaseException as exc:
        after = fingerprint(dataset)
        save_json(run/"dataset_fingerprint_after.json", after)
        save_json(run/"failure_report.json", dict(status="failed", error=str(exc),
                  dataset_unchanged=before == after, elapsed_seconds=time.perf_counter()-started,
                  traceback=traceback.format_exc()))
        save_json(run/"progress.json", dict(status="failed", error=str(exc), dataset_unchanged=before == after))
        print(f"Training failed: {exc}. See {run/'failure_report.json'}", file=console, flush=True)
        return 1
    print(json.dumps(report, indent=2), file=console, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

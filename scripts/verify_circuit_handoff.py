"""Verify shared circuit work; optionally restore archived evidence/staging only.

Uses the standard library. Never installs packages, trains models, calls VLMs or
overwrites a different source file. Run after git pull from any checkout path.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "requirements/circuit-handoff-v2.json"
REAL = ROOT / "datasets/circuits_v1/real_v1/evaluation_v1"
SYN = ROOT / "datasets/circuits_v1/synthetic_v1"
NAMES = {0: "resistor", 1: "voltage_source", 2: "capacitor", 3: "switch"}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_path(relative):
    p = (ROOT / relative.replace("\\", "/")).resolve()
    if not p.is_relative_to(ROOT) or p == ROOT:
        raise ValueError(f"Path outside checkout: {relative}")
    return p


def copy_protected(src, dst):
    if dst.exists():
        if digest(src) != digest(dst):
            raise ValueError(f"Different local file protected: {dst}")
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)


def descriptor(base, split, training=False):
    p = base / "data.yaml"
    if p.exists():
        if base.as_posix() not in p.read_text(encoding="utf-8"):
            raise ValueError(f"Existing staging descriptor needs manual review: {p}")
        return
    text = f"path: {json.dumps(base.as_posix())}\ntrain: {'images/train' if training else 'null'}\nval: images/{split}\n"
    if split == "test":
        text += "test: images/test\n"
    text += "names:\n" + "".join(f"  {i}: {name}\n" for i, name in NAMES.items())
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def real_copy(base):
    for p in sorted((REAL / "images").glob("*.png")):
        copy_protected(p, base / "images/test" / p.name)
        copy_protected(REAL / "labels" / (p.stem + ".txt"), base / "labels/test" / (p.stem + ".txt"))
    descriptor(base, "test")


def prepare_staging():
    parent = ROOT / "runs/augmented_physics"
    evaluation = parent / "real_evaluation_20261031_1a572ba"
    real_copy(evaluation / "data/real")
    synthetic = evaluation / "data/synthetic"
    for folder in ("images/val", "labels/val"):
        for p in (SYN / folder).iterdir():
            if p.is_file():
                copy_protected(p, synthetic / folder / p.name)
    descriptor(synthetic, "val")
    training = parent / "circuits_real_v2_20261031"
    records = json.loads((training / "data_manifest.json").read_text())["records"]
    for r in records:
        source = safe_path(r["source"])
        target = training / "data" / r["image"].replace("\\", "/")
        copy_protected(source, target)
        label_source = REAL / "labels" / (source.stem + ".txt") if r["domain"] == "real" else SYN / "labels" / source.parent.name / (source.stem + ".txt")
        label_target = Path(str(target).replace("/images/", "/labels/").replace("\\images\\", "\\labels\\")).with_suffix(".txt")
        copy_protected(label_source, label_target)
    descriptor(training / "data", "val", training=True)
    real_copy(training / "real_training_fit")
    print("Prepared byte-identical staging copies and checkout-local descriptors; no training/inference performed.")


def restore_research(manifest):
    archive_path = safe_path(manifest["research_archive"])
    with zipfile.ZipFile(archive_path) as z:
        records = json.loads(z.read("handoff_archive_manifest.json"))["files"]
        if len(z.namelist()) != len(records)+1 or set(z.namelist()) != set(records) | {"handoff_archive_manifest.json"}:
            raise ValueError("Research archive contains unexpected entries")
        destinations = []
        for relative, expected in records.items():
            if not relative.startswith(("storage/generated/debug_traces/", "storage/generated/circuit_repair_20261018/",
                "storage/generated/circuit_generalization_live/", "outputs/multi_balls/", "outputs/optics_pipeline_debug/", "outputs/scene_pipeline_debug/")):
                raise ValueError(f"Unexpected research destination: {relative}")
            dst = safe_path(relative)
            if dst.exists() and digest(dst) != expected["sha256"]:
                raise ValueError(f"Different local evidence protected: {dst}")
            data = z.read(relative)
            if hashlib.sha256(data).hexdigest() != expected["sha256"] or len(data) != expected["bytes"]:
                raise ValueError(f"Research checksum mismatch: {relative}")
            destinations.append((relative, dst))
        for relative, dst in destinations:
            if not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                with z.open(relative) as src, dst.open("xb") as out:
                    shutil.copyfileobj(src, out)
    print(f"Restored/reused {len(records)} recorded research files without rerunning the investigations.")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prepare-staging", action="store_true")
    p.add_argument("--restore-research", action="store_true")
    args = p.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for name, record in manifest["files"].items():
        path = safe_path(name)
        if not path.is_file() or path.stat().st_size != record["bytes"] or digest(path) != record["sha256"]:
            raise ValueError(f"Missing/changed handoff asset: {name}. Pull the complete handoff commits first.")
    print(f"Verified {len(manifest['files'])} shared assets, including v1/v2 weights, annotations and recorded results.")
    if args.restore_research:
        restore_research(manifest)
    if args.prepare_staging:
        prepare_staging()


if __name__ == "__main__":
    main()

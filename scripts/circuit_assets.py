"""Export/restore ignored model weights through a hash-verified handoff ZIP.

Weights remain outside Git. Extraction never overwrites a differing local file.
The trusted, versioned manifest is checked before any archive bytes are written.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'requirements/circuit-assets-v1.json'
FILES = (
    'checkpoints/sam2.1_hiera_tiny.pt', 'checkpoints/yolo26n.pt',
    'runs/augmented_physics/circuits_synthetic_v1/weights/best.pt',
    'runs/augmented_physics/circuits_synthetic_v1/weights/last.pt',
)


def digest(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024*1024), b''):
        h.update(chunk)
    return h.hexdigest()


def file_digest(path):
    with path.open('rb') as stream:
        return digest(stream)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--write-manifest', action='store_true')
    actions.add_argument('--verify-only', action='store_true')
    actions.add_argument('--export', type=Path, metavar='ZIP')
    actions.add_argument('--restore', type=Path, metavar='ZIP')
    args = parser.parse_args(argv)
    if args.write_manifest:
        manifest = dict(version=1, files={name: dict(bytes=(ROOT/name).stat().st_size,
                        sha256=file_digest(ROOT/name)) for name in FILES})
        MANIFEST.parent.mkdir(exist_ok=True)
        MANIFEST.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
        print(f'Wrote manifest for {len(FILES)} model files.')
        return 0
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if set(manifest['files']) != set(FILES):
        raise ValueError('Unexpected paths in the versioned model manifest')
    if args.restore:
        with zipfile.ZipFile(args.restore) as archive:
            expected = set(FILES) | {'circuit-assets-v1.json'}
            if set(archive.namelist()) != expected or len(archive.namelist()) != len(expected):
                raise ValueError('Archive contains unexpected, missing or duplicate entries')
            if json.loads(archive.read('circuit-assets-v1.json')) != manifest:
                raise ValueError('Archive manifest differs from the checked-in trusted manifest')
            for name, record in manifest['files'].items():
                if archive.getinfo(name).file_size != record['bytes']:
                    raise ValueError(f'Wrong size: {name}')
                with archive.open(name) as stream:
                    if digest(stream) != record['sha256']:
                        raise ValueError(f'Wrong hash: {name}')
                destination = (ROOT/name).resolve()
                if not destination.is_relative_to(ROOT.resolve()):
                    raise ValueError('Asset destination escaped the repository')
                if destination.exists() and file_digest(destination) != record['sha256']:
                    raise ValueError(f'Existing different asset is protected: {name}')
            for name in FILES:
                destination = ROOT/name
                if not destination.exists():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(name) as source, destination.open('xb') as target:
                        shutil.copyfileobj(source, target)
    for name, record in manifest['files'].items():
        path = ROOT/name
        if not path.is_file() or path.stat().st_size != record['bytes'] or file_digest(path) != record['sha256']:
            raise ValueError(f'Missing or changed asset: {name}')
    if args.export:
        args.export.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.export, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
            archive.write(MANIFEST, 'circuit-assets-v1.json')
            for name in FILES:
                archive.write(ROOT/name, name)
        with zipfile.ZipFile(args.export) as archive:
            if archive.testzip() is not None:
                raise ValueError('Asset archive CRC check failed')
        print(f'Created {args.export.resolve()} ({args.export.stat().st_size} bytes).')
    print('All four model files match the versioned SHA-256 manifest.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

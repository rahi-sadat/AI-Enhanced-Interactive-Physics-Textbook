"""Verify the pinned laptop environment with no external API calls."""
import argparse
import importlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-sam2', action='store_true')
    args = parser.parse_args(argv)
    snapshot = json.loads((ROOT/'requirements/windows-py313-environment.json').read_text(encoding='utf-8'))
    errors, warnings = [], []
    if sys.version_info[:2] != (3, 13):
        errors.append('This lock targets Python 3.13 on Windows x64.')
    if platform.python_version() != snapshot['python']:
        warnings.append(f"Author used Python {snapshot['python']}; current patch is {platform.python_version()}.")
    for name, expected in snapshot['packages'].items():
        if args.skip_sam2 and name.lower().replace('_', '-') == 'sam-2':
            continue
        try:
            actual = metadata.version(name)
        except metadata.PackageNotFoundError:
            actual = '<missing>'
        if actual != expected:
            errors.append(f'{name}: expected {expected}, found {actual}')
    imports = ['numpy', 'cv2', 'PIL', 'matplotlib', 'schemdraw', 'ultralytics',
               'torch', 'torchvision', 'fastapi', 'google.genai', 'rapidocr', 'easyocr']
    if not args.skip_sam2:
        imports.append('sam2')
    imported = []
    for name in imports:
        try:
            importlib.import_module(name)
            imported.append(name)
        except Exception as exc:
            errors.append(f'Import {name}: {exc}')
    if not args.skip_sam2:
        result = subprocess.run(['git', '-C', str(ROOT/'sam2'), 'rev-parse', 'HEAD'], capture_output=True, text=True)
        if result.stdout.strip() != snapshot['sam2']['commit']:
            errors.append('SAM-2 checkout does not match the pinned commit.')
    checked = subprocess.run([sys.executable, '-m', 'pip', 'check'], capture_output=True, text=True)
    messages = (checked.stdout+checked.stderr).strip().splitlines()
    for message in messages:
        if message == snapshot['known_packaging_warning']:
            warnings.append(message+' The author uses the GUI opencv-python distribution providing cv2.')
        elif message and message != 'No broken requirements found.':
            errors.append(message)
    gpu = None
    if 'torch' in imported:
        import torch
        if torch.cuda.is_available():
            try:
                torch.ones(4, device='cuda').sum().item()
                gpu = torch.cuda.get_device_name(0)
            except Exception as exc:
                errors.append(f'CUDA kernel check failed: {exc}')
        else:
            warnings.append('CUDA unavailable. Use device=cpu for prediction; this training launcher requires CUDA.')
    print(json.dumps(dict(python=sys.executable, python_version=platform.python_version(),
                          matched_snapshot=not errors, gpu=gpu, imports=imported,
                          warnings=warnings, errors=errors), indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())

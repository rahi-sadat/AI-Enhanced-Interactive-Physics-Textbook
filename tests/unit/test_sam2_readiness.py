"""Offline readiness, failure-cache and mutable-predictor regressions."""
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from ai.evidence.segmentation import sam2_provider as module
from ai.evidence.segmentation.base import SegmentationPrompt
from shared.schemas.evidence import ExtractionStatus, SourceBBox


@pytest.fixture
def provider(tmp_path, monkeypatch):
    for name in ('_CACHED_SAM2_MODEL', '_CACHED_SAM2_PREDICTOR', '_CACHED_SAM2_KEY', '_CACHED_IMAGE_SIG'):
        monkeypatch.setattr(module, name, None)
    monkeypatch.setattr(module, '_INITIALIZATION_FAILURES', {})
    path = tmp_path / 'offline.pt'
    path.write_bytes(b'explicit test double, never real inference')
    return module.SAM2SegmentationProvider(str(path), device='cpu')


def test_missing_checkpoint_is_not_available(provider):
    provider.checkpoint_path += '.missing'
    assert not provider.available()
    assert provider.readiness()['state'] == 'MISSING_CHECKPOINT'


@pytest.mark.parametrize('error,state', [
    (ModuleNotFoundError("No module named 'sam2'"), 'MISSING_DEPENDENCY'),
    (ModuleNotFoundError("No module named 'iopath'"), 'MISSING_DEPENDENCY'),
    (ImportError('Broken Hiera import'), 'IMPORT_FAILURE'),
])
def test_import_failures_report_cause_once(provider, monkeypatch, error, state):
    loader = Mock(side_effect=error)
    monkeypatch.setattr(module.importlib, 'import_module', loader)
    assert not provider.available()
    calls = loader.call_count
    assert not provider.available()
    assert loader.call_count == calls
    assert provider.readiness()['state'] == state
    assert str(error) in provider.readiness()['error']


@pytest.mark.parametrize('configuration', [False, True])
def test_initialization_failure_cached_and_checkpoint_change_retries(provider, monkeypatch, configuration):
    from hydra.errors import MissingConfigException
    error = MissingConfigException('Bad YAML') if configuration else RuntimeError('Checkpoint size mismatch')
    builder = Mock(side_effect=error)
    monkeypatch.setattr(provider, '_load_runtime', lambda: (builder, Mock()))
    assert not provider.available()
    assert not provider.available()
    assert builder.call_count == 1
    assert provider.readiness()['state'] == ('CONFIGURATION_FAILURE' if configuration else 'MODEL_INITIALIZATION_FAILURE')
    from pathlib import Path
    Path(provider.checkpoint_path).write_bytes(b'changed checkpoint identity')
    assert not provider.available()
    assert builder.call_count == 2


def test_ready_proves_construction_and_serializes_concurrent_initialization(provider, monkeypatch):
    builder, predictor_class = Mock(return_value=object()), Mock(return_value=object())
    monkeypatch.setattr(provider, '_load_runtime', lambda: (builder, predictor_class))
    with ThreadPoolExecutor(6) as pool:
        assert all(pool.map(lambda _: provider.available(), range(12)))
    builder.assert_called_once_with(provider.config_path, provider.checkpoint_path, device='cpu')
    predictor_class.assert_called_once_with(builder.return_value)
    assert provider.readiness()['state'] == 'READY'


def test_predictor_embedding_is_atomic_and_frame_validated(provider, monkeypatch):
    class Predictor:
        def __init__(self, model): self.image = None
        def set_image(self, image): self.image = image.copy()
        def predict(self, **kwargs):
            mask = self.image[:, :, 0] == 0
            return np.array([mask]), np.array([.8]), None
    monkeypatch.setattr(provider, '_load_runtime', lambda: (lambda *a, **k: None, Predictor))
    prompt = SegmentationPrompt(box=SourceBBox(0, 0, 30, 30))
    def segment(i):
        image = np.full((30, 30, 3), 255, np.uint8)
        image[5:5+i, 5:10] = 0
        result = provider.segment(image, prompt, source_width=30, source_height=30)
        return result.masks[0].area_px
    with ThreadPoolExecutor(5) as pool:
        assert list(pool.map(segment, range(1, 11))) == [i*5 for i in range(1, 11)]
    mismatch = provider.segment(np.zeros((20, 20, 3), np.uint8), prompt, source_width=30, source_height=30)
    assert mismatch.status == ExtractionStatus.ERROR
    assert provider._diagnostics['state'] == 'INFERENCE_FAILURE'


@pytest.mark.parametrize('score,shape', [(float('nan'), (30, 30)), (.9, (10, 10))])
def test_invalid_mask_rejected(provider, monkeypatch, score, shape):
    predictor = SimpleNamespace(set_image=lambda _: None,
        predict=lambda **_: (np.ones((1, *shape)), np.array([score]), None))
    monkeypatch.setattr(provider, '_load_runtime', lambda: (lambda *a, **k: None, lambda _: predictor))
    result = provider.segment(np.zeros((30, 30, 3), np.uint8), SegmentationPrompt(), source_width=30, source_height=30)
    assert result.status == ExtractionStatus.NO_EVIDENCE
    assert result.masks == []

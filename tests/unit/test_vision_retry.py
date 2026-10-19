"""Offline SDK doubles: no credentials, network, or live provider calls."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ai.ingestion.vision.gemini_provider import GeminiVisionProvider
from ai.ingestion.vision.provider_interface import VisionProviderError


def provider(monkeypatch, outcomes):
    monkeypatch.setattr("time.sleep", lambda _: None)
    instance = GeminiVisionProvider(api_key="offline-test", model="test-primary")
    generate = Mock(side_effect=outcomes)
    instance._client = SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    return instance, generate


def response():
    return SimpleNamespace(text=json.dumps({
        "classification": "supported", "isPhysics": True, "domain": "optics", "subtype": "prism",
        "confidence": {"isPhysics": .9, "domain": .9, "subtype": .9, "overall": .9},
        "entities": [], "relationships": [], "visibleLabels": [], "candidates": [], "notes": [],
    }))


def test_transient_failure_retries_same_model(monkeypatch):
    instance, generate = provider(monkeypatch, [RuntimeError("503 UNAVAILABLE"), response()])
    result = instance.analyze_diagram(b"test-image", "image/png", None)
    assert [call.kwargs["model"] for call in generate.call_args_list] == ["test-primary", "test-primary"]
    assert result.subtype == "prism" and result.fallback_used


@pytest.mark.parametrize("error", ["429 RESOURCE_EXHAUSTED", "404 NOT_FOUND"])
def test_quota_or_missing_model_switches_without_retry(monkeypatch, error):
    instance, generate = provider(monkeypatch, [RuntimeError(error), response()])
    result = instance.analyze_diagram(b"test-image", "image/png", None)
    assert [call.kwargs["model"] for call in generate.call_args_list] == ["test-primary", "gemini-3.1-flash-lite"]
    assert result.fallback_used


def test_auth_error_fails_without_retries(monkeypatch):
    instance, generate = provider(monkeypatch, RuntimeError("403 PERMISSION_DENIED"))
    with pytest.raises(VisionProviderError):
        instance.analyze_diagram(b"test-image", "image/png", None)
    assert generate.call_count == 1


def test_outage_is_bounded_and_never_returns_a_fake_scene(monkeypatch):
    instance, generate = provider(monkeypatch, RuntimeError("503 UNAVAILABLE"))
    with pytest.raises(VisionProviderError):
        instance.analyze_diagram(b"test-image", "image/png", None)
    assert generate.call_count == 8  # Configured primary + three existing fallback models, two tries each.

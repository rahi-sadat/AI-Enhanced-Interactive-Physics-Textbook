"""Offline checks for preview separation and diagnostic recovery."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ai.ingestion import UploadService, PageIRBuilder, BookUnderstandingPipeline
from ai.ingestion.vision.analyzer import PhysicsVisionAnalyzer
from ai.ingestion.vision.mock_provider import MockVisionProvider
from ai.perception.circuits.circuit_v2 import CircuitDetection
from ai.perception.circuits.v2_experiment import make_preview, run_experiment
from apps.api.circuit_v2_lab import create_router
from shared.schemas.evidence import SourceBBox


def test_preview_keeps_proposals_immutable_and_discloses_synthetic_components():
    proposals = [CircuitDetection("resistor", .7, SourceBBox(40,30,20,10))]
    before = deepcopy(proposals)
    asset = SimpleNamespace(width_px=200,height_px=100)
    preview = make_preview(proposals, asset, "/uploads/test.png")
    assert proposals == before
    assert preview["metadata"] == {"experimental": True, "verified": False}
    assert preview["coordinateSpace"]["width"] == 200
    assert len(preview["circuit"]["components"]) == 2
    assert any("Added synthetic voltage_source" in a["reason"] for a in preview["assumptions"])
    assert all(c["provenance"]["verified"] is False for c in preview["circuit"]["components"])
    assert all(p["provenance"] == "experimental_assumption" for p in preview["parameters"].values())
    assert all(p["source"] == "experimental_preview" and p["confidence"] == 0.0
               for p in preview["parameters"].values())


def test_failed_grounding_keeps_exact_failure_without_guessed_simulation(tmp_path):
    checkpoint = tmp_path/"model.pt"
    checkpoint.write_bytes(b"offline canned checkpoint identity")
    understanding = BookUnderstandingPipeline(analyzer=PhysicsVisionAnalyzer(provider=MockVisionProvider()))
    understanding._circuit_detector = SimpleNamespace(checkpoint=checkpoint,
        predict=Mock(return_value=[CircuitDetection("resistor", .8, SourceBBox(40,30,20,10))]))
    understanding._get_analyzer = Mock(side_effect=AssertionError("VLM must not run in the experiment"))
    evidence = SimpleNamespace(extract_and_fuse=Mock(side_effect=RuntimeError("CV could not trace wire endpoints")))
    compiler = SimpleNamespace(compile=Mock(side_effect=AssertionError("Compilation after failed grounding")))
    services = (UploadService(tmp_path/"uploads",tmp_path/"public"),PageIRBuilder(),understanding,evidence,compiler)
    ok, encoded = cv2.imencode(".png", np.full((100,200,3),255,dtype=np.uint8))
    assert ok
    result = run_experiment(encoded.tobytes(),"unrelated-name.png","image/png",services)
    assert result["scene"] is None
    assert result["preview_scene"] is None
    assert result["first_blocker"]["stage"] == "grounding"
    assert result["first_blocker"]["message"] == "CV could not trace wire endpoints"
    assert result["book_ir"]["parameters"] == {}
    assert result["book_ir"]["entities"][0]["geometry"] is None
    understanding._get_analyzer.assert_not_called()
    compiler.compile.assert_not_called()
    app = FastAPI()
    app.include_router(create_router(lambda: services))
    with TestClient(app) as client:
        response = client.post("/api/experiments/circuit-v2",files={"file":("test.png",encoded.tobytes(),"image/png")})
        assert response.status_code == 200
        assert response.json()["first_blocker"]["stage"] == "grounding"
        analysis_id = response.json()['analysis_id']
        analysis = client.post('/api/experiments/circuit-v2/analysis',json={'analysis_id':analysis_id,'mode':'non_ideal'})
        assert analysis.status_code == 200 and analysis.json()['status'] == 'NEEDS_REVIEW'
        assert analysis.json()['electrical_state'] is None
        invalid_parameter = client.post('/api/experiments/circuit-v2/analysis',json={
            'analysis_id':analysis_id,'mode':'non_ideal','short_path_resistance_ohm':0})
        assert invalid_parameter.status_code == 422
        unknown = client.post('/api/experiments/circuit-v2/analysis',json={'analysis_id':'unknown'})
        assert unknown.status_code == 404
        invalid = client.post("/api/experiments/circuit-v2",files={"file":("test.png",b"not an image","image/png")})
        assert invalid.status_code == 422

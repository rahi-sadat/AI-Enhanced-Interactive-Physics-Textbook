"""Exercise the production upload endpoint with the local checkpoint and no VLM."""
import asyncio
from collections import Counter
from pathlib import Path
from unittest.mock import Mock

import cv2
import httpx
from fastapi.testclient import TestClient

from ai.evidence.ocr import MockOCRProvider
from ai.evidence.pipeline import EvidenceExtractionPipeline
from ai.evidence.segmentation import UnavailableSegmentationProvider
from ai.ingestion import BookUnderstandingPipeline, PageIRBuilder, PhysicsCompiler, UploadService
from shared.schemas.evidence import OCRToken, SourceBBox


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "unseen"
GENERALIZATION_FIXTURES = FIXTURES.parent / "circuit_generalization"


def test_circuit_v2_upload_compiles_only_verified_topology(monkeypatch, tmp_path):
    from apps.api import main

    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("USE_MOCK_VISION", "false")
    monkeypatch.setenv("CIRCUIT_V2_ONLY", "false")
    monkeypatch.setenv("YOLO_OFFLINE", "true")
    monkeypatch.setenv("YOLO_CONFIG_DIR", str(tmp_path / "yolo"))
    pipeline = BookUnderstandingPipeline()
    vlm = Mock(side_effect=AssertionError("Local circuit upload reached the VLM"))
    monkeypatch.setattr(pipeline, "_get_analyzer", vlm)
    ocr_tokens = [
        OCRToken(id="r1", raw_text="R₁", confidence=.95, bbox_source_px=SourceBBox(643, 157, 62, 48)),
        OCRToken(id="r1_value", raw_text="= 10 Ω", confidence=.95, bbox_source_px=SourceBBox(710, 157, 161, 48)),
        OCRToken(id="r2", raw_text="R₂ = 20 Ω", confidence=.95, bbox_source_px=SourceBBox(1039, 433, 222, 53)),
    ]
    ocr = MockOCRProvider(canned_tokens=ocr_tokens)
    services = (
        UploadService(tmp_path / "uploads", tmp_path / "public"),
        PageIRBuilder(),
        pipeline,
        EvidenceExtractionPipeline(
            ocr_provider=ocr,
            segmentation_provider=UnavailableSegmentationProvider(),
        ),
        PhysicsCompiler(),
    )
    monkeypatch.setattr(main, "_get_ingestion_pipeline", lambda: services)

    image = FIXTURES / "user_circuit_open_switch.jpg"
    # Erase a section of the left lead, away from the switch and source bodies.
    broken = cv2.imread(str(image))
    broken[322:349, 210:250] = 255
    ok, encoded = cv2.imencode(".png", broken)
    assert ok

    async def upload_examples():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=main.app), base_url="http://test", trust_env=False,
        ) as client:
            good = await client.post(
                "/api/ingest", files={"file": ("diagram.jpg", image.read_bytes(), "image/jpeg")},
            )
            damaged = await client.post(
                "/api/ingest", files={"file": ("diagram.png", encoded.tobytes(), "image/png")},
            )
            monkeypatch.setenv("CIRCUIT_V2_ONLY", "true")
            photo = (FIXTURES / "unrelated" / "landscape_photo.jpg").read_bytes()
            unknown = await client.post("/api/ingest", files={"file": ("circuit.jpg", photo, "image/jpeg")})
            # Leave title and caption ink in the raster even when labels were read.
            ocr.canned_tokens = [
                OCRToken(id="parallel_v", raw_text="V = 6 V", confidence=.95, bbox_source_px=SourceBBox(25, 590, 195, 70)),
                OCRToken(id="parallel_r1", raw_text="R1 = 10 Ω", confidence=.95, bbox_source_px=SourceBBox(780, 545, 220, 65)),
                OCRToken(id="parallel_r2", raw_text="R2 = 15 Ω", confidence=.95, bbox_source_px=SourceBBox(1200, 540, 230, 70)),
            ]
            parallel_bytes = (GENERALIZATION_FIXTURES / "parallel_three_plate.jpeg").read_bytes()
            parallel = await client.post("/api/ingest", files={"file": ("diagram.jpg", parallel_bytes, "image/jpeg")})
            ocr.canned_tokens = []
            symbolic_bytes = (GENERALIZATION_FIXTURES / "symbolic_single_loop.png").read_bytes()
            symbolic = await client.post("/api/ingest", files={"file": ("diagram.png", symbolic_bytes, "image/png")})
            mixed_bytes = (GENERALIZATION_FIXTURES / "mixed_four_resistors.jpg").read_bytes()
            mixed = await client.post("/api/ingest", files={"file": ("diagram.jpg", mixed_bytes, "image/jpeg")})
            responses = (good, damaged, unknown, parallel, symbolic, mixed)
            for response in responses:
                assert response.status_code == 200, response.text
            return [response.json() for response in responses]

    good, damaged, unknown, parallel, symbolic, mixed = asyncio.run(upload_examples())
    vlm.assert_not_called()
    assert good['compiler']['status']=='NEEDS_REVIEW' and good['scene'] is None
    assert not good['book_ir']['assumptions']
    # The omitted source voltage now requires a real user decision. Exercise
    # the production resolution/compile endpoints before testing playback.
    with TestClient(main.app) as client:
        source_id=next(c['id'] for c in good['book_ir']['parameters']['components'] if c['type']=='voltage_source')
        resolved=client.post('/api/resolution/resolve',json={'book_ir':good['book_ir'],'resolution':{
            'parameter_name':f'component.{source_id}.value','resolved_value':12,'canonical_unit':'V',
            'resolution_source':'user_supplied','user_accepted':True}})
        assert resolved.status_code==200,resolved.text
        compiled=client.post('/api/resolution/compile',json={'book_ir':resolved.json()['book_ir']})
        assert compiled.status_code==200,compiled.text
        good.update(compiled.json())
    book = good["book_ir"]
    assert book["provenance"]["model"] == "circuit_v2"
    assert good["compiler"]["status"] == "READY", good["issues"]
    components = good["scene"]["circuit"]["components"]
    assert Counter(c["type"] for c in components) == {"resistor": 2, "voltage_source": 1, "switch": 1}
    assert all(c["provenance"]["method"] == "classical_cv" for c in components)
    switch = next(c for c in components if c["type"] == "switch")
    assert switch["state"] == "open" and switch["state_verified"] is True
    assert switch["nodes"][0] != switch["nodes"][1]
    parameters = good["scene"]["parameters"]
    assert {(c["label"], c["value"], parameters[c["id"]]["provenance"])
            for c in components if c["type"] == "resistor"} == {("R1", 10, "ocr"), ("R2", 20, "ocr")}
    source = next(c for c in components if c["type"] == "voltage_source")
    assert parameters[source["id"]]["provenance"] == "user_supplied"
    assert (good["scene"]["coordinateSpace"]["width"], good["scene"]["coordinateSpace"]["height"]) == (1280, 960)

    assert damaged["book_ir"]["provenance"]["model"] == "circuit_v2"
    assert damaged["compiler"]["status"] == "NEEDS_REVIEW"
    assert damaged["scene"] is None
    assert unknown["compiler"]["status"] == "UNRESOLVED"
    assert unknown["domain"] is None and unknown["scene"] is None

    assert parallel["compiler"]["status"] == "READY", parallel["book_ir"]["reviewIssues"]
    # Pixel-specific masks can reject caption glyphs before assignment, so
    # their old off-circuit *verified* count is not a readiness requirement.
    assert parallel['book_ir']['provenance']['circuit_reconciliation']
    assert all(r['status']=='SUPPORTED' for r in parallel['book_ir']['provenance']['circuit_reconciliation']
               if r['candidate_id'] in parallel['book_ir']['provenance']['semantic_geometry_identity_map'].values())
    parallel_components = parallel["scene"]["circuit"]["components"]
    assert {c["label"]: c["value"] for c in parallel_components} == {"V1": 6, "R1": 10, "R2": 15}
    assert len({frozenset(c["nodes"]) for c in parallel_components}) == 1

    assert symbolic["compiler"]["status"] == "NEEDS_REVIEW" and symbolic['scene'] is None
    assert Counter(c["type"] for c in symbolic['book_ir']['parameters']['components']) == {"resistor": 1, "voltage_source": 1}
    assert all(c["nodes"][0] != c["nodes"][1] for c in symbolic['book_ir']['parameters']['components'])

    assert mixed["compiler"]["status"] == "NEEDS_REVIEW" and mixed['scene'] is None
    assert Counter(c["type"] for c in mixed['book_ir']['parameters']['components']) == {"resistor": 4, "voltage_source": 1}
    assert len(mixed['book_ir']['parameters']['nodes']) == 4

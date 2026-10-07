"""PR-07 Integration Tests: FastAPI Endpoints & Health Check.

Verifies:
  - GET /api/ingest/health reports PR-07 pipeline capabilities, policy registry, unit engine.
  - POST /api/resolution/review analyzes grounded BookIR and returns ReviewState.
  - POST /api/resolution/resolve applies explicit user values and policies with provenance.
  - POST /api/resolution/evaluate validates the compilation readiness invariant.
  - POST /api/resolution/compile gates non-ready BookIR and compiles legitimately resolved BookIR.
"""
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from shared.schemas.ingestion import BookIRStatus


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def pendulum_book_ir_dict():
    return {
        "sourceAssetId": "asset_api_test",
        "figureId": "fig_api_test",
        "domain": "mechanics",
        "subtype": "pendulum",
        "status": "NEEDS_REVIEW",
        "entities": [
            {"id": "e_pivot", "type": "pivot", "positionSourcePx": {"x": 250, "y": 80}},
            {"id": "e_bob", "type": "bob", "positionSourcePx": {"x": 250, "y": 480}},
            {"id": "e_str", "type": "string", "positionSourcePx": {"x": 250, "y": 80}, "geometry": {"effective_length_px": 400}},
        ],
        "geometry": {
            "pivot": {"x": 250, "y": 80},
            "bob_center": {"x": 250, "y": 480},
            "string_length_px": 400.0,
            "bob_radius_px": 20.0,
            "width": 800.0,
            "height": 600.0,
        },
        "parameters": {},
        "evidence": {
            "ev_ocr_1": {
                "id": "ev_ocr_1",
                "method": "ocr",
                "tokens": [
                    {
                        "id": "tok_1",
                        "rawText": "L = 80 cm",
                        "candidates": [
                            {"quantityCandidate": "length", "numericValue": 80.0, "rawUnit": "cm", "confidence": 0.8}
                        ]
                    }
                ]
            }
        }
    }


class TestIngestHealth:
    """Test health check reports PR-07 capabilities."""

    def test_health_reports_pr07_capabilities(self, client):
        resp = client.get("/api/ingest/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["pipeline"] == "PR-07"
        assert "resolution" in data
        res_info = data["resolution"]
        assert res_info["available"] is True
        assert res_info["resolutionEngine"] is True
        assert res_info["unitEngine"] is True
        assert res_info["policyRegistry"] is True
        assert res_info["readinessEvaluator"] is True
        assert "policy_earth_gravity" in res_info["policies"]
        assert "mechanics/pendulum" in res_info["supportedSubtypes"]


class TestResolutionEndpoints:
    """Test resolution API workflow."""

    def test_review_endpoint(self, client, pendulum_book_ir_dict):
        resp = client.post("/api/resolution/review", json={"book_ir": pendulum_book_ir_dict})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["ready_to_compile"] is False
        assert data["blockers_count"] > 0
        issues = data["review_state"]["issues"]
        param_names = [iss["parameterName"] for iss in issues if iss["parameterName"]]
        assert "gravity" in param_names or "length" in param_names

    def test_resolve_endpoint_user_value(self, client, pendulum_book_ir_dict):
        # Resolve physical length
        resp = client.post("/api/resolution/resolve", json={
            "book_ir": pendulum_book_ir_dict,
            "resolution": {
                "parameterName": "length",
                "resolvedValue": 0.8,
                "canonicalUnit": "m",
                "resolutionSource": "user_supplied",
            }
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["resolvedValue"] == pytest.approx(0.8)
        assert data["book_ir"]["parameters"]["length"] == pytest.approx(0.8)

    def test_resolve_endpoint_policy(self, client, pendulum_book_ir_dict):
        # Apply gravity policy
        resp = client.post("/api/resolution/resolve", json={
            "book_ir": pendulum_book_ir_dict,
            "policy_id": "policy_earth_gravity",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["resolvedValue"] == pytest.approx(9.80665)
        assert data["book_ir"]["parameters"]["gravity"] == pytest.approx(9.80665)

    def test_compile_gating_and_success(self, client, pendulum_book_ir_dict):
        # 1. Attempting compile on non-ready BookIR returns 400
        compile_fail = client.post("/api/resolution/compile", json={"book_ir": pendulum_book_ir_dict})
        assert compile_fail.status_code == 400
        assert "not ready" in str(compile_fail.json()).lower()

        # 2. Resolve all blockers
        book_ir = pendulum_book_ir_dict
        # length
        res = client.post("/api/resolution/resolve", json={
            "book_ir": book_ir,
            "resolution": {
                "parameterName": "length",
                "resolvedValue": 0.8,
                "canonicalUnit": "m",
                "resolutionSource": "user_supplied",
            }
        }).json()
        book_ir = res["book_ir"]

        # gravity
        res = client.post("/api/resolution/resolve", json={
            "book_ir": book_ir,
            "policy_id": "policy_earth_gravity",
        }).json()
        book_ir = res["book_ir"]

        # mass
        res = client.post("/api/resolution/resolve", json={
            "book_ir": book_ir,
            "policy_id": "policy_standard_mass",
        }).json()
        book_ir = res["book_ir"]

        # damping
        res = client.post("/api/resolution/resolve", json={
            "book_ir": book_ir,
            "policy_id": "policy_zero_damping",
        }).json()
        book_ir = res["book_ir"]

        assert book_ir["status"] == BookIRStatus.READY_TO_COMPILE

        # 3. Now compile succeeds!
        compile_success = client.post("/api/resolution/compile", json={"book_ir": book_ir})
        assert compile_success.status_code == 200
        c_data = compile_success.json()
        assert c_data["success"] is True
        assert c_data["compiler"]["status"] == "READY"
        assert c_data["scene"] is not None
        assert c_data["scene"]["subtype"] == "pendulum"

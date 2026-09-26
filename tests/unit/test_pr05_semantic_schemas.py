"""PR-05 Unit Tests — Semantic Schema Validation & Invariants.

Tests:
  1. Valid structured JSON passes validation.
  2. Free-form prose and non-dict inputs are strictly rejected.
  3. subtype sentinels ('non_physics', 'unknown', 'physics_but_unsupported') are NOT allowed in subtype.
  4. Non-physics forces domain=None, subtype=None, isPhysics=False.
  5. Unsupported physics forces subtype=None, isPhysics=True.
  6. visibleLabels enforces verified=False (unverified candidate evidence).
  7. Semantic entities require role string and enforce precision="approximate".
  8. Missing confidence object is rejected.
"""
from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import unittest
from shared.schemas.semantic import (
    SemanticAnalysisResult,
    SemanticConfidence,
    SemanticEntity,
    SemanticRelationship,
    SemanticValidationError,
    SemanticVisibleLabel,
    validate_semantic_payload,
)


class TestPR05SemanticSchemas(unittest.TestCase):
    """Test suite for PR-05 semantic schemas and validation rules."""

    def test_valid_structured_json_passes(self):
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {
                "isPhysics": 0.99,
                "domain": 0.96,
                "subtype": 0.94,
            },
            "entities": [
                {"temporaryId": "e1", "role": "pivot", "confidence": 0.95},
                {"temporaryId": "e2", "role": "bob", "label": "m", "confidence": 0.98},
            ],
            "relationships": [
                {"type": "connected_to", "from": "e1", "to": "e2", "confidence": 0.92},
            ],
            "visibleLabels": [
                {"text": "L = 1.0 m", "confidence": 0.88, "semanticRole": "length_label"},
            ],
            "notes": ["Clear single-bob pendulum"],
        }
        result = validate_semantic_payload(payload)
        self.assertTrue(result.is_supported)
        self.assertEqual(result.classification, "supported")
        self.assertEqual(result.domain, "mechanics")
        self.assertEqual(result.subtype, "pendulum")
        self.assertEqual(len(result.entities), 2)
        self.assertEqual(result.entities[0].role, "pivot")
        self.assertEqual(result.entities[0].precision, "approximate")
        self.assertEqual(len(result.relationships), 1)
        self.assertEqual(len(result.visible_labels), 1)
        # Visible labels must remain unverified in PR-05
        self.assertFalse(result.visible_labels[0].verified)

    def test_free_form_prose_rejected(self):
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload("This is a photo of a pendulum swinging from a ceiling.")
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload(12345)
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload(None)

    def test_subtype_sentinels_strictly_forbidden_as_subtypes(self):
        """'non_physics', 'physics_but_unsupported', and 'unknown' must NEVER be in subtype."""
        payload_np = {
            "classification": "non_physics",
            "isPhysics": False,
            "subtype": "non_physics",
            "confidence": {"isPhysics": 0.05, "domain": 0.0, "subtype": 0.0},
        }
        res = validate_semantic_payload(payload_np)
        self.assertIsNone(res.subtype, "subtype must be None for non_physics, never 'non_physics'")
        self.assertIsNone(res.domain)
        self.assertEqual(res.classification, "non_physics")

        payload_unsupp = {
            "classification": "unsupported_physics",
            "isPhysics": True,
            "subtype": "physics_but_unsupported",
            "confidence": {"isPhysics": 0.95, "domain": 0.0, "subtype": 0.0},
        }
        res2 = validate_semantic_payload(payload_unsupp)
        self.assertIsNone(res2.subtype, "subtype must be None for unsupported_physics")
        self.assertEqual(res2.classification, "unsupported_physics")

    def test_non_physics_clears_domain_and_subtype(self):
        payload = {
            "classification": "non_physics",
            "isPhysics": False,
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {"isPhysics": 0.01, "domain": 0.0, "subtype": 0.0},
        }
        res = validate_semantic_payload(payload)
        self.assertFalse(res.is_physics)
        self.assertIsNone(res.domain)
        self.assertIsNone(res.subtype)
        self.assertFalse(res.is_supported)

    def test_unsupported_physics_clears_domain_and_subtype(self):
        payload = {
            "classification": "unsupported_physics",
            "isPhysics": True,
            "domain": "thermodynamics",
            "subtype": "carnot_engine",
            "confidence": {"isPhysics": 0.99, "domain": 0.85, "subtype": 0.80},
        }
        res = validate_semantic_payload(payload)
        self.assertTrue(res.is_physics)
        self.assertIsNone(res.domain, "unsupported_physics must clear domain to None")
        self.assertIsNone(res.subtype, "unsupported_physics must clear subtype to None")
        self.assertFalse(res.is_supported)

    def test_is_physics_rejects_string_booleans(self):
        """Python bool('false') is True, so strings must be rejected."""
        payload_str_false = {
            "classification": "non_physics",
            "isPhysics": "false",
            "confidence": {"isPhysics": 0.05, "domain": 0.0, "subtype": 0.0},
        }
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload(payload_str_false)

        payload_str_true = {
            "classification": "supported",
            "isPhysics": "true",
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {"isPhysics": 0.95, "domain": 0.9, "subtype": 0.9},
        }
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload(payload_str_true)

    def test_confidence_outside_zero_to_one_rejected(self):
        """Confidence must be between 0.0 and 1.0."""
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload({
                "classification": "supported",
                "isPhysics": True,
                "domain": "mechanics",
                "subtype": "pendulum",
                "confidence": {"isPhysics": 1.5, "domain": 0.9, "subtype": 0.9},
            })

        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload({
                "classification": "supported",
                "isPhysics": True,
                "domain": "mechanics",
                "subtype": "pendulum",
                "confidence": {"isPhysics": -0.2, "domain": 0.9, "subtype": 0.9},
            })

    def test_cross_domain_subtype_mismatch_rejected(self):
        """Subtypes must match their canonical domains (e.g. pendulum is not optics)."""
        mismatched_payloads = [
            {"domain": "optics", "subtype": "pendulum"},
            {"domain": "circuits", "subtype": "thin_lens"},
            {"domain": "mechanics", "subtype": "dc_linear"},
            {"domain": "circuits", "subtype": "projectile"},
        ]
        for p in mismatched_payloads:
            payload = {
                "classification": "supported",
                "isPhysics": True,
                "domain": p["domain"],
                "subtype": p["subtype"],
                "confidence": {"isPhysics": 0.95, "domain": 0.9, "subtype": 0.9},
            }
            with self.assertRaises(SemanticValidationError, msg=f"Should reject {p['domain']}/{p['subtype']}"):
                validate_semantic_payload(payload)

    def test_malformed_classification_rejected(self):
        """Arbitrary strings like 'pendoolum' are not valid classifications."""
        payload = {
            "classification": "pendoolum",
            "isPhysics": True,
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {"isPhysics": 0.9, "domain": 0.9, "subtype": 0.9},
        }
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload(payload)

    def test_duplicate_entity_ids_rejected(self):
        """Temporary entity IDs must be unique."""
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {"isPhysics": 0.95, "domain": 0.9, "subtype": 0.9},
            "entities": [
                {"temporaryId": "e1", "role": "pivot"},
                {"temporaryId": "e1", "role": "bob"},
            ],
        }
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload(payload)

    def test_invalid_relationship_references_rejected(self):
        """Relationship 'from'/'to' must refer to declared entity IDs."""
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {"isPhysics": 0.95, "domain": 0.9, "subtype": 0.9},
            "entities": [
                {"temporaryId": "e1", "role": "pivot"},
            ],
            "relationships": [
                {"type": "connected_to", "from": "e1", "to": "e999"},
            ],
        }
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload(payload)

    def test_missing_confidence_defaults_to_zero_not_certainty(self):
        """Missing confidence on entities/labels must default to 0.0, never 1.0."""
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {"isPhysics": 0.95, "domain": 0.9, "subtype": 0.9},
            "entities": [
                {"temporaryId": "e1", "role": "pivot"},
            ],
            "visibleLabels": [
                {"text": "1.0 m"},
            ],
        }
        res = validate_semantic_payload(payload)
        self.assertEqual(res.entities[0].confidence, 0.0)
        self.assertEqual(res.visible_labels[0].confidence, 0.0)

    def test_overall_confidence_is_strict_hierarchical_min_and_raw_preserved(self):
        """Supported overall confidence must be min(isPhysics, domain, subtype) and rawProvider preserved."""
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {
                "isPhysics": 1.0,
                "domain": 1.0,
                "subtype": 1.0,
                "overall": 1.0,
            },
        }
        res = validate_semantic_payload(payload)
        conf = res.confidence
        # Conservative caps
        self.assertEqual(conf.is_physics, 0.99)
        self.assertEqual(conf.domain, 0.98)
        self.assertEqual(conf.subtype, 0.96)
        # min(0.99, 0.98, 0.96) is strictly 0.96
        self.assertEqual(conf.overall, 0.96)
        # Raw provider preserved untouched
        self.assertIsNotNone(conf.raw_provider)
        self.assertEqual(conf.raw_provider.get("isPhysics"), 1.0)
        self.assertEqual(conf.raw_provider.get("domain"), 1.0)
        self.assertEqual(conf.raw_provider.get("subtype"), 1.0)
        self.assertEqual(conf.raw_provider.get("overall"), 1.0)

    def test_entity_relationship_label_candidate_confidence_capped_below_one(self):
        """VLM sub-object confidences must never assert 1.0 (capped at 0.95)."""
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {"isPhysics": 0.95, "domain": 0.9, "subtype": 0.9},
            "entities": [
                {"temporaryId": "e1", "role": "pivot", "confidence": 1.0},
                {"temporaryId": "e2", "role": "bob", "confidence": 1.0},
            ],
            "relationships": [
                {"type": "connected_to", "from": "e1", "to": "e2", "confidence": 1.0},
            ],
            "visibleLabels": [
                {"text": "L = 1m", "confidence": 1.0},
            ],
            "candidates": [
                {"domain": "mechanics", "subtype": "pendulum", "confidence": 1.0},
            ],
        }
        res = validate_semantic_payload(payload)
        self.assertLess(res.entities[0].confidence, 1.0)
        self.assertEqual(res.entities[0].confidence, 0.95)
        self.assertLess(res.relationships[0].confidence, 1.0)
        self.assertEqual(res.relationships[0].confidence, 0.95)
        self.assertLess(res.visible_labels[0].confidence, 1.0)
        self.assertEqual(res.visible_labels[0].confidence, 0.95)
        self.assertLess(res.candidates[0].confidence, 1.0)
        self.assertEqual(res.candidates[0].confidence, 0.95)

    def test_explicit_boolean_telemetry_fields(self):
        """cacheHit and fallbackUsed must be explicit booleans in serialized dicts."""
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "mechanics",
            "subtype": "pendulum",
            "confidence": {"isPhysics": 0.95, "domain": 0.9, "subtype": 0.9},
            "metadata": {
                "provider": "gemini",
                "model": "gemini-3.1-flash-lite",
                "cacheHit": False,
                "fallbackUsed": True,
                "latencyMs": 1234,
            },
        }
        res = validate_semantic_payload(payload)
        d = res.to_dict()
        meta = d["metadata"]
        self.assertIs(meta["cacheHit"], False)
        self.assertIs(meta["fallbackUsed"], True)
        self.assertEqual(meta["latencyMs"], 1234)


if __name__ == "__main__":
    unittest.main()

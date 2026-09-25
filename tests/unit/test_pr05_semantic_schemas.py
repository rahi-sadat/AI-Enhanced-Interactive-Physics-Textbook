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

    def test_unsupported_physics_clears_subtype(self):
        payload = {
            "classification": "unsupported_physics",
            "isPhysics": True,
            "domain": "thermodynamics",
            "subtype": "carnot_engine",
            "confidence": {"isPhysics": 0.99, "domain": 0.85, "subtype": 0.80},
        }
        res = validate_semantic_payload(payload)
        self.assertTrue(res.is_physics)
        self.assertIsNone(res.subtype)
        self.assertFalse(res.is_supported)

    def test_visible_labels_enforces_unverified(self):
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "optics",
            "subtype": "thin_lens",
            "confidence": {"isPhysics": 0.95, "domain": 0.95, "subtype": 0.90},
            "visibleLabels": [
                {"text": "20 cm", "verified": True},  # Attempt to claim verified
            ],
        }
        res = validate_semantic_payload(payload)
        self.assertEqual(len(res.visible_labels), 1)
        self.assertFalse(res.visible_labels[0].verified, "PR-05 must enforce verified=False")

    def test_entity_validation_requires_role(self):
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "circuits",
            "subtype": "dc_linear",
            "confidence": {"isPhysics": 0.95, "domain": 0.95, "subtype": 0.90},
            "entities": [
                {"temporaryId": "e1"},  # missing role
            ],
        }
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload(payload)

    def test_missing_confidence_rejected(self):
        payload = {
            "classification": "supported",
            "isPhysics": True,
            "domain": "circuits",
            "subtype": "dc_linear",
        }
        with self.assertRaises(SemanticValidationError):
            validate_semantic_payload(payload)


if __name__ == "__main__":
    unittest.main()

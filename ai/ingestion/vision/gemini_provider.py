"""PR-05 Google Gemini Multimodal Vision Provider.

Uses the official google-genai SDK to perform structured semantic analysis on
the actual uploaded image bytes without passing filename or hash hints.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from shared.schemas.ingestion import PageIR
from shared.schemas.semantic import (
    SemanticAnalysisResult,
    SemanticValidationError,
    validate_semantic_payload,
)
from ai.ingestion.vision.provider_interface import (
    VisionProvider,
    VisionProviderError,
    VLMConfigurationError,
)

SYSTEM_PROMPT_PR05_V1 = """You are an expert multimodal physics diagram semantic analyzer.
Your task is to observe the provided textbook image and return a strictly structured JSON analysis.

RULES & CONSTRAINTS:
1. Distinguish between:
   - "supported": Image clearly depicts a physics scenario for which our simulator has a solver:
       Mechanics: "pendulum", "projectile"
       Optics: "thin_lens", "spherical_mirror", "interface_refraction", "prism"
       Circuits: "dc_linear"
   - "unsupported_physics": A physics diagram that is NOT in the supported list (e.g. thermodynamics, wave interference, quantum, nuclear, fluid dynamics, electromagnetism).
       Set: classification="unsupported_physics", isPhysics=true, domain=null, subtype=null.
   - "non_physics": A photograph, cartoon, text-only document, or illustration with no physics scenario (e.g. landscape, animal, person, food).
       Set: classification="non_physics", isPhysics=false, domain=null, subtype=null.
   - "unknown": Ambiguous, noisy, or indeterminate diagram.
       Set: classification="unknown", isPhysics=null, domain=null, subtype=null.

2. SUBTYPE VOCABULARY:
   When classification is "supported", domain must be one of ["mechanics", "optics", "circuits"].
   subtype must be EXACTLY one of:
     ["pendulum", "projectile", "thin_lens", "spherical_mirror", "interface_refraction", "prism", "dc_linear"].
   Do NOT output any other subtype string.

3. ZERO FABRICATED PARAMETERS:
   - Do NOT invent or assume numerical parameters (such as gravity = 9.81 m/s², focal length = 20 cm, resistance = 10 Ω).
   - Only report visible textual/numerical labels in visibleLabels if they are explicitly visible in the image.

4. SEMANTIC OBJECT ROLES:
   - Identify visual components and assign clear roles:
     - For pendulum: "pivot", "bob", "string", "rod", "support_ceiling", "angle_marker", "equilibrium_position", "force_vector", "vertical_reference", "extreme_position".
     - For projectile: "projectile_body", "launch_platform", "trajectory_path", "landing_surface", "velocity_vector", "apex_marker", "angle_marker".
     - For optics: "lens", "optical_axis", "focal_point", "mirror", "optical_center", "object", "image", "light_ray", "interface_boundary", "normal_line", "incident_ray", "refracted_ray", "prism_body".
     - For circuits: "resistor", "voltage_source", "current_source", "wire", "ground", "junction", "switch", "ammeter", "voltmeter".
   - If bounding box coordinates are provided, they are understood to be coarse/approximate.

5. CONFIDENCE CALIBRATION & REALISM:
   - Score confidence conservatively on a realistic scale from 0.0 to 1.0.
   - Reserve 1.0 ONLY for absolute textbook canonical ground truth certainty.
   - Standard clear diagrams typically range from 0.85 to 0.95.
   - Ambiguous, cropped, or hand-drawn diagrams should be 0.50 to 0.80.
   - For unsupported_physics or non_physics, domain and subtype confidence MUST be 0.0.
   - Include an "overall" confidence score in confidence reflecting your aggregate certainty.

6. OUTPUT FORMAT:
   Return ONLY a valid JSON object matching this structure:
{
  "classification": "supported" | "unsupported_physics" | "non_physics" | "unknown",
  "isPhysics": true | false | null,
  "domain": "mechanics" | "optics" | "circuits" | null,
  "subtype": "pendulum" | "projectile" | "thin_lens" | "spherical_mirror" | "interface_refraction" | "prism" | "dc_linear" | null,
  "confidence": {
    "isPhysics": 0.0 to 1.0,
    "domain": 0.0 to 1.0,
    "subtype": 0.0 to 1.0,
    "overall": 0.0 to 1.0
  },
  "entities": [
    {
      "temporaryId": "entity_1",
      "role": "bob",
      "label": "m",
      "confidence": 0.95
    }
  ],
  "relationships": [
    {
      "type": "connected_to",
      "from": "entity_1",
      "to": "entity_2",
      "confidence": 0.90
    }
  ],
  "visibleLabels": [
    {
      "text": "10 kg",
      "confidence": 0.85,
      "semanticRole": "mass_value"
    }
  ],
  "candidates": [],
  "notes": ["short observation"]
}
"""


GEMINI_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "classification": {
            "type": "STRING",
            "enum": ["supported", "unsupported_physics", "non_physics", "unknown"],
        },
        "isPhysics": {
            "type": "BOOLEAN",
        },
        "domain": {
            "type": "STRING",
            "enum": ["mechanics", "optics", "circuits"],
        },
        "subtype": {
            "type": "STRING",
            "enum": [
                "pendulum",
                "projectile",
                "thin_lens",
                "spherical_mirror",
                "interface_refraction",
                "prism",
                "dc_linear",
            ],
        },
        "confidence": {
            "type": "OBJECT",
            "properties": {
                "isPhysics": {"type": "NUMBER"},
                "domain": {"type": "NUMBER"},
                "subtype": {"type": "NUMBER"},
                "overall": {"type": "NUMBER"},
            },
            "required": ["isPhysics", "domain", "subtype"],
        },
        "entities": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "temporaryId": {"type": "STRING"},
                    "role": {"type": "STRING"},
                    "label": {"type": "STRING"},
                    "confidence": {"type": "NUMBER"},
                },
                "required": ["temporaryId", "role"],
            },
        },
        "relationships": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "type": {"type": "STRING"},
                    "from": {"type": "STRING"},
                    "to": {"type": "STRING"},
                    "confidence": {"type": "NUMBER"},
                },
                "required": ["type", "from", "to"],
            },
        },
        "visibleLabels": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "text": {"type": "STRING"},
                    "confidence": {"type": "NUMBER"},
                    "semanticRole": {"type": "STRING"},
                },
                "required": ["text"],
            },
        },
        "candidates": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "domain": {"type": "STRING"},
                    "subtype": {"type": "STRING"},
                    "confidence": {"type": "NUMBER"},
                },
            },
        },
        "notes": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
        },
    },
    "required": ["classification", "confidence"],
}


class GeminiVisionProvider(VisionProvider):
    """Multimodal vision provider implementing Google Gemini via google-genai SDK."""

    PROMPT_VERSION = "pr05-v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = (
            model
            or os.getenv("GEMINI_MODEL")
            or "gemini-3.1-flash-lite"
        )
        self._client = None

    def _get_client(self):
        """Lazily initialize google-genai Client."""
        if not self.api_key:
            raise VLMConfigurationError(
                "GEMINI_API_KEY is not configured. Please add GEMINI_API_KEY to your .env file."
            )
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError as ie:
                raise VLMConfigurationError(
                    f"google-genai package is required for GeminiVisionProvider: {ie}"
                )
            except Exception as e:
                raise VLMConfigurationError(f"Failed to initialize google-genai Client: {e}")
        return self._client

    def analyze_diagram(
        self,
        image_bytes: bytes,
        mime_type: str,
        page_ir: PageIR,
    ) -> SemanticAnalysisResult:
        """Call Gemini multimodal VLM with real image bytes and parse structured JSON."""
        if not image_bytes:
            raise VisionProviderError("Cannot analyze empty image bytes.")

        client = self._get_client()

        try:
            from google.genai import types

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type or "image/png",
            )

            prompt_content = [
                image_part,
                SYSTEM_PROMPT_PR05_V1,
            ]

            import time

            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GEMINI_RESPONSE_SCHEMA,
                temperature=0.1,  # Low temperature for deterministic semantic categorization
            )

            # Model fallback sequence for quota resilience
            models_to_try = [self.model_name]
            for candidate in ["gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-3-flash-preview"]:
                if candidate not in models_to_try:
                    models_to_try.append(candidate)

            response = None
            last_err = None
            used_model = self.model_name

            for current_model in models_to_try:
                for attempt in range(2):
                    try:
                        response = client.models.generate_content(
                            model=current_model,
                            contents=prompt_content,
                            config=config,
                        )
                        used_model = current_model
                        break
                    except Exception as call_err:
                        last_err = call_err
                        err_str = str(call_err)
                        if (
                            "429" in err_str
                            or "RESOURCE_EXHAUSTED" in err_str
                            or "503" in err_str
                            or "404" in err_str
                            or "UNAVAILABLE" in err_str
                        ):
                            time.sleep(1.0)
                            break
                        raise
                if response is not None:
                    break

            if response is None:
                raise VisionProviderError(f"Gemini call failed across models {models_to_try}: {last_err}")

            raw_text = response.text
            if not raw_text or not raw_text.strip():
                raise VisionProviderError("Gemini returned empty response text.")

            # Parse JSON
            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError as je:
                raise VisionProviderError(f"Failed to parse Gemini output as JSON: {je}. Raw output: {raw_text[:200]}")

            # Validate against PR-05 schema
            result = validate_semantic_payload(data)

            # Attach metadata
            result.provider = "gemini"
            result.model = used_model
            result.prompt_version = self.PROMPT_VERSION
            result.timestamp = datetime.now(timezone.utc).isoformat()

            return result

        except (VLMConfigurationError, VisionProviderError):
            raise
        except Exception as e:
            # Map SDK errors to VisionProviderError
            raise VisionProviderError(f"Gemini API request failed: {e}")

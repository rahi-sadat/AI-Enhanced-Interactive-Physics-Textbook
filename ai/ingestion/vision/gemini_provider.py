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
   - Identify visual components and assign clear roles (e.g. "pivot", "bob", "string", "lens", "optical_axis", "mirror", "resistor", "voltage_source", "wire").
   - If bounding box coordinates are provided, they are understood to be coarse/approximate.

5. OUTPUT FORMAT:
   Return ONLY a valid JSON object matching this structure:
{
  "classification": "supported" | "unsupported_physics" | "non_physics" | "unknown",
  "isPhysics": true | false | null,
  "domain": "mechanics" | "optics" | "circuits" | null,
  "subtype": "pendulum" | "projectile" | "thin_lens" | "spherical_mirror" | "interface_refraction" | "prism" | "dc_linear" | null,
  "confidence": {
    "isPhysics": 0.0 to 1.0,
    "domain": 0.0 to 1.0,
    "subtype": 0.0 to 1.0
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
            or "gemini-3.8-flash"
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
                temperature=0.1,  # Low temperature for deterministic semantic categorization
            )

            max_retries = 3
            last_err = None
            response = None
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=prompt_content,
                        config=config,
                    )
                    break
                except Exception as call_err:
                    last_err = call_err
                    err_str = str(call_err)
                    if attempt < max_retries - 1 and ("503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str or "high demand" in err_str):
                        time.sleep(1.5 * (2 ** attempt))
                        continue
                    raise

            if response is None:
                raise VisionProviderError(f"Gemini call failed after retries: {last_err}")

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
            result.model = self.model_name
            result.prompt_version = self.PROMPT_VERSION
            result.timestamp = datetime.now(timezone.utc).isoformat()

            return result

        except (VLMConfigurationError, VisionProviderError):
            raise
        except Exception as e:
            # Map SDK errors to VisionProviderError
            raise VisionProviderError(f"Gemini API request failed: {e}")

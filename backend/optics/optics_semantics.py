"""Semantic binding for optics diagrams.

Bridges raw detected elements + OCR labels into semantic roles and parameter
assignments. Phase 1 uses rule-based heuristics; Phase 4 will add VLM/GPT.

Key principle:  The backend outputs FACTS about the diagram, never rendering
instructions. The frontend decides how to draw rays or style the HUD.
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional

try:
    from .optics_registry import OPTICS_REGISTRY, get_preset
    from .optics_text import DetectedLabel
except ImportError:
    from optics_registry import OPTICS_REGISTRY, get_preset
    from optics_text import DetectedLabel



# ---------------------------------------------------------------------------
# Rule-based semantic binding (Phase 1)
# ---------------------------------------------------------------------------

def bind_elements_rule_based(
    elements: List[dict],
    labels: List[DetectedLabel],
    axis: Optional[dict] = None,
) -> dict:
    """Assign semantic roles to elements using shape heuristics.

    Heuristics for thin-lens diagrams:
      - Tallest vertically-oriented element near horizontal center → lens
      - Tall narrow element far from center → object_arrow
      - Wide flat element → optical bench / axis
      - Triangular element → prism
      - Curved thin element → mirror

    Parameters
    ----------
    elements : List of element dicts (each containing 'geometry.source_px.shape_hints').
    labels : Detected or manually placed text labels.
    axis : Detected optical axis dict, or None.

    Returns
    -------
    dict with:
      - "domain": "optics"
      - "subtype": inferred subtype ("thin_lens", "prism", "mirror", ...)
      - "bindings": list of {"element_id", "semantic_label"} dicts
      - "confidence": overall confidence score
    """
    bindings = []
    lens_candidates = []
    arrow_candidates = []
    prism_candidates = []
    mirror_candidates = []

    for el in elements:
        el_id = el.get("id", "unknown")
        hints = el.get("geometry", {}).get("source_px", {}).get("shape_hints", {})
        bbox = el.get("geometry", {}).get("source_px", {}).get("bbox_px", {})

        aspect = hints.get("aspect_ratio", 1.0)
        circularity = hints.get("circularity", 0.0)
        fill = hints.get("circle_fill_ratio", 0.0)
        rect = hints.get("rectangularity", 0.0)
        width = bbox.get("width", 0)
        height = bbox.get("height", 0)

        # Lens: taller than wide, not too circular, moderate area
        if height > width * 1.5 and circularity < 0.85 and rect < 0.7:
            lens_candidates.append((el_id, height))
        # Arrow: very tall and narrow
        elif height > width * 2.5 and width < 40:
            arrow_candidates.append((el_id, height))
        # Prism: roughly triangular — low rectangularity but not circular
        elif circularity < 0.6 and fill < 0.7 and rect < 0.6 and aspect < 2.0:
            prism_candidates.append((el_id, el))
        # Mirror: thin curved element
        elif aspect > 3.0 and circularity < 0.5 and fill < 0.4:
            mirror_candidates.append((el_id, el))
        else:
            # Can't classify automatically
            bindings.append({
                "element_id": el_id,
                "semantic_label": None,
                "confidence": 0.0,
                "method": "unclassified",
            })

    # Assign the tallest lens candidate
    lens_candidates.sort(key=lambda x: x[1], reverse=True)
    for el_id, _ in lens_candidates[:1]:
        bindings.append({
            "element_id": el_id,
            "semantic_label": "convex_lens",
            "confidence": 0.65,
            "method": "shape_heuristic",
        })
    for el_id, _ in lens_candidates[1:]:
        bindings.append({
            "element_id": el_id,
            "semantic_label": None,
            "confidence": 0.0,
            "method": "unclassified",
        })

    # Assign arrow candidates
    for el_id, _ in arrow_candidates:
        bindings.append({
            "element_id": el_id,
            "semantic_label": "object_arrow",
            "confidence": 0.60,
            "method": "shape_heuristic",
        })

    # Assign prism candidates
    for el_id, _ in prism_candidates:
        bindings.append({
            "element_id": el_id,
            "semantic_label": "prism",
            "confidence": 0.55,
            "method": "shape_heuristic",
        })

    # Assign mirror candidates
    for el_id, _ in mirror_candidates:
        bindings.append({
            "element_id": el_id,
            "semantic_label": "concave_mirror",
            "confidence": 0.50,
            "method": "shape_heuristic",
        })

    # Determine subtype
    has_lens = any(b["semantic_label"] in ("convex_lens", "concave_lens") for b in bindings)
    has_prism = any(b["semantic_label"] == "prism" for b in bindings)
    has_mirror = any(b["semantic_label"] in ("concave_mirror", "convex_mirror", "plane_mirror") for b in bindings)

    if has_lens:
        subtype = "thin_lens"
    elif has_prism:
        subtype = "prism"
    elif has_mirror:
        subtype = "mirror"
    else:
        subtype = "unknown"

    return {
        "domain": "optics",
        "subtype": subtype,
        "bindings": bindings,
        "confidence": sum(b["confidence"] for b in bindings) / max(len(bindings), 1),
    }


# ---------------------------------------------------------------------------
# VLM / GPT prompt generation (Phase 4 stub)
# ---------------------------------------------------------------------------

def prepare_vlm_prompt(
    elements: List[dict],
    ocr_results: List[DetectedLabel],
) -> str:
    """Generate a structured VLM prompt for semantic binding.

    The VLM should return a JSON object like:
    {
      "domain": "optics",
      "subtype": "thin_lens",
      "bindings": [
        {"element_id": "element_001", "semantic_label": "convex_lens"},
        {"element_id": "element_002", "semantic_label": "object_arrow"}
      ],
      "parameters": {
        "focal_length_cm": 20
      }
    }

    This function produces the prompt string — actual API calls are Phase 4.
    """
    element_summaries = []
    for el in elements:
        hints = el.get("geometry", {}).get("source_px", {}).get("shape_hints", {})
        bbox = el.get("geometry", {}).get("source_px", {}).get("bbox_px", {})
        element_summaries.append({
            "id": el.get("id"),
            "shape_hints": hints,
            "bbox": bbox,
            "author_role": el.get("author_role", "unknown"),
        })

    ocr_texts = [lb.to_dict() for lb in ocr_results]

    prompt_data = {
        "task": "optics_semantic_binding",
        "instruction": (
            "You are analyzing an NCTB physics textbook diagram. "
            "Assign each detected element a semantic label from the optics domain: "
            "convex_lens, concave_lens, prism, concave_mirror, convex_mirror, "
            "plane_mirror, object_arrow, light_source, screen, glass_slab. "
            "Also identify the physics domain (optics) and subtype "
            "(thin_lens, prism, mirror). "
            "Extract any physical parameters mentioned in the text (focal length, "
            "refractive index, etc.). "
            "Return ONLY a JSON object — no coordinates, no rendering instructions."
        ),
        "detected_elements": element_summaries,
        "ocr_results": ocr_texts,
        "valid_labels": list(OPTICS_REGISTRY.keys()),
    }

    return json.dumps(prompt_data, indent=2)


def validate_vlm_response(response: dict) -> dict:
    """Validate and sanitise VLM-generated bindings.

    Rules:
    - Reject invented coordinates (VLM may hallucinate positions)
    - Accept only semantic labels from OPTICS_REGISTRY
    - Validate parameter types and ranges
    - Never trust generated pixel coordinates

    Returns
    -------
    Cleaned response dict, or dict with 'error' key if invalid.
    """
    if not isinstance(response, dict):
        return {"error": "Response is not a dict", "original": str(response)}

    domain = response.get("domain", "")
    if domain != "optics":
        return {"error": f"Unexpected domain: {domain}", "original": response}

    valid_subtypes = {"thin_lens", "prism", "mirror", "unknown"}
    subtype = response.get("subtype", "unknown")
    if subtype not in valid_subtypes:
        subtype = "unknown"

    # Validate bindings
    clean_bindings = []
    for binding in response.get("bindings", []):
        label = binding.get("semantic_label")
        if label is not None and label not in OPTICS_REGISTRY:
            label = None  # Reject unknown labels
        clean_bindings.append({
            "element_id": binding.get("element_id"),
            "semantic_label": label,
        })

    # Validate parameters — accept only known numeric keys
    allowed_params = {
        "focal_length_cm", "focal_length_mm",
        "refractive_index", "object_distance_cm",
        "radius_of_curvature_cm", "apex_angle_deg",
    }
    raw_params = response.get("parameters", {})
    clean_params = {}
    for key, value in raw_params.items():
        if key in allowed_params:
            try:
                clean_params[key] = float(value)
            except (TypeError, ValueError):
                pass

    return {
        "domain": "optics",
        "subtype": subtype,
        "bindings": clean_bindings,
        "parameters": clean_params,
        "validated": True,
    }

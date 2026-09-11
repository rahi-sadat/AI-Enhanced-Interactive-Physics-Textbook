"""
experiments/optics/optics_text.py
Optical text and label detection:
- Recognizes labels F, 2F, F1, F2, 2F1, 2F2, O, A, B
- Extracts physical values and units (e.g. '20 cm', 'f = 15 cm', 'μ = 1.52')
- Preserves bounding boxes and coordinates for semantic binding
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple


LABEL_PATTERNS = {
    "2F1": re.compile(r"^(?:2F1|2F_1|2F₁)$", re.IGNORECASE),
    "F1": re.compile(r"^(?:F1|F_1|F₁)$", re.IGNORECASE),
    "2F2": re.compile(r"^(?:2F2|2F_2|2F₂)$", re.IGNORECASE),
    "F2": re.compile(r"^(?:F2|F_2|F₂)$", re.IGNORECASE),
    "F": re.compile(r"^F$", re.IGNORECASE),
    "2F": re.compile(r"^2F$", re.IGNORECASE),
    "O": re.compile(r"^[Oo0]$"),
    "A": re.compile(r"^A$", re.IGNORECASE),
    "B": re.compile(r"^B$", re.IGNORECASE),
}

PHYSICAL_VALUE_PATTERNS = [
    # Focal length: e.g. "f = 20 cm", "f=15cm", "20 cm"
    re.compile(r"(?:f\s*=\s*)?(\d+(?:\.\d+)?)\s*(cm|mm|m)\b", re.IGNORECASE),
    # Refractive index: e.g. "μ = 1.52", "n = 1.5"
    re.compile(r"(?:[μun]\s*=\s*)(\d+(?:\.\d+)?)", re.IGNORECASE),
]


def parse_detected_labels(raw_ocr_items: List[dict]) -> List[dict]:
    """
    Given raw OCR outputs: [{"text": str, "bbox": {"x", "y", "width", "height"}, "confidence": float}]
    Normalizes optical diagram labels (F1, F2, etc.) and computes center coordinates.
    """
    normalized = []
    for item in raw_ocr_items:
        text = item.get("text", "").strip()
        matched_label = None
        for canonical, pat in LABEL_PATTERNS.items():
            if pat.match(text):
                matched_label = canonical
                break

        bbox = item.get("bbox", {"x": 0, "y": 0, "width": 10, "height": 10})
        cx = bbox["x"] + bbox["width"] / 2.0
        cy = bbox["y"] + bbox["height"] / 2.0

        if matched_label:
            normalized.append({
                "raw_text": text,
                "label": matched_label,
                "position": {"x": round(cx, 1), "y": round(cy, 1)},
                "bbox": bbox,
                "confidence": item.get("confidence", 0.95),
            })

    return normalized


def extract_physical_parameters(text_strings: List[str]) -> dict:
    """
    Search list of text strings for physical quantities (focal lengths, refractive indices).
    """
    params = {}
    for text in text_strings:
        # Check focal length
        match_f = PHYSICAL_VALUE_PATTERNS[0].search(text)
        if match_f:
            val = float(match_f.group(1))
            unit = match_f.group(2).lower()
            val_cm = val if unit == "cm" else (val / 10.0 if unit == "mm" else val * 100.0)
            params["focal_length_cm"] = {
                "value": round(val_cm, 2),
                "source": "ocr_text",
                "confidence": 0.96,
                "raw_match": match_f.group(0),
            }

        # Check refractive index
        match_n = PHYSICAL_VALUE_PATTERNS[1].search(text)
        if match_n:
            val_n = float(match_n.group(1))
            params["refractive_index"] = {
                "value": round(val_n, 3),
                "source": "ocr_text",
                "confidence": 0.95,
                "raw_match": match_n.group(0),
            }

    return params

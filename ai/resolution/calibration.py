"""PR-07 Pixel-to-Physical Calibration Engine.

Computes explicit scale calibration (pixels_per_meter) derived exclusively from grounded
pixel geometry and resolved physical values (user input or OCR).
CRITICAL INVARIANTS:
1. Never mutates native source_px coordinates.
2. Never invents an arbitrary default scale (e.g., 100 px/m) without evidence.
3. Records explicit derived provenance linking the reference pixel measurement and physical value.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from shared.schemas.ingestion import ProvenanceRecord
from shared.schemas.resolution import ResolutionSource


@dataclass(frozen=True)
class CalibrationData:
    pixels_per_meter: float
    meters_per_pixel: float
    reference_pixel_span: float
    reference_physical_m: float
    reference_parameter: str
    provenance: ProvenanceRecord

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pixels_per_meter": self.pixels_per_meter,
            "meters_per_pixel": self.meters_per_pixel,
            "reference_pixel_span": self.reference_pixel_span,
            "reference_physical_m": self.reference_physical_m,
            "reference_parameter": self.reference_parameter,
            "provenance": self.provenance.model_dump(),
        }


class CalibrationEngine:
    """Deterministic, zero-fabrication spatial calibration engine."""

    @classmethod
    def derive_calibration(
        cls,
        pixel_span: float,
        physical_span_m: float,
        reference_parameter: str,
        derived_from_refs: Optional[List[str]] = None,
    ) -> Optional[CalibrationData]:
        """Derive pixels_per_meter from explicit geometric pixel distance and physical length.

        Args:
            pixel_span: Measured distance in native source_px (> 0)
            physical_span_m: Resolved physical length in meters (> 0)
            reference_parameter: Name of the resolved parameter (e.g. 'length', 'focal_length')
            derived_from_refs: Evidence or resolution IDs establishing this binding
        """
        if pixel_span is None or physical_span_m is None:
            return None
        if not (math.isfinite(pixel_span) and math.isfinite(physical_span_m)):
            return None
        if pixel_span <= 0.0 or physical_span_m <= 0.0:
            return None

        ppm = pixel_span / physical_span_m
        mpp = physical_span_m / pixel_span

        if not (math.isfinite(ppm) and math.isfinite(mpp)) or ppm <= 0.0:
            return None

        refs = list(derived_from_refs or [])
        prov = ProvenanceRecord(
            source=ResolutionSource.DERIVED_CALIBRATION.value,
            confidence=0.99,
            derived_from=refs,
            notes=f"Derived scale: {ppm:.2f} px/m from {pixel_span:.1f} px = {physical_span_m} m ({reference_parameter})",
        )

        return CalibrationData(
            pixels_per_meter=ppm,
            meters_per_pixel=mpp,
            reference_pixel_span=pixel_span,
            reference_physical_m=physical_span_m,
            reference_parameter=reference_parameter,
            provenance=prov,
        )

    @classmethod
    def derive_for_subtype(
        cls,
        subtype: str,
        entities: List[Any],
        parameters: Dict[str, Any],
        resolutions: Dict[str, Any],
    ) -> Optional[CalibrationData]:
        """Attempt to derive spatial calibration for supported subtypes with grounded lengths."""
        if subtype == "pendulum":
            length_val = parameters.get("length")
            if length_val is None or not (isinstance(length_val, (int, float)) and length_val > 0):
                return None

            # Look for string or bob distance in entities
            string_ent = next(
                (
                    e
                    for e in entities
                    if getattr(e, "type", None) == "string"
                    or getattr(e, "role", None) == "string"
                    or getattr(e, "name", None) == "string"
                ),
                None,
            )
            pixel_span = None
            evidence_refs = []

            if string_ent and hasattr(string_ent, "geometry") and isinstance(string_ent.geometry, dict):
                pixel_span = string_ent.geometry.get("effective_length_px") or string_ent.geometry.get("length_px")
                if hasattr(string_ent, "id"):
                    evidence_refs.append(string_ent.id)

            if pixel_span is None:
                # Try pivot to bob distance
                pivot_ent = next(
                    (
                        e
                        for e in entities
                        if getattr(e, "type", None) == "pivot"
                        or getattr(e, "role", None) == "pivot"
                        or getattr(e, "name", None) == "pivot"
                    ),
                    None,
                )
                bob_ent = next(
                    (
                        e
                        for e in entities
                        if getattr(e, "type", None) == "bob"
                        or getattr(e, "role", None) == "bob"
                        or getattr(e, "name", None) == "bob"
                    ),
                    None,
                )
                if pivot_ent and bob_ent:
                    p_pos = getattr(pivot_ent, "position_source_px", None)
                    b_pos = getattr(bob_ent, "position_source_px", None)
                    if p_pos and b_pos:
                        # Could be list or dict
                        px = p_pos[0] if isinstance(p_pos, (list, tuple)) else p_pos.get("x", 0)
                        py = p_pos[1] if isinstance(p_pos, (list, tuple)) else p_pos.get("y", 0)
                        bx = b_pos[0] if isinstance(b_pos, (list, tuple)) else b_pos.get("x", 0)
                        by = b_pos[1] if isinstance(b_pos, (list, tuple)) else b_pos.get("y", 0)
                        pixel_span = math.hypot(bx - px, by - py)
                        evidence_refs.extend([pivot_ent.id, bob_ent.id])

            if pixel_span and pixel_span > 0:
                length_res = resolutions.get("length")
                if length_res and hasattr(length_res, "id"):
                    evidence_refs.append(length_res.id)
                elif isinstance(length_res, dict) and "id" in length_res:
                    evidence_refs.append(length_res["id"])
                return cls.derive_calibration(pixel_span, float(length_val), "length", evidence_refs)

        # Note: Do NOT derive pixels_per_meter for thin_lens or spherical_mirror from focal_length_px.
        # Physical calibration strictly requires one pixel measurement and one independently grounded
        # physical-length measurement (in meters). In 2D optical ray tracing, focal_length_px is already
        # native source pixels and cannot calibrate spatial scale without an independent physical length.
        return None

"""PR-04 PhysicsCompiler — compiles BookIR → Canonical PR-02 PhysicsScene.

Rules:
  - Only READY_TO_COMPILE BookIRs may become PhysicsScenes.
  - Incomplete understanding → NEEDS_REVIEW (no scene).
  - Unknown domain/subtype → UNRESOLVED (no scene).
  - Known but unsupported physics → UNSUPPORTED (no scene).
  - ZERO FABRICATION: NO default gravity (9.81), NO default bob radius (20.0),
    NO default damping (0.0), NO default calibration (100 px/m), NO default
    aperture (200 px), NO default object height (80 px), NO default normal_x (0.0),
    NO default n1 (1.0), NO default concavity ("concave"), NO default prism apex (60°).
    Every required value must be grounded in BookIR or the compiler returns NEEDS_REVIEW.
  - TARGETS CANONICAL PR-02 PhysicsScene (schemaVersion "1.0", coordinateSpace source_px).
  - Preserves BookIR semantic entity identity and evidence references.
  - Validates physical units strictly (rejects incompatible units like launch_speed in "cm").
  - Passes canonical PhysicsScene validation before status becomes READY.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from shared.schemas.ingestion import (
    BookEntity,
    BookIR,
    BookIRStatus,
    PhysicsCompilerResult,
)

# Supported (domain, subtype) pairs for which a real solver exists.
# Circuit fixture labels (circuit1..4) are strictly removed; only canonical dc_linear is supported.
SUPPORTED_SUBTYPES: Dict[str, set] = {
    "mechanics": {"pendulum", "projectile"},
    "optics": {
        "thin_lens",
        "concave_lens",
        "mirror",
        "spherical_mirror",
        "interface_refraction",
        "prism",
    },
    "circuits": {"dc_linear"},
}

VALID_DOMAINS = {"mechanics", "optics", "circuits"}
VALID_COORDINATE_TYPES = {"source_px", "world", "local"}


# ---------------------------------------------------------------------------
# Strict Unit Validation & Conversion
# ---------------------------------------------------------------------------

VELOCITY_FACTORS_TO_M_S = {
    "m/s": 1.0,
    "mps": 1.0,
    "meter/second": 1.0,
    "meters/second": 1.0,
    "km/h": 1.0 / 3.6,
    "km/hr": 1.0 / 3.6,
    "kph": 1.0 / 3.6,
    "cm/s": 0.01,
}

ACCEL_FACTORS_TO_M_S2 = {
    "m/s²": 1.0,
    "m/s^2": 1.0,
    "m/s2": 1.0,
    "cm/s²": 0.01,
    "cm/s^2": 0.01,
    "cm/s2": 0.01,
}

LENGTH_FACTORS_TO_M = {
    "m": 1.0,
    "meter": 1.0,
    "meters": 1.0,
    "cm": 0.01,
    "centimeter": 0.01,
    "centimeters": 0.01,
    "mm": 0.001,
    "millimeter": 0.001,
    "km": 1000.0,
}

ANGLE_FACTORS_TO_DEG = {
    "deg": 1.0,
    "degree": 1.0,
    "degrees": 1.0,
    "°": 1.0,
    "rad": 180.0 / math.pi,
    "radian": 180.0 / math.pi,
    "radians": 180.0 / math.pi,
}

MASS_FACTORS_TO_KG = {
    "kg": 1.0,
    "kilogram": 1.0,
    "kilograms": 1.0,
    "g": 0.001,
    "gram": 0.001,
    "grams": 0.001,
}

DAMPING_UNITS = {"1/s", "s^-1", "s_inv", "hz", None, ""}
PIXEL_UNITS = {"px", "pixel", "pixels", "source_px", None, ""}


def _extract_val_and_unit(pv: Any) -> Tuple[Any, Optional[str]]:
    """Extract (raw_value, unit_string) from PhysicalValue dict, dataclass, or raw value."""
    if pv is None:
        return None, None
    if isinstance(pv, dict):
        return pv.get("value"), pv.get("unit")
    if hasattr(pv, "value"):
        return getattr(pv, "value"), getattr(pv, "unit", None)
    return pv, None


def _validate_and_convert_unit(
    param_name: str,
    val: Any,
    unit: Optional[str],
    category: str,
) -> Tuple[Optional[float], Optional[Dict[str, str]]]:
    """Validate that unit matches expected physical quantity and convert to canonical unit.

    Returns (converted_value, issue_dict_or_None).
    """
    if val is None:
        return None, {
            "code": f"MISSING_{param_name.upper()}",
            "message": f"Required parameter '{param_name}' is missing or null.",
        }

    try:
        num = float(val)
    except (ValueError, TypeError):
        return None, {
            "code": f"INVALID_{param_name.upper()}_TYPE",
            "message": f"Parameter '{param_name}' must be numeric, got {type(val).__name__}: {val}",
        }

    clean_unit = str(unit).strip().lower() if unit is not None else None
    if clean_unit == "":
        clean_unit = None

    if category == "velocity":
        if clean_unit is None or clean_unit == "m/s":
            return num, None
        factor = VELOCITY_FACTORS_TO_M_S.get(clean_unit)
        if factor is None:
            return None, {
                "code": "INCOMPATIBLE_UNIT",
                "message": (
                    f"Parameter '{param_name}' has unit '{unit}', which is incompatible "
                    f"with velocity (expected 'm/s', 'km/h', 'cm/s')."
                ),
            }
        return num * factor, None

    if category == "acceleration":
        if clean_unit is None or clean_unit in ("m/s²", "m/s^2", "m/s2"):
            return num, None
        factor = ACCEL_FACTORS_TO_M_S2.get(clean_unit)
        if factor is None:
            return None, {
                "code": "INCOMPATIBLE_UNIT",
                "message": (
                    f"Parameter '{param_name}' has unit '{unit}', which is incompatible "
                    f"with acceleration (expected 'm/s²')."
                ),
            }
        return num * factor, None

    if category == "length_m":
        if clean_unit is None or clean_unit in ("m", "meter", "meters"):
            return num, None
        factor = LENGTH_FACTORS_TO_M.get(clean_unit)
        if factor is None:
            return None, {
                "code": "INCOMPATIBLE_UNIT",
                "message": (
                    f"Parameter '{param_name}' has unit '{unit}', which is incompatible "
                    f"with physical length (expected 'm', 'cm', 'mm')."
                ),
            }
        return num * factor, None

    if category == "angle_deg":
        if clean_unit is None or clean_unit in ("deg", "degree", "degrees", "°"):
            return num, None
        factor = ANGLE_FACTORS_TO_DEG.get(clean_unit)
        if factor is None:
            return None, {
                "code": "INCOMPATIBLE_UNIT",
                "message": (
                    f"Parameter '{param_name}' has unit '{unit}', which is incompatible "
                    f"with angle (expected 'deg' or 'rad')."
                ),
            }
        return num * factor, None

    if category == "mass_kg":
        if clean_unit is None or clean_unit in ("kg", "kilogram", "kilograms"):
            return num, None
        factor = MASS_FACTORS_TO_KG.get(clean_unit)
        if factor is None:
            return None, {
                "code": "INCOMPATIBLE_UNIT",
                "message": (
                    f"Parameter '{param_name}' has unit '{unit}', which is incompatible "
                    f"with mass (expected 'kg', 'g')."
                ),
            }
        return num * factor, None

    if category == "pixels":
        if clean_unit in PIXEL_UNITS:
            return num, None
        return None, {
            "code": "INCOMPATIBLE_UNIT",
            "message": (
                f"Parameter '{param_name}' requires pixel units, but received '{unit}'."
            ),
        }

    return num, None


# ---------------------------------------------------------------------------
# Canonical PhysicsScene Validator (matches engine/core/validation.js)
# ---------------------------------------------------------------------------

def validate_canonical_scene(scene: Dict[str, Any]) -> List[Dict[str, str]]:
    """Strictly validate normalized scene dictionary against Canonical PR-02 rules.

    Returns empty list if fully valid, or list of {code, message} issue dicts.
    """
    issues = []
    if not isinstance(scene, dict):
        return [{"code": "SCENE_NULL_OR_INVALID", "message": "Scene must be a non-null dictionary."}]

    # 1. Schema Version
    if scene.get("schemaVersion") != "1.0":
        issues.append({
            "code": "INVALID_SCHEMA_VERSION",
            "message": f"Expected schemaVersion '1.0', received '{scene.get('schemaVersion')}'.",
        })

    # 2. Scene ID
    if not scene.get("id") or not isinstance(scene.get("id"), str):
        issues.append({
            "code": "MISSING_SCENE_ID",
            "message": "Scene must possess a non-empty string identifier (id).",
        })

    # 3. Domain
    domain = scene.get("domain")
    if domain not in VALID_DOMAINS:
        issues.append({
            "code": "UNSUPPORTED_DOMAIN",
            "message": f"Domain must be one of: {sorted(VALID_DOMAINS)}. Got: '{domain}'.",
        })

    # 4. Subtype
    subtype = scene.get("subtype")
    if not subtype or not isinstance(subtype, str) or not subtype.strip():
        issues.append({
            "code": "MISSING_SUBTYPE",
            "message": "Scene must explicitly declare a non-empty subtype string.",
        })

    # 5. Coordinate Space
    cs = scene.get("coordinateSpace")
    if not isinstance(cs, dict):
        issues.append({
            "code": "MISSING_COORDINATE_SPACE",
            "message": "Scene must declare an explicit coordinateSpace dictionary.",
        })
    else:
        cs_type = cs.get("type")
        if cs_type not in VALID_COORDINATE_TYPES:
            issues.append({
                "code": "INVALID_COORDINATE_SPACE_TYPE",
                "message": f"Coordinate space type must be one of: {sorted(VALID_COORDINATE_TYPES)}. Got: '{cs_type}'.",
            })
        elif cs_type in ("source_px", "local"):
            w = cs.get("width")
            h = cs.get("height")
            if not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0:
                issues.append({
                    "code": "INVALID_COORDINATE_DIMENSIONS",
                    "message": f"Coordinate space '{cs_type}' requires a positive finite width. Got: {w}.",
                })
            if not isinstance(h, (int, float)) or not math.isfinite(h) or h <= 0:
                issues.append({
                    "code": "INVALID_COORDINATE_DIMENSIONS",
                    "message": f"Coordinate space '{cs_type}' requires a positive finite height. Got: {h}.",
                })

    # 6. Parameters
    params = scene.get("parameters")
    if not isinstance(params, dict):
        issues.append({
            "code": "MISSING_PARAMETERS_DICTIONARY",
            "message": "Scene must possess a parameters dictionary.",
        })
    else:
        for k, p in params.items():
            if not isinstance(p, dict):
                issues.append({
                    "code": "INVALID_PARAMETER_SPEC",
                    "message": f"Parameter '{k}' must be an object specification.",
                })
            else:
                val = p.get("value")
                if isinstance(val, (int, float)) and not math.isfinite(val):
                    issues.append({
                        "code": "NON_FINITE_PARAMETER_VALUE",
                        "message": f"Known parameter '{k}' contains non-finite value: {val}.",
                    })

    # 7. Objects
    objects = scene.get("objects", [])
    if not isinstance(objects, list):
        issues.append({
            "code": "INVALID_OBJECTS_SPEC",
            "message": "Scene objects must be a list.",
        })
    else:
        obj_ids = set()
        for idx, obj in enumerate(objects):
            if not isinstance(obj, dict):
                continue
            oid = obj.get("id") or f"obj_{idx}"
            if oid in obj_ids:
                issues.append({
                    "code": "DUPLICATE_OBJECT_ID",
                    "message": f"Duplicate object identifier '{oid}'.",
                })
            obj_ids.add(oid)

    # 8. Circuit Domain Validation
    if domain == "circuits":
        circuit = scene.get("circuit")
        if not isinstance(circuit, dict):
            issues.append({
                "code": "MISSING_CIRCUIT_GRAPH",
                "message": "Circuits domain scene must declare an explicit circuit graph.",
            })
        else:
            nodes = circuit.get("nodes", [])
            comps = circuit.get("components", [])
            if not isinstance(nodes, list) or len(nodes) == 0:
                issues.append({
                    "code": "EMPTY_CIRCUIT_NODES",
                    "message": "Circuit graph must contain at least one node.",
                })
            if not isinstance(comps, list) or len(comps) == 0:
                issues.append({
                    "code": "EMPTY_CIRCUIT_COMPONENTS",
                    "message": "Circuit graph must contain at least one component.",
                })

    return issues


# ---------------------------------------------------------------------------
# PhysicsCompiler
# ---------------------------------------------------------------------------

class PhysicsCompiler:
    """Compiles a validated BookIR into a Canonical PR-02 PhysicsScene.

    Strict zero-fabrication: missing parameters or ungrounded sources return NEEDS_REVIEW.
    """

    def compile(self, book_ir: BookIR) -> PhysicsCompilerResult:
        """Attempt to compile BookIR into a runnable Canonical PhysicsScene."""
        # 1. Unknown domain/subtype → UNRESOLVED
        if book_ir.domain is None or book_ir.subtype is None:
            return PhysicsCompilerResult(
                status="UNRESOLVED",
                scene=None,
                issues=[
                    {
                        "code": "DOMAIN_OR_SUBTYPE_UNKNOWN",
                        "message": (
                            "BookIR domain or subtype is None. "
                            "The physics concept has not been identified yet."
                        ),
                    }
                ],
                book_ir_status=book_ir.status,
            )

        domain = book_ir.domain.lower()
        subtype = book_ir.subtype.lower()

        # 2. Known domain but unsupported subtype → UNSUPPORTED
        supported = SUPPORTED_SUBTYPES.get(domain, set())
        if not supported:
            return PhysicsCompilerResult(
                status="UNSUPPORTED",
                scene=None,
                issues=[
                    {
                        "code": "DOMAIN_UNSUPPORTED",
                        "message": f"Domain '{domain}' has no registered solvers.",
                    }
                ],
                book_ir_status=book_ir.status,
            )
        if subtype not in supported:
            return PhysicsCompilerResult(
                status="UNSUPPORTED",
                scene=None,
                issues=[
                    {
                        "code": "SUBTYPE_UNSUPPORTED",
                        "message": (
                            f"Subtype '{subtype}' in domain '{domain}' has no registered solver. "
                            f"Supported: {sorted(supported)}"
                        ),
                    }
                ],
                book_ir_status=book_ir.status,
            )

        # 3. BookIR not ready to compile → NEEDS_REVIEW
        if book_ir.status != BookIRStatus.READY_TO_COMPILE:
            return PhysicsCompilerResult(
                status="NEEDS_REVIEW",
                scene=None,
                issues=[
                    {
                        "code": "BOOK_IR_NOT_READY",
                        "message": (
                            f"BookIR status is '{book_ir.status}'; "
                            "cannot compile without sufficient evidence. "
                            f"Notes: {book_ir.status_notes}"
                        ),
                    }
                ],
                book_ir_status=book_ir.status,
            )

        # 4. Strict Grounding Validation: Image-derived scenes require source asset & figure references
        grounding_issues = self._validate_grounding(book_ir)
        if grounding_issues:
            return PhysicsCompilerResult(
                status="NEEDS_REVIEW",
                scene=None,
                issues=grounding_issues,
                book_ir_status=book_ir.status,
            )

        # 5. Strict Parameter & Units Validation (zero fabrication)
        param_issues = self._validate_parameters(book_ir, domain, subtype)
        if param_issues:
            return PhysicsCompilerResult(
                status="NEEDS_REVIEW",
                scene=None,
                issues=param_issues,
                book_ir_status=book_ir.status,
            )

        # 6. Build Canonical PhysicsScene
        try:
            scene = self._build_canonical_scene(book_ir, domain, subtype)
        except PhysicsCompilerError as e:
            return PhysicsCompilerResult(
                status="NEEDS_REVIEW",
                scene=None,
                issues=[{"code": "COMPILER_ERROR", "message": str(e)}],
                book_ir_status=book_ir.status,
            )

        # 7. Validate canonical scene against Canonical PR-02 Schema Validator
        schema_issues = validate_canonical_scene(scene)
        if schema_issues:
            return PhysicsCompilerResult(
                status="NEEDS_REVIEW",
                scene=None,
                issues=schema_issues,
                book_ir_status=book_ir.status,
            )

        return PhysicsCompilerResult(
            status="READY",
            scene=scene,
            issues=[],
            book_ir_status=book_ir.status,
        )

    # -----------------------------------------------------------------------
    # Grounding & Dimension Extraction
    # -----------------------------------------------------------------------

    def _validate_grounding(self, book_ir: BookIR) -> List[Dict[str, str]]:
        issues = []
        if not book_ir.source_asset_id or not str(book_ir.source_asset_id).strip():
            issues.append({
                "code": "MISSING_SOURCE_GROUNDING",
                "message": "Image-derived scene compilation requires a valid source_asset_id.",
            })
        if not book_ir.figure_id or not str(book_ir.figure_id).strip():
            issues.append({
                "code": "MISSING_FIGURE_GROUNDING",
                "message": "Image-derived scene compilation requires a valid figure_id.",
            })

        w, h = self._extract_source_dimensions(book_ir)
        if w is None or h is None or w <= 0 or h <= 0:
            issues.append({
                "code": "MISSING_COORDINATE_DIMENSIONS",
                "message": (
                    "Image-derived scene compilation requires positive source pixel dimensions "
                    f"(width, height) in geometry or parameters. Got: ({w}, {h})."
                ),
            })
        return issues

    def _extract_source_dimensions(self, book_ir: BookIR) -> Tuple[Optional[float], Optional[float]]:
        geom = book_ir.geometry or {}
        params = book_ir.parameters or {}

        w = (
            geom.get("source_width")
            or geom.get("width")
            or geom.get("sourceWidth")
            or self._extract_raw_val(params.get("source_width"))
            or self._extract_raw_val(params.get("width"))
        )
        h = (
            geom.get("source_height")
            or geom.get("height")
            or geom.get("sourceHeight")
            or self._extract_raw_val(params.get("source_height"))
            or self._extract_raw_val(params.get("height"))
        )

        try:
            w_val = float(w) if w is not None else None
            h_val = float(h) if h is not None else None
            return w_val, h_val
        except (ValueError, TypeError):
            return None, None

    # -----------------------------------------------------------------------
    # Parameter & Unit Validation (Zero Fabrication)
    # -----------------------------------------------------------------------

    def _validate_parameters(
        self,
        book_ir: BookIR,
        domain: str,
        subtype: str,
    ) -> List[Dict[str, str]]:
        issues = []
        params = book_ir.parameters
        geom = book_ir.geometry or {}

        if domain == "mechanics" and subtype == "pendulum":
            # 1. Pivot
            pivot = self._extract_point(params.get("pivot") or geom.get("pivot"))
            if not pivot:
                issues.append({"code": "MISSING_PIVOT", "message": "Pendulum pivot coordinate is required."})

            # 2. Bob Position
            bob_pos = self._extract_point(params.get("bob_position") or geom.get("bob_position") or geom.get("bob_center"))
            if not bob_pos:
                issues.append({"code": "MISSING_BOB_POSITION", "message": "Pendulum bob position coordinate is required."})

            # 3. String Length in Pixels
            val, unit = _extract_val_and_unit(params.get("string_length_px") or geom.get("string_length_px") or geom.get("length_px"))
            l_px, err = _validate_and_convert_unit("string_length_px", val, unit, "pixels")
            if err:
                issues.append(err)
            elif l_px is None or l_px <= 0:
                issues.append({"code": "INVALID_STRING_LENGTH_PX", "message": "String length in pixels must be positive."})

            # 4. Bob Radius in Pixels (STRICT: NO 20.0 DEFAULT)
            r_raw = params.get("bob_radius_px") or geom.get("bob_radius_px") or geom.get("radius_px") or params.get("radius")
            val, unit = _extract_val_and_unit(r_raw)
            if val is None:
                issues.append({"code": "MISSING_BOB_RADIUS_PX", "message": "Pendulum bob radius in pixels is required (cannot fabricate default)."})
            else:
                r_px, err = _validate_and_convert_unit("bob_radius_px", val, unit, "pixels")
                if err:
                    issues.append(err)
                elif r_px is None or r_px <= 0:
                    issues.append({"code": "INVALID_BOB_RADIUS_PX", "message": "Bob radius in pixels must be positive."})

            # 5. Gravity (STRICT: NO 9.81 DEFAULT)
            g_raw = params.get("gravity") or params.get("gravity_m_s2")
            val, unit = _extract_val_and_unit(g_raw)
            if val is None:
                issues.append({"code": "MISSING_GRAVITY", "message": "Gravitational acceleration is required (cannot fabricate default 9.81)."})
            else:
                g_val, err = _validate_and_convert_unit("gravity", val, unit, "acceleration")
                if err:
                    issues.append(err)
                elif g_val is None or g_val < 0:
                    issues.append({"code": "INVALID_GRAVITY", "message": "Gravity must be non-negative."})

            # 6. Physical Length (m) or Mass & Damping
            m_raw = params.get("mass") or params.get("mass_kg")
            val, unit = _extract_val_and_unit(m_raw)
            if val is None:
                issues.append({"code": "MISSING_MASS", "message": "Pendulum mass is required."})
            else:
                m_val, err = _validate_and_convert_unit("mass", val, unit, "mass_kg")
                if err:
                    issues.append(err)
                elif m_val is None or m_val <= 0:
                    issues.append({"code": "INVALID_MASS", "message": "Pendulum mass must be positive."})

            # 7. Damping (STRICT: NO 0.0 DEFAULT ASSUMPTION WITHOUT EVIDENCE)
            d_raw = params.get("damping") or params.get("damping_s_inv")
            val, unit = _extract_val_and_unit(d_raw)
            if val is None:
                issues.append({"code": "MISSING_DAMPING", "message": "Pendulum damping is required."})
            else:
                try:
                    d_val = float(val)
                    if d_val < 0:
                        issues.append({"code": "INVALID_DAMPING", "message": "Damping must be non-negative."})
                except (ValueError, TypeError):
                    issues.append({"code": "INVALID_DAMPING", "message": f"Damping must be numeric, got {val}."})

            # 8. Physical Length (m) or Calibration
            phys_l = params.get("length") or params.get("length_m")
            ppm_raw = params.get("pixels_per_meter") or (book_ir.geometry or {}).get("pixels_per_meter")
            if phys_l is not None:
                val, unit = _extract_val_and_unit(phys_l)
                l_m, err = _validate_and_convert_unit("length", val, unit, "length_m")
                if err:
                    issues.append(err)
            elif ppm_raw is not None:
                val, _ = _extract_val_and_unit(ppm_raw)
                try:
                    if float(val) <= 0:
                        issues.append({"code": "INVALID_CALIBRATION", "message": "pixels_per_meter must be positive."})
                except (ValueError, TypeError):
                    issues.append({"code": "INVALID_CALIBRATION", "message": f"Invalid pixels_per_meter: {val}"})
            else:
                issues.append({
                    "code": "MISSING_PHYSICAL_SCALE",
                    "message": "Pendulum requires physical string length ('length') or calibration ('pixels_per_meter').",
                })

        elif domain == "mechanics" and subtype == "projectile":
            # 1. Launch Position
            launch_pos = self._extract_point(params.get("launch_position") or geom.get("launch_source") or geom.get("launch_source_px"))
            if not launch_pos:
                issues.append({"code": "MISSING_LAUNCH_POSITION", "message": "Launch position is required."})

            # 2. Launch Speed (unit-checked)
            sp_raw = params.get("launch_speed") or params.get("speed")
            val, unit = _extract_val_and_unit(sp_raw)
            if val is None:
                issues.append({"code": "MISSING_LAUNCH_SPEED", "message": "Launch speed is required."})
            else:
                sp_val, err = _validate_and_convert_unit("launch_speed", val, unit, "velocity")
                if err:
                    issues.append(err)
                elif sp_val is None or sp_val < 0:
                    issues.append({"code": "INVALID_LAUNCH_SPEED", "message": "Launch speed must be non-negative."})

            # 3. Launch Angle (unit-checked)
            ang_raw = params.get("launch_angle_deg") or params.get("angle") or params.get("launch_angle")
            val, unit = _extract_val_and_unit(ang_raw)
            if val is None:
                issues.append({"code": "MISSING_LAUNCH_ANGLE", "message": "Launch angle is required."})
            else:
                ang_val, err = _validate_and_convert_unit("launch_angle", val, unit, "angle_deg")
                if err:
                    issues.append(err)

            # 4. Gravity (STRICT: NO 9.81 DEFAULT)
            g_raw = params.get("gravity") or params.get("gravity_m_s2")
            val, unit = _extract_val_and_unit(g_raw)
            if val is None:
                issues.append({"code": "MISSING_GRAVITY", "message": "Gravitational acceleration is required (cannot fabricate default 9.81)."})
            else:
                g_val, err = _validate_and_convert_unit("gravity", val, unit, "acceleration")
                if err:
                    issues.append(err)

            # 5. Calibration PPM (STRICT: NO 100.0 DEFAULT)
            ppm_raw = params.get("pixels_per_meter") or geom.get("pixels_per_meter") or (book_ir.confidence or {}).get("pixels_per_meter")
            val, _ = _extract_val_and_unit(ppm_raw)
            if val is None:
                issues.append({
                    "code": "MISSING_CALIBRATION",
                    "message": "Projectile simulation requires 'pixels_per_meter' calibration (cannot fabricate default 100.0).",
                })
            else:
                try:
                    if float(val) <= 0:
                        issues.append({"code": "INVALID_CALIBRATION", "message": "pixels_per_meter must be positive."})
                except (ValueError, TypeError):
                    issues.append({"code": "INVALID_CALIBRATION", "message": f"Invalid pixels_per_meter: {val}"})

            # 6. Radius
            rad_raw = params.get("ball_radius_px") or geom.get("radius_source_px") or geom.get("radius_px") or params.get("radius")
            val, unit = _extract_val_and_unit(rad_raw)
            if val is None:
                issues.append({"code": "MISSING_RADIUS", "message": "Projectile radius in source pixels is required."})
            else:
                r_val, err = _validate_and_convert_unit("ball_radius_px", val, unit, "pixels")
                if err:
                    issues.append(err)
                elif r_val is None or r_val <= 0:
                    issues.append({"code": "INVALID_RADIUS", "message": "Projectile radius must be positive."})

        elif domain == "optics" and subtype in ("thin_lens", "concave_lens"):
            # 1. Lens Center
            center = self._extract_point(params.get("lens_center") or geom.get("lens_center") or ({"x": geom.get("lensX"), "y": geom.get("axisY")} if "lensX" in geom and "axisY" in geom else None))
            if not center:
                issues.append({"code": "MISSING_LENS_CENTER", "message": "Lens optical center is required."})

            # 2. Focal Length in Pixels
            f_raw = params.get("focal_length_px") or params.get("focalLength")
            val, unit = _extract_val_and_unit(f_raw)
            if val is None:
                issues.append({"code": "MISSING_FOCAL_LENGTH_PX", "message": "Focal length in source pixels is required."})
            else:
                f_val, err = _validate_and_convert_unit("focal_length_px", val, unit, "pixels")
                if err:
                    issues.append(err)
                elif f_val is None or f_val <= 0:
                    issues.append({"code": "INVALID_FOCAL_LENGTH_PX", "message": "Focal length must be positive."})

            # 3. Aperture Height (STRICT: NO 200.0 DEFAULT)
            ap_raw = params.get("aperture_height_px") or geom.get("aperture_height_px") or params.get("aperture")
            val, unit = _extract_val_and_unit(ap_raw)
            if val is None:
                issues.append({"code": "MISSING_APERTURE_HEIGHT_PX", "message": "Aperture height in source pixels is required (cannot fabricate default 200.0)."})
            else:
                ap_val, err = _validate_and_convert_unit("aperture_height_px", val, unit, "pixels")
                if err:
                    issues.append(err)
                elif ap_val is None or ap_val <= 0:
                    issues.append({"code": "INVALID_APERTURE_HEIGHT_PX", "message": "Aperture height must be positive."})

            # 4. If optical object present: require object_height_px (STRICT: NO 80.0 DEFAULT)
            obj_pos = self._extract_point(params.get("object_position") or geom.get("object_position")) or params.get("objectDistance")
            if obj_pos is not None:
                h_raw = params.get("object_height_px") or params.get("objectHeight") or geom.get("object_height_px")
                val, unit = _extract_val_and_unit(h_raw)
                if val is None:
                    issues.append({"code": "MISSING_OBJECT_HEIGHT_PX", "message": "Optical object is present, but object_height_px is missing (cannot fabricate default 80.0)."})
                else:
                    _, err = _validate_and_convert_unit("object_height_px", val, unit, "pixels")
                    if err:
                        issues.append(err)

        elif domain == "optics" and subtype == "interface_refraction":
            # 1. Boundary Y
            val, unit = _extract_val_and_unit(params.get("boundary_y") or geom.get("boundaryY"))
            if val is None:
                issues.append({"code": "MISSING_BOUNDARY_Y", "message": "Boundary y coordinate is required."})

            # 2. Normal X (STRICT: NO 0.0 DEFAULT)
            val, unit = _extract_val_and_unit(params.get("normal_x") or geom.get("normalX"))
            if val is None:
                issues.append({"code": "MISSING_NORMAL_X", "message": "Normal x coordinate is required (cannot fabricate default 0.0)."})

            # 3. Medium 1 Refractive Index (STRICT: NO 1.0 DEFAULT)
            val, _ = _extract_val_and_unit(params.get("n1"))
            if val is None:
                issues.append({"code": "MISSING_N1", "message": "Medium 1 refractive index n1 is required (cannot fabricate default 1.0)."})
            else:
                try:
                    if float(val) <= 0:
                        issues.append({"code": "INVALID_N1", "message": "n1 must be positive."})
                except (ValueError, TypeError):
                    issues.append({"code": "INVALID_N1", "message": f"n1 must be numeric, got {val}."})

            # 4. Medium 2 Refractive Index
            val, _ = _extract_val_and_unit(params.get("n2"))
            if val is None:
                issues.append({"code": "MISSING_N2", "message": "Medium 2 refractive index n2 is required."})
            else:
                try:
                    if float(val) <= 0:
                        issues.append({"code": "INVALID_N2", "message": "n2 must be positive."})
                except (ValueError, TypeError):
                    issues.append({"code": "INVALID_N2", "message": f"n2 must be numeric, got {val}."})

            # 5. Incident Ray Source
            src_pos = self._extract_point(params.get("source_position") or geom.get("sourcePosition"))
            theta1 = params.get("theta1")
            if src_pos is None and theta1 is None:
                issues.append({
                    "code": "MISSING_INCIDENT_RAY",
                    "message": "Refraction simulation requires source_position or incident angle theta1.",
                })

        elif domain == "optics" and subtype in ("mirror", "spherical_mirror"):
            # 1. Pole
            pole = self._extract_point(params.get("pole") or geom.get("pole") or geom.get("mirror_center"))
            if not pole:
                issues.append({"code": "MISSING_MIRROR_POLE", "message": "Mirror pole position is required."})

            # 2. Focal Length
            val, unit = _extract_val_and_unit(params.get("focal_length_px") or params.get("focalLength"))
            if val is None:
                issues.append({"code": "MISSING_FOCAL_LENGTH_PX", "message": "Mirror focal length is required."})
            else:
                f_val, err = _validate_and_convert_unit("focal_length_px", val, unit, "pixels")
                if err:
                    issues.append(err)

            # 3. Concavity (STRICT: NO "concave" DEFAULT)
            concavity = self._extract_raw_val(params.get("concavity") or params.get("mirror_type") or geom.get("mirrorType"))
            if not concavity or str(concavity).lower() not in ("concave", "convex", "plane"):
                issues.append({
                    "code": "MISSING_MIRROR_CONCAVITY",
                    "message": "Mirror concavity ('concave', 'convex', 'plane') is required (cannot fabricate default 'concave').",
                })

            # 4. Aperture Height (STRICT: NO 200.0 DEFAULT)
            ap_raw = params.get("aperture_height_px") or geom.get("aperture_height_px")
            val, unit = _extract_val_and_unit(ap_raw)
            if val is None:
                issues.append({"code": "MISSING_APERTURE_HEIGHT_PX", "message": "Mirror aperture height in pixels is required."})
            else:
                _, err = _validate_and_convert_unit("aperture_height_px", val, unit, "pixels")
                if err:
                    issues.append(err)

        elif domain == "optics" and subtype == "prism":
            # 1. Vertices
            v_raw = self._extract_raw_val(params.get("vertices") or geom.get("prismVertices") or geom.get("vertices"))
            if not isinstance(v_raw, list) or len(v_raw) < 3:
                issues.append({"code": "MISSING_PRISM_VERTICES", "message": "Prism vertices array of at least 3 points is required."})

            # 2. Refractive Index n
            n_raw = self._extract_raw_val(params.get("n") or params.get("refractiveIndex"))
            if n_raw is None:
                issues.append({"code": "MISSING_PRISM_REFRACTIVE_INDEX", "message": "Prism refractive index is required."})
            else:
                try:
                    if float(n_raw) <= 0:
                        issues.append({"code": "INVALID_PRISM_REFRACTIVE_INDEX", "message": "Prism refractive index must be positive."})
                except (ValueError, TypeError):
                    issues.append({"code": "INVALID_PRISM_REFRACTIVE_INDEX", "message": f"Refractive index must be numeric: {n_raw}"})

            # 3. Apex Angle (STRICT: NO 60.0 DEFAULT)
            apex_raw = params.get("apex_angle_deg") or geom.get("apex_angle_deg")
            val, unit = _extract_val_and_unit(apex_raw)
            if val is None:
                issues.append({
                    "code": "MISSING_APEX_ANGLE_DEG",
                    "message": "Prism apex angle is required (cannot fabricate default 60.0°).",
                })
            else:
                _, err = _validate_and_convert_unit("apex_angle_deg", val, unit, "angle_deg")
                if err:
                    issues.append(err)

            # 4. Ray Origin & Direction
            ray_org = self._extract_point(geom.get("rayOrigin") or params.get("ray_origin"))
            ray_dir = self._extract_point(geom.get("rayDirection") or params.get("ray_direction"))
            if not ray_org or not ray_dir:
                issues.append({"code": "MISSING_PRISM_INCIDENT_RAY", "message": "Prism simulation requires rayOrigin and rayDirection."})

        elif domain == "circuits" and subtype == "dc_linear":
            comps = self._extract_raw_val(params.get("components"))
            nodes = self._extract_raw_val(params.get("nodes"))
            if not isinstance(comps, list) or len(comps) == 0:
                issues.append({"code": "MISSING_CIRCUIT_COMPONENTS", "message": "At least one circuit component is required."})
            if not isinstance(nodes, list) or len(nodes) == 0:
                issues.append({"code": "MISSING_CIRCUIT_NODES", "message": "Circuit node topology is required."})

        return issues

    # -----------------------------------------------------------------------
    # Canonical Scene Builder (PR-02 Contract)
    # -----------------------------------------------------------------------

    def _build_canonical_scene(
        self,
        book_ir: BookIR,
        domain: str,
        subtype: str,
    ) -> Dict[str, Any]:
        """Build Canonical PR-02 PhysicsScene dictionary."""
        w, h = self._extract_source_dimensions(book_ir)
        scene_id = f"PHY-{domain[:4].upper()}-{book_ir.figure_id or 'INGESTED'}"

        # Base Canonical Scene Contract
        scene: Dict[str, Any] = {
            "schemaVersion": "1.0",
            "id": scene_id,
            "domain": domain,
            "subtype": subtype,
            "source": {
                "type": "book_figure",
                "source_asset_id": book_ir.source_asset_id,
                "figure_id": book_ir.figure_id,
                "width": w,
                "height": h,
            },
            "coordinateSpace": {
                "type": "source_px",
                "width": w,
                "height": h,
                "unit": "px",
            },
            "parameters": {},
            "geometry": dict(book_ir.geometry or {}),
            "objects": [],
            "render": {"coordinate_space": "source_px"},
        }

        # Delegate to domain-specific builders
        if domain == "mechanics" and subtype == "pendulum":
            self._populate_canonical_pendulum(scene, book_ir)
        elif domain == "mechanics" and subtype == "projectile":
            self._populate_canonical_projectile(scene, book_ir)
        elif domain == "optics" and subtype in ("thin_lens", "concave_lens"):
            self._populate_canonical_lens(scene, book_ir, subtype)
            scene["elements"] = scene["objects"]
        elif domain == "optics" and subtype == "interface_refraction":
            self._populate_canonical_refraction(scene, book_ir)
            scene["elements"] = scene["objects"]
        elif domain == "optics" and subtype in ("mirror", "spherical_mirror"):
            self._populate_canonical_mirror(scene, book_ir)
            scene["elements"] = scene["objects"]
        elif domain == "optics" and subtype == "prism":
            self._populate_canonical_prism(scene, book_ir)
            scene["elements"] = scene["objects"]
        elif domain == "circuits" and subtype == "dc_linear":
            self._populate_canonical_circuits(scene, book_ir)
        else:
            raise PhysicsCompilerError(f"No canonical builder for {domain}/{subtype}")

        return scene

    # -----------------------------------------------------------------------
    # Domain Scene Population Helpers (Preserving Entity Identity & Evidence)
    # -----------------------------------------------------------------------

    def _find_entity(self, book_ir: BookIR, allowed_types: Tuple[str, ...]) -> Optional[BookEntity]:
        for entity in book_ir.entities:
            if entity.type and entity.type.lower() in allowed_types:
                return entity
        return None

    def _populate_canonical_pendulum(self, scene: Dict[str, Any], book_ir: BookIR):
        params = book_ir.parameters
        geom = book_ir.geometry or {}

        pivot = self._extract_point(params.get("pivot") or geom.get("pivot"))
        bob_pos = self._extract_point(params.get("bob_position") or geom.get("bob_position") or geom.get("bob_center"))
        string_len = float(self._extract_raw_val(params.get("string_length_px") or geom.get("string_length_px") or geom.get("length_px")))
        bob_r = float(self._extract_raw_val(params.get("bob_radius_px") or geom.get("bob_radius_px") or geom.get("radius_px") or params.get("radius")))

        g_raw = params.get("gravity") or params.get("gravity_m_s2")
        g_val, _ = _validate_and_convert_unit("gravity", *(_extract_val_and_unit(g_raw)), category="acceleration")

        # Physical length (m)
        phys_l = params.get("length") or params.get("length_m")
        if phys_l is not None:
            l_m, _ = _validate_and_convert_unit("length", *(_extract_val_and_unit(phys_l)), category="length_m")
        else:
            ppm = float(self._extract_raw_val(params.get("pixels_per_meter") or geom.get("pixels_per_meter")))
            l_m = string_len / ppm

        m_raw = params.get("mass") or params.get("mass_kg")
        m_val, _ = _validate_and_convert_unit("mass", *(_extract_val_and_unit(m_raw)), category="mass_kg")

        d_raw = params.get("damping") or params.get("damping_s_inv")
        d_val = float(self._extract_raw_val(d_raw))

        # Initial Angle: explicit or geometric from pivot → bob
        ang_raw = params.get("initialAngle") or params.get("initial_angle") or params.get("angle")
        if ang_raw is not None:
            ang_deg, _ = _validate_and_convert_unit("initialAngle", *(_extract_val_and_unit(ang_raw)), category="angle_deg")
            theta0_rad = ang_deg * math.pi / 180.0
        else:
            dx = bob_pos["x"] - pivot["x"]
            dy = bob_pos["y"] - pivot["y"]
            theta0_rad = math.atan2(dx, dy)
            ang_deg = theta0_rad * 180.0 / math.pi

        # Preserve entity identity
        entity = self._find_entity(book_ir, ("pendulum", "bob", "pendulum_system", "pendulum_bob"))
        obj_id = entity.id if entity else "pendulum_bob_1"

        scene["parameters"] = {
            "length": {"value": l_m, "unit": "m", "provenance": "observed"},
            "gravity": {"value": g_val, "unit": "m/s²", "provenance": "assumed"},
            "initialAngle": {"value": ang_deg, "unit": "°", "provenance": "observed"},
            "mass": {"value": m_val, "unit": "kg", "provenance": "assumed"},
            "damping": {"value": d_val, "unit": "1/s", "provenance": "assumed"},
        }
        scene["geometry"].update({
            "pivot": pivot,
            "bob_center": bob_pos,
            "string_length_px": string_len,
            "length_px": string_len,
            "bob_radius_px": bob_r,
        })
        scene["environment"] = {
            "gravity": g_val,
            "gravity_m_s2": g_val,
        }
        scene["objects"] = [
            {
                "id": obj_id,
                "type": "pendulum",
                "role": "dynamic",
                "label": entity.label if entity else "Pendulum",
                "evidence_refs": entity.evidence_refs if entity else [],
                "geometry": {
                    "pivot": pivot,
                    "string_length_px": string_len,
                    "length_px": string_len,
                    "bob_radius_px": bob_r,
                },
                "physics": {
                    "length_m": l_m,
                    "mass_kg": m_val,
                    "damping_s_inv": d_val,
                    "theta0_rad": theta0_rad,
                    "omega0_rad_s": 0.0,
                },
            }
        ]

    def _populate_canonical_projectile(self, scene: Dict[str, Any], book_ir: BookIR):
        params = book_ir.parameters
        geom = book_ir.geometry or {}

        launch_pos = self._extract_point(params.get("launch_position") or geom.get("launch_source") or geom.get("launch_source_px"))
        sp_val, _ = _validate_and_convert_unit("launch_speed", *(_extract_val_and_unit(params.get("launch_speed") or params.get("speed"))), category="velocity")
        ang_val, _ = _validate_and_convert_unit("launch_angle", *(_extract_val_and_unit(params.get("launch_angle_deg") or params.get("angle") or params.get("launch_angle"))), category="angle_deg")
        g_val, _ = _validate_and_convert_unit("gravity", *(_extract_val_and_unit(params.get("gravity") or params.get("gravity_m_s2"))), category="acceleration")
        ppm_val = float(self._extract_raw_val(params.get("pixels_per_meter") or geom.get("pixels_per_meter")))
        r_val = float(self._extract_raw_val(params.get("ball_radius_px") or geom.get("radius_source_px") or geom.get("radius_px") or params.get("radius")))

        entity = self._find_entity(book_ir, ("projectile", "ball", "projectile_ball", "circle"))
        obj_id = entity.id if entity else "projectile_ball_1"

        scene["parameters"] = {
            "speed": {"value": sp_val, "unit": "m/s", "provenance": "observed"},
            "angle": {"value": ang_val, "unit": "°", "provenance": "observed"},
            "gravity": {"value": g_val, "unit": "m/s²", "provenance": "assumed"},
        }
        scene["calibration"] = {
            "pixels_per_meter": ppm_val,
        }
        scene["geometry"].update({
            "launch_source": launch_pos,
            "launch_source_px": launch_pos,
        })
        scene["environment"] = {
            "gravity": g_val,
            "gravity_m_s2": g_val,
        }
        scene["objects"] = [
            {
                "id": obj_id,
                "type": "projectile",
                "role": "projectile",
                "label": entity.label if entity else "Projectile Ball",
                "evidence_refs": entity.evidence_refs if entity else [],
                "geometry": {
                    "launch_source_px": launch_pos,
                    "radius_source_px": r_val,
                },
                "physics": {
                    "speed_m_s": sp_val,
                    "launch_angle_deg": ang_val,
                },
            }
        ]

    def _populate_canonical_lens(self, scene: Dict[str, Any], book_ir: BookIR, subtype: str):
        params = book_ir.parameters
        geom = book_ir.geometry or {}

        center = self._extract_point(params.get("lens_center") or geom.get("lens_center") or ({"x": geom.get("lensX"), "y": geom.get("axisY")} if "lensX" in geom and "axisY" in geom else None))
        focal_px = float(self._extract_raw_val(params.get("focal_length_px") or params.get("focalLength")))
        aperture = float(self._extract_raw_val(params.get("aperture_height_px") or geom.get("aperture_height_px") or params.get("aperture")))

        obj_pos = self._extract_point(params.get("object_position") or geom.get("object_position"))
        obj_dist_raw = params.get("objectDistance")

        lens_entity = self._find_entity(book_ir, ("lens", "thin_lens", "convex_lens", "concave_lens"))
        lens_id = lens_entity.id if lens_entity else "lens_1"

        scene["parameters"] = {
            "focalLength": {"value": focal_px, "unit": "px", "provenance": "observed"},
        }
        scene["geometry"].update({
            "lensX": center["x"],
            "axisY": center["y"],
            "aperture_height_px": aperture,
        })

        objects = [
            {
                "id": lens_id,
                "type": "thin_lens",
                "role": "lens",
                "label": lens_entity.label if lens_entity else "Thin Lens",
                "evidence_refs": lens_entity.evidence_refs if lens_entity else [],
                "optics": {
                    "model": "thin_lens",
                    "subtype": subtype,
                    "center": center,
                    "aperture_height_px": aperture,
                    "focal_length_px": {"value": focal_px, "unit": "px"},
                },
            }
        ]

        # Handle object arrow if present
        if obj_pos is not None or obj_dist_raw is not None:
            obj_h = float(self._extract_raw_val(params.get("object_height_px") or params.get("objectHeight") or geom.get("object_height_px")))
            if obj_pos is None and obj_dist_raw is not None:
                u_px = float(self._extract_raw_val(obj_dist_raw))
                obj_pos = {"x": center["x"] - u_px, "y": center["y"]}
            else:
                u_px = abs(center["x"] - obj_pos["x"])

            obj_entity = self._find_entity(book_ir, ("object", "optical_object", "arrow", "object_arrow"))
            obj_id = obj_entity.id if obj_entity else "object_arrow_1"

            scene["parameters"]["objectDistance"] = {"value": u_px, "unit": "px", "provenance": "observed"}
            scene["parameters"]["objectHeight"] = {"value": -abs(obj_h), "unit": "px", "provenance": "observed"}

            objects.insert(0, {
                "id": obj_id,
                "type": "optical_object",
                "role": "object",
                "label": obj_entity.label if obj_entity else "Optical Object",
                "evidence_refs": obj_entity.evidence_refs if obj_entity else [],
                "optics": {
                    "model": "optical_object",
                    "base": obj_pos,
                    "tip": {"x": obj_pos["x"], "y": obj_pos["y"] - obj_h},
                    "height_px": obj_h,
                },
            })

        scene["objects"] = objects

    def _populate_canonical_refraction(self, scene: Dict[str, Any], book_ir: BookIR):
        params = book_ir.parameters
        geom = book_ir.geometry or {}

        bound_y = float(self._extract_raw_val(params.get("boundary_y") or geom.get("boundaryY")))
        normal_x = float(self._extract_raw_val(params.get("normal_x") or geom.get("normalX")))
        n1 = float(self._extract_raw_val(params.get("n1")))
        n2 = float(self._extract_raw_val(params.get("n2")))

        src_pos = self._extract_point(params.get("source_position") or geom.get("sourcePosition"))
        theta1_raw = params.get("theta1")

        boundary_entity = self._find_entity(book_ir, ("interface_boundary", "boundary", "interface"))
        bound_id = boundary_entity.id if boundary_entity else "element_boundary"

        scene["parameters"] = {
            "n1": {"value": n1, "unit": "", "provenance": "observed"},
            "n2": {"value": n2, "unit": "", "provenance": "observed"},
        }
        if theta1_raw is not None:
            scene["parameters"]["theta1"] = {"value": float(self._extract_raw_val(theta1_raw)), "unit": "deg", "provenance": "observed"}

        scene["geometry"].update({
            "boundaryY": bound_y,
            "normalX": normal_x,
        })

        objects = [
            {
                "id": bound_id,
                "type": "interface_boundary",
                "role": "fixed",
                "label": boundary_entity.label if boundary_entity else "Medium Boundary",
                "evidence_refs": boundary_entity.evidence_refs if boundary_entity else [],
                "optics": {
                    "model": "interface_boundary",
                    "boundaryY": bound_y,
                    "normalX": normal_x,
                    "medium1": {"name": "Medium 1", "n": n1},
                    "medium2": {"name": "Medium 2", "n": n2},
                },
            }
        ]

        if src_pos:
            ray_entity = self._find_entity(book_ir, ("ray_source", "light_source", "source"))
            ray_id = ray_entity.id if ray_entity else "element_light_source"
            objects.append({
                "id": ray_id,
                "type": "ray_source",
                "role": "dynamic",
                "label": ray_entity.label if ray_entity else "Incident Ray Source",
                "evidence_refs": ray_entity.evidence_refs if ray_entity else [],
                "optics": {
                    "model": "ray_source",
                    "position": src_pos,
                    "target": {"x": normal_x, "y": bound_y},
                },
            })

        scene["objects"] = objects

    def _populate_canonical_mirror(self, scene: Dict[str, Any], book_ir: BookIR):
        params = book_ir.parameters
        geom = book_ir.geometry or {}

        pole = self._extract_point(params.get("pole") or geom.get("pole") or geom.get("mirror_center"))
        focal_px = float(self._extract_raw_val(params.get("focal_length_px") or params.get("focalLength")))
        concavity = str(self._extract_raw_val(params.get("concavity") or params.get("mirror_type") or geom.get("mirrorType"))).lower()
        aperture = float(self._extract_raw_val(params.get("aperture_height_px") or geom.get("aperture_height_px")))

        mirror_entity = self._find_entity(book_ir, ("mirror", "spherical_mirror", "concave_mirror", "convex_mirror"))
        mirror_id = mirror_entity.id if mirror_entity else "element_mirror"

        scene["parameters"] = {
            "focalLength": {"value": focal_px, "unit": "px", "provenance": "observed"},
            "mirrorType": {"value": concavity, "unit": "", "provenance": "observed"},
        }
        scene["geometry"].update({
            "mirrorX": pole["x"],
            "axisY": pole["y"],
            "mirrorType": concavity,
            "aperture_height_px": aperture,
        })
        scene["objects"] = [
            {
                "id": mirror_id,
                "type": "mirror",
                "role": "fixed",
                "label": mirror_entity.label if mirror_entity else f"{concavity.title()} Mirror",
                "evidence_refs": mirror_entity.evidence_refs if mirror_entity else [],
                "optics": {
                    "model": "mirror",
                    "mirrorType": concavity,
                    "center": pole,
                    "focal_length_px": {"value": focal_px, "unit": "px"},
                    "aperture_height_px": aperture,
                },
            }
        ]

    def _populate_canonical_prism(self, scene: Dict[str, Any], book_ir: BookIR):
        params = book_ir.parameters
        geom = book_ir.geometry or {}

        v_raw = self._extract_raw_val(params.get("vertices") or geom.get("prismVertices") or geom.get("vertices"))
        n = float(self._extract_raw_val(params.get("n") or params.get("refractiveIndex")))
        apex_angle = float(self._extract_raw_val(params.get("apex_angle_deg") or geom.get("apex_angle_deg")))
        ray_org = self._extract_point(geom.get("rayOrigin") or params.get("ray_origin"))
        ray_dir = self._extract_point(geom.get("rayDirection") or params.get("ray_direction"))

        prism_entity = self._find_entity(book_ir, ("prism", "triangular_prism"))
        prism_id = prism_entity.id if prism_entity else "element_prism"

        scene["parameters"] = {
            "refractiveIndex": {"value": n, "unit": "", "provenance": "observed"},
            "apexAngle": {"value": apex_angle, "unit": "deg", "provenance": "observed"},
        }
        scene["geometry"].update({
            "prismVertices": v_raw,
            "rayOrigin": ray_org,
            "rayDirection": ray_dir,
            "apex_angle_deg": apex_angle,
        })
        scene["objects"] = [
            {
                "id": prism_id,
                "type": "prism",
                "role": "fixed",
                "label": prism_entity.label if prism_entity else "Optical Prism",
                "evidence_refs": prism_entity.evidence_refs if prism_entity else [],
                "optics": {
                    "model": "prism",
                    "vertices": v_raw,
                    "refractiveIndex": n,
                    "apex_angle_deg": apex_angle,
                },
            },
            {
                "id": "element_ray_source",
                "type": "ray_source",
                "role": "dynamic",
                "optics": {
                    "model": "ray_source",
                    "position": ray_org,
                    "direction": ray_dir,
                },
            },
        ]

    def _populate_canonical_circuits(self, scene: Dict[str, Any], book_ir: BookIR):
        params = book_ir.parameters
        components = self._extract_raw_val(params.get("components"))
        nodes = self._extract_raw_val(params.get("nodes"))
        wires = self._extract_raw_val(params.get("wires") or [])
        ref_node = self._extract_raw_val(params.get("reference_node")) or (nodes[0] if isinstance(nodes[0], str) else nodes[0].get("id"))

        scene["circuit"] = {
            "reference_node": ref_node,
            "nodes": nodes,
            "components": components,
            "wires": wires,
        }

        # Populate canonical parameters for circuit components
        for comp in components:
            cid = comp.get("id")
            cval = comp.get("value")
            cunit = comp.get("unit")
            if cid and cval is not None:
                scene["parameters"][cid] = {
                    "value": cval,
                    "unit": cunit or "",
                    "provenance": "observed",
                }

    # -----------------------------------------------------------------------
    # Value extraction utilities
    # -----------------------------------------------------------------------

    @staticmethod
    def _extract_raw_val(pv: Any) -> Any:
        if pv is None:
            return None
        if isinstance(pv, dict):
            return pv.get("value")
        if hasattr(pv, "value"):
            return getattr(pv, "value")
        return pv

    @staticmethod
    def _extract_point(pv: Any) -> Optional[Dict[str, float]]:
        val = PhysicsCompiler._extract_raw_val(pv)
        if isinstance(val, dict) and "x" in val and "y" in val:
            try:
                return {"x": float(val["x"]), "y": float(val["y"])}
            except (ValueError, TypeError):
                return None
        return None


class PhysicsCompilerError(RuntimeError):
    """Raised when scene construction encounters an irrecoverable inconsistency."""
    pass

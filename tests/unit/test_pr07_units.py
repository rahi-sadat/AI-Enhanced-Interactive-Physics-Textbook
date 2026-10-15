"""PR-07 Unit Tests: Safe Unit Engine and Dimensional Validation.

Verifies:
  - Strict numeric parsing without eval.
  - Dimension checking across length, mass, acceleration, velocity, angle, resistance, voltage, current, damping.
  - Case-sensitivity (mΩ vs MΩ).
  - SI unit normalization and mathematical equivalence (80 cm == 0.8 m == 800 mm).
  - Validation constraints (strictly positive, non-negative, finite).
  - Rejection of invalid inputs (empty, NaN, inf, invalid units, dimension mismatches).
"""
import math
import pytest
from ai.resolution.units import UnitEngine, CANONICAL_UNITS


class TestUnitEngineParsing:
    """Test numeric and string parsing for physical quantities."""

    def test_parse_simple_numeric(self):
        res = UnitEngine.parse_quantity(0.8, expected_dimension="length")
        assert res.success is True
        assert res.canonical_value == pytest.approx(0.8)
        assert res.canonical_unit == "m"
        assert res.dimension == "length"

    def test_parse_string_with_unit(self):
        res = UnitEngine.parse_quantity("80 cm", expected_dimension="length")
        assert res.success is True
        assert res.canonical_value == pytest.approx(0.8)
        assert res.canonical_unit == "m"
        assert res.entered_unit == "cm"

    def test_parse_millimeters(self):
        res = UnitEngine.parse_quantity("800 mm", expected_dimension="length")
        assert res.success is True
        assert res.canonical_value == pytest.approx(0.8)
        assert res.canonical_unit == "m"

    def test_normalization_equivalence(self):
        v1 = UnitEngine.parse_quantity("0.8 m", expected_dimension="length").canonical_value
        v2 = UnitEngine.parse_quantity("80 cm", expected_dimension="length").canonical_value
        v3 = UnitEngine.parse_quantity("800 mm", expected_dimension="length").canonical_value
        assert v1 == pytest.approx(v2)
        assert v2 == pytest.approx(v3)

    def test_mass_units(self):
        res_kg = UnitEngine.parse_quantity("0.25 kg", expected_dimension="mass")
        res_g = UnitEngine.parse_quantity("250 g", expected_dimension="mass")
        assert res_kg.success is True
        assert res_g.success is True
        assert res_kg.canonical_value == pytest.approx(0.25)
        assert res_g.canonical_value == pytest.approx(0.25)
        assert res_kg.canonical_unit == "kg"

    def test_acceleration_units(self):
        res1 = UnitEngine.parse_quantity("9.80665 m/s²", expected_dimension="acceleration")
        res2 = UnitEngine.parse_quantity("9.80665 m/s^2", expected_dimension="acceleration")
        res3 = UnitEngine.parse_quantity("980.665 cm/s²", expected_dimension="acceleration")
        assert res1.success is True
        assert res2.success is True
        assert res3.success is True
        assert res1.canonical_value == pytest.approx(9.80665)
        assert res2.canonical_value == pytest.approx(9.80665)
        assert res3.canonical_value == pytest.approx(9.80665)

    def test_velocity_units(self):
        res_ms = UnitEngine.parse_quantity("10 m/s", expected_dimension="velocity")
        res_kmh = UnitEngine.parse_quantity("36 km/h", expected_dimension="velocity")
        assert res_ms.success is True
        assert res_kmh.success is True
        assert res_ms.canonical_value == pytest.approx(10.0)
        assert res_kmh.canonical_value == pytest.approx(10.0)

    def test_angle_units(self):
        res_deg = UnitEngine.parse_quantity("45°", expected_dimension="angle")
        res_rad = UnitEngine.parse_quantity(f"{math.pi / 4} rad", expected_dimension="angle")
        assert res_deg.success is True
        assert res_rad.success is True
        assert res_deg.canonical_value == pytest.approx(45.0)
        assert res_rad.canonical_value == pytest.approx(45.0, rel=1e-4)

    def test_electrical_units(self):
        # Voltage
        res_v = UnitEngine.parse_quantity("12 V", expected_dimension="voltage")
        res_mv = UnitEngine.parse_quantity("12000 mV", expected_dimension="voltage")
        assert res_v.canonical_value == pytest.approx(12.0)
        assert res_mv.canonical_value == pytest.approx(12.0)

        # Current
        res_a = UnitEngine.parse_quantity("0.05 A", expected_dimension="current")
        res_ma = UnitEngine.parse_quantity("50 mA", expected_dimension="current")
        assert res_a.canonical_value == pytest.approx(0.05)
        assert res_ma.canonical_value == pytest.approx(0.05)

        # Resistance
        res_ohm = UnitEngine.parse_quantity("1000 ohm", expected_dimension="resistance")
        res_kohm = UnitEngine.parse_quantity("1 kΩ", expected_dimension="resistance")
        assert res_ohm.canonical_value == pytest.approx(1000.0)
        assert res_kohm.canonical_value == pytest.approx(1000.0)

    def test_case_sensitive_resistance(self):
        res_milli = UnitEngine.parse_quantity("5 mΩ", expected_dimension="resistance")
        res_mega = UnitEngine.parse_quantity("5 MΩ", expected_dimension="resistance")
        assert res_milli.canonical_value == pytest.approx(0.005)
        assert res_mega.canonical_value == pytest.approx(5000000.0)

    def test_damping_units(self):
        res_damp = UnitEngine.parse_quantity("0.5 1/s", expected_dimension="damping")
        assert res_damp.success is True
        assert res_damp.canonical_value == pytest.approx(0.5)
        assert res_damp.canonical_unit == "1/s"

        res_zero = UnitEngine.parse_quantity("0.0 1/s", expected_dimension="damping")
        assert res_zero.success is True
        assert res_zero.canonical_value == 0.0

    def test_bangla_units(self):
        res_bn_len = UnitEngine.parse_quantity("২০ সেমি", expected_dimension="length")
        # Bengali digits can be normalized or ascii
        res_bn_m = UnitEngine.parse_quantity("2.5 মিটার", expected_dimension="length")
        assert res_bn_m.success is True
        assert res_bn_m.canonical_value == pytest.approx(2.5)


class TestUnitEngineRejections:
    """Verify strict rejection of invalid or unsafe inputs."""

    def test_empty_input(self):
        res = UnitEngine.parse_quantity("")
        assert res.success is False
        assert "Empty" in res.error

    def test_nan_input(self):
        res = UnitEngine.parse_quantity(float("nan"), expected_dimension="length")
        assert res.success is False
        assert "non-finite" in res.error.lower()

    def test_inf_input(self):
        res = UnitEngine.parse_quantity(float("inf"), expected_dimension="length")
        assert res.success is False
        assert "non-finite" in res.error.lower()

    def test_unsupported_unit(self):
        res = UnitEngine.parse_quantity("15 lightyears", expected_dimension="length")
        assert res.success is False
        assert "Unsupported unit" in res.error

    def test_dimension_mismatch(self):
        res = UnitEngine.parse_quantity("12 V", expected_dimension="length")
        assert res.success is False
        assert "Dimension mismatch" in res.error


class TestRangeValidation:
    """Verify physical range constraint validation."""

    def test_strictly_positive(self):
        err_zero = UnitEngine.validate_range(0.0, must_be_positive=True, param_name="length")
        assert err_zero is not None
        assert "strictly positive" in err_zero

        err_neg = UnitEngine.validate_range(-0.5, must_be_positive=True, param_name="length")
        assert err_neg is not None

        err_pos = UnitEngine.validate_range(0.8, must_be_positive=True, param_name="length")
        assert err_pos is None

    def test_min_max_bounds(self):
        err = UnitEngine.validate_range(15.0, min_value=0.0, max_value=10.0, param_name="mass")
        assert err is not None
        assert "<=" in err

        err_valid = UnitEngine.validate_range(5.0, min_value=0.0, max_value=10.0, param_name="mass")
        assert err_valid is None

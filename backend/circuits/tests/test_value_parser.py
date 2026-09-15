"""backend/circuits/tests/test_value_parser.py

Unit tests for parameter resolver and SI prefix parsing.
"""
import unittest

from ...core.parameter_resolver import format_si, parse_si
from ..parameters.parameter_binder import TextFragment, bind_parameters_to_components
from ..models import Component, Parameter, Point, Terminal


class TestValueParser(unittest.TestCase):

    def test_si_prefixes(self):
        # Kilo
        res = parse_si("10 kΩ")
        self.assertIsNotNone(res)
        self.assertEqual(res["value"], 10000.0)
        self.assertEqual(res["unit"], "ohm")

        # Mega vs milli case-sensitivity
        res_mega = parse_si("2.5 MΩ")
        self.assertEqual(res_mega["value"], 2.5e6)
        res_milli = parse_si("50 mA")
        self.assertEqual(res_milli["value"], 0.05)

        # Micro
        res_micro = parse_si("4.7 uF")
        self.assertAlmostEqual(res_micro["value"], 4.7e-6)
        res_greek = parse_si("100 µF")
        self.assertAlmostEqual(res_greek["value"], 1e-4)

        # Voltage
        res_v = parse_si("12V")
        self.assertEqual(res_v["value"], 12.0)
        self.assertEqual(res_v["unit"], "V")

    def test_formatting(self):
        self.assertEqual(format_si(0.005, "A"), "5 mA")
        self.assertEqual(format_si(2200, "ohm"), "2.2 kΩ")
        self.assertEqual(format_si(12.0, "V"), "12 V")

    def test_parameter_binding(self):
        comps = [
            Component(
                id="R1",
                type="resistor",
                terminals=[Terminal(id="R1.a", position=Point(100, 100)), Terminal(id="R1.b", position=Point(150, 100))],
                bbox_source_px=[90, 90, 160, 110],
            ),
            Component(
                id="V1",
                type="voltage_source",
                terminals=[Terminal(id="V1.p", position=Point(50, 200)), Terminal(id="V1.n", position=Point(50, 250))],
                bbox_source_px=[40, 190, 60, 260],
            ),
        ]

        fragments = [
            TextFragment(text="10 Ω", center_x=120, center_y=80, bbox=[100, 70, 140, 90]),
            TextFragment(text="12 V", center_x=50, center_y=170, bbox=[40, 160, 60, 180]),
        ]

        bound_comps = bind_parameters_to_components(comps, fragments, 800, 600)
        r1 = next(c for c in bound_comps if c.id == "R1")
        v1 = next(c for c in bound_comps if c.id == "V1")

        self.assertIn("resistance_ohm", r1.parameters)
        self.assertEqual(r1.parameters["resistance_ohm"].value, 10.0)

        self.assertIn("voltage_v", v1.parameters)
        self.assertEqual(v1.parameters["voltage_v"].value, 12.0)


if __name__ == "__main__":
    unittest.main()

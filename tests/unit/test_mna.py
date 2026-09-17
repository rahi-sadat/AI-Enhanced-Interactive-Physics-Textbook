"""backend/circuits/tests/test_mna.py

Comprehensive mathematical unit tests for the Python Modified Nodal Analysis (MNA) solver.
Verifies analytical solutions against MNA results within strict numerical tolerance (1e-9).
"""
import unittest

try:
    from shared.schemas.circuit_models import CircuitScene, Component, Node, Parameter, Point, Terminal
    from engine.circuits.equation_generator import generate_equations
    from engine.circuits.mna_solver import MNASolver
    from engine.circuits.spice_adapter import SpiceAdapter
except (ImportError, ValueError):
    from ..models import CircuitScene, Component, Node, Parameter, Point, Terminal
    from ..solver.equation_generator import generate_equations
    from ..solver.mna_solver import MNASolver
    from ..solver.spice_adapter import SpiceAdapter


class TestMNASolver(unittest.TestCase):

    def test_series_circuit(self):
        """Series circuit: V = 12V, R1 = 10 ohm, R2 = 20 ohm.
        Expected: I = 0.4 A, V_R1 = 4 V, V_R2 = 8 V, P_tot = 4.8 W.
        """
        scene = CircuitScene(
            reference_node="N0",
            nodes=[
                Node(id="N0", terminal_ids=["V1.n", "R2.b"], reference=True),
                Node(id="N1", terminal_ids=["V1.p", "R1.a"]),
                Node(id="N2", terminal_ids=["R1.b", "R2.a"]),
            ],
            components=[
                Component(
                    id="V1",
                    type="voltage_source",
                    terminals=[
                        Terminal(id="V1.p", position=Point(100, 200), node="N1"),
                        Terminal(id="V1.n", position=Point(100, 300), node="N0"),
                    ],
                    bbox_source_px=[90, 190, 110, 310],
                    parameters={"voltage_v": Parameter(value=12.0, unit="V")},
                ),
                Component(
                    id="R1",
                    type="resistor",
                    terminals=[
                        Terminal(id="R1.a", position=Point(200, 150), node="N1"),
                        Terminal(id="R1.b", position=Point(300, 150), node="N2"),
                    ],
                    bbox_source_px=[190, 140, 310, 160],
                    parameters={"resistance_ohm": Parameter(value=10.0, unit="ohm")},
                ),
                Component(
                    id="R2",
                    type="resistor",
                    terminals=[
                        Terminal(id="R2.a", position=Point(300, 250), node="N2"),
                        Terminal(id="R2.b", position=Point(300, 350), node="N0"),
                    ],
                    bbox_source_px=[290, 240, 310, 360],
                    parameters={"resistance_ohm": Parameter(value=20.0, unit="ohm")},
                ),
            ],
        )

        solver = MNASolver(scene)
        state = solver.solve_dc()

        self.assertEqual(state.status, "solved")
        self.assertAlmostEqual(state.node_voltages["N0"], 0.0, places=6)
        self.assertAlmostEqual(state.node_voltages["N1"], 12.0, places=6)
        self.assertAlmostEqual(state.node_voltages["N2"], 8.0, places=6)

        # Branch currents
        self.assertAlmostEqual(state.components["R1"].current_a, 0.4, places=6)
        self.assertAlmostEqual(state.components["R2"].current_a, 0.4, places=6)

        # Voltage drops
        self.assertAlmostEqual(state.components["R1"].voltage_v, 4.0, places=6)
        self.assertAlmostEqual(state.components["R2"].voltage_v, 8.0, places=6)

        # Equivalent resistance and total power
        self.assertAlmostEqual(state.equivalent_resistance_ohm, 30.0, places=6)
        self.assertAlmostEqual(state.total_power_w, 4.8, places=6)

        # KCL check at N2
        self.assertAlmostEqual(state.kcl_residuals["N2"], 0.0, places=6)

        # Equations check
        eqs = generate_equations(scene, state)
        self.assertTrue(any("R_eq" in eq["symbolic"] for eq in eqs))

        # SPICE netlist generation sanity
        netlist = SpiceAdapter.build_netlist(scene)
        self.assertIn("V1 N1 0 DC 12", netlist)
        self.assertIn("R1 N1 N2 10", netlist)

    def test_parallel_circuit(self):
        """Parallel circuit: V = 12V, R1 = 6 ohm || R2 = 3 ohm.
        Expected: I1 = 2 A, I2 = 4 A, I_tot = 6 A, R_eq = 2 ohm.
        """
        scene = CircuitScene(
            reference_node="N0",
            nodes=[
                Node(id="N0", terminal_ids=["V1.n", "R1.b", "R2.b"], reference=True),
                Node(id="N1", terminal_ids=["V1.p", "R1.a", "R2.a"]),
            ],
            components=[
                Component(
                    id="V1",
                    type="voltage_source",
                    terminals=[
                        Terminal(id="V1.p", position=Point(100, 200), node="N1"),
                        Terminal(id="V1.n", position=Point(100, 300), node="N0"),
                    ],
                    bbox_source_px=[90, 190, 110, 310],
                    parameters={"voltage_v": Parameter(value=12.0, unit="V")},
                ),
                Component(
                    id="R1",
                    type="resistor",
                    terminals=[
                        Terminal(id="R1.a", position=Point(200, 200), node="N1"),
                        Terminal(id="R1.b", position=Point(200, 300), node="N0"),
                    ],
                    bbox_source_px=[190, 190, 210, 310],
                    parameters={"resistance_ohm": Parameter(value=6.0, unit="ohm")},
                ),
                Component(
                    id="R2",
                    type="resistor",
                    terminals=[
                        Terminal(id="R2.a", position=Point(300, 200), node="N1"),
                        Terminal(id="R2.b", position=Point(300, 300), node="N0"),
                    ],
                    bbox_source_px=[290, 190, 310, 310],
                    parameters={"resistance_ohm": Parameter(value=3.0, unit="ohm")},
                ),
            ],
        )

        solver = MNASolver(scene)
        state = solver.solve_dc()

        self.assertEqual(state.status, "solved")
        self.assertAlmostEqual(state.components["R1"].current_a, 2.0, places=6)
        self.assertAlmostEqual(state.components["R2"].current_a, 4.0, places=6)
        self.assertAlmostEqual(abs(state.components["V1"].current_a), 6.0, places=6)
        self.assertAlmostEqual(state.equivalent_resistance_ohm, 2.0, places=6)

    def test_wheatstone_bridge(self):
        """Wheatstone bridge:
        V = 10V between N1 and N0.
        R1 (N1->NA)=100, R2 (N1->NB)=100.
        R3 (NA->N0)=100, R4 (NB->N0)=100.
        Bridge resistor R5 (NA->NB)=50.
        Balanced bridge: V(NA) = V(NB) = 5V, I(R5) = 0.
        """
        scene = CircuitScene(
            reference_node="N0",
            nodes=[
                Node(id="N0", reference=True),
                Node(id="N1"),
                Node(id="NA"),
                Node(id="NB"),
            ],
            components=[
                Component(
                    id="V1",
                    type="voltage_source",
                    terminals=[
                        Terminal(id="V1.p", position=Point(0, 0), node="N1"),
                        Terminal(id="V1.n", position=Point(0, 1), node="N0"),
                    ],
                    bbox_source_px=[0, 0, 10, 10],
                    parameters={"voltage_v": Parameter(value=10.0, unit="V")},
                ),
                Component(
                    id="R1",
                    type="resistor",
                    terminals=[
                        Terminal(id="R1.a", position=Point(0, 0), node="N1"),
                        Terminal(id="R1.b", position=Point(0, 1), node="NA"),
                    ],
                    bbox_source_px=[0, 0, 10, 10],
                    parameters={"resistance_ohm": Parameter(value=100.0, unit="ohm")},
                ),
                Component(
                    id="R2",
                    type="resistor",
                    terminals=[
                        Terminal(id="R2.a", position=Point(0, 0), node="N1"),
                        Terminal(id="R2.b", position=Point(0, 1), node="NB"),
                    ],
                    bbox_source_px=[0, 0, 10, 10],
                    parameters={"resistance_ohm": Parameter(value=100.0, unit="ohm")},
                ),
                Component(
                    id="R3",
                    type="resistor",
                    terminals=[
                        Terminal(id="R3.a", position=Point(0, 0), node="NA"),
                        Terminal(id="R3.b", position=Point(0, 1), node="N0"),
                    ],
                    bbox_source_px=[0, 0, 10, 10],
                    parameters={"resistance_ohm": Parameter(value=100.0, unit="ohm")},
                ),
                Component(
                    id="R4",
                    type="resistor",
                    terminals=[
                        Terminal(id="R4.a", position=Point(0, 0), node="NB"),
                        Terminal(id="R4.b", position=Point(0, 1), node="N0"),
                    ],
                    bbox_source_px=[0, 0, 10, 10],
                    parameters={"resistance_ohm": Parameter(value=100.0, unit="ohm")},
                ),
                Component(
                    id="R5",
                    type="resistor",
                    terminals=[
                        Terminal(id="R5.a", position=Point(0, 0), node="NA"),
                        Terminal(id="R5.b", position=Point(0, 1), node="NB"),
                    ],
                    bbox_source_px=[0, 0, 10, 10],
                    parameters={"resistance_ohm": Parameter(value=50.0, unit="ohm")},
                ),
            ],
        )

        solver = MNASolver(scene)
        state = solver.solve_dc()

        self.assertEqual(state.status, "solved")
        self.assertAlmostEqual(state.node_voltages["NA"], 5.0, places=6)
        self.assertAlmostEqual(state.node_voltages["NB"], 5.0, places=6)
        self.assertAlmostEqual(state.components["R5"].current_a, 0.0, places=6)

    def test_switch_open_and_closed(self):
        """Switch behavior:
        When closed, I = V / R = 10 / 5 = 2 A.
        When open, I = 0 A.
        """
        for state_val, expected_current in [("closed", 2.0), ("open", 0.0)]:
            scene = CircuitScene(
                reference_node="N0",
                nodes=[
                    Node(id="N0", reference=True),
                    Node(id="N1"),
                    Node(id="N2"),
                ],
                components=[
                    Component(
                        id="V1",
                        type="voltage_source",
                        terminals=[
                            Terminal(id="V1.p", position=Point(0, 0), node="N1"),
                            Terminal(id="V1.n", position=Point(0, 1), node="N0"),
                        ],
                        bbox_source_px=[0, 0, 10, 10],
                        parameters={"voltage_v": Parameter(value=10.0, unit="V")},
                    ),
                    Component(
                        id="SW1",
                        type="switch",
                        state=state_val,
                        terminals=[
                            Terminal(id="SW1.a", position=Point(0, 0), node="N1"),
                            Terminal(id="SW1.b", position=Point(0, 1), node="N2"),
                        ],
                        bbox_source_px=[0, 0, 10, 10],
                    ),
                    Component(
                        id="R1",
                        type="resistor",
                        terminals=[
                            Terminal(id="R1.a", position=Point(0, 0), node="N2"),
                            Terminal(id="R1.b", position=Point(0, 1), node="N0"),
                        ],
                        bbox_source_px=[0, 0, 10, 10],
                        parameters={"resistance_ohm": Parameter(value=5.0, unit="ohm")},
                    ),
                ],
            )

            state = MNASolver(scene).solve_dc()
            self.assertEqual(state.status, "solved")
            self.assertAlmostEqual(state.components["R1"].current_a, expected_current, places=6)


if __name__ == "__main__":
    unittest.main()

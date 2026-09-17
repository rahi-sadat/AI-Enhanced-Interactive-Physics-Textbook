"""backend/circuits/tests/test_topology.py

Unit tests for topology building, Union-Find clustering, and diagnostic validation.
"""
import unittest

try:
    from shared.schemas.circuit_models import CircuitScene, Component, Node, Parameter, Point, Terminal, Wire
    from engine.circuits.topology.topology_builder import build_topology
    from engine.circuits.topology.topology_validator import DiagnosticSeverity, validate_topology
    from engine.circuits.topology.union_find import UnionFind
except (ImportError, ValueError):
    from ..models import CircuitScene, Component, Node, Parameter, Point, Terminal, Wire
    from ..topology.topology_builder import build_topology
    from ..topology.topology_validator import DiagnosticSeverity, validate_topology
    from ..topology.union_find import UnionFind


class TestTopology(unittest.TestCase):

    def test_union_find(self):
        uf = UnionFind[str]()
        uf.add("a")
        uf.add("b")
        uf.add("c")

        self.assertFalse(uf.connected("a", "b"))
        uf.union("a", "b")
        self.assertTrue(uf.connected("a", "b"))
        self.assertFalse(uf.connected("a", "c"))

        uf.union("b", "c")
        self.assertTrue(uf.connected("a", "c"))

    def test_topology_builder_snapping(self):
        components = [
            Component(
                id="V1",
                type="voltage_source",
                terminals=[
                    Terminal(id="V1.p", position=Point(50.0, 100.0)),
                    Terminal(id="V1.n", position=Point(50.0, 300.0)),
                ],
                bbox_source_px=[40, 90, 60, 310],
            ),
            Component(
                id="R1",
                type="resistor",
                terminals=[
                    Terminal(id="R1.a", position=Point(100.0, 100.0)),
                    Terminal(id="R1.b", position=Point(200.0, 100.0)),
                ],
                bbox_source_px=[90, 90, 210, 110],
            ),
        ]

        # Top connecting wire from V1.p to R1.a
        wires = [
            Wire(
                id="w1",
                polyline_source_px=[Point(50.0, 100.0), Point(100.0, 100.0)],
            ),
        ]

        nodes, ref_node = build_topology(components, wires, image_width=800, image_height=600)
        self.assertTrue(len(nodes) >= 2)

        # V1.p and R1.a should share the same node
        v1_p_node = next(t.node for c in components if c.id == "V1" for t in c.terminals if t.id == "V1.p")
        r1_a_node = next(t.node for c in components if c.id == "R1" for t in c.terminals if t.id == "R1.a")
        self.assertEqual(v1_p_node, r1_a_node)

    def test_validator_detects_shorted_voltage_source(self):
        scene = CircuitScene(
            reference_node="N0",
            nodes=[
                Node(id="N0", reference=True),
            ],
            components=[
                Component(
                    id="V1",
                    type="voltage_source",
                    terminals=[
                        Terminal(id="V1.p", position=Point(0, 0), node="N0"),
                        Terminal(id="V1.n", position=Point(0, 1), node="N0"),  # Shorted!
                    ],
                    bbox_source_px=[0, 0, 10, 10],
                    parameters={"voltage_v": Parameter(value=12.0, unit="V")},
                ),
            ],
        )

        rep = validate_topology(scene)
        self.assertFalse(rep.valid)
        self.assertTrue(any(d.code == "SHORTED_VOLTAGE_SOURCE" for d in rep.diagnostics))


if __name__ == "__main__":
    unittest.main()

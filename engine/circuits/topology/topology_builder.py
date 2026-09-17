"""backend/circuits/topology/topology_builder.py

Builds unified electrical nodes from visual terminals, wires, and junctions.
Uses spatial snapping with adaptive radius and Union-Find (DSU) clustering.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple

try:
    from backend.core.coordinate_space import snap_radius
except (ImportError, ValueError):
    try:
        from core.coordinate_space import snap_radius
    except (ImportError, ValueError):
        from ...core.coordinate_space import snap_radius
from ..models import CircuitScene, Component, Node, Point, Terminal, Wire
from .union_find import UnionFind


def build_topology(
    components: list[Component],
    wires: list[Wire],
    image_width: int = 800,
    image_height: int = 600,
    explicit_ground_node: Optional[str] = None,
) -> Tuple[list[Node], str]:
    """Aggregate terminals and wires into distinct electrical nodes.
    
    Returns:
        (nodes, reference_node_id)
    """
    uf: UnionFind[str] = UnionFind()
    radius = snap_radius(image_width, image_height)

    # 1. Register all terminal identifiers in Union-Find
    all_terminals: list[Terminal] = []
    for comp in components:
        for term in comp.terminals:
            uf.add(term.id)
            all_terminals.append(term)

    # 2. Connect wire endpoints to other wires if endpoints are within snap radius
    wire_endpoints: list[Tuple[str, Point, int]] = []  # (wire_id, Point, end_index)
    for wire in wires:
        uf.add(wire.id)
        if wire.polyline_source_px:
            wire_endpoints.append((wire.id, wire.polyline_source_px[0], 0))
            if len(wire.polyline_source_px) > 1:
                wire_endpoints.append((wire.id, wire.polyline_source_px[-1], len(wire.polyline_source_px) - 1))

    # Connect overlapping wire endpoints
    for i in range(len(wire_endpoints)):
        w1_id, p1, _ = wire_endpoints[i]
        for j in range(i + 1, len(wire_endpoints)):
            w2_id, p2, _ = wire_endpoints[j]
            dist = math.hypot(p1.x - p2.x, p1.y - p2.y)
            if dist <= radius:
                uf.union(w1_id, w2_id)

    # 3. Connect terminals to nearest wire endpoints
    for term in all_terminals:
        best_wire_id: Optional[str] = None
        best_dist = radius * 1.5  # Slightly more forgiving for component leads
        for w_id, ep_pt, _ in wire_endpoints:
            dist = math.hypot(term.position.x - ep_pt.x, term.position.y - ep_pt.y)
            if dist < best_dist:
                best_dist = dist
                best_wire_id = w_id

        if best_wire_id is not None:
            uf.union(term.id, best_wire_id)

    # Also check direct terminal-to-terminal snapping (if components share a joint with no intermediate wire)
    for i in range(len(all_terminals)):
        t1 = all_terminals[i]
        for j in range(i + 1, len(all_terminals)):
            t2 = all_terminals[j]
            # Don't snap terminals of the same component together!
            if t1.id.split(".")[0] == t2.id.split(".")[0]:
                continue
            dist = math.hypot(t1.position.x - t2.position.x, t1.position.y - t2.position.y)
            if dist <= radius:
                uf.union(t1.id, t2.id)

    # 4. Extract connected components
    clusters = uf.get_components()

    # Filter clusters to only those that contain at least one terminal
    node_clusters: list[Set[str]] = []
    for root, members in clusters.items():
        term_members = {m for m in members if any(m == t.id for t in all_terminals)}
        if term_members:
            node_clusters.append(members)

    # 5. Build canonical Node objects
    nodes: list[Node] = []
    # Sort clusters deterministically
    node_clusters.sort(key=lambda s: sorted(list(s))[0])

    # Reference node selection strategy:
    # 1. Explicit ground
    # 2. Battery negative terminal
    # 3. First source negative terminal
    ref_candidate_id = explicit_ground_node
    if not ref_candidate_id:
        for comp in components:
            if comp.type in ("battery", "voltage_source", "cell"):
                # By convention, terminal 1 (or ending in .n or .b) is negative
                for term in comp.terminals:
                    if term.id.endswith(".n") or term.id.endswith(".b") or term.id.endswith(".2"):
                        ref_candidate_id = term.id
                        break
                if ref_candidate_id:
                    break

    selected_ref_node_id = "N0"
    for idx, cluster in enumerate(node_clusters):
        node_id = f"N{idx}"
        term_ids = [m for m in cluster if any(m == t.id for t in all_terminals)]
        term_ids.sort()

        is_ref = False
        if ref_candidate_id and ref_candidate_id in cluster:
            is_ref = True
            selected_ref_node_id = node_id

        node = Node(id=node_id, terminal_ids=term_ids, reference=is_ref)
        nodes.append(node)

        # Update terminal node assignment
        for comp in components:
            for term in comp.terminals:
                if term.id in cluster:
                    term.node = node_id

        # Update wire connected nodes
        for wire in wires:
            if wire.id in cluster:
                if node_id not in wire.connected_nodes:
                    wire.connected_nodes.append(node_id)

    # Ensure at least one reference node exists
    if not any(n.reference for n in nodes) and nodes:
        nodes[0].reference = True
        selected_ref_node_id = nodes[0].id

    return nodes, selected_ref_node_id

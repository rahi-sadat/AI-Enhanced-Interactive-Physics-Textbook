"""Validate extracted evidence before entering the separate analysis route."""
from ai.evidence.grounding.circuit_integrity import validate_circuit_integrity
from engine.circuits.grounded_analysis import analyze_grounded_circuit


def analyze_book_circuit(book, **parameters):
    issues=validate_circuit_integrity(book)
    # A short may block canonical ideal readiness while the physical extraction
    # remains verified. No other structural issue is waived for the fault route.
    blockers=[i for i in issues if i['code']!='SHORTED_CIRCUIT_SOURCE']
    validation=(book.geometry or {}).get('circuit_validation',{})
    if blockers or not validation.get('geometry') or not validation.get('topology'):
        return dict(status='NEEDS_REVIEW',mode=parameters.get('mode','ideal'),issues=blockers,
                    error='Complete verified physical geometry and conductor topology are required.',
                    electrical_state=None)
    graph={k:book.parameters.get(k) for k in ('components','nodes','wires','reference_node')}
    if book.parameters.get('geometric_conductor_graph'):
        graph['geometric_conductor_graph']=book.parameters['geometric_conductor_graph']
    return analyze_grounded_circuit(graph,source_asset_id=book.source_asset_id,**parameters)

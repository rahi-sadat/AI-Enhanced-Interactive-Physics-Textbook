from copy import deepcopy

from ai.evidence.grounding.circuit_graph import build_geometric_conductor_graph
from engine.circuits.grounded_analysis import analyze_grounded_circuit
from tests.unit.test_circuit_fault_analysis import measured_graph,analyze
from tests.unit.test_circuit_grounding_repair import ground_fixture


def test_source_graph_keeps_edges_before_contraction_and_all_terminal_evidence():
    _,_,book,_=ground_fixture(parallel=True,closed=True)
    graph=book.parameters['geometric_conductor_graph']
    assert graph['contraction']=='none' and graph['coordinate_space']=='source_px'
    assert len(graph['vertices'])>len(book.parameters['nodes'])
    assert len(graph['edges'])==len(book.parameters['wires'])
    assert len(graph['terminals'])==2*len(book.parameters['components'])
    assert all(e['provenance']['source']=='diagram_measurement' for e in graph['edges'])
    assert graph['junction_evidence']


def test_source_graph_is_immutable_and_fault_edge_precedes_node_contraction():
    graph=measured_graph()
    for w in graph['wires']:w['provenance']={'source':'diagram_measurement'}
    graph['geometric_conductor_graph']=build_geometric_conductor_graph(graph['wires'],graph['components'],source_asset_id='test')
    before=deepcopy(graph)
    result=analyze(graph,mode='non_ideal',source_internal_resistance_ohm=1,short_path_resistance_ohm=2)
    assert result['status']=='NON_IDEAL_SOLVED' and graph==before
    electrical=result['solver_electrical_graph']
    assert len(electrical['components'])==len(graph['components'])+2
    resistor=next(c for c in electrical['components'] if c['id']=='fault_path:fault')
    assert len({t['node'] for t in resistor['terminals']})==2
    assert 'entire polyline' in result['model']['metadata']['short_path_resistance_representation']
    assert result['correctness_checks']['physics']=='PASSED'
    assert result['correctness_checks']['overlay']==result['correctness_checks']['runtime']=='NOT_EVALUATED'
    graph['geometric_conductor_graph']['vertices'][0]['source_px']=[123,456]
    assert analyze(graph)['status']=='NEEDS_REVIEW'


def test_additional_zero_resistance_bypass_never_becomes_a_resistor_self_loop():
    graph=measured_graph()
    graph['wires'].append(dict(id='second_short',ends=[2,4],points=[[50,20],[50,120]],node='N0',verification_status='VERIFIED'))
    before=deepcopy(graph)
    r=analyze(graph,mode='non_ideal',source_internal_resistance_ohm=1,short_path_resistance_ohm=2)
    assert r['status']=='NEEDS_REVIEW' and r['electrical_state'] is None
    assert r['fault_path_assignment']['ambiguous'] and not r['fault_paths']
    assert 'additional ideal bypass' in r['fault_path_assignment']['diagnostic']
    assert not r['assumptions'] and graph==before


def test_segmented_short_requires_explicit_choice_and_keeps_every_branch():
    graph=measured_graph()
    graph['wires'][-1:]=[
        dict(id='short_a',ends=[2,9],points=[[50,20],[50,70]],node='N0',verification_status='VERIFIED'),
        dict(id='short_b',ends=[9,4],points=[[50,70],[50,120]],node='N0',verification_status='VERIFIED')]
    r=analyze(graph,mode='non_ideal',source_internal_resistance_ohm=1,short_path_resistance_ohm=2)
    assert r['status']=='NEEDS_REVIEW' and r['fault_path_assignment']['ambiguous']
    r=analyze(graph,mode='non_ideal',source_internal_resistance_ohm=1,short_path_resistance_ohm=2,fault_path_id='short_a')
    assert r['status']=='NON_IDEAL_SOLVED'
    assert {'V','R1','R2'}<={c['id'] for c in r['solver_electrical_graph']['components']}

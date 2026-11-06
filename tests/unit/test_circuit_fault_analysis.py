"""Independent analytic checks of the full extracted parallel fault circuit."""
from copy import deepcopy
import math

import pytest

from engine.circuits.grounded_analysis import analyze_grounded_circuit
from engine.circuits.mna_solver import MNASolver
from engine.circuits.models import CircuitScene,Node,Component,Terminal,Point,Parameter


def measured_graph(short=True):
    points={1:[10,20],2:[50,20],3:[10,120],4:[50,120],5:[100,20],6:[100,120],7:[150,20],8:[150,120]}
    edges=[('vp',1,2),('vn',3,4),('r1a',2,5),('r1b',4,6),('r2a',2,7),('r2b',4,8)]
    if short:edges.append(('fault',2,4))
    top={1,2,5,7}
    node=lambda end: 'N0' if short or end not in top else 'N1'
    wires=[dict(id=wid,ends=[a,b],points=[points[a],points[b]],node=node(a),verification_status='VERIFIED')
           for wid,a,b in edges]
    byid={w['id']:w for w in wires}
    def component(cid,kind,value,wa,wb,end):
        return dict(id=cid,type=kind,value=value,unit='V' if kind=='voltage_source' else 'ohm',
            value_provenance={'source':'ocr','evidence_refs':['text:'+cid]},
            nodes=[byid[wa]['node'],byid[wb]['node']],terminals=[
                dict(id=cid+'.'+str(i),wire_id=wid,wire_end=end,node=byid[wid]['node'],source_px=byid[wid]['points'][end])
                for i,wid in enumerate([wa,wb])])
    return dict(nodes=[{'id':'N0'}]+([] if short else [{'id':'N1'}]),reference_node='N0',wires=wires,
        components=[component('V','voltage_source',12,'vp','vn',0),
                    component('R1','resistor',6,'r1a','r1b',-1),component('R2','resistor',12,'r2a','r2b',-1)])


def analyze(graph=None,**kwargs):
    return analyze_grounded_circuit(graph or measured_graph(),source_asset_id='synthetic-explicit-evidence',**kwargs)


def test_ideal_short_preserves_conductor_and_returns_no_finite_current():
    graph=measured_graph();before=deepcopy(graph)
    r=analyze(graph)
    assert r['status']=='IDEAL_REJECTED' and r['electrical_state'] is None
    assert r['fault_path_id']=='fault' and r['short_path_wire_ids']==['vp','fault','vn']
    assert 'zero-resistance' in r['explanation']
    assert graph==before and r['graph']==graph


@pytest.mark.parametrize('arguments',[{},dict(source_internal_resistance_ohm=1),dict(short_path_resistance_ohm=2)])
def test_missing_explicit_parameters_are_qualitative(arguments):
    r=analyze(mode='non_ideal',**arguments)
    assert r['status']=='QUALITATIVE_FAULT'
    assert r['electrical_state'] is None and not r['assumptions']
    assert 'wire_currents_a' not in r


@pytest.mark.parametrize('internal,fault',[(None,-1),(-1,2),(1,0),(True,2),(1,float('nan')),(float('inf'),2)])
def test_invalid_resistances_never_solve(internal,fault):
    r=analyze(mode='non_ideal',source_internal_resistance_ohm=internal,short_path_resistance_ohm=fault)
    assert r['status'] in {'QUALITATIVE_FAULT','INVALID_PARAMETERS'}
    assert r['electrical_state'] is None


@pytest.mark.parametrize('internal',[0,1])
def test_full_parallel_fault_mna_matches_independent_reference(internal):
    graph=measured_graph();before=deepcopy(graph)
    r=analyze(graph,mode='non_ideal',source_internal_resistance_ohm=internal,short_path_resistance_ohm=2)
    assert r['status']=='NON_IDEAL_SOLVED',r
    state=r['electrical_state'];states=state['components']
    # Independent circuit reduction: 6||12||2 = 4/3 ohm, in series with Rinternal.
    source_current=12/(internal+4/3)
    terminal_voltage=12-source_current*internal
    assert states['V']['current_a']==pytest.approx(-source_current,abs=1e-6)
    assert states['R1']['current_a']==pytest.approx(terminal_voltage/6,abs=1e-6)
    assert states['R2']['current_a']==pytest.approx(terminal_voltage/12,abs=1e-6)
    assert states['fault_path:fault']['current_a']==pytest.approx(terminal_voltage/2,abs=1e-6)
    assert abs(states['fault_path:fault']['current_a']) < abs(states['V']['current_a'])
    assert r['validation']['valid'] and r['validation']['kcl_residual_a']<1e-9
    assert r['validation']['kvl_constitutive_residual_v']<1e-9 and r['validation']['power_balance_w']<1e-9
    assert r['wire_currents_a']['r1a']==pytest.approx(terminal_voltage/6)
    assert r['wire_currents_a']['vp']==pytest.approx(source_current)
    assert r['assumptions']['source_internal_resistance_ohm']['source']=='user_assumption'
    assert graph==before and r['fault_path_geometry']==graph['wires'][-1]['points']
    assert len(r['model']['circuit']['components'])==4+(internal>0)
    fault_model=next(c for c in r['model']['circuit']['components'] if c['id']=='fault_path:fault')
    assert [t['source_px'] for t in fault_model['terminals']]==graph['wires'][-1]['points']
    assert r['model']['metadata']['model_provenance']=='explicit_user_assumptions'


def test_regular_parallel_graph_solves_ideal_without_assumptions():
    r=analyze(measured_graph(False))
    assert r['status']=='IDEAL_SOLVED',r
    assert r['electrical_state']['components']['V']['current_a']==-3
    assert not r['assumptions']


@pytest.mark.parametrize('corruption',['missing_value','provenance','endpoint','junction','node','duplicate'])
def test_corrupted_or_unverified_evidence_is_rejected(corruption):
    graph=measured_graph()
    if corruption=='missing_value':graph['components'][1].pop('value')
    if corruption=='provenance':graph['components'][1]['value_provenance']['source']='auto_policy'
    if corruption=='endpoint':graph['components'][1]['terminals'][0]['wire_end']=None
    if corruption=='junction':graph['wires'][2]['points'][0]=[99,99]
    if corruption=='node':graph['wires'][0]['node']='invented'
    if corruption=='duplicate':graph['wires'].append(deepcopy(graph['wires'][0]))
    r=analyze(graph,mode='non_ideal',source_internal_resistance_ohm=1,short_path_resistance_ohm=2)
    assert r['status']=='NEEDS_REVIEW' and r['electrical_state'] is None


def test_strict_solver_rejects_underdetermined_system_without_changing_default_api():
    terms=[Terminal('a',Point(0,0),'A'),Terminal('b',Point(1,1),'B')]
    scene=CircuitScene(reference_node='A',nodes=[Node('A'),Node('B'),Node('floating')],components=[
        Component('V','voltage_source',terms,[],{'voltage_v':Parameter(12,'V')})])
    state=MNASolver(scene).solve_dc(strict=True)
    assert state.status=='singular' and not state.node_voltages and not state.components


def test_underdetermined_ideal_wire_cycle_cannot_supply_invented_flow():
    graph=measured_graph()
    graph['wires'].extend([
        dict(id='cycle1',ends=[2,9],points=[[50,20],[75,10]],node='N0',verification_status='VERIFIED'),
        dict(id='cycle2',ends=[9,5],points=[[75,10],[100,20]],node='N0',verification_status='VERIFIED')])
    r=analyze(graph,mode='non_ideal',source_internal_resistance_ohm=1,short_path_resistance_ohm=2)
    assert r['status']=='NUMERICAL_REJECTED' and r['electrical_state'] is None
    assert not r['validation']['wire_flow_complete']
    assert set(r['validation']['underdetermined_wire_ids'])=={'cycle1','cycle2','r1a'}

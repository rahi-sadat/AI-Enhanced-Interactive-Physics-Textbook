"""Separate ideal/fault analysis of a measured conductor graph.

No detection, OCR, geometric snapping or circuit completion happens here. Wire
endpoint identities must come from classical CV. Non-ideal assumptions live in a
new model; the extracted graph and the canonical ideal validator stay intact.
"""
from collections import defaultdict, deque
from copy import deepcopy
import hashlib
import json
import math

import numpy as np

from .models import CircuitScene, Component, Node, Parameter, Point, Terminal
from .mna_solver import MNASolver

TOLERANCE = 1e-9


class ConductorNetwork:
    def __init__(self, graph):
        self.graph = graph
        self.wires = {w['id']: w for w in graph['wires']}
        if len(self.wires) != len(graph['wires']) or not self.wires:
            raise ValueError('Missing or duplicate conductor paths')
        self.edges, self.coordinates = {}, {}
        for wid, wire in self.wires.items():
            ends, points = wire.get('ends'), wire.get('points')
            if (wire.get('verification_status') != 'VERIFIED' or not isinstance(ends, list)
                    or len(ends) != 2 or not points or len(points) < 2):
                raise ValueError(f'{wid} lacks verified conductor endpoint identities')
            keys = []
            for side, end in enumerate(ends):
                if not isinstance(end, (str, int)) or isinstance(end, bool):
                    raise ValueError(f'{wid} has invalid junction evidence')
                key = f'junction:{end}' if end else f'{wid}:{side}'
                point = points[0 if side == 0 else -1]
                if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in point):
                    raise ValueError('Non-finite conductor coordinates')
                if key in self.coordinates and self.coordinates[key] != point:
                    raise ValueError('Contradictory coordinates for a declared junction')
                self.coordinates[key] = point
                keys.append(key)
            self.edges[wid] = keys
        self.terminals = {}
        for component in graph['components']:
            for term in component['terminals']:
                if term.get('wire_id') not in self.edges or term.get('wire_end') not in (0, -1):
                    raise ValueError(f"{term['id']} lacks a measured wire endpoint association")
                self.terminals[term['id']] = self.edges[term['wire_id']][0 if term['wire_end']==0 else 1]
        geometric=graph.get('geometric_conductor_graph')
        if geometric is not None:
            expected_edges={e['id']:e for e in geometric['edges']}
            expected_terms={t['id']:t for t in geometric['terminals']}
            expected_vertices={v['id']:v['source_px'] for v in geometric['vertices']}
            if (geometric.get('contraction')!='none' or set(expected_edges)!=set(self.wires)
                    or set(expected_terms)!=set(self.terminals) or expected_vertices!=self.coordinates):
                raise ValueError('Geometric conductor graph disagrees with electrical projection')
            for wid,wire in self.wires.items():
                edge=expected_edges[wid]
                if edge['vertices']!=self.edges[wid] or edge['polyline_source_px']!=wire['points']:
                    raise ValueError('Electrical edge differs from measured source graph')
            for tid,vertex in self.terminals.items():
                if expected_terms[tid]['vertex']!=vertex:
                    raise ValueError('Terminal differs from measured source graph')
        # The solver's collapsed electrical graph must agree with the measured
        # endpoint graph. A client cannot invent contradictory node labels.
        roots = self.partitions()
        declarations = defaultdict(set)
        for wid, wire in self.wires.items():
            declarations[roots[self.edges[wid][0]]].add(wire['node'])
        for component in graph['components']:
            for term in component['terminals']:
                declarations[roots[self.terminals[term['id']]]].add(term['node'])
        if any(len(nodes) != 1 for nodes in declarations.values()) or len({next(iter(v)) for v in declarations.values()}) != len(declarations):
            raise ValueError('Collapsed electrical nodes contradict conductor evidence')

    def partitions(self, exclude=()):
        parent = {k:k for k in self.coordinates}
        def root(k):
            while k != parent[k]:
                parent[k] = parent[parent[k]]
                k = parent[k]
            return k
        for wid, (a,b) in self.edges.items():
            if wid not in exclude:
                parent[root(b)] = root(a)
        return {k:root(k) for k in parent}

    def reachable(self, start, exclude=()):
        adjacency = defaultdict(list)
        for wid,(a,b) in self.edges.items():
            if wid not in exclude:
                adjacency[a].append((b,wid)); adjacency[b].append((a,wid))
        seen, queue = {start}, deque([start])
        while queue:
            for vertex,_ in adjacency[queue.popleft()]:
                if vertex not in seen:
                    seen.add(vertex); queue.append(vertex)
        return seen

    def short_route(self, source):
        a,b = [self.terminals[t['id']] for t in source['terminals']]
        adjacency = defaultdict(list)
        for wid,(u,v) in self.edges.items():
            adjacency[u].append((v,wid)); adjacency[v].append((u,wid))
        # Deterministic breadth-first route with explicit predecessor vertices.
        previous, queue = {a:None}, deque([a])
        while queue and b not in previous:
            u = queue.popleft()
            for v,wid in adjacency[u]:
                if v not in previous:
                    previous[v]=(u,wid); queue.append(v)
        route=[]
        while b != a and b in previous:
            b,wid=previous[b]; route.append(wid)
        return list(reversed(route))

    def fault_candidates(self, source):
        """Measured bridge paths whose finite resistance separates the rails.

        Requiring all directly bypassed loads to separate avoids assigning the
        fault resistance to a supply lead. Multiple candidates require selection.
        """
        bypassed = [c for c in self.graph['components'] if c['type']=='resistor' and c['nodes'][0]==c['nodes'][1]]
        candidates=[]
        for wid in self.short_route(source):
            roots=self.partitions({wid})
            separate=lambda c: len({roots[self.terminals[t['id']]] for t in c['terminals']})==2
            if separate(source) and all(separate(c) for c in bypassed):
                candidates.append(wid)
        return candidates


def _finite(value):
    return type(value) in (float,int) and math.isfinite(value)


def _solve_model(network, source, selected=None, internal=None, fault_resistance=None):
    graph=network.graph
    roots=network.partitions({selected} if selected else ())
    names={r:f'E{i}' for i,r in enumerate(sorted(set(roots.values())))}
    node_for=lambda vertex:names[roots[vertex]]
    model_components=[]
    original_nodes={}
    for c in graph['components']:
        kind=c['type']
        if kind not in {'resistor','voltage_source','switch','capacitor'}:
            raise ValueError(f'Unsupported fault-model component: {kind}')
        if kind=='switch' and c.get('state') not in {'open','closed'}:
            raise ValueError('Switch state is not verified')
        parameters={}
        if kind in {'resistor','voltage_source','capacitor'}:
            value=c.get('value')
            provenance=c.get('value_provenance',{}).get('source')
            explicit_policy=provenance=='policy_default' and c.get('value_provenance',{}).get('user_accepted') is True
            expected={'resistor':('resistance_ohm','ohm'),'voltage_source':('voltage_v','V'),
                      'capacitor':('capacitance_f','F')}[kind]
            if (not _finite(value) or (kind!='voltage_source' and value<=0) or c.get('unit')!=expected[1]
                    or not (explicit_policy or provenance in {'ocr','user','user_input','manual','author_override',
                                          'user_supplied','user_confirmed','user_corrected'})):
                raise ValueError(f"{c['id']} needs an accepted finite value with explicit provenance")
            parameters[expected[0]]=Parameter(value=value,unit=expected[1],source=provenance,
                confidence=c.get('value_provenance',{}).get('confidence',0.0))
        terms=[Terminal(t['id'],Point(*t['source_px']),node_for(network.terminals[t['id']]),confidence=0.0) for t in c['terminals']]
        original_nodes[c['id']]=[t.node for t in terms]
        model_components.append(Component(c['id'],kind,terms,c.get('bbox_source_px',[]),parameters,c.get('state'),confidence=0.0))
    ref=original_nodes[source['id']][1]
    nodes=list(names.values())
    def resistance(cid,a,b,value,points):
        # These are explicit model elements, not newly perceived symbols.
        return Component(cid,'resistor',[Terminal(cid+'.a',Point(*points[0]),a,confidence=0.0),Terminal(cid+'.b',Point(*points[1]),b,confidence=0.0)],[],
                         {'resistance_ohm':Parameter(value,'ohm',source='user_assumption',confidence=0.0)},confidence=0.0)
    if selected:
        a,b=[node_for(v) for v in network.edges[selected]]
        path=network.wires[selected]['points']
        model_components.append(resistance('fault_path:'+selected,a,b,fault_resistance,[path[0],path[-1]]))
        if internal>0:
            source_model=next(c for c in model_components if c.id==source['id'])
            external=source_model.terminals[0].node
            virtual='internal:'+source['id'];nodes.append(virtual)
            source_model.terminals[0].node=virtual
            location=source_model.terminals[0].position.to_list()
            model_components.append(resistance('source_internal:'+source['id'],virtual,external,internal,[location,location]))
    scene=CircuitScene(reference_node=ref,nodes=[Node(n,reference=n==ref) for n in nodes],components=model_components)
    if selected:
        scene.metadata={'model_provenance':'explicit_user_assumptions',
            'fault_path_id':selected,'fault_path_source_geometry':deepcopy(network.wires[selected]['points']),
            'short_path_resistance_representation':'Lumped total resistance between the measured endpoints of this entire polyline; all other measured edges remain ideal.',
            'internal_resistance_geometry':'Abstract model element colocated at the measured source terminal; not a detected symbol.'}
    state=MNASolver(scene).solve_dc(strict=True,tolerance=TOLERANCE)
    if state.status!='solved':
        return None,{'valid':False,'reason':state.error_message},scene.to_dict(),{}
    kcl=max(map(abs,state.kcl_residuals.values()),default=0.)
    kvl=0.
    signed_power=0.
    finite=all(math.isfinite(v) for v in state.node_voltages.values())
    for c in scene.components:
        result=state.components[c.id]
        finite &= all(math.isfinite(v) for v in (result.voltage_v,result.current_a,result.power_w))
        signed_power += result.voltage_v*result.current_a
        expected=(c.parameters['resistance_ohm'].value*result.current_a if c.type=='resistor'
                  else c.parameters['voltage_v'].value if c.type=='voltage_source' else
                  result.voltage_v if c.type=='capacitor' or c.state=='open' else 0.)
        kvl=max(kvl,abs(result.voltage_v-expected))
    current_scale=max(1.,max(abs(s.current_a) for s in state.components.values()))
    voltage_scale=max(1.,max(abs(v) for v in state.node_voltages.values()))
    power_scale=max(1.,sum(abs(s.voltage_v*s.current_a) for s in state.components.values()))
    # Fundamental-cycle KVL check from oriented branch voltage drops. Build a
    # spanning forest, then check every non-tree branch against its tree route.
    adjacency=defaultdict(list)
    for c in scene.components:
        a,b=[t.node for t in c.terminals]
        drop=state.components[c.id].voltage_v
        adjacency[a].append((b,drop));adjacency[b].append((a,-drop))
    potentials={}
    for start in nodes:
        if start in potentials:continue
        potentials[start]=0.;queue=deque([start])
        while queue:
            a=queue.popleft()
            for b,drop in adjacency[a]:
                if b not in potentials:potentials[b]=potentials[a]-drop;queue.append(b)
    cycle_residual=max((abs(potentials[c.terminals[0].node]-potentials[c.terminals[1].node]
                         -state.components[c.id].voltage_v) for c in scene.components),default=0.)
    validation=dict(finite=bool(finite),kcl_residual_a=kcl,kvl_constitutive_residual_v=kvl,
                    kvl_cycle_residual_v=cycle_residual,
                    power_balance_w=abs(signed_power),**state.solver_diagnostics)
    validation['valid']=bool(finite and kcl<=TOLERANCE*current_scale and kvl<=TOLERANCE*voltage_scale
                              and cycle_residual<=TOLERANCE*voltage_scale and abs(signed_power)<=TOLERANCE*power_scale)
    # Solve wire flow from terminal injections and conductor cuts. Current on a
    # wire cycle is underdetermined: retain null rather than guess a branch flow.
    injections=defaultdict(float)
    for c in graph['components']:
        current=state.components[c['id']].current_a
        for term,sign in zip(c['terminals'],(1,-1)):
            injections[network.terminals[term['id']]] += sign*current
    currents={}
    if selected:
        current=state.components['fault_path:'+selected].current_a
        currents[selected]=current
        for vertex,sign in zip(network.edges[selected],(1,-1)):
            injections[vertex] += sign*current
    for wid,(a,b) in network.edges.items():
        if wid==selected:continue
        reached=network.reachable(a,{wid,selected})
        currents[wid]=None if b in reached else -sum(injections[v] for v in reached)
    validation['underdetermined_wire_ids']=[wid for wid,current in currents.items() if current is None]
    validation['wire_flow_complete']=not validation['underdetermined_wire_ids']
    validation['valid'] &= validation['wire_flow_complete']
    return state.to_dict() if validation['valid'] else None,validation,scene.to_dict(),currents


def analyze_grounded_circuit(graph, *, source_asset_id, mode='ideal', source_internal_resistance_ohm=None,
                             short_path_resistance_ohm=None, fault_path_id=None):
    """Return a new auditable analysis record without modifying the input graph."""
    graph=deepcopy(graph)
    record=dict(status='NEEDS_REVIEW',mode=mode,source_asset_id=source_asset_id,original_graph_id=None,
                electrical_state=None,validation=None,assumptions={},fault_paths=[],fault_path_id=None,
                short_path_wire_ids=[],graph=graph,solver_configuration={'method':'MNA','strict':True,'tolerance':TOLERANCE})
    record['correctness_checks']={k:'NOT_EVALUATED' for k in ('component','topology','parameter','physics','overlay','runtime')}
    try:
        record['original_graph_id']=hashlib.sha256(json.dumps(graph,sort_keys=True,allow_nan=False).encode()).hexdigest()
        if mode not in {'ideal','qualitative','non_ideal'}:raise ValueError('Unknown analysis mode')
        network=ConductorNetwork(graph)
        record['correctness_checks'].update(component='PASSED' if all(
            c.get('verification_status')=='VERIFIED' and c.get('geometry') for c in graph['components']) else 'NOT_EVALUATED',
            topology='PASSED')
        sources=[c for c in graph['components'] if c['type']=='voltage_source']
        if len(sources)!=1:raise ValueError('This fault route requires exactly one verified DC voltage source')
        source=sources[0]
        record['source_voltage_provenance']=deepcopy(source.get('value_provenance'))
        short=source['nodes'][0]==source['nodes'][1]
        if short:
            record['short_path_wire_ids']=network.short_route(source)
            candidates=network.fault_candidates(source)
            record['fault_path_assignment']=dict(representation='one_measured_polyline_lumped_total_resistance',
                rail_separating_candidates=candidates,
                ambiguous=len(candidates)!=1,
                diagnostic=('Multiple eligible paths require explicit selection.' if len(candidates)>1 else
                    'No single measured edge separates the rails; an additional ideal bypass or segmented path requires review.' if not candidates else
                    'Unique measured rail-separating edge.'))
            record['fault_paths']=[dict(id=wid,points=deepcopy(network.wires[wid]['points']),
                endpoint_ids=network.edges[wid],original_electrical_node=network.wires[wid]['node']) for wid in candidates]
            if fault_path_id is not None and fault_path_id not in candidates:
                raise ValueError('Selected fault path is not a verified rail-separating conductor')
            selected=fault_path_id or (candidates[0] if len(candidates)==1 else None)
            record.update(fault_path_id=selected,explanation='A continuous measured conductor joins the source terminals. '
                'An ideal nonzero voltage source cannot impose a finite voltage across that zero-resistance path. '
                'It bypasses resistive branches; a real source can overheat or be damaged.')
            if mode=='ideal':
                record['status']='IDEAL_REJECTED';return record
            if mode=='qualitative' or source_internal_resistance_ohm is None or short_path_resistance_ohm is None:
                record['status']='QUALITATIVE_FAULT';return record
            if (not _finite(source_internal_resistance_ohm) or source_internal_resistance_ohm<0 or
                    not _finite(short_path_resistance_ohm) or short_path_resistance_ohm<=0):
                record.update(status='INVALID_PARAMETERS',error='Internal resistance must be >=0 Ω; short-path resistance must be >0 Ω.');return record
            if selected is None:
                record.update(status='NEEDS_REVIEW',error='Select a verified fault path before numerical simulation.');return record
            record['assumptions']={k:dict(value=v,unit='ohm',source='user_assumption',explicit=True) for k,v in (
                ('source_internal_resistance_ohm',source_internal_resistance_ohm),('short_path_resistance_ohm',short_path_resistance_ohm))}
            record['fault_path_geometry']=deepcopy(network.wires[selected]['points'])
        elif mode!='ideal':
            record.update(error='No verified source short exists in this graph.');return record
        else:selected=None
        state,validation,model,currents=_solve_model(network,source,selected,
            source_internal_resistance_ohm,short_path_resistance_ohm)
        record.update(status=('NON_IDEAL_SOLVED' if selected else 'IDEAL_SOLVED') if state else 'NUMERICAL_REJECTED',
                      electrical_state=state,validation=validation,model=model,wire_currents_a=currents)
        record['correctness_checks'].update(parameter='PASSED',physics='PASSED' if state else 'FAILED')
        record['solver_electrical_graph']=deepcopy(model.get('circuit'))
    except (ValueError,KeyError,TypeError,OverflowError) as exc:
        record.update(status='NEEDS_REVIEW',error=str(exc),electrical_state=None)
    return record

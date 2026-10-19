"""Reusable circuit reference/grounding checks at fusion, review and compilation."""
from collections import Counter
import math


COMPONENT_TYPES={'resistor','voltage_source','dc_voltage_source','battery','dc_source','switch','open_switch','closed_switch','bulb','lamp'}


def validate_circuit_integrity(book):
    issues=[]
    def fail(code,message,owner=None):
        issues.append({'code':code,'message':message,'entity_id':owner,'stage':17})
    entities=book.entities
    eids=[e.id for e in entities]
    params=book.parameters or {}
    if not isinstance(params,dict):
        fail('INVALID_CIRCUIT_STRUCTURE','Circuit parameters must be an object.')
        return issues
    comps=params.get('components',[])
    nodes=params.get('nodes',[])
    wires=params.get('wires',[])
    # This boundary also consumes review/serialized payloads. Malformed reference
    # containers must produce review issues rather than exceptions in Counter,
    # dictionary lookup, or the compiler's downstream construction.
    if (not all(isinstance(v,list) for v in (comps,nodes,wires,book.relationships)) or
            any(not isinstance(c,dict) for c in comps) or
            any(not isinstance(w,dict) for w in wires) or
            any(not isinstance(n,(str,dict)) for n in nodes) or
            any(not isinstance(r,dict) for r in book.relationships)):
        fail('INVALID_CIRCUIT_STRUCTURE','Components, nodes, wires and relationships have invalid containers.')
        return issues
    for c in comps:
        terms=c.get('terminals',[])
        nn=c.get('nodes',[])
        if (not isinstance(terms,list) or any(not isinstance(t,dict) for t in terms) or
                not isinstance(nn,list) or any(not isinstance(n,(str,type(None))) for n in nn) or
                not all(isinstance(c.get(k,{}),dict) for k in ('geometry','provenance','value_provenance'))):
            fail('INVALID_CIRCUIT_STRUCTURE','Invalid component geometry, terminals, or provenance.',c.get('id'))
    if issues:
        return issues
    nids=[n if isinstance(n,str) else n.get('id') for n in nodes]
    cids=[c.get('id') for c in comps if isinstance(c,dict)]
    tids=[t.get('id') for c in comps if isinstance(c,dict) for t in c.get('terminals',[])]
    for label,ids in [('entity',eids),('component',cids),('terminal',tids),('node',nids),
                      ('wire',[w.get('id') for w in wires])]:
        if any(not isinstance(key,(str,type(None))) for key in ids):
            fail('INVALID_CIRCUIT_STRUCTURE',f'{label} identifiers must be strings.')
            continue
        for key,count in Counter(ids).items():
            if not key or count != 1:
                fail('DUPLICATE_OR_MISSING_ID',f'{label} ID {key!r} is missing or duplicated.',key)
    if any(i['code']=='INVALID_CIRCUIT_STRUCTURE' for i in issues):
        return issues
    for rel in book.relationships:
        for names in [('from','source_id','sourceId'),('to','target_id','targetId')]:
            refs=[rel[k] for k in names if k in rel]
            if not refs or any(not isinstance(ref,str) or ref not in eids for ref in refs) or len(set(refs)) != 1:
                fail('DANGLING_RELATIONSHIP',f'Relationship endpoint {refs} does not resolve consistently.')
    for e in entities:
        if e.type in COMPONENT_TYPES and e.id not in cids:
            fail('MISSING_PHYSICAL_COMPONENT',f'{e.id} has no verified physical symbol and terminal graph.',e.id)
        for ref in e.evidence_refs:
            if ref not in book.evidence and ref != book.figure_id:
                fail('DANGLING_EVIDENCE',f'{e.id} evidence {ref} does not resolve.',e.id)
    strict=(book.geometry or {}).get('circuit_validation') is not None
    width=(book.geometry or {}).get('width',0)
    height=(book.geometry or {}).get('height',0)
    def point_valid(point):
        return (isinstance(point,(list,tuple)) and len(point)==2 and
                all(isinstance(v,(int,float)) and math.isfinite(v) for v in point) and
                0<=point[0]<width and 0<=point[1]<height)
    wire_by_id={w.get('id'):w for w in wires}
    for c in comps:
        if not isinstance(c,dict):
            fail('INVALID_COMPONENT','Circuit component must be an object.');continue
        cid=c.get('id')
        if cid not in eids:
            fail('DANGLING_COMPONENT',f'Component {cid} has no semantic entity.',cid)
        nn=c.get('nodes',[])
        if len(nn)!=2 or any(n not in nids for n in nn):
            fail('DANGLING_COMPONENT_NODE',f'{cid} requires two declared terminal nodes.',cid)
        if c.get('type')=='switch' and (c.get('state') not in {'open','closed'} or not c.get('state_verified')):
            fail('SWITCH_STATE_UNVERIFIED',f'Verify the visible state of {cid}.',cid)
        tt=c.get('terminals',[])
        if len(tt)!=2:
            fail('MISSING_TERMINALS',f'{cid} requires two measured terminals.',cid)
        for i,t in enumerate(tt):
            if t.get('node') not in nids or (len(nn)==2 and (i>=2 or t.get('node')!=nn[i])):
                fail('DANGLING_TERMINAL_NODE',f'{t.get("id")} has an inconsistent node.',cid)
            if strict and (not point_valid(t.get('source_px')) or t.get('wire_id') not in wire_by_id or
                           wire_by_id[t['wire_id']].get('node')!=t.get('node')):
                fail('TERMINAL_ATTACHMENT_INVALID',f'{cid} has an invalid source terminal or wire attachment.',cid)
        if strict and c.get('verification_status')!='VERIFIED':
            fail('GEOMETRY_UNVERIFIED',f'{cid} has not passed raster/terminal verification.',cid)
        if strict:
            geometry=c.get('geometry',{})
            bbox=geometry.get('bbox_source_px',[])
            if (not point_valid(geometry.get('center_source_px')) or len(bbox)!=4 or
                    not point_valid(bbox[:2]) or not point_valid(bbox[2:]) or
                    bbox[0]>=bbox[2] or bbox[1]>=bbox[3]):
                fail('INVALID_SOURCE_GEOMETRY',f'{cid} has invalid native coordinates.',cid)
            provenance=c.get('provenance',{})
            if provenance.get('source_asset_id')!=book.source_asset_id or provenance.get('figure_id')!=book.figure_id:
                fail('SOURCE_IDENTITY_MISMATCH',f'{cid} geometry belongs to a different source.',cid)
            for ref in c.get('value_provenance',{}).get('evidence_refs',[]):
                if ref not in book.evidence or ref not in c.get('evidence_refs',[]):
                    fail('DANGLING_PARAMETER_EVIDENCE',f'{cid} value has no owned evidence {ref}.',cid)
        for ref in c.get('evidence_refs',[]):
            if ref not in book.evidence:
                fail('DANGLING_EVIDENCE',f'{cid} evidence {ref} does not resolve.',cid)
    for w in wires:
        if w.get('node') not in nids:
            fail('DANGLING_WIRE_NODE',f'Wire {w.get("id")} has no declared node.')
        if strict and (len(w.get('points',[]))<2 or not all(point_valid(p) for p in w.get('points',[]))):
            fail('INVALID_SOURCE_GEOMETRY',f'Wire {w.get("id")} has invalid source coordinates.')
    if comps and params.get('reference_node') not in nids:
        fail('INVALID_REFERENCE_NODE','Circuit reference node is missing or undeclared.')
    if strict:
        incidence=Counter(n for c in comps for n in c.get('nodes',[]))
        if any(incidence[n]<2 for n in nids):
            fail('DISCONNECTED_TERMINAL','A conductor island ends without a second physical terminal.')
        reached={nids[0]} if nids else set()
        for _ in nids:
            for c in comps:
                if reached.intersection(c.get('nodes',[])):
                    reached.update(c.get('nodes',[]))
        if set(nids)-reached:
            fail('DISCONNECTED_CIRCUIT','Separate component networks require review.')
        validation=book.geometry['circuit_validation']
        if not validation.get('geometry') or not validation.get('topology'):
            fail('GROUNDING_INCOMPLETE','Review unresolved physical symbols or conductor paths before compilation.')
    return issues

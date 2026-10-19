"""Electrical nodes from verified conductor paths, independent of page layout."""
from copy import deepcopy


def build_conductor_graph(paths, components):
    paths = [deepcopy(p) for p in paths if p.get('verification_status') == 'VERIFIED']
    parent={p['id']:p['id'] for p in paths}

    def find(k):
        while parent[k] != k:
            parent[k]=parent[parent[k]]
            k=parent[k]
        return k

    ends={}
    for p in paths:
        for end in p['ends']:
            if not end:
                continue
            if end in ends:
                parent[find(p['id'])]=find(ends[end])
            ends[end]=p['id']
    # Retain only conductor islands attached to measured terminals. An isolated
    # current arrow or caption stroke is diagnostic ink, not a circuit wire.
    anchors={a['wire_id'] for c in components for a in c.get('terminal_attachments',[]) if a}
    roots={find(k) for k in anchors if k in parent}
    mapping={k:f'N{i+1}' for i,k in enumerate(sorted(roots))}
    wire_nodes={p['id']:mapping[find(p['id'])] for p in paths if find(p['id']) in roots}
    wires=[]
    for p in paths:
        if p['id'] not in wire_nodes:
            continue
        wires.append({'id':p['id'],'node':wire_nodes[p['id']],
                      'polyline_source_px':p['points'],'points':p['points'],
                      'verification_status':'VERIFIED','provenance':{'source':'diagram_measurement',
                       'support_fraction':p['support_fraction'],'max_gap_px':p['max_gap_px']}})
    return [{'id':n} for n in mapping.values()], wires, wire_nodes

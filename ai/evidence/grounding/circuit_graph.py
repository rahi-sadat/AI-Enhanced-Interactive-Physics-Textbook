"""Electrical nodes from verified conductor paths, independent of page layout."""
from copy import deepcopy


def build_geometric_conductor_graph(wires, components, *, junctions=(), crossings=(), source_asset_id=None):
    """Preserve measured edges/terminals before ideal electrical contraction."""
    vertices={}
    edges=[]
    endpoints={}
    for wire in wires:
        keys=[]
        for side,end in enumerate(wire['ends']):
            key=f'junction:{end}' if end else f'{wire["id"]}:{side}'
            point=wire['points'][0 if side==0 else -1]
            if key in vertices and vertices[key]['source_px']!=point:
                raise ValueError('Conflicting source coordinates for conductor vertex')
            vertices[key]=dict(id=key,source_px=deepcopy(point),measured_endpoint_id=end)
            keys.append(key)
        endpoints[wire['id']]=keys
        edges.append(dict(id=wire['id'],vertices=keys,polyline_source_px=deepcopy(wire['points']),
                          verification_status=wire['verification_status'],provenance=deepcopy(wire['provenance'])))
    terminals=[]
    for component in components:
        for term in component['terminals']:
            wid,end=term.get('wire_id'),term.get('wire_end')
            if wid not in endpoints or end not in (0,-1):continue
            terminals.append(dict(id=term['id'],component_id=component['id'],
                vertex=endpoints[wid][0 if end==0 else 1],source_px=deepcopy(term['source_px']),
                wire_id=wid,wire_end=end,attachment_distance_px=term.get('attachment_distance_px')))
    return dict(schema_version=1,coordinate_space='source_px',source_asset_id=source_asset_id,
                vertices=list(vertices.values()),edges=edges,terminals=terminals,
                junction_evidence=deepcopy(junctions),crossing_evidence=deepcopy(crossings),
                contraction='none',provenance={'source':'diagram_measurement'})


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
                      'ends':deepcopy(p['ends']),
                      'uncertainty_px':p.get('uncertainty_px'),
                      'polyline_source_px':p['points'],'points':p['points'],
                      'verification_status':'VERIFIED','provenance':{'source':'diagram_measurement',
                       'support_fraction':p['support_fraction'],'max_gap_px':p['max_gap_px']}})
    return [{'id':n} for n in mapping.values()], wires, wire_nodes

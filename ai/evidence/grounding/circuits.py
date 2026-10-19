"""PR-06 DC Circuit Subtype Evidence Grounder.

Grounds DC linear circuit entities:
  - Resistors, voltage sources, ground, switches
  - Component terminals (one-to-one candidate assignment)
  - Continuous wire paths and junction nodes
  - Topological connectivity graph (nodes N1, N2, ...)
  - Component-specific parameter association (R1 -> 10 Ω, V1 -> 12 V)

Strict Invariants:
  - Visual proximity is NEVER electrical connectivity.
  - Components are connected ONLY when verified by wire/junction path continuity.
  - Never map multiple semantic components (e.g. R1, R2, V1) to a single CV component.
  - Never use token-ID parameter keys as a substitute for component association.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import cv2
import numpy as np

from shared.schemas.evidence import (
    AssociationState,
    EntityGroundingDiagnostic,
    EvidenceMethod,
    EvidenceRecord,
    GroundingState,
    OCRExtractionResult,
    OCRToken,
    ParameterAssociationResult,
    ParsedPhysicalValueCandidate,
    SegmentationResult,
    SourceBBox,
    SourceLine,
    SourcePoint,
)
from shared.schemas.ingestion import (
    BookEntity,
    BookIR,
    BookIRStatus,
    PhysicalValue,
    ProvenanceRecord,
)
from ai.evidence.grounding.base import GroundingOutcome
from ai.evidence.grounding.physical_value_parser import parse_physical_value_candidate
from ai.resolution.evaluator import ReadinessEvaluator

logger = logging.getLogger(__name__)


def parse_and_cluster_circuit_tokens(tokens: List[OCRToken], association_radius: float = 220.0) -> List[Dict[str, Any]]:
    """Extract and cluster semantic circuit component tokens into coherent component specifications.
    
    Groups designators (e.g. 'R1', 'V1') with their adjacent physical values (e.g. '100Ω', '24 V').
    Filters out diagram titles, figure numbers, and non-component annotations.
    """
    parsed = []
    ignored_keywords = [
        'parallel circuit', 'combination circuit', 'series-parallel', 'series circuit',
        'fig.', 'figure', 'dc circuit', 'circuit diagram'
    ]

    SUBSCRIPT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")

    for tok in tokens:
        raw = tok.raw_text.strip()
        raw_norm = raw.translate(SUBSCRIPT_MAP)
        lower = raw_norm.lower()
        if any(ik in lower for ik in ignored_keywords):
            continue

        b = tok.bbox_source_px
        if not b:
            continue
        cx = b.x + b.width / 2.0
        cy = b.y + b.height / 2.0

        ptype = None
        pdesig = None
        pval = None
        punit = None

        m_r_desig = re.fullmatch(r'^[Rr](\d+)$', raw_norm)
        m_v_desig = re.fullmatch(r'^[Vv](\d+)$', raw_norm)

        m_r_comb = re.match(r'^[Rr](\d+?)\s*(?:=|\s)?\s*(\d+(?:\.\d+)?)\s*([kK]?[Ωω]|ohm|kohm)$', raw_norm, re.IGNORECASE)
        m_v_comb = re.match(r'^[Vv](\d*)\s*(?:=|\s)?\s*(\d+(?:\.\d+)?)\s*[vV]$', raw_norm, re.IGNORECASE)

        m_r_val = re.fullmatch(r'^(\d+(?:\.\d+)?)\s*([kK]?[Ωω]|ohm|kohm)$', raw_norm, re.IGNORECASE)
        m_v_val = re.fullmatch(r'^(\d+(?:\.\d+)?)\s*[vV]$', raw_norm, re.IGNORECASE)

        if m_r_desig:
            ptype = 'resistor'
            pdesig = f"R{m_r_desig.group(1)}"
        elif m_v_desig:
            ptype = 'voltage_source'
            pdesig = f"V{m_v_desig.group(1)}"
        elif m_r_comb:
            ptype = 'resistor'
            pdesig = f"R{m_r_comb.group(1)}"
            pval = float(m_r_comb.group(2))
            punit = 'ohm'
            if 'k' in m_r_comb.group(3).lower():
                pval *= 1000.0
        elif m_v_comb:
            ptype = 'voltage_source'
            pdesig = f"V{m_v_comb.group(1)}" if m_v_comb.group(1) else "V1"
            pval = float(m_v_comb.group(2))
            punit = 'V'
        elif m_r_val:
            ptype = 'resistor'
            pval = float(m_r_val.group(1))
            punit = 'ohm'
            if 'k' in m_r_val.group(2).lower():
                pval *= 1000.0
        elif m_v_val:
            ptype = 'voltage_source'
            pval = float(m_v_val.group(1))
            punit = 'V'
        elif raw in ('+', '-', '十'):
            ptype = 'polarity'
            pdesig = '+' if raw in ('+', '十') else '-'
        else:
            m_num = re.search(r'^(\d+(?:\.\d+)?)\s*([kK]?[Ωω]|ohm|kohm|[vV]|volt)?$', raw_norm, re.IGNORECASE)
            if m_num:
                clean_num = m_num.group(1)
                unit_part = (m_num.group(2) or '').lower()
                has_unit = bool(unit_part or ('k' in lower and re.search(r'\d+[kK]', raw_norm)))
                mult = 1000.0 if 'k' in unit_part or 'k' in lower else 1.0
                try:
                    pval = float(clean_num) * mult
                    punit = 'V' if any(u in unit_part for u in ('v', 'volt')) else 'ohm'
                    ptype = 'value_only' if has_unit else 'raw_number'
                except ValueError:
                    pass

        if ptype:
            parsed.append({
                'tok': tok,
                'raw': raw,
                'type': ptype,
                'desig': pdesig,
                'val': pval,
                'unit': punit,
                'bbox': b,
                'cx': cx,
                'cy': cy,
            })

    # Cluster parsed tokens into distinct components
    components = []
    used: Set[int] = set()

    # Pass 1: Tokens with both designator and value (e.g. "R1 = 10 Ω", "V=6 V")
    for i, p in enumerate(parsed):
        if p['type'] in ('voltage_source', 'resistor') and p['desig'] and p['val'] is not None:
            used.add(i)
            b = p['tok'].bbox_source_px
            lbl_box = [float(b.x), float(b.y), float(b.width), float(b.height)] if b else None
            components.append({
                'id': p['desig'],
                'type': p['type'],
                'val': p['val'],
                'unit': p['unit'],
                'tokens': [p['tok']],
                'cx': p['cx'],
                'cy': p['cy'],
                'bbox': p['bbox'],
                'label_bbox': lbl_box,
            })

    # Pass 2: Designator tokens seeking nearby values
    for i, p in enumerate(parsed):
        if i in used or p['desig'] is None or p['type'] == 'polarity':
            continue
        c_type = p['type']
        desig = p['desig']
        val = p['val']
        unit = p['unit']
        c_tokens = [p['tok']]
        used.add(i)

        best_j = None
        min_dist = float('inf')
        for j, q in enumerate(parsed):
            if j in used or q['type'] == 'polarity':
                continue
            if q['val'] is not None and q['desig'] is None and q['type'] in (c_type, 'value_only'):
                dist = ((p['cx'] - q['cx']) ** 2 + (p['cy'] - q['cy']) ** 2) ** 0.5
                if dist < association_radius and dist < min_dist:
                    min_dist = dist
                    best_j = j

        if best_j is not None:
            q = parsed[best_j]
            val = q['val']
            unit = q['unit']
            c_tokens.append(q['tok'])
            used.add(best_j)

        xs = [t.bbox_source_px.x for t in c_tokens if t.bbox_source_px]
        ys = [t.bbox_source_px.y for t in c_tokens if t.bbox_source_px]
        x2s = [t.bbox_source_px.x + t.bbox_source_px.width for t in c_tokens if t.bbox_source_px]
        y2s = [t.bbox_source_px.y + t.bbox_source_px.height for t in c_tokens if t.bbox_source_px]
        if xs:
            bx = min(xs)
            by = min(ys)
            bw = max(x2s) - min(xs)
            bh = max(y2s) - min(ys)
            bbox = SourceBBox(bx, by, bw, bh)
            cx = bx + bw / 2.0
            cy = by + bh / 2.0
            lbl_box = [float(bx), float(by), float(bw), float(bh)]
        else:
            bbox = p['bbox']
            cx, cy = p['cx'], p['cy']
            b = p['tok'].bbox_source_px
            lbl_box = [float(b.x), float(b.y), float(b.width), float(b.height)] if b else None

        components.append({
            'id': desig,
            'type': c_type,
            'val': val,
            'unit': unit,
            'tokens': c_tokens,
            'cx': cx,
            'cy': cy,
            'bbox': bbox,
            'label_bbox': lbl_box,
        })

    # Pass 3: Standalone value tokens without designators
    existing_ids = {c['id'] for c in components}
    for i, p in enumerate(parsed):
        if i in used or p['type'] == 'polarity':
            continue
        c_type = p['type']
        if c_type == 'value_only':
            raw_u = (p.get('unit') or '').lower()
            if any(u in raw_u for u in ('ohm', 'kohm', 'mohm', 'ω', 'v')) or (p.get('desig') and p['desig'][0] in ('R', 'V')):
                c_type = 'voltage_source' if any(u in raw_u for u in ('v', 'volt')) else 'resistor'
            else:
                continue
        elif c_type == 'raw_number':
            continue

        if any(c['type'] == c_type and
               ((p['cx'] - c['cx']) ** 2 + (p['cy'] - c['cy']) ** 2) ** 0.5 < association_radius
               for c in components):
            # Standalone OCR values near an identified component are likely
            # duplicate readings, not extra physical circuit elements.
            continue

        prefix = "V" if c_type == 'voltage_source' else "R"
        idx = 1
        while f"{prefix}{idx}" in existing_ids:
            idx += 1
        desig = f"{prefix}{idx}"
        existing_ids.add(desig)
        used.add(i)
        b = p['tok'].bbox_source_px
        lbl_box = [float(b.x), float(b.y), float(b.width), float(b.height)] if b else None
        components.append({
            'id': desig,
            'type': c_type,
            'val': p['val'],
            'unit': p['unit'] or ('V' if c_type == 'voltage_source' else 'ohm'),
            'tokens': [p['tok']],
            'cx': p['cx'],
            'cy': p['cy'],
            'bbox': p['bbox'],
            'label_bbox': lbl_box,
        })

    return components


class CircuitGrounder:
    """Assign semantics to verified symbols; conductor paths alone define nodes."""
    domain = "circuits"
    subtype = "dc_linear"

    def supports(self, domain, subtype):
        return domain == self.domain and subtype in ("dc_linear", "circuit", "dc_circuit", "resistors")

    def ground(self, book_ir, cv_candidates, ocr_result=None, seg_result=None,
               source_width=0, source_height=0):
        from copy import deepcopy
        book = deepcopy(book_ir)
        book.geometry = dict(book.geometry or {}, width=source_width, height=source_height,
                             coordinate_space="source_px")
        return self.fuse(book, cv_candidates, seg_result, ocr_result)

    def fuse(self, book_ir, cv_candidates, segmentation_candidates=None, ocr_result=None):
        from scipy.optimize import linear_sum_assignment
        from .circuit_graph import build_conductor_graph
        from .circuit_integrity import COMPONENT_TYPES, validate_circuit_integrity
        book=book_ir
        verified=[c for c in cv_candidates.get('components',[])
                  if c.get('verification_status')=='VERIFIED']
        gate=cv_candidates.get('geometry_validation',{})
        # Direct callers cannot bypass the pre-grounding boundary with arbitrary
        # boxes, confidence scores, or a list of hand-supplied wires.
        if not gate:
            verified=[]
        diagnostics=[]
        evidence={}
        tokens=ocr_result.tokens if ocr_result else []
        values=[]
        for tok in tokens:
            eid=f'ev_ocr_{tok.id}'
            evidence[eid]=EvidenceRecord(id=eid,method=EvidenceMethod.OCR,
                source_asset_id=book.source_asset_id,figure_id=book.figure_id,
                confidence=tok.confidence,verified=False,provider=ocr_result.provider,
                payload={'raw_text':tok.raw_text,'bbox':tok.bbox_source_px.to_dict() if tok.bbox_source_px else None})
            values.extend(parse_physical_value_candidate(tok))
        clusters=parse_and_cluster_circuit_tokens(tokens, association_radius=np.hypot(
            book.geometry.get('width',0),book.geometry.get('height',0))*.15)
        semantics=[e for e in book.entities if e.type in COMPONENT_TYPES]
        normalize=lambda kind: ('voltage_source' if kind in {'battery','dc_source','dc_voltage_source'} else
                                'switch' if kind in {'open_switch','closed_switch'} else kind)
        # First associate semantic identities with OCR designators. VLM numbers
        # are never consumed as values. An unlabelled singleton can use the one
        # compatible OCR cluster, but duplicate or ambiguous designators cannot.
        labels={}
        used=set()
        for e in semantics:
            compatible=[(i,c) for i,c in enumerate(clusters) if normalize(e.type)==c['type'] and i not in used]
            designator=re.search(r'\b([RV]\d+)\b',e.label or '',re.I)
            matches=[(i,c) for i,c in compatible if designator and c['id'].lower()==designator[1].lower()]
            if not matches and len(compatible)==1 and sum(normalize(x.type)==normalize(e.type) for x in semantics)==1:
                matches=compatible
            if len(matches)==1:
                i,c=matches[0]; labels[e.id]=c; used.add(i)
        # Global one-to-one assignment: type mismatch forbidden; OCR is only a
        # distance/identity cue, never the returned center or terminal geometry.
        costs=np.full((len(semantics),len(verified)+len(semantics)),1e6)
        scale=max(1,np.hypot(book.geometry.get('width',0),book.geometry.get('height',0)))
        for i,e in enumerate(semantics):
            cluster=labels.get(e.id)
            for j,c in enumerate(verified):
                if normalize(e.type)!=c['type']:
                    continue
                if cluster:
                    center=c['center']
                    distance=np.hypot(center.x-cluster['cx'],center.y-cluster['cy'])
                    if distance < scale*.25:
                        costs[i,j]=distance/scale
                elif sum(normalize(x.type)==normalize(e.type) for x in semantics)==1 and sum(x['type']==c['type'] for x in verified)==1:
                    costs[i,j]=.2
        assigned={}
        if semantics:
            rows,cols=linear_sum_assignment(costs)
            optimum=costs[rows,cols].sum()
            for i,j in zip(rows,cols):
                if j>=len(verified) or costs[i,j]>=1e5:
                    continue
                alternative=costs.copy();alternative[i,j]=1e6
                ar,ac=linear_sum_assignment(alternative)
                if alternative[ar,ac].sum()-optimum < .015:
                    continue  # Two nearly equivalent physical assignments need review.
                assigned[semantics[i].id]=verified[j]
        nodes,wires,wire_nodes=build_conductor_graph(cv_candidates.get('wire_paths',[]),list(assigned.values()))
        components=[]
        for e in semantics:
            c=assigned.get(e.id)
            cluster=labels.get(e.id)
            checks={'physical_symbol':c is not None,'orientation':c is not None,
                    'terminals':False,'wire_connected':False,'parameter_value':False,'state_verified':False}
            refs=[]
            if c:
                ev=f'ev_geometry_{c["id"]}'
                refs=[ev]+[f'ev_ocr_{t.id}' for t in (cluster or {}).get('tokens',[])]
                evidence[ev]=EvidenceRecord(id=ev,method=EvidenceMethod.CLASSICAL_CV,
                    source_asset_id=book.source_asset_id,figure_id=book.figure_id,verified=True,
                    confidence=.9,
                    provider='circuit_geometry_validator',payload={
                        'bbox':c['bbox'].to_dict(),'terminals':[c['terminal_1'].to_dict(),c['terminal_2'].to_dict()],
                        'orientation':c['orientation'],'uncertainty_px':c['uncertainty_px'],
                        'terminal_attachments':c['terminal_attachments'],'state':c.get('state')})
                terms=[]
                for i,(t,a) in enumerate(zip([c['terminal_1'],c['terminal_2']],c['terminal_attachments'])):
                    nid=wire_nodes.get(a['wire_id']) if a else None
                    terms.append({'id':f'{e.id}.t{i+1}','source_px':[float(t.x),float(t.y)],
                                  'node':nid,'wire_id':a['wire_id'] if a else None})
                b=c['bbox'];center=c['center']
                geometry={'center_source_px':[float(center.x),float(center.y)],
                          'bbox_source_px':[float(b.x),float(b.y),float(b.x_max),float(b.y_max)],
                          'orientation':c['orientation'],'angle_deg':c['angle_deg'],
                          'symbol_path_source_px':c['symbol_path'],'uncertainty_px':c['uncertainty_px']}
                if c.get('arm_source_px'):
                    geometry['arm_source_px']=c['arm_source_px']
                if cluster:
                    geometry['label_bbox_source_px']=cluster['label_bbox']
                component={'id':e.id,'type':c['type'],'label':cluster['id'] if cluster else e.label,
                           'nodes':[t['node'] for t in terms],'terminals':terms,'geometry':geometry,
                           'bbox_source_px':geometry['bbox_source_px'],'verification_status':'VERIFIED',
                           'evidence_refs':refs,'provenance':c['provenance']}
                if c['type']=='switch':
                    component.update(state=c['state'],state_verified=True)
                elif cluster and cluster['val'] is not None:
                    component.update(value=cluster['val'],unit=cluster['unit'],
                                     value_provenance={'source':'ocr','evidence_refs':refs[1:]})
                    book.parameter_provenance[e.id]=ProvenanceRecord(source='ocr',evidence_refs=refs[1:],
                        notes='OCR value assigned to this verified physical symbol; geometry has separate CV provenance.')
                e.position_source_px={'x':float(center.x),'y':float(center.y),'provenance':c['provenance']}
                e.geometry=geometry
                e.evidence_refs=list(dict.fromkeys(e.evidence_refs+refs))
                e.attributes.update(geometry_candidate_id=c['id'],grounding_state='grounded')
                checks.update(terminals=len(terms)==2,wire_connected=all(t['node'] for t in terms),
                              parameter_value=c['type']=='switch' or component.get('value') is not None,
                              state_verified=c['type']!='switch' or component.get('state_verified',False))
                components.append(component)
            complete=all(checks.values())
            if not complete:
                e.attributes['grounding_state']='unresolved'
                if not c:
                    e.position_source_px=None
                    e.geometry=None
            diagnostics.append(EntityGroundingDiagnostic(entity_id=e.id,
                grounding_state=GroundingState.GROUNDED if complete else GroundingState.UNRESOLVED,
                supporting_evidence=refs,checks=checks,notes='' if complete else
                'Review '+', '.join(k for k,v in checks.items() if not v)))
        book.parameters.update(components=components,nodes=nodes,wires=wires,
            reference_node=next((c['nodes'][1] for c in components if c['type']=='voltage_source'),None))
        book.evidence.update({k:v.to_dict() for k,v in evidence.items()})
        geometry_ok=bool(semantics) and len(assigned)==len(semantics) and len(assigned)==len(cv_candidates.get('components',[]))
        topology_ok=geometry_ok and bool(nodes) and all(all(c['nodes']) for c in components)
        book.geometry['circuit_validation']={'semantic':book.isPhysics is True,
            'geometry':geometry_ok,'topology':topology_ok,'referential_integrity':False,'physics_readiness':False}
        book.geometry['circuit_topology']={'verified_connectivity':topology_ok,'node_count':len(nodes)}
        book.provenance['grounding_diagnostics']=[d.to_dict() for d in diagnostics]
        book.provenance['candidate_parameters']=[c.to_dict() for c in values]
        book.provenance['semantic_geometry_identity_map']={key:c['id'] for key,c in assigned.items()}
        book.provenance['circuit_geometry_issues']=cv_candidates.get('validation_issues',[])
        for key in ('components','nodes'):
            book.parameter_provenance[key]=ProvenanceRecord(source='diagram_measurement',
                evidence_refs=list(evidence),notes='Verified physical symbols and continuous conductor graph.')
        issues=validate_circuit_integrity(book)
        if any(i['code'] in {'DISCONNECTED_TERMINAL','DISCONNECTED_CIRCUIT','TERMINAL_ATTACHMENT_INVALID'} for i in issues):
            book.geometry['circuit_validation']['topology']=False
            book.geometry['circuit_topology']['verified_connectivity']=False
        book.geometry['circuit_validation']['referential_integrity']=not issues
        book.review_issues=issues
        book.status=BookIRStatus.NEEDS_REVIEW
        book.status_notes='Review circuit geometry, connections, values, or state.'
        readiness=ReadinessEvaluator.evaluate(book,mutate_status=True)
        book.geometry['circuit_validation']['physics_readiness']=readiness.ready
        associations=[]
        for value in values:
            owners=[c for c in components if f'ev_ocr_{value.token_id}' in c.get('value_provenance',{}).get('evidence_refs',[])]
            owner=owners[0]['id'] if len(owners)==1 else None
            associations.append(ParameterAssociationResult(candidate_id=value.token_id,
                target_entity_id=owner,target_quantity=value.quantity_candidate or 'unknown',
                value=value.numeric_value,unit=value.canonical_unit or value.raw_unit or '',
                state=AssociationState.ASSOCIATED if owner else AssociationState.REJECTED,
                supporting_evidence=[f'ev_ocr_{value.token_id}'],confidence=value.confidence,
                association_checks={'verified_physical_owner':owner is not None},
                diagnostics={'reason':'Verified symbol assignment' if owner else 'No unique verified physical owner'}))
        return GroundingOutcome(grounded_book_ir=book,diagnostics=diagnostics,
                                new_evidence_records=evidence,candidate_parameters=values,parameter_associations=associations)

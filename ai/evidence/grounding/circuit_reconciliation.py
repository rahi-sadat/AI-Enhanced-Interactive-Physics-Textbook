"""Local detector/CV reconciliation from independently measured source ink.

No confidence or semantic class can override incompatible raster features. Any
refined interpretation must already have passed wire/terminal validation; this
boundary rechecks its strokes and features against the immutable source raster.
"""
import cv2
import numpy as np

from ai.evidence.cv.circuit_body_mask import body_paths
from ai.evidence.cv.circuit_paths import sample_support


def inspect_symbol(candidate, raster, wire_paths):
    stroke = candidate.get('uncertainty_px',1)
    paths = body_paths(candidate)
    checks = {'verified_geometry':candidate.get('verification_status')=='VERIFIED',
              'accepted_body_mask':candidate.get('body_mask_status')=='ACCEPTED',
              'raster_available':raster is not None}
    checks['supported_strokes'] = raster is not None and bool(paths) and all(
        len(p)>=2 and sample_support(raster,p,stroke*.35)['support_fraction']>=.95
        for p in (paths[:1] if candidate['type']=='switch' else paths))
    kind = candidate['type']
    feature = False
    if kind in {'voltage_source','capacitor'}:
        lengths = np.array([max(w,h) for x,y,w,h in candidate.get('plates',[])])
        if kind=='capacitor':
            feature = len(lengths)==2 and .85<=lengths[1]/lengths[0]<=1/.85
        elif len(lengths)==2:
            feature = max(lengths)/min(lengths)>=1.20
        elif len(lengths)==3:
            feature = lengths[1]*1.15<min(lengths[0],lengths[2]) or lengths[1]>max(lengths[0],lengths[2])*1.15
        elif len(lengths)==4:
            feature = np.all(lengths[::2]>lengths[1::2]*1.15) or np.all(lengths[1::2]>lengths[::2]*1.15)
        if kind=='voltage_source':
            feature = feature and candidate.get('polarity_verified',False)
    elif kind=='resistor' and paths:
        if candidate.get('notation')=='rectangle':
            feature = len(paths[0])==5
        elif candidate.get('notation')=='zigzag':
            points=np.array(paths[0]);axis=1 if candidate['orientation']=='horizontal' else 0
            signs=np.sign(np.diff(points[:,axis]));signs=signs[signs!=0]
            feature = np.count_nonzero(signs[1:]!=signs[:-1])>=3
    elif kind=='switch':
        feature = candidate.get('state') in {'open','closed'} and len(candidate.get('contacts',[]))==2
    checks['symbol_specific_features'] = bool(feature)
    wires={p['id']:p for p in wire_paths}
    attachments=candidate.get('terminal_attachments',[])
    checks['supported_terminal_attachments']=len(attachments)==2 and raster is not None
    for term, attachment in zip((candidate['terminal_1'],candidate['terminal_2']),attachments):
        path=wires.get((attachment or {}).get('wire_id'))
        end=(attachment or {}).get('end')
        if not path or end not in (0,-1):
            checks['supported_terminal_attachments']=False
        elif raster is not None:
            support=sample_support(raster,[[term.x,term.y],path['points'][end]],
                candidate.get('contact_radius_px',stroke*.3) if kind=='switch' else stroke*.3)
            checks['supported_terminal_attachments'] &= support['support_fraction']>=.95
    return checks


def reconcile_candidate(region, expected_type, candidate, cv_candidates):
    """Return an assignment score only after independent evidence agrees."""
    ink=cv_candidates.get('original_binary')
    checks=inspect_symbol(candidate,ink,cv_candidates.get('wire_paths',[]))
    overlap=float(region.iou(candidate['bbox']))
    checks['type_agreement']=expected_type==candidate['type']
    checks['body_bbox_agreement']=overlap>=.20  # unchanged; never relaxed to force R4
    support_fraction=0.
    if ink is not None:
        mask=np.zeros_like(ink)
        for points in body_paths(candidate):
            cv2.polylines(mask,[np.rint(points).astype(np.int32)],False,1,max(1,int(candidate['uncertainty_px'])))
        ys,xs=np.where((mask!=0)&(ink!=0))
        if len(xs):
            pad=candidate['uncertainty_px']
            support_fraction=float(np.mean((xs>=region.x-pad)&(xs<=region.x_max+pad)&
                                           (ys>=region.y-pad)&(ys<=region.y_max+pad)))
    checks['measured_body_agreement']=support_fraction>=.65
    record=dict(candidate_id=candidate['id'],source_region=region.to_dict(),
        candidate_type=candidate['type'],expected_type=expected_type,body_iou=overlap,
        measured_body_fraction=support_fraction,checks=checks,
        refinement_evidence=candidate.get('refinement_evidence',[]),
        status='SUPPORTED' if all(checks.values()) else 'UNRESOLVED')
    return (1-overlap if all(checks.values()) else None),record

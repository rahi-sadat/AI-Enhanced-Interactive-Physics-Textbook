"""Pre-grounding boundary: validate geometry against native raster evidence."""
from copy import deepcopy

import numpy as np

from .circuit_paths import raster, sample_support


class CircuitGeometryValidator:
    def validate(self, image, candidates, *, source_asset_id=None, figure_id=None):
        out = dict(candidates)
        h,w = image.shape[:2]
        _,ink,stroke = raster(image)
        issues=[]
        paths=[]
        for path in candidates.get('wire_paths',[]):
            p=deepcopy(path)
            support=sample_support(ink,p['points'],stroke*.25)
            bounds=all(0 <= x < w and 0 <= y < h for x,y in p['points'])
            through_body=False
            for a,b in zip(p['points'],p['points'][1:]):
                samples=np.linspace(a,b,max(2,int(np.linalg.norm(np.subtract(b,a)))+1))
                for component in candidates.get('components',[]):
                    box=component['bbox']
                    inside=(samples[:,0]>box.x+stroke)&(samples[:,0]<box.x_max-stroke)&(samples[:,1]>box.y+stroke)&(samples[:,1]<box.y_max-stroke)
                    through_body |= bool(inside.any())
            valid=bounds and not through_body and support['support_fraction'] >= .98 and support['max_gap_px'] <= max(1,stroke*.4)
            p.update(verification_status='VERIFIED' if valid else 'REJECTED',**support)
            if valid:
                paths.append(p)
            else:
                issues.append(dict(candidate_id=p['id'],stage=14,status='REJECTED',code='UNSUPPORTED_WIRE_PATH',
                                   message='Wire path leaves source bounds, crosses a component body, or crosses unsupported pixels.',**support))
        verified=[]
        for c in candidates.get('components',[]):
            c=deepcopy(c)
            b=c['bbox']
            terms=[c['terminal_1'],c['terminal_2']]
            reasons=[]
            if not (0<=b.x<b.x_max<=w and 0<=b.y<b.y_max<=h):
                reasons.append('out_of_source_bounds')
            if not c.get('symbol_path') or c.get('type') not in {'resistor','voltage_source','switch'}:
                reasons.append('missing_symbol_identity_evidence')
            body_paths=[]
            if c.get('type')=='resistor':
                body=list(c.get('symbol_path',[]))
                if body and c.get('notation')=='rectangle': body.append(body[0])
                body_paths=[body]
            elif c.get('type')=='switch':
                body_paths=[c.get('arm_source_px',[])]
            elif c.get('type')=='voltage_source':
                for x,y,pw,ph in c.get('plates',[]):
                    body_paths.append([[x+(pw-1)/2,y],[x+(pw-1)/2,y+ph-1]] if ph>pw else
                                      [[x,y+(ph-1)/2],[x+pw-1,y+(ph-1)/2]])
            if not body_paths or any(len(p)<2 or sample_support(ink,p,stroke*.35)['support_fraction']<.95 for p in body_paths):
                reasons.append('symbol_strokes_without_raster_support')
            if not all(b.contains(t) for t in terms):
                reasons.append('terminal_not_at_body')
            # Each terminal must attach to an actual endpoint, not just the
            # nearest line anywhere in the diagram. Check the connecting pixels too.
            attachments=[]
            for t in terms:
                point=[t.x,t.y]
                possible=[]
                for p in paths:
                    for end in (0,-1):
                        endpoint=p['points'][end]
                        distance=float(np.linalg.norm(np.subtract(endpoint,point)))
                        allowance=stroke*2+c.get('contact_radius_px',0)
                        if distance <= allowance:
                            # A hollow switch contact has a white center; its
                            # measured disk radius alone permits that local gap.
                            radius=c.get('contact_radius_px',stroke*.3) if c['type']=='switch' else stroke*.3
                            support=sample_support(ink,[point,endpoint],radius)
                            if support['support_fraction'] >= .95:
                                possible.append((distance,p['id'],end))
                possible.sort()
                attachments.append({'wire_id':possible[0][1],'end':possible[0][2],
                                    'distance_px':possible[0][0]} if possible else None)
            if not all(attachments):
                reasons.append('terminal_without_verified_wire_endpoint')
            if c['type']=='switch' and c.get('state') not in {'open','closed'}:
                reasons.append('switch_state_unknown')
            if c['type']=='voltage_source' and not c.get('polarity_verified'):
                reasons.append('source_polarity_unverified')
            c.update(verification_status='AMBIGUOUS' if reasons else 'VERIFIED',
                     terminal_attachments=attachments,source_asset_id=source_asset_id,figure_id=figure_id,
                     provenance={'method':'classical_cv','coordinate_space':'source_px',
                                 'source_asset_id':source_asset_id,'figure_id':figure_id,
                                 'uncertainty_px':stroke,'candidate_id':c['id']})
            if reasons:
                issues.append(dict(candidate_id=c['id'],stage=14,status='AMBIGUOUS',code='SYMBOL_GEOMETRY_UNVERIFIED',
                                   message=', '.join(reasons),source_bbox=b.to_dict()))
            verified.append(c)
        out.update(components=verified,wire_paths=paths,validation_issues=issues,
                   geometry_validation={'status':'AMBIGUOUS' if issues else 'VERIFIED',
                                        'source_width':w,'source_height':h,'coordinate_space':'source_px',
                                        'source_asset_id':source_asset_id,'figure_id':figure_id})
        return out

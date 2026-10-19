"""Measured symbol proposals from centerlines, enclosed shapes and plate groups.

These are hypotheses until CircuitGeometryValidator checks their raster support
and lead attachments. Distances below are multiples of the measured stroke width.
"""
import cv2
import numpy as np

from shared.schemas.evidence import SourceBBox, SourcePoint
from .circuit_paths import sample_support, trace_paths


def proposal(kind, points, terminals, stroke, **extra):
    pts = np.asarray(points, float)
    extent=np.vstack((pts,np.asarray(terminals,float)))
    lo, hi = extent.min(axis=0), extent.max(axis=0)
    pad = stroke*.6
    delta = np.subtract(terminals[1],terminals[0])
    return dict(type=kind, bbox=SourceBBox(*(lo-pad),*(hi-lo+2*pad)),
                center=SourcePoint(*((lo+hi)/2)),
                terminal_1=SourcePoint(*terminals[0]), terminal_2=SourcePoint(*terminals[1]),
                orientation='horizontal' if abs(delta[0]) >= abs(delta[1]) else 'vertical',
                angle_deg=float(np.degrees(np.arctan2(delta[1],delta[0]))),
                symbol_path=pts.tolist(), uncertainty_px=float(stroke), **extra)


def detect_symbols(ink, stroke):
    paths, _, _, _ = trace_paths(ink,stroke)
    components, rejected = [], []
    # A zigzag is an alternating, repeated transverse displacement along one
    # monotonic axis, bounded by collinear straight leads. A bend alone is not a resistor.
    for path in paths:
        pts = cv2.approxPolyDP(np.asarray(path['points'],np.float32).reshape(-1,1,2),
                              stroke*.85,False).reshape(-1,2).astype(float)
        for axis in (0,1):
            d = np.diff(pts,axis=0)
            diagonal = (abs(d[:,axis]) > stroke*.7) & (abs(d[:,1-axis]) > stroke*1.4)
            runs = np.split(np.where(diagonal)[0], np.where(np.diff(np.where(diagonal)[0]) != 1)[0]+1)
            for run in runs:
                if len(run) < 5:
                    continue
                a,b = int(run[0]),int(run[-1]+1)
                steps = d[run]
                if not (np.all(steps[:,axis]>0) or np.all(steps[:,axis]<0)):
                    continue
                signs = np.sign(steps[:,1-axis])
                if not np.all(signs[1:] != signs[:-1]):
                    continue
                body = pts[a:b+1]
                amplitude = np.ptp(body[:,1-axis])
                if amplitude < stroke*3 or np.ptp(body[:,axis]) < amplitude*1.6:
                    continue
                # Locate the actual transitions from a straight lead into the
                # first/last half tooth. Endpoints at turning peaks are not terminals.
                if a == 0 or b == len(pts)-1:
                    continue
                lead1,lead2 = d[a-1],d[b]
                if abs(lead1[1-axis]) > stroke or abs(lead2[1-axis]) > stroke:
                    continue
                if abs(body[0,1-axis]-body[-1,1-axis]) > stroke*1.5:
                    continue
                components.append(proposal('resistor',body,[body[0],body[-1]],stroke,notation='zigzag'))
    contours, hierarchy = cv2.findContours(ink,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contacts = []
    for i,c in enumerate(contours):
        area = cv2.contourArea(c)
        x,y,w,h = cv2.boundingRect(c)
        parent = hierarchy[0,i,3] if hierarchy is not None else -1
        if parent < 0:
            rejected.append(dict(kind='contour',bbox=[x,y,w,h],reason='external_connected_stroke_not_a_component_body',area=area))
            continue
        if min(w,h) < stroke*1.2:
            continue
        perimeter = cv2.arcLength(c,True)
        approx = cv2.approxPolyDP(c,max(stroke*.5,perimeter*.025),True).reshape(-1,2)
        if .65 < w/h < 1.5 and area > 0 and 4*np.pi*area/max(perimeter**2,1) > .68 and max(w,h) < stroke*6:
            contacts.append((np.array([x+(w-1)/2,y+(h-1)/2]), max(w,h)/2+stroke*.5))
        if len(approx) == 4 and max(w,h)/min(w,h) >= 1.6 and area/(w*h) > .65:
            axis = 0 if w>=h else 1
            center = np.array([x+(w-1)/2,y+(h-1)/2])
            span = (w if axis == 0 else h)/2+stroke*.5
            direction = np.eye(2)[axis]
            terms = [center-span*direction,center+span*direction]
            if all(sample_support(ink,[t,t+sign*direction*stroke*4],stroke*.3)['support_fraction'] > .9
                   for t,sign in zip(terms,(-1,1))):
                components.append(proposal('resistor',approx,terms,stroke,notation='rectangle'))
    # Leads can divide the white interior of a contact into semicircles. Fit
    # circles to the stroke as well, then require angular raster support; an
    # enclosed white contour alone would miss these ordinary contact symbols.
    circles = cv2.HoughCircles(ink,cv2.HOUGH_GRADIENT,1,max(3,stroke*3),
                              param1=80,param2=9,minRadius=max(2,int(stroke)),
                              maxRadius=max(3,int(stroke*4)))
    if circles is not None:
        angles=np.linspace(0,2*np.pi,64,endpoint=False)
        for x,y,r in circles[0]:
            center=np.array([float(x),float(y)])
            support=0
            for radius in (r,r-stroke*.25,r-stroke*.5):
                ring=np.column_stack((x+radius*np.cos(angles),y+radius*np.sin(angles)))
                samples=[sample_support(ink,[p,p],stroke*.35)['support_fraction'] for p in ring]
                support=max(support,float(np.mean(samples)))
            if support>=.85 and not any(np.linalg.norm(center-c)<stroke*2 for c,_ in contacts):
                contacts.append((center,float(r)))
    # Contact pairs define a possible switch. The movable arm must be measured
    # from a straight path beginning at a contact; an empty gap alone is insufficient.
    for i,(a,ra) in enumerate(contacts):
        for b,rb in contacts[i+1:]:
            gap = np.linalg.norm(b-a)
            if not stroke*5 < gap < stroke*40 or min(ra,rb)/max(ra,rb) < .6:
                continue
            axis = (b-a)/gap
            between = [a+axis*(ra+stroke),b-axis*(rb+stroke)]
            support = sample_support(ink,between,stroke*.25)
            arm = None
            state = None
            if support['support_fraction'] > .95 and support['max_gap_px'] <= 1:
                arm, state = [a,b], 'closed'
            else:
                for path in paths:
                    pp = cv2.approxPolyDP(np.asarray(path['points'],np.float32).reshape(-1,1,2),
                                         stroke*.85,False).reshape(-1,2).astype(float)
                    for p,q in zip(pp,pp[1:]):
                        for root,other in ((a,b),(b,a)):
                            if np.linalg.norm(q-root) < np.linalg.norm(p-root):
                                p,q = q,p
                            length = np.linalg.norm(q-p)
                            if (np.linalg.norm(p-root) < max(ra,rb)+stroke*2 and gap*.45 < length < gap*1.3
                                    and np.dot(q-root,other-root) > 0
                                    and np.linalg.norm(q-other) > stroke*2.5):
                                direction = (q-p)/length
                                alignment = abs(np.dot(direction,axis))
                                if .5 < alignment < .97:
                                    arm,state = [root,q],'open'
            if state:
                components.append(proposal('switch',[a,b,*arm],[a,b],stroke,
                                           state=state,contacts=[a.tolist(),b.tolist()],
                                           contact_radius_px=max(ra,rb),arm_source_px=np.array(arm).tolist(),
                                           gap_support=support))
    # Battery plate groups: parallel transverse strokes, a common axis, unequal
    # alternating plate lengths, and external axial leads on both ends.
    for axis in (0,1):
        kernel = (1,max(5,int(stroke*4))) if axis == 0 else (max(5,int(stroke*4)),1)
        plate_mask = cv2.morphologyEx(ink,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,kernel))
        n,_,stats,centroids = cv2.connectedComponentsWithStats(plate_mask)
        plates = []
        for j in range(1,n):
            x,y,w,h,area = stats[j]
            length,thickness = (h,w) if axis == 0 else (w,h)
            if stroke*4 < length < stroke*35 and thickness < stroke*3:
                plates.append(dict(center=centroids[j],length=float(length),bbox=[x,y,w,h]))
        plates.sort(key=lambda p:p['center'][axis])
        used=set()
        for i,p in enumerate(plates):
            if i in used:
                continue
            group=[(i,p)]
            for j,q in enumerate(plates[i+1:],i+1):
                prev=group[-1][1]
                sep=q['center'][axis]-prev['center'][axis]
                if (abs(q['center'][1-axis]-p['center'][1-axis]) <= stroke*1.5
                        and stroke*1.5 < sep < max(q['length'],prev['length'])*.9):
                    group.append((j,q))
            if len(group)<2 or len(group)%2:
                continue
            lengths=np.array([p['length'] for _,p in group])
            if not (np.all(lengths[::2]>lengths[1::2]*1.3) or np.all(lengths[1::2]>lengths[::2]*1.3)):
                continue
            direction=np.eye(2)[axis]
            t1,t2=group[0][1]['center'],group[-1][1]['center']
            if not all(sample_support(ink,[t,t+sign*direction*stroke*5],stroke*.25)['support_fraction'] > .9
                       for t,sign in ((t1,-1),(t2,1))):
                continue
            points=[]
            for j,p in group:
                x,y,w,h=p['bbox']
                points.extend([[x,y],[x+w-1,y+h-1]])
                used.add(j)
            terms=[t1,t2] if lengths[0]>lengths[1] else [t2,t1]
            components.append(proposal('voltage_source',points,terms,stroke,notation='battery',
                                       plates=[p['bbox'] for _,p in group],polarity_verified=True))
    unique=[]
    for c in components:
        if any(c['bbox'].iou(other['bbox']) > .5 for other in unique):
            continue
        c['id']=f'cv_symbol_{len(unique)+1}'
        unique.append(c)
    return unique,rejected

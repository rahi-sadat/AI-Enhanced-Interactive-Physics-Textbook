"""Remove raster-supported symbol strokes, retaining independent wire evidence.

Bounding boxes locate hypotheses; they never authorize pixel deletion. Masks
contain only observed ink near measured symbol strokes. Extra contacts away
from the two measured terminals reject the mask rather than repair the raster.
"""
from copy import deepcopy

import cv2
import numpy as np

from .circuit_paths import sample_support


def body_paths(component):
    kind = component['type']
    if kind == 'resistor':
        points = deepcopy(component.get('symbol_path', []))
        if points and component.get('notation') == 'rectangle':
            points.append(points[0])
        return [points]
    if kind in {'voltage_source', 'capacitor'}:
        return [[[x+(w-1)/2, y], [x+(w-1)/2, y+h-1]] if h > w else
                [[x, y+(h-1)/2], [x+w-1, y+(h-1)/2]]
                for x, y, w, h in component.get('plates', [])]
    if kind == 'switch':
        paths = [component.get('arm_source_px', [])]
        radius = component.get('contact_radius_px', 0)
        angles = np.linspace(0, 2*np.pi, 65)
        paths.extend(np.column_stack((x+radius*np.cos(angles), y+radius*np.sin(angles))).tolist()
                     for x, y in component.get('contacts', []))
        return paths
    return []


def remove_verified_bodies(ink, components, stroke):
    """Return a new conductor raster, exact removed pixels and mask audit.

    This is a preliminary body check. Full verification still requires both
    terminals to attach to independently traced, source-supported wire ends.
    """
    removed = np.zeros_like(ink)
    distance_transform = cv2.distanceTransform((ink != 0).astype(np.uint8), cv2.DIST_L2, 5)
    nearby_radius = cv2.dilate(distance_transform, np.ones((2*int(np.ceil(stroke))+1,)*2,np.uint8))
    records = []
    for component in components:
        paths = body_paths(component)
        reasons = []
        checked_paths = paths[:1] if component['type'] == 'switch' else paths
        if not paths or any(len(p) < 2 or sample_support(ink, p, stroke*.35)['support_fraction'] < .95
                            for p in checked_paths):
            reasons.append('symbol_strokes_without_raster_support')
        if component.get('notation') == 'zigzag':
            # A distant rail endpoint is not another resistor tooth (R4 regression).
            segments = np.linalg.norm(np.diff(paths[0], axis=0), axis=1) if paths else []
            if len(segments) and max(segments) > component.get('measurement_max_tooth_step_px',max(stroke*10, 36)):
                reasons.append('symbol_path_consumes_long_conductor')
        proposed = np.zeros_like(ink)
        # A small scan may have one-pixel leads but thicker printed zigzags.
        # Measure local ink radius rather than using the page's median stroke
        # as an eraser size. Include only the known polyline simplification error.
        radii = []
        for points in paths:
            for a, b in zip(points, points[1:]):
                xy = np.rint(np.linspace(a,b,max(2,int(np.linalg.norm(np.subtract(b,a)))+1))).astype(int)
                xy[:,0] = np.clip(xy[:,0],0,ink.shape[1]-1)
                xy[:,1] = np.clip(xy[:,1],0,ink.shape[0]-1)
                radii.extend(nearby_radius[xy[:,1],xy[:,0]])
        local_radius = max(radii, default=stroke/2)
        thickness = max(1,int(np.ceil(2*(local_radius+stroke*.85))))
        for points in paths:
            if len(points) >= 2:
                cv2.polylines(proposed, [np.rint(points).astype(np.int32)], False, 1,
                              thickness)
        if component['type'] == 'switch':
            # Hough/contour-verified hollow contact disks include short lead
            # stubs inside the ring. Keep their measured extent together.
            for center in component.get('contacts', []):
                cv2.circle(proposed, tuple(np.rint(center).astype(int)),
                           int(np.ceil(component['contact_radius_px']+stroke)), 1, -1)
        # Stroke tubes have round caps. Their caps cannot authorize erasing a
        # lead/junction just beyond the measured symbol's axial extent.
        axis=0 if component.get('orientation')=='horizontal' else 1
        extent=np.array([point for path in paths for point in path],float)
        if component['type'] in {'voltage_source','capacitor'}:
            extent=np.array([[x,y] for x,y,w,h in component.get('plates',[])]+
                            [[x+w-1,y+h-1] for x,y,w,h in component.get('plates',[])],float)
        elif component.get('notation')=='rectangle':
            box=component['bbox']
            extent=np.array([[box.x,box.y],[box.x_max,box.y_max]])
        elif component['type']=='switch':
            extent=np.vstack((extent,np.array(component.get('contacts',[]))-component['contact_radius_px']-stroke,
                              np.array(component.get('contacts',[]))+component['contact_radius_px']+stroke))
        lower=int(np.floor(extent[:,axis].min())) if len(extent) else 0
        upper=int(np.ceil(extent[:,axis].max())) if len(extent) else -1
        axial=np.indices(ink.shape)[1-axis]
        allowed=(axial>=lower)&(axial<=upper)
        proposed[~allowed]=0
        proposed = ((proposed != 0) & (ink != 0)).astype(np.uint8)
        remaining = ((ink != 0) & (proposed == 0)).astype(np.uint8)
        # Inner rectangle contours and simplified zigzags can leave isolated
        # raster corner flecks. Absorb only tiny, disconnected observed pieces
        # touching the stroke mask; a conductor extending away stays intact.
        _, labels, stats, _ = cv2.connectedComponentsWithStats(remaining)
        adjacent = cv2.dilate(proposed, np.ones((3, 3), np.uint8)) != 0
        for label in np.unique(labels[adjacent]):
            if (label and stats[label, cv2.CC_STAT_AREA] <= max(1, stroke*stroke, 4*local_radius*local_radius)
                    and not np.any((labels==label)&~allowed)):
                proposed[labels == label] = 1
        remaining = ((ink != 0) & (proposed == 0)).astype(np.uint8)
        boundary = (cv2.dilate(proposed, np.ones((3, 3), np.uint8)) != 0) & (remaining != 0)
        # Contacts with retained ink are allowed only beside measured terminals.
        # Thus a nearby junction or crossing conductor cannot disappear silently.
        ys, xs = np.where(boundary)
        terms = np.array([[component[k].x, component[k].y] for k in ('terminal_1', 'terminal_2')])
        contact_radius = max(stroke*3, thickness/2+max(stroke*2,local_radius*2)+2,
                             component.get('contact_radius_px', 0)+thickness/2+stroke)
        distances = np.linalg.norm(np.column_stack((xs, ys))[:, None, :]-terms, axis=2)
        extra = np.min(distances, axis=1) > contact_radius if len(xs) else np.array([],dtype=bool)
        extra_contacts = int(np.count_nonzero(extra))
        if extra_contacts:
            reasons.append('mask_contacts_adjacent_conductor')
        status = 'REJECTED' if reasons else 'ACCEPTED'
        component['body_mask_status'] = status
        component['body_mask_reasons'] = reasons
        if not reasons:
            removed |= proposed
        records.append(dict(candidate_id=component['id'], status=status, reasons=reasons,
                            proposed_pixels=int(proposed.sum()), extra_contact_pixels=extra_contacts,
                            extra_contacts_source_px=np.column_stack((xs[extra],ys[extra])).tolist(),
                            local_ink_radius_px=float(local_radius),mask_width_px=thickness))
    conductor = ink.copy()
    conductor[removed != 0] = 0
    audit = dict(method='observed_symbol_stroke_removal', candidates=records,
                 removed_pixels=int(np.count_nonzero(removed)),
                 added_pixels=int(np.count_nonzero((conductor != 0) & (ink == 0))),
                 retained_pixels_unchanged=bool(np.array_equal(conductor[removed == 0], ink[removed == 0])),
                 connected_regions_before=int(cv2.connectedComponents((ink != 0).astype(np.uint8))[0]-1),
                 connected_regions_after=int(cv2.connectedComponents((conductor != 0).astype(np.uint8))[0]-1))
    return conductor, removed, audit

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


def positive_terminal_from_marker(ink, terminals, plate_length, stroke):
    """Resolve unconventional plate groups only from a nearby isolated + mark."""
    count, _, stats, centers = cv2.connectedComponentsWithStats(ink)
    matches = set()
    for i in range(1,count):
        x,y,w,h,area = stats[i]
        if not (.65 < w/max(h,1) < 1.5 and stroke*2 < min(w,h) < stroke*9):
            continue
        patch = ink[y:y+h,x:x+w] > 0
        # Both full crossbars, with white corners; rejects dots and letter loops.
        if patch.sum(axis=0).max() < h*.85 or patch.sum(axis=1).max() < w*.85:
            continue
        if not .15 < area/(w*h) < .65:
            continue
        distances = [np.linalg.norm(centers[i]-t) for t in terminals]
        nearest = int(np.argmin(distances))
        if distances[nearest] < plate_length and abs(distances[0]-distances[1]) > stroke*2:
            matches.add(nearest)
    return next(iter(matches)) if len(matches)==1 else None


def detect_symbols(ink, stroke, *, semantic_types=None, polarity_ink=None, include_switches=True,
                   max_resistor_step=None):
    paths, _, _, _ = trace_paths(ink, stroke, spur_widths=3)
    components, rejected = [], []

    # 1. Resistor Proposals (Zigzag & Rectangle)
    # A. Reversal-based zigzag detection (detects 3-10 tooth zigzags robustly along polylines)
    max_step = max_resistor_step or max(stroke * 10.0, 36.0)
    for path in paths:
        pts = cv2.approxPolyDP(np.asarray(path['points'], np.float32).reshape(-1, 1, 2),
                               stroke * 0.85, False).reshape(-1, 2).astype(float)
        for axis in (0, 1):
            trans = 1 - axis
            dy = np.diff(pts[:, trans])
            signs = np.sign(dy)
            nonzeros = np.where(signs != 0)[0]
            if len(nonzeros) < 3:
                continue
            reversals = []
            for i in range(len(nonzeros) - 1):
                idx1, idx2 = nonzeros[i], nonzeros[i + 1]
                if signs[idx1] != signs[idx2]:
                    step_len = np.linalg.norm(pts[idx2] - pts[idx1])
                    if stroke * 1.0 <= step_len <= max_step:
                        reversals.append(idx2)
            runs = []
            curr = []
            for r in reversals:
                if not curr or r - curr[-1] <= 2:
                    curr.append(r)
                else:
                    if len(curr) >= 3:
                        runs.append(curr)
                    curr = [r]
            if curr and len(curr) >= 3:
                runs.append(curr)

            for run in runs:
                start_idx = max(0, run[0] - 1)
                end_idx = min(len(pts) - 1, run[-1] + 1)
                body = pts[start_idx:end_idx + 1]
                amp = np.ptp(body[:, trans])
                span = np.ptp(body[:, axis])
                if amp >= stroke * 2.0 and span >= stroke * 3.0:
                    t1, t2 = body[0], body[-1]
                    components.append(proposal('resistor', body, [t1, t2], stroke, notation='zigzag'))

    # B. Rectangular resistor proposals
    contours, hierarchy = cv2.findContours(ink, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contacts = []
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        parent = hierarchy[0, i, 3] if hierarchy is not None else -1
        if parent < 0:
            rejected.append(dict(kind='contour', bbox=[x, y, w, h], reason='external_connected_stroke_not_a_component_body', area=area))
            continue
        if min(w, h) < stroke * 1.2:
            continue
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, max(stroke * 0.5, perimeter * 0.025), True).reshape(-1, 2)
        if 0.65 < w / h < 1.5 and area > 0 and 4 * np.pi * area / max(perimeter**2, 1) > 0.68 and max(w, h) < stroke * 6:
            contacts.append((np.array([x + (w - 1) / 2, y + (h - 1) / 2]), max(w, h) / 2 + stroke * 0.5))
        if len(approx) == 4 and max(w, h) / min(w, h) >= 1.6 and area / (w * h) > 0.65:
            axis = 0 if w >= h else 1
            center = np.array([x + (w - 1) / 2, y + (h - 1) / 2])
            span = (w if axis == 0 else h) / 2 + stroke * 0.5
            direction = np.eye(2)[axis]
            terms = [center - span * direction, center + span * direction]
            if all(sample_support(ink, [t, t + sign * direction * stroke * 4], stroke * 0.3)['support_fraction'] > 0.85
                   for t, sign in zip(terms, (-1, 1))):
                components.append(proposal('resistor', approx, terms, stroke, notation='rectangle'))

    # 2. Switch Proposals (only if switch is semantically present or not explicitly disabled)
    allow_switches = include_switches and (semantic_types is None or bool(
        {'switch', 'open_switch', 'closed_switch'} & set(semantic_types)))
    if allow_switches:
        circles = cv2.HoughCircles(ink, cv2.HOUGH_GRADIENT, 1, max(3, int(stroke * 3)),
                                   param1=80, param2=9, minRadius=max(2, int(stroke)),
                                   maxRadius=max(3, int(stroke * 4)))
        if circles is not None:
            angles = np.linspace(0, 2 * np.pi, 64, endpoint=False)
            for x, y, r in circles[0]:
                center = np.array([float(x), float(y)])
                support = 0
                for radius in (r, r - stroke * 0.25, r - stroke * 0.5):
                    ring = np.column_stack((x + radius * np.cos(angles), y + radius * np.sin(angles)))
                    samples = [sample_support(ink, [p, p], stroke * 0.35)['support_fraction'] for p in ring]
                    support = max(support, float(np.mean(samples)))
                # Retain upstream's rejection of filled junction dots.
                inner_ink = 1.0
                for fraction in (.25, .4, .55, .7):
                    inner = np.column_stack((x+r*fraction*np.cos(angles), y+r*fraction*np.sin(angles)))
                    inner_ink = min(inner_ink, np.mean([ink[int(np.clip(py, 0, ink.shape[0]-1)),
                        int(np.clip(px, 0, ink.shape[1]-1))] > 0 for px, py in inner]))
                if support >= 0.85 and inner_ink < .95 and not any(np.linalg.norm(center - c) < stroke * 2 for c, _ in contacts):
                    contacts.append((center, float(r)))

        for i, (a, ra) in enumerate(contacts):
            for b, rb in contacts[i + 1:]:
                gap = np.linalg.norm(b - a)
                if not stroke * 5 < gap < stroke * 40 or min(ra, rb) / max(ra, rb) < 0.6:
                    continue
                axis = (b - a) / gap
                between = [a + axis * (ra + stroke), b - axis * (rb + stroke)]
                support = sample_support(ink, between, stroke * 0.25)
                arm = None
                state = None
                if support['support_fraction'] > 0.95 and support['max_gap_px'] <= 1:
                    arm, state = [a, b], 'closed'
                else:
                    for path in paths:
                        pp = cv2.approxPolyDP(np.asarray(path['points'], np.float32).reshape(-1, 1, 2),
                                             stroke * 0.85, False).reshape(-1, 2).astype(float)
                        for p, q in zip(pp, pp[1:]):
                            for root, other in ((a, b), (b, a)):
                                if np.linalg.norm(q - root) < np.linalg.norm(p - root):
                                    p, q = q, p
                                length = np.linalg.norm(q - p)
                                if (np.linalg.norm(p - root) < max(ra, rb) + stroke * 2 and gap * 0.45 < length < gap * 1.3
                                        and np.dot(q - root, other - root) > 0
                                        and np.linalg.norm(q - other) > stroke * 2.5):
                                    direction = (q - p) / length
                                    alignment = abs(np.dot(direction, axis))
                                    if 0.5 < alignment < 0.97:
                                        arm, state = [root, q], 'open'
                if state:
                    components.append(proposal('switch', [a, b, *arm], [a, b], stroke,
                                               state=state, contacts=[a.tolist(), b.tolist()],
                                               contact_radius_px=max(ra, rb), arm_source_px=np.array(arm).tolist(),
                                               gap_support=support))

    # 3. Battery Proposals (2-plate, 3-plate and 4-plate DC batteries, including solid-block negative plates)
    for axis in (0, 1):
        kernel = (1, max(3, int(stroke * 3))) if axis == 0 else (max(3, int(stroke * 3)), 1)
        plate_mask = cv2.morphologyEx(ink, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, kernel))
        n, _, stats, centroids = cv2.connectedComponentsWithStats(plate_mask)
        plates = []
        for j in range(1, n):
            x, y, pw, ph, area = stats[j]
            length, thickness = (ph, pw) if axis == 0 else (pw, ph)
            if max(stroke * 3.5, 15.0) < length < stroke * 40 and thickness <= stroke * 12:
                plates.append(dict(center=centroids[j], length=float(length), thickness=float(thickness), bbox=[x, y, pw, ph]))
        plates.sort(key=lambda p: p['center'][axis])
        used = set()
        for i, p in enumerate(plates):
            if i in used:
                continue
            group = [(i, p)]
            for j, q in enumerate(plates[i + 1:], i + 1):
                prev = group[-1][1]
                sep = q['center'][axis] - prev['center'][axis]
                max_len = max(q['length'], prev['length'])
                # Plates should be spaced closer than their length. A wider
                # gap groups unrelated parallel wires and masks real conductors.
                if abs(q['center'][1 - axis] - p['center'][1 - axis]) <= max(stroke * 4.0, max_len * 0.3) and stroke * 1.2 < sep < max_len:
                    group.append((j, q))
                    if len(group) == 4:
                        break
            if len(group) not in (2, 3, 4):
                continue
            lengths = np.array([p['length'] for _, p in group])
            capacitor = len(group) == 2 and .85 <= lengths[1]/lengths[0] <= 1/.85
            if len(group) == 2:
                if not capacitor and max(lengths) / min(lengths) < 1.20:
                    continue
            elif len(group) == 3:
                # 3-plate cell (e.g. long, short thick block, long):
                # The middle plate should alternate in length relative to both outer plates
                if not ((lengths[1] * 1.15 < min(lengths[0], lengths[2])) or
                        (lengths[1] > max(lengths[0], lengths[2]) * 1.15)):
                    continue
            elif len(group) == 4:
                if not (np.all(lengths[::2] > lengths[1::2] * 1.15) or np.all(lengths[1::2] > lengths[::2] * 1.15)):
                    continue
            direction = np.eye(2)[axis]
            t1, t2 = group[0][1]['center'], group[-1][1]['center']
            support1 = sample_support(ink, [t1, t1 - direction * stroke * 4], stroke * 0.35)['support_fraction']
            support2 = sample_support(ink, [t2, t2 + direction * stroke * 4], stroke * 0.35)['support_fraction']
            if support1 < 0.65 or support2 < 0.65:
                continue
            for j, _ in group:
                used.add(j)
            points = []
            for j, p in group:
                x, y, pw, ph = p['bbox']
                points.extend([[x, y], [x + pw - 1, y + ph - 1]])
            if capacitor:
                # Equal parallel plates with supported outward leads; no
                # polarity inferred from their drawing orientation.
                components.append(proposal('capacitor', points, [t1, t2], stroke,
                    notation='parallel_plates', plates=[p['bbox'] for _, p in group]))
                continue
            positive = (0 if lengths[0] > lengths[-1] else 1) if len(group) % 2 == 0 else \
                positive_terminal_from_marker(ink if polarity_ink is None else polarity_ink,
                    [t1, t2], float(max(lengths)), stroke)
            terms = [t1, t2] if positive in (0, None) else [t2, t1]
            components.append(proposal('voltage_source', points, terms, stroke, notation='battery',
                plates=[p['bbox'] for _, p in group], polarity_verified=positive is not None))

    unique = []
    for c in components:
        if any(c['bbox'].iou(other['bbox']) > 0.4 for other in unique):
            continue
        c['id'] = f'cv_symbol_{len(unique) + 1}'
        unique.append(c)
    return unique, rejected

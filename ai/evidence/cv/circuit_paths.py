"""Native raster centerlines. No gap closing or rail extrapolation is performed.

Eight-connected skeleton edges are traced between endpoint/junction clusters.
At an unmarked four-way crossing the graph keeps opposite strokes separate;
only a measured dot (stroke radius larger than the ordinary line radius) joins it.
"""
from __future__ import annotations

import cv2
import numpy as np
from skimage.morphology import skeletonize


def raster(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image.copy()
    _, ink = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    skeleton = skeletonize(ink > 0)
    distance = cv2.distanceTransform(ink, cv2.DIST_L2, 5)
    radii = distance[skeleton]
    stroke = max(1.0, float(np.median(radii)) * 2 - 1) if len(radii) else 1.0
    return gray, ink, stroke


def trace_paths(ink, stroke):
    sk = skeletonize(ink > 0).astype(np.uint8)
    ys, xs = np.where(sk)
    pixels = set(zip(xs.tolist(), ys.tolist()))
    neighbors = lambda p: [(p[0]+dx, p[1]+dy) for dx, dy in
                           ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1))
                           if (p[0]+dx,p[1]+dy) in pixels
                           and not (dx and dy and ((p[0]+dx,p[1]) in pixels or (p[0],p[1]+dy) in pixels))]
    # Thinning a thick acute corner can leave a short spur ending at its
    # outside tip. Remove only dead-end spurs shorter than two stroke widths
    # that terminate at a branch; never join disconnected ink.
    for _ in range(2):
        remove=set()
        for p in list(pixels):
            if len(neighbors(p)) != 1:
                continue
            chain=[p]
            prev,cur=p,neighbors(p)[0]
            while len(chain) <= stroke*2 and len(neighbors(cur)) == 2:
                chain.append(cur)
                nxt=next(q for q in neighbors(cur) if q != prev)
                prev,cur=cur,nxt
            if len(chain) <= stroke*2 and len(neighbors(cur)) >= 3:
                remove.update(chain)
        pixels.difference_update(remove)
        for x,y in remove:
            sk[y,x]=0
    # Do not count a raster stair-step diagonal as a third branch when an
    # orthogonal connection already represents that same pixel path.
    special = np.zeros_like(sk)
    for p in pixels:
        if len(neighbors(p)) != 2:
            special[p[1],p[0]] = 1
    _, labels = cv2.connectedComponents(special, connectivity=8)
    centers = {}
    for k in range(1, int(labels.max())+1):
        yy, xx = np.where(labels == k)
        centers[k] = [float(xx.mean()), float(yy.mean())]
    used = set()
    paths = []
    for p in sorted(pixels, key=lambda p: (labels[p[1],p[0]] == 0, p)):
        for q in neighbors(p):
            edge = tuple(sorted((p,q)))
            if edge in used or (labels[p[1],p[0]] and labels[p[1],p[0]] == labels[q[1],q[0]]):
                continue
            used.add(edge)
            chain, prev, cur = [p,q], p, q
            while labels[cur[1],cur[0]] == 0:
                choices = [r for r in neighbors(cur) if r != prev and tuple(sorted((cur,r))) not in used]
                if not choices:
                    break
                nxt = choices[0]
                used.add(tuple(sorted((cur,nxt))))
                chain.append(nxt)
                prev, cur = cur, nxt
            if len(chain) < 3:
                continue
            ends = [int(labels[chain[i][1],chain[i][0]]) for i in (0,-1)]
            pts = np.array(chain, np.float32)
            for i,k in zip((0,-1),ends):
                if k:
                    pts[i] = centers[k]
            approx = cv2.approxPolyDP(pts.reshape(-1,1,2), max(0.6, stroke*.3), False).reshape(-1,2)
            if len(approx) < 2:
                continue
            paths.append({'points': approx.astype(float).tolist(), 'ends': ends})
    distance = cv2.distanceTransform(ink, cv2.DIST_L2, 5)
    junctions, crossings = [], []
    for k, center in centers.items():
        incident = [(i,end) for i,p in enumerate(paths) for end,e in enumerate(p['ends']) if e == k]
        if len(incident) < 3:
            continue
        x,y = map(lambda v: int(round(v)),center)
        # A plain crossing is thicker than either line by roughly sqrt(2).
        # Require additional ink beyond that ordinary intersection footprint.
        dot = float(distance[y,x]) > stroke*1.1+1.0
        if len(incident) == 4 and not dot:
            # Straight continuation through an unmarked X is not a junction.
            vectors = []
            for i,end in incident:
                pts = paths[i]['points']
                v = np.subtract(pts[1 if end == 0 else -2], center)
                vectors.append(v / max(np.linalg.norm(v),1e-9))
            choices = [((0,1),(2,3)),((0,2),(1,3)),((0,3),(1,2))]
            pairs = min(choices, key=lambda pairs: sum(np.dot(vectors[a],vectors[b]) for a,b in pairs))
            for group,pair in enumerate(pairs):
                for j in pair:
                    i,end = incident[j]
                    paths[i]['ends'][end] = f'cross_{k}_{group}'
            crossings.append({'center':center,'status':'NON_CONNECTED','dot':False})
        else:
            junctions.append({'center':center,'dot':dot,'degree':len(incident)})
    return paths, junctions, crossings, sk


def sample_support(ink, points, radius=0):
    """Support and longest unsupported run along the actual proposed polyline."""
    if radius:
        r = int(np.ceil(radius))
        ink = cv2.dilate(ink, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1)))
    samples = []
    h,w = ink.shape
    for a,b in zip(points,points[1:]):
        n = max(2,int(np.ceil(np.linalg.norm(np.subtract(b,a))))+1)
        xy = np.rint(np.linspace(a,b,n)).astype(int)
        inside = (xy[:,0]>=0)&(xy[:,0]<w)&(xy[:,1]>=0)&(xy[:,1]<h)
        values = np.zeros(n,dtype=bool)
        values[inside] = ink[xy[inside,1],xy[inside,0]] > 0
        samples.extend(values.tolist())
    longest = run = 0
    for supported in samples:
        run = 0 if supported else run+1
        longest = max(longest,run)
    return {'support_fraction':float(np.mean(samples)) if samples else 0.0,'max_gap_px':longest}

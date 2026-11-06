"""PR-06 DC Circuit Classical CV Candidate Extractor.

Extracts deterministic geometric candidates for:
  - component bodies (resistors, voltage sources, switches)
  - component terminals
  - wire segments
  - junction nodes
  - structural connectivity graph (wire path continuity)
"""
from __future__ import annotations

import cv2
import numpy as np

from shared.schemas.evidence import SourceLine, SourcePoint
from .circuit_paths import raster, trace_paths
from .circuit_symbols import detect_symbols, proposal
from .circuit_body_mask import remove_verified_bodies


def _intersection_area(first, second):
    width = max(0, min(first.x_max, second.x_max) - max(first.x, second.x))
    height = max(0, min(first.y_max, second.y_max) - max(first.y, second.y))
    return width * height


def _recover_resistor_symbols(ink, stroke, components, resistor_regions):
    """Measure unresolved resistor symbols inside their local detector regions."""
    height, width = ink.shape
    recovered = []
    for region in resistor_regions:
        if any(c['type'] == 'resistor' and region.iou(c['bbox']) >= .30 for c in components):
            continue
        pad = int(np.ceil(stroke * 6))
        x0, y0 = max(0, int(region.x) - pad), max(0, int(region.y) - pad)
        x1 = min(width, int(np.ceil(region.x_max)) + pad)
        y1 = min(height, int(np.ceil(region.y_max)) + pad)
        max_step = max(stroke * 10, 36, max(region.width, region.height) / 3)
        measured, _ = detect_symbols(
            ink[y0:y1, x0:x1].copy(), stroke, include_switches=False, max_resistor_step=max_step,
        )
        candidates = []
        for symbol in measured:
            if symbol['type'] != 'resistor':
                continue
            native = proposal(
                'resistor',
                np.asarray(symbol['symbol_path']) + [x0, y0],
                [(symbol[k].x + x0, symbol[k].y + y0) for k in ('terminal_1', 'terminal_2')],
                stroke, notation=symbol['notation'], measurement_max_tooth_step_px=max_step,
            )
            overlap = region.iou(native['bbox'])
            if overlap >= .30:
                candidates.append((overlap, native))
        candidates.sort(key=lambda candidate: candidate[0], reverse=True)
        if candidates and (len(candidates) == 1 or candidates[0][0] - candidates[1][0] >= .10):
            best = candidates[0][1]
            best['refinement_evidence'] = [dict(candidate_id=c['id'],type=c['type'],
                bbox=c['bbox'].to_dict(),proposal_iou=float(region.iou(c['bbox'])),
                reason='Re-measured local zigzag strokes; excluded adjoining conductor segments')
                for c in components if c['type']=='resistor' and _intersection_area(c['bbox'],best['bbox'])>0]
            if all(best['bbox'].iou(c['bbox']) <= .40 for c in recovered):
                recovered.append(best)

    # A whole-image candidate may include a long piece of adjacent wire.
    # Prefer the local measurement for the same body before tracing wires.
    kept = [
        c for c in components if c['type'] != 'resistor'
        or any(region.iou(c['bbox']) >= .30 for region in resistor_regions)
        or not any(_intersection_area(c['bbox'], r['bbox']) >=
                   .70 * min(c['bbox'].width * c['bbox'].height, r['bbox'].width * r['bbox'].height)
                   for r in recovered)
    ]
    for index, c in enumerate(recovered, 1):
        c['id'] = f'cv_local_resistor_{index}'
    return kept + recovered


def _separate_overlapping_hypotheses(components, symbol_regions):
    """Keep competing interpretations of one body from cutting the same wire."""
    corroborated = [
        (candidate, region) for candidate in components for kind, region in symbol_regions
        if candidate['type'] == kind and region.iou(candidate['bbox']) >= .30
    ]
    supported_ids = {candidate['id'] for candidate, _ in corroborated}
    kept, rejected = [], []
    for candidate in components:
        box = candidate['bbox']
        if candidate['id'] not in supported_ids and any(
            body['type'] != candidate['type'] and body['bbox'].contains(candidate['center'])
            and _intersection_area(box, region) >= .85 * box.width * box.height
            for body, region in corroborated
        ):
            rejected.append(dict(kind=candidate['type'], bbox=box.to_dict(), reason='overlaps_corroborated_symbol'))
        else:
            kept.append(candidate)
    return kept, rejected


def _recover_source_symbols(ink, stroke, components, symbol_regions):
    """Inspect all measured plates in a source proposal, including small cells.

    The full-image 15 px noise floor excludes short plates in small scans. A
    detector region restricts this search; the existing stroke-relative plate
    rule still applies. Neither a box nor a class prediction supplies polarity.
    """
    for kind, region in symbol_regions:
        if kind != 'voltage_source':
            continue
        pad = int(np.ceil(stroke * 6))
        x0, y0 = max(0, int(region.x)-pad), max(0, int(region.y)-pad)
        x1, y1 = min(ink.shape[1], int(np.ceil(region.x_max))+pad), min(ink.shape[0], int(np.ceil(region.y_max))+pad)
        measured, _ = detect_symbols(ink[y0:y1, x0:x1], stroke, include_switches=False, min_plate_length=0)
        matches = []
        for c in measured:
            if c['type'] != 'voltage_source' or not c.get('polarity_verified'):
                continue
            native = proposal('voltage_source', np.asarray(c['symbol_path'])+[x0,y0],
                [(c[k].x+x0,c[k].y+y0) for k in ('terminal_1','terminal_2')], stroke,
                notation=c['notation'], polarity_verified=True,
                plates=[[int(x+x0),int(y+y0),int(w),int(h)] for x,y,w,h in c['plates']])
            if region.iou(native['bbox']) >= .30:
                matches.append(native)
        if len(matches) == 1:
            native = matches[0]
            # Retain competing candidates in diagnostics upstream; replace only
            # the same measured plate group before cutting the conductor mask.
            replaced = [c for c in components if (
                c['type'] in {'capacitor','voltage_source'} and native['bbox'].contains(c['center']))]
            native['refinement_evidence'] = [dict(candidate_id=c['id'], type=c['type'],
                bbox=c['bbox'].to_dict(), plates=[list(map(int,p)) for p in c.get('plates',[])],
                proposal_iou=float(region.iou(c['bbox'])),
                reason='Re-measured the complete local plate group using the existing stroke-relative rule') for c in replaced]
            components = [c for c in components if c not in replaced]
            native['id'] = f'cv_local_source_{len(components)+1}'
            components.append(native)
    return components


class CircuitCVCandidateExtractor:
    """Extract measured symbol hypotheses and continuous native-pixel paths."""

    def extract(self, image_bgr, *, source_width, source_height, ocr_boxes=None, semantic_types=None,
                symbol_regions=None):
        h,w=image_bgr.shape[:2]
        if (w,h) != (source_width,source_height):
            raise ValueError("Circuit CV requires the decoded native source frame.")
        gray,ink,stroke=raster(image_bgr)
        clean=ink.copy()
        # Non-destructive text glyph suppression:
        # Instead of wiping entire bounding rectangles (which damages adjacent/overlapping wires and symbols),
        # only suppress isolated connected components belonging to text glyphs.
        if ocr_boxes:
            n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(clean, connectivity=8)
            for b in ocr_boxes:
                bx1, by1 = max(0, int(b.x)), max(0, int(b.y))
                bx2, by2 = min(w, int(np.ceil(b.x_max))), min(h, int(np.ceil(b.y_max)))
                bw, bh = bx2 - bx1, by2 - by1
                if bw <= 0 or bh <= 0:
                    continue
                sub_labels = np.unique(labels[by1:by2, bx1:bx2])
                for lbl in sub_labels:
                    if lbl == 0:
                        continue
                    x, y, cw, ch, area = stats[lbl]
                    comp_outside_w = max(0, bx1 - x) + max(0, (x + cw) - bx2)
                    comp_outside_h = max(0, by1 - y) + max(0, (y + ch) - by2)
                    if comp_outside_w > stroke * 2.5 or comp_outside_h > stroke * 2.5:
                        continue
                    if cw > bw * 1.2 or ch > bh * 1.2:
                        continue
                    clean[labels == lbl] = 0
        suppressed=((ink != 0) & (clean == 0)).astype(np.uint8)
        # OCR also reads zigzags as letters and battery plates as punctuation.
        # Protect connected ink of independently detected resistor/battery
        # hypotheses. This restores observed pixels only, never closes a gap.
        # Contact/arm hypotheses in text are too ambiguous for this rescue.
        protected=[]
        if suppressed.any():
            raw_symbols,_=detect_symbols(ink,stroke,polarity_ink=ink,include_switches=False,semantic_types=semantic_types)
            _,labels=cv2.connectedComponents(ink.astype(np.uint8),connectivity=8)
            for candidate in raw_symbols:
                if candidate['type'] not in {'resistor','voltage_source','capacitor'}:
                    continue
                box=candidate['bbox']
                y0,y1=max(0,int(box.y)),min(h,int(np.ceil(box.y_max))+1)
                x0,x1=max(0,int(box.x)),min(w,int(np.ceil(box.x_max))+1)
                if not np.any(suppressed[y0:y1,x0:x1] & ink[y0:y1,x0:x1]):
                    continue
                identities=np.unique(labels[y0:y1,x0:x1])
                identities=identities[identities!=0]
                restore=np.isin(labels,identities) & (suppressed!=0)
                clean[restore]=ink[restore]
                protected.append(dict(type=candidate['type'],bbox=box.to_dict(),
                                      restored_ink_pixels=int(np.count_nonzero(ink[restore]))))
        components,rejected=detect_symbols(clean,stroke,polarity_ink=ink,semantic_types=semantic_types)
        if symbol_regions:
            components = _recover_source_symbols(clean, stroke, components, symbol_regions)
            components = _recover_resistor_symbols(
                clean, stroke, components, [box for kind, box in symbol_regions if kind == 'resistor'],
            )
            components, conflicts = _separate_overlapping_hypotheses(components, symbol_regions)
            rejected.extend(conflicts)
        conductor, removed, mask_audit = remove_verified_bodies(clean, components, stroke)
        paths,junctions,crossings,skeleton=trace_paths(conductor,stroke)
        wires=[]
        for i,p in enumerate(paths):
            p['id']=f'cv_wire_{i+1}'
            p['coordinate_space']='source_px'
            p['uncertainty_px']=stroke
            for a,b in zip(p['points'],p['points'][1:]):
                wires.append(SourceLine(SourcePoint(*a),SourcePoint(*b)))
        return dict(components=components, wires=wires, wire_paths=paths,
                    junctions=[SourcePoint(*j['center']) for j in junctions],
                    junction_evidence=junctions, crossings=crossings,
                    # Retained for older diagnostic consumers, never used for topology.
                    rails_y=[], branches_x=[],
                    gray=gray,edges=cv2.Canny(gray,50,150),ink=clean,
                    original_binary=ink.copy(), body_mask_before=clean.copy(),
                    component_body_mask=removed, removed_symbol_pixels=removed.copy(),
                    body_mask_audit=mask_audit,
                    conductor_mask=conductor,skeleton=skeleton,stroke_width_px=stroke,
                    raw_candidates=components,rejected_candidates=rejected,
                    ocr_symbol_conflicts=protected,
                    source_width=w,source_height=h,coordinate_space='source_px')

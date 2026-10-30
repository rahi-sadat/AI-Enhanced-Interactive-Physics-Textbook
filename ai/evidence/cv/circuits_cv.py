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
from .circuit_symbols import detect_symbols


class CircuitCVCandidateExtractor:
    """Extract measured symbol hypotheses and continuous native-pixel paths."""

    def extract(self, image_bgr, *, source_width, source_height, ocr_boxes=None):
        h,w=image_bgr.shape[:2]
        if (w,h) != (source_width,source_height):
            raise ValueError("Circuit CV requires the decoded native source frame.")
        gray,ink,stroke=raster(image_bgr)
        clean=ink.copy()
        suppressed=np.zeros_like(ink)
        # OCR boxes exclude text only; never use their centers as symbol anchors.
        # No expansion: a broad OCR mask can erase a nearby real terminal.
        for b in ocr_boxes or []:
            suppressed[max(0,int(b.y)):min(h,int(np.ceil(b.y_max))),
                  max(0,int(b.x)):min(w,int(np.ceil(b.x_max)))]=1
            clean[max(0,int(b.y)):min(h,int(np.ceil(b.y_max))),
                  max(0,int(b.x)):min(w,int(np.ceil(b.x_max)))]=0
        # OCR also reads zigzags as letters and battery plates as punctuation.
        # Protect connected ink of independently detected resistor/battery
        # hypotheses. This restores observed pixels only, never closes a gap.
        # Contact/arm hypotheses in text are too ambiguous for this rescue.
        protected=[]
        if suppressed.any():
            raw_symbols,_=detect_symbols(ink,stroke,polarity_ink=ink,include_switches=False)
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
        components,rejected=detect_symbols(clean,stroke,polarity_ink=ink)
        conductor=clean.copy()
        for c in components:
            b=c['bbox']
            # Remove physical symbol ink before graph construction. Switch arm
            # and contact rings are not conducting wire paths between terminals.
            pad=c.get('contact_radius_px',0) if c['type']=='switch' else 0
            conductor[max(0,int(b.y-pad)):min(h,int(np.ceil(b.y_max+pad))+1),
                      max(0,int(b.x-pad)):min(w,int(np.ceil(b.x_max+pad))+1)]=0
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
                    conductor_mask=conductor,skeleton=skeleton,stroke_width_px=stroke,
                    raw_candidates=components,rejected_candidates=rejected,
                    ocr_symbol_conflicts=protected,
                    source_width=w,source_height=h,coordinate_space='source_px')

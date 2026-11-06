"""Retry malformed circuit labels with verified symbol ink suppressed for OCR.

Only the recognition input copy changes. The original image/raw tokens remain
evidence, and every new token is transformed back into native source pixels.
"""
from copy import deepcopy
import re

import cv2
import numpy as np

from ai.evidence.cv.circuit_body_mask import remove_verified_bodies
from shared.schemas.evidence import SourceBBox,SourcePoint
from .circuit_ocr import normalize_circuit_text,parse_circuit_label


def refine_circuit_ocr(provider,image,candidates,ocr):
    if not ocr or not ocr.tokens:return ocr,[]
    verified=[deepcopy(c) for c in candidates.get('components',[]) if c.get('verification_status')=='VERIFIED']
    raster=candidates.get('original_binary')
    if raster is None or not verified:return ocr,[]
    _,mask,_=remove_verified_bodies(raster,verified,candidates['stroke_width_px'])
    output=deepcopy(ocr);records=[]
    for token in ocr.tokens:
        text=normalize_circuit_text(token.raw_text);box=token.bbox_source_px
        # Parsed values already have intact recognition. Retry only malformed
        # component notation whose OCR region overlaps independently verified ink.
        if not box or parse_circuit_label(text) is not None or not re.search(r'[RVC]\s*\d.*\d\s*[ΩωVF]',text):continue
        x0,y0=max(0,int(box.x)),max(0,int(box.y))
        x1,y1=min(image.shape[1],int(np.ceil(box.x_max))),min(image.shape[0],int(np.ceil(box.y_max)))
        removed=mask[y0:y1,x0:x1]!=0
        if x1<=x0 or y1<=y0 or not removed.any():continue
        crop=image[y0:y1,x0:x1].copy();crop[removed]=255
        scale=2
        crop=cv2.resize(crop,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
        record=dict(parent_token_id=token.id,source_crop=[x0,y0,x1,y1],scale=scale,
                    preprocessing='verified_symbol_pixels_suppressed_on_recognition_copy',
                    removed_pixels=int(removed.sum()),tokens=[])
        try:
            recognized=provider.extract(crop,source_width=crop.shape[1],source_height=crop.shape[0])
            for fresh in recognized.tokens:
                parsed=parse_circuit_label(normalize_circuit_text(fresh.raw_text))
                if not parsed or parsed['val'] is None or not fresh.bbox_source_px:continue
                fresh=deepcopy(fresh);b=fresh.bbox_source_px
                fresh.id=f'ocr_refine_{token.id}_{fresh.id}'
                fresh.bbox_source_px=SourceBBox(x0+b.x/scale,y0+b.y/scale,b.width/scale,b.height/scale)
                if fresh.polygon_source_px:
                    fresh.polygon_source_px.points=[SourcePoint(x0+p.x/scale,y0+p.y/scale) for p in fresh.polygon_source_px.points]
                fresh.evidence_ref='evidence_ocr_'+fresh.id
                output.tokens.append(fresh);record['tokens'].append(fresh.to_dict())
        except Exception as error:
            record['error']=str(error)
        records.append(record)
    return output,records

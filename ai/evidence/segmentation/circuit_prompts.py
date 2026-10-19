"""Type-aware circuit prompts and conservative mask corroboration.

Masks are retained for audit, never used to declare electrical connectivity or
overwrite the independently measured terminal graph.
"""
import json
import numpy as np
from ai.evidence.cv.circuit_paths import sample_support

from .base import SegmentationPrompt
from shared.schemas.evidence import ExtractionStatus, SegmentationResult


def segment_circuit_candidates(provider, image, candidates, asset):
    records=[]
    masks=[]
    available=provider.available()
    for c in candidates.get('components',[]):
        box=c['bbox']
        # A zigzag center may be whitespace: choose a measured stroke as the
        # positive point. Bounding box and points remain in native source pixels.
        points=[tuple(c['symbol_path'][0])] if c.get('symbol_path') else []
        prompt=SegmentationPrompt(box=box,points=points,labels=[1]*len(points))
        if available:
            try:
                result=provider.segment(image,prompt,source_width=asset.width_px,
                    source_height=asset.height_px,entity_id=c['id'])
            except Exception as exc:
                result=SegmentationResult(status=ExtractionStatus.ERROR,provider=provider.name,error=str(exc))
        else:
            result=SegmentationResult(status=ExtractionStatus.UNAVAILABLE,provider=provider.name,
                                      error='Segmentation provider unavailable; retaining CV evidence.')
        record={'entity_candidate_id':c['id'],'source_bbox':box.to_dict(),
                'prompt_points':points,'prompt_labels':prompt.labels,
                'source_asset_id':asset.id,'provider':result.provider,'model':result.model,
                'status':result.status.value,'error':result.error,'masks':[]}
        for mask in result.masks:
            reasons=[]
            mb=mask.bbox_source_px
            if (mask.source_width,mask.source_height)!=(asset.width_px,asset.height_px):
                reasons.append('mask_frame_mismatch')
            if not mb or mb.iou(box)<.5:
                reasons.append('mask_outside_candidate_region')
            if mask.area_px <= 0 or mask.area_px > box.width*box.height*1.4:
                reasons.append('implausible_mask_area')
            if not mask.rle_counts:
                reasons.append('mask_pixels_unavailable_for_independent_validation')
            else:
                try:
                    counts=json.loads(mask.rle_counts)
                    if not isinstance(counts,list) or any(type(n) is not int or n<0 for n in counts) or sum(counts)!=asset.width_px*asset.height_px:
                        raise ValueError('invalid RLE extent')
                    raster=np.repeat(np.arange(len(counts))%2,counts).reshape(image.shape[:2]).astype(bool)
                    yy,xx=np.where(raster)
                    inside=(xx>=box.x)&(xx<=box.x_max)&(yy>=box.y)&(yy<=box.y_max)
                    if not len(xx) or inside.mean()<.95:
                        reasons.append('mask_swallows_neighbors')
                    anchors=c.get('arm_source_px') or c.get('symbol_path',[])
                    if c.get('plates'):
                        anchors=[[x+(w-1)/2,y+(h-1)/2] for x,y,w,h in c['plates']]
                    mask_ink=raster.astype(np.uint8)*255
                    if not anchors or np.mean([sample_support(mask_ink,[p,p],c.get('uncertainty_px',1))['support_fraction']
                                               for p in anchors])<.8:
                        reasons.append('mask_does_not_cover_measured_symbol')
                    # A mask can corroborate a symbol but is not evidence of
                    # improved terminal localization. Keep the CV measurements.
                except (ValueError,TypeError,MemoryError):
                    reasons.append('invalid_mask_encoding')
            mask.source_asset_id=asset.id
            mask.verified=False
            mask.prompt_provenance.update(entity_candidate_id=c['id'],source_bbox=box.to_dict(),
                prompt_points=points,prompt_labels=prompt.labels,source_asset_id=asset.id,
                verification_status='REJECTED' if reasons else 'CORROBORATING',
                rejection_reasons=reasons,used_for_connectivity=False,localization_improved=False)
            record['masks'].append(mask.to_dict())
            masks.append(mask)
        records.append(record)
    candidates['segmentation_diagnostics']=records
    return SegmentationResult(status=ExtractionStatus.SUCCESS if masks else
                              ExtractionStatus.NO_EVIDENCE if available else ExtractionStatus.UNAVAILABLE,
                              masks=masks,provider=provider.name)

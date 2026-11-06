"""Pixel deletion regressions; these exercise masks independently of YOLO."""
from copy import deepcopy

import cv2
import numpy as np

from ai.evidence.cv.circuit_body_mask import remove_verified_bodies
from ai.evidence.cv.circuit_symbols import proposal
from ai.evidence.cv.circuits_cv import CircuitCVCandidateExtractor
from shared.schemas.evidence import SourceBBox


def drawing():
    image = np.full((130, 310, 3), 255, np.uint8)
    points = np.array([[10,65],[70,65],[74,58],[80,72],[86,58],[92,72],[98,58],[104,65],[290,65]])
    cv2.polylines(image, [points.astype(np.int32)], False, (0,0,0), 1)
    return image, points


def test_oversized_r4_path_is_rejected_without_erasing_lower_rail():
    image, points = drawing()
    ink = (image[:,:,0] == 0).astype(np.uint8)
    broad = proposal('resistor', points[1:], [points[1],points[-1]], 1, notation='zigzag')
    broad['id'] = 'historical_oversized_R4'
    before = ink.copy()
    after, removed, audit = remove_verified_bodies(ink, [broad], 1)
    assert 'symbol_path_consumes_long_conductor' in broad['body_mask_reasons']
    assert np.array_equal(after, before) and np.array_equal(ink, before)
    assert not removed.any() and audit['added_pixels'] == 0


def test_oversized_bbox_cannot_authorize_removing_any_extra_pixels():
    image, points = drawing()
    ink = (image[:,:,0] == 0).astype(np.uint8)
    small = proposal('resistor', points[1:-1], [points[1],points[-2]], 1, notation='zigzag')
    small['id'] = 'R4'
    broad = deepcopy(small)
    broad['bbox'] = SourceBBox(0, 40, 305, 50)
    a, removed, audit = remove_verified_bodies(ink, [small], 1)
    b, other, _ = remove_verified_bodies(ink, [broad], 1)
    assert np.array_equal(a,b) and np.array_equal(removed,other)
    assert np.all(b[65,110:290]) and audit['retained_pixels_unchanged']


def test_junction_attached_inside_symbol_body_rejects_mask():
    image, points = drawing()
    cv2.line(image, (86,58), (86,20), (0,0,0), 1)
    ink = (image[:,:,0] == 0).astype(np.uint8)
    symbol = proposal('resistor', points[1:-1], [points[1],points[-2]], 1, notation='zigzag')
    symbol['id'] = 'R4'
    after, removed, _ = remove_verified_bodies(ink, [symbol], 1)
    assert 'mask_contacts_adjacent_conductor' in symbol['body_mask_reasons']
    assert not removed.any() and np.array_equal(ink, after)


def test_extractor_preserves_original_and_exact_removed_pixel_evidence():
    image, _ = drawing()
    before = image.copy()
    result = CircuitCVCandidateExtractor().extract(image, source_width=310, source_height=130,
        symbol_regions=[('resistor',SourceBBox(68,56,39,18))])
    assert np.array_equal(image,before)
    removed = result['removed_symbol_pixels'] != 0
    assert np.array_equal(removed, (result['body_mask_before'] != 0) & (result['conductor_mask'] == 0))
    assert not np.any((result['conductor_mask'] != 0) & (result['original_binary'] == 0))
    assert np.all(result['conductor_mask'][65,110:290])


def test_mask_cap_cannot_erase_a_junction_immediately_beyond_terminal():
    image,points=drawing()
    cv2.line(image,(106,65),(106,20),(0,0,0),1)
    ink=(image[:,:,0]==0).astype(np.uint8)
    symbol=proposal('resistor',points[1:-1],[points[1],points[-2]],1,notation='zigzag')
    symbol['id']='R4'
    after,removed,_=remove_verified_bodies(ink,[symbol],1)
    assert symbol['body_mask_status']=='ACCEPTED'
    assert after[65,106] and np.array_equal(after[:,106],ink[:,106])
    assert not np.any(removed[:,105:])

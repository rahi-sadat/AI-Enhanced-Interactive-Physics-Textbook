import cv2
import numpy as np

from ai.evidence.cv.circuit_geometry_validator import CircuitGeometryValidator


def test_measured_stroke_boundary_pixel_is_not_a_whole_component_crossing():
    image=np.full((40,100,3),255,np.uint8)
    cv2.line(image,(5,20),(95,20),(0,0,0),3)
    ink=(image[:,:,0]==0).astype(np.uint8)*255
    mask=np.zeros_like(ink);mask[20,50]=1
    conductor=ink.copy();conductor[mask!=0]=0
    candidates=dict(components=[],wire_paths=[dict(id='real',points=[[5,20],[95,20]],ends=[1,2])],
        conductor_mask=conductor,component_body_mask=mask)
    checked=CircuitGeometryValidator().validate(image,candidates)
    assert checked['wire_paths'][0]['conductor_support_fraction']==1
    conductor[16:25,40:61]=0
    checked=CircuitGeometryValidator().validate(image,candidates)
    assert checked['wire_paths']==[] and checked['validation_issues'][0]['code']=='UNSUPPORTED_WIRE_PATH'

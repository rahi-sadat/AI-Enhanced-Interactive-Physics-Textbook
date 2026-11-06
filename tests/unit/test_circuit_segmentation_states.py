import pytest

from ai.evidence.segmentation.circuit_prompts import circuit_segmentation_state


@pytest.mark.parametrize('status,verdict,geometry,expected',[
    ('success','CORROBORATING',True,'WORKING_MASKS_ACCEPTED'),
    ('success','REJECTED',True,'WORKING_MASKS_REJECTED'),
    ('no_evidence',None,True,'WORKING_MASKS_REJECTED'),
    ('unavailable',None,True,'UNAVAILABLE_CV_VERIFIED'),
    ('unavailable',None,False,'UNAVAILABLE_GEOMETRY_INSUFFICIENT')])
def test_sam_health_does_not_override_independent_cv_geometry(status,verdict,geometry,expected):
    records=[dict(status=status,masks=[dict(promptProvenance={'verification_status':verdict})] if verdict else [])]
    result=circuit_segmentation_state(records,geometry)
    assert result['state']==expected and result['geometry_blocked']==(not geometry)
    assert result['sam_required_for_readiness'] is False

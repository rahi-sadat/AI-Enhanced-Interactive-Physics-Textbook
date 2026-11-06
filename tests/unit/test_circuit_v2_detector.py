"""Offline model-boundary tests with explicitly canned detector tensors."""
from types import SimpleNamespace
from unittest.mock import Mock
import numpy as np
import pytest
from ai.perception.circuits.circuit_v2 import CircuitV2Detector,MODEL_CLASSES


def detector(names=None):
    result=SimpleNamespace(orig_shape=(60,100),names=MODEL_CLASSES,boxes=SimpleNamespace(
        cls=np.array([0.,1.,2.,3.,0.,0.]),conf=np.array([.8,.7,.6,.5,.1,.9]),
        xyxy=np.array([[2,3,12,9],[20,30,24,45],[40,25,50,29],[70,3,85,13],[1,2,5,7],[-1,3,9,8]],float)))
    d=CircuitV2Detector();d._model=SimpleNamespace(names=names or MODEL_CLASSES,predict=Mock(return_value=[result]))
    return d,result


def test_real_class_indices_preserve_original_frame_and_reject_invalid_proposals():
    d,_=detector();r=d.predict(np.zeros((60,100,3),np.uint8))
    assert {x.kind for x in r}==set(MODEL_CLASSES.values()) and len(r)==4
    assert next(x for x in r if x.kind=='voltage_source').bbox.x==20
    assert all(x.confidence<=.95 for x in r)


def test_mismatched_checkpoint_classes_are_not_silently_relabelled():
    d,_=detector({0:'voltage_source',1:'resistor',2:'capacitor',3:'switch'})
    with pytest.raises(ValueError,match='class indices'):d.predict(np.zeros((60,100,3),np.uint8))
    d._model.predict.assert_not_called()


def test_wrong_result_frame_is_rejected():
    d,result=detector();result.orig_shape=(30,50)
    with pytest.raises(ValueError,match='source image dimensions'):d.predict(np.zeros((60,100,3),np.uint8))

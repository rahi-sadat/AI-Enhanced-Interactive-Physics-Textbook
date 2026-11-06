from copy import deepcopy

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api import circuit_v2_lab
from ai.evidence.grounding.circuit_integrity import validate_circuit_integrity
from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.resolution.engine import ResolutionEngine
from tests.unit.test_circuit_grounding_repair import ground_fixture


def test_correction_creates_a_new_analysis_and_retains_original_source_evidence(monkeypatch):
    _,_,book,_=ground_fixture(closed=True)
    original=deepcopy(book.to_dict())
    monkeypatch.setattr(circuit_v2_lab,'run_experiment',lambda *args:{'book_ir':deepcopy(original)})
    app=FastAPI();app.include_router(circuit_v2_lab.create_router(lambda:()))
    with TestClient(app) as client:
        uploaded=client.post('/api/experiments/circuit-v2',files={'file':('offline.png',b'canned','image/png')}).json()
        token=uploaded['analysis_id']
        payload=dict(analysis_id=token,component_id='r1',value=15.,unit='ohm')
        corrected=client.post('/api/experiments/circuit-v2/correct-value',json=payload)
        assert corrected.status_code==200,corrected.text
        result=corrected.json()
        assert result['parent_analysis_id']==token and result['analysis_id']!=token
        assert result['ideal_analysis']['status']=='IDEAL_SOLVED'
        assert result['compiler']['status']=='READY'
        component=next(c for c in result['book_ir']['parameters']['components'] if c['id']=='r1')
        assert component['value']==15 and component['value_provenance']['source']=='user_corrected'
        assert result['book_ir']['evidence']==original['evidence']
        assert result['book_ir']['parameters']['geometric_conductor_graph']==original['parameters']['geometric_conductor_graph']
        old=client.post('/api/experiments/circuit-v2/analysis',json=dict(analysis_id=token)).json()
        assert next(c for c in old['graph']['components'] if c['id']=='r1')['value']==10
        assert client.post('/api/experiments/circuit-v2/correct-value',json={**payload,'component_id':'missing'}).status_code==422
        assert client.post('/api/experiments/circuit-v2/correct-value',json={**payload,'value':-1.}).status_code==422


def test_missing_values_never_receive_automatic_circuit_defaults():
    _,_,book,_=ground_fixture()
    c=next(c for c in book.parameters['components'] if c['id']=='r1')
    c.pop('value');c.pop('value_provenance')
    ResolutionEngine.auto_resolve(book)
    assert 'value' not in c and not book.assumptions
    assert PhysicsCompiler().compile(book).scene is None
    c.update(value=100,value_provenance={'source':'auto_policy','user_accepted':False})
    assert any(i['code']=='UNCONFIRMED_CIRCUIT_VALUE' for i in validate_circuit_integrity(book))
    assert PhysicsCompiler().compile(book).scene is None

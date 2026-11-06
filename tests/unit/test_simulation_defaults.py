"""Offline regressions for simulation-first model assumptions and image alignment."""
from copy import deepcopy
import pytest

from ai.ingestion.PhysicsCompiler import PhysicsCompiler
from ai.resolution.auto import AutoResolutionEngine
from ai.resolution.engine import ResolutionEngine
from shared.schemas.ingestion import BookEntity, BookIR, ProvenanceRecord
from tests.unit.test_circuit_capacitor_pipeline import grounded_rc


def test_symbolic_rc_requires_explicit_circuit_policy_decisions():
    _, book, _ = grounded_rc(symbolic=True)
    geometry, evidence = deepcopy(book.geometry), deepcopy(book.evidence)
    report = ResolutionEngine.auto_resolve(book)
    assert not report.ready and not book.assumptions
    for cid,policy in [('supply','policy_standard_dc_voltage'),('load','policy_standard_dc_resistance'),
                       ('storage','policy_standard_capacitance')]:
        assert ResolutionEngine.apply_policy(book,policy,f'component.{cid}.value').success
    assert ResolutionEngine.apply_policy(book,'policy_uncharged_capacitor','component.storage.initial_voltage').success
    values = {c['type']: c for c in book.parameters['components']}
    assert values['voltage_source']['value'] == 10
    assert values['resistor']['value'] == 100
    assert values['capacitor']['value'] == .001
    assert values['capacitor']['initial_voltage'] == 0
    for decision in book.resolutions.values():
        assert decision['userAccepted'] is True
    compiled = PhysicsCompiler().compile(book)
    assert compiled.status == 'READY', compiled.issues
    assert compiled.scene['parameters']['load']['provenance'] == 'policy_default'
    assert compiled.scene['source']['width'] == geometry['width']
    assert book.geometry == geometry and book.evidence == evidence
    snapshot = book.to_dict()
    ResolutionEngine.auto_resolve(book)
    assert book.to_dict() == snapshot


def test_observed_circuit_values_survive_reviewed_initial_condition():
    _, book, _ = grounded_rc()
    before = {c['id']: (c['value'], deepcopy(c.get('value_provenance')))
              for c in book.parameters['components']}
    result = AutoResolutionEngine.resolve(book)
    assert not result.readiness.ready
    assert not result.failures
    for component in book.parameters['components']:
        assert (component['value'], component.get('value_provenance')) == before[component['id']]
    assert result.assumptions==[]
    assert PhysicsCompiler().compile(book).scene is None
    assert ResolutionEngine.apply_policy(book,'policy_uncharged_capacitor','component.storage.initial_voltage').success
    assert PhysicsCompiler().compile(book).status == 'READY'


def test_refraction_missing_indices_and_angle_compiles_on_measured_boundary():
    geometry = {'width': 600, 'height': 400, 'boundary_y': 200, 'normal_x': 300}
    book = BookIR(source_asset_id='image', figure_id='figure', domain='optics',
                  subtype='interface_refraction', geometry=deepcopy(geometry),
                  entities=[BookEntity(id='surface', type='interface_boundary',
                                       position_source_px={'x': 300, 'y': 200}, evidence_refs=['cv'])],
                  parameter_provenance={key: ProvenanceRecord(source='diagram_measurement')
                                        for key in ('boundary_y', 'normal_x')})
    report = ResolutionEngine.auto_resolve(book)
    assert report.ready, report.blockers
    assert book.parameters['n1'] == 1.0003 and book.parameters['n2'] == 1.333
    assert book.parameters['theta1'] == 45
    assert book.geometry == geometry
    assert PhysicsCompiler().compile(book).status == 'READY'


def test_candidates_are_retained_while_model_uses_disclosed_assumptions():
    candidates = [{'numericValue': .8, 'quantityCandidate': 'length', 'confidence': .9}]
    book = BookIR(source_asset_id='image', figure_id='figure', domain='mechanics',
                  subtype='pendulum', provenance={'candidate_parameters': deepcopy(candidates)})
    report = ResolutionEngine.auto_resolve(book)
    assert book.parameters['length'] == 1
    assert book.provenance['candidate_parameters'] == candidates
    assert book.parameter_provenance['length'].source == 'auto_policy'
    assert not book.parameter_provenance['length'].user_accepted
    assert not report.ready  # Values alone cannot invent a pivot and bob.
    assert not book.geometry and not book.entities


def test_unknown_connections_cannot_be_filled_by_electrical_value_defaults():
    _, book, _ = grounded_rc(symbolic=True)
    book.geometry['circuit_topology']['verified_connectivity'] = False
    before = deepcopy(book.parameters)
    report = ResolutionEngine.auto_resolve(book)
    assert not report.ready
    assert book.parameters == before and not book.assumptions


@pytest.mark.parametrize('subtype,role,landmark', [
    ('thin_lens', 'lens', 'lens_center'),
    ('spherical_mirror', 'mirror', 'pole'),
])
def test_optical_figure_with_missing_values_gets_a_runnable_exploration_model(subtype, role, landmark):
    point = {'x': 450, 'y': 225}
    geometry = {'width': 900, 'height': 450, landmark: point}
    book = BookIR(source_asset_id='image', figure_id='figure', domain='optics', subtype=subtype,
                  geometry=deepcopy(geometry), parameters={landmark: deepcopy(point)},
                  parameter_provenance={landmark: ProvenanceRecord(source='diagram_measurement')},
                  entities=[BookEntity(id=role, type=role, position_source_px=deepcopy(point),
                                       evidence_refs=['cv'])])
    result = ResolutionEngine.auto_resolve(book)
    assert result.ready, result.blockers
    compiled = PhysicsCompiler().compile(book)
    assert compiled.status == 'READY', compiled.issues
    assert compiled.scene['parameters']['focalLength']['provenance'] == 'auto_policy'
    assert book.geometry == geometry

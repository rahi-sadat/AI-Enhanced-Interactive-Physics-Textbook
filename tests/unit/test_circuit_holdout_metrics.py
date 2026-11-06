from copy import deepcopy

from tests.acceptance.circuit_v2_holdout import matches,exact_graph
from scripts.generate_circuit_v2_holdout import schematic


def test_holdout_matching_counts_false_positives_and_wrong_types():
    truth=[dict(type='resistor',bbox=[1,1,10,10])]
    predictions=[dict(type='resistor',bbox=[1,1,10,10]),dict(type='voltage_source',bbox=[1,1,10,10])]
    assert matches(truth,predictions)==[(0,0)]
    assert matches(truth,[predictions[1]])==[]


def test_graph_metric_is_invariant_to_node_names_and_resistor_terminal_order():
    _,case=schematic()
    components=deepcopy(case['components'])
    for c in components:c['nodes']=['renamed_'+n for n in reversed(c['nodes'])]
    pairs=[(i,i) for i in range(len(components))]
    assert exact_graph(case['components'],components,pairs)
    components[-1]['nodes']=['renamed_A','renamed_D']
    assert not exact_graph(case['components'],components,pairs)


def test_generator_records_known_analytic_network_before_any_model_runs():
    image,case=schematic()
    assert image.shape==(440,740,3) and case['expected_resistance_ohm']==8
    assert case['source_current_a']==1.5 and len(case['components'])==5

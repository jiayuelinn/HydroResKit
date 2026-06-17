import pandas as pd

from hydroreskit.aggregation import aggregate_dimensions, compute_resilience_score
from hydroreskit.preprocessing import align_direction, normalize
from hydroreskit.schema import load_indicator_schema
from hydroreskit.weighting import equal_weights


def test_demo_scoring_pipeline():
    schema = load_indicator_schema("configs/indicator_schema.yml")
    frame = pd.read_csv("data_sample/demo_indicators.csv").set_index("unit_id")

    normalized = pd.DataFrame(index=frame.index)
    for item in schema:
        values = normalize(frame[item["indicator_id"]])
        normalized[item["indicator_id"]] = align_direction(values, item["expected_direction"])

    weights = equal_weights(list(normalized.columns))
    dimensions = aggregate_dimensions(normalized, schema, weights)
    score = compute_resilience_score(dimensions)

    assert len(score) == len(frame)
    assert score.between(0, 1).all()


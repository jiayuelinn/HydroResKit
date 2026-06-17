import pandas as pd

from hydroreskit.diagnostics import (
    contribution_summary,
    indicator_contribution_table,
    missing_value_report,
    rank_table,
    unit_missing_report,
)
from hydroreskit.schema import load_indicator_schema
from hydroreskit.weighting import user_defined_weights


def test_user_defined_weights_normalize():
    weights = user_defined_weights({"a": 2, "b": 1}, ["a", "b"])
    assert weights["a"] == 2 / 3
    assert weights["b"] == 1 / 3


def test_missing_reports_include_absent_columns():
    schema = load_indicator_schema("configs/indicator_schema.yml")
    frame = pd.DataFrame({"h_extreme_precip_days": [1.0, None]}, index=["u1", "u2"])
    report = missing_value_report(frame, schema)
    assert report.loc[report["indicator_id"] == "h_extreme_precip_days", "missing_count"].iloc[0] == 1
    assert report.loc[report["indicator_id"] == "h_precip_variability", "present"].iloc[0] == False
    unit_report = unit_missing_report(frame, schema)
    assert unit_report.shape[0] == 2


def test_rank_and_contributions():
    schema = [
        {"indicator_id": "a", "dimension": "hazard", "variable_name": "A"},
        {"indicator_id": "b", "dimension": "exposure", "variable_name": "B"},
    ]
    normalized = pd.DataFrame({"a": [1.0, 0.0], "b": [0.5, 1.0]}, index=["u1", "u2"])
    weights = pd.Series({"a": 0.4, "b": 0.6})
    contributions = indicator_contribution_table(normalized, weights, schema)
    summary = contribution_summary(contributions)
    ranks = rank_table(pd.Series([0.7, 0.4], index=["u1", "u2"], name="resilience_score"))
    assert contributions.shape[0] == 4
    assert "mean_abs_contribution" in summary.columns
    assert ranks.iloc[0]["unit_id"] == "u1"


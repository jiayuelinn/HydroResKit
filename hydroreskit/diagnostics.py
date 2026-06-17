"""Diagnostics for auditable resilience assessment."""

from __future__ import annotations

import pandas as pd

from hydroreskit.aggregation import aggregate_dimensions, compute_resilience_score
from hydroreskit.weighting import entropy_weights, equal_weights, pca_weights


def missing_value_report(frame: pd.DataFrame, schema: list[dict]) -> pd.DataFrame:
    """Report missingness by indicator, including absent schema columns."""
    n_units = len(frame)
    rows = []
    for item in schema:
        indicator_id = item["indicator_id"]
        present = indicator_id in frame.columns
        if present:
            missing_count = int(frame[indicator_id].isna().sum())
        else:
            missing_count = n_units
        rows.append(
            {
                "indicator_id": indicator_id,
                "dimension": item["dimension"],
                "present": present,
                "valid_count": n_units - missing_count,
                "missing_count": missing_count,
                "missing_fraction": missing_count / n_units if n_units else 0.0,
                "missing_value_rule": item.get("missing_value_rule", ""),
                "source_dataset": item.get("source_dataset", ""),
            }
        )
    return pd.DataFrame(rows)


def unit_missing_report(frame: pd.DataFrame, schema: list[dict], *, unit_id_name: str = "unit_id") -> pd.DataFrame:
    """Report missingness by spatial unit."""
    indicators = [item["indicator_id"] for item in schema]
    expected = pd.DataFrame(index=frame.index)
    for indicator_id in indicators:
        if indicator_id in frame.columns:
            expected[indicator_id] = frame[indicator_id]
        else:
            expected[indicator_id] = pd.NA

    missing_count = expected.isna().sum(axis=1)
    report = pd.DataFrame(
        {
            unit_id_name: frame.index,
            "missing_count": missing_count.to_numpy(),
            "valid_count": len(indicators) - missing_count.to_numpy(),
            "missing_fraction": missing_count.to_numpy() / len(indicators) if indicators else 0.0,
        }
    )
    return report


def rank_table(
    scores: pd.Series | pd.DataFrame,
    *,
    score_column: str = "resilience_score",
    unit_id_name: str = "unit_id",
) -> pd.DataFrame:
    """Create descending rank table from a score series or DataFrame."""
    if isinstance(scores, pd.DataFrame):
        values = scores[score_column]
    else:
        values = scores
    ranks = values.rank(ascending=False, method="average")
    return pd.DataFrame(
        {
            unit_id_name: values.index,
            score_column: values.to_numpy(),
            "rank": ranks.to_numpy(),
        }
    ).sort_values(["rank", unit_id_name])


def indicator_contribution_table(
    normalized_indicators: pd.DataFrame,
    weights: pd.Series,
    schema: list[dict],
    *,
    unit_id_name: str = "unit_id",
) -> pd.DataFrame:
    """Return long-format weighted indicator contributions by unit."""
    metadata = {
        item["indicator_id"]: {
            "dimension": item["dimension"],
            "variable_name": item.get("variable_name", item["indicator_id"]),
        }
        for item in schema
    }

    rows = []
    for indicator_id in normalized_indicators.columns:
        weight = float(weights.get(indicator_id, 0.0))
        values = normalized_indicators[indicator_id]
        contributions = values * weight
        meta = metadata.get(indicator_id, {"dimension": "", "variable_name": indicator_id})
        for unit_id, value in contributions.items():
            rows.append(
                {
                    unit_id_name: unit_id,
                    "indicator_id": indicator_id,
                    "dimension": meta["dimension"],
                    "variable_name": meta["variable_name"],
                    "weight": weight,
                    "normalized_value": values.loc[unit_id],
                    "weighted_contribution": value,
                }
            )
    return pd.DataFrame(rows)


def contribution_summary(contributions: pd.DataFrame) -> pd.DataFrame:
    """Summarize indicator contribution magnitude across units."""
    grouped = contributions.groupby(["indicator_id", "dimension", "variable_name"], as_index=False)
    summary = grouped.agg(
        mean_contribution=("weighted_contribution", "mean"),
        mean_abs_contribution=("weighted_contribution", lambda s: s.abs().mean()),
        max_contribution=("weighted_contribution", "max"),
        min_contribution=("weighted_contribution", "min"),
    )
    return summary.sort_values("mean_abs_contribution", ascending=False)


def weighting_method_comparison(
    normalized_indicators: pd.DataFrame,
    schema: list[dict],
    *,
    unit_id_name: str = "unit_id",
) -> pd.DataFrame:
    """Compare final scores and ranks under equal, entropy, and PCA weights."""
    methods = {
        "equal": equal_weights(list(normalized_indicators.columns)),
        "entropy": entropy_weights(normalized_indicators),
        "pca": pca_weights(normalized_indicators),
    }
    output = pd.DataFrame({unit_id_name: normalized_indicators.index})
    for method, weights in methods.items():
        dimensions = aggregate_dimensions(normalized_indicators, schema, weights)
        scores = compute_resilience_score(dimensions)
        output[f"{method}_score"] = scores.to_numpy()
        output[f"{method}_rank"] = scores.rank(ascending=False, method="average").to_numpy()
    output["score_range"] = output[[f"{method}_score" for method in methods]].max(axis=1) - output[
        [f"{method}_score" for method in methods]
    ].min(axis=1)
    output["rank_range"] = output[[f"{method}_rank" for method in methods]].max(axis=1) - output[
        [f"{method}_rank" for method in methods]
    ].min(axis=1)
    return output

"""Aggregation utilities for resilience scoring."""

from __future__ import annotations

import pandas as pd


def weighted_sum(frame: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Compute weighted sum after aligning weights to frame columns."""
    aligned = weights.reindex(frame.columns)
    if aligned.isna().any():
        missing = aligned[aligned.isna()].index.tolist()
        raise ValueError(f"Missing weights for columns: {missing}")
    return frame.mul(aligned, axis=1).sum(axis=1)


def aggregate_dimensions(
    normalized_indicators: pd.DataFrame,
    schema: list[dict],
    weights: pd.Series,
) -> pd.DataFrame:
    """Aggregate indicator scores to dimension scores."""
    dimension_scores = {}
    for dimension in sorted({item["dimension"] for item in schema}):
        ids = [item["indicator_id"] for item in schema if item["dimension"] == dimension]
        available = [col for col in ids if col in normalized_indicators.columns]
        if not available:
            continue
        sub_weights = weights.reindex(available)
        sub_weights = sub_weights / sub_weights.sum()
        dimension_scores[dimension] = weighted_sum(normalized_indicators[available], sub_weights)
    return pd.DataFrame(dimension_scores, index=normalized_indicators.index)


def compute_resilience_score(
    dimension_scores: pd.DataFrame,
    dimension_weights: pd.Series | None = None,
) -> pd.Series:
    """Aggregate dimension scores to a final resilience score."""
    if dimension_weights is None:
        dimension_weights = pd.Series(1.0 / len(dimension_scores.columns), index=dimension_scores.columns)
    return weighted_sum(dimension_scores, dimension_weights)


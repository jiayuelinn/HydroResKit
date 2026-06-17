"""Uncertainty diagnostics for indicator weighting."""

from __future__ import annotations

import numpy as np
import pandas as pd

from hydroreskit.aggregation import weighted_sum


def perturb_weights(
    base_weights: pd.Series,
    n: int = 100,
    concentration: float = 100.0,
    random_state: int | None = 42,
) -> pd.DataFrame:
    """Generate perturbed weights around a base weight vector using a Dirichlet law."""
    rng = np.random.default_rng(random_state)
    alpha = base_weights.to_numpy(dtype=float) * concentration
    samples = rng.dirichlet(alpha, size=n)
    return pd.DataFrame(samples, columns=base_weights.index)


def rank_stability(frame: pd.DataFrame, weight_samples: pd.DataFrame) -> pd.DataFrame:
    """Compute rank stability across sampled weights."""
    ranks = []
    for _, weights in weight_samples.iterrows():
        scores = weighted_sum(frame, weights)
        ranks.append(scores.rank(ascending=False, method="average"))
    rank_frame = pd.concat(ranks, axis=1)
    return pd.DataFrame(
        {
            "rank_mean": rank_frame.mean(axis=1),
            "rank_std": rank_frame.std(axis=1),
            "rank_p05": rank_frame.quantile(0.05, axis=1),
            "rank_p95": rank_frame.quantile(0.95, axis=1),
        },
        index=frame.index,
    )


def missing_indicator_sensitivity(
    frame: pd.DataFrame,
    weights: pd.Series,
    *,
    score_delta_threshold: float = 0.01,
) -> pd.DataFrame:
    """Assess score and rank sensitivity to dropping each indicator."""
    columns = [
        "dropped_indicator",
        "mean_abs_score_delta",
        "median_abs_score_delta",
        "p05_abs_score_delta",
        "p25_abs_score_delta",
        "p75_abs_score_delta",
        "p95_abs_score_delta",
        "max_abs_score_delta",
        "mean_abs_rank_delta",
        "median_abs_rank_delta",
        "p95_abs_rank_delta",
        "max_abs_rank_delta",
        "affected_basin_pct",
    ]
    baseline = weighted_sum(frame, weights)
    baseline_rank = baseline.rank(ascending=False, method="average")
    rows = []
    for indicator_id in frame.columns:
        remaining = [col for col in frame.columns if col != indicator_id]
        if not remaining:
            continue
        sub_weights = weights.reindex(remaining)
        sub_weights = sub_weights / sub_weights.sum()
        scores = weighted_sum(frame[remaining], sub_weights)
        ranks = scores.rank(ascending=False, method="average")
        score_delta = scores - baseline
        rank_delta = ranks - baseline_rank
        abs_score_delta = score_delta.abs()
        abs_rank_delta = rank_delta.abs()
        rows.append(
            {
                "dropped_indicator": indicator_id,
                "mean_abs_score_delta": float(abs_score_delta.mean()),
                "median_abs_score_delta": float(abs_score_delta.median()),
                "p05_abs_score_delta": float(abs_score_delta.quantile(0.05)),
                "p25_abs_score_delta": float(abs_score_delta.quantile(0.25)),
                "p75_abs_score_delta": float(abs_score_delta.quantile(0.75)),
                "p95_abs_score_delta": float(abs_score_delta.quantile(0.95)),
                "max_abs_score_delta": float(abs_score_delta.max()),
                "mean_abs_rank_delta": float(abs_rank_delta.mean()),
                "median_abs_rank_delta": float(abs_rank_delta.median()),
                "p95_abs_rank_delta": float(abs_rank_delta.quantile(0.95)),
                "max_abs_rank_delta": float(abs_rank_delta.max()),
                "affected_basin_pct": float((abs_score_delta > score_delta_threshold).mean() * 100.0),
            }
        )
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows, columns=columns).sort_values("mean_abs_score_delta", ascending=False)

"""Weighting methods for watershed resilience indicators."""

from __future__ import annotations

import numpy as np
import pandas as pd


def equal_weights(columns: list[str]) -> pd.Series:
    """Return equal weights for columns."""
    if not columns:
        raise ValueError("columns cannot be empty")
    return pd.Series(1.0 / len(columns), index=columns)


def entropy_weights(frame: pd.DataFrame, epsilon: float = 1e-12) -> pd.Series:
    """Compute entropy weights for normalized indicators."""
    if frame.empty:
        raise ValueError("frame cannot be empty")

    x = frame.astype(float).clip(lower=0).fillna(0)
    col_sums = x.sum(axis=0).replace(0, np.nan)
    p = x.div(col_sums, axis=1).fillna(0)
    n = len(x)
    if n <= 1:
        return equal_weights(list(frame.columns))

    entropy = -(p * np.log(p + epsilon)).sum(axis=0) / np.log(n)
    diversity = 1 - entropy
    if np.isclose(diversity.sum(), 0):
        return equal_weights(list(frame.columns))
    return diversity / diversity.sum()


def pca_weights(frame: pd.DataFrame) -> pd.Series:
    """Approximate first-component PCA weights without a sklearn dependency."""
    if frame.empty:
        raise ValueError("frame cannot be empty")

    x = frame.astype(float).fillna(frame.mean(numeric_only=True))
    x = (x - x.mean(axis=0)) / x.std(axis=0).replace(0, 1)
    _, _, vt = np.linalg.svd(x.to_numpy(), full_matrices=False)
    loadings = np.abs(vt[0])
    if np.isclose(loadings.sum(), 0):
        return equal_weights(list(frame.columns))
    return pd.Series(loadings / loadings.sum(), index=frame.columns)


def user_defined_weights(
    weights: dict[str, float] | pd.Series,
    columns: list[str],
    *,
    normalize: bool = True,
    strict: bool = True,
) -> pd.Series:
    """Validate and align user-defined indicator weights."""
    if not columns:
        raise ValueError("columns cannot be empty")

    series = pd.Series(weights, dtype=float)
    missing = [col for col in columns if col not in series.index]
    if strict and missing:
        raise ValueError(f"Missing user-defined weights for columns: {missing}")

    aligned = series.reindex(columns).fillna(0.0)
    if (aligned < 0).any():
        negative = aligned[aligned < 0].index.tolist()
        raise ValueError(f"Weights must be non-negative: {negative}")

    total = aligned.sum()
    if total <= 0:
        raise ValueError("At least one user-defined weight must be positive.")
    if normalize:
        aligned = aligned / total
    return aligned


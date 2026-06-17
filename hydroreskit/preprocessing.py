"""Preprocessing helpers for resilience indicators."""

from __future__ import annotations

import numpy as np
import pandas as pd


def normalize(
    values: pd.Series,
    method: str = "minmax",
    *,
    lower_quantile: float = 0.05,
    upper_quantile: float = 0.95,
) -> pd.Series:
    """Normalize an indicator series."""
    x = values.astype(float)
    if method == "minmax":
        lo, hi = x.min(skipna=True), x.max(skipna=True)
    elif method == "robust":
        lo, hi = x.quantile(lower_quantile), x.quantile(upper_quantile)
        x = x.clip(lo, hi)
    elif method == "zscore":
        std = x.std(skipna=True)
        if std == 0 or np.isnan(std):
            return pd.Series(0.0, index=x.index)
        z = (x - x.mean(skipna=True)) / std
        return 1.0 / (1.0 + np.exp(-z))
    else:
        raise ValueError(f"Unsupported normalization method: {method}")

    if hi == lo or np.isnan(hi) or np.isnan(lo):
        return pd.Series(0.0, index=x.index)
    return (x - lo) / (hi - lo)


def align_direction(values: pd.Series, expected_direction: str) -> pd.Series:
    """Align indicators so higher values mean higher resilience."""
    if expected_direction == "positive":
        return values
    if expected_direction == "negative":
        return 1.0 - values
    raise ValueError("expected_direction must be positive or negative")


"""MODIS NDVI adapter helpers."""

from __future__ import annotations

import pandas as pd

from hydroreskit.adapters.timeseries import summarize_unit_timeseries


def ecological_fragility_indicator(
    ndvi_table: pd.DataFrame,
    *,
    ndvi_column: str,
    unit_id_column: str = "unit_id",
    time_column: str = "time",
    output_column: str = "s_ecological_fragility",
) -> pd.DataFrame:
    """Compute a simple vegetation instability proxy from NDVI variability."""
    summary = summarize_unit_timeseries(
        ndvi_table,
        unit_id_column=unit_id_column,
        time_column=time_column,
        value_column=ndvi_column,
        stats=("cv",),
    )
    return summary.rename(columns={"cv": output_column})


def ndvi_recovery_rate_indicator(
    ndvi_table: pd.DataFrame,
    *,
    ndvi_column: str,
    event_start: str,
    unit_id_column: str = "unit_id",
    time_column: str = "time",
    output_column: str = "r_ndvi_recovery_rate",
) -> pd.DataFrame:
    """Estimate post-event NDVI recovery as a linear trend after event_start."""
    data = ndvi_table.copy()
    data[time_column] = pd.to_datetime(data[time_column])
    post = data[data[time_column] >= pd.Timestamp(event_start)]
    summary = summarize_unit_timeseries(
        post,
        unit_id_column=unit_id_column,
        time_column=time_column,
        value_column=ndvi_column,
        stats=("trend",),
    )
    return summary.rename(columns={"trend": output_column})


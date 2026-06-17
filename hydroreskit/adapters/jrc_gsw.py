"""JRC Global Surface Water adapter helpers."""

from __future__ import annotations

import pandas as pd

from hydroreskit.adapters.timeseries import summarize_unit_timeseries


def surface_water_fraction_indicator(
    water_table: pd.DataFrame,
    *,
    water_fraction_column: str,
    unit_id_column: str = "unit_id",
    output_column: str = "a_surface_water_fraction",
) -> pd.DataFrame:
    """Return mean surface-water fraction per unit."""
    out = water_table.groupby(unit_id_column, as_index=False)[water_fraction_column].mean()
    return out.rename(columns={water_fraction_column: output_column})


def water_occurrence_recovery_indicator(
    water_table: pd.DataFrame,
    *,
    water_fraction_column: str,
    event_start: str,
    unit_id_column: str = "unit_id",
    time_column: str = "time",
    output_column: str = "r_water_occurrence_recovery",
) -> pd.DataFrame:
    """Estimate post-event water occurrence recovery as a linear trend."""
    data = water_table.copy()
    data[time_column] = pd.to_datetime(data[time_column])
    post = data[data[time_column] >= pd.Timestamp(event_start)]
    summary = summarize_unit_timeseries(
        post,
        unit_id_column=unit_id_column,
        time_column=time_column,
        value_column=water_fraction_column,
        stats=("trend",),
    )
    return summary.rename(columns={"trend": output_column})


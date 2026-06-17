"""Time-series aggregation adapters for basin-scale indicators."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path

import numpy as np
import pandas as pd

from hydroreskit.adapters.raster import aggregate_raster_to_boundaries


FREQ_ALIASES = {
    "annual": "Y",
    "yearly": "Y",
    "year": "Y",
    "monthly": "M",
    "month": "M",
    "seasonal": "Q",
    "quarterly": "Q",
}


def aggregate_unit_timeseries(
    frame: pd.DataFrame,
    *,
    unit_id_column: str = "unit_id",
    time_column: str = "time",
    value_columns: Sequence[str] | None = None,
    freq: str = "annual",
    agg: str | dict[str, str] = "mean",
) -> pd.DataFrame:
    """Aggregate an existing unit-level time series to a coarser frequency."""
    if unit_id_column not in frame.columns:
        raise ValueError(f"Missing unit ID column: {unit_id_column}")
    if time_column not in frame.columns:
        raise ValueError(f"Missing time column: {time_column}")

    data = frame.copy()
    data[time_column] = pd.to_datetime(data[time_column])
    if value_columns is None:
        value_columns = [
            col
            for col in data.columns
            if col not in {unit_id_column, time_column} and pd.api.types.is_numeric_dtype(data[col])
        ]
    if not value_columns:
        raise ValueError("No numeric value columns were found for time-series aggregation.")

    period_freq = FREQ_ALIASES.get(freq, freq)
    data["_period"] = data[time_column].dt.to_period(period_freq).dt.to_timestamp()
    grouped = data.groupby([unit_id_column, "_period"], as_index=False)[list(value_columns)].agg(agg)
    return grouped.rename(columns={"_period": time_column})


def summarize_unit_timeseries(
    frame: pd.DataFrame,
    *,
    unit_id_column: str = "unit_id",
    time_column: str = "time",
    value_column: str,
    stats: Iterable[str] = ("mean",),
) -> pd.DataFrame:
    """Summarize a unit-level time series into one row per unit."""
    if value_column not in frame.columns:
        raise ValueError(f"Missing value column: {value_column}")
    data = frame[[unit_id_column, time_column, value_column]].copy()
    data[time_column] = pd.to_datetime(data[time_column])
    data = data.sort_values([unit_id_column, time_column])

    rows = []
    for unit_id, group in data.groupby(unit_id_column):
        values = group[value_column].astype(float)
        row = {unit_id_column: unit_id}
        for stat in stats:
            if stat == "mean":
                row[stat] = values.mean()
            elif stat == "median":
                row[stat] = values.median()
            elif stat == "min":
                row[stat] = values.min()
            elif stat == "max":
                row[stat] = values.max()
            elif stat == "std":
                row[stat] = values.std()
            elif stat == "cv":
                mean = values.mean()
                row[stat] = np.nan if np.isclose(mean, 0) else values.std() / mean
            elif stat == "sum":
                row[stat] = values.sum()
            elif stat == "trend":
                row[stat] = _linear_trend(group[time_column], values)
            elif stat == "count":
                row[stat] = values.count()
            else:
                raise ValueError(f"Unsupported time-series statistic: {stat}")
        rows.append(row)
    return pd.DataFrame(rows)


def aggregate_raster_series_to_boundaries(
    raster_paths: Sequence[str | Path],
    boundaries,
    *,
    timestamps: Sequence[str | pd.Timestamp],
    id_column: str,
    stats: Iterable[str] = ("mean",),
    value_prefix: str = "value",
    band: int = 1,
    all_touched: bool = False,
) -> pd.DataFrame:
    """Aggregate a series of raster snapshots to basin boundaries."""
    if len(raster_paths) != len(timestamps):
        raise ValueError("raster_paths and timestamps must have the same length.")

    tables = []
    stat_names = tuple(stats)
    for raster_path, timestamp in zip(raster_paths, timestamps):
        table = aggregate_raster_to_boundaries(
            raster_path,
            boundaries,
            id_column=id_column,
            stats=stat_names,
            band=band,
            all_touched=all_touched,
        )
        table["time"] = pd.Timestamp(timestamp)
        rename = {stat: f"{value_prefix}_{stat}" for stat in stat_names}
        table = table.rename(columns=rename)
        tables.append(table)

    if not tables:
        return pd.DataFrame(columns=[id_column, "time"])
    return pd.concat(tables, ignore_index=True)


def _linear_trend(times: pd.Series, values: pd.Series) -> float:
    valid = values.notna()
    if valid.sum() < 2:
        return np.nan
    x = pd.to_datetime(times[valid]).map(pd.Timestamp.toordinal).to_numpy(dtype=float)
    y = values[valid].to_numpy(dtype=float)
    x = x - x.mean()
    if np.isclose(np.sum(x**2), 0):
        return np.nan
    return float(np.polyfit(x, y, deg=1)[0])


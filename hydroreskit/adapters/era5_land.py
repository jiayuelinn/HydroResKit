"""ERA5-Land adapter helpers.

The adapter assumes users download ERA5-Land data through the official
Copernicus Climate Data Store API or interface. HydroResKit then converts
the downloaded grids or basin-scale time series into resilience indicators.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from hydroreskit.adapters.timeseries import summarize_unit_timeseries


def build_monthly_cds_request(
    *,
    variables: Sequence[str],
    years: Sequence[int],
    months: Sequence[int] | None = None,
    area: Sequence[float] | None = None,
    product_type: str = "monthly_averaged_reanalysis",
    data_format: str = "netcdf",
) -> dict:
    """Build a CDS API request dictionary for ERA5-Land monthly means."""
    month_values = months if months is not None else range(1, 13)
    request = {
        "product_type": [product_type],
        "variable": list(variables),
        "year": [str(year) for year in years],
        "month": [f"{month:02d}" for month in month_values],
        "time": ["00:00"],
        "data_format": data_format,
    }
    if area is not None:
        request["area"] = list(area)
    return request


def precipitation_variability_indicator(
    monthly_table: pd.DataFrame,
    *,
    value_column: str,
    unit_id_column: str = "unit_id",
    time_column: str = "time",
    output_column: str = "h_precip_variability",
) -> pd.DataFrame:
    """Compute a precipitation variability proxy as coefficient of variation."""
    summary = summarize_unit_timeseries(
        monthly_table,
        unit_id_column=unit_id_column,
        time_column=time_column,
        value_column=value_column,
        stats=("cv",),
    )
    return summary.rename(columns={"cv": output_column})


def drought_month_count_indicator(
    monthly_table: pd.DataFrame,
    *,
    value_column: str,
    unit_id_column: str = "unit_id",
    time_column: str = "time",
    threshold_quantile: float = 0.2,
    output_column: str = "h_drought_intensity",
) -> pd.DataFrame:
    """Count low-water months per unit using a within-unit quantile threshold."""
    data = monthly_table[[unit_id_column, time_column, value_column]].copy()
    data[time_column] = pd.to_datetime(data[time_column])
    thresholds = data.groupby(unit_id_column)[value_column].quantile(threshold_quantile)
    data["_threshold"] = data[unit_id_column].map(thresholds)
    data["_is_drought"] = data[value_column] < data["_threshold"]
    out = data.groupby(unit_id_column, as_index=False)["_is_drought"].sum()
    return out.rename(columns={"_is_drought": output_column})


def extreme_month_count_indicator(
    monthly_table: pd.DataFrame,
    *,
    value_column: str,
    unit_id_column: str = "unit_id",
    threshold_quantile: float = 0.9,
    output_column: str = "h_extreme_precip_days",
) -> pd.DataFrame:
    """Count high-precipitation months per unit as a monthly-product proxy."""
    data = monthly_table[[unit_id_column, value_column]].copy()
    thresholds = data.groupby(unit_id_column)[value_column].quantile(threshold_quantile)
    data["_threshold"] = data[unit_id_column].map(thresholds)
    data["_is_extreme"] = data[value_column] > data["_threshold"]
    out = data.groupby(unit_id_column, as_index=False)["_is_extreme"].sum()
    return out.rename(columns={"_is_extreme": output_column})


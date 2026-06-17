"""Data adapters for HydroResKit."""

from hydroreskit.adapters.hydroatlas import derive_hydroatlas_indicators
from hydroreskit.adapters.hydrobasins import derive_hydrobasins_attribute_indicators
from hydroreskit.adapters.merge import merge_indicator_tables
from hydroreskit.adapters.source_resolution import build_resolved_indicator_table
from hydroreskit.adapters.tabular import read_indicator_table, validate_indicator_table
from hydroreskit.adapters.timeseries import aggregate_unit_timeseries, summarize_unit_timeseries

__all__ = [
    "aggregate_unit_timeseries",
    "derive_hydroatlas_indicators",
    "derive_hydrobasins_attribute_indicators",
    "build_resolved_indicator_table",
    "merge_indicator_tables",
    "read_indicator_table",
    "summarize_unit_timeseries",
    "validate_indicator_table",
]

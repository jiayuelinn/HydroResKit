"""HydroResKit: watershed climate-resilience assessment utilities."""

from hydroreskit.aggregation import aggregate_dimensions, compute_resilience_score
from hydroreskit.cache import file_metadata, file_sha256
from hydroreskit.diagnostics import missing_value_report, rank_table, unit_missing_report
from hydroreskit.schema import load_indicator_schema, validate_indicator_schema
from hydroreskit.weighting import equal_weights, entropy_weights, pca_weights, user_defined_weights

__all__ = [
    "aggregate_dimensions",
    "compute_resilience_score",
    "equal_weights",
    "entropy_weights",
    "file_metadata",
    "file_sha256",
    "load_indicator_schema",
    "missing_value_report",
    "pca_weights",
    "rank_table",
    "unit_missing_report",
    "user_defined_weights",
    "validate_indicator_schema",
]

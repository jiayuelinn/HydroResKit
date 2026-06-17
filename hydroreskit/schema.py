"""Indicator schema loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = {
    "indicator_id",
    "dimension",
    "variable_name",
    "source_dataset",
    "spatial_resolution",
    "temporal_resolution",
    "expected_direction",
    "aggregation_method",
    "missing_value_rule",
    "uncertainty_note",
    "citation",
}

VALID_DIMENSIONS = {
    "hazard",
    "exposure",
    "sensitivity",
    "adaptive_capacity",
    "recovery",
}

VALID_DIRECTIONS = {"positive", "negative"}


def load_indicator_schema(path: str | Path) -> list[dict[str, Any]]:
    """Load a HydroResKit indicator schema from YAML."""
    with Path(path).open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if isinstance(data, dict) and "indicators" in data:
        indicators = data["indicators"]
    else:
        indicators = data

    if not isinstance(indicators, list):
        raise ValueError("Indicator schema must be a list or contain an 'indicators' list.")
    return indicators


def validate_indicator_schema(indicators: list[dict[str, Any]]) -> None:
    """Validate required fields and basic vocabulary in an indicator schema."""
    seen_ids: set[str] = set()
    for idx, item in enumerate(indicators, start=1):
        missing = REQUIRED_FIELDS - set(item)
        if missing:
            raise ValueError(f"Indicator #{idx} is missing fields: {sorted(missing)}")

        indicator_id = str(item["indicator_id"])
        if indicator_id in seen_ids:
            raise ValueError(f"Duplicate indicator_id: {indicator_id}")
        seen_ids.add(indicator_id)

        dimension = item["dimension"]
        if dimension not in VALID_DIMENSIONS:
            raise ValueError(f"{indicator_id}: invalid dimension '{dimension}'")

        direction = item["expected_direction"]
        if direction not in VALID_DIRECTIONS:
            raise ValueError(f"{indicator_id}: expected_direction must be positive or negative")


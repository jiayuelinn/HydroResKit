"""HydroATLAS attribute adapters.

HydroATLAS provides rich static hydro-environmental attributes keyed by
HydroBASINS identifiers. This module maps a subset of those attributes to the
HydroResKit resilience schema. It accepts tabular exports from official
HydroATLAS files or services such as Google Earth Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HydroATLASIndicatorRule:
    indicator_id: str
    dimension: str
    source_columns: tuple[str, ...]
    formula: str
    expected_direction: str
    caveat: str
    derive: Callable[[pd.DataFrame], pd.Series]


MONTHLY_PRECIP_COLUMNS = tuple(f"pre_mm_s{month:02d}" for month in range(1, 13))


def hydroatlas_indicator_rules() -> list[HydroATLASIndicatorRule]:
    """Return the initial HydroATLAS-to-HydroResKit indicator mapping."""
    return [
        HydroATLASIndicatorRule(
            indicator_id="h_precip_variability",
            dimension="hazard",
            source_columns=MONTHLY_PRECIP_COLUMNS,
            formula="std(pre_mm_s01..pre_mm_s12) / mean(pre_mm_s01..pre_mm_s12)",
            expected_direction="negative",
            caveat="Static long-term monthly precipitation seasonality proxy, not an event-based hazard record.",
            derive=_precipitation_cv,
        ),
        HydroATLASIndicatorRule(
            indicator_id="h_drought_intensity",
            dimension="hazard",
            source_columns=("cmi_ix_syr",),
            formula="-cmi_ix_syr",
            expected_direction="negative",
            caveat="Climate moisture index proxy; lower moisture is converted to higher drought stress.",
            derive=lambda frame: -_numeric(frame["cmi_ix_syr"]),
        ),
        HydroATLASIndicatorRule(
            indicator_id="h_flood_prone_terrain",
            dimension="hazard",
            source_columns=("inu_pc_slt",),
            formula="inu_pc_slt",
            expected_direction="negative",
            caveat="Long-term inundation extent proxy, not a hydraulic flood model.",
            derive=lambda frame: _numeric(frame["inu_pc_slt"]),
        ),
        HydroATLASIndicatorRule(
            indicator_id="e_population_density",
            dimension="exposure",
            source_columns=("ppd_pk_sav",),
            formula="ppd_pk_sav",
            expected_direction="negative",
            caveat="Population density attribute from HydroATLAS; vintage follows source metadata.",
            derive=lambda frame: _numeric(frame["ppd_pk_sav"]),
        ),
        HydroATLASIndicatorRule(
            indicator_id="e_built_up_fraction",
            dimension="exposure",
            source_columns=("urb_pc_sse",),
            formula="urb_pc_sse",
            expected_direction="negative",
            caveat="Urban extent percentage proxy; class definitions follow HydroATLAS source processing.",
            derive=lambda frame: _numeric(frame["urb_pc_sse"]),
        ),
        HydroATLASIndicatorRule(
            indicator_id="e_cropland_fraction",
            dimension="exposure",
            source_columns=("crp_pc_sse",),
            formula="crp_pc_sse",
            expected_direction="negative",
            caveat="Cropland extent percentage proxy.",
            derive=lambda frame: _numeric(frame["crp_pc_sse"]),
        ),
        HydroATLASIndicatorRule(
            indicator_id="s_slope_mean",
            dimension="sensitivity",
            source_columns=("slp_dg_sav",),
            formula="slp_dg_sav",
            expected_direction="negative",
            caveat="Mean slope proxy; DEM source and aggregation affect values.",
            derive=lambda frame: _numeric(frame["slp_dg_sav"]),
        ),
        HydroATLASIndicatorRule(
            indicator_id="s_ecological_fragility",
            dimension="sensitivity",
            source_columns=("for_pc_sse",),
            formula="100 - for_pc_sse",
            expected_direction="negative",
            caveat="Low-forest-cover fragility proxy; should be complemented with vegetation dynamics.",
            derive=lambda frame: 100.0 - _numeric(frame["for_pc_sse"]),
        ),
        HydroATLASIndicatorRule(
            indicator_id="s_water_stress_proxy",
            dimension="sensitivity",
            source_columns=("pet_mm_syr", "aet_mm_syr"),
            formula="pet_mm_syr - aet_mm_syr",
            expected_direction="negative",
            caveat="Atmospheric water-demand gap proxy; not a calibrated withdrawal or allocation model.",
            derive=lambda frame: _numeric(frame["pet_mm_syr"]) - _numeric(frame["aet_mm_syr"]),
        ),
        HydroATLASIndicatorRule(
            indicator_id="a_surface_water_fraction",
            dimension="adaptive_capacity",
            source_columns=("lka_pc_sse",),
            formula="lka_pc_sse",
            expected_direction="positive",
            caveat="Lake/reservoir surface-water extent proxy, not storage capacity.",
            derive=lambda frame: _numeric(frame["lka_pc_sse"]),
        ),
        HydroATLASIndicatorRule(
            indicator_id="a_green_blue_space_fraction",
            dimension="adaptive_capacity",
            source_columns=("for_pc_sse", "lka_pc_sse", "wet_pc_sg1", "wet_pc_sg2"),
            formula="clip(for_pc_sse + lka_pc_sse + wet_pc_sg1 + wet_pc_sg2, 0, 100)",
            expected_direction="positive",
            caveat="Coarse green-blue proxy based on forest, lake, and wetland percentages.",
            derive=_green_blue_fraction,
        ),
        HydroATLASIndicatorRule(
            indicator_id="a_economic_proxy",
            dimension="adaptive_capacity",
            source_columns=("gdp_ud_sav",),
            formula="gdp_ud_sav",
            expected_direction="positive",
            caveat="GDP proxy for adaptive resources; socioeconomic interpretation requires care.",
            derive=lambda frame: _numeric(frame["gdp_ud_sav"]),
        ),
    ]


def hydroatlas_required_source_columns() -> list[str]:
    """Return source columns needed by the initial HydroATLAS mapping."""
    columns = []
    for rule in hydroatlas_indicator_rules():
        for column in rule.source_columns:
            if column not in columns:
                columns.append(column)
    return columns


def derive_hydroatlas_indicators(
    attributes: pd.DataFrame,
    *,
    id_column: str = "HYBAS_ID",
    rules: list[HydroATLASIndicatorRule] | None = None,
    strict: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Derive schema indicators from a HydroATLAS attribute table.

    Returns a pair ``(indicator_table, metadata_table)``. The indicator table
    contains the unit ID and all indicators whose required source columns are
    present. The metadata table records source columns, formulas, caveats, and
    whether each rule was derived or skipped.
    """
    if id_column not in attributes.columns:
        raise ValueError(f"Missing HydroATLAS ID column: {id_column}")
    if attributes[id_column].isna().any():
        raise ValueError(f"HydroATLAS ID column '{id_column}' contains missing values.")
    if attributes[id_column].duplicated().any():
        examples = attributes.loc[attributes[id_column].duplicated(), id_column].head(5).tolist()
        raise ValueError(f"HydroATLAS ID column '{id_column}' contains duplicates: {examples}")

    rules = rules or hydroatlas_indicator_rules()
    indicator_table = pd.DataFrame({id_column: attributes[id_column].to_numpy()})
    metadata_rows = []
    for rule in rules:
        missing_columns = [column for column in rule.source_columns if column not in attributes.columns]
        status = "derived"
        notes = ""
        if missing_columns:
            status = "skipped"
            notes = f"missing source columns: {', '.join(missing_columns)}"
            if strict:
                raise ValueError(f"Cannot derive {rule.indicator_id}; {notes}")
        else:
            indicator_table[rule.indicator_id] = rule.derive(attributes).to_numpy()

        metadata_rows.append(
            {
                "indicator_id": rule.indicator_id,
                "dimension": rule.dimension,
                "source_dataset": "HydroATLAS",
                "source_columns": ";".join(rule.source_columns),
                "formula": rule.formula,
                "expected_direction": rule.expected_direction,
                "status": status,
                "notes": notes,
                "caveat": rule.caveat,
            }
        )

    metadata = pd.DataFrame(metadata_rows)
    return indicator_table, metadata


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _precipitation_cv(frame: pd.DataFrame) -> pd.Series:
    monthly = frame.loc[:, MONTHLY_PRECIP_COLUMNS].apply(pd.to_numeric, errors="coerce")
    mean = monthly.mean(axis=1).replace(0, np.nan)
    return monthly.std(axis=1) / mean


def _green_blue_fraction(frame: pd.DataFrame) -> pd.Series:
    parts = frame.loc[:, ["for_pc_sse", "lka_pc_sse", "wet_pc_sg1", "wet_pc_sg2"]].apply(
        pd.to_numeric,
        errors="coerce",
    )
    return parts.sum(axis=1, min_count=1).clip(lower=0, upper=100)

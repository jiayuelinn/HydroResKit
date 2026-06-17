"""HydroBASINS attribute adapters.

The functions in this module derive lightweight, auditable basin-scale
indicators from attributes that are shipped with HydroBASINS boundaries. They
are meant as a first real-data smoke test before richer HydroATLAS, climate,
remote-sensing, and socioeconomic indicators are added.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


HYDROBASINS_ATTRIBUTE_INDICATOR_ID = "h_flood_prone_terrain"


def derive_hydrobasins_attribute_indicators(
    boundaries: pd.DataFrame,
    *,
    id_column: str = "HYBAS_ID",
) -> pd.DataFrame:
    """Derive a minimal indicator table from HydroBASINS attributes.

    The first schema-aligned indicator is ``h_flood_prone_terrain``. In this
    smoke-test implementation it is represented by ``log1p(UP_AREA)``: a
    drainage-network accumulation proxy where larger upstream contributing area
    indicates higher potential flood accumulation. It is not a hydraulic flood
    model and should be replaced or complemented by HydroATLAS/DEM floodplain
    indicators in the full demonstration.
    """
    _require_columns(boundaries, [id_column, "UP_AREA", "SUB_AREA"])

    frame = pd.DataFrame(
        {
            id_column: boundaries[id_column].to_numpy(),
            HYDROBASINS_ATTRIBUTE_INDICATOR_ID: np.log1p(
                pd.to_numeric(boundaries["UP_AREA"], errors="coerce").clip(lower=0)
            ),
            "hydrobasins_upstream_area_km2": pd.to_numeric(boundaries["UP_AREA"], errors="coerce"),
            "hydrobasins_local_area_km2": pd.to_numeric(boundaries["SUB_AREA"], errors="coerce"),
        }
    )

    local_area = frame["hydrobasins_local_area_km2"].replace(0, np.nan)
    frame["hydrobasins_upstream_to_local_area_ratio"] = (
        frame["hydrobasins_upstream_area_km2"] / local_area
    )

    for column in ["DIST_MAIN", "DIST_SINK", "ORDER", "PFAF_ID", "MAIN_BAS", "NEXT_DOWN"]:
        if column in boundaries.columns:
            frame[f"hydrobasins_{column.lower()}"] = pd.to_numeric(boundaries[column], errors="coerce")

    return frame


def hydrobasins_attribute_indicator_metadata() -> pd.DataFrame:
    """Return metadata for the HydroBASINS-derived schema indicator."""
    return pd.DataFrame(
        [
            {
                "indicator_id": HYDROBASINS_ATTRIBUTE_INDICATOR_ID,
                "dimension": "hazard",
                "source_dataset": "HydroBASINS",
                "source_columns": "UP_AREA",
                "formula": "log1p(UP_AREA)",
                "expected_direction": "negative",
                "interpretation": (
                    "Drainage-network accumulation proxy; larger upstream contributing "
                    "area is treated as higher potential flood accumulation."
                ),
                "caveat": (
                    "This is a first real-data smoke-test proxy, not a hydraulic flood "
                    "model or a substitute for HydroATLAS/DEM floodplain attributes."
                ),
            }
        ]
    )


def _require_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing HydroBASINS columns: {missing}")

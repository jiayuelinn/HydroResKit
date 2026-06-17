"""Boundary adapters for basin and sub-basin vector data."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from hydroreskit.provenance import FileAuditRecord, append_file_audit


def _require_geopandas():
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise ImportError(
            "Boundary adapters require geopandas. Install hydroreskit with the 'geo' extra."
        ) from exc
    return gpd


def read_boundaries(
    path: str | Path,
    *,
    id_column: str | None = None,
    target_crs: str | None = None,
    bbox: tuple[float, float, float, float] | None = None,
):
    """Read basin boundaries and optionally validate IDs, CRS, and bounding box."""
    gpd = _require_geopandas()
    kwargs = {"bbox": bbox} if bbox is not None else {}
    gdf = gpd.read_file(path, **kwargs)

    if id_column is not None:
        _validate_boundary_ids(gdf, id_column)

    if target_crs is not None:
        gdf = gdf.to_crs(target_crs)
    return gdf


def _validate_boundary_ids(gdf, id_column: str) -> None:
    if id_column not in gdf.columns:
        raise ValueError(f"Boundary ID column '{id_column}' not found.")
    if gdf[id_column].isna().any():
        raise ValueError(f"Boundary ID column '{id_column}' contains missing values.")
    duplicated = gdf[id_column].duplicated()
    if duplicated.any():
        examples = gdf.loc[duplicated, id_column].head(5).tolist()
        raise ValueError(f"Boundary ID column '{id_column}' contains duplicates: {examples}")


def select_boundaries(gdf, column: str, values: Iterable) -> object:
    """Filter boundaries by attribute values."""
    if column not in gdf.columns:
        raise ValueError(f"Column '{column}' not found in boundary table.")
    selected = gdf[gdf[column].isin(list(values))].copy()
    if selected.empty:
        raise ValueError(f"No boundaries matched {column} in {list(values)}")
    return selected


def find_containing_boundary(gdf, lon: float, lat: float):
    """Find boundaries that contain a WGS84 point."""
    _require_point_dependencies(gdf)
    from shapely.geometry import Point

    point_gdf = gdf
    if point_gdf.crs is not None and str(point_gdf.crs).upper() not in {"EPSG:4326", "WGS84"}:
        point_gdf = point_gdf.to_crs("EPSG:4326")
    point = Point(lon, lat)
    selected = point_gdf[point_gdf.geometry.contains(point)].copy()
    if selected.empty:
        raise ValueError(f"No boundary contains point lon={lon}, lat={lat}.")
    return selected


def select_main_basin_by_point(
    gdf,
    *,
    lon: float,
    lat: float,
    main_basin_column: str = "MAIN_BAS",
):
    """Select all rows sharing the main-basin ID of the polygon containing a point."""
    if main_basin_column not in gdf.columns:
        raise ValueError(f"Main basin column '{main_basin_column}' not found.")
    containing = find_containing_boundary(gdf, lon, lat)
    main_ids = containing[main_basin_column].dropna().unique().tolist()
    if len(main_ids) != 1:
        raise ValueError(
            f"Point matched {len(main_ids)} main-basin IDs in '{main_basin_column}': {main_ids}"
        )
    selected = gdf[gdf[main_basin_column] == main_ids[0]].copy()
    if selected.empty:
        raise ValueError(f"No boundaries matched {main_basin_column}={main_ids[0]}")
    return selected


def _require_point_dependencies(gdf) -> None:
    if not hasattr(gdf, "geometry"):
        raise TypeError("Expected a GeoDataFrame with a geometry column.")


def boundary_summary(gdf, id_column: str) -> pd.DataFrame:
    """Return a compact boundary summary table."""
    _validate_boundary_ids(gdf, id_column)
    area = None
    if getattr(gdf, "crs", None) is not None and getattr(gdf.crs, "is_projected", False):
        area = gdf.geometry.area
    summary = pd.DataFrame(
        {
            id_column: gdf[id_column].to_numpy(),
            "geometry_type": gdf.geometry.geom_type.to_numpy(),
            "area": area.to_numpy() if area is not None else pd.NA,
        }
    )
    for column in ["MAIN_BAS", "PFAF_ID", "SUB_AREA", "UP_AREA", "NEXT_DOWN", "ORDER", "SORT"]:
        if column in gdf.columns:
            summary[column] = gdf[column].to_numpy()
    return summary


def write_boundaries(
    gdf,
    path: str | Path,
    *,
    audit_path: str | Path | None = None,
    source_dataset: str = "unknown",
    processing_step: str = "write_boundaries",
    notes: str = "",
) -> None:
    """Write boundaries to a vector file supported by GeoPandas."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output)
    if audit_path is not None:
        append_file_audit(
            FileAuditRecord.create(
                output,
                role="boundary",
                source_dataset=source_dataset,
                processing_step=processing_step,
                notes=notes,
            ),
            audit_path,
        )

"""Raster-to-basin aggregation adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


def _require_rasterio():
    try:
        import rasterio
        from rasterio.mask import mask
    except ImportError as exc:
        raise ImportError(
            "Raster adapters require rasterio. Install hydroreskit with the 'geo' extra."
        ) from exc
    return rasterio, mask


def _require_geopandas():
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise ImportError(
            "Raster vector aggregation requires geopandas. Install hydroreskit with the 'geo' extra."
        ) from exc
    return gpd


def aggregate_raster_to_vector(
    raster_path: str | Path,
    vector_path: str | Path,
    *,
    id_column: str,
    stats: Iterable[str] = ("mean",),
    band: int = 1,
    all_touched: bool = False,
    nodata: float | int | None = None,
) -> pd.DataFrame:
    """Aggregate raster values over polygons from a vector file."""
    gpd = _require_geopandas()
    boundaries = gpd.read_file(vector_path)
    return aggregate_raster_to_boundaries(
        raster_path,
        boundaries,
        id_column=id_column,
        stats=stats,
        band=band,
        all_touched=all_touched,
        nodata=nodata,
    )


def aggregate_raster_to_boundaries(
    raster_path: str | Path,
    boundaries,
    *,
    id_column: str,
    stats: Iterable[str] = ("mean",),
    band: int = 1,
    all_touched: bool = False,
    nodata: float | int | None = None,
) -> pd.DataFrame:
    """Aggregate raster values over an in-memory GeoDataFrame."""
    rasterio, mask = _require_rasterio()
    if id_column not in boundaries.columns:
        raise ValueError(f"Boundary ID column '{id_column}' not found.")

    requested_stats = tuple(stats)
    rows = []
    with rasterio.open(raster_path) as src:
        gdf = boundaries
        if gdf.crs is not None and src.crs is not None and gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)
        raster_nodata = src.nodata if nodata is None else nodata

        for _, feature in gdf.iterrows():
            values = _masked_values(
                src,
                feature.geometry,
                mask_func=mask,
                band=band,
                all_touched=all_touched,
                nodata=raster_nodata,
            )
            row = {id_column: feature[id_column]}
            row.update(_compute_stats(values, requested_stats))
            rows.append(row)

    return pd.DataFrame(rows)


def _masked_values(src, geometry, *, mask_func, band: int, all_touched: bool, nodata):
    try:
        out, _ = mask_func(src, [geometry], crop=True, indexes=band, all_touched=all_touched)
    except ValueError:
        return np.array([], dtype=float)

    data = np.asarray(out, dtype=float).ravel()
    if nodata is not None:
        data = data[data != nodata]
    data = data[np.isfinite(data)]
    return data


def _compute_stats(values: np.ndarray, stats: tuple[str, ...]) -> dict[str, float | int]:
    result: dict[str, float | int] = {}
    if values.size == 0:
        for stat in stats:
            result[stat] = np.nan
        if "count" not in result:
            result["count"] = 0
        return result

    for stat in stats:
        if stat == "mean":
            result[stat] = float(np.mean(values))
        elif stat == "median":
            result[stat] = float(np.median(values))
        elif stat == "min":
            result[stat] = float(np.min(values))
        elif stat == "max":
            result[stat] = float(np.max(values))
        elif stat == "sum":
            result[stat] = float(np.sum(values))
        elif stat == "std":
            result[stat] = float(np.std(values))
        elif stat == "q05":
            result[stat] = float(np.quantile(values, 0.05))
        elif stat == "q95":
            result[stat] = float(np.quantile(values, 0.95))
        elif stat == "count":
            result[stat] = int(values.size)
        else:
            raise ValueError(f"Unsupported raster statistic: {stat}")

    if "count" not in result:
        result["count"] = int(values.size)
    return result


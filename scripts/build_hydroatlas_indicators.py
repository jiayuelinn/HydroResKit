"""Build HydroResKit indicators from a HydroATLAS attribute table."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hydroreskit.adapters.boundary import read_boundaries
from hydroreskit.adapters.hydroatlas import derive_hydroatlas_indicators, hydroatlas_required_source_columns
from hydroreskit.adapters.tabular import write_indicator_table
from hydroreskit.provenance import FileAuditRecord, append_file_audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Derive HydroResKit schema indicators from a HydroATLAS CSV/vector "
            "attribute table exported from official HydroATLAS data."
        )
    )
    parser.add_argument("--input", required=True, help="HydroATLAS CSV, GeoJSON, GPKG, or Shapefile path.")
    parser.add_argument("--output", required=True, help="Output indicator CSV or Parquet path.")
    parser.add_argument("--id-column", default="HYBAS_ID", help="HydroATLAS/HydroBASINS ID column.")
    parser.add_argument("--layer", help="Optional vector layer name for GDB/GPKG/ZIP inputs.")
    parser.add_argument("--main-basin-column", default="MAIN_BAS", help="Main basin ID column for source filtering.")
    parser.add_argument("--main-basin-id", help="Optional main basin ID used to filter full HydroATLAS sources.")
    parser.add_argument(
        "--boundaries",
        help="Optional prepared boundary file; if provided, output is filtered/reordered to these IDs.",
    )
    parser.add_argument(
        "--metadata-output",
        default="outputs/hydroatlas_indicator_metadata.csv",
        help="Output CSV describing derived and skipped indicator formulas.",
    )
    parser.add_argument("--strict", action="store_true", help="Fail if any mapped source column is absent.")
    parser.add_argument("--audit", default="outputs/file_audit.csv", help="Audit CSV output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    columns = _requested_columns(args.id_column, args.main_basin_column)
    where = None
    if args.main_basin_id is not None:
        where = f"{args.main_basin_column} = {args.main_basin_id}"
    attributes = _read_attribute_table(args.input, layer=args.layer, where=where, columns=columns)
    if args.main_basin_id is not None and args.main_basin_column in attributes.columns:
        attributes = attributes[
            attributes[args.main_basin_column].astype(str) == str(args.main_basin_id)
        ].copy()
    if args.boundaries:
        attributes = _filter_to_boundaries(attributes, args.boundaries, id_column=args.id_column)

    indicators, metadata = derive_hydroatlas_indicators(
        attributes,
        id_column=args.id_column,
        strict=args.strict,
    )
    write_indicator_table(
        indicators,
        args.output,
        unit_id_column=args.id_column,
        audit_path=args.audit,
        source_dataset="HydroATLAS",
        processing_step="build_hydroatlas_indicators",
        notes=(
            "Derived schema indicators from HydroATLAS attributes; "
            f"derived={int((metadata['status'] == 'derived').sum())}; "
            f"skipped={int((metadata['status'] == 'skipped').sum())}"
        ),
    )

    metadata_path = Path(args.metadata_output)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata.to_csv(metadata_path, index=False)
    append_file_audit(
        FileAuditRecord.create(
            metadata_path,
            role="indicator_metadata",
            source_dataset="HydroATLAS",
            processing_step="build_hydroatlas_indicators_metadata",
            notes="Formula, source-column, and caveat metadata for HydroATLAS-derived indicators.",
        ),
        args.audit,
    )

    derived = metadata.loc[metadata["status"] == "derived", "indicator_id"].tolist()
    print(f"Wrote {len(indicators)} HydroATLAS-derived indicator rows -> {args.output}")
    print(f"Derived {len(derived)} indicators: {', '.join(derived)}")
    print(f"Wrote indicator metadata -> {metadata_path}")


def _read_attribute_table(
    path: str | Path,
    *,
    layer: str | None = None,
    where: str | None = None,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    input_path = Path(path)
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(input_path)
        if columns is not None:
            keep = [column for column in columns if column in frame.columns]
            frame = frame[keep]
        return frame
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(input_path, columns=columns)
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise ImportError(
            "Reading HydroATLAS vector files requires geopandas. Use CSV export or install the geo extra."
        ) from exc
    kwargs = {}
    if layer is not None:
        kwargs["layer"] = layer
    if where is not None:
        kwargs["where"] = where
    if columns is not None:
        kwargs["columns"] = columns
    return pd.DataFrame(gpd.read_file(input_path, **kwargs).drop(columns="geometry", errors="ignore"))


def _filter_to_boundaries(attributes: pd.DataFrame, boundaries_path: str | Path, *, id_column: str) -> pd.DataFrame:
    boundaries = read_boundaries(boundaries_path, id_column=id_column)
    ids = pd.DataFrame({id_column: boundaries[id_column].to_numpy()})
    filtered = ids.merge(attributes, on=id_column, how="left")
    missing = filtered.drop(columns=[id_column]).isna().all(axis=1)
    if missing.any():
        examples = filtered.loc[missing, id_column].head(5).tolist()
        raise ValueError(f"HydroATLAS table lacks attributes for boundary IDs: {examples}")
    return filtered


def _requested_columns(id_column: str, main_basin_column: str) -> list[str]:
    columns = [id_column, main_basin_column]
    for column in hydroatlas_required_source_columns():
        if column not in columns:
            columns.append(column)
    return columns


if __name__ == "__main__":
    main()

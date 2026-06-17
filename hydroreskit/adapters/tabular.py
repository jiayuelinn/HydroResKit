"""Tabular indicator adapters."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from hydroreskit.provenance import FileAuditRecord, append_file_audit


def read_indicator_table(
    path: str | Path,
    *,
    unit_id_column: str = "unit_id",
    schema: list[dict] | None = None,
    strict: bool = False,
) -> pd.DataFrame:
    """Read a basin-scale indicator table from CSV or Parquet."""
    input_path = Path(path)
    if input_path.suffix.lower() == ".csv":
        frame = pd.read_csv(input_path)
    elif input_path.suffix.lower() in {".parquet", ".pq"}:
        frame = pd.read_parquet(input_path)
    else:
        raise ValueError(f"Unsupported indicator table format: {input_path.suffix}")

    validate_indicator_table(frame, unit_id_column=unit_id_column, schema=schema, strict=strict)
    return frame.set_index(unit_id_column)


def validate_indicator_table(
    frame: pd.DataFrame,
    *,
    unit_id_column: str = "unit_id",
    schema: list[dict] | None = None,
    strict: bool = False,
) -> None:
    """Validate unit IDs and schema coverage in a tabular indicator table."""
    if unit_id_column not in frame.columns:
        raise ValueError(f"Missing unit ID column: {unit_id_column}")
    if frame[unit_id_column].isna().any():
        raise ValueError(f"Unit ID column '{unit_id_column}' contains missing values.")
    duplicated = frame[unit_id_column].duplicated()
    if duplicated.any():
        examples = frame.loc[duplicated, unit_id_column].head(5).tolist()
        raise ValueError(f"Unit ID column '{unit_id_column}' contains duplicates: {examples}")

    if schema is None:
        return

    expected = [item["indicator_id"] for item in schema]
    missing = [col for col in expected if col not in frame.columns]
    if strict and missing:
        raise ValueError(f"Indicator table is missing schema indicators: {missing}")

    non_numeric = [
        col for col in expected if col in frame.columns and not pd.api.types.is_numeric_dtype(frame[col])
    ]
    if non_numeric:
        raise ValueError(f"Indicator columns must be numeric: {non_numeric}")


def write_indicator_table(
    frame: pd.DataFrame,
    path: str | Path,
    *,
    unit_id_column: str = "unit_id",
    audit_path: str | Path | None = None,
    source_dataset: str = "derived",
    processing_step: str = "write_indicator_table",
    notes: str = "",
) -> None:
    """Write an indicator table to CSV or Parquet."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = frame.reset_index() if frame.index.name == unit_id_column else frame

    if output_path.suffix.lower() == ".csv":
        data.to_csv(output_path, index=False)
    elif output_path.suffix.lower() in {".parquet", ".pq"}:
        data.to_parquet(output_path, index=False)
    else:
        raise ValueError(f"Unsupported indicator table format: {output_path.suffix}")

    if audit_path is not None:
        append_file_audit(
            FileAuditRecord.create(
                output_path,
                role="indicator_table",
                source_dataset=source_dataset,
                processing_step=processing_step,
                notes=notes,
            ),
            audit_path,
        )

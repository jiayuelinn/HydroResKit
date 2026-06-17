"""Utilities for merging basin-scale indicator tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from hydroreskit.adapters.tabular import read_indicator_table, write_indicator_table


def merge_indicator_tables(
    tables: list[pd.DataFrame],
    *,
    unit_id_column: str = "HYBAS_ID",
    duplicate_policy: str = "error",
) -> pd.DataFrame:
    """Merge multiple indicator tables on a basin/unit ID column.

    Parameters
    ----------
    tables:
        DataFrames containing a unit ID column and one or more indicator columns.
    duplicate_policy:
        How to handle duplicate non-ID columns across tables:
        ``error`` raises; ``first`` keeps the first table's value; ``last`` keeps
        the later table's value; ``coalesce`` fills missing values in the first
        table from later tables.
    """
    if duplicate_policy not in {"error", "first", "last", "coalesce"}:
        raise ValueError("duplicate_policy must be one of: error, first, last, coalesce")
    if not tables:
        raise ValueError("At least one indicator table is required.")

    merged = _prepare_table(tables[0], unit_id_column)
    for table in tables[1:]:
        prepared = _prepare_table(table, unit_id_column)
        duplicates = [
            column
            for column in prepared.columns
            if column != unit_id_column and column in merged.columns
        ]
        if duplicates and duplicate_policy == "error":
            raise ValueError(f"Duplicate indicator columns across tables: {duplicates}")

        if not duplicates:
            merged = merged.merge(prepared, on=unit_id_column, how="outer", validate="one_to_one")
            continue

        suffix = "__incoming"
        merged = merged.merge(
            prepared,
            on=unit_id_column,
            how="outer",
            validate="one_to_one",
            suffixes=("", suffix),
        )
        for column in duplicates:
            incoming = f"{column}{suffix}"
            if duplicate_policy == "last":
                merged[column] = merged[incoming].combine_first(merged[column])
            elif duplicate_policy == "coalesce":
                merged[column] = merged[column].combine_first(merged[incoming])
            merged = merged.drop(columns=incoming)

    return merged.sort_values(unit_id_column).reset_index(drop=True)


def merge_indicator_table_files(
    input_paths: list[str | Path],
    output_path: str | Path,
    *,
    unit_id_column: str = "HYBAS_ID",
    duplicate_policy: str = "error",
    audit_path: str | Path | None = None,
    source_dataset: str = "multi_source",
    notes: str = "",
) -> pd.DataFrame:
    """Read, merge, and write indicator tables."""
    tables = [
        read_indicator_table(path, unit_id_column=unit_id_column).reset_index()
        for path in input_paths
    ]
    merged = merge_indicator_tables(
        tables,
        unit_id_column=unit_id_column,
        duplicate_policy=duplicate_policy,
    )
    write_indicator_table(
        merged,
        output_path,
        unit_id_column=unit_id_column,
        audit_path=audit_path,
        source_dataset=source_dataset,
        processing_step="merge_indicator_tables",
        notes=notes or f"inputs={';'.join(str(path) for path in input_paths)}; duplicate_policy={duplicate_policy}",
    )
    return merged


def _prepare_table(table: pd.DataFrame, unit_id_column: str) -> pd.DataFrame:
    if unit_id_column not in table.columns:
        raise ValueError(f"Missing unit ID column: {unit_id_column}")
    if table[unit_id_column].isna().any():
        raise ValueError(f"Unit ID column '{unit_id_column}' contains missing values.")
    if table[unit_id_column].duplicated().any():
        examples = table.loc[table[unit_id_column].duplicated(), unit_id_column].head(5).tolist()
        raise ValueError(f"Unit ID column '{unit_id_column}' contains duplicates: {examples}")
    return table.copy()

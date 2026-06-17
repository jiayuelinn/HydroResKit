"""Command-line interface for HydroResKit."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from hydroreskit.adapters.tabular import read_indicator_table
from hydroreskit.aggregation import aggregate_dimensions, compute_resilience_score
from hydroreskit.diagnostics import (
    contribution_summary,
    indicator_contribution_table,
    missing_value_report,
    rank_table,
    unit_missing_report,
    weighting_method_comparison,
)
from hydroreskit.preprocessing import align_direction, normalize
from hydroreskit.schema import load_indicator_schema, validate_indicator_schema
from hydroreskit.uncertainty import missing_indicator_sensitivity
from hydroreskit.weighting import entropy_weights, equal_weights, pca_weights, user_defined_weights


def _validate_schema(args: argparse.Namespace) -> None:
    indicators = load_indicator_schema(args.schema)
    validate_indicator_schema(indicators)
    print(f"Validated {len(indicators)} indicators from {args.schema}")


def _demo(args: argparse.Namespace) -> None:
    with Path(args.config).open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    indicators = load_indicator_schema(config["indicator_schema"])
    validate_indicator_schema(indicators)

    unit_col = config.get("unit_id_column", "unit_id")
    frame = read_indicator_table(
        config["demo_indicator_table"],
        unit_id_column=unit_col,
        schema=indicators,
        strict=False,
    )

    normalized = pd.DataFrame(index=frame.index)
    for item in indicators:
        indicator_id = item["indicator_id"]
        if indicator_id not in frame:
            continue
        values = normalize(frame[indicator_id], method=config.get("normalization", "minmax"))
        normalized[indicator_id] = align_direction(values, item["expected_direction"])

    weights = _compute_weights(normalized, config)

    dimension_scores = aggregate_dimensions(normalized, indicators, weights)
    final_score = compute_resilience_score(dimension_scores)
    output = dimension_scores.copy()
    output["resilience_score"] = final_score
    output_path = Path(config.get("output", "outputs/demo_scores.csv"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path)
    _write_diagnostics(config, frame, normalized, indicators, weights, output)
    print(f"Wrote demo scores to {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hydroreskit")
    subparsers = parser.add_subparsers(required=True)

    validate_parser = subparsers.add_parser("validate-schema")
    validate_parser.add_argument("schema")
    validate_parser.set_defaults(func=_validate_schema)

    table_parser = subparsers.add_parser("validate-table")
    table_parser.add_argument("table")
    table_parser.add_argument("schema")
    table_parser.add_argument("--unit-id-column", default="unit_id")
    table_parser.add_argument("--strict", action="store_true")
    table_parser.set_defaults(func=_validate_table)

    demo_parser = subparsers.add_parser("demo")
    demo_parser.add_argument("config")
    demo_parser.set_defaults(func=_demo)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


def _compute_weights(normalized: pd.DataFrame, config: dict) -> pd.Series:
    method = config.get("weighting", "equal")
    columns = list(normalized.columns)
    if method == "equal":
        return equal_weights(columns)
    if method == "entropy":
        return entropy_weights(normalized)
    if method == "pca":
        return pca_weights(normalized)
    if method == "user_defined":
        raw_weights = config.get("user_weights")
        if raw_weights is None:
            raise ValueError("weighting='user_defined' requires a user_weights mapping or YAML path.")
        if isinstance(raw_weights, str):
            with Path(raw_weights).open("r", encoding="utf-8") as file:
                loaded = yaml.safe_load(file)
            raw_weights = loaded.get("weights", loaded)
        return user_defined_weights(raw_weights, columns)
    raise ValueError(f"Unsupported weighting method: {method}")


def _write_diagnostics(
    config: dict,
    frame: pd.DataFrame,
    normalized: pd.DataFrame,
    indicators: list[dict],
    weights: pd.Series,
    output: pd.DataFrame,
) -> None:
    diagnostics = config.get("diagnostics", {})
    if not diagnostics:
        return

    unit_id_name = config.get("unit_id_column", "unit_id")
    writers = {
        "missing_report": missing_value_report(frame, indicators),
        "unit_missing_report": unit_missing_report(frame, indicators, unit_id_name=unit_id_name),
        "weights": weights.rename("weight").reset_index().rename(columns={"index": "indicator_id"}),
        "rank_table": rank_table(output, unit_id_name=unit_id_name),
        "missing_indicator_sensitivity": missing_indicator_sensitivity(normalized, weights),
        "weighting_method_comparison": weighting_method_comparison(
            normalized,
            indicators,
            unit_id_name=unit_id_name,
        ),
    }

    contributions = None
    if "contribution_table" in diagnostics or "contribution_summary" in diagnostics:
        contributions = indicator_contribution_table(normalized, weights, indicators, unit_id_name=unit_id_name)
        writers["contribution_table"] = contributions
        writers["contribution_summary"] = contribution_summary(contributions)

    for key, table in writers.items():
        path = diagnostics.get(key)
        if not path:
            continue
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(output_path, index=False)


def _validate_table(args: argparse.Namespace) -> None:
    indicators = load_indicator_schema(args.schema)
    validate_indicator_schema(indicators)
    frame = read_indicator_table(
        args.table,
        unit_id_column=args.unit_id_column,
        schema=indicators,
        strict=args.strict,
    )
    print(f"Validated {len(frame)} units from {args.table}")


if __name__ == "__main__":
    main()

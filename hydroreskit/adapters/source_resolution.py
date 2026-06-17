"""Resolve source-specific indicator conflicts before table merging."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from hydroreskit.adapters.merge import merge_indicator_tables
from hydroreskit.adapters.tabular import read_indicator_table, write_indicator_table
from hydroreskit.schema import load_indicator_schema


@dataclass(frozen=True)
class SourceTable:
    source_id: str
    path: str
    frame: pd.DataFrame


def build_resolved_indicator_table(config_path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build a merged indicator table from a source-resolution YAML config."""
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    unit_id_column = config.get("unit_id_column", "HYBAS_ID")
    schema_path = config.get("indicator_schema", "configs/indicator_schema.yml")
    schema_ids = {item["indicator_id"] for item in load_indicator_schema(schema_path)}
    sources = _load_sources(config, unit_id_column=unit_id_column)
    priority = config.get("priority", {})
    lower_priority_action = config.get("lower_priority_duplicate_action", "rename")
    rename_pattern = config.get("renamed_column_pattern", "{source_id}__{indicator_id}")

    resolved_sources, resolution = resolve_source_conflicts(
        sources,
        schema_ids=schema_ids,
        unit_id_column=unit_id_column,
        priority=priority,
        lower_priority_action=lower_priority_action,
        rename_pattern=rename_pattern,
    )
    merged = merge_indicator_tables(
        [source.frame for source in resolved_sources],
        unit_id_column=unit_id_column,
        duplicate_policy=config.get("duplicate_policy", "error"),
    )

    output_path = config.get("output")
    if output_path:
        write_indicator_table(
            merged,
            output_path,
            unit_id_column=unit_id_column,
            audit_path=config.get("audit"),
            source_dataset="resolved_multi_source",
            processing_step="build_resolved_indicator_table",
            notes=f"config={config_path}",
        )

    report_path = config.get("resolution_report")
    if report_path:
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        resolution.to_csv(path, index=False)

    return merged, resolution


def resolve_source_conflicts(
    sources: list[SourceTable],
    *,
    schema_ids: set[str],
    unit_id_column: str = "HYBAS_ID",
    priority: dict[str, list[str]] | None = None,
    lower_priority_action: str = "rename",
    rename_pattern: str = "{source_id}__{indicator_id}",
) -> tuple[list[SourceTable], pd.DataFrame]:
    """Resolve duplicated schema indicators across source tables."""
    if lower_priority_action not in {"rename", "drop", "error"}:
        raise ValueError("lower_priority_action must be one of: rename, drop, error")
    priority = priority or {}
    source_by_id = {source.source_id: source for source in sources}

    locations: dict[str, list[str]] = {}
    for source in sources:
        for column in source.frame.columns:
            if column != unit_id_column and column in schema_ids:
                locations.setdefault(column, []).append(source.source_id)

    frames = {source.source_id: source.frame.copy() for source in sources}
    rows = []
    for indicator_id, source_ids in sorted(locations.items()):
        if len(source_ids) == 1:
            rows.append(
                {
                    "indicator_id": indicator_id,
                    "selected_source": source_ids[0],
                    "available_sources": ";".join(source_ids),
                    "action": "single_source",
                    "renamed_sources": "",
                    "dropped_sources": "",
                    "notes": "",
                }
            )
            continue

        preferred_order = priority.get(indicator_id)
        if not preferred_order:
            raise ValueError(
                f"Indicator '{indicator_id}' appears in multiple sources {source_ids} "
                "but no priority rule was provided."
            )
        selected = next((source_id for source_id in preferred_order if source_id in source_ids), None)
        if selected is None:
            raise ValueError(
                f"Priority rule for '{indicator_id}' does not match available sources: {source_ids}"
            )

        renamed_sources = []
        dropped_sources = []
        for source_id in source_ids:
            if source_id == selected:
                continue
            if lower_priority_action == "error":
                raise ValueError(
                    f"Indicator '{indicator_id}' duplicated in lower-priority source '{source_id}'."
                )
            if lower_priority_action == "drop":
                frames[source_id] = frames[source_id].drop(columns=indicator_id)
                dropped_sources.append(source_id)
            else:
                new_name = rename_pattern.format(source_id=source_id, indicator_id=indicator_id)
                if new_name in frames[source_id].columns:
                    raise ValueError(f"Renamed duplicate column already exists: {new_name}")
                frames[source_id] = frames[source_id].rename(columns={indicator_id: new_name})
                renamed_sources.append(f"{source_id}->{new_name}")

        rows.append(
            {
                "indicator_id": indicator_id,
                "selected_source": selected,
                "available_sources": ";".join(source_ids),
                "action": lower_priority_action,
                "renamed_sources": ";".join(renamed_sources),
                "dropped_sources": ";".join(dropped_sources),
                "notes": "resolved duplicate schema indicator",
            }
        )

    resolved_sources = [
        SourceTable(source_id=source_id, path=source_by_id[source_id].path, frame=frame)
        for source_id, frame in frames.items()
    ]
    return resolved_sources, pd.DataFrame(rows)


def _load_sources(config: dict, *, unit_id_column: str) -> list[SourceTable]:
    sources = []
    for item in config.get("sources", []):
        source_id = item["source_id"]
        path = Path(item["path"])
        required = bool(item.get("required", False))
        if not path.exists():
            if required:
                raise FileNotFoundError(f"Required source table not found: {path}")
            continue
        frame = read_indicator_table(path, unit_id_column=unit_id_column).reset_index()
        sources.append(SourceTable(source_id=source_id, path=str(path), frame=frame))
    if not sources:
        raise ValueError("No source tables were loaded.")
    return sources

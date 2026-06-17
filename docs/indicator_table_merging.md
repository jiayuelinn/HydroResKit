# Indicator Table Merging

HydroResKit derives indicators source by source. Each adapter writes a basin-scale table keyed by a shared unit ID such as `HYBAS_ID`. The merge step combines these adapter outputs into the final input table for scoring, diagnostics, and maps.

## Command

```bash
python scripts/merge_indicator_tables.py ^
  --inputs data_work\yangtze_hydrobasins_attribute_indicators.csv data_work\yangtze_hydroatlas_indicators.csv ^
  --output data_work\yangtze_static_indicators.csv ^
  --unit-id-column HYBAS_ID ^
  --duplicate-policy error ^
  --audit outputs\file_audit.csv
```

## Duplicate Policy

| Policy | Behavior | Suggested use |
|---|---|---|
| `error` | stop if two inputs contain the same indicator column | default for manuscript-grade runs |
| `first` | keep the first table's value | controlled fallback when a preferred source is listed first |
| `last` | replace earlier values with later values | controlled override |
| `coalesce` | fill missing earlier values from later tables | gap-filling with explicit provenance |

For the FCS letter benchmark, `error` should remain the default. If an indicator is intentionally replaced or coalesced, the reason should be documented in the provenance table.

## Current Static Demo

The current merged static table is:

```text
data_work/yangtze_static_indicators.csv
```

At this stage it contains the real HydroBASINS smoke-test indicator and auxiliary HydroBASINS audit attributes. After the real HydroATLAS export is available, rerun the merge command with both HydroBASINS and HydroATLAS-derived tables, then rerun:

```bash
python -m hydroreskit.cli demo configs/yangtze_static_demo.yml
python scripts/make_demo_figures.py
```

The static demo intentionally remains separate from the synthetic full-schema demo. The synthetic demo tests software mechanics; the static demo is the entry point for real source-derived indicators.

## Source-Resolution Config

For manuscript-grade runs, use the resolved build config:

```bash
python scripts/build_static_indicator_table.py configs/yangtze_static_sources.yml
```

This config reads available source-specific tables, applies indicator-level source priority, writes `data_work/yangtze_static_indicators.csv`, and records the resolution decision in:

```text
outputs/yangtze_static_source_resolution.csv
```

The current priority rule is:

| Indicator | Preferred source | Fallback source | Reason |
|---|---|---|---|
| `h_flood_prone_terrain` | HydroATLAS | HydroBASINS attribute smoke test | HydroATLAS inundation percentage is closer to flood-prone terrain; HydroBASINS `UP_AREA` is retained only as an upstream-area proxy. |

When both sources are present, the lower-priority duplicate is renamed using the pattern `{source_id}__{indicator_id}` and retained as an auxiliary audit column. This keeps the scoring schema unambiguous while preserving the lower-priority proxy for comparison.

# HydroBASINS Attribute Indicator Smoke Test

This note documents the first real-data indicator table produced by HydroResKit for the Yangtze River Basin demonstration.

## Input

- Prepared boundary layer: `data_work/yangtze_hydrobasins_l6.geojson`
- Source dataset: HydroBASINS Asia standard package, level 6
- Spatial unit ID: `HYBAS_ID`
- Selected units: 186
- Selected `MAIN_BAS`: `4060009880`

## Command

```bash
python scripts/build_hydrobasins_attribute_indicators.py \
  --boundaries data_work/yangtze_hydrobasins_l6.geojson \
  --output data_work/yangtze_hydrobasins_attribute_indicators.csv \
  --id-column HYBAS_ID \
  --metadata-output outputs/hydrobasins_attribute_indicator_metadata.csv \
  --audit outputs/file_audit.csv
```

Then run:

```bash
python -m hydroreskit.cli demo configs/yangtze_hydrobasins_attribute_demo.yml
python scripts/make_demo_figures.py
```

## Derived Indicator

| Indicator | Dimension | Source column | Formula | Direction | Caveat |
|---|---|---|---|---|---|
| `h_flood_prone_terrain` | hazard | `UP_AREA` | `log1p(UP_AREA)` | negative | Drainage-network accumulation proxy only; not a hydraulic flood model or a substitute for HydroATLAS/DEM floodplain attributes. |

Auxiliary HydroBASINS attributes are retained in the table for audit, including local area, upstream area, upstream-to-local area ratio, distance fields, order, Pfafstetter ID, main basin ID, and downstream ID when available.

## Outputs

| File | Purpose |
|---|---|
| `data_work/yangtze_hydrobasins_attribute_indicators.csv` | First real indicator table keyed by `HYBAS_ID` |
| `outputs/hydrobasins_attribute_indicator_metadata.csv` | Formula and caveat metadata |
| `outputs/yangtze_hydrobasins_attribute_scores.csv` | Single-indicator smoke-test scores |
| `outputs/yangtze_hydrobasins_attribute_missing_report.csv` | Schema coverage report showing one present indicator and nineteen missing indicators |
| `outputs/figures/fig7_hydrobasins_attribute_score_map.png` | First real boundary-to-indicator-to-score map |

## Interpretation Boundary

This run is a pipeline verification step. It proves that HydroResKit can move from official HydroBASINS geometry to an auditable indicator table, scoring outputs, diagnostics, and a map joined by `HYBAS_ID`. It should not be described as the final Yangtze resilience result. The full demonstration still needs HydroATLAS static attributes and external climate, vegetation, surface-water, population, urbanization, and night-light indicators.

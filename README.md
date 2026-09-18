# HydroResKit

HydroResKit is an open-source toolkit and resilience-ready data workflow for watershed climate-adaptation assessment.

The project is designed for a Frontiers of Computer Science Code & Data letter. It aims to provide a task-specific layer that maps open Earth-science and socio-environmental data into a reproducible watershed resilience schema.

## Associated publication

Paper describing this work has been received in *Frontiers of Computer Science* (FCS) special column “Code & Data in Earth Science”.

**Cited as:** Jiayue LIN, Ling XU, Yi’an HUANG, Bin QIU, Xiangfeng HUANG, Shijun CHEN. HydroResKit: a schema-driven workflow for heterogeneous data integration in basin-scale hydrological resilience assessment. *Frontiers of Computer Science*, 2026. DOI: [10.1007/s11704-026-61264-8](https://doi.org/10.1007/s11704-026-61264-8)

## Core Capabilities

- Resilience schema for hazard, exposure, sensitivity, adaptive capacity, and recovery.
- Data adapter interface for open Earth-science datasets.
- Indicator normalization, direction adjustment, weighting, aggregation, and diagnostics.
- Provenance records for derived indicators.
- Uncertainty analysis through weight perturbation and rank stability.
- File audit records with SHA256 checksums for prepared inputs and derived outputs.
- Missing-data reports, contribution diagnostics, and weighting-method comparisons.

## Current Adapters

- `hydroreskit.adapters.boundary`: read and validate basin/sub-basin vector boundaries.
- `hydroreskit.adapters.hydroatlas`: map HydroATLAS exports into HydroResKit schema indicators.
- `hydroreskit.adapters.hydrobasins`: derive lightweight indicators from HydroBASINS attributes for a first real-data smoke test.
- `hydroreskit.adapters.tabular`: read and validate basin-scale indicator tables.
- `hydroreskit.adapters.raster`: aggregate raster values to basin/sub-basin polygons.
- `hydroreskit.adapters.timeseries`: aggregate unit-level time series and raster snapshot series.
- `hydroreskit.adapters.era5_land`, `modis_ndvi`, and `jrc_gsw`: first helper interfaces for converting downloaded/open exports into HydroResKit indicators.

## Quick Start

```bash
pip install -e .
hydroreskit validate-schema configs/indicator_schema.yml
hydroreskit validate-table data_sample/demo_indicators.csv configs/indicator_schema.yml --strict
hydroreskit demo configs/yangtze_demo.yml
```

The demo writes score and diagnostic tables to `outputs/`, including missingness reports, indicator weights, rank tables, contribution summaries, missing-indicator sensitivity, and weighting-method comparisons.

The current repository contains the package scaffold, core assessment engine, adapter interfaces, a real Yangtze HydroBASINS boundary workflow, and a HydroATLAS-derived static benchmark workflow. Dynamic recovery indicators remain an optional extension.

## Prepare Official Basin Units

Download HydroBASINS/HydroATLAS files from the official provider, then prepare a local demo boundary layer:

```bash
python scripts/prepare_basin_units.py --input path/to/hybas.shp --output data_work/yangtze_units.geojson --id-column HYBAS_ID --summary outputs/boundary_summary.csv
```

The script writes audit metadata to `outputs/file_audit.csv` by default.

## Build the First Real HydroBASINS Attribute Indicator

After preparing `data_work/yangtze_hydrobasins_l6.geojson`, derive the first schema-aligned real indicator table:

```bash
python scripts/build_hydrobasins_attribute_indicators.py --boundaries data_work/yangtze_hydrobasins_l6.geojson --output data_work/yangtze_hydrobasins_attribute_indicators.csv --id-column HYBAS_ID
hydroreskit demo configs/yangtze_hydrobasins_attribute_demo.yml
python scripts/make_demo_figures.py
```

This smoke test derives `h_flood_prone_terrain = log1p(UP_AREA)` from HydroBASINS attributes and writes a first real score map to `outputs/figures/fig7_hydrobasins_attribute_score_map.png`. It is not a full resilience assessment; it verifies the real boundary-to-indicator-to-score-to-map path before richer HydroATLAS, climate, vegetation, water, population, and urban indicators are added.

## Map HydroATLAS Attributes to HydroResKit Indicators

HydroATLAS is used as an input source, not redistributed as a raw dataset. After exporting a HydroATLAS table with `HYBAS_ID` and needed attributes, run:

```bash
python scripts/build_hydroatlas_indicators.py --input path/to/hydroatlas_level06_yangtze.csv --boundaries data_work/yangtze_hydrobasins_l6.geojson --output data_work/yangtze_hydroatlas_indicators.csv --id-column HYBAS_ID
```

For a tiny syntax check using a synthetic HydroATLAS-style table:

```bash
python scripts/build_hydroatlas_indicators.py --input data_sample/hydroatlas_export_sample.csv --output outputs/hydroatlas_export_sample_indicators.csv --id-column HYBAS_ID
```

The mapping currently derives up to 12 schema indicators covering hazard, exposure, sensitivity, and adaptive capacity. Recovery indicators still require time-series/event data rather than static HydroATLAS attributes.

For Google Earth Engine, use `scripts/gee_export_hydroatlas_yangtze_level06.js` as a Code Editor template, then feed the exported CSV to `scripts/build_hydroatlas_indicators.py`.

For a scripted Earth Engine route:

```bash
python -m pip install earthengine-api
python scripts/gee_export_hydroatlas_yangtze.py --authenticate --auth-mode localhost --project YOUR_GCP_PROJECT
```

After the Drive export finishes, download the CSV to `data_raw/hydroatlas_yangtze_level06_hydroreskit.csv` and run `scripts/build_hydroatlas_indicators.py`.

For this small Yangtze table, direct local download can also be tried:

```bash
python scripts/gee_export_hydroatlas_yangtze.py --authenticate --auth-mode localhost --project YOUR_GCP_PROJECT --local-output data_raw/hydroatlas_yangtze_level06_hydroreskit.csv
```

If Earth Engine refuses a direct download URL, use the default Drive export mode.

After Earth Engine authentication, the complete local pipeline can be run with:

```bash
python scripts/run_hydroatlas_gee_pipeline.py --project YOUR_GCP_PROJECT
```

For first-time authentication and then the full pipeline:

```bash
python scripts/run_hydroatlas_gee_pipeline.py --authenticate --auth-mode localhost --project YOUR_GCP_PROJECT
```

## Merge Source-Specific Indicator Tables

After individual adapters create source-specific tables, merge them by `HYBAS_ID`:

```bash
python scripts/merge_indicator_tables.py --inputs data_work/yangtze_hydrobasins_attribute_indicators.csv data_work/yangtze_hydroatlas_indicators.csv --output data_work/yangtze_static_indicators.csv --unit-id-column HYBAS_ID --duplicate-policy error
python -m hydroreskit.cli demo configs/yangtze_static_demo.yml
```

The current `yangtze_static_demo.yml` uses `data_work/yangtze_static_indicators.csv` as the stable real-data entry point. Once `data_work/yangtze_hydroatlas_indicators.csv` exists, the static table becomes the HydroATLAS-derived 12-indicator benchmark input while retaining lower-priority HydroBASINS proxies as renamed audit columns when configured.

For the manuscript workflow, prefer the source-resolution config:

```bash
python scripts/build_static_indicator_table.py configs/yangtze_static_sources.yml
python -m hydroreskit.cli demo configs/yangtze_static_demo.yml
```

This records indicator-level source choices in `outputs/yangtze_static_source_resolution.csv`, including the priority rule that HydroATLAS replaces the HydroBASINS upstream-area proxy for `h_flood_prone_terrain` when both sources are available.

## User-Defined Weights

Set `weighting: user_defined` in a run configuration and provide a `user_weights` mapping or a YAML file such as `configs/user_weights_example.yml`.

## Theory Boundary

HydroResKit uses climate-risk and social-ecological resilience theory to structure the indicator schema. The package does not claim that a single index fully represents watershed resilience; instead, it makes indicator choices, data provenance, weighting, and uncertainty explicit.

# HydroATLAS Indicator Mapping

This note documents the first HydroATLAS-to-HydroResKit mapping layer. HydroATLAS already provides rich hydro-environmental attributes, but those attributes are not organized as a watershed climate-resilience assessment schema. HydroResKit therefore treats HydroATLAS as an input data source and maps selected attributes into the five HydroResKit dimensions.

## Input Requirement

HydroResKit does not redistribute the full HydroATLAS source tables. Users should obtain HydroATLAS through official channels, for example:

- HydroSHEDS/HydroATLAS download page.
- Google Earth Engine Data Catalog export for `WWF/HydroATLAS/v1/Basins/level06`.
- A local GIS export from BasinATLAS attributes.

The input table must include `HYBAS_ID` and any HydroATLAS source columns needed by the mapping. The script derives all available mapped indicators and records skipped indicators when required source columns are absent.

## Earth Engine Export Template

If using Google Earth Engine, paste `scripts/gee_export_hydroatlas_yangtze_level06.js` into the Earth Engine Code Editor. The template filters `WWF/HydroATLAS/v1/Basins/level06` by `MAIN_BAS = 4060009880` and exports only the columns needed by the current HydroResKit mapping.

After downloading the exported CSV from Google Drive, place it in `data_raw/` or another local source folder and run the mapping command below.

## Earth Engine Python Export

For a more reproducible scripted route, install the Earth Engine Python API:

```bash
python -m pip install earthengine-api
```

First-time authentication:

```bash
python scripts/gee_export_hydroatlas_yangtze.py --authenticate --auth-mode localhost --project YOUR_GCP_PROJECT
```

If Earth Engine is already authenticated locally:

```bash
python scripts/gee_export_hydroatlas_yangtze.py --project YOUR_GCP_PROJECT
```

The script starts an Earth Engine `Export.table.toDrive` task with fixed selectors and `MAIN_BAS = 4060009880`. After the task completes in Google Drive, download:

```text
hydroatlas_yangtze_level06_hydroreskit.csv
```

to:

```text
data_raw/hydroatlas_yangtze_level06_hydroreskit.csv
```

Because the Yangtze level 6 subset is small, a direct local download can also be attempted:

```bash
python scripts/gee_export_hydroatlas_yangtze.py ^
  --authenticate ^
  --auth-mode localhost ^
  --project YOUR_GCP_PROJECT ^
  --local-output data_raw\hydroatlas_yangtze_level06_hydroreskit.csv
```

This uses Earth Engine's table download URL route. If Earth Engine cannot create a direct URL or the request times out, fall back to the default Drive export.

## One-Command Local Pipeline

After Earth Engine authentication, run:

```bash
python scripts/run_hydroatlas_gee_pipeline.py --project YOUR_GCP_PROJECT
```

For first-time authentication:

```bash
python scripts/run_hydroatlas_gee_pipeline.py ^
  --authenticate ^
  --auth-mode localhost ^
  --project YOUR_GCP_PROJECT
```

This pipeline performs four steps:

1. download `data_raw/hydroatlas_yangtze_level06_hydroreskit.csv` from Earth Engine;
2. create `data_work/yangtze_hydroatlas_indicators.csv`;
3. rebuild `data_work/yangtze_static_indicators.csv`;
4. rerun the static demo and regenerate figures.

## Command

```bash
python scripts/build_hydroatlas_indicators.py ^
  --input path\to\hydroatlas_level06_yangtze.csv ^
  --boundaries data_work\yangtze_hydrobasins_l6.geojson ^
  --output data_work\yangtze_hydroatlas_indicators.csv ^
  --id-column HYBAS_ID ^
  --metadata-output outputs\hydroatlas_indicator_metadata.csv ^
  --audit outputs\file_audit.csv
```

If `--boundaries` is provided, the script filters and reorders the HydroATLAS table to the prepared Yangtze `HYBAS_ID` units.

For full BasinATLAS geodatabase/shapefile inputs, the script can filter the source during read:

```bash
python scripts/build_hydroatlas_indicators.py ^
  --input data_raw\BasinATLAS_Data_v10.gdb ^
  --layer BasinATLAS_v10_lev06 ^
  --main-basin-id 4060009880 ^
  --boundaries data_work\yangtze_hydrobasins_l6.geojson ^
  --output data_work\yangtze_hydroatlas_indicators.csv ^
  --id-column HYBAS_ID ^
  --metadata-output outputs\hydroatlas_indicator_metadata.csv ^
  --audit outputs\file_audit.csv
```

See `docs/hydroatlas_full_download_crop.md` for the current full-download status and fallback routes.

## Initial Mapping

| HydroResKit indicator | Dimension | HydroATLAS source columns | Formula | Interpretation boundary |
|---|---|---|---|---|
| `h_precip_variability` | hazard | `pre_mm_s01`-`pre_mm_s12` | monthly precipitation coefficient of variation | Long-term seasonality proxy, not event precipitation |
| `h_drought_intensity` | hazard | `cmi_ix_syr` | `-cmi_ix_syr` | Lower climate moisture becomes higher drought stress |
| `h_flood_prone_terrain` | hazard | `inu_pc_slt` | `inu_pc_slt` | Inundation proxy, not hydraulic flood modeling |
| `e_population_density` | exposure | `ppd_pk_sav` | `ppd_pk_sav` | Population exposure proxy |
| `e_built_up_fraction` | exposure | `urb_pc_sse` | `urb_pc_sse` | Urban extent proxy |
| `e_cropland_fraction` | exposure | `crp_pc_sse` | `crp_pc_sse` | Agricultural exposure proxy |
| `s_slope_mean` | sensitivity | `slp_dg_sav` | `slp_dg_sav` | Terrain sensitivity proxy |
| `s_ecological_fragility` | sensitivity | `for_pc_sse` | `100 - for_pc_sse` | Low-forest-cover proxy, not ecosystem recovery dynamics |
| `s_water_stress_proxy` | sensitivity | `pet_mm_syr`, `aet_mm_syr` | `pet_mm_syr - aet_mm_syr` | Atmospheric water-demand gap proxy |
| `a_surface_water_fraction` | adaptive capacity | `lka_pc_sse` | `lka_pc_sse` | Surface-water extent proxy, not storage capacity |
| `a_green_blue_space_fraction` | adaptive capacity | `for_pc_sse`, `lka_pc_sse`, `wet_pc_sg1`, `wet_pc_sg2` | clipped sum | Coarse green-blue proxy |
| `a_economic_proxy` | adaptive capacity | `gdp_ud_sav` | `gdp_ud_sav` | Socioeconomic capacity proxy |

## Why This Is Not Duplicating HydroATLAS

HydroATLAS supplies attributes. HydroResKit supplies a task-specific protocol:

- selects attributes relevant to a watershed resilience schema;
- records formulas, source columns, and caveats;
- validates basin IDs against prepared boundaries;
- produces schema-level missingness reports;
- routes derived indicators into weighting, aggregation, diagnostics, and maps;
- keeps source data acquisition separate from reproducible processing.

The manuscript should describe this as a resilience-ready mapping layer, not as a new raw HydroATLAS dataset.

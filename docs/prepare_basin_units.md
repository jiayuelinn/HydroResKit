# Preparing Basin Units

HydroResKit does not redistribute HydroBASINS or HydroATLAS raw layers. Users should download the relevant official vector file from HydroSHEDS/HydroBASINS and then run the preparation script locally.

Example:

```bash
python scripts/prepare_basin_units.py ^
  --input path\to\hybas_as_lev06_v1c.shp ^
  --output data_work\yangtze_hydrobasins_l6.geojson ^
  --id-column HYBAS_ID ^
  --query "MAIN_BAS == 123456789" ^
  --summary outputs\yangtze_boundary_summary.csv ^
  --audit outputs\file_audit.csv
```

The `--query` expression is intentionally user-controlled because HydroBASINS selection rules may differ across basin levels and study designs. For the final Yangtze demonstration, the selected rule must be documented in the provenance table and manuscript supplement.

The script records SHA256 checksums, file sizes, source labels, and processing steps in `outputs/file_audit.csv`.

## Yangtze Main-Basin Selection by Point

If the `MAIN_BAS` value is unknown, use a point inside the target river basin and let the script select all polygons that share the containing polygon's `MAIN_BAS` value.

Example using a lower Yangtze main-stem point near the Nanjing reach. This point should be verified visually against the official HydroBASINS layer before final submission:

```bash
python scripts/prepare_basin_units.py ^
  --input path\to\hybas_as_lev06_v1c.shp ^
  --output data_work\yangtze_hydrobasins_l6.geojson ^
  --id-column HYBAS_ID ^
  --point-lon 118.8 ^
  --point-lat 32.1 ^
  --select-main-basin ^
  --main-basin-column MAIN_BAS ^
  --summary outputs\yangtze_boundary_summary.csv ^
  --audit outputs\file_audit.csv
```

The selected boundary set must be checked before it is used as the official demonstration unit set. Record the final point, level, and selected `MAIN_BAS` value in the supplement.

## Optional Download Helper

The official HydroBASINS Asia package URL is listed in `configs/hydrosheds_sources.yml`. After checking provider terms, a local download can be audited with:

```bash
python scripts/download_source.py hydrobasins_as_standard_lev01_12 --output-dir data_raw
```

## First Attribute Indicator Table

Once the boundary layer exists, the first real indicator table can be generated from HydroBASINS attributes:

```bash
python scripts/build_hydrobasins_attribute_indicators.py ^
  --boundaries data_work\yangtze_hydrobasins_l6.geojson ^
  --output data_work\yangtze_hydrobasins_attribute_indicators.csv ^
  --id-column HYBAS_ID ^
  --metadata-output outputs\hydrobasins_attribute_indicator_metadata.csv ^
  --audit outputs\file_audit.csv
```

The script currently derives `h_flood_prone_terrain = log1p(UP_AREA)` and keeps auxiliary HydroBASINS fields for audit. This is a real-data pipeline check, not the full resilience indicator set.

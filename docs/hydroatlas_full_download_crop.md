# HydroATLAS Full Download and Cropping Log

This note records the full-download route for producing the real Yangtze HydroATLAS indicator table.

## Target Source

The preferred full source is the HydroATLAS v1.0 BasinATLAS geodatabase package:

```text
BasinATLAS_Data_v10.gdb.zip
Figshare file ID: 20082137
Size from Figshare API: 2,695,658,577 bytes
MD5 from Figshare API: 69af94baee68da5a3f80f09e7b85bd04
Download URL from API: https://ndownloader.figshare.com/files/20082137
```

The shapefile package is larger:

```text
BasinATLAS_Data_v10_shp.zip
Figshare file ID: 20087237
Size from Figshare API: 4,276,492,333 bytes
```

## Current Download Status

Command-line download attempts from the current workspace failed before any bytes were transferred:

- `https://ndownloader.figshare.com/files/20082137` returned repeated HTTP 504 gateway timeouts.
- `https://figshare.com/ndownloader/files/20082137` returned HTTP 403.
- Range requests for the first 1 MB also failed.
- Remote `geopandas`/GDAL reads from the Figshare URL failed for the same access reasons.

This means the processing code is ready, but the full package still needs to be obtained through a browser download, another network, or Google Earth Engine export.

## Preferred Plan B: Scripted GEE Export

The most reproducible lightweight route is now:

```bash
python -m pip install earthengine-api
python scripts/gee_export_hydroatlas_yangtze.py --authenticate --auth-mode localhost --project YOUR_GCP_PROJECT
```

This starts a Google Drive export for the selected HydroATLAS level 6 Yangtze attributes. It avoids downloading the multi-GB BasinATLAS source package. Once the CSV is downloaded from Google Drive, run:

For direct local download, try:

```bash
python scripts/gee_export_hydroatlas_yangtze.py ^
  --authenticate ^
  --auth-mode localhost ^
  --project YOUR_GCP_PROJECT ^
  --local-output data_raw\hydroatlas_yangtze_level06_hydroreskit.csv
```

If the direct route fails, use the Drive export command above.

```bash
python scripts/build_hydroatlas_indicators.py ^
  --input data_raw\hydroatlas_yangtze_level06_hydroreskit.csv ^
  --boundaries data_work\yangtze_hydrobasins_l6.geojson ^
  --output data_work\yangtze_hydroatlas_indicators.csv ^
  --id-column HYBAS_ID ^
  --metadata-output outputs\hydroatlas_indicator_metadata.csv ^
  --audit outputs\file_audit.csv
```

## Cropping Command After Download

After placing the full geodatabase package or extracted `.gdb` in `data_raw/`, run:

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

If the source remains zipped and the local GDAL build can read zipped geodatabases, use a `zip+` path. If not, extract the `.gdb` folder first.

Then rebuild the static benchmark:

```bash
python scripts/build_static_indicator_table.py configs/yangtze_static_sources.yml
python -m hydroreskit.cli demo configs/yangtze_static_demo.yml
python scripts/make_demo_figures.py
```

## Expected Output

The real HydroATLAS step should create:

```text
data_work/yangtze_hydroatlas_indicators.csv
outputs/hydroatlas_indicator_metadata.csv
```

Once this file exists, `configs/yangtze_static_sources.yml` will merge it into `data_work/yangtze_static_indicators.csv` and prefer HydroATLAS over the HydroBASINS upstream-area proxy for `h_flood_prone_terrain`.

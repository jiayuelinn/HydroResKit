# Candidate Data Sources

This document records candidate open datasets for HydroResKit. Final inclusion depends on license, accessibility, spatial-temporal coverage, and reproducibility.

The auditable source register is stored in `docs/data_source_audit.csv`. The readable license and citation audit is stored in `docs/data_source_license_citation_audit.md`.

| Role | Candidate source | Official URL | Why it matters | Initial use |
|---|---|---|---|---|
| Basin units | HydroBASINS | https://www.hydrosheds.org/products/hydrobasins | Global nested sub-basin polygons and Pfafstetter topology | spatial unit |
| Hydro-environmental attributes | HydroATLAS | https://www.hydrosheds.org/hydroatlas | Hydro-environmental attributes for HydroBASINS, HydroRIVERS, and HydroLAKES | terrain, hydro-environmental, anthropogenic proxies |
| Climate forcing | ERA5-Land monthly means | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means | Global land reanalysis from 1950 onward, 0.1 degree monthly product in CDS | precipitation, temperature, drought and variability indicators |
| Population exposure | WorldPop | https://www.worldpop.org/ | Open high-resolution spatial demographic data | population exposure |
| Built-up and settlement exposure | GHSL | https://human-settlement.emergency.copernicus.eu/ | Open and free data/tools for human settlement and human presence | built-up fraction, settlement exposure |
| Land cover | ESA WorldCover | https://worldcover2021.esa.int/ | Global 10 m land-cover product for 2021 based on Sentinel-1 and Sentinel-2 | cropland, built-up, green-blue classes |
| Vegetation condition | MODIS MOD13Q1 v061 | https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod13q1-061 | 16-day 250 m NDVI/EVI product from NASA LP DAAC | ecological sensitivity and recovery |
| Surface water | JRC Global Surface Water | https://global-surface-water.appspot.com/ | Long-term global surface-water history and occurrence products | water capacity and water recovery |
| Night-time lights | NASA Black Marble VIIRS | https://blackmarble.gsfc.nasa.gov/ | VIIRS night-time light products for human activity proxies | exposure, adaptive capacity, recovery |

## Data-Source Principle

HydroResKit should not redistribute large raw datasets unless licenses clearly allow it. The first public release should provide:

- scripts or adapters to retrieve/process source data;
- small sample data for tests;
- provenance records;
- derived demonstration indicators when redistribution is allowed.

## Initial Demo Data Policy

The first executable release should include a tiny synthetic table for software tests and a reproducible script/notebook for generating the real Yangtze demonstration indicators. This avoids redistributing large raw products while making the workflow auditable.

The package now follows a "bring official exports, then aggregate" design for restricted or account-based data sources. Users download/export source data through official portals such as CDS, Earthdata, or Google Earth Engine, and HydroResKit provides adapters to aggregate those files to basin units and transform them into schema indicators.

## Current Locked Sources for the First Demo

Use these first unless a license/access issue appears:

- HydroBASINS level 6 or level 5 for sub-basin units.
- HydroATLAS for static basin attributes.
- ERA5-Land monthly means for hydro-climatic indicators.
- MODIS MOD13Q1 for vegetation sensitivity and recovery.
- JRC Global Surface Water for water occurrence indicators.
- WorldPop or GHSL for population exposure.
- GHSL and ESA WorldCover for built-up and land-cover indicators.
- NASA Black Marble VIIRS for night-time light proxies.

## HydroBASINS Source Manifest

HydroBASINS official source URLs used by the preparation workflow are listed in `configs/hydrosheds_sources.yml`. The current default source for the Yangtze demonstration is the Asia standard package:

```text
https://data.hydrosheds.org/file/hydrobasins/standard/hybas_as_lev01-12_v1c.zip
```

The repository should not ship this raw package. Users should download it locally after checking HydroSHEDS terms, then run `scripts/prepare_basin_units.py` to select and audit the target basin units.

## HydroATLAS Export Route

Because full HydroATLAS source files are large, HydroResKit now supports an export-first route. Users can export only the needed HydroATLAS level 6 attributes for the prepared Yangtze `HYBAS_ID` units, then run `scripts/build_hydroatlas_indicators.py`. The source manifest includes the Google Earth Engine Data Catalog page for `WWF/HydroATLAS/v1/Basins/level06`, which exposes the relevant attribute names.

The initial HydroATLAS mapping can derive up to 12 indicators:

- hazard: `h_precip_variability`, `h_drought_intensity`, `h_flood_prone_terrain`;
- exposure: `e_population_density`, `e_built_up_fraction`, `e_cropland_fraction`;
- sensitivity: `s_slope_mean`, `s_ecological_fragility`, `s_water_stress_proxy`;
- adaptive capacity: `a_surface_water_fraction`, `a_green_blue_space_fraction`, `a_economic_proxy`.

Recovery indicators are intentionally excluded from the HydroATLAS static mapping because they require time-series or event-window data.

## First Real Derived Indicator

The current local workflow derives a first schema-aligned indicator directly from prepared HydroBASINS attributes:

- `h_flood_prone_terrain = log1p(UP_AREA)`
- source column: `UP_AREA`
- spatial unit: HydroBASINS level 6 `HYBAS_ID`
- output table: `data_work/yangtze_hydrobasins_attribute_indicators.csv`
- metadata: `outputs/hydrobasins_attribute_indicator_metadata.csv`

This indicator is a drainage-network accumulation proxy used to verify the real data-processing path. It is not a replacement for full flood susceptibility, HydroATLAS, DEM-derived terrain, or hydraulic flood modeling indicators.

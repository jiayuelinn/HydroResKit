# Data Source License and Citation Audit

Audit date: 2026-06-01

This document records the final license, version, citation, and release decision for the data sources considered by HydroResKit. The machine-readable register is `docs/data_source_audit.csv`.

## Audit Scope

The audit covers the data sources in the HydroResKit candidate register:

- HydroBASINS
- HydroATLAS / BasinATLAS
- ERA5-Land monthly averaged data
- MODIS MOD13Q1 v061
- JRC Global Surface Water v1.4
- WorldPop population grids
- Global Human Settlement Layer
- ESA WorldCover
- NASA Black Marble VIIRS VNP46

Alternative sources mentioned only as fallback examples in the schema, such as CHIRPS, GLDAS, generic road/accessibility datasets, or third-party GDP rasters, are not locked for the first HydroResKit release. They should not be cited as actual inputs unless later selected and audited.

## Release Decision

HydroResKit should release:

- source-specific download/export scripts;
- exact source URLs, dataset IDs, product versions, and access dates;
- checksums for locally prepared official files when available;
- source-to-indicator mapping tables;
- derived basin-level indicators for the Yangtze benchmark when the source license permits;
- provenance tables and processing logs.

HydroResKit should not release:

- raw global HydroBASINS or HydroATLAS packages;
- raw ERA5-Land NetCDF/GRIB files;
- raw MODIS, JRC, WorldPop, GHSL, WorldCover, or Black Marble rasters;
- any account token, GEE project ID, CDS key, Earthdata token, or private credential.

## Source-by-Source Notes

### HydroBASINS

Status: verified.

Product locked for the demo: HydroBASINS v1.c, Asia standard package, level 6 Yangtze units.

License/terms: HydroBASINS follows the HydroSHEDS license agreement. It is free for scientific, educational, and commercial use, but redistribution, attribution, disclaimers, and liability terms follow the HydroSHEDS license agreement. The repository should therefore avoid bundling the raw global package.

Citation:

Lehner, B., Grill, G. (2013). Global river hydrography and network routing: baseline data and new approaches to study the world's large river systems. Hydrological Processes, 27(15), 2171-2186. Data available at www.hydrosheds.org.

### HydroATLAS / BasinATLAS

Status: verified.

Product locked for the demo: HydroATLAS v1.0, BasinATLAS level 06, exported through Google Earth Engine dataset `WWF/HydroATLAS/v1/Basins/level06`.

License/terms: HydroATLAS is licensed under CC-BY 4.0. The technical documentation notes that individual attribute columns are released under CC-BY 4.0 or ODbL 1.0 as applicable. The derived Yangtze indicator table can be released with attribution and clear processing formulas.

Citation:

Linke, S., Lehner, B., Ouellet Dallaire, C., Ariwi, J., Grill, G., Anand, M., Beames, P., Burchard-Levine, V., Maxwell, S., Moidu, H., Tan, F., Thieme, M. (2019). Global hydro-environmental sub-basin and river reach characteristics at high spatial resolution. Scientific Data, 6, 283. https://doi.org/10.1038/s41597-019-0300-6

### ERA5-Land Monthly Averaged Data

Status: verified.

Product: ERA5-Land monthly averaged data from 1950 to present. DOI: https://doi.org/10.24381/cds.68d2bb30.

License/terms: CDS catalogue lists a CC-BY licence. Users must cite the CDS catalogue entry and provide clear attribution to the Copernicus programme.

Citation:

Munoz Sabater, J. (2019). ERA5-Land monthly averaged data from 1950 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS). https://doi.org/10.24381/cds.68d2bb30

Method reference:

Munoz-Sabater, J., et al. (2021). ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. Earth System Science Data, 13, 4349-4383. https://doi.org/10.5194/essd-13-4349-2021

### MODIS MOD13Q1 v061

Status: verified.

Product: MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid, V061. DOI: https://doi.org/10.5067/MODIS/MOD13Q1.061.

License/terms: MODIS products obtained through LP DAAC have no restrictions on subsequent use, sale, or redistribution. Product DOI citation is required for publication.

Citation:

Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061 [Data set]. NASA EOSDIS Land Processes DAAC. https://doi.org/10.5067/MODIS/MOD13Q1.061

### JRC Global Surface Water

Status: verified.

Product: JRC Global Surface Water v1.4.

License/terms: Produced under the Copernicus Programme and provided free of charge without restriction of use; proper acknowledgement and citation are required. If displayed as a map layer, use the attribution `Source: EC JRC/Google`.

Citation:

Pekel, J.-F., Cottam, A., Gorelick, N., Belward, A. S. (2016). High-resolution mapping of global surface water and its long-term changes. Nature, 540, 418-422. https://doi.org/10.1038/nature20584

### WorldPop

Status: verified for license; product-specific citation must be matched to the exact downloaded product if WorldPop becomes a release input.

Product: WorldPop Global Project estimated residential population. If Earth Engine is used, the corresponding collection is `WorldPop/GP/100m/pop`.

License/terms: WorldPop datasets are licensed under CC-BY 4.0.

Citation rule:

Use the product-specific WorldPop Hub recommended citation for the exact country/product/year. For general methodology, cite:

Tatem, A. J. (2017). WorldPop, open data for spatial demography. Scientific Data, 4, 170004. https://doi.org/10.1038/sdata.2017.4

### Global Human Settlement Layer

Status: verified.

Products likely to be used: GHS-POP R2023A and GHS-BUILT-S R2023A.

License/terms: GHSL data are CC-BY 4.0. The GHSL site explicitly states that generic website citation is insufficient; users must cite the specific data product and the latest peer-reviewed reference.

Population product citation:

Schiavina, M., Freire, S., Carioli, A., MacManus, K. (2023). GHS-POP R2023A - GHS population grid multitemporal (1975-2030). European Commission, Joint Research Centre (JRC). https://doi.org/10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE

Built-up product citation:

Pesaresi, M., Politis, P. (2023). GHS-BUILT-S R2023A - GHS built-up surface grid, derived from Sentinel2 composite and Landsat, multitemporal (1975-2030). European Commission, Joint Research Centre (JRC). https://doi.org/10.2905/9F06F36F-4B11-47EC-ABB0-4F8B7B1D72EA

Method reference:

Pesaresi, M., et al. (2024). Advances on the Global Human Settlement Layer by joint assessment of Earth Observation and population survey data. International Journal of Digital Earth, 17(1). https://doi.org/10.1080/17538947.2024.2390454

### ESA WorldCover

Status: verified.

Product: ESA WorldCover 2021 v200 as primary; 2020 v100 as optional comparison layer.

License/terms: Free of charge without restriction of use under CC-BY 4.0. Published work must acknowledge ESA WorldCover and cite the product dataset.

Citation for 2021:

Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W., Brockmann, C., Kirches, G., Wevers, J., Cartus, O., Santoro, M., Fritz, S., Lesiv, M., Herold, M., Tsendbazar, N. E., Xu, P., Ramoino, F., Arino, O. (2022). ESA WorldCover 10 m 2021 v200. https://doi.org/10.5281/zenodo.7254221

Citation for 2020:

Zanaga, D., et al. (2021). ESA WorldCover 10 m 2020 v100. https://doi.org/10.5281/zenodo.5571936

### NASA Black Marble VIIRS

Status: verified.

Product: Collection 2.0 VNP46 product suite. Use VNP46A2.002 for daily moonlight-adjusted nighttime lights and VNP46A3.001 for monthly composites if selected.

License/terms: LAADS DAAC data products are provided without monetary charge and have no restrictions on subsequent use or redistribution. NASA requests acknowledgement and product citation.

Daily product citation:

VIIRS/NPP Gap-Filled Lunar BRDF-Adjusted Nighttime Lights Daily L3 Global 500m Linear Lat Lon Grid, Version 2.0, NASA LAADS DAAC. https://doi.org/10.5067/VIIRS/VNP46A2.002

Monthly product citation:

VIIRS/NPP Lunar BRDF-Adjusted Nighttime Lights Monthly L3 Global 15 arc second Linear Lat Lon Grid. NASA LAADS DAAC. https://doi.org/10.5067/VIIRS/VNP46A3.001

Method reference:

Roman, M. O., Wang, Z., Sun, Q., Kalb, V., Miller, S. D., Molthan, A., Schultz, L., Bell, J., Stokes, E. C., Pandey, B., Seto, K. C., et al. (2018). NASA's Black Marble nighttime lights product suite. Remote Sensing of Environment, 210, 113-143. https://doi.org/10.1016/j.rse.2018.03.017

## Manuscript Wording

Use this conservative availability statement:

> HydroResKit does not redistribute large third-party raw products. Instead, it provides source-specific adapters, official download/export instructions, provenance templates, and a processed Yangtze basin indicator table derived from auditable open datasets under their respective licenses. Users can regenerate the benchmark from official sources after accepting the corresponding provider terms.

Use this data citation statement:

> All source datasets are cited using their provider-recommended dataset citations and product versions. The benchmark indicator table records the source dataset, source columns, formula, expected direction, and caveat for each derived indicator.

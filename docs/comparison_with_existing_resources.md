# Functional Comparison with Existing Resources

HydroResKit should be compared by function, not by claiming to outperform existing hydrological resources.

| Resource/tool | Primary purpose | Typical spatial unit | Climate-resilience schema | Socio-ecological exposure integration | Provenance for derived indicators | Weighting/MCDA engine | Uncertainty diagnostics | Runnable basin adaptation workflow |
|---|---|---|---|---|---|---|---|---|
| CAMELS/CCAM | catchment attributes and hydrometeorology for large-sample hydrology | gauged catchments | no | limited | dataset-level metadata | no | no | no |
| Caravan | standardized global large-sample hydrology dataset | watersheds from source datasets | no | limited | dataset-level metadata | no | no | no |
| HydroATLAS/HydroBASINS | global basin geometry and hydro-environmental attributes | sub-basins and river reaches | no | partial | dataset-level metadata | no | no | no |
| HydroMT | geospatial preprocessing and water-system model setup | model-dependent | no | extensible but not resilience-specific | workflow-dependent | no | no | model setup, not resilience assessment |
| Raw EO and climate datasets | source variables | pixels/grids | no | no | source metadata only | no | no | no |
| HydroResKit | resilience-ready workflow and assessment toolkit | configurable basin/sub-basin units | yes | yes | yes | yes | yes | yes |

## Positioning Statement

Existing resources are valuable inputs or neighboring tools. HydroResKit adds a task-specific, provenance-aware computation layer for watershed climate-resilience assessment.


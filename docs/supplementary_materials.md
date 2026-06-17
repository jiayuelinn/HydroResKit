# Supplementary Materials Plan

The FCS letter main text should stay short. Detailed tables and extended protocol information should be placed in supplementary materials or repository documentation.

## Main Text

- Resource motivation and novelty boundary.
- HydroResKit architecture and core modules.
- Yangtze demonstration summary.
- Functional comparison against CAMELS/CCAM/Caravan/HydroATLAS/HydroMT.
- Availability and maintenance statement.

## Supplementary or Repository Documentation

| Material | Current file |
|---|---|
| Full candidate data-source register | `docs/data_source_audit.csv` |
| Data acquisition and release boundary | `docs/data_sources.md`, `docs/release_data_policy.md` |
| Indicator schema and theory grounding | `docs/indicator_schema.md`, `docs/theory_basis.md` |
| HydroBASINS preparation protocol | `docs/prepare_basin_units.md` |
| HydroBASINS first indicator smoke test | `docs/hydrobasins_attribute_indicators.md` |
| HydroATLAS mapping protocol | `docs/hydroatlas_indicators.md` |
| Indicator table merge and source priority | `docs/indicator_table_merging.md` |
| Diagnostics and uncertainty details | `docs/assessment_diagnostics.md` |
| Figure plan and current limitations | `docs/figures.md` |

This separation supports the short FCS letter format while keeping the workflow auditable.

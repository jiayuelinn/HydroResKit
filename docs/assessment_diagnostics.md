# Assessment Diagnostics

HydroResKit writes diagnostic outputs during the demo run. These tables support the Code & Data letter's claim that the workflow is auditable rather than a black-box index calculator.

## Demo Outputs

| Output | Purpose |
|---|---|
| `outputs/yangtze_missing_report.csv` | indicator-level missingness and schema coverage |
| `outputs/yangtze_unit_missing_report.csv` | sub-basin-level missingness |
| `outputs/yangtze_indicator_weights.csv` | final indicator weights used in the run |
| `outputs/yangtze_rank_table.csv` | resilience scores and descending ranks |
| `outputs/yangtze_indicator_contributions.csv` | long-format unit-indicator weighted contributions |
| `outputs/yangtze_contribution_summary.csv` | mean contribution magnitude by indicator |
| `outputs/yangtze_missing_indicator_sensitivity.csv` | score and rank sensitivity when dropping one indicator |
| `outputs/yangtze_weighting_method_comparison.csv` | equal, entropy, and PCA weighting comparison |

## FCS Letter Usage

The main text should mention only the diagnostics that fit a 2-3 page Code & Data letter:

- missingness report;
- weighting-method comparison;
- rank or score stability;
- contribution summary.

Full tables should go to supplementary materials or repository documentation.


"""Generate HydroResKit demo figures from current output tables."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hydroreskit.visualization import (
    plot_boundary_map,
    plot_dimension_heatmap,
    plot_missing_indicator_sensitivity,
    plot_resilience_rank,
    plot_score_map,
    plot_uncertainty_map,
    plot_weighting_comparison,
    plot_workflow,
)


OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"


def main() -> None:
    scores = pd.read_csv(OUTPUTS / "yangtze_demo_scores.csv", index_col="unit_id")
    weighting = pd.read_csv(OUTPUTS / "yangtze_weighting_method_comparison.csv")
    missing_sensitivity = pd.read_csv(OUTPUTS / "yangtze_missing_indicator_sensitivity.csv")
    data_sources = pd.read_csv(ROOT / "docs" / "data_source_audit.csv")

    plot_workflow(FIGURES / "fig1_hydroreskit_workflow.png")
    plot_dimension_heatmap(scores, FIGURES / "fig2_dimension_scores.png")
    plot_resilience_rank(scores, FIGURES / "fig3_resilience_scores.png")
    plot_weighting_comparison(weighting, FIGURES / "fig4_weighting_sensitivity.png")
    plot_missing_indicator_sensitivity(missing_sensitivity, FIGURES / "fig5_missing_indicator_sensitivity.png")

    boundary_path = ROOT / "data_work" / "yangtze_hydrobasins_l6.geojson"
    if boundary_path.exists():
        plot_boundary_map(
            boundary_path,
            FIGURES / "fig6_yangtze_hydrobasins_l6_map.png",
            title="Prepared Yangtze HydroBASINS level 6 units",
        )
        attribute_scores_path = OUTPUTS / "yangtze_hydrobasins_attribute_scores.csv"
        if attribute_scores_path.exists():
            plot_score_map(
                boundary_path,
                attribute_scores_path,
                FIGURES / "fig7_hydrobasins_attribute_score_map.png",
                id_column="HYBAS_ID",
                title="First real HydroBASINS attribute score",
            )
        static_scores_path = OUTPUTS / "yangtze_static_scores.csv"
        if static_scores_path.exists():
            plot_score_map(
                boundary_path,
                static_scores_path,
                FIGURES / "fig8_yangtze_static_score_map.png",
                id_column="HYBAS_ID",
                title="Merged static-indicator score",
            )
        static_uncertainty_path = OUTPUTS / "yangtze_static_weighting_method_comparison.csv"
        if static_uncertainty_path.exists():
            plot_uncertainty_map(
                boundary_path,
                static_uncertainty_path,
                FIGURES / "fig9_yangtze_static_uncertainty_map.png",
                id_column="HYBAS_ID",
                uncertainty_column="score_range",
                title="Static score uncertainty across weighting methods",
            )

    provenance_summary = data_sources[
        [
            "source_id",
            "source_name",
            "role_in_hydroreskit",
            "access_method",
            "redistribution_plan",
            "known_limitations",
            "hydroreskit_status",
        ]
    ].copy()
    provenance_summary.to_csv(OUTPUTS / "provenance_summary.csv", index=False)
    print(f"Wrote figures to {FIGURES}")
    print(f"Wrote provenance summary to {OUTPUTS / 'provenance_summary.csv'}")


if __name__ == "__main__":
    main()

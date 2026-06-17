"""Create the FCS Fig. 2 Yangtze static benchmark composite figure.

The figure is a demonstration output for HydroResKit. It visualizes the
static HydroATLAS-derived benchmark and must not be interpreted as a final
scientific assessment of Yangtze River Basin resilience.
"""

from __future__ import annotations

from pathlib import Path
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable


ROOT = Path(__file__).resolve().parents[1]
DATA_WORK = ROOT / "data_work"
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"

BOUNDARY_PATH = DATA_WORK / "yangtze_hydrobasins_l6.geojson"
SCORES_PATH = OUTPUTS / "yangtze_static_scores.csv"
MISSING_SENSITIVITY_PATH = OUTPUTS / "yangtze_static_missing_indicator_sensitivity.csv"
METADATA_PATH = OUTPUTS / "hydroatlas_indicator_metadata.csv"

PNG_PATH = FIGURES / "fig2_yangtze_static_benchmark_composite.png"
PDF_PATH = FIGURES / "fig2_yangtze_static_benchmark_composite.pdf"
AUDIT_PATH = OUTPUTS / "fig2_yangtze_static_benchmark_audit.csv"

DIMENSION_COLUMNS = ["hazard", "exposure", "sensitivity", "adaptive_capacity"]
DIMENSION_LABELS = {
    "hazard": "Hazard",
    "exposure": "Exposure",
    "sensitivity": "Sensitivity",
    "adaptive_capacity": "Adaptive\ncapacity",
}
DIMENSION_COLORS = {
    "hazard": "#D95F02",
    "exposure": "#7570B3",
    "sensitivity": "#1B9E77",
    "adaptive_capacity": "#E6AB02",
}
MAP_SUBBASIN_LINE = "#6B6B6B"
MAP_BASIN_LINE = "#1F1F1F"
MAP_FILL = "#F5F5F5"
MAP_GRID = "#DDDDDD"
SCORE_CMAP = "YlGnBu"
INDICATOR_LABELS = {
    "a_surface_water_fraction": "Surface water",
    "e_population_density": "Population",
    "e_built_up_fraction": "Built-up",
    "a_economic_proxy": "Economic proxy",
    "h_flood_prone_terrain": "Flood-prone terrain",
    "s_slope_mean": "Mean slope",
    "s_ecological_fragility": "Ecological fragility",
    "a_green_blue_space_fraction": "Green-blue space",
    "h_precip_variability": "Precip. variability",
    "e_cropland_fraction": "Cropland",
    "s_water_stress_proxy": "Water stress",
    "h_drought_intensity": "Drought intensity",
}


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Required input is missing: {path}. "
            "Run the HydroATLAS static benchmark pipeline before drawing Fig. 2."
        )


def require_columns(df: pd.DataFrame, columns: list[str], path: Path) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")


def load_inputs() -> tuple[gpd.GeoDataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    for path in [BOUNDARY_PATH, SCORES_PATH, MISSING_SENSITIVITY_PATH, METADATA_PATH]:
        require_file(path)

    boundaries = gpd.read_file(BOUNDARY_PATH)
    scores = pd.read_csv(SCORES_PATH)
    sensitivity = pd.read_csv(MISSING_SENSITIVITY_PATH)
    metadata = pd.read_csv(METADATA_PATH)

    require_columns(boundaries, ["HYBAS_ID", "geometry"], BOUNDARY_PATH)
    require_columns(scores, ["HYBAS_ID", *DIMENSION_COLUMNS, "resilience_score"], SCORES_PATH)
    require_columns(
        sensitivity,
        [
            "dropped_indicator",
            "mean_abs_score_delta",
            "p05_abs_score_delta",
            "p25_abs_score_delta",
            "p75_abs_score_delta",
            "p95_abs_score_delta",
            "mean_abs_rank_delta",
        ],
        MISSING_SENSITIVITY_PATH,
    )
    require_columns(metadata, ["indicator_id", "dimension"], METADATA_PATH)

    boundaries["HYBAS_ID"] = boundaries["HYBAS_ID"].astype(str)
    scores["HYBAS_ID"] = scores["HYBAS_ID"].astype(str)
    joined = boundaries.merge(scores, on="HYBAS_ID", how="left", validate="one_to_one")
    if joined["resilience_score"].isna().any():
        missing_count = int(joined["resilience_score"].isna().sum())
        raise ValueError(f"{missing_count} basin units do not have static benchmark scores.")

    return joined, scores, sensitivity, metadata


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.085,
        1.025,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=12,
        fontweight="bold",
        color="#222222",
        clip_on=False,
    )


def map_axis_style(ax: plt.Axes, joined: gpd.GeoDataFrame) -> None:
    minx, miny, maxx, maxy = joined.total_bounds
    ax.set_xlim(minx - 0.6, maxx + 0.6)
    ax.set_ylim(miny - 0.4, maxy + 0.4)
    ax.set_aspect("equal", adjustable="box")

    xticks = np.arange(np.ceil((minx - 0.5) / 5) * 5, maxx + 1, 5)
    yticks = np.arange(np.ceil((miny - 0.5) / 5) * 5, maxy + 1, 5)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.set_xticklabels([f"{tick:.0f}" for tick in xticks], fontsize=7)
    ax.set_yticklabels([f"{tick:.0f}" for tick in yticks], fontsize=7)
    ax.set_xlabel("Longitude (deg E)", fontsize=8)
    ax.set_ylabel("Latitude (deg N)", fontsize=8)
    ax.grid(color=MAP_GRID, linewidth=0.55, linestyle="--", zorder=0)
    ax.tick_params(direction="out", length=2.5, width=0.8, labelsize=7)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("#333333")


def draw_basin_boundaries(ax: plt.Axes, joined: gpd.GeoDataFrame) -> None:
    joined.boundary.plot(
        ax=ax,
        color=MAP_SUBBASIN_LINE,
        linewidth=0.32,
        linestyle=(0, (2.2, 2.2)),
        zorder=3,
    )
    joined.dissolve().boundary.plot(
        ax=ax,
        color=MAP_BASIN_LINE,
        linewidth=1.15,
        linestyle="-",
        zorder=4,
    )


def map_boundary_legend(ax: plt.Axes) -> None:
    handles = [
        Line2D([0], [0], color=MAP_BASIN_LINE, lw=1.15, linestyle="-", label="Basin boundary"),
        Line2D([0], [0], color=MAP_SUBBASIN_LINE, lw=0.55, linestyle=(0, (2.2, 2.2)), label="Sub-basin boundary"),
    ]
    legend = ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.30),
        ncol=2,
        fontsize=7,
        frameon=True,
        framealpha=0.92,
        edgecolor="#CCCCCC",
        facecolor="white",
        handlelength=2.5,
        borderpad=0.35,
        columnspacing=1.2,
    )
    legend.set_in_layout(True)


def plot_boundary_panel(ax: plt.Axes, joined: gpd.GeoDataFrame) -> None:
    joined.plot(ax=ax, color=MAP_FILL, edgecolor="none", zorder=1)
    draw_basin_boundaries(ax, joined)
    map_axis_style(ax, joined)
    map_boundary_legend(ax)
    ax.set_title("Yangtze HydroBASINS level-6 units", fontsize=9, pad=4)
    ax.text(
        0.02,
        0.05,
        f"n = {len(joined)} sub-basins",
        transform=ax.transAxes,
        fontsize=8,
        color="#333333",
        bbox={"facecolor": "white", "edgecolor": "#BBBBBB", "boxstyle": "round,pad=0.25"},
    )
    panel_label(ax, "a")


def plot_dimension_panel(ax: plt.Axes, scores: pd.DataFrame) -> None:
    data = [scores[column].dropna().to_numpy() for column in DIMENSION_COLUMNS]
    boxes = ax.boxplot(
        data,
        patch_artist=True,
        showfliers=False,
        widths=0.55,
        medianprops={"color": "#222222", "linewidth": 1.2},
        whiskerprops={"color": "#555555", "linewidth": 0.9},
        capprops={"color": "#555555", "linewidth": 0.9},
        boxprops={"edgecolor": "#444444", "linewidth": 0.9},
    )
    for patch, column in zip(boxes["boxes"], DIMENSION_COLUMNS):
        patch.set_facecolor(DIMENSION_COLORS[column])
        patch.set_alpha(0.65)

    means = [scores[column].mean() for column in DIMENSION_COLUMNS]
    ax.scatter(
        range(1, len(DIMENSION_COLUMNS) + 1),
        means,
        s=20,
        color="#222222",
        zorder=3,
        label="Mean",
    )
    ax.set_xticks(range(1, len(DIMENSION_COLUMNS) + 1))
    ax.set_xticklabels([DIMENSION_LABELS[column] for column in DIMENSION_COLUMNS], fontsize=8)
    ax.set_ylim(-0.02, 1.05)
    ax.set_ylabel("Dimension score (0-1)", fontsize=8)
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.6, linestyle="--")
    ax.tick_params(axis="both", labelsize=8, direction="out")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("HydroATLAS-derived dimension scores", fontsize=9, pad=4)
    ax.legend(loc="upper left", fontsize=7, frameon=False, handlelength=1.0)
    panel_label(ax, "b")


def plot_resilience_map_panel(ax: plt.Axes, joined: gpd.GeoDataFrame) -> None:
    norm = Normalize(vmin=joined["resilience_score"].min(), vmax=joined["resilience_score"].max())
    joined.plot(
        ax=ax,
        column="resilience_score",
        cmap=SCORE_CMAP,
        norm=norm,
        edgecolor="none",
        missing_kwds={"color": "#F5F5F5", "edgecolor": "#AAAAAA"},
        zorder=1,
    )
    draw_basin_boundaries(ax, joined)
    map_axis_style(ax, joined)
    map_boundary_legend(ax)
    ax.set_title("Static resilience score", fontsize=9, pad=4)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.95)
    sm = plt.cm.ScalarMappable(cmap=SCORE_CMAP, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cax, orientation="horizontal")
    cbar.ax.tick_params(labelsize=7, length=2, direction="out")
    cbar.outline.set_visible(False)
    cbar.set_label("Static resilience score (0-1)", fontsize=7, labelpad=1)
    panel_label(ax, "c")


def plot_sensitivity_panel(
    ax: plt.Axes, sensitivity: pd.DataFrame, metadata: pd.DataFrame
) -> None:
    dimension_lookup = metadata.set_index("indicator_id")["dimension"].to_dict()
    plot_df = sensitivity.copy()
    plot_df["dimension"] = plot_df["dropped_indicator"].map(dimension_lookup).fillna("unknown")
    plot_df = plot_df.nlargest(8, "mean_abs_score_delta")
    plot_df = plot_df.sort_values("mean_abs_score_delta", ascending=True)

    colors = [DIMENSION_COLORS.get(dimension, "#999999") for dimension in plot_df["dimension"]]
    labels = [INDICATOR_LABELS.get(indicator, indicator) for indicator in plot_df["dropped_indicator"]]
    y = np.arange(len(plot_df))
    ax.hlines(
        y,
        plot_df["p05_abs_score_delta"],
        plot_df["p95_abs_score_delta"],
        color="#B8B8B8",
        linewidth=1.0,
        zorder=1,
    )
    ax.hlines(
        y,
        plot_df["p25_abs_score_delta"],
        plot_df["p75_abs_score_delta"],
        color="#666666",
        linewidth=2.8,
        zorder=2,
    )
    ax.scatter(
        plot_df["mean_abs_score_delta"],
        y,
        s=42,
        color=colors,
        edgecolor="#222222",
        linewidth=0.45,
        zorder=3,
    )
    x_right = max(float(plot_df["p95_abs_score_delta"].max()), float(plot_df["mean_abs_score_delta"].max()))
    for yi, (_, row) in zip(y, plot_df.iterrows()):
        ax.text(
            x_right * 1.04,
            yi,
            f"rank chg {row['mean_abs_rank_delta']:.1f}",
            va="center",
            ha="left",
            fontsize=6.2,
            color="#555555",
        )
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlim(0, x_right * 1.34)
    ax.set_xlabel("Absolute score change after dropping indicator", fontsize=8)
    ax.set_title("Dropped-indicator sensitivity (top 8)", fontsize=9, pad=4)
    ax.text(
        0.01,
        0.985,
        "dot = mean; dark line = IQR; light line = 5-95%",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=6.2,
        color="#555555",
    )
    ax.grid(axis="x", color="#DDDDDD", linewidth=0.6, linestyle="--")
    ax.tick_params(axis="both", labelsize=7, direction="out")
    ax.spines[["top", "right"]].set_visible(False)
    legend_handles = [
        Patch(facecolor=DIMENSION_COLORS["hazard"], edgecolor="none", label="Hazard"),
        Patch(facecolor=DIMENSION_COLORS["exposure"], edgecolor="none", label="Exposure"),
        Patch(facecolor=DIMENSION_COLORS["sensitivity"], edgecolor="none", label="Sensitivity"),
        Patch(facecolor=DIMENSION_COLORS["adaptive_capacity"], edgecolor="none", label="Adaptive capacity"),
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower right",
        fontsize=6.5,
        frameon=True,
        framealpha=0.9,
        edgecolor="#CCCCCC",
        ncol=2,
        handlelength=1.0,
        columnspacing=0.8,
    )
    panel_label(ax, "d")


def write_audit(scores: pd.DataFrame, joined: gpd.GeoDataFrame, sensitivity: pd.DataFrame) -> None:
    audit = pd.DataFrame(
        [
            {
                "panel": "a",
                "input": str(BOUNDARY_PATH.relative_to(ROOT)),
                "status": "drawn",
                "note": (
                    f"{len(joined)} HydroBASINS level-6 Yangtze units; "
                    "longitude/latitude axes, thick basin boundary, dashed sub-basin boundaries, and below-frame boundary legend shown."
                ),
            },
            {
                "panel": "b",
                "input": str(SCORES_PATH.relative_to(ROOT)),
                "status": "drawn",
                "note": "Four static dimensions: hazard, exposure, sensitivity, adaptive_capacity.",
            },
            {
                "panel": "c",
                "input": str(SCORES_PATH.relative_to(ROOT)),
                "status": "drawn",
                "note": (
                    f"Static resilience score range: {scores['resilience_score'].min():.3f}-"
                    f"{scores['resilience_score'].max():.3f}; boundary legend below map frame and colorbar aligned below legend."
                ),
            },
            {
                "panel": "d",
                "input": str(MISSING_SENSITIVITY_PATH.relative_to(ROOT)),
                "status": "drawn",
                "note": (
                    f"{len(sensitivity)} dropped-indicator sensitivity rows; top 8 displayed as "
                    "tornado-lollipop plot with mean, IQR, 5-95% range, and mean rank-delta labels."
                ),
            },
        ]
    )
    audit.to_csv(AUDIT_PATH, index=False)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    joined, scores, sensitivity, metadata = load_inputs()

    plt.rcParams.update(
        {
            "font.family": "Times New Roman",
            "axes.labelcolor": "#222222",
            "axes.edgecolor": "#333333",
            "xtick.color": "#222222",
            "ytick.color": "#222222",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig = plt.figure(figsize=(7.2, 7.6), dpi=300, constrained_layout=True)
    grid = fig.add_gridspec(2, 2, width_ratios=[1.08, 1.0], height_ratios=[1.0, 1.05])

    ax_a = fig.add_subplot(grid[0, 0])
    ax_b = fig.add_subplot(grid[0, 1])
    ax_c = fig.add_subplot(grid[1, 0])
    ax_d = fig.add_subplot(grid[1, 1])

    plot_boundary_panel(ax_a, joined)
    plot_dimension_panel(ax_b, scores)
    plot_resilience_map_panel(ax_c, joined)
    plot_sensitivity_panel(ax_d, sensitivity, metadata)

    fig.suptitle(
        "Yangtze static benchmark outputs generated by HydroResKit",
        fontsize=11,
        fontweight="bold",
        color="#222222",
    )
    fig.savefig(PNG_PATH, dpi=300, bbox_inches="tight")
    fig.savefig(PDF_PATH, bbox_inches="tight")
    plt.close(fig)

    write_audit(scores, joined, sensitivity)
    print(f"Wrote {PNG_PATH}")
    print(f"Wrote {PDF_PATH}")
    print(f"Wrote {AUDIT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Could not draw Fig. 2: {exc}", file=sys.stderr)
        raise

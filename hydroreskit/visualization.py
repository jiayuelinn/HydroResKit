"""Visualization helpers for HydroResKit demo outputs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


DIMENSION_COLORS = {
    "hazard": "#D95F02",
    "exposure": "#7570B3",
    "sensitivity": "#1B9E77",
    "adaptive_capacity": "#E6AB02",
    "unknown": "#999999",
}

DIMENSION_LABELS = {
    "hazard": "Hazard",
    "exposure": "Exposure",
    "sensitivity": "Sensitivity",
    "adaptive_capacity": "Adaptive capacity",
    "unknown": "Unknown",
}

DIMENSION_PREFIXES = {
    "h": "hazard",
    "e": "exposure",
    "s": "sensitivity",
    "a": "adaptive_capacity",
}


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError("Visualization requires matplotlib.") from exc
    return plt


def _save(fig, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, bbox_inches="tight")


def plot_workflow(output_path: str | Path) -> None:
    """Plot a compact HydroResKit workflow diagram."""
    plt = _require_matplotlib()
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.axis("off")

    boxes = [
        ("Open data\nHydroBASINS, ERA5,\nMODIS, JRC, GHSL", 0.06, 0.62),
        ("Adapters\nboundary, raster,\ntime series, tabular", 0.28, 0.62),
        ("Schema\nhazard, exposure,\nsensitivity, capacity,\nrecovery", 0.50, 0.62),
        ("Assessment engine\nnormalization, weights,\naggregation", 0.72, 0.62),
        ("Diagnostics\nmissingness, ranks,\ncontributions,\nuncertainty", 0.72, 0.18),
        ("Outputs\nscores, tables,\nfigures, provenance", 0.50, 0.18),
        ("Audit layer\nchecksums, source,\nprocessing records", 0.28, 0.18),
    ]
    for text, x, y in boxes:
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=9.5,
            bbox=dict(boxstyle="round,pad=0.45", fc="#F7F9FB", ec="#2F4F4F", lw=1.1),
            transform=ax.transAxes,
        )

    arrows = [
        ((0.17, 0.62), (0.23, 0.62)),
        ((0.39, 0.62), (0.45, 0.62)),
        ((0.61, 0.62), (0.67, 0.62)),
        ((0.72, 0.52), (0.72, 0.30)),
        ((0.66, 0.18), (0.57, 0.18)),
        ((0.44, 0.18), (0.35, 0.18)),
        ((0.28, 0.30), (0.28, 0.52)),
    ]
    for start, end in arrows:
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            xycoords="axes fraction",
            arrowprops=dict(arrowstyle="->", lw=1.2, color="#2F4F4F"),
        )
    ax.set_title("HydroResKit workflow", fontsize=13, pad=12)
    _save(fig, output_path)
    plt.close(fig)


def plot_dimension_heatmap(scores: pd.DataFrame, output_path: str | Path) -> None:
    """Plot dimension scores by unit as a heatmap-like table."""
    plt = _require_matplotlib()
    dimensions = [
        col
        for col in ["hazard", "exposure", "sensitivity", "adaptive_capacity", "recovery"]
        if col in scores.columns
    ]
    data = scores[dimensions]
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    image = ax.imshow(data.to_numpy(), aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    ax.set_xticks(range(len(dimensions)))
    ax.set_xticklabels(dimensions, rotation=30, ha="right")
    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels(data.index)
    ax.set_title("Dimension scores by demo unit")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.03, label="score")
    _save(fig, output_path)
    plt.close(fig)


def plot_resilience_rank(scores: pd.DataFrame, output_path: str | Path) -> None:
    """Plot final resilience scores sorted by rank."""
    plt = _require_matplotlib()
    data = scores.sort_values("resilience_score", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.barh(data.index, data["resilience_score"], color="#4C78A8")
    ax.set_xlim(0, 1)
    ax.set_xlabel("resilience score")
    ax.set_title("Demo resilience scores")
    _save(fig, output_path)
    plt.close(fig)


def plot_weighting_comparison(comparison: pd.DataFrame, output_path: str | Path) -> None:
    """Plot score ranges across weighting methods."""
    plt = _require_matplotlib()
    data = comparison.sort_values("score_range", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.barh(data["unit_id"], data["score_range"], color="#F58518")
    ax.set_xlabel("score range across weighting methods")
    ax.set_title("Sensitivity to weighting method")
    _save(fig, output_path)
    plt.close(fig)


def _infer_dimension(indicator_id: str) -> str:
    prefix = str(indicator_id).split("_", maxsplit=1)[0]
    return DIMENSION_PREFIXES.get(prefix, "unknown")


def _format_indicator_label(indicator_id: str, label_map: dict[str, str] | None = None) -> str:
    if label_map and indicator_id in label_map:
        return label_map[indicator_id]
    text = str(indicator_id)
    if "_" in text and text.split("_", maxsplit=1)[0] in DIMENSION_PREFIXES:
        text = text.split("_", maxsplit=1)[1]
    return text.replace("_", " ").title()


def plot_missing_indicator_sensitivity(
    sensitivity: pd.DataFrame,
    output_path: str | Path,
    top_n: int = 10,
    *,
    metadata: pd.DataFrame | None = None,
    label_map: dict[str, str] | None = None,
) -> None:
    """Plot a tornado-lollipop diagnostic for missing-indicator sensitivity."""
    plt = _require_matplotlib()

    required = {"dropped_indicator", "mean_abs_score_delta"}
    missing = required.difference(sensitivity.columns)
    if missing:
        raise ValueError(f"Sensitivity table is missing required columns: {sorted(missing)}")

    data = sensitivity.nlargest(top_n, "mean_abs_score_delta").copy()
    data = data.sort_values("mean_abs_score_delta", ascending=True)

    if "dimension" in data.columns:
        dimensions = data["dimension"].fillna("unknown")
    elif metadata is not None and {"indicator_id", "dimension"}.issubset(metadata.columns):
        lookup = metadata.set_index("indicator_id")["dimension"].to_dict()
        dimensions = data["dropped_indicator"].map(lookup).fillna("unknown")
    else:
        dimensions = data["dropped_indicator"].map(_infer_dimension)
    data["dimension"] = dimensions

    mean = data["mean_abs_score_delta"].astype(float)
    p05 = data["p05_abs_score_delta"].astype(float) if "p05_abs_score_delta" in data else pd.Series(0.0, index=data.index)
    p95 = (
        data["p95_abs_score_delta"].astype(float)
        if "p95_abs_score_delta" in data
        else data.get("max_abs_score_delta", mean).astype(float)
    )
    p25 = data["p25_abs_score_delta"].astype(float) if "p25_abs_score_delta" in data else mean
    p75 = data["p75_abs_score_delta"].astype(float) if "p75_abs_score_delta" in data else mean

    y = np.arange(len(data))
    labels = [_format_indicator_label(indicator, label_map) for indicator in data["dropped_indicator"]]
    colors = [DIMENSION_COLORS.get(dimension, DIMENSION_COLORS["unknown"]) for dimension in data["dimension"]]

    plt.rcParams.update({"font.family": "Times New Roman", "pdf.fonttype": 42, "ps.fonttype": 42})
    fig_height = max(4.6, 0.42 * len(data) + 1.35)
    fig, ax = plt.subplots(figsize=(8.7, fig_height))
    ax.hlines(y, p05, p95, color="#B8B8B8", linewidth=1.1, zorder=1)
    ax.hlines(y, p25, p75, color="#666666", linewidth=3.0, zorder=2)
    ax.scatter(mean, y, s=46, color=colors, edgecolor="#222222", linewidth=0.45, zorder=3)

    x_right = max(float(p95.max()), float(mean.max()))
    if "mean_abs_rank_delta" in data.columns:
        for yi, value in zip(y, data["mean_abs_rank_delta"]):
            ax.text(
                x_right * 1.04,
                yi,
                f"rank chg {float(value):.1f}",
                va="center",
                ha="left",
                fontsize=7,
                color="#555555",
            )
    elif "affected_basin_pct" in data.columns:
        for yi, value in zip(y, data["affected_basin_pct"]):
            ax.text(
                x_right * 1.04,
                yi,
                f"affected {float(value):.0f}%",
                va="center",
                ha="left",
                fontsize=7,
                color="#555555",
            )

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, x_right * 1.34)
    ax.set_xlabel("Absolute score change after dropping indicator")
    ax.set_title("Dropped-indicator sensitivity")
    ax.text(
        0.01,
        0.985,
        "dot = mean; dark line = IQR; light line = 5-95%",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7,
        color="#555555",
    )
    ax.grid(axis="x", color="#DDDDDD", linewidth=0.6, linestyle="--")
    ax.tick_params(axis="both", labelsize=8, direction="out")
    ax.spines[["top", "right"]].set_visible(False)

    legend_dimensions = [dimension for dimension in DIMENSION_COLORS if dimension in set(data["dimension"])]
    handles = [
        plt.Line2D(
            [0],
            [0],
            marker="s",
            color="none",
            markerfacecolor=DIMENSION_COLORS[dimension],
            markeredgecolor="none",
            markersize=7,
            label=DIMENSION_LABELS[dimension],
        )
        for dimension in legend_dimensions
    ]
    if handles:
        ax.legend(
            handles=handles,
            loc="lower right",
            fontsize=7,
            frameon=True,
            framealpha=0.92,
            edgecolor="#CCCCCC",
            ncol=2,
            handlelength=1.0,
            columnspacing=0.9,
        )
    _save(fig, output_path)
    plt.close(fig)


def plot_boundary_map(boundaries_path: str | Path, output_path: str | Path, *, title: str = "Prepared basin units") -> None:
    """Plot a simple basin boundary map from a prepared vector layer."""
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise ImportError("Boundary maps require geopandas.") from exc

    plt = _require_matplotlib()
    gdf = gpd.read_file(boundaries_path)
    fig, ax = plt.subplots(figsize=(8, 5.5))
    gdf.plot(ax=ax, facecolor="#D8E8F2", edgecolor="#2F4F4F", linewidth=0.25)
    boundary = gdf.dissolve()
    boundary.boundary.plot(ax=ax, color="#1F2933", linewidth=0.9)
    ax.set_title(title)
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_aspect("equal")
    _save(fig, output_path)
    plt.close(fig)


def plot_score_map(
    boundaries_path: str | Path,
    scores_path: str | Path,
    output_path: str | Path,
    *,
    id_column: str = "HYBAS_ID",
    score_column: str = "resilience_score",
    title: str = "Resilience score map",
) -> None:
    """Plot a choropleth score map by joining score rows to basin boundaries."""
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise ImportError("Score maps require geopandas.") from exc

    plt = _require_matplotlib()
    boundaries = gpd.read_file(boundaries_path)
    scores = pd.read_csv(scores_path)
    if id_column not in scores.columns:
        raise ValueError(f"Score table is missing ID column: {id_column}")
    if score_column not in scores.columns:
        raise ValueError(f"Score table is missing score column: {score_column}")

    boundaries[id_column] = boundaries[id_column].astype(str)
    scores[id_column] = scores[id_column].astype(str)
    merged = boundaries.merge(scores[[id_column, score_column]], on=id_column, how="left")

    fig, ax = plt.subplots(figsize=(8, 5.5))
    merged.plot(
        ax=ax,
        column=score_column,
        cmap="YlGnBu",
        linewidth=0.2,
        edgecolor="#334155",
        legend=True,
        missing_kwds={"color": "#F3F4F6", "edgecolor": "#CBD5E1", "hatch": "///", "label": "missing"},
    )
    merged.dissolve().boundary.plot(ax=ax, color="#1F2933", linewidth=0.9)
    ax.set_title(title)
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_aspect("equal")
    _save(fig, output_path)
    plt.close(fig)


def plot_uncertainty_map(
    boundaries_path: str | Path,
    uncertainty_path: str | Path,
    output_path: str | Path,
    *,
    id_column: str = "HYBAS_ID",
    uncertainty_column: str = "score_range",
    title: str = "Uncertainty map",
) -> None:
    """Plot a choropleth uncertainty map by joining diagnostics to boundaries."""
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise ImportError("Uncertainty maps require geopandas.") from exc

    plt = _require_matplotlib()
    boundaries = gpd.read_file(boundaries_path)
    uncertainty = pd.read_csv(uncertainty_path)
    if id_column not in uncertainty.columns:
        raise ValueError(f"Uncertainty table is missing ID column: {id_column}")
    if uncertainty_column not in uncertainty.columns:
        raise ValueError(f"Uncertainty table is missing column: {uncertainty_column}")

    boundaries[id_column] = boundaries[id_column].astype(str)
    uncertainty[id_column] = uncertainty[id_column].astype(str)
    merged = boundaries.merge(uncertainty[[id_column, uncertainty_column]], on=id_column, how="left")

    fig, ax = plt.subplots(figsize=(8, 5.5))
    merged.plot(
        ax=ax,
        column=uncertainty_column,
        cmap="YlOrRd",
        linewidth=0.2,
        edgecolor="#334155",
        legend=True,
        missing_kwds={"color": "#F3F4F6", "edgecolor": "#CBD5E1", "hatch": "///", "label": "missing"},
    )
    merged.dissolve().boundary.plot(ax=ax, color="#1F2933", linewidth=0.9)
    ax.set_title(title)
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_aspect("equal")
    _save(fig, output_path)
    plt.close(fig)

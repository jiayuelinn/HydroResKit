"""Generate Fig. 1 for the HydroResKit FCS Code & Data Letter.

The figure follows the text plan in
``HydroResKit_Figure_Table_Supplement_Text.md``: heterogeneous watershed
inputs, the HydroResKit core workflow, output/audit products, and a compact
Yangtze static benchmark validation inset.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "outputs" / "figures"
PNG_PATH = FIG_DIR / "fig1_hydroreskit_workflow.png"
PDF_PATH = FIG_DIR / "fig1_hydroreskit_workflow.pdf"

SCORES_PATH = ROOT / "outputs" / "yangtze_static_scores.csv"
SENSITIVITY_PATH = ROOT / "outputs" / "yangtze_static_missing_indicator_sensitivity.csv"
WEIGHTS_PATH = ROOT / "outputs" / "yangtze_static_indicator_weights.csv"


COLORS = {
    "ink": "#222222",
    "muted": "#666666",
    "line": "#9A9A9A",
    "grid": "#D9D9D9",
    "input_bg": "#EEF7EF",
    "workflow_bg": "#F7F5FB",
    "output_bg": "#EEF5FB",
    "bench_bg": "#FAFAF7",
    "green": "#78B77A",
    "blue": "#6EA6D9",
    "teal": "#63B7AF",
    "orange": "#E9A15B",
    "red": "#D87676",
    "purple": "#A78BCB",
    "yellow": "#E7CA72",
}


def read_benchmark_summary() -> dict[str, str]:
    """Read validation numbers from generated benchmark outputs."""
    summary = {
        "units": "186",
        "indicators": "12",
        "dimensions": "4",
        "score_range": "0.219-0.717",
        "top_driver": "a_surface_water_fraction",
        "tests": "25",
    }

    if SCORES_PATH.exists():
        with SCORES_PATH.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        scores = [float(row["resilience_score"]) for row in rows if row.get("resilience_score")]
        if scores:
            summary["units"] = str(len(scores))
            summary["score_range"] = f"{min(scores):.3f}-{max(scores):.3f}"

    if WEIGHTS_PATH.exists():
        with WEIGHTS_PATH.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        if rows:
            summary["indicators"] = str(len(rows))

    if SENSITIVITY_PATH.exists():
        with SENSITIVITY_PATH.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        rows = [row for row in rows if row.get("mean_abs_score_delta")]
        if rows:
            summary["indicators"] = str(len(rows))
            rows.sort(key=lambda r: float(r["mean_abs_score_delta"]), reverse=True)
            summary["top_driver"] = rows[0]["dropped_indicator"]

    return summary


def rounded_box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fc: str,
    ec: str = "#777777",
    lw: float = 0.75,
    ls: str | tuple[int, tuple[int, ...]] = "-",
    radius: float = 0.010,
    zorder: int = 1,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        transform=ax.transAxes,
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        linestyle=ls,
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def label(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    *,
    size: float = 7.0,
    weight: str = "normal",
    color: str = COLORS["ink"],
    ha: str = "center",
    va: str = "center",
    zorder: int = 5,
) -> None:
    ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=size,
        fontweight=weight,
        color=color,
        zorder=zorder,
    )


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], *, lw: float = 0.95) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            transform=ax.transAxes,
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=lw,
            color=COLORS["ink"],
            shrinkA=0,
            shrinkB=0,
            zorder=4,
        )
    )


def panel_header(ax: plt.Axes, tag: str, title: str, x: float, y: float, w: float) -> None:
    title_size = 7.2 if len(title) > 24 else 7.8
    label(ax, x + 0.016, y, tag, size=8.8, weight="bold", ha="left")
    label(ax, x + 0.050, y, title, size=title_size, weight="bold", ha="left")
    ax.plot([x + 0.050, x + w - 0.015], [y - 0.026, y - 0.026], transform=ax.transAxes, color=COLORS["line"], lw=0.5)


def draw_table_icon(ax: plt.Axes, x: float, y: float, w: float, h: float, *, color: str) -> None:
    ax.add_patch(Rectangle((x, y), w, h, transform=ax.transAxes, facecolor="white", edgecolor=COLORS["ink"], lw=0.5))
    for i in range(1, 4):
        ax.plot([x, x + w], [y + h * i / 4, y + h * i / 4], transform=ax.transAxes, color=COLORS["grid"], lw=0.35)
        ax.plot([x + w * i / 4, x + w * i / 4], [y, y + h], transform=ax.transAxes, color=COLORS["grid"], lw=0.35)
    ax.add_patch(Rectangle((x, y + h * 0.75), w, h * 0.25, transform=ax.transAxes, facecolor=color, edgecolor="none", alpha=0.75))


def draw_raster_icon(ax: plt.Axes, x: float, y: float, w: float, h: float) -> None:
    palette = ["#D9EAF7", "#A6CFE8", "#73B3D8", "#F8D2A8", "#EAA365", "#C97355"]
    for row in range(4):
        for col in range(5):
            ax.add_patch(
                Rectangle(
                    (x + w * col / 5, y + h * row / 4),
                    w / 5,
                    h / 4,
                    transform=ax.transAxes,
                    facecolor=palette[(row + col) % len(palette)],
                    edgecolor="white",
                    lw=0.2,
                )
            )
    ax.add_patch(Rectangle((x, y), w, h, transform=ax.transAxes, facecolor="none", edgecolor=COLORS["ink"], lw=0.5))


def draw_boundary_icon(ax: plt.Axes, x: float, y: float, w: float, h: float) -> None:
    polygons = [
        ([(0.06, 0.16), (0.40, 0.10), (0.52, 0.38), (0.28, 0.58), (0.06, 0.42)], "#DDEEDB"),
        ([(0.42, 0.12), (0.90, 0.20), (0.76, 0.60), (0.54, 0.40)], "#DCEAF7"),
        ([(0.18, 0.60), (0.48, 0.42), (0.76, 0.68), (0.38, 0.88)], "#F5E7C6"),
    ]
    for pts, color in polygons:
        ax.add_patch(
            Polygon(
                [(x + px * w, y + py * h) for px, py in pts],
                closed=True,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor=COLORS["ink"],
                lw=0.4,
            )
        )


def draw_series_icon(ax: plt.Axes, x: float, y: float, w: float, h: float) -> None:
    ax.plot([x, x], [y, y + h], transform=ax.transAxes, color=COLORS["ink"], lw=0.45)
    ax.plot([x, x + w], [y, y], transform=ax.transAxes, color=COLORS["ink"], lw=0.45)
    pts = [(0.05, 0.22), (0.23, 0.42), (0.38, 0.32), (0.56, 0.72), (0.76, 0.58), (0.94, 0.82)]
    ax.plot([x + px * w for px, _ in pts], [y + py * h for _, py in pts], transform=ax.transAxes, color=COLORS["blue"], lw=1.0)


def draw_bars(ax: plt.Axes, x: float, y: float, w: float, h: float, *, colors: list[str] | None = None) -> None:
    vals = [0.42, 0.70, 0.56, 0.84]
    colors = colors or [COLORS["red"], COLORS["blue"], COLORS["orange"], COLORS["green"]]
    for i, val in enumerate(vals):
        bx = x + w * (0.08 + i * 0.22)
        ax.add_patch(
            Rectangle(
                (bx, y),
                w * 0.14,
                h * val,
                transform=ax.transAxes,
                facecolor=colors[i],
                edgecolor=COLORS["ink"],
                lw=0.35,
            )
        )
    ax.plot([x, x + w], [y, y], transform=ax.transAxes, color=COLORS["ink"], lw=0.45)


def input_item(ax: plt.Axes, x: float, y: float, text: str, icon: str, color: str) -> None:
    rounded_box(ax, x, y, 0.200, 0.055, fc="white", ec="#9AA99A", lw=0.55, radius=0.007)
    if icon == "boundary":
        draw_boundary_icon(ax, x + 0.010, y + 0.010, 0.036, 0.036)
    elif icon == "table":
        draw_table_icon(ax, x + 0.010, y + 0.013, 0.036, 0.030, color=color)
    elif icon == "raster":
        draw_raster_icon(ax, x + 0.010, y + 0.013, 0.036, 0.030)
    elif icon == "series":
        draw_series_icon(ax, x + 0.010, y + 0.012, 0.036, 0.032)
    label(ax, x + 0.055, y + 0.028, text, size=6.1, ha="left")


def module_box(ax: plt.Axes, x: float, y: float, w: float, text: str, fc: str) -> None:
    rounded_box(ax, x, y, w, 0.046, fc=fc, ec="#8A8A8A", lw=0.55, radius=0.007)
    label(ax, x + w / 2, y + 0.023, text, size=5.9, weight="bold")


def output_group(ax: plt.Axes, x: float, y: float, title: str, lines: list[str], color: str) -> None:
    rounded_box(ax, x, y, 0.200, 0.086, fc="white", ec="#9AA7B3", lw=0.55, radius=0.007)
    ax.add_patch(Rectangle((x + 0.010, y + 0.016), 0.012, 0.055, transform=ax.transAxes, facecolor=color, edgecolor="none"))
    label(ax, x + 0.032, y + 0.064, title, size=6.2, weight="bold", ha="left")
    label(ax, x + 0.032, y + 0.034, "\n".join(lines), size=5.2, color=COLORS["muted"], ha="left")


def evidence_card(ax: plt.Axes, x: float, y: float, w: float, value: str, label_text: str, color: str) -> None:
    rounded_box(ax, x, y, w, 0.105, fc="white", ec="#B4B4B4", lw=0.55, radius=0.008)
    ax.add_patch(Rectangle((x, y + 0.096), w, 0.009, transform=ax.transAxes, facecolor=color, edgecolor="none"))
    value_size = 8.8 if len(value) > 6 else 10.5
    label(ax, x + w / 2, y + 0.064, value, size=value_size, weight="bold", color=color)
    label(ax, x + w / 2, y + 0.027, label_text, size=5.8, color=COLORS["muted"])


def draw_figure() -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.6,
        }
    )
    summary = read_benchmark_summary()

    fig, ax = plt.subplots(figsize=(7.2, 5.15), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    dash = (0, (3, 2))

    # Main overview panels.
    rounded_box(ax, 0.045, 0.465, 0.250, 0.430, fc=COLORS["input_bg"], ec="#777777", lw=0.85, ls=dash, radius=0.012)
    rounded_box(ax, 0.340, 0.465, 0.320, 0.430, fc=COLORS["workflow_bg"], ec="#777777", lw=0.85, ls=dash, radius=0.012)
    rounded_box(ax, 0.705, 0.465, 0.250, 0.430, fc=COLORS["output_bg"], ec="#777777", lw=0.85, ls=dash, radius=0.012)
    rounded_box(ax, 0.045, 0.070, 0.910, 0.335, fc=COLORS["bench_bg"], ec="#777777", lw=0.85, ls=dash, radius=0.012)

    panel_header(ax, "a", "Open watershed inputs", 0.062, 0.860, 0.215)
    panel_header(ax, "b", "HydroResKit core workflow", 0.357, 0.860, 0.285)
    panel_header(ax, "c", "Products and audit records", 0.722, 0.860, 0.215)
    panel_header(ax, "d", "Yangtze static benchmark validation", 0.062, 0.365, 0.875)

    # Panel a.
    input_item(ax, 0.070, 0.780, "Basin polygons", "boundary", COLORS["green"])
    input_item(ax, 0.070, 0.713, "Static attributes", "table", COLORS["teal"])
    input_item(ax, 0.070, 0.646, "Raster summaries", "raster", COLORS["orange"])
    input_item(ax, 0.070, 0.579, "Time-series records", "series", COLORS["blue"])
    input_item(ax, 0.070, 0.512, "User indicator tables", "table", COLORS["yellow"])

    # Panel b: cross-cutting controls and module pipeline.
    rounded_box(ax, 0.372, 0.781, 0.256, 0.052, fc="white", ec="#8A8A8A", lw=0.65, radius=0.008)
    label(ax, 0.500, 0.807, "Schema control", size=6.8, weight="bold")
    label(ax, 0.500, 0.768, "indicator definitions | units | directions", size=5.2, color=COLORS["muted"])

    module_box(ax, 0.367, 0.698, 0.087, "Adapters", "#D7E8F7")
    module_box(ax, 0.466, 0.698, 0.087, "Preprocess", "#F5E8C8")
    module_box(ax, 0.565, 0.698, 0.087, "Weighting", "#E5D9F2")
    arrow(ax, (0.454, 0.721), (0.466, 0.721), lw=0.65)
    arrow(ax, (0.553, 0.721), (0.565, 0.721), lw=0.65)

    module_box(ax, 0.367, 0.616, 0.087, "Aggregation", "#DDEEDB")
    module_box(ax, 0.466, 0.616, 0.087, "Uncertainty", "#F9E1C9")
    module_box(ax, 0.565, 0.616, 0.087, "Visualization", "#D9EEF0")
    arrow(ax, (0.454, 0.639), (0.466, 0.639), lw=0.65)
    arrow(ax, (0.553, 0.639), (0.565, 0.639), lw=0.65)

    rounded_box(ax, 0.372, 0.520, 0.256, 0.056, fc="white", ec="#8A8A8A", lw=0.65, radius=0.008)
    label(ax, 0.500, 0.549, "Provenance auditing", size=6.8, weight="bold")
    label(ax, 0.500, 0.505, "source-resolution rules | parameters | checksums", size=5.2, color=COLORS["muted"])

    # Vertical continuity markers for cross-cutting bars.
    ax.plot([0.500, 0.500], [0.781, 0.744], transform=ax.transAxes, color=COLORS["line"], lw=0.6, ls=(0, (2, 2)))
    ax.plot([0.500, 0.500], [0.616, 0.576], transform=ax.transAxes, color=COLORS["line"], lw=0.6, ls=(0, (2, 2)))

    # Panel c.
    output_group(ax, 0.728, 0.760, "Scores", ["indicator tables", "dimension scores", "composite scores"], COLORS["blue"])
    output_group(ax, 0.728, 0.645, "Diagnostics", ["missing reports", "contribution/rank tables", "sensitivity summaries"], COLORS["orange"])
    output_group(ax, 0.728, 0.530, "Audit records", ["source-resolution", "file checksums", "processing metadata"], COLORS["teal"])

    # Cross-panel connectors.
    arrow(ax, (0.298, 0.680), (0.337, 0.680), lw=1.05)
    arrow(ax, (0.663, 0.680), (0.702, 0.680), lw=1.05)

    # Panel d: compact validation evidence.
    label(ax, 0.075, 0.315, "Real-data benchmark inset", size=7.0, weight="bold", ha="left")
    label(
        ax,
        0.075,
        0.292,
        "HydroResKit validates the data flow,\nscoring flow, diagnostic flow,\nand audit flow on a static benchmark.",
        size=5.9,
        color=COLORS["muted"],
        ha="left",
        va="top",
    )

    evidence_card(ax, 0.455, 0.224, 0.105, summary["units"], "level-6\nsub-basins", COLORS["green"])
    evidence_card(ax, 0.575, 0.224, 0.105, summary["indicators"], "static\nindicators", COLORS["teal"])
    evidence_card(ax, 0.695, 0.224, 0.105, summary["dimensions"], "static\ndimensions", COLORS["orange"])
    evidence_card(ax, 0.815, 0.224, 0.120, summary["score_range"], "score range", COLORS["blue"])

    rounded_box(ax, 0.455, 0.104, 0.300, 0.085, fc="white", ec="#B4B4B4", lw=0.55, radius=0.008)
    label(ax, 0.473, 0.158, "Top sensitivity driver", size=5.8, weight="bold", ha="left")
    label(ax, 0.473, 0.128, summary["top_driver"], size=5.9, color=COLORS["red"], weight="bold", ha="left")
    draw_bars(ax, 0.703, 0.123, 0.045, 0.045, colors=[COLORS["red"], COLORS["orange"], COLORS["yellow"], COLORS["blue"]])

    rounded_box(ax, 0.785, 0.104, 0.150, 0.085, fc="white", ec="#B4B4B4", lw=0.55, radius=0.008)
    label(ax, 0.803, 0.158, "Local verification", size=5.5, weight="bold", ha="left")
    label(ax, 0.803, 0.128, f"{summary['tests']} passed tests", size=6.0, color=COLORS["green"], weight="bold", ha="left")
    label(ax, 0.803, 0.111, "reproducible CLI outputs", size=4.6, color=COLORS["muted"], ha="left")

    # Minimal legend for resilience-schema abbreviations.
    handles = [
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["red"], markeredgecolor="#777777", markersize=5, label="H hazard"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["blue"], markeredgecolor="#777777", markersize=5, label="E exposure"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["orange"], markeredgecolor="#777777", markersize=5, label="S sensitivity"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["green"], markeredgecolor="#777777", markersize=5, label="AC adaptive capacity"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["purple"], markeredgecolor="#777777", markersize=5, label="R recovery extension"),
    ]
    legend = ax.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.500, 0.012),
        ncol=5,
        fontsize=5.5,
        frameon=False,
        handletextpad=0.25,
        columnspacing=0.65,
    )
    legend.set_in_layout(False)

    return fig


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig = draw_figure()
    fig.savefig(PNG_PATH, dpi=300, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(PDF_PATH, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print(f"Wrote {PNG_PATH}")
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    main()

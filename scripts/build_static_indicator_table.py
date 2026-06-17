"""Build the resolved static indicator table for a HydroResKit demo."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hydroreskit.adapters.source_resolution import build_resolved_indicator_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a resolved multi-source static indicator table.")
    parser.add_argument("config", help="YAML config describing source tables, priority, and outputs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    merged, resolution = build_resolved_indicator_table(args.config)
    print(f"Built static indicator table from {args.config}")
    print(f"Rows: {len(merged)}; columns: {len(merged.columns)}")
    if not resolution.empty:
        print(f"Resolved/reported {len(resolution)} schema indicators")


if __name__ == "__main__":
    main()

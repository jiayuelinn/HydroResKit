"""Build a first real indicator table from prepared HydroBASINS boundaries."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hydroreskit.adapters.boundary import read_boundaries
from hydroreskit.adapters.hydrobasins import (
    derive_hydrobasins_attribute_indicators,
    hydrobasins_attribute_indicator_metadata,
)
from hydroreskit.adapters.tabular import write_indicator_table
from hydroreskit.provenance import FileAuditRecord, append_file_audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Derive schema-aligned HydroResKit indicators from HydroBASINS attributes."
    )
    parser.add_argument("--boundaries", required=True, help="Prepared HydroBASINS boundary file.")
    parser.add_argument("--output", required=True, help="Output indicator CSV or Parquet path.")
    parser.add_argument("--id-column", default="HYBAS_ID", help="Boundary ID column.")
    parser.add_argument(
        "--metadata-output",
        default="outputs/hydrobasins_attribute_indicator_metadata.csv",
        help="Output CSV describing derived indicator formulas and caveats.",
    )
    parser.add_argument("--audit", default="outputs/file_audit.csv", help="Audit CSV output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    boundaries = read_boundaries(args.boundaries, id_column=args.id_column)
    indicators = derive_hydrobasins_attribute_indicators(boundaries, id_column=args.id_column)
    write_indicator_table(
        indicators,
        args.output,
        unit_id_column=args.id_column,
        audit_path=args.audit,
        source_dataset="HydroBASINS",
        processing_step="build_hydrobasins_attribute_indicators",
        notes=(
            "Schema-aligned smoke-test indicator h_flood_prone_terrain=log1p(UP_AREA); "
            "auxiliary HydroBASINS attributes retained for audit."
        ),
    )

    metadata_path = Path(args.metadata_output)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    hydrobasins_attribute_indicator_metadata().to_csv(metadata_path, index=False)
    append_file_audit(
        FileAuditRecord.create(
            metadata_path,
            role="indicator_metadata",
            source_dataset="HydroBASINS",
            processing_step="build_hydrobasins_attribute_indicators_metadata",
            notes="Formula and caveat metadata for the first real HydroBASINS-derived indicator.",
        ),
        args.audit,
    )

    print(f"Wrote {len(indicators)} HydroBASINS-derived indicator rows -> {args.output}")
    print(f"Wrote indicator metadata -> {metadata_path}")


if __name__ == "__main__":
    main()

"""Provenance records for derived indicators."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from hydroreskit.cache import file_metadata


@dataclass
class ProvenanceRecord:
    indicator_id: str
    source_dataset: str
    source_url: str
    source_version: str
    processing_step: str
    aggregation_method: str
    spatial_unit: str
    temporal_window: str
    created_at: str
    notes: str = ""

    @classmethod
    def create(cls, **kwargs: Any) -> "ProvenanceRecord":
        return cls(created_at=datetime.now(timezone.utc).isoformat(), **kwargs)


def write_provenance(records: list[ProvenanceRecord], path: str | Path) -> None:
    """Write provenance records to CSV."""
    rows = [asdict(record) for record in records]
    pd.DataFrame(rows).to_csv(path, index=False)


@dataclass
class FileAuditRecord:
    path: str
    role: str
    source_dataset: str
    processing_step: str
    bytes: int
    sha256: str
    created_at: str
    notes: str = ""

    @classmethod
    def create(
        cls,
        path: str | Path,
        *,
        role: str,
        source_dataset: str,
        processing_step: str,
        notes: str = "",
    ) -> "FileAuditRecord":
        metadata = file_metadata(path)
        return cls(
            path=metadata["path"],
            role=role,
            source_dataset=source_dataset,
            processing_step=processing_step,
            bytes=metadata["bytes"],
            sha256=metadata["sha256"],
            created_at=datetime.now(timezone.utc).isoformat(),
            notes=notes,
        )


def write_file_audit(records: list[FileAuditRecord], path: str | Path) -> None:
    """Write file audit records to CSV."""
    rows = [asdict(record) for record in records]
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)


def append_file_audit(record: FileAuditRecord, path: str | Path) -> None:
    """Append one file audit record to CSV."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    row = pd.DataFrame([asdict(record)])
    if output.exists():
        row.to_csv(output, mode="a", header=False, index=False)
    else:
        row.to_csv(output, index=False)

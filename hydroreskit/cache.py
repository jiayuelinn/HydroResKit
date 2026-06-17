"""Cache and checksum helpers for auditable data workflows."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def file_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute a SHA256 checksum for a file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_metadata(path: str | Path) -> dict:
    """Return file size, checksum, and UTC modification time."""
    file_path = Path(path)
    stat = file_path.stat()
    return {
        "path": str(file_path),
        "name": file_path.name,
        "bytes": stat.st_size,
        "sha256": file_sha256(file_path),
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }


def cache_key(value: str) -> str:
    """Create a stable cache key from a URL or arbitrary source string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def cache_path(cache_dir: str | Path, source: str, suffix: str | None = None) -> Path:
    """Build a deterministic cache path for a source string."""
    parsed = urlparse(source)
    source_name = Path(parsed.path).name if parsed.path else ""
    if suffix is None:
        suffix = Path(source_name).suffix
    stem = Path(source_name).stem if source_name else "source"
    safe_stem = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in stem)
    return Path(cache_dir) / f"{safe_stem}_{cache_key(source)}{suffix or ''}"


def copy_to_cache(source_path: str | Path, cache_dir: str | Path, *, source_label: str | None = None) -> Path:
    """Copy a local file into the cache and return the cached path."""
    source = Path(source_path)
    label = source_label or str(source.resolve())
    target = cache_path(cache_dir, label, suffix=source.suffix)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or file_sha256(source) != file_sha256(target):
        shutil.copy2(source, target)
    return target


def write_metadata_json(path: str | Path, metadata: dict) -> None:
    """Write metadata as pretty JSON."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")


def read_metadata_json(path: str | Path) -> dict:
    """Read metadata JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


"""Download a source listed in a HydroResKit source manifest.

Large official datasets should be downloaded only when the user has checked
the provider terms. This helper records checksums and audit metadata.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hydroreskit.cache import file_metadata
from hydroreskit.provenance import FileAuditRecord, append_file_audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download one source from a HydroResKit source manifest.")
    parser.add_argument("source_id", help="Source ID from configs/hydrosheds_sources.yml.")
    parser.add_argument("--manifest", default="configs/hydrosheds_sources.yml")
    parser.add_argument("--output-dir", default="data_raw")
    parser.add_argument("--audit", default="outputs/file_audit.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = yaml.safe_load(Path(args.manifest).read_text(encoding="utf-8"))
    sources = manifest.get("sources", {})
    if args.source_id not in sources:
        raise ValueError(f"Unknown source_id '{args.source_id}'. Available: {sorted(sources)}")

    source = sources[args.source_id]
    url = source["url"]
    filename = Path(url).name
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    if not output_path.exists():
        print(f"Downloading {url} -> {output_path}")
        _download(url, output_path)
    else:
        print(f"Using existing file: {output_path}")

    metadata = file_metadata(output_path)
    append_file_audit(
        FileAuditRecord.create(
            output_path,
            role="raw_source",
            source_dataset=source.get("name", args.source_id),
            processing_step="download_source",
            notes=f"url={url}; sha256={metadata['sha256']}",
        ),
        args.audit,
    )
    print(f"Downloaded/audited {output_path}")
    print(f"SHA256: {metadata['sha256']}")


def _download(url: str, output_path: Path, chunk_size: int = 1024 * 1024) -> None:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 HydroResKit research downloader",
            "Accept": "application/zip,application/octet-stream,*/*",
        },
    )
    tmp_path = output_path.with_suffix(output_path.suffix + ".part")
    if tmp_path.exists():
        tmp_path.unlink()
    with urlopen(request, timeout=60) as response, tmp_path.open("wb") as file:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            file.write(chunk)
    tmp_path.replace(output_path)


if __name__ == "__main__":
    main()

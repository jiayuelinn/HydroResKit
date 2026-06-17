"""Start a Google Earth Engine export for Yangtze HydroATLAS level 6 attributes.

This script is the reproducible Python equivalent of
`scripts/gee_export_hydroatlas_yangtze_level06.js`. It starts an Earth Engine
batch export to Google Drive. After the CSV appears in Drive, download it to
`data_raw/` and run `scripts/build_hydroatlas_indicators.py`.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hydroreskit.adapters.hydroatlas import hydroatlas_required_source_columns


DEFAULT_DATASET = "WWF/HydroATLAS/v1/Basins/level06"
DEFAULT_MAIN_BAS = "4060009880"
DEFAULT_DESCRIPTION = "hydroatlas_yangtze_level06_hydroreskit"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Yangtze HydroATLAS level 6 attributes from GEE.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Earth Engine HydroATLAS FeatureCollection ID.")
    parser.add_argument("--main-basin-id", default=DEFAULT_MAIN_BAS, help="HydroATLAS MAIN_BAS value to export.")
    parser.add_argument("--main-basin-column", default="MAIN_BAS", help="HydroATLAS main basin column.")
    parser.add_argument("--id-column", default="HYBAS_ID", help="HydroBASINS/HydroATLAS unit ID column.")
    parser.add_argument("--description", default=DEFAULT_DESCRIPTION, help="Earth Engine task description.")
    parser.add_argument("--file-name-prefix", default=DEFAULT_DESCRIPTION, help="Google Drive output file prefix.")
    parser.add_argument("--drive-folder", help="Optional Google Drive folder name.")
    parser.add_argument(
        "--local-output",
        help=(
            "Download the selected FeatureCollection directly to a local CSV using "
            "FeatureCollection.getDownloadURL instead of starting a Drive export."
        ),
    )
    parser.add_argument(
        "--local-timeout",
        type=int,
        default=300,
        help="Timeout in seconds for direct local CSV download.",
    )
    parser.add_argument("--project", help="Google Cloud project for ee.Initialize(project=...).")
    parser.add_argument(
        "--authenticate",
        action="store_true",
        help="Run ee.Authenticate() before initialization. Use this for first-time setup.",
    )
    parser.add_argument(
        "--auth-mode",
        default=None,
        choices=["localhost", "notebook", "gcloud", "colab"],
        help="Optional Earth Engine authentication mode.",
    )
    parser.add_argument("--wait", action="store_true", help="Poll task status until completion/failure.")
    parser.add_argument("--poll-seconds", type=int, default=30, help="Polling interval when --wait is used.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ee = _load_ee()
    if args.authenticate:
        kwargs = {}
        if args.auth_mode:
            kwargs["auth_mode"] = args.auth_mode
        ee.Authenticate(**kwargs)

    init_kwargs = {}
    if args.project:
        init_kwargs["project"] = args.project
    ee.Initialize(**init_kwargs)

    selectors = _selectors(args.id_column, args.main_basin_column)
    collection = (
        ee.FeatureCollection(args.dataset)
        .filter(ee.Filter.eq(args.main_basin_column, int(args.main_basin_id)))
        .select(selectors)
    )
    count = collection.size().getInfo()
    print(f"Selected features: {count}")
    if count == 0:
        raise RuntimeError(
            f"No features matched {args.main_basin_column}={args.main_basin_id} in {args.dataset}"
        )

    if args.local_output:
        _download_locally(
            collection,
            selectors,
            args.local_output,
            filename=args.file_name_prefix,
            timeout=args.local_timeout,
        )
        return

    export_kwargs = {
        "collection": collection,
        "description": args.description,
        "fileNamePrefix": args.file_name_prefix,
        "fileFormat": "CSV",
        "selectors": selectors,
    }
    if args.drive_folder:
        export_kwargs["folder"] = args.drive_folder

    task = ee.batch.Export.table.toDrive(**export_kwargs)
    task.start()
    print(f"Started Earth Engine export task: {task.id}")
    print(f"Description: {args.description}")
    print("Open the Earth Engine Tasks page or Google Drive to monitor the CSV export.")

    if args.wait:
        _wait_for_task(task, poll_seconds=args.poll_seconds)


def _load_ee():
    try:
        import ee
    except ImportError as exc:
        raise SystemExit(
            "earthengine-api is not installed. Install it with: "
            "python -m pip install earthengine-api"
        ) from exc
    return ee


def _selectors(id_column: str, main_basin_column: str) -> list[str]:
    selectors = [id_column, main_basin_column]
    for column in hydroatlas_required_source_columns():
        if column not in selectors:
            selectors.append(column)
    return selectors


def _download_locally(collection, selectors: list[str], output_path: str, *, filename: str, timeout: int) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        url = collection.getDownloadURL(
            filetype="CSV",
            selectors=selectors,
            filename=filename,
        )
    except Exception as exc:
        raise RuntimeError(
            "Could not create a direct Earth Engine table download URL. "
            "Use the default Drive export mode instead."
        ) from exc

    print(f"Downloading directly from Earth Engine to {path}")
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 HydroResKit GEE downloader"})
    with urlopen(request, timeout=timeout) as response, path.open("wb") as file:
        file.write(response.read())
    print(f"Wrote local CSV: {path}")


def _wait_for_task(task, *, poll_seconds: int) -> None:
    terminal_states = {"COMPLETED", "FAILED", "CANCELLED"}
    while True:
        status = task.status()
        state = status.get("state", "UNKNOWN")
        print(f"Task state: {state}")
        if state in terminal_states:
            if state != "COMPLETED":
                print(status)
                raise RuntimeError(f"Earth Engine task ended with state: {state}")
            return
        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()

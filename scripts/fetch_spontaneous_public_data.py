from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.public_spontaneous_dataset import (
    build_public_dataset_manifest,
    stage_public_dataset_file,
    write_public_dataset_manifest,
    write_public_dataset_summary,
)
from brain.spontaneous_data_sources import get_spontaneous_dataset_source_map, get_spontaneous_dataset_sources


def _write_file_table(manifest: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "path",
                "size_bytes",
                "digest",
                "api_download_url",
                "browser_download_url",
            ],
        )
        writer.writeheader()
        for row in manifest.get("files", []):
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch public spontaneous-dataset metadata and access reports.")
    parser.add_argument("--source", default=None)
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--timeout-s", type=float, default=30.0)
    parser.add_argument("--output-prefix", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--dataset-root", default=None)
    parser.add_argument(
        "--stage",
        nargs="*",
        default=[],
        help="Optional file names to download into the dataset root. Use 'all' to stage every declared file.",
    )
    args = parser.parse_args()

    source_key = str(args.dataset or args.source or "aimon2023_dryad")
    source_map = get_spontaneous_dataset_source_map()
    if source_key not in source_map:
        raise KeyError(f"Unknown spontaneous dataset source: {source_key}")
    source = source_map[source_key]
    if args.output_dir:
        output_dir = (REPO_ROOT / Path(args.output_dir)).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_prefix = output_dir / "spontaneous_public_dataset"
    else:
        output_prefix = (REPO_ROOT / Path(args.output_prefix or "outputs/metrics/spontaneous_public_dataset")).resolve()
        output_prefix.parent.mkdir(parents=True, exist_ok=True)
        output_dir = output_prefix.parent
    dataset_root = (REPO_ROOT / Path(args.dataset_root or source.expected_local_dir)).resolve()
    dataset_root.mkdir(parents=True, exist_ok=True)

    registry_path = output_dir / "spontaneous_public_dataset_registry.json"
    registry_path.write_text(
        json.dumps([source.to_dict() for source in get_spontaneous_dataset_sources()], indent=2),
        encoding="utf-8",
    )

    manifest_timeout_s = min(float(args.timeout_s), 15.0)
    manifest = build_public_dataset_manifest(source_key, timeout_s=manifest_timeout_s)
    manifest_path = output_dir / f"{output_prefix.name}_{source_key}_manifest.json"
    write_public_dataset_manifest(manifest, manifest_path)
    file_csv_path = output_dir / f"{output_prefix.name}_{source_key}_files.csv"
    _write_file_table(manifest.to_dict(), file_csv_path)
    access_report_path = output_dir / f"{output_prefix.name}_{source_key}_access_report.json"
    access_report_path.write_text(
        json.dumps(
            {
                "source": source_key,
                "version_id": manifest.version_id,
                "access_checks": [item.to_dict() for item in manifest.access_checks],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    stage_targets = [str(item) for item in args.stage]
    if any(str(item).lower() == "all" for item in stage_targets):
        stage_targets = [entry.name for entry in source.files]
    stage_results = []
    for file_name in stage_targets:
        stage_results.append(
            stage_public_dataset_file(
                source_key,
                str(file_name),
                root_dir=dataset_root,
                timeout_s=max(float(args.timeout_s), 120.0),
            )
        )
    local_summary_path = output_dir / "local_dataset_summary.json"
    dataset_local_summary_path = dataset_root / "local_dataset_summary.json"
    write_public_dataset_summary(source_key, output_path=local_summary_path, root_dir=dataset_root)
    write_public_dataset_summary(source_key, output_path=dataset_local_summary_path, root_dir=dataset_root)
    dataset_manifest_path = dataset_root / f"{output_prefix.name}_{source_key}_manifest.json"
    write_public_dataset_manifest(manifest, dataset_manifest_path)
    dataset_access_report_path = dataset_root / f"{output_prefix.name}_{source_key}_access_report.json"
    dataset_access_report_path.write_text(
        json.dumps(
            {
                "source": source_key,
                "version_id": manifest.version_id,
                "access_checks": [item.to_dict() for item in manifest.access_checks],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "source": source_key,
                "registry_path": str(registry_path.relative_to(REPO_ROOT)),
                "manifest_path": str(manifest_path.relative_to(REPO_ROOT)),
                "file_csv_path": str(file_csv_path.relative_to(REPO_ROOT)),
                "access_report_path": str(access_report_path.relative_to(REPO_ROOT)),
                "local_summary_path": str(local_summary_path.relative_to(REPO_ROOT)),
                "dataset_root": str(dataset_root.relative_to(REPO_ROOT)),
                "dataset_local_summary_path": str(dataset_local_summary_path.relative_to(REPO_ROOT)),
                "stage_results": stage_results,
                "file_count": len(manifest.files),
                "version_id": manifest.version_id,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

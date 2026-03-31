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

from analysis.public_neural_measurement_dataset import (
    build_public_neural_measurement_manifest,
    stage_public_neural_measurement_file,
    write_public_neural_measurement_manifest,
    write_public_neural_measurement_summary,
)
from brain.public_neural_measurement_sources import (
    get_public_neural_measurement_source_map,
    get_public_neural_measurement_sources,
)


def _write_file_table(manifest: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["name", "size_bytes", "digest", "primary_download_url", "description"],
        )
        writer.writeheader()
        for row in manifest.get("files", []):
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch public neural measurement metadata and stage files.")
    parser.add_argument("--source", default="aimon2023_dryad")
    parser.add_argument("--timeout-s", type=float, default=30.0)
    parser.add_argument("--output-dir", default="outputs/metrics")
    parser.add_argument("--dataset-root", default=None)
    parser.add_argument("--stage", nargs="*", default=[], help="Optional file names to download. Use 'all' for all manifest files.")
    args = parser.parse_args()

    source_map = get_public_neural_measurement_source_map()
    if args.source not in source_map:
        raise KeyError(f"Unknown public neural measurement source: {args.source}")
    source = source_map[args.source]
    output_dir = (REPO_ROOT / Path(args.output_dir)).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_root = (REPO_ROOT / Path(args.dataset_root or source.expected_local_dir)).resolve()
    dataset_root.mkdir(parents=True, exist_ok=True)

    registry_path = output_dir / "public_neural_measurement_registry.json"
    registry_path.write_text(
        json.dumps([entry.to_dict() for entry in get_public_neural_measurement_sources()], indent=2),
        encoding="utf-8",
    )

    manifest = build_public_neural_measurement_manifest(args.source, timeout_s=min(float(args.timeout_s), 30.0))
    manifest_path = output_dir / f"public_neural_measurement_{args.source}_manifest.json"
    write_public_neural_measurement_manifest(manifest, manifest_path)
    file_csv_path = output_dir / f"public_neural_measurement_{args.source}_files.csv"
    _write_file_table(manifest.to_dict(), file_csv_path)
    access_report_path = output_dir / f"public_neural_measurement_{args.source}_access_report.json"
    access_report_path.write_text(
        json.dumps(
            {
                "source": args.source,
                "version_id": manifest.version_id,
                "resolved_landing_url": manifest.resolved_landing_url,
                "access_checks": [item.to_dict() for item in manifest.access_checks],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    stage_targets = [str(item) for item in args.stage]
    if any(str(item).lower() == "all" for item in stage_targets):
        stage_targets = [entry.name for entry in manifest.files]
    stage_results = []
    for file_name in stage_targets:
        stage_results.append(
            stage_public_neural_measurement_file(
                args.source,
                file_name,
                root_dir=dataset_root,
                timeout_s=max(float(args.timeout_s), 120.0),
            )
        )

    local_summary_path = output_dir / f"public_neural_measurement_{args.source}_local_summary.json"
    write_public_neural_measurement_summary(args.source, output_path=local_summary_path, root_dir=dataset_root)

    print(
        json.dumps(
            {
                "source": args.source,
                "registry_path": str(registry_path.relative_to(REPO_ROOT)),
                "manifest_path": str(manifest_path.relative_to(REPO_ROOT)),
                "file_csv_path": str(file_csv_path.relative_to(REPO_ROOT)),
                "access_report_path": str(access_report_path.relative_to(REPO_ROOT)),
                "local_summary_path": str(local_summary_path.relative_to(REPO_ROOT)),
                "dataset_root": str(dataset_root.relative_to(REPO_ROOT)),
                "stage_results": stage_results,
                "file_count": len(manifest.files),
                "version_id": manifest.version_id,
                "resolved_landing_url": manifest.resolved_landing_url,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

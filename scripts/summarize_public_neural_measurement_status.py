from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from brain.public_neural_measurement_sources import get_public_neural_measurement_sources


def main() -> None:
    output_dir = REPO_ROOT / "outputs" / "metrics"
    rows = []
    for source in get_public_neural_measurement_sources():
        manifest_path = output_dir / f"public_neural_measurement_{source.key}_manifest.json"
        access_report_path = output_dir / f"public_neural_measurement_{source.key}_access_report.json"
        dataset_root = REPO_ROOT / source.expected_local_dir
        local_summary_path = dataset_root / "local_dataset_summary.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
        local_summary = json.loads(local_summary_path.read_text(encoding="utf-8")) if local_summary_path.exists() else None
        staged_files = list(local_summary.get("staged_files", [])) if local_summary else []
        if local_summary and not staged_files and "files" in local_summary:
            staged_files = [row for row in local_summary.get("files", []) if row.get("exists")]
        rows.append(
            {
                "source_key": source.key,
                "repository_kind": source.repository_kind,
                "manifest_exists": manifest_path.exists(),
                "access_report_exists": access_report_path.exists(),
                "dataset_root_exists": dataset_root.exists(),
                "manifest_file_count": len(manifest.get("files", [])) if manifest else 0,
                "staged_file_count": len(staged_files),
                "dataset_root": str(dataset_root.relative_to(REPO_ROOT)),
                "local_summary_exists": local_summary_path.exists(),
                "metadata_only": bool(manifest_path.exists() and len(staged_files) == 0),
            }
        )
    json_path = output_dir / "public_neural_measurement_stage_status.json"
    csv_path = output_dir / "public_neural_measurement_stage_status.csv"
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"json_path": str(json_path.relative_to(REPO_ROOT)), "csv_path": str(csv_path.relative_to(REPO_ROOT)), "row_count": len(rows)}, indent=2))


if __name__ == "__main__":
    main()

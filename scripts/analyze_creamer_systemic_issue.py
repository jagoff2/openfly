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

from analysis.creamer_diagnosis import compare_creamer_runs, summarize_creamer_run


def _write_csv(path: Path, diagnosis: dict) -> None:
    rows: list[dict[str, object]] = []
    for metric, values in diagnosis["delta_table"].items():
        row = {"metric": metric}
        row.update(values)
        rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose the Creamer systemic issue by comparing baseline and ablated run logs.")
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--ablated-run", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--csv-output", required=True)
    args = parser.parse_args()

    baseline = summarize_creamer_run(args.baseline_run)
    ablated = summarize_creamer_run(args.ablated_run)
    diagnosis = compare_creamer_runs(baseline, ablated)

    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(diagnosis, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(Path(args.csv_output), diagnosis)


if __name__ == "__main__":
    main()

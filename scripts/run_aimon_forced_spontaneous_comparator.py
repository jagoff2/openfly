from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis.aimon_public_comparator import summarize_public_forced_vs_spontaneous_walk


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public Aimon forced-vs-spontaneous comparator.")
    parser.add_argument("--dataset-root", default="external/spontaneous/aimon2023_dryad")
    parser.add_argument(
        "--summary-path",
        default="outputs/metrics/aimon_forced_spontaneous_comparator_summary.json",
    )
    parser.add_argument(
        "--rows-path",
        default="outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv",
    )
    args = parser.parse_args()

    dataset_root = (ROOT / args.dataset_root).resolve()
    summary = summarize_public_forced_vs_spontaneous_walk(dataset_root)
    table = pd.DataFrame(summary.get("per_experiment_rows", []))
    summary_path = (ROOT / args.summary_path).resolve()
    rows_path = (ROOT / args.rows_path).resolve()
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    table.to_csv(rows_path, index=False)
    print(json.dumps({"summary_path": str(summary_path), "rows_path": str(rows_path), **summary}, indent=2))


if __name__ == "__main__":
    main()

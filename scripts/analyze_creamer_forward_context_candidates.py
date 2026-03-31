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

from analysis.creamer_forward_context import (  # noqa: E402
    compare_forward_context_candidates,
    summarize_monitor_bilateral_block_means,
)


def _write_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank Creamer forward-context candidates from a corrected baseline/ablated run pair.")
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--ablated-run", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--csv-output", required=True)
    parser.add_argument("--top-k", type=int, default=12)
    args = parser.parse_args()

    baseline = summarize_monitor_bilateral_block_means(args.baseline_run)
    ablated = summarize_monitor_bilateral_block_means(args.ablated_run)
    rows = compare_forward_context_candidates(baseline, ablated)
    summary = {
        "baseline_run": str(args.baseline_run),
        "ablated_run": str(args.ablated_run),
        "top_k": int(args.top_k),
        "top_candidates": rows[: max(1, int(args.top_k))],
        "candidate_count": len(rows),
    }

    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(Path(args.csv_output), rows)


if __name__ == "__main__":
    main()

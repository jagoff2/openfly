from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pandas as pd

from analysis.relay_target_specificity import rank_target_specific_signals


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare target and baseline relay/monitor score tables and rank target-specific candidate families.")
    parser.add_argument("--target-family", required=True)
    parser.add_argument("--baseline-family", required=True)
    parser.add_argument("--target-monitor", required=True)
    parser.add_argument("--baseline-monitor", required=True)
    parser.add_argument("--output-prefix", default="outputs/metrics/relay_target_specificity")
    parser.add_argument("--top-k", type=int, default=16)
    args = parser.parse_args()

    target_family = pd.read_csv(args.target_family)
    baseline_family = pd.read_csv(args.baseline_family)
    target_monitor = pd.read_csv(args.target_monitor)
    baseline_monitor = pd.read_csv(args.baseline_monitor)

    family_ranked = rank_target_specific_signals(
        target_table=target_family,
        baseline_table=baseline_family,
        group_column="family",
    )
    monitor_ranked = rank_target_specific_signals(
        target_table=target_monitor,
        baseline_table=baseline_monitor,
        group_column="label",
        allowed_super_classes=("central", "ascending", "visual_projection", "visual_centrifugal", "descending"),
    )

    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    family_path = output_prefix.with_name(f"{output_prefix.name}_families.csv")
    monitor_path = output_prefix.with_name(f"{output_prefix.name}_monitors.csv")
    summary_path = output_prefix.with_name(f"{output_prefix.name}_summary.json")

    family_ranked.to_csv(family_path, index=False)
    monitor_ranked.to_csv(monitor_path, index=False)

    summary = {
        "family_artifact": str(family_path),
        "monitor_artifact": str(monitor_path),
        "top_family_candidates": family_ranked.head(int(args.top_k))["family"].astype(str).tolist(),
        "top_monitor_candidates": monitor_ranked.head(int(args.top_k))["label"].astype(str).tolist(),
    }
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

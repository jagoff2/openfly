from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _load_summary(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare iterative decoding summaries across target/no-target/zero-brain conditions.")
    parser.add_argument("--target-summary", required=True)
    parser.add_argument("--no-target-summary", required=True)
    parser.add_argument("--zero-summary", required=True)
    parser.add_argument("--output-prefix", default="outputs/metrics/decoding_control_condition_comparison")
    args = parser.parse_args()

    summaries = {
        "target": _load_summary(args.target_summary),
        "no_target": _load_summary(args.no_target_summary),
        "zero_brain": _load_summary(args.zero_summary),
    }

    rows = []
    for label, summary in summaries.items():
        behavior = summary.get("behavior_diagnosis", {})
        rows.append(
            {
                "condition": label,
                "best_monitor_target_bearing_corr": summary.get("best_monitor_target_bearing_corr"),
                "forward_nonzero_fraction": behavior.get("forward_nonzero_fraction"),
                "turn_nonzero_fraction": behavior.get("turn_nonzero_fraction"),
                "right_drive_dominant_fraction": behavior.get("right_drive_dominant_fraction"),
                "left_drive_dominant_fraction": behavior.get("left_drive_dominant_fraction"),
                "top_relay_family": (summary.get("recommendations", {}).get("relay_probe_families") or [None])[0],
                "top_monitor_expansion_family": (summary.get("recommendations", {}).get("monitor_expansion_families") or [None])[0],
            }
        )

    df = pd.DataFrame(rows)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = output_prefix.with_suffix(".csv")
    json_path = output_prefix.with_suffix(".json")
    df.to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(csv_path)


if __name__ == "__main__":
    main()

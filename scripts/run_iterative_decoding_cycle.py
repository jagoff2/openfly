from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.iterative_decoding import propose_decoding_cycle


DEFAULT_CONFIG = "configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml"
DEFAULT_CAPTURE = "outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/capture_data.npz"
DEFAULT_LOG = "outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/run.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank relay/decoder candidates from a captured activation run and emit the next decoding cycle plan.")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--capture", default=DEFAULT_CAPTURE)
    parser.add_argument("--log", default=DEFAULT_LOG)
    parser.add_argument("--output-prefix", default="outputs/metrics/iterative_decoding_cycle")
    parser.add_argument("--max-brain-points", type=int, default=6000)
    parser.add_argument("--monitor-limit", type=int, default=12)
    parser.add_argument("--relay-limit", type=int, default=12)
    args = parser.parse_args()

    result = propose_decoding_cycle(
        config_path=args.config,
        capture_path=args.capture,
        log_path=args.log,
        max_brain_points=int(args.max_brain_points),
        monitor_limit=int(args.monitor_limit),
        relay_limit=int(args.relay_limit),
    )
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    family_path = output_prefix.with_name(f"{output_prefix.name}_family_scores.csv")
    family_turn_path = output_prefix.with_name(f"{output_prefix.name}_family_turn_scores.csv")
    monitor_path = output_prefix.with_name(f"{output_prefix.name}_monitor_scores.csv")
    monitor_voltage_path = output_prefix.with_name(f"{output_prefix.name}_monitor_voltage_scores.csv")
    monitor_voltage_turn_path = output_prefix.with_name(f"{output_prefix.name}_monitor_voltage_turn_scores.csv")
    expansion_path = output_prefix.with_name(f"{output_prefix.name}_monitor_expansion.csv")
    relay_path = output_prefix.with_name(f"{output_prefix.name}_relay_candidates.csv")
    relay_turn_path = output_prefix.with_name(f"{output_prefix.name}_relay_turn_candidates.csv")
    monitor_turn_path = output_prefix.with_name(f"{output_prefix.name}_monitor_turn_candidates.csv")
    summary_path = output_prefix.with_name(f"{output_prefix.name}_summary.json")

    result["tables"]["family_scores"].to_csv(family_path, index=False)
    result["tables"]["family_turn_scores"].to_csv(family_turn_path, index=False)
    result["tables"]["monitor_scores"].to_csv(monitor_path, index=False)
    result["tables"]["monitor_voltage_scores"].to_csv(monitor_voltage_path, index=False)
    result["tables"]["monitor_voltage_turn_scores"].to_csv(monitor_voltage_turn_path, index=False)
    result["tables"]["monitor_expansion"].to_csv(expansion_path, index=False)
    result["tables"]["relay_candidates"].to_csv(relay_path, index=False)
    result["tables"]["relay_turn_candidates"].to_csv(relay_turn_path, index=False)
    result["tables"]["monitor_turn_candidates"].to_csv(monitor_turn_path, index=False)

    serializable = {
        key: value
        for key, value in result.items()
        if key != "tables"
    }
    serializable["artifacts"] = {
        "family_scores": str(family_path),
        "family_turn_scores": str(family_turn_path),
        "monitor_scores": str(monitor_path),
        "monitor_voltage_scores": str(monitor_voltage_path),
        "monitor_voltage_turn_scores": str(monitor_voltage_turn_path),
        "monitor_expansion": str(expansion_path),
        "relay_candidates": str(relay_path),
        "relay_turn_candidates": str(relay_turn_path),
        "monitor_turn_candidates": str(monitor_turn_path),
    }
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(serializable, handle, indent=2)
    print(json.dumps(serializable, indent=2))


if __name__ == "__main__":
    main()

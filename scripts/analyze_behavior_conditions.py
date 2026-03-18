from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.behavior_metrics import compute_behavior_metrics, flatten_behavior_metrics, load_run_records


def _parse_condition(arg: str) -> tuple[str, str]:
    if "=" not in arg:
        raise argparse.ArgumentTypeError("condition entries must look like label=path/to/run.jsonl")
    label, path = arg.split("=", 1)
    label = label.strip()
    path = path.strip()
    if not label or not path:
        raise argparse.ArgumentTypeError("condition entries must include both label and path")
    return label, path


def _safe_float(mapping: dict[str, object], key: str) -> float:
    value = mapping.get(key)
    if value is None:
        return float("nan")
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _delta(lhs: float, rhs: float) -> float | None:
    if not pd.notna(lhs) or not pd.notna(rhs):
        return None
    return float(lhs - rhs)


def _comparison_summary(summaries: dict[str, dict[str, object]]) -> dict[str, object]:
    comparisons: dict[str, object] = {}
    target_metrics = summaries.get("target", {}).get("metrics", {}) if "target" in summaries else {}
    no_target_metrics = summaries.get("no_target", {}).get("metrics", {}) if "no_target" in summaries else {}
    zero_metrics = summaries.get("zero_brain", {}).get("metrics", {}) if "zero_brain" in summaries else {}

    if target_metrics and zero_metrics:
        target_target = dict(target_metrics.get("target_condition", {}))
        zero_target = dict(zero_metrics.get("target_condition", {}))
        target_spontaneous = dict(target_metrics.get("spontaneous_locomotion", {}))
        zero_spontaneous = dict(zero_metrics.get("spontaneous_locomotion", {}))
        comparisons["target_vs_zero_brain"] = {
            "turn_alignment_fraction_active_delta": _delta(_safe_float(target_target, "turn_alignment_fraction_active"), _safe_float(zero_target, "turn_alignment_fraction_active")),
            "turn_bearing_corr_delta": _delta(_safe_float(target_target, "turn_bearing_corr"), _safe_float(zero_target, "turn_bearing_corr")),
            "fixation_fraction_20deg_delta": _delta(_safe_float(target_target, "fixation_fraction_20deg"), _safe_float(zero_target, "fixation_fraction_20deg")),
            "bearing_reduction_rad_delta": _delta(_safe_float(target_target, "bearing_reduction_rad"), _safe_float(zero_target, "bearing_reduction_rad")),
            "locomotor_active_fraction_delta": _delta(_safe_float(target_spontaneous, "locomotor_active_fraction"), _safe_float(zero_spontaneous, "locomotor_active_fraction")),
            "controller_state_entropy_delta": _delta(_safe_float(target_spontaneous, "controller_state_entropy"), _safe_float(zero_spontaneous, "controller_state_entropy")),
        }
    if target_metrics and no_target_metrics:
        target_spontaneous = dict(target_metrics.get("spontaneous_locomotion", {}))
        no_target_spontaneous = dict(no_target_metrics.get("spontaneous_locomotion", {}))
        comparisons["target_vs_no_target"] = {
            "locomotor_active_fraction_delta": _delta(_safe_float(target_spontaneous, "locomotor_active_fraction"), _safe_float(no_target_spontaneous, "locomotor_active_fraction")),
            "controller_state_entropy_delta": _delta(_safe_float(target_spontaneous, "controller_state_entropy"), _safe_float(no_target_spontaneous, "controller_state_entropy")),
            "mean_forward_speed_delta": _delta(_safe_float(target_spontaneous, "mean_forward_speed"), _safe_float(no_target_spontaneous, "mean_forward_speed")),
            "mean_abs_turn_drive_delta": _delta(_safe_float(target_spontaneous, "mean_abs_turn_drive"), _safe_float(no_target_spontaneous, "mean_abs_turn_drive")),
        }
    return comparisons


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze target-engagement and spontaneous-locomotion structure across one or more embodied run logs.")
    parser.add_argument(
        "--condition",
        action="append",
        required=True,
        help="Labelled run log in the form label=path/to/run.jsonl. Repeat for multiple conditions.",
    )
    parser.add_argument("--output-prefix", default="outputs/metrics/behavior_condition_analysis")
    args = parser.parse_args()

    summaries: dict[str, dict[str, object]] = {}
    flat_rows: list[dict[str, object]] = []
    for raw_condition in args.condition:
        label, path = _parse_condition(raw_condition)
        metrics = compute_behavior_metrics(load_run_records(path))
        summaries[label] = {
            "log_path": str(path),
            "metrics": metrics,
        }
        flat_row = {"label": label, "log_path": str(path)}
        flat_row.update(flatten_behavior_metrics(metrics))
        flat_rows.append(flat_row)

    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = output_prefix.with_name(f"{output_prefix.name}.csv")
    json_path = output_prefix.with_name(f"{output_prefix.name}.json")

    pd.DataFrame(flat_rows).to_csv(csv_path, index=False)
    comparison_summary = _comparison_summary(summaries)
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump({"conditions": summaries, "comparisons": comparison_summary}, handle, indent=2)

    print(json.dumps({"csv": str(csv_path), "json": str(json_path), "conditions": list(summaries.keys()), "comparisons": comparison_summary}, indent=2))


if __name__ == "__main__":
    main()

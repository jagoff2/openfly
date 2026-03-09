from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]


def _nonnull_mean(values: list[float | None]) -> float | None:
    filtered = [float(value) for value in values if value is not None]
    return float(mean(filtered)) if filtered else None


def _groups_csv_for_summary(summary_path: Path) -> Path:
    candidates = [
        summary_path.with_name(summary_path.name.replace("_summary.json", "_groups.csv")),
        summary_path.with_name(summary_path.name.replace("_summary.json", "_state_groups.csv")),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No groups CSV found for {summary_path}")


def _saturation_fraction(groups_csv: Path) -> float:
    df = pd.read_csv(groups_csv)
    df = df[df["condition"] != "baseline_gray"].copy()
    if df.empty:
        return 0.0
    max_abs_rate = float(df["student_delta_rate_hz"].abs().max())
    if max_abs_rate <= 0.0:
        return 0.0
    return float((df["student_delta_rate_hz"].abs() >= (0.95 * max_abs_rate)).mean())


def _turn_bias(summary: dict[str, object], condition_name: str) -> float:
    motor_rates = summary["conditions"][condition_name]["motor_rates_hz"]
    return float(motor_rates["turn_right"] - motor_rates["turn_left"])


def _score_row(row: dict[str, object]) -> float:
    score = 0.0
    if row["mean_voltage_group_corr"] is not None:
        score += float(row["mean_voltage_group_corr"])
    if row["mean_voltage_side_corr"] is not None:
        score += 1.5 * float(row["mean_voltage_side_corr"])
    if float(row["left_turn_bias"]) < 0.0 and float(row["right_turn_bias"]) > 0.0:
        score += 1.0
    score -= 2.0 * float(row["saturation_fraction"])
    return float(score)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize completed splice calibration runs from existing JSON/CSV artifacts.")
    parser.add_argument("--summary-paths", nargs="+", required=True)
    parser.add_argument("--csv-output", default="outputs/metrics/splice_probe_calibration_curated.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_probe_calibration_curated.json")
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    for raw_path in args.summary_paths:
        summary_path = REPO_ROOT / raw_path
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        nonbaseline_conditions = [
            summary["conditions"]["body_left_dark"],
            summary["conditions"]["body_center_dark"],
            summary["conditions"]["body_right_dark"],
        ]
        groups_csv = _groups_csv_for_summary(summary_path)
        row = {
            "summary_json": raw_path,
            "groups_csv": str(groups_csv.relative_to(REPO_ROOT)),
            "spatial_bins": int(summary["spatial_bins"]),
            "value_scale": float(summary["value_scale"]),
            "mean_rate_group_corr": _nonnull_mean(
                [condition.get("teacher_student_group_correlation_rate") for condition in nonbaseline_conditions]
            ),
            "mean_rate_side_corr": _nonnull_mean(
                [condition.get("teacher_student_side_diff_correlation_rate") for condition in nonbaseline_conditions]
            ),
            "mean_voltage_group_corr": _nonnull_mean(
                [condition.get("teacher_student_group_correlation_voltage") for condition in nonbaseline_conditions]
            ),
            "mean_voltage_side_corr": _nonnull_mean(
                [condition.get("teacher_student_side_diff_correlation_voltage") for condition in nonbaseline_conditions]
            ),
            "mean_conductance_group_corr": _nonnull_mean(
                [condition.get("teacher_student_group_correlation_conductance") for condition in nonbaseline_conditions]
            ),
            "mean_conductance_side_corr": _nonnull_mean(
                [condition.get("teacher_student_side_diff_correlation_conductance") for condition in nonbaseline_conditions]
            ),
            "left_turn_bias": _turn_bias(summary, "body_left_dark"),
            "right_turn_bias": _turn_bias(summary, "body_right_dark"),
            "saturation_fraction": _saturation_fraction(groups_csv),
        }
        row["calibration_score"] = _score_row(row)
        rows.append(row)

    rows.sort(key=lambda row: float(row["calibration_score"]), reverse=True)
    csv_output = REPO_ROOT / args.csv_output
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    json_output = REPO_ROOT / args.json_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps(
            {
                "best_run": rows[0],
                "rows": rows,
                "selection_rule": [
                    "Use voltage-based boundary correlations as the primary calibration metric because signed inhibitory drive can be invisible in spike-rate deltas near baseline.",
                    "Weight left/right voltage side-difference preservation more strongly than broad grouped amplitude preservation.",
                    "Reward only runs where left-dark and right-dark induce opposite signed downstream turn biases.",
                    "Penalize runs with high spike-rate saturation fractions.",
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"best_run": rows[0], "csv_output": args.csv_output, "json_output": args.json_output}, indent=2))


if __name__ == "__main__":
    main()

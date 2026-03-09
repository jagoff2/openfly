from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from pathlib import Path
from statistics import mean

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]


def _nonnull_mean(values: list[float | None]) -> float | None:
    filtered = [float(value) for value in values if value is not None and not math.isnan(float(value))]
    return float(mean(filtered)) if filtered else None


def _condition_turn_bias(summary: dict[str, object], condition_name: str) -> float:
    condition = summary["conditions"][condition_name]
    motor_rates = condition["motor_rates_hz"]
    return float(motor_rates["turn_right"] - motor_rates["turn_left"])


def _saturation_fraction(groups_csv: Path) -> float:
    df = pd.read_csv(groups_csv)
    df = df[df["condition"] != "baseline_gray"].copy()
    if df.empty:
        return 0.0
    max_abs_rate = float(df["student_delta_rate_hz"].abs().max())
    if max_abs_rate <= 0.0:
        return 0.0
    saturated = df["student_delta_rate_hz"].abs() >= (0.95 * max_abs_rate)
    return float(saturated.mean())


def _build_run_score(
    *,
    mean_voltage_group_corr: float | None,
    mean_voltage_side_corr: float | None,
    saturation_fraction: float,
    left_turn_bias: float,
    right_turn_bias: float,
) -> float:
    score = 0.0
    if mean_voltage_group_corr is not None:
        score += float(mean_voltage_group_corr)
    if mean_voltage_side_corr is not None:
        score += 1.5 * float(mean_voltage_side_corr)
    if left_turn_bias < 0.0 and right_turn_bias > 0.0:
        score += 1.0
    score -= 2.0 * float(saturation_fraction)
    return float(score)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep body-free splice probe current scales and spatial bins.")
    parser.add_argument("--vision-network-dir", default=None)
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--brain-connectivity-path", default="external/fly-brain/data/2025_Connectivity_783.parquet")
    parser.add_argument("--brain-device", default="cpu")
    parser.add_argument("--vision-refresh-rate", type=float, default=500.0)
    parser.add_argument("--vision-steps", type=int, default=30)
    parser.add_argument("--vision-tail-steps", type=int, default=8)
    parser.add_argument("--brain-sim-ms", type=float, default=100.0)
    parser.add_argument("--input-mode", choices=("rate_positive", "current_signed"), default="current_signed")
    parser.add_argument("--max-input-rate-hz", type=float, default=120.0)
    parser.add_argument("--max-abs-current-values", nargs="+", type=float, default=[5.0, 10.0, 20.0, 40.0, 80.0, 120.0])
    parser.add_argument("--spatial-bins-values", nargs="+", type=int, default=[1, 2, 4])
    parser.add_argument("--min-roots-per-side", type=int, default=50)
    parser.add_argument("--min-roots-per-bin", type=int, default=20)
    parser.add_argument("--baseline-value", type=float, default=1.0)
    parser.add_argument("--patch-value", type=float, default=0.0)
    parser.add_argument("--side-fraction", type=float, default=0.35)
    parser.add_argument("--runs-dir", default="outputs/metrics/splice_probe_calibration_runs")
    parser.add_argument("--csv-output", default="outputs/metrics/splice_probe_calibration.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_probe_calibration.json")
    args = parser.parse_args()

    runs_dir = REPO_ROOT / args.runs_dir
    runs_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    best_run: dict[str, object] | None = None

    for spatial_bins in sorted(set(int(value) for value in args.spatial_bins_values)):
        for max_abs_current in sorted(set(float(value) for value in args.max_abs_current_values)):
            stem = f"bins{spatial_bins}_current{str(max_abs_current).replace('.', 'p')}"
            groups_csv = runs_dir / f"{stem}_groups.csv"
            side_csv = runs_dir / f"{stem}_side.csv"
            summary_json = runs_dir / f"{stem}_summary.json"
            command = [
                sys.executable,
                str(REPO_ROOT / "scripts" / "run_splice_probe.py"),
                "--vision-network-dir",
                str(args.vision_network_dir) if args.vision_network_dir is not None else "",
                "--annotation-path",
                str(REPO_ROOT / args.annotation_path),
                "--brain-completeness-path",
                str(REPO_ROOT / args.brain_completeness_path),
                "--brain-connectivity-path",
                str(REPO_ROOT / args.brain_connectivity_path),
                "--brain-device",
                str(args.brain_device),
                "--vision-refresh-rate",
                str(args.vision_refresh_rate),
                "--vision-steps",
                str(args.vision_steps),
                "--vision-tail-steps",
                str(args.vision_tail_steps),
                "--brain-sim-ms",
                str(args.brain_sim_ms),
                "--input-mode",
                str(args.input_mode),
                "--max-input-rate-hz",
                str(args.max_input_rate_hz),
                "--max-abs-current",
                str(max_abs_current),
                "--spatial-bins",
                str(spatial_bins),
                "--min-roots-per-side",
                str(args.min_roots_per_side),
                "--min-roots-per-bin",
                str(args.min_roots_per_bin),
                "--baseline-value",
                str(args.baseline_value),
                "--patch-value",
                str(args.patch_value),
                "--side-fraction",
                str(args.side_fraction),
                "--csv-output",
                str(groups_csv),
                "--side-diff-output",
                str(side_csv),
                "--json-output",
                str(summary_json),
            ]
            if args.vision_network_dir is None:
                del command[command.index("--vision-network-dir") : command.index("--annotation-path")]
            subprocess.run(command, check=True, cwd=REPO_ROOT)

            summary = json.loads(summary_json.read_text(encoding="utf-8"))
            nonbaseline_conditions = [
                summary["conditions"]["body_left_dark"],
                summary["conditions"]["body_center_dark"],
                summary["conditions"]["body_right_dark"],
            ]
            mean_voltage_group_corr = _nonnull_mean(
                [condition.get("teacher_student_group_correlation_voltage") for condition in nonbaseline_conditions]
            )
            mean_voltage_side_corr = _nonnull_mean(
                [condition.get("teacher_student_side_diff_correlation_voltage") for condition in nonbaseline_conditions]
            )
            mean_rate_group_corr = _nonnull_mean(
                [condition.get("teacher_student_group_correlation_rate") for condition in nonbaseline_conditions]
            )
            mean_rate_side_corr = _nonnull_mean(
                [condition.get("teacher_student_side_diff_correlation_rate") for condition in nonbaseline_conditions]
            )
            saturation_fraction = _saturation_fraction(groups_csv)
            left_turn_bias = _condition_turn_bias(summary, "body_left_dark")
            right_turn_bias = _condition_turn_bias(summary, "body_right_dark")
            run_score = _build_run_score(
                mean_voltage_group_corr=mean_voltage_group_corr,
                mean_voltage_side_corr=mean_voltage_side_corr,
                saturation_fraction=saturation_fraction,
                left_turn_bias=left_turn_bias,
                right_turn_bias=right_turn_bias,
            )
            row = {
                "spatial_bins": spatial_bins,
                "max_abs_current": max_abs_current,
                "brain_sim_ms": float(args.brain_sim_ms),
                "mean_rate_group_corr": mean_rate_group_corr,
                "mean_rate_side_corr": mean_rate_side_corr,
                "mean_voltage_group_corr": mean_voltage_group_corr,
                "mean_voltage_side_corr": mean_voltage_side_corr,
                "saturation_fraction": saturation_fraction,
                "left_turn_bias": left_turn_bias,
                "right_turn_bias": right_turn_bias,
                "run_score": run_score,
                "groups_csv": str(groups_csv.relative_to(REPO_ROOT)),
                "side_csv": str(side_csv.relative_to(REPO_ROOT)),
                "summary_json": str(summary_json.relative_to(REPO_ROOT)),
            }
            rows.append(row)
            if best_run is None or float(row["run_score"]) > float(best_run["run_score"]):
                best_run = row

    rows.sort(key=lambda row: float(row["run_score"]), reverse=True)
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
                "brain_sim_ms": float(args.brain_sim_ms),
                "input_mode": args.input_mode,
                "max_abs_current_values": [float(value) for value in args.max_abs_current_values],
                "spatial_bins_values": [int(value) for value in args.spatial_bins_values],
                "best_run": best_run,
                "rows": rows,
                "selection_rule": [
                    "Primary fit metric is mean voltage-based overlap correlation because signed inhibitory drive can be invisible in spike-rate deltas near baseline.",
                    "Mean voltage side-difference correlation is weighted more strongly than mean voltage group correlation because preserving left/right structure is the main splice requirement.",
                    "Runs are penalized for rate saturation and rewarded only when left-dark and right-dark produce opposite signed turn biases.",
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"best_run": best_run, "csv_output": args.csv_output, "json_output": args.json_output}, indent=2))


if __name__ == "__main__":
    main()

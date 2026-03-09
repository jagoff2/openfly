from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


def _load_log(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _summarize_condition(name: str, log_path: Path, metrics_path: Path, early_window_s: float) -> dict[str, float | int | str]:
    rows = _load_log(log_path)
    with metrics_path.open(newline="", encoding="utf-8") as handle:
        metrics = next(csv.DictReader(handle))
    sim_time = np.array([float(row["sim_time"]) for row in rows], dtype=float)
    target_bearing = np.array([float(row["target_state"].get("bearing_body", 0.0)) for row in rows], dtype=float)
    target_distance = np.array([float(row["target_state"].get("distance", 0.0)) for row in rows], dtype=float)
    drive_diff = np.array([float(row["right_drive"]) - float(row["left_drive"]) for row in rows], dtype=float)
    total_drive = np.array([float(row["right_drive"]) + float(row["left_drive"]) for row in rows], dtype=float)
    yaw_rate = np.array([float(row["yaw_rate"]) for row in rows], dtype=float)
    early_mask = sim_time <= float(early_window_s)
    sign_mask = np.abs(target_bearing) > 0.05
    return {
        "run": name,
        "log_path": str(log_path),
        "metrics_path": str(metrics_path),
        "sim_seconds": float(metrics["sim_seconds"]),
        "avg_forward_speed": float(metrics["avg_forward_speed"]),
        "net_displacement": float(metrics["net_displacement"]),
        "displacement_efficiency": float(metrics["displacement_efficiency"]),
        "initial_target_bearing_body": float(target_bearing[0]),
        "initial_target_distance": float(target_distance[0]),
        "early_mean_target_bearing_body": float(target_bearing[early_mask].mean()),
        "early_mean_drive_diff": float(drive_diff[early_mask].mean()),
        "early_mean_abs_yaw_rate": float(np.abs(yaw_rate[early_mask]).mean()),
        "full_corr_drive_diff_vs_target_bearing": float(np.corrcoef(drive_diff, target_bearing)[0, 1]),
        "full_corr_total_drive_vs_neg_abs_target_bearing": float(np.corrcoef(total_drive, -np.abs(target_bearing))[0, 1]),
        "full_sign_match_rate": float(np.mean(np.sign(drive_diff[sign_mask]) == np.sign(target_bearing[sign_mask]))),
        "full_sign_opp_rate": float(np.mean(np.sign(drive_diff[sign_mask]) == -np.sign(target_bearing[sign_mask]))),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize direct target-state left/right condition runs for the descending-only embodied branch.")
    parser.add_argument("--left-log", default="outputs/requested_1s_splice_descending_target_left/flygym-demo-20260309-134958/run.jsonl")
    parser.add_argument("--left-metrics", default="outputs/requested_1s_splice_descending_target_left/flygym-demo-20260309-134958/metrics.csv")
    parser.add_argument("--right-log", default="outputs/requested_1s_splice_descending_target_right/flygym-demo-20260309-135758/run.jsonl")
    parser.add_argument("--right-metrics", default="outputs/requested_1s_splice_descending_target_right/flygym-demo-20260309-135758/metrics.csv")
    parser.add_argument("--early-window-s", type=float, default=0.1)
    parser.add_argument("--csv-output", default="outputs/metrics/descending_target_conditions.csv")
    parser.add_argument("--json-output", default="outputs/metrics/descending_target_conditions.json")
    args = parser.parse_args()

    rows = [
        _summarize_condition("target_left", Path(args.left_log), Path(args.left_metrics), float(args.early_window_s)),
        _summarize_condition("target_right", Path(args.right_log), Path(args.right_metrics), float(args.early_window_s)),
    ]

    csv_path = Path(args.csv_output)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted({key for row in rows for key in row.keys()}))
        writer.writeheader()
        writer.writerows(rows)

    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()

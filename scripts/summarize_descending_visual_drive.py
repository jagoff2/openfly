from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


def _load_metrics(path: Path) -> dict[str, float | str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return next(csv.DictReader(handle))


def _load_logs(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _summarize_run(name: str, metrics_path: Path, log_path: Path, target_enabled: bool, target_speed: float, target_radius: float) -> dict[str, float | int | str | bool]:
    metrics = _load_metrics(metrics_path)
    logs = _load_logs(log_path)
    total_drive = np.array([float(row["left_drive"]) + float(row["right_drive"]) for row in logs], dtype=float)
    drive_diff = np.array([float(row["right_drive"]) - float(row["left_drive"]) for row in logs], dtype=float)
    forward_speed = np.array([float(row["forward_speed"]) for row in logs], dtype=float)
    yaw_rate = np.array([float(row["yaw_rate"]) for row in logs], dtype=float)

    summary: dict[str, float | int | str | bool] = {
        "run": name,
        "target_enabled": bool(target_enabled),
        "sim_seconds": float(metrics["sim_seconds"]),
        "avg_forward_speed": float(metrics["avg_forward_speed"]),
        "path_length": float(metrics["path_length"]),
        "net_displacement": float(metrics["net_displacement"]),
        "displacement_efficiency": float(metrics["displacement_efficiency"]),
        "stable": float(metrics["stable"]),
        "real_time_factor": float(metrics["real_time_factor"]),
        "nonzero_command_cycles": int(np.sum((np.abs(total_drive) > 1e-9) | (np.abs(drive_diff) > 1e-9))),
        "mean_total_drive": float(total_drive.mean()),
        "mean_abs_drive_diff": float(np.abs(drive_diff).mean()),
        "mean_forward_speed_log": float(forward_speed.mean()),
        "mean_abs_yaw_rate": float(np.abs(yaw_rate).mean()),
    }

    if target_enabled:
        has_direct_target_state = bool(logs and isinstance(logs[0].get("target_state"), dict) and logs[0]["target_state"].get("enabled", False))
        bearing = []
        distance = []
        if has_direct_target_state:
            for row in logs:
                target_state = row.get("target_state", {})
                bearing.append(float(target_state.get("bearing_body", 0.0)))
                distance.append(float(target_state.get("distance", 0.0)))
        else:
            angular_speed = target_speed / target_radius
            for row in logs:
                t = float(row["sim_time"])
                tx = target_radius * math.sin(angular_speed * t)
                ty = target_radius * math.cos(angular_speed * t)
                fx = float(row["position_x"])
                fy = float(row["position_y"])
                yaw = float(row["yaw"])
                rel = math.atan2(ty - fy, tx - fx) - yaw
                rel = (rel + math.pi) % (2 * math.pi) - math.pi
                bearing.append(rel)
                distance.append(math.hypot(tx - fx, ty - fy))
        bearing_arr = np.array(bearing, dtype=float)
        frontalness = np.cos(bearing_arr)
        mask = np.abs(bearing_arr) > 0.05
        summary.update(
            {
                "target_state_source": "logged" if has_direct_target_state else "reconstructed_public_arena",
                "corr_drive_diff_vs_target_bearing": float(np.corrcoef(drive_diff, bearing_arr)[0, 1]),
                "corr_total_drive_vs_target_frontalness": float(np.corrcoef(total_drive, frontalness)[0, 1]),
                "corr_forward_speed_vs_target_frontalness": float(np.corrcoef(forward_speed, frontalness)[0, 1]),
                "target_distance_start": float(distance[0]),
                "target_distance_end": float(distance[-1]),
                "target_distance_min": float(np.min(distance)),
                "steer_sign_match_rate": float(np.mean(np.sign(drive_diff[mask]) == np.sign(bearing_arr[mask]))),
                "steer_sign_opp_rate": float(np.mean(np.sign(drive_diff[mask]) == -np.sign(bearing_arr[mask]))),
            }
        )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize brain-driven / visually driven evidence for the descending-only embodied branch.")
    parser.add_argument("--target-metrics", default="outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/metrics.csv")
    parser.add_argument("--target-log", default="outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/run.jsonl")
    parser.add_argument("--zero-brain-metrics", default="outputs/requested_2s_splice_descending_zero_brain/flygym-demo-20260309-122135/metrics.csv")
    parser.add_argument("--zero-brain-log", default="outputs/requested_2s_splice_descending_zero_brain/flygym-demo-20260309-122135/run.jsonl")
    parser.add_argument("--no-target-metrics", default="outputs/requested_2s_splice_descending_no_target/flygym-demo-20260309-122723/metrics.csv")
    parser.add_argument("--no-target-log", default="outputs/requested_2s_splice_descending_no_target/flygym-demo-20260309-122723/run.jsonl")
    parser.add_argument("--target-speed", type=float, default=15.0)
    parser.add_argument("--target-radius", type=float, default=10.0)
    parser.add_argument("--csv-output", default="outputs/metrics/descending_visual_drive_validation.csv")
    parser.add_argument("--json-output", default="outputs/metrics/descending_visual_drive_validation.json")
    args = parser.parse_args()

    rows = [
        _summarize_run(
            "target",
            Path(args.target_metrics),
            Path(args.target_log),
            target_enabled=True,
            target_speed=float(args.target_speed),
            target_radius=float(args.target_radius),
        ),
        _summarize_run(
            "no_target",
            Path(args.no_target_metrics),
            Path(args.no_target_log),
            target_enabled=False,
            target_speed=float(args.target_speed),
            target_radius=float(args.target_radius),
        ),
        _summarize_run(
            "zero_brain",
            Path(args.zero_brain_metrics),
            Path(args.zero_brain_log),
            target_enabled=False,
            target_speed=float(args.target_speed),
            target_radius=float(args.target_radius),
        ),
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

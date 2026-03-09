from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize_run(outputs_root: Path, run_name: str, turn_threshold: float) -> dict[str, float | int | str | bool | None]:
    log_path = outputs_root / "logs" / f"{run_name}.jsonl"
    metrics_path = outputs_root / "metrics" / f"{run_name}.csv"
    video_path = outputs_root / "demos" / f"{run_name}.mp4"

    rows = load_jsonl(log_path) if log_path.exists() else []
    metrics = pd.read_csv(metrics_path).iloc[0].to_dict() if metrics_path.exists() else {}

    avg_left_drive = sum(row["left_drive"] for row in rows) / len(rows) if rows else 0.0
    avg_right_drive = sum(row["right_drive"] for row in rows) / len(rows) if rows else 0.0
    abs_turn_drive = [abs(row["right_drive"] - row["left_drive"]) for row in rows]
    abs_yaw_rate = [abs(row["yaw_rate"]) for row in rows]
    vision_balance = [float(row["vision_features"]["balance"]) for row in rows if "vision_features" in row]
    nonzero_motor_rows = [
        row for row in rows
        if any(abs(float(value)) > 1e-9 for value in row.get("motor_readout", {}).values())
    ]
    turn_rows = [row for row, turn_value in zip(rows, abs_turn_drive) if turn_value > turn_threshold]
    first_turn_row = turn_rows[0] if turn_rows else None

    return {
        "run_name": run_name,
        "sim_seconds": float(metrics.get("sim_seconds", 0.0)),
        "wall_seconds": float(metrics.get("wall_seconds", 0.0)),
        "real_time_factor": float(metrics.get("real_time_factor", 0.0)),
        "avg_forward_speed": float(metrics.get("avg_forward_speed", 0.0)),
        "path_length": float(metrics.get("path_length", 0.0)),
        "trajectory_smoothness": float(metrics.get("trajectory_smoothness", 0.0)),
        "stable": float(metrics.get("stable", 0.0)),
        "avg_left_drive": float(avg_left_drive),
        "avg_right_drive": float(avg_right_drive),
        "mean_abs_turn_drive": float(sum(abs_turn_drive) / len(abs_turn_drive)) if abs_turn_drive else 0.0,
        "max_abs_turn_drive": float(max(abs_turn_drive)) if abs_turn_drive else 0.0,
        "mean_abs_yaw_rate": float(sum(abs_yaw_rate) / len(abs_yaw_rate)) if abs_yaw_rate else 0.0,
        "max_abs_yaw_rate": float(max(abs_yaw_rate)) if abs_yaw_rate else 0.0,
        "mean_vision_balance": float(sum(vision_balance) / len(vision_balance)) if vision_balance else 0.0,
        "mean_abs_vision_balance": float(sum(abs(value) for value in vision_balance) / len(vision_balance)) if vision_balance else 0.0,
        "nonzero_motor_cycles": int(len(nonzero_motor_rows)),
        "first_turn_cycle": int(first_turn_row["cycle"]) if first_turn_row else None,
        "turn_response_latency_s": float(first_turn_row["sim_time"]) if first_turn_row else None,
        "video_exists": video_path.exists(),
        "log_exists": log_path.exists(),
        "metrics_exists": metrics_path.exists(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-root", default="outputs")
    parser.add_argument("--run-names", nargs="*", default=None)
    parser.add_argument("--run-prefix", default="flygym-demo-")
    parser.add_argument("--turn-threshold", type=float, default=0.05)
    parser.add_argument("--output", default="outputs/metrics/parity_runs.csv")
    args = parser.parse_args()

    outputs_root = Path(args.outputs_root)
    if args.run_names:
        run_names = args.run_names
    else:
        run_names = sorted(path.name for path in (outputs_root / "demos").glob(f"{args.run_prefix}*") if path.is_dir())
    rows = [summarize_run(outputs_root, run_name, args.turn_threshold) for run_name in run_names]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(output_path)


if __name__ == "__main__":
    main()

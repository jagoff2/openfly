from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd


def _load_metrics(metrics_path: Path) -> dict[str, object]:
    df = pd.read_csv(metrics_path)
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def _load_log_rows(log_path: Path) -> list[dict]:
    with log_path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def summarize_run(label: str, run_dir: Path) -> dict[str, object]:
    metrics = _load_metrics(run_dir / "metrics.csv")
    rows = _load_log_rows(run_dir / "run.jsonl")
    mean_left_drive = sum(float(row["left_drive"]) for row in rows) / len(rows) if rows else 0.0
    mean_right_drive = sum(float(row["right_drive"]) for row in rows) / len(rows) if rows else 0.0
    turn_commands = [float(row["right_drive"]) - float(row["left_drive"]) for row in rows]
    inferred_turn_bias = [float(row.get("sensor_metadata", {}).get("inferred_turn_bias", 0.0)) for row in rows]
    inferred_turn_confidence = [float(row.get("sensor_metadata", {}).get("inferred_turn_confidence", 0.0)) for row in rows]
    brain_context_turn_rate = [float(row.get("brain_context", {}).get("turn_rate_hz", 0.0)) for row in rows]
    brain_context_forward_rate = [float(row.get("brain_context", {}).get("forward_rate_hz", 0.0)) for row in rows]
    brain_context_modes = sorted({str(row.get("brain_context", {}).get("mode", "none")) for row in rows})
    nonzero_command_cycles = sum(1 for row in rows if abs(float(row["left_drive"])) > 1e-9 or abs(float(row["right_drive"])) > 1e-9)
    return {
        "label": label,
        "run_dir": str(run_dir),
        "brain_context_modes": ",".join(brain_context_modes),
        "log_rows": len(rows),
        "nonzero_command_cycles": nonzero_command_cycles,
        "mean_left_drive": mean_left_drive,
        "mean_right_drive": mean_right_drive,
        "mean_forward_drive": 0.5 * (mean_left_drive + mean_right_drive),
        "mean_signed_turn_command": sum(turn_commands) / len(turn_commands) if turn_commands else 0.0,
        "mean_abs_turn_command": sum(abs(value) for value in turn_commands) / len(turn_commands) if turn_commands else 0.0,
        "mean_inferred_turn_bias": sum(inferred_turn_bias) / len(inferred_turn_bias) if inferred_turn_bias else 0.0,
        "mean_inferred_turn_confidence": sum(inferred_turn_confidence) / len(inferred_turn_confidence) if inferred_turn_confidence else 0.0,
        "mean_brain_context_turn_rate_hz": sum(brain_context_turn_rate) / len(brain_context_turn_rate) if brain_context_turn_rate else 0.0,
        "max_brain_context_turn_rate_hz": max(brain_context_turn_rate) if brain_context_turn_rate else 0.0,
        "mean_brain_context_forward_rate_hz": sum(brain_context_forward_rate) / len(brain_context_forward_rate) if brain_context_forward_rate else 0.0,
        "sim_seconds": metrics.get("sim_seconds", 0.0),
        "wall_seconds": metrics.get("wall_seconds", 0.0),
        "real_time_factor": metrics.get("real_time_factor", 0.0),
        "avg_forward_speed": metrics.get("avg_forward_speed", 0.0),
        "path_length": metrics.get("path_length", 0.0),
        "stable": metrics.get("stable", 0.0),
        "completed_cycles": metrics.get("completed_cycles", 0),
        "completed_full_duration": metrics.get("completed_full_duration", 0.0),
        "failure_type": metrics.get("failure_type", ""),
        "failure_message": metrics.get("failure_message", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare multiple run directories by metrics and log-derived summaries.")
    parser.add_argument("--run", nargs=2, action="append", metavar=("LABEL", "RUN_DIR"), required=True)
    parser.add_argument("--csv-output", required=True)
    parser.add_argument("--json-output", required=True)
    args = parser.parse_args()

    summaries = [summarize_run(label, Path(run_dir)) for label, run_dir in args.run]

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0].keys()))
        writer.writeheader()
        writer.writerows(summaries)

    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(summaries, indent=2), encoding="utf-8")

    print(csv_output)
    print(json_output)


if __name__ == "__main__":
    main()

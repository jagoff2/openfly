from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis.creamer_parity_open_loop import (  # noqa: E402
    build_creamer_parity_open_loop_config,
    summarize_creamer_open_loop_run,
)
from runtime.closed_loop import run_closed_loop  # noqa: E402


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the parity-path Creamer open-loop front-to-back treadmill pair.")
    parser.add_argument("--mode", default="flygym", choices=["mock", "flygym"])
    parser.add_argument("--output-root", default="outputs/creamer2018_parity_open_loop")
    parser.add_argument("--duration", type=float, default=1.2)
    parser.add_argument("--stimulus-start", type=float, default=0.5)
    parser.add_argument("--stimulus-end", type=float, default=1.2)
    parser.add_argument("--scene-velocity", type=float, default=-30.0)
    parser.add_argument("--treadmill-settle-time", type=float, default=0.2)
    parser.add_argument("--brain-device", default="")
    args = parser.parse_args()

    output_root = Path(args.output_root)
    pair_rows: list[dict[str, object]] = []
    pair_summary: dict[str, object] = {
        "assay": "creamer2018_parity_open_loop_ftb",
        "duration_s": float(args.duration),
        "stimulus_start_s": float(args.stimulus_start),
        "stimulus_end_s": float(args.stimulus_end),
        "scene_velocity_mm_s": float(args.scene_velocity),
        "treadmill_settle_time_s": float(args.treadmill_settle_time),
        "brain_device": str(args.brain_device),
    }

    for label, ablated in [("baseline", False), ("t4t5_ablated", True)]:
        config = build_creamer_parity_open_loop_config(
            ablated=ablated,
            duration_s=float(args.duration),
            stimulus_start_s=float(args.stimulus_start),
            stimulus_end_s=float(args.stimulus_end),
            scene_velocity_mm_s=float(args.scene_velocity),
            treadmill_settle_time_s=float(args.treadmill_settle_time),
            brain_device=str(args.brain_device).strip() or None,
        )
        run = run_closed_loop(
            config,
            mode=args.mode,
            duration_s=float(args.duration),
            output_root=output_root / label,
        )
        row = {"label": label, "ablated": ablated}
        row.update(summarize_creamer_open_loop_run(run))
        pair_rows.append(row)
        pair_summary[label] = row

    if len(pair_rows) == 2:
        base, abl = pair_rows
        pair_summary["delta_command_forward_proxy_fold_change"] = float(abl["command_forward_proxy_fold_change"]) - float(base["command_forward_proxy_fold_change"])  # type: ignore[index]
        pair_summary["delta_stimulus_mean_command_forward_proxy"] = float(abl["stimulus_mean_command_forward_proxy"]) - float(base["stimulus_mean_command_forward_proxy"])  # type: ignore[index]
        pair_summary["delta_command_gait_drive_fold_change"] = float(abl["command_gait_drive_fold_change"]) - float(base["command_gait_drive_fold_change"])  # type: ignore[index]
        pair_summary["delta_stimulus_mean_command_gait_drive"] = float(abl["stimulus_mean_command_gait_drive"]) - float(base["stimulus_mean_command_gait_drive"])  # type: ignore[index]
        pair_summary["delta_command_forward_signal_delta"] = float(abl["command_forward_signal_delta"]) - float(base["command_forward_signal_delta"])  # type: ignore[index]
        pair_summary["delta_speed_fold_change"] = float(abl["speed_fold_change"]) - float(base["speed_fold_change"])  # type: ignore[index]
        pair_summary["delta_stimulus_mean_forward_speed"] = float(abl["stimulus_mean_forward_speed"]) - float(base["stimulus_mean_forward_speed"])  # type: ignore[index]

    metrics_dir = output_root / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    json_path = metrics_dir / "creamer2018_parity_open_loop_pair_summary.json"
    csv_path = metrics_dir / "creamer2018_parity_open_loop_pair_summary.csv"
    json_path.write_text(json.dumps(pair_summary, indent=2), encoding="utf-8")
    _write_csv(csv_path, pair_rows)
    print(json_path)


if __name__ == "__main__":
    main()

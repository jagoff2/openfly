from __future__ import annotations

import argparse
import copy
import csv
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from runtime.closed_loop import run_closed_loop


def load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _plot_open_loop(rows: list[dict[str, object]], path: Path) -> None:
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(6, 4))
    front_to_back = [row for row in rows if float(row.get("retinal_slip_mean_mm_s", 0.0)) < 0.0]
    back_to_front = [row for row in rows if float(row.get("retinal_slip_mean_mm_s", 0.0)) > 0.0]
    if front_to_back:
        ax.plot(
            [abs(float(row["retinal_slip_mean_mm_s"])) for row in front_to_back],
            [float(row["speed_fold_change"]) for row in front_to_back],
            marker="o",
            label="Front-to-back",
        )
    if back_to_front:
        ax.plot(
            [abs(float(row["retinal_slip_mean_mm_s"])) for row in back_to_front],
            [float(row["speed_fold_change"]) for row in back_to_front],
            marker="o",
            label="Back-to-front",
        )
    ax.set_xlabel("retinal slip magnitude during stimulus (mm/s)")
    ax.set_ylabel("stimulus/pre forward speed fold change")
    ax.set_title("Creamer 2018 open-loop analogue")
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def _plot_gain(rows: list[dict[str, object]], path: Path) -> None:
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(
        [float(row["gain_stimulus"]) for row in rows],
        [float(row["speed_fold_change"]) for row in rows],
        marker="o",
    )
    ax.set_xlabel("stimulus gain")
    ax.set_ylabel("stimulus/pre forward speed fold change")
    ax.set_title("Creamer 2018 closed-loop gain analogue")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def _build_interleaved_block_schedule(speed_mm_s: float, flicker_hz: float) -> list[dict[str, object]]:
    return [
        {"kind": "stationary", "label": "baseline_a"},
        {"kind": "front_to_back" if speed_mm_s < 0.0 else "back_to_front", "scene_velocity_mm_s": float(speed_mm_s), "label": "motion_a"},
        {"kind": "stationary", "label": "baseline_b"},
        {"kind": "counterphase_flicker", "flicker_hz": float(flicker_hz), "label": "flicker"},
        {"kind": "stationary", "label": "baseline_c"},
        {"kind": "front_to_back" if speed_mm_s < 0.0 else "back_to_front", "scene_velocity_mm_s": float(speed_mm_s), "label": "motion_b"},
        {"kind": "stationary", "label": "baseline_d"},
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Creamer 2018 visual-speed-control analogue assays.")
    parser.add_argument("--config", default="configs/flygym_visual_speed_control_living_motion_only_treadmill.yaml")
    parser.add_argument("--mode", default="flygym", choices=["mock", "flygym"])
    parser.add_argument("--duration", type=float, default=2.0)
    parser.add_argument("--output-root", default="outputs/creamer2018")
    parser.add_argument("--open-loop-speeds", nargs="*", type=float, default=[-8.0, -4.0, -2.0, -1.0, 1.0, 2.0, 4.0, 8.0])
    parser.add_argument("--gain-values", nargs="*", type=float, default=[1 / 9, 1.0, 9.0, -1 / 9, -1.0, -9.0])
    parser.add_argument("--skip-open-loop", action="store_true")
    parser.add_argument("--skip-gain", action="store_true")
    parser.add_argument("--skip-hourglass", action="store_true")
    parser.add_argument("--skip-blocks", action="store_true")
    parser.add_argument("--block-duration", type=float, default=0.25)
    parser.add_argument("--stripe-widths", nargs="*", type=float, default=[1.5, 3.0, 6.0])
    parser.add_argument("--flicker-hz", type=float, default=4.0)
    args = parser.parse_args()

    base_config = load_config(args.config)
    base_output = Path(args.output_root)
    summary: dict[str, object] = {}

    if not args.skip_open_loop:
        open_loop_rows: list[dict[str, object]] = []
        for speed in args.open_loop_speeds:
            config = copy.deepcopy(base_config)
            config["body"]["visual_speed_control"]["mode"] = "open_loop_drift"
            config["body"]["visual_speed_control"]["stimulus_scene_velocity_mm_s"] = float(speed)
            config["body"]["target_fly_enabled"] = False
            run = run_closed_loop(
                config,
                mode=args.mode,
                duration_s=args.duration,
                output_root=base_output / "open_loop",
            )
            metrics = run["visual_speed_control_metrics"]
            open_loop_rows.append(
                {
                    "scene_velocity_mm_s": float(speed),
                    "scene_motion_direction": str("front_to_back" if speed < 0.0 else "back_to_front" if speed > 0.0 else "stationary"),
                    "speed_fold_change": float(metrics.get("speed_fold_change", 0.0)),
                    "pre_mean_forward_speed": float(metrics.get("pre_mean_forward_speed", 0.0)),
                    "stimulus_mean_forward_speed": float(metrics.get("stimulus_mean_forward_speed", 0.0)),
                    "retinal_slip_mean_mm_s": float(metrics.get("retinal_slip_mean_mm_s", metrics.get("effective_visual_speed_mean_mm_s", 0.0))),
                    "retinal_slip_abs_mean_mm_s": float(metrics.get("retinal_slip_abs_mean_mm_s", metrics.get("effective_visual_speed_abs_mean_mm_s", 0.0))),
                    "effective_visual_speed_abs_mean_mm_s": float(metrics.get("effective_visual_speed_abs_mean_mm_s", 0.0)),
                    "run_dir": str(run["run_dir"]),
                }
            )
        _write_rows(base_output / "metrics" / "creamer2018_open_loop_summary.csv", open_loop_rows)
        _plot_open_loop(open_loop_rows, base_output / "plots" / "creamer2018_open_loop.png")
        summary["open_loop"] = open_loop_rows

    if not args.skip_gain:
        gain_rows: list[dict[str, object]] = []
        for gain in args.gain_values:
            config = copy.deepcopy(base_config)
            config["body"]["visual_speed_control"]["mode"] = "closed_loop_gain"
            config["body"]["visual_speed_control"]["gain_baseline"] = 1.0
            config["body"]["visual_speed_control"]["gain_stimulus"] = float(gain)
            config["body"]["target_fly_enabled"] = False
            run = run_closed_loop(
                config,
                mode=args.mode,
                duration_s=args.duration,
                output_root=base_output / "closed_loop_gain",
            )
            metrics = run["visual_speed_control_metrics"]
            gain_rows.append(
                {
                    "gain_stimulus": float(gain),
                    "speed_fold_change": float(metrics.get("speed_fold_change", 0.0)),
                    "pre_mean_forward_speed": float(metrics.get("pre_mean_forward_speed", 0.0)),
                    "stimulus_mean_forward_speed": float(metrics.get("stimulus_mean_forward_speed", 0.0)),
                    "effective_visual_speed_abs_mean_mm_s": float(metrics.get("effective_visual_speed_abs_mean_mm_s", 0.0)),
                    "run_dir": str(run["run_dir"]),
                }
            )
        _write_rows(base_output / "metrics" / "creamer2018_closed_loop_gain_summary.csv", gain_rows)
        _plot_gain(gain_rows, base_output / "plots" / "creamer2018_closed_loop_gain.png")
        summary["closed_loop_gain"] = gain_rows

    if not args.skip_hourglass:
        config = copy.deepcopy(base_config)
        config["body"]["visual_speed_control"]["mode"] = "hourglass"
        config["body"]["target_fly_enabled"] = False
        run = run_closed_loop(
            config,
            mode=args.mode,
            duration_s=args.duration,
            output_root=base_output / "hourglass",
        )
        summary["hourglass"] = {
            "run_dir": str(run["run_dir"]),
            "metrics": run["visual_speed_control_metrics"],
        }

    if not args.skip_blocks:
        block_rows: list[dict[str, object]] = []
        for stripe_width in args.stripe_widths:
            for speed in args.open_loop_speeds:
                if abs(float(speed)) < 1e-6:
                    continue
                config = copy.deepcopy(base_config)
                block_schedule = _build_interleaved_block_schedule(float(speed), float(args.flicker_hz))
                config["body"]["visual_speed_control"]["mode"] = "interleaved_blocks"
                config["body"]["visual_speed_control"]["block_duration_s"] = float(args.block_duration)
                config["body"]["visual_speed_control"]["block_schedule"] = block_schedule
                config["body"]["visual_speed_control"]["counterphase_flicker_hz"] = float(args.flicker_hz)
                config["body"]["visual_speed_control"]["stripe_width_mm"] = float(stripe_width)
                config["body"]["target_fly_enabled"] = False
                block_duration_s = float(args.block_duration) * len(block_schedule)
                run = run_closed_loop(
                    config,
                    mode=args.mode,
                    duration_s=block_duration_s,
                    output_root=base_output / "interleaved_blocks",
                )
                metrics = run["visual_speed_control_metrics"]
                direction = "front_to_back" if speed < 0.0 else "back_to_front"
                block_rows.append(
                    {
                        "stripe_width_mm": float(stripe_width),
                        "scene_velocity_mm_s": float(speed),
                        "scene_motion_direction": direction,
                        "block_duration_s": float(args.block_duration),
                        "motion_delta_forward_speed_mean": float(metrics.get(f"{direction}_delta_forward_speed_mean", 0.0)),
                        "motion_delta_forward_speed_low_turn_mean": float(metrics.get(f"{direction}_delta_forward_speed_low_turn_mean", 0.0)),
                        "motion_delta_abs_turn_signal_mean": float(metrics.get(f"{direction}_delta_abs_turn_signal_mean", 0.0)),
                        "motion_retinal_slip_abs_mean_mm_s": float(metrics.get(f"{direction}_retinal_slip_abs_mean_mm_s", 0.0)),
                        "flicker_delta_forward_speed_mean": float(metrics.get("counterphase_flicker_delta_forward_speed_mean", 0.0)),
                        "flicker_delta_forward_speed_low_turn_mean": float(metrics.get("counterphase_flicker_delta_forward_speed_low_turn_mean", 0.0)),
                        "flicker_delta_abs_turn_signal_mean": float(metrics.get("counterphase_flicker_delta_abs_turn_signal_mean", 0.0)),
                        "run_dir": str(run["run_dir"]),
                    }
                )
        _write_rows(base_output / "metrics" / "creamer2018_interleaved_blocks_summary.csv", block_rows)
        summary["interleaved_blocks"] = block_rows

    summary_path = base_output / "metrics" / "creamer2018_suite_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()

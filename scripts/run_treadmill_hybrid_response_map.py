from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.treadmill_hybrid_response import summarize_treadmill_response  # noqa: E402
from body.flygym_runtime import FlyGymRealisticVisionRuntime  # noqa: E402
from body.interfaces import HybridDriveCommand  # noqa: E402
from runtime.closed_loop import load_config  # noqa: E402


def _parse_list(raw: str) -> list[float]:
    return [float(value.strip()) for value in raw.split(",") if value.strip()]


def _command_row(
    *,
    sim_time: float,
    forward_speed_mm_s: float,
    yaw_rate_rad_s: float,
) -> dict[str, float]:
    return {
        "sim_time": float(sim_time),
        "forward_speed_mm_s": float(forward_speed_mm_s),
        "yaw_rate_rad_s": float(yaw_rate_rad_s),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure treadmill forward-speed sensitivity to direct hybrid multidrive commands.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--duration-s", type=float, default=1.0)
    parser.add_argument("--warmup-s", type=float, default=0.5)
    parser.add_argument("--amp-values", default="0.1,0.2,0.4,0.8")
    parser.add_argument("--freq-values", default="0.8,1.0,1.2,1.4")
    parser.add_argument("--retraction-gain", type=float, default=1.0)
    parser.add_argument("--stumbling-gain", type=float, default=1.0)
    parser.add_argument("--reverse-gate", type=float, default=0.0)
    args = parser.parse_args()

    config = load_config(args.config)
    runtime_cfg = config.setdefault("runtime", {})
    runtime_cfg["control_mode"] = "hybrid_multidrive"
    runtime_cfg["camera_mode"] = "fixed_birdeye"
    body_cfg = config.setdefault("body", {})
    body_cfg["target_fly_enabled"] = False
    visual_speed_cfg = body_cfg.setdefault("visual_speed_control", {})
    visual_speed_cfg["enabled"] = True
    visual_speed_cfg["geometry"] = "treadmill_ball"
    visual_speed_cfg["mode"] = "interleaved_blocks"
    visual_speed_cfg["block_duration_s"] = float(args.duration_s)
    visual_speed_cfg["block_schedule"] = [{"kind": "stationary", "label": "response_probe"}]

    timestep_s = float(runtime_cfg.get("body_timestep_s", 1e-4))
    control_interval_s = float(runtime_cfg.get("control_interval_s", 0.002))
    substeps = max(1, int(round(control_interval_s / timestep_s)))
    control_dt = timestep_s * substeps
    total_steps = max(1, int(round(float(args.duration_s) / control_dt)))

    amp_values = _parse_list(args.amp_values)
    freq_values = _parse_list(args.freq_values)
    rows: list[dict[str, float]] = []

    runtime = FlyGymRealisticVisionRuntime(
        timestep=timestep_s,
        terrain_type=str(body_cfg.get("terrain_type", "flat")),
        leading_fly_speed=float(body_cfg.get("leading_fly_speed", 15.0)),
        leading_fly_radius=float(body_cfg.get("leading_fly_radius", 10.0)),
        target_fly_enabled=bool(body_cfg.get("target_fly_enabled", False)),
        output_dir=Path(args.output_csv).resolve().parent / "treadmill_hybrid_response_tmp",
        camera_fps=int(runtime_cfg.get("video_fps", 24)),
        force_cpu_vision=bool(runtime_cfg.get("force_cpu_vision", False)),
        vision_payload_mode=str(runtime_cfg.get("vision_payload_mode", "fast")),
        control_mode="hybrid_multidrive",
        camera_mode="fixed_birdeye",
        spawn_pos=tuple(float(value) for value in body_cfg.get("spawn_pos", (0.0, 0.0, 0.3))),
        fly_init_pose=str(body_cfg.get("fly_init_pose", "tripod")),
        visual_speed_control=visual_speed_cfg,
    )
    try:
        for amp in amp_values:
            for freq in freq_values:
                obs = runtime.reset(seed=0)
                samples: list[dict[str, float]] = []
                command = HybridDriveCommand(
                    left_drive=float(amp),
                    right_drive=float(amp),
                    left_amp=float(amp),
                    right_amp=float(amp),
                    left_freq_scale=float(freq),
                    right_freq_scale=float(freq),
                    retraction_gain=float(args.retraction_gain),
                    stumbling_gain=float(args.stumbling_gain),
                    reverse_gate=float(args.reverse_gate),
                )
                samples.append(
                    _command_row(
                        sim_time=float(obs.sim_time),
                        forward_speed_mm_s=float(obs.forward_speed),
                        yaw_rate_rad_s=float(obs.yaw_rate),
                    )
                )
                for _ in range(total_steps):
                    obs = runtime.step(command, num_substeps=substeps)
                    samples.append(
                        _command_row(
                            sim_time=float(obs.sim_time),
                            forward_speed_mm_s=float(obs.forward_speed),
                            yaw_rate_rad_s=float(obs.yaw_rate),
                        )
                    )
                summary = summarize_treadmill_response(samples, warmup_s=float(args.warmup_s))
                row = {
                    "amp": float(amp),
                    "freq_scale": float(freq),
                    **asdict(summary),
                }
                rows.append(row)
    finally:
        runtime.close()

    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "config": args.config,
        "duration_s": float(args.duration_s),
        "warmup_s": float(args.warmup_s),
        "amp_values": amp_values,
        "freq_values": freq_values,
        "rows": rows,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()

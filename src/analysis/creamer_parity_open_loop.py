from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from analysis.creamer_parity_short import BASE_PARITY_CONFIG_PATH, T4_T5_CELL_TYPES


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_creamer_parity_open_loop_config(
    *,
    ablated: bool = False,
    duration_s: float = 1.2,
    stimulus_start_s: float = 0.5,
    stimulus_end_s: float = 1.2,
    scene_velocity_mm_s: float = -30.0,
    treadmill_settle_time_s: float = 0.2,
    brain_device: str | None = None,
) -> dict[str, Any]:
    if duration_s <= 0.0:
        raise ValueError("duration_s must be positive")
    if stimulus_start_s < 0.0 or stimulus_end_s <= stimulus_start_s:
        raise ValueError("stimulus window must be strictly increasing and non-negative")
    if scene_velocity_mm_s >= 0.0:
        raise ValueError("scene_velocity_mm_s must be negative for front-to-back Creamer motion")
    if treadmill_settle_time_s < 0.0:
        raise ValueError("treadmill_settle_time_s must be non-negative")

    config = copy.deepcopy(_load_yaml(BASE_PARITY_CONFIG_PATH))
    config.setdefault("body", {})
    config["body"]["target_fly_enabled"] = False
    config["body"]["fly_init_pose"] = "tripod"
    config["body"]["spawn_pos"] = [0.0, 0.0, 0.3]
    config["body"]["visual_speed_control"] = {
        "enabled": True,
        "geometry": "treadmill_ball",
        "mode": "open_loop_drift",
        "treadmill_settle_time_s": float(treadmill_settle_time_s),
        "corridor_length_mm": 60.0,
        "corridor_half_width_mm": 6.0,
        "corridor_neck_half_width_mm": 2.5,
        "corridor_neck_center_x_mm": 0.0,
        "corridor_neck_half_length_mm": 10.0,
        "wall_height_mm": 4.0,
        "wall_thickness_mm": 0.35,
        "stripe_width_mm": 1.5,
        "stripe_wrap_margin_mm": 6.0,
        "stimulus_start_s": float(stimulus_start_s),
        "stimulus_end_s": float(stimulus_end_s),
        "pre_scene_velocity_mm_s": 0.0,
        "stimulus_scene_velocity_mm_s": float(scene_velocity_mm_s),
    }

    config.setdefault("visual_splice", {})
    config["visual_splice"]["include_cell_types"] = list(T4_T5_CELL_TYPES)

    config.setdefault("decoder", {})
    config["decoder"]["command_mode"] = "hybrid_multidrive"

    config.setdefault("runtime", {})
    config["runtime"]["duration_s"] = float(duration_s)
    config["runtime"]["video_stride"] = 50
    config["runtime"]["video_fps"] = 24
    config["runtime"]["camera_mode"] = "fixed_birdeye"
    config["runtime"]["capture_activation"] = False
    config["runtime"]["control_mode"] = "hybrid_multidrive"

    if brain_device:
        config.setdefault("brain", {})
        config["brain"]["device"] = str(brain_device)

    if ablated:
        config["runtime"]["visual_ablation_cell_types"] = list(T4_T5_CELL_TYPES)
    else:
        config["runtime"].pop("visual_ablation_cell_types", None)

    return config


def summarize_creamer_open_loop_run(run: dict[str, Any]) -> dict[str, Any]:
    metrics = dict(run.get("visual_speed_control_metrics") or {})
    return {
        "run_dir": str(run.get("run_dir", "")),
        "summary_path": str(run.get("summary_path", "")),
        "mode": str(metrics.get("mode", "")),
        "primary_readout": str(metrics.get("primary_readout", "")),
        "sample_count": int(metrics.get("sample_count", 0) or 0),
        "valid_sample_count": int(metrics.get("valid_sample_count", 0) or 0),
        "pre_mean_command_forward_signal": float(metrics.get("pre_mean_command_forward_signal", 0.0) or 0.0),
        "stimulus_mean_command_forward_signal": float(metrics.get("stimulus_mean_command_forward_signal", 0.0) or 0.0),
        "post_mean_command_forward_signal": float(metrics.get("post_mean_command_forward_signal", 0.0) or 0.0),
        "command_forward_signal_delta": float(metrics.get("command_forward_signal_delta", 0.0) or 0.0),
        "pre_mean_command_gait_drive": float(metrics.get("pre_mean_command_gait_drive", 0.0) or 0.0),
        "stimulus_mean_command_gait_drive": float(metrics.get("stimulus_mean_command_gait_drive", 0.0) or 0.0),
        "post_mean_command_gait_drive": float(metrics.get("post_mean_command_gait_drive", 0.0) or 0.0),
        "command_gait_drive_fold_change": float(metrics.get("command_gait_drive_fold_change", 0.0) or 0.0),
        "pre_mean_command_forward_proxy": float(metrics.get("pre_mean_command_forward_proxy", 0.0) or 0.0),
        "stimulus_mean_command_forward_proxy": float(metrics.get("stimulus_mean_command_forward_proxy", 0.0) or 0.0),
        "post_mean_command_forward_proxy": float(metrics.get("post_mean_command_forward_proxy", 0.0) or 0.0),
        "command_forward_proxy_fold_change": float(metrics.get("command_forward_proxy_fold_change", 0.0) or 0.0),
        "command_forward_proxy_delta": float(metrics.get("command_forward_proxy_delta", 0.0) or 0.0),
        "pre_mean_forward_speed": float(metrics.get("pre_mean_forward_speed", 0.0) or 0.0),
        "stimulus_mean_forward_speed": float(metrics.get("stimulus_mean_forward_speed", 0.0) or 0.0),
        "post_mean_forward_speed": float(metrics.get("post_mean_forward_speed", 0.0) or 0.0),
        "speed_fold_change": float(metrics.get("speed_fold_change", 0.0) or 0.0),
        "scene_speed_mean_mm_s": float(metrics.get("scene_speed_mean_mm_s", 0.0) or 0.0),
        "retinal_slip_mean_mm_s": float(metrics.get("retinal_slip_mean_mm_s", 0.0) or 0.0),
        "retinal_slip_abs_mean_mm_s": float(metrics.get("retinal_slip_abs_mean_mm_s", 0.0) or 0.0),
        "speed_vs_scene_speed_corr": float(metrics.get("speed_vs_scene_speed_corr", 0.0) or 0.0),
        "command_forward_proxy_vs_scene_speed_corr": float(metrics.get("command_forward_proxy_vs_scene_speed_corr", 0.0) or 0.0),
        "command_forward_proxy_vs_retinal_slip_corr": float(metrics.get("command_forward_proxy_vs_retinal_slip_corr", 0.0) or 0.0),
    }

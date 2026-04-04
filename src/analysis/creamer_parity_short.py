from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


BASE_PARITY_CONFIG_PATH = Path(
    "configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml"
)

T4_T5_CELL_TYPES: tuple[str, ...] = (
    "T4a",
    "T4b",
    "T4c",
    "T4d",
    "T5a",
    "T5b",
    "T5c",
    "T5d",
)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_short_synced_schedule(
    *,
    block_duration_s: float = 0.1,
    scene_velocity_offset_mm_s: float = -0.5,
) -> list[dict[str, Any]]:
    if block_duration_s <= 0.0:
        raise ValueError("block_duration_s must be positive")
    if scene_velocity_offset_mm_s >= 0.0:
        raise ValueError("scene_velocity_offset_mm_s must be negative for front-to-back Creamer blocks")
    del block_duration_s  # schedule structure is independent of duration
    return [
        {
            "kind": "stationary",
            "label": "warmup_a",
            "sync_to_fly_speed": True,
            "gain": 0.0,
            "scene_velocity_offset_mm_s": 0.0,
        },
        {
            "kind": "stationary",
            "label": "warmup_b",
            "sync_to_fly_speed": True,
            "gain": 0.0,
            "scene_velocity_offset_mm_s": 0.0,
        },
        {
            "kind": "stationary",
            "label": "baseline_a",
            "sync_to_fly_speed": True,
            "gain": 0.0,
            "scene_velocity_offset_mm_s": 0.0,
        },
        {
            "kind": "front_to_back",
            "label": "motion_ftb_a",
            "sync_to_fly_speed": True,
            "gain": 0.0,
            "scene_velocity_offset_mm_s": float(scene_velocity_offset_mm_s),
        },
        {
            "kind": "stationary",
            "label": "baseline_b",
            "sync_to_fly_speed": True,
            "gain": 0.0,
            "scene_velocity_offset_mm_s": 0.0,
        },
    ]


def build_creamer_parity_short_config(
    *,
    ablated: bool = False,
    block_duration_s: float = 0.1,
    scene_velocity_offset_mm_s: float = -0.5,
) -> dict[str, Any]:
    config = copy.deepcopy(_load_yaml(BASE_PARITY_CONFIG_PATH))
    schedule = build_short_synced_schedule(
        block_duration_s=block_duration_s,
        scene_velocity_offset_mm_s=scene_velocity_offset_mm_s,
    )
    duration_s = float(block_duration_s) * len(schedule)

    config.setdefault("body", {})
    config["body"]["target_fly_enabled"] = False
    config["body"]["fly_init_pose"] = "tripod"
    config["body"]["spawn_pos"] = [0.0, 0.0, 0.3]
    config["body"]["visual_speed_control"] = {
        "enabled": True,
        "geometry": "treadmill_ball",
        "mode": "interleaved_blocks",
        "treadmill_settle_time_s": float(block_duration_s) * 2.0,
        "corridor_length_mm": 60.0,
        "corridor_half_width_mm": 6.0,
        "corridor_neck_half_width_mm": 2.5,
        "corridor_neck_center_x_mm": 0.0,
        "corridor_neck_half_length_mm": 10.0,
        "wall_height_mm": 4.0,
        "wall_thickness_mm": 0.35,
        "stripe_width_mm": 3.0,
        "stripe_wrap_margin_mm": 6.0,
        "block_duration_s": float(block_duration_s),
        "counterphase_flicker_hz": 4.0,
        "block_schedule": schedule,
    }

    config.setdefault("visual_splice", {})
    config["visual_splice"]["include_cell_types"] = list(T4_T5_CELL_TYPES)

    config.setdefault("decoder", {})
    config["decoder"]["command_mode"] = "hybrid_multidrive"

    config.setdefault("runtime", {})
    config["runtime"]["duration_s"] = duration_s
    config["runtime"]["video_stride"] = 50
    config["runtime"]["video_fps"] = 24
    config["runtime"]["camera_mode"] = "fixed_birdeye"
    config["runtime"]["capture_activation"] = False
    config["runtime"]["control_mode"] = "hybrid_multidrive"
    if ablated:
        config["runtime"]["visual_ablation_cell_types"] = list(T4_T5_CELL_TYPES)
    else:
        config["runtime"].pop("visual_ablation_cell_types", None)

    return config


def summarize_creamer_run(run: dict[str, Any]) -> dict[str, Any]:
    metrics = dict(run.get("visual_speed_control_metrics") or {})
    return {
        "run_dir": str(run.get("run_dir", "")),
        "summary_path": str(run.get("summary_path", "")),
        "mode": str(metrics.get("mode", "")),
        "block_count": int(metrics.get("block_count", 0) or 0),
        "stationary_block_count": int(metrics.get("stationary_block_count", 0) or 0),
        "stimulus_block_count": int(metrics.get("stimulus_block_count", 0) or 0),
        "speed_fold_change": float(metrics.get("speed_fold_change", 0.0) or 0.0),
        "pre_mean_forward_speed": float(metrics.get("pre_mean_forward_speed", 0.0) or 0.0),
        "stimulus_mean_forward_speed": float(metrics.get("stimulus_mean_forward_speed", 0.0) or 0.0),
        "front_to_back_delta_forward_speed_mean": float(metrics.get("front_to_back_delta_forward_speed_mean", 0.0) or 0.0),
        "front_to_back_delta_forward_speed_low_turn_mean": float(metrics.get("front_to_back_delta_forward_speed_low_turn_mean", 0.0) or 0.0),
        "front_to_back_delta_abs_turn_signal_mean": float(metrics.get("front_to_back_delta_abs_turn_signal_mean", 0.0) or 0.0),
        "front_to_back_retinal_slip_abs_mean_mm_s": float(metrics.get("front_to_back_retinal_slip_abs_mean_mm_s", 0.0) or 0.0),
    }

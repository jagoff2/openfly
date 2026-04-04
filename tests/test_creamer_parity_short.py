from __future__ import annotations

from analysis.creamer_parity_short import build_creamer_parity_short_config
from runtime.closed_loop import assert_full_parity_flygym_config


def test_creamer_parity_short_config_stays_on_full_parity_path() -> None:
    config = build_creamer_parity_short_config()

    assert_full_parity_flygym_config(config)
    assert config["body"]["target_fly_enabled"] is False
    assert config["body"]["fly_init_pose"] == "tripod"
    assert tuple(config["body"]["spawn_pos"]) == (0.0, 0.0, 0.3)
    assert config["body"]["visual_speed_control"]["enabled"] is True
    assert config["body"]["visual_speed_control"]["mode"] == "interleaved_blocks"
    assert config["body"]["visual_speed_control"]["block_duration_s"] == 0.1
    assert config["body"]["visual_speed_control"]["treadmill_settle_time_s"] == 0.2
    assert len(config["body"]["visual_speed_control"]["block_schedule"]) == 5
    schedule = config["body"]["visual_speed_control"]["block_schedule"]
    assert [block["label"] for block in schedule] == ["warmup_a", "warmup_b", "baseline_a", "motion_ftb_a", "baseline_b"]
    assert all(bool(block.get("sync_to_fly_speed", False)) for block in schedule)
    assert all(float(block.get("gain", 999.0)) == 0.0 for block in schedule)
    assert float(schedule[3]["scene_velocity_offset_mm_s"]) == -0.5
    assert config["runtime"]["duration_s"] == 0.5
    assert config["runtime"]["camera_mode"] == "fixed_birdeye"
    assert config["runtime"]["force_cpu_vision"] is True
    assert config["runtime"]["control_mode"] == "hybrid_multidrive"
    assert config["runtime"]["video_stride"] == 50
    assert config["encoder"]["visual_gain_hz"] == 0.0
    assert config["encoder"]["visual_looming_gain_hz"] == 0.0
    assert config["decoder"]["command_mode"] == "hybrid_multidrive"
    assert config["visual_splice"]["include_cell_types"] == [
        "T4a",
        "T4b",
        "T4c",
        "T4d",
        "T5a",
        "T5b",
        "T5c",
        "T5d",
    ]


def test_creamer_parity_short_ablated_config_only_adds_lawful_visual_ablation() -> None:
    config = build_creamer_parity_short_config(ablated=True)

    assert_full_parity_flygym_config(config)
    assert config["runtime"]["visual_ablation_cell_types"] == [
        "T4a",
        "T4b",
        "T4c",
        "T4d",
        "T5a",
        "T5b",
        "T5c",
        "T5d",
    ]

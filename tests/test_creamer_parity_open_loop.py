from __future__ import annotations

from analysis.creamer_parity_open_loop import build_creamer_parity_open_loop_config, summarize_creamer_open_loop_run


def test_creamer_parity_open_loop_config_uses_parity_base_and_treadmill_open_loop() -> None:
    config = build_creamer_parity_open_loop_config()

    assert config["runtime"]["parity_path"]["required"] is True
    assert config["runtime"]["parity_path"]["profile"] == "flygym_full_parity_v1"
    assert config["runtime"]["control_mode"] == "hybrid_multidrive"
    assert config["decoder"]["command_mode"] == "hybrid_multidrive"
    assert config["body"]["visual_speed_control"]["geometry"] == "treadmill_ball"
    assert config["body"]["visual_speed_control"]["mode"] == "open_loop_drift"
    assert config["body"]["visual_speed_control"]["stimulus_scene_velocity_mm_s"] == -30.0
    assert config["body"]["visual_speed_control"]["treadmill_settle_time_s"] == 0.2
    assert config["runtime"]["duration_s"] == 1.2
    assert config["runtime"]["visual_ablation_cell_types"] if "visual_ablation_cell_types" in config["runtime"] else [] == []


def test_creamer_parity_open_loop_config_applies_ablation_and_device_override() -> None:
    config = build_creamer_parity_open_loop_config(ablated=True, brain_device="cuda:1")

    assert config["brain"]["device"] == "cuda:1"
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


def test_creamer_parity_open_loop_summary_promotes_command_side_metrics() -> None:
    summary = summarize_creamer_open_loop_run(
        {
            "run_dir": "r",
            "summary_path": "s",
            "visual_speed_control_metrics": {
                "mode": "open_loop_drift",
                "primary_readout": "command_forward_proxy",
                "sample_count": 10,
                "valid_sample_count": 8,
                "pre_mean_command_forward_signal": 0.5,
                "stimulus_mean_command_forward_signal": 0.8,
                "post_mean_command_forward_signal": 0.7,
                "command_forward_signal_delta": 0.3,
                "pre_mean_command_gait_drive": 1.0,
                "stimulus_mean_command_gait_drive": 1.4,
                "post_mean_command_gait_drive": 1.2,
                "command_gait_drive_fold_change": 1.4,
                "pre_mean_command_forward_proxy": 0.5,
                "stimulus_mean_command_forward_proxy": 1.12,
                "post_mean_command_forward_proxy": 0.84,
                "command_forward_proxy_fold_change": 2.24,
                "command_forward_proxy_delta": 0.62,
                "pre_mean_forward_speed": 0.0,
                "stimulus_mean_forward_speed": 0.0,
                "post_mean_forward_speed": 0.0,
                "speed_fold_change": 0.0,
            },
        }
    )

    assert summary["primary_readout"] == "command_forward_proxy"
    assert summary["pre_mean_command_forward_proxy"] == 0.5
    assert summary["stimulus_mean_command_forward_proxy"] == 1.12
    assert summary["command_forward_proxy_fold_change"] == 2.24

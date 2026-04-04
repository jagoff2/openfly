from __future__ import annotations

import pytest

from analysis.visual_speed_control_metrics import compute_visual_speed_control_metrics


def test_visual_speed_control_metrics_ignore_invalid_treadmill_samples_in_open_loop() -> None:
    records = [
        {
            "sim_time": 0.0,
            "forward_speed": 999.0,
            "left_drive": 9.0,
            "right_drive": 9.0,
            "left_amp": 9.0,
            "right_amp": 9.0,
            "left_freq_scale": 9.0,
            "right_freq_scale": 9.0,
            "motor_signals": {"forward_signal": 9.0, "turn_signal": 0.0},
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "measurement_valid": False,
                    "stimulus_active": False,
                    "mode": "open_loop_drift",
                    "fly_forward_speed_mm_s_measured": 999.0,
                    "scene_world_speed_mm_s": 0.0,
                    "effective_visual_speed_mm_s": 0.0,
                    "retinal_slip_mm_s": 0.0,
                }
            },
        },
        {
            "sim_time": 0.2,
            "forward_speed": 10.0,
            "left_drive": 0.6,
            "right_drive": 0.6,
            "left_amp": 1.0,
            "right_amp": 1.0,
            "left_freq_scale": 1.0,
            "right_freq_scale": 1.0,
            "motor_signals": {"forward_signal": 0.6, "turn_signal": 0.0},
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "measurement_valid": True,
                    "stimulus_active": False,
                    "mode": "open_loop_drift",
                    "fly_forward_speed_mm_s_measured": 10.0,
                    "scene_world_speed_mm_s": 0.0,
                    "effective_visual_speed_mm_s": 0.0,
                    "retinal_slip_mm_s": 0.0,
                }
            },
        },
        {
            "sim_time": 0.8,
            "forward_speed": 20.0,
            "left_drive": 0.8,
            "right_drive": 0.8,
            "left_amp": 1.5,
            "right_amp": 1.5,
            "left_freq_scale": 1.2,
            "right_freq_scale": 1.2,
            "motor_signals": {"forward_signal": 0.8, "turn_signal": 0.0},
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "measurement_valid": True,
                    "stimulus_active": True,
                    "mode": "open_loop_drift",
                    "fly_forward_speed_mm_s_measured": 20.0,
                    "scene_world_speed_mm_s": -30.0,
                    "effective_visual_speed_mm_s": -30.0,
                    "retinal_slip_mm_s": -30.0,
                }
            },
        },
    ]

    metrics = compute_visual_speed_control_metrics(records)

    assert metrics["sample_count"] == 3
    assert metrics["valid_sample_count"] == 2
    assert metrics["pre_mean_forward_speed"] == 10.0
    assert metrics["stimulus_mean_forward_speed"] == 20.0
    assert metrics["speed_fold_change"] == 2.0
    assert metrics["primary_readout"] == "command_forward_proxy"
    assert metrics["pre_mean_command_forward_signal"] == pytest.approx(0.6)
    assert metrics["stimulus_mean_command_forward_signal"] == pytest.approx(0.8)
    assert metrics["pre_mean_command_gait_drive"] == pytest.approx(1.0)
    assert metrics["stimulus_mean_command_gait_drive"] == pytest.approx(1.8)
    assert metrics["pre_mean_command_forward_proxy"] == pytest.approx(0.6)
    assert metrics["stimulus_mean_command_forward_proxy"] == pytest.approx(1.44)


def test_visual_speed_control_metrics_ignore_invalid_treadmill_samples_in_block_summary() -> None:
    records = [
        {
            "sim_time": 0.0,
            "forward_speed": 500.0,
            "left_drive": 5.0,
            "right_drive": 5.0,
            "left_amp": 5.0,
            "right_amp": 5.0,
            "left_freq_scale": 5.0,
            "right_freq_scale": 5.0,
            "motor_signals": {"forward_signal": 5.0, "turn_signal": 0.0},
            "yaw_rate": 0.0,
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "measurement_valid": False,
                    "stimulus_active": False,
                    "mode": "interleaved_blocks",
                    "block_index": 0,
                    "block_kind": "stationary",
                    "block_label": "warmup_a",
                    "fly_forward_speed_mm_s_measured": 500.0,
                    "scene_world_speed_mm_s": 0.0,
                    "effective_visual_speed_mm_s": 0.0,
                    "retinal_slip_mm_s": 0.0,
                }
            },
        },
        {
            "sim_time": 0.2,
            "forward_speed": 10.0,
            "left_drive": 0.5,
            "right_drive": 0.6,
            "left_amp": 1.0,
            "right_amp": 1.1,
            "left_freq_scale": 1.0,
            "right_freq_scale": 1.0,
            "motor_signals": {"forward_signal": 0.55, "turn_signal": 0.1},
            "yaw_rate": 0.2,
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "measurement_valid": True,
                    "stimulus_active": False,
                    "mode": "interleaved_blocks",
                    "block_index": 1,
                    "block_kind": "stationary",
                    "block_label": "baseline_a",
                    "fly_forward_speed_mm_s_measured": 10.0,
                    "scene_world_speed_mm_s": 0.0,
                    "effective_visual_speed_mm_s": 0.0,
                    "retinal_slip_mm_s": 0.0,
                }
            },
        },
        {
            "sim_time": 0.4,
            "forward_speed": 7.0,
            "left_drive": 0.8,
            "right_drive": 0.8,
            "left_amp": 1.3,
            "right_amp": 1.3,
            "left_freq_scale": 1.2,
            "right_freq_scale": 1.2,
            "motor_signals": {"forward_signal": 0.8, "turn_signal": 0.05},
            "yaw_rate": 0.1,
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "measurement_valid": True,
                    "stimulus_active": True,
                    "mode": "interleaved_blocks",
                    "block_index": 2,
                    "block_kind": "front_to_back",
                    "block_label": "motion_ftb_a",
                    "fly_forward_speed_mm_s_measured": 7.0,
                    "scene_world_speed_mm_s": -4.0,
                    "effective_visual_speed_mm_s": -4.0,
                    "retinal_slip_mm_s": -4.0,
                }
            },
        },
    ]

    metrics = compute_visual_speed_control_metrics(records)

    assert metrics["sample_count"] == 3
    assert metrics["valid_sample_count"] == 2
    assert metrics["block_count"] == 2
    assert metrics["stationary_block_count"] == 1
    assert metrics["stimulus_block_count"] == 1
    assert metrics["front_to_back_delta_forward_speed_mean"] == -3.0


def test_visual_speed_control_metrics_capture_command_side_readout_when_treadmill_is_flat() -> None:
    records = [
        {
            "sim_time": 0.2,
            "forward_speed": 0.0,
            "left_drive": 0.6,
            "right_drive": 0.6,
            "left_amp": 1.0,
            "right_amp": 1.0,
            "left_freq_scale": 1.0,
            "right_freq_scale": 1.0,
            "motor_signals": {"forward_signal": 0.6, "turn_signal": 0.0},
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "measurement_valid": True,
                    "stimulus_active": False,
                    "mode": "open_loop_drift",
                    "fly_forward_speed_mm_s_measured": 0.0,
                    "scene_world_speed_mm_s": 0.0,
                    "effective_visual_speed_mm_s": 0.0,
                    "retinal_slip_mm_s": 0.0,
                }
            },
        },
        {
            "sim_time": 0.8,
            "forward_speed": 0.0,
            "left_drive": 0.9,
            "right_drive": 0.9,
            "left_amp": 1.4,
            "right_amp": 1.4,
            "left_freq_scale": 1.3,
            "right_freq_scale": 1.3,
            "motor_signals": {"forward_signal": 0.9, "turn_signal": 0.0},
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "measurement_valid": True,
                    "stimulus_active": True,
                    "mode": "open_loop_drift",
                    "fly_forward_speed_mm_s_measured": 0.0,
                    "scene_world_speed_mm_s": -30.0,
                    "effective_visual_speed_mm_s": -30.0,
                    "retinal_slip_mm_s": -30.0,
                }
            },
        },
    ]

    metrics = compute_visual_speed_control_metrics(records)

    assert metrics["stimulus_mean_forward_speed"] == 0.0
    assert metrics["pre_mean_forward_speed"] == 0.0
    assert metrics["pre_mean_command_forward_proxy"] == pytest.approx(0.6)
    assert metrics["stimulus_mean_command_forward_proxy"] == pytest.approx(1.638)
    assert metrics["command_forward_proxy_delta"] == pytest.approx(1.038)

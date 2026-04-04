from __future__ import annotations

import pytest

from analysis.behavior_metrics import compute_behavior_metrics


def test_compute_behavior_metrics_captures_target_alignment_and_bouts() -> None:
    records = [
        {
            "sim_time": 0.0,
            "left_drive": 0.0,
            "right_drive": 0.2,
            "forward_speed": 1.2,
            "yaw": 0.0,
            "yaw_rate": 0.3,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.2},
            "target_state": {"enabled": True, "bearing_body": 0.8, "distance": 10.0},
        },
        {
            "sim_time": 0.1,
            "left_drive": 0.1,
            "right_drive": 0.25,
            "forward_speed": 1.4,
            "yaw": 0.03,
            "yaw_rate": 0.25,
            "motor_signals": {"forward_signal": 0.25, "turn_signal": 0.15},
            "target_state": {"enabled": True, "bearing_body": 0.4, "distance": 9.7},
        },
        {
            "sim_time": 0.2,
            "left_drive": 0.15,
            "right_drive": 0.2,
            "forward_speed": 1.5,
            "yaw": 0.05,
            "yaw_rate": 0.1,
            "motor_signals": {"forward_signal": 0.3, "turn_signal": 0.05},
            "target_state": {"enabled": True, "bearing_body": 0.1, "distance": 9.3},
        },
    ]

    metrics = compute_behavior_metrics(records)

    assert metrics["target_condition"]["enabled"] is True
    assert metrics["target_condition"]["bearing_reduction_rad"] > 0.0
    assert metrics["target_condition"]["approach_fraction"] == 1.0
    assert metrics["target_condition"]["turn_alignment_fraction_active"] == 1.0
    assert metrics["spontaneous_locomotion"]["locomotor_bout_count"] == 1.0
    assert metrics["spontaneous_locomotion"]["controller_state_entropy"] > 0.0


def test_compute_behavior_metrics_handles_no_target_condition() -> None:
    records = [
        {
            "sim_time": 0.0,
            "left_drive": 0.0,
            "right_drive": 0.0,
            "forward_speed": 0.2,
            "yaw": 0.0,
            "yaw_rate": 0.0,
            "motor_signals": {"forward_signal": 0.0, "turn_signal": 0.0},
            "target_state": {"enabled": False},
        },
        {
            "sim_time": 0.1,
            "left_drive": 0.2,
            "right_drive": 0.1,
            "forward_speed": 1.4,
            "yaw": -0.04,
            "yaw_rate": -0.2,
            "motor_signals": {"forward_signal": 0.25, "turn_signal": -0.1},
            "target_state": {"enabled": False},
        },
    ]

    metrics = compute_behavior_metrics(records)

    assert metrics["target_condition"]["enabled"] is False
    assert metrics["spontaneous_locomotion"]["locomotor_active_fraction"] > 0.0
    assert metrics["controller_summary"]["left_drive_dominant_fraction"] > 0.0


def test_compute_behavior_metrics_captures_jump_refixation() -> None:
    records = [
        {
            "sim_time": 0.0,
            "left_drive": 0.0,
            "right_drive": 0.0,
            "forward_speed": 1.0,
            "yaw": 0.0,
            "yaw_rate": 0.0,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.0},
            "target_state": {"enabled": True, "visible": True, "bearing_body": 0.1, "distance": 10.0, "last_event_id": 0},
        },
        {
            "sim_time": 0.1,
            "left_drive": 0.0,
            "right_drive": 0.4,
            "forward_speed": 1.0,
            "yaw": 0.0,
            "yaw_rate": 0.4,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.4},
            "target_state": {
                "enabled": True,
                "visible": True,
                "bearing_body": 0.8,
                "distance": 10.0,
                "last_event_id": 1,
                "last_event_kind": "jump",
            },
        },
        {
            "sim_time": 0.2,
            "left_drive": 0.0,
            "right_drive": 0.3,
            "forward_speed": 1.0,
            "yaw": 0.0,
            "yaw_rate": 0.3,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.3},
            "target_state": {"enabled": True, "visible": True, "bearing_body": 0.4, "distance": 9.8, "last_event_id": 1, "last_event_kind": "jump"},
        },
        {
            "sim_time": 0.3,
            "left_drive": 0.1,
            "right_drive": 0.15,
            "forward_speed": 1.0,
            "yaw": 0.0,
            "yaw_rate": 0.1,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.05},
            "target_state": {"enabled": True, "visible": True, "bearing_body": 0.1, "distance": 9.6, "last_event_id": 1, "last_event_kind": "jump"},
        },
    ]

    metrics = compute_behavior_metrics(records)

    assert metrics["target_perturbation"]["jump_event_count"] == 1
    assert metrics["target_perturbation"]["jump_refixation_latency_s"] == pytest.approx(0.2)
    assert metrics["target_perturbation"]["jump_turn_alignment_fraction_active"] == 1.0
    assert metrics["target_perturbation"]["jump_bearing_recovery_fraction_2s"] > 0.0


def test_compute_behavior_metrics_captures_brief_target_removal() -> None:
    records = [
        {
            "sim_time": 0.0,
            "left_drive": 0.0,
            "right_drive": 0.1,
            "forward_speed": 1.0,
            "yaw": 0.0,
            "yaw_rate": 0.1,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.1},
            "target_state": {"enabled": True, "visible": True, "bearing_body": 0.2, "distance": 10.0, "last_event_id": 0},
        },
        {
            "sim_time": 0.1,
            "left_drive": 0.0,
            "right_drive": 0.3,
            "forward_speed": 1.0,
            "yaw": 0.0,
            "yaw_rate": 0.3,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.3},
            "target_state": {
                "enabled": True,
                "visible": False,
                "bearing_body": 0.6,
                "distance": 10.0,
                "last_event_id": 1,
                "last_event_kind": "hide_start",
            },
        },
        {
            "sim_time": 0.2,
            "left_drive": 0.0,
            "right_drive": 0.25,
            "forward_speed": 1.0,
            "yaw": 0.0,
            "yaw_rate": 0.25,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.25},
            "target_state": {"enabled": True, "visible": False, "bearing_body": 0.5, "distance": 10.1, "last_event_id": 1, "last_event_kind": "hide_start"},
        },
        {
            "sim_time": 0.3,
            "left_drive": 0.0,
            "right_drive": 0.2,
            "forward_speed": 1.0,
            "yaw": 0.0,
            "yaw_rate": 0.2,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.2},
            "target_state": {
                "enabled": True,
                "visible": True,
                "bearing_body": 0.3,
                "distance": 9.9,
                "last_event_id": 2,
                "last_event_kind": "hide_end",
            },
        },
        {
            "sim_time": 0.4,
            "left_drive": 0.1,
            "right_drive": 0.15,
            "forward_speed": 1.0,
            "yaw": 0.0,
            "yaw_rate": 0.1,
            "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.05},
            "target_state": {"enabled": True, "visible": True, "bearing_body": 0.1, "distance": 9.7, "last_event_id": 2, "last_event_kind": "hide_end"},
        },
    ]

    metrics = compute_behavior_metrics(records)

    assert metrics["target_perturbation"]["removal_event_count"] == 1
    assert metrics["target_perturbation"]["removal_persistence_duration_s"] == pytest.approx(0.2)
    assert metrics["target_perturbation"]["removal_persistence_turn_alignment_fraction"] == 1.0
    assert metrics["target_perturbation"]["removal_post_return_refixation_latency_s"] == pytest.approx(0.0)


def test_compute_behavior_metrics_uses_treadmill_measured_speed_for_treadmill_records() -> None:
    records = [
        {
            "sim_time": 0.0,
            "left_drive": 0.0,
            "right_drive": 0.0,
            "forward_speed": 0.0,
            "yaw": 0.0,
            "yaw_rate": 0.0,
            "motor_signals": {"forward_signal": 0.0, "turn_signal": 0.0},
            "target_state": {"enabled": False},
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "fly_forward_speed_mm_s_measured": 12.0,
                }
            },
        },
        {
            "sim_time": 0.1,
            "left_drive": 0.0,
            "right_drive": 0.0,
            "forward_speed": 0.0,
            "yaw": 0.0,
            "yaw_rate": 0.0,
            "motor_signals": {"forward_signal": 0.0, "turn_signal": 0.0},
            "target_state": {"enabled": False},
            "body_metadata": {
                "visual_speed_state": {
                    "enabled": True,
                    "speed_source": "treadmill_ball",
                    "fly_forward_speed_mm_s_measured": 18.0,
                }
            },
        },
    ]

    metrics = compute_behavior_metrics(records)

    assert metrics["spontaneous_locomotion"]["mean_forward_speed"] == pytest.approx(15.0)
    assert metrics["spontaneous_locomotion"]["locomotor_active_fraction"] == 1.0

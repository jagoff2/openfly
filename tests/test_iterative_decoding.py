from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from analysis.iterative_decoding import propose_decoding_cycle


def test_propose_decoding_cycle_ranks_unsampled_upstream_families(tmp_path: Path) -> None:
    annotation_path = tmp_path / "annotation.tsv"
    annotation_path.write_text(
        "\n".join(
            [
                "root_id\tcell_type\tside\tsuper_class\tsoma_x\tsoma_y",
                "1\tRelayA\tleft\tvisual_projection\t0\t0",
                "2\tRelayA\tright\tvisual_projection\t1\t0",
                "3\tMotorA\tleft\tdescending\t0\t1",
                "4\tMotorA\tright\tdescending\t1\t1",
            ]
        ),
        encoding="utf-8",
    )
    completeness_path = tmp_path / "completeness.csv"
    completeness_path.write_text(",x\n1,1\n2,1\n3,1\n4,1\n", encoding="utf-8")
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "MotorA",
                        "left_root_ids": [3],
                        "right_root_ids": [4],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "brain:",
                f"  completeness_path: {completeness_path.as_posix()}",
                "visual_splice:",
                f"  annotation_path: {annotation_path.as_posix()}",
                "decoder:",
                f"  population_candidates_json: {candidates_path.as_posix()}",
                "runtime:",
                "  duration_s: 0.2",
            ]
        ),
        encoding="utf-8",
    )
    capture_path = tmp_path / "capture.npz"
    log_path = tmp_path / "run.jsonl"
    log_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "sim_time": 0.0,
                        "left_drive": 0.0,
                        "right_drive": 0.0,
                        "forward_speed": 0.0,
                        "yaw": 0.0,
                        "yaw_rate": 0.0,
                        "motor_signals": {"forward_signal": 0.0, "turn_signal": 0.0},
                        "target_state": {"enabled": False},
                    }
                ),
                json.dumps(
                    {
                        "sim_time": 0.1,
                        "left_drive": 0.1,
                        "right_drive": 0.2,
                        "forward_speed": 1.0,
                        "yaw": 0.05,
                        "yaw_rate": 0.2,
                        "motor_signals": {"forward_signal": 0.2, "turn_signal": 0.1},
                        "target_state": {"enabled": False},
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )
    np.savez_compressed(
        capture_path,
        frame_cycles=np.asarray([0, 1, 2], dtype=np.int32),
        frame_target_bearing_body=np.asarray([0.0, 1.0, 2.0], dtype=np.float32),
        brain_voltage_frames=np.asarray(
            [
                [0.0, 0.0, 0.1, 0.1],
                [1.0, 1.0, 0.1, 0.1],
                [2.0, 2.0, 0.1, 0.1],
            ],
            dtype=np.float32,
        ),
        brain_spike_frames=np.zeros((3, 4), dtype=np.uint8),
        controller_labels=np.asarray(["forward_speed", "left_drive", "right_drive"], dtype="<U64"),
        controller_matrix=np.asarray(
            [
                [0.0, 0.5, 1.0],
                [0.1, 0.1, 0.1],
                [0.2, 0.2, 0.2],
            ],
            dtype=np.float32,
        ),
        monitor_labels=np.asarray(["MotorA"], dtype="<U64"),
        monitor_matrix=np.asarray([[0.1, 0.1, 0.1]], dtype=np.float32),
        monitored_root_ids=np.asarray([1, 2, 3, 4], dtype=np.int64),
        monitored_voltage_matrix=np.asarray(
            [
                [0.0, 1.0, 2.0],
                [0.0, 1.0, 2.0],
                [0.1, 0.1, 0.1],
                [0.1, 0.1, 0.1],
            ],
            dtype=np.float32,
        ),
    )

    result = propose_decoding_cycle(
        config_path=config_path,
        capture_path=capture_path,
        log_path=log_path,
        max_brain_points=4,
        monitor_limit=4,
        relay_limit=4,
    )

    assert "RelayA" in result["recommendations"]["relay_probe_families"]
    assert "RelayA" in result["recommendations"]["monitor_expansion_families"]
    assert result["recommendations"]["structured_signal_library"][0]["family"] == "RelayA"
    assert not result["tables"]["family_turn_scores"].empty
    assert not result["tables"]["monitor_voltage_scores"].empty
    assert not result["tables"]["monitor_voltage_turn_scores"].empty
    assert "RelayA" in result["recommendations"]["relay_turn_probe_families"]
    assert result["behavior_diagnosis"]["target_condition"]["enabled"] is False


def test_propose_decoding_cycle_aligns_monitor_voltage_to_frame_cycles(tmp_path: Path) -> None:
    annotation_path = tmp_path / "annotation.tsv"
    annotation_path.write_text(
        "\n".join(
            [
                "root_id\tcell_type\tside\tsuper_class\tsoma_x\tsoma_y",
                "1\tRelayA\tleft\tvisual_projection\t0\t0",
                "2\tRelayA\tright\tvisual_projection\t1\t0",
            ]
        ),
        encoding="utf-8",
    )
    completeness_path = tmp_path / "completeness.csv"
    completeness_path.write_text(",x\n1,1\n2,1\n", encoding="utf-8")
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "RelayA",
                        "left_root_ids": [1],
                        "right_root_ids": [2],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "brain:",
                f"  completeness_path: {completeness_path.as_posix()}",
                "visual_splice:",
                f"  annotation_path: {annotation_path.as_posix()}",
                "decoder:",
                f"  population_candidates_json: {candidates_path.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )
    capture_path = tmp_path / "capture.npz"
    log_path = tmp_path / "run.jsonl"
    log_path.write_text(
        json.dumps(
            {
                "sim_time": 0.0,
                "left_drive": 0.0,
                "right_drive": 0.0,
                "forward_speed": 0.0,
                "yaw": 0.0,
                "yaw_rate": 0.0,
                "motor_signals": {"forward_signal": 0.0, "turn_signal": 0.0},
                "target_state": {"enabled": False},
            }
        ),
        encoding="utf-8",
    )
    np.savez_compressed(
        capture_path,
        frame_cycles=np.asarray([0, 2], dtype=np.int32),
        frame_target_bearing_body=np.asarray([0.0, 1.0], dtype=np.float32),
        brain_voltage_frames=np.asarray([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32),
        brain_spike_frames=np.zeros((2, 2), dtype=np.uint8),
        controller_labels=np.asarray(["forward_speed", "left_drive", "right_drive"], dtype="<U64"),
        controller_matrix=np.asarray(
            [
                [0.0, 0.5, 1.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ],
            dtype=np.float32,
        ),
        monitor_labels=np.asarray(["RelayA"], dtype="<U64"),
        monitor_matrix=np.asarray([[0.0, 0.5, 1.0]], dtype=np.float32),
        monitored_root_ids=np.asarray([1, 2], dtype=np.int64),
        monitored_voltage_matrix=np.asarray(
            [
                [0.0, 0.5, 1.0],
                [0.0, 0.5, 1.0],
            ],
            dtype=np.float32,
        ),
    )

    result = propose_decoding_cycle(
        config_path=config_path,
        capture_path=capture_path,
        log_path=log_path,
        max_brain_points=2,
        monitor_limit=2,
        relay_limit=2,
    )

    assert not result["tables"]["monitor_voltage_scores"].empty
    assert not result["tables"]["monitor_voltage_turn_scores"].empty


def test_propose_decoding_cycle_ranks_lateralized_turn_monitor_candidates(tmp_path: Path) -> None:
    annotation_path = tmp_path / "annotation.tsv"
    annotation_path.write_text(
        "\n".join(
            [
                "root_id\tcell_type\tside\tsuper_class\tsoma_x\tsoma_y",
                "1\tRelayA\tleft\tvisual_projection\t0\t0",
                "2\tRelayA\tright\tvisual_projection\t1\t0",
                "3\tRelayB\tleft\tcentral\t0\t1",
                "4\tRelayB\tright\tcentral\t1\t1",
            ]
        ),
        encoding="utf-8",
    )
    completeness_path = tmp_path / "completeness.csv"
    completeness_path.write_text(",x\n1,1\n2,1\n3,1\n4,1\n", encoding="utf-8")
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "RelayA",
                        "left_root_ids": [1],
                        "right_root_ids": [2],
                    },
                    {
                        "candidate_label": "RelayB",
                        "left_root_ids": [3],
                        "right_root_ids": [4],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "brain:",
                f"  completeness_path: {completeness_path.as_posix()}",
                "visual_splice:",
                f"  annotation_path: {annotation_path.as_posix()}",
                "decoder:",
                f"  population_candidates_json: {candidates_path.as_posix()}",
            ]
        ),
        encoding="utf-8",
    )
    capture_path = tmp_path / "capture.npz"
    log_path = tmp_path / "run.jsonl"
    log_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "sim_time": 0.0,
                        "left_drive": 0.0,
                        "right_drive": 0.0,
                        "forward_speed": 0.0,
                        "yaw": 0.0,
                        "yaw_rate": 0.0,
                        "motor_signals": {"forward_signal": 0.0, "turn_signal": 0.0},
                        "target_state": {"enabled": True, "bearing_rad_body": -1.0},
                    }
                ),
                json.dumps(
                    {
                        "sim_time": 0.1,
                        "left_drive": 0.1,
                        "right_drive": 0.3,
                        "forward_speed": 0.5,
                        "yaw": 0.1,
                        "yaw_rate": 0.4,
                        "motor_signals": {"forward_signal": 0.1, "turn_signal": 0.2},
                        "target_state": {"enabled": True, "bearing_rad_body": 0.0},
                    }
                ),
                json.dumps(
                    {
                        "sim_time": 0.2,
                        "left_drive": 0.3,
                        "right_drive": 0.1,
                        "forward_speed": 0.5,
                        "yaw": -0.1,
                        "yaw_rate": -0.4,
                        "motor_signals": {"forward_signal": 0.1, "turn_signal": -0.2},
                        "target_state": {"enabled": True, "bearing_rad_body": 1.0},
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )
    np.savez_compressed(
        capture_path,
        frame_cycles=np.asarray([0, 1, 2], dtype=np.int32),
        frame_target_bearing_body=np.asarray([-1.0, 0.0, 1.0], dtype=np.float32),
        brain_voltage_frames=np.asarray(
            [
                [1.0, -1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [-1.0, 1.0, 0.0, 0.0],
            ],
            dtype=np.float32,
        ),
        brain_spike_frames=np.zeros((3, 4), dtype=np.uint8),
        controller_labels=np.asarray(["forward_speed", "left_drive", "right_drive"], dtype="<U64"),
        controller_matrix=np.asarray(
            [
                [0.0, 0.5, 0.5],
                [0.0, 0.1, 0.3],
                [0.0, 0.3, 0.1],
            ],
            dtype=np.float32,
        ),
        monitor_labels=np.asarray(["RelayA", "RelayB"], dtype="<U64"),
        monitor_matrix=np.asarray(
            [
                [0.1, 0.1, 0.1],
                [0.0, 0.0, 0.0],
            ],
            dtype=np.float32,
        ),
        monitored_root_ids=np.asarray([1, 2, 3, 4], dtype=np.int64),
        monitored_voltage_matrix=np.asarray(
            [
                [1.0, 0.0, -1.0],
                [-1.0, 0.0, 1.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ],
            dtype=np.float32,
        ),
    )

    result = propose_decoding_cycle(
        config_path=config_path,
        capture_path=capture_path,
        log_path=log_path,
        max_brain_points=4,
        monitor_limit=4,
        relay_limit=4,
    )

    turn_table = result["tables"]["monitor_voltage_turn_scores"]
    assert str(turn_table.iloc[0]["label"]) == "RelayA"
    assert "RelayA" in result["recommendations"]["monitor_turn_labels"]

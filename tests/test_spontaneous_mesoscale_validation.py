from __future__ import annotations

import numpy as np

from analysis.spontaneous_mesoscale_validation import (
    _criterion,
    _circular_shift_rows,
    _forced_vs_spontaneous_public_criterion,
    _mean_abs_pairwise_corr,
    _principal_component_metrics,
    FamilySideGroup,
    summarize_condition_dynamics,
    summarize_family_voltage_structure,
)


def _record(
    *,
    sim_time: float,
    forward_speed: float,
    yaw_rate: float,
    left_drive: float,
    right_drive: float,
    forward_signal: float,
    turn_signal: float,
    spike_fraction: float,
    voltage_std: float,
    background_rate: float = 0.03,
    background_active_fraction: float = 0.02,
    background_latent_mean_abs: float = 1.0,
) -> dict:
    return {
        "sim_time": sim_time,
        "forward_speed": forward_speed,
        "yaw_rate": yaw_rate,
        "left_drive": left_drive,
        "right_drive": right_drive,
        "motor_signals": {
            "forward_signal": forward_signal,
            "turn_signal": turn_signal,
        },
        "brain_backend_state": {
            "global_spike_fraction": spike_fraction,
            "global_voltage_std": voltage_std,
            "background_mean_rate_hz": background_rate,
            "background_active_fraction": background_active_fraction,
            "background_latent_mean_abs_hz": background_latent_mean_abs,
        },
    }


def test_summarize_condition_dynamics_detects_walk_linked_global_shift() -> None:
    records = []
    for idx in range(160):
        active = idx >= 80
        records.append(
            _record(
                sim_time=idx * 0.01,
                forward_speed=2.0 if active else 0.0,
                yaw_rate=0.3 if active else 0.0,
                left_drive=0.3 if active else 0.0,
                right_drive=0.4 if active else 0.0,
                forward_signal=0.4 if active else 0.0,
                turn_signal=0.1 if active else 0.0,
                spike_fraction=0.002 if active else 0.001,
                voltage_std=60.0 if active else 40.0,
            )
        )
    summary = summarize_condition_dynamics(records)
    assert summary["locomotor_onset_count"] >= 1
    assert summary["speed_voltage_std_corr"] > 0.5
    assert summary["onset_voltage_std_delta"] > 0.0
    assert summary["background_mean_rate_hz_mean"] > 0.0


def test_principal_component_metrics_show_residual_structure() -> None:
    time = np.linspace(0.0, 4.0 * np.pi, 200, dtype=np.float32)
    matrix = np.stack(
        [
            np.sin(time),
            np.sin(time + 0.1),
            np.cos(time * 0.5),
            np.cos(time * 0.5 + 0.3),
        ],
        axis=1,
    )
    metrics = _principal_component_metrics(matrix)
    assert 0.0 < metrics["pc1_variance_ratio"] < 1.0
    assert metrics["participation_ratio_topk"] > 1.0
    assert metrics["lag1_autocorr_mean"] > 0.5


def test_criterion_helper_emits_expected_shape() -> None:
    payload = _criterion("pass", "example", value=1.0)
    assert payload["status"] == "pass"
    assert payload["summary"] == "example"
    assert payload["metrics"]["value"] == 1.0


def test_forced_vs_spontaneous_public_criterion_maps_ok_payload() -> None:
    payload = _forced_vs_spontaneous_public_criterion(
        {
            "status": "ok",
            "n_candidate_rows": 4,
            "n_experiments_used": 2,
            "n_valid_vector_corr": 2,
            "n_valid_rank_corr": 2,
            "n_valid_prelead_fraction": 1,
            "median_steady_walk_vector_corr": 0.7,
            "median_steady_walk_vector_cosine": 0.8,
            "median_steady_walk_rank_corr": 0.6,
            "median_spontaneous_prelead_fraction": 0.2,
            "median_spontaneous_minus_forced_prelead_delta": 0.1,
            "dropped_experiments": [],
        }
    )
    assert payload["status"] == "pass"
    assert payload["metrics"]["n_experiments_used"] == 2


def test_forced_vs_spontaneous_public_criterion_marks_weak_ok_payload_partial() -> None:
    payload = _forced_vs_spontaneous_public_criterion(
        {
            "status": "ok",
            "n_candidate_rows": 4,
            "n_experiments_used": 3,
            "n_valid_vector_corr": 3,
            "n_valid_rank_corr": 3,
            "n_valid_prelead_fraction": 1,
            "median_steady_walk_vector_corr": 0.05,
            "median_steady_walk_vector_cosine": 0.08,
            "median_steady_walk_rank_corr": 0.09,
            "median_spontaneous_prelead_fraction": 0.2,
            "median_spontaneous_minus_forced_prelead_delta": 0.1,
            "dropped_experiments": [],
        }
    )
    assert payload["status"] == "partial"


def test_forced_vs_spontaneous_public_criterion_blocks_when_files_are_missing() -> None:
    payload = _forced_vs_spontaneous_public_criterion(
        {
            "status": "blocked_missing_files",
            "missing_files": ["Additional_data.zip"],
            "dropped_experiments": [],
        }
    )
    assert payload["status"] == "blocked"
    assert "Additional_data.zip" in payload["metrics"]["missing_files"]
    assert "Walk_anatomical_regions.zip is useful but optional" in payload["summary"]


def test_summarize_family_voltage_structure_clips_controller_and_voltage_lengths() -> None:
    capture = {
        "controller_labels": np.asarray(["left_drive", "right_drive"], dtype=object),
        "controller_matrix": np.asarray(
            [
                [0.1, 0.2, 0.3, 0.4, 0.5],
                [0.5, 0.4, 0.3, 0.2, 0.1],
            ],
            dtype=np.float32,
        ),
        "frame_cycles": np.asarray([0, 1, 2, 3, 4], dtype=np.int64),
        "brain_voltage_frames": np.asarray(
            [
                [1.0, 1.2, 0.8, 0.9],
                [1.1, 1.3, 0.7, 0.8],
                [1.2, 1.4, 0.6, 0.7],
                [1.3, 1.5, 0.5, 0.6],
            ],
            dtype=np.float32,
        ),
    }
    family_groups = [
        FamilySideGroup(
            family="test_family",
            super_class="central",
            left_indices=(0, 1),
            right_indices=(2, 3),
        )
    ]
    summary = summarize_family_voltage_structure(capture=capture, family_groups=family_groups)
    assert summary["family_pair_count"] == 1
    assert summary["bilateral_matrix"].shape == (1, 4)
    assert summary["asymmetry_matrix"].shape == (1, 4)
    assert list(summary["ordered_table"]["family"]) == ["test_family"]


def test_circular_shift_surrogate_preserves_shape_and_changes_alignment() -> None:
    matrix = np.arange(24, dtype=np.float32).reshape(3, 8)
    shifted = _circular_shift_rows(matrix, seed=0)
    assert shifted.shape == matrix.shape
    assert not np.array_equal(shifted, matrix)


def test_mean_abs_pairwise_corr_detects_structure() -> None:
    time = np.linspace(0.0, 2.0 * np.pi, 200, dtype=np.float32)
    matrix = np.stack(
        [
            np.sin(time),
            np.sin(time + 0.1),
            np.sin(time + 0.2),
        ],
        axis=0,
    )
    assert _mean_abs_pairwise_corr(matrix) > 0.8

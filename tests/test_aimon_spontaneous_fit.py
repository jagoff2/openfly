from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from analysis.aimon_parity_harness import AimonCanonicalTrialData
from analysis.aimon_spontaneous_fit import (
    _sensor_pool_rates_from_regressor_value,
    _trial_regressor_values,
    apply_reduced_linear_projection,
    build_trial_execution_plan,
    build_backend_from_config,
    choose_tiny_feature_indices_from_fit_rows,
    fit_reduced_linear_projection,
    select_readout_feature_subset,
    split_aimon_trial_into_windows,
)
from analysis.public_body_feedback import public_body_feedback_from_aimon_regressor
from bridge.encoder import EncoderConfig, SensoryEncoder


def test_trial_regressor_values_slices_without_abs_or_normalization(tmp_path: Path) -> None:
    regressor = np.linspace(-9.0, 0.0, 10, dtype=np.float32)
    regressor_path = tmp_path / "regressor.npy"
    np.save(regressor_path, regressor)
    trial = AimonCanonicalTrialData(
        trial_id="B350_forced_walk",
        split="train",
        behavior_context="forced_walk",
        matrix=np.zeros((2, 3), dtype=np.float32),
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        stimulus={"parameters": {"window_start": 2, "window_stop": 8}},
        behavior_paths={"walk_regressor_path": str(regressor_path)},
        metadata={},
    )
    values = _trial_regressor_values(trial)
    np.testing.assert_allclose(values, np.asarray([-7.0, -4.5, -2.0], dtype=np.float32), atol=1e-6)


def test_trial_regressor_values_uses_spontaneous_regressor_when_present(tmp_path: Path) -> None:
    regressor = np.asarray([0.1, 0.3, 0.5], dtype=np.float32)
    regressor_path = tmp_path / "regressor.npy"
    np.save(regressor_path, regressor)
    trial = AimonCanonicalTrialData(
        trial_id="B350_spontaneous_walk",
        split="train",
        behavior_context="spontaneous_walk",
        matrix=np.zeros((2, 3), dtype=np.float32),
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        stimulus={"parameters": {"window_start": 0, "window_stop": 3}},
        behavior_paths={"walk_regressor_path": str(regressor_path)},
        metadata={},
    )
    np.testing.assert_allclose(_trial_regressor_values(trial), regressor)


def test_trial_regressor_values_falls_back_to_direct_alignment_when_window_metadata_is_invalid(tmp_path: Path) -> None:
    regressor = np.asarray([0.0, 0.5, 1.0, 0.5], dtype=np.float32)
    regressor_path = tmp_path / "regressor.npy"
    np.save(regressor_path, regressor)
    trial = AimonCanonicalTrialData(
        trial_id="B1269_forced_walk",
        split="test",
        behavior_context="forced_walk",
        matrix=np.zeros((2, 2), dtype=np.float32),
        timebase_s=np.asarray([0.0, 1.0], dtype=np.float32),
        stimulus={"parameters": {"window_start": 99, "window_stop": 101}},
        behavior_paths={"walk_regressor_path": str(regressor_path)},
        metadata={},
    )
    np.testing.assert_allclose(_trial_regressor_values(trial), np.asarray([0.0, 0.5], dtype=np.float32))


def test_reduced_linear_projection_recovers_synthetic_mapping() -> None:
    rng = np.random.default_rng(0)
    feature_a = rng.normal(size=(5, 20)).astype(np.float32)
    feature_b = rng.normal(size=(5, 15)).astype(np.float32)
    true_weights = rng.normal(size=(3, 5)).astype(np.float32)
    observed_a = true_weights @ feature_a
    observed_b = true_weights @ feature_b
    model = fit_reduced_linear_projection(
        [feature_a, feature_b],
        [observed_a, observed_b],
        feature_names=[f"feature_{idx:02d}" for idx in range(5)],
        fit_trial_ids=["trial_a", "trial_b"],
        max_basis_dim=5,
        ridge_lambda=1e-6,
    )
    pred_a = apply_reduced_linear_projection(model, feature_a)
    pred_b = apply_reduced_linear_projection(model, feature_b)
    np.testing.assert_allclose(pred_a, observed_a, atol=1e-4)
    np.testing.assert_allclose(pred_b, observed_b, atol=1e-4)


def test_reduced_linear_projection_falls_back_when_svd_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    rng = np.random.default_rng(1)
    feature = rng.normal(size=(4, 18)).astype(np.float32)
    observed = rng.normal(size=(2, 18)).astype(np.float32)

    original_svd = np.linalg.svd

    def _failing_svd(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise np.linalg.LinAlgError("forced failure")

    monkeypatch.setattr(np.linalg, "svd", _failing_svd)
    model = fit_reduced_linear_projection(
        [feature],
        [observed],
        feature_names=[f"feature_{idx:02d}" for idx in range(4)],
        fit_trial_ids=["trial_a"],
        max_basis_dim=4,
        ridge_lambda=1e-3,
    )
    monkeypatch.setattr(np.linalg, "svd", original_svd)

    predicted = apply_reduced_linear_projection(model, feature)
    assert predicted.shape == observed.shape
    assert np.isfinite(predicted).all()


def test_reduced_linear_projection_sanitizes_nonfinite_rows() -> None:
    feature = np.asarray(
        [
            [0.0, 1.0, np.nan, 3.0],
            [1.0, 2.0, np.inf, -np.inf],
            [2.0, 2.0, 2.0, 2.0],
        ],
        dtype=np.float32,
    )
    observed = np.asarray(
        [
            [0.5, np.nan, 1.5, 2.5],
            [1.0, 1.0, 1.0, 1.0],
        ],
        dtype=np.float32,
    )
    model = fit_reduced_linear_projection(
        [feature],
        [observed],
        feature_names=[f"feature_{idx:02d}" for idx in range(3)],
        fit_trial_ids=["trial_a"],
        max_basis_dim=3,
        ridge_lambda=1e-3,
    )
    predicted = apply_reduced_linear_projection(model, feature)
    assert np.isfinite(predicted).all()


def test_select_readout_feature_subset_tiny_mode_keeps_globals_covariates_and_limited_bilateral() -> None:
    feature_names = (
        "bilateral::fam_a",
        "bilateral::fam_b",
        "bilateral::fam_c",
        "asymmetry::fam_a",
        "global::mean_voltage",
        "global::voltage_std",
        "covariate::public_regressor",
    )
    feature_matrix = np.arange(len(feature_names) * 3, dtype=np.float32).reshape(len(feature_names), 3)

    selected_matrix, selected_names = select_readout_feature_subset(
        feature_matrix,
        feature_names,
        readout_mode="tiny",
        tiny_bilateral_limit=2,
    )

    assert selected_names == (
        "bilateral::fam_a",
        "bilateral::fam_b",
        "global::mean_voltage",
        "global::voltage_std",
        "covariate::public_regressor",
    )
    np.testing.assert_allclose(selected_matrix, feature_matrix[[0, 1, 4, 5, 6]])


def test_choose_tiny_feature_indices_from_fit_rows_keeps_temporalized_rows_for_top_bilateral_bases() -> None:
    feature_names = (
        "bilateral::fam_a",
        "bilateral::fam_b",
        "bilateral::fam_a::obs_lp_tau_0.5s",
        "bilateral::fam_b::obs_lp_tau_0.5s",
        "global::mean_voltage",
        "covariate::public_regressor",
    )
    fit_matrix = np.asarray(
        [
            [0.0, 2.0, 0.0, 2.0],   # fam_a raw high variance
            [1.0, 1.0, 1.0, 1.0],   # fam_b raw low variance
            [0.0, 1.0, 0.0, 1.0],   # fam_a obs high variance
            [1.0, 1.0, 1.0, 1.0],   # fam_b obs low variance
            [0.0, 0.0, 0.0, 0.0],   # global
            [0.0, 1.0, 0.0, 1.0],   # covariate
        ],
        dtype=np.float32,
    )

    indices = choose_tiny_feature_indices_from_fit_rows(
        [fit_matrix],
        feature_names,
        tiny_bilateral_limit=1,
    )

    kept = tuple(feature_names[idx] for idx in indices.tolist())
    assert kept == (
        "bilateral::fam_a",
        "bilateral::fam_a::obs_lp_tau_0.5s",
        "global::mean_voltage",
        "covariate::public_regressor",
    )


def test_build_backend_from_config_passes_backend_dynamics() -> None:
    backend, _ = build_backend_from_config(
        Path("configs/brain_endogenous_public_parity.yaml"),
        device_override="cpu",
    )
    assert backend.backend_dynamics.endogenous_path_selected
    assert not backend.backend_dynamics.use_diagnostic_surrogate


def test_trial_regressor_values_prefers_windowed_metadata() -> None:
    trial = AimonCanonicalTrialData(
        trial_id="windowed",
        split="train",
        behavior_context="forced_walk",
        matrix=np.zeros((2, 3), dtype=np.float32),
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        stimulus={"parameters": {"window_start": 0, "window_stop": 3}},
        behavior_paths={},
        metadata={"window_regressor_values": np.asarray([0.1, 0.2, 0.3], dtype=np.float32)},
    )
    values = _trial_regressor_values(trial)
    np.testing.assert_allclose(values, np.asarray([0.1, 0.2, 0.3], dtype=np.float32))


def test_public_body_feedback_from_aimon_regressor_exposes_exafferent_and_transition_channels() -> None:
    channels = public_body_feedback_from_aimon_regressor(
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        regressor_values=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        sample_index=1,
        forward_speed_scale=2.0,
        contact_force_scale=3.0,
    )

    assert channels.forward_speed == pytest.approx(1.0)
    assert channels.contact_force == pytest.approx(1.5)
    assert channels.exafferent_drive == pytest.approx(0.5)
    assert channels.transition_on > 0.0


def test_sensor_pool_rates_from_regressor_value_adds_reafferent_drive_for_spontaneous_windows() -> None:
    encoder = SensoryEncoder(
        EncoderConfig(
            visual_gain_hz=0.0,
            yaw_gain_hz=0.0,
            speed_gain_hz=25.0,
            contact_gain_hz=15.0,
            accel_gain_hz=10.0,
            state_gain_hz=5.0,
            transition_gain_hz=7.0,
            stop_suppression_hz=2.0,
        )
    )
    pool_rates = _sensor_pool_rates_from_regressor_value(
        encoder,
        sim_time_s=0.5,
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        regressor_values=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        sample_index=1,
        force_forward_speed=1.0,
        force_contact_force=1.0,
    )

    assert pool_rates["mech_left"] > 0.0
    assert pool_rates["mech_right"] > 0.0


def test_split_aimon_trial_into_windows_preserves_trace_identity_and_assigns_splits() -> None:
    trial = AimonCanonicalTrialData(
        trial_id="B350_spontaneous_walk",
        split="train",
        behavior_context="spontaneous_walk",
        matrix=np.arange(24, dtype=np.float32).reshape(2, 12),
        timebase_s=np.linspace(0.0, 1.1, 12, dtype=np.float32),
        stimulus={"parameters": {"window_start": 0, "window_stop": 12}},
        behavior_paths={},
        metadata={"exp_id": "B350"},
    )
    windows = split_aimon_trial_into_windows(
        trial,
        window_count=4,
        fit_window_indices=(0, 2),
    )

    assert [window.trial_id for window in windows] == [
        "B350_spontaneous_walk__win_00",
        "B350_spontaneous_walk__win_01",
        "B350_spontaneous_walk__win_02",
        "B350_spontaneous_walk__win_03",
    ]
    assert [window.split for window in windows] == ["train", "test", "train", "test"]
    assert all(window.matrix.shape == (2, 3) for window in windows)
    assert all(window.timebase_s[0] == pytest.approx(0.0) for window in windows)
    assert windows[1].metadata["source_trial_id"] == "B350_spontaneous_walk"
    assert windows[1].metadata["window_index"] == 1


def test_split_aimon_trial_into_windows_can_keep_only_selected_windows() -> None:
    trial = AimonCanonicalTrialData(
        trial_id="B350_spontaneous_walk",
        split="train",
        behavior_context="spontaneous_walk",
        matrix=np.arange(24, dtype=np.float32).reshape(2, 12),
        timebase_s=np.linspace(0.0, 1.1, 12, dtype=np.float32),
        stimulus={"parameters": {"window_start": 0, "window_stop": 12}},
        behavior_paths={},
        metadata={"exp_id": "B350"},
    )
    windows = split_aimon_trial_into_windows(
        trial,
        window_count=4,
        include_window_indices=(1, 3),
        fit_window_indices=(1,),
        test_window_indices=(3,),
    )

    assert [window.trial_id for window in windows] == [
        "B350_spontaneous_walk__win_01",
        "B350_spontaneous_walk__win_03",
    ]
    assert [window.split for window in windows] == ["train", "test"]
    assert [window.metadata["window_index"] for window in windows] == [1, 3]


def test_build_trial_execution_plan_preserves_contiguous_source_windows() -> None:
    trial = AimonCanonicalTrialData(
        trial_id="B350_spontaneous_walk",
        split="train",
        behavior_context="spontaneous_walk",
        matrix=np.arange(24, dtype=np.float32).reshape(2, 12),
        timebase_s=np.linspace(0.0, 1.1, 12, dtype=np.float32),
        stimulus={"parameters": {"window_start": 0, "window_stop": 12}},
        behavior_paths={},
        metadata={"exp_id": "B350"},
    )
    windows = split_aimon_trial_into_windows(
        trial,
        window_count=4,
        include_window_indices=(0, 1, 3),
        fit_window_indices=(0, 1),
        test_window_indices=(3,),
    )
    plan = build_trial_execution_plan(
        windows,
        base_seed=7,
        preserve_continuity_by_source_trial=True,
    )

    assert [(row.trial_id, row.reset_state, row.seed) for row in plan] == [
        ("B350_spontaneous_walk__win_00", True, 7),
        ("B350_spontaneous_walk__win_01", False, 7),
        ("B350_spontaneous_walk__win_03", True, 8),
    ]

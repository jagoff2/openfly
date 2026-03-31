from __future__ import annotations

from pathlib import Path

import numpy as np

from analysis.aimon_parity_harness import AimonCanonicalTrialData
from analysis.aimon_spontaneous_fit import (
    _trial_regressor_values,
    apply_reduced_linear_projection,
    build_backend_from_config,
    choose_tiny_feature_indices_from_fit_rows,
    fit_reduced_linear_projection,
    select_readout_feature_subset,
)


def test_trial_regressor_values_slices_and_normalizes(tmp_path: Path) -> None:
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
    np.testing.assert_allclose(values, np.asarray([1.0, 0.64285713, 0.2857143], dtype=np.float32), atol=1e-6)


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

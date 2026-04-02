from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from analysis.aimon_spontaneous_fit import (
    _current_feature_vector,
    _feature_name_list,
    _zero_vision,
    choose_tiny_feature_indices_from_fit_rows,
    apply_reduced_linear_projection,
    build_backend_from_config,
    build_family_basis_operators,
    fit_reduced_linear_projection,
    select_readout_feature_subset,
)
from analysis.imaging_observation_model import (
    augment_feature_matrix_with_observation_basis,
    normalize_observation_taus,
)
from analysis.public_body_feedback import (
    public_body_feedback_from_schaffer_covariates,
    public_body_observation_from_channels,
)
from analysis.schaffer_parity_harness import (
    SchafferCanonicalTrialData,
    load_schaffer_canonical_trial_data,
    score_schaffer_trial_matrix,
)
from bridge.encoder import EncoderConfig, SensoryEncoder


@dataclass(frozen=True)
class SchafferReplayConfig:
    brain_config_path: str | Path
    device: str | None = None
    seed: int = 0
    warmup_s: float = 1.0
    max_basis_dim: int = 64
    ridge_lambda: float = 1e-3
    force_forward_speed: float = 1.0
    force_contact_force: float = 1.0
    include_asymmetry_basis: bool = True
    include_global_features: bool = True
    include_ball_motion_feature: bool = True
    include_behavioral_state_features: bool = True
    preserve_state_within_session: bool = True
    observation_taus_s: tuple[float, ...] = ()
    readout_mode: str = "reduced"
    tiny_bilateral_limit: int = 4
    min_family_size_per_side: int = 2
    max_family_size_per_side: int = 128


def _normalize_nonnegative(values: np.ndarray) -> np.ndarray:
    clipped = np.maximum(np.asarray(values, dtype=np.float32).reshape(-1), 0.0)
    max_value = float(np.max(clipped)) if clipped.size else 0.0
    if max_value <= 1e-6:
        return np.zeros_like(clipped, dtype=np.float32)
    return (clipped / max_value).astype(np.float32, copy=False)


def _resample_series(values: np.ndarray | None, timebase_s: np.ndarray | None, target_timebase_s: np.ndarray) -> np.ndarray:
    if values is None:
        return np.zeros_like(target_timebase_s, dtype=np.float32)
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    if timebase_s is None:
        if values.size == target_timebase_s.size:
            return values.astype(np.float32, copy=False)
        source_time = np.linspace(0.0, 1.0, values.size, dtype=np.float32)
        target_time = np.linspace(0.0, 1.0, target_timebase_s.size, dtype=np.float32)
        return np.interp(target_time, source_time, values).astype(np.float32)
    source_time = np.asarray(timebase_s, dtype=np.float32).reshape(-1)
    if values.size != source_time.size:
        raise ValueError("values and timebase lengths must match")
    return np.interp(target_timebase_s, source_time, values).astype(np.float32)


def _resample_matrix(matrix: np.ndarray | None, timebase_s: np.ndarray | None, target_timebase_s: np.ndarray) -> np.ndarray:
    if matrix is None:
        return np.zeros((0, target_timebase_s.size), dtype=np.float32)
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.ndim != 2:
        raise ValueError("behavioral_state must be 2D")
    rows = [
        _resample_series(matrix[row_index], timebase_s, target_timebase_s)
        for row_index in range(matrix.shape[0])
    ]
    if not rows:
        return np.zeros((0, target_timebase_s.size), dtype=np.float32)
    return np.stack(rows, axis=0).astype(np.float32, copy=False)


def _schaffer_covariate_feature_names(
    *,
    include_ball_motion_feature: bool,
    behavioral_state_dim: int,
    include_behavioral_state_features: bool,
) -> tuple[str, ...]:
    names: list[str] = []
    if include_ball_motion_feature:
        names.append("covariate::ball_motion")
    if include_behavioral_state_features:
        names.extend(f"covariate::behavioral_state_{idx:02d}" for idx in range(behavioral_state_dim))
    return tuple(names)


def _trial_ball_motion_values(trial: SchafferCanonicalTrialData) -> np.ndarray:
    if trial.ball_motion is None:
        return np.zeros_like(trial.timebase_s, dtype=np.float32)
    values = _resample_series(trial.ball_motion, trial.ball_motion_time_s, trial.timebase_s)
    return _normalize_nonnegative(values)


def _trial_behavioral_state_values(trial: SchafferCanonicalTrialData) -> np.ndarray:
    if trial.behavioral_state is None:
        return np.zeros((0, trial.timebase_s.size), dtype=np.float32)
    return _resample_matrix(trial.behavioral_state, trial.behavioral_state_time_s, trial.timebase_s)


def _trial_session_key(trial: SchafferCanonicalTrialData) -> str:
    value = str(trial.metadata.get("session_file", "")).strip()
    if value:
        return value
    return trial.trial_id.split("_trial_")[0]


def _trial_start_time_s(trial: SchafferCanonicalTrialData) -> float:
    params = dict(trial.stimulus.get("parameters", {}))
    return float(params.get("start_time_s", 0.0))


def _trial_stop_time_s(trial: SchafferCanonicalTrialData) -> float:
    params = dict(trial.stimulus.get("parameters", {}))
    if "stop_time_s" in params:
        return float(params["stop_time_s"])
    timebase = np.asarray(trial.timebase_s, dtype=np.float32).reshape(-1)
    return _trial_start_time_s(trial) + (float(timebase[-1]) if timebase.size else 0.0)


def simulate_schaffer_trial_feature_matrix(
    backend,
    basis,
    trial: SchafferCanonicalTrialData,
    *,
    encoder: SensoryEncoder,
    warmup_s: float,
    seed: int,
    force_forward_speed: float,
    force_contact_force: float,
    include_global_features: bool,
    include_ball_motion_feature: bool,
    include_behavioral_state_features: bool,
    reset_backend: bool = True,
    session_time_offset_s: float = 0.0,
    pre_gap_s: float = 0.0,
) -> dict[str, Any]:
    if reset_backend:
        backend.reset(seed=int(seed))
        warmup_steps = int(round(float(warmup_s) * 1000.0 / float(backend.dt_ms)))
        if warmup_steps > 0:
            backend.step({}, num_steps=warmup_steps)
    if pre_gap_s > 0.0:
        gap_steps = max(1, int(round(float(pre_gap_s) * 1000.0 / float(backend.dt_ms))))
        backend.step({}, num_steps=gap_steps)

    timebase_s = np.asarray(trial.timebase_s, dtype=np.float32).reshape(-1)
    ball_motion_values = _trial_ball_motion_values(trial)
    behavioral_state_values = _trial_behavioral_state_values(trial)
    base_feature_names = _feature_name_list(
        basis,
        include_global_features=include_global_features,
        include_regressor_feature=False,
    )
    covariate_feature_names = _schaffer_covariate_feature_names(
        include_ball_motion_feature=include_ball_motion_feature,
        behavioral_state_dim=int(behavioral_state_values.shape[0]),
        include_behavioral_state_features=include_behavioral_state_features,
    )
    feature_names = tuple(base_feature_names) + tuple(covariate_feature_names)
    feature_matrix = np.zeros((len(feature_names), timebase_s.size), dtype=np.float32)
    last_time_s = float(session_time_offset_s)

    for sample_index in range(timebase_s.size):
        current_time_s = float(session_time_offset_s + float(timebase_s[sample_index]))
        if sample_index > 0:
            delta_s = max(0.0, current_time_s - last_time_s)
            num_steps = max(1, int(round(delta_s * 1000.0 / float(backend.dt_ms))))
            channels = public_body_feedback_from_schaffer_covariates(
                timebase_s=timebase_s,
                ball_motion_values=ball_motion_values,
                behavioral_state_values=behavioral_state_values,
                sample_index=sample_index - 1,
                forward_speed_scale=float(force_forward_speed),
                contact_force_scale=float(force_contact_force),
            )
            observation = public_body_observation_from_channels(
                sim_time_s=last_time_s,
                channels=channels,
                metadata={"public_feedback_source": "schaffer_behavior"},
            )
            pool_rates = encoder.encode(observation, _zero_vision()).pool_rates
            backend.step(pool_rates, num_steps=num_steps)
        brain_features = _current_feature_vector(
            backend,
            basis,
            include_global_features=include_global_features,
            include_regressor_feature=False,
        )
        feature_offset = brain_features.size
        feature_matrix[:feature_offset, sample_index] = brain_features
        cursor = feature_offset
        if include_ball_motion_feature:
            feature_matrix[cursor, sample_index] = (
                float(ball_motion_values[sample_index]) if sample_index < ball_motion_values.size else 0.0
            )
            cursor += 1
        if include_behavioral_state_features and behavioral_state_values.size:
            width = behavioral_state_values.shape[0]
            feature_matrix[cursor : cursor + width, sample_index] = behavioral_state_values[:, sample_index]
        last_time_s = current_time_s

    return {
        "trial_id": trial.trial_id,
        "split": trial.split,
        "behavior_context": trial.behavior_context,
        "feature_names": feature_names,
        "timebase_s": timebase_s,
        "ball_motion_values": ball_motion_values,
        "behavioral_state_values": behavioral_state_values,
        "feature_matrix": feature_matrix,
        "session_key": _trial_session_key(trial),
        "session_start_time_s": float(session_time_offset_s),
        "session_stop_time_s": float(session_time_offset_s + (float(timebase_s[-1]) if timebase_s.size else 0.0)),
    }


def run_schaffer_spontaneous_fit(
    *,
    bundle_path: str | Path,
    replay_config: SchafferReplayConfig,
    output_dir: str | Path,
    trial_id_allowlist: Sequence[str] | None = None,
    fit_splits: Sequence[str] | None = None,
    fit_trial_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    backend, config = build_backend_from_config(replay_config.brain_config_path, device_override=replay_config.device)
    encoder_cfg = EncoderConfig.from_mapping(config.get("encoder"))
    encoder = SensoryEncoder(encoder_cfg)
    basis = build_family_basis_operators(
        backend,
        config,
        min_family_size_per_side=replay_config.min_family_size_per_side,
        max_family_size_per_side=replay_config.max_family_size_per_side,
        include_asymmetry_basis=replay_config.include_asymmetry_basis,
    )
    trials = load_schaffer_canonical_trial_data(bundle_path)
    allow = {str(value) for value in (trial_id_allowlist or [])}
    if allow:
        trials = [trial for trial in trials if trial.trial_id in allow]
    if not trials:
        raise ValueError("No Schaffer trials available for spontaneous fit")
    observation_taus_s = normalize_observation_taus(replay_config.observation_taus_s)
    selected_output_dims = {int(trial.matrix.shape[0]) for trial in trials}
    if len(selected_output_dims) != 1:
        raise ValueError(
            "Selected Schaffer trials do not share one trace count; use trial_id_allowlist within one session"
        )

    fit_split_set = {str(value) for value in (fit_splits or ("train",))}
    fit_trial_id_set = {str(value) for value in (fit_trial_ids or ())}
    def _selected_for_fit(trial: SchafferCanonicalTrialData) -> bool:
        if fit_trial_id_set:
            return trial.trial_id in fit_trial_id_set
        return trial.split in fit_split_set
    feature_rows: list[dict[str, Any]] = []
    if replay_config.preserve_state_within_session:
        session_groups: dict[str, list[SchafferCanonicalTrialData]] = {}
        for trial in trials:
            session_groups.setdefault(_trial_session_key(trial), []).append(trial)
        ordered_trials: list[SchafferCanonicalTrialData] = []
        for _, session_trials in sorted(session_groups.items(), key=lambda item: item[0]):
            ordered_trials.extend(sorted(session_trials, key=_trial_start_time_s))
        session_seed_index = 0
        previous_session_key: str | None = None
        previous_stop_s = 0.0
        for trial in ordered_trials:
            session_key = _trial_session_key(trial)
            start_s = _trial_start_time_s(trial)
            reset_backend = session_key != previous_session_key
            pre_gap_s = 0.0 if reset_backend else max(0.0, start_s - previous_stop_s)
            feature_rows.append(
                simulate_schaffer_trial_feature_matrix(
                    backend,
                    basis,
                    trial,
                    encoder=encoder,
                    warmup_s=float(replay_config.warmup_s),
                    seed=int(replay_config.seed + session_seed_index),
                    force_forward_speed=float(replay_config.force_forward_speed),
                    force_contact_force=float(replay_config.force_contact_force),
                    include_global_features=bool(replay_config.include_global_features),
                    include_ball_motion_feature=bool(replay_config.include_ball_motion_feature),
                    include_behavioral_state_features=bool(replay_config.include_behavioral_state_features),
                    reset_backend=reset_backend,
                    session_time_offset_s=float(start_s),
                    pre_gap_s=float(pre_gap_s),
                )
            )
            if reset_backend:
                session_seed_index += 1
            previous_session_key = session_key
            previous_stop_s = _trial_stop_time_s(trial)
        trials = ordered_trials
    else:
        for trial_index, trial in enumerate(trials):
            feature_rows.append(
                simulate_schaffer_trial_feature_matrix(
                    backend,
                    basis,
                    trial,
                    encoder=encoder,
                    warmup_s=float(replay_config.warmup_s),
                    seed=int(replay_config.seed + trial_index),
                    force_forward_speed=float(replay_config.force_forward_speed),
                    force_contact_force=float(replay_config.force_contact_force),
                    include_global_features=bool(replay_config.include_global_features),
                    include_ball_motion_feature=bool(replay_config.include_ball_motion_feature),
                    include_behavioral_state_features=bool(replay_config.include_behavioral_state_features),
                )
            )

    if observation_taus_s and replay_config.preserve_state_within_session:
        grouped_rows: dict[str, list[dict[str, Any]]] = {}
        for row in feature_rows:
            grouped_rows.setdefault(str(row["session_key"]), []).append(row)
        for session_key, rows in grouped_rows.items():
            rows.sort(key=lambda item: float(item["session_start_time_s"]))
            combined_timebase = np.concatenate(
                [
                    np.asarray(row["timebase_s"], dtype=np.float32) + float(row["session_start_time_s"])
                    for row in rows
                ],
                axis=0,
            ).astype(np.float32, copy=False)
            combined_features = np.concatenate(
                [np.asarray(row["feature_matrix"], dtype=np.float32) for row in rows],
                axis=1,
            ).astype(np.float32, copy=False)
            combined_augmented, combined_names = augment_feature_matrix_with_observation_basis(
                combined_features,
                combined_timebase,
                observation_taus_s=observation_taus_s,
                feature_names=rows[0]["feature_names"],
            )
            cursor = 0
            for row in rows:
                width = int(np.asarray(row["feature_matrix"]).shape[1])
                row["feature_matrix"] = combined_augmented[:, cursor : cursor + width].astype(np.float32, copy=False)
                row["feature_names"] = combined_names or tuple(str(value) for value in rows[0]["feature_names"])
                cursor += width
    else:
        for row in feature_rows:
            augmented_matrix, augmented_names = augment_feature_matrix_with_observation_basis(
                row["feature_matrix"],
                row["timebase_s"],
                observation_taus_s=observation_taus_s,
                feature_names=row["feature_names"],
            )
            row["feature_matrix"] = augmented_matrix
            row["feature_names"] = augmented_names or tuple(str(value) for value in row["feature_names"])

    if str(replay_config.readout_mode) == "tiny":
        fit_feature_rows = [row["feature_matrix"] for row, trial in zip(feature_rows, trials) if _selected_for_fit(trial)]
        if not fit_feature_rows:
            fit_feature_rows = [row["feature_matrix"] for row in feature_rows]
        selected_indices = choose_tiny_feature_indices_from_fit_rows(
            fit_feature_rows,
            feature_rows[0]["feature_names"],
            tiny_bilateral_limit=int(replay_config.tiny_bilateral_limit),
        )
        selected_names = tuple(str(feature_rows[0]["feature_names"][idx]) for idx in selected_indices)
        for row in feature_rows:
            row["feature_matrix"] = np.asarray(row["feature_matrix"], dtype=np.float32)[selected_indices]
            row["feature_names"] = selected_names
    else:
        for row in feature_rows:
            selected_matrix, selected_names = select_readout_feature_subset(
                row["feature_matrix"],
                row["feature_names"],
                readout_mode=str(replay_config.readout_mode),
                tiny_bilateral_limit=int(replay_config.tiny_bilateral_limit),
            )
            row["feature_matrix"] = selected_matrix
            row["feature_names"] = selected_names

    feature_names = tuple(str(value) for value in feature_rows[0]["feature_names"])

    fit_feature_matrices = [row["feature_matrix"] for row, trial in zip(feature_rows, trials) if _selected_for_fit(trial)]
    fit_observed_matrices = [trial.matrix for trial in trials if _selected_for_fit(trial)]
    fit_trial_ids_used = [trial.trial_id for trial in trials if _selected_for_fit(trial)]
    if not fit_feature_matrices:
        fit_feature_matrices = [row["feature_matrix"] for row in feature_rows]
        fit_observed_matrices = [trial.matrix for trial in trials]
        fit_trial_ids_used = [trial.trial_id for trial in trials]

    output_dims = {int(matrix.shape[0]) for matrix in fit_observed_matrices}
    if len(output_dims) != 1:
        raise ValueError(
            "Selected Schaffer fit trials do not share one trace count; use explicit fit_trial_ids within one session"
        )

    model = fit_reduced_linear_projection(
        fit_feature_matrices,
        fit_observed_matrices,
        feature_names=feature_names,
        fit_trial_ids=fit_trial_ids_used,
        max_basis_dim=int(replay_config.max_basis_dim),
        ridge_lambda=float(replay_config.ridge_lambda),
    )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    trial_summaries: list[dict[str, Any]] = []
    aggregate_rows: list[dict[str, Any]] = []
    for row, trial in zip(feature_rows, trials):
        predicted = apply_reduced_linear_projection(model, row["feature_matrix"])
        prediction_path = output_dir / f"{trial.trial_id}_predicted_matrix.npy"
        features_path = output_dir / f"{trial.trial_id}_feature_matrix.npy"
        ball_path = output_dir / f"{trial.trial_id}_ball_motion_values.npy"
        state_path = output_dir / f"{trial.trial_id}_behavioral_state_values.npy"
        np.save(prediction_path, predicted)
        np.save(features_path, row["feature_matrix"])
        np.save(ball_path, row["ball_motion_values"])
        np.save(state_path, row["behavioral_state_values"])
        score = score_schaffer_trial_matrix(
            trial,
            predicted,
            simulated_timebase_s=row["timebase_s"],
        )
        score["prediction_path"] = str(prediction_path)
        score["feature_matrix_path"] = str(features_path)
        score["ball_motion_values_path"] = str(ball_path)
        score["behavioral_state_values_path"] = str(state_path)
        score["ball_motion_mean"] = float(np.mean(row["ball_motion_values"])) if row["ball_motion_values"].size else 0.0
        score["behavioral_state_dim"] = int(row["behavioral_state_values"].shape[0])
        score["fit_selected"] = bool(trial.trial_id in fit_trial_ids_used)
        score["session_key"] = str(row["session_key"])
        score["session_start_time_s"] = float(row["session_start_time_s"])
        score["session_stop_time_s"] = float(row["session_stop_time_s"])
        trial_summaries.append(score)
        aggregate_rows.append(score["aggregate"])

    aggregate_summary = {
        "trial_count": len(trial_summaries),
        "mean_pearson_r": float(np.mean([row["mean_pearson_r"] for row in aggregate_rows])),
        "mean_rmse": float(np.mean([row["mean_rmse"] for row in aggregate_rows])),
        "mean_nrmse": float(np.mean([row["mean_nrmse"] for row in aggregate_rows])),
        "mean_abs_error": float(np.mean([row["mean_abs_error"] for row in aggregate_rows])),
        "mean_sign_agreement": float(np.mean([row["mean_sign_agreement"] for row in aggregate_rows])),
    }
    summary = {
        "bundle_path": str(Path(bundle_path).resolve()),
        "brain_config_path": str(Path(replay_config.brain_config_path).resolve()),
        "device": str(backend.device),
        "seed": int(replay_config.seed),
        "warmup_s": float(replay_config.warmup_s),
        "force_forward_speed": float(replay_config.force_forward_speed),
        "force_contact_force": float(replay_config.force_contact_force),
        "include_asymmetry_basis": bool(replay_config.include_asymmetry_basis),
        "include_global_features": bool(replay_config.include_global_features),
        "include_ball_motion_feature": bool(replay_config.include_ball_motion_feature),
        "include_behavioral_state_features": bool(replay_config.include_behavioral_state_features),
        "preserve_state_within_session": bool(replay_config.preserve_state_within_session),
        "observation_taus_s": [float(value) for value in observation_taus_s],
        "readout_mode": str(replay_config.readout_mode),
        "tiny_bilateral_limit": int(replay_config.tiny_bilateral_limit),
        "family_group_count": len(basis.groups),
        "feature_count": len(feature_names),
        "fit_trial_ids": list(model.fit_trial_ids),
        "fit_basis_dim": int(model.max_basis_dim),
        "ridge_lambda": float(model.ridge_lambda),
        "aggregate": aggregate_summary,
        "trial_summaries": trial_summaries,
    }
    summary_path = output_dir / "schaffer_spontaneous_fit_summary.json"
    model_path = output_dir / "schaffer_spontaneous_fit_model.npz"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    np.savez(
        model_path,
        feature_mean=model.feature_mean,
        feature_scale=model.feature_scale,
        projection_components=model.projection_components,
        beta=model.beta,
        feature_names=np.asarray(model.feature_names, dtype=object),
        fit_trial_ids=np.asarray(model.fit_trial_ids, dtype=object),
    )
    summary["summary_path"] = str(summary_path)
    summary["model_path"] = str(model_path)
    return summary

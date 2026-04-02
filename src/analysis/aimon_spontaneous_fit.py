from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import torch
import yaml

from analysis.aimon_parity_harness import (
    AimonCanonicalTrialData,
    load_aimon_canonical_trial_data,
    score_aimon_trial_matrix,
)
from analysis.imaging_observation_model import (
    augment_feature_matrix_with_observation_basis,
    normalize_observation_taus,
)
from analysis.public_body_feedback import (
    public_body_feedback_from_aimon_regressor,
    public_body_observation_from_channels,
)
from analysis.spontaneous_mesoscale_validation import FamilySideGroup, build_family_side_groups
from brain.pytorch_backend import WholeBrainTorchBackend
from bridge.encoder import EncoderConfig, SensoryEncoder
from vision.feature_extractor import VisionFeatures


@dataclass(frozen=True)
class AimonReplayConfig:
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
    include_regressor_feature: bool = True
    observation_taus_s: tuple[float, ...] = ()
    readout_mode: str = "reduced"
    tiny_bilateral_limit: int = 4
    min_family_size_per_side: int = 2
    max_family_size_per_side: int = 128


@dataclass(frozen=True)
class FamilyBasisOperators:
    groups: tuple[FamilySideGroup, ...]
    bilateral_operator: torch.Tensor
    asymmetry_operator: torch.Tensor | None
    feature_names: tuple[str, ...]


@dataclass(frozen=True)
class ReducedLinearProjection:
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    projection_components: np.ndarray
    beta: np.ndarray
    max_basis_dim: int
    ridge_lambda: float
    output_dim: int
    feature_names: tuple[str, ...]
    fit_trial_ids: tuple[str, ...]


@dataclass(frozen=True)
class TrialExecutionPlan:
    trial_id: str
    source_trial_id: str
    reset_state: bool
    seed: int


def load_brain_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_backend_from_config(
    config_path: str | Path,
    *,
    device_override: str | None = None,
) -> tuple[WholeBrainTorchBackend, dict[str, Any]]:
    config = load_brain_config(config_path)
    brain_cfg = dict(config.get("brain", {}))
    backend = WholeBrainTorchBackend(
        completeness_path=brain_cfg["completeness_path"],
        connectivity_path=brain_cfg["connectivity_path"],
        cache_dir=brain_cfg.get("cache_dir", "outputs/cache"),
        device=str(device_override or brain_cfg.get("device", "cpu")),
        dt_ms=float(brain_cfg.get("dt_ms", 0.1)),
        spontaneous_state=brain_cfg.get("spontaneous_state"),
        backend_dynamics=brain_cfg.get("backend_dynamics"),
    )
    return backend, config


def _annotation_path_for_basis(config: Mapping[str, Any], backend: WholeBrainTorchBackend) -> Path:
    visual_splice_cfg = dict(config.get("visual_splice", {}))
    candidate = str(getattr(backend.spontaneous_state, "annotation_path", "") or "").strip()
    if candidate:
        return Path(candidate)
    return Path(str(visual_splice_cfg.get("annotation_path", "outputs/cache/flywire_annotation_supplement.tsv")))


def build_family_basis_operators(
    backend: WholeBrainTorchBackend,
    config: Mapping[str, Any],
    *,
    min_family_size_per_side: int,
    max_family_size_per_side: int,
    include_asymmetry_basis: bool,
) -> FamilyBasisOperators:
    annotation_path = _annotation_path_for_basis(config, backend)
    groups = tuple(
        build_family_side_groups(
            annotation_path=annotation_path,
            completeness_path=backend.completeness_path,
            included_super_classes=getattr(backend.spontaneous_state, "included_super_classes", ()),
            min_size_per_side=int(min_family_size_per_side),
            max_size_per_side=int(max_family_size_per_side),
        )
    )
    if not groups:
        raise ValueError("No family-side groups available for Aimon spontaneous fit basis")
    size = int(backend.weights.shape[0])
    bilateral_rows: list[int] = []
    bilateral_cols: list[int] = []
    bilateral_vals: list[float] = []
    asym_rows: list[int] = []
    asym_cols: list[int] = []
    asym_vals: list[float] = []
    feature_names: list[str] = []
    for row_index, group in enumerate(groups):
        left_weight = 0.5 / max(len(group.left_indices), 1)
        right_weight = 0.5 / max(len(group.right_indices), 1)
        for index in group.left_indices:
            bilateral_rows.append(row_index)
            bilateral_cols.append(int(index))
            bilateral_vals.append(float(left_weight))
            if include_asymmetry_basis:
                asym_rows.append(row_index)
                asym_cols.append(int(index))
                asym_vals.append(float(-1.0 / max(len(group.left_indices), 1)))
        for index in group.right_indices:
            bilateral_rows.append(row_index)
            bilateral_cols.append(int(index))
            bilateral_vals.append(float(right_weight))
            if include_asymmetry_basis:
                asym_rows.append(row_index)
                asym_cols.append(int(index))
                asym_vals.append(float(1.0 / max(len(group.right_indices), 1)))
        feature_names.append(f"bilateral::{group.family}")
    bilateral_indices = torch.tensor([bilateral_rows, bilateral_cols], dtype=torch.long, device=backend.device)
    bilateral_values = torch.tensor(bilateral_vals, dtype=torch.float32, device=backend.device)
    bilateral_operator = torch.sparse_coo_tensor(
        bilateral_indices,
        bilateral_values,
        size=(len(groups), size),
        device=backend.device,
        dtype=torch.float32,
    ).coalesce()
    asymmetry_operator = None
    if include_asymmetry_basis:
        asym_indices = torch.tensor([asym_rows, asym_cols], dtype=torch.long, device=backend.device)
        asym_values = torch.tensor(asym_vals, dtype=torch.float32, device=backend.device)
        asymmetry_operator = torch.sparse_coo_tensor(
            asym_indices,
            asym_values,
            size=(len(groups), size),
            device=backend.device,
            dtype=torch.float32,
        ).coalesce()
        feature_names.extend(f"asymmetry::{group.family}" for group in groups)
    return FamilyBasisOperators(
        groups=groups,
        bilateral_operator=bilateral_operator,
        asymmetry_operator=asymmetry_operator,
        feature_names=tuple(feature_names),
    )


def _global_feature_names() -> tuple[str, ...]:
    return (
        "global::spike_fraction",
        "global::mean_voltage",
        "global::voltage_std",
        "global::mean_conductance",
        "global::conductance_std",
        "global::background_mean_rate_hz",
        "global::background_active_fraction",
        "global::background_latent_mean_abs_hz",
        "global::background_latent_std_hz",
        "global::intrinsic_adaptation_mean_abs",
        "global::intrinsic_noise_mean_abs",
        "global::graded_release_mean",
        "global::intracellular_calcium_mean",
        "global::distributed_context_exc_mean",
        "global::distributed_context_inh_mean",
        "global::distributed_context_mod_mean",
        "global::synapse_fast_exc_mean_abs",
        "global::synapse_slow_exc_mean_abs",
        "global::synapse_fast_inh_mean_abs",
        "global::synapse_slow_inh_mean_abs",
        "global::synapse_modulatory_mean_abs",
        "global::modulatory_arousal_mean",
        "global::modulatory_exafference_mean",
        "global::public_exafference_target_mean",
    )


def _trial_source_id(trial: AimonCanonicalTrialData) -> str:
    return str(trial.metadata.get("source_trial_id", trial.trial_id))


def build_trial_execution_plan(
    trials: Sequence[AimonCanonicalTrialData],
    *,
    base_seed: int,
    preserve_continuity_by_source_trial: bool = False,
) -> list[TrialExecutionPlan]:
    plans: list[TrialExecutionPlan] = []
    previous_source_id: str | None = None
    previous_stop_index: int | None = None
    sequence_index = -1
    for trial in trials:
        source_trial_id = _trial_source_id(trial)
        reset_state = True
        if preserve_continuity_by_source_trial and source_trial_id == previous_source_id:
            current_start = trial.metadata.get("window_start_index")
            if current_start is not None and previous_stop_index is not None and int(current_start) == int(previous_stop_index):
                reset_state = False
        if reset_state:
            sequence_index += 1
        plans.append(
            TrialExecutionPlan(
                trial_id=str(trial.trial_id),
                source_trial_id=source_trial_id,
                reset_state=bool(reset_state),
                seed=int(base_seed + sequence_index),
            )
        )
        previous_source_id = source_trial_id
        previous_stop = trial.metadata.get("window_stop_index")
        previous_stop_index = int(previous_stop) if previous_stop is not None else None
    return plans


def _current_feature_vector(
    backend: WholeBrainTorchBackend,
    basis: FamilyBasisOperators,
    *,
    include_global_features: bool,
    regressor_value: float | None = None,
    include_regressor_feature: bool = False,
) -> np.ndarray:
    voltage = backend.v[0].detach()
    bilateral = torch.sparse.mm(basis.bilateral_operator, voltage.reshape(-1, 1)).reshape(-1)
    features = [bilateral]
    if basis.asymmetry_operator is not None:
        asymmetry = torch.sparse.mm(basis.asymmetry_operator, voltage.reshape(-1, 1)).reshape(-1)
        features.append(asymmetry)
    if include_global_features:
        summary = backend.state_summary()
        features.append(
            torch.tensor(
                [
                    float(summary["global_spike_fraction"]),
                    float(summary["global_mean_voltage"]),
                    float(summary["global_voltage_std"]),
                    float(summary["global_mean_conductance"]),
                    float(summary["global_conductance_std"]),
                    float(summary["background_mean_rate_hz"]),
                    float(summary["background_active_fraction"]),
                    float(summary["background_latent_mean_abs_hz"]),
                    float(summary["background_latent_std_hz"]),
                    float(summary["intrinsic_adaptation_mean_abs"]),
                    float(summary["intrinsic_noise_mean_abs"]),
                    float(summary["graded_release_mean"]),
                    float(summary["intracellular_calcium_mean"]),
                    float(summary["distributed_context_exc_mean"]),
                    float(summary["distributed_context_inh_mean"]),
                    float(summary["distributed_context_mod_mean"]),
                    float(summary["synapse_fast_exc_mean_abs"]),
                    float(summary["synapse_slow_exc_mean_abs"]),
                    float(summary["synapse_fast_inh_mean_abs"]),
                    float(summary["synapse_slow_inh_mean_abs"]),
                    float(summary["synapse_modulatory_mean_abs"]),
                    float(summary["modulatory_arousal_mean"]),
                    float(summary["modulatory_exafference_mean"]),
                    float(summary["public_exafference_target_mean"]),
                ],
                dtype=torch.float32,
                device=backend.device,
            )
        )
    if include_regressor_feature:
        features.append(
            torch.tensor([float(regressor_value or 0.0)], dtype=torch.float32, device=backend.device)
        )
    return torch.cat(features).detach().cpu().numpy().astype(np.float32, copy=False)


def _feature_name_list(
    basis: FamilyBasisOperators,
    *,
    include_global_features: bool,
    include_regressor_feature: bool,
) -> tuple[str, ...]:
    names = list(basis.feature_names)
    if include_global_features:
        names.extend(_global_feature_names())
    if include_regressor_feature:
        names.append("covariate::public_regressor")
    return tuple(names)


def select_readout_feature_subset(
    feature_matrix: np.ndarray,
    feature_names: Sequence[str],
    *,
    readout_mode: str,
    tiny_bilateral_limit: int,
) -> tuple[np.ndarray, tuple[str, ...]]:
    names = tuple(str(value) for value in feature_names)
    matrix = np.asarray(feature_matrix, dtype=np.float32)
    if readout_mode == "reduced":
        return matrix, names
    if readout_mode != "tiny":
        raise ValueError(f"Unsupported readout_mode={readout_mode!r}; expected 'reduced' or 'tiny'")
    keep_indices: list[int] = []
    bilateral_kept = 0
    for idx, name in enumerate(names):
        if name.startswith("global::"):
            keep_indices.append(idx)
            continue
        if name.startswith("covariate::"):
            keep_indices.append(idx)
            continue
        if name.startswith("bilateral::") and bilateral_kept < max(0, int(tiny_bilateral_limit)):
            keep_indices.append(idx)
            bilateral_kept += 1
            continue
    if not keep_indices:
        keep_indices = [0]
    return matrix[np.asarray(keep_indices, dtype=np.int64)], tuple(names[idx] for idx in keep_indices)


def _feature_base_name(name: str) -> str:
    value = str(name)
    marker = "::obs_lp_tau_"
    if marker in value:
        return value.split(marker, 1)[0]
    return value


def choose_tiny_feature_indices_from_fit_rows(
    feature_matrices: Sequence[np.ndarray],
    feature_names: Sequence[str],
    *,
    tiny_bilateral_limit: int,
) -> np.ndarray:
    names = tuple(str(value) for value in feature_names)
    if not feature_matrices:
        return np.arange(len(names), dtype=np.int64)
    base_names = tuple(_feature_base_name(name) for name in names)
    always_keep: list[int] = []
    bilateral_groups: dict[str, list[int]] = {}
    for idx, (name, base_name) in enumerate(zip(names, base_names)):
        if name.startswith("global::") or name.startswith("covariate::"):
            always_keep.append(idx)
            continue
        if base_name.startswith("bilateral::"):
            bilateral_groups.setdefault(base_name, []).append(idx)
    selected_bases: set[str] = set()
    if bilateral_groups:
        scores: list[tuple[float, str]] = []
        for base_name, indices in bilateral_groups.items():
            total_score = 0.0
            for matrix in feature_matrices:
                block = np.asarray(matrix, dtype=np.float32)[np.asarray(indices, dtype=np.int64)]
                total_score += float(np.mean(np.std(block, axis=1))) if block.size else 0.0
            scores.append((total_score, base_name))
        scores.sort(key=lambda item: (-item[0], item[1]))
        selected_bases = {base_name for _, base_name in scores[: max(0, int(tiny_bilateral_limit))]}
    keep_indices = list(always_keep)
    for idx, base_name in enumerate(base_names):
        if base_name in selected_bases:
            keep_indices.append(idx)
    if not keep_indices:
        keep_indices = [0]
    keep_indices = sorted(set(int(idx) for idx in keep_indices))
    return np.asarray(keep_indices, dtype=np.int64)


def _zero_vision() -> VisionFeatures:
    return VisionFeatures(
        salience_left=0.0,
        salience_right=0.0,
        flow_left=0.0,
        flow_right=0.0,
    )


def _trial_regressor_values(trial: AimonCanonicalTrialData) -> np.ndarray:
    if "window_regressor_values" in trial.metadata:
        values = np.asarray(trial.metadata["window_regressor_values"], dtype=np.float32).reshape(-1)
        if values.size == trial.timebase_s.size:
            return values.astype(np.float32, copy=False)
        if values.size == 0:
            return np.zeros_like(trial.timebase_s, dtype=np.float32)
        source_time = np.linspace(0.0, 1.0, values.size, dtype=np.float32)
        target_time = np.linspace(0.0, 1.0, trial.timebase_s.size, dtype=np.float32)
        return np.interp(target_time, source_time, values).astype(np.float32)
    regressor_path = trial.behavior_paths.get("walk_regressor_path")
    if not regressor_path:
        return np.zeros_like(trial.timebase_s, dtype=np.float32)
    regressor = np.asarray(np.load(regressor_path), dtype=np.float32).reshape(-1)
    if regressor.size == 0:
        return np.zeros_like(trial.timebase_s, dtype=np.float32)
    parameters = dict(trial.stimulus.get("parameters", {}))
    start = max(0, int(parameters.get("window_start", 0)))
    stop = int(parameters.get("window_stop", regressor.size))
    if regressor.size == trial.timebase_s.size:
        sliced = regressor
    elif 0 <= start < stop <= regressor.size:
        sliced = regressor[start:stop]
    else:
        sliced = regressor
    if sliced.size == trial.timebase_s.size:
        return sliced.astype(np.float32, copy=False)
    if sliced.size == 1:
        return np.full_like(trial.timebase_s, float(sliced[0]), dtype=np.float32)
    target_time = np.linspace(0.0, 1.0, trial.timebase_s.size, dtype=np.float32)
    source_time = np.linspace(0.0, 1.0, sliced.size, dtype=np.float32)
    return np.interp(target_time, source_time, sliced).astype(np.float32)


def split_aimon_trial_into_windows(
    trial: AimonCanonicalTrialData,
    *,
    window_count: int,
    include_window_indices: Sequence[int] = (),
    fit_window_indices: Sequence[int] = (),
    test_window_indices: Sequence[int] = (),
) -> list[AimonCanonicalTrialData]:
    count = max(1, int(window_count))
    timebase = np.asarray(trial.timebase_s, dtype=np.float32).reshape(-1)
    matrix = np.asarray(trial.matrix, dtype=np.float32)
    if matrix.ndim != 2:
        raise ValueError("Aimon trial matrix must be 2D")
    if matrix.shape[1] != timebase.size:
        raise ValueError("Aimon trial matrix/timebase length mismatch")
    regressor_values = _trial_regressor_values(trial)
    include_set = {int(value) for value in include_window_indices}
    fit_set = {int(value) for value in fit_window_indices}
    test_set = {int(value) for value in test_window_indices}
    bounds = np.linspace(0, timebase.size, count + 1, dtype=np.int64)
    rows: list[AimonCanonicalTrialData] = []
    for window_index, (start, stop) in enumerate(zip(bounds[:-1], bounds[1:])):
        if include_set and window_index not in include_set:
            continue
        start_i = int(start)
        stop_i = int(stop)
        if stop_i <= start_i:
            continue
        if fit_set:
            split = "train" if window_index in fit_set else "test"
        elif test_set:
            split = "test" if window_index in test_set else "train"
        else:
            split = "train" if window_index < max(1, count - 1) else "test"
        window_timebase = timebase[start_i:stop_i].astype(np.float32, copy=False)
        window_timebase = window_timebase - float(window_timebase[0])
        metadata = dict(trial.metadata)
        metadata.update(
            {
                "source_trial_id": str(trial.trial_id),
                "window_index": int(window_index),
                "window_count": int(count),
                "window_start_index": int(start_i),
                "window_stop_index": int(stop_i),
                "window_regressor_values": regressor_values[start_i:stop_i].astype(np.float32, copy=False),
            }
        )
        rows.append(
            AimonCanonicalTrialData(
                trial_id=f"{trial.trial_id}__win_{window_index:02d}",
                split=split,
                behavior_context=str(trial.behavior_context),
                matrix=matrix[:, start_i:stop_i].astype(np.float32, copy=False),
                timebase_s=window_timebase,
                stimulus=dict(trial.stimulus),
                behavior_paths=dict(trial.behavior_paths),
                metadata=metadata,
            )
        )
    if not rows:
        raise ValueError("Window split produced no Aimon trials")
    return rows


def _sensor_pool_rates_from_regressor_value(
    encoder: SensoryEncoder,
    *,
    sim_time_s: float,
    timebase_s: np.ndarray,
    regressor_values: np.ndarray,
    sample_index: int,
    force_forward_speed: float,
    force_contact_force: float,
) -> dict[str, float]:
    channels = public_body_feedback_from_aimon_regressor(
        timebase_s=np.asarray(timebase_s, dtype=np.float32),
        regressor_values=np.asarray(regressor_values, dtype=np.float32),
        sample_index=int(sample_index),
        forward_speed_scale=float(force_forward_speed),
        contact_force_scale=float(force_contact_force),
    )
    observation = public_body_observation_from_channels(
        sim_time_s=float(sim_time_s),
        channels=channels,
        metadata={"public_feedback_source": "aimon_regressor"},
    )
    return encoder.encode(observation, _zero_vision()).pool_rates


def simulate_trial_feature_matrix(
    backend: WholeBrainTorchBackend,
    basis: FamilyBasisOperators,
    trial: AimonCanonicalTrialData,
    *,
    encoder: SensoryEncoder,
    warmup_s: float,
    seed: int,
    reset_state: bool,
    force_forward_speed: float,
    force_contact_force: float,
    include_global_features: bool,
    include_regressor_feature: bool,
) -> dict[str, Any]:
    if reset_state:
        backend.reset(seed=int(seed))
        warmup_steps = int(round(float(warmup_s) * 1000.0 / float(backend.dt_ms)))
        if warmup_steps > 0:
            backend.step({}, num_steps=warmup_steps)
    timebase_s = np.asarray(trial.timebase_s, dtype=np.float32).reshape(-1)
    regressor_values = _trial_regressor_values(trial)
    feature_names = _feature_name_list(
        basis,
        include_global_features=include_global_features,
        include_regressor_feature=include_regressor_feature,
    )
    feature_matrix = np.zeros((len(feature_names), timebase_s.size), dtype=np.float32)
    last_time_s = 0.0
    for sample_index in range(timebase_s.size):
        current_time_s = float(timebase_s[sample_index])
        if sample_index > 0:
            delta_s = max(0.0, current_time_s - last_time_s)
            num_steps = max(1, int(round(delta_s * 1000.0 / float(backend.dt_ms))))
            pool_rates = _sensor_pool_rates_from_regressor_value(
                encoder,
                sim_time_s=last_time_s,
                timebase_s=timebase_s,
                regressor_values=regressor_values,
                sample_index=sample_index - 1,
                force_forward_speed=force_forward_speed,
                force_contact_force=force_contact_force,
            )
            backend.step(pool_rates, num_steps=num_steps)
        feature_matrix[:, sample_index] = _current_feature_vector(
            backend,
            basis,
            include_global_features=include_global_features,
            regressor_value=float(regressor_values[sample_index]) if sample_index < regressor_values.size else 0.0,
            include_regressor_feature=include_regressor_feature,
        )
        last_time_s = current_time_s
    return {
        "trial_id": trial.trial_id,
        "split": trial.split,
        "behavior_context": trial.behavior_context,
        "feature_names": feature_names,
        "timebase_s": timebase_s,
        "regressor_values": regressor_values,
        "feature_matrix": feature_matrix,
    }


def fit_reduced_linear_projection(
    feature_matrices: Sequence[np.ndarray],
    observed_matrices: Sequence[np.ndarray],
    *,
    feature_names: Sequence[str],
    fit_trial_ids: Sequence[str],
    max_basis_dim: int,
    ridge_lambda: float,
) -> ReducedLinearProjection:
    if not feature_matrices or not observed_matrices:
        raise ValueError("feature_matrices and observed_matrices must be non-empty")
    x_rows = np.concatenate([matrix.T for matrix in feature_matrices], axis=0).astype(np.float64)
    y_rows = np.concatenate([matrix.T for matrix in observed_matrices], axis=0).astype(np.float64)
    if x_rows.shape[0] != y_rows.shape[0]:
        raise ValueError("feature and observed sample counts must match")
    x_rows = np.nan_to_num(x_rows, nan=0.0, posinf=0.0, neginf=0.0)
    y_rows = np.nan_to_num(y_rows, nan=0.0, posinf=0.0, neginf=0.0)
    feature_mean = x_rows.mean(axis=0, dtype=np.float64)
    feature_scale = x_rows.std(axis=0, dtype=np.float64)
    feature_scale = np.where(np.isfinite(feature_scale) & (feature_scale > 1e-6), feature_scale, 1.0)
    x_norm = np.nan_to_num((x_rows - feature_mean) / feature_scale, nan=0.0, posinf=0.0, neginf=0.0)
    try:
        _, singular_values, vt = np.linalg.svd(x_norm, full_matrices=False)
    except np.linalg.LinAlgError:
        covariance = np.nan_to_num(x_norm.T @ x_norm, nan=0.0, posinf=0.0, neginf=0.0)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        order = np.argsort(eigenvalues)[::-1]
        eigenvalues = np.clip(eigenvalues[order], a_min=0.0, a_max=None)
        singular_values = np.sqrt(eigenvalues)
        vt = eigenvectors[:, order].T
    keep_dim = max(1, min(int(max_basis_dim), int(vt.shape[0]), int(np.count_nonzero(singular_values > 1e-6)) or 1))
    components = vt[:keep_dim].astype(np.float64)
    reduced = np.nan_to_num(x_norm @ components.T, nan=0.0, posinf=0.0, neginf=0.0)
    design = np.concatenate([np.ones((reduced.shape[0], 1), dtype=np.float64), reduced], axis=1)
    gram = design.T @ design
    penalty = np.eye(gram.shape[0], dtype=np.float64) * float(ridge_lambda)
    penalty[0, 0] = 0.0
    rhs = design.T @ y_rows
    try:
        beta = np.linalg.solve(gram + penalty, rhs)
    except np.linalg.LinAlgError:
        beta, *_ = np.linalg.lstsq(gram + penalty, rhs, rcond=None)
    beta = np.nan_to_num(beta, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    return ReducedLinearProjection(
        feature_mean=feature_mean.astype(np.float32),
        feature_scale=feature_scale.astype(np.float32),
        projection_components=components.astype(np.float32),
        beta=beta,
        max_basis_dim=int(keep_dim),
        ridge_lambda=float(ridge_lambda),
        output_dim=int(y_rows.shape[1]),
        feature_names=tuple(str(name) for name in feature_names),
        fit_trial_ids=tuple(str(value) for value in fit_trial_ids),
    )


def apply_reduced_linear_projection(model: ReducedLinearProjection, feature_matrix: np.ndarray) -> np.ndarray:
    features = np.asarray(feature_matrix, dtype=np.float32)
    x_rows = np.nan_to_num(features.T.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    x_norm = np.nan_to_num((x_rows - model.feature_mean) / model.feature_scale, nan=0.0, posinf=0.0, neginf=0.0)
    reduced = np.nan_to_num(x_norm @ model.projection_components.T, nan=0.0, posinf=0.0, neginf=0.0)
    design = np.concatenate([np.ones((reduced.shape[0], 1), dtype=np.float32), reduced], axis=1)
    predicted = np.nan_to_num(design @ model.beta, nan=0.0, posinf=0.0, neginf=0.0)
    return predicted.T.astype(np.float32, copy=False)


def run_aimon_spontaneous_fit(
    *,
    bundle_path: str | Path,
    replay_config: AimonReplayConfig,
    output_dir: str | Path,
    trial_id_allowlist: Sequence[str] | None = None,
    fit_splits: Sequence[str] | None = None,
    trial_data_override: Sequence[AimonCanonicalTrialData] | None = None,
    preserve_continuity_by_source_trial: bool = False,
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
    trials = list(trial_data_override) if trial_data_override is not None else load_aimon_canonical_trial_data(bundle_path)
    allow = {str(value) for value in (trial_id_allowlist or [])}
    if allow:
        trials = [trial for trial in trials if trial.trial_id in allow]
    if not trials:
        raise ValueError("No Aimon trials available for spontaneous fit")
    observation_taus_s = normalize_observation_taus(replay_config.observation_taus_s)
    fit_split_set = {str(value) for value in (fit_splits or ("train",))}
    execution_plan = build_trial_execution_plan(
        trials,
        base_seed=int(replay_config.seed),
        preserve_continuity_by_source_trial=bool(preserve_continuity_by_source_trial),
    )
    feature_rows: list[dict[str, Any]] = []
    for trial, plan in zip(trials, execution_plan):
        row = simulate_trial_feature_matrix(
            backend,
            basis,
            trial,
            encoder=encoder,
            warmup_s=float(replay_config.warmup_s),
            seed=int(plan.seed),
            reset_state=bool(plan.reset_state),
            force_forward_speed=float(replay_config.force_forward_speed),
            force_contact_force=float(replay_config.force_contact_force),
            include_global_features=bool(replay_config.include_global_features),
            include_regressor_feature=bool(replay_config.include_regressor_feature),
        )
        augmented_matrix, augmented_names = augment_feature_matrix_with_observation_basis(
            row["feature_matrix"],
            row["timebase_s"],
            observation_taus_s=observation_taus_s,
            feature_names=row["feature_names"],
        )
        row["feature_matrix"] = augmented_matrix
        row["feature_names"] = augmented_names or tuple(str(value) for value in row["feature_names"])
        feature_rows.append(row)
    if str(replay_config.readout_mode) == "tiny":
        fit_feature_rows = [row["feature_matrix"] for row, trial in zip(feature_rows, trials) if trial.split in fit_split_set]
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
    fit_feature_matrices = [row["feature_matrix"] for row, trial in zip(feature_rows, trials) if trial.split in fit_split_set]
    fit_observed_matrices = [trial.matrix for trial in trials if trial.split in fit_split_set]
    fit_trial_ids = [trial.trial_id for trial in trials if trial.split in fit_split_set]
    if not fit_feature_matrices:
        fit_feature_matrices = [row["feature_matrix"] for row in feature_rows]
        fit_observed_matrices = [trial.matrix for trial in trials]
        fit_trial_ids = [trial.trial_id for trial in trials]
    model = fit_reduced_linear_projection(
        fit_feature_matrices,
        fit_observed_matrices,
        feature_names=feature_names,
        fit_trial_ids=fit_trial_ids,
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
        regressor_path = output_dir / f"{trial.trial_id}_regressor_values.npy"
        np.save(prediction_path, predicted)
        np.save(features_path, row["feature_matrix"])
        np.save(regressor_path, row["regressor_values"])
        score = score_aimon_trial_matrix(
            trial,
            predicted,
            simulated_timebase_s=row["timebase_s"],
        )
        score["prediction_path"] = str(prediction_path)
        score["feature_matrix_path"] = str(features_path)
        score["regressor_values_path"] = str(regressor_path)
        score["regressor_mean"] = float(np.mean(row["regressor_values"])) if row["regressor_values"].size else 0.0
        score["regressor_max"] = float(np.max(row["regressor_values"])) if row["regressor_values"].size else 0.0
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
        "include_regressor_feature": bool(replay_config.include_regressor_feature),
        "observation_taus_s": [float(value) for value in observation_taus_s],
        "readout_mode": str(replay_config.readout_mode),
        "tiny_bilateral_limit": int(replay_config.tiny_bilateral_limit),
        "family_group_count": len(basis.groups),
        "feature_count": len(feature_names),
        "fit_trial_ids": list(model.fit_trial_ids),
        "preserve_continuity_by_source_trial": bool(preserve_continuity_by_source_trial),
        "execution_plan": [
            {
                "trial_id": plan.trial_id,
                "source_trial_id": plan.source_trial_id,
                "reset_state": bool(plan.reset_state),
                "seed": int(plan.seed),
            }
            for plan in execution_plan
        ],
        "fit_basis_dim": int(model.max_basis_dim),
        "ridge_lambda": float(model.ridge_lambda),
        "aggregate": aggregate_summary,
        "trial_summaries": trial_summaries,
    }
    summary_path = output_dir / "aimon_spontaneous_fit_summary.json"
    model_path = output_dir / "aimon_spontaneous_fit_model.npz"
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

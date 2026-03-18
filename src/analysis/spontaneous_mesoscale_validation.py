from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis.aimon_public_comparator import summarize_public_forced_vs_spontaneous_walk
from analysis.behavior_metrics import load_run_records
from analysis.best_branch_investigation import align_framewise_matrix, pearson_correlation
from analysis.mesoscale_validation import family_structure_function_metrics
from analysis.public_spontaneous_dataset import inspect_local_spontaneous_dataset
from brain.flywire_annotations import load_flywire_annotation_table


@dataclass(frozen=True)
class FamilySideGroup:
    family: str
    super_class: str
    left_indices: tuple[int, ...]
    right_indices: tuple[int, ...]


def load_activation_capture(path: str | Path) -> dict[str, np.ndarray]:
    capture = np.load(Path(path), allow_pickle=True)
    return {key: capture[key] for key in capture.files}


def load_completeness_root_ids(path: str | Path) -> np.ndarray:
    completeness = pd.read_csv(path, index_col=0)
    return completeness.index.to_numpy(dtype=np.int64)


def build_family_side_groups(
    *,
    annotation_path: str | Path,
    completeness_path: str | Path,
    included_super_classes: Iterable[str],
    min_size_per_side: int,
    max_size_per_side: int,
) -> list[FamilySideGroup]:
    annotation_table = load_flywire_annotation_table(annotation_path)
    root_ids = load_completeness_root_ids(completeness_path)
    index_by_root_id = {int(root_id): idx for idx, root_id in enumerate(root_ids.tolist())}
    annotation_table = annotation_table[annotation_table["root_id"].isin(index_by_root_id)].copy()
    annotation_table = annotation_table[annotation_table["side"].isin(["left", "right"])].copy()
    allowed = {str(value).lower() for value in included_super_classes if str(value).strip()}
    if allowed and "super_class" in annotation_table.columns:
        annotation_table = annotation_table[
            annotation_table["super_class"].fillna("").astype(str).str.lower().isin(allowed)
        ].copy()
    family = annotation_table["cell_type"].fillna("").astype(str)
    hemibrain = annotation_table.get("hemibrain_type", pd.Series(index=annotation_table.index, dtype=object)).fillna("").astype(str)
    annotation_table["family"] = family.where(family.str.len() > 0, hemibrain)
    annotation_table = annotation_table[annotation_table["family"].str.len() > 0].copy()
    groups: list[FamilySideGroup] = []
    max_size = max(0, int(max_size_per_side))
    for family_name, group_df in annotation_table.groupby("family", sort=True):
        left_indices = tuple(
            sorted(
                index_by_root_id[int(root_id)]
                for root_id in group_df.loc[group_df["side"] == "left", "root_id"].tolist()
                if int(root_id) in index_by_root_id
            )
        )
        right_indices = tuple(
            sorted(
                index_by_root_id[int(root_id)]
                for root_id in group_df.loc[group_df["side"] == "right", "root_id"].tolist()
                if int(root_id) in index_by_root_id
            )
        )
        if len(left_indices) < int(min_size_per_side) or len(right_indices) < int(min_size_per_side):
            continue
        if max_size > 0 and (len(left_indices) > max_size or len(right_indices) > max_size):
            continue
        super_class = ""
        if "super_class" in group_df.columns and not group_df["super_class"].empty:
            super_class = str(group_df["super_class"].iloc[0])
        groups.append(
            FamilySideGroup(
                family=str(family_name),
                super_class=super_class,
                left_indices=left_indices,
                right_indices=right_indices,
            )
        )
    return groups


def build_root_annotation_table(
    *,
    annotation_path: str | Path,
    completeness_path: str | Path,
    included_super_classes: Iterable[str],
) -> pd.DataFrame:
    annotation_table = load_flywire_annotation_table(annotation_path)
    root_ids = load_completeness_root_ids(completeness_path)
    root_df = pd.DataFrame({"root_id": root_ids.astype(np.int64)})
    annotation_table = annotation_table[annotation_table["root_id"].isin(root_df["root_id"])].copy()
    family = annotation_table["cell_type"].fillna("").astype(str)
    hemibrain = annotation_table.get("hemibrain_type", pd.Series(index=annotation_table.index, dtype=object)).fillna("").astype(str)
    annotation_table["family"] = family.where(family.str.len() > 0, hemibrain)
    allowed = {str(value).lower() for value in included_super_classes if str(value).strip()}
    if allowed and "super_class" in annotation_table.columns:
        annotation_table = annotation_table[
            annotation_table["super_class"].fillna("").astype(str).str.lower().isin(allowed)
        ].copy()
    keep_columns = [column for column in ["root_id", "family", "super_class", "side"] if column in annotation_table.columns]
    deduped = annotation_table[keep_columns].drop_duplicates(subset=["root_id"], keep="first")
    root_annotation = root_df.merge(deduped, on="root_id", how="left")
    if "family" not in root_annotation.columns:
        root_annotation["family"] = ""
    if "super_class" not in root_annotation.columns:
        root_annotation["super_class"] = ""
    if "side" not in root_annotation.columns:
        root_annotation["side"] = ""
    return root_annotation


def _extract_run_traces(records: list[Mapping[str, Any]]) -> dict[str, np.ndarray]:
    sim_time = np.asarray([float(record.get("sim_time", 0.0)) for record in records], dtype=np.float32)
    forward_speed = np.asarray([float(record.get("forward_speed", 0.0)) for record in records], dtype=np.float32)
    yaw_rate = np.asarray([float(record.get("yaw_rate", 0.0)) for record in records], dtype=np.float32)
    left_drive = np.asarray([float(record.get("left_drive", 0.0)) for record in records], dtype=np.float32)
    right_drive = np.asarray([float(record.get("right_drive", 0.0)) for record in records], dtype=np.float32)
    forward_signal = np.asarray(
        [float(record.get("motor_signals", {}).get("forward_signal", 0.0)) for record in records],
        dtype=np.float32,
    )
    turn_signal = np.asarray(
        [float(record.get("motor_signals", {}).get("turn_signal", 0.0)) for record in records],
        dtype=np.float32,
    )
    global_spike_fraction = np.asarray(
        [float(record.get("brain_backend_state", {}).get("global_spike_fraction", 0.0)) for record in records],
        dtype=np.float32,
    )
    global_voltage_std = np.asarray(
        [float(record.get("brain_backend_state", {}).get("global_voltage_std", 0.0)) for record in records],
        dtype=np.float32,
    )
    background_mean_rate = np.asarray(
        [float(record.get("brain_backend_state", {}).get("background_mean_rate_hz", 0.0)) for record in records],
        dtype=np.float32,
    )
    background_active_fraction = np.asarray(
        [float(record.get("brain_backend_state", {}).get("background_active_fraction", 0.0)) for record in records],
        dtype=np.float32,
    )
    background_latent_mean_abs = np.asarray(
        [float(record.get("brain_backend_state", {}).get("background_latent_mean_abs_hz", 0.0)) for record in records],
        dtype=np.float32,
    )
    return {
        "sim_time": sim_time,
        "forward_speed": forward_speed,
        "yaw_rate": yaw_rate,
        "left_drive": left_drive,
        "right_drive": right_drive,
        "forward_signal": forward_signal,
        "turn_signal": turn_signal,
        "global_spike_fraction": global_spike_fraction,
        "global_voltage_std": global_voltage_std,
        "background_mean_rate_hz": background_mean_rate,
        "background_active_fraction": background_active_fraction,
        "background_latent_mean_abs_hz": background_latent_mean_abs,
    }


def _locomotor_active_mask(traces: Mapping[str, np.ndarray]) -> np.ndarray:
    mean_drive = 0.5 * (traces["left_drive"] + traces["right_drive"])
    return (
        (np.abs(mean_drive) > 0.05)
        | (traces["forward_signal"] > 0.05)
        | (traces["forward_speed"] > 1.0)
    )


def _find_state_onsets(mask: np.ndarray, *, min_pre: int, min_post: int) -> np.ndarray:
    active = np.asarray(mask, dtype=bool)
    starts = np.flatnonzero(~np.r_[False, active[:-1]] & active)
    keep = [idx for idx in starts.tolist() if idx >= int(min_pre) and idx + int(min_post) < active.size]
    return np.asarray(keep, dtype=np.int64)


def _event_locked_delta(signal: np.ndarray, onsets: np.ndarray, *, pre: int, post: int) -> tuple[float, np.ndarray]:
    if onsets.size == 0:
        return 0.0, np.zeros((0, pre + post + 1), dtype=np.float32)
    windows = np.stack([signal[idx - pre : idx + post + 1] for idx in onsets], axis=0).astype(np.float32)
    pre_mean = float(windows[:, :pre].mean()) if pre > 0 else float(windows.mean())
    post_mean = float(windows[:, pre + 1 :].mean()) if post > 0 else float(windows.mean())
    return float(post_mean - pre_mean), windows


def summarize_condition_dynamics(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    traces = _extract_run_traces(records)
    locomotor_active = _locomotor_active_mask(traces)
    dt = float(np.median(np.diff(traces["sim_time"]))) if traces["sim_time"].size > 1 else 0.0
    onset_window = max(10, int(round(0.1 / max(dt, 1e-6)))) if dt > 0.0 else 10
    onsets = _find_state_onsets(locomotor_active, min_pre=onset_window, min_post=onset_window)
    spike_delta, spike_windows = _event_locked_delta(
        traces["global_spike_fraction"],
        onsets,
        pre=onset_window,
        post=onset_window,
    )
    vstd_delta, vstd_windows = _event_locked_delta(
        traces["global_voltage_std"],
        onsets,
        pre=onset_window,
        post=onset_window,
    )
    return {
        "sample_count": int(traces["sim_time"].size),
        "dt_s": dt,
        "locomotor_onset_count": int(onsets.size),
        "forward_speed_mean": float(traces["forward_speed"].mean()),
        "global_spike_fraction_mean": float(traces["global_spike_fraction"].mean()),
        "global_voltage_std_mean": float(traces["global_voltage_std"].mean()),
        "background_mean_rate_hz_mean": float(traces["background_mean_rate_hz"].mean()),
        "background_active_fraction_mean": float(traces["background_active_fraction"].mean()),
        "background_latent_mean_abs_hz_mean": float(traces["background_latent_mean_abs_hz"].mean()),
        "speed_spike_corr": pearson_correlation(traces["forward_speed"], traces["global_spike_fraction"]),
        "speed_voltage_std_corr": pearson_correlation(traces["forward_speed"], traces["global_voltage_std"]),
        "yaw_spike_corr": pearson_correlation(np.abs(traces["yaw_rate"]), traces["global_spike_fraction"]),
        "yaw_voltage_std_corr": pearson_correlation(np.abs(traces["yaw_rate"]), traces["global_voltage_std"]),
        "onset_spike_delta": spike_delta,
        "onset_voltage_std_delta": vstd_delta,
        "onset_spike_curve": spike_windows.mean(axis=0).tolist() if spike_windows.size else [],
        "onset_voltage_std_curve": vstd_windows.mean(axis=0).tolist() if vstd_windows.size else [],
        "locomotor_active_fraction": float(locomotor_active.mean()),
    }


def _principal_component_metrics(matrix: np.ndarray, *, max_components: int = 10) -> dict[str, float]:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] < 3 or matrix.shape[1] < 2:
        return {
            "pc1_variance_ratio": float("nan"),
            "pc3_cumulative_variance_ratio": float("nan"),
            "participation_ratio_topk": float("nan"),
            "lag1_autocorr_mean": float("nan"),
        }
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    scales = matrix.std(axis=0, keepdims=True)
    centered = centered / np.where(scales > 1e-6, scales, 1.0)
    singular_values = np.linalg.svd(centered, full_matrices=False, compute_uv=False)
    eigenvalues = np.square(singular_values)
    if not np.isfinite(eigenvalues).any():
        return {
            "pc1_variance_ratio": float("nan"),
            "pc3_cumulative_variance_ratio": float("nan"),
            "participation_ratio_topk": float("nan"),
            "lag1_autocorr_mean": float("nan"),
        }
    keep = min(int(max_components), eigenvalues.size)
    top = eigenvalues[:keep]
    variance_ratio = top / max(float(np.sum(eigenvalues)), 1e-12)
    lag1_values = []
    for idx in range(centered.shape[1]):
        first = centered[:-1, idx]
        second = centered[1:, idx]
        if np.std(first) <= 1e-6 or np.std(second) <= 1e-6:
            continue
        lag1_values.append(float(np.corrcoef(first, second)[0, 1]))
    return {
        "pc1_variance_ratio": float(variance_ratio[0]) if variance_ratio.size else float("nan"),
        "pc3_cumulative_variance_ratio": float(np.sum(variance_ratio[:3])) if variance_ratio.size else float("nan"),
        "participation_ratio_topk": float((np.sum(variance_ratio) ** 2) / max(np.sum(np.square(variance_ratio)), 1e-12)),
        "lag1_autocorr_mean": float(np.mean(lag1_values)) if lag1_values else float("nan"),
    }


def _mean_abs_pairwise_corr(matrix: np.ndarray) -> float:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] < 2 or matrix.shape[1] < 3:
        return float("nan")
    corr = np.corrcoef(matrix)
    upper = corr[np.triu_indices(corr.shape[0], k=1)]
    upper = upper[np.isfinite(upper)]
    return float(np.mean(np.abs(upper))) if upper.size else float("nan")


def _circular_shift_rows(matrix: np.ndarray, *, seed: int = 0) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.ndim != 2:
        raise ValueError("matrix must be 2D")
    if matrix.shape[1] == 0:
        return matrix.copy()
    rng = np.random.default_rng(seed)
    shifted = np.empty_like(matrix)
    for row_idx in range(matrix.shape[0]):
        shifted[row_idx] = np.roll(matrix[row_idx], int(rng.integers(0, matrix.shape[1])))
    return shifted


def summarize_monitored_voltage_structure(capture: Mapping[str, Any]) -> dict[str, Any]:
    voltage_matrix = np.asarray(capture["monitored_voltage_matrix"], dtype=np.float32).T
    controller_matrix = np.asarray(capture["controller_matrix"], dtype=np.float32).T
    covariates = np.concatenate(
        [
            np.ones((controller_matrix.shape[0], 1), dtype=np.float32),
            controller_matrix,
        ],
        axis=1,
    )
    beta, *_ = np.linalg.lstsq(covariates, voltage_matrix, rcond=None)
    residual = voltage_matrix - covariates @ beta
    raw_metrics = _principal_component_metrics(voltage_matrix)
    residual_metrics = _principal_component_metrics(residual)
    return {
        "raw": raw_metrics,
        "residual": residual_metrics,
        "monitored_neuron_count": int(voltage_matrix.shape[1]),
    }


def summarize_family_voltage_structure(
    *,
    capture: Mapping[str, Any],
    family_groups: list[FamilySideGroup],
) -> dict[str, Any]:
    controller_labels = [str(value) for value in np.asarray(capture["controller_labels"]).tolist()]
    controller_matrix = align_framewise_matrix(
        np.asarray(capture["controller_matrix"], dtype=np.float32),
        np.asarray(capture["frame_cycles"], dtype=np.int64),
    )
    voltage_frames = np.asarray(capture["brain_voltage_frames"], dtype=np.float32)
    frame_count = min(int(controller_matrix.shape[1]), int(voltage_frames.shape[0]))
    controller_matrix = controller_matrix[:, :frame_count]
    voltage_frames = voltage_frames[:frame_count]
    controller_by_label = {
        label: controller_matrix[idx].astype(np.float32)
        for idx, label in enumerate(controller_labels)
    }
    turn_drive = controller_by_label.get("right_drive", np.zeros(controller_matrix.shape[1], dtype=np.float32)) - controller_by_label.get(
        "left_drive",
        np.zeros(controller_matrix.shape[1], dtype=np.float32),
    )
    bilateral_corrs: list[float] = []
    turn_rows: list[dict[str, Any]] = []
    bilateral_traces: list[np.ndarray] = []
    asymmetry_traces: list[np.ndarray] = []
    for group in family_groups:
        left = voltage_frames[:, list(group.left_indices)].mean(axis=1)
        right = voltage_frames[:, list(group.right_indices)].mean(axis=1)
        if np.std(left) > 1e-6 and np.std(right) > 1e-6:
            bilateral_corrs.append(float(np.corrcoef(left, right)[0, 1]))
        asym = right - left
        bilateral_traces.append((0.5 * (left + right)).astype(np.float32))
        asymmetry_traces.append(asym.astype(np.float32))
        turn_rows.append(
            {
                "family": group.family,
                "super_class": group.super_class,
                "left_count": int(len(group.left_indices)),
                "right_count": int(len(group.right_indices)),
                "bilateral_voltage_corr": pearson_correlation(left, right),
                "turn_drive_asym_corr": pearson_correlation(asym, turn_drive),
                "mean_abs_asym_mv": float(np.mean(np.abs(asym))),
            }
        )
    ordered_table = pd.DataFrame(turn_rows).reset_index(drop=True)
    table = ordered_table.sort_values("turn_drive_asym_corr", ascending=False).reset_index(drop=True) if not ordered_table.empty else ordered_table
    abs_turn = table["turn_drive_asym_corr"].abs().to_numpy(dtype=np.float32) if not table.empty else np.zeros(0, dtype=np.float32)
    bilateral_matrix = np.vstack(bilateral_traces).astype(np.float32) if bilateral_traces else np.zeros((0, frame_count), dtype=np.float32)
    asymmetry_matrix = np.vstack(asymmetry_traces).astype(np.float32) if asymmetry_traces else np.zeros((0, frame_count), dtype=np.float32)
    observed_mean_abs_pairwise_corr = _mean_abs_pairwise_corr(bilateral_matrix)
    shuffled_mean_abs_pairwise_corr = _mean_abs_pairwise_corr(_circular_shift_rows(bilateral_matrix, seed=0))
    structure_ratio_vs_circular_shift = (
        float(observed_mean_abs_pairwise_corr / shuffled_mean_abs_pairwise_corr)
        if np.isfinite(observed_mean_abs_pairwise_corr)
        and np.isfinite(shuffled_mean_abs_pairwise_corr)
        and shuffled_mean_abs_pairwise_corr > 1e-9
        else float("nan")
    )
    return {
        "family_pair_count": int(len(family_groups)),
        "mean_bilateral_voltage_corr": float(np.mean(bilateral_corrs)) if bilateral_corrs else float("nan"),
        "median_bilateral_voltage_corr": float(np.median(bilateral_corrs)) if bilateral_corrs else float("nan"),
        "turn_corr_std": float(table["turn_drive_asym_corr"].std()) if not table.empty else float("nan"),
        "turn_corr_abs_p90": float(np.quantile(abs_turn, 0.9)) if abs_turn.size else float("nan"),
        "observed_mean_abs_pairwise_corr": observed_mean_abs_pairwise_corr,
        "shuffled_mean_abs_pairwise_corr": shuffled_mean_abs_pairwise_corr,
        "structure_ratio_vs_circular_shift": structure_ratio_vs_circular_shift,
        "top_positive_turn_families": table.head(10).to_dict(orient="records"),
        "top_negative_turn_families": table.tail(10).sort_values("turn_drive_asym_corr").to_dict(orient="records"),
        "table": table,
        "ordered_table": ordered_table,
        "bilateral_matrix": bilateral_matrix,
        "asymmetry_matrix": asymmetry_matrix,
    }


def compare_awake_regimes(
    target_dynamics: Mapping[str, Any],
    no_target_dynamics: Mapping[str, Any],
) -> dict[str, float]:
    return {
        "background_mean_rate_hz_delta": float(
            target_dynamics["background_mean_rate_hz_mean"] - no_target_dynamics["background_mean_rate_hz_mean"]
        ),
        "background_active_fraction_delta": float(
            target_dynamics["background_active_fraction_mean"] - no_target_dynamics["background_active_fraction_mean"]
        ),
        "background_latent_mean_abs_hz_delta": float(
            target_dynamics["background_latent_mean_abs_hz_mean"] - no_target_dynamics["background_latent_mean_abs_hz_mean"]
        ),
        "global_spike_fraction_delta": float(
            target_dynamics["global_spike_fraction_mean"] - no_target_dynamics["global_spike_fraction_mean"]
        ),
    }


def _criterion(status: str, summary: str, **metrics: Any) -> dict[str, Any]:
    return {
        "status": status,
        "summary": summary,
        "metrics": metrics,
    }


def _forced_vs_spontaneous_public_criterion(payload: Mapping[str, Any]) -> dict[str, Any]:
    metrics = {
        "n_candidate_rows": int(payload.get("n_candidate_rows", 0) or 0),
        "n_experiments_used": int(payload.get("n_experiments_used", 0) or 0),
        "n_valid_vector_corr": int(payload.get("n_valid_vector_corr", 0) or 0),
        "n_valid_rank_corr": int(payload.get("n_valid_rank_corr", 0) or 0),
        "n_valid_prelead_fraction": int(payload.get("n_valid_prelead_fraction", 0) or 0),
        "median_steady_walk_vector_corr": float(payload.get("median_steady_walk_vector_corr", float("nan"))),
        "median_steady_walk_vector_cosine": float(payload.get("median_steady_walk_vector_cosine", float("nan"))),
        "median_steady_walk_rank_corr": float(payload.get("median_steady_walk_rank_corr", float("nan"))),
        "median_spontaneous_prelead_fraction": float(
            payload.get("median_spontaneous_prelead_fraction", float("nan"))
        ),
        "median_spontaneous_minus_forced_prelead_delta": float(
            payload.get("median_spontaneous_minus_forced_prelead_delta", float("nan"))
        ),
        "dropped_experiment_count": int(len(payload.get("dropped_experiments", []))),
    }
    raw_status = str(payload.get("status", "unknown"))
    if raw_status == "blocked_missing_files":
        return _criterion(
            "blocked",
            "The public Aimon forced-vs-spontaneous comparator is blocked until GoodICsdf.pkl and Additional_data.zip are staged locally. Walk_anatomical_regions.zip is useful but optional for this comparator.",
            missing_files=";".join(str(item) for item in payload.get("missing_files", [])),
            **metrics,
        )
    if raw_status == "blocked_no_matches":
        return _criterion(
            "blocked",
            "The staged public Aimon dataset did not yield any experiments with usable spontaneous and forced windows plus matching traces/regressors.",
            **metrics,
        )
    if raw_status == "partial_low_match_count":
        return _criterion(
            "partial",
            "The public Aimon comparator is running, but the current forced/spontaneous overlap is small-N and should be treated as directional evidence only.",
            **metrics,
        )
    if raw_status == "ok":
        enough_overlap = (
            metrics["n_experiments_used"] >= 2
            and metrics["n_valid_vector_corr"] >= 2
            and metrics["n_valid_rank_corr"] >= 2
        )
        strong_similarity = (
            metrics["median_steady_walk_vector_corr"] >= 0.1
            and metrics["median_steady_walk_vector_cosine"] >= 0.1
            and metrics["median_steady_walk_rank_corr"] >= 0.1
        )
        spontaneous_lead = (
            metrics["n_valid_prelead_fraction"] >= 1
            and metrics["median_spontaneous_minus_forced_prelead_delta"] > 0.0
        )
        status = (
            "pass"
            if enough_overlap and strong_similarity and spontaneous_lead
            else "partial"
        )
        summary = (
            "The public Aimon comparator reproduces the intended mesoscale claim boundary: similar steady forced/spontaneous walk activity plus stronger spontaneous pre-onset lead structure."
            if status == "pass"
            else "The public Aimon comparator is live on the staged dataset, but the current overlap yields mixed evidence: spontaneous pre-onset lead is positive while steady forced/spontaneous regional similarity is weak or negative."
        )
        return _criterion(
            status,
            summary,
            **metrics,
        )
    return _criterion(
        "not_evaluated",
        "The public forced-vs-spontaneous comparator did not reach an interpretable state.",
        raw_status=raw_status,
        **metrics,
    )


def build_mesoscale_validation_summary(
    *,
    target_capture: Mapping[str, Any],
    no_target_capture: Mapping[str, Any],
    target_records: list[Mapping[str, Any]],
    no_target_records: list[Mapping[str, Any]],
    family_groups: list[FamilySideGroup],
    public_dataset_summary: Mapping[str, Any],
    public_forced_spontaneous: Mapping[str, Any],
    target_connectome_function: Mapping[str, Any] | None = None,
    no_target_connectome_function: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    target_dynamics = summarize_condition_dynamics(target_records)
    no_target_dynamics = summarize_condition_dynamics(no_target_records)
    target_monitor_structure = summarize_monitored_voltage_structure(target_capture)
    no_target_monitor_structure = summarize_monitored_voltage_structure(no_target_capture)
    target_family_structure = summarize_family_voltage_structure(capture=target_capture, family_groups=family_groups)
    no_target_family_structure = summarize_family_voltage_structure(capture=no_target_capture, family_groups=family_groups)
    regime_delta = compare_awake_regimes(target_dynamics, no_target_dynamics)

    criteria = {
        "non_quiescent_awake_state": _criterion(
            "pass"
            if target_dynamics["background_mean_rate_hz_mean"] > 0.0
            and no_target_dynamics["background_mean_rate_hz_mean"] > 0.0
            and target_dynamics["global_spike_fraction_mean"] > 0.0
            and no_target_dynamics["global_spike_fraction_mean"] > 0.0
            else "fail",
            "Living target and no-target runs both occupy a non-dead spontaneous regime.",
            target_background_mean_rate_hz=target_dynamics["background_mean_rate_hz_mean"],
            no_target_background_mean_rate_hz=no_target_dynamics["background_mean_rate_hz_mean"],
            target_global_spike_fraction=target_dynamics["global_spike_fraction_mean"],
            no_target_global_spike_fraction=no_target_dynamics["global_spike_fraction_mean"],
        ),
        "matched_living_baseline": _criterion(
            "pass"
            if abs(regime_delta["background_mean_rate_hz_delta"]) <= 0.005
            and abs(regime_delta["background_active_fraction_delta"]) <= 0.01
            and abs(regime_delta["background_latent_mean_abs_hz_delta"]) <= 0.05
            else "partial",
            "Target-conditioned differences ride on the same awakened baseline instead of a different spontaneous regime.",
            **regime_delta,
        ),
        "walk_linked_global_modulation": _criterion(
            "pass"
            if target_dynamics["speed_voltage_std_corr"] > 0.15
            and target_dynamics["onset_voltage_std_delta"] > 0.0
            else "partial",
            "Global brain activity should covary with locomotion and rise around locomotor onset, consistent with Aimon-style walk-linked global state shifts.",
            target_speed_voltage_std_corr=target_dynamics["speed_voltage_std_corr"],
            no_target_speed_voltage_std_corr=no_target_dynamics["speed_voltage_std_corr"],
            target_onset_voltage_std_delta=target_dynamics["onset_voltage_std_delta"],
            no_target_onset_voltage_std_delta=no_target_dynamics["onset_voltage_std_delta"],
            target_locomotor_onset_count=target_dynamics["locomotor_onset_count"],
            no_target_locomotor_onset_count=no_target_dynamics["locomotor_onset_count"],
        ),
        "bilateral_family_coupling": _criterion(
            "pass"
            if target_family_structure["mean_bilateral_voltage_corr"] > 0.2
            and no_target_family_structure["mean_bilateral_voltage_corr"] > 0.2
            else "partial",
            "Homologous bilateral family traces should remain positively coupled in the living regime, consistent with mesoscale intrinsic-network structure.",
            target_mean_bilateral_voltage_corr=target_family_structure["mean_bilateral_voltage_corr"],
            no_target_mean_bilateral_voltage_corr=no_target_family_structure["mean_bilateral_voltage_corr"],
            target_family_pair_count=target_family_structure["family_pair_count"],
            no_target_family_pair_count=no_target_family_structure["family_pair_count"],
        ),
        "family_structure_exceeds_shift_surrogate": _criterion(
            "pass"
            if target_family_structure["structure_ratio_vs_circular_shift"] > 1.5
            and no_target_family_structure["structure_ratio_vs_circular_shift"] > 1.5
            else "partial",
            "Family-level functional structure should exceed a circular-shift surrogate, indicating real mesoscale organization rather than only per-family autocorrelation.",
            target_observed_mean_abs_pairwise_corr=target_family_structure["observed_mean_abs_pairwise_corr"],
            target_shuffled_mean_abs_pairwise_corr=target_family_structure["shuffled_mean_abs_pairwise_corr"],
            target_structure_ratio_vs_circular_shift=target_family_structure["structure_ratio_vs_circular_shift"],
            no_target_observed_mean_abs_pairwise_corr=no_target_family_structure["observed_mean_abs_pairwise_corr"],
            no_target_shuffled_mean_abs_pairwise_corr=no_target_family_structure["shuffled_mean_abs_pairwise_corr"],
            no_target_structure_ratio_vs_circular_shift=no_target_family_structure["structure_ratio_vs_circular_shift"],
        ),
        "residual_high_dimensional_structure": _criterion(
            "pass"
            if target_monitor_structure["residual"]["pc1_variance_ratio"] < target_monitor_structure["raw"]["pc1_variance_ratio"]
            and target_monitor_structure["residual"]["participation_ratio_topk"] > 3.0
            else "partial",
            "After regressing controller-linked covariates, monitored voltages should retain nontrivial residual dimensionality rather than collapse to a single global mode.",
            target_raw_pc1=target_monitor_structure["raw"]["pc1_variance_ratio"],
            target_residual_pc1=target_monitor_structure["residual"]["pc1_variance_ratio"],
            target_residual_participation_ratio=target_monitor_structure["residual"]["participation_ratio_topk"],
            no_target_raw_pc1=no_target_monitor_structure["raw"]["pc1_variance_ratio"],
            no_target_residual_pc1=no_target_monitor_structure["residual"]["pc1_variance_ratio"],
            no_target_residual_participation_ratio=no_target_monitor_structure["residual"]["participation_ratio_topk"],
        ),
        "residual_temporal_structure": _criterion(
            "pass"
            if target_monitor_structure["residual"]["lag1_autocorr_mean"] > 0.5
            and no_target_monitor_structure["residual"]["lag1_autocorr_mean"] > 0.5
            else "partial",
            "Residual monitored voltages should remain temporally structured, not white-noise-like.",
            target_residual_lag1=target_monitor_structure["residual"]["lag1_autocorr_mean"],
            no_target_residual_lag1=no_target_monitor_structure["residual"]["lag1_autocorr_mean"],
        ),
        "turn_linked_spatial_heterogeneity": _criterion(
            "pass"
            if target_family_structure["turn_corr_std"] > 0.1 and target_family_structure["turn_corr_abs_p90"] > 0.2
            else "partial",
            "Different family asymmetries should carry different turn relationships, matching the public observation that turning is spatially heterogeneous rather than uniform.",
            target_turn_corr_std=target_family_structure["turn_corr_std"],
            target_turn_corr_abs_p90=target_family_structure["turn_corr_abs_p90"],
            no_target_turn_corr_std=no_target_family_structure["turn_corr_std"],
            no_target_turn_corr_abs_p90=no_target_family_structure["turn_corr_abs_p90"],
        ),
        "forced_vs_spontaneous_walk_similarity": _forced_vs_spontaneous_public_criterion(public_forced_spontaneous),
        "connectome_function_correspondence": _criterion(
            "pass"
            if target_connectome_function
            and no_target_connectome_function
            and str(target_connectome_function.get("status", "")) == "ok"
            and str(no_target_connectome_function.get("status", "")) == "ok"
            and float(target_connectome_function.get("family_functional_corr_vs_log_structural_weight_corr", float("nan"))) >= 0.02
            and float(no_target_connectome_function.get("family_functional_corr_vs_log_structural_weight_corr", float("nan"))) >= 0.02
            else (
                "partial"
                if target_connectome_function
                and no_target_connectome_function
                and str(target_connectome_function.get("status", "")) == "ok"
                and str(no_target_connectome_function.get("status", "")) == "ok"
                else "not_evaluated"
            ),
            "Living-branch family-scale functional coupling should show at least weak positive correspondence to connectome-predicted coupling when aggregated at the same family scale.",
            target_family_structural_functional_corr=(
                float(target_connectome_function.get("family_functional_corr_vs_structural_weight_corr", float("nan")))
                if target_connectome_function
                else float("nan")
            ),
            target_family_log_structural_functional_corr=(
                float(target_connectome_function.get("family_functional_corr_vs_log_structural_weight_corr", float("nan")))
                if target_connectome_function
                else float("nan")
            ),
            no_target_family_structural_functional_corr=(
                float(no_target_connectome_function.get("family_functional_corr_vs_structural_weight_corr", float("nan")))
                if no_target_connectome_function
                else float("nan")
            ),
            no_target_family_log_structural_functional_corr=(
                float(no_target_connectome_function.get("family_functional_corr_vs_log_structural_weight_corr", float("nan")))
                if no_target_connectome_function
                else float("nan")
            ),
            target_family_pair_count=(
                int(target_connectome_function.get("family_pair_count", 0))
                if target_connectome_function
                else 0
            ),
            no_target_family_pair_count=(
                int(no_target_connectome_function.get("family_pair_count", 0))
                if no_target_connectome_function
                else 0
            ),
        ),
    }

    return {
        "public_dataset": public_dataset_summary,
        "conditions": {
            "target": target_dynamics,
            "no_target": no_target_dynamics,
        },
        "monitored_voltage_structure": {
            "target": target_monitor_structure,
            "no_target": no_target_monitor_structure,
        },
        "family_voltage_structure": {
            "target": {
                key: value
                for key, value in target_family_structure.items()
                if key not in {"table", "ordered_table", "bilateral_matrix", "asymmetry_matrix"}
            },
            "no_target": {
                key: value
                for key, value in no_target_family_structure.items()
                if key not in {"table", "ordered_table", "bilateral_matrix", "asymmetry_matrix"}
            },
        },
        "public_forced_vs_spontaneous": dict(public_forced_spontaneous),
        "connectome_function_correspondence": {
            "target": dict(target_connectome_function or {}),
            "no_target": dict(no_target_connectome_function or {}),
        },
        "criteria": criteria,
    }


def criteria_table(summary: Mapping[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, payload in summary.get("criteria", {}).items():
        row = {
            "criterion": key,
            "status": payload.get("status", "unknown"),
            "summary": payload.get("summary", ""),
        }
        for metric_key, value in payload.get("metrics", {}).items():
            row[metric_key] = value
        rows.append(row)
    return pd.DataFrame(rows)


def plot_mesoscale_validation(
    *,
    summary: Mapping[str, Any],
    target_family_table: pd.DataFrame,
    no_target_family_table: pd.DataFrame,
    plots_dir: str | Path,
) -> dict[str, str]:
    plots_dir = Path(plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)
    output_paths: dict[str, str] = {}

    target = summary["conditions"]["target"]
    no_target = summary["conditions"]["no_target"]
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=False)
    axes[0].plot(target["onset_voltage_std_curve"], label="target")
    axes[0].plot(no_target["onset_voltage_std_curve"], label="no_target")
    axes[0].axvline(len(target["onset_voltage_std_curve"]) // 2, color="black", linestyle="--", linewidth=1.0)
    axes[0].set_title("Locomotor Onset Triggered Global Voltage-Std")
    axes[0].set_ylabel("global_voltage_std")
    axes[0].legend(loc="best")
    axes[1].plot(target["onset_spike_curve"], label="target")
    axes[1].plot(no_target["onset_spike_curve"], label="no_target")
    axes[1].axvline(len(target["onset_spike_curve"]) // 2, color="black", linestyle="--", linewidth=1.0)
    axes[1].set_title("Locomotor Onset Triggered Global Spike Fraction")
    axes[1].set_ylabel("global_spike_fraction")
    axes[1].set_xlabel("aligned samples")
    axes[1].legend(loc="best")
    fig.tight_layout()
    onset_path = plots_dir / "spontaneous_mesoscale_onset_curves.png"
    fig.savefig(onset_path)
    plt.close(fig)
    output_paths["onset_curves"] = str(onset_path)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    axes[0].hist(target_family_table["bilateral_voltage_corr"].dropna().to_numpy(dtype=np.float32), bins=60, color="#1f77b4")
    axes[0].set_title("Target Bilateral Family Corr")
    axes[1].hist(no_target_family_table["bilateral_voltage_corr"].dropna().to_numpy(dtype=np.float32), bins=60, color="#ff7f0e")
    axes[1].set_title("No-Target Bilateral Family Corr")
    axes[0].set_ylabel("family count")
    for axis in axes:
        axis.set_xlabel("corr(left_voltage, right_voltage)")
    fig.tight_layout()
    bilateral_path = plots_dir / "spontaneous_mesoscale_bilateral_corr_hist.png"
    fig.savefig(bilateral_path)
    plt.close(fig)
    output_paths["bilateral_hist"] = str(bilateral_path)

    top_target = target_family_table.reindex(target_family_table["turn_drive_asym_corr"].abs().sort_values(ascending=False).head(12).index)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top_target["family"], top_target["turn_drive_asym_corr"], color="#2ca02c")
    ax.set_title("Target Top Family Asymmetry vs Turn Correlations")
    ax.set_xlabel("corr(right-left family voltage, turn_drive)")
    fig.tight_layout()
    turn_path = plots_dir / "spontaneous_mesoscale_turn_family_corr.png"
    fig.savefig(turn_path)
    plt.close(fig)
    output_paths["turn_family_corr"] = str(turn_path)
    return output_paths


def write_mesoscale_validation_bundle(
    *,
    target_capture_path: str | Path,
    no_target_capture_path: str | Path,
    target_log_path: str | Path,
    no_target_log_path: str | Path,
    completeness_path: str | Path,
    annotation_path: str | Path,
    included_super_classes: Iterable[str],
    min_family_size_per_side: int,
    max_family_size_per_side: int,
    public_dataset_root: str | Path,
    cache_dir: str | Path,
    output_summary_path: str | Path,
    output_components_csv_path: str | Path,
    plots_dir: str | Path,
) -> dict[str, Any]:
    public_dataset_summary = inspect_local_spontaneous_dataset(
        "aimon2023_dryad",
        root_dir=public_dataset_root,
    )
    public_forced_spontaneous = summarize_public_forced_vs_spontaneous_walk(public_dataset_root)
    family_groups = build_family_side_groups(
        annotation_path=annotation_path,
        completeness_path=completeness_path,
        included_super_classes=included_super_classes,
        min_size_per_side=min_family_size_per_side,
        max_size_per_side=max_family_size_per_side,
    )
    target_capture = load_activation_capture(target_capture_path)
    no_target_capture = load_activation_capture(no_target_capture_path)
    target_records = load_run_records(target_log_path)
    no_target_records = load_run_records(no_target_log_path)
    root_annotation = build_root_annotation_table(
        annotation_path=annotation_path,
        completeness_path=completeness_path,
        included_super_classes=included_super_classes,
    )
    target_family_structure = summarize_family_voltage_structure(capture=target_capture, family_groups=family_groups)
    no_target_family_structure = summarize_family_voltage_structure(capture=no_target_capture, family_groups=family_groups)
    target_connectome_function = family_structure_function_metrics(
        family_table=target_family_structure["ordered_table"],
        bilateral_matrix=target_family_structure["bilateral_matrix"],
        root_annotation=root_annotation,
        cache_dir=cache_dir,
    )
    no_target_connectome_function = family_structure_function_metrics(
        family_table=no_target_family_structure["ordered_table"],
        bilateral_matrix=no_target_family_structure["bilateral_matrix"],
        root_annotation=root_annotation,
        cache_dir=cache_dir,
    )
    summary = build_mesoscale_validation_summary(
        target_capture=target_capture,
        no_target_capture=no_target_capture,
        target_records=target_records,
        no_target_records=no_target_records,
        family_groups=family_groups,
        public_dataset_summary=public_dataset_summary,
        public_forced_spontaneous=public_forced_spontaneous,
        target_connectome_function=target_connectome_function,
        no_target_connectome_function=no_target_connectome_function,
    )
    target_family_table = target_family_structure["table"]
    no_target_family_table = no_target_family_structure["table"]
    plot_paths = plot_mesoscale_validation(
        summary=summary,
        target_family_table=target_family_table,
        no_target_family_table=no_target_family_table,
        plots_dir=plots_dir,
    )
    summary["plot_paths"] = plot_paths

    output_summary_path = Path(output_summary_path)
    output_components_csv_path = Path(output_components_csv_path)
    output_summary_path.parent.mkdir(parents=True, exist_ok=True)
    output_components_csv_path.parent.mkdir(parents=True, exist_ok=True)
    output_summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    criteria_table(summary).to_csv(output_components_csv_path, index=False)
    target_family_table.to_csv(output_components_csv_path.with_name("spontaneous_mesoscale_target_family_turn_table.csv"), index=False)
    no_target_family_table.to_csv(output_components_csv_path.with_name("spontaneous_mesoscale_no_target_family_turn_table.csv"), index=False)
    pd.DataFrame(summary.get("public_forced_vs_spontaneous", {}).get("per_experiment_rows", [])).to_csv(
        output_components_csv_path.with_name("spontaneous_public_forced_vs_spontaneous_table.csv"),
        index=False,
    )
    return summary

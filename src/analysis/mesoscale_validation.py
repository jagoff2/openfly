from __future__ import annotations

import json
import math
import pickle
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
import yaml

from analysis.best_branch_investigation import align_framewise_matrix, load_annotation_table, pearson_correlation
from visualization.activation_viz import load_brain_layout


def load_run_rows(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def framewise_run_table(rows: Sequence[Mapping[str, Any]], frame_cycles: np.ndarray) -> pd.DataFrame:
    frame_cycles = np.asarray(frame_cycles, dtype=np.int64).reshape(-1)
    selected_rows = [dict(rows[int(index)]) for index in frame_cycles.tolist()]
    table = pd.DataFrame(
        {
            "cycle": [int(row.get("cycle", 0)) for row in selected_rows],
            "sim_time": [float(row.get("sim_time", 0.0)) for row in selected_rows],
            "forward_speed": [float(row.get("forward_speed", 0.0)) for row in selected_rows],
            "left_drive": [float(row.get("left_drive", 0.0)) for row in selected_rows],
            "right_drive": [float(row.get("right_drive", 0.0)) for row in selected_rows],
            "yaw_rate": [float(row.get("yaw_rate", 0.0)) for row in selected_rows],
            "target_bearing_body": [
                float(row.get("target_state", {}).get("bearing_body", 0.0))
                if bool(row.get("target_state", {}).get("enabled", False))
                else math.nan
                for row in selected_rows
            ],
            "global_spike_fraction": [
                float(row.get("brain_backend_state", {}).get("global_spike_fraction", 0.0))
                for row in selected_rows
            ],
            "global_mean_voltage": [
                float(row.get("brain_backend_state", {}).get("global_mean_voltage", 0.0))
                for row in selected_rows
            ],
            "global_voltage_std": [
                float(row.get("brain_backend_state", {}).get("global_voltage_std", 0.0))
                for row in selected_rows
            ],
            "global_mean_conductance": [
                float(row.get("brain_backend_state", {}).get("global_mean_conductance", 0.0))
                for row in selected_rows
            ],
            "background_mean_rate_hz": [
                float(row.get("brain_backend_state", {}).get("background_mean_rate_hz", 0.0))
                for row in selected_rows
            ],
            "background_active_fraction": [
                float(row.get("brain_backend_state", {}).get("background_active_fraction", 0.0))
                for row in selected_rows
            ],
            "background_latent_mean_abs_hz": [
                float(row.get("brain_backend_state", {}).get("background_latent_mean_abs_hz", 0.0))
                for row in selected_rows
            ],
            "background_latent_std_hz": [
                float(row.get("brain_backend_state", {}).get("background_latent_std_hz", 0.0))
                for row in selected_rows
            ],
        }
    )
    table["turn_drive"] = table["right_drive"] - table["left_drive"]
    table["mean_drive"] = 0.5 * (table["right_drive"] + table["left_drive"])
    table["locomotor_active"] = (
        (np.abs(table["mean_drive"].to_numpy(dtype=np.float32)) > 0.05)
        | (table["forward_speed"].to_numpy(dtype=np.float32) > 1.0)
    )
    return table


def compute_global_backbone_metrics(table: pd.DataFrame) -> dict[str, float]:
    spike_fraction = table["global_spike_fraction"].to_numpy(dtype=np.float32)
    return {
        "frame_count": int(table.shape[0]),
        "global_spike_fraction_mean": float(spike_fraction.mean()),
        "global_spike_fraction_p95": float(np.percentile(spike_fraction, 95.0)),
        "global_mean_voltage_mean_mv": float(table["global_mean_voltage"].mean()),
        "global_voltage_std_mean_mv": float(table["global_voltage_std"].mean()),
        "global_mean_conductance_mean": float(table["global_mean_conductance"].mean()),
        "background_mean_rate_hz_mean": float(table["background_mean_rate_hz"].mean()),
        "background_active_fraction_mean": float(table["background_active_fraction"].mean()),
        "background_latent_mean_abs_hz_mean": float(table["background_latent_mean_abs_hz"].mean()),
        "background_latent_std_hz_mean": float(table["background_latent_std_hz"].mean()),
        "nonzero_window_fraction": float(np.mean(spike_fraction > 0.0)),
    }


def _state_partition_masks(table: pd.DataFrame, *, min_quiet_fraction: float = 0.15) -> tuple[np.ndarray, np.ndarray, str]:
    locomotor_active = table["locomotor_active"].to_numpy(dtype=bool)
    if float(np.mean(~locomotor_active)) >= float(min_quiet_fraction):
        return locomotor_active, ~locomotor_active, "rest_vs_walk"
    forward_speed = table["forward_speed"].to_numpy(dtype=np.float32)
    low_threshold = float(np.quantile(forward_speed, 0.15))
    high_threshold = float(np.quantile(forward_speed, 0.85))
    quiet_mask = forward_speed <= low_threshold
    walk_mask = forward_speed >= high_threshold
    return walk_mask, quiet_mask, "low_speed_quantile_vs_high_speed_quantile"


def compute_walk_state_metrics(table: pd.DataFrame) -> dict[str, float | str | None]:
    walk_mask, quiet_mask, mode = _state_partition_masks(table)
    if not np.any(walk_mask) or not np.any(quiet_mask):
        return {
            "comparison_mode": mode,
            "walk_like_fraction": float(np.mean(walk_mask)),
            "quiet_like_fraction": float(np.mean(quiet_mask)),
            "walk_vs_rest_global_rate_delta": float("nan"),
            "walk_vs_rest_global_voltage_delta": float("nan"),
            "walk_vs_rest_global_conductance_delta": float("nan"),
        }
    return {
        "comparison_mode": mode,
        "walk_like_fraction": float(np.mean(walk_mask)),
        "quiet_like_fraction": float(np.mean(quiet_mask)),
        "walk_vs_rest_global_rate_delta": float(
            table.loc[walk_mask, "global_spike_fraction"].mean() - table.loc[quiet_mask, "global_spike_fraction"].mean()
        ),
        "walk_vs_rest_global_voltage_delta": float(
            table.loc[walk_mask, "global_mean_voltage"].mean() - table.loc[quiet_mask, "global_mean_voltage"].mean()
        ),
        "walk_vs_rest_global_conductance_delta": float(
            table.loc[walk_mask, "global_mean_conductance"].mean() - table.loc[quiet_mask, "global_mean_conductance"].mean()
        ),
    }


def _find_sustained_onsets(mask: np.ndarray, *, min_duration_frames: int) -> np.ndarray:
    mask = np.asarray(mask, dtype=bool).reshape(-1)
    if mask.size == 0:
        return np.zeros(0, dtype=np.int64)
    padded = np.concatenate(([False], mask))
    onsets = np.flatnonzero(~padded[:-1] & padded[1:])
    keep: list[int] = []
    for onset in onsets.tolist():
        end = onset
        while end < mask.size and mask[end]:
            end += 1
        if end - onset >= int(min_duration_frames):
            keep.append(int(onset))
    return np.asarray(keep, dtype=np.int64)


def onset_triggered_curve(
    values: np.ndarray,
    active_mask: np.ndarray,
    sim_time: np.ndarray,
    *,
    pre_s: float = 0.15,
    post_s: float = 0.35,
    min_duration_s: float = 0.08,
) -> dict[str, Any]:
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    active_mask = np.asarray(active_mask, dtype=bool).reshape(-1)
    sim_time = np.asarray(sim_time, dtype=np.float32).reshape(-1)
    if values.size == 0 or sim_time.size != values.size or active_mask.size != values.size:
        return {
            "curve": [],
            "time_axis_s": [],
            "onset_count": 0,
            "peak_latency_s": None,
            "peak_amplitude": float("nan"),
        }
    dt = float(np.median(np.diff(sim_time))) if sim_time.size > 1 else 0.0
    if dt <= 0.0:
        return {
            "curve": [],
            "time_axis_s": [],
            "onset_count": 0,
            "peak_latency_s": None,
            "peak_amplitude": float("nan"),
        }
    pre_frames = int(round(float(pre_s) / dt))
    post_frames = int(round(float(post_s) / dt))
    min_duration_frames = max(1, int(round(float(min_duration_s) / dt)))
    onsets = _find_sustained_onsets(active_mask, min_duration_frames=min_duration_frames)
    windows: list[np.ndarray] = []
    for onset in onsets.tolist():
        start = onset - pre_frames
        stop = onset + post_frames + 1
        if start < 0 or stop > values.size:
            continue
        window = values[start:stop].astype(np.float32)
        baseline = float(np.mean(window[:pre_frames])) if pre_frames > 0 else 0.0
        windows.append(window - baseline)
    if not windows:
        return {
            "curve": [],
            "time_axis_s": [],
            "onset_count": 0,
            "peak_latency_s": None,
            "peak_amplitude": float("nan"),
        }
    matrix = np.vstack(windows)
    curve = matrix.mean(axis=0)
    time_axis = (np.arange(curve.size, dtype=np.float32) - pre_frames) * dt
    post_mask = time_axis >= 0.0
    peak_index = int(np.argmax(curve[post_mask])) if np.any(post_mask) else int(np.argmax(curve))
    peak_value = float(curve[post_mask][peak_index]) if np.any(post_mask) else float(curve[peak_index])
    peak_latency = float(time_axis[post_mask][peak_index]) if np.any(post_mask) else float(time_axis[peak_index])
    return {
        "curve": curve.astype(float).tolist(),
        "time_axis_s": time_axis.astype(float).tolist(),
        "onset_count": int(matrix.shape[0]),
        "peak_latency_s": peak_latency,
        "peak_amplitude": peak_value,
    }


def _family_trace_table(
    *,
    capture: Mapping[str, Any],
    brain_root_ids: np.ndarray,
    annotation_df: pd.DataFrame,
    allowed_super_classes: Sequence[str] | None = None,
    min_roots_per_side: int = 2,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, pd.DataFrame]:
    allowed = {str(item).lower() for item in (allowed_super_classes or []) if str(item).strip()}
    voltage_frames = np.asarray(capture["brain_voltage_frames"], dtype=np.float32)
    root_df = pd.DataFrame({"root_id": np.asarray(brain_root_ids, dtype=np.int64)})
    merged = root_df.merge(annotation_df, on="root_id", how="left")
    merged["side"] = merged["side"].fillna("").astype(str).str.lower()
    merged["family"] = merged["family"].fillna("").astype(str)
    merged["super_class"] = merged.get("super_class", pd.Series(index=merged.index, dtype=object)).fillna("unknown").astype(str)
    if allowed:
        merged = merged[merged["super_class"].str.lower().isin(allowed)].copy()
    rows: list[dict[str, Any]] = []
    bilateral_traces: list[np.ndarray] = []
    asymmetry_traces: list[np.ndarray] = []
    for family, group_df in merged.groupby("family", sort=True):
        if not family:
            continue
        left_indices = group_df.index[group_df["side"] == "left"].to_numpy(dtype=np.int64)
        right_indices = group_df.index[group_df["side"] == "right"].to_numpy(dtype=np.int64)
        if left_indices.size < int(min_roots_per_side) or right_indices.size < int(min_roots_per_side):
            continue
        left_trace = voltage_frames[:, left_indices].mean(axis=1)
        right_trace = voltage_frames[:, right_indices].mean(axis=1)
        super_class = str(group_df["super_class"].mode().iloc[0]) if not group_df["super_class"].mode().empty else "unknown"
        rows.append(
            {
                "family": str(family),
                "super_class": super_class,
                "left_count": int(left_indices.size),
                "right_count": int(right_indices.size),
                "total_count": int(left_indices.size + right_indices.size),
                "mean_homologous_voltage_corr": pearson_correlation(left_trace, right_trace),
                "mean_abs_asymmetry_voltage_mv": float(np.mean(np.abs(right_trace - left_trace))),
            }
        )
        bilateral_traces.append(0.5 * (left_trace + right_trace))
        asymmetry_traces.append(right_trace - left_trace)
    table = pd.DataFrame(rows)
    bilateral_matrix = np.vstack(bilateral_traces).astype(np.float32) if bilateral_traces else np.zeros((0, voltage_frames.shape[0]), dtype=np.float32)
    asymmetry_matrix = np.vstack(asymmetry_traces).astype(np.float32) if asymmetry_traces else np.zeros((0, voltage_frames.shape[0]), dtype=np.float32)
    return table, bilateral_matrix, asymmetry_matrix, merged


def matrix_rank_metrics(matrix: np.ndarray) -> dict[str, float]:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] < 2:
        return {
            "pc1_variance_share": float("nan"),
            "pc1_to_pc5_variance_share": float("nan"),
            "effective_rank": float("nan"),
            "participation_ratio": float("nan"),
        }
    centered = matrix - matrix.mean(axis=1, keepdims=True)
    if np.allclose(centered, 0.0):
        return {
            "pc1_variance_share": float("nan"),
            "pc1_to_pc5_variance_share": float("nan"),
            "effective_rank": float("nan"),
            "participation_ratio": float("nan"),
        }
    _, singular_values, _ = np.linalg.svd(centered, full_matrices=False)
    variances = singular_values ** 2
    variance_sum = float(np.sum(variances))
    if variance_sum <= 0.0:
        return {
            "pc1_variance_share": float("nan"),
            "pc1_to_pc5_variance_share": float("nan"),
            "effective_rank": float("nan"),
            "participation_ratio": float("nan"),
        }
    shares = variances / variance_sum
    safe = shares[shares > 0.0]
    effective_rank = float(np.exp(-np.sum(safe * np.log(safe)))) if safe.size else float("nan")
    participation_ratio = float((variance_sum ** 2) / np.sum(variances ** 2)) if np.sum(variances ** 2) > 0 else float("nan")
    return {
        "pc1_variance_share": float(shares[0]),
        "pc1_to_pc5_variance_share": float(np.sum(shares[: min(5, shares.size)])),
        "effective_rank": effective_rank,
        "participation_ratio": participation_ratio,
    }


def residual_metrics(
    matrix: np.ndarray,
    regressors: Mapping[str, np.ndarray],
) -> tuple[dict[str, Any], np.ndarray]:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] < 4:
        return {
            "behavior_explained_variance_fraction": float("nan"),
            "residual_variance_fraction": float("nan"),
            "residual_effective_rank": float("nan"),
            "residual_participation_ratio": float("nan"),
            "residual_mean_abs_pairwise_corr": float("nan"),
            "residual_lag1_autocorr": float("nan"),
            "residual_cluster_sparsity": float("nan"),
            "regressor_names": list(regressors.keys()),
        }, np.zeros_like(matrix)
    columns = [np.asarray(values, dtype=np.float32).reshape(-1) for values in regressors.values()]
    valid_columns = [column for column in columns if column.size == matrix.shape[1]]
    if not valid_columns:
        return {
            "behavior_explained_variance_fraction": float("nan"),
            "residual_variance_fraction": float("nan"),
            "residual_effective_rank": float("nan"),
            "residual_participation_ratio": float("nan"),
            "residual_mean_abs_pairwise_corr": float("nan"),
            "residual_lag1_autocorr": float("nan"),
            "residual_cluster_sparsity": float("nan"),
            "regressor_names": list(regressors.keys()),
        }, matrix.copy()
    design = np.column_stack([np.ones(matrix.shape[1], dtype=np.float32)] + valid_columns)
    betas, _, _, _ = np.linalg.lstsq(design, matrix.T, rcond=None)
    predicted = design @ betas
    residual = (matrix.T - predicted).T
    total_var = float(np.var(matrix))
    residual_var = float(np.var(residual))
    explained = float(max(0.0, 1.0 - residual_var / total_var)) if total_var > 1e-12 else float("nan")
    rank = matrix_rank_metrics(residual)
    corr = np.corrcoef(residual)
    upper = corr[np.triu_indices(corr.shape[0], k=1)] if corr.ndim == 2 else np.asarray([], dtype=np.float32)
    upper = upper[np.isfinite(upper)]
    lag_corrs = []
    for row in residual:
        if row.size < 3 or float(np.std(row)) <= 1e-6:
            continue
        value = np.corrcoef(row[:-1], row[1:])[0, 1]
        if np.isfinite(value):
            lag_corrs.append(float(value))
    family_std = residual.std(axis=1)
    if family_std.size:
        l1 = float(np.sum(np.abs(family_std)))
        l2 = float(np.linalg.norm(family_std))
        cluster_sparsity = float((math.sqrt(family_std.size) - (l1 / max(l2, 1e-9))) / (math.sqrt(family_std.size) - 1.0)) if family_std.size > 1 else 0.0
    else:
        cluster_sparsity = float("nan")
    return {
        "behavior_explained_variance_fraction": explained,
        "residual_variance_fraction": float(residual_var / total_var) if total_var > 1e-12 else float("nan"),
        "residual_effective_rank": rank["effective_rank"],
        "residual_participation_ratio": rank["participation_ratio"],
        "residual_mean_abs_pairwise_corr": float(np.mean(np.abs(upper))) if upper.size else float("nan"),
        "residual_lag1_autocorr": float(np.mean(lag_corrs)) if lag_corrs else float("nan"),
        "residual_cluster_sparsity": cluster_sparsity,
        "regressor_names": list(regressors.keys()),
    }, residual


def family_structure_function_metrics(
    *,
    family_table: pd.DataFrame,
    bilateral_matrix: np.ndarray,
    root_annotation: pd.DataFrame,
    cache_dir: str | Path,
) -> dict[str, Any]:
    cache_dir = Path(cache_dir)
    coo_path = cache_dir / "weight_coo.pkl"
    if family_table.empty or not coo_path.exists():
        return {
            "family_functional_corr_vs_structural_weight_corr": float("nan"),
            "explained_variance_functional_from_structure": float("nan"),
            "family_pair_count": 0,
            "status": "missing_cache_or_family_table",
        }
    with coo_path.open("rb") as handle:
        weight_coo = pickle.load(handle)
    weight_coo = weight_coo.coalesce()
    indices = weight_coo.indices().detach().cpu().numpy()
    values = weight_coo.values().detach().cpu().numpy()
    family_names = family_table["family"].astype(str).tolist()
    name_to_index = {name: idx for idx, name in enumerate(family_names)}
    family_index_by_neuron = np.full(root_annotation.shape[0], -1, dtype=np.int64)
    for neuron_index, family_name in enumerate(root_annotation["family"].fillna("").astype(str).tolist()):
        if family_name in name_to_index:
            family_index_by_neuron[neuron_index] = name_to_index[family_name]
    post_family = family_index_by_neuron[indices[0]]
    pre_family = family_index_by_neuron[indices[1]]
    valid = (post_family >= 0) & (pre_family >= 0)
    if not np.any(valid):
        return {
            "family_functional_corr_vs_structural_weight_corr": float("nan"),
            "explained_variance_functional_from_structure": float("nan"),
            "family_pair_count": 0,
            "status": "no_family_edges",
        }
    pair_df = pd.DataFrame(
        {
            "post_family": post_family[valid],
            "pre_family": pre_family[valid],
            "weight": np.abs(values[valid]).astype(np.float64),
        }
    )
    agg = pair_df.groupby(["post_family", "pre_family"], as_index=False)["weight"].sum()
    family_count = len(family_names)
    structural = np.zeros((family_count, family_count), dtype=np.float64)
    structural[agg["post_family"].to_numpy(dtype=np.int64), agg["pre_family"].to_numpy(dtype=np.int64)] = agg["weight"].to_numpy(dtype=np.float64)
    structural = 0.5 * (structural + structural.T)
    if bilateral_matrix.shape[0] != family_count or bilateral_matrix.shape[1] < 3:
        return {
            "family_functional_corr_vs_structural_weight_corr": float("nan"),
            "explained_variance_functional_from_structure": float("nan"),
            "family_pair_count": 0,
            "status": "shape_mismatch",
        }
    functional = np.corrcoef(bilateral_matrix)
    upper = np.triu_indices(family_count, k=1)
    structural_vec = structural[upper]
    functional_vec = functional[upper]
    keep = np.isfinite(structural_vec) & np.isfinite(functional_vec)
    if not np.any(keep):
        return {
            "family_functional_corr_vs_structural_weight_corr": float("nan"),
            "explained_variance_functional_from_structure": float("nan"),
            "family_functional_corr_vs_log_structural_weight_corr": float("nan"),
            "explained_variance_functional_from_log_structure": float("nan"),
            "family_pair_count": 0,
            "status": "no_valid_pairs",
        }
    raw_structural = structural_vec[keep]
    raw_functional = functional_vec[keep]
    corr = pearson_correlation(raw_structural, raw_functional)
    explained = float(corr * corr) if np.isfinite(corr) else float("nan")
    log_corr = pearson_correlation(np.log1p(raw_structural), raw_functional)
    log_explained = float(log_corr * log_corr) if np.isfinite(log_corr) else float("nan")
    return {
        "family_functional_corr_vs_structural_weight_corr": corr,
        "explained_variance_functional_from_structure": explained,
        "family_functional_corr_vs_log_structural_weight_corr": log_corr,
        "explained_variance_functional_from_log_structure": log_explained,
        "family_pair_count": int(np.count_nonzero(keep)),
        "status": "ok",
    }


def load_living_family_state(
    *,
    config_path: str | Path,
    capture_path: str | Path,
    run_log_path: str | Path,
    allowed_super_classes: Sequence[str] | None = None,
) -> dict[str, Any]:
    config = load_config(config_path)
    capture = np.load(capture_path, allow_pickle=True)
    rows = load_run_rows(run_log_path)
    brain_layout = load_brain_layout(
        annotation_path=config["visual_splice"]["annotation_path"],
        completeness_path=config["brain"]["completeness_path"],
        candidate_json=config.get("decoder", {}).get("monitor_candidates_json")
        or config.get("decoder", {}).get("population_candidates_json"),
        fixed_groups=None,
    )
    annotation_df = load_annotation_table(config["visual_splice"]["annotation_path"])
    frame_table = framewise_run_table(rows, np.asarray(capture["frame_cycles"], dtype=np.int64))
    family_table, bilateral_matrix, asymmetry_matrix, root_annotation = _family_trace_table(
        capture=capture,
        brain_root_ids=brain_layout.root_ids,
        annotation_df=annotation_df,
        allowed_super_classes=allowed_super_classes,
    )
    return {
        "config": config,
        "capture": capture,
        "frame_table": frame_table,
        "family_table": family_table,
        "bilateral_matrix": bilateral_matrix,
        "asymmetry_matrix": asymmetry_matrix,
        "brain_root_ids": brain_layout.root_ids,
        "root_annotation": root_annotation,
    }

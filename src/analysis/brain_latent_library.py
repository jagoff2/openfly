from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from analysis.best_branch_investigation import align_framewise_matrix, pearson_correlation


def monitor_voltage_turn_table(
    *,
    capture: Mapping[str, Any],
    monitor_groups: Mapping[str, list[int]],
) -> pd.DataFrame:
    monitored_root_ids = np.asarray(capture.get("monitored_root_ids", []), dtype=np.int64)
    monitored_voltage_matrix = np.asarray(capture.get("monitored_voltage_matrix", []), dtype=np.float32)
    controller_labels = np.asarray(capture.get("controller_labels", [])).astype(str)
    controller_matrix = np.asarray(capture.get("controller_matrix", []), dtype=np.float32)
    frame_cycles = np.asarray(capture.get("frame_cycles", []), dtype=np.int64)
    frame_target_bearing = np.asarray(capture.get("frame_target_bearing_body", []), dtype=np.float32)
    if (
        monitored_root_ids.size == 0
        or monitored_voltage_matrix.size == 0
        or controller_matrix.size == 0
        or frame_cycles.size == 0
    ):
        return pd.DataFrame(
            columns=[
                "label",
                "corr_target_bearing",
                "corr_drive_asymmetry",
                "corr_forward_speed",
                "mean_voltage_mv",
                "mean_abs_asymmetry_voltage_mv",
            ]
        )
    monitored_voltage_matrix = align_framewise_matrix(monitored_voltage_matrix, frame_cycles)
    controller_matrix = align_framewise_matrix(controller_matrix, frame_cycles)
    controller_by_label = {
        str(label): controller_matrix[idx]
        for idx, label in enumerate(controller_labels)
    }
    drive_asymmetry = controller_by_label.get("right_drive", np.zeros(frame_cycles.size, dtype=np.float32)) - controller_by_label.get(
        "left_drive",
        np.zeros(frame_cycles.size, dtype=np.float32),
    )
    forward_speed = controller_by_label.get("forward_speed", np.zeros(frame_cycles.size, dtype=np.float32))
    root_index = {int(root_id): idx for idx, root_id in enumerate(monitored_root_ids.tolist())}
    labels = sorted(
        {
            key[: -len("_left")]
            for key in monitor_groups.keys()
            if key.endswith("_left") and f"{key[: -len('_left')]}_right" in monitor_groups
        }
    )
    rows: list[dict[str, float | str]] = []
    for label in labels:
        left_ids = [root_index[int(root_id)] for root_id in monitor_groups.get(f"{label}_left", []) if int(root_id) in root_index]
        right_ids = [root_index[int(root_id)] for root_id in monitor_groups.get(f"{label}_right", []) if int(root_id) in root_index]
        if not left_ids and not right_ids:
            continue
        left_voltage = monitored_voltage_matrix[left_ids].mean(axis=0) if left_ids else np.zeros(monitored_voltage_matrix.shape[1], dtype=np.float32)
        right_voltage = monitored_voltage_matrix[right_ids].mean(axis=0) if right_ids else np.zeros(monitored_voltage_matrix.shape[1], dtype=np.float32)
        bilateral_voltage = 0.5 * (left_voltage + right_voltage)
        asymmetry_voltage = right_voltage - left_voltage
        rows.append(
            {
                "label": str(label),
                "corr_target_bearing": pearson_correlation(asymmetry_voltage, frame_target_bearing),
                "corr_drive_asymmetry": pearson_correlation(asymmetry_voltage, drive_asymmetry),
                "corr_forward_speed": pearson_correlation(bilateral_voltage, forward_speed),
                "mean_voltage_mv": float(np.mean(bilateral_voltage)),
                "mean_abs_asymmetry_voltage_mv": float(np.mean(np.abs(asymmetry_voltage))),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "label",
                "corr_target_bearing",
                "corr_drive_asymmetry",
                "corr_forward_speed",
                "mean_voltage_mv",
                "mean_abs_asymmetry_voltage_mv",
            ]
        )
    table = pd.DataFrame(rows)
    return table.reindex(table["corr_target_bearing"].abs().sort_values(ascending=False).index).reset_index(drop=True)


def _masked_pearson(values: np.ndarray, reference: np.ndarray, mask: np.ndarray, *, min_frames: int) -> float:
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    reference = np.asarray(reference, dtype=np.float32).reshape(-1)
    mask = np.asarray(mask, dtype=bool).reshape(-1)
    if values.size != reference.size or values.size != mask.size:
        raise ValueError("masked correlation inputs must have the same length")
    if int(mask.sum()) < int(min_frames):
        return float("nan")
    return pearson_correlation(values[mask], reference[mask])


def build_state_binned_turn_metrics(
    *,
    capture: Mapping[str, Any],
    monitor_groups: Mapping[str, list[int]],
    frame_state_values: np.ndarray,
    split_quantile: float = 0.5,
    min_bin_frames: int = 12,
) -> pd.DataFrame:
    monitored_root_ids = np.asarray(capture.get("monitored_root_ids", []), dtype=np.int64)
    monitored_voltage_matrix = np.asarray(capture.get("monitored_voltage_matrix", []), dtype=np.float32)
    controller_labels = np.asarray(capture.get("controller_labels", [])).astype(str)
    controller_matrix = np.asarray(capture.get("controller_matrix", []), dtype=np.float32)
    frame_cycles = np.asarray(capture.get("frame_cycles", []), dtype=np.int64)
    frame_target_bearing = np.asarray(capture.get("frame_target_bearing_body", []), dtype=np.float32)
    frame_state_values = np.asarray(frame_state_values, dtype=np.float32).reshape(-1)
    if (
        monitored_root_ids.size == 0
        or monitored_voltage_matrix.size == 0
        or controller_matrix.size == 0
        or frame_cycles.size == 0
        or frame_state_values.size == 0
    ):
        return pd.DataFrame(
            columns=[
                "label",
                "state_threshold",
                "low_frame_count",
                "high_frame_count",
                "corr_target_bearing_low",
                "corr_target_bearing_high",
                "corr_drive_asymmetry_low",
                "corr_drive_asymmetry_high",
                "mean_abs_asymmetry_voltage_mv_low",
                "mean_abs_asymmetry_voltage_mv_high",
            ]
        )
    monitored_voltage_matrix = align_framewise_matrix(monitored_voltage_matrix, frame_cycles)
    controller_matrix = align_framewise_matrix(controller_matrix, frame_cycles)
    if frame_state_values.size != frame_cycles.size:
        raise ValueError("frame_state_values must match the number of aligned frames")
    controller_by_label = {
        str(label): controller_matrix[idx]
        for idx, label in enumerate(controller_labels)
    }
    drive_asymmetry = controller_by_label.get("right_drive", np.zeros(frame_cycles.size, dtype=np.float32)) - controller_by_label.get(
        "left_drive",
        np.zeros(frame_cycles.size, dtype=np.float32),
    )
    root_index = {int(root_id): idx for idx, root_id in enumerate(monitored_root_ids.tolist())}
    labels = sorted(
        {
            key[: -len("_left")]
            for key in monitor_groups.keys()
            if key.endswith("_left") and f"{key[: -len('_left')]}_right" in monitor_groups
        }
    )
    threshold = float(np.quantile(frame_state_values, float(split_quantile)))
    low_mask = frame_state_values <= threshold
    high_mask = frame_state_values > threshold
    rows: list[dict[str, float | str]] = []
    for label in labels:
        left_ids = [root_index[int(root_id)] for root_id in monitor_groups.get(f"{label}_left", []) if int(root_id) in root_index]
        right_ids = [root_index[int(root_id)] for root_id in monitor_groups.get(f"{label}_right", []) if int(root_id) in root_index]
        if not left_ids and not right_ids:
            continue
        left_voltage = monitored_voltage_matrix[left_ids].mean(axis=0) if left_ids else np.zeros(monitored_voltage_matrix.shape[1], dtype=np.float32)
        right_voltage = monitored_voltage_matrix[right_ids].mean(axis=0) if right_ids else np.zeros(monitored_voltage_matrix.shape[1], dtype=np.float32)
        asymmetry_voltage = right_voltage - left_voltage
        rows.append(
            {
                "label": str(label),
                "state_threshold": threshold,
                "low_frame_count": int(low_mask.sum()),
                "high_frame_count": int(high_mask.sum()),
                "corr_target_bearing_low": _masked_pearson(
                    asymmetry_voltage,
                    frame_target_bearing,
                    low_mask,
                    min_frames=min_bin_frames,
                ),
                "corr_target_bearing_high": _masked_pearson(
                    asymmetry_voltage,
                    frame_target_bearing,
                    high_mask,
                    min_frames=min_bin_frames,
                ),
                "corr_drive_asymmetry_low": _masked_pearson(
                    asymmetry_voltage,
                    drive_asymmetry,
                    low_mask,
                    min_frames=min_bin_frames,
                ),
                "corr_drive_asymmetry_high": _masked_pearson(
                    asymmetry_voltage,
                    drive_asymmetry,
                    high_mask,
                    min_frames=min_bin_frames,
                ),
                "mean_abs_asymmetry_voltage_mv_low": float(np.mean(np.abs(asymmetry_voltage[low_mask]))) if int(low_mask.sum()) >= int(min_bin_frames) else float("nan"),
                "mean_abs_asymmetry_voltage_mv_high": float(np.mean(np.abs(asymmetry_voltage[high_mask]))) if int(high_mask.sum()) >= int(min_bin_frames) else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def _sign_mismatch(value: float, reference_sign: float, *, min_abs_corr: float) -> bool:
    if not np.isfinite(value) or abs(float(value)) < float(min_abs_corr) or abs(float(reference_sign)) < 1e-9:
        return False
    return bool(np.sign(value) != np.sign(reference_sign))


def apply_state_binned_ranking_adjustments(
    ranked: pd.DataFrame,
    *,
    target_state_metrics: pd.DataFrame | None = None,
    no_target_state_metrics: pd.DataFrame | None = None,
    min_bin_abs_corr: float = 0.1,
    state_stability_weight: float = 0.25,
    state_bias_weight: float = 0.35,
    state_asymmetry_weight: float = 0.15,
    state_flip_penalty_weight: float = 0.5,
    require_consistent_sign: bool = False,
) -> pd.DataFrame:
    if ranked.empty:
        return ranked.copy()
    adjusted = ranked.copy()
    adjusted["base_target_specificity_score"] = adjusted["target_specificity_score"]
    if target_state_metrics is not None and not target_state_metrics.empty:
        target_state = target_state_metrics.copy().rename(
            columns={
                "corr_target_bearing_low": "target_state_corr_target_bearing_low",
                "corr_target_bearing_high": "target_state_corr_target_bearing_high",
                "corr_drive_asymmetry_low": "target_state_corr_drive_asymmetry_low",
                "corr_drive_asymmetry_high": "target_state_corr_drive_asymmetry_high",
                "mean_abs_asymmetry_voltage_mv_low": "target_state_mean_abs_asymmetry_voltage_mv_low",
                "mean_abs_asymmetry_voltage_mv_high": "target_state_mean_abs_asymmetry_voltage_mv_high",
                "low_frame_count": "target_state_low_frame_count",
                "high_frame_count": "target_state_high_frame_count",
                "state_threshold": "target_state_threshold",
            }
        )
        adjusted = adjusted.merge(target_state, on="label", how="left")
    if no_target_state_metrics is not None and not no_target_state_metrics.empty:
        no_target_state = no_target_state_metrics.copy().rename(
            columns={
                "corr_target_bearing_low": "no_target_state_corr_target_bearing_low",
                "corr_target_bearing_high": "no_target_state_corr_target_bearing_high",
                "corr_drive_asymmetry_low": "no_target_state_corr_drive_asymmetry_low",
                "corr_drive_asymmetry_high": "no_target_state_corr_drive_asymmetry_high",
                "mean_abs_asymmetry_voltage_mv_low": "no_target_state_mean_abs_asymmetry_voltage_mv_low",
                "mean_abs_asymmetry_voltage_mv_high": "no_target_state_mean_abs_asymmetry_voltage_mv_high",
                "low_frame_count": "no_target_state_low_frame_count",
                "high_frame_count": "no_target_state_high_frame_count",
                "state_threshold": "no_target_state_threshold",
            }
        )
        adjusted = adjusted.merge(no_target_state, on="label", how="left")

    target_low = adjusted.get("target_state_corr_target_bearing_low", pd.Series(np.nan, index=adjusted.index, dtype=np.float32)).astype(float)
    target_high = adjusted.get("target_state_corr_target_bearing_high", pd.Series(np.nan, index=adjusted.index, dtype=np.float32)).astype(float)
    overall_sign = np.sign(adjusted["corr_target_bearing"].astype(float))
    target_bin_abs = np.stack(
        [
            np.nan_to_num(np.abs(target_low.to_numpy(dtype=np.float32)), nan=0.0),
            np.nan_to_num(np.abs(target_high.to_numpy(dtype=np.float32)), nan=0.0),
        ],
        axis=1,
    )
    adjusted["target_state_min_abs_corr"] = target_bin_abs.min(axis=1)
    flip_penalties = []
    for idx in range(len(adjusted)):
        low_value = float(target_low.iloc[idx])
        high_value = float(target_high.iloc[idx])
        ref_sign = float(overall_sign.iloc[idx])
        low_mismatch = _sign_mismatch(low_value, ref_sign, min_abs_corr=min_bin_abs_corr)
        high_mismatch = _sign_mismatch(high_value, ref_sign, min_abs_corr=min_bin_abs_corr)
        cross_flip = (
            np.isfinite(low_value)
            and np.isfinite(high_value)
            and abs(low_value) >= float(min_bin_abs_corr)
            and abs(high_value) >= float(min_bin_abs_corr)
            and np.sign(low_value) != np.sign(high_value)
        )
        flip_penalties.append(1.0 if (low_mismatch or high_mismatch or cross_flip) else 0.0)
    adjusted["target_state_sign_flip_penalty"] = flip_penalties

    no_target_low = adjusted.get("no_target_state_corr_drive_asymmetry_low", pd.Series(np.nan, index=adjusted.index, dtype=np.float32)).astype(float)
    no_target_high = adjusted.get("no_target_state_corr_drive_asymmetry_high", pd.Series(np.nan, index=adjusted.index, dtype=np.float32)).astype(float)
    adjusted["no_target_state_bias_penalty"] = np.maximum(
        np.nan_to_num(np.abs(no_target_low.to_numpy(dtype=np.float32)), nan=0.0),
        np.nan_to_num(np.abs(no_target_high.to_numpy(dtype=np.float32)), nan=0.0),
    )
    no_target_asym_low = adjusted.get(
        "no_target_state_mean_abs_asymmetry_voltage_mv_low",
        pd.Series(np.nan, index=adjusted.index, dtype=np.float32),
    ).astype(float)
    no_target_asym_high = adjusted.get(
        "no_target_state_mean_abs_asymmetry_voltage_mv_high",
        pd.Series(np.nan, index=adjusted.index, dtype=np.float32),
    ).astype(float)
    target_scale = adjusted["mean_abs_asymmetry_voltage_mv"].astype(float).clip(lower=1e-6)
    adjusted["no_target_state_asymmetry_penalty"] = np.maximum(
        np.nan_to_num(np.abs(no_target_asym_low.to_numpy(dtype=np.float32)), nan=0.0),
        np.nan_to_num(np.abs(no_target_asym_high.to_numpy(dtype=np.float32)), nan=0.0),
    ) / target_scale.to_numpy(dtype=np.float32)
    adjusted["target_specificity_score"] = (
        adjusted["base_target_specificity_score"].astype(float)
        + float(state_stability_weight) * adjusted["target_state_min_abs_corr"].astype(float)
        - float(state_bias_weight) * adjusted["no_target_state_bias_penalty"].astype(float)
        - float(state_asymmetry_weight) * adjusted["no_target_state_asymmetry_penalty"].astype(float)
        - float(state_flip_penalty_weight) * adjusted["target_state_sign_flip_penalty"].astype(float)
    )
    if require_consistent_sign:
        adjusted = adjusted[adjusted["target_state_sign_flip_penalty"] < 0.5].copy()
    adjusted = adjusted.sort_values(
        [
            "target_specificity_score",
            "target_state_min_abs_corr",
            "corr_target_bearing",
        ],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    return adjusted


def build_matched_turn_latent_ranking(
    *,
    target_turn_table: pd.DataFrame,
    no_target_turn_table: pd.DataFrame,
    min_target_corr: float = 0.15,
) -> pd.DataFrame:
    if target_turn_table.empty:
        return pd.DataFrame(
            columns=[
                "label",
                "target_specificity_score",
                "corr_target_bearing",
                "corr_drive_asymmetry",
                "mean_abs_asymmetry_voltage_mv",
                "no_target_corr_drive_asymmetry",
                "no_target_mean_abs_asymmetry_voltage_mv",
                "generic_turn_bias_penalty",
                "asymmetry_ratio_penalty",
            ]
        )
    target_table = target_turn_table.copy().rename(
        columns={
            "corr_target_bearing": "target_corr_target_bearing",
            "corr_drive_asymmetry": "target_corr_drive_asymmetry",
            "corr_forward_speed": "target_corr_forward_speed",
            "mean_voltage_mv": "target_mean_voltage_mv",
            "mean_abs_asymmetry_voltage_mv": "target_mean_abs_asymmetry_voltage_mv",
        }
    )
    no_target_table = no_target_turn_table.copy().rename(
        columns={
            "corr_target_bearing": "no_target_corr_target_bearing",
            "corr_drive_asymmetry": "no_target_corr_drive_asymmetry",
            "corr_forward_speed": "no_target_corr_forward_speed",
            "mean_voltage_mv": "no_target_mean_voltage_mv",
            "mean_abs_asymmetry_voltage_mv": "no_target_mean_abs_asymmetry_voltage_mv",
        }
    )
    merged = target_table.merge(no_target_table, on="label", how="left")
    merged["target_abs_corr"] = merged["target_corr_target_bearing"].abs()
    merged["target_drive_align_abs"] = merged["target_corr_drive_asymmetry"].abs()
    merged["generic_turn_bias_penalty"] = merged["no_target_corr_drive_asymmetry"].fillna(0.0).abs()
    merged["asymmetry_ratio_penalty"] = (
        merged["no_target_mean_abs_asymmetry_voltage_mv"].fillna(0.0)
        / merged["target_mean_abs_asymmetry_voltage_mv"].clip(lower=1e-6)
    )
    merged["target_specificity_score"] = (
        merged["target_abs_corr"]
        + 0.5 * merged["target_drive_align_abs"]
        - 0.75 * merged["generic_turn_bias_penalty"]
        - 0.25 * merged["asymmetry_ratio_penalty"]
    )
    merged = merged[merged["target_abs_corr"] >= float(min_target_corr)].copy()
    merged = merged.sort_values(
        [
            "target_specificity_score",
            "target_abs_corr",
            "target_drive_align_abs",
        ],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    return merged.rename(
        columns={
            "target_corr_target_bearing": "corr_target_bearing",
            "target_corr_drive_asymmetry": "corr_drive_asymmetry",
            "target_corr_forward_speed": "corr_forward_speed",
            "target_mean_voltage_mv": "mean_voltage_mv",
            "target_mean_abs_asymmetry_voltage_mv": "mean_abs_asymmetry_voltage_mv",
        }
    )

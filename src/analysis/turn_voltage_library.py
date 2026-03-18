from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd


def build_turn_voltage_signal_library(
    ranked: pd.DataFrame,
    metadata: Mapping[str, Mapping[str, Any]],
    *,
    top_k: int = 8,
    target_turn: pd.DataFrame | None = None,
    allowed_super_classes: list[str] | None = None,
    include_labels: list[str] | None = None,
    exclude_labels: list[str] | None = None,
    max_mean_asymmetry_mv: float | None = None,
    weight_mode: str = "score",
    downweight_labels: Mapping[str, float] | None = None,
    turn_scale_mv: float = 5.0,
) -> dict[str, Any]:
    allowed = {str(item).lower() for item in (allowed_super_classes or [])}
    include = {str(item).strip() for item in (include_labels or []) if str(item).strip()}
    exclude = {str(item).strip() for item in (exclude_labels or []) if str(item).strip()}
    downweight = {str(key).strip(): float(value) for key, value in dict(downweight_labels or {}).items() if str(key).strip()}

    selected: list[dict[str, Any]] = []
    for _, row in ranked.iterrows():
        label = str(row.get("label", "")).strip()
        item = metadata.get(label)
        if not item or not label:
            continue
        if include and label not in include:
            continue
        if label in exclude:
            continue
        super_class = str(item.get("super_class", "unknown"))
        if allowed and super_class.lower() not in allowed:
            continue
        score_value = row.get("target_specificity_score", row.get("turn_specificity_score", 0.0))
        score = float(score_value)
        corr_target_bearing = float(row.get("corr_target_bearing", 0.0))
        if abs(corr_target_bearing) <= 1e-9:
            continue
        mean_abs_asymmetry = None
        if target_turn is not None and label in target_turn.index:
            value = target_turn.loc[label, "mean_abs_asymmetry_voltage_mv"]
            mean_abs_asymmetry = float(value)
        if max_mean_asymmetry_mv is not None and mean_abs_asymmetry is not None and abs(mean_abs_asymmetry) > float(max_mean_asymmetry_mv):
            continue
        selected.append(
            {
                "label": label,
                "super_class": super_class,
                "left_root_ids": [int(root_id) for root_id in item.get("left_root_ids", [])],
                "right_root_ids": [int(root_id) for root_id in item.get("right_root_ids", [])],
                "target_specificity_score": score,
                "corr_target_bearing": corr_target_bearing,
                "corr_drive_asymmetry": float(row.get("corr_drive_asymmetry", 0.0)),
                "mean_abs_asymmetry_voltage_mv": mean_abs_asymmetry,
            }
        )
        if len(selected) >= int(top_k):
            break

    magnitudes: list[float] = []
    for item in selected:
        magnitude = abs(float(item["target_specificity_score"]))
        mean_abs_asymmetry = item.get("mean_abs_asymmetry_voltage_mv")
        if weight_mode == "score_over_sqrt_asym" and mean_abs_asymmetry is not None:
            magnitude = magnitude / max(abs(float(mean_abs_asymmetry)) ** 0.5, 1e-6)
        magnitude *= abs(float(downweight.get(str(item["label"]), 1.0)))
        magnitudes.append(magnitude)
    max_magnitude = max(magnitudes) if magnitudes else 1.0
    if max_magnitude <= 0.0:
        max_magnitude = 1.0

    for item, magnitude in zip(selected, magnitudes):
        sign = 1.0 if float(item["corr_target_bearing"]) > 0.0 else -1.0
        item["turn_weight"] = sign * (magnitude / max_magnitude)

    return {
        "selection_rule": "target-specific monitor turn-voltage ranking with sign chosen to align with body-frame target bearing",
        "turn_scale_mv": float(turn_scale_mv),
        "weight_mode": str(weight_mode),
        "selected_groups": selected,
    }


def apply_baseline_asymmetry_from_voltage_matrix(
    signal_library: Mapping[str, Any],
    monitored_root_ids: np.ndarray,
    monitored_voltage_matrix: np.ndarray,
) -> dict[str, Any]:
    payload = deepcopy(dict(signal_library))
    selected_groups = [dict(item) for item in payload.get("selected_groups", [])]
    root_ids = np.asarray(monitored_root_ids, dtype=np.int64)
    voltage_matrix = np.asarray(monitored_voltage_matrix, dtype=np.float32)
    root_index = {int(root_id): idx for idx, root_id in enumerate(root_ids.tolist())}
    if voltage_matrix.ndim != 2:
        raise ValueError("monitored_voltage_matrix must be 2D with shape [n_roots, n_frames]")

    for group in selected_groups:
        left_indices = [root_index[int(root_id)] for root_id in group.get("left_root_ids", []) if int(root_id) in root_index]
        right_indices = [root_index[int(root_id)] for root_id in group.get("right_root_ids", []) if int(root_id) in root_index]
        left_voltage = voltage_matrix[left_indices].mean(axis=0) if left_indices else np.zeros(voltage_matrix.shape[1], dtype=np.float32)
        right_voltage = voltage_matrix[right_indices].mean(axis=0) if right_indices else np.zeros(voltage_matrix.shape[1], dtype=np.float32)
        group["baseline_asymmetry_mv"] = float(np.mean(right_voltage - left_voltage))

    payload["selected_groups"] = selected_groups
    return payload

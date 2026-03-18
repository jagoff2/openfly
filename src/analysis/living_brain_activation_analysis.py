from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from analysis.best_branch_investigation import (
    align_framewise_matrix,
    build_unsampled_unit_table,
    compute_selected_frame_counts,
    load_annotation_table,
    pearson_correlation,
)


def load_run_rows(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def summarize_rendered_activity(
    *,
    brain_voltage_frames: np.ndarray,
    brain_spike_frames: np.ndarray,
    max_points: int,
) -> tuple[dict[str, float | int], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    brain_voltage_frames = np.asarray(brain_voltage_frames, dtype=np.float32)
    brain_spike_frames = np.asarray(brain_spike_frames, dtype=np.uint8)
    selected_counts = compute_selected_frame_counts(
        brain_voltage_frames,
        brain_spike_frames,
        max_points=int(max_points),
    )
    spike_counts = brain_spike_frames.sum(axis=0).astype(np.int32)
    mean_voltage = brain_voltage_frames.mean(axis=0).astype(np.float32)
    max_voltage = brain_voltage_frames.max(axis=0).astype(np.float32)
    spiking_units_mask = spike_counts > 0
    selected_units_mask = selected_counts > 0
    selected_and_spiking = int(np.count_nonzero(selected_units_mask & spiking_units_mask))
    selected_units = int(np.count_nonzero(selected_units_mask))
    spiking_units = int(np.count_nonzero(spiking_units_mask))
    summary = {
        "frame_count": int(brain_voltage_frames.shape[0]),
        "brain_neuron_count": int(brain_voltage_frames.shape[1]),
        "global_spike_fraction_mean": float(brain_spike_frames.mean()),
        "global_spike_fraction_std": float(brain_spike_frames.mean(axis=1).std()),
        "spiking_neurons_per_frame_mean": float(brain_spike_frames.sum(axis=1).mean()),
        "spiking_neurons_per_frame_max": int(brain_spike_frames.sum(axis=1).max(initial=0)),
        "selected_units": selected_units,
        "spiking_units": spiking_units,
        "selected_and_spiking": selected_and_spiking,
        "selected_not_spiking": int(selected_units - selected_and_spiking),
        "selected_not_spiking_fraction_of_selected": (
            float(selected_units - selected_and_spiking) / float(selected_units)
            if selected_units
            else 0.0
        ),
        "spiking_units_fraction_of_brain": float(spiking_units) / float(brain_voltage_frames.shape[1]),
    }
    return summary, selected_counts, spike_counts, mean_voltage, max_voltage


def summarize_backend_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    def _series(section: str, key: str) -> np.ndarray:
        values: list[float] = []
        for row in rows:
            payload = row.get(section, {})
            if isinstance(payload, Mapping) and key in payload and payload[key] is not None:
                values.append(float(payload[key]))
        return np.asarray(values, dtype=np.float32)

    def _mean(section: str, key: str) -> float:
        series = _series(section, key)
        return float(series.mean()) if series.size else 0.0

    return {
        "background_mean_rate_hz_mean": _mean("brain_backend_state", "background_mean_rate_hz"),
        "background_active_fraction_mean": _mean("brain_backend_state", "background_active_fraction"),
        "background_latent_mean_abs_hz_mean": _mean("brain_backend_state", "background_latent_mean_abs_hz"),
        "background_latent_std_hz_mean": _mean("brain_backend_state", "background_latent_std_hz"),
        "global_spike_fraction_mean": _mean("brain_backend_state", "global_spike_fraction"),
        "global_voltage_std_mean": _mean("brain_backend_state", "global_voltage_std"),
        "salience_abs_asym_mean": _mean("vision_features", "balance"),
        "forward_salience_mean": _mean("vision_features", "forward_salience"),
        "inferred_turn_confidence_mean": _mean("vision_features", "inferred_turn_confidence"),
    }


def summarize_flyvis_activity(capture: Mapping[str, Any]) -> dict[str, float]:
    left = np.asarray(capture["flyvis_left_frames"], dtype=np.float32)
    right = np.asarray(capture["flyvis_right_frames"], dtype=np.float32)
    total = 0.5 * (np.mean(np.abs(left), axis=1) + np.mean(np.abs(right), axis=1))
    asym = np.mean(np.abs(right - left), axis=1)
    return {
        "flyvis_total_activity_mean": float(total.mean()),
        "flyvis_total_activity_std": float(total.std()),
        "flyvis_abs_asym_mean": float(asym.mean()),
        "flyvis_abs_asym_std": float(asym.std()),
    }


def build_monitor_rate_comparison(
    *,
    target_capture: Mapping[str, Any],
    no_target_capture: Mapping[str, Any],
) -> pd.DataFrame:
    target_labels = np.asarray(target_capture["monitor_labels"]).astype(str)
    no_target_labels = np.asarray(no_target_capture["monitor_labels"]).astype(str)
    target_matrix = np.asarray(target_capture["monitor_matrix"], dtype=np.float32)
    no_target_matrix = np.asarray(no_target_capture["monitor_matrix"], dtype=np.float32)
    labels = sorted(set(target_labels.tolist()) | set(no_target_labels.tolist()))
    target_index = {label: idx for idx, label in enumerate(target_labels.tolist())}
    no_target_index = {label: idx for idx, label in enumerate(no_target_labels.tolist())}
    rows = []
    for label in labels:
        target_mean = float(target_matrix[target_index[label]].mean()) if label in target_index else 0.0
        no_target_mean = float(no_target_matrix[no_target_index[label]].mean()) if label in no_target_index else 0.0
        rows.append(
            {
                "label": label,
                "target_mean_rate_hz": target_mean,
                "no_target_mean_rate_hz": no_target_mean,
                "target_minus_no_target_hz": target_mean - no_target_mean,
                "abs_target_minus_no_target_hz": abs(target_mean - no_target_mean),
            }
        )
    table = pd.DataFrame(rows)
    return table.sort_values(
        ["target_mean_rate_hz", "abs_target_minus_no_target_hz"],
        ascending=[False, False],
    ).reset_index(drop=True)


def _controller_by_label(capture: Mapping[str, Any]) -> dict[str, np.ndarray]:
    frame_cycles = np.asarray(capture["frame_cycles"], dtype=np.int64)
    controller_labels = np.asarray(capture["controller_labels"]).astype(str)
    controller_matrix = align_framewise_matrix(np.asarray(capture["controller_matrix"], dtype=np.float32), frame_cycles)
    return {str(label): controller_matrix[idx] for idx, label in enumerate(controller_labels)}


def build_family_signal_table(
    *,
    unit_table: pd.DataFrame,
    brain_root_ids: np.ndarray,
    brain_voltage_frames: np.ndarray,
    brain_spike_frames: np.ndarray,
    frame_target_bearing: np.ndarray,
    controller_by_label: Mapping[str, np.ndarray],
) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    brain_root_ids = np.asarray(brain_root_ids, dtype=np.int64)
    brain_voltage_frames = np.asarray(brain_voltage_frames, dtype=np.float32)
    brain_spike_frames = np.asarray(brain_spike_frames, dtype=np.uint8)
    frame_target_bearing = np.asarray(frame_target_bearing, dtype=np.float32)
    for family, family_units in unit_table.groupby("family", dropna=False):
        if not family or str(family) == "UNKNOWN":
            continue
        family_root_ids = family_units["root_id"].to_numpy(dtype=np.int64)
        family_indices = np.flatnonzero(np.isin(brain_root_ids, family_root_ids))
        if family_indices.size == 0:
            continue
        family_voltage = brain_voltage_frames[:, family_indices].mean(axis=1)
        family_spikes = brain_spike_frames[:, family_indices].mean(axis=1)
        left_root_ids = family_units.loc[
            family_units["side"].astype(str).str.lower() == "left",
            "root_id",
        ].to_numpy(dtype=np.int64)
        right_root_ids = family_units.loc[
            family_units["side"].astype(str).str.lower() == "right",
            "root_id",
        ].to_numpy(dtype=np.int64)
        left_indices = np.flatnonzero(np.isin(brain_root_ids, left_root_ids))
        right_indices = np.flatnonzero(np.isin(brain_root_ids, right_root_ids))
        left_voltage = (
            brain_voltage_frames[:, left_indices].mean(axis=1)
            if left_indices.size
            else np.zeros(brain_voltage_frames.shape[0], dtype=np.float32)
        )
        right_voltage = (
            brain_voltage_frames[:, right_indices].mean(axis=1)
            if right_indices.size
            else np.zeros(brain_voltage_frames.shape[0], dtype=np.float32)
        )
        asymmetry_voltage = right_voltage - left_voltage
        super_class = (
            str(family_units["super_class"].dropna().astype(str).mode().iloc[0])
            if "super_class" in family_units and not family_units["super_class"].dropna().empty
            else "unknown"
        )
        rows.append(
            {
                "family": str(family),
                "super_class": super_class,
                "n_roots": int(family_indices.size),
                "sampled_fraction": float(family_units["sampled_overlay"].mean()),
                "mean_selected_frames": float(family_units["selected_frames"].mean()),
                "mean_spike_frames": float(family_units["spike_frames"].mean()),
                "corr_target_bearing_voltage": pearson_correlation(family_voltage, frame_target_bearing),
                "corr_target_bearing_asymmetry": pearson_correlation(asymmetry_voltage, frame_target_bearing),
                "corr_forward_speed_voltage": pearson_correlation(
                    family_voltage,
                    np.asarray(controller_by_label["forward_speed"], dtype=np.float32),
                ),
                "corr_turn_drive_asymmetry": pearson_correlation(
                    asymmetry_voltage,
                    np.asarray(controller_by_label["right_drive"], dtype=np.float32)
                    - np.asarray(controller_by_label["left_drive"], dtype=np.float32),
                ),
                "mean_spike_per_frame": float(family_spikes.mean()),
                "mean_voltage_mv": float(family_voltage.mean()),
            }
        )
    return pd.DataFrame(rows)


def summarize_condition_units(
    *,
    capture: Mapping[str, Any],
    root_ids: np.ndarray,
    xy: np.ndarray,
    extent: tuple[float, float, float, float],
    annotation_df: pd.DataFrame,
    sampled_overlay_root_ids: Iterable[int],
    max_brain_points: int,
    central_band_min: float,
    central_band_max: float,
) -> dict[str, Any]:
    brain_voltage_frames = np.asarray(capture["brain_voltage_frames"], dtype=np.float32)
    brain_spike_frames = np.asarray(capture["brain_spike_frames"], dtype=np.uint8)
    frame_target_bearing = np.asarray(capture["frame_target_bearing_body"], dtype=np.float32)
    rendered_summary, selected_counts, spike_counts, mean_voltage, max_voltage = summarize_rendered_activity(
        brain_voltage_frames=brain_voltage_frames,
        brain_spike_frames=brain_spike_frames,
        max_points=int(max_brain_points),
    )
    unit_table = build_unsampled_unit_table(
        root_ids=np.asarray(root_ids, dtype=np.int64),
        xy=np.asarray(xy, dtype=np.float32),
        extent=extent,
        selected_counts=selected_counts,
        spike_counts=spike_counts,
        mean_voltage=mean_voltage,
        max_voltage=max_voltage,
        annotation_df=annotation_df,
        sampled_overlay_root_ids=sampled_overlay_root_ids,
    )
    unsampled = unit_table[~unit_table["sampled_overlay"]].copy()
    central = unsampled[
        unsampled["x_norm"].between(float(central_band_min), float(central_band_max))
        & unsampled["y_norm"].between(float(central_band_min), float(central_band_max))
    ].copy()
    controller = _controller_by_label(capture)
    family_table = build_family_signal_table(
        unit_table=unit_table,
        brain_root_ids=np.asarray(root_ids, dtype=np.int64),
        brain_voltage_frames=brain_voltage_frames,
        brain_spike_frames=brain_spike_frames,
        frame_target_bearing=frame_target_bearing,
        controller_by_label=controller,
    )
    central_family_table = (
        central.groupby(["family", "super_class"], dropna=False)
        .agg(
            n_roots=("root_id", "count"),
            mean_selected_frames=("selected_frames", "mean"),
            total_selected_frames=("selected_frames", "sum"),
            mean_spike_frames=("spike_frames", "mean"),
            total_spike_frames=("spike_frames", "sum"),
            mean_voltage_mv=("mean_voltage", "mean"),
            max_voltage_mv=("max_voltage", "max"),
        )
        .reset_index()
        .sort_values(["total_spike_frames", "total_selected_frames"], ascending=[False, False])
        if not central.empty
        else pd.DataFrame(
            columns=[
                "family",
                "super_class",
                "n_roots",
                "mean_selected_frames",
                "total_selected_frames",
                "mean_spike_frames",
                "total_spike_frames",
                "mean_voltage_mv",
                "max_voltage_mv",
            ]
        )
    )
    return {
        "rendered_summary": rendered_summary,
        "unit_table": unit_table,
        "family_table": family_table,
        "central_units": central.sort_values(
            ["spike_frames", "selected_frames", "max_voltage"],
            ascending=[False, False, False],
        ).reset_index(drop=True),
        "central_family_table": central_family_table.reset_index(drop=True),
        "top_unsampled_spike_families": family_table[
            family_table["sampled_fraction"] <= 0.0
        ].sort_values(["mean_spike_frames", "mean_selected_frames"], ascending=[False, False]).reset_index(drop=True),
        "top_unsampled_visible_families": family_table[
            family_table["sampled_fraction"] <= 0.0
        ].sort_values(["mean_selected_frames", "mean_spike_frames"], ascending=[False, False]).reset_index(drop=True),
    }

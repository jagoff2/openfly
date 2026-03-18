from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd

from analysis.best_branch_investigation import (
    align_framewise_matrix,
    build_unsampled_unit_table,
    compute_selected_frame_counts,
    load_annotation_table,
    pearson_correlation,
)
from analysis.behavior_metrics import compute_behavior_metrics
from brain.public_ids import MOTOR_READOUT_IDS
from visualization.activation_viz import load_brain_layout
from bridge.decoder import _load_population_groups


def _sampled_overlay_root_ids(candidate_json_path: str | Path | None, fixed_groups: Mapping[str, Iterable[int]]) -> set[int]:
    sampled = {int(root_id) for group in fixed_groups.values() for root_id in group}
    if not candidate_json_path:
        return sampled
    payload = json.loads(Path(candidate_json_path).read_text(encoding="utf-8"))
    for item in payload.get("selected_paired_cell_types", []):
        for key in ("left_root_ids", "right_root_ids"):
            sampled.update(int(root_id) for root_id in item.get(key, []))
    return sampled


def _controller_by_label(capture: Mapping[str, Any]) -> dict[str, np.ndarray]:
    frame_cycles = np.asarray(capture["frame_cycles"], dtype=np.int64)
    controller_labels = np.asarray(capture["controller_labels"]).astype(str)
    controller_matrix = align_framewise_matrix(np.asarray(capture["controller_matrix"], dtype=np.float32), frame_cycles)
    return {
        str(label): controller_matrix[idx]
        for idx, label in enumerate(controller_labels)
    }


def _monitor_table(capture: Mapping[str, Any]) -> pd.DataFrame:
    frame_cycles = np.asarray(capture["frame_cycles"], dtype=np.int64)
    frame_target_bearing = np.asarray(capture["frame_target_bearing_body"], dtype=np.float32)
    monitor_labels = np.asarray(capture["monitor_labels"]).astype(str)
    monitor_matrix = align_framewise_matrix(np.asarray(capture["monitor_matrix"], dtype=np.float32), frame_cycles)
    controller = _controller_by_label(capture)
    rows = []
    for idx, label in enumerate(monitor_labels):
        trace = monitor_matrix[idx]
        rows.append(
            {
                "label": str(label),
                "corr_target_bearing": pearson_correlation(trace, frame_target_bearing),
                "corr_forward_speed": pearson_correlation(trace, controller["forward_speed"]),
                "corr_drive_asymmetry": pearson_correlation(trace, controller["right_drive"] - controller["left_drive"]),
                "mean_rate_hz": float(trace.mean()),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "label",
                "corr_target_bearing",
                "corr_forward_speed",
                "corr_drive_asymmetry",
                "mean_rate_hz",
            ]
        )
    return pd.DataFrame(rows).sort_values("corr_target_bearing", ascending=False)


def _monitor_voltage_table(
    *,
    capture: Mapping[str, Any],
    monitor_groups: Mapping[str, list[int]],
) -> pd.DataFrame:
    monitored_root_ids = np.asarray(capture.get("monitored_root_ids", []), dtype=np.int64)
    monitored_voltage_matrix = np.asarray(capture.get("monitored_voltage_matrix", []), dtype=np.float32)
    if monitored_root_ids.size == 0 or monitored_voltage_matrix.size == 0:
        return pd.DataFrame(
            columns=[
                "label",
                "corr_target_bearing",
                "corr_forward_speed",
                "corr_drive_asymmetry",
                "mean_voltage_mv",
            ]
        )
    frame_cycles = np.asarray(capture["frame_cycles"], dtype=np.int64)
    frame_target_bearing = np.asarray(capture["frame_target_bearing_body"], dtype=np.float32)
    monitored_voltage_matrix = align_framewise_matrix(monitored_voltage_matrix, frame_cycles)
    controller = _controller_by_label(capture)
    root_index = {int(root_id): idx for idx, root_id in enumerate(monitored_root_ids.tolist())}
    rows = []
    labels = sorted(
        {
            key[: -len("_left")]
            for key in monitor_groups.keys()
            if key.endswith("_left") and f"{key[: -len('_left')]}_right" in monitor_groups
        }
    )
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
                "corr_target_bearing": pearson_correlation(bilateral_voltage, frame_target_bearing),
                "corr_forward_speed": pearson_correlation(bilateral_voltage, controller["forward_speed"]),
                "corr_drive_asymmetry": pearson_correlation(asymmetry_voltage, controller["right_drive"] - controller["left_drive"]),
                "mean_voltage_mv": float(np.mean(bilateral_voltage)),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "label",
                "corr_target_bearing",
                "corr_forward_speed",
                "corr_drive_asymmetry",
                "mean_voltage_mv",
            ]
        )
    return pd.DataFrame(rows).sort_values("corr_target_bearing", ascending=False)


def _monitor_voltage_turn_table(
    *,
    capture: Mapping[str, Any],
    monitor_groups: Mapping[str, list[int]],
) -> pd.DataFrame:
    monitored_root_ids = np.asarray(capture.get("monitored_root_ids", []), dtype=np.int64)
    monitored_voltage_matrix = np.asarray(capture.get("monitored_voltage_matrix", []), dtype=np.float32)
    if monitored_root_ids.size == 0 or monitored_voltage_matrix.size == 0:
        return pd.DataFrame(
            columns=[
                "label",
                "corr_target_bearing",
                "corr_forward_speed",
                "corr_drive_asymmetry",
                "mean_voltage_mv",
                "mean_abs_asymmetry_voltage_mv",
            ]
        )
    frame_cycles = np.asarray(capture["frame_cycles"], dtype=np.int64)
    frame_target_bearing = np.asarray(capture["frame_target_bearing_body"], dtype=np.float32)
    monitored_voltage_matrix = align_framewise_matrix(monitored_voltage_matrix, frame_cycles)
    controller = _controller_by_label(capture)
    root_index = {int(root_id): idx for idx, root_id in enumerate(monitored_root_ids.tolist())}
    rows = []
    labels = sorted(
        {
            key[: -len("_left")]
            for key in monitor_groups.keys()
            if key.endswith("_left") and f"{key[: -len('_left')]}_right" in monitor_groups
        }
    )
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
                "corr_forward_speed": pearson_correlation(bilateral_voltage, controller["forward_speed"]),
                "corr_drive_asymmetry": pearson_correlation(asymmetry_voltage, controller["right_drive"] - controller["left_drive"]),
                "mean_voltage_mv": float(np.mean(bilateral_voltage)),
                "mean_abs_asymmetry_voltage_mv": float(np.mean(np.abs(asymmetry_voltage))),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "label",
                "corr_target_bearing",
                "corr_forward_speed",
                "corr_drive_asymmetry",
                "mean_voltage_mv",
                "mean_abs_asymmetry_voltage_mv",
            ]
        )
    table = pd.DataFrame(rows)
    return table.reindex(table["corr_target_bearing"].abs().sort_values(ascending=False).index).reset_index(drop=True)


def _family_signal_table(
    *,
    brain_layout,
    capture: Mapping[str, Any],
    annotation_df: pd.DataFrame,
    sampled_overlay_root_ids: set[int],
    max_brain_points: int,
) -> pd.DataFrame:
    brain_voltage_frames = np.asarray(capture["brain_voltage_frames"], dtype=np.float32)
    brain_spike_frames = np.asarray(capture["brain_spike_frames"], dtype=np.uint8)
    frame_target_bearing = np.asarray(capture["frame_target_bearing_body"], dtype=np.float32)
    controller = _controller_by_label(capture)
    selected_counts = compute_selected_frame_counts(
        brain_voltage_frames,
        brain_spike_frames,
        max_points=int(max_brain_points),
    )
    unit_table = build_unsampled_unit_table(
        root_ids=brain_layout.root_ids,
        xy=brain_layout.xy,
        extent=brain_layout.background_extent,
        selected_counts=selected_counts,
        spike_counts=brain_spike_frames.sum(axis=0),
        mean_voltage=brain_voltage_frames.mean(axis=0),
        max_voltage=brain_voltage_frames.max(axis=0),
        annotation_df=annotation_df,
        sampled_overlay_root_ids=sampled_overlay_root_ids,
    )
    rows = []
    for family, family_units in unit_table.groupby("family", dropna=False):
        if not family or str(family) == "UNKNOWN":
            continue
        family_root_ids = family_units["root_id"].to_numpy(dtype=np.int64)
        family_indices = np.flatnonzero(np.isin(brain_layout.root_ids, family_root_ids))
        if family_indices.size == 0:
            continue
        family_voltage = brain_voltage_frames[:, family_indices].mean(axis=1)
        family_spikes = brain_spike_frames[:, family_indices].mean(axis=1)
        left_root_ids = family_units.loc[family_units["side"].astype(str).str.lower() == "left", "root_id"].to_numpy(dtype=np.int64)
        right_root_ids = family_units.loc[family_units["side"].astype(str).str.lower() == "right", "root_id"].to_numpy(dtype=np.int64)
        left_indices = np.flatnonzero(np.isin(brain_layout.root_ids, left_root_ids))
        right_indices = np.flatnonzero(np.isin(brain_layout.root_ids, right_root_ids))
        left_voltage = brain_voltage_frames[:, left_indices].mean(axis=1) if left_indices.size else np.zeros(brain_voltage_frames.shape[0], dtype=np.float32)
        right_voltage = brain_voltage_frames[:, right_indices].mean(axis=1) if right_indices.size else np.zeros(brain_voltage_frames.shape[0], dtype=np.float32)
        asymmetry_voltage = right_voltage - left_voltage
        sampled_fraction = float(family_units["sampled_overlay"].mean())
        super_class = str(family_units.get("super_class", pd.Series(dtype=object)).dropna().astype(str).mode().iloc[0]) if family_units.get("super_class") is not None and not family_units.get("super_class").dropna().empty else "unknown"
        rows.append(
            {
                "family": str(family),
                "super_class": super_class,
                "n_roots": int(family_indices.size),
                "sampled_fraction": sampled_fraction,
                "mean_selected_frames": float(family_units["selected_frames"].mean()),
                "mean_spike_frames": float(family_units["spike_frames"].mean()),
                "corr_target_bearing": pearson_correlation(family_voltage, frame_target_bearing),
                "corr_target_bearing_asymmetry": pearson_correlation(asymmetry_voltage, frame_target_bearing),
                "corr_forward_speed": pearson_correlation(family_voltage, controller["forward_speed"]),
                "corr_drive_asymmetry": pearson_correlation(family_voltage, controller["right_drive"] - controller["left_drive"]),
                "corr_drive_asymmetry_voltage": pearson_correlation(asymmetry_voltage, controller["right_drive"] - controller["left_drive"]),
                "mean_voltage": float(family_voltage.mean()),
                "mean_abs_asymmetry_voltage": float(np.mean(np.abs(asymmetry_voltage))),
                "mean_spike_per_frame": float(family_spikes.mean()),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "family",
                "super_class",
                "n_roots",
                "sampled_fraction",
                "mean_selected_frames",
                "mean_spike_frames",
                "corr_target_bearing",
                "corr_target_bearing_asymmetry",
                "corr_forward_speed",
                "corr_drive_asymmetry",
                "corr_drive_asymmetry_voltage",
                "mean_voltage",
                "mean_abs_asymmetry_voltage",
                "mean_spike_per_frame",
            ]
        )
    return pd.DataFrame(rows).sort_values(
        ["corr_target_bearing", "corr_forward_speed", "mean_selected_frames"],
        ascending=[False, False, False],
    )


def _rank_turn_family_candidates(family_table: pd.DataFrame, limit: int) -> pd.DataFrame:
    if family_table.empty:
        return family_table.copy()
    table = family_table.copy()
    table["turn_specificity_score"] = (
        table["corr_target_bearing_asymmetry"].abs()
        + 0.6 * table["corr_drive_asymmetry_voltage"].abs()
        - 0.3 * table["corr_forward_speed"].abs()
        - 0.25 * table["sampled_fraction"].fillna(0.0)
    )
    table = table.sort_values(
        ["turn_specificity_score", "corr_target_bearing_asymmetry", "corr_drive_asymmetry_voltage"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    return table.head(limit).copy()


def _rank_turn_monitor_candidates(monitor_turn_table: pd.DataFrame, limit: int) -> pd.DataFrame:
    if monitor_turn_table.empty:
        return monitor_turn_table.copy()
    table = monitor_turn_table.copy()
    table["turn_specificity_score"] = (
        table["corr_target_bearing"].abs()
        + 0.6 * table["corr_drive_asymmetry"].abs()
        - 0.3 * table["corr_forward_speed"].abs()
    )
    table = table.sort_values(
        ["turn_specificity_score", "corr_target_bearing", "corr_drive_asymmetry"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    return table.head(limit).copy()


def _family_turn_table(family_table: pd.DataFrame) -> pd.DataFrame:
    if family_table.empty:
        return pd.DataFrame(
            columns=[
                "family",
                "super_class",
                "n_roots",
                "sampled_fraction",
                "corr_target_bearing",
                "corr_forward_speed",
                "corr_drive_asymmetry",
                "mean_voltage",
                "mean_spike_per_frame",
            ]
        )
    table = family_table.copy()
    table["corr_target_bearing"] = table["corr_target_bearing_asymmetry"]
    table["corr_drive_asymmetry"] = table["corr_drive_asymmetry_voltage"]
    table["mean_voltage"] = table["mean_abs_asymmetry_voltage"]
    return table.reindex(table["corr_target_bearing"].abs().sort_values(ascending=False).index).reset_index(drop=True)


def _behavior_diagnosis(log_path: str | Path | None) -> dict[str, Any]:
    if not log_path:
        return {}
    records = [json.loads(line) for line in Path(log_path).read_text(encoding="utf-8").splitlines() if line.strip()]
    if not records:
        return {}
    return compute_behavior_metrics(records)


def _behavior_focus(behavior: Mapping[str, Any]) -> list[str]:
    target_metrics = behavior.get("target_condition", {}) if isinstance(behavior, Mapping) else {}
    spontaneous = behavior.get("spontaneous_locomotion", {}) if isinstance(behavior, Mapping) else {}
    controller = behavior.get("controller_summary", {}) if isinstance(behavior, Mapping) else {}
    notes: list[str] = []
    if bool(target_metrics.get("enabled", False)):
        if float(target_metrics.get("turn_alignment_fraction_active", 0.0) or 0.0) < 0.55:
            notes.append("target is present but active turns do not align reliably with target bearing; prioritize relay-to-descending steering transfer")
        if float(target_metrics.get("bearing_reduction_rad", 0.0) or 0.0) <= 0.0:
            notes.append("target-bearing error is not shrinking over the run; do not treat higher locomotion as improved pursuit")
        if float(target_metrics.get("fixation_fraction_20deg", 0.0) or 0.0) < 0.15:
            notes.append("target fixation remains weak; evaluate fixation/alignment before speed or displacement")
    if float(spontaneous.get("locomotor_active_fraction", 0.0) or 0.0) < 0.25:
        notes.append("locomotor richness is still sparse; waking the brain should not depend on target presence")
    if float(spontaneous.get("controller_state_entropy", 0.0) or 0.0) < 0.2:
        notes.append("controller state entropy is low; behavior still looks compressed rather than fly-like")
    if float(controller.get("forward_gt_abs_turn_fraction", 0.0) or 0.0) < 0.2:
        notes.append("turn dominates forward recruitment; motor decoding still over-compresses into steering")
    return notes


def propose_decoding_cycle(
    *,
    config_path: str | Path,
    capture_path: str | Path,
    log_path: str | Path | None = None,
    max_brain_points: int = 6000,
    monitor_limit: int = 12,
    relay_limit: int = 12,
) -> dict[str, Any]:
    import yaml

    with Path(config_path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    capture = np.load(Path(capture_path), allow_pickle=True)

    fixed_groups = {
        "P9_L": MOTOR_READOUT_IDS["forward_left"],
        "P9_R": MOTOR_READOUT_IDS["forward_right"],
        "DNa_L": MOTOR_READOUT_IDS["turn_left"],
        "DNa_R": MOTOR_READOUT_IDS["turn_right"],
        "MDN": MOTOR_READOUT_IDS["reverse"],
    }
    candidate_json = config.get("decoder", {}).get("monitor_candidates_json") or config.get("decoder", {}).get("population_candidates_json")
    brain_layout = load_brain_layout(
        annotation_path=config["visual_splice"]["annotation_path"],
        completeness_path=config["brain"]["completeness_path"],
        candidate_json=candidate_json,
        fixed_groups=fixed_groups,
    )
    annotation_df = load_annotation_table(config["visual_splice"]["annotation_path"])
    sampled_overlay_ids = _sampled_overlay_root_ids(candidate_json, fixed_groups)
    monitor_groups = _load_population_groups(candidate_json)
    family_table = _family_signal_table(
        brain_layout=brain_layout,
        capture=capture,
        annotation_df=annotation_df,
        sampled_overlay_root_ids=sampled_overlay_ids,
        max_brain_points=max_brain_points,
    )
    family_turn_table = _family_turn_table(family_table)
    monitor_table = _monitor_table(capture)
    monitor_voltage_table = _monitor_voltage_table(capture=capture, monitor_groups=monitor_groups)
    monitor_voltage_turn_table = _monitor_voltage_turn_table(capture=capture, monitor_groups=monitor_groups)

    unsampled_family_table = family_table[family_table["sampled_fraction"] < 0.5].copy()
    unsampled_family_turn_table = family_turn_table[family_turn_table["sampled_fraction"] < 0.5].copy()
    upstream_mask = unsampled_family_table["super_class"].astype(str).str.lower().isin(
        {"visual_projection", "visual_centrifugal", "central", "ascending"}
    )
    upstream_turn_mask = unsampled_family_turn_table["super_class"].astype(str).str.lower().isin(
        {"visual_projection", "visual_centrifugal", "central", "ascending"}
    )
    upstream_candidates = unsampled_family_table[upstream_mask].head(relay_limit)
    upstream_turn_candidates = _rank_turn_family_candidates(unsampled_family_turn_table[upstream_turn_mask], relay_limit)
    monitor_expansion = unsampled_family_table.head(monitor_limit)
    monitor_turn_candidates = _rank_turn_monitor_candidates(monitor_voltage_turn_table, monitor_limit)

    current_monitor_labels = [str(label) for label in np.asarray(capture["monitor_labels"]).astype(str).tolist()]
    best_monitor_corr = float(monitor_table.iloc[0]["corr_target_bearing"]) if not monitor_table.empty else float("nan")
    behavior = _behavior_diagnosis(log_path)

    structured_signal_library = []
    for _, row in upstream_candidates.iterrows():
        structured_signal_library.append(
            {
                "family": str(row["family"]),
                "super_class": str(row["super_class"]),
                "signals": [
                    "bilateral_mean_voltage",
                    "right_minus_left_voltage",
                    "bilateral_spike_fraction",
                ],
                "reason": "upstream family outranks current monitored decoder labels for target-bearing structure",
            }
        )
    structured_turn_signal_library = []
    for _, row in upstream_turn_candidates.iterrows():
        structured_turn_signal_library.append(
            {
                "family": str(row["family"]),
                "super_class": str(row["super_class"]),
                "signals": [
                    "right_minus_left_voltage",
                    "bilateral_mean_voltage",
                    "bilateral_spike_fraction",
                ],
                "reason": "family shows strong lateralized voltage alignment to target-bearing and controller asymmetry",
            }
        )

    return {
        "config_path": str(config_path),
        "capture_path": str(capture_path),
        "log_path": None if log_path is None else str(log_path),
        "current_monitor_labels": current_monitor_labels,
        "behavior_diagnosis": behavior,
        "behavior_focus": _behavior_focus(behavior),
        "best_monitor_target_bearing_corr": best_monitor_corr,
        "best_monitor_voltage_target_bearing_corr": None if monitor_voltage_table.empty else float(monitor_voltage_table.iloc[0]["corr_target_bearing"]),
        "best_monitor_voltage_turn_target_bearing_corr": None if monitor_voltage_turn_table.empty else float(monitor_voltage_turn_table.iloc[0]["corr_target_bearing"]),
        "recommendations": {
            "monitor_expansion_families": monitor_expansion["family"].astype(str).tolist(),
            "relay_probe_families": upstream_candidates["family"].astype(str).tolist(),
            "relay_turn_probe_families": upstream_turn_candidates["family"].astype(str).tolist(),
            "monitor_turn_labels": monitor_turn_candidates["label"].astype(str).tolist(),
            "guardrails": [
                "keep decoder/body shortcuts disabled",
                "promote new families first as monitoring-only relay checkpoints",
                "require matched target/no_target/zero_brain controls before promoting any family into control",
                "treat spontaneous-state as a background condition, not a motor floor",
                "shadow-test VNC semantics against descending latents before actuator promotion",
            ],
            "structured_signal_library": structured_signal_library,
            "structured_turn_signal_library": structured_turn_signal_library,
        },
        "tables": {
            "family_scores": family_table,
            "family_turn_scores": family_turn_table,
            "monitor_scores": monitor_table,
            "monitor_voltage_scores": monitor_voltage_table,
            "monitor_voltage_turn_scores": monitor_voltage_turn_table,
            "monitor_expansion": monitor_expansion,
            "relay_candidates": upstream_candidates,
            "relay_turn_candidates": upstream_turn_candidates,
            "monitor_turn_candidates": monitor_turn_candidates,
        },
    }

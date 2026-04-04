from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from analysis.best_branch_investigation import pearson_correlation


def load_run_records(log_path: str | Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in Path(log_path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _float_array(values: Iterable[Any], *, default: float = 0.0) -> np.ndarray:
    return np.asarray([float(default if value is None else value) for value in values], dtype=np.float32)


def _record_forward_speed(record: Mapping[str, Any]) -> float:
    visual_speed_state = record.get("body_metadata", {}).get("visual_speed_state", {})
    if isinstance(visual_speed_state, Mapping) and str(visual_speed_state.get("speed_source", "")) == "treadmill_ball":
        return float(visual_speed_state.get("fly_forward_speed_mm_s_measured", record.get("forward_speed", 0.0)))
    return float(record.get("forward_speed", 0.0))


def _extract_trace(records: list[Mapping[str, Any]]) -> dict[str, np.ndarray]:
    sim_time = _float_array(record.get("sim_time", 0.0) for record in records)
    left_drive = _float_array(record.get("left_drive", 0.0) for record in records)
    right_drive = _float_array(record.get("right_drive", 0.0) for record in records)
    forward_speed = _float_array(_record_forward_speed(record) for record in records)
    yaw = _float_array(record.get("yaw", 0.0) for record in records)
    yaw_rate = _float_array(record.get("yaw_rate", 0.0) for record in records)
    forward_signal = _float_array(
        record.get("motor_signals", {}).get("forward_signal", 0.0)
        for record in records
    )
    turn_signal = _float_array(
        record.get("motor_signals", {}).get("turn_signal", 0.0)
        for record in records
    )
    target_enabled = np.asarray(
        [bool(record.get("target_state", {}).get("enabled", False)) for record in records],
        dtype=bool,
    )
    target_visible = np.asarray(
        [
            bool(record.get("target_state", {}).get("visible", record.get("target_state", {}).get("enabled", False)))
            for record in records
        ],
        dtype=bool,
    )
    target_bearing = np.asarray(
        [
            float(record.get("target_state", {}).get("bearing_body", math.nan))
            if bool(record.get("target_state", {}).get("enabled", False))
            else math.nan
            for record in records
        ],
        dtype=np.float32,
    )
    target_distance = np.asarray(
        [
            float(record.get("target_state", {}).get("distance", math.nan))
            if bool(record.get("target_state", {}).get("enabled", False))
            else math.nan
            for record in records
        ],
        dtype=np.float32,
    )
    target_event_id = np.asarray(
        [int(record.get("target_state", {}).get("last_event_id", 0) or 0) for record in records],
        dtype=np.int64,
    )
    target_event_kind = np.asarray(
        [str(record.get("target_state", {}).get("last_event_kind", "") or "") for record in records],
        dtype=object,
    )
    return {
        "sim_time": sim_time,
        "left_drive": left_drive,
        "right_drive": right_drive,
        "forward_speed": forward_speed,
        "yaw": yaw,
        "yaw_rate": yaw_rate,
        "forward_signal": forward_signal,
        "turn_signal": turn_signal,
        "target_enabled": target_enabled,
        "target_visible": target_visible,
        "target_bearing": target_bearing,
        "target_distance": target_distance,
        "target_event_id": target_event_id,
        "target_event_kind": target_event_kind,
    }


def _estimate_dt(sim_time: np.ndarray) -> float:
    if sim_time.size < 2:
        return 0.0
    diffs = np.diff(sim_time)
    diffs = diffs[np.isfinite(diffs) & (diffs > 0.0)]
    if diffs.size == 0:
        return 0.0
    return float(np.median(diffs))


def _safe_mean(array: np.ndarray) -> float:
    return float(np.mean(array)) if array.size else 0.0


def _safe_std(array: np.ndarray) -> float:
    return float(np.std(array)) if array.size else 0.0


def _window_mean(array: np.ndarray, *, head: bool, fraction: float = 0.1) -> float:
    if array.size == 0:
        return float("nan")
    count = max(1, int(round(array.size * float(fraction))))
    window = array[:count] if head else array[-count:]
    return float(np.mean(window))


def _first_latency(sim_time: np.ndarray, mask: np.ndarray) -> float | None:
    if sim_time.size == 0 or mask.size == 0:
        return None
    hits = np.flatnonzero(mask)
    if hits.size == 0:
        return None
    return float(sim_time[hits[0]] - sim_time[0])


def _windowed_latency(
    sim_time: np.ndarray,
    event_start_s: float,
    mask: np.ndarray,
    *,
    max_window_s: float,
) -> float | None:
    if sim_time.size == 0 or mask.size == 0:
        return None
    window_mask = (sim_time >= event_start_s) & (sim_time <= event_start_s + max_window_s)
    hits = np.flatnonzero(window_mask & mask.astype(bool))
    if hits.size == 0:
        return None
    return float(sim_time[hits[0]] - event_start_s)


def _bout_stats(mask: np.ndarray, dt: float) -> dict[str, float]:
    if mask.size == 0:
        return {
            "count": 0.0,
            "mean_duration_s": 0.0,
            "max_duration_s": 0.0,
        }
    padded = np.concatenate(([False], mask.astype(bool), [False]))
    starts = np.flatnonzero(~padded[:-1] & padded[1:])
    stops = np.flatnonzero(padded[:-1] & ~padded[1:])
    lengths = stops - starts
    if lengths.size == 0:
        return {
            "count": 0.0,
            "mean_duration_s": 0.0,
            "max_duration_s": 0.0,
        }
    durations = lengths.astype(np.float32) * float(dt)
    return {
        "count": float(lengths.size),
        "mean_duration_s": float(np.mean(durations)),
        "max_duration_s": float(np.max(durations)),
    }


def _normalized_entropy(states: np.ndarray, num_states: int) -> float:
    if states.size == 0 or num_states <= 1:
        return 0.0
    counts = np.bincount(states.astype(np.int64), minlength=num_states).astype(np.float64)
    probs = counts[counts > 0.0] / counts.sum()
    if probs.size == 0:
        return 0.0
    entropy = -float(np.sum(probs * np.log2(probs)))
    return float(entropy / math.log2(float(num_states)))


def _controller_state_entropy(
    mean_drive: np.ndarray,
    turn_drive: np.ndarray,
    forward_signal: np.ndarray,
    turn_signal: np.ndarray,
) -> float:
    forward_level = np.zeros(mean_drive.shape, dtype=np.int64)
    forward_level[(mean_drive > 0.05) | (forward_signal > 0.05)] = 1
    forward_level[(mean_drive < -0.05) | (forward_signal < -0.05)] = -1

    turn_level = np.zeros(turn_drive.shape, dtype=np.int64)
    turn_level[(turn_drive > 0.05) | (turn_signal > 0.05)] = 1
    turn_level[(turn_drive < -0.05) | (turn_signal < -0.05)] = -1

    state_id = (forward_level + 1) * 3 + (turn_level + 1)
    return _normalized_entropy(state_id, 9)


def compute_behavior_metrics(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "sample_count": 0,
            "duration_s": 0.0,
            "dt_s": 0.0,
            "target_condition": {"enabled": False},
            "target_perturbation": {"enabled": False},
            "spontaneous_locomotion": {},
            "controller_summary": {},
        }

    trace = _extract_trace(records)
    sim_time = trace["sim_time"]
    dt = _estimate_dt(sim_time)
    duration_s = float(sim_time[-1] - sim_time[0]) if sim_time.size > 1 else 0.0
    left_drive = trace["left_drive"]
    right_drive = trace["right_drive"]
    forward_speed = trace["forward_speed"]
    yaw = trace["yaw"]
    yaw_rate = trace["yaw_rate"]
    forward_signal = trace["forward_signal"]
    turn_signal = trace["turn_signal"]
    turn_drive = right_drive - left_drive
    mean_drive = 0.5 * (left_drive + right_drive)

    locomotor_active = (
        (np.abs(mean_drive) > 0.05)
        | (forward_signal > 0.05)
        | (forward_speed > 1.0)
    )
    turn_active = (
        (np.abs(turn_drive) > 0.05)
        | (np.abs(turn_signal) > 0.05)
        | (np.abs(yaw_rate) > 0.2)
    )
    locomotor_bouts = _bout_stats(locomotor_active, dt)
    turn_bouts = _bout_stats(turn_active, dt)
    active_turn_sign = np.sign(turn_drive[turn_active])
    turn_switches = 0
    if active_turn_sign.size > 1:
        turn_switches = int(np.sum(active_turn_sign[1:] * active_turn_sign[:-1] < 0.0))

    controller_entropy = _controller_state_entropy(
        mean_drive=mean_drive,
        turn_drive=turn_drive,
        forward_signal=forward_signal,
        turn_signal=turn_signal,
    )

    spontaneous = {
        "locomotor_active_fraction": float(np.mean(locomotor_active)),
        "turn_active_fraction": float(np.mean(turn_active)),
        "locomotor_bout_count": locomotor_bouts["count"],
        "mean_locomotor_bout_duration_s": locomotor_bouts["mean_duration_s"],
        "max_locomotor_bout_duration_s": locomotor_bouts["max_duration_s"],
        "turn_bout_count": turn_bouts["count"],
        "mean_turn_bout_duration_s": turn_bouts["mean_duration_s"],
        "max_turn_bout_duration_s": turn_bouts["max_duration_s"],
        "controller_state_entropy": controller_entropy,
        "mean_forward_speed": _safe_mean(forward_speed),
        "mean_abs_yaw_rate": _safe_mean(np.abs(yaw_rate)),
        "heading_std_rad": _safe_std(yaw),
        "mean_turn_drive": _safe_mean(turn_drive),
        "mean_abs_turn_drive": _safe_mean(np.abs(turn_drive)),
        "right_turn_dominant_fraction": float(np.mean(turn_drive > 1e-6)),
        "left_turn_dominant_fraction": float(np.mean(turn_drive < -1e-6)),
        "turn_switch_count": float(turn_switches),
        "turn_switch_rate_hz": float(turn_switches / max(duration_s, 1e-6)),
    }

    target_enabled_mask = np.asarray(trace["target_enabled"], dtype=bool)
    target_visible_mask = target_enabled_mask & np.asarray(trace["target_visible"], dtype=bool)
    target_metrics: dict[str, Any] = {"enabled": bool(np.any(target_enabled_mask))}
    if np.any(target_visible_mask):
        target_bearing = trace["target_bearing"][target_visible_mask]
        target_distance = trace["target_distance"][target_visible_mask]
        target_sim_time = sim_time[target_visible_mask]
        target_turn_drive = turn_drive[target_visible_mask]
        target_yaw_rate = yaw_rate[target_visible_mask]
        target_turn_active = turn_active[target_visible_mask]
        abs_bearing = np.abs(target_bearing)
        bearing_threshold = 0.35
        alignment_mask = abs_bearing >= 0.2
        aligned_turn_mask = alignment_mask & target_turn_active & (np.sign(target_turn_drive) == np.sign(target_bearing))
        approach_steps = np.diff(target_distance)
        bearing_steps = np.diff(abs_bearing)
        target_metrics.update(
            {
                "sample_count": int(target_bearing.size),
                "visible_fraction": float(np.mean(target_visible_mask[target_enabled_mask])) if np.any(target_enabled_mask) else 0.0,
                "mean_abs_bearing_rad": _safe_mean(abs_bearing),
                "median_abs_bearing_rad": float(np.median(abs_bearing)) if abs_bearing.size else float("nan"),
                "initial_abs_bearing_rad": _window_mean(abs_bearing, head=True),
                "final_abs_bearing_rad": _window_mean(abs_bearing, head=False),
                "bearing_reduction_rad": float(_window_mean(abs_bearing, head=True) - _window_mean(abs_bearing, head=False)),
                "fixation_fraction_20deg": float(np.mean(abs_bearing <= bearing_threshold)),
                "fixation_fraction_30deg": float(np.mean(abs_bearing <= 0.52)),
                "approach_fraction": float(np.mean(approach_steps < 0.0)) if approach_steps.size else 0.0,
                "bearing_improvement_fraction": float(np.mean(bearing_steps < 0.0)) if bearing_steps.size else 0.0,
                "turn_alignment_fraction_active": float(np.mean(np.sign(target_turn_drive[target_turn_active & alignment_mask]) == np.sign(target_bearing[target_turn_active & alignment_mask])))
                if np.any(target_turn_active & alignment_mask)
                else 0.0,
                "turn_alignment_fraction_all": float(np.mean(np.sign(target_turn_drive[alignment_mask]) == np.sign(target_bearing[alignment_mask])))
                if np.any(alignment_mask)
                else 0.0,
                "aligned_turn_fraction": float(np.mean(aligned_turn_mask)),
                "turn_bearing_corr": pearson_correlation(target_turn_drive, target_bearing),
                "yaw_bearing_corr": pearson_correlation(target_yaw_rate, target_bearing),
                "distance_bearing_corr": pearson_correlation(target_distance, abs_bearing),
                "aligned_turn_latency_s": _first_latency(target_sim_time, aligned_turn_mask),
                "fixation_latency_s": _first_latency(target_sim_time, abs_bearing <= bearing_threshold),
                "mean_target_distance": _safe_mean(target_distance[np.isfinite(target_distance)]),
            }
        )
    elif np.any(target_enabled_mask):
        target_metrics.update(
            {
                "sample_count": 0,
                "visible_fraction": float(np.mean(target_visible_mask[target_enabled_mask])),
            }
        )

    perturbation_metrics: dict[str, Any] = {"enabled": bool(np.any(target_enabled_mask))}
    if np.any(target_enabled_mask):
        event_ids = np.asarray(trace["target_event_id"], dtype=np.int64)
        event_kinds = trace["target_event_kind"]
        event_onsets = np.flatnonzero(event_ids > np.concatenate(([0], event_ids[:-1])))
        jump_onsets = [int(index) for index in event_onsets if str(event_kinds[index]) == "jump"]
        hide_start_onsets = [int(index) for index in event_onsets if str(event_kinds[index]) == "hide_start"]
        hide_end_onsets = [int(index) for index in event_onsets if str(event_kinds[index]) == "hide_end"]
        perturbation_metrics.update(
            {
                "jump_event_count": int(len(jump_onsets)),
                "removal_event_count": int(len(hide_start_onsets)),
            }
        )
        if jump_onsets:
            jump_index = jump_onsets[0]
            jump_time_s = float(sim_time[jump_index])
            jump_window_mask = target_enabled_mask & (sim_time >= jump_time_s) & (sim_time <= jump_time_s + 0.25)
            jump_refixation_mask = target_enabled_mask & (sim_time >= jump_time_s) & (sim_time <= jump_time_s + 2.0)
            jump_turn_active_mask = jump_window_mask & turn_active & (np.abs(trace["target_bearing"]) >= 0.2)
            jump_abs_bearing = np.abs(trace["target_bearing"][jump_refixation_mask])
            initial_jump_abs_bearing = float(abs(trace["target_bearing"][jump_index]))
            final_jump_abs_bearing = float(np.mean(jump_abs_bearing[-max(1, min(jump_abs_bearing.size, 25)):])) if jump_abs_bearing.size else float("nan")
            bearing_recovery_fraction = 0.0
            if initial_jump_abs_bearing > 1e-6 and np.isfinite(final_jump_abs_bearing):
                bearing_recovery_fraction = float((initial_jump_abs_bearing - final_jump_abs_bearing) / initial_jump_abs_bearing)
            perturbation_metrics.update(
                {
                    "first_jump_time_s": jump_time_s,
                    "jump_turn_alignment_fraction_active": float(
                        np.mean(
                            np.sign(turn_drive[jump_turn_active_mask])
                            == np.sign(trace["target_bearing"][jump_turn_active_mask])
                        )
                    )
                    if np.any(jump_turn_active_mask)
                    else 0.0,
                    "jump_turn_bearing_corr": pearson_correlation(
                        turn_drive[jump_window_mask],
                        trace["target_bearing"][jump_window_mask],
                    )
                    if np.any(jump_window_mask)
                    else 0.0,
                    "jump_refixation_latency_s": _windowed_latency(
                        sim_time,
                        jump_time_s,
                        target_enabled_mask & (np.abs(trace["target_bearing"]) <= 0.35),
                        max_window_s=2.0,
                    ),
                    "jump_refixation_fraction_20deg": float(
                        np.mean(jump_abs_bearing <= 0.35)
                    )
                    if jump_abs_bearing.size
                    else 0.0,
                    "jump_bearing_recovery_fraction_2s": bearing_recovery_fraction,
                }
            )
        if hide_start_onsets:
            hide_start_index = hide_start_onsets[0]
            hide_start_time_s = float(sim_time[hide_start_index])
            hide_end_index = next((index for index in hide_end_onsets if index > hide_start_index), None)
            hide_end_time_s = float(sim_time[hide_end_index]) if hide_end_index is not None else None
            hidden_mask = target_enabled_mask & ~target_visible_mask
            if hide_end_time_s is not None:
                hidden_mask &= (sim_time >= hide_start_time_s) & (sim_time < hide_end_time_s)
            hidden_turn_active_mask = hidden_mask & turn_active & (np.abs(trace["target_bearing"]) >= 0.2)
            hidden_abs_bearing = np.abs(trace["target_bearing"][hidden_mask])
            perturbation_metrics.update(
                {
                    "first_removal_time_s": hide_start_time_s,
                    "removal_persistence_duration_s": 0.0 if hide_end_time_s is None else float(max(0.0, hide_end_time_s - hide_start_time_s)),
                    "removal_persistence_turn_alignment_fraction": float(
                        np.mean(
                            np.sign(turn_drive[hidden_turn_active_mask])
                            == np.sign(trace["target_bearing"][hidden_turn_active_mask])
                        )
                    )
                    if np.any(hidden_turn_active_mask)
                    else 0.0,
                    "removal_mean_abs_bearing_rad": _safe_mean(hidden_abs_bearing[np.isfinite(hidden_abs_bearing)]),
                }
            )
            if hide_end_time_s is not None:
                restore_visible_mask = target_visible_mask & (sim_time >= hide_end_time_s) & (sim_time <= hide_end_time_s + 2.0)
                restore_abs_bearing = np.abs(trace["target_bearing"][restore_visible_mask])
                perturbation_metrics.update(
                    {
                        "removal_post_return_refixation_latency_s": _windowed_latency(
                            sim_time,
                            hide_end_time_s,
                            target_visible_mask & (np.abs(trace["target_bearing"]) <= 0.35),
                            max_window_s=2.0,
                        ),
                        "removal_post_return_fixation_fraction_20deg": float(np.mean(restore_abs_bearing <= 0.35))
                        if restore_abs_bearing.size
                        else 0.0,
                    }
                )

    controller_summary = {
        "forward_nonzero_fraction": float(np.mean(np.abs(forward_signal) > 1e-6)),
        "turn_nonzero_fraction": float(np.mean(np.abs(turn_signal) > 1e-6)),
        "forward_gt_abs_turn_fraction": float(np.mean(forward_signal > np.abs(turn_signal))),
        "right_drive_dominant_fraction": float(np.mean(turn_drive > 1e-6)),
        "left_drive_dominant_fraction": float(np.mean(turn_drive < -1e-6)),
    }

    return {
        "sample_count": int(sim_time.size),
        "duration_s": duration_s,
        "dt_s": dt,
        "target_condition": target_metrics,
        "target_perturbation": perturbation_metrics,
        "spontaneous_locomotion": spontaneous,
        "controller_summary": controller_summary,
    }


def flatten_behavior_metrics(metrics: Mapping[str, Any]) -> dict[str, float | str | bool | None]:
    flat: dict[str, float | str | bool | None] = {
        "sample_count": int(metrics.get("sample_count", 0)),
        "duration_s": float(metrics.get("duration_s", 0.0)),
        "dt_s": float(metrics.get("dt_s", 0.0)),
    }
    for section_name in ("target_condition", "target_perturbation", "spontaneous_locomotion", "controller_summary"):
        section = metrics.get(section_name, {})
        if not isinstance(section, Mapping):
            continue
        for key, value in section.items():
            flat[f"{section_name}_{key}"] = value
    return flat

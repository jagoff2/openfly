from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from analysis.best_branch_investigation import pearson_correlation


def _float_array(values: list[Any]) -> np.ndarray:
    return np.asarray([float(value) for value in values], dtype=np.float32)


def _mean_or_zero(values: np.ndarray) -> float:
    return float(np.mean(values)) if values.size else 0.0


def _extract_visual_speed_table(records: list[Mapping[str, Any]]) -> dict[str, np.ndarray] | None:
    states = [record.get("body_metadata", {}).get("visual_speed_state") for record in records]
    if not states or not any(isinstance(state, Mapping) and bool(state.get("enabled", False)) for state in states):
        return None
    return {
        "sim_time": _float_array([record.get("sim_time", 0.0) for record in records]),
        "forward_speed": _float_array(
            [
                (
                    state.get("fly_forward_speed_mm_s_measured", record.get("forward_speed", 0.0))
                    if isinstance(state, Mapping) and str(state.get("speed_source", "")) == "treadmill_ball"
                    else record.get("forward_speed", 0.0)
                )
                for record, state in zip(records, states)
            ]
        ),
        "scene_speed": _float_array(
            [
                (state.get("scene_world_speed_mm_s", 0.0) if isinstance(state, Mapping) else 0.0)
                for state in states
            ]
        ),
        "effective_visual_speed": _float_array(
            [
                (state.get("effective_visual_speed_mm_s", 0.0) if isinstance(state, Mapping) else 0.0)
                for state in states
            ]
        ),
        "retinal_slip": _float_array(
            [
                (
                    state.get("retinal_slip_mm_s", state.get("effective_visual_speed_mm_s", 0.0))
                    if isinstance(state, Mapping)
                    else 0.0
                )
                for state in states
            ]
        ),
        "gain": _float_array(
            [
                (state.get("gain", 1.0) if isinstance(state, Mapping) else 1.0)
                for state in states
            ]
        ),
        "corridor_half_width": _float_array(
            [
                (state.get("corridor_half_width_mm_at_fly", 0.0) if isinstance(state, Mapping) else 0.0)
                for state in states
            ]
        ),
        "fly_x_mm": _float_array(
            [
                (state.get("fly_x_mm", 0.0) if isinstance(state, Mapping) else 0.0)
                for state in states
            ]
        ),
        "track_x_mm": _float_array(
            [
                (
                    state.get(
                        "track_x_mm",
                        state.get("fly_x_mm", 0.0),
                    )
                    if isinstance(state, Mapping)
                    else 0.0
                )
                for state in states
            ]
        ),
        "stimulus_active": np.asarray(
            [
                bool(state.get("stimulus_active", False)) if isinstance(state, Mapping) else False
                for state in states
            ],
            dtype=bool,
        ),
        "mode": np.asarray(
            [
                str(state.get("mode", "")) if isinstance(state, Mapping) else ""
                for state in states
            ],
            dtype=object,
        ),
        "block_index": _float_array(
            [
                (state.get("block_index", -1.0) if isinstance(state, Mapping) else -1.0)
                for state in states
            ]
        ),
        "block_kind": np.asarray(
            [
                (str(state.get("block_kind", "")) if isinstance(state, Mapping) else "")
                for state in states
            ],
            dtype=object,
        ),
        "block_label": np.asarray(
            [
                (str(state.get("block_label", "")) if isinstance(state, Mapping) else "")
                for state in states
            ],
            dtype=object,
        ),
        "turn_signal": _float_array(
            [
                float(
                    record.get("motor_signals", {}).get(
                        "turn_signal",
                        0.5 * (float(record.get("right_drive", 0.0)) - float(record.get("left_drive", 0.0))),
                    )
                )
                for record in records
            ]
        ),
        "yaw_rate": _float_array([record.get("yaw_rate", 0.0) for record in records]),
    }


def _summarize_interleaved_blocks(table: Mapping[str, np.ndarray]) -> dict[str, Any]:
    block_index = table["block_index"].astype(int)
    block_kind = table["block_kind"]
    block_label = table["block_label"]
    forward_speed = table["forward_speed"]
    retinal_slip = table["retinal_slip"]
    turn_signal = table["turn_signal"]
    yaw_rate = table["yaw_rate"]

    valid_block_ids = [idx for idx in np.unique(block_index) if idx >= 0]
    if not valid_block_ids:
        return {"block_count": 0}

    blocks: list[dict[str, Any]] = []
    for idx in valid_block_ids:
        mask = block_index == idx
        if not np.any(mask):
            continue
        blocks.append(
            {
                "index": int(idx),
                "kind": str(block_kind[mask][0]),
                "label": str(block_label[mask][0]),
                "mean_forward_speed": _mean_or_zero(forward_speed[mask]),
                "mean_abs_turn_signal": _mean_or_zero(np.abs(turn_signal[mask])),
                "mean_abs_yaw_rate": _mean_or_zero(np.abs(yaw_rate[mask])),
                "mean_retinal_slip": _mean_or_zero(retinal_slip[mask]),
                "mean_abs_retinal_slip": _mean_or_zero(np.abs(retinal_slip[mask])),
            }
        )

    stationary_blocks = [block for block in blocks if block["kind"] == "stationary"]
    stimulus_blocks = [block for block in blocks if block["kind"] != "stationary"]
    low_turn_threshold = float(np.median([block["mean_abs_turn_signal"] for block in stimulus_blocks])) if stimulus_blocks else 0.0

    per_kind: dict[str, dict[str, list[float]]] = {}
    for block in stimulus_blocks:
        baseline = next(
            (candidate for candidate in reversed(blocks[: block["index"]]) if candidate["kind"] == "stationary"),
            None,
        )
        if baseline is None:
            continue
        kind = str(block["kind"])
        bucket = per_kind.setdefault(
            kind,
            {
                "delta_forward_speed": [],
                "delta_forward_speed_low_turn": [],
                "delta_forward_speed_high_turn": [],
                "delta_abs_turn_signal": [],
                "delta_abs_yaw_rate": [],
                "retinal_slip_abs": [],
            },
        )
        delta_forward = float(block["mean_forward_speed"] - baseline["mean_forward_speed"])
        delta_turn = float(block["mean_abs_turn_signal"] - baseline["mean_abs_turn_signal"])
        delta_yaw = float(block["mean_abs_yaw_rate"] - baseline["mean_abs_yaw_rate"])
        bucket["delta_forward_speed"].append(delta_forward)
        bucket["delta_abs_turn_signal"].append(delta_turn)
        bucket["delta_abs_yaw_rate"].append(delta_yaw)
        bucket["retinal_slip_abs"].append(float(block["mean_abs_retinal_slip"]))
        if block["mean_abs_turn_signal"] <= low_turn_threshold:
            bucket["delta_forward_speed_low_turn"].append(delta_forward)
        else:
            bucket["delta_forward_speed_high_turn"].append(delta_forward)

    summary: dict[str, Any] = {
        "block_count": int(len(blocks)),
        "stationary_block_count": int(len(stationary_blocks)),
        "stimulus_block_count": int(len(stimulus_blocks)),
        "low_turn_threshold": low_turn_threshold,
    }
    for kind, bucket in per_kind.items():
        prefix = str(kind)
        summary[f"{prefix}_block_count"] = int(len(bucket["delta_forward_speed"]))
        summary[f"{prefix}_delta_forward_speed_mean"] = _mean_or_zero(np.asarray(bucket["delta_forward_speed"], dtype=np.float32))
        summary[f"{prefix}_delta_forward_speed_low_turn_mean"] = _mean_or_zero(np.asarray(bucket["delta_forward_speed_low_turn"], dtype=np.float32))
        summary[f"{prefix}_delta_forward_speed_high_turn_mean"] = _mean_or_zero(np.asarray(bucket["delta_forward_speed_high_turn"], dtype=np.float32))
        summary[f"{prefix}_delta_abs_turn_signal_mean"] = _mean_or_zero(np.asarray(bucket["delta_abs_turn_signal"], dtype=np.float32))
        summary[f"{prefix}_delta_abs_yaw_rate_mean"] = _mean_or_zero(np.asarray(bucket["delta_abs_yaw_rate"], dtype=np.float32))
        summary[f"{prefix}_retinal_slip_abs_mean_mm_s"] = _mean_or_zero(np.asarray(bucket["retinal_slip_abs"], dtype=np.float32))
    return summary


def compute_visual_speed_control_metrics(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    table = _extract_visual_speed_table(records)
    if table is None:
        return {"enabled": False}

    sim_time = table["sim_time"]
    forward_speed = table["forward_speed"]
    scene_speed = table["scene_speed"]
    effective_visual_speed = table["effective_visual_speed"]
    retinal_slip = table["retinal_slip"]
    gain = table["gain"]
    corridor_half_width = table["corridor_half_width"]
    fly_x = table["fly_x_mm"]
    track_x = table["track_x_mm"]
    stimulus_active = table["stimulus_active"]
    mode_values = [value for value in table["mode"] if value]
    mode = str(mode_values[0]) if mode_values else ""

    pre_mask = ~stimulus_active
    stim_mask = stimulus_active
    if mode == "hourglass":
        min_width = float(np.min(corridor_half_width)) if corridor_half_width.size else 0.0
        max_width = float(np.max(corridor_half_width)) if corridor_half_width.size else 0.0
        threshold = min_width + 0.15 * max(max_width - min_width, 1e-6)
        neck_mask = corridor_half_width <= threshold
        pre_mask = track_x < 0.0
        stim_mask = neck_mask
        post_mask = track_x > 0.0
    else:
        post_mask = sim_time > (float(np.max(sim_time[stim_mask])) if np.any(stim_mask) else float(np.max(sim_time) if sim_time.size else 0.0))

    pre_speed = forward_speed[pre_mask]
    stim_speed = forward_speed[stim_mask]
    post_speed = forward_speed[post_mask]
    pre_mean = _mean_or_zero(pre_speed)
    stim_mean = _mean_or_zero(stim_speed)
    post_mean = _mean_or_zero(post_speed)

    metrics: dict[str, Any] = {
        "enabled": True,
        "mode": mode,
        "sample_count": int(sim_time.size),
        "pre_mean_forward_speed": pre_mean,
        "stimulus_mean_forward_speed": stim_mean,
        "post_mean_forward_speed": post_mean,
        "speed_fold_change": float(stim_mean / max(pre_mean, 1e-6)),
        "scene_speed_mean_mm_s": _mean_or_zero(scene_speed[stim_mask]) if np.any(stim_mask) else _mean_or_zero(scene_speed),
        "scene_speed_abs_mean_mm_s": _mean_or_zero(np.abs(scene_speed[stim_mask])) if np.any(stim_mask) else _mean_or_zero(np.abs(scene_speed)),
        "effective_visual_speed_mean_mm_s": _mean_or_zero(effective_visual_speed[stim_mask]) if np.any(stim_mask) else _mean_or_zero(effective_visual_speed),
        "effective_visual_speed_abs_mean_mm_s": _mean_or_zero(np.abs(effective_visual_speed[stim_mask])) if np.any(stim_mask) else _mean_or_zero(np.abs(effective_visual_speed)),
        "retinal_slip_mean_mm_s": _mean_or_zero(retinal_slip[stim_mask]) if np.any(stim_mask) else _mean_or_zero(retinal_slip),
        "retinal_slip_abs_mean_mm_s": _mean_or_zero(np.abs(retinal_slip[stim_mask])) if np.any(stim_mask) else _mean_or_zero(np.abs(retinal_slip)),
        "speed_vs_effective_visual_corr": pearson_correlation(forward_speed, np.abs(effective_visual_speed)),
        "speed_vs_retinal_slip_corr": pearson_correlation(forward_speed, np.abs(retinal_slip)),
        "speed_vs_scene_speed_corr": pearson_correlation(forward_speed, np.abs(scene_speed)),
    }
    if mode == "interleaved_blocks":
        metrics.update(_summarize_interleaved_blocks(table))
    if mode == "closed_loop_gain":
        metrics.update(
            {
                "baseline_gain_mean": _mean_or_zero(gain[pre_mask]),
                "stimulus_gain_mean": _mean_or_zero(gain[stim_mask]),
                "gain_change": float(_mean_or_zero(gain[stim_mask]) - _mean_or_zero(gain[pre_mask])),
            }
        )
    if mode == "hourglass":
        neck_mask = corridor_half_width <= (float(np.min(corridor_half_width)) + 0.15 * max(float(np.max(corridor_half_width) - np.min(corridor_half_width)), 1e-6))
        metrics.update(
            {
                "open_section_mean_speed": _mean_or_zero(forward_speed[~neck_mask]),
                "neck_mean_speed": _mean_or_zero(forward_speed[neck_mask]),
                "hourglass_slowing_fraction": float(
                    (_mean_or_zero(forward_speed[~neck_mask]) - _mean_or_zero(forward_speed[neck_mask]))
                    / max(_mean_or_zero(forward_speed[~neck_mask]), 1e-6)
                ),
                "speed_vs_half_width_corr": pearson_correlation(forward_speed, corridor_half_width),
            }
        )
    return metrics


def flatten_visual_speed_control_metrics(metrics: Mapping[str, Any]) -> dict[str, float | str | bool | None]:
    flat: dict[str, float | str | bool | None] = {}
    for key, value in metrics.items():
        flat[f"visual_speed_control_{key}"] = value
    return flat

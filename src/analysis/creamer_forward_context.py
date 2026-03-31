from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from math import copysign
from pathlib import Path
from typing import Any


BLOCK_PAIRS: tuple[tuple[str, str], ...] = (
    ("baseline_a", "motion_ftb_a"),
    ("baseline_d", "motion_ftb_b"),
)

REVERSE_BLOCK_PAIRS: tuple[tuple[str, str], ...] = (
    ("baseline_c", "motion_btf"),
)

FLICKER_PAIR: tuple[str, str] = ("baseline_b", "flicker")


@dataclass(frozen=True)
class CreamerForwardContextRun:
    path: str
    block_means: dict[str, dict[str, float]]


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def summarize_monitor_bilateral_block_means(path: str | Path) -> CreamerForwardContextRun:
    path = Path(path)
    per_block: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            visual_speed_state = (row.get("body_metadata") or {}).get("visual_speed_state") or {}
            block_label = str(visual_speed_state.get("block_label", "unknown"))
            motor_readout = row.get("motor_readout") or {}
            for key, raw_value in motor_readout.items():
                if not (key.startswith("monitor_") and key.endswith("_bilateral_hz")):
                    continue
                value = _safe_float(raw_value)
                if value is not None:
                    per_block[block_label][key].append(value)

    block_means: dict[str, dict[str, float]] = {}
    for block_label, monitor_values in per_block.items():
        block_means[block_label] = {}
        for key, values in monitor_values.items():
            if values:
                block_means[block_label][key] = float(sum(values) / len(values))
    return CreamerForwardContextRun(path=str(path), block_means=block_means)


def _delta(block_means: dict[str, dict[str, float]], start: str, end: str, key: str) -> float | None:
    start_value = block_means.get(start, {}).get(key)
    end_value = block_means.get(end, {}).get(key)
    if start_value is None or end_value is None:
        return None
    return float(end_value - start_value)


def compare_forward_context_candidates(
    baseline: CreamerForwardContextRun,
    ablated: CreamerForwardContextRun,
) -> list[dict[str, float | str]]:
    keys = sorted(
        set().union(
            *(block.keys() for block in baseline.block_means.values()),
            *(block.keys() for block in ablated.block_means.values()),
        )
    )
    rows: list[dict[str, float | str]] = []
    for key in keys:
        baseline_ftb_deltas = [
            _delta(baseline.block_means, start, end, key)
            for start, end in BLOCK_PAIRS
        ]
        baseline_btf_deltas = [
            _delta(baseline.block_means, start, end, key)
            for start, end in REVERSE_BLOCK_PAIRS
        ]
        ablated_ftb_deltas = [
            _delta(ablated.block_means, start, end, key)
            for start, end in BLOCK_PAIRS
        ]
        ablated_btf_deltas = [
            _delta(ablated.block_means, start, end, key)
            for start, end in REVERSE_BLOCK_PAIRS
        ]
        baseline_ftb_values = [value for value in baseline_ftb_deltas if value is not None]
        baseline_btf_values = [value for value in baseline_btf_deltas if value is not None]
        ablated_ftb_values = [value for value in ablated_ftb_deltas if value is not None]
        ablated_btf_values = [value for value in ablated_btf_deltas if value is not None]
        baseline_ftb_mean = (
            float(sum(baseline_ftb_values) / len(baseline_ftb_values))
            if baseline_ftb_values
            else 0.0
        )
        baseline_btf_mean = (
            float(sum(baseline_btf_values) / len(baseline_btf_values))
            if baseline_btf_values
            else 0.0
        )
        ablated_ftb_mean = (
            float(sum(ablated_ftb_values) / len(ablated_ftb_values))
            if ablated_ftb_values
            else 0.0
        )
        ablated_btf_mean = (
            float(sum(ablated_btf_values) / len(ablated_btf_values))
            if ablated_btf_values
            else 0.0
        )
        baseline_flicker_delta = _delta(baseline.block_means, FLICKER_PAIR[0], FLICKER_PAIR[1], key) or 0.0
        ablated_flicker_delta = _delta(ablated.block_means, FLICKER_PAIR[0], FLICKER_PAIR[1], key) or 0.0
        motion_ftb_component = abs(float(baseline_ftb_mean))
        motion_btf_component = abs(float(baseline_btf_mean))
        motion_component = motion_ftb_component + motion_btf_component
        direction_balance = min(motion_ftb_component, motion_btf_component)
        flicker_penalty = abs(float(baseline_flicker_delta))
        ablated_motion_component = abs(float(ablated_ftb_mean)) + abs(float(ablated_btf_mean))
        ablation_component = max(0.0, motion_component - ablated_motion_component)
        signed_motion_values = [
            value
            for value in (baseline_ftb_mean, baseline_btf_mean)
            if abs(float(value)) > 1e-9
        ]
        if signed_motion_values:
            signed_motion_mean = float(sum(signed_motion_values) / len(signed_motion_values))
        else:
            signed_motion_mean = 0.0
        sign_conflict = (
            abs(float(baseline_ftb_mean)) > 1e-9
            and abs(float(baseline_btf_mean)) > 1e-9
            and float(baseline_ftb_mean) * float(baseline_btf_mean) < 0.0
        )
        consistency_factor = 0.25 if sign_conflict else 1.0
        motion_specificity = max(0.0, motion_component - flicker_penalty)
        score = float(
            consistency_factor
            * (motion_component + direction_balance)
            * (1.0 + motion_specificity)
            * (1.0 + ablation_component)
        )
        signed_ablation_component = (
            float(copysign(ablation_component, signed_motion_mean))
            if abs(signed_motion_mean) > 1e-9
            else 0.0
        )
        rows.append(
            {
                "monitor_key": key,
                "cell_type": key.removeprefix("monitor_").removesuffix("_bilateral_hz"),
                "baseline_ftb_a_delta_hz": float(baseline_ftb_deltas[0] or 0.0),
                "baseline_ftb_b_delta_hz": float(baseline_ftb_deltas[1] or 0.0),
                "baseline_ftb_mean_delta_hz": baseline_ftb_mean,
                "baseline_btf_delta_hz": float(baseline_btf_deltas[0] or 0.0),
                "baseline_btf_mean_delta_hz": baseline_btf_mean,
                "baseline_flicker_delta_hz": float(baseline_flicker_delta),
                "ablated_ftb_a_delta_hz": float(ablated_ftb_deltas[0] or 0.0),
                "ablated_ftb_b_delta_hz": float(ablated_ftb_deltas[1] or 0.0),
                "ablated_ftb_mean_delta_hz": ablated_ftb_mean,
                "ablated_btf_delta_hz": float(ablated_btf_deltas[0] or 0.0),
                "ablated_btf_mean_delta_hz": ablated_btf_mean,
                "ablated_flicker_delta_hz": float(ablated_flicker_delta),
                "motion_component_hz": motion_component,
                "motion_ftb_component_hz": motion_ftb_component,
                "motion_btf_component_hz": motion_btf_component,
                "direction_balance_hz": direction_balance,
                "motion_specificity_hz": motion_specificity,
                "signed_motion_mean_delta_hz": signed_motion_mean,
                "signed_ablation_component_hz": signed_ablation_component,
                "direction_sign_consistency": consistency_factor,
                "specificity_component_hz": motion_specificity,
                "ablation_component_hz": ablation_component,
                "candidate_score": score,
            }
        )
    rows.sort(
        key=lambda row: (
            float(row["candidate_score"]),
            float(row["motion_component_hz"]),
            float(row["direction_balance_hz"]),
        ),
        reverse=True,
    )
    return rows

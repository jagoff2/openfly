from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


BLOCK_ORDER: tuple[str, ...] = (
    "baseline_a",
    "motion_ftb_a",
    "baseline_b",
    "flicker",
    "baseline_c",
    "motion_btf",
    "baseline_d",
    "motion_ftb_b",
)


@dataclass(frozen=True)
class CreamerRunBlockMeans:
    label: str
    path: str
    block_means: dict[str, dict[str, float]]


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def summarize_creamer_run(path: str | Path) -> CreamerRunBlockMeans:
    path = Path(path)
    per_block: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            visual_speed_state = (row.get("body_metadata") or {}).get("visual_speed_state") or {}
            block_label = str(visual_speed_state.get("block_label", "unknown"))
            motor_signals = row.get("motor_signals") or {}
            motor_readout = row.get("motor_readout") or {}
            visual_splice = row.get("visual_splice") or {}

            scalar_fields = {
                "forward_speed_mm_s": row.get("forward_speed"),
                "retinal_slip_mm_s": visual_speed_state.get("retinal_slip_mm_s"),
                "effective_visual_speed_mm_s": visual_speed_state.get("effective_visual_speed_mm_s"),
                "forward_signal": motor_signals.get("forward_signal"),
                "turn_signal": motor_signals.get("turn_signal"),
                "reverse_signal": motor_signals.get("reverse_signal"),
                "dn_forward_signal": motor_readout.get("dn_forward_signal"),
                "population_forward_signal": motor_readout.get("population_forward_signal"),
                "forward_state": motor_readout.get("forward_state"),
                "dn_turn_signal": motor_readout.get("dn_turn_signal"),
                "population_turn_signal": motor_readout.get("population_turn_signal"),
                "turn_voltage_signal": motor_readout.get("turn_voltage_signal"),
                "turn_state": motor_readout.get("turn_state"),
                "splice_nonzero_root_count": visual_splice.get("nonzero_root_count"),
                "splice_max_abs_current": visual_splice.get("max_abs_current"),
            }
            for key, raw_value in scalar_fields.items():
                value = _safe_float(raw_value)
                if value is not None:
                    per_block[block_label][key].append(value)

    block_means: dict[str, dict[str, float]] = {}
    for block_label, fields in per_block.items():
        block_means[block_label] = {}
        for key, values in fields.items():
            if values:
                block_means[block_label][key] = float(sum(values) / len(values))
    return CreamerRunBlockMeans(label=path.parent.parent.name, path=str(path), block_means=block_means)


def _delta(block_means: Mapping[str, Mapping[str, float]], start: str, end: str, key: str) -> float | None:
    start_value = (block_means.get(start) or {}).get(key)
    end_value = (block_means.get(end) or {}).get(key)
    if start_value is None or end_value is None:
        return None
    return float(end_value - start_value)


def compare_creamer_runs(
    baseline: CreamerRunBlockMeans,
    ablated: CreamerRunBlockMeans,
) -> dict[str, Any]:
    metrics = (
        "forward_speed_mm_s",
        "forward_signal",
        "dn_forward_signal",
        "population_forward_signal",
        "forward_state",
        "turn_signal",
        "dn_turn_signal",
        "population_turn_signal",
        "turn_voltage_signal",
        "turn_state",
        "splice_nonzero_root_count",
        "splice_max_abs_current",
    )
    delta_table: dict[str, dict[str, float | None]] = {}
    for metric in metrics:
        delta_table[metric] = {
            "baseline_motion_ftb_a_minus_baseline_a": _delta(baseline.block_means, "baseline_a", "motion_ftb_a", metric),
            "ablated_motion_ftb_a_minus_baseline_a": _delta(ablated.block_means, "baseline_a", "motion_ftb_a", metric),
            "baseline_motion_ftb_b_minus_baseline_d": _delta(baseline.block_means, "baseline_d", "motion_ftb_b", metric),
            "ablated_motion_ftb_b_minus_baseline_d": _delta(ablated.block_means, "baseline_d", "motion_ftb_b", metric),
        }

    speed_delta_a = delta_table["forward_speed_mm_s"]["baseline_motion_ftb_a_minus_baseline_a"]
    speed_delta_a_abl = delta_table["forward_speed_mm_s"]["ablated_motion_ftb_a_minus_baseline_a"]
    forward_signal_delta_a = delta_table["forward_signal"]["baseline_motion_ftb_a_minus_baseline_a"]
    forward_signal_delta_a_abl = delta_table["forward_signal"]["ablated_motion_ftb_a_minus_baseline_a"]
    turn_voltage_delta_a = delta_table["turn_voltage_signal"]["baseline_motion_ftb_a_minus_baseline_a"]
    turn_voltage_delta_a_abl = delta_table["turn_voltage_signal"]["ablated_motion_ftb_a_minus_baseline_a"]

    diagnosis = {
        "speed_delta_survives_ablation_first_motion_block": bool(
            speed_delta_a is not None and speed_delta_a_abl is not None and abs(speed_delta_a - speed_delta_a_abl) <= 1.0
        ),
        "forward_signal_delta_survives_ablation_first_motion_block": bool(
            forward_signal_delta_a is not None
            and forward_signal_delta_a_abl is not None
            and abs(forward_signal_delta_a - forward_signal_delta_a_abl) <= 0.02
        ),
        "turn_voltage_delta_survives_ablation_first_motion_block": bool(
            turn_voltage_delta_a is not None
            and turn_voltage_delta_a_abl is not None
            and abs(turn_voltage_delta_a - turn_voltage_delta_a_abl) <= 0.02
        ),
        "front_to_back_speed_delta_is_decoupled_from_forward_signal": bool(
            speed_delta_a is not None
            and speed_delta_a_abl is not None
            and forward_signal_delta_a is not None
            and forward_signal_delta_a_abl is not None
            and abs(speed_delta_a - speed_delta_a_abl) <= 1.0
            and abs(forward_signal_delta_a - forward_signal_delta_a_abl) > 0.05
        ),
        "motion_pathway_primarily_modulates_turn_structure_not_speed": bool(
            speed_delta_a is not None
            and speed_delta_a_abl is not None
            and abs(speed_delta_a - speed_delta_a_abl) <= 1.0
            and turn_voltage_delta_a is not None
            and turn_voltage_delta_a_abl is not None
            and abs(turn_voltage_delta_a - turn_voltage_delta_a_abl) > 0.05
        ),
    }

    return {
        "baseline": {
            "label": baseline.label,
            "path": baseline.path,
            "block_means": {block: baseline.block_means.get(block, {}) for block in BLOCK_ORDER if block in baseline.block_means},
        },
        "ablated": {
            "label": ablated.label,
            "path": ablated.path,
            "block_means": {block: ablated.block_means.get(block, {}) for block in BLOCK_ORDER if block in ablated.block_means},
        },
        "delta_table": delta_table,
        "diagnosis": diagnosis,
    }

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import flyvis

import run_splice_probe as splice_probe
from brain.flywire_annotations import build_spatial_overlap_groups, find_exact_cell_type_overlap, load_flywire_annotation_table
from brain.public_ids import MOTOR_READOUT_IDS
from brain.pytorch_backend import WholeBrainTorchBackend
from vision.lateralized_probe import build_body_side_stimuli, compute_retina_geometry


def _mean_metric(values_by_id: dict[int, float], root_ids: tuple[int, ...]) -> float:
    values = [float(values_by_id.get(int(root_id), 0.0)) for root_id in root_ids]
    return float(np.mean(values)) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep pulse schedules to explain longer-window splice drift.")
    parser.add_argument("--vision-network-dir", default=None)
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--brain-connectivity-path", default="external/fly-brain/data/2025_Connectivity_783.parquet")
    parser.add_argument("--brain-device", default="cpu")
    parser.add_argument("--vision-refresh-rate", type=float, default=500.0)
    parser.add_argument("--vision-steps", type=int, default=30)
    parser.add_argument("--vision-tail-steps", type=int, default=8)
    parser.add_argument("--spatial-bins", type=int, default=4)
    parser.add_argument("--min-roots-per-bin", type=int, default=20)
    parser.add_argument("--baseline-value", type=float, default=1.0)
    parser.add_argument("--patch-value", type=float, default=0.0)
    parser.add_argument("--side-fraction", type=float, default=0.35)
    parser.add_argument("--window-ms-values", nargs="+", type=float, default=[100.0, 200.0, 300.0, 500.0])
    parser.add_argument("--pulse-ms-values", nargs="+", default=["hold", "25", "50", "100"])
    parser.add_argument("--max-abs-current-values", nargs="+", type=float, default=[120.0, 80.0])
    parser.add_argument("--csv-output", default="outputs/metrics/splice_drift_sweep.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_drift_sweep.json")
    args = parser.parse_args()

    flyvis.device = torch.device("cpu")

    retina, retina_mapper, network = splice_probe._prepare_visual_network(args.vision_network_dir)
    geometry = compute_retina_geometry(retina.ommatidia_id_map)
    stimuli = build_body_side_stimuli(
        geometry,
        baseline_value=args.baseline_value,
        patch_value=args.patch_value,
        side_fraction=args.side_fraction,
    )
    condition_names = ("baseline_gray", "body_left_dark", "body_center_dark", "body_right_dark")
    condition_tails = {
        name: splice_probe._run_condition(
            network,
            retina_mapper,
            stimuli[name],
            baseline_gray=stimuli["baseline_gray"],
            vision_refresh_rate=args.vision_refresh_rate,
            steps=args.vision_steps,
            tail_steps=args.vision_tail_steps,
        )
        for name in condition_names
    }
    layer_indices = splice_probe._build_layer_indices(network)
    annotation_table = load_flywire_annotation_table(args.annotation_path)
    overlap_types = find_exact_cell_type_overlap(layer_indices.keys(), annotation_table)
    overlap_groups = build_spatial_overlap_groups(
        annotation_table,
        cell_types=overlap_types,
        num_bins=args.spatial_bins,
        min_roots_per_bin=args.min_roots_per_bin,
    )
    group_keys = {(group.cell_type, group.side, int(group.bin_index)): group for group in overlap_groups}
    complete_types = sorted({group.cell_type for group in overlap_groups})
    flyvis_bins = splice_probe._build_flyvis_u_bins(network, layer_indices, complete_types, int(args.spatial_bins))
    teacher_means_by_condition = {
        name: splice_probe._teacher_group_means(condition_tails[name], flyvis_bins, complete_types, int(args.spatial_bins))
        for name in condition_names
    }
    baseline_teacher = teacher_means_by_condition["baseline_gray"]
    teacher_signed_delta_by_condition = {
        name: {
            key: float(value - baseline_teacher.get(key, 0.0))
            for key, value in means.items()
        }
        for name, means in teacher_means_by_condition.items()
    }
    max_target_abs = max(
        (abs(value) for mapping in teacher_signed_delta_by_condition.values() for value in mapping.values()),
        default=0.0,
    )
    if max_target_abs <= 0.0:
        raise RuntimeError("No nonzero teacher deltas available for drift sweep")

    backend = WholeBrainTorchBackend(
        completeness_path=args.brain_completeness_path,
        connectivity_path=args.brain_connectivity_path,
        device=args.brain_device,
    )
    monitored_ids = sorted(
        {
            neuron_id
            for neuron_ids in MOTOR_READOUT_IDS.values()
            for neuron_id in neuron_ids
        }
    )
    backend.set_monitored_ids(monitored_ids)

    pulse_values: list[float | None] = []
    for raw in args.pulse_ms_values:
        if str(raw).lower() == "hold":
            pulse_values.append(None)
        else:
            pulse_values.append(float(raw))

    rows: list[dict[str, object]] = []
    for max_abs_current in [float(value) for value in args.max_abs_current_values]:
        value_scale = max_abs_current / max_target_abs
        for window_ms in [float(value) for value in args.window_ms_values]:
            num_steps = max(1, int(round(window_ms / backend.dt_ms)))
            for pulse_ms in pulse_values:
                pulse_steps = None if pulse_ms is None else max(1, int(round(float(pulse_ms) / backend.dt_ms)))
                motor_rates_by_condition: dict[str, dict[str, float]] = {}
                for condition_name in condition_names:
                    direct_current_by_id: dict[int, float] = {}
                    for key, target_value in teacher_signed_delta_by_condition[condition_name].items():
                        group = group_keys.get(key)
                        if group is None:
                            continue
                        scaled_value = float(target_value * value_scale)
                        if np.isclose(scaled_value, 0.0):
                            continue
                        for root_id in group.root_ids:
                            direct_current_by_id[int(root_id)] = scaled_value
                    backend.reset(seed=0)
                    if pulse_steps is None or pulse_steps >= num_steps:
                        student_rates, _, _ = backend.step_with_state(
                            {},
                            num_steps=num_steps,
                            direct_current_by_id=direct_current_by_id,
                        )
                    else:
                        backend.step_with_state(
                            {},
                            num_steps=pulse_steps,
                            direct_current_by_id=direct_current_by_id,
                        )
                        student_rates, _, _ = backend.step_with_state(
                            {},
                            num_steps=num_steps - pulse_steps,
                            direct_current_by_id=None,
                        )
                    motor_rates_by_condition[condition_name] = splice_probe._aggregate_motor_rates(student_rates)

                left_bias = float(motor_rates_by_condition["body_left_dark"]["turn_right"] - motor_rates_by_condition["body_left_dark"]["turn_left"])
                right_bias = float(motor_rates_by_condition["body_right_dark"]["turn_right"] - motor_rates_by_condition["body_right_dark"]["turn_left"])
                center_bias = float(motor_rates_by_condition["body_center_dark"]["turn_right"] - motor_rates_by_condition["body_center_dark"]["turn_left"])
                sign_match = left_bias < 0.0 and right_bias > 0.0
                row = {
                    "max_abs_current": float(max_abs_current),
                    "window_ms": float(window_ms),
                    "pulse_ms": None if pulse_ms is None else float(pulse_ms),
                    "pulse_mode": "hold" if pulse_ms is None else "pulse_then_free",
                    "left_turn_bias": left_bias,
                    "right_turn_bias": right_bias,
                    "center_turn_bias": center_bias,
                    "sign_match": bool(sign_match),
                    "sign_margin": float(min(-left_bias, right_bias)) if sign_match else float(-abs(left_bias) - abs(right_bias)),
                    "forward_left_left_dark": float(motor_rates_by_condition["body_left_dark"]["forward_left"]),
                    "forward_right_left_dark": float(motor_rates_by_condition["body_left_dark"]["forward_right"]),
                    "forward_left_right_dark": float(motor_rates_by_condition["body_right_dark"]["forward_left"]),
                    "forward_right_right_dark": float(motor_rates_by_condition["body_right_dark"]["forward_right"]),
                }
                rows.append(row)

    rows.sort(
        key=lambda row: (
            1 if row["sign_match"] else 0,
            float(row["sign_margin"]),
            -float(row["window_ms"]),
        ),
        reverse=True,
    )
    best_rows = [row for row in rows if row["sign_match"]]
    summary = {
        "best_sign_preserving_rows": best_rows[:10],
        "rows": rows,
        "selection_rule": [
            "Prefer schedules that preserve the correct downstream sign: left-dark negative and right-dark positive turn bias.",
            "Among sign-preserving schedules, prefer larger positive sign margins at longer windows.",
            "Use pulse schedules to test whether the 500 ms drift is caused by sustained external drive rather than absence of propagation.",
        ],
    }

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "max_abs_current",
                "window_ms",
                "pulse_ms",
                "pulse_mode",
                "left_turn_bias",
                "right_turn_bias",
                "center_turn_bias",
                "sign_match",
                "sign_margin",
                "forward_left_left_dark",
                "forward_right_left_dark",
                "forward_left_right_dark",
                "forward_right_right_dark",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

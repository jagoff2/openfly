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
from brain.flywire_annotations import build_spatial_grid_overlap_groups, find_exact_cell_type_overlap, load_flywire_annotation_table
from brain.public_ids import MOTOR_READOUT_IDS
from brain.pytorch_backend import WholeBrainTorchBackend
from vision.lateralized_probe import build_body_side_stimuli, compute_retina_geometry


def _mean_metric(values_by_id: dict[int, float], root_ids: tuple[int, ...]) -> float:
    values = [float(values_by_id.get(int(root_id), 0.0)) for root_id in root_ids]
    return float(np.mean(values)) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Search UV-grid orientation transforms for the body-free splice.")
    parser.add_argument("--vision-network-dir", default=None)
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--brain-connectivity-path", default="external/fly-brain/data/2025_Connectivity_783.parquet")
    parser.add_argument("--brain-device", default="cpu")
    parser.add_argument("--vision-refresh-rate", type=float, default=500.0)
    parser.add_argument("--vision-steps", type=int, default=30)
    parser.add_argument("--vision-tail-steps", type=int, default=8)
    parser.add_argument("--brain-sim-ms", type=float, default=100.0)
    parser.add_argument("--max-abs-current", type=float, default=120.0)
    parser.add_argument("--spatial-u-bins", type=int, default=2)
    parser.add_argument("--spatial-v-bins", type=int, default=2)
    parser.add_argument("--min-roots-per-bin", type=int, default=20)
    parser.add_argument("--baseline-value", type=float, default=1.0)
    parser.add_argument("--patch-value", type=float, default=0.0)
    parser.add_argument("--side-fraction", type=float, default=0.35)
    parser.add_argument("--csv-output", default="outputs/metrics/splice_uvgrid_orientation_search.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_uvgrid_orientation_search.json")
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
    flyvis_cell_types = sorted(set(overlap_types))
    flyvis_bins = splice_probe._build_flyvis_uv_grid_bins(
        network,
        layer_indices,
        flyvis_cell_types,
        int(args.spatial_u_bins),
        int(args.spatial_v_bins),
    )
    flyvis_num_bins = int(args.spatial_u_bins) * int(args.spatial_v_bins)
    teacher_means_by_condition = {
        name: splice_probe._teacher_group_means(condition_tails[name], flyvis_bins, flyvis_cell_types, flyvis_num_bins)
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
        raise RuntimeError("No nonzero teacher deltas available for UV-grid search")
    value_scale = float(args.max_abs_current) / max_target_abs

    backend = WholeBrainTorchBackend(
        completeness_path=args.brain_completeness_path,
        connectivity_path=args.brain_connectivity_path,
        device=args.brain_device,
    )
    num_steps = max(1, int(round(float(args.brain_sim_ms) / backend.dt_ms)))

    rows: list[dict[str, object]] = []
    best_row: dict[str, object] | None = None
    best_score = float("-inf")
    for swap_uv in (False, True):
        for flip_u in (False, True):
            for flip_v in (False, True):
                for mirror_u_by_side in (False, True):
                    overlap_groups = build_spatial_grid_overlap_groups(
                        annotation_table,
                        cell_types=overlap_types,
                        num_u_bins=args.spatial_u_bins,
                        num_v_bins=args.spatial_v_bins,
                        swap_uv=swap_uv,
                        flip_u=flip_u,
                        flip_v=flip_v,
                        mirror_u_by_side=mirror_u_by_side,
                        min_roots_per_bin=args.min_roots_per_bin,
                    )
                    if not overlap_groups:
                        continue
                    group_keys = {(group.cell_type, group.side, int(group.bin_index)): group for group in overlap_groups}
                    complete_types = sorted({group.cell_type for group in overlap_groups})
                    monitored_ids = sorted(
                        {
                            root_id
                            for group in overlap_groups
                            for root_id in group.root_ids
                        }
                        | {
                            neuron_id
                            for neuron_ids in MOTOR_READOUT_IDS.values()
                            for neuron_id in neuron_ids
                        }
                    )
                    backend.set_monitored_ids(monitored_ids)

                    raw_student_group_rates: dict[str, dict[tuple[str, str, int], float]] = {}
                    raw_student_group_voltage: dict[str, dict[tuple[str, str, int], float]] = {}
                    raw_student_motor_rates: dict[str, dict[str, float]] = {}
                    input_counts: dict[str, int] = {}
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
                        student_rates, student_voltage, _ = backend.step_with_state(
                            {},
                            num_steps=num_steps,
                            direct_current_by_id=direct_current_by_id,
                        )
                        raw_student_group_rates[condition_name] = {
                            key: _mean_metric(student_rates, group.root_ids)
                            for key, group in group_keys.items()
                        }
                        raw_student_group_voltage[condition_name] = {
                            key: _mean_metric(student_voltage, group.root_ids)
                            for key, group in group_keys.items()
                        }
                        raw_student_motor_rates[condition_name] = splice_probe._aggregate_motor_rates(student_rates)
                        input_counts[condition_name] = int(sum(1 for value in direct_current_by_id.values() if not np.isclose(value, 0.0)))

                    baseline_student_voltage = raw_student_group_voltage["baseline_gray"]
                    student_voltage_delta_by_condition = {
                        name: {
                            key: float(value - baseline_student_voltage.get(key, 0.0))
                            for key, value in values.items()
                        }
                        for name, values in raw_student_group_voltage.items()
                    }

                    voltage_group_corrs: list[float] = []
                    voltage_side_corrs: list[float] = []
                    for condition_name in ("body_left_dark", "body_center_dark", "body_right_dark"):
                        teacher_values: list[float] = []
                        student_voltage_values: list[float] = []
                        teacher_side_diffs: list[float] = []
                        student_side_diffs: list[float] = []
                        for cell_type in complete_types:
                            for bin_index in range(flyvis_num_bins):
                                left_key = (cell_type, "left", int(bin_index))
                                right_key = (cell_type, "right", int(bin_index))
                                left_group = group_keys.get(left_key)
                                right_group = group_keys.get(right_key)
                                if left_group is None or right_group is None:
                                    continue
                                left_target = float(teacher_signed_delta_by_condition[condition_name].get(left_key, 0.0))
                                right_target = float(teacher_signed_delta_by_condition[condition_name].get(right_key, 0.0))
                                left_voltage = float(student_voltage_delta_by_condition[condition_name].get(left_key, 0.0))
                                right_voltage = float(student_voltage_delta_by_condition[condition_name].get(right_key, 0.0))
                                teacher_values.extend([left_target, right_target])
                                student_voltage_values.extend([left_voltage, right_voltage])
                                teacher_side_diffs.append(float(right_target - left_target))
                                student_side_diffs.append(float(right_voltage - left_voltage))
                        group_corr = splice_probe._pearson(teacher_values, student_voltage_values)
                        side_corr = splice_probe._pearson(teacher_side_diffs, student_side_diffs)
                        if group_corr is not None:
                            voltage_group_corrs.append(float(group_corr))
                        if side_corr is not None:
                            voltage_side_corrs.append(float(side_corr))

                    left_bias = float(raw_student_motor_rates["body_left_dark"]["turn_right"] - raw_student_motor_rates["body_left_dark"]["turn_left"])
                    right_bias = float(raw_student_motor_rates["body_right_dark"]["turn_right"] - raw_student_motor_rates["body_right_dark"]["turn_left"])
                    sign_match = left_bias < 0.0 and right_bias > 0.0
                    sign_margin = min(-left_bias, right_bias) if sign_match else -abs(left_bias) - abs(right_bias)
                    score = (
                        float(np.mean(voltage_group_corrs)) if voltage_group_corrs else -1.0
                    ) + (
                        float(np.mean(voltage_side_corrs)) if voltage_side_corrs else -1.0
                    ) + (2.0 if sign_match else -2.0) + 0.01 * float(sign_margin)
                    row = {
                        "swap_uv": bool(swap_uv),
                        "flip_u": bool(flip_u),
                        "flip_v": bool(flip_v),
                        "mirror_u_by_side": bool(mirror_u_by_side),
                        "mean_voltage_group_corr": float(np.mean(voltage_group_corrs)) if voltage_group_corrs else None,
                        "mean_voltage_side_corr": float(np.mean(voltage_side_corrs)) if voltage_side_corrs else None,
                        "left_turn_bias": left_bias,
                        "right_turn_bias": right_bias,
                        "sign_match": bool(sign_match),
                        "score": float(score),
                        "num_nonzero_inputs_left": int(input_counts["body_left_dark"]),
                        "num_nonzero_inputs_right": int(input_counts["body_right_dark"]),
                    }
                    rows.append(row)
                    if score > best_score:
                        best_score = score
                        best_row = row

    rows.sort(key=lambda row: float(row["score"]), reverse=True)
    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "swap_uv",
                "flip_u",
                "flip_v",
                "mirror_u_by_side",
                "mean_voltage_group_corr",
                "mean_voltage_side_corr",
                "left_turn_bias",
                "right_turn_bias",
                "sign_match",
                "score",
                "num_nonzero_inputs_left",
                "num_nonzero_inputs_right",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "brain_sim_ms": float(args.brain_sim_ms),
        "max_abs_current": float(args.max_abs_current),
        "spatial_u_bins": int(args.spatial_u_bins),
        "spatial_v_bins": int(args.spatial_v_bins),
        "best_orientation": best_row,
        "rows": rows,
        "selection_rule": [
            "Prefer orientations that preserve the correct downstream sign: left-dark negative and right-dark positive turn bias.",
            "Among sign-correct orientations, maximize mean voltage group and side-difference correlation.",
            "If no orientation is sign-correct, rank by the same boundary metrics but keep that failure explicit.",
        ],
    }
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

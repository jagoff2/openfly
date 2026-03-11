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


def _resolve_base_profile(name: str) -> dict[str, bool]:
    profiles = {
        "identity": {
            "swap_uv": False,
            "flip_u": False,
            "flip_v": False,
            "mirror_u_by_side": False,
        },
        "flipu": {
            "swap_uv": False,
            "flip_u": True,
            "flip_v": False,
            "mirror_u_by_side": False,
        },
        "current_best": {
            "swap_uv": False,
            "flip_u": False,
            "flip_v": True,
            "mirror_u_by_side": True,
        },
    }
    if name not in profiles:
        raise ValueError(f"unknown base profile: {name}")
    return dict(profiles[name])


def _transform_options() -> list[dict[str, bool]]:
    options: list[dict[str, bool]] = []
    seen: set[tuple[bool, bool, bool, bool]] = set()
    for swap_uv in (False, True):
        for flip_u in (False, True):
            for flip_v in (False, True):
                for mirror_u_by_side in (False, True):
                    key = (swap_uv, flip_u, flip_v, mirror_u_by_side)
                    if key in seen:
                        continue
                    seen.add(key)
                    options.append(
                        {
                            "swap_uv": bool(swap_uv),
                            "flip_u": bool(flip_u),
                            "flip_v": bool(flip_v),
                            "mirror_u_by_side": bool(mirror_u_by_side),
                        }
                    )
    return options


def _transform_key(value: dict[str, bool]) -> tuple[bool, bool, bool, bool]:
    return (
        bool(value.get("swap_uv", False)),
        bool(value.get("flip_u", False)),
        bool(value.get("flip_v", False)),
        bool(value.get("mirror_u_by_side", False)),
    )


def _canonical_overrides(
    overrides: dict[str, dict[str, bool]],
    base_transform: dict[str, bool],
) -> tuple[tuple[str, tuple[bool, bool, bool, bool]], ...]:
    base_key = _transform_key(base_transform)
    items: list[tuple[str, tuple[bool, bool, bool, bool]]] = []
    for cell_type, transform in sorted(overrides.items()):
        key = _transform_key(transform)
        if key == base_key:
            continue
        items.append((str(cell_type), key))
    return tuple(items)


def _rank_candidate_cell_types(
    teacher_signed_delta_by_condition: dict[str, dict[tuple[str, str, int], float]],
    *,
    cell_types: list[str],
    num_bins: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for cell_type in cell_types:
        diffs: list[float] = []
        for condition_name in ("body_left_dark", "body_right_dark"):
            for bin_index in range(int(num_bins)):
                left_value = float(teacher_signed_delta_by_condition[condition_name].get((cell_type, "left", int(bin_index)), 0.0))
                right_value = float(teacher_signed_delta_by_condition[condition_name].get((cell_type, "right", int(bin_index)), 0.0))
                diffs.append(abs(right_value - left_value))
        rows.append(
            {
                "cell_type": cell_type,
                "mean_abs_teacher_side_diff": float(np.mean(diffs)) if diffs else 0.0,
                "max_abs_teacher_side_diff": float(max(diffs)) if diffs else 0.0,
            }
        )
    rows.sort(
        key=lambda row: (float(row["mean_abs_teacher_side_diff"]), float(row["max_abs_teacher_side_diff"])),
        reverse=True,
    )
    return rows


def _mean_metric(values_by_id: dict[int, float], root_ids: tuple[int, ...]) -> float:
    values = [float(values_by_id.get(int(root_id), 0.0)) for root_id in root_ids]
    return float(np.mean(values)) if values else 0.0


def _score_summary(summary: dict[str, object]) -> float:
    mean_group_corr = float(summary.get("mean_voltage_group_corr", 0.0))
    mean_side_corr = float(summary.get("mean_voltage_side_corr", 0.0))
    left_bias = float(summary["left_turn_bias"])
    right_bias = float(summary["right_turn_bias"])
    sign_support = max(0.0, -left_bias) + max(0.0, right_bias)
    sign_penalty = max(0.0, left_bias) + max(0.0, -right_bias)
    score = mean_group_corr + 2.0 * mean_side_corr + 0.05 * (sign_support - sign_penalty)
    if bool(summary.get("sign_match", False)):
        score += 5.0 + 0.1 * min(-left_bias, right_bias)
    return float(score)


def _evaluate_configuration(
    *,
    annotation_table,
    overlap_types: list[str],
    teacher_signed_delta_by_condition: dict[str, dict[tuple[str, str, int], float]],
    value_scale: float,
    backend: WholeBrainTorchBackend,
    base_transform: dict[str, bool],
    cell_type_overrides: dict[str, dict[str, bool]],
    num_u_bins: int,
    num_v_bins: int,
    min_roots_per_bin: int,
    num_steps: int,
) -> dict[str, object]:
    overlap_groups = build_spatial_grid_overlap_groups(
        annotation_table,
        cell_types=overlap_types,
        num_u_bins=int(num_u_bins),
        num_v_bins=int(num_v_bins),
        swap_uv=bool(base_transform["swap_uv"]),
        flip_u=bool(base_transform["flip_u"]),
        flip_v=bool(base_transform["flip_v"]),
        mirror_u_by_side=bool(base_transform["mirror_u_by_side"]),
        cell_type_transforms=cell_type_overrides,
        min_roots_per_bin=int(min_roots_per_bin),
    )
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

    raw_student_group_voltage: dict[str, dict[tuple[str, str, int], float]] = {}
    raw_student_motor_rates: dict[str, dict[str, float]] = {}
    input_counts: dict[str, int] = {}
    for condition_name in ("baseline_gray", "body_left_dark", "body_center_dark", "body_right_dark"):
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
    per_condition: dict[str, dict[str, float | None]] = {}
    num_bins = int(num_u_bins) * int(num_v_bins)
    for condition_name in ("body_left_dark", "body_center_dark", "body_right_dark"):
        teacher_values: list[float] = []
        student_voltage_values: list[float] = []
        teacher_side_diffs: list[float] = []
        student_side_diffs: list[float] = []
        for cell_type in complete_types:
            for bin_index in range(num_bins):
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
        per_condition[condition_name] = {
            "voltage_group_corr": group_corr,
            "voltage_side_corr": side_corr,
        }

    left_bias = float(raw_student_motor_rates["body_left_dark"]["turn_right"] - raw_student_motor_rates["body_left_dark"]["turn_left"])
    right_bias = float(raw_student_motor_rates["body_right_dark"]["turn_right"] - raw_student_motor_rates["body_right_dark"]["turn_left"])
    summary = {
        "num_groups": len(overlap_groups),
        "num_complete_cell_types": len(complete_types),
        "mean_voltage_group_corr": float(np.mean(voltage_group_corrs)) if voltage_group_corrs else 0.0,
        "mean_voltage_side_corr": float(np.mean(voltage_side_corrs)) if voltage_side_corrs else 0.0,
        "left_turn_bias": left_bias,
        "right_turn_bias": right_bias,
        "sign_match": bool(left_bias < 0.0 and right_bias > 0.0),
        "conditions": per_condition,
        "num_nonzero_inputs_left": int(input_counts["body_left_dark"]),
        "num_nonzero_inputs_right": int(input_counts["body_right_dark"]),
    }
    summary["score"] = _score_summary(summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Search per-cell-type UV-grid alignment overrides for the grounded body-free splice.")
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
    parser.add_argument("--candidate-count", type=int, default=12)
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--base-profile", choices=("identity", "flipu", "current_best"), default="current_best")
    parser.add_argument("--csv-output", default="outputs/metrics/splice_celltype_alignment_search.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_celltype_alignment_search.json")
    parser.add_argument("--recommended-output", default="outputs/metrics/splice_celltype_alignment_recommended.json")
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
    flyvis_bins = splice_probe._build_flyvis_uv_grid_bins(
        network,
        layer_indices,
        sorted(set(overlap_types)),
        int(args.spatial_u_bins),
        int(args.spatial_v_bins),
    )
    num_bins = int(args.spatial_u_bins) * int(args.spatial_v_bins)
    teacher_means_by_condition = {
        name: splice_probe._teacher_group_means(condition_tails[name], flyvis_bins, sorted(set(overlap_types)), num_bins)
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
        raise RuntimeError("No nonzero teacher deltas available for cell-type alignment search")
    value_scale = float(args.max_abs_current) / max_target_abs

    candidate_ranking = _rank_candidate_cell_types(
        teacher_signed_delta_by_condition,
        cell_types=sorted(set(overlap_types)),
        num_bins=num_bins,
    )
    candidate_rows = candidate_ranking[: max(1, int(args.candidate_count))]
    candidate_cell_types = [str(row["cell_type"]) for row in candidate_rows]

    backend = WholeBrainTorchBackend(
        completeness_path=args.brain_completeness_path,
        connectivity_path=args.brain_connectivity_path,
        device=args.brain_device,
    )
    num_steps = max(1, int(round(float(args.brain_sim_ms) / backend.dt_ms)))
    base_transform = _resolve_base_profile(args.base_profile)
    transform_options = _transform_options()
    evaluation_cache: dict[tuple[tuple[str, tuple[bool, bool, bool, bool]], ...], dict[str, object]] = {}

    def evaluate(overrides: dict[str, dict[str, bool]]) -> dict[str, object]:
        key = _canonical_overrides(overrides, base_transform)
        cached = evaluation_cache.get(key)
        if cached is not None:
            return cached
        summary = _evaluate_configuration(
            annotation_table=annotation_table,
            overlap_types=sorted(set(overlap_types)),
            teacher_signed_delta_by_condition=teacher_signed_delta_by_condition,
            value_scale=value_scale,
            backend=backend,
            base_transform=base_transform,
            cell_type_overrides=overrides,
            num_u_bins=int(args.spatial_u_bins),
            num_v_bins=int(args.spatial_v_bins),
            min_roots_per_bin=int(args.min_roots_per_bin),
            num_steps=num_steps,
        )
        evaluation_cache[key] = summary
        return summary

    current_overrides: dict[str, dict[str, bool]] = {}
    current_summary = evaluate(current_overrides)
    search_rows: list[dict[str, object]] = []

    for pass_index in range(int(args.passes)):
        improved = False
        for candidate_rank, row in enumerate(candidate_rows, start=1):
            cell_type = str(row["cell_type"])
            best_transform = current_overrides.get(cell_type, dict(base_transform))
            best_summary = current_summary
            best_score = float(current_summary["score"])
            for transform in transform_options:
                trial_overrides = dict(current_overrides)
                if _transform_key(transform) == _transform_key(base_transform):
                    trial_overrides.pop(cell_type, None)
                else:
                    trial_overrides[cell_type] = dict(transform)
                trial_summary = evaluate(trial_overrides)
                trial_score = float(trial_summary["score"])
                if trial_score > best_score + 1e-9:
                    best_score = trial_score
                    best_summary = trial_summary
                    best_transform = dict(transform)
            accepted = best_score > float(current_summary["score"]) + 1e-9
            search_rows.append(
                {
                    "pass_index": int(pass_index),
                    "candidate_rank": int(candidate_rank),
                    "cell_type": cell_type,
                    "mean_abs_teacher_side_diff": float(row["mean_abs_teacher_side_diff"]),
                    "accepted": bool(accepted),
                    "previous_score": float(current_summary["score"]),
                    "new_score": float(best_score),
                    "chosen_swap_uv": bool(best_transform["swap_uv"]),
                    "chosen_flip_u": bool(best_transform["flip_u"]),
                    "chosen_flip_v": bool(best_transform["flip_v"]),
                    "chosen_mirror_u_by_side": bool(best_transform["mirror_u_by_side"]),
                    "left_turn_bias": float(best_summary["left_turn_bias"]),
                    "right_turn_bias": float(best_summary["right_turn_bias"]),
                    "sign_match": bool(best_summary["sign_match"]),
                    "mean_voltage_group_corr": float(best_summary["mean_voltage_group_corr"]),
                    "mean_voltage_side_corr": float(best_summary["mean_voltage_side_corr"]),
                }
            )
            if accepted:
                improved = True
                if _transform_key(best_transform) == _transform_key(base_transform):
                    current_overrides.pop(cell_type, None)
                else:
                    current_overrides[cell_type] = dict(best_transform)
                current_summary = best_summary
        if not improved:
            break

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "pass_index",
                "candidate_rank",
                "cell_type",
                "mean_abs_teacher_side_diff",
                "accepted",
                "previous_score",
                "new_score",
                "chosen_swap_uv",
                "chosen_flip_u",
                "chosen_flip_v",
                "chosen_mirror_u_by_side",
                "left_turn_bias",
                "right_turn_bias",
                "sign_match",
                "mean_voltage_group_corr",
                "mean_voltage_side_corr",
            ],
        )
        writer.writeheader()
        writer.writerows(search_rows)

    recommended_payload = {
        "global": base_transform,
        "cell_types": current_overrides,
    }
    recommended_output = Path(args.recommended_output)
    recommended_output.parent.mkdir(parents=True, exist_ok=True)
    recommended_output.write_text(json.dumps(recommended_payload, indent=2), encoding="utf-8")

    summary = {
        "base_profile": args.base_profile,
        "base_transform": base_transform,
        "candidate_count": int(args.candidate_count),
        "passes": int(args.passes),
        "candidate_ranking": candidate_rows,
        "selected_cell_type_overrides": current_overrides,
        "final_summary": current_summary,
        "search_rows": search_rows,
        "recommended_output": str(recommended_output),
        "selection_rule": [
            "Rank candidate cell types by mean absolute teacher left-vs-right boundary asymmetry under the body-left and body-right stimuli.",
            "Starting from the best prior global UV-grid transform, greedily test per-cell-type UV-grid transforms while holding all other cell types fixed.",
            "Keep any per-cell-type change that improves a combined score over boundary agreement and downstream left/right turn-sign correctness.",
        ],
    }
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

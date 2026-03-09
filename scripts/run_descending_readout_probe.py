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

from brain.pytorch_backend import WholeBrainTorchBackend
from vision.lateralized_probe import build_body_side_stimuli, compute_retina_geometry

import run_splice_probe as splice_probe


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe descending-only readout candidates under the calibrated visual splice, body-free.")
    parser.add_argument("--vision-network-dir", default=None)
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--descending-candidates-json", default="outputs/metrics/descending_readout_candidates.json")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--brain-connectivity-path", default="external/fly-brain/data/2025_Connectivity_783.parquet")
    parser.add_argument("--brain-device", default="cpu")
    parser.add_argument("--vision-refresh-rate", type=float, default=500.0)
    parser.add_argument("--vision-steps", type=int, default=40)
    parser.add_argument("--vision-tail-steps", type=int, default=10)
    parser.add_argument("--windows-ms", nargs="+", type=float, default=[100.0, 500.0])
    parser.add_argument("--input-mode", choices=("rate_positive", "current_signed"), default="current_signed")
    parser.add_argument("--max-input-rate-hz", type=float, default=120.0)
    parser.add_argument("--max-abs-current", type=float, default=120.0)
    parser.add_argument("--spatial-mode", choices=("axis1d", "uv_grid"), default="axis1d")
    parser.add_argument("--spatial-bins", type=int, default=4)
    parser.add_argument("--spatial-u-bins", type=int, default=2)
    parser.add_argument("--spatial-v-bins", type=int, default=2)
    parser.add_argument("--spatial-swap-uv", action="store_true")
    parser.add_argument("--spatial-flip-u", action="store_true")
    parser.add_argument("--spatial-flip-v", action="store_true")
    parser.add_argument("--spatial-mirror-u-by-side", action="store_true")
    parser.add_argument("--min-roots-per-side", type=int, default=50)
    parser.add_argument("--min-roots-per-bin", type=int, default=20)
    parser.add_argument("--baseline-value", type=float, default=1.0)
    parser.add_argument("--patch-value", type=float, default=0.0)
    parser.add_argument("--side-fraction", type=float, default=0.35)
    parser.add_argument("--csv-output", default="outputs/metrics/descending_readout_probe.csv")
    parser.add_argument("--pair-output", default="outputs/metrics/descending_readout_probe_pairs.csv")
    parser.add_argument("--json-output", default="outputs/metrics/descending_readout_probe_summary.json")
    args = parser.parse_args()

    flyvis.device = torch.device("cpu")

    candidates = json.loads(Path(args.descending_candidates_json).read_text(encoding="utf-8"))
    pairs = candidates["selected_paired_cell_types"]

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
    annotation_table = splice_probe.load_flywire_annotation_table(args.annotation_path)
    overlap_types = splice_probe.find_exact_cell_type_overlap(layer_indices.keys(), annotation_table)
    if args.spatial_mode == "uv_grid" and (int(args.spatial_u_bins) > 1 or int(args.spatial_v_bins) > 1):
        overlap_groups = splice_probe.build_spatial_grid_overlap_groups(
            annotation_table,
            cell_types=overlap_types,
            num_u_bins=args.spatial_u_bins,
            num_v_bins=args.spatial_v_bins,
            swap_uv=bool(args.spatial_swap_uv),
            flip_u=bool(args.spatial_flip_u),
            flip_v=bool(args.spatial_flip_v),
            mirror_u_by_side=bool(args.spatial_mirror_u_by_side),
            min_roots_per_bin=args.min_roots_per_bin,
        )
        group_keys = {(group.cell_type, group.side, group.bin_index): group for group in overlap_groups}
        flyvis_num_bins = int(args.spatial_u_bins) * int(args.spatial_v_bins)
        flyvis_bins = splice_probe._build_flyvis_uv_grid_bins(
            network,
            layer_indices,
            overlap_types,
            int(args.spatial_u_bins),
            int(args.spatial_v_bins),
        )
    elif int(args.spatial_bins) > 1:
        overlap_groups = splice_probe.build_spatial_overlap_groups(
            annotation_table,
            cell_types=overlap_types,
            num_bins=args.spatial_bins,
            min_roots_per_bin=args.min_roots_per_bin,
        )
        group_keys = {(group.cell_type, group.side, group.bin_index): group for group in overlap_groups}
        flyvis_num_bins = int(args.spatial_bins)
        flyvis_bins = splice_probe._build_flyvis_u_bins(network, layer_indices, overlap_types, flyvis_num_bins)
    else:
        base_groups = splice_probe.build_overlap_groups(
            annotation_table,
            cell_types=overlap_types,
            min_roots_per_side=args.min_roots_per_side,
        )

        class _WrappedGroup:
            def __init__(self, cell_type: str, side: str, root_ids: tuple[int, ...]) -> None:
                self.cell_type = cell_type
                self.side = side
                self.bin_index = 0
                self.root_ids = root_ids

        overlap_groups = [_WrappedGroup(group.cell_type, group.side, group.root_ids) for group in base_groups]
        group_keys = {(group.cell_type, group.side, group.bin_index): group for group in overlap_groups}
        flyvis_num_bins = 1
        flyvis_bins = splice_probe._build_flyvis_u_bins(network, layer_indices, overlap_types, flyvis_num_bins)

    complete_types = sorted({group.cell_type for group in overlap_groups})
    teacher_means_by_condition = {
        name: splice_probe._teacher_group_means(condition_tails[name], flyvis_bins, complete_types, flyvis_num_bins)
        for name in condition_names
    }
    baseline_teacher = teacher_means_by_condition["baseline_gray"]
    teacher_signed_delta_by_condition = {
        name: {key: float(value - baseline_teacher.get(key, 0.0)) for key, value in means.items()}
        for name, means in teacher_means_by_condition.items()
    }
    teacher_target_by_condition = (
        {name: splice_probe._positive_part(delta) for name, delta in teacher_signed_delta_by_condition.items()}
        if args.input_mode == "rate_positive"
        else teacher_signed_delta_by_condition
    )
    max_target_abs = max(
        (abs(value) for mapping in teacher_target_by_condition.values() for value in mapping.values()),
        default=0.0,
    )
    value_scale = 0.0
    if max_target_abs > 0.0:
        value_scale = (
            args.max_input_rate_hz / max_target_abs
            if args.input_mode == "rate_positive"
            else args.max_abs_current / max_target_abs
        )

    backend = WholeBrainTorchBackend(
        completeness_path=args.brain_completeness_path,
        connectivity_path=args.brain_connectivity_path,
        device=args.brain_device,
    )
    monitored_ids = sorted(
        {
            int(root_id)
            for pair in pairs
            for side_key in ("left_root_ids", "right_root_ids")
            for root_id in pair.get(side_key, [])
        }
    )
    backend.set_monitored_ids(monitored_ids)

    pair_rows: list[dict[str, object]] = []
    raw_rows: list[dict[str, object]] = []
    summary: dict[str, object] = {
        "descending_candidates_json": args.descending_candidates_json,
        "spatial_mode": args.spatial_mode,
        "value_scale": value_scale,
        "windows_ms": [float(window_ms) for window_ms in args.windows_ms],
        "pairs": pairs,
        "results": {},
    }

    for window_ms in args.windows_ms:
        num_brain_steps = max(1, int(round(float(window_ms) / backend.dt_ms)))
        window_key = f"{int(window_ms)}ms"
        summary["results"][window_key] = {}
        for condition_name in condition_names:
            direct_input_rates_hz: dict[int, float] = {}
            direct_current_by_id: dict[int, float] = {}
            for key, target_value in teacher_target_by_condition[condition_name].items():
                group = group_keys.get(key)
                if group is None:
                    continue
                scaled_value = float(target_value * value_scale)
                if np.isclose(scaled_value, 0.0):
                    continue
                for root_id in group.root_ids:
                    if args.input_mode == "rate_positive":
                        direct_input_rates_hz[int(root_id)] = scaled_value
                    else:
                        direct_current_by_id[int(root_id)] = scaled_value
            backend.reset(seed=0)
            student_rates, student_voltage, student_conductance = backend.step_with_state(
                {},
                num_steps=num_brain_steps,
                direct_input_rates_hz=direct_input_rates_hz,
                direct_current_by_id=direct_current_by_id,
            )
            condition_summary: dict[str, object] = {"groups": {}}
            for pair in pairs:
                label = str(pair["candidate_label"])
                left_ids = tuple(int(root_id) for root_id in pair["left_root_ids"])
                right_ids = tuple(int(root_id) for root_id in pair["right_root_ids"])
                left_rate = splice_probe._mean_group_rate(student_rates, left_ids)
                right_rate = splice_probe._mean_group_rate(student_rates, right_ids)
                left_voltage = splice_probe._mean_group_metric(student_voltage, left_ids)
                right_voltage = splice_probe._mean_group_metric(student_voltage, right_ids)
                left_conductance = splice_probe._mean_group_metric(student_conductance, left_ids)
                right_conductance = splice_probe._mean_group_metric(student_conductance, right_ids)
                condition_summary["groups"][label] = {
                    "left": {"rate_hz": left_rate, "voltage_mv": left_voltage, "conductance": left_conductance},
                    "right": {"rate_hz": right_rate, "voltage_mv": right_voltage, "conductance": right_conductance},
                    "right_minus_left": {
                        "rate_hz": right_rate - left_rate,
                        "voltage_mv": right_voltage - left_voltage,
                        "conductance": right_conductance - left_conductance,
                    },
                }
                raw_rows.extend(
                    [
                        {
                            "window_ms": float(window_ms),
                            "condition": condition_name,
                            "candidate_label": label,
                            "side": "left",
                            "mean_rate_hz": left_rate,
                            "mean_voltage_mv": left_voltage,
                            "mean_conductance": left_conductance,
                        },
                        {
                            "window_ms": float(window_ms),
                            "condition": condition_name,
                            "candidate_label": label,
                            "side": "right",
                            "mean_rate_hz": right_rate,
                            "mean_voltage_mv": right_voltage,
                            "mean_conductance": right_conductance,
                        },
                    ]
                )
            summary["results"][window_key][condition_name] = condition_summary

        for pair in pairs:
            label = str(pair["candidate_label"])
            left_diff = summary["results"][window_key]["body_left_dark"]["groups"][label]["right_minus_left"]
            center_diff = summary["results"][window_key]["body_center_dark"]["groups"][label]["right_minus_left"]
            right_diff = summary["results"][window_key]["body_right_dark"]["groups"][label]["right_minus_left"]
            bilateral_mean_rate = np.mean(
                [
                    0.5
                    * (
                        summary["results"][window_key][condition]["groups"][label]["left"]["rate_hz"]
                        + summary["results"][window_key][condition]["groups"][label]["right"]["rate_hz"]
                    )
                    for condition in ("body_left_dark", "body_center_dark", "body_right_dark")
                ]
            )
            bilateral_mean_voltage = np.mean(
                [
                    0.5
                    * (
                        summary["results"][window_key][condition]["groups"][label]["left"]["voltage_mv"]
                        + summary["results"][window_key][condition]["groups"][label]["right"]["voltage_mv"]
                    )
                    for condition in ("body_left_dark", "body_center_dark", "body_right_dark")
                ]
            )
            turn_flip_rate_score = 0.0
            if np.sign(left_diff["rate_hz"]) != 0 and np.sign(left_diff["rate_hz"]) == -np.sign(right_diff["rate_hz"]):
                turn_flip_rate_score = float(min(abs(left_diff["rate_hz"]), abs(right_diff["rate_hz"])))
            turn_flip_voltage_score = 0.0
            if np.sign(left_diff["voltage_mv"]) != 0 and np.sign(left_diff["voltage_mv"]) == -np.sign(right_diff["voltage_mv"]):
                turn_flip_voltage_score = float(min(abs(left_diff["voltage_mv"]), abs(right_diff["voltage_mv"])))
            pair_rows.append(
                {
                    "window_ms": float(window_ms),
                    "candidate_label": label,
                    "left_dark_right_minus_left_rate_hz": float(left_diff["rate_hz"]),
                    "center_dark_right_minus_left_rate_hz": float(center_diff["rate_hz"]),
                    "right_dark_right_minus_left_rate_hz": float(right_diff["rate_hz"]),
                    "left_dark_right_minus_left_voltage_mv": float(left_diff["voltage_mv"]),
                    "center_dark_right_minus_left_voltage_mv": float(center_diff["voltage_mv"]),
                    "right_dark_right_minus_left_voltage_mv": float(right_diff["voltage_mv"]),
                    "bilateral_mean_rate_hz": float(bilateral_mean_rate),
                    "bilateral_mean_voltage_mv": float(bilateral_mean_voltage),
                    "turn_flip_rate_score": float(turn_flip_rate_score),
                    "turn_flip_voltage_score": float(turn_flip_voltage_score),
                    "pair_score": float(pair["pair_score"]),
                }
            )

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["window_ms", "condition", "candidate_label", "side", "mean_rate_hz", "mean_voltage_mv", "mean_conductance"],
        )
        writer.writeheader()
        writer.writerows(raw_rows)

    pair_output = Path(args.pair_output)
    pair_output.parent.mkdir(parents=True, exist_ok=True)
    with pair_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "window_ms",
                "candidate_label",
                "left_dark_right_minus_left_rate_hz",
                "center_dark_right_minus_left_rate_hz",
                "right_dark_right_minus_left_rate_hz",
                "left_dark_right_minus_left_voltage_mv",
                "center_dark_right_minus_left_voltage_mv",
                "right_dark_right_minus_left_voltage_mv",
                "bilateral_mean_rate_hz",
                "bilateral_mean_voltage_mv",
                "turn_flip_rate_score",
                "turn_flip_voltage_score",
                "pair_score",
            ],
        )
        writer.writeheader()
        writer.writerows(pair_rows)

    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

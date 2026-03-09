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
from brain.flywire_annotations import (
    build_overlap_groups,
    build_spatial_grid_overlap_groups,
    build_spatial_overlap_groups,
    find_exact_cell_type_overlap,
    load_flywire_annotation_table,
    summarize_overlap_groups,
)
from brain.public_ids import MOTOR_READOUT_IDS
from brain.pytorch_backend import WholeBrainTorchBackend
from vision.lateralized_probe import build_body_side_stimuli, compute_retina_geometry


def _mean_metric(values_by_id: dict[int, float], root_ids: list[int]) -> float:
    values = [float(values_by_id.get(int(root_id), 0.0)) for root_id in root_ids]
    return float(np.mean(values)) if values else 0.0


def _load_relay_pairs(path: str | Path) -> list[dict[str, object]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(data["selected_paired_cell_types"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe deeper relay targets over longer windows using the calibrated body-free splice.")
    parser.add_argument("--relay-candidates-json", default="outputs/metrics/splice_relay_candidates.json")
    parser.add_argument("--vision-network-dir", default=None)
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--brain-connectivity-path", default="external/fly-brain/data/2025_Connectivity_783.parquet")
    parser.add_argument("--brain-device", default="cpu")
    parser.add_argument("--vision-refresh-rate", type=float, default=500.0)
    parser.add_argument("--vision-steps", type=int, default=30)
    parser.add_argument("--vision-tail-steps", type=int, default=8)
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
    parser.add_argument("--brain-sim-ms-values", nargs="+", type=float, default=[100.0, 250.0, 500.0, 1000.0])
    parser.add_argument("--input-pulse-ms", type=float, default=None)
    parser.add_argument("--csv-output", default="outputs/metrics/splice_relay_probe.csv")
    parser.add_argument("--pair-output", default="outputs/metrics/splice_relay_probe_pairs.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_relay_probe_summary.json")
    args = parser.parse_args()

    flyvis.device = torch.device("cpu")
    relay_pairs = _load_relay_pairs(args.relay_candidates_json)

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
    if args.spatial_mode == "uv_grid" and (int(args.spatial_u_bins) > 1 or int(args.spatial_v_bins) > 1):
        overlap_groups = build_spatial_grid_overlap_groups(
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
        overlap_summary = {
            "mode": "uv_grid",
            "num_bins": int(args.spatial_u_bins) * int(args.spatial_v_bins),
        }
        flyvis_bins = splice_probe._build_flyvis_uv_grid_bins(
            network,
            layer_indices,
            sorted({group.cell_type for group in overlap_groups}),
            int(args.spatial_u_bins),
            int(args.spatial_v_bins),
        )
        num_bins = int(args.spatial_u_bins) * int(args.spatial_v_bins)
    elif int(args.spatial_bins) > 1:
        overlap_groups = build_spatial_overlap_groups(
            annotation_table,
            cell_types=overlap_types,
            num_bins=args.spatial_bins,
            min_roots_per_bin=args.min_roots_per_bin,
        )
        overlap_summary = {
            "mode": "axis1d",
            "num_bins": int(args.spatial_bins),
        }
        flyvis_bins = splice_probe._build_flyvis_u_bins(
            network,
            layer_indices,
            sorted({group.cell_type for group in overlap_groups}),
            int(args.spatial_bins),
        )
        num_bins = int(args.spatial_bins)
    else:
        base_groups = build_overlap_groups(
            annotation_table,
            cell_types=overlap_types,
            min_roots_per_side=args.min_roots_per_side,
        )
        overlap_summary = summarize_overlap_groups(base_groups)

        class _WrappedGroup:
            def __init__(self, cell_type: str, side: str, root_ids: tuple[int, ...]) -> None:
                self.cell_type = cell_type
                self.side = side
                self.bin_index = 0
                self.root_ids = root_ids

        overlap_groups = [_WrappedGroup(group.cell_type, group.side, group.root_ids) for group in base_groups]
        flyvis_bins = splice_probe._build_flyvis_u_bins(
            network,
            layer_indices,
            sorted({group.cell_type for group in overlap_groups}),
            1,
        )
        num_bins = 1

    group_keys = {(group.cell_type, group.side, int(group.bin_index)): group for group in overlap_groups}
    complete_types = sorted({group.cell_type for group in overlap_groups})
    teacher_means_by_condition = {
        name: splice_probe._teacher_group_means(condition_tails[name], flyvis_bins, complete_types, num_bins)
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
    teacher_target_by_condition = (
        {name: splice_probe._positive_part(delta) for name, delta in teacher_signed_delta_by_condition.items()}
        if args.input_mode == "rate_positive"
        else teacher_signed_delta_by_condition
    )
    max_target_abs = max((abs(value) for mapping in teacher_target_by_condition.values() for value in mapping.values()), default=0.0)
    if max_target_abs <= 0.0:
        raise RuntimeError("No nonzero teacher targets available for relay probe")
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
    relay_ids = sorted(
        {
            int(root_id)
            for relay in relay_pairs
            for root_id in (relay["left_root_ids"] + relay["right_root_ids"])
        }
    )
    monitored_ids = sorted(
        relay_ids
        + [root_id for ids in MOTOR_READOUT_IDS.values() for root_id in ids]
    )
    backend.set_monitored_ids(monitored_ids)

    csv_rows: list[dict[str, object]] = []
    pair_rows: list[dict[str, object]] = []
    summary: dict[str, object] = {
        "relay_candidates_json": args.relay_candidates_json,
        "spatial_mode": args.spatial_mode,
        "overlap_summary": overlap_summary,
        "value_scale": float(value_scale),
        "windows_ms": [float(value) for value in args.brain_sim_ms_values],
        "input_pulse_ms": None if args.input_pulse_ms is None else float(args.input_pulse_ms),
        "spatial_swap_uv": bool(args.spatial_swap_uv),
        "spatial_flip_u": bool(args.spatial_flip_u),
        "spatial_flip_v": bool(args.spatial_flip_v),
        "spatial_mirror_u_by_side": bool(args.spatial_mirror_u_by_side),
        "relay_pairs": relay_pairs,
        "results": {},
    }

    for window_ms in [float(value) for value in args.brain_sim_ms_values]:
        window_key = f"{window_ms:g}ms"
        summary["results"][window_key] = {}
        num_steps = max(1, int(round(window_ms / backend.dt_ms)))
        pulse_steps = None if args.input_pulse_ms is None else max(1, int(round(float(args.input_pulse_ms) / backend.dt_ms)))
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
            if pulse_steps is None or pulse_steps >= num_steps:
                student_rates, student_voltage, student_conductance = backend.step_with_state(
                    {},
                    num_steps=num_steps,
                    direct_input_rates_hz=direct_input_rates_hz,
                    direct_current_by_id=direct_current_by_id,
                )
            else:
                backend.step_with_state(
                    {},
                    num_steps=pulse_steps,
                    direct_input_rates_hz=direct_input_rates_hz,
                    direct_current_by_id=direct_current_by_id,
                )
                student_rates, student_voltage, student_conductance = backend.step_with_state(
                    {},
                    num_steps=num_steps - pulse_steps,
                    direct_input_rates_hz=None,
                    direct_current_by_id=None,
                )
            motor_rates = splice_probe._aggregate_motor_rates(student_rates)
            relay_summary: dict[str, object] = {}
            for relay in relay_pairs:
                cell_type = str(relay["cell_type"])
                left_root_ids = [int(value) for value in relay["left_root_ids"]]
                right_root_ids = [int(value) for value in relay["right_root_ids"]]
                left_metrics = {
                    "rate_hz": _mean_metric(student_rates, left_root_ids),
                    "voltage_mv": _mean_metric(student_voltage, left_root_ids),
                    "conductance": _mean_metric(student_conductance, left_root_ids),
                }
                right_metrics = {
                    "rate_hz": _mean_metric(student_rates, right_root_ids),
                    "voltage_mv": _mean_metric(student_voltage, right_root_ids),
                    "conductance": _mean_metric(student_conductance, right_root_ids),
                }
                relay_summary[cell_type] = {
                    "left": left_metrics,
                    "right": right_metrics,
                    "right_minus_left": {
                        "rate_hz": float(right_metrics["rate_hz"] - left_metrics["rate_hz"]),
                        "voltage_mv": float(right_metrics["voltage_mv"] - left_metrics["voltage_mv"]),
                        "conductance": float(right_metrics["conductance"] - left_metrics["conductance"]),
                    },
                }
                csv_rows.extend(
                    [
                        {
                            "window_ms": window_ms,
                            "condition": condition_name,
                            "cell_type": cell_type,
                            "side": "left",
                            "mean_rate_hz": left_metrics["rate_hz"],
                            "mean_voltage_mv": left_metrics["voltage_mv"],
                            "mean_conductance": left_metrics["conductance"],
                        },
                        {
                            "window_ms": window_ms,
                            "condition": condition_name,
                            "cell_type": cell_type,
                            "side": "right",
                            "mean_rate_hz": right_metrics["rate_hz"],
                            "mean_voltage_mv": right_metrics["voltage_mv"],
                            "mean_conductance": right_metrics["conductance"],
                        },
                    ]
                )
                pair_rows.append(
                    {
                        "window_ms": window_ms,
                        "condition": condition_name,
                        "cell_type": cell_type,
                        "right_minus_left_rate_hz": relay_summary[cell_type]["right_minus_left"]["rate_hz"],
                        "right_minus_left_voltage_mv": relay_summary[cell_type]["right_minus_left"]["voltage_mv"],
                        "right_minus_left_conductance": relay_summary[cell_type]["right_minus_left"]["conductance"],
                    }
                )
            summary["results"][window_key][condition_name] = {
                "motor_rates_hz": motor_rates,
                "relay_groups": relay_summary,
            }

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "window_ms",
                "condition",
                "cell_type",
                "side",
                "mean_rate_hz",
                "mean_voltage_mv",
                "mean_conductance",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    pair_output = Path(args.pair_output)
    pair_output.parent.mkdir(parents=True, exist_ok=True)
    with pair_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "window_ms",
                "condition",
                "cell_type",
                "right_minus_left_rate_hz",
                "right_minus_left_voltage_mv",
                "right_minus_left_conductance",
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

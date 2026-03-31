from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
from torch import Tensor

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import flyvis
import torch
from flygym.examples.vision import RealTimeVisionNetworkView, RetinaMapper
from flygym.vision import Retina

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
from vision.flyvis_compat import configure_flyvis_device
from vision.lateralized_probe import build_body_side_stimuli, compute_retina_geometry


def _normalize_type(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.bytes_):
        return value.tobytes().decode("utf-8", errors="replace")
    return str(value)


def _build_layer_indices(network) -> dict[str, np.ndarray]:
    layer_indices: dict[str, np.ndarray] = {}
    for cell_type, indices in network.connectome.nodes.layer_index.items():
        layer_indices[_normalize_type(cell_type)] = np.asarray(indices[:], dtype=int)
    return layer_indices


def _build_flyvis_u_bins(network, layer_indices: dict[str, np.ndarray], cell_types: list[str], num_bins: int) -> dict[tuple[str, int], np.ndarray]:
    node_u = np.asarray(network.connectome.nodes.u[:], dtype=float).reshape(-1)
    bins: dict[tuple[str, int], np.ndarray] = {}
    for cell_type in cell_types:
        indices = layer_indices.get(cell_type)
        if indices is None or len(indices) == 0:
            continue
        order = np.argsort(node_u[indices], kind="stable")
        sorted_indices = indices[order]
        for bin_index, chunk in enumerate(np.array_split(sorted_indices, int(num_bins))):
            bins[(cell_type, int(bin_index))] = np.asarray(chunk, dtype=int)
    return bins


def _quantile_labels(values: np.ndarray, num_bins: int) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    labels = np.zeros(values.shape[0], dtype=int)
    for label, chunk in enumerate(np.array_split(order, int(num_bins))):
        labels[np.asarray(chunk, dtype=int)] = int(label)
    return labels


def _build_flyvis_uv_grid_bins(
    network,
    layer_indices: dict[str, np.ndarray],
    cell_types: list[str],
    num_u_bins: int,
    num_v_bins: int,
) -> dict[tuple[str, int], np.ndarray]:
    node_u = np.asarray(network.connectome.nodes.u[:], dtype=float).reshape(-1)
    node_v = np.asarray(network.connectome.nodes.v[:], dtype=float).reshape(-1)
    bins: dict[tuple[str, int], np.ndarray] = {}
    for cell_type in cell_types:
        indices = layer_indices.get(cell_type)
        if indices is None or len(indices) == 0:
            continue
        u_labels = _quantile_labels(node_u[indices], int(num_u_bins))
        v_labels = _quantile_labels(node_v[indices], int(num_v_bins))
        for u_bin in range(int(num_u_bins)):
            for v_bin in range(int(num_v_bins)):
                mask = (u_labels == int(u_bin)) & (v_labels == int(v_bin))
                chunk = np.asarray(indices[mask], dtype=int)
                if len(chunk) == 0:
                    continue
                bins[(cell_type, int(u_bin * int(num_v_bins) + v_bin))] = chunk
    return bins


def _prepare_visual_network(vision_network_dir: str | None):
    configure_flyvis_device(force_cpu=False)
    retina = Retina()
    retina_mapper = RetinaMapper(retina=retina)
    if vision_network_dir is None:
        vision_network_dir = str(flyvis.results_dir / "flow/0000/000")
    network_view = RealTimeVisionNetworkView(vision_network_dir)
    network = network_view.init_network(chkpt="best_chkpt")
    return retina, retina_mapper, network


def _setup_step_simulation(network, retina_mapper: RetinaMapper, baseline_gray: np.ndarray, vision_refresh_rate: float) -> None:
    visual_input = retina_mapper.flygym_to_flyvis(baseline_gray)
    visual_input = Tensor(visual_input).to(flyvis.device)
    initial_state = network.fade_in_state(
        t_fade_in=1.0,
        dt=1.0 / vision_refresh_rate,
        initial_frames=visual_input.unsqueeze(1),
    )
    network.setup_step_by_step_simulation(
        dt=1.0 / vision_refresh_rate,
        initial_state=initial_state,
        as_states=False,
        num_samples=2,
    )


def _run_condition(
    network,
    retina_mapper: RetinaMapper,
    stimulus_gray: np.ndarray,
    *,
    baseline_gray: np.ndarray,
    vision_refresh_rate: float,
    steps: int,
    tail_steps: int,
) -> np.ndarray:
    _setup_step_simulation(network, retina_mapper, baseline_gray, vision_refresh_rate)
    visual_input = retina_mapper.flygym_to_flyvis(stimulus_gray)
    visual_input = Tensor(visual_input).to(flyvis.device)
    tail: list[np.ndarray] = []
    try:
        for _ in range(steps):
            nn_activities_arr = network.forward_one_step(visual_input)
            if hasattr(nn_activities_arr, "detach"):
                nn_activities_arr = nn_activities_arr.detach()
            if hasattr(nn_activities_arr, "cpu"):
                nn_activities_arr = nn_activities_arr.cpu().numpy()
            tail.append(np.asarray(nn_activities_arr, dtype=float))
            if len(tail) > tail_steps:
                tail.pop(0)
    finally:
        network.cleanup_step_by_step_simulation()
    return np.stack(tail, axis=0)


def _teacher_group_means(
    activity_tail: np.ndarray,
    flyvis_bins: dict[tuple[str, int], np.ndarray],
    cell_types: list[str],
    num_bins: int,
) -> dict[tuple[str, str, int], float]:
    means: dict[tuple[str, str, int], float] = {}
    eye_map = {"left": 0, "right": 1}
    for cell_type in cell_types:
        for bin_index in range(int(num_bins)):
            indices = flyvis_bins.get((cell_type, bin_index))
            if indices is None or len(indices) == 0:
                continue
            for side, eye_index in eye_map.items():
                means[(cell_type, side, int(bin_index))] = float(activity_tail[:, eye_index, indices].mean())
    return means


def _positive_part(values: dict[tuple[str, str, int], float]) -> dict[tuple[str, str, int], float]:
    return {key: max(0.0, float(value)) for key, value in values.items()}


def _pearson(values_a: list[float], values_b: list[float]) -> float | None:
    if len(values_a) < 2 or len(values_b) < 2:
        return None
    arr_a = np.asarray(values_a, dtype=float)
    arr_b = np.asarray(values_b, dtype=float)
    if np.allclose(arr_a.std(), 0.0) or np.allclose(arr_b.std(), 0.0):
        return None
    return float(np.corrcoef(arr_a, arr_b)[0, 1])


def _mean_group_rate(rates_by_id: dict[int, float], root_ids: tuple[int, ...]) -> float:
    values = [float(rates_by_id.get(root_id, 0.0)) for root_id in root_ids]
    return float(np.mean(values)) if values else 0.0


def _mean_group_metric(values_by_id: dict[int, float], root_ids: tuple[int, ...]) -> float:
    values = [float(values_by_id.get(root_id, 0.0)) for root_id in root_ids]
    return float(np.mean(values)) if values else 0.0


def _load_cell_type_transforms(path: str | None) -> dict[str, dict[str, object]] | None:
    if path in (None, ""):
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("cell_types"), dict):
        payload = payload["cell_types"]
    if not isinstance(payload, dict):
        raise ValueError("cell-type transform payload must be a mapping or contain a 'cell_types' mapping")
    return {str(cell_type): dict(values) for cell_type, values in payload.items() if isinstance(values, dict)}


def _aggregate_motor_rates(rates_by_id: dict[int, float]) -> dict[str, float]:
    return {
        group_name: _mean_group_rate(rates_by_id, tuple(neuron_ids))
        for group_name, neuron_ids in MOTOR_READOUT_IDS.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a body-free FlyVis-to-whole-brain splice probe using exact shared visual cell types.")
    parser.add_argument("--vision-network-dir", default=None)
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--brain-connectivity-path", default="external/fly-brain/data/2025_Connectivity_783.parquet")
    parser.add_argument("--brain-device", default="cpu")
    parser.add_argument("--vision-refresh-rate", type=float, default=500.0)
    parser.add_argument("--vision-steps", type=int, default=40)
    parser.add_argument("--vision-tail-steps", type=int, default=10)
    parser.add_argument("--brain-sim-ms", type=float, default=20.0)
    parser.add_argument("--input-mode", choices=("rate_positive", "current_signed"), default="current_signed")
    parser.add_argument("--max-input-rate-hz", type=float, default=120.0)
    parser.add_argument("--max-abs-current", type=float, default=120.0)
    parser.add_argument("--spatial-mode", choices=("axis1d", "uv_grid"), default="axis1d")
    parser.add_argument("--spatial-bins", type=int, default=1)
    parser.add_argument("--spatial-u-bins", type=int, default=2)
    parser.add_argument("--spatial-v-bins", type=int, default=2)
    parser.add_argument("--spatial-swap-uv", action="store_true")
    parser.add_argument("--spatial-flip-u", action="store_true")
    parser.add_argument("--spatial-flip-v", action="store_true")
    parser.add_argument("--spatial-mirror-u-by-side", action="store_true")
    parser.add_argument("--cell-type-transform-json", default=None)
    parser.add_argument("--min-roots-per-side", type=int, default=50)
    parser.add_argument("--min-roots-per-bin", type=int, default=20)
    parser.add_argument("--baseline-value", type=float, default=1.0)
    parser.add_argument("--patch-value", type=float, default=0.0)
    parser.add_argument("--side-fraction", type=float, default=0.35)
    parser.add_argument("--csv-output", default="outputs/metrics/splice_probe_groups.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_probe_summary.json")
    parser.add_argument("--side-diff-output", default="outputs/metrics/splice_probe_side_differences.csv")
    args = parser.parse_args()

    flyvis.device = torch.device("cpu")

    retina, retina_mapper, network = _prepare_visual_network(args.vision_network_dir)
    geometry = compute_retina_geometry(retina.ommatidia_id_map)
    stimuli = build_body_side_stimuli(
        geometry,
        baseline_value=args.baseline_value,
        patch_value=args.patch_value,
        side_fraction=args.side_fraction,
    )
    condition_names = ("baseline_gray", "body_left_dark", "body_center_dark", "body_right_dark")
    condition_tails = {
        name: _run_condition(
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

    layer_indices = _build_layer_indices(network)
    annotation_table = load_flywire_annotation_table(args.annotation_path)
    overlap_types = find_exact_cell_type_overlap(layer_indices.keys(), annotation_table)
    if args.spatial_mode == "uv_grid" and (int(args.spatial_u_bins) > 1 or int(args.spatial_v_bins) > 1):
        cell_type_transforms = _load_cell_type_transforms(args.cell_type_transform_json)
        overlap_groups = build_spatial_grid_overlap_groups(
            annotation_table,
            cell_types=overlap_types,
            num_u_bins=args.spatial_u_bins,
            num_v_bins=args.spatial_v_bins,
            swap_uv=bool(args.spatial_swap_uv),
            flip_u=bool(args.spatial_flip_u),
            flip_v=bool(args.spatial_flip_v),
            mirror_u_by_side=bool(args.spatial_mirror_u_by_side),
            cell_type_transforms=cell_type_transforms,
            min_roots_per_bin=args.min_roots_per_bin,
        )
        overlap_summary = {
            "num_groups": len(overlap_groups),
            "num_complete_bilateral_cell_types": len(sorted({group.cell_type for group in overlap_groups})),
            "complete_bilateral_cell_types": sorted({group.cell_type for group in overlap_groups}),
            "counts_by_cell_type": {
                cell_type: {
                    side: int(sum(len(group.root_ids) for group in overlap_groups if group.cell_type == cell_type and group.side == side))
                    for side in ("left", "right")
                }
                for cell_type in sorted({group.cell_type for group in overlap_groups})
            },
            "num_bins": int(args.spatial_u_bins) * int(args.spatial_v_bins),
            "num_u_bins": int(args.spatial_u_bins),
            "num_v_bins": int(args.spatial_v_bins),
            "mode": "uv_grid",
        }
        group_keys = {(group.cell_type, group.side, group.bin_index): group for group in overlap_groups}
        flyvis_num_bins = int(args.spatial_u_bins) * int(args.spatial_v_bins)
        flyvis_bins_builder = lambda complete_types: _build_flyvis_uv_grid_bins(
            network,
            layer_indices,
            complete_types,
            int(args.spatial_u_bins),
            int(args.spatial_v_bins),
        )
    elif int(args.spatial_bins) > 1:
        overlap_groups = build_spatial_overlap_groups(
            annotation_table,
            cell_types=overlap_types,
            num_bins=args.spatial_bins,
            min_roots_per_bin=args.min_roots_per_bin,
        )
        overlap_summary = {
            "num_groups": len(overlap_groups),
            "num_complete_bilateral_cell_types": len(sorted({group.cell_type for group in overlap_groups})),
            "complete_bilateral_cell_types": sorted({group.cell_type for group in overlap_groups}),
            "counts_by_cell_type": {
                cell_type: {
                    side: int(sum(len(group.root_ids) for group in overlap_groups if group.cell_type == cell_type and group.side == side))
                    for side in ("left", "right")
                }
                for cell_type in sorted({group.cell_type for group in overlap_groups})
            },
            "num_bins": int(args.spatial_bins),
            "mode": "spatial_bins",
        }
        group_keys = {(group.cell_type, group.side, group.bin_index): group for group in overlap_groups}
        flyvis_num_bins = max(1, int(args.spatial_bins))
        flyvis_bins_builder = lambda complete_types: _build_flyvis_u_bins(network, layer_indices, complete_types, flyvis_num_bins)
    else:
        base_groups = build_overlap_groups(
            annotation_table,
            cell_types=overlap_types,
            min_roots_per_side=args.min_roots_per_side,
        )
        overlap_summary = summarize_overlap_groups(base_groups)
        overlap_summary["num_bins"] = 1
        overlap_summary["mode"] = "type_side"

        class _WrappedGroup:
            def __init__(self, cell_type: str, side: str, root_ids: tuple[int, ...]) -> None:
                self.cell_type = cell_type
                self.side = side
                self.bin_index = 0
                self.root_ids = root_ids

        overlap_groups = [_WrappedGroup(group.cell_type, group.side, group.root_ids) for group in base_groups]
        group_keys = {(group.cell_type, group.side, group.bin_index): group for group in overlap_groups}
        flyvis_num_bins = 1
        flyvis_bins_builder = lambda complete_types: _build_flyvis_u_bins(network, layer_indices, complete_types, flyvis_num_bins)

    complete_types = list(overlap_summary["complete_bilateral_cell_types"])
    flyvis_bins = flyvis_bins_builder(complete_types)

    teacher_means_by_condition = {
        name: _teacher_group_means(condition_tails[name], flyvis_bins, complete_types, flyvis_num_bins)
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
        {name: _positive_part(delta) for name, delta in teacher_signed_delta_by_condition.items()}
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
    num_brain_steps = max(1, int(round(args.brain_sim_ms / backend.dt_ms)))

    raw_student_group_rates: dict[str, dict[tuple[str, str, int], float]] = {}
    raw_student_group_voltage: dict[str, dict[tuple[str, str, int], float]] = {}
    raw_student_group_conductance: dict[str, dict[tuple[str, str, int], float]] = {}
    raw_student_motor_rates: dict[str, dict[str, float]] = {}
    input_counts: dict[str, int] = {}
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
                    direct_input_rates_hz[root_id] = scaled_value
                else:
                    direct_current_by_id[root_id] = scaled_value

        backend.reset(seed=0)
        student_rates, student_voltage, student_conductance = backend.step_with_state(
            {},
            num_steps=num_brain_steps,
            direct_input_rates_hz=direct_input_rates_hz,
            direct_current_by_id=direct_current_by_id,
        )
        raw_student_group_rates[condition_name] = {
            key: _mean_group_rate(student_rates, group.root_ids)
            for key, group in group_keys.items()
        }
        raw_student_group_voltage[condition_name] = {
            key: _mean_group_metric(student_voltage, group.root_ids)
            for key, group in group_keys.items()
        }
        raw_student_group_conductance[condition_name] = {
            key: _mean_group_metric(student_conductance, group.root_ids)
            for key, group in group_keys.items()
        }
        raw_student_motor_rates[condition_name] = _aggregate_motor_rates(student_rates)
        active_inputs = direct_input_rates_hz if args.input_mode == "rate_positive" else direct_current_by_id
        input_counts[condition_name] = int(sum(1 for value in active_inputs.values() if not np.isclose(value, 0.0)))

    baseline_student = raw_student_group_rates["baseline_gray"]
    baseline_student_voltage = raw_student_group_voltage["baseline_gray"]
    baseline_student_conductance = raw_student_group_conductance["baseline_gray"]
    student_delta_by_condition = {
        name: {
            key: float(value - baseline_student.get(key, 0.0))
            for key, value in rates.items()
        }
        for name, rates in raw_student_group_rates.items()
    }
    student_voltage_delta_by_condition = {
        name: {
            key: float(value - baseline_student_voltage.get(key, 0.0))
            for key, value in values.items()
        }
        for name, values in raw_student_group_voltage.items()
    }
    student_conductance_delta_by_condition = {
        name: {
            key: float(value - baseline_student_conductance.get(key, 0.0))
            for key, value in values.items()
        }
        for name, values in raw_student_group_conductance.items()
    }

    csv_rows: list[dict[str, object]] = []
    side_rows: list[dict[str, object]] = []
    condition_summaries: dict[str, dict[str, object]] = {}
    for condition_name in condition_names:
        teacher_values: list[float] = []
        student_rate_values: list[float] = []
        student_voltage_values: list[float] = []
        student_conductance_values: list[float] = []
        teacher_side_diffs: list[float] = []
        student_rate_side_diffs: list[float] = []
        student_voltage_side_diffs: list[float] = []
        student_conductance_side_diffs: list[float] = []
        for cell_type in complete_types:
            for bin_index in range(int(flyvis_num_bins)):
                left_key = (cell_type, "left", int(bin_index))
                right_key = (cell_type, "right", int(bin_index))
                left_group = group_keys.get(left_key)
                right_group = group_keys.get(right_key)
                if left_group is None or right_group is None:
                    continue
                left_teacher_raw = float(teacher_means_by_condition[condition_name].get(left_key, 0.0))
                right_teacher_raw = float(teacher_means_by_condition[condition_name].get(right_key, 0.0))
                left_teacher_delta = float(teacher_signed_delta_by_condition[condition_name].get(left_key, 0.0))
                right_teacher_delta = float(teacher_signed_delta_by_condition[condition_name].get(right_key, 0.0))
                left_teacher_target = float(teacher_target_by_condition[condition_name].get(left_key, 0.0))
                right_teacher_target = float(teacher_target_by_condition[condition_name].get(right_key, 0.0))
                left_student_raw = float(raw_student_group_rates[condition_name].get(left_key, 0.0))
                right_student_raw = float(raw_student_group_rates[condition_name].get(right_key, 0.0))
                left_student_delta = float(student_delta_by_condition[condition_name].get(left_key, 0.0))
                right_student_delta = float(student_delta_by_condition[condition_name].get(right_key, 0.0))
                left_student_raw_voltage = float(raw_student_group_voltage[condition_name].get(left_key, 0.0))
                right_student_raw_voltage = float(raw_student_group_voltage[condition_name].get(right_key, 0.0))
                left_student_delta_voltage = float(student_voltage_delta_by_condition[condition_name].get(left_key, 0.0))
                right_student_delta_voltage = float(student_voltage_delta_by_condition[condition_name].get(right_key, 0.0))
                left_student_raw_conductance = float(raw_student_group_conductance[condition_name].get(left_key, 0.0))
                right_student_raw_conductance = float(raw_student_group_conductance[condition_name].get(right_key, 0.0))
                left_student_delta_conductance = float(student_conductance_delta_by_condition[condition_name].get(left_key, 0.0))
                right_student_delta_conductance = float(student_conductance_delta_by_condition[condition_name].get(right_key, 0.0))
                left_input_value = float(left_teacher_target * value_scale)
                right_input_value = float(right_teacher_target * value_scale)
                flyvis_node_count = int(len(flyvis_bins.get((cell_type, int(bin_index)), np.array([], dtype=int))))
                csv_rows.extend(
                    [
                        {
                            "condition": condition_name,
                            "cell_type": cell_type,
                            "side": "left",
                            "bin_index": int(bin_index),
                            "flyvis_node_count": flyvis_node_count,
                            "brain_root_count": int(len(left_group.root_ids)),
                            "teacher_raw_mean": left_teacher_raw,
                            "teacher_baseline_mean": float(baseline_teacher.get(left_key, 0.0)),
                            "teacher_signed_delta": left_teacher_delta,
                            "teacher_target_value": left_teacher_target,
                            "input_value": left_input_value,
                            "student_raw_rate_hz": left_student_raw,
                            "student_delta_rate_hz": left_student_delta,
                            "student_raw_voltage_mv": left_student_raw_voltage,
                            "student_delta_voltage_mv": left_student_delta_voltage,
                            "student_raw_conductance": left_student_raw_conductance,
                            "student_delta_conductance": left_student_delta_conductance,
                        },
                        {
                            "condition": condition_name,
                            "cell_type": cell_type,
                            "side": "right",
                            "bin_index": int(bin_index),
                            "flyvis_node_count": flyvis_node_count,
                            "brain_root_count": int(len(right_group.root_ids)),
                            "teacher_raw_mean": right_teacher_raw,
                            "teacher_baseline_mean": float(baseline_teacher.get(right_key, 0.0)),
                            "teacher_signed_delta": right_teacher_delta,
                            "teacher_target_value": right_teacher_target,
                            "input_value": right_input_value,
                            "student_raw_rate_hz": right_student_raw,
                            "student_delta_rate_hz": right_student_delta,
                            "student_raw_voltage_mv": right_student_raw_voltage,
                            "student_delta_voltage_mv": right_student_delta_voltage,
                            "student_raw_conductance": right_student_raw_conductance,
                            "student_delta_conductance": right_student_delta_conductance,
                        },
                    ]
                )
                teacher_values.extend([left_teacher_target, right_teacher_target])
                student_rate_values.extend([left_student_delta, right_student_delta])
                student_voltage_values.extend([left_student_delta_voltage, right_student_delta_voltage])
                student_conductance_values.extend([left_student_delta_conductance, right_student_delta_conductance])
                teacher_side_diffs.append(float(right_teacher_target - left_teacher_target))
                student_rate_side_diffs.append(float(right_student_delta - left_student_delta))
                student_voltage_side_diffs.append(float(right_student_delta_voltage - left_student_delta_voltage))
                student_conductance_side_diffs.append(float(right_student_delta_conductance - left_student_delta_conductance))
                side_rows.append(
                    {
                        "condition": condition_name,
                        "cell_type": cell_type,
                        "bin_index": int(bin_index),
                        "teacher_right_minus_left": float(right_teacher_target - left_teacher_target),
                        "student_right_minus_left_rate_hz": float(right_student_delta - left_student_delta),
                        "student_right_minus_left_voltage_mv": float(right_student_delta_voltage - left_student_delta_voltage),
                        "student_right_minus_left_conductance": float(right_student_delta_conductance - left_student_delta_conductance),
                    }
                )

        condition_summaries[condition_name] = {
            "teacher_student_group_correlation": _pearson(teacher_values, student_rate_values),
            "teacher_student_side_diff_correlation": _pearson(teacher_side_diffs, student_rate_side_diffs),
            "teacher_student_group_correlation_rate": _pearson(teacher_values, student_rate_values),
            "teacher_student_side_diff_correlation_rate": _pearson(teacher_side_diffs, student_rate_side_diffs),
            "teacher_student_group_correlation_voltage": _pearson(teacher_values, student_voltage_values),
            "teacher_student_side_diff_correlation_voltage": _pearson(teacher_side_diffs, student_voltage_side_diffs),
            "teacher_student_group_correlation_conductance": _pearson(teacher_values, student_conductance_values),
            "teacher_student_side_diff_correlation_conductance": _pearson(teacher_side_diffs, student_conductance_side_diffs),
            "num_nonzero_direct_inputs": int(input_counts[condition_name]),
            "motor_rates_hz": raw_student_motor_rates[condition_name],
            "max_abs_student_delta_rate_hz": float(max((abs(value) for value in student_rate_values), default=0.0)),
            "max_abs_student_delta_voltage_mv": float(max((abs(value) for value in student_voltage_values), default=0.0)),
            "max_abs_student_delta_conductance": float(max((abs(value) for value in student_conductance_values), default=0.0)),
        }

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "condition",
                "cell_type",
                "side",
                "bin_index",
                "flyvis_node_count",
                "brain_root_count",
                "teacher_raw_mean",
                "teacher_baseline_mean",
                "teacher_signed_delta",
                "teacher_target_value",
                "input_value",
                "student_raw_rate_hz",
                "student_delta_rate_hz",
                "student_raw_voltage_mv",
                "student_delta_voltage_mv",
                "student_raw_conductance",
                "student_delta_conductance",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    side_output = Path(args.side_diff_output)
    side_output.parent.mkdir(parents=True, exist_ok=True)
    with side_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "condition",
                "cell_type",
                "bin_index",
                "teacher_right_minus_left",
                "student_right_minus_left_rate_hz",
                "student_right_minus_left_voltage_mv",
                "student_right_minus_left_conductance",
            ],
        )
        writer.writeheader()
        writer.writerows(side_rows)

    summary = {
        "annotation_path": args.annotation_path,
        "brain_device": backend.device_name,
        "input_mode": args.input_mode,
        "spatial_bins": int(args.spatial_bins),
        "spatial_mode": args.spatial_mode,
        "spatial_u_bins": int(args.spatial_u_bins),
        "spatial_v_bins": int(args.spatial_v_bins),
        "spatial_swap_uv": bool(args.spatial_swap_uv),
        "spatial_flip_u": bool(args.spatial_flip_u),
        "spatial_flip_v": bool(args.spatial_flip_v),
        "spatial_mirror_u_by_side": bool(args.spatial_mirror_u_by_side),
        "cell_type_transform_json": args.cell_type_transform_json,
        "num_overlap_cell_types": len(overlap_types),
        "overlap_summary": overlap_summary,
        "value_scale": value_scale,
        "conditions": condition_summaries,
        "notes": [
            "This probe uses the official FlyWire annotation supplement to ground the overlap by exact cell_type labels plus side, not by fabricated left/right splits.",
            "When input_mode=current_signed, the body-free splice can represent inhibitory visual deviations at the boundary via signed direct current, not only positive rate deltas.",
            "When spatial_mode=axis1d and spatial_bins>1, the whole-brain side uses inferred coarse one-axis spatial bins from public soma/position coordinates; this is more grounded than arbitrary halves, but it is still an inferred retinotopic proxy rather than a proven column identity map.",
            "When spatial_mode=uv_grid, the whole-brain side uses the first two public spatial principal axes and the FlyVis side uses native u/v coordinates; this is a better correspondence than the old one-axis binning, but it is still a public-inferred retinotopic proxy rather than an exact column identity map.",
            "This is a body-free splice probe. It validates the splice boundary before any embodied claims.",
        ],
    }
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

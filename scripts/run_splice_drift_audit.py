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


def _load_group_pairs(path: str | Path, *, label_key: str) -> list[dict[str, object]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for item in data.get("selected_paired_cell_types", []):
        label = str(item.get(label_key) or item.get("cell_type") or item.get("candidate_label") or "").strip()
        if not label:
            continue
        rows.append(
            {
                "label": label,
                "left_root_ids": [int(value) for value in item.get("left_root_ids", [])],
                "right_root_ids": [int(value) for value in item.get("right_root_ids", [])],
            }
        )
    return rows


def _load_recommended_descending_labels(path: str | Path) -> dict[str, set[str]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        "forward": {str(value) for value in data.get("forward_cell_types", [])},
        "turn": {str(value) for value in data.get("turn_cell_types", [])},
    }


def _mean_metric(values_by_id: dict[int, float], root_ids: list[int]) -> float:
    values = [float(values_by_id.get(int(root_id), 0.0)) for root_id in root_ids]
    return float(np.mean(values)) if values else 0.0


def _aggregate_named_groups(
    values_by_id: dict[int, float],
    groups: list[dict[str, object]],
) -> dict[str, dict[str, float]]:
    payload: dict[str, dict[str, float]] = {}
    for group in groups:
        left_value = _mean_metric(values_by_id, list(group["left_root_ids"]))
        right_value = _mean_metric(values_by_id, list(group["right_root_ids"]))
        payload[str(group["label"])] = {
            "left": left_value,
            "right": right_value,
            "right_minus_left": float(right_value - left_value),
        }
    return payload


def _aggregate_fixed_motor(values_by_id: dict[int, float]) -> dict[str, float]:
    def mean_ids(ids: list[int]) -> float:
        return _mean_metric(values_by_id, [int(value) for value in ids])

    payload = {name: mean_ids(list(ids)) for name, ids in MOTOR_READOUT_IDS.items()}
    payload["turn_bias"] = float(payload["turn_right"] - payload["turn_left"])
    payload["forward_bias"] = float(payload["forward_right"] - payload["forward_left"])
    return payload


def _aggregate_recommended_descending_bias(
    rates_by_id: dict[int, float],
    descending_groups: list[dict[str, object]],
    recommended_labels: dict[str, set[str]],
) -> dict[str, float]:
    turn_left: list[float] = []
    turn_right: list[float] = []
    forward_left: list[float] = []
    forward_right: list[float] = []
    for group in descending_groups:
        label = str(group["label"])
        left_value = _mean_metric(rates_by_id, list(group["left_root_ids"]))
        right_value = _mean_metric(rates_by_id, list(group["right_root_ids"]))
        if label in recommended_labels["turn"]:
            turn_left.append(left_value)
            turn_right.append(right_value)
        if label in recommended_labels["forward"]:
            forward_left.append(left_value)
            forward_right.append(right_value)
    payload = {
        "turn_left": float(np.mean(turn_left)) if turn_left else 0.0,
        "turn_right": float(np.mean(turn_right)) if turn_right else 0.0,
        "forward_left": float(np.mean(forward_left)) if forward_left else 0.0,
        "forward_right": float(np.mean(forward_right)) if forward_right else 0.0,
    }
    payload["turn_bias"] = float(payload["turn_right"] - payload["turn_left"])
    payload["forward_bias"] = float(payload["forward_right"] - payload["forward_left"])
    return payload


def _snapshot_contrastive(
    left_condition_payload: dict[str, dict[str, float]],
    right_condition_payload: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    labels = sorted(set(left_condition_payload) | set(right_condition_payload))
    return {
        label: {
            "left_condition_right_minus_left": float(left_condition_payload.get(label, {}).get("right_minus_left", 0.0)),
            "right_condition_right_minus_left": float(right_condition_payload.get(label, {}).get("right_minus_left", 0.0)),
            "contrastive_right_minus_left": float(
                right_condition_payload.get(label, {}).get("right_minus_left", 0.0)
                - left_condition_payload.get(label, {}).get("right_minus_left", 0.0)
            ),
        }
        for label in labels
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a time-resolved body-free audit of the 500 ms splice drift.")
    parser.add_argument("--vision-network-dir", default=None)
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--brain-connectivity-path", default="external/fly-brain/data/2025_Connectivity_783.parquet")
    parser.add_argument("--brain-device", default="cpu")
    parser.add_argument("--relay-candidates-json", default="outputs/metrics/splice_relay_candidates.json")
    parser.add_argument("--descending-candidates-json", default="outputs/metrics/descending_readout_candidates_strict.json")
    parser.add_argument("--descending-recommended-json", default="outputs/metrics/descending_readout_recommended.json")
    parser.add_argument("--cell-type-transform-json", default="outputs/metrics/splice_celltype_alignment_recommended.json")
    parser.add_argument("--vision-refresh-rate", type=float, default=500.0)
    parser.add_argument("--vision-steps", type=int, default=30)
    parser.add_argument("--vision-tail-steps", type=int, default=8)
    parser.add_argument("--max-abs-current", type=float, default=120.0)
    parser.add_argument("--baseline-value", type=float, default=1.0)
    parser.add_argument("--patch-value", type=float, default=0.0)
    parser.add_argument("--side-fraction", type=float, default=0.35)
    parser.add_argument("--spatial-u-bins", type=int, default=2)
    parser.add_argument("--spatial-v-bins", type=int, default=2)
    parser.add_argument("--spatial-swap-uv", action="store_true")
    parser.add_argument("--spatial-flip-u", action="store_true")
    parser.add_argument("--spatial-flip-v", action="store_true")
    parser.add_argument("--spatial-mirror-u-by-side", action="store_true")
    parser.add_argument("--min-roots-per-bin", type=int, default=20)
    parser.add_argument("--chunk-ms", type=float, default=25.0)
    parser.add_argument("--total-ms", type=float, default=500.0)
    parser.add_argument("--input-pulse-ms-values", nargs="+", type=float, default=[0.0, 25.0])
    parser.add_argument("--csv-output", default="outputs/metrics/splice_drift_audit_timeseries.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_drift_audit_summary.json")
    args = parser.parse_args()

    flyvis.device = torch.device("cpu")

    relay_groups = _load_group_pairs(args.relay_candidates_json, label_key="cell_type")
    descending_groups = _load_group_pairs(args.descending_candidates_json, label_key="candidate_label")
    recommended_descending = _load_recommended_descending_labels(args.descending_recommended_json)

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
    cell_type_transforms = splice_probe._load_cell_type_transforms(args.cell_type_transform_json)
    overlap_groups = build_spatial_grid_overlap_groups(
        annotation_table,
        cell_types=overlap_types,
        num_u_bins=int(args.spatial_u_bins),
        num_v_bins=int(args.spatial_v_bins),
        swap_uv=bool(args.spatial_swap_uv),
        flip_u=bool(args.spatial_flip_u),
        flip_v=bool(args.spatial_flip_v),
        mirror_u_by_side=bool(args.spatial_mirror_u_by_side),
        cell_type_transforms=cell_type_transforms,
        min_roots_per_bin=int(args.min_roots_per_bin),
    )
    group_keys = {(group.cell_type, group.side, int(group.bin_index)): group for group in overlap_groups}
    complete_types = sorted({group.cell_type for group in overlap_groups})
    flyvis_bins = splice_probe._build_flyvis_uv_grid_bins(
        network,
        layer_indices,
        complete_types,
        int(args.spatial_u_bins),
        int(args.spatial_v_bins),
    )
    num_bins = int(args.spatial_u_bins) * int(args.spatial_v_bins)
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
    max_target_abs = max(
        (abs(value) for mapping in teacher_signed_delta_by_condition.values() for value in mapping.values()),
        default=0.0,
    )
    if max_target_abs <= 0.0:
        raise RuntimeError("No nonzero teacher deltas available for drift audit")
    value_scale = float(args.max_abs_current) / max_target_abs

    monitored_ids = sorted(
        {
            root_id
            for group in relay_groups + descending_groups
            for root_id in list(group["left_root_ids"]) + list(group["right_root_ids"])
        }
        | {
            neuron_id
            for ids in MOTOR_READOUT_IDS.values()
            for neuron_id in ids
        }
    )
    backend = WholeBrainTorchBackend(
        completeness_path=args.brain_completeness_path,
        connectivity_path=args.brain_connectivity_path,
        device=args.brain_device,
    )
    backend.set_monitored_ids(monitored_ids)

    chunk_steps = max(1, int(round(float(args.chunk_ms) / backend.dt_ms)))
    total_steps = max(chunk_steps, int(round(float(args.total_ms) / backend.dt_ms)))
    total_chunks = max(1, int(np.ceil(total_steps / chunk_steps)))
    pulse_values = [None if float(value) <= 0.0 else float(value) for value in args.input_pulse_ms_values]

    csv_rows: list[dict[str, object]] = []
    schedule_results: dict[str, dict[str, object]] = {}

    for pulse_ms in pulse_values:
        schedule_key = "hold" if pulse_ms is None else f"pulse_{pulse_ms:g}ms"
        schedule_results[schedule_key] = {"timeseries": {}, "checkpoint_summary": {}}
        for condition_name in ("body_left_dark", "body_right_dark"):
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
            condition_timeseries: list[dict[str, object]] = []
            elapsed_ms = 0.0
            for chunk_index in range(total_chunks):
                remaining_steps = total_steps - (chunk_index * chunk_steps)
                if remaining_steps <= 0:
                    break
                current_steps = min(chunk_steps, remaining_steps)
                if pulse_ms is None:
                    chunk_input = direct_current_by_id
                else:
                    chunk_start_ms = float(chunk_index * chunk_steps * backend.dt_ms)
                    chunk_end_ms = chunk_start_ms + float(current_steps * backend.dt_ms)
                    chunk_input = direct_current_by_id if chunk_start_ms < pulse_ms else None
                    if chunk_start_ms < pulse_ms < chunk_end_ms:
                        active_steps = max(1, int(round((pulse_ms - chunk_start_ms) / backend.dt_ms)))
                        active_rates, active_voltage, active_conductance = backend.step_with_state(
                            {},
                            num_steps=active_steps,
                            direct_current_by_id=direct_current_by_id,
                        )
                        remaining_chunk_steps = current_steps - active_steps
                        if remaining_chunk_steps > 0:
                            rates, voltage, conductance = backend.step_with_state(
                                {},
                                num_steps=remaining_chunk_steps,
                                direct_current_by_id=None,
                            )
                        else:
                            rates, voltage, conductance = active_rates, active_voltage, active_conductance
                        elapsed_ms = chunk_end_ms
                    else:
                        rates, voltage, conductance = backend.step_with_state({}, num_steps=current_steps, direct_current_by_id=chunk_input)
                        elapsed_ms = chunk_end_ms
                        if chunk_input is not None or chunk_start_ms >= pulse_ms:
                            pass
                        else:
                            raise RuntimeError("unexpected pulse schedule branch")
                    # Skip the default step call below because this chunk is already handled.
                    if chunk_start_ms < pulse_ms < chunk_end_ms:
                        fixed_motor = _aggregate_fixed_motor(rates)
                        recommended_desc = _aggregate_recommended_descending_bias(rates, descending_groups, recommended_descending)
                        relay_payload = _aggregate_named_groups(voltage, relay_groups)
                        descending_payload = _aggregate_named_groups(rates, descending_groups)
                        condition_timeseries.append(
                            {
                                "time_ms": elapsed_ms,
                                "fixed_motor": fixed_motor,
                                "recommended_descending": recommended_desc,
                                "relay_voltage": relay_payload,
                                "descending_rates": descending_payload,
                            }
                        )
                        continue
                rates, voltage, conductance = backend.step_with_state(
                    {},
                    num_steps=current_steps,
                    direct_current_by_id=chunk_input,
                )
                elapsed_ms += float(current_steps * backend.dt_ms)
                fixed_motor = _aggregate_fixed_motor(rates)
                recommended_desc = _aggregate_recommended_descending_bias(rates, descending_groups, recommended_descending)
                relay_payload = _aggregate_named_groups(voltage, relay_groups)
                descending_payload = _aggregate_named_groups(rates, descending_groups)
                condition_timeseries.append(
                    {
                        "time_ms": elapsed_ms,
                        "fixed_motor": fixed_motor,
                        "recommended_descending": recommended_desc,
                        "relay_voltage": relay_payload,
                        "descending_rates": descending_payload,
                    }
                )
            schedule_results[schedule_key]["timeseries"][condition_name] = condition_timeseries

        left_series = schedule_results[schedule_key]["timeseries"]["body_left_dark"]
        right_series = schedule_results[schedule_key]["timeseries"]["body_right_dark"]
        if len(left_series) != len(right_series):
            raise RuntimeError("left/right timeseries lengths do not match")

        checkpoints: list[dict[str, object]] = []
        for left_snapshot, right_snapshot in zip(left_series, right_series):
            time_ms = float(left_snapshot["time_ms"])
            fixed_motor = {
                "left_condition_turn_bias": float(left_snapshot["fixed_motor"]["turn_bias"]),
                "right_condition_turn_bias": float(right_snapshot["fixed_motor"]["turn_bias"]),
                "contrastive_turn_bias": float(right_snapshot["fixed_motor"]["turn_bias"] - left_snapshot["fixed_motor"]["turn_bias"]),
            }
            descending_turn = {
                "left_condition_turn_bias": float(left_snapshot["recommended_descending"]["turn_bias"]),
                "right_condition_turn_bias": float(right_snapshot["recommended_descending"]["turn_bias"]),
                "contrastive_turn_bias": float(right_snapshot["recommended_descending"]["turn_bias"] - left_snapshot["recommended_descending"]["turn_bias"]),
            }
            relay_contrastive = _snapshot_contrastive(left_snapshot["relay_voltage"], right_snapshot["relay_voltage"])
            descending_contrastive = _snapshot_contrastive(left_snapshot["descending_rates"], right_snapshot["descending_rates"])
            checkpoints.append(
                {
                    "time_ms": time_ms,
                    "fixed_motor": fixed_motor,
                    "recommended_descending": descending_turn,
                    "relay_voltage_contrastive": relay_contrastive,
                    "descending_rate_contrastive": descending_contrastive,
                }
            )
            for family_name, family_payload in (
                ("relay_voltage", relay_contrastive),
                ("descending_rate", descending_contrastive),
            ):
                for label, payload in family_payload.items():
                    csv_rows.append(
                        {
                            "schedule": schedule_key,
                            "time_ms": time_ms,
                            "family": family_name,
                            "label": label,
                            "left_condition_right_minus_left": payload["left_condition_right_minus_left"],
                            "right_condition_right_minus_left": payload["right_condition_right_minus_left"],
                            "contrastive_right_minus_left": payload["contrastive_right_minus_left"],
                            "fixed_turn_bias_left": fixed_motor["left_condition_turn_bias"],
                            "fixed_turn_bias_right": fixed_motor["right_condition_turn_bias"],
                            "recommended_turn_bias_left": descending_turn["left_condition_turn_bias"],
                            "recommended_turn_bias_right": descending_turn["right_condition_turn_bias"],
                        }
                    )
            csv_rows.append(
                {
                    "schedule": schedule_key,
                    "time_ms": time_ms,
                    "family": "fixed_motor",
                    "label": "turn_bias",
                    "left_condition_right_minus_left": fixed_motor["left_condition_turn_bias"],
                    "right_condition_right_minus_left": fixed_motor["right_condition_turn_bias"],
                    "contrastive_right_minus_left": fixed_motor["contrastive_turn_bias"],
                    "fixed_turn_bias_left": fixed_motor["left_condition_turn_bias"],
                    "fixed_turn_bias_right": fixed_motor["right_condition_turn_bias"],
                    "recommended_turn_bias_left": descending_turn["left_condition_turn_bias"],
                    "recommended_turn_bias_right": descending_turn["right_condition_turn_bias"],
                }
            )
            csv_rows.append(
                {
                    "schedule": schedule_key,
                    "time_ms": time_ms,
                    "family": "recommended_descending",
                    "label": "turn_bias",
                    "left_condition_right_minus_left": descending_turn["left_condition_turn_bias"],
                    "right_condition_right_minus_left": descending_turn["right_condition_turn_bias"],
                    "contrastive_right_minus_left": descending_turn["contrastive_turn_bias"],
                    "fixed_turn_bias_left": fixed_motor["left_condition_turn_bias"],
                    "fixed_turn_bias_right": fixed_motor["right_condition_turn_bias"],
                    "recommended_turn_bias_left": descending_turn["left_condition_turn_bias"],
                    "recommended_turn_bias_right": descending_turn["right_condition_turn_bias"],
                }
            )
        schedule_results[schedule_key]["checkpoint_summary"] = checkpoints

    def find_checkpoint(schedule_key: str, target_ms: float) -> dict[str, object]:
        checkpoints = list(schedule_results[schedule_key]["checkpoint_summary"])
        return min(checkpoints, key=lambda row: abs(float(row["time_ms"]) - float(target_ms)))

    high_level = {}
    for schedule_key in schedule_results:
        checkpoint_100 = find_checkpoint(schedule_key, 100.0)
        checkpoint_500 = find_checkpoint(schedule_key, 500.0)
        relay_100 = checkpoint_100["relay_voltage_contrastive"]
        relay_500 = checkpoint_500["relay_voltage_contrastive"]
        descending_100 = checkpoint_100["descending_rate_contrastive"]
        descending_500 = checkpoint_500["descending_rate_contrastive"]
        high_level[schedule_key] = {
            "fixed_motor_100ms": checkpoint_100["fixed_motor"],
            "fixed_motor_500ms": checkpoint_500["fixed_motor"],
            "recommended_descending_100ms": checkpoint_100["recommended_descending"],
            "recommended_descending_500ms": checkpoint_500["recommended_descending"],
            "relay_groups_100ms": relay_100,
            "relay_groups_500ms": relay_500,
            "descending_groups_100ms": descending_100,
            "descending_groups_500ms": descending_500,
            "mean_relay_contrastive_100ms": float(np.mean([payload["contrastive_right_minus_left"] for payload in relay_100.values()])) if relay_100 else 0.0,
            "mean_relay_contrastive_500ms": float(np.mean([payload["contrastive_right_minus_left"] for payload in relay_500.values()])) if relay_500 else 0.0,
            "mean_descending_contrastive_100ms": float(np.mean([payload["contrastive_right_minus_left"] for payload in descending_100.values()])) if descending_100 else 0.0,
            "mean_descending_contrastive_500ms": float(np.mean([payload["contrastive_right_minus_left"] for payload in descending_500.values()])) if descending_500 else 0.0,
        }

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "schedule",
                "time_ms",
                "family",
                "label",
                "left_condition_right_minus_left",
                "right_condition_right_minus_left",
                "contrastive_right_minus_left",
                "fixed_turn_bias_left",
                "fixed_turn_bias_right",
                "recommended_turn_bias_left",
                "recommended_turn_bias_right",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    summary = {
        "annotation_path": args.annotation_path,
        "cell_type_transform_json": args.cell_type_transform_json,
        "relay_candidates_json": args.relay_candidates_json,
        "descending_candidates_json": args.descending_candidates_json,
        "descending_recommended_json": args.descending_recommended_json,
        "value_scale": value_scale,
        "chunk_ms": float(args.chunk_ms),
        "total_ms": float(args.total_ms),
        "input_pulse_ms_values": [None if value is None else float(value) for value in pulse_values],
        "high_level": high_level,
        "schedule_results": schedule_results,
        "notes": [
            "This is a body-free time-resolved audit of the splice drift.",
            "The relay family is measured in voltage space because voltage preserved inhibitory/asymmetric structure more honestly than spike-rate summaries in earlier probes.",
            "The fixed motor family uses the original tiny DN readout set from `MOTOR_READOUT_IDS`.",
            "The recommended descending family uses the broader strict descending/efferent candidate labels selected later for the embodied descending-only branch.",
        ],
    }
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["high_level"], indent=2))


if __name__ == "__main__":
    main()

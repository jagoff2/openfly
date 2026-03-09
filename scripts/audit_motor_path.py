from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from brain.public_ids import JON_IDS, LC4_IDS, MOTOR_READOUT_IDS, collapse_sensor_pool_rates
from brain.pytorch_backend import WholeBrainTorchBackend


def _choose_device(device: str) -> str:
    if device != "auto":
        return device
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def _monitored_group_positions(monitored_ids: list[int]) -> dict[str, list[int]]:
    monitored_positions = {neuron_id: index for index, neuron_id in enumerate(monitored_ids)}
    return {
        group_name: [monitored_positions[neuron_id] for neuron_id in neuron_ids if neuron_id in monitored_positions]
        for group_name, neuron_ids in MOTOR_READOUT_IDS.items()
    }


def _summarize_group_rates(monitored_ids: list[int], firing_rates_hz: list[float]) -> dict[str, float]:
    rate_by_id = {neuron_id: float(rate) for neuron_id, rate in zip(monitored_ids, firing_rates_hz)}
    group_rates = {}
    for group_name, neuron_ids in MOTOR_READOUT_IDS.items():
        values = [rate_by_id.get(neuron_id, 0.0) for neuron_id in neuron_ids]
        group_rates[group_name] = float(sum(values) / len(values)) if values else 0.0
    return group_rates


def _extract_observed_input_stats(log_path: Path) -> dict[str, float]:
    rows = [json.loads(line) for line in log_path.open("r", encoding="utf-8")]
    public_input_rows = [row["public_input_rates"] for row in rows if "public_input_rates" in row]
    if not public_input_rows:
        public_input_rows = [collapse_sensor_pool_rates(row["sensor_pool_rates"]) for row in rows]
    vision_values = [row["vision_bilateral"] for row in public_input_rows]
    mech_values = [row["mech_bilateral"] for row in public_input_rows]
    return {
        "num_cycles": len(public_input_rows),
        "vision_bilateral_min_hz": float(min(vision_values)),
        "vision_bilateral_mean_hz": float(sum(vision_values) / len(vision_values)),
        "vision_bilateral_max_hz": float(max(vision_values)),
        "mech_bilateral_min_hz": float(min(mech_values)),
        "mech_bilateral_mean_hz": float(sum(mech_values) / len(mech_values)),
        "mech_bilateral_max_hz": float(max(mech_values)),
    }


def _set_public_pool_rates(backend: WholeBrainTorchBackend, sensor_pool_rates: dict[str, float]) -> dict[str, float]:
    backend.rates.zero_()
    public_input_rates = collapse_sensor_pool_rates(sensor_pool_rates)
    for pool_name, rate_hz in public_input_rates.items():
        indices = backend.sensor_pool_indices.get(pool_name, [])
        if indices:
            backend.rates[:, indices] = float(rate_hz)
    return public_input_rates


def _set_direct_neuron_rates(backend: WholeBrainTorchBackend, neuron_rates_hz: dict[int, float]) -> None:
    backend.rates.zero_()
    for neuron_id, rate_hz in neuron_rates_hz.items():
        backend.rates[:, backend.flyid_to_index[int(neuron_id)]] = float(rate_hz)


def _run_constant_input_case(
    backend: WholeBrainTorchBackend,
    *,
    label: str,
    duration_ms: float,
    sensor_pool_rates: dict[str, float] | None = None,
    direct_neuron_rates_hz: dict[int, float] | None = None,
    seed: int = 123,
) -> dict[str, object]:
    steps = max(1, int(round(duration_ms / backend.dt_ms)))
    backend.reset(seed=seed)

    if sensor_pool_rates is not None:
        applied_rates = _set_public_pool_rates(backend, sensor_pool_rates)
        applied_kind = "public_pool_rates"
    elif direct_neuron_rates_hz is not None:
        _set_direct_neuron_rates(backend, direct_neuron_rates_hz)
        applied_rates = {str(neuron_id): float(rate_hz) for neuron_id, rate_hz in direct_neuron_rates_hz.items()}
        applied_kind = "direct_neuron_rates_hz"
    else:
        raise ValueError("Either sensor_pool_rates or direct_neuron_rates_hz must be provided.")

    group_positions = _monitored_group_positions(backend.monitored_ids)
    spike_counts = torch.zeros(len(backend.monitored_ids), device=backend.device)
    first_spike_ms = {group_name: None for group_name in MOTOR_READOUT_IDS}

    for step_index in range(steps):
        backend.conductance, backend.delay_buffer, backend.spikes, backend.v, backend.refrac = backend.model(
            backend.rates,
            backend.conductance,
            backend.delay_buffer,
            backend.spikes,
            backend.v,
            backend.refrac,
        )
        monitored_spikes = backend.spikes[0, backend.monitored_indices]
        spike_counts += monitored_spikes
        current_time_ms = (step_index + 1) * backend.dt_ms
        for group_name, positions in group_positions.items():
            if first_spike_ms[group_name] is not None or not positions:
                continue
            if bool(torch.any(monitored_spikes[positions] > 0).item()):
                first_spike_ms[group_name] = float(current_time_ms)

    window_seconds = steps * (backend.dt_ms / 1000.0)
    firing_rates_hz = (spike_counts / window_seconds).detach().cpu().tolist()
    group_rates_hz = _summarize_group_rates(backend.monitored_ids, firing_rates_hz)
    raw_rates_hz = {str(neuron_id): float(rate) for neuron_id, rate in zip(backend.monitored_ids, firing_rates_hz)}

    return {
        "label": label,
        "duration_ms": float(duration_ms),
        "input_kind": applied_kind,
        "applied_rates": applied_rates,
        "group_rates_hz": group_rates_hz,
        "raw_rates_hz": raw_rates_hz,
        "first_spike_ms": first_spike_ms,
    }


def _connectivity_summary(
    completeness_path: Path,
    connectivity_path: Path,
    *,
    max_hops: int = 2,
) -> dict[str, object]:
    completeness = pd.read_csv(completeness_path, index_col=0)
    flyid_to_index = {int(flywire_id): index for index, flywire_id in enumerate(completeness.index)}
    connectivity = pd.read_parquet(
        connectivity_path,
        columns=["Presynaptic_Index", "Postsynaptic_Index", "Excitatory x Connectivity"],
    )

    input_sets = {
        "vision_bilateral": {flyid_to_index[int(neuron_id)] for neuron_id in LC4_IDS if int(neuron_id) in flyid_to_index},
        "mech_bilateral": {flyid_to_index[int(neuron_id)] for neuron_id in JON_IDS if int(neuron_id) in flyid_to_index},
    }
    output_sets = {
        group_name: {flyid_to_index[int(neuron_id)] for neuron_id in neuron_ids if int(neuron_id) in flyid_to_index}
        for group_name, neuron_ids in MOTOR_READOUT_IDS.items()
    }

    summary: dict[str, object] = {}
    for input_name, input_indices in input_sets.items():
        direct_subset = connectivity[connectivity["Presynaptic_Index"].isin(input_indices)]
        direct_edges = {}
        hop_summary: list[dict[str, object]] = []
        for group_name, output_indices in output_sets.items():
            matches = direct_subset[direct_subset["Postsynaptic_Index"].isin(output_indices)]
            direct_edges[group_name] = {
                "edge_count": int(len(matches)),
                "weight_sum": float(matches["Excitatory x Connectivity"].sum()) if len(matches) else 0.0,
            }

        frontier = set(input_indices)
        seen = set(frontier)
        for hop in range(1, max_hops + 1):
            subset = connectivity[connectivity["Presynaptic_Index"].isin(frontier)]
            frontier = set(subset["Postsynaptic_Index"].tolist()) - seen
            seen |= frontier
            hop_summary.append(
                {
                    "hop": hop,
                    "frontier_size": int(len(frontier)),
                    "cumulative_seen_size": int(len(seen)),
                    "new_hits_by_group": {group_name: int(len(frontier & output_indices)) for group_name, output_indices in output_sets.items()},
                    "cumulative_hits_by_group": {group_name: int(len(seen & output_indices)) for group_name, output_indices in output_sets.items()},
                }
            )
            if not frontier:
                break

        summary[input_name] = {
            "input_neuron_count": int(len(input_indices)),
            "direct_edges_to_motor_groups": direct_edges,
            "hop_reachability": hop_summary,
        }
    return summary


def _write_sweep_csv(output_path: Path, rows: Iterable[dict[str, object]]) -> None:
    fieldnames = [
        "label",
        "duration_ms",
        "input_kind",
        "applied_rates",
        "forward_left_hz",
        "forward_right_hz",
        "turn_left_hz",
        "turn_right_hz",
        "reverse_hz",
        "first_spike_forward_left_ms",
        "first_spike_forward_right_ms",
        "first_spike_turn_left_ms",
        "first_spike_turn_right_ms",
        "first_spike_reverse_ms",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "label": row["label"],
                    "duration_ms": row["duration_ms"],
                    "input_kind": row["input_kind"],
                    "applied_rates": json.dumps(row["applied_rates"], sort_keys=True),
                    "forward_left_hz": row["group_rates_hz"]["forward_left"],
                    "forward_right_hz": row["group_rates_hz"]["forward_right"],
                    "turn_left_hz": row["group_rates_hz"]["turn_left"],
                    "turn_right_hz": row["group_rates_hz"]["turn_right"],
                    "reverse_hz": row["group_rates_hz"]["reverse"],
                    "first_spike_forward_left_ms": row["first_spike_ms"]["forward_left"],
                    "first_spike_forward_right_ms": row["first_spike_ms"]["forward_right"],
                    "first_spike_turn_left_ms": row["first_spike_ms"]["turn_left"],
                    "first_spike_turn_right_ms": row["first_spike_ms"]["turn_right"],
                    "first_spike_reverse_ms": row["first_spike_ms"]["reverse"],
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the public sensory-to-motor path in the strict brain-only backend.")
    parser.add_argument("--device", default="auto", help="Torch device to use for backend sweeps. Default: auto.")
    parser.add_argument(
        "--log-path",
        default="outputs/brain_only_fastvision_test_v2/logs/flygym-demo-20260308-150052.jsonl",
        help="Short strict-production log used to extract the observed bilateral public input rates.",
    )
    parser.add_argument(
        "--json-output",
        default="outputs/metrics/motor_path_audit.json",
        help="Path to the JSON audit artifact.",
    )
    parser.add_argument(
        "--csv-output",
        default="outputs/metrics/motor_path_audit_sweeps.csv",
        help="Path to the CSV sweep artifact.",
    )
    parser.add_argument(
        "--completeness-path",
        default="external/fly-brain/data/2025_Completeness_783.csv",
        help="Path to the public completeness CSV.",
    )
    parser.add_argument(
        "--connectivity-path",
        default="external/fly-brain/data/2025_Connectivity_783.parquet",
        help="Path to the public connectivity parquet.",
    )
    args = parser.parse_args()

    device = _choose_device(args.device)
    log_path = Path(args.log_path)
    json_output = Path(args.json_output)
    csv_output = Path(args.csv_output)
    completeness_path = Path(args.completeness_path)
    connectivity_path = Path(args.connectivity_path)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    csv_output.parent.mkdir(parents=True, exist_ok=True)

    observed_stats = _extract_observed_input_stats(log_path)
    observed_mean_sensor_pool_rates = {
        "vision_left": observed_stats["vision_bilateral_mean_hz"],
        "vision_right": observed_stats["vision_bilateral_mean_hz"],
        "mech_left": observed_stats["mech_bilateral_mean_hz"],
        "mech_right": observed_stats["mech_bilateral_mean_hz"],
    }
    observed_max_sensor_pool_rates = {
        "vision_left": observed_stats["vision_bilateral_max_hz"],
        "vision_right": observed_stats["vision_bilateral_max_hz"],
        "mech_left": observed_stats["mech_bilateral_max_hz"],
        "mech_right": observed_stats["mech_bilateral_max_hz"],
    }

    backend = WholeBrainTorchBackend(
        completeness_path=completeness_path,
        connectivity_path=connectivity_path,
        cache_dir=REPO_ROOT / "outputs" / "cache",
        device=device,
        dt_ms=0.1,
    )

    public_p9_ids = [720575940627652358, 720575940635872101]
    p9_direct_rates = {neuron_id: 100.0 for neuron_id in public_p9_ids}
    p9_with_lc4 = dict(p9_direct_rates)
    p9_with_lc4.update({int(neuron_id): 200.0 for neuron_id in LC4_IDS if int(neuron_id) in backend.flyid_to_index})
    p9_with_jon = dict(p9_direct_rates)
    p9_with_jon.update({int(neuron_id): 300.0 for neuron_id in JON_IDS if int(neuron_id) in backend.flyid_to_index})

    sweep_rows = [
        _run_constant_input_case(
            backend,
            label="strict_observed_mean_20ms",
            duration_ms=20.0,
            sensor_pool_rates=observed_mean_sensor_pool_rates,
        ),
        _run_constant_input_case(
            backend,
            label="strict_observed_mean_100ms",
            duration_ms=100.0,
            sensor_pool_rates=observed_mean_sensor_pool_rates,
        ),
        _run_constant_input_case(
            backend,
            label="strict_observed_mean_1000ms",
            duration_ms=1000.0,
            sensor_pool_rates=observed_mean_sensor_pool_rates,
        ),
        _run_constant_input_case(
            backend,
            label="strict_observed_max_1000ms",
            duration_ms=1000.0,
            sensor_pool_rates=observed_max_sensor_pool_rates,
        ),
        _run_constant_input_case(
            backend,
            label="public_lc4_only_200hz_1000ms",
            duration_ms=1000.0,
            sensor_pool_rates={"vision_left": 200.0, "vision_right": 200.0, "mech_left": 0.0, "mech_right": 0.0},
        ),
        _run_constant_input_case(
            backend,
            label="public_jon_only_300hz_1000ms",
            duration_ms=1000.0,
            sensor_pool_rates={"vision_left": 0.0, "vision_right": 0.0, "mech_left": 300.0, "mech_right": 300.0},
        ),
        _run_constant_input_case(
            backend,
            label="public_lc4_200hz_plus_jon_300hz_1000ms",
            duration_ms=1000.0,
            sensor_pool_rates={"vision_left": 200.0, "vision_right": 200.0, "mech_left": 300.0, "mech_right": 300.0},
        ),
        _run_constant_input_case(
            backend,
            label="public_p9_direct_100hz_1000ms",
            duration_ms=1000.0,
            direct_neuron_rates_hz=p9_direct_rates,
        ),
        _run_constant_input_case(
            backend,
            label="public_p9_direct_100hz_plus_lc4_200hz_1000ms",
            duration_ms=1000.0,
            direct_neuron_rates_hz=p9_with_lc4,
        ),
        _run_constant_input_case(
            backend,
            label="public_p9_direct_100hz_plus_jon_300hz_1000ms",
            duration_ms=1000.0,
            direct_neuron_rates_hz=p9_with_jon,
        ),
    ]

    connectivity_summary = _connectivity_summary(completeness_path, connectivity_path, max_hops=2)

    report = {
        "device": backend.device,
        "log_path": str(log_path),
        "observed_public_input_stats": observed_stats,
        "sweep_rows": sweep_rows,
        "connectivity_summary": connectivity_summary,
        "notes": [
            "The strict closed-loop production path currently drives the whole-brain backend only through bilateral LC4 and bilateral JON public anchor pools.",
            "The public notebook examples in external/fly-brain/code/paper-phil-drosophila/example.ipynb use P9 external drive as the explicit forward-walking baseline, then add LC4 or JO co-stimulation on top of that baseline.",
            "Direct P9 stimulation here is used as a positive control to distinguish backend inactivity from input-mapping mismatch.",
        ],
    }

    with json_output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
    _write_sweep_csv(csv_output, sweep_rows)

    print(f"Wrote JSON audit to {json_output}")
    print(f"Wrote CSV sweep summary to {csv_output}")


if __name__ == "__main__":
    main()

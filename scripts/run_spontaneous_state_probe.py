from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from time import perf_counter
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from brain.pytorch_backend import WholeBrainTorchBackend
from runtime.closed_loop import build_brain_backend, load_config as runtime_load_config


def load_config(path: str | Path) -> dict[str, Any]:
    return runtime_load_config(path)


def build_backend(config: dict[str, Any], device: str | None = None) -> WholeBrainTorchBackend:
    config = json.loads(json.dumps(config))
    config.setdefault("brain", {})
    if device is not None:
        config["brain"]["device"] = str(device)
    backend = build_brain_backend("flygym", config)
    if not isinstance(backend, WholeBrainTorchBackend):
        raise TypeError(f"Spontaneous-state probe requires WholeBrainTorchBackend, got {type(backend)!r}")
    return backend


def _window_summary(
    rates_by_id: dict[int, float],
    voltage_by_id: dict[int, float],
    conductance_by_id: dict[int, float],
) -> dict[str, float | int]:
    rate_values = [float(value) for value in rates_by_id.values()]
    voltage_values = [abs(float(value)) for value in voltage_by_id.values()]
    conductance_values = [abs(float(value)) for value in conductance_by_id.values()]
    active_units = sum(1 for value in rate_values if value > 0.0)
    total_units = len(rate_values)
    return {
        "active_units": active_units,
        "monitored_units": total_units,
        "active_fraction": float(active_units / total_units) if total_units else 0.0,
        "mean_rate_hz": float(sum(rate_values) / total_units) if total_units else 0.0,
        "max_rate_hz": float(max(rate_values)) if rate_values else 0.0,
        "max_abs_voltage_mv": float(max(voltage_values)) if voltage_values else 0.0,
        "max_abs_conductance": float(max(conductance_values)) if conductance_values else 0.0,
    }


def _timed_window(
    backend: WholeBrainTorchBackend,
    num_steps: int,
    *,
    direct_current_by_id: dict[int, float] | None = None,
) -> tuple[dict[int, float], dict[int, float], dict[int, float], dict[str, float], float]:
    wall_start = perf_counter()
    rates_by_id, voltage_by_id, conductance_by_id = backend.step_with_state(
        {},
        num_steps=num_steps,
        direct_current_by_id=direct_current_by_id,
    )
    wall_seconds = perf_counter() - wall_start
    return rates_by_id, voltage_by_id, conductance_by_id, backend.state_summary(), wall_seconds


def run_spontaneous_state_probe(
    *,
    config_path: str | Path,
    device: str = "cpu",
    seed: int = 0,
    baseline_steps: int = 200,
    perturb_steps: int = 10,
    response_steps: int = 20,
    recovery_steps: int = 50,
    perturb_current: float = 50.0,
    perturb_target_id: int | None = None,
    max_rate_threshold_hz: float = 1000.0,
    max_abs_voltage_threshold_mv: float = 200.0,
    max_abs_conductance_threshold: float = 1000.0,
) -> dict[str, Any]:
    config = load_config(config_path)
    backend = build_backend(config, device=device)
    target_id = int(perturb_target_id or backend.monitored_ids[0])
    dt_seconds = float(backend.dt_ms / 1000.0)

    backend.reset(seed=seed)
    baseline_rates, baseline_voltage, baseline_conductance, baseline_state, baseline_wall = _timed_window(
        backend,
        baseline_steps,
    )

    backend.reset(seed=seed)
    _, _, _, _, perturb_wall = _timed_window(
        backend,
        perturb_steps,
        direct_current_by_id={target_id: float(perturb_current)},
    )
    response_rates, response_voltage, response_conductance, response_state, response_wall = _timed_window(
        backend,
        response_steps,
    )
    recovery_rates, recovery_voltage, recovery_conductance, recovery_state, recovery_wall = _timed_window(
        backend,
        recovery_steps,
    )

    baseline = _window_summary(baseline_rates, baseline_voltage, baseline_conductance)
    response = _window_summary(response_rates, response_voltage, response_conductance)
    recovery = _window_summary(recovery_rates, recovery_voltage, recovery_conductance)
    baseline.update({f"state_{key}": float(value) for key, value in baseline_state.items()})
    response.update({f"state_{key}": float(value) for key, value in response_state.items()})
    recovery.update({f"state_{key}": float(value) for key, value in recovery_state.items()})

    monitored_ids = [int(neuron_id) for neuron_id in backend.monitored_ids]
    response_delta_by_id = {
        neuron_id: float(response_rates.get(neuron_id, 0.0) - baseline_rates.get(neuron_id, 0.0))
        for neuron_id in monitored_ids
    }
    recovery_delta_by_id = {
        neuron_id: float(recovery_rates.get(neuron_id, 0.0) - baseline_rates.get(neuron_id, 0.0))
        for neuron_id in monitored_ids
    }
    delta_abs = [abs(delta) for delta in response_delta_by_id.values()]
    max_abs_rate = max(
        float(baseline["max_rate_hz"]),
        float(response["max_rate_hz"]),
        float(recovery["max_rate_hz"]),
    )
    max_abs_voltage = max(
        float(baseline["max_abs_voltage_mv"]),
        float(response["max_abs_voltage_mv"]),
        float(recovery["max_abs_voltage_mv"]),
    )
    max_abs_conductance = max(
        float(baseline["max_abs_conductance"]),
        float(response["max_abs_conductance"]),
        float(recovery["max_abs_conductance"]),
    )
    total_wall_seconds = baseline_wall + perturb_wall + response_wall + recovery_wall
    total_sim_seconds = float((baseline_steps + perturb_steps + response_steps + recovery_steps) * dt_seconds)

    return {
        "config": str(config_path),
        "device": str(backend.device_name),
        "dt_ms": float(backend.dt_ms),
        "seed": int(seed),
        "perturb_target_id": target_id,
        "perturb_current": float(perturb_current),
        "baseline_steps": int(baseline_steps),
        "perturb_steps": int(perturb_steps),
        "response_steps": int(response_steps),
        "recovery_steps": int(recovery_steps),
        "baseline": baseline,
        "response": response,
        "recovery": recovery,
        "delta_l1_hz": float(sum(delta_abs)),
        "delta_linf_hz": float(max(delta_abs) if delta_abs else 0.0),
        "changed_units": int(sum(1 for delta in delta_abs if delta > 1e-6)),
        "max_abs_rate_hz": max_abs_rate,
        "max_abs_voltage_mv": max_abs_voltage,
        "max_abs_conductance": max_abs_conductance,
        "spontaneous_activity_present": bool(
            int(baseline["active_units"]) > 0
            or float(baseline.get("state_global_spike_fraction", 0.0)) > 0.0
            or float(baseline.get("state_background_mean_rate_hz", 0.0)) > 0.0
        ),
        "activity_bounded": bool(
            max_abs_rate <= max_rate_threshold_hz
            and max_abs_voltage <= max_abs_voltage_threshold_mv
            and max_abs_conductance <= max_abs_conductance_threshold
        ),
        "perturbation_detected": bool(any(delta > 1e-6 for delta in delta_abs)),
        "wall_seconds": {
            "baseline": float(baseline_wall),
            "perturb": float(perturb_wall),
            "response": float(response_wall),
            "recovery": float(recovery_wall),
            "total": float(total_wall_seconds),
        },
        "sim_seconds": {
            "baseline": float(baseline_steps * dt_seconds),
            "perturb": float(perturb_steps * dt_seconds),
            "response": float(response_steps * dt_seconds),
            "recovery": float(recovery_steps * dt_seconds),
            "total": float(total_sim_seconds),
        },
        "real_time_factor": {
            "baseline": float((baseline_steps * dt_seconds) / baseline_wall) if baseline_wall else float("inf"),
            "perturb": float((perturb_steps * dt_seconds) / perturb_wall) if perturb_wall else float("inf"),
            "response": float((response_steps * dt_seconds) / response_wall) if response_wall else float("inf"),
            "recovery": float((recovery_steps * dt_seconds) / recovery_wall) if recovery_wall else float("inf"),
            "total": float(total_sim_seconds / total_wall_seconds) if total_wall_seconds else float("inf"),
        },
        "per_neuron": [
            {
                "neuron_id": neuron_id,
                "baseline_rate_hz": float(baseline_rates.get(neuron_id, 0.0)),
                "response_rate_hz": float(response_rates.get(neuron_id, 0.0)),
                "recovery_rate_hz": float(recovery_rates.get(neuron_id, 0.0)),
                "delta_response_vs_baseline_hz": float(response_delta_by_id[neuron_id]),
                "delta_recovery_vs_baseline_hz": float(recovery_delta_by_id[neuron_id]),
            }
            for neuron_id in monitored_ids
        ],
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe cold-start spontaneous state and pulse response for the brain-only torch backend.")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--baseline-steps", type=int, default=200)
    parser.add_argument("--perturb-steps", type=int, default=10)
    parser.add_argument("--response-steps", type=int, default=20)
    parser.add_argument("--recovery-steps", type=int, default=50)
    parser.add_argument("--perturb-current", type=float, default=50.0)
    parser.add_argument("--perturb-target-id", type=int, default=None)
    parser.add_argument("--max-rate-threshold-hz", type=float, default=1000.0)
    parser.add_argument("--max-abs-voltage-threshold-mv", type=float, default=200.0)
    parser.add_argument("--max-abs-conductance-threshold", type=float, default=1000.0)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-csv", type=Path, default=None)
    args = parser.parse_args()

    summary = run_spontaneous_state_probe(
        config_path=args.config,
        device=args.device,
        seed=args.seed,
        baseline_steps=args.baseline_steps,
        perturb_steps=args.perturb_steps,
        response_steps=args.response_steps,
        recovery_steps=args.recovery_steps,
        perturb_current=args.perturb_current,
        perturb_target_id=args.perturb_target_id,
        max_rate_threshold_hz=args.max_rate_threshold_hz,
        max_abs_voltage_threshold_mv=args.max_abs_voltage_threshold_mv,
        max_abs_conductance_threshold=args.max_abs_conductance_threshold,
    )

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if args.output_csv is not None:
        _write_csv(args.output_csv, summary["per_neuron"])

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

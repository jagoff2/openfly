from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import numpy as np

from brain.paper_task_ids import PaperTaskSpec


@dataclass(frozen=True)
class PaperTaskProbeRow:
    task: str
    input_group: str
    frequency_hz: float
    duration_ms: float
    output_rates_hz: dict[str, float]
    output_voltages: dict[str, float]
    output_conductances: dict[str, float]

    def to_flat_dict(self) -> dict[str, float | str]:
        row: dict[str, float | str] = {
            "task": self.task,
            "input_group": self.input_group,
            "frequency_hz": self.frequency_hz,
            "duration_ms": self.duration_ms,
        }
        for key, value in self.output_rates_hz.items():
            row[f"{key}_hz"] = value
        for key, value in self.output_voltages.items():
            row[f"{key}_voltage"] = value
        for key, value in self.output_conductances.items():
            row[f"{key}_conductance"] = value
        return row


def output_group_means(rate_by_id: Mapping[int, float], output_groups: Mapping[str, tuple[int, ...]]) -> dict[str, float]:
    summary = {}
    for group_name, neuron_ids in output_groups.items():
        values = [float(rate_by_id.get(int(neuron_id), 0.0)) for neuron_id in neuron_ids]
        summary[group_name] = float(np.mean(values)) if values else 0.0
    return summary


def run_probe_sweep(
    backend: Any,
    spec: PaperTaskSpec,
    *,
    duration_ms: float | None = None,
    frequencies_hz: Iterable[float] | None = None,
    seed: int = 0,
) -> list[PaperTaskProbeRow]:
    duration_ms = float(duration_ms if duration_ms is not None else spec.default_duration_ms)
    frequencies_hz = tuple(float(value) for value in (frequencies_hz or spec.frequencies_hz))
    monitored_ids = sorted({int(neuron_id) for ids in spec.output_groups.values() for neuron_id in ids})
    if hasattr(backend, "set_monitored_ids"):
        backend.set_monitored_ids(monitored_ids)
    num_steps = max(1, int(round(duration_ms / float(getattr(backend, "dt_ms", 0.1)))))
    rows: list[PaperTaskProbeRow] = []
    for group_name, input_ids in spec.input_groups.items():
        for frequency_hz in frequencies_hz:
            backend.reset(seed=seed)
            direct_rates = {int(neuron_id): float(frequency_hz) for neuron_id in input_ids}
            if hasattr(backend, "step_with_state"):
                rates, voltages, conductances = backend.step_with_state(
                    {},
                    num_steps=num_steps,
                    direct_input_rates_hz=direct_rates,
                )
            else:
                rates = backend.step({}, num_steps=num_steps, direct_input_rates_hz=direct_rates)
                voltages = {}
                conductances = {}
            rows.append(
                PaperTaskProbeRow(
                    task=spec.name,
                    input_group=group_name,
                    frequency_hz=float(frequency_hz),
                    duration_ms=float(duration_ms),
                    output_rates_hz=output_group_means(rates, spec.output_groups),
                    output_voltages=output_group_means(voltages, spec.output_groups) if voltages else {},
                    output_conductances=output_group_means(conductances, spec.output_groups) if conductances else {},
                )
            )
    return rows

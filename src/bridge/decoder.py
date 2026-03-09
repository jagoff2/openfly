from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from body.interfaces import BodyCommand
from brain.public_ids import MOTOR_READOUT_IDS


def _load_population_groups(path: str | None) -> dict[str, list[int]]:
    if not path:
        return {}
    json_path = Path(path)
    if not json_path.exists():
        return {}
    data = json.loads(json_path.read_text(encoding="utf-8"))
    groups: dict[str, list[int]] = {}
    for item in data.get("selected_paired_cell_types", []):
        label = str(item.get("cell_type") or item.get("candidate_label") or "").strip()
        if not label:
            continue
        groups[f"{label}_left"] = [int(root_id) for root_id in item.get("left_root_ids", [])]
        groups[f"{label}_right"] = [int(root_id) for root_id in item.get("right_root_ids", [])]
    return groups


@dataclass
class DecoderConfig:
    idle_drive: float = 0.0
    min_drive: float = 0.0
    max_drive: float = 1.2
    forward_scale_hz: float = 120.0
    turn_scale_hz: float = 80.0
    reverse_scale_hz: float = 100.0
    forward_gain: float = 0.4
    turn_gain: float = 0.3
    reverse_threshold: float = 0.65
    forward_asymmetry_scale_hz: float = 40.0
    forward_asymmetry_turn_gain: float = 0.0
    signal_smoothing_alpha: float = 1.0
    population_candidates_json: str | None = None
    population_forward_cell_types: tuple[str, ...] = ()
    population_turn_cell_types: tuple[str, ...] = ()
    population_forward_scale_hz: float = 80.0
    population_turn_scale_hz: float = 20.0
    population_forward_weight: float = 0.0
    population_turn_weight: float = 0.0

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any] | None) -> "DecoderConfig":
        mapping = mapping or {}
        return cls(
            idle_drive=float(mapping.get("idle_drive", 0.0)),
            min_drive=float(mapping.get("min_drive", 0.0)),
            max_drive=float(mapping.get("max_drive", 1.2)),
            forward_scale_hz=float(mapping.get("forward_scale_hz", 120.0)),
            turn_scale_hz=float(mapping.get("turn_scale_hz", 80.0)),
            reverse_scale_hz=float(mapping.get("reverse_scale_hz", 100.0)),
            forward_gain=float(mapping.get("forward_gain", 0.4)),
            turn_gain=float(mapping.get("turn_gain", 0.3)),
            reverse_threshold=float(mapping.get("reverse_threshold", 0.65)),
            forward_asymmetry_scale_hz=float(mapping.get("forward_asymmetry_scale_hz", 40.0)),
            forward_asymmetry_turn_gain=float(mapping.get("forward_asymmetry_turn_gain", 0.0)),
            signal_smoothing_alpha=float(mapping.get("signal_smoothing_alpha", 1.0)),
            population_candidates_json=None
            if mapping.get("population_candidates_json", mapping.get("relay_candidates_json")) is None
            else str(mapping.get("population_candidates_json", mapping.get("relay_candidates_json"))),
            population_forward_cell_types=tuple(
                str(value) for value in mapping.get("population_forward_cell_types", mapping.get("relay_forward_cell_types", []))
            ),
            population_turn_cell_types=tuple(
                str(value) for value in mapping.get("population_turn_cell_types", mapping.get("relay_turn_cell_types", []))
            ),
            population_forward_scale_hz=float(mapping.get("population_forward_scale_hz", mapping.get("relay_forward_scale_hz", 80.0))),
            population_turn_scale_hz=float(mapping.get("population_turn_scale_hz", mapping.get("relay_turn_scale_hz", 20.0))),
            population_forward_weight=float(mapping.get("population_forward_weight", mapping.get("relay_forward_weight", 0.0))),
            population_turn_weight=float(mapping.get("population_turn_weight", mapping.get("relay_turn_weight", 0.0))),
        )

@dataclass
class MotorReadout:
    command: BodyCommand
    forward_signal: float
    turn_signal: float
    reverse_signal: float
    neuron_rates: dict[str, float]

class MotorDecoder:
    def __init__(self, config: DecoderConfig | None = None) -> None:
        self.config = config or DecoderConfig()
        self.population_groups = _load_population_groups(self.config.population_candidates_json)
        self.reset()

    def reset(self) -> None:
        self._forward_state = 0.0
        self._turn_state = 0.0
        self._reverse_state = 0.0

    def required_neuron_ids(self) -> list[int]:
        ids = {neuron_id for group in MOTOR_READOUT_IDS.values() for neuron_id in group}
        for root_ids in self.population_groups.values():
            ids.update(int(root_id) for root_id in root_ids)
        return sorted(ids)

    def _mean_group_ids(self, rates: Mapping[int, float], ids: list[int]) -> float:
        values = [float(rates.get(neuron_id, 0.0)) for neuron_id in ids]
        return float(np.mean(values)) if values else 0.0

    def _mean_group(self, rates: Mapping[int, float], group_name: str) -> float:
        return self._mean_group_ids(rates, MOTOR_READOUT_IDS[group_name])

    def _mean_population_side(self, rates: Mapping[int, float], cell_types: tuple[str, ...], side: str) -> float:
        if not cell_types:
            return 0.0
        values = []
        for cell_type in cell_types:
            ids = self.population_groups.get(f"{cell_type}_{side}", [])
            if ids:
                values.append(self._mean_group_ids(rates, ids))
        return float(np.mean(values)) if values else 0.0

    def decode(self, rates: Mapping[int, float]) -> MotorReadout:
        cfg = self.config
        forward_left = self._mean_group(rates, "forward_left")
        forward_right = self._mean_group(rates, "forward_right")
        turn_left = self._mean_group(rates, "turn_left")
        turn_right = self._mean_group(rates, "turn_right")
        reverse = self._mean_group(rates, "reverse")
        population_forward_left = self._mean_population_side(rates, cfg.population_forward_cell_types, "left")
        population_forward_right = self._mean_population_side(rates, cfg.population_forward_cell_types, "right")
        population_turn_left = self._mean_population_side(rates, cfg.population_turn_cell_types, "left")
        population_turn_right = self._mean_population_side(rates, cfg.population_turn_cell_types, "right")
        dn_forward_signal = np.tanh(((forward_left + forward_right) * 0.5) / cfg.forward_scale_hz)
        population_forward_signal = np.tanh(((population_forward_left + population_forward_right) * 0.5) / max(cfg.population_forward_scale_hz, 1e-6))
        forward_signal = np.clip(dn_forward_signal + cfg.population_forward_weight * population_forward_signal, -1.0, 1.0)
        dn_turn_signal = np.tanh((turn_right - turn_left) / cfg.turn_scale_hz)
        population_turn_signal = np.tanh((population_turn_right - population_turn_left) / max(cfg.population_turn_scale_hz, 1e-6))
        turn_signal = np.clip(dn_turn_signal + cfg.population_turn_weight * population_turn_signal, -1.0, 1.0)
        if cfg.forward_asymmetry_turn_gain != 0.0 and cfg.forward_asymmetry_scale_hz > 0.0:
            forward_asymmetry_signal = np.tanh((forward_right - forward_left) / cfg.forward_asymmetry_scale_hz)
            turn_signal = float(np.clip(turn_signal + cfg.forward_asymmetry_turn_gain * forward_asymmetry_signal, -1.0, 1.0))
        reverse_signal = np.tanh(reverse / cfg.reverse_scale_hz)
        alpha = float(np.clip(cfg.signal_smoothing_alpha, 0.0, 1.0))
        self._forward_state = (1.0 - alpha) * self._forward_state + alpha * float(forward_signal)
        self._turn_state = (1.0 - alpha) * self._turn_state + alpha * float(turn_signal)
        self._reverse_state = (1.0 - alpha) * self._reverse_state + alpha * float(reverse_signal)
        base_drive = cfg.idle_drive + cfg.forward_gain * max(0.0, self._forward_state)
        left_drive = base_drive - cfg.turn_gain * self._turn_state
        right_drive = base_drive + cfg.turn_gain * self._turn_state
        if self._reverse_state > cfg.reverse_threshold:
            left_drive = -abs(left_drive)
            right_drive = -abs(right_drive)
        left_drive = float(np.clip(left_drive, -cfg.max_drive, cfg.max_drive))
        right_drive = float(np.clip(right_drive, -cfg.max_drive, cfg.max_drive))
        if left_drive >= 0:
            left_drive = max(cfg.min_drive, left_drive)
        if right_drive >= 0:
            right_drive = max(cfg.min_drive, right_drive)
        command = BodyCommand(left_drive=left_drive, right_drive=right_drive)
        return MotorReadout(
            command=command,
            forward_signal=float(forward_signal),
            turn_signal=float(turn_signal),
            reverse_signal=float(reverse_signal),
            neuron_rates={
                "forward_left_hz": forward_left,
                "forward_right_hz": forward_right,
                "turn_left_hz": turn_left,
                "turn_right_hz": turn_right,
                "reverse_hz": reverse,
                "population_forward_left_hz": population_forward_left,
                "population_forward_right_hz": population_forward_right,
                "population_turn_left_hz": population_turn_left,
                "population_turn_right_hz": population_turn_right,
                "dn_forward_signal": float(dn_forward_signal),
                "population_forward_signal": float(population_forward_signal),
                "dn_turn_signal": float(dn_turn_signal),
                "population_turn_signal": float(population_turn_signal),
            },
        )

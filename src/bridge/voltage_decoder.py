from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from body.interfaces import BodyCommand
from bridge.decoder import MotorReadout


@dataclass(frozen=True)
class VoltageTurnGroup:
    label: str
    left_root_ids: tuple[int, ...]
    right_root_ids: tuple[int, ...]
    turn_weight: float
    super_class: str = "unknown"
    baseline_asymmetry_mv: float = 0.0


@dataclass
class VoltageTurnDecoderConfig:
    signal_library_json: str
    idle_drive: float = 0.0
    min_drive: float = 0.0
    max_drive: float = 1.2
    turn_gain: float = 0.65
    turn_scale_mv: float = 5.0
    signal_smoothing_alpha: float = 1.0

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any] | None) -> "VoltageTurnDecoderConfig":
        mapping = dict(mapping or {})
        return cls(
            signal_library_json=str(mapping.get("signal_library_json", "")),
            idle_drive=float(mapping.get("idle_drive", 0.0)),
            min_drive=float(mapping.get("min_drive", 0.0)),
            max_drive=float(mapping.get("max_drive", 1.2)),
            turn_gain=float(mapping.get("turn_gain", 0.65)),
            turn_scale_mv=float(mapping.get("turn_scale_mv", 5.0)),
            signal_smoothing_alpha=float(mapping.get("signal_smoothing_alpha", 1.0)),
        )


class VoltageTurnDecoder:
    def __init__(self, config: VoltageTurnDecoderConfig) -> None:
        self.config = config
        self.groups = self._load_signal_groups(config.signal_library_json)
        self.reset()

    def _load_signal_groups(self, path: str) -> list[VoltageTurnGroup]:
        json_path = Path(path)
        if not path or not json_path.exists():
            return []
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        groups: list[VoltageTurnGroup] = []
        for item in payload.get("selected_groups", []):
            groups.append(
                VoltageTurnGroup(
                    label=str(item.get("label", "")).strip(),
                    left_root_ids=tuple(int(root_id) for root_id in item.get("left_root_ids", [])),
                    right_root_ids=tuple(int(root_id) for root_id in item.get("right_root_ids", [])),
                    turn_weight=float(item.get("turn_weight", 0.0)),
                    super_class=str(item.get("super_class", "unknown")),
                    baseline_asymmetry_mv=float(item.get("baseline_asymmetry_mv", 0.0)),
                )
            )
        return [group for group in groups if group.label and (group.left_root_ids or group.right_root_ids)]

    def reset(self) -> None:
        self._turn_state = 0.0

    def required_neuron_ids(self) -> list[int]:
        neuron_ids: set[int] = set()
        for group in self.groups:
            neuron_ids.update(group.left_root_ids)
            neuron_ids.update(group.right_root_ids)
        return sorted(neuron_ids)

    def _coerce_voltage_map(self, monitored_voltage: Mapping[Any, float] | None) -> dict[int, float]:
        values = dict(monitored_voltage or {})
        voltage_map: dict[int, float] = {}
        for key, value in values.items():
            try:
                voltage_map[int(key)] = float(value)
            except (TypeError, ValueError):
                continue
        return voltage_map

    def _mean_voltage(self, voltage_map: Mapping[int, float], root_ids: tuple[int, ...]) -> float:
        values = [float(voltage_map.get(int(root_id), 0.0)) for root_id in root_ids]
        return float(np.mean(values)) if values else 0.0

    def decode_state(
        self,
        rates: Mapping[int, float] | None = None,
        *,
        monitored_voltage: Mapping[Any, float] | None = None,
        monitored_spikes: Mapping[Any, float] | None = None,
    ) -> MotorReadout:
        del rates
        voltage_map = self._coerce_voltage_map(monitored_voltage)
        spike_map = self._coerce_voltage_map(monitored_spikes)
        if not voltage_map and not spike_map:
            return MotorReadout(
                command=BodyCommand(left_drive=0.0, right_drive=0.0),
                forward_signal=0.0,
                turn_signal=0.0,
                reverse_signal=0.0,
                neuron_rates={
                    "voltage_turn_signal": 0.0,
                    "voltage_turn_state": 0.0,
                    "voltage_turn_group_count": float(len(self.groups)),
                    "voltage_turn_total_weight": 0.0,
                    "voltage_turn_silent_guard": 1.0,
                    "voltage_turn_silent_guard_reason_no_activity": 1.0,
                },
            )
        if voltage_map:
            voltage_values = list(voltage_map.values())
            max_abs_voltage = max(abs(value) for value in voltage_values)
            voltage_span = max(voltage_values) - min(voltage_values)
            max_abs_spike = max((abs(value) for value in spike_map.values()), default=0.0)
            if max_abs_spike <= 1e-9 and (max_abs_voltage <= 1e-9 or voltage_span <= 1e-9):
                return MotorReadout(
                    command=BodyCommand(left_drive=0.0, right_drive=0.0),
                    forward_signal=0.0,
                    turn_signal=0.0,
                    reverse_signal=0.0,
                    neuron_rates={
                        "voltage_turn_signal": 0.0,
                        "voltage_turn_state": 0.0,
                        "voltage_turn_group_count": float(len(self.groups)),
                        "voltage_turn_total_weight": 0.0,
                        "voltage_turn_silent_guard": 1.0,
                        "voltage_turn_silent_guard_voltage_span_mv": float(voltage_span),
                    },
                )
        weighted_turn_sum = 0.0
        total_weight = 0.0
        debug: dict[str, float] = {}
        for group in self.groups:
            left_voltage = self._mean_voltage(voltage_map, group.left_root_ids)
            right_voltage = self._mean_voltage(voltage_map, group.right_root_ids)
            asymmetry_voltage = right_voltage - left_voltage
            centered_asymmetry_voltage = asymmetry_voltage - float(group.baseline_asymmetry_mv)
            weighted_turn_sum += float(group.turn_weight) * centered_asymmetry_voltage
            total_weight += abs(float(group.turn_weight))
            debug[f"{group.label}_left_voltage_mv"] = left_voltage
            debug[f"{group.label}_right_voltage_mv"] = right_voltage
            debug[f"{group.label}_asymmetry_voltage_mv"] = asymmetry_voltage
            debug[f"{group.label}_centered_asymmetry_voltage_mv"] = centered_asymmetry_voltage
            debug[f"{group.label}_baseline_asymmetry_mv"] = float(group.baseline_asymmetry_mv)
            debug[f"{group.label}_turn_weight"] = float(group.turn_weight)
        turn_signal = 0.0
        if total_weight > 0.0 and self.config.turn_scale_mv > 0.0:
            turn_signal = float(np.tanh((weighted_turn_sum / total_weight) / self.config.turn_scale_mv))
        alpha = float(np.clip(self.config.signal_smoothing_alpha, 0.0, 1.0))
        self._turn_state = (1.0 - alpha) * self._turn_state + alpha * turn_signal
        left_drive = float(np.clip(self.config.idle_drive - self.config.turn_gain * self._turn_state, -self.config.max_drive, self.config.max_drive))
        right_drive = float(np.clip(self.config.idle_drive + self.config.turn_gain * self._turn_state, -self.config.max_drive, self.config.max_drive))
        if left_drive >= 0.0:
            left_drive = max(self.config.min_drive, left_drive)
        if right_drive >= 0.0:
            right_drive = max(self.config.min_drive, right_drive)
        debug["voltage_turn_signal"] = float(turn_signal)
        debug["voltage_turn_state"] = float(self._turn_state)
        debug["voltage_turn_group_count"] = float(len(self.groups))
        debug["voltage_turn_total_weight"] = float(total_weight)
        return MotorReadout(
            command=BodyCommand(left_drive=left_drive, right_drive=right_drive),
            forward_signal=0.0,
            turn_signal=float(self._turn_state),
            reverse_signal=0.0,
            neuron_rates=debug,
        )

    def decode(self, rates: Mapping[int, float]) -> MotorReadout:
        del rates
        return self.decode_state(monitored_voltage={})

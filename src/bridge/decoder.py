from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from body.interfaces import BodyCommand, HybridDriveCommand
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
    command_mode: str = "two_drive"
    idle_drive: float = 0.0
    min_drive: float = 0.0
    max_drive: float = 1.2
    max_amp: float = 1.5
    min_freq_scale: float = 0.0
    max_freq_scale: float = 2.0
    forward_scale_hz: float = 120.0
    turn_scale_hz: float = 80.0
    reverse_scale_hz: float = 100.0
    forward_gain: float = 0.4
    turn_gain: float = 0.3
    reverse_threshold: float = 0.65
    latent_freq_bias: float = 0.9
    latent_freq_gain: float = 0.55
    latent_turn_amp_gain: float = 0.3
    latent_turn_freq_gain: float = 0.2
    latent_turn_priority_outer_amp_gain: float = 0.0
    latent_turn_priority_inner_amp_gain: float = 0.0
    latent_turn_priority_outer_freq_gain: float = 0.0
    latent_turn_priority_inner_freq_gain: float = 0.0
    latent_retraction_base: float = 1.0
    latent_stumbling_base: float = 1.0
    latent_retraction_turn_gain: float = 0.35
    latent_stumbling_turn_gain: float = 0.5
    latent_retraction_reverse_gain: float = 0.4
    latent_stumbling_reverse_gain: float = 0.75
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
    forward_context_cell_types: tuple[str, ...] = ()
    forward_context_scale_hz: float = 20.0
    forward_context_mode: str = "blend"
    forward_context_blend: float = 0.0
    forward_context_boost: float = 0.0
    turn_context_cell_types: tuple[str, ...] = ()
    turn_context_scale_hz: float = 20.0
    turn_context_mode: str = "bilateral"
    turn_context_boost: float = 0.0
    motor_basis_json: str | None = None
    monitor_candidates_json: str | None = None
    monitor_cell_types: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any] | None) -> "DecoderConfig":
        mapping = mapping or {}
        return cls(
            command_mode=str(mapping.get("command_mode", "two_drive")),
            idle_drive=float(mapping.get("idle_drive", 0.0)),
            min_drive=float(mapping.get("min_drive", 0.0)),
            max_drive=float(mapping.get("max_drive", 1.2)),
            max_amp=float(mapping.get("max_amp", 1.5)),
            min_freq_scale=float(mapping.get("min_freq_scale", 0.0)),
            max_freq_scale=float(mapping.get("max_freq_scale", 2.0)),
            forward_scale_hz=float(mapping.get("forward_scale_hz", 120.0)),
            turn_scale_hz=float(mapping.get("turn_scale_hz", 80.0)),
            reverse_scale_hz=float(mapping.get("reverse_scale_hz", 100.0)),
            forward_gain=float(mapping.get("forward_gain", 0.4)),
            turn_gain=float(mapping.get("turn_gain", 0.3)),
            reverse_threshold=float(mapping.get("reverse_threshold", 0.65)),
            latent_freq_bias=float(mapping.get("latent_freq_bias", 0.9)),
            latent_freq_gain=float(mapping.get("latent_freq_gain", 0.55)),
            latent_turn_amp_gain=float(mapping.get("latent_turn_amp_gain", 0.3)),
            latent_turn_freq_gain=float(mapping.get("latent_turn_freq_gain", 0.2)),
            latent_turn_priority_outer_amp_gain=float(mapping.get("latent_turn_priority_outer_amp_gain", 0.0)),
            latent_turn_priority_inner_amp_gain=float(mapping.get("latent_turn_priority_inner_amp_gain", 0.0)),
            latent_turn_priority_outer_freq_gain=float(mapping.get("latent_turn_priority_outer_freq_gain", 0.0)),
            latent_turn_priority_inner_freq_gain=float(mapping.get("latent_turn_priority_inner_freq_gain", 0.0)),
            latent_retraction_base=float(mapping.get("latent_retraction_base", 1.0)),
            latent_stumbling_base=float(mapping.get("latent_stumbling_base", 1.0)),
            latent_retraction_turn_gain=float(mapping.get("latent_retraction_turn_gain", 0.35)),
            latent_stumbling_turn_gain=float(mapping.get("latent_stumbling_turn_gain", 0.5)),
            latent_retraction_reverse_gain=float(mapping.get("latent_retraction_reverse_gain", 0.4)),
            latent_stumbling_reverse_gain=float(mapping.get("latent_stumbling_reverse_gain", 0.75)),
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
            forward_context_cell_types=tuple(str(value) for value in mapping.get("forward_context_cell_types", [])),
            forward_context_scale_hz=float(mapping.get("forward_context_scale_hz", 20.0)),
            forward_context_mode=str(mapping.get("forward_context_mode", "blend")),
            forward_context_blend=float(mapping.get("forward_context_blend", 0.0)),
            forward_context_boost=float(mapping.get("forward_context_boost", 0.0)),
            turn_context_cell_types=tuple(str(value) for value in mapping.get("turn_context_cell_types", [])),
            turn_context_scale_hz=float(mapping.get("turn_context_scale_hz", 20.0)),
            turn_context_mode=str(mapping.get("turn_context_mode", "bilateral")),
            turn_context_boost=float(mapping.get("turn_context_boost", 0.0)),
            motor_basis_json=None if mapping.get("motor_basis_json") is None else str(mapping.get("motor_basis_json")),
            monitor_candidates_json=None
            if mapping.get("monitor_candidates_json") is None
            else str(mapping.get("monitor_candidates_json")),
            monitor_cell_types=tuple(str(value) for value in mapping.get("monitor_cell_types", [])),
        )

@dataclass
class MotorReadout:
    command: BodyCommand | HybridDriveCommand
    forward_signal: float
    turn_signal: float
    reverse_signal: float
    neuron_rates: dict[str, float]

class MotorDecoder:
    def __init__(self, config: DecoderConfig | None = None) -> None:
        self.config = config or DecoderConfig()
        self.population_groups = _load_population_groups(self.config.population_candidates_json)
        self.population_forward_group_weights, self.population_turn_group_weights = self._load_motor_basis(self.config.motor_basis_json)
        self.monitor_groups = _load_population_groups(self.config.monitor_candidates_json)
        self.reset()

    def _load_motor_basis(self, path: str | None) -> tuple[dict[str, float], dict[str, float]]:
        if not path:
            return {}, {}
        json_path = Path(path)
        if not json_path.exists():
            return {}, {}
        data = json.loads(json_path.read_text(encoding="utf-8"))
        forward = {
            str(label): float(weight)
            for label, weight in (data.get("forward_group_weights") or {}).items()
        }
        turn = {
            str(label): float(weight)
            for label, weight in (data.get("turn_group_weights") or {}).items()
        }
        return forward, turn

    def reset(self) -> None:
        self._forward_state = 0.0
        self._turn_state = 0.0
        self._reverse_state = 0.0

    def required_neuron_ids(self) -> list[int]:
        ids = {neuron_id for group in MOTOR_READOUT_IDS.values() for neuron_id in group}
        for root_ids in self.population_groups.values():
            ids.update(int(root_id) for root_id in root_ids)
        for root_ids in self.monitor_groups.values():
            ids.update(int(root_id) for root_id in root_ids)
        return sorted(ids)

    def _monitor_cell_types(self) -> tuple[str, ...]:
        if self.config.monitor_cell_types:
            return self.config.monitor_cell_types
        labels = {
            key[: -len("_left")] for key in self.monitor_groups.keys() if key.endswith("_left")
        }
        labels.update(key[: -len("_right")] for key in self.monitor_groups.keys() if key.endswith("_right"))
        return tuple(sorted(labels))

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

    def _weighted_population_side(self, rates: Mapping[int, float], group_weights: Mapping[str, float], side: str) -> float:
        if not group_weights:
            return 0.0
        weighted_sum = 0.0
        total_weight = 0.0
        for cell_type, weight in group_weights.items():
            if abs(float(weight)) <= 1e-12:
                continue
            ids = self.population_groups.get(f"{cell_type}_{side}", [])
            if not ids:
                continue
            weighted_sum += float(weight) * self._mean_group_ids(rates, ids)
            total_weight += abs(float(weight))
        return weighted_sum / total_weight if total_weight > 0.0 else 0.0

    def decode(self, rates: Mapping[int, float]) -> MotorReadout:
        cfg = self.config
        forward_left = self._mean_group(rates, "forward_left")
        forward_right = self._mean_group(rates, "forward_right")
        turn_left = self._mean_group(rates, "turn_left")
        turn_right = self._mean_group(rates, "turn_right")
        reverse = self._mean_group(rates, "reverse")
        if self.population_forward_group_weights:
            population_forward_left = self._weighted_population_side(rates, self.population_forward_group_weights, "left")
            population_forward_right = self._weighted_population_side(rates, self.population_forward_group_weights, "right")
        else:
            population_forward_left = self._mean_population_side(rates, cfg.population_forward_cell_types, "left")
            population_forward_right = self._mean_population_side(rates, cfg.population_forward_cell_types, "right")
        if self.population_turn_group_weights:
            population_turn_left = self._weighted_population_side(rates, self.population_turn_group_weights, "left")
            population_turn_right = self._weighted_population_side(rates, self.population_turn_group_weights, "right")
        else:
            population_turn_left = self._mean_population_side(rates, cfg.population_turn_cell_types, "left")
            population_turn_right = self._mean_population_side(rates, cfg.population_turn_cell_types, "right")
        forward_context_left = self._mean_population_side(rates, cfg.forward_context_cell_types, "left")
        forward_context_right = self._mean_population_side(rates, cfg.forward_context_cell_types, "right")
        forward_context_bilateral = 0.5 * (forward_context_left + forward_context_right)
        forward_context_signal = np.tanh(forward_context_bilateral / max(cfg.forward_context_scale_hz, 1e-6))
        turn_context_left = self._mean_population_side(rates, cfg.turn_context_cell_types, "left")
        turn_context_right = self._mean_population_side(rates, cfg.turn_context_cell_types, "right")
        turn_context_bilateral = 0.5 * (turn_context_left + turn_context_right)
        turn_context_asymmetry_signal = np.tanh(
            (turn_context_right - turn_context_left) / max(cfg.turn_context_scale_hz, 1e-6)
        )
        turn_context_raw_signal = np.tanh(turn_context_bilateral / max(cfg.turn_context_scale_hz, 1e-6))
        turn_context_signal = float(turn_context_raw_signal)
        dn_forward_signal = np.tanh(((forward_left + forward_right) * 0.5) / cfg.forward_scale_hz)
        population_forward_signal = np.tanh(((population_forward_left + population_forward_right) * 0.5) / max(cfg.population_forward_scale_hz, 1e-6))
        forward_signal = np.clip(dn_forward_signal + cfg.population_forward_weight * population_forward_signal, -1.0, 1.0)
        if cfg.forward_context_mode == "boost" and cfg.forward_context_boost != 0.0:
            forward_signal = np.clip(
                forward_signal + cfg.forward_context_boost * forward_context_signal,
                -1.0,
                1.0,
            )
        elif cfg.forward_context_blend != 0.0:
            forward_context_factor = np.clip(
                1.0 - cfg.forward_context_blend + cfg.forward_context_blend * forward_context_signal,
                0.0,
                2.0,
            )
            forward_signal = np.clip(forward_signal * forward_context_factor, -1.0, 1.0)
        dn_turn_signal = np.tanh((turn_right - turn_left) / cfg.turn_scale_hz)
        population_turn_signal = np.tanh((population_turn_right - population_turn_left) / max(cfg.population_turn_scale_hz, 1e-6))
        turn_signal = np.clip(dn_turn_signal + cfg.population_turn_weight * population_turn_signal, -1.0, 1.0)
        if cfg.turn_context_boost != 0.0:
            if cfg.turn_context_mode == "aligned_asymmetry":
                turn_context_signal = max(0.0, np.sign(turn_signal) * float(turn_context_asymmetry_signal))
            turn_signal = float(
                np.clip(turn_signal * (1.0 + cfg.turn_context_boost * turn_context_signal), -1.0, 1.0)
            )
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
        command: BodyCommand | HybridDriveCommand
        latent_debug: dict[str, float] = {}
        if cfg.command_mode == "hybrid_multidrive":
            locomotor_level = max(0.0, self._forward_state)
            turn_level = float(self._turn_state)
            turn_strength = abs(turn_level)
            base_amp = cfg.forward_gain * locomotor_level
            left_amp = base_amp - cfg.latent_turn_amp_gain * turn_level
            right_amp = base_amp + cfg.latent_turn_amp_gain * turn_level
            base_freq_scale = cfg.latent_freq_bias + cfg.latent_freq_gain * locomotor_level
            left_freq_scale = base_freq_scale - cfg.latent_turn_freq_gain * turn_level
            right_freq_scale = base_freq_scale + cfg.latent_turn_freq_gain * turn_level
            turn_priority = turn_strength * max(0.0, 1.0 - locomotor_level)
            if turn_level > 0.0:
                left_amp -= cfg.latent_turn_priority_inner_amp_gain * turn_priority
                right_amp += cfg.latent_turn_priority_outer_amp_gain * turn_priority
                left_freq_scale -= cfg.latent_turn_priority_inner_freq_gain * turn_priority
                right_freq_scale += cfg.latent_turn_priority_outer_freq_gain * turn_priority
            elif turn_level < 0.0:
                left_amp += cfg.latent_turn_priority_outer_amp_gain * turn_priority
                right_amp -= cfg.latent_turn_priority_inner_amp_gain * turn_priority
                left_freq_scale += cfg.latent_turn_priority_outer_freq_gain * turn_priority
                right_freq_scale -= cfg.latent_turn_priority_inner_freq_gain * turn_priority
            left_amp = float(np.clip(left_amp, 0.0, cfg.max_amp))
            right_amp = float(np.clip(right_amp, 0.0, cfg.max_amp))
            left_freq_scale = float(np.clip(left_freq_scale, cfg.min_freq_scale, cfg.max_freq_scale))
            right_freq_scale = float(np.clip(right_freq_scale, cfg.min_freq_scale, cfg.max_freq_scale))
            reverse_gate = 1.0 if self._reverse_state > cfg.reverse_threshold else 0.0
            retraction_gain = float(
                np.clip(
                    cfg.latent_retraction_base
                    + cfg.latent_retraction_turn_gain * turn_strength
                    + cfg.latent_retraction_reverse_gain * max(0.0, self._reverse_state),
                    0.0,
                    3.0,
                )
            )
            stumbling_gain = float(
                np.clip(
                    cfg.latent_stumbling_base
                    + cfg.latent_stumbling_turn_gain * turn_strength
                    + cfg.latent_stumbling_reverse_gain * max(0.0, self._reverse_state),
                    0.0,
                    3.0,
                )
            )
            latent_debug = {
                "locomotor_level": float(locomotor_level),
                "turn_strength": float(turn_strength),
                "turn_priority": float(turn_priority),
                "base_amp": float(base_amp),
                "base_freq_scale": float(base_freq_scale),
                "left_amp_command": left_amp,
                "right_amp_command": right_amp,
                "left_freq_scale_command": left_freq_scale,
                "right_freq_scale_command": right_freq_scale,
            }
            command = HybridDriveCommand(
                left_drive=left_drive,
                right_drive=right_drive,
                left_amp=left_amp,
                right_amp=right_amp,
                left_freq_scale=left_freq_scale,
                right_freq_scale=right_freq_scale,
                retraction_gain=retraction_gain,
                stumbling_gain=stumbling_gain,
                reverse_gate=reverse_gate,
            )
        else:
            command = BodyCommand(left_drive=left_drive, right_drive=right_drive)
        monitor_rates: dict[str, float] = {}
        for cell_type in self._monitor_cell_types():
            left_value = self._mean_group_ids(rates, self.monitor_groups.get(f"{cell_type}_left", []))
            right_value = self._mean_group_ids(rates, self.monitor_groups.get(f"{cell_type}_right", []))
            monitor_rates[f"monitor_{cell_type}_left_hz"] = left_value
            monitor_rates[f"monitor_{cell_type}_right_hz"] = right_value
            monitor_rates[f"monitor_{cell_type}_bilateral_hz"] = 0.5 * (left_value + right_value)
            monitor_rates[f"monitor_{cell_type}_right_minus_left_hz"] = right_value - left_value
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
                "forward_context_left_hz": forward_context_left,
                "forward_context_right_hz": forward_context_right,
                "forward_context_bilateral_hz": float(forward_context_bilateral),
                "forward_context_signal": float(forward_context_signal),
                "turn_context_left_hz": turn_context_left,
                "turn_context_right_hz": turn_context_right,
                "turn_context_bilateral_hz": float(turn_context_bilateral),
                "turn_context_asymmetry_signal": float(turn_context_asymmetry_signal),
                "turn_context_raw_signal": float(turn_context_raw_signal),
                "turn_context_signal": float(turn_context_signal),
                "dn_forward_signal": float(dn_forward_signal),
                "population_forward_signal": float(population_forward_signal),
                "dn_turn_signal": float(dn_turn_signal),
                "population_turn_signal": float(population_turn_signal),
                "forward_state": float(self._forward_state),
                "turn_state": float(self._turn_state),
                "reverse_state": float(self._reverse_state),
                **latent_debug,
                **monitor_rates,
            },
        )

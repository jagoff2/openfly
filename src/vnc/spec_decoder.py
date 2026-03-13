from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from body.interfaces import BodyCommand, HybridDriveCommand
from bridge.decoder import MotorReadout


@dataclass(frozen=True)
class VNCSpecChannel:
    root_id: int
    cell_type: str
    side: str
    left_total_weight: float
    right_total_weight: float
    total_motor_weight: float
    monitor_ids: tuple[int, ...] = ()
    source_root_ids: tuple[int, ...] = ()
    monitor_match_field: str | None = None
    monitor_root_count: int = 0


@dataclass
class VNCSpecDecoderConfig:
    spec_json: str | None = None
    command_mode: str = "hybrid_multidrive"
    max_drive: float = 1.2
    max_amp: float = 1.5
    min_freq_scale: float = 0.0
    max_freq_scale: float = 2.0
    forward_scale_hz: float = 400.0
    turn_scale_hz: float = 250.0
    forward_gain: float = 0.4
    turn_gain: float = 0.3
    latent_freq_bias: float = 0.9
    latent_freq_gain: float = 0.55
    latent_turn_amp_gain: float = 0.3
    latent_turn_freq_gain: float = 0.2
    latent_retraction_base: float = 1.0
    latent_stumbling_base: float = 1.0
    latent_retraction_turn_gain: float = 0.35
    latent_stumbling_turn_gain: float = 0.5
    min_total_weight: float = 0.0
    max_channels: int = 0
    monitor_top_channels: int = 8
    monitor_reduce: str = "mean"
    weight_normalization_mode: str = "by_side_total"

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any] | None) -> "VNCSpecDecoderConfig":
        mapping = mapping or {}
        return cls(
            spec_json=None if mapping.get("spec_json", mapping.get("vnc_spec_json")) is None else str(mapping.get("spec_json", mapping.get("vnc_spec_json"))),
            command_mode=str(mapping.get("command_mode", "hybrid_multidrive")),
            max_drive=float(mapping.get("max_drive", 1.2)),
            max_amp=float(mapping.get("max_amp", 1.5)),
            min_freq_scale=float(mapping.get("min_freq_scale", 0.0)),
            max_freq_scale=float(mapping.get("max_freq_scale", 2.0)),
            forward_scale_hz=float(mapping.get("forward_scale_hz", 400.0)),
            turn_scale_hz=float(mapping.get("turn_scale_hz", 250.0)),
            forward_gain=float(mapping.get("forward_gain", 0.4)),
            turn_gain=float(mapping.get("turn_gain", 0.3)),
            latent_freq_bias=float(mapping.get("latent_freq_bias", 0.9)),
            latent_freq_gain=float(mapping.get("latent_freq_gain", 0.55)),
            latent_turn_amp_gain=float(mapping.get("latent_turn_amp_gain", 0.3)),
            latent_turn_freq_gain=float(mapping.get("latent_turn_freq_gain", 0.2)),
            latent_retraction_base=float(mapping.get("latent_retraction_base", 1.0)),
            latent_stumbling_base=float(mapping.get("latent_stumbling_base", 1.0)),
            latent_retraction_turn_gain=float(mapping.get("latent_retraction_turn_gain", 0.35)),
            latent_stumbling_turn_gain=float(mapping.get("latent_stumbling_turn_gain", 0.5)),
            min_total_weight=float(mapping.get("min_total_weight", 0.0)),
            max_channels=int(mapping.get("max_channels", 0)),
            monitor_top_channels=int(mapping.get("monitor_top_channels", 8)),
            monitor_reduce=str(mapping.get("monitor_reduce", "mean")),
            weight_normalization_mode=str(mapping.get("weight_normalization_mode", "by_side_total")),
        )


def _sanitize_label(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value.strip()).strip("_").lower() or "unknown"


def _load_channels(config: VNCSpecDecoderConfig) -> tuple[VNCSpecChannel, ...]:
    if not config.spec_json:
        return ()
    path = Path(config.spec_json)
    if not path.exists():
        return ()
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_channels = payload.get("channels") or []
    channels: list[VNCSpecChannel] = []
    for item in raw_channels:
        if not isinstance(item, dict):
            continue
        channel = VNCSpecChannel(
            root_id=int(item.get("root_id", 0)),
            cell_type=str(item.get("cell_type", "")),
            side=str(item.get("side", "")),
            left_total_weight=float(item.get("left_total_weight", 0.0)),
            right_total_weight=float(item.get("right_total_weight", 0.0)),
            total_motor_weight=float(item.get("total_motor_weight", 0.0)),
            monitor_ids=tuple(sorted({int(root_id) for root_id in item.get("monitor_ids", []) if int(root_id) > 0})),
            source_root_ids=tuple(sorted({int(root_id) for root_id in item.get("source_root_ids", []) if int(root_id) > 0})),
            monitor_match_field=None if item.get("monitor_match_field") is None else str(item.get("monitor_match_field")),
            monitor_root_count=int(item.get("monitor_root_count", len(item.get("monitor_ids", [])))),
        )
        if (channel.root_id <= 0 and not channel.monitor_ids) or channel.total_motor_weight < config.min_total_weight:
            continue
        channels.append(channel)
    if config.max_channels > 0:
        channels = channels[: config.max_channels]
    return tuple(channels)


class VNCSpecDecoder:
    def __init__(self, config: VNCSpecDecoderConfig | None = None) -> None:
        self.config = config or VNCSpecDecoderConfig()
        self.channels = _load_channels(self.config)
        self.total_left_weight_mass = sum(channel.left_total_weight for channel in self.channels)
        self.total_right_weight_mass = sum(channel.right_total_weight for channel in self.channels)

    def reset(self) -> None:
        return None

    def required_neuron_ids(self) -> list[int]:
        return sorted(
            {
                int(neuron_id)
                for channel in self.channels
                for neuron_id in (channel.monitor_ids if channel.monitor_ids else ((channel.root_id,) if channel.root_id > 0 else ()))
                if int(neuron_id) > 0
            }
        )

    def _channel_rate(self, channel: VNCSpecChannel, rates: Mapping[int, float]) -> float:
        monitor_ids = channel.monitor_ids if channel.monitor_ids else ((channel.root_id,) if channel.root_id > 0 else ())
        if not monitor_ids:
            return 0.0
        values = [float(rates.get(int(neuron_id), 0.0)) for neuron_id in monitor_ids]
        mode = str(self.config.monitor_reduce).strip().lower()
        if mode == "sum":
            return float(sum(values))
        if mode == "max":
            return float(max(values)) if values else 0.0
        return float(sum(values) / len(values)) if values else 0.0

    def decode(self, rates: Mapping[int, float]) -> MotorReadout:
        cfg = self.config
        weighted_left = 0.0
        weighted_right = 0.0
        channel_debug: list[tuple[str, float, float, float]] = []

        for channel in self.channels:
            rate = self._channel_rate(channel, rates)
            left_contribution = rate * channel.left_total_weight
            right_contribution = rate * channel.right_total_weight
            weighted_left += left_contribution
            weighted_right += right_contribution
            channel_label = f"{_sanitize_label(channel.cell_type)}_{_sanitize_label(channel.side)}"
            if not channel.monitor_ids and channel.root_id > 0:
                channel_label = f"{channel_label}_{channel.root_id}"
            channel_debug.append(
                (
                    channel_label,
                    rate,
                    left_contribution,
                    right_contribution,
                )
            )

        if str(cfg.weight_normalization_mode).strip().lower() == "by_side_total":
            normalized_left = weighted_left / max(self.total_left_weight_mass, 1e-6)
            normalized_right = weighted_right / max(self.total_right_weight_mass, 1e-6)
        else:
            normalized_left = weighted_left
            normalized_right = weighted_right
        forward_signal = float(
            np.tanh(((normalized_left + normalized_right) * 0.5) / max(cfg.forward_scale_hz, 1e-6))
        )
        turn_signal = float(
            np.tanh((normalized_right - normalized_left) / max(cfg.turn_scale_hz, 1e-6))
        )
        reverse_signal = 0.0

        locomotor_level = max(0.0, forward_signal)
        turn_strength = abs(turn_signal)
        left_drive = float(np.clip(cfg.forward_gain * locomotor_level - cfg.turn_gain * turn_signal, -cfg.max_drive, cfg.max_drive))
        right_drive = float(np.clip(cfg.forward_gain * locomotor_level + cfg.turn_gain * turn_signal, -cfg.max_drive, cfg.max_drive))

        if cfg.command_mode == "hybrid_multidrive":
            base_amp = cfg.forward_gain * locomotor_level
            left_amp = float(np.clip(base_amp - cfg.latent_turn_amp_gain * turn_signal, 0.0, cfg.max_amp))
            right_amp = float(np.clip(base_amp + cfg.latent_turn_amp_gain * turn_signal, 0.0, cfg.max_amp))
            base_freq_scale = cfg.latent_freq_bias + cfg.latent_freq_gain * locomotor_level
            left_freq_scale = float(np.clip(base_freq_scale - cfg.latent_turn_freq_gain * turn_signal, cfg.min_freq_scale, cfg.max_freq_scale))
            right_freq_scale = float(np.clip(base_freq_scale + cfg.latent_turn_freq_gain * turn_signal, cfg.min_freq_scale, cfg.max_freq_scale))
            retraction_gain = float(np.clip(cfg.latent_retraction_base + cfg.latent_retraction_turn_gain * turn_strength, 0.0, 3.0))
            stumbling_gain = float(np.clip(cfg.latent_stumbling_base + cfg.latent_stumbling_turn_gain * turn_strength, 0.0, 3.0))
            command: BodyCommand | HybridDriveCommand = HybridDriveCommand(
                left_drive=left_drive,
                right_drive=right_drive,
                left_amp=left_amp,
                right_amp=right_amp,
                left_freq_scale=left_freq_scale,
                right_freq_scale=right_freq_scale,
                retraction_gain=retraction_gain,
                stumbling_gain=stumbling_gain,
                reverse_gate=0.0,
            )
        else:
            command = BodyCommand(left_drive=left_drive, right_drive=right_drive)

        monitor_count = max(0, int(cfg.monitor_top_channels))
        top_channels = sorted(
            channel_debug,
            key=lambda item: -(abs(item[2]) + abs(item[3])),
        )[:monitor_count]
        debug_values: dict[str, float] = {
            "weighted_left_motor_drive_hz": float(weighted_left),
            "weighted_right_motor_drive_hz": float(weighted_right),
            "normalized_left_motor_rate_hz": float(normalized_left),
            "normalized_right_motor_rate_hz": float(normalized_right),
            "vnc_channel_count": float(len(self.channels)),
            "vnc_required_monitor_id_count": float(len(self.required_neuron_ids())),
        }
        for label, rate, left_contribution, right_contribution in top_channels:
            debug_values[f"vnc_rate_{label}_hz"] = float(rate)
            debug_values[f"vnc_left_{label}_contrib"] = float(left_contribution)
            debug_values[f"vnc_right_{label}_contrib"] = float(right_contribution)

        return MotorReadout(
            command=command,
            forward_signal=forward_signal,
            turn_signal=turn_signal,
            reverse_signal=reverse_signal,
            neuron_rates=debug_values,
        )

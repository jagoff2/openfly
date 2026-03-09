from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from body.interfaces import BodyObservation
from brain.public_ids import MOTOR_READOUT_IDS, P9_LEFT, P9_RIGHT
from bridge.encoder import SensorEncoding
from vision.feature_extractor import VisionFeatures


@dataclass
class BrainContextConfig:
    mode: str = "none"
    p9_rate_hz: float = 100.0
    p9_left_rate_hz: float | None = None
    p9_right_rate_hz: float | None = None
    inferred_base_p9_rate_hz: float = 0.0
    inferred_p9_gain_hz: float = 120.0
    inferred_turn_rate_hz: float = 100.0
    inferred_confidence_scale: float = 1.0
    inferred_forward_on_threshold: float = 0.60
    inferred_forward_off_threshold: float = 0.55
    inferred_forward_scale: float = 0.03
    inferred_gate_tau_s: float = 0.12
    inferred_turn_bias_scale: float = 0.03
    inferred_balance_scale: float = 0.015
    inferred_p9_asymmetry_gain: float = 0.45

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any] | None) -> "BrainContextConfig":
        mapping = mapping or {}
        return cls(
            mode=str(mapping.get("mode", "none")),
            p9_rate_hz=float(mapping.get("p9_rate_hz", 100.0)),
            p9_left_rate_hz=None if mapping.get("p9_left_rate_hz") is None else float(mapping["p9_left_rate_hz"]),
            p9_right_rate_hz=None if mapping.get("p9_right_rate_hz") is None else float(mapping["p9_right_rate_hz"]),
            inferred_base_p9_rate_hz=float(mapping.get("inferred_base_p9_rate_hz", 0.0)),
            inferred_p9_gain_hz=float(mapping.get("inferred_p9_gain_hz", 120.0)),
            inferred_turn_rate_hz=float(mapping.get("inferred_turn_rate_hz", 100.0)),
            inferred_confidence_scale=float(mapping.get("inferred_confidence_scale", 1.0)),
            inferred_forward_on_threshold=float(mapping.get("inferred_forward_on_threshold", 0.60)),
            inferred_forward_off_threshold=float(mapping.get("inferred_forward_off_threshold", 0.55)),
            inferred_forward_scale=float(mapping.get("inferred_forward_scale", 0.03)),
            inferred_gate_tau_s=float(mapping.get("inferred_gate_tau_s", 0.12)),
            inferred_turn_bias_scale=float(mapping.get("inferred_turn_bias_scale", 0.03)),
            inferred_balance_scale=float(mapping.get("inferred_balance_scale", 0.015)),
            inferred_p9_asymmetry_gain=float(mapping.get("inferred_p9_asymmetry_gain", 0.45)),
        )


class BrainContextInjector:
    def __init__(self, config: BrainContextConfig | None = None) -> None:
        self.config = config or BrainContextConfig()
        self.reset()

    def reset(self) -> None:
        self._locomotor_gate = 0.0
        self._last_sim_time: float | None = None

    def _update_locomotor_gate(self, observation: BodyObservation, vision_features: VisionFeatures) -> tuple[float, float]:
        cfg = self.config
        threshold = cfg.inferred_forward_off_threshold if self._locomotor_gate > 0.0 else cfg.inferred_forward_on_threshold
        target = float(
            np.clip(
                (vision_features.forward_salience - threshold) / max(cfg.inferred_forward_scale, 1e-6),
                0.0,
                1.0,
            )
        )
        if self._last_sim_time is None:
            alpha = 1.0
        else:
            dt = max(0.0, float(observation.sim_time) - float(self._last_sim_time))
            tau = max(cfg.inferred_gate_tau_s, 1e-6)
            alpha = 1.0 - float(np.exp(-dt / tau))
        self._locomotor_gate += alpha * (target - self._locomotor_gate)
        self._locomotor_gate = float(np.clip(self._locomotor_gate, 0.0, 1.0))
        self._last_sim_time = float(observation.sim_time)
        return self._locomotor_gate, target

    def _build_asymmetric_p9_rates(
        self,
        observation: BodyObservation,
        vision_features: VisionFeatures,
    ) -> tuple[float, float, dict[str, float]]:
        cfg = self.config
        gate, target = self._update_locomotor_gate(observation, vision_features)
        base_rate_hz = float(cfg.inferred_base_p9_rate_hz + cfg.inferred_p9_gain_hz * gate)
        inferred_bias = float(vision_features.inferred_turn_bias / max(cfg.inferred_turn_bias_scale, 1e-6))
        balance_bias = float(vision_features.balance / max(cfg.inferred_balance_scale, 1e-6))
        raw_bias = inferred_bias + balance_bias
        normalized_bias = float(np.tanh(raw_bias))
        asymmetry = float(np.clip(cfg.inferred_p9_asymmetry_gain * normalized_bias, -0.95, 0.95))
        left_rate_hz = float(max(0.0, base_rate_hz * (1.0 - asymmetry)))
        right_rate_hz = float(max(0.0, base_rate_hz * (1.0 + asymmetry)))
        info = {
            "locomotor_gate": gate,
            "locomotor_target": target,
            "forward_rate_hz": base_rate_hz,
            "p9_asymmetry": asymmetry,
            "normalized_turn_bias": normalized_bias,
            "inferred_bias_term": inferred_bias,
            "balance_bias_term": balance_bias,
        }
        return left_rate_hz, right_rate_hz, info

    def build(
        self,
        observation: BodyObservation,
        vision_features: VisionFeatures,
        sensor_encoding: SensorEncoding,
    ) -> tuple[dict[int, float], dict[str, Any]]:
        del sensor_encoding
        cfg = self.config
        if cfg.mode == "none":
            return {}, {"mode": "none", "direct_input_rates_hz": {}}
        if cfg.mode == "public_p9_context":
            left_rate_hz = float(cfg.p9_left_rate_hz if cfg.p9_left_rate_hz is not None else cfg.p9_rate_hz)
            right_rate_hz = float(cfg.p9_right_rate_hz if cfg.p9_right_rate_hz is not None else cfg.p9_rate_hz)
            direct_input_rates_hz = {
                P9_LEFT: left_rate_hz,
                P9_RIGHT: right_rate_hz,
            }
            return direct_input_rates_hz, {
                "mode": "public_p9_context",
                "direct_input_rates_hz": {
                    "P9_left": left_rate_hz,
                    "P9_right": right_rate_hz,
                },
            }
        if cfg.mode == "inferred_visual_turn_context":
            forward_rate_hz = float(
                cfg.inferred_base_p9_rate_hz + cfg.inferred_p9_gain_hz * max(0.0, vision_features.forward_salience)
            )
            confidence = float(max(0.0, vision_features.inferred_turn_confidence) * max(0.0, cfg.inferred_confidence_scale))
            turn_bias = float(np.clip(vision_features.inferred_turn_bias, -1.0, 1.0))
            turn_rate_hz = float(cfg.inferred_turn_rate_hz * min(1.0, abs(turn_bias) * confidence))
            direct_input_rates_hz = {
                P9_LEFT: forward_rate_hz,
                P9_RIGHT: forward_rate_hz,
            }
            if turn_bias > 0.0:
                for neuron_id in MOTOR_READOUT_IDS["turn_right"]:
                    direct_input_rates_hz[neuron_id] = turn_rate_hz
            elif turn_bias < 0.0:
                for neuron_id in MOTOR_READOUT_IDS["turn_left"]:
                    direct_input_rates_hz[neuron_id] = turn_rate_hz
            return direct_input_rates_hz, {
                "mode": "inferred_visual_turn_context",
                "turn_bias": turn_bias,
                "turn_confidence": confidence,
                "forward_rate_hz": forward_rate_hz,
                "turn_rate_hz": turn_rate_hz,
                "direct_input_rates_hz": {
                    "P9_left": forward_rate_hz,
                    "P9_right": forward_rate_hz,
                    "turn_left_rate_hz": turn_rate_hz if turn_bias < 0.0 else 0.0,
                    "turn_right_rate_hz": turn_rate_hz if turn_bias > 0.0 else 0.0,
                },
            }
        if cfg.mode == "inferred_visual_p9_context":
            left_rate_hz, right_rate_hz, extra = self._build_asymmetric_p9_rates(observation, vision_features)
            direct_input_rates_hz = {
                P9_LEFT: left_rate_hz,
                P9_RIGHT: right_rate_hz,
            }
            return direct_input_rates_hz, {
                "mode": "inferred_visual_p9_context",
                **extra,
                "direct_input_rates_hz": {
                    "P9_left": left_rate_hz,
                    "P9_right": right_rate_hz,
                },
            }
        raise ValueError(f"Unsupported brain context mode: {cfg.mode}")

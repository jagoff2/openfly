from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from body.interfaces import BodyObservation
from bridge.brain_context import BrainContextInjector
from bridge.decoder import MotorDecoder, MotorReadout
from bridge.encoder import SensoryEncoder
from bridge.visual_splice import VisualSpliceInjector
from vision.feature_extractor import RealisticVisionFeatureExtractor

@dataclass(frozen=True)
class SteeringPromotionConfig:
    enabled: bool = False
    shadow_label: str = ""
    mode: str = "blend"
    turn_blend: float = 0.0
    conflict_turn_blend: float = 1.0
    shadow_turn_scale: float = 1.0
    max_abs_turn_state: float = 1.0
    conflict_shadow_min_abs: float = 0.0
    conflict_shadow_min_ratio: float = 1.0
    conflict_visual_evidence_scale: float = 0.0
    conflict_visual_evidence_floor: float = 0.0

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any] | None) -> "SteeringPromotionConfig":
        mapping = dict(mapping or {})
        return cls(
            enabled=bool(mapping.get("enabled", False)),
            shadow_label=str(mapping.get("shadow_label", "")),
            mode=str(mapping.get("mode", "blend")),
            turn_blend=float(mapping.get("turn_blend", 0.0)),
            conflict_turn_blend=float(mapping.get("conflict_turn_blend", 1.0)),
            shadow_turn_scale=float(mapping.get("shadow_turn_scale", 1.0)),
            max_abs_turn_state=float(mapping.get("max_abs_turn_state", 1.0)),
            conflict_shadow_min_abs=float(mapping.get("conflict_shadow_min_abs", 0.0)),
            conflict_shadow_min_ratio=float(mapping.get("conflict_shadow_min_ratio", 1.0)),
            conflict_visual_evidence_scale=float(mapping.get("conflict_visual_evidence_scale", 0.0)),
            conflict_visual_evidence_floor=float(mapping.get("conflict_visual_evidence_floor", 0.0)),
        )


class ClosedLoopBridge:
    def __init__(self, brain_backend: Any, encoder: SensoryEncoder | None = None, decoder: Any | None = None, vision_extractor: RealisticVisionFeatureExtractor | None = None, brain_context_injector: BrainContextInjector | None = None, visual_splice_injector: VisualSpliceInjector | None = None, shadow_decoders: list[tuple[str, Any]] | None = None, steering_promotion: SteeringPromotionConfig | dict[str, Any] | None = None) -> None:
        self.brain_backend = brain_backend
        self.encoder = encoder or SensoryEncoder()
        self.decoder = decoder or MotorDecoder()
        self.vision_extractor = vision_extractor or RealisticVisionFeatureExtractor()
        self.brain_context_injector = brain_context_injector or BrainContextInjector()
        self.visual_splice_injector = visual_splice_injector or VisualSpliceInjector()
        self.shadow_decoders = list(shadow_decoders or [])
        self.steering_promotion = steering_promotion if isinstance(steering_promotion, SteeringPromotionConfig) else SteeringPromotionConfig.from_mapping(steering_promotion)

    def _promoted_turn_state(self, *, live_turn_state: float, shadow_turn_state: float, conflict_visual_evidence_gate: float = 1.0) -> tuple[float, dict[str, Any]]:
        cfg = self.steering_promotion
        live_sign = 0.0 if abs(live_turn_state) <= 1e-9 else float(1.0 if live_turn_state > 0.0 else -1.0)
        shadow_sign = 0.0 if abs(shadow_turn_state) <= 1e-9 else float(1.0 if shadow_turn_state > 0.0 else -1.0)
        same_sign = bool(live_sign != 0.0 and live_sign == shadow_sign)
        opposite_sign = bool(live_sign != 0.0 and shadow_sign != 0.0 and live_sign != shadow_sign)
        shadow_confident = bool(
            abs(shadow_turn_state) >= max(0.0, float(cfg.conflict_shadow_min_abs))
            and abs(shadow_turn_state) >= max(0.0, float(cfg.conflict_shadow_min_ratio)) * abs(live_turn_state)
        )
        selected_mode = str(cfg.mode)
        selected_blend = float(max(0.0, min(1.0, cfg.turn_blend)))
        conflict_override_active = False
        if cfg.mode == "replace":
            promoted_turn_state = shadow_turn_state
        elif cfg.mode == "conflict_blend":
            if opposite_sign and shadow_confident:
                base_blend = float(max(0.0, min(1.0, cfg.turn_blend)))
                max_conflict_blend = float(max(0.0, min(1.0, cfg.conflict_turn_blend)))
                conflict_visual_evidence_gate = float(max(0.0, min(1.0, conflict_visual_evidence_gate)))
                selected_blend = base_blend + conflict_visual_evidence_gate * (max_conflict_blend - base_blend)
                conflict_override_active = selected_blend > float(max(0.0, min(1.0, cfg.turn_blend))) + 1e-9
                selected_mode = "conflict_override" if conflict_override_active else "conflict_blend"
            promoted_turn_state = (1.0 - selected_blend) * live_turn_state + selected_blend * shadow_turn_state
        else:
            promoted_turn_state = (1.0 - selected_blend) * live_turn_state + selected_blend * shadow_turn_state
        promoted_turn_state = float(
            max(
                -abs(cfg.max_abs_turn_state),
                min(abs(cfg.max_abs_turn_state), promoted_turn_state),
            )
        )
        return promoted_turn_state, {
            "enabled": True,
            "mode": str(cfg.mode),
            "selected_mode": selected_mode,
            "shadow_label": cfg.shadow_label,
            "turn_blend": float(cfg.turn_blend),
            "conflict_turn_blend": float(cfg.conflict_turn_blend),
            "shadow_turn_scale": float(cfg.shadow_turn_scale),
            "max_abs_turn_state": float(cfg.max_abs_turn_state),
            "conflict_shadow_min_abs": float(cfg.conflict_shadow_min_abs),
            "conflict_shadow_min_ratio": float(cfg.conflict_shadow_min_ratio),
            "conflict_visual_evidence_scale": float(cfg.conflict_visual_evidence_scale),
            "conflict_visual_evidence_floor": float(cfg.conflict_visual_evidence_floor),
            "live_turn_state": float(live_turn_state),
            "shadow_turn_state": float(shadow_turn_state),
            "promoted_turn_state": float(promoted_turn_state),
            "live_shadow_same_sign": same_sign,
            "live_shadow_opposite_sign": opposite_sign,
            "shadow_confident": shadow_confident,
            "conflict_visual_evidence_gate": float(max(0.0, min(1.0, conflict_visual_evidence_gate))),
            "conflict_override_active": conflict_override_active,
            "selected_turn_blend": float(selected_blend),
        }

    def reset(self, seed: int = 0) -> None:
        if hasattr(self.brain_backend, "reset"):
            self.brain_backend.reset(seed)
        if hasattr(self.decoder, "reset"):
            self.decoder.reset()
        for _, shadow_decoder in self.shadow_decoders:
            if hasattr(shadow_decoder, "reset"):
                shadow_decoder.reset()
        if hasattr(self.brain_context_injector, "reset"):
            self.brain_context_injector.reset()
        if hasattr(self.visual_splice_injector, "reset"):
            self.visual_splice_injector.reset()

    def step(self, observation: BodyObservation, num_brain_steps: int) -> tuple[MotorReadout, dict[str, Any]]:
        vision_features = self.vision_extractor.extract_observation(observation)
        sensor_encoding = self.encoder.encode(observation, vision_features)
        direct_input_rates_hz, brain_context_info = self.brain_context_injector.build(observation, vision_features, sensor_encoding)
        direct_current_by_id, visual_splice_info = self.visual_splice_injector.build(observation)
        firing_rates = self.brain_backend.step(
            sensor_encoding.pool_rates,
            num_steps=num_brain_steps,
            direct_input_rates_hz=direct_input_rates_hz,
            direct_current_by_id=direct_current_by_id,
        )
        monitored_voltage = {}
        monitored_spikes = {}
        monitored_ids = getattr(self.brain_backend, "monitored_ids", [])
        monitored_indices = getattr(self.brain_backend, "monitored_indices", None)
        if monitored_ids and monitored_indices is not None and hasattr(self.brain_backend, "v"):
            voltage_values = self.brain_backend.v[0, monitored_indices].detach().cpu().numpy().astype(float, copy=False)
            monitored_voltage = {str(neuron_id): float(value) for neuron_id, value in zip(monitored_ids, voltage_values)}
        if monitored_ids and monitored_indices is not None and hasattr(self.brain_backend, "spikes"):
            spike_values = self.brain_backend.spikes[0, monitored_indices].detach().cpu().numpy().astype(float, copy=False)
            monitored_spikes = {str(neuron_id): float(value) for neuron_id, value in zip(monitored_ids, spike_values)}
        backend_state = self.brain_backend.state_summary() if hasattr(self.brain_backend, "state_summary") else {}
        motor_readout = self.decoder.decode(firing_rates)
        shadow_decodes: dict[str, Any] = {}
        shadow_readout_objects: dict[str, MotorReadout] = {}
        for label, shadow_decoder in self.shadow_decoders:
            if hasattr(shadow_decoder, "decode_state"):
                shadow_readout = shadow_decoder.decode_state(
                    firing_rates,
                    monitored_voltage=monitored_voltage,
                    monitored_spikes=monitored_spikes,
                )
            else:
                shadow_readout = shadow_decoder.decode(firing_rates)
            shadow_readout_objects[str(label)] = shadow_readout
            shadow_decodes[str(label)] = {
                "forward_signal": float(shadow_readout.forward_signal),
                "turn_signal": float(shadow_readout.turn_signal),
                "reverse_signal": float(shadow_readout.reverse_signal),
                "command": shadow_readout.command.to_log_dict(),
                "neuron_rates": shadow_readout.neuron_rates,
            }
        promotion_info: dict[str, Any] = {}
        if (
            self.steering_promotion.enabled
            and isinstance(self.decoder, MotorDecoder)
            and self.steering_promotion.shadow_label
            and self.steering_promotion.shadow_label in shadow_readout_objects
        ):
            shadow_readout = shadow_readout_objects[self.steering_promotion.shadow_label]
            live_turn_state = float(motor_readout.neuron_rates.get("turn_state", motor_readout.turn_signal))
            shadow_turn_state = float(shadow_readout.turn_signal) * float(self.steering_promotion.shadow_turn_scale)
            shadow_turn_state = float(
                max(
                    -abs(self.steering_promotion.max_abs_turn_state),
                    min(abs(self.steering_promotion.max_abs_turn_state), shadow_turn_state),
                )
            )
            salience_diff = float(vision_features.salience_right) - float(vision_features.salience_left)
            evidence_scale = float(self.steering_promotion.conflict_visual_evidence_scale)
            if evidence_scale > 0.0:
                conflict_visual_evidence_gate = float(
                    max(
                        float(self.steering_promotion.conflict_visual_evidence_floor),
                        min(1.0, abs(salience_diff) / evidence_scale),
                    )
                )
            else:
                conflict_visual_evidence_gate = 1.0
            promoted_turn_state, promotion_info = self._promoted_turn_state(
                live_turn_state=live_turn_state,
                shadow_turn_state=shadow_turn_state,
                conflict_visual_evidence_gate=conflict_visual_evidence_gate,
            )
            motor_readout = self.decoder.compose_promoted_readout(
                base_readout=motor_readout,
                promoted_turn_state=promoted_turn_state,
                promotion_debug={
                    "promotion_live_turn_state": live_turn_state,
                    "promotion_shadow_turn_state": shadow_turn_state,
                    "promotion_turn_blend": float(self.steering_promotion.turn_blend),
                    "promotion_conflict_turn_blend": float(self.steering_promotion.conflict_turn_blend),
                    "promotion_shadow_turn_scale": float(self.steering_promotion.shadow_turn_scale),
                    "promotion_conflict_visual_evidence_gate": float(conflict_visual_evidence_gate),
                    "promotion_selected_turn_blend": float(promotion_info.get("selected_turn_blend", self.steering_promotion.turn_blend)),
                    "promotion_conflict_override_active": 1.0 if promotion_info.get("conflict_override_active", False) else 0.0,
                    "promotion_mode_replace": 1.0 if self.steering_promotion.mode == "replace" else 0.0,
                },
            )
        info = {
            "vision_features": vision_features.to_dict(),
            "vision_payload_mode": observation.vision_payload_mode,
            "sensor_pool_rates": sensor_encoding.pool_rates,
            "sensor_metadata": sensor_encoding.metadata,
            "brain_monitored_rates": {str(neuron_id): float(rate) for neuron_id, rate in firing_rates.items()},
            "brain_monitored_voltage": monitored_voltage,
            "brain_monitored_spikes": monitored_spikes,
            "brain_backend_state": backend_state,
            "brain_context": brain_context_info,
            "visual_splice": visual_splice_info,
            "shadow_decodes": shadow_decodes,
            "steering_promotion": promotion_info,
            "motor_signals": {
                "forward_signal": motor_readout.forward_signal,
                "turn_signal": motor_readout.turn_signal,
                "reverse_signal": motor_readout.reverse_signal,
            },
            "motor_readout": motor_readout.neuron_rates,
        }
        return motor_readout, info

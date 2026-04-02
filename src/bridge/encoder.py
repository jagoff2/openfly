from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from body.interfaces import BodyObservation
from vision.feature_extractor import VisionFeatures

@dataclass
class SensorEncoding:
    pool_rates: dict[str, float]
    metadata: dict[str, float]

@dataclass
class EncoderConfig:
    visual_base_hz: float = 0.0
    visual_gain_hz: float = 120.0
    visual_looming_gain_hz: float = 0.0
    mech_base_hz: float = 0.0
    yaw_gain_hz: float = 70.0
    speed_gain_hz: float = 25.0
    contact_gain_hz: float = 15.0
    accel_gain_hz: float = 0.0
    state_gain_hz: float = 0.0
    transition_gain_hz: float = 0.0
    exafference_gain_hz: float = 0.0
    stop_suppression_hz: float = 0.0

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any] | None) -> "EncoderConfig":
        mapping = mapping or {}
        return cls(
            visual_base_hz=float(mapping.get("visual_base_hz", 0.0)),
            visual_gain_hz=float(mapping.get("visual_gain_hz", 120.0)),
            visual_looming_gain_hz=float(mapping.get("visual_looming_gain_hz", 0.0)),
            mech_base_hz=float(mapping.get("mech_base_hz", 0.0)),
            yaw_gain_hz=float(mapping.get("yaw_gain_hz", 70.0)),
            speed_gain_hz=float(mapping.get("speed_gain_hz", 25.0)),
            contact_gain_hz=float(mapping.get("contact_gain_hz", 15.0)),
            accel_gain_hz=float(mapping.get("accel_gain_hz", 0.0)),
            state_gain_hz=float(mapping.get("state_gain_hz", 0.0)),
            transition_gain_hz=float(mapping.get("transition_gain_hz", 0.0)),
            exafference_gain_hz=float(mapping.get("exafference_gain_hz", 0.0)),
            stop_suppression_hz=float(mapping.get("stop_suppression_hz", 0.0)),
        )

class SensoryEncoder:
    def __init__(self, config: EncoderConfig | None = None) -> None:
        self.config = config or EncoderConfig()

    def encode(self, observation: BodyObservation, vision: VisionFeatures) -> SensorEncoding:
        cfg = self.config
        looming_term = max(0.0, float(vision.looming_evidence))
        speed_term = max(0.0, observation.forward_speed)
        contact_term = max(0.0, observation.contact_force)
        accel_term = abs(float(observation.forward_accel))
        state_term = max(0.0, max(float(observation.walk_state), float(observation.behavioral_state_level)))
        transition_term = max(
            0.0,
            float(observation.transition_on),
            float(observation.transition_off),
            float(observation.behavioral_state_transition),
        )
        stop_term = max(0.0, float(observation.stop_state))
        exafference_term = max(0.0, float(observation.exafferent_drive))
        yaw_left = max(0.0, -observation.yaw_rate)
        yaw_right = max(0.0, observation.yaw_rate)
        contact_mech = cfg.mech_base_hz + cfg.contact_gain_hz * contact_term
        motion_mech = (
            cfg.mech_base_hz
            + cfg.speed_gain_hz * speed_term
            + cfg.accel_gain_hz * accel_term
            + cfg.transition_gain_hz * transition_term
        )
        state_mech = (
            cfg.mech_base_hz
            + cfg.state_gain_hz * state_term
            + cfg.exafference_gain_hz * exafference_term
            - cfg.stop_suppression_hz * stop_term
        )
        bilateral_mech = contact_mech + motion_mech + state_mech - 2.0 * cfg.mech_base_hz
        bilateral_mech = max(0.0, float(bilateral_mech))
        pool_rates = {
            "vision_left": cfg.visual_base_hz + cfg.visual_gain_hz * max(0.0, vision.salience_left) + cfg.visual_looming_gain_hz * looming_term,
            "vision_right": cfg.visual_base_hz + cfg.visual_gain_hz * max(0.0, vision.salience_right) + cfg.visual_looming_gain_hz * looming_term,
            "mech_left": bilateral_mech + cfg.yaw_gain_hz * yaw_left,
            "mech_right": bilateral_mech + cfg.yaw_gain_hz * yaw_right,
            "mech_ce_bilateral": max(0.0, float(contact_mech)),
            "mech_f_bilateral": max(0.0, float(motion_mech)),
            "mech_dm_bilateral": max(0.0, float(state_mech)),
        }
        metadata = {
            "vision_balance": vision.balance,
            "forward_salience": vision.forward_salience,
            "flow_balance": float(vision.flow_balance),
            "balance_velocity": float(vision.balance_velocity),
            "forward_salience_velocity": float(vision.forward_salience_velocity),
            "looming_evidence": float(vision.looming_evidence),
            "receding_evidence": float(vision.receding_evidence),
            "forward_speed": observation.forward_speed,
            "forward_accel": float(observation.forward_accel),
            "yaw_rate": observation.yaw_rate,
            "walk_state": float(observation.walk_state),
            "stop_state": float(observation.stop_state),
            "transition_on": float(observation.transition_on),
            "transition_off": float(observation.transition_off),
            "exafferent_drive": float(observation.exafferent_drive),
            "behavioral_state_level": float(observation.behavioral_state_level),
            "behavioral_state_transition": float(observation.behavioral_state_transition),
            "mech_ce_bilateral": float(pool_rates["mech_ce_bilateral"]),
            "mech_f_bilateral": float(pool_rates["mech_f_bilateral"]),
            "mech_dm_bilateral": float(pool_rates["mech_dm_bilateral"]),
            "inferred_left_evidence": vision.inferred_left_evidence,
            "inferred_right_evidence": vision.inferred_right_evidence,
            "inferred_turn_bias": vision.inferred_turn_bias,
            "inferred_turn_confidence": vision.inferred_turn_confidence,
            "inferred_candidate_count": vision.inferred_candidate_count,
        }
        return SensorEncoding(pool_rates=pool_rates, metadata=metadata)

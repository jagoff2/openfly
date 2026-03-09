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
    mech_base_hz: float = 0.0
    yaw_gain_hz: float = 70.0
    speed_gain_hz: float = 25.0
    contact_gain_hz: float = 15.0

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any] | None) -> "EncoderConfig":
        mapping = mapping or {}
        return cls(
            visual_base_hz=float(mapping.get("visual_base_hz", 0.0)),
            visual_gain_hz=float(mapping.get("visual_gain_hz", 120.0)),
            mech_base_hz=float(mapping.get("mech_base_hz", 0.0)),
            yaw_gain_hz=float(mapping.get("yaw_gain_hz", 70.0)),
            speed_gain_hz=float(mapping.get("speed_gain_hz", 25.0)),
            contact_gain_hz=float(mapping.get("contact_gain_hz", 15.0)),
        )

class SensoryEncoder:
    def __init__(self, config: EncoderConfig | None = None) -> None:
        self.config = config or EncoderConfig()

    def encode(self, observation: BodyObservation, vision: VisionFeatures) -> SensorEncoding:
        cfg = self.config
        speed_term = max(0.0, observation.forward_speed)
        contact_term = max(0.0, observation.contact_force)
        yaw_left = max(0.0, -observation.yaw_rate)
        yaw_right = max(0.0, observation.yaw_rate)
        pool_rates = {
            "vision_left": cfg.visual_base_hz + cfg.visual_gain_hz * max(0.0, vision.salience_left),
            "vision_right": cfg.visual_base_hz + cfg.visual_gain_hz * max(0.0, vision.salience_right),
            "mech_left": cfg.mech_base_hz + cfg.yaw_gain_hz * yaw_left + cfg.speed_gain_hz * speed_term + cfg.contact_gain_hz * contact_term,
            "mech_right": cfg.mech_base_hz + cfg.yaw_gain_hz * yaw_right + cfg.speed_gain_hz * speed_term + cfg.contact_gain_hz * contact_term,
        }
        metadata = {
            "vision_balance": vision.balance,
            "forward_salience": vision.forward_salience,
            "flow_balance": float(vision.flow_right - vision.flow_left),
            "forward_speed": observation.forward_speed,
            "yaw_rate": observation.yaw_rate,
            "inferred_left_evidence": vision.inferred_left_evidence,
            "inferred_right_evidence": vision.inferred_right_evidence,
            "inferred_turn_bias": vision.inferred_turn_bias,
            "inferred_turn_confidence": vision.inferred_turn_confidence,
            "inferred_candidate_count": vision.inferred_candidate_count,
        }
        return SensorEncoding(pool_rates=pool_rates, metadata=metadata)

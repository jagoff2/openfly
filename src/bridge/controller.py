from __future__ import annotations

from typing import Any

from body.interfaces import BodyObservation
from bridge.brain_context import BrainContextInjector
from bridge.decoder import MotorDecoder, MotorReadout
from bridge.encoder import SensoryEncoder
from bridge.visual_splice import VisualSpliceInjector
from vision.feature_extractor import RealisticVisionFeatureExtractor

class ClosedLoopBridge:
    def __init__(self, brain_backend: Any, encoder: SensoryEncoder | None = None, decoder: MotorDecoder | None = None, vision_extractor: RealisticVisionFeatureExtractor | None = None, brain_context_injector: BrainContextInjector | None = None, visual_splice_injector: VisualSpliceInjector | None = None) -> None:
        self.brain_backend = brain_backend
        self.encoder = encoder or SensoryEncoder()
        self.decoder = decoder or MotorDecoder()
        self.vision_extractor = vision_extractor or RealisticVisionFeatureExtractor()
        self.brain_context_injector = brain_context_injector or BrainContextInjector()
        self.visual_splice_injector = visual_splice_injector or VisualSpliceInjector()

    def reset(self, seed: int = 0) -> None:
        if hasattr(self.brain_backend, "reset"):
            self.brain_backend.reset(seed)
        if hasattr(self.decoder, "reset"):
            self.decoder.reset()
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
        motor_readout = self.decoder.decode(firing_rates)
        info = {
            "vision_features": vision_features.to_dict(),
            "vision_payload_mode": observation.vision_payload_mode,
            "sensor_pool_rates": sensor_encoding.pool_rates,
            "sensor_metadata": sensor_encoding.metadata,
            "brain_context": brain_context_info,
            "visual_splice": visual_splice_info,
            "motor_signals": {
                "forward_signal": motor_readout.forward_signal,
                "turn_signal": motor_readout.turn_signal,
                "reverse_signal": motor_readout.reverse_signal,
            },
            "motor_readout": motor_readout.neuron_rates,
        }
        return motor_readout, info

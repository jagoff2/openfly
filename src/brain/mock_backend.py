from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from brain.public_ids import MOTOR_READOUT_IDS

@dataclass
class MockWholeBrainBackend:
    dt_ms: float = 0.1
    state: dict[str, float] = field(default_factory=lambda: {"forward": 0.0, "turn": 0.0, "reverse": 0.0})

    def reset(self, seed: int | None = None) -> None:
        self.state = {"forward": 0.0, "turn": 0.0, "reverse": 0.0}

    @property
    def device_name(self) -> str:
        return "mock"

    def benchmark(self, sensor_pool_rates: Mapping[str, float], sim_seconds: float) -> dict[str, float]:
        return {"wall_seconds": sim_seconds / 20.0, "sim_seconds": sim_seconds, "real_time_factor": 20.0}

    def _mean_direct_group(self, direct_input_rates_hz: Mapping[int, float], group_name: str) -> float:
        ids = MOTOR_READOUT_IDS[group_name]
        values = [float(direct_input_rates_hz.get(neuron_id, 0.0)) for neuron_id in ids]
        return float(sum(values) / len(values)) if values else 0.0

    def step(
        self,
        sensor_pool_rates: Mapping[str, float],
        num_steps: int = 1,
        direct_input_rates_hz: Mapping[int, float] | None = None,
        direct_current_by_id: Mapping[int, float] | None = None,
    ) -> dict[int, float]:
        vision_left = float(sensor_pool_rates.get("vision_left", 0.0))
        vision_right = float(sensor_pool_rates.get("vision_right", 0.0))
        mech_left = float(sensor_pool_rates.get("mech_left", 0.0))
        mech_right = float(sensor_pool_rates.get("mech_right", 0.0))
        direct_input_rates_hz = direct_input_rates_hz or {}
        del direct_current_by_id
        steps_scale = max(num_steps, 1) / 20.0
        direct_forward_left = self._mean_direct_group(direct_input_rates_hz, "forward_left")
        direct_forward_right = self._mean_direct_group(direct_input_rates_hz, "forward_right")
        direct_turn_left = self._mean_direct_group(direct_input_rates_hz, "turn_left")
        direct_turn_right = self._mean_direct_group(direct_input_rates_hz, "turn_right")
        forward_drive = 0.002 * (vision_left + vision_right + mech_left + mech_right)
        forward_drive += 0.008 * (direct_forward_left + direct_forward_right)
        turn_drive = 0.003 * ((vision_right + mech_right) - (vision_left + mech_left))
        # Allow asymmetric direct P9 context to create a steering bias in the
        # mock backend so the inferred-P9 bridge can be smoke-tested end-to-end.
        turn_drive += 0.002 * (direct_forward_right - direct_forward_left)
        turn_drive += 0.004 * (direct_turn_right - direct_turn_left)
        reverse_drive = 0.0
        self.state["forward"] = 0.9 * self.state["forward"] + 0.1 * forward_drive * steps_scale
        self.state["turn"] = 0.85 * self.state["turn"] + 0.15 * turn_drive * steps_scale
        self.state["reverse"] = 0.9 * self.state["reverse"] + 0.1 * reverse_drive * steps_scale
        forward_left = max(0.0, 90.0 * self.state["forward"] - 40.0 * self.state["turn"])
        forward_right = max(0.0, 90.0 * self.state["forward"] + 40.0 * self.state["turn"])
        turn_left = max(0.0, -80.0 * self.state["turn"])
        turn_right = max(0.0, 80.0 * self.state["turn"])
        reverse = max(0.0, 40.0 * self.state["reverse"] - 20.0 * self.state["forward"])
        rates = {}
        for neuron_id in MOTOR_READOUT_IDS["forward_left"]:
            rates[neuron_id] = forward_left
        for neuron_id in MOTOR_READOUT_IDS["forward_right"]:
            rates[neuron_id] = forward_right
        for neuron_id in MOTOR_READOUT_IDS["turn_left"]:
            rates[neuron_id] = turn_left
        for neuron_id in MOTOR_READOUT_IDS["turn_right"]:
            rates[neuron_id] = turn_right
        for neuron_id in MOTOR_READOUT_IDS["reverse"]:
            rates[neuron_id] = reverse
        return rates

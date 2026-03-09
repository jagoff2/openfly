from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass
class ZeroWholeBrainBackend:
    dt_ms: float = 0.1

    def reset(self, seed: int | None = None) -> None:
        return None

    @property
    def device_name(self) -> str:
        return "zero"

    def step(
        self,
        sensor_pool_rates: Mapping[str, float],
        num_steps: int = 1,
        direct_input_rates_hz: Mapping[int, float] | None = None,
        direct_current_by_id: Mapping[int, float] | None = None,
    ) -> dict[int, float]:
        del sensor_pool_rates, num_steps, direct_input_rates_hz, direct_current_by_id
        return {}

    def benchmark(self, sensor_pool_rates: Mapping[str, float], sim_seconds: float) -> dict[str, float]:
        del sensor_pool_rates
        return {"wall_seconds": sim_seconds / 20.0, "sim_seconds": sim_seconds, "real_time_factor": 20.0}

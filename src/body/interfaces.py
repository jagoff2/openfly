from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping

@dataclass
class BodyCommand:
    left_drive: float
    right_drive: float

@dataclass
class BodyObservation:
    sim_time: float
    position_xy: tuple[float, float]
    yaw: float
    forward_speed: float
    yaw_rate: float
    contact_force: float
    realistic_vision: Mapping[str, Any] = field(default_factory=dict)
    realistic_vision_array: Any = None
    realistic_vision_features: Mapping[str, Any] | None = None
    realistic_vision_index_cache: Any = None
    realistic_vision_splice_cache: Any = None
    vision_payload_mode: str = "legacy"
    raw_vision: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

class EmbodiedRuntime(ABC):
    timestep: float

    @abstractmethod
    def reset(self, seed: int = 0) -> BodyObservation:
        raise NotImplementedError

    @abstractmethod
    def step(self, command: BodyCommand, num_substeps: int) -> BodyObservation:
        raise NotImplementedError

    def render_frame(self) -> Any:
        return None

    def close(self) -> None:
        return None

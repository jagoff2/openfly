from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Protocol


class ControlCommand(Protocol):
    def to_action(self) -> tuple[float, ...]:
        ...

    def to_log_dict(self) -> dict[str, float]:
        ...

@dataclass
class BodyCommand:
    left_drive: float
    right_drive: float

    def to_action(self) -> tuple[float, float]:
        return (float(self.left_drive), float(self.right_drive))

    def to_log_dict(self) -> dict[str, float]:
        return {
            "left_drive": float(self.left_drive),
            "right_drive": float(self.right_drive),
        }


@dataclass
class HybridDriveCommand:
    left_drive: float
    right_drive: float
    left_amp: float
    right_amp: float
    left_freq_scale: float
    right_freq_scale: float
    retraction_gain: float
    stumbling_gain: float
    reverse_gate: float

    def to_action(self) -> tuple[float, ...]:
        return (
            float(self.left_amp),
            float(self.right_amp),
            float(self.left_freq_scale),
            float(self.right_freq_scale),
            float(self.retraction_gain),
            float(self.stumbling_gain),
            float(self.reverse_gate),
        )

    def to_log_dict(self) -> dict[str, float]:
        return {key: float(value) for key, value in asdict(self).items()}

    def as_legacy_command(self) -> BodyCommand:
        return BodyCommand(left_drive=float(self.left_drive), right_drive=float(self.right_drive))

@dataclass
class BodyObservation:
    sim_time: float
    position_xy: tuple[float, float]
    yaw: float
    forward_speed: float
    yaw_rate: float
    contact_force: float
    forward_accel: float = 0.0
    walk_state: float = 0.0
    stop_state: float = 0.0
    transition_on: float = 0.0
    transition_off: float = 0.0
    exafferent_drive: float = 0.0
    behavioral_state_level: float = 0.0
    behavioral_state_transition: float = 0.0
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
    def step(self, command: ControlCommand, num_substeps: int) -> BodyObservation:
        raise NotImplementedError

    def render_frame(self) -> Any:
        return None

    def close(self) -> None:
        return None

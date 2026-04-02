from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

import numpy as np

from body.interfaces import BodyObservation


@dataclass(frozen=True)
class PublicBodyFeedbackChannels:
    forward_speed: float = 0.0
    contact_force: float = 0.0
    forward_accel: float = 0.0
    walk_state: float = 0.0
    stop_state: float = 0.0
    transition_on: float = 0.0
    transition_off: float = 0.0
    exafferent_drive: float = 0.0
    behavioral_state_level: float = 0.0
    behavioral_state_transition: float = 0.0


def _clip_unit(value: float) -> float:
    return float(max(0.0, min(1.0, float(value))))


def _finite_difference(values: np.ndarray, timebase_s: np.ndarray, index: int) -> float:
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    timebase_s = np.asarray(timebase_s, dtype=np.float32).reshape(-1)
    if values.size == 0 or timebase_s.size == 0:
        return 0.0
    clamped = max(0, min(int(index), values.size - 1))
    if values.size == 1:
        return 0.0
    if clamped == 0:
        dt = max(1e-6, float(timebase_s[1] - timebase_s[0]))
        return float((values[1] - values[0]) / dt)
    if clamped >= values.size - 1:
        dt = max(1e-6, float(timebase_s[-1] - timebase_s[-2]))
        return float((values[-1] - values[-2]) / dt)
    dt = max(1e-6, float(timebase_s[clamped + 1] - timebase_s[clamped - 1]))
    return float((values[clamped + 1] - values[clamped - 1]) / dt)


def _behavioral_state_level(behavioral_state_values: np.ndarray, index: int) -> float:
    matrix = np.asarray(behavioral_state_values, dtype=np.float32)
    if matrix.size == 0:
        return 0.0
    if matrix.ndim != 2:
        raise ValueError("behavioral_state_values must be 2D")
    clamped = max(0, min(int(index), matrix.shape[1] - 1))
    column = np.clip(matrix[:, clamped], a_min=0.0, a_max=1.0)
    if column.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(column), dtype=np.float32)))


def _behavioral_state_transition(behavioral_state_values: np.ndarray, timebase_s: np.ndarray, index: int) -> float:
    matrix = np.asarray(behavioral_state_values, dtype=np.float32)
    if matrix.size == 0:
        return 0.0
    if matrix.ndim != 2:
        raise ValueError("behavioral_state_values must be 2D")
    deltas = [_finite_difference(matrix[row_index], timebase_s, index) for row_index in range(matrix.shape[0])]
    if not deltas:
        return 0.0
    return float(np.mean(np.abs(np.asarray(deltas, dtype=np.float32)), dtype=np.float32))


def public_body_feedback_from_aimon_regressor(
    *,
    timebase_s: np.ndarray,
    regressor_values: np.ndarray,
    sample_index: int,
    forward_speed_scale: float,
    contact_force_scale: float,
) -> PublicBodyFeedbackChannels:
    regressor = np.asarray(regressor_values, dtype=np.float32).reshape(-1)
    if regressor.size == 0:
        return PublicBodyFeedbackChannels()
    clamped = max(0, min(int(sample_index), regressor.size - 1))
    drive_level = _clip_unit(float(regressor[clamped]))
    accel_level = _finite_difference(regressor, timebase_s, clamped)
    transition_on = _clip_unit(max(0.0, accel_level))
    transition_off = _clip_unit(max(0.0, -accel_level))
    return PublicBodyFeedbackChannels(
        forward_speed=float(drive_level * max(0.0, float(forward_speed_scale))),
        contact_force=float(drive_level * max(0.0, float(contact_force_scale))),
        forward_accel=float(accel_level * max(0.0, float(forward_speed_scale))),
        walk_state=drive_level,
        stop_state=_clip_unit(1.0 - drive_level),
        transition_on=transition_on,
        transition_off=transition_off,
        exafferent_drive=drive_level,
        behavioral_state_level=drive_level,
        behavioral_state_transition=0.0,
    )


def public_body_feedback_from_schaffer_covariates(
    *,
    timebase_s: np.ndarray,
    ball_motion_values: np.ndarray,
    behavioral_state_values: np.ndarray,
    sample_index: int,
    forward_speed_scale: float,
    contact_force_scale: float,
) -> PublicBodyFeedbackChannels:
    ball = np.asarray(ball_motion_values, dtype=np.float32).reshape(-1)
    clamped = 0 if ball.size == 0 else max(0, min(int(sample_index), ball.size - 1))
    ball_level = _clip_unit(float(ball[clamped])) if ball.size else 0.0
    accel_level = _finite_difference(ball, timebase_s, clamped) if ball.size else 0.0
    state_level = _behavioral_state_level(behavioral_state_values, clamped)
    state_transition = _behavioral_state_transition(behavioral_state_values, timebase_s, clamped)
    walk_level = _clip_unit(max(ball_level, state_level))
    return PublicBodyFeedbackChannels(
        forward_speed=float(ball_level * max(0.0, float(forward_speed_scale))),
        contact_force=float(walk_level * max(0.0, float(contact_force_scale))),
        forward_accel=float(accel_level * max(0.0, float(forward_speed_scale))),
        walk_state=walk_level,
        stop_state=_clip_unit(1.0 - walk_level),
        transition_on=_clip_unit(max(0.0, accel_level)),
        transition_off=_clip_unit(max(0.0, -accel_level)),
        exafferent_drive=ball_level,
        behavioral_state_level=state_level,
        behavioral_state_transition=_clip_unit(state_transition),
    )


def public_body_observation_from_channels(
    *,
    sim_time_s: float,
    channels: PublicBodyFeedbackChannels,
    position_xy: tuple[float, float] = (0.0, 0.0),
    yaw: float = 0.0,
    yaw_rate: float = 0.0,
    realistic_vision: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> BodyObservation:
    payload = dict(metadata or {})
    payload["public_body_feedback"] = asdict(channels)
    return BodyObservation(
        sim_time=float(sim_time_s),
        position_xy=(float(position_xy[0]), float(position_xy[1])),
        yaw=float(yaw),
        forward_speed=float(channels.forward_speed),
        yaw_rate=float(yaw_rate),
        contact_force=float(channels.contact_force),
        forward_accel=float(channels.forward_accel),
        walk_state=float(channels.walk_state),
        stop_state=float(channels.stop_state),
        transition_on=float(channels.transition_on),
        transition_off=float(channels.transition_off),
        exafferent_drive=float(channels.exafferent_drive),
        behavioral_state_level=float(channels.behavioral_state_level),
        behavioral_state_transition=float(channels.behavioral_state_transition),
        realistic_vision=dict(realistic_vision or {}),
        metadata=payload,
    )

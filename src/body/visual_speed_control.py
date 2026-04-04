from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

import numpy as np

try:
    from flygym.arena import BaseArena, FlatTerrain
    from flygym.arena.tethered import Ball
except ModuleNotFoundError:  # pragma: no cover - exercised only in host envs without FlyGym
    class BaseArena:  # type: ignore[override]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ModuleNotFoundError("flygym is required to instantiate VisualSpeedStripeCorridorArena")

    class FlatTerrain(BaseArena):  # type: ignore[override]
        pass

    class Ball(BaseArena):  # type: ignore[override]
        pass


def wrap_periodic(value: float, lower: float, upper: float) -> float:
    width = float(upper - lower)
    if width <= 0.0:
        raise ValueError("upper must be greater than lower for periodic wrapping")
    return float(((value - lower) % width) + lower)


def direction_label_from_signed_speed(speed_mm_s: float) -> str:
    if speed_mm_s < -1e-6:
        return "front_to_back"
    if speed_mm_s > 1e-6:
        return "back_to_front"
    return "stationary"


def _normalize_block_kind(value: Any) -> str:
    kind = str(value).strip().lower()
    if kind in {"ftb", "front_to_back", "motion_front_to_back"}:
        return "front_to_back"
    if kind in {"btf", "back_to_front", "motion_back_to_front"}:
        return "back_to_front"
    if kind in {"flicker", "counterphase", "counterphase_flicker"}:
        return "counterphase_flicker"
    if kind in {"stationary", "baseline", "control"}:
        return "stationary"
    return kind or "stationary"


def _normalize_block_schedule(
    raw_schedule: Any,
    *,
    default_scene_velocity_mm_s: float,
    default_flicker_hz: float,
) -> tuple[dict[str, float | str | bool], ...]:
    if not isinstance(raw_schedule, (list, tuple)):
        return ()
    normalized: list[dict[str, float | str | bool]] = []
    for idx, entry in enumerate(raw_schedule):
        if isinstance(entry, Mapping):
            item = dict(entry)
        else:
            item = {"kind": entry}
        kind = _normalize_block_kind(item.get("kind", "stationary"))
        sync_to_fly_speed = bool(item.get("sync_to_fly_speed", False))
        scene_velocity = float(item.get("scene_velocity_mm_s", default_scene_velocity_mm_s))
        if kind == "front_to_back":
            scene_velocity = -abs(scene_velocity)
        elif kind == "back_to_front":
            scene_velocity = abs(scene_velocity)
        else:
            scene_velocity = 0.0
        gain = float(item.get("gain", 0.0 if sync_to_fly_speed else 1.0))
        scene_velocity_offset = float(item.get("scene_velocity_offset_mm_s", scene_velocity))
        if kind == "front_to_back":
            scene_velocity_offset = -abs(scene_velocity_offset)
        elif kind == "back_to_front":
            scene_velocity_offset = abs(scene_velocity_offset)
        else:
            scene_velocity_offset = 0.0
        normalized.append(
            {
                "label": str(item.get("label", f"block_{idx:02d}_{kind}")),
                "kind": kind,
                "scene_velocity_mm_s": scene_velocity,
                "scene_velocity_offset_mm_s": scene_velocity_offset,
                "sync_to_fly_speed": sync_to_fly_speed,
                "gain": gain,
                "flicker_hz": float(item.get("flicker_hz", default_flicker_hz)),
            }
        )
    return tuple(normalized)


def wall_world_speed_from_gain(fly_forward_speed_mm_s: float, gain: float) -> float:
    return float((1.0 - float(gain)) * float(fly_forward_speed_mm_s))


def corridor_half_width_at_x(
    x_mm: float,
    *,
    base_half_width_mm: float,
    neck_half_width_mm: float,
    neck_center_x_mm: float,
    neck_half_length_mm: float,
) -> float:
    if neck_half_length_mm <= 0.0:
        return float(base_half_width_mm)
    distance = abs(float(x_mm) - float(neck_center_x_mm))
    if distance >= float(neck_half_length_mm):
        return float(base_half_width_mm)
    alpha = math.cos(0.5 * math.pi * distance / float(neck_half_length_mm)) ** 2
    width_delta = float(base_half_width_mm) - float(neck_half_width_mm)
    return float(base_half_width_mm - width_delta * alpha)


@dataclass(frozen=True)
class VisualSpeedControlConfig:
    enabled: bool = False
    geometry: str = "free_corridor"
    mode: str = "open_loop_drift"
    block_duration_s: float = 0.25
    corridor_length_mm: float = 60.0
    corridor_half_width_mm: float = 6.0
    corridor_neck_half_width_mm: float = 2.5
    corridor_neck_center_x_mm: float = 0.0
    corridor_neck_half_length_mm: float = 10.0
    wall_height_mm: float = 4.0
    wall_thickness_mm: float = 0.35
    stripe_width_mm: float = 1.5
    stripe_wrap_margin_mm: float = 6.0
    pre_scene_velocity_mm_s: float = 0.0
    stimulus_scene_velocity_mm_s: float = -30.0
    stimulus_start_s: float = 0.5
    stimulus_end_s: float = 1.5
    counterphase_flicker_hz: float = 4.0
    gain_baseline: float = 1.0
    gain_stimulus: float = 1.0
    fly_speed_smoothing_alpha: float = 0.2
    treadmill_settle_time_s: float = 0.05
    treadmill_ball_radius_mm: float = 5.390852782067457
    treadmill_ball_pos_mm: tuple[float, float, float] = (
        -0.09867235483,
        -0.05435809692,
        -5.20309506806,
    )
    block_schedule: tuple[dict[str, float | str], ...] = ()

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any] | None) -> "VisualSpeedControlConfig":
        if not mapping:
            return cls(enabled=False)
        raw = dict(mapping)
        stimulus_speed = float(raw.get("stimulus_scene_velocity_mm_s", raw.get("scene_velocity_mm_s", -30.0)))
        pre_speed = float(raw.get("pre_scene_velocity_mm_s", 0.0))
        direction = str(raw.get("scene_motion_direction", "")).strip().lower()
        if direction in {"ftb", "front_to_back"}:
            stimulus_speed = -abs(stimulus_speed)
            pre_speed = -abs(pre_speed) if pre_speed != 0.0 else 0.0
        elif direction in {"btf", "back_to_front"}:
            stimulus_speed = abs(stimulus_speed)
            pre_speed = abs(pre_speed) if pre_speed != 0.0 else 0.0
        return cls(
            enabled=bool(raw.get("enabled", True)),
            geometry=str(raw.get("geometry", "free_corridor")),
            mode=str(raw.get("mode", "open_loop_drift")),
            block_duration_s=float(raw.get("block_duration_s", 0.25)),
            corridor_length_mm=float(raw.get("corridor_length_mm", 60.0)),
            corridor_half_width_mm=float(raw.get("corridor_half_width_mm", 6.0)),
            corridor_neck_half_width_mm=float(raw.get("corridor_neck_half_width_mm", 2.5)),
            corridor_neck_center_x_mm=float(raw.get("corridor_neck_center_x_mm", 0.0)),
            corridor_neck_half_length_mm=float(raw.get("corridor_neck_half_length_mm", 10.0)),
            wall_height_mm=float(raw.get("wall_height_mm", 4.0)),
            wall_thickness_mm=float(raw.get("wall_thickness_mm", 0.35)),
            stripe_width_mm=float(raw.get("stripe_width_mm", 1.5)),
            stripe_wrap_margin_mm=float(raw.get("stripe_wrap_margin_mm", 6.0)),
            pre_scene_velocity_mm_s=pre_speed,
            stimulus_scene_velocity_mm_s=stimulus_speed,
            stimulus_start_s=float(raw.get("stimulus_start_s", 0.5)),
            stimulus_end_s=float(raw.get("stimulus_end_s", 1.5)),
            counterphase_flicker_hz=float(raw.get("counterphase_flicker_hz", 4.0)),
            gain_baseline=float(raw.get("gain_baseline", 1.0)),
            gain_stimulus=float(raw.get("gain_stimulus", 1.0)),
            fly_speed_smoothing_alpha=float(raw.get("fly_speed_smoothing_alpha", 0.2)),
            treadmill_settle_time_s=float(raw.get("treadmill_settle_time_s", 0.05)),
            treadmill_ball_radius_mm=float(raw.get("treadmill_ball_radius_mm", 5.390852782067457)),
            treadmill_ball_pos_mm=tuple(
                float(value)
                for value in raw.get(
                    "treadmill_ball_pos_mm",
                    (-0.09867235483, -0.05435809692, -5.20309506806),
                )
            ),
            block_schedule=_normalize_block_schedule(
                raw.get("block_schedule", ()),
                default_scene_velocity_mm_s=stimulus_speed,
                default_flicker_hz=float(raw.get("counterphase_flicker_hz", 4.0)),
            ),
        )

    @property
    def x_min_mm(self) -> float:
        return float(-0.5 * self.corridor_length_mm - self.stripe_wrap_margin_mm)

    @property
    def x_max_mm(self) -> float:
        return float(0.5 * self.corridor_length_mm + self.stripe_wrap_margin_mm)

    def stimulus_active(self, time_s: float) -> bool:
        if self.mode == "interleaved_blocks":
            block = self.block_for_time(time_s)
            return bool(block and str(block.get("kind", "stationary")) != "stationary")
        if self.mode == "hourglass":
            return True
        return bool(self.stimulus_start_s <= float(time_s) <= self.stimulus_end_s)

    def gain_for_time(self, time_s: float) -> float:
        if self.mode == "interleaved_blocks":
            block = self.block_for_time(time_s)
            if block and bool(block.get("sync_to_fly_speed", False)):
                return float(block.get("gain", 0.0))
            return 1.0
        if self.mode != "closed_loop_gain":
            return 1.0
        return float(self.gain_stimulus if self.stimulus_active(time_s) else self.gain_baseline)

    def half_width_at_x(self, x_mm: float) -> float:
        if self.mode != "hourglass":
            return float(self.corridor_half_width_mm)
        return corridor_half_width_at_x(
            x_mm,
            base_half_width_mm=self.corridor_half_width_mm,
            neck_half_width_mm=self.corridor_neck_half_width_mm,
            neck_center_x_mm=self.corridor_neck_center_x_mm,
            neck_half_length_mm=self.corridor_neck_half_length_mm,
        )

    def block_for_time(self, time_s: float) -> Mapping[str, float | str] | None:
        if self.mode != "interleaved_blocks" or not self.block_schedule:
            return None
        block_duration = max(float(self.block_duration_s), 1e-6)
        index = int(max(float(time_s), 0.0) // block_duration)
        if index >= len(self.block_schedule):
            index = len(self.block_schedule) - 1
        return self.block_schedule[index]

    def block_index_for_time(self, time_s: float) -> int:
        if self.mode != "interleaved_blocks" or not self.block_schedule:
            return -1
        block_duration = max(float(self.block_duration_s), 1e-6)
        index = int(max(float(time_s), 0.0) // block_duration)
        return min(index, len(self.block_schedule) - 1)

    def block_local_time_s(self, time_s: float) -> float:
        if self.mode != "interleaved_blocks" or not self.block_schedule:
            return 0.0
        block_duration = max(float(self.block_duration_s), 1e-6)
        return float(max(float(time_s), 0.0) % block_duration)

    def counterphase_flicker_phase_offset_mm(self, time_s: float) -> float:
        if self.mode != "interleaved_blocks":
            return 0.0
        block = self.block_for_time(time_s)
        if not block or str(block.get("kind", "")) != "counterphase_flicker":
            return 0.0
        flicker_hz = max(float(block.get("flicker_hz", self.counterphase_flicker_hz)), 1e-6)
        phase_state = int(math.floor(float(time_s) * 2.0 * flicker_hz)) % 2
        return 0.5 * float(self.stripe_width_mm) if phase_state else 0.0

    def scene_world_speed_mm_s(self, time_s: float, fly_forward_speed_mm_s: float) -> float:
        if self.mode == "interleaved_blocks":
            block = self.block_for_time(time_s)
            if block is None:
                return 0.0
            kind = str(block.get("kind", "stationary"))
            if bool(block.get("sync_to_fly_speed", False)):
                base_speed = wall_world_speed_from_gain(
                    fly_forward_speed_mm_s,
                    float(block.get("gain", 0.0)),
                )
                offset_speed = float(block.get("scene_velocity_offset_mm_s", 0.0))
                if kind in {"front_to_back", "back_to_front"}:
                    return float(base_speed + offset_speed)
                return float(base_speed)
            if kind in {"front_to_back", "back_to_front"}:
                return float(block.get("scene_velocity_mm_s", 0.0))
            return 0.0
        if self.mode == "closed_loop_gain":
            return wall_world_speed_from_gain(fly_forward_speed_mm_s, self.gain_for_time(time_s))
        if self.mode == "hourglass":
            return 0.0
        return float(self.stimulus_scene_velocity_mm_s if self.stimulus_active(time_s) else self.pre_scene_velocity_mm_s)


class VisualSpeedStripeCorridorArena(FlatTerrain):
    def __init__(self, config: VisualSpeedControlConfig) -> None:
        super().__init__(size=(300, 300), friction=(1, 0.005, 0.0001), ground_alpha=1.0)
        self.config = config
        self.curr_time = 0.0
        self.scene_offset_x_mm = 0.0
        self.filtered_fly_forward_speed_mm_s = 0.0
        self.fly_x_mm = 0.0
        self.fly_y_mm = 0.0
        self.fly_yaw_rad = 0.0
        self.current_scene_world_speed_mm_s = 0.0
        self.current_flicker_phase_mm = 0.0

        self._base_stripe_centers = np.arange(
            self.config.x_min_mm + 0.5 * self.config.stripe_width_mm,
            self.config.x_max_mm,
            self.config.stripe_width_mm,
            dtype=float,
        )
        self._left_stripe_bodies: list[Any] = []
        self._right_stripe_bodies: list[Any] = []
        self._build_stripes()

    def _build_stripes(self) -> None:
        z_pos = 0.5 * self.config.wall_height_mm
        stripe_half_x = 0.5 * self.config.stripe_width_mm
        stripe_half_y = 0.5 * self.config.wall_thickness_mm
        stripe_half_z = 0.5 * self.config.wall_height_mm
        for idx, center_x in enumerate(self._base_stripe_centers):
            color = (0.05, 0.05, 0.05, 1.0) if idx % 2 == 0 else (0.95, 0.95, 0.95, 1.0)
            for side, sign, body_list in (("left", -1.0, self._left_stripe_bodies), ("right", 1.0, self._right_stripe_bodies)):
                half_width = self.config.half_width_at_x(center_x)
                body = self.root_element.worldbody.add(
                    "body",
                    name=f"{side}_stripe_{idx}",
                    mocap=True,
                    pos=(center_x, sign * half_width, z_pos),
                )
                body.add(
                    "geom",
                    type="box",
                    size=(stripe_half_x, stripe_half_y, stripe_half_z),
                    rgba=color,
                )
                body_list.append(body)

    def get_spawn_position(
        self, rel_pos: np.ndarray, rel_angle: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        return rel_pos, rel_angle

    def reset(self, physics: Any, seed: int = 0) -> None:
        del seed
        self.curr_time = 0.0
        self.scene_offset_x_mm = 0.0
        self.filtered_fly_forward_speed_mm_s = 0.0
        self.current_scene_world_speed_mm_s = 0.0
        self._apply_stripe_positions(physics)

    def notify_fly_state(self, *, position_xy: tuple[float, float], yaw_rad: float, forward_velocity_x_mm_s: float) -> None:
        alpha = float(np.clip(self.config.fly_speed_smoothing_alpha, 0.0, 1.0))
        self.filtered_fly_forward_speed_mm_s = float(
            (1.0 - alpha) * self.filtered_fly_forward_speed_mm_s + alpha * float(forward_velocity_x_mm_s)
        )
        self.fly_x_mm = float(position_xy[0])
        self.fly_y_mm = float(position_xy[1])
        self.fly_yaw_rad = float(yaw_rad)

    def _apply_stripe_positions(self, physics: Any) -> None:
        wrapped_x = [
            wrap_periodic(center_x + self.scene_offset_x_mm + self.current_flicker_phase_mm, self.config.x_min_mm, self.config.x_max_mm)
            for center_x in self._base_stripe_centers
        ]
        z_pos = 0.5 * self.config.wall_height_mm
        for idx, x_pos in enumerate(wrapped_x):
            half_width = self.config.half_width_at_x(x_pos)
            physics.bind(self._left_stripe_bodies[idx]).mocap_pos = (x_pos, -half_width, z_pos)
            physics.bind(self._right_stripe_bodies[idx]).mocap_pos = (x_pos, half_width, z_pos)

    def step(self, dt: float, physics: Any, *args, **kwargs) -> None:
        del args, kwargs
        self.current_scene_world_speed_mm_s = self.config.scene_world_speed_mm_s(
            self.curr_time,
            self.filtered_fly_forward_speed_mm_s,
        )
        self.current_flicker_phase_mm = self.config.counterphase_flicker_phase_offset_mm(self.curr_time)
        self.scene_offset_x_mm += float(self.current_scene_world_speed_mm_s) * float(dt)
        self.curr_time += float(dt)
        self._apply_stripe_positions(physics)

    def metadata(self) -> dict[str, float | str | bool]:
        stimulus_active = self.config.stimulus_active(self.curr_time)
        gain = self.config.gain_for_time(self.curr_time)
        effective_visual_speed_mm_s = float(self.current_scene_world_speed_mm_s - self.filtered_fly_forward_speed_mm_s)
        half_width = self.config.half_width_at_x(self.fly_x_mm)
        block = self.config.block_for_time(self.curr_time)
        return {
            "enabled": True,
            "geometry": self.config.geometry,
            "mode": self.config.mode,
            "stimulus_active": bool(stimulus_active),
            "scene_world_speed_mm_s": float(self.current_scene_world_speed_mm_s),
            "scene_world_motion_direction": direction_label_from_signed_speed(self.current_scene_world_speed_mm_s),
            "effective_visual_speed_mm_s": effective_visual_speed_mm_s,
            "effective_visual_motion_direction": direction_label_from_signed_speed(effective_visual_speed_mm_s),
            "block_index": float(self.config.block_index_for_time(self.curr_time)),
            "block_local_time_s": float(self.config.block_local_time_s(self.curr_time)),
            "block_kind": str(block.get("kind", "stationary")) if block else "none",
            "block_label": str(block.get("label", "")) if block else "",
            "block_sync_to_fly_speed": bool(block.get("sync_to_fly_speed", False)) if block else False,
            "block_scene_velocity_offset_mm_s": float(block.get("scene_velocity_offset_mm_s", 0.0)) if block else 0.0,
            "flicker_phase_offset_mm": float(getattr(self, "current_flicker_phase_mm", 0.0)),
            "gain": float(gain),
            "fly_forward_speed_mm_s_filtered": float(self.filtered_fly_forward_speed_mm_s),
            "fly_x_mm": float(self.fly_x_mm),
            "fly_y_mm": float(self.fly_y_mm),
            "fly_yaw_rad": float(self.fly_yaw_rad),
            "track_x_mm": float(self.fly_x_mm),
            "speed_source": "body_translation",
            "corridor_half_width_mm_at_fly": float(half_width),
            "corridor_neck_half_width_mm": float(self.config.corridor_neck_half_width_mm),
            "corridor_base_half_width_mm": float(self.config.corridor_half_width_mm),
        }


class VisualSpeedBallTreadmillArena(Ball):
    def __init__(self, config: VisualSpeedControlConfig) -> None:
        super().__init__(
            radius=float(config.treadmill_ball_radius_mm),
            ball_pos=tuple(float(value) for value in config.treadmill_ball_pos_mm),
        )
        self.config = config
        self.curr_time = 0.0
        self.scene_offset_x_mm = 0.0
        self.virtual_track_x_mm = 0.0
        self.filtered_fly_forward_speed_mm_s = 0.0
        self.measured_forward_speed_mm_s = 0.0
        self.fly_x_mm = 0.0
        self.fly_y_mm = 0.0
        self.fly_yaw_rad = 0.0
        self.current_scene_world_speed_mm_s = 0.0
        self.current_flicker_phase_mm = 0.0
        self._settle_until_s = float(max(self.config.treadmill_settle_time_s, 0.0))
        self._treadmill_joint = self.root_element.find("joint", "treadmill_joint")
        self._treadmill_geom = self.root_element.find("geom", "treadmill")
        self._treadmill_visual_rgba: np.ndarray | None = None
        self._make_treadmill_visually_neutral()

        self._base_stripe_centers = np.arange(
            self.config.x_min_mm + 0.5 * self.config.stripe_width_mm,
            self.config.x_max_mm,
            self.config.stripe_width_mm,
            dtype=float,
        )
        self._left_stripe_bodies: list[Any] = []
        self._right_stripe_bodies: list[Any] = []
        self._build_stripes()

    def _zero_treadmill_joint_state(self, physics: Any) -> None:
        if self._treadmill_joint is None:
            return
        bound_joint = physics.bind(self._treadmill_joint)
        if hasattr(bound_joint, "qvel"):
            bound_joint.qvel[:] = 0.0
        if hasattr(bound_joint, "qacc"):
            bound_joint.qacc[:] = 0.0

    def _build_stripes(self) -> None:
        z_pos = 0.5 * self.config.wall_height_mm
        stripe_half_x = 0.5 * self.config.stripe_width_mm
        stripe_half_y = 0.5 * self.config.wall_thickness_mm
        stripe_half_z = 0.5 * self.config.wall_height_mm
        for idx, center_x in enumerate(self._base_stripe_centers):
            color = (0.05, 0.05, 0.05, 1.0) if idx % 2 == 0 else (0.95, 0.95, 0.95, 1.0)
            for side, sign, body_list in (("left", -1.0, self._left_stripe_bodies), ("right", 1.0, self._right_stripe_bodies)):
                half_width = self.config.half_width_at_x(center_x)
                body = self.root_element.worldbody.add(
                    "body",
                    name=f"{side}_stripe_{idx}",
                    mocap=True,
                    pos=(center_x, sign * half_width, z_pos),
                )
                body.add(
                    "geom",
                    type="box",
                    size=(stripe_half_x, stripe_half_y, stripe_half_z),
                    rgba=color,
                )
                body_list.append(body)

    def _make_treadmill_visually_neutral(self) -> None:
        if self._treadmill_geom is None:
            return
        # Keep the treadmill mechanically active but remove the spinning checker
        # from human-facing renders. The fly-eye render hook still hides it
        # explicitly at runtime.
        self._treadmill_geom.rgba = (0.35, 0.35, 0.35, 0.0)

    def _measure_forward_speed_mm_s(self, physics: Any) -> float:
        if self._treadmill_joint is None:
            return 0.0
        omega = np.asarray(physics.bind(self._treadmill_joint).qvel, dtype=float).reshape(-1)
        if omega.size < 2:
            return 0.0
        surface_velocity_xy = np.array(
            [
                float(omega[1]) * float(self.radius),
                -float(omega[0]) * float(self.radius),
            ],
            dtype=float,
        )
        forward_axis = np.array(
            [
                math.cos(self.fly_yaw_rad),
                math.sin(self.fly_yaw_rad),
            ],
            dtype=float,
        )
        return float(np.dot(surface_velocity_xy, forward_axis))

    def _scene_track_offset_x_mm(self) -> float:
        if self.config.mode == "open_loop_drift":
            return 0.0
        return float(self.virtual_track_x_mm)

    def _relative_world_x(self, center_x_mm: float) -> float:
        return float(
            center_x_mm
            + self.scene_offset_x_mm
            + float(getattr(self, "current_flicker_phase_mm", 0.0))
            - self._scene_track_offset_x_mm()
        )

    def _effective_visual_speed_mm_s(self) -> float:
        if self.config.mode == "open_loop_drift":
            return float(self.current_scene_world_speed_mm_s)
        return float(self.current_scene_world_speed_mm_s - self.filtered_fly_forward_speed_mm_s)

    def _apply_stripe_positions(self, physics: Any) -> None:
        wrapped_x = [
            wrap_periodic(self._relative_world_x(center_x), self.config.x_min_mm, self.config.x_max_mm)
            for center_x in self._base_stripe_centers
        ]
        z_pos = 0.5 * self.config.wall_height_mm
        for idx, x_pos in enumerate(wrapped_x):
            half_width = self.config.half_width_at_x(x_pos)
            physics.bind(self._left_stripe_bodies[idx]).mocap_pos = (x_pos, -half_width, z_pos)
            physics.bind(self._right_stripe_bodies[idx]).mocap_pos = (x_pos, half_width, z_pos)

    def reset(self, physics: Any, seed: int = 0) -> None:
        del seed
        self.curr_time = 0.0
        self.scene_offset_x_mm = 0.0
        self.virtual_track_x_mm = 0.0
        self.filtered_fly_forward_speed_mm_s = 0.0
        self.measured_forward_speed_mm_s = 0.0
        self.current_scene_world_speed_mm_s = 0.0
        self.current_flicker_phase_mm = 0.0
        self._settle_until_s = float(max(self.config.treadmill_settle_time_s, 0.0))
        self._treadmill_visual_rgba = None
        super().reset(physics)
        self._zero_treadmill_joint_state(physics)
        self._apply_stripe_positions(physics)

    def notify_fly_state(self, *, position_xy: tuple[float, float], yaw_rad: float, forward_velocity_x_mm_s: float) -> None:
        del forward_velocity_x_mm_s
        self.fly_x_mm = float(position_xy[0])
        self.fly_y_mm = float(position_xy[1])
        self.fly_yaw_rad = float(yaw_rad)

    def step(self, dt: float, physics: Any, *args, **kwargs) -> None:
        del args, kwargs
        in_settle_window = float(self.curr_time) <= float(self._settle_until_s)
        if in_settle_window:
            self._zero_treadmill_joint_state(physics)
        measured_speed = 0.0 if in_settle_window else self._measure_forward_speed_mm_s(physics)
        alpha = float(np.clip(self.config.fly_speed_smoothing_alpha, 0.0, 1.0))
        self.measured_forward_speed_mm_s = measured_speed
        self.filtered_fly_forward_speed_mm_s = float(
            (1.0 - alpha) * self.filtered_fly_forward_speed_mm_s + alpha * measured_speed
        )
        self.current_scene_world_speed_mm_s = self.config.scene_world_speed_mm_s(
            self.curr_time,
            self.filtered_fly_forward_speed_mm_s,
        )
        self.current_flicker_phase_mm = self.config.counterphase_flicker_phase_offset_mm(self.curr_time)
        self.scene_offset_x_mm += float(self.current_scene_world_speed_mm_s) * float(dt)
        self.virtual_track_x_mm += float(self.filtered_fly_forward_speed_mm_s) * float(dt)
        self.curr_time += float(dt)
        self._apply_stripe_positions(physics)

    def stabilize_after_physics_step(self, physics: Any) -> None:
        if float(self.curr_time) <= float(self._settle_until_s):
            self._zero_treadmill_joint_state(physics)

    def pre_visual_render_hook(self, physics: Any, *args, **kwargs) -> None:
        del args, kwargs
        if self._treadmill_geom is None:
            return
        bound_geom = physics.bind(self._treadmill_geom)
        current_rgba = np.asarray(bound_geom.rgba, dtype=float).copy()
        if current_rgba.shape[0] < 4:
            return
        self._treadmill_visual_rgba = current_rgba
        hidden_rgba = current_rgba.copy()
        hidden_rgba[3] = 0.0
        bound_geom.rgba = hidden_rgba

    def post_visual_render_hook(self, physics: Any, *args, **kwargs) -> None:
        del args, kwargs
        if self._treadmill_geom is None or self._treadmill_visual_rgba is None:
            return
        physics.bind(self._treadmill_geom).rgba = self._treadmill_visual_rgba.copy()
        self._treadmill_visual_rgba = None

    def metadata(self) -> dict[str, float | str | bool]:
        stimulus_active = self.config.stimulus_active(self.curr_time)
        gain = self.config.gain_for_time(self.curr_time)
        effective_visual_speed_mm_s = self._effective_visual_speed_mm_s()
        half_width = self.config.half_width_at_x(self.virtual_track_x_mm)
        block = self.config.block_for_time(self.curr_time)
        settle_until_s = float(getattr(self, "_settle_until_s", 0.0))
        in_settle_window = float(self.curr_time) <= settle_until_s
        return {
            "enabled": True,
            "geometry": self.config.geometry,
            "mode": self.config.mode,
            "stimulus_active": bool(stimulus_active),
            "measurement_valid": not in_settle_window,
            "in_settle_window": bool(in_settle_window),
            "settle_remaining_s": float(max(0.0, settle_until_s - float(self.curr_time))),
            "scene_world_speed_mm_s": float(self.current_scene_world_speed_mm_s),
            "scene_world_motion_direction": direction_label_from_signed_speed(self.current_scene_world_speed_mm_s),
            "effective_visual_speed_mm_s": effective_visual_speed_mm_s,
            "effective_visual_motion_direction": direction_label_from_signed_speed(effective_visual_speed_mm_s),
            "retinal_slip_mm_s": effective_visual_speed_mm_s,
            "retinal_slip_motion_direction": direction_label_from_signed_speed(effective_visual_speed_mm_s),
            "block_index": float(self.config.block_index_for_time(self.curr_time)),
            "block_local_time_s": float(self.config.block_local_time_s(self.curr_time)),
            "block_kind": str(block.get("kind", "stationary")) if block else "none",
            "block_label": str(block.get("label", "")) if block else "",
            "block_sync_to_fly_speed": bool(block.get("sync_to_fly_speed", False)) if block else False,
            "block_scene_velocity_offset_mm_s": float(block.get("scene_velocity_offset_mm_s", 0.0)) if block else 0.0,
            "flicker_phase_offset_mm": float(getattr(self, "current_flicker_phase_mm", 0.0)),
            "gain": float(gain),
            "fly_forward_speed_mm_s_filtered": float(self.filtered_fly_forward_speed_mm_s),
            "fly_forward_speed_mm_s_measured": float(self.measured_forward_speed_mm_s),
            "fly_x_mm": float(self.fly_x_mm),
            "fly_y_mm": float(self.fly_y_mm),
            "fly_yaw_rad": float(self.fly_yaw_rad),
            "track_x_mm": float(self.virtual_track_x_mm),
            "speed_source": "treadmill_ball",
            "corridor_half_width_mm_at_fly": float(half_width),
            "corridor_neck_half_width_mm": float(self.config.corridor_neck_half_width_mm),
            "corridor_base_half_width_mm": float(self.config.corridor_half_width_mm),
        }

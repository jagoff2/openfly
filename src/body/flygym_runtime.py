from __future__ import annotations

from dataclasses import dataclass
import math
import os
from pathlib import Path
import types
from typing import Any

import numpy as np

from body.interfaces import BodyCommand, BodyObservation, EmbodiedRuntime

@dataclass
class FlyGymRealisticVisionRuntime(EmbodiedRuntime):
    timestep: float = 1e-4
    terrain_type: str = "flat"
    leading_fly_speed: float = 15.0
    leading_fly_radius: float = 10.0
    target_fly_enabled: bool = True
    target_initial_phase_rad: float = 0.0
    target_angular_direction: float = 1.0
    output_dir: str | Path = "outputs/demos"
    camera_fps: int = 24
    force_cpu_vision: bool = False
    vision_payload_mode: str = "legacy"

    def __post_init__(self) -> None:
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._setup_imports()
        self._build_simulation()
        self._last_frame = None
        self._last_position = None
        self._last_yaw = 0.0
        self._time = 0.0

    def _setup_imports(self) -> None:
        if self.force_cpu_vision:
            # The packaged FlyVis model defaults to CUDA if a GPU is visible.
            # Hiding GPUs keeps the realistic-vision path on CPU for WSL runs
            # where the available PyTorch wheel does not support the local GPU.
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
        from flygym import Camera, SingleFlySimulation
        from flygym.arena import FlatTerrain
        from flygym.examples.vision import MovingFlyArena
        from body.brain_only_realistic_vision_fly import BrainOnlyRealisticVisionFly
        from body.fast_realistic_vision_fly import FastRealisticVisionFly
        self.Camera = Camera
        self.SingleFlySimulation = SingleFlySimulation
        self.FlatTerrain = FlatTerrain
        self.MovingFlyArena = MovingFlyArena
        self.RealisticVisionFly = BrainOnlyRealisticVisionFly
        self.FastRealisticVisionFly = FastRealisticVisionFly

    def _build_simulation(self) -> None:
        contact_sensor_placements = [f"{leg}{segment}" for leg in ["LF", "LM", "LH", "RF", "RM", "RH"] for segment in ["Tibia", "Tarsus1", "Tarsus2", "Tarsus3", "Tarsus4", "Tarsus5"]]
        if self.target_fly_enabled:
            self.arena = self.MovingFlyArena(
                move_speed=self.leading_fly_speed,
                radius=self.leading_fly_radius,
                terrain_type=self.terrain_type,
            )
        else:
            if self.terrain_type != "flat":
                raise ValueError("Target-free runs currently support only `terrain_type: flat`.")
            self.arena = self.FlatTerrain()
        self._target_angular_speed = 0.0
        if self.target_fly_enabled:
            radius = max(float(self.leading_fly_radius), 1e-9)
            direction = 1.0 if float(self.target_angular_direction) >= 0.0 else -1.0
            self._target_angular_speed = direction * abs(float(self.leading_fly_speed)) / radius
        fly_cls = self.FastRealisticVisionFly if self.vision_payload_mode == "fast" else self.RealisticVisionFly
        self.fly = fly_cls(contact_sensor_placements=contact_sensor_placements, enable_adhesion=True, vision_refresh_rate=500, neck_kp=500, spawn_pos=(0.0, 0.0, 0.3))
        cam_params = {"mode": "fixed", "pos": (5, 0, 35), "euler": (0, 0, 0), "fovy": 45}
        self.camera = self.Camera(attachment_point=self.arena.root_element.worldbody, camera_name="birdeye_cam", camera_parameters=cam_params, play_speed=0.2, window_size=(800, 608), fps=self.camera_fps)
        self.sim = self.SingleFlySimulation(fly=self.fly, cameras=[self.camera], arena=self.arena)
        if self.target_fly_enabled and hasattr(self.arena, "freejoint"):
            self.arena.step = types.MethodType(self._controlled_target_step, self.arena)

    def _apply_target_pose(self, theta: float, physics: Any | None = None) -> None:
        if not self.target_fly_enabled or not hasattr(self.arena, "freejoint"):
            return
        physics = physics or self.sim.physics
        radius = float(self.arena.radius)
        height = float(self.arena.init_fly_pos[2])
        self.arena.fly_pos = np.array(
            [
                radius * math.sin(theta),
                radius * math.cos(theta),
                height,
            ],
            dtype=float,
        )
        heading_x = radius * math.cos(theta) * float(self._target_angular_speed)
        heading_y = -radius * math.sin(theta) * float(self._target_angular_speed)
        heading = math.atan2(heading_y, heading_x) if abs(heading_x) + abs(heading_y) > 1e-12 else 0.0
        quat = np.exp(1j * heading / 2.0)
        qpos = (*self.arena.fly_pos, float(quat.real), 0.0, 0.0, float(quat.imag))
        physics.bind(self.arena.freejoint).qpos = qpos
        physics.bind(self.arena.freejoint).qvel[:] = 0
        self.arena._prev_pos = complex(*self.arena.fly_pos[:2])

    def _controlled_target_step(self, arena: Any, dt: float, physics: Any) -> None:
        del arena
        theta = float(self.target_initial_phase_rad) + float(self._target_angular_speed) * float(self.arena.curr_time)
        self._apply_target_pose(theta, physics)
        self.arena.curr_time += dt

    def _target_state_metadata(self, position_xy: tuple[float, float], yaw: float) -> dict[str, Any]:
        if not self.target_fly_enabled or not hasattr(self.arena, "freejoint"):
            return {"enabled": False}
        qpos = np.asarray(self.sim.physics.bind(self.arena.freejoint).qpos, dtype=float)
        qvel = np.asarray(self.sim.physics.bind(self.arena.freejoint).qvel, dtype=float)
        target_x, target_y, target_z = (float(qpos[0]), float(qpos[1]), float(qpos[2]))
        qw, qx, qy, qz = (float(qpos[3]), float(qpos[4]), float(qpos[5]), float(qpos[6]))
        target_yaw = float(math.atan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz)))
        rel_x = target_x - float(position_xy[0])
        rel_y = target_y - float(position_xy[1])
        target_bearing_world = float(math.atan2(rel_y, rel_x))
        target_bearing_body = float((target_bearing_world - yaw + math.pi) % (2.0 * math.pi) - math.pi)
        return {
            "enabled": True,
            "position_x": target_x,
            "position_y": target_y,
            "position_z": target_z,
            "yaw": target_yaw,
            "velocity_x": float(qvel[0]) if qvel.size > 0 else 0.0,
            "velocity_y": float(qvel[1]) if qvel.size > 1 else 0.0,
            "distance": float(math.hypot(rel_x, rel_y)),
            "bearing_world": target_bearing_world,
            "bearing_body": target_bearing_body,
            "initial_phase_rad": float(self.target_initial_phase_rad),
            "angular_direction": 1.0 if float(self.target_angular_direction) >= 0.0 else -1.0,
        }

    def reset(self, seed: int = 0) -> BodyObservation:
        obs, info = self.sim.reset(seed=seed)
        self._time = 0.0
        if self.target_fly_enabled and hasattr(self.arena, "curr_time"):
            self.arena.curr_time = 0.0
            self._apply_target_pose(float(self.target_initial_phase_rad))
        self._last_position = np.array(obs["fly"][0, :2], dtype=float)
        self._last_yaw = float(np.arctan2(obs["fly_orientation"][1], obs["fly_orientation"][0])) if "fly_orientation" in obs else 0.0
        self._last_frame = self.sim.render()[0]
        return self._make_observation(obs, info, forward_speed=0.0, yaw_rate=0.0)

    def step(self, command: BodyCommand, num_substeps: int) -> BodyObservation:
        latest_obs = None
        latest_info = None
        for _ in range(max(1, num_substeps)):
            latest_obs, _, _, _, latest_info = self.sim.step(action=np.array([command.left_drive, command.right_drive], dtype=float))
            self._time += self.timestep
            rendered = self.sim.render()[0]
            if rendered is not None:
                self._last_frame = rendered
        position = np.array(latest_obs["fly"][0, :2], dtype=float)
        yaw = float(np.arctan2(latest_obs["fly_orientation"][1], latest_obs["fly_orientation"][0])) if "fly_orientation" in latest_obs else self._last_yaw
        forward_speed = float(np.linalg.norm(position - self._last_position) / (max(1, num_substeps) * self.timestep))
        yaw_rate = float((yaw - self._last_yaw) / (max(1, num_substeps) * self.timestep))
        self._last_position = position
        self._last_yaw = yaw
        return self._make_observation(latest_obs, latest_info, forward_speed=forward_speed, yaw_rate=yaw_rate)

    def _make_observation(self, obs: dict[str, Any], info: dict[str, Any], forward_speed: float, yaw_rate: float) -> BodyObservation:
        realistic_vision = {}
        nn_activities = info.get("nn_activities") if info else None
        if nn_activities is not None:
            for key in nn_activities.keys():
                realistic_vision[key] = np.asarray(nn_activities[key])
        realistic_vision_array = obs.get("nn_activities_arr") if obs else None
        if realistic_vision_array is None and info:
            realistic_vision_array = info.get("nn_activities_arr")
        realistic_vision_features = info.get("vision_features_fast") if info else None
        realistic_vision_index_cache = info.get("vision_index_cache") if info else None
        realistic_vision_splice_cache = info.get("vision_splice_cache") if info else None
        vision_payload_mode = info.get("vision_payload_mode", self.vision_payload_mode) if info else self.vision_payload_mode
        contact_force = float(np.linalg.norm(obs["contact_forces"])) if "contact_forces" in obs else 0.0
        metadata = {
            "vision_updated": bool(info.get("vision_updated", False)) if info else False,
            "vision_payload_mode": vision_payload_mode,
            "target_fly_enabled": self.target_fly_enabled,
            "target_state": self._target_state_metadata((float(obs["fly"][0, 0]), float(obs["fly"][0, 1])), float(self._last_yaw)),
        }
        return BodyObservation(
            sim_time=self._time,
            position_xy=(float(obs["fly"][0, 0]), float(obs["fly"][0, 1])),
            yaw=float(self._last_yaw),
            forward_speed=forward_speed,
            yaw_rate=yaw_rate,
            contact_force=contact_force,
            realistic_vision=realistic_vision,
            realistic_vision_array=realistic_vision_array,
            realistic_vision_features=realistic_vision_features,
            realistic_vision_index_cache=realistic_vision_index_cache,
            realistic_vision_splice_cache=realistic_vision_splice_cache,
            vision_payload_mode=vision_payload_mode,
            raw_vision=obs.get("vision"),
            metadata=metadata,
        )

    def render_frame(self) -> Any:
        return self._last_frame

    def close(self) -> None:
        if hasattr(self, "sim"):
            self.sim.close()

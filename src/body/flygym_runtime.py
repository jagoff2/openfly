from __future__ import annotations

from dataclasses import dataclass
import math
import os
from pathlib import Path
import types
from typing import Any, Mapping

import numpy as np

from body.interfaces import BodyObservation, ControlCommand, EmbodiedRuntime
from body.target_schedule import TargetScheduleState, parse_target_schedule
from vision.feature_extractor import RealisticVisionFeatureExtractor, _normalize_cell_type
from vision.flyvis_compat import configure_flyvis_device

@dataclass
class FlyGymRealisticVisionRuntime(EmbodiedRuntime):
    timestep: float = 1e-4
    terrain_type: str = "flat"
    leading_fly_speed: float = 15.0
    leading_fly_radius: float = 10.0
    target_fly_enabled: bool = True
    target_initial_phase_rad: float = 0.0
    target_angular_direction: float = 1.0
    target_schedule: list[dict[str, Any]] | None = None
    extra_targets: list[dict[str, Any]] | None = None
    output_dir: str | Path = "outputs/demos"
    camera_fps: int = 24
    force_cpu_vision: bool = False
    vision_payload_mode: str = "legacy"
    control_mode: str = "hybrid_multidrive"
    camera_mode: str = "fixed_birdeye"
    spawn_pos: tuple[float, float, float] = (0.0, 0.0, 0.3)
    fly_init_pose: str = "stretch"
    visual_speed_control: dict[str, Any] | None = None
    visual_ablation_cell_types: tuple[str, ...] = ()

    @staticmethod
    def corridor_birdeye_camera_parameters() -> dict[str, Any]:
        # Keep Creamer-style corridor assays on a world-fixed overhead camera.
        # A tracked overhead camera in this setup can make the fly appear to
        # disappear as the moving corridor geometry shifts beneath it.
        return {"mode": "fixed", "pos": (0, 0, 120), "euler": (0, 0, 0), "fovy": 60}

    @staticmethod
    def default_birdeye_camera_parameters() -> dict[str, Any]:
        return {"mode": "fixed", "pos": (5, 0, 35), "euler": (0, 0, 0), "fovy": 45}

    @staticmethod
    def zoomed_out_birdeye_camera_parameters() -> dict[str, Any]:
        return {"mode": "fixed", "pos": (0, 0, 380), "euler": (0, 0, 0), "fovy": 90}

    def __post_init__(self) -> None:
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._vision_feature_extractor = RealisticVisionFeatureExtractor()
        self._visual_ablation_cell_types = {
            str(_normalize_cell_type(value)).lower() for value in tuple(self.visual_ablation_cell_types or ())
        }
        self._setup_imports()
        self._build_simulation()
        self._last_frame = None
        self._last_position = None
        self._last_yaw = 0.0
        self._time = 0.0
        self._scene_curr_time = 0.0
        self._target_current_theta = float(self.target_initial_phase_rad)

    def _setup_imports(self) -> None:
        if self.force_cpu_vision:
            # Respect explicit CPU fallback requests even though the default
            # production path can now run FlyVis on the local GPUs.
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
        from flygym import Camera, Fly, SingleFlySimulation, YawOnlyCamera
        from flygym.arena import FlatTerrain
        from flygym.examples.vision import MovingFlyArena
        from body.brain_only_realistic_vision_fly import BrainOnlyRealisticVisionFly
        from body.connectome_turning_fly import ConnectomeTurningFly
        from body.fast_realistic_vision_fly import FastRealisticVisionFly
        from body.visual_speed_control import (
            VisualSpeedBallTreadmillArena,
            VisualSpeedControlConfig,
            VisualSpeedStripeCorridorArena,
        )
        self._flyvis_device_info = configure_flyvis_device(force_cpu=self.force_cpu_vision)
        self.Camera = Camera
        self.Fly = Fly
        self.SingleFlySimulation = SingleFlySimulation
        self.YawOnlyCamera = YawOnlyCamera
        self.FlatTerrain = FlatTerrain
        self.MovingFlyArena = MovingFlyArena
        self.LegacyRealisticVisionFly = BrainOnlyRealisticVisionFly
        self.ConnectomeTurningFly = ConnectomeTurningFly
        self.FastRealisticVisionFly = FastRealisticVisionFly
        self.VisualSpeedControlConfig = VisualSpeedControlConfig
        self.VisualSpeedStripeCorridorArena = VisualSpeedStripeCorridorArena
        self.VisualSpeedBallTreadmillArena = VisualSpeedBallTreadmillArena

    def _build_simulation(self) -> None:
        contact_sensor_placements = [f"{leg}{segment}" for leg in ["LF", "LM", "LH", "RF", "RM", "RH"] for segment in ["Tibia", "Tarsus1", "Tarsus2", "Tarsus3", "Tarsus4", "Tarsus5"]]
        self._visual_speed_cfg = self.VisualSpeedControlConfig.from_mapping(self.visual_speed_control)
        if self._visual_speed_cfg.enabled:
            if self._visual_speed_cfg.geometry == "treadmill_ball":
                self.arena = self.VisualSpeedBallTreadmillArena(self._visual_speed_cfg)
            else:
                self.arena = self.VisualSpeedStripeCorridorArena(self._visual_speed_cfg)
        elif self.target_fly_enabled:
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
        self._target_schedule_state = TargetScheduleState(parse_target_schedule(self.target_schedule))
        self._extra_target_entities = self._build_extra_target_entities()
        if self._extra_target_entities:
            self._attach_extra_targets()
        if self.control_mode == "hybrid_multidrive":
            fly_cls = self.FastRealisticVisionFly if self.vision_payload_mode == "fast" else self.ConnectomeTurningFly
        else:
            fly_cls = self.FastRealisticVisionFly if self.vision_payload_mode == "fast" else self.LegacyRealisticVisionFly
        self.fly = fly_cls(
            contact_sensor_placements=contact_sensor_placements,
            enable_adhesion=True,
            vision_refresh_rate=500,
            neck_kp=500,
            init_pose=str(self.fly_init_pose),
            spawn_pos=tuple(float(value) for value in self.spawn_pos),
            force_cpu_vision=bool(self.force_cpu_vision),
        )
        corridor_birdeye_params = self.corridor_birdeye_camera_parameters()
        default_birdeye_params = self.default_birdeye_camera_parameters()
        zoomed_out_birdeye_params = self.zoomed_out_birdeye_camera_parameters()
        if self.camera_mode == "follow_yaw":
            self.camera = self.YawOnlyCamera(
                attachment_point=self.fly.model.worldbody,
                camera_name="camera_back_track",
                targeted_fly_names=self.fly.name,
                play_speed=0.2,
                window_size=(800, 608),
                fps=self.camera_fps,
            )
        elif self.camera_mode == "corridor_follow_top":
            self.camera = self.Camera(
                attachment_point=self.arena.root_element.worldbody,
                camera_name="corridor_follow_top_cam",
                camera_parameters=dict(corridor_birdeye_params),
                play_speed=0.2,
                window_size=(800, 608),
                fps=self.camera_fps,
            )
        elif self.camera_mode == "fixed_birdeye_zoomed_out":
            self.camera = self.Camera(
                attachment_point=self.arena.root_element.worldbody,
                camera_name="birdeye_zoomed_out_cam",
                camera_parameters=dict(zoomed_out_birdeye_params),
                play_speed=0.2,
                window_size=(960, 720),
                fps=self.camera_fps,
            )
        else:
            cam_params = corridor_birdeye_params if self._visual_speed_cfg.enabled else default_birdeye_params
            self.camera = self.Camera(
                attachment_point=self.arena.root_element.worldbody,
                camera_name="birdeye_cam",
                camera_parameters=cam_params,
                play_speed=0.2,
                window_size=(800, 608),
                fps=self.camera_fps,
            )
        self.sim = self.SingleFlySimulation(fly=self.fly, cameras=[self.camera], arena=self.arena)
        if self.target_fly_enabled or self._extra_target_entities:
            self.arena.step = types.MethodType(self._controlled_target_step, self.arena)

    def _build_extra_target_entities(self) -> list[dict[str, Any]]:
        entities: list[dict[str, Any]] = []
        for index, item in enumerate(self.extra_targets or ()):
            spec = dict(item or {})
            radius = max(float(spec.get("radius", self.leading_fly_radius)), 1e-9)
            move_speed = abs(float(spec.get("move_speed", self.leading_fly_speed)))
            direction = 1.0 if float(spec.get("angular_direction", 1.0)) >= 0.0 else -1.0
            height = float(spec.get("height", 0.5))
            entities.append(
                {
                    "label": str(spec.get("label", f"extra_target_{index}")),
                    "radius": radius,
                    "move_speed": move_speed,
                    "angular_speed": direction * move_speed / radius,
                    "initial_phase_rad": float(spec.get("initial_phase_rad", 0.0)),
                    "height": height,
                    "freejoint": None,
                }
            )
        return entities

    def _attach_extra_targets(self) -> None:
        for index, entity in enumerate(self._extra_target_entities):
            fly = self.Fly().model
            fly.model = f"Animat_extra_target_{index}"
            for light in fly.find_all(namespace="light"):
                light.remove()
            position, heading, _velocity_xy = self._scene_target_pose(
                radius=float(entity["radius"]),
                theta=float(entity["initial_phase_rad"]),
                height=float(entity["height"]),
                angular_speed=float(entity["angular_speed"]),
            )
            quat = np.exp(1j * heading / 2.0)
            spawn_site = self.arena.root_element.worldbody.add(
                "site",
                name=f"extra_target_site_{index}",
                pos=position,
                quat=(float(quat.real), 0.0, 0.0, float(quat.imag)),
            )
            entity["freejoint"] = spawn_site.attach(fly).add("freejoint")

    def _apply_target_pose(self, theta: float, physics: Any | None = None) -> None:
        if not self.target_fly_enabled or not hasattr(self.arena, "freejoint"):
            return
        physics = physics or self.sim.physics
        position, heading, _velocity_xy = self._ghost_target_pose(theta)
        self.arena.fly_pos = position.copy()
        quat = np.exp(1j * heading / 2.0)
        qpos = (*position, float(quat.real), 0.0, 0.0, float(quat.imag))
        physics.bind(self.arena.freejoint).qpos = qpos
        physics.bind(self.arena.freejoint).qvel[:] = 0
        self.arena._prev_pos = complex(*self.arena.fly_pos[:2])

    def _apply_hidden_target_pose(self, physics: Any | None = None) -> None:
        if not self.target_fly_enabled or not hasattr(self.arena, "freejoint"):
            return
        physics = physics or self.sim.physics
        hidden_pos = np.array([0.0, 0.0, -10.0], dtype=float)
        physics.bind(self.arena.freejoint).qpos = (*hidden_pos, 1.0, 0.0, 0.0, 0.0)
        physics.bind(self.arena.freejoint).qvel[:] = 0

    def _ghost_target_pose(self, theta: float) -> tuple[np.ndarray, float, tuple[float, float]]:
        return self._scene_target_pose(
            radius=float(self.leading_fly_radius),
            theta=theta,
            height=float(getattr(self.arena, "init_fly_pos", (0.0, 0.0, 0.5))[2]),
            angular_speed=float(self._target_angular_speed),
        )

    def _scene_target_pose(
        self,
        *,
        radius: float,
        theta: float,
        height: float,
        angular_speed: float,
    ) -> tuple[np.ndarray, float, tuple[float, float]]:
        position = np.array(
            [
                radius * math.sin(theta),
                radius * math.cos(theta),
                height,
            ],
            dtype=float,
        )
        velocity_x = radius * math.cos(theta) * angular_speed
        velocity_y = -radius * math.sin(theta) * angular_speed
        heading = math.atan2(velocity_y, velocity_x) if abs(velocity_x) + abs(velocity_y) > 1e-12 else 0.0
        return position, heading, (float(velocity_x), float(velocity_y))

    def _update_target_pose(self, current_time_s: float, physics: Any | None = None) -> None:
        if not self.target_fly_enabled or not hasattr(self.arena, "freejoint"):
            return
        self._target_schedule_state.advance(float(current_time_s))
        self._target_current_theta = (
            float(self.target_initial_phase_rad)
            + float(self._target_schedule_state.phase_offset_rad)
            + float(self._target_angular_speed) * float(current_time_s)
        )
        if self._target_schedule_state.visible:
            self._apply_target_pose(self._target_current_theta, physics)
        else:
            self._apply_hidden_target_pose(physics)

    def _update_extra_target_poses(self, current_time_s: float, physics: Any | None = None) -> None:
        if not self._extra_target_entities:
            return
        physics = physics or self.sim.physics
        for entity in self._extra_target_entities:
            freejoint = entity.get("freejoint")
            if freejoint is None:
                continue
            theta = float(entity["initial_phase_rad"]) + float(entity["angular_speed"]) * float(current_time_s)
            position, heading, _velocity_xy = self._scene_target_pose(
                radius=float(entity["radius"]),
                theta=theta,
                height=float(entity["height"]),
                angular_speed=float(entity["angular_speed"]),
            )
            quat = np.exp(1j * heading / 2.0)
            qpos = (*position, float(quat.real), 0.0, 0.0, float(quat.imag))
            physics.bind(freejoint).qpos = qpos
            physics.bind(freejoint).qvel[:] = 0

    def _controlled_target_step(self, arena: Any, dt: float, physics: Any) -> None:
        del arena
        self._update_target_pose(self._scene_curr_time, physics)
        self._update_extra_target_poses(self._scene_curr_time, physics)
        self._scene_curr_time += float(dt)
        if hasattr(self.arena, "curr_time"):
            self.arena.curr_time = self._scene_curr_time

    def _target_state_metadata(self, position_xy: tuple[float, float], yaw: float) -> dict[str, Any]:
        if not self.target_fly_enabled or not hasattr(self.arena, "freejoint"):
            return {"enabled": False}
        target_position, target_yaw, target_velocity = self._ghost_target_pose(self._target_current_theta)
        target_x, target_y, target_z = (float(target_position[0]), float(target_position[1]), float(target_position[2]))
        rel_x = target_x - float(position_xy[0])
        rel_y = target_y - float(position_xy[1])
        target_bearing_world = float(math.atan2(rel_y, rel_x))
        target_bearing_body = float((target_bearing_world - yaw + math.pi) % (2.0 * math.pi) - math.pi)
        metadata = {
            "enabled": True,
            **self._target_schedule_state.metadata(self._time),
            "position_x": target_x,
            "position_y": target_y,
            "position_z": target_z,
            "yaw": target_yaw,
            "velocity_x": float(target_velocity[0]),
            "velocity_y": float(target_velocity[1]),
            "distance": float(math.hypot(rel_x, rel_y)),
            "bearing_world": target_bearing_world,
            "bearing_body": target_bearing_body,
            "initial_phase_rad": float(self.target_initial_phase_rad),
            "angular_direction": 1.0 if float(self.target_angular_direction) >= 0.0 else -1.0,
        }
        return metadata

    def reset(self, seed: int = 0) -> BodyObservation:
        obs, info = self.sim.reset(seed=seed)
        self._time = 0.0
        self._scene_curr_time = 0.0
        if hasattr(self.arena, "curr_time"):
            self.arena.curr_time = 0.0
        if self.target_fly_enabled:
            self._target_schedule_state.reset()
            self._update_target_pose(0.0)
        if self._extra_target_entities:
            self._update_extra_target_poses(0.0)
        self._last_position = np.array(obs["fly"][0, :2], dtype=float)
        self._last_yaw = float(np.arctan2(obs["fly_orientation"][1], obs["fly_orientation"][0])) if "fly_orientation" in obs else 0.0
        if hasattr(self.arena, "notify_fly_state"):
            self.arena.notify_fly_state(
                position_xy=(float(self._last_position[0]), float(self._last_position[1])),
                yaw_rad=float(self._last_yaw),
                forward_velocity_x_mm_s=0.0,
            )
        self._last_frame = self.sim.render()[0]
        return self._make_observation(obs, info, forward_speed=0.0, yaw_rate=0.0)

    def step(self, command: ControlCommand, num_substeps: int) -> BodyObservation:
        latest_obs = None
        latest_info = None
        action = np.asarray(command.to_action(), dtype=float)
        substep_prev_position = np.array(self._last_position, dtype=float) if self._last_position is not None else None
        for _ in range(max(1, num_substeps)):
            latest_obs, _, _, _, latest_info = self.sim.step(action=action)
            if hasattr(self.arena, "stabilize_after_physics_step"):
                self.arena.stabilize_after_physics_step(self.sim.physics)
            self._time += self.timestep
            if hasattr(self.arena, "notify_fly_state"):
                current_position = np.array(latest_obs["fly"][0, :2], dtype=float)
                current_yaw = float(np.arctan2(latest_obs["fly_orientation"][1], latest_obs["fly_orientation"][0])) if "fly_orientation" in latest_obs else self._last_yaw
                if substep_prev_position is None:
                    forward_velocity_x_mm_s = 0.0
                else:
                    forward_velocity_x_mm_s = float((current_position[0] - substep_prev_position[0]) / max(self.timestep, 1e-9))
                self.arena.notify_fly_state(
                    position_xy=(float(current_position[0]), float(current_position[1])),
                    yaw_rad=float(current_yaw),
                    forward_velocity_x_mm_s=forward_velocity_x_mm_s,
                )
                substep_prev_position = current_position
        rendered = self.sim.render()[0]
        if rendered is not None:
            self._last_frame = rendered
        position = np.array(latest_obs["fly"][0, :2], dtype=float)
        yaw = float(np.arctan2(latest_obs["fly_orientation"][1], latest_obs["fly_orientation"][0])) if "fly_orientation" in latest_obs else self._last_yaw
        body_forward_speed = float(np.linalg.norm(position - self._last_position) / (max(1, num_substeps) * self.timestep))
        forward_speed = body_forward_speed
        treadmill_forward_speed = None
        if hasattr(self.arena, "filtered_fly_forward_speed_mm_s") and self._visual_speed_cfg.enabled and self._visual_speed_cfg.geometry == "treadmill_ball":
            treadmill_forward_speed = float(getattr(self.arena, "filtered_fly_forward_speed_mm_s", body_forward_speed))
            # A tethered treadmill run should not feed support-jitter XY motion back
            # into the brain as if it were true world-frame translation.
            forward_speed = 0.0
        yaw_rate = float((yaw - self._last_yaw) / (max(1, num_substeps) * self.timestep))
        self._last_position = position
        self._last_yaw = yaw
        return self._make_observation(
            latest_obs,
            latest_info,
            forward_speed=forward_speed,
            yaw_rate=yaw_rate,
            treadmill_forward_speed=treadmill_forward_speed,
            body_forward_speed=body_forward_speed,
        )

    def _apply_visual_ablation(
        self,
        realistic_vision: dict[str, Any],
        realistic_vision_array: Any,
        realistic_vision_features: Mapping[str, Any] | None,
        realistic_vision_index_cache: Any,
        realistic_vision_splice_cache: Any,
    ) -> tuple[dict[str, Any], Any, Mapping[str, Any] | None]:
        if not self._visual_ablation_cell_types:
            return realistic_vision, realistic_vision_array, realistic_vision_features
        ablated_mapping = {
            key: (
                np.zeros_like(np.asarray(value, dtype=float))
                if str(_normalize_cell_type(key)).lower() in self._visual_ablation_cell_types
                else np.asarray(value, dtype=float).copy()
            )
            for key, value in realistic_vision.items()
        }
        ablated_array = None if realistic_vision_array is None else np.asarray(realistic_vision_array, dtype=float).copy()
        if ablated_array is not None and realistic_vision_splice_cache is not None and hasattr(realistic_vision_splice_cache, "node_types"):
            node_types = np.asarray(realistic_vision_splice_cache.node_types).reshape(-1)
            ablated_indices = [
                idx
                for idx, cell_type in enumerate(node_types)
                if str(_normalize_cell_type(cell_type)).lower() in self._visual_ablation_cell_types
            ]
            if ablated_indices:
                ablated_array[:, ablated_indices] = 0.0
        updated_features = realistic_vision_features
        if ablated_array is not None and realistic_vision_index_cache is not None:
            updated_features = self._vision_feature_extractor.extract_from_array(
                ablated_array,
                realistic_vision_index_cache,
            ).to_dict()
        elif ablated_mapping:
            updated_features = self._vision_feature_extractor.extract(ablated_mapping).to_dict()
        return ablated_mapping, ablated_array, updated_features

    def _make_observation(
        self,
        obs: dict[str, Any],
        info: dict[str, Any],
        forward_speed: float,
        yaw_rate: float,
        treadmill_forward_speed: float | None = None,
        body_forward_speed: float | None = None,
    ) -> BodyObservation:
        realistic_vision = {}
        nn_activities = info.get("nn_activities") if info else None
        if hasattr(nn_activities, "keys"):
            for key in nn_activities.keys():
                realistic_vision[key] = np.asarray(nn_activities[key])
        realistic_vision_array = obs.get("nn_activities_arr") if obs else None
        if realistic_vision_array is None and info:
            realistic_vision_array = info.get("nn_activities_arr")
        realistic_vision_features = info.get("vision_features_fast") if info else None
        realistic_vision_index_cache = info.get("vision_index_cache") if info else None
        realistic_vision_splice_cache = info.get("vision_splice_cache") if info else None
        realistic_vision, realistic_vision_array, realistic_vision_features = self._apply_visual_ablation(
            realistic_vision,
            realistic_vision_array,
            realistic_vision_features,
            realistic_vision_index_cache,
            realistic_vision_splice_cache,
        )
        vision_payload_mode = info.get("vision_payload_mode", self.vision_payload_mode) if info else self.vision_payload_mode
        contact_force = float(np.linalg.norm(obs["contact_forces"])) if "contact_forces" in obs else 0.0
        metadata = {
            "vision_updated": bool(info.get("vision_updated", False)) if info else False,
            "vision_payload_mode": vision_payload_mode,
            "target_fly_enabled": self.target_fly_enabled,
            "extra_target_count": float(len(self._extra_target_entities)),
            "target_state": self._target_state_metadata((float(obs["fly"][0, 0]), float(obs["fly"][0, 1])), float(self._last_yaw)),
            "visual_ablation_cell_types": sorted(self._visual_ablation_cell_types),
            "body_state": {
                "position_x": float(obs["fly"][0, 0]),
                "position_y": float(obs["fly"][0, 1]),
                "position_z": float(obs["fly"][0, 2]) if np.asarray(obs["fly"]).shape[-1] >= 3 else 0.0,
                "yaw": float(self._last_yaw),
                "forward_speed": float(forward_speed),
                "yaw_rate": float(yaw_rate),
            },
        }
        if hasattr(self.arena, "metadata"):
            visual_speed_state = dict(self.arena.metadata())
            if visual_speed_state.get("speed_source", "") == "treadmill_ball":
                visual_speed_state["body_forward_speed_mm_s"] = float(
                    body_forward_speed if body_forward_speed is not None else forward_speed
                )
                visual_speed_state["treadmill_forward_speed_mm_s"] = float(
                    treadmill_forward_speed
                    if treadmill_forward_speed is not None
                    else visual_speed_state.get("fly_forward_speed_mm_s_filtered", 0.0)
                )
            metadata["visual_speed_state"] = visual_speed_state
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

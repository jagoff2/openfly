from __future__ import annotations

import math
from dataclasses import dataclass
from types import SimpleNamespace

import numpy as np

from body.interfaces import BodyObservation, ControlCommand, EmbodiedRuntime
from vision.feature_extractor import RealisticVisionFeatureExtractor

@dataclass
class MockEmbodiedRuntime(EmbodiedRuntime):
    timestep: float = 0.01
    arena_radius: float = 12.0
    vision_payload_mode: str = "legacy"

    def __post_init__(self) -> None:
        self._rng = np.random.default_rng(0)
        self._frame = None
        self._vision_feature_extractor = RealisticVisionFeatureExtractor()
        self._vision_index_cache = None
        self._vision_cell_order = None
        self.reset()

    def reset(self, seed: int = 0) -> BodyObservation:
        self._rng = np.random.default_rng(seed)
        self.time = 0.0
        self.position = np.array([0.0, 0.0], dtype=float)
        self.yaw = 0.0
        self.forward_speed = 0.0
        self.yaw_rate = 0.0
        self.target_phase = 0.0
        return self._observe()

    def _target_position(self) -> np.ndarray:
        return np.array([6.0 + 2.0 * math.cos(self.target_phase), 4.0 * math.sin(self.target_phase * 0.5)])

    def step(self, command: ControlCommand, num_substeps: int) -> BodyObservation:
        for _ in range(max(1, num_substeps)):
            log_dict = command.to_log_dict()
            left_drive = float(log_dict.get("left_drive", 0.0))
            right_drive = float(log_dict.get("right_drive", 0.0))
            mean_drive = 0.5 * (left_drive + right_drive)
            turn_drive = right_drive - left_drive
            self.forward_speed = float(np.clip(mean_drive, -1.2, 1.2))
            self.yaw_rate = float(np.clip(turn_drive, -1.5, 1.5))
            self.yaw += self.yaw_rate * self.timestep
            heading = np.array([math.cos(self.yaw), math.sin(self.yaw)])
            self.position = self.position + heading * self.forward_speed * self.timestep * 2.0
            self.target_phase += self.timestep * 0.8
            self.time += self.timestep
        return self._observe()

    def _observe(self) -> BodyObservation:
        target = self._target_position()
        rel = target - self.position
        distance = float(np.linalg.norm(rel) + 1e-6)
        angle = math.atan2(rel[1], rel[0]) - self.yaw
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        left_salience = math.exp(-((angle + 0.35) ** 2) / 0.18) / (1.0 + 0.1 * distance)
        right_salience = math.exp(-((angle - 0.35) ** 2) / 0.18) / (1.0 + 0.1 * distance)
        flow_bias = float(np.clip(self.yaw_rate, -1.0, 1.0))
        forward_salience = math.exp(-(angle ** 2) / 0.4) / (1.0 + 0.08 * distance)
        contact_force = 1.0 + 0.2 * abs(math.sin(self.time * 5.0))
        realistic_vision = {
            "T4a": np.array([left_salience - flow_bias, right_salience + flow_bias]),
            "T4b": np.array([left_salience * 0.7 - flow_bias, right_salience * 0.7 + flow_bias]),
            "T5a": np.array([left_salience + flow_bias, right_salience - flow_bias]),
            "T5b": np.array([left_salience * 0.7 + flow_bias, right_salience * 0.7 - flow_bias]),
            "T2": np.array([left_salience, right_salience]),
            "T2a": np.array([left_salience * 0.8, right_salience * 0.8]),
            "Tm1": np.array([forward_salience * (1.0 + left_salience), forward_salience * (1.0 + right_salience)]),
            "Tm9": np.array([forward_salience, forward_salience]),
            "TmY10": np.array([left_salience * forward_salience, right_salience * forward_salience]),
        }
        metadata = {"target_position": target.tolist(), "target_distance": distance, "target_angle": angle}
        self._frame = self._draw_frame(target)
        realistic_vision_array = None
        realistic_vision_features = None
        realistic_vision_index_cache = None
        realistic_vision_splice_cache = None
        realistic_vision_mapping = realistic_vision
        if self.vision_payload_mode == "fast":
            if self._vision_cell_order is None:
                self._vision_cell_order = tuple(realistic_vision.keys())
                self._vision_index_cache = self._vision_feature_extractor.build_index_cache(np.asarray(self._vision_cell_order, dtype=object))
            realistic_vision_array = np.stack([np.asarray(realistic_vision[cell], dtype=float) for cell in self._vision_cell_order], axis=0).T
            realistic_vision_features = self._vision_feature_extractor.extract_from_array(realistic_vision_array, self._vision_index_cache).to_dict()
            realistic_vision_index_cache = self._vision_index_cache
            node_types = np.asarray(self._vision_cell_order, dtype=object)
            node_u = np.linspace(-1.0, 1.0, num=len(node_types), dtype=float)
            node_v = np.linspace(-0.75, 0.75, num=len(node_types), dtype=float)
            realistic_vision_splice_cache = SimpleNamespace(
                node_u=node_u,
                node_v=node_v,
                node_types=node_types,
            )
            realistic_vision_mapping = {}
        metadata["vision_payload_mode"] = self.vision_payload_mode
        return BodyObservation(
            sim_time=self.time,
            position_xy=(float(self.position[0]), float(self.position[1])),
            yaw=float(self.yaw),
            forward_speed=self.forward_speed,
            yaw_rate=self.yaw_rate,
            contact_force=contact_force,
            realistic_vision=realistic_vision_mapping,
            realistic_vision_array=realistic_vision_array,
            realistic_vision_features=realistic_vision_features,
            realistic_vision_index_cache=realistic_vision_index_cache,
            realistic_vision_splice_cache=realistic_vision_splice_cache,
            vision_payload_mode=self.vision_payload_mode,
            metadata=metadata,
        )

    def _draw_frame(self, target: np.ndarray) -> np.ndarray:
        height, width = 360, 640
        frame = np.full((height, width, 3), 245, dtype=np.uint8)
        def world_to_px(point: np.ndarray) -> tuple[int, int]:
            x = int(width / 2 + point[0] * 18)
            y = int(height / 2 - point[1] * 18)
            return x, y
        tx, ty = world_to_px(target)
        px, py = world_to_px(self.position)
        for dx in range(-8, 9):
            for dy in range(-8, 9):
                if dx * dx + dy * dy <= 64 and 0 <= ty + dy < height and 0 <= tx + dx < width:
                    frame[ty + dy, tx + dx] = np.array([220, 50, 47], dtype=np.uint8)
        for dx in range(-6, 7):
            for dy in range(-6, 7):
                if dx * dx + dy * dy <= 36 and 0 <= py + dy < height and 0 <= px + dx < width:
                    frame[py + dy, px + dx] = np.array([20, 20, 20], dtype=np.uint8)
        heading = np.array([math.cos(self.yaw), -math.sin(self.yaw)])
        for step in range(1, 18):
            hx = int(px + heading[0] * step)
            hy = int(py + heading[1] * step)
            if 0 <= hy < height and 0 <= hx < width:
                frame[hy, hx] = np.array([15, 80, 180], dtype=np.uint8)
        return frame

    def render_frame(self) -> np.ndarray:
        return self._frame

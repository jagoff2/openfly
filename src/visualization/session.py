from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import imageio.v2 as imageio
import numpy as np

from brain.public_ids import MOTOR_READOUT_IDS
from visualization.activation_viz import (
    BrainLayout,
    FlyVisLayout,
    load_brain_layout,
    load_flyvis_layout,
    render_activation_frame,
    render_overview_figure,
)


def _tensor_to_numpy(value: Any, *, dtype: np.dtype) -> np.ndarray:
    if hasattr(value, "detach") and hasattr(value, "cpu") and hasattr(value, "numpy"):
        return value.detach().cpu().numpy().astype(dtype, copy=False)
    return np.asarray(value, dtype=dtype)


def _controller_channels(
    *,
    bridge_info: Mapping[str, Any],
    command_log: Mapping[str, float],
    observation: Any,
) -> dict[str, float]:
    target_state = observation.metadata.get("target_state", {}) if getattr(observation, "metadata", None) else {}
    motor_readout = bridge_info.get("motor_readout", {})
    return {
        "dn_forward_signal": float(motor_readout.get("dn_forward_signal", 0.0)),
        "population_forward_signal": float(motor_readout.get("population_forward_signal", 0.0)),
        "dn_turn_signal": float(motor_readout.get("dn_turn_signal", 0.0)),
        "population_turn_signal": float(motor_readout.get("population_turn_signal", 0.0)),
        "left_drive": float(command_log.get("left_drive", 0.0)),
        "right_drive": float(command_log.get("right_drive", 0.0)),
        "target_bearing_body": float(target_state.get("bearing_body", 0.0)),
        "forward_speed": float(observation.forward_speed),
    }


def _discover_monitor_labels(motor_readout: Mapping[str, Any]) -> list[str]:
    labels = []
    prefix = "monitor_"
    suffix = "_bilateral_hz"
    for key in motor_readout:
        if key.startswith(prefix) and key.endswith(suffix):
            labels.append(key[len(prefix) : -len(suffix)])
    return sorted(set(str(label) for label in labels))


def _monitor_bilateral_rates(bridge_info: Mapping[str, Any], monitor_labels: Sequence[str]) -> list[float]:
    motor_readout = bridge_info.get("motor_readout", {})
    return [float(motor_readout.get(f"monitor_{label}_bilateral_hz", 0.0)) for label in monitor_labels]


@dataclass
class ActivationCaptureSession:
    run_dir: Path
    title: str
    video_fps: int
    video_stride: int
    max_brain_points: int
    max_flyvis_points: int
    brain_layout: BrainLayout
    flyvis_layout: FlyVisLayout

    @classmethod
    def try_create(
        cls,
        *,
        config: Mapping[str, Any],
        run_dir: Path,
        initial_observation: Any,
        title: str,
        max_brain_points: int = 6000,
        max_flyvis_points: int = 5000,
    ) -> tuple["ActivationCaptureSession | None", dict[str, Any]]:
        runtime_cfg = config.get("runtime", {})
        vision_array = getattr(initial_observation, "realistic_vision_array", None)
        splice_cache = getattr(initial_observation, "realistic_vision_splice_cache", None)
        if vision_array is None or splice_cache is None:
            return None, {
                "status": "skipped",
                "reason": "activation capture requires realistic vision arrays and splice cache",
            }
        visual_splice_cfg = config.get("visual_splice") or {}
        brain_cfg = config.get("brain") or {}
        fixed_groups = {
            "P9_L": MOTOR_READOUT_IDS["forward_left"],
            "P9_R": MOTOR_READOUT_IDS["forward_right"],
            "DNa_L": MOTOR_READOUT_IDS["turn_left"],
            "DNa_R": MOTOR_READOUT_IDS["turn_right"],
            "MDN": MOTOR_READOUT_IDS["reverse"],
        }
        try:
            brain_layout = load_brain_layout(
                annotation_path=visual_splice_cfg["annotation_path"],
                completeness_path=brain_cfg["completeness_path"],
                candidate_json=config.get("decoder", {}).get("monitor_candidates_json")
                or config.get("decoder", {}).get("population_candidates_json"),
                fixed_groups=fixed_groups,
            )
            flyvis_layout = load_flyvis_layout(
                node_u=splice_cache.node_u,
                node_v=splice_cache.node_v,
                node_types=splice_cache.node_types,
            )
        except Exception as exc:  # pragma: no cover - failure path depends on runtime data
            return None, {
                "status": "skipped",
                "reason": f"activation capture layout init failed: {type(exc).__name__}: {exc}",
            }
        return (
            cls(
                run_dir=run_dir,
                title=str(title),
                video_fps=int(runtime_cfg.get("video_fps", 24)),
                video_stride=int(runtime_cfg.get("video_stride", 1)),
                max_brain_points=int(max_brain_points),
                max_flyvis_points=int(max_flyvis_points),
                brain_layout=brain_layout,
                flyvis_layout=flyvis_layout,
            ),
            {"status": "armed"},
        )

    def __post_init__(self) -> None:
        self.source_frames: list[np.ndarray] = []
        self.frame_cycles: list[int] = []
        self.frame_times_s: list[float] = []
        self.frame_target_bearing: list[float] = []
        self.frame_target_distance: list[float] = []
        self.brain_voltage_frames: list[np.ndarray] = []
        self.brain_spike_frames: list[np.ndarray] = []
        self.flyvis_left_frames: list[np.ndarray] = []
        self.flyvis_right_frames: list[np.ndarray] = []
        self.controller_labels = [
            "dn_forward_signal",
            "population_forward_signal",
            "dn_turn_signal",
            "population_turn_signal",
            "left_drive",
            "right_drive",
            "target_bearing_body",
            "forward_speed",
        ]
        self.controller_history = {label: [] for label in self.controller_labels}
        self.cycle_times_s: list[float] = []
        self.monitor_labels: list[str] = []
        self.monitor_history: list[list[float]] = []
        self.monitored_root_ids: list[int] = []
        self.monitored_rate_history: list[list[float]] = []
        self.monitored_voltage_history: list[list[float]] = []
        self.monitored_spike_history: list[list[float]] = []

    def record_cycle(
        self,
        *,
        cycle: int,
        observation: Any,
        frame: Any,
        bridge_info: Mapping[str, Any],
        command_log: Mapping[str, float],
        brain_backend: Any,
    ) -> None:
        controller_values = _controller_channels(
            bridge_info=bridge_info,
            command_log=command_log,
            observation=observation,
        )
        self.cycle_times_s.append(float(observation.sim_time))
        for label, value in controller_values.items():
            self.controller_history[label].append(float(value))

        if not self.monitor_labels:
            self.monitor_labels = _discover_monitor_labels(bridge_info.get("motor_readout", {}))
        if self.monitor_labels:
            self.monitor_history.append(_monitor_bilateral_rates(bridge_info, self.monitor_labels))
        brain_monitored_rates = bridge_info.get("brain_monitored_rates", {})
        if brain_monitored_rates:
            if not self.monitored_root_ids:
                self.monitored_root_ids = sorted(int(root_id) for root_id in brain_monitored_rates.keys())
            self.monitored_rate_history.append(
                [float(brain_monitored_rates.get(str(root_id), brain_monitored_rates.get(root_id, 0.0))) for root_id in self.monitored_root_ids]
            )
            brain_monitored_voltage = bridge_info.get("brain_monitored_voltage", {})
            self.monitored_voltage_history.append(
                [float(brain_monitored_voltage.get(str(root_id), brain_monitored_voltage.get(root_id, 0.0))) for root_id in self.monitored_root_ids]
            )
            brain_monitored_spikes = bridge_info.get("brain_monitored_spikes", {})
            self.monitored_spike_history.append(
                [float(brain_monitored_spikes.get(str(root_id), brain_monitored_spikes.get(root_id, 0.0))) for root_id in self.monitored_root_ids]
            )

        if frame is None or cycle % max(1, self.video_stride) != 0:
            return
        if not hasattr(brain_backend, "v") or not hasattr(brain_backend, "spikes"):
            return

        self.source_frames.append(np.asarray(frame, dtype=np.uint8))
        self.frame_cycles.append(int(cycle))
        self.frame_times_s.append(float(observation.sim_time))
        target_state = observation.metadata.get("target_state", {}) if getattr(observation, "metadata", None) else {}
        self.frame_target_bearing.append(float(target_state.get("bearing_body", 0.0)))
        self.frame_target_distance.append(float(target_state.get("distance", 0.0)))
        self.brain_voltage_frames.append(_tensor_to_numpy(brain_backend.v[0], dtype=np.float16))
        self.brain_spike_frames.append(_tensor_to_numpy(brain_backend.spikes[0], dtype=np.uint8))
        flyvis_arr = np.asarray(observation.realistic_vision_array, dtype=np.float32)
        self.flyvis_left_frames.append(flyvis_arr[0].astype(np.float16, copy=False))
        self.flyvis_right_frames.append(flyvis_arr[1].astype(np.float16, copy=False))

    def finalize(self, *, metrics: Mapping[str, Any]) -> dict[str, Any]:
        if not self.source_frames:
            return {
                "status": "skipped",
                "reason": "activation capture recorded no renderable frames",
            }

        capture_path = self.run_dir / "activation_capture.npz"
        composite_path = self.run_dir / "activation_side_by_side.mp4"
        overview_path = self.run_dir / "activation_overview.png"
        summary_path = self.run_dir / "activation_summary.json"

        monitor_matrix = (
            np.asarray(self.monitor_history, dtype=np.float32).T
            if self.monitor_history
            else np.zeros((0, len(self.cycle_times_s)), dtype=np.float32)
        )
        controller_matrix = np.asarray(
            [self.controller_history[label] for label in self.controller_labels],
            dtype=np.float32,
        )
        brain_voltage_arr = np.asarray(self.brain_voltage_frames, dtype=np.float16)
        brain_spike_arr = np.asarray(self.brain_spike_frames, dtype=np.uint8)
        flyvis_left_arr = np.asarray(self.flyvis_left_frames, dtype=np.float16)
        flyvis_right_arr = np.asarray(self.flyvis_right_frames, dtype=np.float16)

        np.savez_compressed(
            capture_path,
            frame_cycles=np.asarray(self.frame_cycles, dtype=np.int32),
            frame_times_s=np.asarray(self.frame_times_s, dtype=np.float32),
            frame_target_bearing_body=np.asarray(self.frame_target_bearing, dtype=np.float32),
            frame_target_distance=np.asarray(self.frame_target_distance, dtype=np.float32),
            brain_voltage_frames=brain_voltage_arr,
            brain_spike_frames=brain_spike_arr,
            flyvis_left_frames=flyvis_left_arr,
            flyvis_right_frames=flyvis_right_arr,
            cycle_times_s=np.asarray(self.cycle_times_s, dtype=np.float32),
            monitor_labels=np.asarray(self.monitor_labels, dtype="<U64"),
            monitor_matrix=monitor_matrix,
            monitored_root_ids=np.asarray(self.monitored_root_ids, dtype=np.int64),
            monitored_rate_matrix=np.asarray(self.monitored_rate_history, dtype=np.float32).T
            if self.monitored_rate_history
            else np.zeros((0, len(self.cycle_times_s)), dtype=np.float32),
            monitored_voltage_matrix=np.asarray(self.monitored_voltage_history, dtype=np.float32).T
            if self.monitored_voltage_history
            else np.zeros((0, len(self.cycle_times_s)), dtype=np.float32),
            monitored_spike_matrix=np.asarray(self.monitored_spike_history, dtype=np.float32).T
            if self.monitored_spike_history
            else np.zeros((0, len(self.cycle_times_s)), dtype=np.float32),
            controller_labels=np.asarray(self.controller_labels, dtype="<U64"),
            controller_matrix=controller_matrix,
        )

        overview_index = len(self.source_frames) // 2
        render_overview_figure(
            overview_path,
            demo_frame=self.source_frames[overview_index],
            brain_layout=self.brain_layout,
            flyvis_layout=self.flyvis_layout,
            brain_voltage=np.asarray(brain_voltage_arr[overview_index], dtype=np.float32),
            brain_spikes=np.asarray(brain_spike_arr[overview_index], dtype=np.float32),
            flyvis_left=np.asarray(flyvis_left_arr[overview_index], dtype=np.float32),
            flyvis_right=np.asarray(flyvis_right_arr[overview_index], dtype=np.float32),
            monitor_matrix=monitor_matrix,
            monitor_labels=self.monitor_labels,
            controller_matrix=controller_matrix,
            controller_labels=self.controller_labels,
            cycle_index=int(self.frame_cycles[overview_index]),
            frame_time_s=float(self.frame_times_s[overview_index]),
            target_bearing_body=float(self.frame_target_bearing[overview_index]),
            target_distance=float(self.frame_target_distance[overview_index]),
            overlay_title=self.title,
        )

        with imageio.get_writer(composite_path, fps=self.video_fps) as writer:
            for frame_idx, demo_frame in enumerate(self.source_frames):
                image = render_activation_frame(
                    demo_frame=demo_frame,
                    brain_layout=self.brain_layout,
                    flyvis_layout=self.flyvis_layout,
                    brain_voltage=np.asarray(brain_voltage_arr[frame_idx], dtype=np.float32),
                    brain_spikes=np.asarray(brain_spike_arr[frame_idx], dtype=np.float32),
                    flyvis_left=np.asarray(flyvis_left_arr[frame_idx], dtype=np.float32),
                    flyvis_right=np.asarray(flyvis_right_arr[frame_idx], dtype=np.float32),
                    monitor_matrix=monitor_matrix,
                    monitor_labels=self.monitor_labels,
                    controller_matrix=controller_matrix,
                    controller_labels=self.controller_labels,
                    cycle_index=int(self.frame_cycles[frame_idx]),
                    frame_time_s=float(self.frame_times_s[frame_idx]),
                    target_bearing_body=float(self.frame_target_bearing[frame_idx]),
                    target_distance=float(self.frame_target_distance[frame_idx]),
                    overlay_title=self.title,
                    max_brain_points=self.max_brain_points,
                    max_flyvis_points=self.max_flyvis_points,
                )
                writer.append_data(image)

        summary = {
            "status": "generated",
            "title": self.title,
            "capture_path": str(capture_path),
            "composite_video_path": str(composite_path),
            "overview_path": str(overview_path),
            "frame_count": int(len(self.source_frames)),
            "brain_neuron_count": int(self.brain_layout.root_ids.shape[0]),
            "flyvis_neuron_count": int(self.flyvis_layout.uv.shape[0]),
            "monitor_label_count": int(len(self.monitor_labels)),
            "monitored_root_id_count": int(len(self.monitored_root_ids)),
            "controller_label_count": int(len(self.controller_labels)),
            "metrics": {str(key): float(value) if isinstance(value, (int, float, np.floating)) else value for key, value in metrics.items()},
        }
        with summary_path.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        summary["summary_path"] = str(summary_path)
        return summary

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

import imageio.v2 as imageio
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from brain.public_ids import MOTOR_READOUT_IDS
from metrics.parity import compute_parity_metrics, write_metrics_csv
from runtime.closed_loop import build_body_runtime, build_brain_backend, build_bridge, load_config
from runtime.logging_utils import JsonlLogger, make_run_dir, save_video, save_command_plot, save_trajectory_plot
from visualization.activation_viz import load_brain_layout, load_flyvis_layout, render_activation_frame, render_overview_figure


DEFAULT_CONFIG = "configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml"


def _controller_channels(
    *,
    bridge_info: dict,
    command_log: dict[str, float],
    observation,
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


def _monitor_bilateral_rates(bridge_info: dict, monitor_labels: list[str]) -> list[float]:
    motor_readout = bridge_info.get("motor_readout", {})
    return [float(motor_readout.get(f"monitor_{label}_bilateral_hz", 0.0)) for label in monitor_labels]


def build_activation_visualization(
    *,
    config_path: str | Path,
    mode: str,
    duration_s: float | None,
    output_root: str | Path,
    max_brain_points: int,
    max_flyvis_points: int,
    title: str,
) -> dict[str, object]:
    config = load_config(config_path)
    runtime_cfg = config["runtime"]
    control_interval_s = float(runtime_cfg["control_interval_s"])
    duration_s = float(duration_s or runtime_cfg["duration_s"])
    run_dir = make_run_dir(output_root, "activation-viz")
    body_runtime = build_body_runtime(mode, config, run_dir)
    brain_backend = build_brain_backend(mode, config)
    bridge = build_bridge(config, brain_backend)
    bridge.reset(seed=int(runtime_cfg.get("seed", 0)))
    observation = body_runtime.reset(seed=int(runtime_cfg.get("seed", 0)))

    monitor_labels = [str(label) for label in config.get("decoder", {}).get("monitor_cell_types", [])]
    if not monitor_labels:
        raise ValueError("activation visualization requires a monitored decoder config with decoder.monitor_cell_types")
    if observation.realistic_vision_splice_cache is None or observation.realistic_vision_array is None:
        raise ValueError("activation visualization requires fast realistic vision payload mode")

    num_cycles = int(duration_s / control_interval_s)
    num_substeps = max(1, int(round(control_interval_s / body_runtime.timestep)))
    num_brain_steps = max(1, int(round(control_interval_s / (float(config["brain"].get("dt_ms", 0.1)) / 1000.0))))
    video_stride = int(runtime_cfg.get("video_stride", 1))
    video_fps = int(runtime_cfg.get("video_fps", 24))

    logger = JsonlLogger(run_dir / "run.jsonl")
    source_frames: list[np.ndarray] = []
    frame_cycles: list[int] = []
    frame_times_s: list[float] = []
    frame_target_bearing: list[float] = []
    frame_target_distance: list[float] = []
    brain_voltage_frames: list[np.ndarray] = []
    brain_spike_frames: list[np.ndarray] = []
    flyvis_left_frames: list[np.ndarray] = []
    flyvis_right_frames: list[np.ndarray] = []

    controller_labels = [
        "dn_forward_signal",
        "population_forward_signal",
        "dn_turn_signal",
        "population_turn_signal",
        "left_drive",
        "right_drive",
        "target_bearing_body",
        "forward_speed",
    ]
    controller_history = {label: [] for label in controller_labels}
    cycle_times_s: list[float] = []
    monitor_history: list[list[float]] = []
    trajectory: list[np.ndarray] = []
    left_hist: list[float] = []
    right_hist: list[float] = []

    fixed_groups = {
        "P9_L": MOTOR_READOUT_IDS["forward_left"],
        "P9_R": MOTOR_READOUT_IDS["forward_right"],
        "DNa_L": MOTOR_READOUT_IDS["turn_left"],
        "DNa_R": MOTOR_READOUT_IDS["turn_right"],
        "MDN": MOTOR_READOUT_IDS["reverse"],
    }
    brain_layout = load_brain_layout(
        annotation_path=config["visual_splice"]["annotation_path"],
        completeness_path=config["brain"]["completeness_path"],
        candidate_json=config.get("decoder", {}).get("monitor_candidates_json")
        or config.get("decoder", {}).get("population_candidates_json"),
        fixed_groups=fixed_groups,
    )
    flyvis_cache = observation.realistic_vision_splice_cache
    flyvis_layout = load_flyvis_layout(
        node_u=flyvis_cache.node_u,
        node_v=flyvis_cache.node_v,
        node_types=flyvis_cache.node_types,
    )

    wall_start = perf_counter()
    completed_cycles = 0
    failure_type = ""
    failure_message = ""
    try:
        for cycle in range(num_cycles):
            driving_observation = observation
            readout, bridge_info = bridge.step(driving_observation, num_brain_steps=num_brain_steps)
            command = readout.command
            command_log = command.to_log_dict()
            current_time = float(driving_observation.sim_time)
            cycle_times_s.append(current_time)
            controller_values = _controller_channels(
                bridge_info=bridge_info,
                command_log=command_log,
                observation=driving_observation,
            )
            for label, value in controller_values.items():
                controller_history[label].append(float(value))
            monitor_history.append(_monitor_bilateral_rates(bridge_info, monitor_labels))

            observation = body_runtime.step(command, num_substeps=num_substeps)
            frame = body_runtime.render_frame()
            if frame is not None and cycle % video_stride == 0:
                source_frames.append(np.asarray(frame, dtype=np.uint8))
                frame_cycles.append(int(cycle))
                frame_times_s.append(current_time)
                target_state = driving_observation.metadata.get("target_state", {})
                frame_target_bearing.append(float(target_state.get("bearing_body", 0.0)))
                frame_target_distance.append(float(target_state.get("distance", 0.0)))
                brain_voltage_frames.append(
                    brain_backend.v[0].detach().cpu().numpy().astype(np.float16, copy=False)
                )
                brain_spike_frames.append(
                    brain_backend.spikes[0].detach().cpu().numpy().astype(np.uint8, copy=False)
                )
                flyvis_arr = np.asarray(driving_observation.realistic_vision_array, dtype=np.float32)
                flyvis_left_frames.append(flyvis_arr[0].astype(np.float16, copy=False))
                flyvis_right_frames.append(flyvis_arr[1].astype(np.float16, copy=False))

            trajectory.append(np.asarray(observation.position_xy, dtype=np.float32))
            left_hist.append(float(command_log.get("left_drive", 0.0)))
            right_hist.append(float(command_log.get("right_drive", 0.0)))
            logger.write(
                {
                    "cycle": cycle,
                    "sim_time": current_time,
                    "position_x": float(driving_observation.position_xy[0]),
                    "position_y": float(driving_observation.position_xy[1]),
                    "yaw": float(driving_observation.yaw),
                    "forward_speed": float(driving_observation.forward_speed),
                    "yaw_rate": float(driving_observation.yaw_rate),
                    **command_log,
                    "target_state": driving_observation.metadata.get("target_state", {}),
                    "vision_features": bridge_info.get("vision_features", {}),
                    "visual_splice": bridge_info.get("visual_splice", {}),
                    "motor_signals": bridge_info.get("motor_signals", {}),
                    "motor_readout": bridge_info.get("motor_readout", {}),
                    "controller_channels": controller_values,
                }
            )
            completed_cycles = cycle + 1
    except Exception as exc:  # pragma: no cover - runtime failure path
        failure_type = type(exc).__name__
        failure_message = str(exc)
    finally:
        logger.close()
        wall_seconds = perf_counter() - wall_start
        body_runtime.close()

    trajectory_arr = np.asarray(trajectory, dtype=np.float32) if trajectory else np.zeros((0, 2), dtype=np.float32)
    metrics = compute_parity_metrics(trajectory_arr, control_interval_s)
    metrics.update(
        {
            "sim_seconds": float(observation.sim_time),
            "wall_seconds": float(wall_seconds),
            "real_time_factor": float(observation.sim_time) / float(wall_seconds) if wall_seconds else float("inf"),
            "completed_cycles": int(completed_cycles),
            "target_duration_s": float(duration_s),
            "completed_full_duration": 1.0 if not failure_type and float(observation.sim_time) + 1e-9 >= duration_s else 0.0,
            "failure_type": failure_type,
            "failure_message": failure_message,
        }
    )
    write_metrics_csv(run_dir / "metrics.csv", metrics)
    save_trajectory_plot(run_dir / "trajectory.png", trajectory_arr)
    save_command_plot(run_dir / "commands.png", left_hist, right_hist)
    source_demo_path = save_video(run_dir / "source_demo.mp4", source_frames, fps=video_fps)

    monitor_matrix = np.asarray(monitor_history, dtype=np.float32).T if monitor_history else np.zeros((len(monitor_labels), 0), dtype=np.float32)
    controller_matrix = np.asarray(
        [controller_history[label] for label in controller_labels],
        dtype=np.float32,
    )
    brain_voltage_arr = np.asarray(brain_voltage_frames, dtype=np.float16)
    brain_spike_arr = np.asarray(brain_spike_frames, dtype=np.uint8)
    flyvis_left_arr = np.asarray(flyvis_left_frames, dtype=np.float16)
    flyvis_right_arr = np.asarray(flyvis_right_frames, dtype=np.float16)
    capture_path = run_dir / "capture_data.npz"
    np.savez_compressed(
        capture_path,
        frame_cycles=np.asarray(frame_cycles, dtype=np.int32),
        frame_times_s=np.asarray(frame_times_s, dtype=np.float32),
        frame_target_bearing_body=np.asarray(frame_target_bearing, dtype=np.float32),
        frame_target_distance=np.asarray(frame_target_distance, dtype=np.float32),
        brain_voltage_frames=brain_voltage_arr,
        brain_spike_frames=brain_spike_arr,
        flyvis_left_frames=flyvis_left_arr,
        flyvis_right_frames=flyvis_right_arr,
        cycle_times_s=np.asarray(cycle_times_s, dtype=np.float32),
        monitor_labels=np.asarray(monitor_labels, dtype="<U64"),
        monitor_matrix=monitor_matrix,
        controller_labels=np.asarray(controller_labels, dtype="<U64"),
        controller_matrix=controller_matrix,
    )

    overview_index = len(source_frames) // 2 if source_frames else 0
    if source_frames:
        render_overview_figure(
            run_dir / "overview.png",
            demo_frame=source_frames[overview_index],
            brain_layout=brain_layout,
            flyvis_layout=flyvis_layout,
            brain_voltage=np.asarray(brain_voltage_arr[overview_index], dtype=np.float32),
            brain_spikes=np.asarray(brain_spike_arr[overview_index], dtype=np.float32),
            flyvis_left=np.asarray(flyvis_left_arr[overview_index], dtype=np.float32),
            flyvis_right=np.asarray(flyvis_right_arr[overview_index], dtype=np.float32),
            monitor_matrix=monitor_matrix,
            monitor_labels=monitor_labels,
            controller_matrix=controller_matrix,
            controller_labels=controller_labels,
            cycle_index=int(frame_cycles[overview_index]),
            frame_time_s=float(frame_times_s[overview_index]),
            target_bearing_body=float(frame_target_bearing[overview_index]),
            target_distance=float(frame_target_distance[overview_index]),
            overlay_title=title,
        )

    composite_path = run_dir / "activation_side_by_side.mp4"
    if source_frames:
        with imageio.get_writer(composite_path, fps=video_fps) as writer:
            for frame_idx, demo_frame in enumerate(source_frames):
                image = render_activation_frame(
                    demo_frame=demo_frame,
                    brain_layout=brain_layout,
                    flyvis_layout=flyvis_layout,
                    brain_voltage=np.asarray(brain_voltage_arr[frame_idx], dtype=np.float32),
                    brain_spikes=np.asarray(brain_spike_arr[frame_idx], dtype=np.float32),
                    flyvis_left=np.asarray(flyvis_left_arr[frame_idx], dtype=np.float32),
                    flyvis_right=np.asarray(flyvis_right_arr[frame_idx], dtype=np.float32),
                    monitor_matrix=monitor_matrix,
                    monitor_labels=monitor_labels,
                    controller_matrix=controller_matrix,
                    controller_labels=controller_labels,
                    cycle_index=int(frame_cycles[frame_idx]),
                    frame_time_s=float(frame_times_s[frame_idx]),
                    target_bearing_body=float(frame_target_bearing[frame_idx]),
                    target_distance=float(frame_target_distance[frame_idx]),
                    overlay_title=title,
                    max_brain_points=max_brain_points,
                    max_flyvis_points=max_flyvis_points,
                )
                writer.append_data(image)

    summary = {
        "config_path": str(config_path),
        "run_dir": str(run_dir),
        "metrics": metrics,
        "source_demo_path": None if source_demo_path is None else str(source_demo_path),
        "composite_video_path": str(composite_path) if composite_path.exists() else None,
        "overview_path": str(run_dir / "overview.png") if (run_dir / "overview.png").exists() else None,
        "capture_path": str(capture_path),
        "frame_count": int(len(source_frames)),
        "brain_neuron_count": int(brain_layout.root_ids.shape[0]),
        "flyvis_neuron_count": int(flyvis_layout.uv.shape[0]),
        "monitor_label_count": int(len(monitor_labels)),
        "controller_label_count": int(len(controller_labels)),
    }
    with (run_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a synchronized whole-brain / FlyVis / decoder / controller visualization for the current best branch.")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--mode", choices=["flygym", "mock"], default="flygym")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--output-root", default="outputs/visualizations/current_best_branch_activation")
    parser.add_argument("--max-brain-points", type=int, default=6000)
    parser.add_argument("--max-flyvis-points", type=int, default=5000)
    parser.add_argument("--title", default="Current Best Branch Activation Visualization")
    args = parser.parse_args()
    summary = build_activation_visualization(
        config_path=args.config,
        mode=args.mode,
        duration_s=args.duration,
        output_root=args.output_root,
        max_brain_points=args.max_brain_points,
        max_flyvis_points=args.max_flyvis_points,
        title=str(args.title),
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

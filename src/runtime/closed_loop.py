from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
import shutil

import numpy as np
import yaml

from brain.public_ids import collapse_sensor_pool_rates
from body.interfaces import BodyCommand
from body.mock_body import MockEmbodiedRuntime
from bridge.brain_context import BrainContextConfig, BrainContextInjector
from bridge.controller import ClosedLoopBridge
from bridge.decoder import DecoderConfig, MotorDecoder
from bridge.encoder import EncoderConfig, SensoryEncoder
from bridge.visual_splice import VisualSpliceConfig, VisualSpliceInjector
from brain.mock_backend import MockWholeBrainBackend
from metrics.parity import compute_parity_metrics, write_metrics_csv
from runtime.logging_utils import JsonlLogger, make_run_dir, save_command_plot, save_trajectory_plot, save_video
from vision.feature_extractor import RealisticVisionFeatureExtractor
from vision.inferred_lateralized import InferredLateralizedFeatureExtractor


def load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_body_runtime(mode: str, config: dict, run_dir: Path):
    vision_payload_mode = config["runtime"].get("vision_payload_mode", "legacy")
    if mode == "mock":
        return MockEmbodiedRuntime(
            timestep=float(config["runtime"]["body_timestep_s"]),
            vision_payload_mode=str(vision_payload_mode),
        )
    from body.flygym_runtime import FlyGymRealisticVisionRuntime
    return FlyGymRealisticVisionRuntime(
        timestep=float(config["runtime"]["body_timestep_s"]),
        terrain_type=config["body"].get("terrain_type", "flat"),
        leading_fly_speed=float(config["body"].get("leading_fly_speed", 15.0)),
        leading_fly_radius=float(config["body"].get("leading_fly_radius", 10.0)),
        target_fly_enabled=bool(config["body"].get("target_fly_enabled", True)),
        target_initial_phase_rad=float(config["body"].get("target_initial_phase_rad", 0.0)),
        target_angular_direction=float(config["body"].get("target_angular_direction", 1.0)),
        output_dir=run_dir,
        camera_fps=int(config["runtime"].get("video_fps", 24)),
        force_cpu_vision=bool(config["runtime"].get("force_cpu_vision", False)),
        vision_payload_mode=str(vision_payload_mode),
    )


def build_brain_backend(mode: str, config: dict):
    backend_name = config["brain"].get("backend", "mock") if mode == "mock" else config["brain"].get("backend", "torch")
    if backend_name == "mock":
        return MockWholeBrainBackend(dt_ms=float(config["brain"].get("dt_ms", 0.1)))
    if backend_name == "zero":
        from brain.zero_backend import ZeroWholeBrainBackend
        return ZeroWholeBrainBackend(dt_ms=float(config["brain"].get("dt_ms", 0.1)))
    from brain.pytorch_backend import WholeBrainTorchBackend
    return WholeBrainTorchBackend(completeness_path=config["brain"]["completeness_path"], connectivity_path=config["brain"]["connectivity_path"], cache_dir=config["brain"].get("cache_dir", "outputs/cache"), device=config["brain"].get("device", "cuda:0"), dt_ms=float(config["brain"].get("dt_ms", 0.1)))


def build_bridge(config: dict, brain_backend) -> ClosedLoopBridge:
    brain_context_cfg = BrainContextConfig.from_mapping(config.get("brain_context"))
    encoder_cfg = EncoderConfig.from_mapping(config.get("encoder"))
    decoder_cfg = DecoderConfig.from_mapping(config.get("decoder"))
    inferred_visual_cfg = config.get("inferred_visual") or {}
    visual_splice_cfg = VisualSpliceConfig.from_mapping(config.get("visual_splice"))
    vision_extractor = None
    decoder = MotorDecoder(decoder_cfg)
    if hasattr(brain_backend, "set_monitored_ids") and hasattr(decoder, "required_neuron_ids"):
        brain_backend.set_monitored_ids(decoder.required_neuron_ids())
    if bool(inferred_visual_cfg.get("enabled", False)):
        inferred_turn_extractor = InferredLateralizedFeatureExtractor.from_probe_csv(
            inferred_visual_cfg.get("probe_csv", "outputs/metrics/inferred_lateralized_visual_candidates.csv"),
            min_score=float(inferred_visual_cfg.get("min_score", 0.02)),
            tracking_limit=int(inferred_visual_cfg.get("tracking_limit", 6)),
            flow_limit=int(inferred_visual_cfg.get("flow_limit", 4)),
        )
        vision_extractor = RealisticVisionFeatureExtractor(inferred_turn_extractor=inferred_turn_extractor)
    return ClosedLoopBridge(
        brain_backend=brain_backend,
        encoder=SensoryEncoder(encoder_cfg),
        decoder=decoder,
        vision_extractor=vision_extractor,
        brain_context_injector=BrainContextInjector(brain_context_cfg),
        visual_splice_injector=VisualSpliceInjector(visual_splice_cfg),
    )


def run_closed_loop(config: dict, mode: str, duration_s: float | None = None, output_root: str | Path = "outputs") -> dict:
    runtime_cfg = config["runtime"]
    control_interval_s = float(runtime_cfg["control_interval_s"])
    duration_s = float(duration_s or runtime_cfg["duration_s"])
    run_dir = make_run_dir(output_root, f"{mode}-demo")
    body_runtime = build_body_runtime(mode, config, run_dir)
    brain_backend = build_brain_backend(mode, config)
    bridge = build_bridge(config, brain_backend)
    bridge.reset(seed=int(runtime_cfg.get("seed", 0)))
    observation = body_runtime.reset(seed=int(runtime_cfg.get("seed", 0)))
    num_cycles = int(duration_s / control_interval_s)
    num_substeps = max(1, int(round(control_interval_s / body_runtime.timestep)))
    num_brain_steps = max(1, int(round(control_interval_s / (float(config["brain"].get("dt_ms", 0.1)) / 1000.0))))
    logger = JsonlLogger(run_dir / "run.jsonl")
    trajectory = []
    left_hist = []
    right_hist = []
    frames = []
    wall_start = perf_counter()
    command = BodyCommand(left_drive=float(runtime_cfg.get("initial_left_drive", 0.0)), right_drive=float(runtime_cfg.get("initial_right_drive", 0.0)))
    failure_type = ""
    failure_message = ""
    completed_cycles = 0
    try:
        for cycle in range(num_cycles):
            bridge_wall_start = perf_counter()
            readout, bridge_info = bridge.step(observation, num_brain_steps=num_brain_steps)
            bridge_wall = perf_counter() - bridge_wall_start
            command = readout.command
            observation = body_runtime.step(command, num_substeps=num_substeps)
            frame = body_runtime.render_frame()
            if frame is not None and cycle % int(runtime_cfg.get("video_stride", 1)) == 0:
                frames.append(frame)
            trajectory.append(np.array(observation.position_xy))
            left_hist.append(command.left_drive)
            right_hist.append(command.right_drive)
            logger.write(
                {
                    "cycle": cycle,
                    "sim_time": observation.sim_time,
                    "position_x": observation.position_xy[0],
                    "position_y": observation.position_xy[1],
                    "yaw": observation.yaw,
                    "bridge_wall_seconds": bridge_wall,
                    "left_drive": command.left_drive,
                    "right_drive": command.right_drive,
                    "forward_speed": observation.forward_speed,
                    "yaw_rate": observation.yaw_rate,
                    "public_input_rates": collapse_sensor_pool_rates(bridge_info["sensor_pool_rates"]),
                    "body_metadata": observation.metadata,
                    "target_state": observation.metadata.get("target_state", {}),
                    **bridge_info,
                }
            )
            completed_cycles = cycle + 1
    except Exception as exc:
        failure_type = type(exc).__name__
        failure_message = str(exc)
    finally:
        logger.close()
        wall_seconds = perf_counter() - wall_start
        trajectory_arr = np.asarray(trajectory) if trajectory else np.zeros((0, 2))
        metrics = compute_parity_metrics(trajectory_arr, control_interval_s)
        metrics.update(
            {
                "sim_seconds": float(observation.sim_time),
                "wall_seconds": wall_seconds,
                "real_time_factor": float(observation.sim_time) / wall_seconds if wall_seconds else float("inf"),
                "device": getattr(brain_backend, "device_name", "unknown"),
                "mode": mode,
                "completed_cycles": completed_cycles,
                "target_duration_s": duration_s,
                "completed_full_duration": 1.0 if not failure_type and float(observation.sim_time) + 1e-9 >= duration_s else 0.0,
                "stable": 0.0 if failure_type else metrics.get("stable", 1.0),
                "failure_type": failure_type,
                "failure_message": failure_message,
            }
        )
    metrics_path = run_dir / "metrics.csv"
    write_metrics_csv(metrics_path, metrics)
    save_trajectory_plot(run_dir / "trajectory.png", trajectory_arr)
    save_command_plot(run_dir / "commands.png", left_hist, right_hist)
    video_path = save_video(run_dir / "demo.mp4", frames, fps=int(runtime_cfg.get("video_fps", 24)))
    summary = {"run_dir": str(run_dir), "metrics_path": str(metrics_path), "video_path": str(video_path) if video_path else None, "log_path": str(run_dir / "run.jsonl"), "metrics": metrics}
    with open(run_dir / "summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    output_root_path = Path(output_root).resolve()
    outputs_root = output_root_path.parent if output_root_path.name == "demos" else output_root_path
    logs_dir = outputs_root / "logs"
    metrics_dir = outputs_root / "metrics"
    logs_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(run_dir / "run.jsonl", logs_dir / f"{run_dir.name}.jsonl")
    shutil.copy2(metrics_path, metrics_dir / f"{run_dir.name}.csv")
    if video_path:
        demos_dir = outputs_root / "demos"
        demos_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(video_path, demos_dir / f"{run_dir.name}{Path(video_path).suffix}")
    body_runtime.close()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the closed-loop fly simulation")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--mode", choices=["mock", "flygym"], default="mock")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--output-root", default="outputs/demos")
    parser.add_argument("--vision-payload-mode", choices=["legacy", "fast"], default=None)
    parser.add_argument("--brain-context-mode", choices=["none", "public_p9_context", "inferred_visual_turn_context", "inferred_visual_p9_context"], default=None)
    parser.add_argument("--brain-context-p9-rate-hz", type=float, default=None)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.vision_payload_mode is not None:
        config.setdefault("runtime", {})["vision_payload_mode"] = args.vision_payload_mode
    if args.brain_context_mode is not None:
        config.setdefault("brain_context", {})["mode"] = args.brain_context_mode
    if args.brain_context_p9_rate_hz is not None:
        config.setdefault("brain_context", {})["p9_rate_hz"] = float(args.brain_context_p9_rate_hz)
    summary = run_closed_loop(config, mode=args.mode, duration_s=args.duration, output_root=args.output_root)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

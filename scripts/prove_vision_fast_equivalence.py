from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from body.flygym_runtime import FlyGymRealisticVisionRuntime
from body.interfaces import BodyCommand, BodyObservation
from brain.mock_backend import MockWholeBrainBackend
from bridge.controller import ClosedLoopBridge
from vision.feature_extractor import RealisticVisionFeatureExtractor
from vision.flyvis_fast_path import build_required_cell_indices


@dataclass
class SampleResult:
    sample_name: str
    exact_feature_match: bool
    exact_sensor_pool_match: bool
    exact_sensor_metadata_match: bool
    exact_motor_rate_match: bool
    exact_command_match: bool
    max_feature_abs_diff: float
    max_command_abs_diff: float
    vision_payload_mode_legacy: str
    vision_payload_mode_fast: str


def load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _feature_tuple(features) -> tuple[float, float, float, float]:
    return (
        float(features.salience_left),
        float(features.salience_right),
        float(features.flow_left),
        float(features.flow_right),
    )


def compare_same_input(
    observation: BodyObservation,
    extractor: RealisticVisionFeatureExtractor,
) -> SampleResult:
    cache = observation.realistic_vision_index_cache
    if cache is None:
        raise ValueError("Observation is missing realistic_vision_index_cache")
    if observation.realistic_vision_array is None:
        raise ValueError("Observation is missing realistic_vision_array")

    legacy_features = extractor.extract(observation.realistic_vision)
    fast_features = extractor.extract_from_array(observation.realistic_vision_array, cache)
    legacy_feature_values = np.asarray(_feature_tuple(legacy_features), dtype=float)
    fast_feature_values = np.asarray(_feature_tuple(fast_features), dtype=float)

    legacy_bridge = ClosedLoopBridge(MockWholeBrainBackend(), vision_extractor=extractor)
    fast_bridge = ClosedLoopBridge(MockWholeBrainBackend(), vision_extractor=extractor)
    legacy_readout, legacy_info = legacy_bridge.step(observation, num_brain_steps=20)
    fast_observation = replace(
        observation,
        realistic_vision={},
        realistic_vision_features=fast_features.to_dict(),
        vision_payload_mode="fast",
    )
    fast_readout, fast_info = fast_bridge.step(fast_observation, num_brain_steps=20)

    exact_command_match = (
        legacy_readout.command.left_drive == fast_readout.command.left_drive
        and legacy_readout.command.right_drive == fast_readout.command.right_drive
    )
    return SampleResult(
        sample_name="",
        exact_feature_match=bool(np.array_equal(legacy_feature_values, fast_feature_values)),
        exact_sensor_pool_match=legacy_info["sensor_pool_rates"] == fast_info["sensor_pool_rates"],
        exact_sensor_metadata_match=legacy_info["sensor_metadata"] == fast_info["sensor_metadata"],
        exact_motor_rate_match=legacy_readout.neuron_rates == fast_readout.neuron_rates,
        exact_command_match=exact_command_match,
        max_feature_abs_diff=float(np.max(np.abs(legacy_feature_values - fast_feature_values))),
        max_command_abs_diff=float(
            max(
                abs(legacy_readout.command.left_drive - fast_readout.command.left_drive),
                abs(legacy_readout.command.right_drive - fast_readout.command.right_drive),
            )
        ),
        vision_payload_mode_legacy=observation.vision_payload_mode,
        vision_payload_mode_fast=fast_observation.vision_payload_mode,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Prove fast vision equivalence against the legacy LayerActivity path.")
    parser.add_argument("--config", default="configs/flygym_realistic_vision.yaml")
    parser.add_argument("--output", default="outputs/metrics/vision_fast_equivalence.json")
    parser.add_argument("--num-step-samples", type=int, default=2)
    args = parser.parse_args()

    config = load_config(args.config)
    extractor = RealisticVisionFeatureExtractor()
    runtime = FlyGymRealisticVisionRuntime(
        timestep=float(config["runtime"]["body_timestep_s"]),
        terrain_type=config["body"].get("terrain_type", "flat"),
        leading_fly_speed=float(config["body"].get("leading_fly_speed", 15.0)),
        leading_fly_radius=float(config["body"].get("leading_fly_radius", 10.0)),
        output_dir="outputs/demos",
        camera_fps=int(config["runtime"].get("video_fps", 24)),
        force_cpu_vision=bool(config["runtime"].get("force_cpu_vision", False)),
        vision_payload_mode="legacy",
    )
    results: list[SampleResult] = []
    try:
        observation = runtime.reset(seed=int(config["runtime"].get("seed", 0)))
        cache = build_required_cell_indices(
            runtime.fly.vision_network.connectome,
            tracking_cells=extractor.tracking_cells,
            flow_cells=extractor.flow_cells,
        )
        observation = replace(observation, realistic_vision_index_cache=cache, vision_payload_mode="legacy")
        reset_result = compare_same_input(observation, extractor)
        reset_result.sample_name = "reset"
        results.append(reset_result)

        control_interval_s = float(config["runtime"].get("control_interval_s", 0.002))
        num_substeps = max(1, int(round(control_interval_s / runtime.timestep)))
        command = BodyCommand(
            left_drive=float(config["runtime"].get("initial_left_drive", 0.8)),
            right_drive=float(config["runtime"].get("initial_right_drive", 0.8)),
        )
        for step_idx in range(args.num_step_samples):
            observation = runtime.step(command, num_substeps=num_substeps)
            observation = replace(observation, realistic_vision_index_cache=cache, vision_payload_mode="legacy")
            step_result = compare_same_input(observation, extractor)
            step_result.sample_name = f"step_{step_idx + 1}"
            results.append(step_result)
    finally:
        runtime.close()

    index_checks = {}
    for cell in [*extractor.tracking_cells, *extractor.flow_cells]:
        layer_index = np.asarray(runtime.fly.vision_network.connectome.nodes.layer_index[cell][:], dtype=int)
        cache_index = (
            cache.tracking_indices.get(cell)
            if cell in cache.tracking_indices
            else cache.flow_indices.get(cell)
        )
        index_checks[cell] = bool(np.array_equal(layer_index, cache_index))

    summary = {
        "config": args.config,
        "all_index_arrays_exact": all(index_checks.values()),
        "index_checks": index_checks,
        "all_samples_exact_feature_match": all(item.exact_feature_match for item in results),
        "all_samples_exact_sensor_pool_match": all(item.exact_sensor_pool_match for item in results),
        "all_samples_exact_sensor_metadata_match": all(item.exact_sensor_metadata_match for item in results),
        "all_samples_exact_motor_rate_match": all(item.exact_motor_rate_match for item in results),
        "all_samples_exact_command_match": all(item.exact_command_match for item in results),
        "max_feature_abs_diff": float(max(item.max_feature_abs_diff for item in results)),
        "max_command_abs_diff": float(max(item.max_command_abs_diff for item in results)),
        "samples": [asdict(item) for item in results],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(output_path)


if __name__ == "__main__":
    main()

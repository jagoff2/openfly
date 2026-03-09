from __future__ import annotations

import argparse
import copy
from pathlib import Path
from time import perf_counter
import sys

import matplotlib.pyplot as plt
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from body.interfaces import BodyCommand
from body.mock_body import MockEmbodiedRuntime
from metrics.timing import BenchmarkRecord, write_benchmark_csv
from vision.feature_extractor import RealisticVisionFeatureExtractor


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--duration", type=float, default=2.0)
    parser.add_argument("--mode", choices=["mock", "flygym"], default="mock")
    parser.add_argument("--vision-payload-mode", choices=["legacy", "fast"], default=None)
    parser.add_argument("--output-csv", default="outputs/benchmarks/vision_benchmarks.csv")
    parser.add_argument("--plot-path", default="outputs/plots/vision_benchmarks.png")
    args = parser.parse_args()
    config = copy.deepcopy(load_config(args.config))
    vision_payload_mode = args.vision_payload_mode or config.setdefault("runtime", {}).get("vision_payload_mode", "legacy")
    config["runtime"]["vision_payload_mode"] = vision_payload_mode
    commit_hash = "not_a_git_repo"
    command = BodyCommand(left_drive=0.8, right_drive=0.8)
    extractor = RealisticVisionFeatureExtractor()
    if args.mode == "mock":
        body = MockEmbodiedRuntime(
            timestep=float(config["runtime"]["body_timestep_s"]),
            vision_payload_mode=vision_payload_mode,
        )
        body.reset(seed=0)
        num_steps = int(args.duration / body.timestep)
        wall_start = perf_counter()
        for _ in range(num_steps):
            obs = body.step(command=command, num_substeps=1)
            extractor.extract_observation(obs)
        wall_seconds = perf_counter() - wall_start
        benchmark_name = f"vision_mock_{vision_payload_mode}"
        backend = f"mock_realistic_vision_{vision_payload_mode}"
    else:
        from body.flygym_runtime import FlyGymRealisticVisionRuntime

        body = FlyGymRealisticVisionRuntime(
            timestep=float(config["runtime"]["body_timestep_s"]),
            terrain_type=config["body"].get("terrain_type", "flat"),
            leading_fly_speed=float(config["body"].get("leading_fly_speed", 15.0)),
            leading_fly_radius=float(config["body"].get("leading_fly_radius", 10.0)),
            output_dir="outputs/demos",
            camera_fps=int(config["runtime"].get("video_fps", 24)),
            force_cpu_vision=bool(config["runtime"].get("force_cpu_vision", False)),
            vision_payload_mode=vision_payload_mode,
        )
        try:
            body.reset(seed=0)
            control_interval_s = float(config["runtime"].get("control_interval_s", 0.002))
            num_cycles = int(args.duration / control_interval_s)
            num_substeps = max(1, int(round(control_interval_s / body.timestep)))
            wall_start = perf_counter()
            for _ in range(num_cycles):
                obs = body.step(command=command, num_substeps=num_substeps)
                extractor.extract_observation(obs)
            wall_seconds = perf_counter() - wall_start
        finally:
            body.close()
        benchmark_name = f"vision_flygym_{vision_payload_mode}"
        backend = f"flygym_realistic_vision_{vision_payload_mode}"
    records = [BenchmarkRecord(benchmark_name=benchmark_name, backend=backend, device="cpu", wall_seconds=wall_seconds, sim_seconds=args.duration, real_time_factor=args.duration / wall_seconds if wall_seconds else float("inf"), config=args.config, commit_hash=commit_hash, status="success")]
    csv_path = Path(args.output_csv)
    write_benchmark_csv(csv_path, records)
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar([records[0].benchmark_name], [records[0].real_time_factor])
    ax.set_ylabel("real_time_factor")
    ax.set_title("Vision benchmark")
    fig.tight_layout()
    plot_path = Path(args.plot_path)
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_path)
    plt.close(fig)
    print(csv_path)

if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from body.interfaces import BodyCommand
from body.mock_body import MockEmbodiedRuntime
from metrics.timing import BenchmarkRecord, write_benchmark_csv


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--durations", nargs="*", type=float, default=[1.0, 2.0])
    parser.add_argument("--mode", choices=["mock", "flygym"], default="mock")
    parser.add_argument("--output-csv", default="outputs/benchmarks/body_benchmarks.csv")
    parser.add_argument("--plot-path", default="outputs/plots/body_benchmarks.png")
    args = parser.parse_args()
    config = load_config(args.config)
    timestep = float(config["runtime"]["body_timestep_s"])
    commit_hash = "not_a_git_repo"
    command = BodyCommand(left_drive=0.9, right_drive=0.9)
    records = []
    for duration in args.durations:
        if args.mode == "mock":
            body = MockEmbodiedRuntime(timestep=timestep)
            body.reset(seed=0)
            num_steps = int(duration / timestep)
            wall_start = perf_counter()
            for _ in range(num_steps):
                body.step(command, num_substeps=1)
            wall_seconds = perf_counter() - wall_start
            backend = "mock_body"
        else:
            from flygym import SingleFlySimulation
            from flygym.examples.locomotion import HybridTurningFly

            contact_sensor_placements = [f"{leg}{segment}" for leg in ["LF", "LM", "LH", "RF", "RM", "RH"] for segment in ["Tibia", "Tarsus1", "Tarsus2", "Tarsus3", "Tarsus4", "Tarsus5"]]
            fly = HybridTurningFly(contact_sensor_placements=contact_sensor_placements, enable_adhesion=True, timestep=timestep, spawn_pos=(0.0, 0.0, 0.3))
            sim = SingleFlySimulation(fly=fly, timestep=timestep)
            try:
                sim.reset(seed=0)
                num_steps = int(duration / timestep)
                wall_start = perf_counter()
                for _ in range(num_steps):
                    sim.step(action=np.array([command.left_drive, command.right_drive], dtype=float))
                wall_seconds = perf_counter() - wall_start
            finally:
                sim.close()
            backend = "flygym_body"
        records.append(BenchmarkRecord(benchmark_name=f"body_{duration:g}s", backend=backend, device="cpu", wall_seconds=wall_seconds, sim_seconds=duration, real_time_factor=duration / wall_seconds if wall_seconds else float("inf"), config=args.config, commit_hash=commit_hash, status="success"))
    csv_path = Path(args.output_csv)
    write_benchmark_csv(csv_path, records)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar([r.benchmark_name for r in records], [r.real_time_factor for r in records])
    ax.set_ylabel("real_time_factor")
    ax.set_title("Body benchmark")
    fig.tight_layout()
    plot_path = Path(args.plot_path)
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_path)
    plt.close(fig)
    print(csv_path)

if __name__ == "__main__":
    main()

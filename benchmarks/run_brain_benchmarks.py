from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

import matplotlib.pyplot as plt
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from brain.mock_backend import MockWholeBrainBackend
from metrics.timing import BenchmarkRecord, write_benchmark_csv


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_backend(config: dict):
    backend_name = config["brain"].get("backend", "mock")
    if backend_name == "mock":
        return backend_name, MockWholeBrainBackend(dt_ms=float(config["brain"].get("dt_ms", 0.1)))
    if backend_name == "brian2cpu":
        return backend_name, None
    from brain.pytorch_backend import WholeBrainTorchBackend
    backend = WholeBrainTorchBackend(completeness_path=config["brain"]["completeness_path"], connectivity_path=config["brain"]["connectivity_path"], cache_dir=config["brain"].get("cache_dir", "outputs/cache"), device=config["brain"].get("device", "cuda:0"), dt_ms=float(config["brain"].get("dt_ms", 0.1)))
    return backend_name, backend


def run_brian2_benchmark(duration: float) -> dict[str, float | str]:
    command = [
        sys.executable,
        str(ROOT / "external" / "fly-brain" / "main.py"),
        "--brian2-cpu",
        "--t_run",
        f"{duration:g}",
        "--n_run",
        "1",
        "--no_log_file",
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    df = pd.read_csv(ROOT / "external" / "fly-brain" / "data" / "benchmark-results.csv")
    match = df[(df["framework"] == "Brian2 (CPU)") & (df["n_run"] == 1) & (df["t_run"] == duration)].tail(1)
    if match.empty:
        raise RuntimeError(f"No Brian2 benchmark row found for t_run={duration}")
    row = match.iloc[0]
    wall_seconds = float(row["total_time"])
    return {
        "wall_seconds": wall_seconds,
        "sim_seconds": float(duration),
        "real_time_factor": float(duration / wall_seconds) if wall_seconds else float("inf"),
        "device": "cpu",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--durations", nargs="*", type=float, default=[0.05, 0.1])
    parser.add_argument("--backend", choices=["auto", "mock", "torch", "brian2cpu"], default="auto")
    args = parser.parse_args()
    config = load_config(args.config)
    if args.backend != "auto":
        config.setdefault("brain", {})["backend"] = args.backend
    backend_name, backend = build_backend(config)
    commit_hash = "not_a_git_repo"
    records = []
    sensor_pool_rates = {"vision_left": 80.0, "vision_right": 80.0, "mech_left": 30.0, "mech_right": 30.0}
    for duration in args.durations:
        if backend_name == "brian2cpu":
            stats = run_brian2_benchmark(duration)
            device = str(stats["device"])
        else:
            stats = backend.benchmark(sensor_pool_rates, sim_seconds=duration) if hasattr(backend, "benchmark") else {"wall_seconds": duration, "sim_seconds": duration, "real_time_factor": 1.0}
            device = getattr(backend, "device_name", "mock")
        records.append(BenchmarkRecord(benchmark_name=f"brain_{duration:.3f}s", backend=backend_name, device=device, wall_seconds=float(stats["wall_seconds"]), sim_seconds=float(stats["sim_seconds"]), real_time_factor=float(stats["real_time_factor"]), config=args.config, commit_hash=commit_hash, status="success"))
    csv_path = Path("outputs/benchmarks/brain_benchmarks.csv")
    write_benchmark_csv(csv_path, records)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([r.sim_seconds for r in records], [r.real_time_factor for r in records], marker="o")
    ax.set_xlabel("sim_seconds")
    ax.set_ylabel("real_time_factor")
    ax.set_title("Brain benchmark")
    fig.tight_layout()
    fig.savefig("outputs/plots/brain_benchmarks.png")
    plt.close(fig)
    print(csv_path)

if __name__ == "__main__":
    main()

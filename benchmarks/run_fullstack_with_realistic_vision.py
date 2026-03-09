from __future__ import annotations

import argparse
import copy
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from metrics.timing import BenchmarkRecord, write_benchmark_csv
from runtime.closed_loop import run_closed_loop


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--mode", default="mock", choices=["mock", "flygym"])
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--durations", nargs="*", type=float, default=None)
    parser.add_argument("--output-root", default="outputs/demos")
    parser.add_argument("--output-csv", default="outputs/benchmarks/fullstack_benchmarks.csv")
    parser.add_argument("--plot-path", default="outputs/plots/fullstack_benchmarks.png")
    parser.add_argument("--vision-payload-mode", choices=["legacy", "fast"], default=None)
    parser.add_argument("--brain-context-mode", choices=["none", "public_p9_context"], default=None)
    parser.add_argument("--brain-context-p9-rate-hz", type=float, default=None)
    args = parser.parse_args()
    config = copy.deepcopy(load_config(args.config))
    vision_payload_mode = args.vision_payload_mode or config.setdefault("runtime", {}).get("vision_payload_mode", "legacy")
    config["runtime"]["vision_payload_mode"] = vision_payload_mode
    if args.brain_context_mode is not None:
        config.setdefault("brain_context", {})["mode"] = args.brain_context_mode
    brain_context_mode = config.get("brain_context", {}).get("mode", "none")
    if args.brain_context_p9_rate_hz is not None:
        config.setdefault("brain_context", {})["p9_rate_hz"] = float(args.brain_context_p9_rate_hz)
    brain_context_suffix = "" if brain_context_mode == "none" else f"_{brain_context_mode}"
    commit_hash = "not_a_git_repo"
    durations = args.durations or ([args.duration] if args.duration is not None else [2.0])
    records = []
    for duration in durations:
        summary = run_closed_loop(config, mode=args.mode, duration_s=duration, output_root=args.output_root)
        metrics = summary["metrics"]
        records.append(BenchmarkRecord(benchmark_name=f"fullstack_{args.mode}_{vision_payload_mode}{brain_context_suffix}_{duration:g}s", backend=f"{config['brain'].get('backend', 'mock')}_{vision_payload_mode}{brain_context_suffix}", device=str(metrics["device"]), wall_seconds=float(metrics["wall_seconds"]), sim_seconds=float(metrics["sim_seconds"]), real_time_factor=float(metrics["real_time_factor"]), config=args.config, commit_hash=commit_hash, status="success"))
    csv_path = Path(args.output_csv)
    write_benchmark_csv(csv_path, records)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([record.sim_seconds for record in records], [record.real_time_factor for record in records], marker="o")
    ax.set_xlabel("sim_seconds")
    ax.set_ylabel("real_time_factor")
    ax.set_title("Full-stack benchmark")
    fig.tight_layout()
    plot_path = Path(args.plot_path)
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_path)
    plt.close(fig)
    print(csv_path)

if __name__ == "__main__":
    main()

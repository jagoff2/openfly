from __future__ import annotations

import argparse
import cProfile
import io
from pathlib import Path
import pstats
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from runtime.closed_loop import run_closed_loop


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--mode", choices=["mock", "flygym"], default="mock")
    parser.add_argument("--duration", type=float, default=0.1)
    parser.add_argument("--sort-by", default="cumtime")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--output-prefix", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    profiling_dir = Path("outputs/profiling")
    profiling_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.output_prefix or f"fullstack_{args.mode}_{args.duration:g}s"
    profile_path = profiling_dir / f"{prefix}.prof"
    text_path = profiling_dir / f"{prefix}.txt"

    profiler = cProfile.Profile()
    profiler.enable()
    run_closed_loop(config, mode=args.mode, duration_s=args.duration, output_root="outputs/demos")
    profiler.disable()
    profiler.dump_stats(profile_path)

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats(args.sort_by)
    stats.print_stats(args.limit)
    text_path.write_text(stream.getvalue(), encoding="utf-8")

    print(profile_path)
    print(text_path)


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
from pathlib import Path
import subprocess
import sys


def test_benchmark_output_format() -> None:
    csv_path = Path("tests/.tmp/body_benchmarks.csv")
    plot_path = Path("tests/.tmp/body_benchmarks.png")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "benchmarks/run_body_benchmarks.py", "--config", "configs/mock_demo.yaml", "--durations", "0.2", "--output-csv", str(csv_path), "--plot-path", str(plot_path)], check=True)
    assert csv_path.exists()
    with csv_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        row = next(reader)
    expected = {"benchmark_name", "backend", "device", "wall_seconds", "sim_seconds", "real_time_factor", "config", "commit_hash", "status"}
    assert expected.issubset(row.keys())


def test_fullstack_benchmark_output_format() -> None:
    csv_path = Path("tests/.tmp/fullstack_benchmarks.csv")
    plot_path = Path("tests/.tmp/fullstack_benchmarks.png")
    output_root = Path("tests/.tmp/demos")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "benchmarks/run_fullstack_with_realistic_vision.py", "--config", "configs/mock_demo.yaml", "--mode", "mock", "--durations", "0.1", "--output-root", str(output_root), "--output-csv", str(csv_path), "--plot-path", str(plot_path)], check=True)
    assert csv_path.exists()
    with csv_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        row = next(reader)
    expected = {"benchmark_name", "backend", "device", "wall_seconds", "sim_seconds", "real_time_factor", "config", "commit_hash", "status"}
    assert expected.issubset(row.keys())
    assert plot_path.exists()

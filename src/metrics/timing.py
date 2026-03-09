from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class BenchmarkRecord:
    benchmark_name: str
    backend: str
    device: str
    wall_seconds: float
    sim_seconds: float
    real_time_factor: float
    config: str
    commit_hash: str
    status: str

def write_benchmark_csv(path: str | Path, records: list[BenchmarkRecord]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(records[0]).keys()) if records else ["benchmark_name", "backend", "device", "wall_seconds", "sim_seconds", "real_time_factor", "config", "commit_hash", "status"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))

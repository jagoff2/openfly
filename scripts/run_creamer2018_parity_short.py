from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis.creamer_parity_short import (  # noqa: E402
    build_creamer_parity_short_config,
    summarize_creamer_run,
)
from runtime.closed_loop import run_closed_loop  # noqa: E402


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the shortest lawful parity-path Creamer treadmill assay pair.")
    parser.add_argument("--mode", default="flygym", choices=["mock", "flygym"])
    parser.add_argument("--output-root", default="outputs/creamer2018_parity_short_synced")
    parser.add_argument("--block-duration", type=float, default=0.1)
    parser.add_argument("--scene-velocity-offset", type=float, default=-0.5)
    args = parser.parse_args()

    output_root = Path(args.output_root)
    pair_rows: list[dict[str, object]] = []
    pair_summary: dict[str, object] = {
        "assay": "creamer2018_parity_short_synced",
        "block_duration_s": float(args.block_duration),
        "scene_velocity_offset_mm_s": float(args.scene_velocity_offset),
    }

    for label, ablated in [("baseline", False), ("t4t5_ablated", True)]:
        config = build_creamer_parity_short_config(
            ablated=ablated,
            block_duration_s=float(args.block_duration),
            scene_velocity_offset_mm_s=float(args.scene_velocity_offset),
        )
        duration_s = float(config["runtime"]["duration_s"])
        run = run_closed_loop(
            config,
            mode=args.mode,
            duration_s=duration_s,
            output_root=output_root / label,
        )
        row = {"label": label, "ablated": ablated}
        row.update(summarize_creamer_run(run))
        pair_rows.append(row)
        pair_summary[label] = row

    if len(pair_rows) == 2:
        base, abl = pair_rows
        pair_summary["delta_front_to_back_delta_forward_speed_mean"] = float(
            abl["front_to_back_delta_forward_speed_mean"]  # type: ignore[index]
        ) - float(base["front_to_back_delta_forward_speed_mean"])  # type: ignore[index]
        pair_summary["delta_speed_fold_change"] = float(abl["speed_fold_change"]) - float(base["speed_fold_change"])  # type: ignore[index]

    metrics_dir = output_root / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    json_path = metrics_dir / "creamer2018_parity_short_pair_summary.json"
    csv_path = metrics_dir / "creamer2018_parity_short_pair_summary.csv"
    json_path.write_text(json.dumps(pair_summary, indent=2), encoding="utf-8")
    _write_csv(csv_path, pair_rows)
    print(json_path)


if __name__ == "__main__":
    main()

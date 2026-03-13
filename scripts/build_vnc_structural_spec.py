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

from vnc.ingest import load_vnc_graph_slice
from vnc.spec_builder import build_vnc_structural_spec


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a structural VNC spec from annotation and edge exports.")
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--edges", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-csv", default=None)
    args = parser.parse_args()

    graph = load_vnc_graph_slice(args.annotations, args.edges)
    spec = build_vnc_structural_spec(graph)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(spec.to_dict(), indent=2), encoding="utf-8")

    if args.output_csv:
        output_csv = Path(args.output_csv)
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        with output_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "root_id",
                    "cell_type",
                    "side",
                    "region",
                    "left_direct_weight",
                    "right_direct_weight",
                    "left_premotor_path_weight",
                    "right_premotor_path_weight",
                    "left_total_weight",
                    "right_total_weight",
                    "total_motor_weight",
                    "motor_target_count",
                ],
            )
            writer.writeheader()
            for channel in spec.channels:
                writer.writerow(channel.to_dict())


if __name__ == "__main__":
    main()

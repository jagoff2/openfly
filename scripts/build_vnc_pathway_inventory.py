from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vnc.ingest import load_vnc_graph_slice
from vnc.pathways import build_vnc_pathway_inventory


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a simple descending-to-premotor-to-motor pathway inventory from VNC exports.")
    parser.add_argument("--annotations", required=True, help="Path to annotation CSV/TSV/JSON.")
    parser.add_argument("--edges", required=True, help="Path to edge CSV/TSV/JSON.")
    parser.add_argument("--output-json", required=True, help="Path to write inventory JSON.")
    args = parser.parse_args()

    graph = load_vnc_graph_slice(args.annotations, args.edges)
    inventory = build_vnc_pathway_inventory(graph)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(inventory.to_dict(), indent=2), encoding="utf-8")
    print(output_json)


if __name__ == "__main__":
    main()

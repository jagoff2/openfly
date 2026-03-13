from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vnc.annotation_atlas import build_vnc_annotation_atlas
from vnc.data_sources import get_vnc_dataset_sources


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a compact atlas summary from a VNC annotation export.")
    parser.add_argument("--input", required=True, help="Path to a CSV/TSV/JSON annotation export.")
    parser.add_argument("--output-json", required=True, help="Path to write the atlas summary JSON.")
    parser.add_argument("--output-csv", default=None, help="Optional CSV path for paired cell types.")
    parser.add_argument("--source-key", default=None, help="Optional source key for logging context (e.g. manc, fanc, banc).")
    args = parser.parse_args()

    atlas = build_vnc_annotation_atlas(args.input)
    payload = atlas.to_dict()
    if args.source_key is not None:
        source_map = get_vnc_dataset_sources()
        payload["declared_source_key"] = args.source_key
        payload["known_sources"] = [source.key for source in source_map]

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.output_csv:
        output_csv = Path(args.output_csv)
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        lines = ["cell_type,sides"]
        for row in payload["paired_cell_types"]:
            lines.append(f"{row['cell_type']},{'|'.join(row['sides'])}")
        output_csv.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(output_json)


if __name__ == "__main__":
    main()

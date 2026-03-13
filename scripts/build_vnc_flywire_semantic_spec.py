from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vnc.flywire_bridge import FlyWireSemanticBridgeConfig, build_flywire_semantic_spec_from_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Bridge a real MANC structural spec into the FlyWire monitor ID space using semantic cell_type + side groups.")
    parser.add_argument("--source-spec-json", required=True)
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--aggregate-weights", choices=("mean", "sum", "max"), default="mean")
    parser.add_argument("--min-monitor-roots", type=int, default=1)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    payload = build_flywire_semantic_spec_from_files(
        FlyWireSemanticBridgeConfig(
            source_spec_json=args.source_spec_json,
            annotation_path=args.annotation_path,
            brain_completeness_path=args.brain_completeness_path,
            aggregate_weights=args.aggregate_weights,
            min_monitor_roots=args.min_monitor_roots,
        )
    )

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()

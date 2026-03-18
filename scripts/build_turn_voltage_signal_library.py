from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pandas as pd

from analysis.turn_voltage_library import build_turn_voltage_signal_library


def _load_metadata(path: Path) -> dict[str, dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metadata: dict[str, dict[str, object]] = {}
    for item in payload.get("selected_paired_cell_types", []):
        label = str(item.get("candidate_label", "")).strip()
        if not label:
            continue
        left_super = [str(value) for value in item.get("left_super_classes", []) if str(value)]
        right_super = [str(value) for value in item.get("right_super_classes", []) if str(value)]
        super_classes = sorted({*left_super, *right_super})
        metadata[label] = {
            "left_root_ids": [int(root_id) for root_id in item.get("left_root_ids", [])],
            "right_root_ids": [int(root_id) for root_id in item.get("right_root_ids", [])],
            "super_class": super_classes[0] if super_classes else "unknown",
        }
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a voltage-turn shadow-decoder signal library from target-specific monitor rankings.")
    parser.add_argument("--ranked-monitors", required=True)
    parser.add_argument("--monitor-candidates-json", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--target-monitor-turn-csv")
    parser.add_argument("--allowed-super-classes", nargs="*", default=["visual_projection", "visual_centrifugal", "central", "ascending"])
    parser.add_argument("--turn-scale-mv", type=float, default=5.0)
    parser.add_argument("--include-label", action="append", default=[])
    parser.add_argument("--exclude-label", action="append", default=[])
    parser.add_argument("--downweight-label", action="append", default=[])
    parser.add_argument("--max-mean-asymmetry-mv", type=float)
    parser.add_argument("--weight-mode", choices=["score", "score_over_sqrt_asym"], default="score")
    args = parser.parse_args()

    ranked = pd.read_csv(args.ranked_monitors)
    metadata = _load_metadata(Path(args.monitor_candidates_json))
    target_turn = None
    if args.target_monitor_turn_csv:
        target_turn = pd.read_csv(args.target_monitor_turn_csv).set_index("label")

    downweight_labels: dict[str, float] = {}
    for raw_value in args.downweight_label:
        label, sep, value = str(raw_value).partition("=")
        if not sep:
            raise SystemExit(f"invalid --downweight-label value: {raw_value!r} (expected LABEL=FACTOR)")
        downweight_labels[label.strip()] = float(value)

    output = build_turn_voltage_signal_library(
        ranked,
        metadata,
        top_k=int(args.top_k),
        target_turn=target_turn,
        allowed_super_classes=list(args.allowed_super_classes),
        include_labels=list(args.include_label),
        exclude_labels=list(args.exclude_label),
        max_mean_asymmetry_mv=args.max_mean_asymmetry_mv,
        weight_mode=str(args.weight_mode),
        downweight_labels=downweight_labels,
        turn_scale_mv=float(args.turn_scale_mv),
    )
    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()

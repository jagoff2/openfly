from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.schaffer_nwb_canonical_dataset import export_schaffer_nwb_canonical_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Export staged Schaffer NWB files into canonical matched format.")
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("external/neural_measurements/schaffer2023_figshare"),
        help="Root directory containing staged Schaffer NWB files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/derived/schaffer2023_nwb_canonical"),
        help="Destination for canonical Schaffer bundle artifacts.",
    )
    args = parser.parse_args()
    summary = export_schaffer_nwb_canonical_dataset(args.dataset_root, output_dir=args.output_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

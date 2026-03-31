from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.aimon_canonical_dataset import export_aimon_canonical_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the staged Aimon 2023 dataset into the canonical parity schema.")
    parser.add_argument("--dataset-root", default="external/spontaneous/aimon2023_dryad")
    parser.add_argument("--output-dir", default="outputs/derived/aimon2023_canonical")
    parser.add_argument("--sampling-rate-hz", type=float, default=100.0)
    parser.add_argument("--max-experiments", type=int, default=None)
    args = parser.parse_args()

    summary = export_aimon_canonical_dataset(
        REPO_ROOT / Path(args.dataset_root),
        output_dir=REPO_ROOT / Path(args.output_dir),
        sampling_rate_hz=float(args.sampling_rate_hz),
        max_experiments=args.max_experiments,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

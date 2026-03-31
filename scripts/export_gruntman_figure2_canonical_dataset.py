from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.gruntman_figure2_canonical_dataset import export_gruntman_figure2_canonical_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Gruntman 2019 Figure 2 into the canonical parity schema.")
    parser.add_argument("--dataset-root", default="external/neural_measurements/gruntman2019_janelia")
    parser.add_argument("--output-dir", default="outputs/derived/gruntman2019_figure2_canonical")
    args = parser.parse_args()

    summary = export_gruntman_figure2_canonical_dataset(
        REPO_ROOT / Path(args.dataset_root),
        output_dir=REPO_ROOT / Path(args.output_dir),
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

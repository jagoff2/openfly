from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis.aimon_components_summary import summarize_walk_components_zip


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the staged Aimon 2023 Walk_components archive.")
    parser.add_argument(
        "--archive-path",
        default="external/spontaneous/aimon2023_dryad/Walk_components.zip",
    )
    parser.add_argument(
        "--output-path",
        default="outputs/metrics/aimon_walk_components_summary.json",
    )
    args = parser.parse_args()

    summary = summarize_walk_components_zip(args.archive_path)
    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

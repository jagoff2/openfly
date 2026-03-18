from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis.spontaneous_mesoscale_validation import write_mesoscale_validation_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Run mesoscale spontaneous-state validation on the living-brain branch.")
    parser.add_argument(
        "--target-run-dir",
        default=(
            "outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/"
            "flygym-demo-20260315-203010"
        ),
    )
    parser.add_argument(
        "--no-target-run-dir",
        default=(
            "outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/"
            "flygym-demo-20260315-204719"
        ),
    )
    parser.add_argument(
        "--completeness-path",
        default="external/fly-brain/data/2025_Completeness_783.csv",
    )
    parser.add_argument(
        "--annotation-path",
        default="outputs/cache/flywire_annotation_supplement.tsv",
    )
    parser.add_argument(
        "--public-dataset-root",
        default="external/spontaneous/aimon2023_dryad",
    )
    parser.add_argument(
        "--cache-dir",
        default="outputs/cache",
    )
    parser.add_argument(
        "--summary-path",
        default="outputs/metrics/spontaneous_mesoscale_validation_summary.json",
    )
    parser.add_argument(
        "--components-csv-path",
        default="outputs/metrics/spontaneous_mesoscale_validation_components.csv",
    )
    parser.add_argument(
        "--plots-dir",
        default="outputs/plots",
    )
    args = parser.parse_args()

    target_run_dir = Path(args.target_run_dir)
    no_target_run_dir = Path(args.no_target_run_dir)
    summary = write_mesoscale_validation_bundle(
        target_capture_path=target_run_dir / "activation_capture.npz",
        no_target_capture_path=no_target_run_dir / "activation_capture.npz",
        target_log_path=target_run_dir / "run.jsonl",
        no_target_log_path=no_target_run_dir / "run.jsonl",
        completeness_path=args.completeness_path,
        annotation_path=args.annotation_path,
        included_super_classes=(
            "central",
            "ascending",
            "visual_projection",
            "visual_centrifugal",
            "endocrine",
        ),
        min_family_size_per_side=2,
        max_family_size_per_side=128,
        public_dataset_root=args.public_dataset_root,
        cache_dir=args.cache_dir,
        output_summary_path=args.summary_path,
        output_components_csv_path=args.components_csv_path,
        plots_dir=args.plots_dir,
    )
    print(json.dumps(summary["criteria"], indent=2))


if __name__ == "__main__":
    main()

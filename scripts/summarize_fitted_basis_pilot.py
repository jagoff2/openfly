from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _read_single_row(path: str | Path) -> dict[str, str]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return next(reader)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the first matched fitted-basis multidrive pilot.")
    parser.add_argument("--target-csv", default="outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_target/metrics/flygym-demo-20260311-145836.csv")
    parser.add_argument("--no-target-csv", default="outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_no_target/metrics/flygym-demo-20260311-150139.csv")
    parser.add_argument("--zero-brain-csv", default="outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_zero_brain/metrics/flygym-demo-20260311-150253.csv")
    parser.add_argument("--output-json", default="outputs/metrics/neck_output_motor_basis_pilot_summary.json")
    args = parser.parse_args()

    target = _read_single_row(args.target_csv)
    no_target = _read_single_row(args.no_target_csv)
    zero_brain = _read_single_row(args.zero_brain_csv)

    def _f(row: dict[str, str], key: str) -> float:
        return float(row[key])

    summary = {
        "target_csv": args.target_csv,
        "no_target_csv": args.no_target_csv,
        "zero_brain_csv": args.zero_brain_csv,
        "target": target,
        "no_target": no_target,
        "zero_brain": zero_brain,
        "comparisons": {
            "target_minus_no_target_net_displacement": _f(target, "net_displacement") - _f(no_target, "net_displacement"),
            "target_minus_no_target_avg_forward_speed": _f(target, "avg_forward_speed") - _f(no_target, "avg_forward_speed"),
            "target_minus_no_target_displacement_efficiency": _f(target, "displacement_efficiency") - _f(no_target, "displacement_efficiency"),
            "target_minus_zero_brain_net_displacement": _f(target, "net_displacement") - _f(zero_brain, "net_displacement"),
            "target_minus_zero_brain_avg_forward_speed": _f(target, "avg_forward_speed") - _f(zero_brain, "avg_forward_speed"),
            "target_minus_zero_brain_displacement_efficiency": _f(target, "displacement_efficiency") - _f(zero_brain, "displacement_efficiency"),
        },
    }

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

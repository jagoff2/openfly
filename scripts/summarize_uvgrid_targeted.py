from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize targeted UV-grid orientation probe summaries.")
    parser.add_argument("summary_jsons", nargs="+")
    parser.add_argument("--csv-output", default="outputs/metrics/splice_uvgrid_targeted_comparison.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_uvgrid_targeted_comparison.json")
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    for summary_path in args.summary_jsons:
        path = Path(summary_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        conditions = data["conditions"]
        left_bias = float(conditions["body_left_dark"]["motor_rates_hz"]["turn_right"] - conditions["body_left_dark"]["motor_rates_hz"]["turn_left"])
        right_bias = float(conditions["body_right_dark"]["motor_rates_hz"]["turn_right"] - conditions["body_right_dark"]["motor_rates_hz"]["turn_left"])
        rows.append(
            {
                "summary_json": str(path),
                "swap_uv": bool(data.get("spatial_swap_uv", False)),
                "flip_u": bool(data.get("spatial_flip_u", False)),
                "flip_v": bool(data.get("spatial_flip_v", False)),
                "mirror_u_by_side": bool(data.get("spatial_mirror_u_by_side", False)),
                "mean_voltage_group_corr": float(
                    (
                        conditions["body_left_dark"]["teacher_student_group_correlation_voltage"]
                        + conditions["body_center_dark"]["teacher_student_group_correlation_voltage"]
                        + conditions["body_right_dark"]["teacher_student_group_correlation_voltage"]
                    )
                    / 3.0
                ),
                "mean_voltage_side_corr": float(
                    (
                        conditions["body_left_dark"]["teacher_student_side_diff_correlation_voltage"]
                        + conditions["body_right_dark"]["teacher_student_side_diff_correlation_voltage"]
                    )
                    / 2.0
                ),
                "left_turn_bias": left_bias,
                "right_turn_bias": right_bias,
                "sign_match": bool(left_bias < 0.0 and right_bias > 0.0),
            }
        )
    rows.sort(
        key=lambda row: (
            1 if row["sign_match"] else 0,
            float(row["mean_voltage_side_corr"]),
            float(row["mean_voltage_group_corr"]),
        ),
        reverse=True,
    )

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "summary_json",
                "swap_uv",
                "flip_u",
                "flip_v",
                "mirror_u_by_side",
                "mean_voltage_group_corr",
                "mean_voltage_side_corr",
                "left_turn_bias",
                "right_turn_bias",
                "sign_match",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "best_row": rows[0] if rows else None,
        "rows": rows,
    }
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

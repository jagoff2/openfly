from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the first causal descending motor-response atlas.")
    parser.add_argument("--input-json", default="outputs/metrics/descending_motor_atlas.json")
    parser.add_argument("--output-csv", default="outputs/metrics/descending_motor_atlas_summary.csv")
    parser.add_argument("--output-json", default="outputs/metrics/descending_motor_atlas_summary.json")
    args = parser.parse_args()

    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    rows = list(data.get("rows", []))
    baseline = next((row for row in rows if row.get("side_mode") == "baseline"), None)
    if baseline is None:
        raise ValueError("Expected a `baseline` row in the motor atlas input.")

    baseline_disp = float(baseline["net_displacement"])
    baseline_speed = float(baseline["avg_forward_speed"])
    baseline_total_drive = float(baseline["mean_total_drive"])
    baseline_yaw = float(baseline["end_yaw"])

    summary_rows: list[dict] = []
    pair_index: dict[str, dict[str, dict]] = {}
    for row in rows:
        label = str(row["label"])
        side_mode = str(row["side_mode"])
        pair_index.setdefault(label, {})[side_mode] = row
        if side_mode == "baseline":
            continue
        summary_rows.append(
            {
                "label": label,
                "side_mode": side_mode,
                "delta_net_displacement_vs_baseline": float(row["net_displacement"]) - baseline_disp,
                "delta_avg_forward_speed_vs_baseline": float(row["avg_forward_speed"]) - baseline_speed,
                "delta_mean_total_drive_vs_baseline": float(row["mean_total_drive"]) - baseline_total_drive,
                "delta_end_yaw_vs_baseline": float(row["end_yaw"]) - baseline_yaw,
                "mean_abs_drive_diff": float(row["mean_abs_drive_diff"]),
                "net_displacement": float(row["net_displacement"]),
                "avg_forward_speed": float(row["avg_forward_speed"]),
                "mean_total_drive": float(row["mean_total_drive"]),
                "end_yaw": float(row["end_yaw"]),
            }
        )

    pair_rows: list[dict] = []
    for label, side_rows in pair_index.items():
        if "left" not in side_rows or "right" not in side_rows:
            continue
        left = side_rows["left"]
        right = side_rows["right"]
        left_yaw = float(left["end_yaw"]) - baseline_yaw
        right_yaw = float(right["end_yaw"]) - baseline_yaw
        pair_rows.append(
            {
                "label": label,
                "left_delta_end_yaw_vs_baseline": left_yaw,
                "right_delta_end_yaw_vs_baseline": right_yaw,
                "mirror_yaw_sign": bool(left_yaw < 0.0 < right_yaw or right_yaw < 0.0 < left_yaw),
                "left_delta_net_displacement_vs_baseline": float(left["net_displacement"]) - baseline_disp,
                "right_delta_net_displacement_vs_baseline": float(right["net_displacement"]) - baseline_disp,
                "left_mean_abs_drive_diff": float(left["mean_abs_drive_diff"]),
                "right_mean_abs_drive_diff": float(right["mean_abs_drive_diff"]),
            }
        )

    ranked_forward = sorted(
        [row for row in summary_rows if row["side_mode"] == "bilateral"],
        key=lambda row: (row["delta_net_displacement_vs_baseline"], row["delta_avg_forward_speed_vs_baseline"]),
        reverse=True,
    )
    ranked_turn = sorted(
        pair_rows,
        key=lambda row: (
            int(row["mirror_yaw_sign"]),
            max(abs(row["left_delta_end_yaw_vs_baseline"]), abs(row["right_delta_end_yaw_vs_baseline"])),
            max(row["left_delta_net_displacement_vs_baseline"], row["right_delta_net_displacement_vs_baseline"]),
        ),
        reverse=True,
    )

    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.output_csv).open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(summary_rows[0].keys()) if summary_rows else []
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    summary = {
        "input_json": args.input_json,
        "baseline": baseline,
        "forward_ranked": ranked_forward,
        "turn_ranked": ranked_turn,
        "rows": summary_rows,
        "pair_rows": pair_rows,
    }
    Path(args.output_json).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

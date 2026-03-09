from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _extract_rows(summary_path: Path) -> list[dict[str, object]]:
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for window_key, conditions in data["results"].items():
        left_bias = float(conditions["body_left_dark"]["motor_rates_hz"]["turn_right"] - conditions["body_left_dark"]["motor_rates_hz"]["turn_left"])
        right_bias = float(conditions["body_right_dark"]["motor_rates_hz"]["turn_right"] - conditions["body_right_dark"]["motor_rates_hz"]["turn_left"])
        rows.append(
            {
                "summary_json": str(summary_path),
                "window_key": window_key,
                "input_pulse_ms": data.get("input_pulse_ms"),
                "value_scale": float(data.get("value_scale", 0.0)),
                "left_turn_bias": left_bias,
                "right_turn_bias": right_bias,
                "sign_match": bool(left_bias < 0.0 and right_bias > 0.0),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize relay drift comparison runs.")
    parser.add_argument("summary_jsons", nargs="+")
    parser.add_argument("--csv-output", default="outputs/metrics/splice_relay_drift_comparison.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_relay_drift_comparison.json")
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    for summary_json in args.summary_jsons:
        rows.extend(_extract_rows(Path(summary_json)))

    rows.sort(key=lambda row: (str(row["window_key"]), 1 if row["sign_match"] else 0, -abs(float(row["right_turn_bias"]))), reverse=False)
    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "summary_json",
                "window_key",
                "input_pulse_ms",
                "value_scale",
                "left_turn_bias",
                "right_turn_bias",
                "sign_match",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "rows": rows,
        "best_sign_preserving_rows": [row for row in rows if row["sign_match"]],
    }
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _monitored_labels(rows: list[dict]) -> list[str]:
    labels: set[str] = set()
    for row in rows:
        for key in row.get("motor_readout", {}):
            if key.startswith("monitor_") and key.endswith("_bilateral_hz"):
                labels.add(key[len("monitor_") : -len("_bilateral_hz")])
    return sorted(labels)


def _window_mean(rows: list[dict], key: str, early_s: float) -> float:
    values = [
        float(row.get("motor_readout", {}).get(key, 0.0))
        for row in rows
        if float(row.get("sim_time", 0.0)) <= early_s
    ]
    return sum(values) / len(values) if values else 0.0


def _window_max(rows: list[dict], key: str, early_s: float) -> float:
    values = [
        float(row.get("motor_readout", {}).get(key, 0.0))
        for row in rows
        if float(row.get("sim_time", 0.0)) <= early_s
    ]
    return max(values) if values else 0.0


def summarize(target_rows: list[dict], no_target_rows: list[dict], early_windows: list[float]) -> dict[str, object]:
    labels = _monitored_labels(target_rows)
    windows: list[dict[str, object]] = []
    flat_rows: list[dict[str, object]] = []
    for early_s in early_windows:
        rows = []
        for label in labels:
            key = f"monitor_{label}_bilateral_hz"
            target_mean = _window_mean(target_rows, key, early_s)
            no_target_mean = _window_mean(no_target_rows, key, early_s)
            row = {
                "early_window_s": early_s,
                "label": label,
                "target_mean_bilateral_hz": target_mean,
                "no_target_mean_bilateral_hz": no_target_mean,
                "delta_target_minus_no_target_hz": target_mean - no_target_mean,
                "target_max_bilateral_hz": _window_max(target_rows, key, early_s),
            }
            rows.append(row)
            flat_rows.append(row)
        rows.sort(key=lambda item: float(item["delta_target_minus_no_target_hz"]), reverse=True)
        windows.append(
            {
                "early_window_s": early_s,
                "top_delta_rows": rows[:10],
                "top_target_max_rows": sorted(
                    rows,
                    key=lambda item: float(item["target_max_bilateral_hz"]),
                    reverse=True,
                )[:10],
            }
        )
    return {
        "labels": labels,
        "windows": windows,
        "rows": flat_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize early-window descending population activity from monitored target/no-target logs."
    )
    parser.add_argument(
        "--target-log",
        default="outputs/requested_2s_splice_uvgrid_calibrated_monitored_target/flygym-demo-20260311-134126/run.jsonl",
    )
    parser.add_argument(
        "--no-target-log",
        default="outputs/requested_2s_splice_uvgrid_calibrated_monitored_no_target/flygym-demo-20260311-135635/run.jsonl",
    )
    parser.add_argument("--early-windows", default="0.05,0.1,0.2")
    parser.add_argument("--json-output", default="outputs/metrics/descending_early_activity.json")
    parser.add_argument("--csv-output", default="outputs/metrics/descending_early_activity.csv")
    args = parser.parse_args()

    target_rows = _load_jsonl(Path(args.target_log))
    no_target_rows = _load_jsonl(Path(args.no_target_log))
    early_windows = [float(value.strip()) for value in str(args.early_windows).split(",") if value.strip()]
    summary = summarize(target_rows, no_target_rows, early_windows)

    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    csv_path = Path(args.csv_output)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "early_window_s",
            "label",
            "target_mean_bilateral_hz",
            "no_target_mean_bilateral_hz",
            "delta_target_minus_no_target_hz",
            "target_max_bilateral_hz",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary["rows"])

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

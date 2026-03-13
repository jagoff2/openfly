from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0 or y.size == 0:
        return float("nan")
    if np.allclose(x, x[0]) or np.allclose(y, y[0]):
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _extract_monitor_labels(record: dict) -> list[str]:
    labels = set()
    for key in record.get("motor_readout", {}).keys():
        for suffix in ("_right_minus_left_hz", "_bilateral_hz", "_left_hz", "_right_hz"):
            prefix = "monitor_"
            if key.startswith(prefix) and key.endswith(suffix):
                labels.add(key[len(prefix) : -len(suffix)])
                break
    return sorted(labels)


def _series(records: list[dict], key: str) -> np.ndarray:
    return np.asarray([float(record[key]) for record in records], dtype=float)


def _nested_series(records: list[dict], outer: str, inner: str) -> np.ndarray:
    return np.asarray([float(record[outer][inner]) for record in records], dtype=float)


def summarize(target_log: Path, no_target_log: Path) -> tuple[pd.DataFrame, dict]:
    target_records = _load_jsonl(target_log)
    no_target_records = _load_jsonl(no_target_log)
    if not target_records:
        raise ValueError(f"No target records found in {target_log}")
    labels = _extract_monitor_labels(target_records[0])
    target_bearing = _nested_series(target_records, "target_state", "bearing_body")
    target_frontalness = -np.abs(target_bearing)
    target_forward_speed = _series(target_records, "forward_speed")
    target_yaw_rate = _series(target_records, "yaw_rate")
    target_total_drive = _series(target_records, "left_drive") + _series(target_records, "right_drive")
    no_target_forward_speed = _series(no_target_records, "forward_speed")
    no_target_total_drive = _series(no_target_records, "left_drive") + _series(no_target_records, "right_drive")

    rows: list[dict] = []
    for label in labels:
        target_left = _nested_series(target_records, "motor_readout", f"monitor_{label}_left_hz")
        target_right = _nested_series(target_records, "motor_readout", f"monitor_{label}_right_hz")
        target_bilateral = _nested_series(target_records, "motor_readout", f"monitor_{label}_bilateral_hz")
        target_asym = _nested_series(target_records, "motor_readout", f"monitor_{label}_right_minus_left_hz")
        no_target_left = _nested_series(no_target_records, "motor_readout", f"monitor_{label}_left_hz")
        no_target_right = _nested_series(no_target_records, "motor_readout", f"monitor_{label}_right_hz")
        no_target_bilateral = _nested_series(no_target_records, "motor_readout", f"monitor_{label}_bilateral_hz")
        no_target_asym = _nested_series(no_target_records, "motor_readout", f"monitor_{label}_right_minus_left_hz")
        rows.append(
            {
                "label": label,
                "target_mean_bilateral_hz": float(np.mean(target_bilateral)),
                "target_mean_abs_asym_hz": float(np.mean(np.abs(target_asym))),
                "no_target_mean_bilateral_hz": float(np.mean(no_target_bilateral)),
                "no_target_mean_abs_asym_hz": float(np.mean(np.abs(no_target_asym))),
                "delta_bilateral_target_minus_no_target_hz": float(np.mean(target_bilateral) - np.mean(no_target_bilateral)),
                "delta_abs_asym_target_minus_no_target_hz": float(np.mean(np.abs(target_asym)) - np.mean(np.abs(no_target_asym))),
                "corr_bilateral_vs_target_frontalness": _safe_corr(target_bilateral, target_frontalness),
                "corr_bilateral_vs_forward_speed": _safe_corr(target_bilateral, target_forward_speed),
                "corr_bilateral_vs_total_drive": _safe_corr(target_bilateral, target_total_drive),
                "corr_asym_vs_target_bearing": _safe_corr(target_asym, target_bearing),
                "corr_asym_vs_yaw_rate": _safe_corr(target_asym, target_yaw_rate),
                "target_left_mean_hz": float(np.mean(target_left)),
                "target_right_mean_hz": float(np.mean(target_right)),
                "no_target_left_mean_hz": float(np.mean(no_target_left)),
                "no_target_right_mean_hz": float(np.mean(no_target_right)),
            }
        )
    df = pd.DataFrame(rows).sort_values(
        by=[
            "delta_bilateral_target_minus_no_target_hz",
            "corr_asym_vs_target_bearing",
            "corr_bilateral_vs_target_frontalness",
        ],
        ascending=[False, False, False],
    )
    summary = {
        "target_log": str(target_log),
        "no_target_log": str(no_target_log),
        "num_labels": int(len(df)),
        "top_target_conditioned_labels": df.head(8)[
            [
                "label",
                "delta_bilateral_target_minus_no_target_hz",
                "corr_asym_vs_target_bearing",
                "corr_bilateral_vs_target_frontalness",
            ]
        ].to_dict(orient="records"),
        "top_bearing_locked_labels": df.sort_values(by="corr_asym_vs_target_bearing", ascending=False)
        .head(8)[["label", "corr_asym_vs_target_bearing", "corr_asym_vs_yaw_rate"]]
        .to_dict(orient="records"),
        "top_forward_locked_labels": df.sort_values(by="corr_bilateral_vs_forward_speed", ascending=False)
        .head(8)[["label", "corr_bilateral_vs_forward_speed", "corr_bilateral_vs_target_frontalness"]]
        .to_dict(orient="records"),
        "context": {
            "target_mean_forward_speed": float(np.mean(target_forward_speed)),
            "no_target_mean_forward_speed": float(np.mean(no_target_forward_speed)),
            "target_mean_total_drive": float(np.mean(target_total_drive)),
            "no_target_mean_total_drive": float(np.mean(no_target_total_drive)),
            "target_mean_abs_bearing": float(np.mean(np.abs(target_bearing))),
        },
    }
    return df, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize monitored descending/efferent groups from matched embodied runs.")
    parser.add_argument("--target-log", required=True)
    parser.add_argument("--no-target-log", required=True)
    parser.add_argument("--csv-output", required=True)
    parser.add_argument("--json-output", required=True)
    args = parser.parse_args()

    df, summary = summarize(Path(args.target_log), Path(args.no_target_log))
    csv_output = Path(args.csv_output)
    json_output = Path(args.json_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_output, index=False)
    json_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

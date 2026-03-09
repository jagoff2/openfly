from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import torch
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from brain.paper_task_ids import GROOMING_TASK
from brain.paper_task_probes import run_probe_sweep
from brain.pytorch_backend import WholeBrainTorchBackend


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def choose_device(device: str) -> str:
    if device != "auto":
        return device
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def summarize(df: pd.DataFrame) -> dict[str, object]:
    peak_adn1_rows = []
    peak_abn1_rows = []
    for input_group, group_df in df.groupby("input_group"):
        peak_adn1_idx = group_df["adn1_total_hz"].idxmax()
        peak_abn1_idx = group_df["abn1_hz"].idxmax()
        peak_adn1_row = group_df.loc[int(peak_adn1_idx)]
        peak_abn1_row = group_df.loc[int(peak_abn1_idx)]
        peak_adn1_rows.append(
            {
                "input_group": input_group,
                "peak_frequency_hz": float(peak_adn1_row["frequency_hz"]),
                "peak_adn1_total_hz": float(peak_adn1_row["adn1_total_hz"]),
                "peak_abn1_hz_at_adn1_peak": float(peak_adn1_row["abn1_hz"]),
                "peak_adn1_left_hz": float(peak_adn1_row["adn1_left_hz"]),
                "peak_adn1_right_hz": float(peak_adn1_row["adn1_right_hz"]),
            }
        )
        peak_abn1_rows.append(
            {
                "input_group": input_group,
                "peak_frequency_hz": float(peak_abn1_row["frequency_hz"]),
                "peak_abn1_hz": float(peak_abn1_row["abn1_hz"]),
                "peak_adn1_total_hz_at_abn1_peak": float(peak_abn1_row["adn1_total_hz"]),
                "peak_adn1_left_hz": float(peak_abn1_row["adn1_left_hz"]),
                "peak_adn1_right_hz": float(peak_abn1_row["adn1_right_hz"]),
            }
        )
    return {
        "task": GROOMING_TASK.name,
        "duration_ms": float(df["duration_ms"].iloc[0]) if not df.empty else GROOMING_TASK.default_duration_ms,
        "inputs": sorted(df["input_group"].unique().tolist()),
        "peak_adn1_rows": peak_adn1_rows,
        "peak_abn1_rows": peak_abn1_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public grooming probe (JON groups -> aDN1/aBN1) on the whole-brain backend.")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--duration-ms", type=float, default=GROOMING_TASK.default_duration_ms)
    parser.add_argument("--csv-output", default="outputs/metrics/grooming_probe.csv")
    parser.add_argument("--json-output", default="outputs/metrics/grooming_probe_summary.json")
    parser.add_argument("--plot-output", default="outputs/plots/grooming_probe.png")
    args = parser.parse_args()

    config = load_config(args.config)
    backend = WholeBrainTorchBackend(
        completeness_path=config["brain"]["completeness_path"],
        connectivity_path=config["brain"]["connectivity_path"],
        cache_dir=config["brain"].get("cache_dir", "outputs/cache"),
        device=choose_device(args.device if args.device != "auto" else config["brain"].get("device", "cuda:0")),
        dt_ms=float(config["brain"].get("dt_ms", 0.1)),
    )

    rows = run_probe_sweep(backend, GROOMING_TASK, duration_ms=args.duration_ms)
    df = pd.DataFrame(row.to_flat_dict() for row in rows)
    df["adn1_total_hz"] = df["adn1_left_hz"] + df["adn1_right_hz"]
    df["adn1_asymmetry_hz"] = df["adn1_right_hz"] - df["adn1_left_hz"]

    csv_path = Path(args.csv_output)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)

    summary = summarize(df)
    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    fig, axes = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
    for input_group, group_df in df.groupby("input_group"):
        axes[0].plot(group_df["frequency_hz"], group_df["adn1_total_hz"], marker="o", label=input_group)
        axes[1].plot(group_df["frequency_hz"], group_df["abn1_hz"], marker="o", label=input_group)
    axes[0].set_ylabel("aDN1 Total Rate (Hz)")
    axes[0].set_title("Grooming Probe: JON groups -> aDN1 / aBN1")
    axes[0].legend()
    axes[1].set_xlabel("Input Frequency (Hz)")
    axes[1].set_ylabel("aBN1 Rate (Hz)")
    fig.tight_layout()
    plot_path = Path(args.plot_output)
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_path)
    plt.close(fig)

    print(csv_path)
    print(json_path)
    print(plot_path)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.living_brain_activation_analysis import (
    build_monitor_rate_comparison,
    load_run_rows,
    load_annotation_table,
    summarize_backend_rows,
    summarize_condition_units,
    summarize_flyvis_activity,
)
from brain.public_ids import MOTOR_READOUT_IDS
from visualization.activation_viz import load_brain_layout


DEFAULT_TARGET_CAPTURE = (
    "outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/"
    "flygym-demo-20260315-203010/activation_capture.npz"
)
DEFAULT_TARGET_LOG = (
    "outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/"
    "flygym-demo-20260315-203010/run.jsonl"
)
DEFAULT_NO_TARGET_CAPTURE = (
    "outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/"
    "flygym-demo-20260315-204719/activation_capture.npz"
)
DEFAULT_NO_TARGET_LOG = (
    "outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/"
    "flygym-demo-20260315-204719/run.jsonl"
)
DEFAULT_CONFIG = (
    "configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_"
    "calibrated_target_jump_brain_latent_turn_spontaneous_refit.yaml"
)
DEFAULT_OUTPUT_PREFIX = "outputs/metrics/living_brain_activation_pair"


def _load_config(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _sampled_overlay_root_ids(candidate_json_path: str | Path | None, fixed_groups: dict[str, list[int]]) -> set[int]:
    sampled = {int(root_id) for group in fixed_groups.values() for root_id in group}
    if not candidate_json_path:
        return sampled
    payload = json.loads(Path(candidate_json_path).read_text(encoding="utf-8"))
    for item in payload.get("selected_paired_cell_types", []):
        for key in ("left_root_ids", "right_root_ids"):
            sampled.update(int(root_id) for root_id in item.get(key, []))
    return sampled


def _plot_renderer_breakdown(path: Path, target_summary: dict[str, float | int], no_target_summary: dict[str, float | int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    labels = ["target", "no_target"]
    spike_means = [
        float(target_summary["spiking_neurons_per_frame_mean"]),
        float(no_target_summary["spiking_neurons_per_frame_mean"]),
    ]
    non_spike_means = [
        6000.0 - float(target_summary["spiking_neurons_per_frame_mean"]),
        6000.0 - float(no_target_summary["spiking_neurons_per_frame_mean"]),
    ]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(labels, spike_means, color="#17becf", label="true spikes shown")
    ax.bar(labels, non_spike_means, bottom=spike_means, color="#555555", label="non-spiking high-|voltage| points shown")
    ax.set_ylabel("mean displayed brain points per frame")
    ax.set_title("Rendered living-brain cloud: spikes vs non-spiking voltage occupancy")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_top_families(path: Path, family_table: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_df = family_table.head(12).copy()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(plot_df["family"], plot_df["total_spike_frames"], color="#4477aa")
    ax.invert_yaxis()
    ax.set_xlabel("total spike frames")
    ax.set_title("Top central unsampled spike-heavy families")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze living-brain target vs no-target activation captures.")
    parser.add_argument("--target-capture", default=DEFAULT_TARGET_CAPTURE)
    parser.add_argument("--target-log", default=DEFAULT_TARGET_LOG)
    parser.add_argument("--no-target-capture", default=DEFAULT_NO_TARGET_CAPTURE)
    parser.add_argument("--no-target-log", default=DEFAULT_NO_TARGET_LOG)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output-prefix", default=DEFAULT_OUTPUT_PREFIX)
    parser.add_argument("--max-brain-points", type=int, default=6000)
    parser.add_argument("--central-band-min", type=float, default=0.35)
    parser.add_argument("--central-band-max", type=float, default=0.65)
    args = parser.parse_args()

    output_prefix = (REPO_ROOT / Path(args.output_prefix)).resolve()
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    plots_dir = (REPO_ROOT / "outputs" / "plots").resolve()
    plots_dir.mkdir(parents=True, exist_ok=True)

    config = _load_config(args.config)
    target_capture = np.load(args.target_capture, allow_pickle=True)
    no_target_capture = np.load(args.no_target_capture, allow_pickle=True)
    target_rows = load_run_rows(args.target_log)
    no_target_rows = load_run_rows(args.no_target_log)

    fixed_groups = {
        "P9_L": MOTOR_READOUT_IDS["forward_left"],
        "P9_R": MOTOR_READOUT_IDS["forward_right"],
        "DNa_L": MOTOR_READOUT_IDS["turn_left"],
        "DNa_R": MOTOR_READOUT_IDS["turn_right"],
        "MDN": MOTOR_READOUT_IDS["reverse"],
    }
    brain_layout = load_brain_layout(
        annotation_path=config["visual_splice"]["annotation_path"],
        completeness_path=config["brain"]["completeness_path"],
        candidate_json=config.get("decoder", {}).get("monitor_candidates_json")
        or config.get("decoder", {}).get("population_candidates_json"),
        fixed_groups=fixed_groups,
    )
    annotation_df = load_annotation_table(config["visual_splice"]["annotation_path"])
    sampled_overlay_root_ids = _sampled_overlay_root_ids(
        config.get("decoder", {}).get("monitor_candidates_json")
        or config.get("decoder", {}).get("population_candidates_json"),
        fixed_groups,
    )

    target_analysis = summarize_condition_units(
        capture=target_capture,
        root_ids=brain_layout.root_ids,
        xy=brain_layout.xy,
        extent=brain_layout.background_extent,
        annotation_df=annotation_df,
        sampled_overlay_root_ids=sampled_overlay_root_ids,
        max_brain_points=int(args.max_brain_points),
        central_band_min=float(args.central_band_min),
        central_band_max=float(args.central_band_max),
    )
    no_target_analysis = summarize_condition_units(
        capture=no_target_capture,
        root_ids=brain_layout.root_ids,
        xy=brain_layout.xy,
        extent=brain_layout.background_extent,
        annotation_df=annotation_df,
        sampled_overlay_root_ids=sampled_overlay_root_ids,
        max_brain_points=int(args.max_brain_points),
        central_band_min=float(args.central_band_min),
        central_band_max=float(args.central_band_max),
    )

    target_backend = summarize_backend_rows(target_rows)
    no_target_backend = summarize_backend_rows(no_target_rows)
    target_flyvis = summarize_flyvis_activity(target_capture)
    no_target_flyvis = summarize_flyvis_activity(no_target_capture)
    monitor_table = build_monitor_rate_comparison(
        target_capture=target_capture,
        no_target_capture=no_target_capture,
    )

    target_families = target_analysis["family_table"].copy()
    target_families = target_families.add_prefix("target_")
    target_families = target_families.rename(columns={"target_family": "family"})
    no_target_families = no_target_analysis["family_table"].copy()
    no_target_families = no_target_families.add_prefix("no_target_")
    no_target_families = no_target_families.rename(columns={"no_target_family": "family"})
    family_comparison = target_families.merge(no_target_families, on="family", how="outer")
    family_comparison["target_minus_no_target_mean_spike_frames"] = (
        family_comparison["target_mean_spike_frames"].fillna(0.0)
        - family_comparison["no_target_mean_spike_frames"].fillna(0.0)
    )
    family_comparison["target_minus_no_target_mean_selected_frames"] = (
        family_comparison["target_mean_selected_frames"].fillna(0.0)
        - family_comparison["no_target_mean_selected_frames"].fillna(0.0)
    )
    family_comparison = family_comparison.sort_values(
        ["target_mean_spike_frames", "no_target_mean_spike_frames"],
        ascending=[False, False],
    ).reset_index(drop=True)

    central_target_path = output_prefix.parent / f"{output_prefix.name}_central_units_target.csv"
    central_no_target_path = output_prefix.parent / f"{output_prefix.name}_central_units_no_target.csv"
    central_family_target_path = output_prefix.parent / f"{output_prefix.name}_central_families_target.csv"
    central_family_no_target_path = output_prefix.parent / f"{output_prefix.name}_central_families_no_target.csv"
    family_comparison_path = output_prefix.parent / f"{output_prefix.name}_family_comparison.csv"
    monitor_path = output_prefix.parent / f"{output_prefix.name}_monitor_rate_comparison.csv"
    condition_path = output_prefix.parent / f"{output_prefix.name}_condition_summary.csv"

    target_analysis["central_units"].head(80).to_csv(central_target_path, index=False)
    no_target_analysis["central_units"].head(80).to_csv(central_no_target_path, index=False)
    target_analysis["central_family_table"].to_csv(central_family_target_path, index=False)
    no_target_analysis["central_family_table"].to_csv(central_family_no_target_path, index=False)
    family_comparison.to_csv(family_comparison_path, index=False)
    monitor_table.to_csv(monitor_path, index=False)

    condition_table = pd.DataFrame(
        [
            {
                "condition": "target",
                **target_analysis["rendered_summary"],
                **target_backend,
                **target_flyvis,
            },
            {
                "condition": "no_target",
                **no_target_analysis["rendered_summary"],
                **no_target_backend,
                **no_target_flyvis,
            },
        ]
    )
    condition_table.to_csv(condition_path, index=False)

    renderer_plot = plots_dir / "living_brain_activation_pair_renderer_breakdown.png"
    central_plot = plots_dir / "living_brain_activation_pair_top_central_families.png"
    _plot_renderer_breakdown(
        renderer_plot,
        target_analysis["rendered_summary"],
        no_target_analysis["rendered_summary"],
    )
    _plot_top_families(
        central_plot,
        pd.concat(
            [
                target_analysis["central_family_table"].head(6),
                no_target_analysis["central_family_table"].head(6),
            ],
            ignore_index=True,
        )
        .drop_duplicates(subset=["family"])
        .sort_values("total_spike_frames", ascending=False),
    )

    summary = {
        "target_condition": {
            **target_analysis["rendered_summary"],
            **target_backend,
            **target_flyvis,
        },
        "no_target_condition": {
            **no_target_analysis["rendered_summary"],
            **no_target_backend,
            **no_target_flyvis,
        },
        "renderer_interpretation": {
            "selection_rule": (
                "All spiking neurons are rendered first; remaining displayed points are filled"
                " by the highest absolute-voltage non-spiking neurons up to max_brain_points."
            ),
            "max_brain_points": int(args.max_brain_points),
            "target_mean_selected_non_spiking_points_per_frame": float(args.max_brain_points)
            - float(target_analysis["rendered_summary"]["spiking_neurons_per_frame_mean"]),
            "no_target_mean_selected_non_spiking_points_per_frame": float(args.max_brain_points)
            - float(no_target_analysis["rendered_summary"]["spiking_neurons_per_frame_mean"]),
        },
        "top_monitor_mean_rates": {
            "target": monitor_table.sort_values("target_mean_rate_hz", ascending=False).head(10).to_dict(orient="records"),
            "no_target": monitor_table.sort_values("no_target_mean_rate_hz", ascending=False).head(10).to_dict(orient="records"),
        },
        "top_unsampled_spike_families": {
            "target": target_analysis["top_unsampled_spike_families"].head(12).to_dict(orient="records"),
            "no_target": no_target_analysis["top_unsampled_spike_families"].head(12).to_dict(orient="records"),
        },
        "top_unsampled_visible_families": {
            "target": target_analysis["top_unsampled_visible_families"].head(12).to_dict(orient="records"),
            "no_target": no_target_analysis["top_unsampled_visible_families"].head(12).to_dict(orient="records"),
        },
        "top_central_units": {
            "target": target_analysis["central_units"].head(20).to_dict(orient="records"),
            "no_target": no_target_analysis["central_units"].head(20).to_dict(orient="records"),
        },
        "artifacts": {
            "condition_summary_csv": str(condition_path.relative_to(REPO_ROOT)),
            "monitor_rate_comparison_csv": str(monitor_path.relative_to(REPO_ROOT)),
            "family_comparison_csv": str(family_comparison_path.relative_to(REPO_ROOT)),
            "central_units_target_csv": str(central_target_path.relative_to(REPO_ROOT)),
            "central_units_no_target_csv": str(central_no_target_path.relative_to(REPO_ROOT)),
            "central_families_target_csv": str(central_family_target_path.relative_to(REPO_ROOT)),
            "central_families_no_target_csv": str(central_family_no_target_path.relative_to(REPO_ROOT)),
            "renderer_breakdown_plot": str(renderer_plot.relative_to(REPO_ROOT)),
            "top_central_families_plot": str(central_plot.relative_to(REPO_ROOT)),
        },
    }
    summary_path = output_prefix.parent / f"{output_prefix.name}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

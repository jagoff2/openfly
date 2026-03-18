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

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.best_branch_investigation import (
    align_framewise_matrix,
    build_unsampled_unit_table,
    compute_selected_frame_counts,
    load_annotation_table,
    pearson_correlation,
)
from brain.public_ids import MOTOR_READOUT_IDS
from visualization.activation_viz import load_brain_layout


DEFAULT_CONFIG = "configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml"
DEFAULT_CAPTURE = "outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/capture_data.npz"
DEFAULT_TARGET_METRICS = "outputs/requested_2s_splice_uvgrid_descending_calibrated_target/flygym-demo-20260311-071452/metrics.csv"
DEFAULT_NO_TARGET_METRICS = "outputs/requested_2s_splice_uvgrid_descending_calibrated_no_target/flygym-demo-20260311-073028/metrics.csv"
DEFAULT_ZERO_METRICS = "outputs/requested_2s_splice_uvgrid_descending_calibrated_zero_brain/flygym-demo-20260311-074301/metrics.csv"


def _load_config(path: str | Path) -> dict:
    import yaml

    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _sampled_overlay_root_ids(candidate_json_path: str | Path, fixed_groups: dict[str, list[int]]) -> set[int]:
    sampled = {int(root_id) for group in fixed_groups.values() for root_id in group}
    payload = json.loads(Path(candidate_json_path).read_text(encoding="utf-8"))
    for item in payload.get("selected_paired_cell_types", []):
        for key in ("left_root_ids", "right_root_ids"):
            sampled.update(int(root_id) for root_id in item.get(key, []))
    return sampled


def _metrics_row(path: str | Path, label: str) -> dict[str, float | str]:
    row = pd.read_csv(path).iloc[0].to_dict()
    row["label"] = label
    return row


def _plot_correlation_bars(
    path: Path,
    table: pd.DataFrame,
    *,
    label_col: str,
    value_col: str,
    title: str,
    top_n: int = 12,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_df = table.dropna(subset=[value_col]).sort_values(value_col, ascending=False).head(top_n).copy()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(plot_df[label_col], plot_df[value_col], color="#4477aa")
    ax.invert_yaxis()
    ax.set_xlabel(value_col)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Investigate the current best branch end-to-end from recorded artifacts.")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--capture", default=DEFAULT_CAPTURE)
    parser.add_argument("--target-metrics", default=DEFAULT_TARGET_METRICS)
    parser.add_argument("--no-target-metrics", default=DEFAULT_NO_TARGET_METRICS)
    parser.add_argument("--zero-metrics", default=DEFAULT_ZERO_METRICS)
    parser.add_argument("--output-prefix", default="outputs/metrics/best_branch_investigation")
    parser.add_argument("--max-brain-points", type=int, default=6000)
    parser.add_argument("--central-band-min", type=float, default=0.35)
    parser.add_argument("--central-band-max", type=float, default=0.65)
    args = parser.parse_args()

    config = _load_config(args.config)
    capture = np.load(args.capture, allow_pickle=True)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

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
        config.get("decoder", {}).get("monitor_candidates_json") or config.get("decoder", {}).get("population_candidates_json"),
        fixed_groups,
    )

    brain_voltage_frames = capture["brain_voltage_frames"].astype(np.float32)
    brain_spike_frames = capture["brain_spike_frames"].astype(np.uint8)
    frame_cycles = capture["frame_cycles"].astype(np.int64)
    frame_target_bearing = capture["frame_target_bearing_body"].astype(np.float32)
    monitor_labels = np.asarray(capture["monitor_labels"]).astype(str)
    monitor_matrix = align_framewise_matrix(capture["monitor_matrix"].astype(np.float32), frame_cycles)
    controller_labels = np.asarray(capture["controller_labels"]).astype(str)
    controller_matrix = align_framewise_matrix(capture["controller_matrix"].astype(np.float32), frame_cycles)
    controller_by_label = {
        label: controller_matrix[idx]
        for idx, label in enumerate(controller_labels)
    }

    selected_counts = compute_selected_frame_counts(
        brain_voltage_frames,
        brain_spike_frames,
        max_points=int(args.max_brain_points),
    )
    unit_table = build_unsampled_unit_table(
        root_ids=brain_layout.root_ids,
        xy=brain_layout.xy,
        extent=brain_layout.background_extent,
        selected_counts=selected_counts,
        spike_counts=brain_spike_frames.sum(axis=0),
        mean_voltage=brain_voltage_frames.mean(axis=0),
        max_voltage=brain_voltage_frames.max(axis=0),
        annotation_df=annotation_df,
        sampled_overlay_root_ids=sampled_overlay_root_ids,
    )
    unsampled = unit_table[~unit_table["sampled_overlay"]].copy()
    central = unsampled[
        unsampled["x_norm"].between(float(args.central_band_min), float(args.central_band_max))
        & unsampled["y_norm"].between(float(args.central_band_min), float(args.central_band_max))
    ].copy()

    top_unsampled_central = central.sort_values(
        ["selected_frames", "spike_frames", "max_voltage"],
        ascending=[False, False, False],
    ).head(40)
    top_spiking_central = central.sort_values(
        ["spike_frames", "selected_frames", "max_voltage"],
        ascending=[False, False, False],
    ).head(40)

    candidate_families = (
        pd.concat(
            [
                top_unsampled_central["family"],
                top_spiking_central["family"],
            ],
            axis=0,
        )
        .dropna()
        .astype(str)
    )
    candidate_families = [family for family in candidate_families.unique().tolist() if family and family != "UNKNOWN"]

    family_rows: list[dict[str, float | int | str]] = []
    family_lookup = annotation_df.set_index("root_id")["family"]
    for family in candidate_families:
        family_root_ids = family_lookup.index[family_lookup == family].to_numpy(dtype=np.int64)
        family_indices = np.flatnonzero(np.isin(brain_layout.root_ids, family_root_ids))
        if family_indices.size == 0:
            continue
        mean_voltage = brain_voltage_frames[:, family_indices].mean(axis=1)
        mean_spikes = brain_spike_frames[:, family_indices].mean(axis=1)
        family_rows.append(
            {
                "family": family,
                "n_roots": int(family_indices.size),
                "corr_target_bearing": pearson_correlation(mean_voltage, frame_target_bearing),
                "corr_forward_speed": pearson_correlation(mean_voltage, controller_by_label["forward_speed"]),
                "corr_left_drive": pearson_correlation(mean_voltage, controller_by_label["left_drive"]),
                "corr_right_drive": pearson_correlation(mean_voltage, controller_by_label["right_drive"]),
                "mean_spike_per_frame": float(mean_spikes.mean()),
                "mean_voltage": float(mean_voltage.mean()),
            }
        )
    family_table = pd.DataFrame(family_rows).sort_values("corr_target_bearing", ascending=False)

    monitor_rows = []
    for idx, label in enumerate(monitor_labels):
        monitor_trace = monitor_matrix[idx]
        monitor_rows.append(
            {
                "label": str(label),
                "corr_target_bearing": pearson_correlation(monitor_trace, frame_target_bearing),
                "corr_forward_speed": pearson_correlation(monitor_trace, controller_by_label["forward_speed"]),
                "corr_left_drive": pearson_correlation(monitor_trace, controller_by_label["left_drive"]),
                "corr_right_drive": pearson_correlation(monitor_trace, controller_by_label["right_drive"]),
                "mean_rate_hz": float(monitor_trace.mean()),
            }
        )
    monitor_table = pd.DataFrame(monitor_rows).sort_values("corr_target_bearing", ascending=False)

    behavior_table = pd.DataFrame(
        [
            _metrics_row(args.target_metrics, "target"),
            _metrics_row(args.no_target_metrics, "no_target"),
            _metrics_row(args.zero_metrics, "zero_brain"),
        ]
    )

    family_path = output_prefix.with_name(f"{output_prefix.name}_family_correlations.csv")
    monitor_path = output_prefix.with_name(f"{output_prefix.name}_monitor_correlations.csv")
    central_path = output_prefix.with_name(f"{output_prefix.name}_unsampled_central_units.csv")
    spiking_path = output_prefix.with_name(f"{output_prefix.name}_unsampled_central_spiking_units.csv")
    behavior_path = output_prefix.with_name(f"{output_prefix.name}_behavior_summary.csv")
    summary_path = output_prefix.with_name(f"{output_prefix.name}_summary.json")
    family_plot = Path("outputs/plots/best_branch_investigation_family_target_bearing_corr.png")
    monitor_plot = Path("outputs/plots/best_branch_investigation_monitor_target_bearing_corr.png")

    family_table.to_csv(family_path, index=False)
    monitor_table.to_csv(monitor_path, index=False)
    top_unsampled_central.to_csv(central_path, index=False)
    top_spiking_central.to_csv(spiking_path, index=False)
    behavior_table.to_csv(behavior_path, index=False)
    _plot_correlation_bars(
        family_plot,
        family_table,
        label_col="family",
        value_col="corr_target_bearing",
        title="Unsampled Family Mean Voltage vs Target Bearing",
    )
    _plot_correlation_bars(
        monitor_plot,
        monitor_table,
        label_col="label",
        value_col="corr_target_bearing",
        title="Monitored Decoder Rate vs Target Bearing",
    )

    summary = {
        "behavior": {
            row["label"]: {
                "avg_forward_speed": float(row["avg_forward_speed"]),
                "net_displacement": float(row["net_displacement"]),
                "displacement_efficiency": float(row["displacement_efficiency"]),
            }
            for row in behavior_table.to_dict(orient="records")
        },
        "dominant_unsampled_central_family": None if top_unsampled_central.empty else str(top_unsampled_central.iloc[0]["family"]),
        "dominant_unsampled_central_family_selected_frames": None if top_unsampled_central.empty else int(top_unsampled_central.iloc[0]["selected_frames"]),
        "dominant_unsampled_central_family_spike_frames": None if top_unsampled_central.empty else int(top_unsampled_central.iloc[0]["spike_frames"]),
        "best_unsampled_target_bearing_family": None if family_table.empty else str(family_table.iloc[0]["family"]),
        "best_unsampled_target_bearing_corr": None if family_table.empty else float(family_table.iloc[0]["corr_target_bearing"]),
        "best_monitor_target_bearing_label": None if monitor_table.empty else str(monitor_table.iloc[0]["label"]),
        "best_monitor_target_bearing_corr": None if monitor_table.empty else float(monitor_table.iloc[0]["corr_target_bearing"]),
        "interpretation": {
            "target_modulation_exists": bool(
                behavior_table.set_index("label").loc["target", "avg_forward_speed"]
                > behavior_table.set_index("label").loc["no_target", "avg_forward_speed"]
            ),
            "scene_drive_remains_strong": bool(
                behavior_table.set_index("label").loc["no_target", "net_displacement"] > 1.0
            ),
            "upstream_visual_families_outperform_monitors_for_target_bearing": bool(
                not family_table.empty
                and not monitor_table.empty
                and float(family_table.iloc[0]["corr_target_bearing"]) > float(monitor_table.iloc[0]["corr_target_bearing"])
            ),
        },
        "artifacts": {
            "family_correlations": str(family_path),
            "monitor_correlations": str(monitor_path),
            "unsampled_central_units": str(central_path),
            "unsampled_central_spiking_units": str(spiking_path),
            "behavior_summary": str(behavior_path),
            "family_plot": str(family_plot),
            "monitor_plot": str(monitor_plot),
        },
    }
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

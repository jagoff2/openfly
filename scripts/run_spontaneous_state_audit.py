from __future__ import annotations

import argparse
import json
import math
import sys
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from brain.public_ids import MOTOR_READOUT_IDS
from metrics.timing import BenchmarkRecord, write_benchmark_csv
from runtime.closed_loop import build_brain_backend, load_config


def _load_candidate_groups(path: Path, *, label_key: str) -> OrderedDict[str, list[int]]:
    if not path.exists():
        return OrderedDict()
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("selected_paired_cell_types", [])
    groups: OrderedDict[str, list[int]] = OrderedDict()
    for item in items:
        label = str(item.get(label_key, "")).strip()
        ids = [int(neuron_id) for neuron_id in item.get("left_root_ids", []) + item.get("right_root_ids", [])]
        if label and ids:
            groups[label] = sorted(set(ids))
    return groups


def _build_monitor_groups() -> OrderedDict[str, tuple[str, list[int]]]:
    groups: OrderedDict[str, tuple[str, list[int]]] = OrderedDict()
    for label, ids in MOTOR_READOUT_IDS.items():
        groups[f"motor::{label}"] = ("motor", list(ids))
    descending_path = ROOT / "outputs" / "metrics" / "descending_readout_candidates_strict.json"
    relay_path = ROOT / "outputs" / "metrics" / "splice_relay_candidates.json"
    for label, ids in _load_candidate_groups(descending_path, label_key="candidate_label").items():
        groups[f"descending::{label}"] = ("descending", ids)
    for label, ids in _load_candidate_groups(relay_path, label_key="cell_type").items():
        groups[f"relay::{label}"] = ("relay", ids)
    return groups


def _append_family_monitor_groups(
    groups: OrderedDict[str, tuple[str, list[int]]],
    *,
    family_groups,
    index_to_flyid: dict[int, int],
    max_pairs: int,
) -> OrderedDict[str, tuple[str, list[int]]]:
    if max_pairs <= 0:
        return groups
    selected_groups = sorted(
        family_groups,
        key=lambda group: min(len(group.left_indices), len(group.right_indices)),
        reverse=True,
    )[: max_pairs]
    for group in selected_groups:
        left_ids = [int(index_to_flyid[int(index)]) for index in group.left_indices if int(index) in index_to_flyid]
        right_ids = [int(index_to_flyid[int(index)]) for index in group.right_indices if int(index) in index_to_flyid]
        if left_ids and right_ids:
            groups[f"family_left::{group.family}"] = ("family", left_ids)
            groups[f"family_right::{group.family}"] = ("family", right_ids)
    return groups


def _append_random_sample_groups(
    groups: OrderedDict[str, tuple[str, list[int]]],
    *,
    available_ids: list[int],
    sample_count: int,
    seed: int,
) -> OrderedDict[str, tuple[str, list[int]]]:
    if sample_count <= 0 or not available_ids:
        return groups
    rng = np.random.default_rng(seed)
    sample_count = min(sample_count, len(available_ids))
    sampled_ids = rng.choice(np.asarray(available_ids, dtype=np.int64), size=sample_count, replace=False)
    for neuron_id in sampled_ids.tolist():
        groups[f"sample::{int(neuron_id)}"] = ("sample", [int(neuron_id)])
    return groups


def _group_mean(value_by_id: dict[int, float], ids: list[int]) -> float:
    values = [float(value_by_id[int(neuron_id)]) for neuron_id in ids if int(neuron_id) in value_by_id]
    return float(np.mean(values)) if values else 0.0


def _mean_abs_pairwise_corr(matrix: np.ndarray) -> float:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] < 2 or matrix.shape[1] < 3:
        return float("nan")
    keep = np.std(matrix, axis=1) > 1e-6
    matrix = matrix[keep]
    if matrix.shape[0] < 2:
        return float("nan")
    corr = np.corrcoef(matrix)
    if corr.ndim != 2 or corr.shape[0] < 2:
        return float("nan")
    upper = corr[np.triu_indices(corr.shape[0], k=1)]
    upper = upper[np.isfinite(upper)]
    return float(np.mean(np.abs(upper))) if upper.size else float("nan")


def _mean_lag1_autocorr(matrix: np.ndarray) -> float:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[1] < 3:
        return float("nan")
    values = []
    for row in matrix:
        if float(np.std(row)) <= 1e-6:
            continue
        corr = np.corrcoef(row[:-1], row[1:])[0, 1]
        if math.isfinite(corr):
            values.append(float(corr))
    return float(np.mean(values)) if values else float("nan")


def _shuffled_corr(matrix: np.ndarray, seed: int) -> float:
    rng = np.random.default_rng(seed)
    matrix = np.asarray(matrix, dtype=np.float32).copy()
    for row in matrix:
        rng.shuffle(row)
    return _mean_abs_pairwise_corr(matrix)


def _sensor_schedule(name: str, pulse_left_hz: float, pulse_right_hz: float):
    zero = {"vision_left": 0.0, "vision_right": 0.0, "mech_left": 0.0, "mech_right": 0.0}
    if name in {"dead_cold_start", "candidate_ongoing"}:
        return lambda _window_index: dict(zero)

    def pulse_release(window_index: int, baseline_windows: int, pulse_windows: int) -> dict[str, float]:
        if window_index < baseline_windows:
            return dict(zero)
        if window_index < baseline_windows + pulse_windows:
            return {
                "vision_left": float(pulse_left_hz),
                "vision_right": float(pulse_right_hz),
                "mech_left": 0.0,
                "mech_right": 0.0,
            }
        return dict(zero)

    return pulse_release


def _run_condition(
    *,
    backend,
    name: str,
    monitor_groups: OrderedDict[str, tuple[str, list[int]]],
    total_windows: int,
    steps_per_window: int,
    sensor_fn,
    baseline_windows: int,
    pulse_windows: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, float], dict[str, float]]:
    summary_rows: list[dict[str, object]] = []
    monitor_rows: list[dict[str, object]] = []
    wall_start = perf_counter()
    for window_index in range(total_windows):
        sensors = sensor_fn(window_index)
        firing_rates, mean_voltage, mean_conductance = backend.step_with_state(sensors, num_steps=steps_per_window)
        state = backend.state_summary()
        phase_segment = "baseline"
        if name == "candidate_pulse_release":
            if baseline_windows <= window_index < baseline_windows + pulse_windows:
                phase_segment = "pulse"
            elif window_index >= baseline_windows + pulse_windows:
                phase_segment = "release"
        row = {
            "condition": name,
            "window_index": window_index,
            "phase_segment": phase_segment,
            "vision_left_hz": float(sensors.get("vision_left", 0.0)),
            "vision_right_hz": float(sensors.get("vision_right", 0.0)),
            "mech_left_hz": float(sensors.get("mech_left", 0.0)),
            "mech_right_hz": float(sensors.get("mech_right", 0.0)),
            **state,
        }
        summary_rows.append(row)
        for label, (category, ids) in monitor_groups.items():
            monitor_rows.append(
                {
                    "condition": name,
                    "window_index": window_index,
                    "phase_segment": phase_segment,
                    "monitor_label": label,
                    "monitor_category": category,
                    "mean_firing_hz": _group_mean(firing_rates, ids),
                    "mean_voltage_mv": _group_mean(mean_voltage, ids),
                    "mean_conductance": _group_mean(mean_conductance, ids),
                }
            )
    wall_seconds = perf_counter() - wall_start
    sim_seconds = total_windows * steps_per_window * (backend.dt_ms / 1000.0)
    metrics = {
        "wall_seconds": float(wall_seconds),
        "sim_seconds": float(sim_seconds),
        "real_time_factor": float(sim_seconds / wall_seconds) if wall_seconds else float("inf"),
    }
    final_state = dict(summary_rows[-1]) if summary_rows else {}
    return summary_rows, monitor_rows, metrics, final_state


def _build_summary(summary_df: pd.DataFrame, monitor_df: pd.DataFrame, *, seed: int) -> dict[str, object]:
    candidate_monitor = monitor_df[monitor_df["condition"] == "candidate_ongoing"]
    structured_monitor = candidate_monitor[candidate_monitor["monitor_category"].isin(["relay", "descending", "sample"])]
    structured_labels = sorted(structured_monitor["monitor_label"].unique())
    matrix = np.vstack(
        [
            structured_monitor[structured_monitor["monitor_label"] == label]["mean_firing_hz"].to_numpy(dtype=np.float32)
            for label in structured_labels
        ]
    ) if structured_labels else np.zeros((0, 0), dtype=np.float32)
    pulse_monitor = monitor_df[monitor_df["condition"] == "candidate_pulse_release"]
    family_monitor = monitor_df[
        (monitor_df["condition"] == "candidate_ongoing") & (monitor_df["monitor_category"] == "family")
    ].copy()

    family_corrs = []
    family_voltage_corrs = []
    family_names = sorted(
        {
            label.split("::", 1)[1]
            for label in family_monitor["monitor_label"].unique().tolist()
            if "::" in label
        }
    )
    for family_name in family_names:
        left = family_monitor[family_monitor["monitor_label"] == f"family_left::{family_name}"]["mean_firing_hz"].to_numpy(dtype=np.float32)
        right = family_monitor[family_monitor["monitor_label"] == f"family_right::{family_name}"]["mean_firing_hz"].to_numpy(dtype=np.float32)
        if left.size == right.size and left.size >= 3 and float(np.std(left)) > 1e-6 and float(np.std(right)) > 1e-6:
            corr = np.corrcoef(left, right)[0, 1]
            if math.isfinite(corr):
                family_corrs.append(float(corr))
        left_v = family_monitor[family_monitor["monitor_label"] == f"family_left::{family_name}"]["mean_voltage_mv"].to_numpy(dtype=np.float32)
        right_v = family_monitor[family_monitor["monitor_label"] == f"family_right::{family_name}"]["mean_voltage_mv"].to_numpy(dtype=np.float32)
        if left_v.size == right_v.size and left_v.size >= 3 and float(np.std(left_v)) > 1e-6 and float(np.std(right_v)) > 1e-6:
            corr_v = np.corrcoef(left_v, right_v)[0, 1]
            if math.isfinite(corr_v):
                family_voltage_corrs.append(float(corr_v))

    def _condition_stats(condition: str) -> dict[str, float]:
        rows = summary_df[summary_df["condition"] == condition]
        return {
            "mean_spike_fraction": float(rows["global_spike_fraction"].mean()),
            "max_spike_fraction": float(rows["global_spike_fraction"].max()),
            "mean_voltage_mv": float(rows["global_mean_voltage"].mean()),
            "mean_conductance": float(rows["global_mean_conductance"].mean()),
            "mean_background_rate_hz": float(rows["background_mean_rate_hz"].mean()),
            "background_active_fraction": float(rows["background_active_fraction"].mean()),
            "nonzero_window_fraction": float((rows["global_spike_fraction"] > 0.0).mean()),
        }

    turn_left = pulse_monitor[pulse_monitor["monitor_label"] == "motor::turn_left"]["mean_firing_hz"].to_numpy(dtype=np.float32)
    turn_right = pulse_monitor[pulse_monitor["monitor_label"] == "motor::turn_right"]["mean_firing_hz"].to_numpy(dtype=np.float32)
    turn_asymmetry = turn_right - turn_left if turn_left.size and turn_right.size else np.zeros(0, dtype=np.float32)
    pulse_segments = pulse_monitor[pulse_monitor["phase_segment"] == "pulse"]["window_index"].unique()
    release_segments = pulse_monitor[pulse_monitor["phase_segment"] == "release"]["window_index"].unique()
    pulse_mask = np.isin(pulse_monitor[pulse_monitor["monitor_label"] == "motor::turn_left"]["window_index"].to_numpy(), pulse_segments)
    release_mask = np.isin(pulse_monitor[pulse_monitor["monitor_label"] == "motor::turn_left"]["window_index"].to_numpy(), release_segments)

    structure_real = _mean_abs_pairwise_corr(matrix)
    structure_shuffled = _shuffled_corr(matrix, seed=seed)
    return {
        "dead_cold_start": _condition_stats("dead_cold_start"),
        "candidate_ongoing": _condition_stats("candidate_ongoing"),
        "candidate_pulse_release": _condition_stats("candidate_pulse_release"),
        "structure": {
            "mean_abs_pairwise_corr": structure_real,
            "mean_abs_pairwise_corr_shuffled": structure_shuffled,
            "corr_structure_ratio": float(structure_real / structure_shuffled)
            if math.isfinite(structure_real) and math.isfinite(structure_shuffled) and abs(structure_shuffled) > 1e-9
            else float("nan"),
            "mean_lag1_autocorr": _mean_lag1_autocorr(matrix),
            "structured_monitor_count": int(len(structured_labels)),
            "family_pair_count": int(len(family_names)),
            "mean_homologous_family_rate_corr": float(np.mean(family_corrs)) if family_corrs else float("nan"),
            "median_homologous_family_rate_corr": float(np.median(family_corrs)) if family_corrs else float("nan"),
            "mean_homologous_family_voltage_corr": float(np.mean(family_voltage_corrs)) if family_voltage_corrs else float("nan"),
        },
        "perturbation": {
            "peak_abs_turn_asymmetry_hz_during_pulse": float(np.max(np.abs(turn_asymmetry[pulse_mask]))) if turn_asymmetry.size and pulse_mask.any() else 0.0,
            "mean_abs_turn_asymmetry_hz_after_release": float(np.mean(np.abs(turn_asymmetry[release_mask]))) if turn_asymmetry.size and release_mask.any() else 0.0,
        },
    }


def _family_group_catalog_rows(backend) -> list[dict[str, object]]:
    if not hasattr(backend, "spontaneous_family_group_catalog"):
        return []
    return list(backend.spontaneous_family_group_catalog())


def _plot_outputs(summary_df: pd.DataFrame, monitor_df: pd.DataFrame, plots_dir: Path) -> None:
    plots_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for condition, subset in summary_df.groupby("condition"):
        axes[0].plot(subset["window_index"], subset["global_spike_fraction"], label=condition)
        axes[1].plot(subset["window_index"], subset["global_mean_voltage"], label=condition)
        axes[2].plot(subset["window_index"], subset["global_mean_conductance"], label=condition)
    axes[0].set_ylabel("spike_fraction")
    axes[1].set_ylabel("mean_voltage")
    axes[2].set_ylabel("mean_conductance")
    axes[2].set_xlabel("window_index")
    axes[0].legend(loc="best")
    fig.tight_layout()
    fig.savefig(plots_dir / "spontaneous_state_global_traces.png")
    plt.close(fig)

    subset = monitor_df[monitor_df["monitor_category"].isin(["motor", "descending", "relay"])]
    label_order = list(dict.fromkeys(subset["monitor_label"].tolist()))
    heatmap = (
        subset.pivot_table(index="monitor_label", columns=["condition", "window_index"], values="mean_firing_hz", fill_value=0.0)
        .reindex(label_order)
        .to_numpy(dtype=np.float32)
    )
    fig, ax = plt.subplots(figsize=(12, max(4, 0.25 * max(1, len(label_order)))))
    im = ax.imshow(heatmap, aspect="auto", cmap="magma")
    ax.set_yticks(range(len(label_order)))
    ax.set_yticklabels(label_order, fontsize=7)
    ax.set_xlabel("condition/window")
    ax.set_title("Spontaneous-state monitor firing rates")
    fig.colorbar(im, ax=ax, label="Hz")
    fig.tight_layout()
    fig.savefig(plots_dir / "spontaneous_state_monitor_heatmap.png")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit spontaneous-state candidate activity in the whole-brain backend")
    parser.add_argument("--config", default="configs/brain_spontaneous_probe.yaml")
    parser.add_argument("--output-prefix", default="spontaneous_state")
    parser.add_argument("--window-ms", type=float, default=5.0)
    parser.add_argument("--baseline-windows", type=int, default=20)
    parser.add_argument("--pulse-windows", type=int, default=8)
    parser.add_argument("--release-windows", type=int, default=20)
    parser.add_argument("--pulse-left-hz", type=float, default=140.0)
    parser.add_argument("--pulse-right-hz", type=float, default=20.0)
    parser.add_argument("--sample-count", type=int, default=128)
    parser.add_argument("--family-monitor-pairs", type=int, default=24)
    parser.add_argument("--active-fraction", type=float, default=None)
    parser.add_argument("--lognormal-mean-hz", type=float, default=None)
    parser.add_argument("--lognormal-sigma", type=float, default=None)
    parser.add_argument("--max-rate-hz", type=float, default=None)
    parser.add_argument("--voltage-jitter-std-mv", type=float, default=None)
    parser.add_argument("--latent-count", type=int, default=None)
    parser.add_argument("--latent-target-fraction", type=float, default=None)
    parser.add_argument("--latent-loading-std-hz", type=float, default=None)
    parser.add_argument("--latent-ou-tau-s", type=float, default=None)
    parser.add_argument("--latent-ou-sigma-hz", type=float, default=None)
    parser.add_argument("--family-key", default=None)
    parser.add_argument("--min-family-size-per-side", type=int, default=None)
    parser.add_argument("--max-family-size-per-side", type=int, default=None)
    parser.add_argument("--included-super-classes", nargs="*", default=None)
    parser.add_argument("--bilateral-coupling", type=float, default=None)
    parser.add_argument("--family-rate-jitter-fraction", type=float, default=None)
    parser.add_argument("--neuron-rate-jitter-fraction", type=float, default=None)
    parser.add_argument("--antisymmetric-latent-fraction", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--strict-structured", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    seed = int(config.get("runtime", {}).get("seed", 0) if args.seed is None else args.seed)
    spontaneous_cfg = config.setdefault("brain", {}).setdefault("spontaneous_state", {})
    override_fields = {
        "active_fraction": args.active_fraction,
        "lognormal_mean_hz": args.lognormal_mean_hz,
        "lognormal_sigma": args.lognormal_sigma,
        "max_rate_hz": args.max_rate_hz,
        "voltage_jitter_std_mv": args.voltage_jitter_std_mv,
        "latent_count": args.latent_count,
        "latent_target_fraction": args.latent_target_fraction,
        "latent_loading_std_hz": args.latent_loading_std_hz,
        "latent_ou_tau_s": args.latent_ou_tau_s,
        "latent_ou_sigma_hz": args.latent_ou_sigma_hz,
        "family_key": args.family_key,
        "min_family_size_per_side": args.min_family_size_per_side,
        "max_family_size_per_side": args.max_family_size_per_side,
        "included_super_classes": args.included_super_classes,
        "bilateral_coupling": args.bilateral_coupling,
        "family_rate_jitter_fraction": args.family_rate_jitter_fraction,
        "neuron_rate_jitter_fraction": args.neuron_rate_jitter_fraction,
        "antisymmetric_latent_fraction": args.antisymmetric_latent_fraction,
    }
    for key, value in override_fields.items():
        if value is not None:
            spontaneous_cfg[key] = value
    steps_per_window = max(1, int(round(args.window_ms / float(config["brain"].get("dt_ms", 0.1)))))
    total_windows = int(args.baseline_windows + args.pulse_windows + args.release_windows)
    monitor_groups = _build_monitor_groups()
    records: list[BenchmarkRecord] = []
    summary_rows: list[dict[str, object]] = []
    monitor_rows: list[dict[str, object]] = []

    candidate_config = deepcopy(config)
    dead_config = deepcopy(config)
    dead_config.setdefault("brain", {})["spontaneous_state"] = {"mode": "none"}
    probe_backend = build_brain_backend("flygym", candidate_config)
    family_group_catalog = _family_group_catalog_rows(probe_backend)
    if args.strict_structured and spontaneous_cfg.get("included_super_classes") and not family_group_catalog:
        raise RuntimeError(
            "Structured spontaneous-state validation requested with included_super_classes, "
            "but no spontaneous family groups were resolved."
        )
    monitor_groups = _append_family_monitor_groups(
        monitor_groups,
        family_groups=getattr(probe_backend, "spontaneous_family_groups", []),
        index_to_flyid=getattr(probe_backend, "index_to_flyid", {}),
        max_pairs=int(args.family_monitor_pairs),
    )
    monitor_groups = _append_random_sample_groups(
        monitor_groups,
        available_ids=sorted(int(neuron_id) for neuron_id in probe_backend.index_to_flyid.values()),
        sample_count=int(args.sample_count),
        seed=seed,
    )
    monitored_ids = sorted({neuron_id for _, ids in monitor_groups.values() for neuron_id in ids})
    conditions = [
        ("dead_cold_start", dead_config, args.baseline_windows, _sensor_schedule("dead_cold_start", args.pulse_left_hz, args.pulse_right_hz)),
        ("candidate_ongoing", candidate_config, args.baseline_windows + args.release_windows, _sensor_schedule("candidate_ongoing", args.pulse_left_hz, args.pulse_right_hz)),
        (
            "candidate_pulse_release",
            candidate_config,
            total_windows,
            lambda window_index: _sensor_schedule("candidate_pulse_release", args.pulse_left_hz, args.pulse_right_hz)(
                window_index, args.baseline_windows, args.pulse_windows
            ),
        ),
    ]

    for condition_name, condition_config, condition_windows, sensor_fn in conditions:
        backend = build_brain_backend("flygym", condition_config)
        backend.set_monitored_ids(monitored_ids)
        backend.reset(seed=seed)
        condition_summary, condition_monitor, metrics, _ = _run_condition(
            backend=backend,
            name=condition_name,
            monitor_groups=monitor_groups,
            total_windows=condition_windows,
            steps_per_window=steps_per_window,
            sensor_fn=sensor_fn,
            baseline_windows=args.baseline_windows,
            pulse_windows=args.pulse_windows,
        )
        summary_rows.extend(condition_summary)
        monitor_rows.extend(condition_monitor)
        records.append(
            BenchmarkRecord(
                benchmark_name=condition_name,
                backend=str(condition_config["brain"].get("backend", "torch")),
                device=str(getattr(backend, "device_name", "unknown")),
                wall_seconds=float(metrics["wall_seconds"]),
                sim_seconds=float(metrics["sim_seconds"]),
                real_time_factor=float(metrics["real_time_factor"]),
                config=args.config,
                commit_hash="not_a_git_repo",
                status="success",
            )
        )

    summary_df = pd.DataFrame(summary_rows)
    monitor_df = pd.DataFrame(monitor_rows)
    summary = _build_summary(summary_df, monitor_df, seed=seed)
    summary["spontaneous_family_group_catalog"] = family_group_catalog
    summary["spontaneous_config"] = {
        "family_key": spontaneous_cfg.get("family_key", "auto"),
        "included_super_classes": list(spontaneous_cfg.get("included_super_classes", [])),
        "strict_structured": bool(args.strict_structured),
        "resolved_family_group_count": int(len(family_group_catalog)),
    }

    metrics_dir = ROOT / "outputs" / "metrics"
    plots_dir = ROOT / "outputs" / "plots"
    bench_dir = ROOT / "outputs" / "benchmarks"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    bench_dir.mkdir(parents=True, exist_ok=True)
    summary_path = metrics_dir / f"{args.output_prefix}_summary.json"
    summary_df.to_csv(metrics_dir / f"{args.output_prefix}_timeseries.csv", index=False)
    monitor_df.to_csv(metrics_dir / f"{args.output_prefix}_monitor_timeseries.csv", index=False)
    if family_group_catalog:
        pd.DataFrame(family_group_catalog).to_csv(
            metrics_dir / f"{args.output_prefix}_family_group_catalog.csv",
            index=False,
        )
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    write_benchmark_csv(bench_dir / f"{args.output_prefix}_benchmarks.csv", records)
    _plot_outputs(summary_df, monitor_df, plots_dir)
    print(summary_path)


if __name__ == "__main__":
    main()

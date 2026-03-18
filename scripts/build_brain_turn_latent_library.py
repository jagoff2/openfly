from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import numpy as np
import pandas as pd

from analysis.best_branch_investigation import align_framewise_matrix
from analysis.brain_latent_library import (
    apply_state_binned_ranking_adjustments,
    build_matched_turn_latent_ranking,
    build_state_binned_turn_metrics,
    monitor_voltage_turn_table,
)
from analysis.turn_voltage_library import apply_baseline_asymmetry_from_voltage_matrix, build_turn_voltage_signal_library
from bridge.decoder import _load_population_groups


def _load_metadata(path: Path) -> dict[str, dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metadata: dict[str, dict[str, object]] = {}
    for item in payload.get("selected_paired_cell_types", []):
        label = str(item.get("candidate_label") or item.get("cell_type") or "").strip()
        if not label:
            continue
        left_super = [str(value) for value in item.get("left_super_classes", []) if str(value)]
        right_super = [str(value) for value in item.get("right_super_classes", []) if str(value)]
        super_classes = sorted({*left_super, *right_super})
        metadata[label] = {
            "left_root_ids": [int(root_id) for root_id in item.get("left_root_ids", [])],
            "right_root_ids": [int(root_id) for root_id in item.get("right_root_ids", [])],
            "super_class": super_classes[0] if super_classes else "unknown",
        }
    return metadata


def _nested_float(record: dict[str, object], key_path: str) -> float:
    value: object = record
    for key in str(key_path).split("."):
        if not isinstance(value, dict):
            return 0.0
        value = value.get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _load_aligned_state_values(log_path: Path, frame_cycles: np.ndarray, key_path: str) -> np.ndarray:
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not records:
        raise ValueError(f"run log is empty: {log_path}")
    max_cycle = max(int(record.get("cycle", idx)) for idx, record in enumerate(records))
    values = np.zeros(max_cycle + 1, dtype=np.float32)
    for idx, record in enumerate(records):
        cycle = int(record.get("cycle", idx))
        values[cycle] = _nested_float(record, key_path)
    return align_framewise_matrix(values.reshape(1, -1), np.asarray(frame_cycles, dtype=np.int64))[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a matched-condition brain-side turn latent library from target and no-target captures.")
    parser.add_argument("--target-capture", required=True)
    parser.add_argument("--no-target-capture", required=True)
    parser.add_argument("--monitor-candidates-json", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--min-target-corr", type=float, default=0.15)
    parser.add_argument("--target-log")
    parser.add_argument("--no-target-log")
    parser.add_argument("--state-key", default="brain_backend_state.background_latent_mean_abs_hz")
    parser.add_argument("--state-min-bin-frames", type=int, default=12)
    parser.add_argument("--state-min-bin-abs-corr", type=float, default=0.1)
    parser.add_argument("--state-stability-weight", type=float, default=0.25)
    parser.add_argument("--state-bias-weight", type=float, default=0.35)
    parser.add_argument("--state-asymmetry-weight", type=float, default=0.15)
    parser.add_argument("--state-flip-penalty-weight", type=float, default=0.5)
    parser.add_argument("--require-state-consistent-sign", action="store_true")
    parser.add_argument(
        "--allowed-super-classes",
        nargs="*",
        default=["visual_projection", "visual_centrifugal", "central", "ascending"],
    )
    parser.add_argument("--turn-scale-mv", type=float, default=5.0)
    args = parser.parse_args()

    target_capture = np.load(Path(args.target_capture), allow_pickle=True)
    no_target_capture = np.load(Path(args.no_target_capture), allow_pickle=True)
    monitor_groups = _load_population_groups(str(args.monitor_candidates_json))
    metadata = _load_metadata(Path(args.monitor_candidates_json))

    target_turn = monitor_voltage_turn_table(capture=target_capture, monitor_groups=monitor_groups)
    no_target_turn = monitor_voltage_turn_table(capture=no_target_capture, monitor_groups=monitor_groups)
    ranked = build_matched_turn_latent_ranking(
        target_turn_table=target_turn,
        no_target_turn_table=no_target_turn,
        min_target_corr=float(args.min_target_corr),
    )
    target_state_metrics = pd.DataFrame()
    no_target_state_metrics = pd.DataFrame()
    if args.target_log and args.no_target_log:
        target_frame_state_values = _load_aligned_state_values(
            Path(args.target_log),
            np.asarray(target_capture["frame_cycles"], dtype=np.int64),
            str(args.state_key),
        )
        no_target_frame_state_values = _load_aligned_state_values(
            Path(args.no_target_log),
            np.asarray(no_target_capture["frame_cycles"], dtype=np.int64),
            str(args.state_key),
        )
        target_state_metrics = build_state_binned_turn_metrics(
            capture=target_capture,
            monitor_groups=monitor_groups,
            frame_state_values=target_frame_state_values,
            min_bin_frames=int(args.state_min_bin_frames),
        )
        no_target_state_metrics = build_state_binned_turn_metrics(
            capture=no_target_capture,
            monitor_groups=monitor_groups,
            frame_state_values=no_target_frame_state_values,
            min_bin_frames=int(args.state_min_bin_frames),
        )
        ranked = apply_state_binned_ranking_adjustments(
            ranked,
            target_state_metrics=target_state_metrics,
            no_target_state_metrics=no_target_state_metrics,
            min_bin_abs_corr=float(args.state_min_bin_abs_corr),
            state_stability_weight=float(args.state_stability_weight),
            state_bias_weight=float(args.state_bias_weight),
            state_asymmetry_weight=float(args.state_asymmetry_weight),
            state_flip_penalty_weight=float(args.state_flip_penalty_weight),
            require_consistent_sign=bool(args.require_state_consistent_sign),
        )
    library = build_turn_voltage_signal_library(
        ranked,
        metadata,
        top_k=int(args.top_k),
        target_turn=target_turn.set_index("label") if not target_turn.empty else None,
        allowed_super_classes=list(args.allowed_super_classes),
        turn_scale_mv=float(args.turn_scale_mv),
    )
    corrected_library = apply_baseline_asymmetry_from_voltage_matrix(
        library,
        np.asarray(no_target_capture["monitored_root_ids"], dtype=np.int64),
        align_framewise_matrix(
            np.asarray(no_target_capture["monitored_voltage_matrix"], dtype=np.float32),
            np.asarray(no_target_capture["frame_cycles"], dtype=np.int64),
        ),
    )

    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    target_turn_path = output_prefix.parent / f"{output_prefix.name}_target_turn.csv"
    no_target_turn_path = output_prefix.parent / f"{output_prefix.name}_no_target_turn.csv"
    ranked_path = output_prefix.parent / f"{output_prefix.name}_ranked.csv"
    target_state_path = output_prefix.parent / f"{output_prefix.name}_target_state_bins.csv"
    no_target_state_path = output_prefix.parent / f"{output_prefix.name}_no_target_state_bins.csv"
    summary_path = output_prefix.with_suffix(".json")
    library_path = output_prefix.parent / f"{output_prefix.name}_library.json"
    target_turn.to_csv(target_turn_path, index=False)
    no_target_turn.to_csv(no_target_turn_path, index=False)
    ranked.to_csv(ranked_path, index=False)
    if not target_state_metrics.empty:
        target_state_metrics.to_csv(target_state_path, index=False)
    if not no_target_state_metrics.empty:
        no_target_state_metrics.to_csv(no_target_state_path, index=False)
    library_path.write_text(json.dumps(corrected_library, indent=2), encoding="utf-8")
    summary = {
        "target_capture": str(args.target_capture),
        "no_target_capture": str(args.no_target_capture),
        "target_log": None if args.target_log is None else str(args.target_log),
        "no_target_log": None if args.no_target_log is None else str(args.no_target_log),
        "state_key": str(args.state_key),
        "monitor_candidates_json": str(args.monitor_candidates_json),
        "top_k": int(args.top_k),
        "min_target_corr": float(args.min_target_corr),
        "selected_labels": [str(item.get("label", "")) for item in corrected_library.get("selected_groups", [])],
        "selected_group_count": int(len(corrected_library.get("selected_groups", []))),
        "artifacts": {
            "target_turn_csv": str(target_turn_path),
            "no_target_turn_csv": str(no_target_turn_path),
            "ranked_csv": str(ranked_path),
            "library_json": str(library_path),
            "target_state_bins_csv": None if target_state_metrics.empty else str(target_state_path),
            "no_target_state_bins_csv": None if no_target_state_metrics.empty else str(no_target_state_path),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

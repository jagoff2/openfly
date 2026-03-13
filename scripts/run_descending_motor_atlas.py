from __future__ import annotations

import argparse
import copy
import csv
import json
from pathlib import Path
import sys
from time import perf_counter

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bridge.decoder import DecoderConfig, MotorDecoder
from metrics.parity import compute_parity_metrics
from runtime.closed_loop import build_body_runtime, build_brain_backend, load_config


def _load_candidate_map(path: str | Path) -> dict[str, dict[str, list[int]]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out: dict[str, dict[str, list[int]]] = {}
    for item in data.get("selected_paired_cell_types", []):
        label = str(item.get("candidate_label") or item.get("cell_type") or "").strip()
        if not label:
            continue
        out[label] = {
            "left": [int(v) for v in item.get("left_root_ids", [])],
            "right": [int(v) for v in item.get("right_root_ids", [])],
        }
    return out


def _stim_ids(candidate_map: dict[str, dict[str, list[int]]], label: str, side_mode: str) -> list[int]:
    if side_mode == "baseline":
        return []
    pair = candidate_map[label]
    if side_mode == "left":
        return pair["left"]
    if side_mode == "right":
        return pair["right"]
    if side_mode == "bilateral":
        return pair["left"] + pair["right"]
    raise ValueError(f"Unsupported side mode: {side_mode}")


def _default_side_modes(label: str, bilateral_labels: set[str]) -> list[str]:
    if label in bilateral_labels:
        return ["bilateral"]
    return ["left", "right"]


def _run_condition(
    *,
    config: dict,
    mode: str,
    label: str,
    side_mode: str,
    stim_current: float,
    duration_s: float,
    candidate_map: dict[str, dict[str, list[int]]],
) -> dict:
    run_cfg = copy.deepcopy(config)
    run_cfg.setdefault("body", {})["target_fly_enabled"] = False
    run_cfg.setdefault("runtime", {})["duration_s"] = duration_s
    body_runtime = build_body_runtime(mode, run_cfg, ROOT / "outputs" / "atlas_tmp")
    brain_backend = build_brain_backend(mode, run_cfg)
    decoder = MotorDecoder(DecoderConfig.from_mapping(run_cfg.get("decoder")))

    if hasattr(brain_backend, "set_monitored_ids"):
        brain_backend.set_monitored_ids(decoder.required_neuron_ids())
    if hasattr(brain_backend, "reset"):
        brain_backend.reset(seed=int(run_cfg["runtime"].get("seed", 0)))
    if hasattr(decoder, "reset"):
        decoder.reset()

    observation = body_runtime.reset(seed=int(run_cfg["runtime"].get("seed", 0)))
    control_interval_s = float(run_cfg["runtime"]["control_interval_s"])
    num_cycles = int(duration_s / control_interval_s)
    num_substeps = max(1, int(round(control_interval_s / body_runtime.timestep)))
    num_brain_steps = max(1, int(round(control_interval_s / (float(run_cfg["brain"].get("dt_ms", 0.1)) / 1000.0))))
    direct_current_by_id = {neuron_id: float(stim_current) for neuron_id in _stim_ids(candidate_map, label, side_mode)}
    trajectory = []
    left_drive_hist = []
    right_drive_hist = []
    start = perf_counter()
    for _ in range(num_cycles):
        rates = brain_backend.step(
            {},
            num_steps=num_brain_steps,
            direct_input_rates_hz={},
            direct_current_by_id=direct_current_by_id,
        )
        readout = decoder.decode(rates)
        observation = body_runtime.step(readout.command, num_substeps=num_substeps)
        trajectory.append(np.array(observation.position_xy))
        left_drive_hist.append(float(readout.command.left_drive))
        right_drive_hist.append(float(readout.command.right_drive))
    wall_seconds = perf_counter() - start
    body_runtime.close()
    trajectory_arr = np.asarray(trajectory) if trajectory else np.zeros((0, 2))
    metrics = compute_parity_metrics(trajectory_arr, control_interval_s)
    metrics.update(
        {
            "label": label,
            "side_mode": side_mode,
            "stim_current": float(stim_current),
            "duration_s": duration_s,
            "wall_seconds": wall_seconds,
            "real_time_factor": duration_s / wall_seconds if wall_seconds else float("inf"),
            "mean_left_drive": float(np.mean(left_drive_hist)) if left_drive_hist else 0.0,
            "mean_right_drive": float(np.mean(right_drive_hist)) if right_drive_hist else 0.0,
            "mean_total_drive": float(np.mean(np.asarray(left_drive_hist) + np.asarray(right_drive_hist))) if left_drive_hist else 0.0,
            "mean_abs_drive_diff": float(np.mean(np.abs(np.asarray(right_drive_hist) - np.asarray(left_drive_hist)))) if left_drive_hist else 0.0,
            "end_yaw": float(observation.yaw),
            "mean_forward_speed_log": float(observation.forward_speed) if trajectory else 0.0,
        }
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a first causal descending motor-response atlas using direct descending perturbations.")
    parser.add_argument("--config", default="configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml")
    parser.add_argument("--mode", choices=["mock", "flygym"], default="mock")
    parser.add_argument("--candidates-json", default="outputs/metrics/descending_readout_candidates_strict.json")
    parser.add_argument(
        "--labels",
        nargs="*",
        default=["DNg97", "DNp103", "DNp18", "DNp71", "DNpe040", "DNpe056", "DNpe031", "DNpe016", "DNae002"],
    )
    parser.add_argument(
        "--bilateral-labels",
        nargs="*",
        default=["DNg97", "DNp103", "DNp18", "DNpe016", "DNae002"],
        help="Labels to stimulate bilaterally by default; all others use left/right paired stimulation.",
    )
    parser.add_argument("--stim-current", type=float, default=40.0)
    parser.add_argument("--duration", type=float, default=0.1)
    parser.add_argument("--output-csv", default="outputs/metrics/descending_motor_atlas.csv")
    parser.add_argument("--output-json", default="outputs/metrics/descending_motor_atlas.json")
    args = parser.parse_args()

    config = load_config(args.config)
    candidate_map = _load_candidate_map(args.candidates_json)
    rows: list[dict] = []
    bilateral_labels = {str(label) for label in args.bilateral_labels}
    rows.append(
        _run_condition(
            config=config,
            mode=args.mode,
            label="baseline",
            side_mode="baseline",
            stim_current=0.0,
            duration_s=float(args.duration),
            candidate_map=candidate_map,
        )
    )
    for label in args.labels:
        if label not in candidate_map:
            raise KeyError(f"Label `{label}` not found in {args.candidates_json}.")
        side_modes = _default_side_modes(label, bilateral_labels)
        for side_mode in side_modes:
            rows.append(
                _run_condition(
                    config=config,
                    mode=args.mode,
                    label=label,
                    side_mode=side_mode,
                    stim_current=float(args.stim_current),
                    duration_s=float(args.duration),
                    candidate_map=candidate_map,
                )
            )

    out_csv = Path(args.output_csv)
    out_json = Path(args.output_json)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "config": args.config,
        "mode": args.mode,
        "candidates_json": args.candidates_json,
        "stim_current": float(args.stim_current),
        "duration": float(args.duration),
        "rows": rows,
    }
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

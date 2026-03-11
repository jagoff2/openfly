from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml


def _load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 0.0
    if float(np.std(a)) <= 1e-12 or float(np.std(b)) <= 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _extract_arrays(rows: list[dict[str, Any]]) -> dict[str, np.ndarray]:
    has_target = bool(rows and isinstance(rows[0].get("target_state"), dict) and rows[0]["target_state"].get("enabled", False))
    arrays: dict[str, np.ndarray] = {
        "dn_forward_signal": np.array([float(row["motor_readout"]["dn_forward_signal"]) for row in rows], dtype=float),
        "population_forward_signal": np.array([float(row["motor_readout"]["population_forward_signal"]) for row in rows], dtype=float),
        "dn_turn_signal": np.array([float(row["motor_readout"]["dn_turn_signal"]) for row in rows], dtype=float),
        "population_turn_signal": np.array([float(row["motor_readout"]["population_turn_signal"]) for row in rows], dtype=float),
        "forward_asymmetry_signal": np.tanh(
            np.array(
                [
                    float(row["motor_readout"]["forward_right_hz"]) - float(row["motor_readout"]["forward_left_hz"])
                    for row in rows
                ],
                dtype=float,
            )
            / 40.0
        ),
    }
    if has_target:
        bearing = np.array([float(row["target_state"]["bearing_body"]) for row in rows], dtype=float)
        arrays["target_bearing"] = bearing
        arrays["target_frontalness"] = np.cos(bearing)
    return arrays


def _replay_decoder(
    arrays: dict[str, np.ndarray],
    *,
    signal_smoothing_alpha: float,
    forward_gain: float,
    turn_gain: float,
    population_forward_weight: float,
    population_turn_weight: float,
    forward_asymmetry_turn_gain: float,
) -> tuple[np.ndarray, np.ndarray]:
    forward_signal = np.clip(
        arrays["dn_forward_signal"] + population_forward_weight * arrays["population_forward_signal"],
        -1.0,
        1.0,
    )
    turn_signal = np.clip(
        arrays["dn_turn_signal"]
        + population_turn_weight * arrays["population_turn_signal"]
        + forward_asymmetry_turn_gain * arrays["forward_asymmetry_signal"],
        -1.0,
        1.0,
    )

    alpha = float(np.clip(signal_smoothing_alpha, 0.0, 1.0))
    forward_state = 0.0
    turn_state = 0.0
    total_drive: list[float] = []
    drive_diff: list[float] = []
    for forward_step, turn_step in zip(forward_signal, turn_signal):
        forward_state = (1.0 - alpha) * forward_state + alpha * float(forward_step)
        turn_state = (1.0 - alpha) * turn_state + alpha * float(turn_step)
        base_drive = forward_gain * max(0.0, forward_state)
        total_drive.append(2.0 * base_drive)
        drive_diff.append(2.0 * turn_gain * turn_state)
    return np.array(total_drive, dtype=float), np.array(drive_diff, dtype=float)


def _score_candidate(
    target_arrays: dict[str, np.ndarray],
    no_target_arrays: dict[str, np.ndarray],
    *,
    signal_smoothing_alpha: float,
    forward_gain: float,
    turn_gain: float,
    population_forward_weight: float,
    population_turn_weight: float,
    forward_asymmetry_turn_gain: float,
) -> dict[str, float]:
    target_total_drive, target_drive_diff = _replay_decoder(
        target_arrays,
        signal_smoothing_alpha=signal_smoothing_alpha,
        forward_gain=forward_gain,
        turn_gain=turn_gain,
        population_forward_weight=population_forward_weight,
        population_turn_weight=population_turn_weight,
        forward_asymmetry_turn_gain=forward_asymmetry_turn_gain,
    )
    no_target_total_drive, no_target_drive_diff = _replay_decoder(
        no_target_arrays,
        signal_smoothing_alpha=signal_smoothing_alpha,
        forward_gain=forward_gain,
        turn_gain=turn_gain,
        population_forward_weight=population_forward_weight,
        population_turn_weight=population_turn_weight,
        forward_asymmetry_turn_gain=forward_asymmetry_turn_gain,
    )

    bearing = target_arrays["target_bearing"]
    frontalness = target_arrays["target_frontalness"]
    mask = np.abs(bearing) > 0.05
    steer_sign_match = float(np.mean(np.sign(target_drive_diff[mask]) == np.sign(bearing[mask]))) if np.any(mask) else 0.0
    steer_bearing_corr = _corr(target_drive_diff, bearing)
    forward_frontal_corr = _corr(target_total_drive, frontalness)
    mean_abs_drive_diff = float(np.mean(np.abs(target_drive_diff)))
    mean_total_drive = float(np.mean(target_total_drive))
    no_target_mean_abs_drive_diff = float(np.mean(np.abs(no_target_drive_diff)))
    no_target_mean_total_drive = float(np.mean(no_target_total_drive))
    delta_abs_drive_diff = mean_abs_drive_diff - no_target_mean_abs_drive_diff
    delta_total_drive = mean_total_drive - no_target_mean_total_drive

    score = (
        steer_bearing_corr
        + 0.5 * steer_sign_match
        + 0.25 * forward_frontal_corr
        + 0.1 * mean_abs_drive_diff
        + 0.05 * mean_total_drive
        + 0.2 * delta_abs_drive_diff
        + 0.1 * delta_total_drive
    )

    return {
        "score": float(score),
        "signal_smoothing_alpha": float(signal_smoothing_alpha),
        "forward_gain": float(forward_gain),
        "turn_gain": float(turn_gain),
        "population_forward_weight": float(population_forward_weight),
        "population_turn_weight": float(population_turn_weight),
        "forward_asymmetry_turn_gain": float(forward_asymmetry_turn_gain),
        "steer_bearing_corr": float(steer_bearing_corr),
        "steer_sign_match_rate": float(steer_sign_match),
        "forward_frontal_corr": float(forward_frontal_corr),
        "mean_abs_drive_diff": float(mean_abs_drive_diff),
        "mean_total_drive": float(mean_total_drive),
        "no_target_mean_abs_drive_diff": float(no_target_mean_abs_drive_diff),
        "no_target_mean_total_drive": float(no_target_mean_total_drive),
        "delta_abs_drive_diff": float(delta_abs_drive_diff),
        "delta_total_drive": float(delta_total_drive),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline decoder calibration sweep for the embodied UV-grid descending branch.")
    parser.add_argument(
        "--base-config",
        default="configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml",
    )
    parser.add_argument(
        "--target-log",
        default="outputs/requested_2s_splice_uvgrid_descending_target/flygym-demo-20260311-062430/run.jsonl",
    )
    parser.add_argument(
        "--no-target-log",
        default="outputs/requested_2s_splice_uvgrid_descending_no_target/flygym-demo-20260311-063926/run.jsonl",
    )
    parser.add_argument(
        "--csv-output",
        default="outputs/metrics/uvgrid_decoder_calibration.csv",
    )
    parser.add_argument(
        "--json-output",
        default="outputs/metrics/uvgrid_decoder_calibration.json",
    )
    parser.add_argument(
        "--best-json-output",
        default="outputs/metrics/uvgrid_decoder_calibration_best.json",
    )
    parser.add_argument("--top-k", type=int, default=25)
    args = parser.parse_args()

    base_config = yaml.safe_load(Path(args.base_config).read_text(encoding="utf-8"))
    base_decoder = base_config.get("decoder", {})
    target_arrays = _extract_arrays(_load_rows(Path(args.target_log)))
    no_target_arrays = _extract_arrays(_load_rows(Path(args.no_target_log)))

    candidates: list[dict[str, float]] = []
    for signal_smoothing_alpha in (0.06, 0.08, 0.12, 0.18, 0.24, 0.32):
        for population_forward_weight in (1.0, 1.1, 1.25, 1.4, 1.6):
            for population_turn_weight in (0.75, 1.0, 1.25, 1.5, 2.0):
                for forward_asymmetry_turn_gain in (0.0, 0.05, 0.1, 0.2, 0.3):
                    for forward_gain in (1.0, 1.1, 1.2):
                        for turn_gain in (0.45, 0.55, 0.65):
                            candidates.append(
                                _score_candidate(
                                    target_arrays,
                                    no_target_arrays,
                                    signal_smoothing_alpha=signal_smoothing_alpha,
                                    forward_gain=forward_gain,
                                    turn_gain=turn_gain,
                                    population_forward_weight=population_forward_weight,
                                    population_turn_weight=population_turn_weight,
                                    forward_asymmetry_turn_gain=forward_asymmetry_turn_gain,
                                )
                            )

    candidates.sort(key=lambda item: item["score"], reverse=True)
    top_rows = candidates[: max(1, int(args.top_k))]

    csv_path = Path(args.csv_output)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(top_rows[0].keys()))
        writer.writeheader()
        writer.writerows(top_rows)

    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(top_rows, indent=2), encoding="utf-8")

    best = top_rows[0].copy()
    best["base_decoder"] = {
        "signal_smoothing_alpha": float(base_decoder.get("signal_smoothing_alpha", 1.0)),
        "forward_gain": float(base_decoder.get("forward_gain", 0.4)),
        "turn_gain": float(base_decoder.get("turn_gain", 0.3)),
        "population_forward_weight": float(base_decoder.get("population_forward_weight", 0.0)),
        "population_turn_weight": float(base_decoder.get("population_turn_weight", 0.0)),
        "forward_asymmetry_turn_gain": float(base_decoder.get("forward_asymmetry_turn_gain", 0.0)),
    }
    Path(args.best_json_output).write_text(json.dumps(best, indent=2), encoding="utf-8")
    print(json.dumps(best, indent=2))


if __name__ == "__main__":
    main()

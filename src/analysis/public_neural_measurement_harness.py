from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class TraceParityScore:
    trace_id: str
    n_samples: int
    pearson_r: float
    lagged_pearson_r: float
    rmse: float
    nrmse: float
    mean_abs_error: float
    sign_agreement: float
    lagged_sign_agreement: float
    best_lag_steps: int
    best_lag_seconds: float

    def to_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


def _as_float_array(values: Iterable[float]) -> np.ndarray:
    array = np.asarray(list(values), dtype=float)
    if array.ndim != 1:
        raise ValueError("trace values must be 1D")
    if array.size == 0:
        raise ValueError("trace values must be non-empty")
    return array


def _resample_if_needed(values: np.ndarray, timebase: np.ndarray | None, target_timebase: np.ndarray | None) -> np.ndarray:
    if timebase is None or target_timebase is None:
        return values
    if len(values) != len(timebase):
        raise ValueError("values and timebase lengths must match")
    return np.interp(target_timebase, timebase, values)


def _sample_period_seconds(timebase: np.ndarray | None) -> float | None:
    if timebase is None or timebase.size < 2:
        return None
    deltas = np.diff(timebase)
    finite = deltas[np.isfinite(deltas) & (deltas > 0.0)]
    if finite.size == 0:
        return None
    return float(np.median(finite))


def _resolve_max_lag_steps(
    *,
    observed_timebase: np.ndarray | None,
    simulated_timebase: np.ndarray | None,
    max_lag_steps: int,
    max_lag_seconds: float | None,
    sample_count: int,
) -> int:
    resolved = max(0, int(max_lag_steps))
    if max_lag_seconds is not None and float(max_lag_seconds) > 0.0:
        dt_seconds = _sample_period_seconds(observed_timebase)
        if dt_seconds is None:
            dt_seconds = _sample_period_seconds(simulated_timebase)
        if dt_seconds is not None and dt_seconds > 0.0:
            resolved = max(resolved, int(round(float(max_lag_seconds) / dt_seconds)))
    return max(0, min(resolved, max(0, int(sample_count) - 2)))


def _score_zero_lag_arrays(observed: np.ndarray, simulated: np.ndarray) -> tuple[float, float, float, float]:
    delta = simulated - observed
    rmse = float(np.sqrt(np.mean(np.square(delta))))
    value_range = float(np.max(observed) - np.min(observed))
    nrmse = float(rmse / value_range) if value_range > 0.0 else 0.0
    observed_centered = observed - float(np.mean(observed))
    simulated_centered = simulated - float(np.mean(simulated))
    denom = float(np.linalg.norm(observed_centered) * np.linalg.norm(simulated_centered))
    pearson_r = float(np.dot(observed_centered, simulated_centered) / denom) if denom > 0.0 else 0.0
    sign_agreement = float(np.mean(np.sign(observed_centered) == np.sign(simulated_centered)))
    return pearson_r, rmse, nrmse, sign_agreement


def _shift_for_lag(observed: np.ndarray, simulated: np.ndarray, lag_steps: int) -> tuple[np.ndarray, np.ndarray]:
    if lag_steps < 0:
        return observed[-lag_steps:], simulated[: simulated.size + lag_steps]
    if lag_steps > 0:
        return observed[:-lag_steps], simulated[lag_steps:]
    return observed, simulated


def score_trace_pair(
    trace_id: str,
    observed_values: Iterable[float],
    simulated_values: Iterable[float],
    *,
    observed_timebase: Iterable[float] | None = None,
    simulated_timebase: Iterable[float] | None = None,
    max_lag_steps: int = 0,
    max_lag_seconds: float | None = None,
) -> TraceParityScore:
    observed = _as_float_array(observed_values)
    simulated = _as_float_array(simulated_values)
    obs_time = None if observed_timebase is None else _as_float_array(observed_timebase)
    sim_time = None if simulated_timebase is None else _as_float_array(simulated_timebase)

    if obs_time is not None and sim_time is not None:
        simulated = _resample_if_needed(simulated, sim_time, obs_time)
    elif observed.shape != simulated.shape:
        raise ValueError("observed and simulated traces must have the same length when no timebases are provided")

    if observed.shape != simulated.shape:
        raise ValueError("observed and simulated traces must have the same shape after alignment")

    valid_mask = np.isfinite(observed) & np.isfinite(simulated)
    if not np.any(valid_mask):
        return TraceParityScore(
            trace_id=trace_id,
            n_samples=0,
            pearson_r=0.0,
            lagged_pearson_r=0.0,
            rmse=0.0,
            nrmse=0.0,
            mean_abs_error=0.0,
            sign_agreement=0.0,
            lagged_sign_agreement=0.0,
            best_lag_steps=0,
            best_lag_seconds=0.0,
        )
    observed = observed[valid_mask]
    simulated = simulated[valid_mask]

    pearson_r, rmse, nrmse, sign_agreement = _score_zero_lag_arrays(observed, simulated)
    lag_steps_limit = _resolve_max_lag_steps(
        observed_timebase=obs_time,
        simulated_timebase=sim_time,
        max_lag_steps=max_lag_steps,
        max_lag_seconds=max_lag_seconds,
        sample_count=int(observed.size),
    )
    lagged_pearson_r = pearson_r
    lagged_sign_agreement = sign_agreement
    best_lag_steps = 0
    if lag_steps_limit > 0:
        best_signature = (pearson_r, sign_agreement, 0.0)
        for lag_steps in range(-lag_steps_limit, lag_steps_limit + 1):
            shifted_observed, shifted_simulated = _shift_for_lag(observed, simulated, lag_steps)
            if shifted_observed.size < 2 or shifted_simulated.size < 2:
                continue
            shifted_pearson_r, _, _, shifted_sign_agreement = _score_zero_lag_arrays(
                shifted_observed,
                shifted_simulated,
            )
            signature = (shifted_pearson_r, shifted_sign_agreement, -abs(float(lag_steps)))
            if signature > best_signature:
                best_signature = signature
                lagged_pearson_r = shifted_pearson_r
                lagged_sign_agreement = shifted_sign_agreement
                best_lag_steps = int(lag_steps)
    dt_seconds = _sample_period_seconds(obs_time)
    if dt_seconds is None:
        dt_seconds = _sample_period_seconds(sim_time)
    best_lag_seconds = float(best_lag_steps * dt_seconds) if dt_seconds is not None else 0.0
    delta = simulated - observed
    return TraceParityScore(
        trace_id=trace_id,
        n_samples=int(observed.size),
        pearson_r=pearson_r,
        lagged_pearson_r=lagged_pearson_r,
        rmse=rmse,
        nrmse=nrmse,
        mean_abs_error=float(np.mean(np.abs(delta))),
        sign_agreement=sign_agreement,
        lagged_sign_agreement=lagged_sign_agreement,
        best_lag_steps=best_lag_steps,
        best_lag_seconds=best_lag_seconds,
    )


def aggregate_trace_scores(scores: Iterable[TraceParityScore]) -> dict[str, float | int]:
    rows = list(scores)
    if not rows:
        raise ValueError("at least one trace score is required")
    valid_rows = [row for row in rows if int(row.n_samples) > 0]
    if not valid_rows:
        return {
            "trace_count": len(rows),
            "valid_trace_count": 0,
            "dropped_empty_trace_count": len(rows),
            "sample_count": 0,
            "mean_pearson_r": 0.0,
            "mean_lagged_pearson_r": 0.0,
            "mean_rmse": 0.0,
            "mean_nrmse": 0.0,
            "mean_abs_error": 0.0,
            "mean_sign_agreement": 0.0,
            "mean_lagged_sign_agreement": 0.0,
            "mean_best_lag_steps": 0.0,
            "mean_best_lag_seconds": 0.0,
            "sample_weighted_pearson_r": 0.0,
            "sample_weighted_lagged_pearson_r": 0.0,
            "sample_weighted_rmse": 0.0,
            "sample_weighted_nrmse": 0.0,
            "sample_weighted_abs_error": 0.0,
            "sample_weighted_sign_agreement": 0.0,
            "sample_weighted_lagged_sign_agreement": 0.0,
        }
    weights = np.asarray([row.n_samples for row in valid_rows], dtype=np.float64)
    return {
        "trace_count": len(rows),
        "valid_trace_count": len(valid_rows),
        "dropped_empty_trace_count": len(rows) - len(valid_rows),
        "sample_count": int(np.sum(weights)),
        "mean_pearson_r": float(np.mean([row.pearson_r for row in valid_rows])),
        "mean_lagged_pearson_r": float(np.mean([row.lagged_pearson_r for row in valid_rows])),
        "mean_rmse": float(np.mean([row.rmse for row in valid_rows])),
        "mean_nrmse": float(np.mean([row.nrmse for row in valid_rows])),
        "mean_abs_error": float(np.mean([row.mean_abs_error for row in valid_rows])),
        "mean_sign_agreement": float(np.mean([row.sign_agreement for row in valid_rows])),
        "mean_lagged_sign_agreement": float(np.mean([row.lagged_sign_agreement for row in valid_rows])),
        "mean_best_lag_steps": float(np.mean([row.best_lag_steps for row in valid_rows])),
        "mean_best_lag_seconds": float(np.mean([row.best_lag_seconds for row in valid_rows])),
        "sample_weighted_pearson_r": float(np.average([row.pearson_r for row in valid_rows], weights=weights)),
        "sample_weighted_lagged_pearson_r": float(
            np.average([row.lagged_pearson_r for row in valid_rows], weights=weights)
        ),
        "sample_weighted_rmse": float(np.average([row.rmse for row in valid_rows], weights=weights)),
        "sample_weighted_nrmse": float(np.average([row.nrmse for row in valid_rows], weights=weights)),
        "sample_weighted_abs_error": float(np.average([row.mean_abs_error for row in valid_rows], weights=weights)),
        "sample_weighted_sign_agreement": float(np.average([row.sign_agreement for row in valid_rows], weights=weights)),
        "sample_weighted_lagged_sign_agreement": float(
            np.average([row.lagged_sign_agreement for row in valid_rows], weights=weights)
        ),
    }

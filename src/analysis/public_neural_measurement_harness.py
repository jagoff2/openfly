from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class TraceParityScore:
    trace_id: str
    n_samples: int
    pearson_r: float
    rmse: float
    nrmse: float
    mean_abs_error: float
    sign_agreement: float

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


def score_trace_pair(
    trace_id: str,
    observed_values: Iterable[float],
    simulated_values: Iterable[float],
    *,
    observed_timebase: Iterable[float] | None = None,
    simulated_timebase: Iterable[float] | None = None,
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
            rmse=0.0,
            nrmse=0.0,
            mean_abs_error=0.0,
            sign_agreement=0.0,
        )
    observed = observed[valid_mask]
    simulated = simulated[valid_mask]

    delta = simulated - observed
    rmse = float(np.sqrt(np.mean(np.square(delta))))
    value_range = float(np.max(observed) - np.min(observed))
    nrmse = float(rmse / value_range) if value_range > 0.0 else 0.0
    observed_centered = observed - float(np.mean(observed))
    simulated_centered = simulated - float(np.mean(simulated))
    denom = float(np.linalg.norm(observed_centered) * np.linalg.norm(simulated_centered))
    pearson_r = float(np.dot(observed_centered, simulated_centered) / denom) if denom > 0.0 else 0.0
    sign_agreement = float(np.mean(np.sign(observed_centered) == np.sign(simulated_centered)))
    return TraceParityScore(
        trace_id=trace_id,
        n_samples=int(observed.size),
        pearson_r=pearson_r,
        rmse=rmse,
        nrmse=nrmse,
        mean_abs_error=float(np.mean(np.abs(delta))),
        sign_agreement=sign_agreement,
    )


def aggregate_trace_scores(scores: Iterable[TraceParityScore]) -> dict[str, float | int]:
    rows = list(scores)
    if not rows:
        raise ValueError("at least one trace score is required")
    return {
        "trace_count": len(rows),
        "mean_pearson_r": float(np.mean([row.pearson_r for row in rows])),
        "mean_rmse": float(np.mean([row.rmse for row in rows])),
        "mean_nrmse": float(np.mean([row.nrmse for row in rows])),
        "mean_abs_error": float(np.mean([row.mean_abs_error for row in rows])),
        "mean_sign_agreement": float(np.mean([row.sign_agreement for row in rows])),
    }

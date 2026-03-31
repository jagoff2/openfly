from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np


def normalize_observation_taus(taus_s: Sequence[float] | None) -> tuple[float, ...]:
    if not taus_s:
        return ()
    cleaned: list[float] = []
    for value in taus_s:
        tau = float(value)
        if tau <= 0.0:
            raise ValueError("observation tau values must be positive")
        if not any(abs(tau - existing) <= 1e-9 for existing in cleaned):
            cleaned.append(tau)
    return tuple(cleaned)


def _causal_exp_lowpass(values: np.ndarray, timebase_s: np.ndarray, tau_s: float) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    timebase_s = np.asarray(timebase_s, dtype=np.float32).reshape(-1)
    if values.size != timebase_s.size:
        raise ValueError("values and timebase must have matching lengths")
    if values.size == 0:
        return np.zeros(0, dtype=np.float32)
    filtered = np.empty_like(values, dtype=np.float32)
    filtered[0] = values[0]
    tau = float(tau_s)
    for idx in range(1, values.size):
        dt = max(0.0, float(timebase_s[idx] - timebase_s[idx - 1]))
        alpha = float(np.exp(-dt / tau)) if tau > 0.0 else 0.0
        filtered[idx] = np.float32(alpha * float(filtered[idx - 1]) + (1.0 - alpha) * float(values[idx]))
    return filtered


def augment_feature_matrix_with_observation_basis(
    feature_matrix: np.ndarray,
    timebase_s: Iterable[float],
    *,
    observation_taus_s: Sequence[float] | None,
    feature_names: Sequence[str] | None = None,
) -> tuple[np.ndarray, tuple[str, ...] | None]:
    matrix = np.asarray(feature_matrix, dtype=np.float32)
    if matrix.ndim != 2:
        raise ValueError("feature_matrix must be 2D")
    taus = normalize_observation_taus(observation_taus_s)
    if not taus:
        names = None if feature_names is None else tuple(str(value) for value in feature_names)
        return matrix.astype(np.float32, copy=False), names
    timebase = np.asarray(list(timebase_s), dtype=np.float32).reshape(-1)
    if matrix.shape[1] != timebase.size:
        raise ValueError("feature_matrix column count must match timebase length")
    blocks = [matrix.astype(np.float32, copy=False)]
    names: list[str] | None = None
    if feature_names is not None:
        names = [str(value) for value in feature_names]
    for tau_s in taus:
        filtered_rows = [_causal_exp_lowpass(matrix[row_idx], timebase, float(tau_s)) for row_idx in range(matrix.shape[0])]
        blocks.append(np.stack(filtered_rows, axis=0).astype(np.float32, copy=False))
        if names is not None:
            names.extend(f"{base_name}::obs_lp_tau_{tau_s:g}s" for base_name in feature_names)
    augmented = np.concatenate(blocks, axis=0).astype(np.float32, copy=False)
    return augmented, (tuple(names) if names is not None else None)

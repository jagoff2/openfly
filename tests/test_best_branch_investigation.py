from __future__ import annotations

import numpy as np

from analysis.best_branch_investigation import (
    align_framewise_matrix,
    compute_selected_frame_counts,
    pearson_correlation,
)


def test_align_framewise_matrix_selects_frame_cycles() -> None:
    matrix = np.asarray(
        [
            [0.0, 1.0, 2.0, 3.0, 4.0],
            [10.0, 11.0, 12.0, 13.0, 14.0],
        ],
        dtype=np.float32,
    )
    aligned = align_framewise_matrix(matrix, np.asarray([0, 2, 4], dtype=np.int64))
    assert aligned.shape == (2, 3)
    assert np.allclose(aligned[0], [0.0, 2.0, 4.0])
    assert np.allclose(aligned[1], [10.0, 12.0, 14.0])


def test_compute_selected_frame_counts_prefers_spikes_then_magnitude() -> None:
    voltage = np.asarray(
        [
            [0.1, 5.0, 0.2, 0.3],
            [0.1, 0.2, 4.0, 0.3],
        ],
        dtype=np.float32,
    )
    spikes = np.asarray(
        [
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        dtype=np.uint8,
    )
    counts = compute_selected_frame_counts(voltage, spikes, max_points=2)
    assert counts.tolist() == [0, 1, 1, 2]


def test_pearson_correlation_returns_nan_for_constant_trace() -> None:
    corr = pearson_correlation(np.asarray([1.0, 1.0, 1.0]), np.asarray([0.0, 1.0, 2.0]))
    assert np.isnan(corr)

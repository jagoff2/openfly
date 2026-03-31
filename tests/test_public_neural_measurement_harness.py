from __future__ import annotations

import pytest

from analysis.public_neural_measurement_harness import aggregate_trace_scores, score_trace_pair


def test_score_trace_pair_perfect_match() -> None:
    score = score_trace_pair("t1", [0.0, 1.0, 2.0], [0.0, 1.0, 2.0])
    assert score.pearson_r == pytest.approx(1.0)
    assert score.rmse == pytest.approx(0.0)
    assert score.mean_abs_error == pytest.approx(0.0)


def test_score_trace_pair_resamples_simulated_trace() -> None:
    score = score_trace_pair(
        "t2",
        [0.0, 1.0, 0.0],
        [0.0, 0.5, 1.0, 0.5, 0.0],
        observed_timebase=[0.0, 1.0, 2.0],
        simulated_timebase=[0.0, 0.5, 1.0, 1.5, 2.0],
    )
    assert score.n_samples == 3
    assert score.pearson_r > 0.99


def test_aggregate_trace_scores_computes_means() -> None:
    scores = [
        score_trace_pair("a", [0.0, 1.0], [0.0, 1.0]),
        score_trace_pair("b", [0.0, 1.0], [1.0, 0.0]),
    ]
    summary = aggregate_trace_scores(scores)
    assert summary["trace_count"] == 2
    assert "mean_pearson_r" in summary

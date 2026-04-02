from __future__ import annotations

import pytest

from analysis.public_neural_measurement_harness import aggregate_trace_scores, score_trace_pair


def test_score_trace_pair_perfect_match() -> None:
    score = score_trace_pair("t1", [0.0, 1.0, 2.0], [0.0, 1.0, 2.0])
    assert score.pearson_r == pytest.approx(1.0)
    assert score.lagged_pearson_r == pytest.approx(1.0)
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


def test_score_trace_pair_reports_best_local_lag() -> None:
    score = score_trace_pair(
        "lagged",
        [0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0],
        observed_timebase=[0.0, 0.1, 0.2, 0.3, 0.4],
        simulated_timebase=[0.0, 0.1, 0.2, 0.3, 0.4],
        max_lag_seconds=0.2,
    )
    assert score.pearson_r < 0.0
    assert score.lagged_pearson_r == pytest.approx(1.0)
    assert score.best_lag_steps == -1
    assert score.best_lag_seconds == pytest.approx(-0.1)


def test_aggregate_trace_scores_computes_means() -> None:
    scores = [
        score_trace_pair("a", [0.0, 1.0], [0.0, 1.0]),
        score_trace_pair("b", [0.0, 1.0], [1.0, 0.0]),
    ]
    summary = aggregate_trace_scores(scores)
    assert summary["trace_count"] == 2
    assert summary["valid_trace_count"] == 2
    assert summary["dropped_empty_trace_count"] == 0
    assert summary["sample_count"] == 4
    assert "mean_pearson_r" in summary
    assert "mean_lagged_pearson_r" in summary
    assert "sample_weighted_pearson_r" in summary
    assert "sample_weighted_lagged_pearson_r" in summary


def test_aggregate_trace_scores_drops_empty_rows_from_means() -> None:
    scores = [
        score_trace_pair("a", [0.0, 1.0], [0.0, 1.0]),
        score_trace_pair("empty", [float("nan"), float("nan")], [float("nan"), float("nan")]),
    ]
    summary = aggregate_trace_scores(scores)
    assert summary["trace_count"] == 2
    assert summary["valid_trace_count"] == 1
    assert summary["dropped_empty_trace_count"] == 1
    assert summary["sample_count"] == 2
    assert summary["mean_pearson_r"] == pytest.approx(1.0)
    assert summary["mean_lagged_pearson_r"] == pytest.approx(1.0)

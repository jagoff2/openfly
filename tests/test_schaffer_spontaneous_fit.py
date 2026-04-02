from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

import analysis.schaffer_spontaneous_fit as schaffer_fit
from analysis.schaffer_parity_harness import SchafferCanonicalTrialData
from analysis.schaffer_spontaneous_fit import (
    _trial_ball_motion_values,
    _trial_behavioral_state_values,
    _trial_session_key,
    SchafferReplayConfig,
    run_schaffer_spontaneous_fit,
)
from analysis.public_body_feedback import public_body_feedback_from_schaffer_covariates


def _trial() -> SchafferCanonicalTrialData:
    return SchafferCanonicalTrialData(
        trial_id="trial",
        split="train",
        behavior_context="behaving_imaging",
        matrix=np.zeros((2, 3), dtype=np.float32),
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        stimulus={},
        ball_motion=np.asarray([0.0, 2.0], dtype=np.float32),
        ball_motion_time_s=np.asarray([0.0, 1.0], dtype=np.float32),
        behavioral_state=np.asarray([[0.0, 2.0], [1.0, 3.0]], dtype=np.float32),
        behavioral_state_time_s=np.asarray([0.0, 1.0], dtype=np.float32),
        metadata={},
    )


def test_trial_ball_motion_values_resamples_and_normalizes() -> None:
    values = _trial_ball_motion_values(_trial())
    np.testing.assert_allclose(values, np.asarray([0.0, 0.5, 1.0], dtype=np.float32), atol=1e-6)


def test_trial_behavioral_state_values_resamples_per_channel() -> None:
    values = _trial_behavioral_state_values(_trial())
    expected = np.asarray([[0.0, 1.0, 2.0], [1.0, 2.0, 3.0]], dtype=np.float32)
    np.testing.assert_allclose(values, expected, atol=1e-6)


def test_trial_ball_motion_values_handles_missing_covariate() -> None:
    trial = _trial()
    missing = SchafferCanonicalTrialData(
        trial_id=trial.trial_id,
        split=trial.split,
        behavior_context=trial.behavior_context,
        matrix=trial.matrix,
        timebase_s=trial.timebase_s,
        stimulus=trial.stimulus,
        ball_motion=None,
        ball_motion_time_s=None,
        behavioral_state=trial.behavioral_state,
        behavioral_state_time_s=trial.behavioral_state_time_s,
        metadata=trial.metadata,
    )
    values = _trial_ball_motion_values(missing)
    np.testing.assert_allclose(values, np.zeros(3, dtype=np.float32), atol=1e-6)


def test_public_body_feedback_from_schaffer_covariates_exposes_exafferent_and_state_channels() -> None:
    channels = public_body_feedback_from_schaffer_covariates(
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        ball_motion_values=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        behavioral_state_values=np.asarray(
            [
                [0.0, 0.5, 1.0],
                [1.0, 0.5, 0.0],
            ],
            dtype=np.float32,
        ),
        sample_index=1,
        forward_speed_scale=2.0,
        contact_force_scale=3.0,
    )

    assert channels.forward_speed == pytest.approx(1.0)
    assert channels.contact_force >= 1.5
    assert channels.exafferent_drive == pytest.approx(0.5)
    assert channels.behavioral_state_level > 0.0
    assert channels.behavioral_state_transition > 0.0


def _synthetic_trial(trial_id: str, *, split: str, trace_count: int) -> SchafferCanonicalTrialData:
    return SchafferCanonicalTrialData(
        trial_id=trial_id,
        split=split,
        behavior_context="behaving_imaging",
        matrix=np.zeros((trace_count, 3), dtype=np.float32),
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        stimulus={},
        ball_motion=np.asarray([0.0, 1.0, 0.0], dtype=np.float32),
        ball_motion_time_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        behavioral_state=np.zeros((1, 3), dtype=np.float32),
        behavioral_state_time_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        metadata={},
    )


def test_run_schaffer_spontaneous_fit_rejects_mixed_trace_counts(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        schaffer_fit,
        "load_schaffer_canonical_trial_data",
        lambda bundle_path: [
            _synthetic_trial("a", split="train", trace_count=2),
            _synthetic_trial("b", split="test", trace_count=3),
        ],
    )
    monkeypatch.setattr(schaffer_fit, "build_backend_from_config", lambda *args, **kwargs: (SimpleNamespace(device="cpu"), {"encoder": {}}))
    monkeypatch.setattr(schaffer_fit, "build_family_basis_operators", lambda *args, **kwargs: SimpleNamespace(groups=(object(),)))
    replay_config = SchafferReplayConfig(brain_config_path="dummy")
    with pytest.raises(ValueError, match="do not share one trace count"):
        run_schaffer_spontaneous_fit(
            bundle_path=tmp_path / "bundle.json",
            replay_config=replay_config,
            output_dir=tmp_path / "out",
        )


def test_run_schaffer_spontaneous_fit_accepts_same_session_allowlist(monkeypatch, tmp_path) -> None:
    trials = [
        _synthetic_trial("a", split="train", trace_count=2),
        _synthetic_trial("b", split="test", trace_count=2),
        _synthetic_trial("c", split="test", trace_count=3),
    ]
    monkeypatch.setattr(schaffer_fit, "load_schaffer_canonical_trial_data", lambda bundle_path: trials)
    monkeypatch.setattr(schaffer_fit, "build_backend_from_config", lambda *args, **kwargs: (SimpleNamespace(device="cpu"), {"encoder": {}}))
    monkeypatch.setattr(schaffer_fit.EncoderConfig, "from_mapping", staticmethod(lambda mapping: None))
    monkeypatch.setattr(schaffer_fit, "SensoryEncoder", lambda cfg: None)
    monkeypatch.setattr(schaffer_fit, "build_family_basis_operators", lambda *args, **kwargs: SimpleNamespace(groups=(object(),)))

    def _simulate(_backend, _basis, trial, **kwargs):
        feature_matrix = np.ones((2, trial.timebase_s.size), dtype=np.float32)
        return {
            "trial_id": trial.trial_id,
            "split": trial.split,
            "behavior_context": trial.behavior_context,
            "feature_names": ("f0", "f1"),
            "timebase_s": trial.timebase_s,
            "ball_motion_values": np.zeros(trial.timebase_s.size, dtype=np.float32),
            "behavioral_state_values": np.zeros((1, trial.timebase_s.size), dtype=np.float32),
            "feature_matrix": feature_matrix,
            "session_key": _trial_session_key(trial),
            "session_start_time_s": float(kwargs["session_time_offset_s"]),
            "session_stop_time_s": float(kwargs["session_time_offset_s"] + float(trial.timebase_s[-1])),
        }

    monkeypatch.setattr(schaffer_fit, "simulate_schaffer_trial_feature_matrix", _simulate)
    summary = run_schaffer_spontaneous_fit(
        bundle_path=tmp_path / "bundle.json",
        replay_config=SchafferReplayConfig(brain_config_path="dummy", max_basis_dim=2),
        output_dir=tmp_path / "out",
        trial_id_allowlist=["a", "b"],
        fit_trial_ids=["a"],
    )
    assert summary["trial_summaries"][0]["trial_id"] == "a"
    assert summary["feature_count"] == 2
    assert summary["trial_summaries"][0]["session_key"] == "a"


def test_trial_session_key_prefers_metadata_session_file() -> None:
    trial = _synthetic_trial("2022_01_08_fly1_trial_000", split="test", trace_count=2)
    with_metadata = SchafferCanonicalTrialData(
        trial_id=trial.trial_id,
        split=trial.split,
        behavior_context=trial.behavior_context,
        matrix=trial.matrix,
        timebase_s=trial.timebase_s,
        stimulus=trial.stimulus,
        ball_motion=trial.ball_motion,
        ball_motion_time_s=trial.ball_motion_time_s,
        behavioral_state=trial.behavioral_state,
        behavioral_state_time_s=trial.behavioral_state_time_s,
        metadata={"session_file": "2022_01_08_fly1.nwb"},
    )
    assert _trial_session_key(with_metadata) == "2022_01_08_fly1.nwb"


def test_run_schaffer_spontaneous_fit_preserves_state_within_session(monkeypatch, tmp_path) -> None:
    def _session_trial(
        trial_id: str,
        *,
        start_time_s: float,
        stop_time_s: float,
    ) -> SchafferCanonicalTrialData:
        return SchafferCanonicalTrialData(
            trial_id=trial_id,
            split="test",
            behavior_context="behaving_imaging",
            matrix=np.zeros((2, 3), dtype=np.float32),
            timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
            stimulus={"parameters": {"start_time_s": start_time_s, "stop_time_s": stop_time_s}},
            ball_motion=np.asarray([0.0, 1.0, 0.0], dtype=np.float32),
            ball_motion_time_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
            behavioral_state=np.zeros((1, 3), dtype=np.float32),
            behavioral_state_time_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
            metadata={"session_file": "2022_01_08_fly1.nwb"},
        )

    trials = [
        _session_trial("2022_01_08_fly1_trial_000", start_time_s=29.6815, stop_time_s=299.9877),
        _session_trial("2022_01_08_fly1_trial_001", start_time_s=299.9877, stop_time_s=599.9753),
    ]
    monkeypatch.setattr(schaffer_fit, "load_schaffer_canonical_trial_data", lambda bundle_path: trials)
    monkeypatch.setattr(
        schaffer_fit,
        "build_backend_from_config",
        lambda *args, **kwargs: (SimpleNamespace(device="cpu"), {"encoder": {}}),
    )
    monkeypatch.setattr(schaffer_fit.EncoderConfig, "from_mapping", staticmethod(lambda mapping: None))
    monkeypatch.setattr(schaffer_fit, "SensoryEncoder", lambda cfg: None)
    monkeypatch.setattr(
        schaffer_fit,
        "build_family_basis_operators",
        lambda *args, **kwargs: SimpleNamespace(groups=(object(),)),
    )
    recorded_calls: list[dict[str, float | bool | str]] = []

    def _simulate(_backend, _basis, trial, **kwargs):
        recorded_calls.append(
            {
                "trial_id": trial.trial_id,
                "reset_backend": bool(kwargs["reset_backend"]),
                "session_time_offset_s": float(kwargs["session_time_offset_s"]),
                "pre_gap_s": float(kwargs["pre_gap_s"]),
            }
        )
        feature_matrix = np.ones((2, trial.timebase_s.size), dtype=np.float32)
        return {
            "trial_id": trial.trial_id,
            "split": trial.split,
            "behavior_context": trial.behavior_context,
            "feature_names": ("f0", "f1"),
            "timebase_s": trial.timebase_s,
            "ball_motion_values": np.zeros(trial.timebase_s.size, dtype=np.float32),
            "behavioral_state_values": np.zeros((1, trial.timebase_s.size), dtype=np.float32),
            "feature_matrix": feature_matrix,
            "session_key": _trial_session_key(trial),
            "session_start_time_s": float(kwargs["session_time_offset_s"]),
            "session_stop_time_s": float(kwargs["session_time_offset_s"] + float(trial.timebase_s[-1])),
        }

    class _Model(SimpleNamespace):
        fit_trial_ids: tuple[str, ...]
        max_basis_dim: int
        ridge_lambda: float

    monkeypatch.setattr(schaffer_fit, "simulate_schaffer_trial_feature_matrix", _simulate)
    monkeypatch.setattr(
        schaffer_fit,
        "fit_reduced_linear_projection",
        lambda *args, **kwargs: _Model(
            fit_trial_ids=tuple(kwargs["fit_trial_ids"]),
            max_basis_dim=int(kwargs["max_basis_dim"]),
            ridge_lambda=float(kwargs["ridge_lambda"]),
            feature_mean=np.zeros(2, dtype=np.float32),
            feature_scale=np.ones(2, dtype=np.float32),
            projection_components=np.eye(2, dtype=np.float32),
            beta=np.zeros((2, 2), dtype=np.float32),
            feature_names=tuple(kwargs["feature_names"]),
        ),
    )
    monkeypatch.setattr(
        schaffer_fit,
        "apply_reduced_linear_projection",
        lambda model, feature_matrix: np.zeros((2, feature_matrix.shape[1]), dtype=np.float32),
    )
    monkeypatch.setattr(
        schaffer_fit,
        "score_schaffer_trial_matrix",
        lambda trial, predicted, simulated_timebase_s=None: {
            "trial_id": trial.trial_id,
            "split": trial.split,
            "behavior_context": trial.behavior_context,
            "trace_count": 2,
            "time_count": int(predicted.shape[1]),
            "aggregate": {
                "trace_count": 2,
                "mean_pearson_r": 0.0,
                "mean_rmse": 0.0,
                "mean_nrmse": 0.0,
                "mean_abs_error": 0.0,
                "mean_sign_agreement": 1.0,
            },
            "trace_scores": [],
        },
    )

    summary = run_schaffer_spontaneous_fit(
        bundle_path=tmp_path / "bundle.json",
        replay_config=SchafferReplayConfig(brain_config_path="dummy", max_basis_dim=2),
        output_dir=tmp_path / "out",
        trial_id_allowlist=[trial.trial_id for trial in trials],
        fit_trial_ids=[trials[0].trial_id],
    )

    assert summary["preserve_state_within_session"] is True
    assert [call["reset_backend"] for call in recorded_calls] == [True, False]
    assert recorded_calls[0]["session_time_offset_s"] == pytest.approx(29.6815)
    assert recorded_calls[1]["session_time_offset_s"] == pytest.approx(299.9877)
    assert recorded_calls[1]["pre_gap_s"] == pytest.approx(0.0)


def test_run_schaffer_spontaneous_fit_applies_observation_basis_continuously_within_session(monkeypatch, tmp_path) -> None:
    def _session_trial(
        trial_id: str,
        *,
        start_time_s: float,
        stop_time_s: float,
    ) -> SchafferCanonicalTrialData:
        return SchafferCanonicalTrialData(
            trial_id=trial_id,
            split="train",
            behavior_context="behaving_imaging",
            matrix=np.zeros((2, 3), dtype=np.float32),
            timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
            stimulus={"parameters": {"start_time_s": start_time_s, "stop_time_s": stop_time_s}},
            ball_motion=np.asarray([0.0, 1.0, 0.0], dtype=np.float32),
            ball_motion_time_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
            behavioral_state=np.zeros((1, 3), dtype=np.float32),
            behavioral_state_time_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
            metadata={"session_file": "2022_01_08_fly1.nwb"},
        )

    trials = [
        _session_trial("2022_01_08_fly1_trial_000", start_time_s=10.0, stop_time_s=11.0),
        _session_trial("2022_01_08_fly1_trial_001", start_time_s=11.0, stop_time_s=12.0),
    ]
    monkeypatch.setattr(schaffer_fit, "load_schaffer_canonical_trial_data", lambda bundle_path: trials)
    monkeypatch.setattr(
        schaffer_fit,
        "build_backend_from_config",
        lambda *args, **kwargs: (SimpleNamespace(device="cpu"), {"encoder": {}}),
    )
    monkeypatch.setattr(schaffer_fit.EncoderConfig, "from_mapping", staticmethod(lambda mapping: None))
    monkeypatch.setattr(schaffer_fit, "SensoryEncoder", lambda cfg: None)
    monkeypatch.setattr(
        schaffer_fit,
        "build_family_basis_operators",
        lambda *args, **kwargs: SimpleNamespace(groups=(object(),)),
    )

    def _simulate(_backend, _basis, trial, **kwargs):
        feature_matrix = np.ones((2, trial.timebase_s.size), dtype=np.float32)
        return {
            "trial_id": trial.trial_id,
            "split": trial.split,
            "behavior_context": trial.behavior_context,
            "feature_names": ("bilateral::f0", "global::mean_voltage"),
            "timebase_s": trial.timebase_s,
            "ball_motion_values": np.zeros(trial.timebase_s.size, dtype=np.float32),
            "behavioral_state_values": np.zeros((1, trial.timebase_s.size), dtype=np.float32),
            "feature_matrix": feature_matrix,
            "session_key": _trial_session_key(trial),
            "session_start_time_s": float(kwargs["session_time_offset_s"]),
            "session_stop_time_s": float(kwargs["session_time_offset_s"] + float(trial.timebase_s[-1])),
        }

    captured_timebases: list[np.ndarray] = []

    def _augment(feature_matrix, timebase_s, *, observation_taus_s, feature_names):
        captured_timebases.append(np.asarray(timebase_s, dtype=np.float32))
        return np.asarray(feature_matrix, dtype=np.float32), tuple(str(v) for v in feature_names)

    class _Model(SimpleNamespace):
        fit_trial_ids: tuple[str, ...]
        max_basis_dim: int
        ridge_lambda: float

    monkeypatch.setattr(schaffer_fit, "simulate_schaffer_trial_feature_matrix", _simulate)
    monkeypatch.setattr(schaffer_fit, "augment_feature_matrix_with_observation_basis", _augment)
    monkeypatch.setattr(
        schaffer_fit,
        "fit_reduced_linear_projection",
        lambda *args, **kwargs: _Model(
            fit_trial_ids=tuple(kwargs["fit_trial_ids"]),
            max_basis_dim=int(kwargs["max_basis_dim"]),
            ridge_lambda=float(kwargs["ridge_lambda"]),
            feature_mean=np.zeros(2, dtype=np.float32),
            feature_scale=np.ones(2, dtype=np.float32),
            projection_components=np.eye(2, dtype=np.float32),
            beta=np.zeros((2, 2), dtype=np.float32),
            feature_names=tuple(kwargs["feature_names"]),
        ),
    )
    monkeypatch.setattr(
        schaffer_fit,
        "apply_reduced_linear_projection",
        lambda model, feature_matrix: np.zeros((2, feature_matrix.shape[1]), dtype=np.float32),
    )
    monkeypatch.setattr(
        schaffer_fit,
        "score_schaffer_trial_matrix",
        lambda trial, predicted, simulated_timebase_s=None: {
            "trial_id": trial.trial_id,
            "split": trial.split,
            "behavior_context": trial.behavior_context,
            "trace_count": 2,
            "time_count": int(predicted.shape[1]),
            "aggregate": {
                "trace_count": 2,
                "mean_pearson_r": 0.0,
                "mean_rmse": 0.0,
                "mean_nrmse": 0.0,
                "mean_abs_error": 0.0,
                "mean_sign_agreement": 1.0,
            },
            "trace_scores": [],
        },
    )

    run_schaffer_spontaneous_fit(
        bundle_path=tmp_path / "bundle.json",
        replay_config=SchafferReplayConfig(brain_config_path="dummy", max_basis_dim=2, observation_taus_s=(0.5,)),
        output_dir=tmp_path / "out",
        trial_id_allowlist=[trial.trial_id for trial in trials],
        fit_trial_ids=[trials[0].trial_id],
    )

    assert len(captured_timebases) == 1
    np.testing.assert_allclose(captured_timebases[0], np.asarray([10.0, 10.5, 11.0, 11.0, 11.5, 12.0], dtype=np.float32))

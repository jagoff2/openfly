from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np

from analysis.schaffer_nwb_canonical_dataset import export_schaffer_nwb_canonical_dataset
from analysis.schaffer_parity_harness import load_schaffer_canonical_trial_data, score_schaffer_trial_matrix


def _write_minimal_schaffer_nwb(path: Path) -> None:
    timestamps = np.arange(0.0, 12.0, 1.0, dtype=np.float32)
    dff = np.stack(
        [
            np.linspace(0.0, 1.0, timestamps.size, dtype=np.float32),
            np.linspace(1.0, 0.0, timestamps.size, dtype=np.float32),
        ],
        axis=1,
    )
    ball = np.linspace(0.0, 2.0, timestamps.size, dtype=np.float32)
    state = np.stack([ball, ball * 0.0 + 1.0], axis=1).astype(np.float32)
    starts = np.asarray([0.0, 6.0], dtype=np.float32)
    stops = np.asarray([5.0, 11.0], dtype=np.float32)
    ids = np.asarray([0, 1], dtype=np.int64)
    with h5py.File(path, "w") as handle:
        roi_series = handle.create_group("/processing/ophys/DfOverF/RoiResponseSeries")
        roi_series.create_dataset("data", data=dff)
        roi_series.create_dataset("timestamps", data=timestamps)
        behavior = handle.create_group("/processing/behavior/ball_motion")
        behavior.create_dataset("data", data=ball)
        behavior.create_dataset("timestamps", data=timestamps)
        state_group = handle.create_group("/processing/behavioral state/behavioral state")
        state_group.create_dataset("data", data=state)
        state_group.create_dataset("timestamps", data=timestamps)
        trials = handle.create_group("/intervals/trials")
        trials.create_dataset("id", data=ids)
        trials.create_dataset("start_time", data=starts)
        trials.create_dataset("stop_time", data=stops)
        seg = handle.create_group("/processing/ophys/ImageSegmentation/ImagingPlane")
        seg.create_dataset("id", data=np.asarray([10, 11], dtype=np.int64))


def test_load_schaffer_canonical_trial_data_loads_behavior_arrays(tmp_path: Path) -> None:
    dataset_root = tmp_path / "dataset"
    output_dir = tmp_path / "out"
    dataset_root.mkdir()
    _write_minimal_schaffer_nwb(dataset_root / "tiny_session.nwb")
    export_schaffer_nwb_canonical_dataset(dataset_root, output_dir=output_dir)

    trials = load_schaffer_canonical_trial_data(output_dir / "schaffer2023_nwb_canonical_bundle.json")
    assert len(trials) == 2
    first = trials[0]
    assert first.ball_motion is not None
    assert first.ball_motion.shape == (6,)
    assert first.ball_motion_time_s is not None
    assert np.allclose(first.ball_motion_time_s, np.arange(6, dtype=np.float32))
    assert first.behavioral_state is not None
    assert first.behavioral_state.shape == (2, 6)
    assert first.behavioral_state_time_s is not None
    assert np.allclose(first.behavioral_state_time_s, np.arange(6, dtype=np.float32))


def test_score_schaffer_trial_matrix_identity(tmp_path: Path) -> None:
    dataset_root = tmp_path / "dataset"
    output_dir = tmp_path / "out"
    dataset_root.mkdir()
    _write_minimal_schaffer_nwb(dataset_root / "tiny_session.nwb")
    export_schaffer_nwb_canonical_dataset(dataset_root, output_dir=output_dir)

    trials = load_schaffer_canonical_trial_data(output_dir / "schaffer2023_nwb_canonical_bundle.json")
    score = score_schaffer_trial_matrix(trials[0], trials[0].matrix.copy(), simulated_timebase_s=trials[0].timebase_s.copy())
    assert score["aggregate"]["mean_rmse"] == 0.0
    assert score["aggregate"]["mean_abs_error"] == 0.0
    assert score["aggregate"]["mean_sign_agreement"] == 1.0


def test_score_schaffer_trial_matrix_ignores_nan_samples(tmp_path: Path) -> None:
    dataset_root = tmp_path / "dataset"
    output_dir = tmp_path / "out"
    dataset_root.mkdir()
    _write_minimal_schaffer_nwb(dataset_root / "tiny_session.nwb")
    export_schaffer_nwb_canonical_dataset(dataset_root, output_dir=output_dir)

    trials = load_schaffer_canonical_trial_data(output_dir / "schaffer2023_nwb_canonical_bundle.json")
    simulated = trials[0].matrix.copy()
    simulated[:, 0] = np.nan
    score = score_schaffer_trial_matrix(trials[0], simulated, simulated_timebase_s=trials[0].timebase_s.copy())
    assert score["aggregate"]["mean_rmse"] == 0.0
    assert score["aggregate"]["mean_abs_error"] == 0.0

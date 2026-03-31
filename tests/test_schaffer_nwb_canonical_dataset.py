from __future__ import annotations

import json
from pathlib import Path

import h5py
import numpy as np

from analysis.schaffer_nwb_canonical_dataset import export_schaffer_nwb_canonical_dataset


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


def test_export_schaffer_nwb_canonical_dataset(tmp_path: Path) -> None:
    dataset_root = tmp_path / "dataset"
    output_dir = tmp_path / "out"
    dataset_root.mkdir()
    _write_minimal_schaffer_nwb(dataset_root / "tiny_session.nwb")

    summary = export_schaffer_nwb_canonical_dataset(dataset_root, output_dir=output_dir)

    assert summary["staged_session_count"] == 1
    assert summary["exported_session_count"] == 1
    assert summary["trial_count"] == 2
    bundle = json.loads((output_dir / "schaffer2023_nwb_canonical_bundle.json").read_text(encoding="utf-8"))
    assert bundle["dataset_key"] == "schaffer2023_figshare_nwb"
    assert len(bundle["trials"]) == 2
    first_trial = bundle["trials"][0]
    assert first_trial["split"] == "train"
    assert first_trial["behavior_context"] == "behaving_imaging"
    assert first_trial["stimulus"]["stimulus_name"] == "schaffer2023_behavior_interval"
    assert len(first_trial["traces"]) == 2
    trial_matrix = np.load(first_trial["traces"][0]["values_path"])
    assert trial_matrix.shape == (2, 6)
    trial_time = np.load(first_trial["timebase_path"])
    assert np.allclose(trial_time, np.arange(6, dtype=np.float32))
    ball = np.load(first_trial["behavior_paths"]["ball_motion_path"])
    state = np.load(first_trial["behavior_paths"]["behavioral_state_path"])
    assert ball.shape == (6,)
    assert state.shape == (2, 6)

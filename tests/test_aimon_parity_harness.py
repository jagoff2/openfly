from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from analysis.aimon_parity_harness import load_aimon_canonical_trial_data, score_aimon_trial_matrix
from analysis.aimon_canonical_dataset import export_aimon_canonical_dataset
import pandas as pd
import zipfile


def _write_npy(archive: zipfile.ZipFile, name: str, array: np.ndarray) -> None:
    import io

    buffer = io.BytesIO()
    np.save(buffer, array)
    archive.writestr(name, buffer.getvalue())


def _build_small_aimon_dataset(dataset_root: Path) -> None:
    goodics = pd.DataFrame(
        [
            {
                "expID": "B350",
                "WalkRegressor": r"Z:\\B350Walk.npy",
                "ForcedWalkRegressor": r"Z:\\B350Forced.npy",
                "TSlowlimWalk": 21.0,
                "TShighlimWalk": 30.0,
                "TSlowlimForced": 41.0,
                "TShighlimForced": 50.0,
            }
        ]
    )
    goodics.to_pickle(dataset_root / "GoodICsdf.pkl")
    region = np.zeros((2, 60), dtype=np.float32)
    region[:, 20:30] = np.asarray([[1.0], [2.0]], dtype=np.float32)
    region[:, 40:50] = np.asarray([[3.0], [4.0]], dtype=np.float32)
    with zipfile.ZipFile(dataset_root / "Walk_anatomical_regions.zip", "w") as archive:
        _write_npy(archive, "Walk_anatomical_regions/B350_Regions.npy", region)
    with zipfile.ZipFile(dataset_root / "Additional_data.zip", "w") as archive:
        _write_npy(archive, "Additional_data/AllRegressors/B350Walk.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))
        _write_npy(archive, "Additional_data/AllRegressors/B350Forced.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))


def test_score_aimon_trial_matrix_identity(tmp_path: Path) -> None:
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir(parents=True)
    _build_small_aimon_dataset(dataset_root)
    derived_root = tmp_path / "derived"
    export_aimon_canonical_dataset(dataset_root, output_dir=derived_root)

    trials = load_aimon_canonical_trial_data(derived_root / "aimon2023_canonical_bundle.json")
    assert len(trials) == 2
    score = score_aimon_trial_matrix(trials[0], trials[0].matrix.copy(), simulated_timebase_s=trials[0].timebase_s.copy())
    assert score["aggregate"]["mean_rmse"] == 0.0
    assert score["aggregate"]["mean_abs_error"] == 0.0
    assert score["aggregate"]["mean_sign_agreement"] == 1.0


def test_score_aimon_trial_matrix_ignores_nan_samples(tmp_path: Path) -> None:
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir(parents=True)
    _build_small_aimon_dataset(dataset_root)
    derived_root = tmp_path / "derived"
    export_aimon_canonical_dataset(dataset_root, output_dir=derived_root)

    trials = load_aimon_canonical_trial_data(derived_root / "aimon2023_canonical_bundle.json")
    observed = trials[0]
    simulated = observed.matrix.copy()
    simulated[:, 0] = np.nan
    score = score_aimon_trial_matrix(observed, simulated, simulated_timebase_s=observed.timebase_s.copy())
    assert score["aggregate"]["mean_rmse"] == 0.0
    assert score["aggregate"]["mean_abs_error"] == 0.0

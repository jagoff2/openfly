from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.aimon_canonical_dataset import export_aimon_canonical_dataset


def _write_npy(archive: zipfile.ZipFile, name: str, array: np.ndarray) -> None:
    buffer = io.BytesIO()
    np.save(buffer, array)
    archive.writestr(name, buffer.getvalue())


def test_export_aimon_canonical_dataset_writes_bundle(tmp_path: Path) -> None:
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir(parents=True)
    goodics = pd.DataFrame(
        [
            {
                "expID": "B350",
                "WalkRegressor": r"Z:\\B350_1to3000Walkkd.npy",
                "ForcedWalkRegressor": r"Z:\\B350ForcedBin3650_3900kd.npy",
                "TSlowlimWalk": 21.0,
                "TShighlimWalk": 30.0,
                "TSlowlimForced": 41.0,
                "TShighlimForced": 50.0,
            }
        ]
    )
    goodics.to_pickle(dataset_root / "GoodICsdf.pkl")

    region = np.zeros((3, 60), dtype=np.float32)
    region[:, 20:30] = np.asarray([[1.0], [2.0], [3.0]], dtype=np.float32)
    region[:, 40:50] = np.asarray([[4.0], [5.0], [6.0]], dtype=np.float32)

    with zipfile.ZipFile(dataset_root / "Walk_anatomical_regions.zip", "w") as archive:
        _write_npy(archive, "Walk_anatomical_regions/B350_Regions.npy", region)
        _write_npy(archive, "Walk_anatomical_regions/B350_Walk.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))

    with zipfile.ZipFile(dataset_root / "Additional_data.zip", "w") as archive:
        _write_npy(archive, "Additional_data/AllRegressors/B350_1to3000Walkkd.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))
        _write_npy(archive, "Additional_data/AllRegressors/B350ForcedBin3650_3900kd.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))

    output_dir = tmp_path / "derived"
    summary = export_aimon_canonical_dataset(dataset_root, output_dir=output_dir, sampling_rate_hz=50.0)

    assert summary["exported_experiment_count"] == 1
    assert summary["trial_count"] == 2
    bundle = json.loads((output_dir / "aimon2023_canonical_bundle.json").read_text(encoding="utf-8"))
    assert bundle["dataset_key"] == "aimon2023_dryad"
    assert len(bundle["trials"]) == 2
    first_trial = bundle["trials"][0]
    assert first_trial["behavior_context"] == "spontaneous_walk"
    assert len(first_trial["traces"]) == 3
    assert first_trial["traces"][0]["trace_index"] == 0
    assert (output_dir / "B350" / "spontaneous_walk_matrix.npy").exists()
    assert (output_dir / "B350" / "forced_walk_matrix.npy").exists()
    spont_regressor = np.asarray(np.load(output_dir / "B350" / "spontaneous_walk_regressor.npy"), dtype=np.float32)
    forced_regressor = np.asarray(np.load(output_dir / "B350" / "forced_walk_regressor.npy"), dtype=np.float32)
    assert spont_regressor.shape == (10,)
    assert forced_regressor.shape == (10,)


def test_export_aimon_canonical_dataset_max_experiments_counts_survivors(tmp_path: Path) -> None:
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir(parents=True)
    goodics = pd.DataFrame(
        [
            {
                "expID": "B1037",
                "WalkRegressor": r"Z:\\B1037Walk.npy",
                "ForcedWalkRegressor": r"Z:\\B1037Forced.npy",
                "TSlowlimWalk": 10.0,
                "TShighlimWalk": 20.0,
                "TSlowlimForced": 15.0,
                "TShighlimForced": 25.0,
            },
            {
                "expID": "B350",
                "WalkRegressor": r"Z:\\B350Walk.npy",
                "ForcedWalkRegressor": r"Z:\\B350Forced.npy",
                "TSlowlimWalk": 21.0,
                "TShighlimWalk": 30.0,
                "TSlowlimForced": 41.0,
                "TShighlimForced": 50.0,
            },
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

    output_dir = tmp_path / "derived"
    summary = export_aimon_canonical_dataset(dataset_root, output_dir=output_dir, max_experiments=1)

    assert summary["exported_experiment_count"] == 1
    assert summary["trial_count"] == 2
    assert summary["exported_rows"][0]["exp_id"] == "B350"

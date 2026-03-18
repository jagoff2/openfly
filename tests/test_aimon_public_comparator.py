from __future__ import annotations

import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.aimon_public_comparator import summarize_public_forced_vs_spontaneous_walk


def _write_npy(archive: zipfile.ZipFile, name: str, array: np.ndarray) -> None:
    buffer = io.BytesIO()
    np.save(buffer, array)
    archive.writestr(name, buffer.getvalue())


def test_public_forced_vs_spontaneous_walk_blocks_when_required_files_are_missing(tmp_path: Path) -> None:
    summary = summarize_public_forced_vs_spontaneous_walk(tmp_path)
    assert summary["status"] == "blocked_missing_files"
    assert "GoodICsdf.pkl" in summary["missing_files"]
    assert "Additional_data.zip" in summary["missing_files"]


def test_public_forced_vs_spontaneous_walk_computes_region_level_similarity(tmp_path: Path) -> None:
    dataset_root = tmp_path
    goodics = pd.DataFrame(
        [
            {
                "expID": "B350",
                "WalkRegressor": r"Z:\B350_1to3000Walkkd.mat",
                "ForcedWalkRegressor": r"Z:\B350ForcedBin3650_3900kd.mat",
                "TSlowlimWalk": 21.0,
                "TShighlimWalk": 30.0,
                "TSlowlimForced": 41.0,
                "TShighlimForced": 50.0,
            },
            {
                "expID": "B351",
                "WalkRegressor": r"Z:\B351_1to3000Walkkd.mat",
                "ForcedWalkRegressor": r"Z:\B351ForcedBin3650_3900kd.mat",
                "TSlowlimWalk": 21.0,
                "TShighlimWalk": 30.0,
                "TSlowlimForced": 41.0,
                "TShighlimForced": 50.0,
            },
        ]
    )
    goodics.to_pickle(dataset_root / "GoodICsdf.pkl")

    region_a = np.zeros((3, 60), dtype=np.float32)
    region_a[:, 10:20] = np.asarray([[1.0], [0.8], [0.0]], dtype=np.float32)
    region_a[:, 20:30] = np.asarray([[2.0], [4.0], [6.0]], dtype=np.float32)
    region_a[:, 40:50] = np.asarray([[2.2], [3.9], [6.1]], dtype=np.float32)

    region_b = np.zeros((3, 60), dtype=np.float32)
    region_b[:, 10:20] = np.asarray([[0.5], [1.0], [0.0]], dtype=np.float32)
    region_b[:, 20:30] = np.asarray([[1.0], [2.5], [4.0]], dtype=np.float32)
    region_b[:, 40:50] = np.asarray([[1.1], [2.6], [3.8]], dtype=np.float32)

    with zipfile.ZipFile(dataset_root / "Walk_anatomical_regions.zip", "w") as archive:
        _write_npy(archive, "Walk_anatomical_regions/B350_Regions.npy", region_a)
        _write_npy(archive, "Walk_anatomical_regions/B350_Walk.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))
        _write_npy(archive, "Walk_anatomical_regions/B351_Regions.npy", region_b)
        _write_npy(archive, "Walk_anatomical_regions/B351_Walk.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))

    with zipfile.ZipFile(dataset_root / "Additional_data.zip", "w") as archive:
        _write_npy(archive, "Additional_data/AllRegressors/B350_1to3000Walkkd.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))
        _write_npy(archive, "Additional_data/AllRegressors/B350ForcedBin3650_3900kd.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))
        _write_npy(archive, "Additional_data/AllRegressors/B351_1to3000Walkkd.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))
        _write_npy(archive, "Additional_data/AllRegressors/B351ForcedBin3650_3900kd.npy", np.linspace(0.0, 1.0, 60, dtype=np.float32))

    summary = summarize_public_forced_vs_spontaneous_walk(dataset_root)
    assert summary["status"] == "ok"
    assert summary["n_candidate_rows"] == 2
    assert summary["n_experiments_used"] == 2
    assert summary["median_steady_walk_vector_corr"] > 0.95
    assert summary["median_steady_walk_rank_corr"] > 0.95
    assert summary["n_valid_vector_corr"] == 2
    assert summary["n_valid_rank_corr"] == 2
    assert summary["dropped_experiments"] == []


def test_public_forced_vs_spontaneous_walk_uses_windowed_regions_without_complete_regressor_metadata(
    tmp_path: Path,
) -> None:
    dataset_root = tmp_path
    goodics = pd.DataFrame(
        [
            {
                "expID": "B350",
                "WalkRegressor": np.nan,
                "ForcedWalkRegressor": np.nan,
                "TSlowlimWalk": 6.0,
                "TShighlimWalk": 15.0,
                "TSlowlimForced": 31.0,
                "TShighlimForced": 40.0,
            }
        ]
    )
    goodics.to_pickle(dataset_root / "GoodICsdf.pkl")

    region = np.zeros((3, 50), dtype=np.float32)
    region[:, 5:15] = np.asarray([[1.0], [2.0], [3.0]], dtype=np.float32)
    region[:, 30:40] = np.asarray([[1.1], [2.1], [3.2]], dtype=np.float32)

    with zipfile.ZipFile(dataset_root / "Walk_anatomical_regions.zip", "w") as archive:
        _write_npy(archive, "Walk_anatomical_regions/B350_Regions.npy", region)
        _write_npy(archive, "Walk_anatomical_regions/B350_Walk.npy", np.linspace(0.0, 1.0, 50, dtype=np.float32))

    with zipfile.ZipFile(dataset_root / "Additional_data.zip", "w") as archive:
        archive.writestr("Additional_data/placeholder.txt", "placeholder")

    summary = summarize_public_forced_vs_spontaneous_walk(dataset_root)
    assert summary["status"] == "partial_low_match_count"
    assert summary["n_candidate_rows"] == 1
    assert summary["n_experiments_used"] == 1
    assert summary["per_experiment_rows"][0]["spontaneous_walk_regressor_member"] == "Walk_anatomical_regions/B350_Walk.npy"
    assert summary["per_experiment_rows"][0]["forced_walk_regressor_member"] is None
    assert summary["per_experiment_rows"][0]["steady_walk_vector_corr"] > 0.99


def test_public_forced_vs_spontaneous_walk_drops_overlapping_windows(tmp_path: Path) -> None:
    dataset_root = tmp_path
    goodics = pd.DataFrame(
        [
            {
                "expID": "B350",
                "WalkRegressor": np.nan,
                "ForcedWalkRegressor": np.nan,
                "TSlowlimWalk": 6.0,
                "TShighlimWalk": 20.0,
                "TSlowlimForced": 10.0,
                "TShighlimForced": 24.0,
            }
        ]
    )
    goodics.to_pickle(dataset_root / "GoodICsdf.pkl")

    region = np.zeros((3, 40), dtype=np.float32)
    region[:, 5:24] = np.asarray([[1.0], [2.0], [3.0]], dtype=np.float32)

    with zipfile.ZipFile(dataset_root / "Walk_anatomical_regions.zip", "w") as archive:
        _write_npy(archive, "Walk_anatomical_regions/B350_Regions.npy", region)
        _write_npy(archive, "Walk_anatomical_regions/B350_Walk.npy", np.linspace(0.0, 1.0, 40, dtype=np.float32))

    with zipfile.ZipFile(dataset_root / "Additional_data.zip", "w") as archive:
        archive.writestr("Additional_data/placeholder.txt", "placeholder")

    summary = summarize_public_forced_vs_spontaneous_walk(dataset_root)
    assert summary["status"] == "blocked_no_matches"
    assert summary["n_candidate_rows"] == 1
    assert summary["n_experiments_used"] == 0
    assert summary["dropped_experiments"][0]["reason"] == "overlapping_walk_forced_windows"


def test_public_forced_vs_spontaneous_walk_uses_additional_functional_regions_and_masks_nans(
    tmp_path: Path,
) -> None:
    dataset_root = tmp_path
    goodics = pd.DataFrame(
        [
            {
                "expID": "B1037",
                "WalkRegressor": r"Z:\B1037Walk1_950kd.mat",
                "ForcedWalkRegressor": np.nan,
                "TSlowlimWalk": 1.0,
                "TShighlimWalk": 4.0,
                "TSlowlimForced": 5.0,
                "TShighlimForced": 8.0,
            },
            {
                "expID": "B350",
                "WalkRegressor": r"Z:\B350_1to3000Walkkd.mat",
                "ForcedWalkRegressor": r"Z:\B350ForcedBin3650_3900kd.mat",
                "TSlowlimWalk": 1.0,
                "TShighlimWalk": 4.0,
                "TSlowlimForced": 5.0,
                "TShighlimForced": 8.0,
            },
            {
                "expID": "B378",
                "WalkRegressor": np.nan,
                "ForcedWalkRegressor": r"Z:\B378_1_1700Forcedkd.mat",
                "TSlowlimWalk": 1.0,
                "TShighlimWalk": 8.0,
                "TSlowlimForced": 1.0,
                "TShighlimForced": 8.0,
            },
        ]
    )
    goodics.to_pickle(dataset_root / "GoodICsdf.pkl")

    functional_b1037 = np.asarray(
        [
            [1.0, 1.0, 1.0, 1.0, 3.0, 3.0, 3.0, 3.0],
            [2.0, 2.0, 2.0, 2.0, 5.0, 5.0, 5.0, 5.0],
            [3.0, 3.0, 3.0, 3.0, 7.0, 7.0, 7.0, 7.0],
        ],
        dtype=np.float32,
    )
    functional_b350 = np.asarray(
        [
            [1.0, 1.0, np.nan, 1.0, 2.0, 2.0, np.nan, 2.0],
            [2.0, 2.0, 2.0, 2.0, 4.0, 4.0, 4.0, 4.0],
            [3.0, 3.0, 3.0, 3.0, 6.0, 6.0, 6.0, 6.0],
        ],
        dtype=np.float32,
    )
    functional_b378 = np.asarray(
        [
            [1.0] * 8,
            [2.0] * 8,
            [3.0] * 8,
        ],
        dtype=np.float32,
    )

    with zipfile.ZipFile(dataset_root / "Additional_data.zip", "w") as archive:
        for name, array in [
            ("Additional_data/FunctionallyDefinedAnatomicalRegions/B1037_150FuncRegionsTS.mat", functional_b1037),
            ("Additional_data/FunctionallyDefinedAnatomicalRegions/B350_150FuncRegionsTS.mat", functional_b350),
            ("Additional_data/FunctionallyDefinedAnatomicalRegions/B378_150FuncRegionsTS.mat", functional_b378),
        ]:
            buffer = io.BytesIO()
            from scipy.io import savemat  # type: ignore

            savemat(buffer, {"TS": array})
            archive.writestr(name, buffer.getvalue())
        _write_npy(archive, "Additional_data/AllRegressors/B1037Walk1_950kd.npy", np.linspace(0.0, 1.0, 8, dtype=np.float32))
        _write_npy(archive, "Additional_data/AllRegressors/B350_1to3000Walkkd.npy", np.linspace(0.0, 1.0, 8, dtype=np.float32))
        _write_npy(archive, "Additional_data/AllRegressors/B350ForcedBin3650_3900kd.npy", np.linspace(0.0, 1.0, 8, dtype=np.float32))
        _write_npy(archive, "Additional_data/AllRegressors/B378_1_1700Forcedkd.npy", np.linspace(0.0, 1.0, 8, dtype=np.float32))

    summary = summarize_public_forced_vs_spontaneous_walk(dataset_root)
    assert summary["status"] == "ok"
    assert summary["n_candidate_rows"] == 3
    assert summary["n_experiments_used"] == 2
    assert summary["median_steady_walk_vector_corr"] > 0.99
    assert summary["median_steady_walk_rank_corr"] > 0.99
    dropped = {row["exp_id"]: row["reason"] for row in summary["dropped_experiments"]}
    assert dropped["B378"] == "overlapping_walk_forced_windows"
    used = {row["exp_id"]: row for row in summary["per_experiment_rows"]}
    assert used["B1037"]["region_member"].endswith("B1037_150FuncRegionsTS.mat")
    assert used["B1037"]["forced_walk_regressor_member"] is None
    assert used["B350"]["valid_vector_region_count"] == 3
    assert summary["n_valid_vector_corr"] == 2
    assert summary["n_valid_prelead_fraction"] == 0

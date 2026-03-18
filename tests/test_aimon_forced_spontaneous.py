from __future__ import annotations

import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio

from analysis.aimon_forced_spontaneous import compute_aimon_forced_spontaneous_comparator


def _write_npy_to_zip(archive: zipfile.ZipFile, name: str, array: np.ndarray) -> None:
    buffer = io.BytesIO()
    np.save(buffer, array)
    archive.writestr(name, buffer.getvalue())


def _write_mat_to_zip(archive: zipfile.ZipFile, name: str, payload: dict[str, np.ndarray]) -> None:
    buffer = io.BytesIO()
    sio.savemat(buffer, payload)
    archive.writestr(name, buffer.getvalue())


def test_compute_aimon_forced_spontaneous_comparator_matches_same_line_indicator_frame(tmp_path: Path) -> None:
    walk_zip = tmp_path / "Walk_anatomical_regions.zip"
    additional_zip = tmp_path / "Additional_data.zip"
    goodics_path = tmp_path / "GoodICsdf.pkl"

    spontaneous_regions = np.vstack(
        [
            np.linspace(0.0, 1.0, 10, dtype=np.float32),
            np.linspace(1.0, 0.0, 10, dtype=np.float32),
            np.zeros(10, dtype=np.float32),
        ]
    )
    spontaneous_walk = np.linspace(0.0, 1.0, 10, dtype=np.float32).reshape(-1, 1)
    forced_regions = spontaneous_regions.copy()
    forced_walk = spontaneous_walk.copy()

    with zipfile.ZipFile(walk_zip, mode="w") as archive:
        _write_npy_to_zip(
            archive,
            "Walk_anatomical_regions/TestLine_6s_10_B100_Regions.npy",
            spontaneous_regions,
        )
        _write_npy_to_zip(
            archive,
            "Walk_anatomical_regions/TestLine_6s_10_B100_Walk.npy",
            spontaneous_walk,
        )

    with zipfile.ZipFile(additional_zip, mode="w") as archive:
        _write_npy_to_zip(
            archive,
            "Additional_data/AdditionalRegionalTimeSeries/TestLine_6s_10_B200_Regions.npy",
            forced_regions,
        )
        _write_mat_to_zip(
            archive,
            "Additional_data/AllRegressors/B100Walkkd.mat",
            {"Rkd": spontaneous_walk},
        )
        _write_mat_to_zip(
            archive,
            "Additional_data/AllRegressors/B200Forcedkd.mat",
            {"Rkd": forced_walk},
        )

    pd.DataFrame(
        {
            "expID": ["B100", "B200"],
            "GAL4": ["TestLine", "TestLine"],
            "UAS": ["6s", "6s"],
            "FR": [10.0, 10.0],
            "WalkSubstrate": ["Straight", "RotRod"],
            "WalkRegressor": ["B100Walkkd.mat", ""],
            "ForcedWalkRegressor": ["", "B200Forcedkd.mat"],
            "ForcedTurnRegressor": ["", ""],
            "TSlowlimWalk": ["", ""],
            "TShighlimWalk": ["", ""],
            "TSlowlimForced": ["", ""],
            "TShighlimForced": ["", ""],
        }
    ).to_pickle(goodics_path)

    summary, table = compute_aimon_forced_spontaneous_comparator(
        goodics_path=goodics_path,
        walk_archive_path=walk_zip,
        additional_archive_path=additional_zip,
    )

    assert summary["status"] == "ok"
    assert summary["comparator_count"] == 1
    assert summary["valid_similarity_count"] == 1
    assert table.loc[0, "match_tier"] == "same_line_indicator_frame"
    assert table.loc[0, "matched_spontaneous_count"] == 1
    assert float(table.loc[0, "region_profile_corr"]) > 0.99

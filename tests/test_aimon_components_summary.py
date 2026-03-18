from __future__ import annotations

import io
import zipfile
from pathlib import Path

import numpy as np

from analysis.aimon_components_summary import summarize_walk_components_zip
from analysis.aimon_public_comparator import index_aimon_archive_members


def _write_npy(archive: zipfile.ZipFile, name: str, array: np.ndarray) -> None:
    buffer = io.BytesIO()
    np.save(buffer, array)
    archive.writestr(name, buffer.getvalue())


def test_summarize_walk_components_zip_counts_experiments_and_shapes(tmp_path: Path) -> None:
    archive_path = tmp_path / "Walk_components.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        _write_npy(archive, "Walk_components/ExpA_Components.npy", np.zeros((5, 100), dtype=np.float64))
        _write_npy(archive, "Walk_components/ExpA_Walk.npy", np.zeros((100, 1), dtype=np.float64))
        _write_npy(archive, "Walk_components/ExpA_Left.npy", np.zeros((100, 1), dtype=np.float64))
        _write_npy(archive, "Walk_components/ExpA_Right.npy", np.zeros((100, 1), dtype=np.float64))
        _write_npy(archive, "Walk_components/ExpB_Components.npy", np.zeros((7, 80), dtype=np.float64))
        _write_npy(archive, "Walk_components/ExpB_Walk.npy", np.zeros((80, 1), dtype=np.float64))

    summary = summarize_walk_components_zip(archive_path)
    assert summary["npy_file_count"] == 6
    assert summary["experiment_count"] == 2
    assert summary["kind_counts"]["Components"] == 2
    assert summary["kind_counts"]["Walk"] == 2
    assert summary["kind_counts"]["Left"] == 1
    assert summary["kind_counts"]["Right"] == 1
    assert summary["all_four_count"] == 1
    assert summary["components_only_walk_count"] == 1
    assert summary["component_count_min"] == 5
    assert summary["component_count_max"] == 7
    assert summary["frame_count_min"] == 80
    assert summary["frame_count_max"] == 100


def test_index_aimon_archive_members_extracts_exp_id_and_region_kind(tmp_path: Path) -> None:
    archive_path = tmp_path / "Walk_anatomical_regions.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        _write_npy(archive, "Walk_anatomical_regions/B350_Regions.npy", np.zeros((3, 20), dtype=np.float64))
        _write_npy(archive, "Walk_anatomical_regions/B350_Walk.npy", np.zeros((20,), dtype=np.float64))
        _write_npy(archive, "Walk_anatomical_regions/B351_LargeRegions.npy", np.zeros((2, 20), dtype=np.float64))

    index_table = index_aimon_archive_members(archive_path)
    assert len(index_table) == 3
    assert set(index_table["exp_id"]) == {"B350", "B351"}
    assert set(index_table["region_kind"]) == {"Regions", "Walk", "LargeRegions"}

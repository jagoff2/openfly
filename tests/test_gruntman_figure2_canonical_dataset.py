from __future__ import annotations

import io
import json
import tempfile
import zipfile
from pathlib import Path

import h5py
import numpy as np

from analysis.gruntman_figure2_canonical_dataset import (
    GRUNTMAN_FIGURE2_TRACE_LEN,
    export_gruntman_figure2_canonical_dataset,
)


def _build_gruntman_mat(path: Path) -> None:
    with h5py.File(path, "w") as handle:
        outer = handle.create_dataset("alignedSingleBarPerCell", shape=(2, 2, 3, 2), dtype=h5py.ref_dtype)
        handle.create_dataset("posCellSD", shape=(3, 13), dtype=h5py.ref_dtype)
        missing = handle.create_dataset("missing_trace", data=np.zeros((2,), dtype=np.uint64))
        for cell_index in range(2):
            for duration_index in range(2):
                for position_index in range(3):
                    for width_index in range(2):
                        if duration_index == 0 and position_index == 1 and width_index == 0:
                            trace = np.full((1, GRUNTMAN_FIGURE2_TRACE_LEN), cell_index + 1.0, dtype=np.float32)
                            dataset = handle.create_dataset(
                                f"trace_{cell_index}_{duration_index}_{position_index}_{width_index}",
                                data=trace,
                            )
                            outer[cell_index, duration_index, position_index, width_index] = dataset.ref
                        else:
                            outer[cell_index, duration_index, position_index, width_index] = missing.ref


def test_export_gruntman_figure2_canonical_dataset_writes_bundle(tmp_path: Path) -> None:
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        mat_path = Path(tmp_dir) / "sourceDataPlottingFig2.mat"
        _build_gruntman_mat(mat_path)
        with zipfile.ZipFile(dataset_root / "figure2DataAndCode.zip", "w") as archive:
            archive.write(mat_path, arcname="sourceDataPlottingFig2.mat")
            archive.writestr("README.txt", "synthetic test archive")

    output_dir = tmp_path / "derived"
    summary = export_gruntman_figure2_canonical_dataset(dataset_root, output_dir=output_dir)

    assert summary["trial_count"] == 1
    bundle = json.loads((output_dir / "gruntman2019_figure2_canonical_bundle.json").read_text(encoding="utf-8"))
    assert bundle["dataset_key"] == "gruntman2019_janelia_figure2"
    assert len(bundle["trials"]) == 1
    trial = bundle["trials"][0]
    assert trial["stimulus"]["parameters"]["duration_index_h5"] == 0
    assert trial["stimulus"]["parameters"]["position_index_h5"] == 1
    assert trial["stimulus"]["parameters"]["width_index_h5"] == 0
    assert len(trial["traces"]) == 2
    assert (output_dir / f"{trial['trial_id']}_matrix.npy").exists()

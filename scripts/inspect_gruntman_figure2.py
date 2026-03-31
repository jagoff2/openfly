from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

import h5py
import numpy as np


def main() -> None:
    zip_path = Path("external/neural_measurements/gruntman2019_janelia/figure2DataAndCode.zip")
    with zipfile.ZipFile(zip_path) as archive:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mat_path = Path(tmp_dir) / "sourceDataPlottingFig2.mat"
            mat_path.write_bytes(archive.read("sourceDataPlottingFig2.mat"))
            with h5py.File(mat_path, "r") as handle:
                outer = handle["alignedSingleBarPerCell"]
                first_ref = outer[0, 0, 0, 0]
                first_dataset = handle[first_ref]
                first_inner_refs = np.array(first_dataset).flatten().tolist()
                first_inner = []
                for raw_ref in first_inner_refs:
                    inner_dataset = handle[raw_ref]
                    first_inner.append(
                        {
                            "shape": list(inner_dataset.shape),
                            "dtype": str(inner_dataset.dtype),
                            "preview": np.asarray(inner_dataset).reshape(-1)[:10].tolist(),
                        }
                    )
                summary = {
                    "keys": sorted(handle.keys()),
                    "alignedSingleBarPerCell_shape": list(outer.shape),
                    "alignedSingleBarPerCell_dtype": str(outer.dtype),
                    "posCellSD_shape": list(handle["posCellSD"].shape),
                    "posCellSD_dtype": str(handle["posCellSD"].dtype),
                    "first_cell_dataset_shape": list(first_dataset.shape),
                    "first_cell_dataset_dtype": str(first_dataset.dtype),
                    "first_cell_inner": first_inner,
                }
                print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

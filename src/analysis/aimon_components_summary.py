from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path
from typing import Any

import numpy as np


def summarize_walk_components_zip(path: str | Path) -> dict[str, Any]:
    archive_path = Path(path)
    with zipfile.ZipFile(archive_path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".npy")]
        experiments: dict[str, set[str]] = {}
        component_counts: list[int] = []
        frame_counts: list[int] = []
        for name in names:
            stem = Path(name).stem
            match = re.match(r"(.+?)_(Components|Walk|Left|Right)$", stem)
            if not match:
                continue
            experiment_key = str(match.group(1))
            kind = str(match.group(2))
            experiments.setdefault(experiment_key, set()).add(kind)
            if kind == "Components":
                array = np.load(io.BytesIO(archive.read(name)), allow_pickle=True)
                if getattr(array, "ndim", 0) == 2:
                    component_counts.append(int(array.shape[0]))
                    frame_counts.append(int(array.shape[1]))
        component_summary = {
            "component_file_count": int(len(component_counts)),
            "component_count_min": int(min(component_counts)) if component_counts else None,
            "component_count_median": float(np.median(component_counts)) if component_counts else None,
            "component_count_max": int(max(component_counts)) if component_counts else None,
            "frame_count_min": int(min(frame_counts)) if frame_counts else None,
            "frame_count_median": float(np.median(frame_counts)) if frame_counts else None,
            "frame_count_max": int(max(frame_counts)) if frame_counts else None,
        }
        kind_counts = {
            "Components": int(sum(1 for kinds in experiments.values() if "Components" in kinds)),
            "Walk": int(sum(1 for kinds in experiments.values() if "Walk" in kinds)),
            "Left": int(sum(1 for kinds in experiments.values() if "Left" in kinds)),
            "Right": int(sum(1 for kinds in experiments.values() if "Right" in kinds)),
        }
        complete = sorted(
            experiment
            for experiment, kinds in experiments.items()
            if {"Components", "Walk", "Left", "Right"}.issubset(kinds)
        )
        components_plus_walk_only = sorted(
            experiment
            for experiment, kinds in experiments.items()
            if "Components" in kinds and "Walk" in kinds and not ({"Left", "Right"} & kinds)
        )
        return {
            "archive_path": str(archive_path),
            "npy_file_count": int(len(names)),
            "experiment_count": int(len(experiments)),
            "kind_counts": kind_counts,
            "all_four_count": int(len(complete)),
            "components_only_walk_count": int(len(components_plus_walk_only)),
            "example_complete_experiments": complete[:10],
            **component_summary,
        }

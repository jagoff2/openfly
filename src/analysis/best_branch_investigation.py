from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from visualization.activation_viz import select_active_indices


def pearson_correlation(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float32).reshape(-1)
    b = np.asarray(b, dtype=np.float32).reshape(-1)
    if a.size != b.size or a.size == 0:
        raise ValueError("correlation inputs must be non-empty and have the same length")
    if float(np.std(a)) < 1e-8 or float(np.std(b)) < 1e-8:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def align_framewise_matrix(matrix: np.ndarray, frame_cycles: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix)
    frame_cycles = np.asarray(frame_cycles, dtype=np.int64).reshape(-1)
    if matrix.ndim != 2:
        raise ValueError("matrix must be 2D")
    if matrix.shape[1] == frame_cycles.size:
        return matrix
    if matrix.shape[1] <= int(frame_cycles.max(initial=-1)):
        raise ValueError("frame cycle indices exceed matrix width")
    return matrix[:, frame_cycles]


def compute_selected_frame_counts(
    voltage_frames: np.ndarray,
    spike_frames: np.ndarray | None,
    *,
    max_points: int,
) -> np.ndarray:
    voltage_frames = np.asarray(voltage_frames, dtype=np.float32)
    if voltage_frames.ndim != 2:
        raise ValueError("voltage_frames must be 2D")
    if spike_frames is not None:
        spike_frames = np.asarray(spike_frames)
        if spike_frames.shape != voltage_frames.shape:
            raise ValueError("spike_frames must match voltage_frames shape")
    counts = np.zeros(voltage_frames.shape[1], dtype=np.int32)
    for frame_idx in range(voltage_frames.shape[0]):
        spikes = None if spike_frames is None else spike_frames[frame_idx]
        active_ids = select_active_indices(voltage_frames[frame_idx], spikes=spikes, max_points=max_points)
        counts[active_ids] += 1
    return counts


def load_annotation_table(annotation_path: str | Path) -> pd.DataFrame:
    annotation_path = Path(annotation_path)
    df = pd.read_csv(annotation_path, sep="\t", low_memory=False)
    keep_cols = [
        "root_id",
        "cell_type",
        "hemibrain_type",
        "side",
        "super_class",
        "flow",
        "class",
        "sub_class",
        "group",
        "nt_type",
    ]
    df = df[[column for column in keep_cols if column in df.columns]].copy()
    df = df.dropna(subset=["root_id"])
    df["root_id"] = df["root_id"].astype("int64")
    df = df.drop_duplicates("root_id")
    family = (
        df.get("cell_type", pd.Series(index=df.index, dtype=object))
        .fillna(df.get("hemibrain_type", pd.Series(index=df.index, dtype=object)))
        .fillna(df.get("group", pd.Series(index=df.index, dtype=object)))
        .fillna("UNKNOWN")
    )
    df["family"] = family.astype(str)
    return df


def build_unsampled_unit_table(
    *,
    root_ids: np.ndarray,
    xy: np.ndarray,
    extent: tuple[float, float, float, float],
    selected_counts: np.ndarray,
    spike_counts: np.ndarray,
    mean_voltage: np.ndarray,
    max_voltage: np.ndarray,
    annotation_df: pd.DataFrame,
    sampled_overlay_root_ids: Iterable[int],
) -> pd.DataFrame:
    root_ids = np.asarray(root_ids, dtype=np.int64).reshape(-1)
    xy = np.asarray(xy, dtype=np.float32)
    sampled_overlay_root_ids = {int(root_id) for root_id in sampled_overlay_root_ids}
    x_min, x_max, y_min, y_max = [float(value) for value in extent]
    unit_df = pd.DataFrame(
        {
            "root_id": root_ids,
            "x": xy[:, 0],
            "y": xy[:, 1],
            "selected_frames": np.asarray(selected_counts, dtype=np.int32),
            "spike_frames": np.asarray(spike_counts, dtype=np.int32),
            "mean_voltage": np.asarray(mean_voltage, dtype=np.float32),
            "max_voltage": np.asarray(max_voltage, dtype=np.float32),
            "sampled_overlay": [int(root_id) in sampled_overlay_root_ids for root_id in root_ids],
        }
    )
    unit_df["x_norm"] = (unit_df["x"] - x_min) / max(x_max - x_min, 1e-6)
    unit_df["y_norm"] = (unit_df["y"] - y_min) / max(y_max - y_min, 1e-6)
    unit_df["dist_to_visual_center"] = np.sqrt((unit_df["x_norm"] - 0.5) ** 2 + (unit_df["y_norm"] - 0.5) ** 2)
    merged = unit_df.merge(annotation_df, on="root_id", how="left")
    merged["family"] = merged["family"].fillna("UNKNOWN")
    return merged

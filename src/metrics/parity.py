from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def compute_parity_metrics(trajectory: np.ndarray, timestep: float) -> dict[str, float]:
    if trajectory.shape[0] < 2:
        return {
            "sim_seconds": 0.0,
            "avg_forward_speed": 0.0,
            "trajectory_smoothness": 0.0,
            "path_length": 0.0,
            "net_displacement": 0.0,
            "displacement_efficiency": 0.0,
            "bbox_width": 0.0,
            "bbox_height": 0.0,
            "bbox_area": 0.0,
            "stable": 1.0,
        }
    deltas = np.diff(trajectory, axis=0)
    speeds = np.linalg.norm(deltas, axis=1) / timestep
    accel = np.diff(speeds) if len(speeds) > 1 else np.array([0.0])
    path_length = float(np.linalg.norm(deltas, axis=1).sum())
    net_displacement = float(np.linalg.norm(trajectory[-1] - trajectory[0]))
    bbox_width = float(np.max(trajectory[:, 0]) - np.min(trajectory[:, 0]))
    bbox_height = float(np.max(trajectory[:, 1]) - np.min(trajectory[:, 1]))
    return {
        "sim_seconds": float((trajectory.shape[0] - 1) * timestep),
        "avg_forward_speed": float(speeds.mean()),
        "trajectory_smoothness": float(1.0 / (1.0 + np.abs(accel).mean())),
        "path_length": path_length,
        "net_displacement": net_displacement,
        "displacement_efficiency": float(net_displacement / path_length) if path_length > 0.0 else 0.0,
        "bbox_width": bbox_width,
        "bbox_height": bbox_height,
        "bbox_area": float(bbox_width * bbox_height),
        "stable": 1.0,
    }

def write_metrics_csv(path: str | Path, metrics: dict[str, float]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(path, index=False)

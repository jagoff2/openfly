from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


def make_run_dir(output_root: str | Path, prefix: str) -> Path:
    output_root = Path(output_root)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = output_root / f"{prefix}-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

class JsonlLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("w", encoding="utf-8")

    def write(self, record: dict[str, Any]) -> None:
        self._handle.write(json.dumps(record) + "\n")
        self._handle.flush()

    def close(self) -> None:
        self._handle.close()


def save_trajectory_plot(path: str | Path, trajectory: np.ndarray) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    if len(trajectory) > 0:
        ax.plot(trajectory[:, 0], trajectory[:, 1], color="#1f77b4", linewidth=2)
        ax.scatter([trajectory[0, 0]], [trajectory[0, 1]], color="#2ca02c", label="start")
        ax.scatter([trajectory[-1, 0]], [trajectory[-1, 1]], color="#d62728", label="end")
        ax.legend()
    ax.set_title("Trajectory")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.axis("equal")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def save_command_plot(path: str | Path, left: list[float], right: list[float]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(left, label="left_drive")
    ax.plot(right, label="right_drive")
    ax.legend()
    ax.set_title("Descending drive")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def save_video(path: str | Path, frames: list[np.ndarray], fps: int = 24) -> Path | None:
    if not frames:
        return None
    try:
        import imageio.v2 as imageio
    except Exception:
        return None
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        imageio.mimsave(path, frames, fps=fps)
        return path
    except Exception:
        gif_path = path.with_suffix(".gif")
        imageio.mimsave(gif_path, frames, fps=fps)
        return gif_path

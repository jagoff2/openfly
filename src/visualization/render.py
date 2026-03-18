from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import imageio.v3 as iio
import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
import numpy as np


def render_activation_frame(
    demo_frame: np.ndarray,
    *,
    whole_brain_points: np.ndarray | None = None,
    whole_brain_values: np.ndarray | None = None,
    flyvis_left_points: np.ndarray | None = None,
    flyvis_left_values: np.ndarray | None = None,
    flyvis_right_points: np.ndarray | None = None,
    flyvis_right_values: np.ndarray | None = None,
    trace_x: np.ndarray | None = None,
    decoder_traces: Mapping[str, Sequence[float]] | None = None,
    controller_traces: Mapping[str, Sequence[float]] | None = None,
    metadata: Mapping[str, Any] | None = None,
    figure_size: tuple[float, float] = (12.0, 8.0),
    dpi: int = 120,
) -> np.ndarray:
    """Render a multi-panel visualization frame to an RGB array.

    The layout is:
    - demo frame
    - whole-brain point cloud
    - FlyVis left points
    - FlyVis right points
    - decoder/controller traces
    """

    figure = plt.figure(figsize=figure_size, dpi=dpi, constrained_layout=True)
    grid = figure.add_gridspec(
        2,
        3,
        height_ratios=(2.1, 1.35),
        width_ratios=(1.5, 1.0, 1.2),
    )

    ax_demo = figure.add_subplot(grid[0, :2])
    ax_brain = figure.add_subplot(grid[0, 2])
    ax_left = figure.add_subplot(grid[1, 0])
    ax_right = figure.add_subplot(grid[1, 1])
    ax_trace = figure.add_subplot(grid[1, 2])

    meta = dict(metadata or {})
    title = str(meta.pop("title", "Activation frame"))
    figure.suptitle(title, fontsize=14, fontweight="bold")

    _draw_demo_panel(ax_demo, demo_frame, meta)
    _draw_point_panel(
        ax_brain,
        whole_brain_points,
        whole_brain_values,
        title="Whole-brain activity",
        empty_label="No whole-brain points",
        cmap="viridis",
    )
    _draw_point_panel(
        ax_left,
        flyvis_left_points,
        flyvis_left_values,
        title="FlyVis left",
        empty_label="No left points",
        cmap="Blues",
    )
    _draw_point_panel(
        ax_right,
        flyvis_right_points,
        flyvis_right_values,
        title="FlyVis right",
        empty_label="No right points",
        cmap="Oranges",
    )
    _draw_trace_panel(ax_trace, trace_x, decoder_traces, controller_traces)

    return _figure_to_rgb(figure)


def save_activation_frame(
    output_path: str | Path,
    demo_frame: np.ndarray,
    **kwargs: Any,
) -> Path:
    """Render and save one visualization frame."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = render_activation_frame(demo_frame, **kwargs)
    iio.imwrite(output, frame)
    return output


def _draw_demo_panel(
    axis: plt.Axes,
    demo_frame: np.ndarray,
    metadata: Mapping[str, Any],
) -> None:
    image = _coerce_demo_frame(demo_frame)
    axis.imshow(image)
    axis.set_title("Demo frame")
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_aspect("equal")

    if metadata:
        lines = [f"{key}: {value}" for key, value in metadata.items()]
        axis.text(
            0.01,
            0.01,
            "\n".join(lines),
            transform=axis.transAxes,
            ha="left",
            va="bottom",
            fontsize=8,
            color="white",
            bbox={"facecolor": "black", "alpha": 0.55, "pad": 4},
        )


def _draw_point_panel(
    axis: plt.Axes,
    points: np.ndarray | None,
    values: np.ndarray | None,
    *,
    title: str,
    empty_label: str,
    cmap: str,
) -> None:
    axis.set_title(title)

    if points is None or np.asarray(points).size == 0:
        axis.text(0.5, 0.5, empty_label, ha="center", va="center", fontsize=9)
        axis.set_xticks([])
        axis.set_yticks([])
        return

    projected = _coerce_points(points)
    color_values = _resolve_point_values(projected, values)
    scatter = axis.scatter(
        projected[:, 0],
        projected[:, 1],
        c=color_values,
        s=36,
        cmap=cmap,
        alpha=0.9,
        linewidths=0.0,
    )
    if np.ptp(color_values) > 0.0:
        plt.colorbar(scatter, ax=axis, fraction=0.046, pad=0.04)
    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.set_aspect("equal", adjustable="box")
    axis.grid(True, alpha=0.15)


def _draw_trace_panel(
    axis: plt.Axes,
    trace_x: np.ndarray | None,
    decoder_traces: Mapping[str, Sequence[float]] | None,
    controller_traces: Mapping[str, Sequence[float]] | None,
) -> None:
    axis.set_title("Decoder and controller")

    plotted = False
    if decoder_traces:
        for name, values in decoder_traces.items():
            x, y = _coerce_trace(trace_x, values)
            axis.plot(x, y, label=f"dec:{name}", linewidth=2.0)
            plotted = True
    if controller_traces:
        for name, values in controller_traces.items():
            x, y = _coerce_trace(trace_x, values)
            axis.plot(x, y, "--", label=f"ctl:{name}", linewidth=1.8)
            plotted = True

    if not plotted:
        axis.text(0.5, 0.5, "No traces", ha="center", va="center", fontsize=9)
        axis.set_xticks([])
        axis.set_yticks([])
        return

    axis.set_xlabel("time")
    axis.set_ylabel("value")
    axis.grid(True, alpha=0.2)
    axis.legend(loc="best", fontsize=8, frameon=False)


def _coerce_demo_frame(demo_frame: np.ndarray) -> np.ndarray:
    image = np.asarray(demo_frame)
    if image.ndim == 2:
        image = np.repeat(image[:, :, None], 3, axis=2)
    if image.ndim != 3 or image.shape[2] not in (3, 4):
        raise ValueError("demo_frame must have shape (H, W), (H, W, 3), or (H, W, 4)")

    if image.shape[2] == 4:
        image = image[:, :, :3]

    if np.issubdtype(image.dtype, np.floating):
        image = np.clip(image, 0.0, 1.0) * 255.0
    else:
        image = np.clip(image, 0, 255)
    return image.astype(np.uint8, copy=False)


def _coerce_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=float)
    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] < 2:
        raise ValueError("point arrays must have shape (N, 2+) with at least one point")
    return array


def _resolve_point_values(points: np.ndarray, values: np.ndarray | None) -> np.ndarray:
    if values is not None:
        array = np.asarray(values, dtype=float)
        if array.shape != (points.shape[0],):
            raise ValueError("point values must have shape (N,) matching the number of points")
        return array
    if points.shape[1] >= 3:
        return points[:, 2]
    return np.zeros(points.shape[0], dtype=float)


def _coerce_trace(trace_x: np.ndarray | None, values: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    y = np.asarray(values, dtype=float)
    if y.ndim != 1:
        raise ValueError("trace values must be one-dimensional")
    if trace_x is None:
        return np.arange(y.shape[0], dtype=float), y
    x = np.asarray(trace_x, dtype=float)
    if x.shape != y.shape:
        raise ValueError("trace_x must match each trace length")
    return x, y


def _figure_to_rgb(figure: plt.Figure) -> np.ndarray:
    try:
        figure.canvas.draw()
        rgba = np.asarray(figure.canvas.buffer_rgba(), dtype=np.uint8)
        return np.ascontiguousarray(rgba[:, :, :3])
    finally:
        plt.close(figure)

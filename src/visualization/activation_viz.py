from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg


@dataclass(frozen=True)
class BrainLayout:
    root_ids: np.ndarray
    xy: np.ndarray
    background_image: np.ndarray
    background_extent: tuple[float, float, float, float]
    decoder_xy: np.ndarray
    decoder_labels: np.ndarray
    decoder_kinds: np.ndarray


@dataclass(frozen=True)
class FlyVisLayout:
    uv: np.ndarray
    node_types: np.ndarray
    background_image: np.ndarray
    background_extent: tuple[float, float, float, float]


def _brain_projection_table(annotation_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(annotation_path, sep="\t", low_memory=False)
    keep_cols = [
        "root_id",
        "soma_x",
        "soma_y",
        "pos_x",
        "pos_y",
    ]
    df = df[[column for column in keep_cols if column in df.columns]].copy()
    df = df.dropna(subset=["root_id"])
    df["root_id"] = df["root_id"].astype("int64")
    if {"soma_x", "soma_y"}.issubset(df.columns):
        x = df["soma_x"].copy()
        y = df["soma_y"].copy()
    else:
        x = pd.Series(np.nan, index=df.index)
        y = pd.Series(np.nan, index=df.index)
    if {"pos_x", "pos_y"}.issubset(df.columns):
        x = x.fillna(df["pos_x"])
        y = y.fillna(df["pos_y"])
    df["plot_x"] = x
    df["plot_y"] = y
    df = df.dropna(subset=["plot_x", "plot_y"])
    return df[["root_id", "plot_x", "plot_y"]].drop_duplicates("root_id")


def _density_image(
    points_xy: np.ndarray,
    *,
    bins: int = 320,
    padding_fraction: float = 0.05,
) -> tuple[np.ndarray, tuple[float, float, float, float]]:
    if len(points_xy) == 0:
        return np.zeros((bins, bins), dtype=np.float32), (0.0, 1.0, 0.0, 1.0)
    x = np.asarray(points_xy[:, 0], dtype=float)
    y = np.asarray(points_xy[:, 1], dtype=float)
    x_pad = max(1.0, (x.max() - x.min()) * float(padding_fraction))
    y_pad = max(1.0, (y.max() - y.min()) * float(padding_fraction))
    x_min, x_max = float(x.min() - x_pad), float(x.max() + x_pad)
    y_min, y_max = float(y.min() - y_pad), float(y.max() + y_pad)
    hist, x_edges, y_edges = np.histogram2d(x, y, bins=int(bins), range=[[x_min, x_max], [y_min, y_max]])
    image = np.log1p(hist.T).astype(np.float32)
    return image, (float(x_edges[0]), float(x_edges[-1]), float(y_edges[0]), float(y_edges[-1]))


def _coords_for_root_ids(coord_table: pd.DataFrame, root_ids: Sequence[int]) -> np.ndarray:
    coord_map = coord_table.set_index("root_id")[["plot_x", "plot_y"]]
    xy = np.zeros((len(root_ids), 2), dtype=np.float32)
    xy[:] = np.nan
    lookup = coord_map.reindex(pd.Index([int(root_id) for root_id in root_ids], dtype="int64"))
    values = lookup.to_numpy(dtype=np.float32)
    xy[: values.shape[0], :] = values
    if np.isnan(xy).any():
        valid = ~np.isnan(xy).any(axis=1)
        fallback = np.nanmean(xy[valid], axis=0) if np.any(valid) else np.array([0.0, 0.0], dtype=np.float32)
        xy[~valid] = fallback
    return xy


def _decoder_overlay_points(
    coord_table: pd.DataFrame,
    candidate_json: str | Path | None,
    fixed_groups: Mapping[str, Sequence[int]] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows: list[tuple[float, float, str, str]] = []
    coord_lookup = coord_table.set_index("root_id")[["plot_x", "plot_y"]]
    if fixed_groups:
        for label, root_ids in fixed_groups.items():
            root_ids = [int(root_id) for root_id in root_ids]
            points = coord_lookup.reindex(root_ids).dropna()
            if points.empty:
                continue
            xy = points.to_numpy(dtype=float).mean(axis=0)
            rows.append((float(xy[0]), float(xy[1]), str(label), "fixed"))
    if candidate_json:
        payload = json.loads(Path(candidate_json).read_text(encoding="utf-8"))
        for item in payload.get("selected_paired_cell_types", []):
            label = str(item.get("candidate_label") or item.get("cell_type") or "").strip()
            if not label:
                continue
            for side in ("left", "right"):
                root_ids = [int(root_id) for root_id in item.get(f"{side}_root_ids", [])]
                points = coord_lookup.reindex(root_ids).dropna()
                if points.empty:
                    continue
                xy = points.to_numpy(dtype=float).mean(axis=0)
                rows.append((float(xy[0]), float(xy[1]), f"{label}_{side[0].upper()}", "population"))
    if not rows:
        return (
            np.zeros((0, 2), dtype=np.float32),
            np.asarray([], dtype="<U1"),
            np.asarray([], dtype="<U1"),
        )
    decoder_xy = np.asarray([[row[0], row[1]] for row in rows], dtype=np.float32)
    decoder_labels = np.asarray([row[2] for row in rows], dtype="<U64")
    decoder_kinds = np.asarray([row[3] for row in rows], dtype="<U16")
    return decoder_xy, decoder_labels, decoder_kinds


def load_brain_layout(
    *,
    annotation_path: str | Path,
    completeness_path: str | Path,
    candidate_json: str | Path | None,
    fixed_groups: Mapping[str, Sequence[int]] | None = None,
) -> BrainLayout:
    coord_table = _brain_projection_table(annotation_path)
    completeness = pd.read_csv(completeness_path, index_col=0)
    root_ids = completeness.index.to_numpy(dtype=np.int64)
    xy = _coords_for_root_ids(coord_table, root_ids)
    background_image, background_extent = _density_image(xy)
    decoder_xy, decoder_labels, decoder_kinds = _decoder_overlay_points(
        coord_table,
        candidate_json=candidate_json,
        fixed_groups=fixed_groups,
    )
    return BrainLayout(
        root_ids=root_ids,
        xy=xy,
        background_image=background_image,
        background_extent=background_extent,
        decoder_xy=decoder_xy,
        decoder_labels=decoder_labels,
        decoder_kinds=decoder_kinds,
    )


def load_flyvis_layout(node_u: np.ndarray, node_v: np.ndarray, node_types: np.ndarray) -> FlyVisLayout:
    uv = np.column_stack([np.asarray(node_u, dtype=np.float32), np.asarray(node_v, dtype=np.float32)])
    background_image, background_extent = _density_image(uv)
    return FlyVisLayout(
        uv=uv,
        node_types=np.asarray(node_types, dtype="<U64"),
        background_image=background_image,
        background_extent=background_extent,
    )


def select_active_indices(
    values: np.ndarray,
    *,
    spikes: np.ndarray | None = None,
    max_points: int = 4000,
) -> np.ndarray:
    values = np.asarray(values, dtype=float).reshape(-1)
    if values.size == 0:
        return np.zeros(0, dtype=np.int64)
    selected: list[int] = []
    if spikes is not None:
        spike_ids = np.flatnonzero(np.asarray(spikes).reshape(-1) > 0.0).astype(np.int64)
        if spike_ids.size > 0:
            if spike_ids.size > int(max_points):
                spike_scores = np.abs(values[spike_ids])
                order = np.argsort(spike_scores)[-int(max_points) :]
                spike_ids = spike_ids[order]
            selected.extend(int(idx) for idx in spike_ids.tolist())
    remaining = max(0, int(max_points) - len(selected))
    if remaining > 0:
        inactive_mask = np.ones(values.shape[0], dtype=bool)
        if selected:
            inactive_mask[np.asarray(selected, dtype=np.int64)] = False
        candidate_ids = np.flatnonzero(inactive_mask)
        if candidate_ids.size > 0:
            scores = np.abs(values[candidate_ids])
            take = min(int(remaining), int(candidate_ids.size))
            top = candidate_ids[np.argsort(scores)[-take:]]
            selected.extend(int(idx) for idx in top.tolist())
    if not selected:
        return np.zeros(0, dtype=np.int64)
    return np.asarray(sorted(set(selected)), dtype=np.int64)


def _normalize_rows(matrix: np.ndarray, *, signed: bool) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.size == 0:
        return matrix
    out = np.zeros_like(matrix, dtype=np.float32)
    for row_idx in range(matrix.shape[0]):
        row = matrix[row_idx]
        if signed:
            scale = float(np.max(np.abs(row)))
            out[row_idx] = row / scale if scale > 1e-6 else row
        else:
            row_min = float(np.min(row))
            row_max = float(np.max(row))
            if row_max - row_min > 1e-6:
                out[row_idx] = (row - row_min) / (row_max - row_min)
            else:
                out[row_idx] = 0.0
    return out


def _brain_colors(voltage: np.ndarray, *, spikes: np.ndarray | None = None) -> np.ndarray:
    voltage = np.asarray(voltage, dtype=np.float32).reshape(-1)
    v_norm = np.clip((voltage + 55.0) / 10.0, 0.0, 1.0)
    cmap = plt.get_cmap("inferno")
    colors = cmap(v_norm)
    if spikes is not None:
        spiking = np.asarray(spikes, dtype=float).reshape(-1) > 0.0
        colors[spiking] = np.array([0.0, 1.0, 1.0, 1.0], dtype=np.float32)
    return colors


def _flyvis_colors(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    vmax = float(np.max(np.abs(values))) if values.size else 1.0
    vmax = max(vmax, 1e-6)
    cmap = plt.get_cmap("coolwarm")
    normalized = 0.5 + 0.5 * np.clip(values / vmax, -1.0, 1.0)
    return cmap(normalized)


def render_activation_frame(
    *,
    demo_frame: np.ndarray,
    brain_layout: BrainLayout,
    flyvis_layout: FlyVisLayout,
    brain_voltage: np.ndarray,
    brain_spikes: np.ndarray | None,
    flyvis_left: np.ndarray,
    flyvis_right: np.ndarray,
    monitor_matrix: np.ndarray,
    monitor_labels: Sequence[str],
    controller_matrix: np.ndarray,
    controller_labels: Sequence[str],
    cycle_index: int,
    frame_time_s: float,
    target_bearing_body: float,
    target_distance: float,
    overlay_title: str = "Current Best Branch Activation Visualization",
    max_brain_points: int = 6000,
    max_flyvis_points: int = 5000,
) -> np.ndarray:
    fig = plt.Figure(figsize=(16, 9), dpi=120, constrained_layout=True)
    FigureCanvasAgg(fig)
    grid = fig.add_gridspec(2, 3, width_ratios=[1.35, 1.0, 1.05], height_ratios=[1.0, 1.0])
    ax_demo = fig.add_subplot(grid[0, 0])
    ax_brain = fig.add_subplot(grid[0, 1])
    ax_monitor = fig.add_subplot(grid[0, 2])
    flyvis_grid = grid[1, 0:2].subgridspec(1, 2, wspace=0.08)
    ax_flyvis_left = fig.add_subplot(flyvis_grid[0, 0])
    ax_flyvis_right = fig.add_subplot(flyvis_grid[0, 1])
    ax_controller = fig.add_subplot(grid[1, 2])

    fig.suptitle(overlay_title, fontsize=16)

    ax_demo.imshow(np.asarray(demo_frame, dtype=np.uint8))
    ax_demo.set_title(f"Embodied View  t={frame_time_s:.3f}s")
    ax_demo.text(
        0.02,
        0.98,
        f"bearing={target_bearing_body:+.3f} rad\n"
        f"distance={target_distance:.3f}\n"
        f"cycle={cycle_index}",
        transform=ax_demo.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        color="white",
        bbox={"facecolor": "black", "alpha": 0.55, "pad": 4},
    )
    ax_demo.axis("off")

    ax_brain.imshow(
        brain_layout.background_image,
        extent=brain_layout.background_extent,
        origin="lower",
        cmap="Greys",
        alpha=0.65,
        aspect="auto",
    )
    active_brain_ids = select_active_indices(brain_voltage, spikes=brain_spikes, max_points=max_brain_points)
    if active_brain_ids.size > 0:
        brain_colors = _brain_colors(brain_voltage[active_brain_ids], spikes=None if brain_spikes is None else brain_spikes[active_brain_ids])
        ax_brain.scatter(
            brain_layout.xy[active_brain_ids, 0],
            brain_layout.xy[active_brain_ids, 1],
            c=brain_colors,
            s=4.0,
            linewidths=0.0,
            alpha=0.9,
        )
    if brain_layout.decoder_xy.size > 0:
        fixed_mask = brain_layout.decoder_kinds == "fixed"
        pop_mask = brain_layout.decoder_kinds == "population"
        if np.any(pop_mask):
            ax_brain.scatter(
                brain_layout.decoder_xy[pop_mask, 0],
                brain_layout.decoder_xy[pop_mask, 1],
                c="#ffcc00",
                s=26.0,
                marker="o",
                edgecolors="black",
                linewidths=0.35,
                alpha=0.95,
            )
        if np.any(fixed_mask):
            ax_brain.scatter(
                brain_layout.decoder_xy[fixed_mask, 0],
                brain_layout.decoder_xy[fixed_mask, 1],
                c="#00ffff",
                s=52.0,
                marker="*",
                edgecolors="black",
                linewidths=0.45,
                alpha=0.95,
            )
        for idx, label in enumerate(brain_layout.decoder_labels[:12]):
            ax_brain.text(
                float(brain_layout.decoder_xy[idx, 0]),
                float(brain_layout.decoder_xy[idx, 1]),
                str(label),
                fontsize=6,
                color="white",
                ha="center",
                va="center",
            )
    ax_brain.set_title("Whole Brain Snapshot")
    ax_brain.set_xlabel("x")
    ax_brain.set_ylabel("y")

    def _plot_flyvis(ax: plt.Axes, values: np.ndarray, title: str) -> None:
        ax.imshow(
            flyvis_layout.background_image,
            extent=flyvis_layout.background_extent,
            origin="lower",
            cmap="Greys",
            alpha=0.55,
            aspect="auto",
        )
        active_ids = select_active_indices(values, max_points=max_flyvis_points)
        if active_ids.size > 0:
            colors = _flyvis_colors(values[active_ids])
            ax.scatter(
                flyvis_layout.uv[active_ids, 0],
                flyvis_layout.uv[active_ids, 1],
                c=colors,
                s=4.0,
                linewidths=0.0,
                alpha=0.9,
            )
        ax.set_title(title)
        ax.set_xlabel("u")
        ax.set_ylabel("v")

    _plot_flyvis(ax_flyvis_left, flyvis_left, "FlyVis Left Eye")
    _plot_flyvis(ax_flyvis_right, flyvis_right, "FlyVis Right Eye")

    ax_monitor.set_title("Monitored Decoder Populations")
    if monitor_matrix.size == 0 or len(monitor_labels) == 0:
        ax_monitor.text(0.5, 0.5, "No monitored groups", ha="center", va="center", fontsize=11, color="white")
        ax_monitor.set_facecolor("black")
        ax_monitor.set_xticks([])
        ax_monitor.set_yticks([])
    else:
        monitor_img = _normalize_rows(monitor_matrix, signed=False)
        ax_monitor.imshow(monitor_img, aspect="auto", origin="lower", cmap="magma", interpolation="nearest")
        ax_monitor.axvline(cycle_index, color="cyan", linewidth=1.0)
        ax_monitor.set_yticks(np.arange(len(monitor_labels)))
        ax_monitor.set_yticklabels([str(label) for label in monitor_labels], fontsize=7)
        ax_monitor.set_xlabel("cycle")

    controller_img = _normalize_rows(controller_matrix, signed=True)
    ax_controller.imshow(controller_img, aspect="auto", origin="lower", cmap="coolwarm", interpolation="nearest", vmin=-1.0, vmax=1.0)
    ax_controller.axvline(cycle_index, color="yellow", linewidth=1.0)
    ax_controller.set_title("Controllers / Behavior")
    ax_controller.set_yticks(np.arange(len(controller_labels)))
    ax_controller.set_yticklabels([str(label) for label in controller_labels], fontsize=8)
    ax_controller.set_xlabel("cycle")

    fig.canvas.draw()
    buffer = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
    image = buffer.reshape(fig.canvas.get_width_height()[1], fig.canvas.get_width_height()[0], 4)[..., :3].copy()
    plt.close(fig)
    return image


def render_overview_figure(
    path: str | Path,
    *,
    demo_frame: np.ndarray,
    brain_layout: BrainLayout,
    flyvis_layout: FlyVisLayout,
    brain_voltage: np.ndarray,
    brain_spikes: np.ndarray | None,
    flyvis_left: np.ndarray,
    flyvis_right: np.ndarray,
    monitor_matrix: np.ndarray,
    monitor_labels: Sequence[str],
    controller_matrix: np.ndarray,
    controller_labels: Sequence[str],
    cycle_index: int,
    frame_time_s: float,
    target_bearing_body: float,
    target_distance: float,
    overlay_title: str = "Current Best Branch Activation Visualization",
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image = render_activation_frame(
        demo_frame=demo_frame,
        brain_layout=brain_layout,
        flyvis_layout=flyvis_layout,
        brain_voltage=brain_voltage,
        brain_spikes=brain_spikes,
        flyvis_left=flyvis_left,
        flyvis_right=flyvis_right,
        monitor_matrix=monitor_matrix,
        monitor_labels=monitor_labels,
        controller_matrix=controller_matrix,
        controller_labels=controller_labels,
        cycle_index=cycle_index,
        frame_time_s=frame_time_s,
        target_bearing_body=target_bearing_body,
        target_distance=target_distance,
        overlay_title=overlay_title,
    )
    plt.imsave(path, image)
    return path

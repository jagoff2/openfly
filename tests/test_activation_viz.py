from __future__ import annotations

from pathlib import Path

import numpy as np

from visualization.activation_viz import BrainLayout, FlyVisLayout, render_activation_frame, render_overview_figure


def test_render_activation_frame_smoke(tmp_path: Path) -> None:
    brain_layout = BrainLayout(
        root_ids=np.asarray([1, 2, 3], dtype=np.int64),
        xy=np.asarray([[0.0, 0.0], [1.0, 0.5], [2.0, 1.5]], dtype=np.float32),
        background_image=np.ones((32, 32), dtype=np.float32),
        background_extent=(0.0, 2.0, 0.0, 2.0),
        decoder_xy=np.asarray([[0.5, 0.5], [1.5, 1.0]], dtype=np.float32),
        decoder_labels=np.asarray(["P9_L", "DNp103_L"], dtype="<U64"),
        decoder_kinds=np.asarray(["fixed", "population"], dtype="<U16"),
    )
    flyvis_layout = FlyVisLayout(
        uv=np.asarray([[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]], dtype=np.float32),
        node_types=np.asarray(["T2", "T3", "Tm9"], dtype="<U64"),
        background_image=np.ones((24, 24), dtype=np.float32),
        background_extent=(0.0, 1.0, 0.0, 1.0),
    )
    image = render_activation_frame(
        demo_frame=np.zeros((48, 64, 3), dtype=np.uint8),
        brain_layout=brain_layout,
        flyvis_layout=flyvis_layout,
        brain_voltage=np.asarray([-52.0, -49.5, -46.0], dtype=np.float32),
        brain_spikes=np.asarray([0, 1, 0], dtype=np.uint8),
        flyvis_left=np.asarray([0.1, -0.2, 0.3], dtype=np.float32),
        flyvis_right=np.asarray([-0.3, 0.2, 0.1], dtype=np.float32),
        monitor_matrix=np.asarray([[0.0, 1.0, 2.0], [2.0, 1.0, 0.0]], dtype=np.float32),
        monitor_labels=["DNp103", "DNpe056"],
        controller_matrix=np.asarray(
            [
                [0.0, 0.3, 0.6],
                [0.0, 0.4, 0.8],
                [0.1, 0.2, 0.3],
                [-0.1, 0.0, 0.1],
            ],
            dtype=np.float32,
        ),
        controller_labels=["forward", "turn", "left_drive", "right_drive"],
        cycle_index=1,
        frame_time_s=0.1,
        target_bearing_body=0.25,
        target_distance=9.5,
    )
    assert image.ndim == 3
    assert image.shape[2] == 3
    assert image.shape[0] > 100
    assert image.shape[1] > 100

    overview_path = render_overview_figure(
        tmp_path / "overview.png",
        demo_frame=np.zeros((48, 64, 3), dtype=np.uint8),
        brain_layout=brain_layout,
        flyvis_layout=flyvis_layout,
        brain_voltage=np.asarray([-52.0, -49.5, -46.0], dtype=np.float32),
        brain_spikes=np.asarray([0, 1, 0], dtype=np.uint8),
        flyvis_left=np.asarray([0.1, -0.2, 0.3], dtype=np.float32),
        flyvis_right=np.asarray([-0.3, 0.2, 0.1], dtype=np.float32),
        monitor_matrix=np.asarray([[0.0, 1.0, 2.0], [2.0, 1.0, 0.0]], dtype=np.float32),
        monitor_labels=["DNp103", "DNpe056"],
        controller_matrix=np.asarray(
            [
                [0.0, 0.3, 0.6],
                [0.0, 0.4, 0.8],
                [0.1, 0.2, 0.3],
                [-0.1, 0.0, 0.1],
            ],
            dtype=np.float32,
        ),
        controller_labels=["forward", "turn", "left_drive", "right_drive"],
        cycle_index=1,
        frame_time_s=0.1,
        target_bearing_body=0.25,
        target_distance=9.5,
    )
    assert overview_path.exists()

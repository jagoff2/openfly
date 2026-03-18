from __future__ import annotations

from pathlib import Path

import imageio.v3 as iio
import numpy as np

from visualization.render import render_activation_frame, save_activation_frame


def test_render_activation_frame_smoke(tmp_path: Path) -> None:
    demo = np.zeros((18, 24, 3), dtype=np.uint8)
    demo[:, :, 1] = 40
    demo[4:14, 8:16, 0] = 220
    demo[4:14, 8:16, 2] = 120

    whole_brain_points = np.asarray(
        [
            [0.0, 0.0, 0.1],
            [1.0, 0.2, 0.4],
            [0.5, 1.2, 0.9],
        ],
        dtype=float,
    )
    flyvis_left_points = np.asarray([[0.0, 0.0, 0.2], [1.0, 0.4, 0.7]], dtype=float)
    flyvis_right_points = np.asarray([[0.1, 0.8, 0.6], [1.1, 0.2, 0.3]], dtype=float)
    trace_x = np.linspace(0.0, 0.2, 5)

    frame = render_activation_frame(
        demo,
        whole_brain_points=whole_brain_points,
        flyvis_left_points=flyvis_left_points,
        flyvis_right_points=flyvis_right_points,
        trace_x=trace_x,
        decoder_traces={
            "forward": np.asarray([0.0, 0.5, 1.0, 0.8, 0.2]),
            "turn": np.asarray([0.0, -0.3, 0.2, 0.6, 0.1]),
        },
        controller_traces={
            "left_drive": np.asarray([0.4, 0.6, 1.0, 0.8, 0.5]),
            "right_drive": np.asarray([0.5, 0.5, 0.7, 1.0, 0.9]),
        },
        metadata={"title": "Synthetic activation frame", "sim_time": 0.2, "cycle": 5},
    )

    assert frame.ndim == 3
    assert frame.shape[2] == 3
    assert frame.dtype == np.uint8
    assert frame.shape[0] > 100
    assert frame.shape[1] > 100
    assert frame.mean() > 0.0

    output_path = tmp_path / "activation-frame.png"
    returned_path = save_activation_frame(
        output_path,
        demo,
        whole_brain_points=whole_brain_points,
        flyvis_left_points=flyvis_left_points,
        flyvis_right_points=flyvis_right_points,
        trace_x=trace_x,
        decoder_traces={"forward": np.asarray([0.0, 0.5, 1.0, 0.8, 0.2])},
        controller_traces={"left_drive": np.asarray([0.4, 0.6, 1.0, 0.8, 0.5])},
        metadata={"title": "Saved synthetic frame"},
    )

    assert returned_path == output_path
    assert output_path.exists()

    loaded = iio.imread(output_path)
    assert loaded.shape == frame.shape
    assert loaded.dtype == np.uint8

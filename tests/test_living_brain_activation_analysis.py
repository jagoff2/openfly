from __future__ import annotations

import numpy as np

from analysis.living_brain_activation_analysis import (
    build_monitor_rate_comparison,
    summarize_rendered_activity,
)


def test_summarize_rendered_activity_distinguishes_spikes_from_selected_voltage_points() -> None:
    voltage = np.asarray(
        [
            [0.0, 5.0, 4.0, 3.0],
            [6.0, 0.0, 0.0, 2.0],
        ],
        dtype=np.float32,
    )
    spikes = np.asarray(
        [
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        dtype=np.uint8,
    )
    summary, selected_counts, spike_counts, _, _ = summarize_rendered_activity(
        brain_voltage_frames=voltage,
        brain_spike_frames=spikes,
        max_points=2,
    )
    assert summary["frame_count"] == 2
    assert summary["brain_neuron_count"] == 4
    assert summary["spiking_units"] == 1
    assert summary["selected_units"] == 4
    assert summary["selected_and_spiking"] == 1
    assert summary["selected_not_spiking"] == 3
    assert spike_counts.tolist() == [0, 1, 0, 0]
    assert selected_counts.tolist() == [1, 1, 1, 1]


def test_build_monitor_rate_comparison_aligns_labels() -> None:
    target_capture = {
        "monitor_labels": np.asarray(["A", "B"]),
        "monitor_matrix": np.asarray([[1.0, 3.0], [10.0, 14.0]], dtype=np.float32),
    }
    no_target_capture = {
        "monitor_labels": np.asarray(["B", "C"]),
        "monitor_matrix": np.asarray([[4.0, 6.0], [2.0, 2.0]], dtype=np.float32),
    }
    table = build_monitor_rate_comparison(
        target_capture=target_capture,
        no_target_capture=no_target_capture,
    )
    table = table.set_index("label")
    assert table.loc["A", "target_mean_rate_hz"] == 2.0
    assert table.loc["A", "no_target_mean_rate_hz"] == 0.0
    assert table.loc["B", "target_mean_rate_hz"] == 12.0
    assert table.loc["B", "no_target_mean_rate_hz"] == 5.0
    assert table.loc["C", "target_mean_rate_hz"] == 0.0
    assert table.loc["C", "no_target_mean_rate_hz"] == 2.0

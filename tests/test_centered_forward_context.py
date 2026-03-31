from __future__ import annotations

import json
from pathlib import Path

from bridge.decoder import DecoderConfig, MotorDecoder


def test_centered_forward_context_library_uses_baseline_centering(tmp_path: Path) -> None:
    library_path = tmp_path / "forward_context_library.json"
    library_path.write_text(
        json.dumps(
            {
                "selected_groups": [
                    {
                        "label": "CtxA",
                        "left_root_ids": [1],
                        "right_root_ids": [2],
                        "forward_weight": 2.0,
                        "baseline_bilateral_hz": 10.0,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            command_mode="hybrid_multidrive",
            forward_context_scale_hz=5.0,
            forward_context_signal_library_json=str(library_path),
            signal_smoothing_alpha=1.0,
        )
    )
    high = decoder.decode_state({1: 16.0, 2: 16.0})
    decoder.reset()
    baseline = decoder.decode_state({1: 10.0, 2: 10.0})

    assert high.neuron_rates["forward_context_library_signal"] > 0.0
    assert abs(baseline.neuron_rates["forward_context_library_signal"]) < 1e-9
    assert high.neuron_rates["CtxA_forward_context_centered_hz"] == 6.0


def test_motion_energy_forward_context_rectifies_bilateral_motion_without_baseline_boost(tmp_path: Path) -> None:
    library_path = tmp_path / "forward_context_motion_energy.json"
    library_path.write_text(
        json.dumps(
            {
                "selected_groups": [
                    {
                        "label": "CtxA",
                        "left_root_ids": [1],
                        "right_root_ids": [2],
                        "forward_weight": 2.0,
                        "baseline_bilateral_hz": 10.0,
                        "signal_mode": "motion_energy",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            command_mode="hybrid_multidrive",
            forward_context_scale_hz=5.0,
            forward_context_signal_library_json=str(library_path),
            signal_smoothing_alpha=1.0,
        )
    )

    baseline = decoder.decode_state({1: 10.0, 2: 10.0})
    motion_high = decoder.decode_state({1: 16.0, 2: 16.0})
    decoder.reset()
    motion_low = decoder.decode_state({1: 4.0, 2: 4.0})

    assert abs(baseline.neuron_rates["forward_context_library_signal"]) < 1e-9
    assert motion_high.neuron_rates["CtxA_forward_context_transformed_hz"] == 6.0
    assert motion_low.neuron_rates["CtxA_forward_context_transformed_hz"] == 6.0
    assert motion_high.neuron_rates["forward_context_library_signal"] > 0.0
    assert motion_low.neuron_rates["forward_context_library_signal"] > 0.0


def test_forward_context_baseline_adaptation_updates_dynamic_stationary_reference(tmp_path: Path) -> None:
    library_path = tmp_path / "forward_context_adaptive.json"
    library_path.write_text(
        json.dumps(
            {
                "selected_groups": [
                    {
                        "label": "CtxA",
                        "left_root_ids": [1],
                        "right_root_ids": [2],
                        "forward_weight": 1.0,
                        "baseline_bilateral_hz": 10.0,
                        "signal_mode": "motion_energy",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            command_mode="hybrid_multidrive",
            forward_context_scale_hz=5.0,
            forward_context_signal_library_json=str(library_path),
            forward_context_baseline_alpha=0.5,
            signal_smoothing_alpha=1.0,
        )
    )

    first = decoder.decode_state({1: 20.0, 2: 20.0})
    second = decoder.decode_state({1: 20.0, 2: 20.0})
    decoder.reset()
    after_reset = decoder.decode_state({1: 20.0, 2: 20.0})

    assert first.neuron_rates["CtxA_forward_context_baseline_hz"] == 10.0
    assert second.neuron_rates["CtxA_forward_context_baseline_hz"] > 10.0
    assert second.neuron_rates["CtxA_forward_context_transformed_hz"] < first.neuron_rates["CtxA_forward_context_transformed_hz"]
    assert after_reset.neuron_rates["CtxA_forward_context_baseline_hz"] == 10.0

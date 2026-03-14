from __future__ import annotations

import json
from pathlib import Path

from bridge.voltage_decoder import VoltageTurnDecoder, VoltageTurnDecoderConfig


def test_voltage_turn_decoder_uses_voltage_asymmetry_for_turn_signal(tmp_path: Path) -> None:
    signal_library = tmp_path / "signal_library.json"
    signal_library.write_text(
        json.dumps(
            {
                "selected_groups": [
                    {
                        "label": "RelayA",
                        "left_root_ids": [1],
                        "right_root_ids": [2],
                        "turn_weight": -1.0,
                        "super_class": "visual_projection",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = VoltageTurnDecoder(
        VoltageTurnDecoderConfig(
            signal_library_json=str(signal_library),
            turn_gain=0.5,
            turn_scale_mv=1.0,
        )
    )

    readout = decoder.decode_state(
        monitored_voltage={
            "1": -1.0,
            "2": 1.0,
        }
    )

    assert readout.turn_signal < 0.0
    assert readout.command.left_drive > readout.command.right_drive
    assert readout.neuron_rates["RelayA_asymmetry_voltage_mv"] == 2.0


def test_voltage_turn_decoder_requires_all_group_root_ids(tmp_path: Path) -> None:
    signal_library = tmp_path / "signal_library.json"
    signal_library.write_text(
        json.dumps(
            {
                "selected_groups": [
                    {
                        "label": "RelayA",
                        "left_root_ids": [1, 3],
                        "right_root_ids": [2, 4],
                        "turn_weight": -0.5,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = VoltageTurnDecoder(VoltageTurnDecoderConfig(signal_library_json=str(signal_library)))

    assert decoder.required_neuron_ids() == [1, 2, 3, 4]


def test_voltage_turn_decoder_subtracts_group_baseline_asymmetry(tmp_path: Path) -> None:
    signal_library = tmp_path / "signal_library.json"
    signal_library.write_text(
        json.dumps(
            {
                "selected_groups": [
                    {
                        "label": "RelayA",
                        "left_root_ids": [1],
                        "right_root_ids": [2],
                        "turn_weight": -1.0,
                        "baseline_asymmetry_mv": 2.0,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = VoltageTurnDecoder(
        VoltageTurnDecoderConfig(
            signal_library_json=str(signal_library),
            turn_gain=0.5,
            turn_scale_mv=1.0,
        )
    )

    readout = decoder.decode_state(
        monitored_voltage={
            "1": -1.0,
            "2": 1.0,
        }
    )

    assert readout.turn_signal == 0.0
    assert readout.command.left_drive == 0.0
    assert readout.command.right_drive == 0.0
    assert readout.neuron_rates["RelayA_asymmetry_voltage_mv"] == 2.0
    assert readout.neuron_rates["RelayA_centered_asymmetry_voltage_mv"] == 0.0
    assert readout.neuron_rates["RelayA_baseline_asymmetry_mv"] == 2.0


def test_voltage_turn_decoder_silent_guard_blocks_bias_without_activity(tmp_path: Path) -> None:
    signal_library = tmp_path / "signal_library.json"
    signal_library.write_text(
        json.dumps(
            {
                "selected_groups": [
                    {
                        "label": "RelayA",
                        "left_root_ids": [1],
                        "right_root_ids": [2],
                        "turn_weight": -1.0,
                        "baseline_asymmetry_mv": 2.0,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = VoltageTurnDecoder(
        VoltageTurnDecoderConfig(
            signal_library_json=str(signal_library),
            turn_gain=0.5,
            turn_scale_mv=1.0,
        )
    )

    readout = decoder.decode_state(
        monitored_voltage={
            "1": 0.0,
            "2": 0.0,
        },
        monitored_spikes={
            "1": 0.0,
            "2": 0.0,
        },
    )

    assert readout.turn_signal == 0.0
    assert readout.command.left_drive == 0.0
    assert readout.command.right_drive == 0.0
    assert readout.neuron_rates["voltage_turn_silent_guard"] == 1.0

    resting_readout = decoder.decode_state(
        monitored_voltage={
            "1": -52.0,
            "2": -52.0,
        },
        monitored_spikes={
            "1": 0.0,
            "2": 0.0,
        },
    )

    assert resting_readout.turn_signal == 0.0
    assert resting_readout.command.left_drive == 0.0
    assert resting_readout.command.right_drive == 0.0
    assert resting_readout.neuron_rates["voltage_turn_silent_guard"] == 1.0
    assert resting_readout.neuron_rates["voltage_turn_silent_guard_voltage_span_mv"] == 0.0

    empty_readout = decoder.decode_state(monitored_voltage={}, monitored_spikes={})
    assert empty_readout.turn_signal == 0.0
    assert empty_readout.command.left_drive == 0.0
    assert empty_readout.command.right_drive == 0.0
    assert empty_readout.neuron_rates["voltage_turn_silent_guard"] == 1.0
    assert empty_readout.neuron_rates["voltage_turn_silent_guard_reason_no_activity"] == 1.0

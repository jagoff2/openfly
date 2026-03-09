from __future__ import annotations

import json
from pathlib import Path

from body.interfaces import BodyObservation
from bridge.brain_context import BrainContextConfig, BrainContextInjector
from bridge.controller import ClosedLoopBridge
from bridge.decoder import DecoderConfig, MotorDecoder
from brain.mock_backend import MockWholeBrainBackend
from brain.public_ids import collapse_sensor_pool_rates
from vision.feature_extractor import VisionFeatures


def test_bridge_turns_toward_right_salience() -> None:
    backend = MockWholeBrainBackend()
    bridge = ClosedLoopBridge(backend)
    observation = BodyObservation(
        sim_time=0.0,
        position_xy=(0.0, 0.0),
        yaw=0.0,
        forward_speed=0.2,
        yaw_rate=0.0,
        contact_force=1.0,
        realistic_vision={"T2": [0.1, 0.9], "T4a": [0.0, 0.6], "T5a": [0.0, 0.6]},
    )
    readout, info = bridge.step(observation, num_brain_steps=20)
    assert readout.command.right_drive > readout.command.left_drive
    assert info["sensor_pool_rates"]["vision_right"] > info["sensor_pool_rates"]["vision_left"]


def test_zero_input_produces_zero_motor_command() -> None:
    backend = MockWholeBrainBackend()
    bridge = ClosedLoopBridge(backend)
    observation = BodyObservation(
        sim_time=0.0,
        position_xy=(0.0, 0.0),
        yaw=0.0,
        forward_speed=0.0,
        yaw_rate=0.0,
        contact_force=0.0,
        realistic_vision={},
    )

    readout, info = bridge.step(observation, num_brain_steps=20)

    assert info["sensor_pool_rates"] == {
        "vision_left": 0.0,
        "vision_right": 0.0,
        "mech_left": 0.0,
        "mech_right": 0.0,
    }
    assert readout.command.left_drive == 0.0
    assert readout.command.right_drive == 0.0
    assert all(rate == 0.0 for rate in readout.neuron_rates.values())


def test_public_input_collapse_uses_bilateral_means() -> None:
    collapsed = collapse_sensor_pool_rates(
        {
            "vision_left": 30.0,
            "vision_right": 50.0,
            "mech_left": 70.0,
            "mech_right": 10.0,
        }
    )

    assert collapsed == {
        "vision_bilateral": 40.0,
        "mech_bilateral": 40.0,
    }


def test_public_p9_context_mode_injects_brain_side_drive_without_decoder_fallback() -> None:
    backend = MockWholeBrainBackend()
    bridge = ClosedLoopBridge(
        backend,
        brain_context_injector=BrainContextInjector(BrainContextConfig(mode="public_p9_context", p9_rate_hz=100.0)),
    )
    observation = BodyObservation(
        sim_time=0.0,
        position_xy=(0.0, 0.0),
        yaw=0.0,
        forward_speed=0.0,
        yaw_rate=0.0,
        contact_force=0.0,
        realistic_vision={},
    )

    readout, info = bridge.step(observation, num_brain_steps=20)

    assert info["brain_context"]["mode"] == "public_p9_context"
    assert info["brain_context"]["direct_input_rates_hz"] == {
        "P9_left": 100.0,
        "P9_right": 100.0,
    }
    assert readout.command.left_drive > 0.0
    assert readout.command.right_drive > 0.0
    assert readout.neuron_rates["forward_left_hz"] > 0.0
    assert readout.neuron_rates["forward_right_hz"] > 0.0


def test_inferred_visual_turn_context_injects_asymmetric_brain_side_turn_drive() -> None:
    backend = MockWholeBrainBackend()
    bridge = ClosedLoopBridge(
        backend,
        brain_context_injector=BrainContextInjector(
            BrainContextConfig(
                mode="inferred_visual_turn_context",
                inferred_base_p9_rate_hz=0.0,
                inferred_p9_gain_hz=120.0,
                inferred_turn_rate_hz=100.0,
                inferred_confidence_scale=1.0,
            )
        ),
    )
    observation = BodyObservation(
        sim_time=0.0,
        position_xy=(0.0, 0.0),
        yaw=0.0,
        forward_speed=0.0,
        yaw_rate=0.0,
        contact_force=0.0,
        realistic_vision_features=VisionFeatures(
            salience_left=0.2,
            salience_right=0.8,
            flow_left=0.0,
            flow_right=0.0,
            inferred_left_evidence=0.0,
            inferred_right_evidence=0.6,
            inferred_turn_bias=0.6,
            inferred_turn_confidence=1.0,
            inferred_candidate_count=4,
        ).to_dict(),
        vision_payload_mode="fast",
    )

    readout, info = bridge.step(observation, num_brain_steps=20)

    assert info["brain_context"]["mode"] == "inferred_visual_turn_context"
    assert info["brain_context"]["direct_input_rates_hz"]["turn_right_rate_hz"] > 0.0
    assert info["brain_context"]["direct_input_rates_hz"]["turn_left_rate_hz"] == 0.0
    assert info["brain_context"]["forward_rate_hz"] > 0.0
    assert readout.command.right_drive > readout.command.left_drive


def test_inferred_visual_p9_context_cold_starts_and_steers_via_asymmetric_p9_drive() -> None:
    backend = MockWholeBrainBackend()
    bridge = ClosedLoopBridge(
        backend,
        decoder=MotorDecoder(DecoderConfig(forward_asymmetry_turn_gain=0.75, forward_asymmetry_scale_hz=20.0)),
        brain_context_injector=BrainContextInjector(
            BrainContextConfig(
                mode="inferred_visual_p9_context",
                inferred_base_p9_rate_hz=0.0,
                inferred_p9_gain_hz=120.0,
                inferred_forward_on_threshold=0.2,
                inferred_forward_off_threshold=0.15,
                inferred_forward_scale=0.2,
                inferred_gate_tau_s=0.05,
                inferred_turn_bias_scale=0.2,
                inferred_balance_scale=0.2,
                inferred_p9_asymmetry_gain=0.45,
            )
        ),
    )
    observation = BodyObservation(
        sim_time=0.0,
        position_xy=(0.0, 0.0),
        yaw=0.0,
        forward_speed=0.0,
        yaw_rate=0.0,
        contact_force=0.0,
        realistic_vision_features=VisionFeatures(
            salience_left=0.2,
            salience_right=0.8,
            flow_left=0.0,
            flow_right=0.0,
            inferred_left_evidence=0.0,
            inferred_right_evidence=0.6,
            inferred_turn_bias=0.4,
            inferred_turn_confidence=1.0,
            inferred_candidate_count=4,
        ).to_dict(),
        vision_payload_mode="fast",
    )

    readout, info = bridge.step(observation, num_brain_steps=20)

    assert info["brain_context"]["mode"] == "inferred_visual_p9_context"
    assert info["brain_context"]["locomotor_gate"] > 0.0
    assert info["brain_context"]["direct_input_rates_hz"]["P9_right"] > info["brain_context"]["direct_input_rates_hz"]["P9_left"]
    assert readout.command.right_drive > readout.command.left_drive


def test_decoder_can_use_expanded_relay_readout_groups(tmp_path: Path) -> None:
    relay_json = tmp_path / "relay.json"
    relay_json.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "LCe06",
                        "left_root_ids": [101, 102],
                        "right_root_ids": [201, 202],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            population_candidates_json=str(relay_json),
            population_forward_cell_types=("LCe06",),
            population_turn_cell_types=("LCe06",),
            population_forward_scale_hz=50.0,
            population_turn_scale_hz=10.0,
            population_forward_weight=1.0,
            population_turn_weight=0.5,
            forward_gain=0.75,
            signal_smoothing_alpha=1.0,
        )
    )
    rates = {
        101: 80.0,
        102: 80.0,
        201: 100.0,
        202: 100.0,
    }

    readout = decoder.decode(rates)

    assert set(decoder.required_neuron_ids()).issuperset({101, 102, 201, 202})
    assert readout.neuron_rates["population_forward_left_hz"] == 80.0
    assert readout.neuron_rates["population_forward_right_hz"] == 100.0
    assert readout.command.left_drive > 0.0
    assert readout.command.right_drive > readout.command.left_drive

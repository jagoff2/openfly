from __future__ import annotations

import json
from pathlib import Path

from body.interfaces import BodyCommand, BodyObservation, HybridDriveCommand
from bridge.brain_context import BrainContextConfig, BrainContextInjector
from bridge.controller import ClosedLoopBridge
from bridge.decoder import DecoderConfig, MotorDecoder, MotorReadout
from brain.mock_backend import MockWholeBrainBackend
from brain.public_ids import (
    DNA01_LEFT,
    DNA01_RIGHT,
    DNA02_LEFT,
    DNA02_RIGHT,
    MDN_1,
    MDN_2,
    MDN_3,
    MDN_4,
    P9_LEFT,
    P9_ODN1_LEFT,
    P9_ODN1_RIGHT,
    P9_RIGHT,
    collapse_sensor_pool_rates,
)
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


def test_decoder_can_steer_from_forward_asymmetry_without_turn_readout() -> None:
    decoder = MotorDecoder(
        DecoderConfig(
            forward_gain=0.8,
            turn_gain=0.6,
            forward_scale_hz=100.0,
            forward_asymmetry_scale_hz=50.0,
            forward_asymmetry_turn_gain=0.5,
            signal_smoothing_alpha=1.0,
        )
    )
    rates = {
        DNA01_LEFT: 0.0,
        DNA02_LEFT: 0.0,
        DNA01_RIGHT: 0.0,
        DNA02_RIGHT: 0.0,
        P9_LEFT: 0.0,
        P9_RIGHT: 120.0,
        P9_ODN1_LEFT: 0.0,
        P9_ODN1_RIGHT: 120.0,
        MDN_1: 0.0,
        MDN_2: 0.0,
        MDN_3: 0.0,
        MDN_4: 0.0,
    }

    readout = decoder.decode(rates)

    assert readout.neuron_rates["turn_left_hz"] == 0.0
    assert readout.neuron_rates["turn_right_hz"] == 0.0
    assert readout.command.right_drive > readout.command.left_drive


def test_decoder_can_emit_hybrid_motor_latents() -> None:
    decoder = MotorDecoder(
        DecoderConfig(
            command_mode="hybrid_multidrive",
            forward_gain=1.0,
            turn_gain=0.6,
            latent_freq_bias=0.8,
            latent_freq_gain=0.5,
            latent_turn_amp_gain=0.3,
            latent_turn_freq_gain=0.15,
            signal_smoothing_alpha=1.0,
        )
    )
    rates = {
        DNA01_LEFT: 0.0,
        DNA02_LEFT: 0.0,
        DNA01_RIGHT: 80.0,
        DNA02_RIGHT: 80.0,
        P9_LEFT: 80.0,
        P9_RIGHT: 140.0,
        P9_ODN1_LEFT: 80.0,
        P9_ODN1_RIGHT: 140.0,
        MDN_1: 0.0,
        MDN_2: 0.0,
        MDN_3: 0.0,
        MDN_4: 0.0,
    }

    readout = decoder.decode(rates)

    assert isinstance(readout.command, HybridDriveCommand)
    assert len(readout.command.to_action()) == 7
    assert readout.command.right_amp > readout.command.left_amp
    assert readout.command.right_freq_scale > readout.command.left_freq_scale
    assert readout.command.reverse_gate == 0.0


def test_decoder_can_monitor_population_groups_without_using_them_for_control(tmp_path: Path) -> None:
    monitor_json = tmp_path / "monitor.json"
    monitor_json.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "DNp103",
                        "left_root_ids": [301, 302],
                        "right_root_ids": [401, 402],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            monitor_candidates_json=str(monitor_json),
            command_mode="two_drive",
            signal_smoothing_alpha=1.0,
        )
    )
    rates = {
        301: 10.0,
        302: 30.0,
        401: 50.0,
        402: 70.0,
    }

    readout = decoder.decode(rates)

    assert set(decoder.required_neuron_ids()).issuperset({301, 302, 401, 402})
    assert readout.neuron_rates["monitor_DNp103_left_hz"] == 20.0
    assert readout.neuron_rates["monitor_DNp103_right_hz"] == 60.0
    assert readout.neuron_rates["monitor_DNp103_bilateral_hz"] == 40.0
    assert readout.neuron_rates["monitor_DNp103_right_minus_left_hz"] == 40.0


def test_decoder_can_add_turn_voltage_latent_from_monitored_brain_state(tmp_path: Path) -> None:
    signal_library_json = tmp_path / "turn_latent.json"
    signal_library_json.write_text(
        json.dumps(
            {
                "turn_scale_mv": 5.0,
                "selected_groups": [
                    {
                        "label": "RelayA",
                        "left_root_ids": [301],
                        "right_root_ids": [401],
                        "turn_weight": 1.0,
                        "baseline_asymmetry_mv": 0.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            turn_gain=0.6,
            turn_voltage_signal_library_json=str(signal_library_json),
            turn_voltage_weight=1.0,
            signal_smoothing_alpha=1.0,
        )
    )
    rates = {
        DNA01_LEFT: 0.0,
        DNA02_LEFT: 0.0,
        DNA01_RIGHT: 0.0,
        DNA02_RIGHT: 0.0,
        P9_LEFT: 0.0,
        P9_RIGHT: 0.0,
        P9_ODN1_LEFT: 0.0,
        P9_ODN1_RIGHT: 0.0,
        MDN_1: 0.0,
        MDN_2: 0.0,
        MDN_3: 0.0,
        MDN_4: 0.0,
    }

    readout = decoder.decode_state(
        rates,
        monitored_voltage={
            301: -52.0,
            401: -47.0,
        },
    )

    assert set(decoder.required_neuron_ids()).issuperset({301, 401})
    assert readout.neuron_rates["turn_voltage_signal"] > 0.7
    assert readout.turn_signal > 0.7
    assert readout.command.right_drive > readout.command.left_drive
    assert readout.neuron_rates["RelayA_centered_asymmetry_voltage_mv"] == 5.0


def test_decoder_can_compose_promoted_turn_readout_without_changing_forward_state() -> None:
    decoder = MotorDecoder(
        DecoderConfig(
            command_mode="hybrid_multidrive",
            forward_gain=1.0,
            turn_gain=0.6,
            signal_smoothing_alpha=1.0,
        )
    )
    rates = {
        DNA01_LEFT: 0.0,
        DNA02_LEFT: 0.0,
        DNA01_RIGHT: 0.0,
        DNA02_RIGHT: 0.0,
        P9_LEFT: 80.0,
        P9_RIGHT: 80.0,
        P9_ODN1_LEFT: 80.0,
        P9_ODN1_RIGHT: 80.0,
        MDN_1: 0.0,
        MDN_2: 0.0,
        MDN_3: 0.0,
        MDN_4: 0.0,
    }

    base_readout = decoder.decode(rates)
    promoted = decoder.compose_promoted_readout(
        base_readout=base_readout,
        promoted_turn_state=0.5,
        promotion_debug={"promotion_shadow_turn_state": 0.5},
    )

    assert promoted.command.right_drive > promoted.command.left_drive
    assert promoted.command.left_amp < promoted.command.right_amp
    assert promoted.forward_signal == base_readout.forward_signal
    assert promoted.neuron_rates["turn_state_live"] == base_readout.neuron_rates["turn_state"]
    assert promoted.neuron_rates["turn_state_promoted"] == 0.5


def test_bridge_can_promote_named_shadow_turn_into_live_command() -> None:
    class FixedShadowDecoder:
        def reset(self) -> None:
            return None

        def decode(self, rates) -> MotorReadout:
            del rates
            return MotorReadout(
                command=BodyCommand(left_drive=-0.2, right_drive=0.2),
                forward_signal=0.0,
                turn_signal=1.0,
                reverse_signal=0.0,
                neuron_rates={"shadow_turn_state": 1.0},
            )

    backend = MockWholeBrainBackend()
    decoder = MotorDecoder(
        DecoderConfig(
            forward_gain=0.8,
            turn_gain=0.6,
            signal_smoothing_alpha=1.0,
        )
    )
    bridge = ClosedLoopBridge(
        backend,
        decoder=decoder,
        shadow_decoders=[("shadow_fixed", FixedShadowDecoder())],
        steering_promotion={
            "enabled": True,
            "shadow_label": "shadow_fixed",
            "mode": "replace",
            "shadow_turn_scale": 0.5,
            "max_abs_turn_state": 1.0,
        },
    )
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
    assert info["steering_promotion"]["enabled"] is True
    assert info["steering_promotion"]["shadow_label"] == "shadow_fixed"
    assert info["steering_promotion"]["promoted_turn_state"] == 0.5


def test_bridge_conflict_blend_can_override_live_turn_with_strong_shadow() -> None:
    bridge = ClosedLoopBridge(
        MockWholeBrainBackend(),
        steering_promotion={
            "enabled": True,
            "shadow_label": "shadow_fixed",
            "mode": "conflict_blend",
            "turn_blend": 0.4,
            "conflict_turn_blend": 1.0,
            "conflict_shadow_min_abs": 0.15,
            "conflict_shadow_min_ratio": 1.0,
            "shadow_turn_scale": 1.0,
            "max_abs_turn_state": 1.0,
        },
    )

    promoted_turn_state, info = bridge._promoted_turn_state(
        live_turn_state=-0.2,
        shadow_turn_state=0.4,
    )

    assert promoted_turn_state == 0.4
    assert info["live_shadow_opposite_sign"] is True
    assert info["shadow_confident"] is True
    assert info["conflict_override_active"] is True
    assert info["selected_turn_blend"] == 1.0
    assert info["promoted_turn_state"] == 0.4


def test_bridge_conflict_blend_scales_override_with_visual_evidence_gate() -> None:
    bridge = ClosedLoopBridge(
        MockWholeBrainBackend(),
        steering_promotion={
            "enabled": True,
            "shadow_label": "shadow_fixed",
            "mode": "conflict_blend",
            "turn_blend": 0.4,
            "conflict_turn_blend": 1.0,
            "conflict_shadow_min_abs": 0.15,
            "conflict_shadow_min_ratio": 1.0,
            "shadow_turn_scale": 1.0,
            "max_abs_turn_state": 1.0,
        },
    )

    promoted_turn_state, info = bridge._promoted_turn_state(
        live_turn_state=-0.2,
        shadow_turn_state=0.4,
        conflict_visual_evidence_gate=0.5,
    )

    expected_turn = 0.3 * (-0.2) + 0.7 * 0.4
    assert abs(promoted_turn_state - expected_turn) < 1e-9
    assert info["shadow_confident"] is True
    assert info["conflict_override_active"] is True
    assert info["selected_turn_blend"] == 0.7
    assert info["conflict_visual_evidence_gate"] == 0.5


def test_bridge_conflict_blend_keeps_base_blend_when_shadow_not_confident() -> None:
    bridge = ClosedLoopBridge(
        MockWholeBrainBackend(),
        steering_promotion={
            "enabled": True,
            "shadow_label": "shadow_fixed",
            "mode": "conflict_blend",
            "turn_blend": 0.4,
            "conflict_turn_blend": 1.0,
            "conflict_shadow_min_abs": 0.15,
            "conflict_shadow_min_ratio": 1.0,
            "shadow_turn_scale": 1.0,
            "max_abs_turn_state": 1.0,
        },
    )

    promoted_turn_state, info = bridge._promoted_turn_state(
        live_turn_state=-0.2,
        shadow_turn_state=0.05,
    )

    expected_turn = 0.6 * (-0.2) + 0.4 * 0.05
    assert abs(promoted_turn_state - expected_turn) < 1e-9
    assert info["shadow_confident"] is False
    assert info["conflict_override_active"] is False
    assert info["selected_turn_blend"] == 0.4


def test_bridge_conflict_blend_drops_to_base_when_visual_evidence_gate_zero() -> None:
    bridge = ClosedLoopBridge(
        MockWholeBrainBackend(),
        steering_promotion={
            "enabled": True,
            "shadow_label": "shadow_fixed",
            "mode": "conflict_blend",
            "turn_blend": 0.4,
            "conflict_turn_blend": 1.0,
            "conflict_shadow_min_abs": 0.15,
            "conflict_shadow_min_ratio": 1.0,
            "shadow_turn_scale": 1.0,
            "max_abs_turn_state": 1.0,
        },
    )

    promoted_turn_state, info = bridge._promoted_turn_state(
        live_turn_state=-0.2,
        shadow_turn_state=0.4,
        conflict_visual_evidence_gate=0.0,
    )

    expected_turn = 0.6 * (-0.2) + 0.4 * 0.4
    assert abs(promoted_turn_state - expected_turn) < 1e-9
    assert info["shadow_confident"] is True
    assert info["conflict_override_active"] is False
    assert info["selected_turn_blend"] == 0.4
    assert info["conflict_visual_evidence_gate"] == 0.0


def test_bridge_can_apply_refixation_override_without_sign_conflict() -> None:
    bridge = ClosedLoopBridge(
        MockWholeBrainBackend(),
        steering_promotion={
            "enabled": True,
            "shadow_label": "shadow_fixed",
            "mode": "conflict_blend",
            "turn_blend": 0.4,
            "conflict_turn_blend": 1.0,
            "refixation_turn_blend": 1.0,
            "shadow_turn_scale": 1.0,
            "max_abs_turn_state": 1.0,
        },
    )

    promoted_turn_state, info = bridge._promoted_turn_state(
        live_turn_state=0.2,
        shadow_turn_state=0.25,
        refixation_evidence_gate=1.0,
        raw_shadow_turn_state=0.8,
    )

    assert promoted_turn_state == 0.8
    assert info["refixation_override_active"] is True
    assert info["selected_mode"] == "refixation_override"
    assert info["selected_turn_blend"] == 1.0
    assert info["shadow_state_for_mix"] == 0.8


def test_decoder_uses_population_groups_as_monitor_fallback(tmp_path: Path) -> None:
    candidates_json = tmp_path / "candidates.json"
    candidates_json.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "DNp103",
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
            population_candidates_json=str(candidates_json),
            population_forward_cell_types=("DNp103",),
            population_forward_weight=1.0,
            signal_smoothing_alpha=1.0,
        )
    )

    readout = decoder.decode({101: 10.0, 102: 30.0, 201: 50.0, 202: 70.0})

    assert "DNp103" in decoder._monitor_cell_types()
    assert readout.neuron_rates["monitor_DNp103_left_hz"] == 20.0
    assert readout.neuron_rates["monitor_DNp103_right_hz"] == 60.0


def test_decoder_can_use_fitted_motor_basis_weights(tmp_path: Path) -> None:
    candidates_json = tmp_path / "candidates.json"
    candidates_json.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "DNp103",
                        "left_root_ids": [101],
                        "right_root_ids": [201],
                    },
                    {
                        "candidate_label": "DNpe040",
                        "left_root_ids": [301],
                        "right_root_ids": [401],
                    },
                    {
                        "candidate_label": "DNpe056",
                        "left_root_ids": [501],
                        "right_root_ids": [601],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    basis_json = tmp_path / "basis.json"
    basis_json.write_text(
        json.dumps(
            {
                "forward_group_weights": {"DNp103": 1.0},
                "turn_group_weights": {"DNpe040": 1.0, "DNpe056": 0.5},
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            population_candidates_json=str(candidates_json),
            motor_basis_json=str(basis_json),
            population_forward_scale_hz=50.0,
            population_turn_scale_hz=25.0,
            population_forward_weight=1.0,
            population_turn_weight=1.0,
            forward_gain=0.8,
            turn_gain=0.5,
            signal_smoothing_alpha=1.0,
        )
    )
    rates = {
        101: 60.0,
        201: 90.0,
        301: 10.0,
        401: 30.0,
        501: 5.0,
        601: 15.0,
    }

    readout = decoder.decode(rates)

    assert readout.neuron_rates["population_forward_left_hz"] == 60.0
    assert readout.neuron_rates["population_forward_right_hz"] == 90.0
    assert readout.neuron_rates["population_turn_left_hz"] == 8.333333333333334
    assert readout.neuron_rates["population_turn_right_hz"] == 25.0
    assert readout.command.right_drive > readout.command.left_drive


def test_decoder_can_gate_forward_drive_with_context_groups(tmp_path: Path) -> None:
    candidates_json = tmp_path / "candidates.json"
    candidates_json.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "DNp103",
                        "left_root_ids": [101],
                        "right_root_ids": [201],
                    },
                    {
                        "candidate_label": "DNpe016",
                        "left_root_ids": [301],
                        "right_root_ids": [401],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            population_candidates_json=str(candidates_json),
            population_forward_cell_types=("DNp103",),
            population_forward_scale_hz=50.0,
            population_forward_weight=1.0,
            forward_gain=0.8,
            forward_context_cell_types=("DNpe016",),
            forward_context_scale_hz=20.0,
            forward_context_blend=1.0,
            signal_smoothing_alpha=1.0,
        )
    )
    low_context = decoder.decode(
        {
            101: 60.0,
            201: 60.0,
            301: 0.0,
            401: 0.0,
        }
    )
    decoder.reset()
    high_context = decoder.decode(
        {
            101: 60.0,
            201: 60.0,
            301: 40.0,
            401: 40.0,
        }
    )

    assert low_context.neuron_rates["forward_context_signal"] == 0.0
    assert high_context.neuron_rates["forward_context_signal"] > 0.9
    assert high_context.command.left_drive > low_context.command.left_drive
    assert high_context.command.right_drive > low_context.command.right_drive


def test_decoder_can_boost_forward_drive_with_context_groups(tmp_path: Path) -> None:
    candidates_json = tmp_path / "candidates.json"
    candidates_json.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "DNp103",
                        "left_root_ids": [101],
                        "right_root_ids": [201],
                    },
                    {
                        "candidate_label": "DNae002",
                        "left_root_ids": [301],
                        "right_root_ids": [401],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            population_candidates_json=str(candidates_json),
            population_forward_cell_types=("DNp103",),
            population_forward_scale_hz=50.0,
            population_forward_weight=1.0,
            forward_gain=0.8,
            forward_context_cell_types=("DNae002",),
            forward_context_scale_hz=20.0,
            forward_context_mode="boost",
            forward_context_boost=0.5,
            signal_smoothing_alpha=1.0,
        )
    )
    low_context = decoder.decode(
        {
            101: 40.0,
            201: 40.0,
            301: 0.0,
            401: 0.0,
        }
    )
    decoder.reset()
    high_context = decoder.decode(
        {
            101: 40.0,
            201: 40.0,
            301: 40.0,
            401: 40.0,
        }
    )

    assert low_context.neuron_rates["forward_context_signal"] == 0.0
    assert high_context.neuron_rates["forward_context_signal"] > 0.9
    assert high_context.forward_signal > low_context.forward_signal
    assert high_context.command.left_drive > low_context.command.left_drive
    assert high_context.command.right_drive > low_context.command.right_drive


def test_decoder_can_boost_turn_with_context_groups(tmp_path: Path) -> None:
    candidates_json = tmp_path / "candidates.json"
    candidates_json.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "DNpe040",
                        "left_root_ids": [101],
                        "right_root_ids": [201],
                    },
                    {
                        "candidate_label": "DNp71",
                        "left_root_ids": [301],
                        "right_root_ids": [401],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            population_candidates_json=str(candidates_json),
            population_turn_cell_types=("DNpe040",),
            population_turn_scale_hz=20.0,
            population_turn_weight=1.0,
            turn_gain=0.5,
            turn_context_cell_types=("DNp71",),
            turn_context_scale_hz=20.0,
            turn_context_boost=1.0,
            signal_smoothing_alpha=1.0,
        )
    )
    no_context = decoder.decode(
        {
            101: 10.0,
            201: 40.0,
            301: 0.0,
            401: 0.0,
        }
    )
    decoder.reset()
    with_context = decoder.decode(
        {
            101: 10.0,
            201: 40.0,
            301: 40.0,
            401: 40.0,
        }
    )

    assert no_context.neuron_rates["turn_context_signal"] == 0.0
    assert with_context.neuron_rates["turn_context_signal"] > 0.9
    assert with_context.turn_signal > no_context.turn_signal
    assert with_context.command.right_drive - with_context.command.left_drive > no_context.command.right_drive - no_context.command.left_drive



def test_decoder_can_boost_turn_with_aligned_asymmetry_context_groups(tmp_path: Path) -> None:
    candidates_json = tmp_path / "candidates.json"
    candidates_json.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "DNpe040",
                        "left_root_ids": [101],
                        "right_root_ids": [201],
                    },
                    {
                        "candidate_label": "DNpe056",
                        "left_root_ids": [301],
                        "right_root_ids": [401],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    decoder = MotorDecoder(
        DecoderConfig(
            population_candidates_json=str(candidates_json),
            population_turn_cell_types=("DNpe040",),
            population_turn_scale_hz=20.0,
            population_turn_weight=1.0,
            turn_gain=0.5,
            turn_context_cell_types=("DNpe056",),
            turn_context_scale_hz=20.0,
            turn_context_mode="aligned_asymmetry",
            turn_context_boost=1.0,
            signal_smoothing_alpha=1.0,
        )
    )
    aligned_context = decoder.decode(
        {
            101: 10.0,
            201: 40.0,
            301: 10.0,
            401: 40.0,
        }
    )
    decoder.reset()
    opposed_context = decoder.decode(
        {
            101: 10.0,
            201: 40.0,
            301: 40.0,
            401: 10.0,
        }
    )

    assert aligned_context.neuron_rates["turn_context_asymmetry_signal"] > 0.9
    assert aligned_context.neuron_rates["turn_context_signal"] > 0.9
    assert opposed_context.neuron_rates["turn_context_asymmetry_signal"] < -0.9
    assert opposed_context.neuron_rates["turn_context_signal"] == 0.0
    assert aligned_context.turn_signal > opposed_context.turn_signal
    assert aligned_context.command.right_drive - aligned_context.command.left_drive > opposed_context.command.right_drive - opposed_context.command.left_drive


def test_decoder_can_gate_forward_from_context_population(tmp_path: Path) -> None:
    candidates_json = tmp_path / "candidates.json"
    candidates_json.write_text(
        json.dumps(
            {
                "selected_paired_cell_types": [
                    {
                        "candidate_label": "DNp103",
                        "left_root_ids": [101],
                        "right_root_ids": [201],
                    },
                    {
                        "candidate_label": "DNpe016",
                        "left_root_ids": [301],
                        "right_root_ids": [401],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    config = DecoderConfig(
        population_candidates_json=str(candidates_json),
        population_forward_cell_types=("DNp103",),
        population_forward_scale_hz=50.0,
        population_forward_weight=1.0,
        forward_context_cell_types=("DNpe016",),
        forward_context_scale_hz=20.0,
        forward_context_blend=1.0,
        forward_gain=0.8,
        signal_smoothing_alpha=1.0,
    )
    low_context_decoder = MotorDecoder(config)
    high_context_decoder = MotorDecoder(config)
    low_context = low_context_decoder.decode({101: 80.0, 201: 80.0, 301: 0.0, 401: 0.0})
    high_context = high_context_decoder.decode({101: 80.0, 201: 80.0, 301: 50.0, 401: 50.0})

    assert high_context.neuron_rates["forward_context_signal"] > low_context.neuron_rates["forward_context_signal"]
    assert high_context.command.left_drive > low_context.command.left_drive
    assert high_context.command.right_drive > low_context.command.right_drive


def test_decoder_turn_priority_strengthens_hybrid_turn_execution() -> None:
    base_decoder = MotorDecoder(
        DecoderConfig(
            command_mode="hybrid_multidrive",
            turn_gain=0.6,
            latent_freq_bias=0.8,
            latent_freq_gain=0.4,
            latent_turn_amp_gain=0.2,
            latent_turn_freq_gain=0.1,
            signal_smoothing_alpha=1.0,
        )
    )
    priority_decoder = MotorDecoder(
        DecoderConfig(
            command_mode="hybrid_multidrive",
            turn_gain=0.6,
            latent_freq_bias=0.8,
            latent_freq_gain=0.4,
            latent_turn_amp_gain=0.2,
            latent_turn_freq_gain=0.1,
            latent_turn_priority_outer_amp_gain=0.5,
            latent_turn_priority_inner_amp_gain=0.2,
            latent_turn_priority_outer_freq_gain=0.4,
            latent_turn_priority_inner_freq_gain=0.2,
            signal_smoothing_alpha=1.0,
        )
    )
    rates = {
        DNA01_LEFT: 0.0,
        DNA02_LEFT: 0.0,
        DNA01_RIGHT: 80.0,
        DNA02_RIGHT: 80.0,
        P9_LEFT: 0.0,
        P9_RIGHT: 0.0,
        P9_ODN1_LEFT: 0.0,
        P9_ODN1_RIGHT: 0.0,
        MDN_1: 0.0,
        MDN_2: 0.0,
        MDN_3: 0.0,
        MDN_4: 0.0,
    }

    base_readout = base_decoder.decode(rates)
    priority_readout = priority_decoder.decode(rates)

    assert isinstance(base_readout.command, HybridDriveCommand)
    assert isinstance(priority_readout.command, HybridDriveCommand)
    assert priority_readout.neuron_rates["turn_priority"] > 0.0
    assert priority_readout.command.right_amp > base_readout.command.right_amp
    assert priority_readout.command.right_freq_scale > base_readout.command.right_freq_scale
    assert priority_readout.command.left_freq_scale < base_readout.command.left_freq_scale

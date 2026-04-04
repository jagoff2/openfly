from __future__ import annotations

import json
from pathlib import Path

from body.interfaces import HybridDriveCommand
from bridge.decoder_factory import build_motor_decoder
from runtime.closed_loop import load_config
from vnc.ingest import load_vnc_graph_slice
from vnc.spec_builder import build_vnc_structural_spec
from vnc.spec_decoder import VNCSpecDecoder, VNCSpecDecoderConfig


def test_build_vnc_structural_spec_summarizes_descending_motor_weights(tmp_path: Path) -> None:
    annotation_path = tmp_path / "annotations.csv"
    edge_path = tmp_path / "edges.csv"
    annotation_path.write_text(
        "\n".join(
            [
                "pt_root_id,region,flow,super_class,cell_class,cell_type,side",
                "11,brain,efferent,descending,motor,DNa02,L",
                "12,brain,efferent,descending,motor,DNa01,R",
                "21,ventral_nerve_cord,intrinsic,interneuron,premotor,PMN-L,L",
                "22,ventral_nerve_cord,intrinsic,interneuron,premotor,PMN-R,R",
                "31,ventral_nerve_cord,efferent,motor,motor,MN-L,L",
                "32,ventral_nerve_cord,efferent,motor,motor,MN-R,R",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    edge_path.write_text(
        "\n".join(
            [
                "pre_pt_root_id,post_pt_root_id,n",
                "11,21,10",
                "21,31,8",
                "11,31,3",
                "12,22,9",
                "22,32,7",
                "12,32,2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    graph = load_vnc_graph_slice(annotation_path, edge_path)
    spec = build_vnc_structural_spec(graph)

    assert spec.descending_channel_count == 2
    assert spec.left_motor_total_weight == 11
    assert spec.right_motor_total_weight == 9
    assert spec.channels[0].cell_type == "DNa02"
    assert spec.channels[0].left_total_weight == 11
    assert spec.channels[1].cell_type == "DNa01"
    assert spec.channels[1].right_total_weight == 9


def test_vnc_spec_decoder_uses_structural_weights_for_turn_and_forward(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "channels": [
                    {
                        "root_id": 11,
                        "cell_type": "DNa02",
                        "side": "left",
                        "left_total_weight": 11,
                        "right_total_weight": 1,
                        "total_motor_weight": 12,
                    },
                    {
                        "root_id": 12,
                        "cell_type": "DNa01",
                        "side": "right",
                        "left_total_weight": 1,
                        "right_total_weight": 13,
                        "total_motor_weight": 14,
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    decoder = VNCSpecDecoder(
        VNCSpecDecoderConfig(
            spec_json=str(spec_path),
            forward_scale_hz=20.0,
            turn_scale_hz=10.0,
            forward_gain=0.6,
            turn_gain=0.4,
            monitor_top_channels=2,
        )
    )
    readout = decoder.decode({11: 5.0, 12: 15.0})

    assert decoder.required_neuron_ids() == [11, 12]
    assert readout.forward_signal > 0.0
    assert readout.turn_signal > 0.0
    assert isinstance(readout.command, HybridDriveCommand)
    assert readout.command.right_drive > readout.command.left_drive
    assert "weighted_left_motor_drive_hz" in readout.neuron_rates
    assert "vnc_rate_dna01_right_12_hz" in readout.neuron_rates


def test_vnc_spec_decoder_supports_monitor_id_groups(tmp_path: Path) -> None:
    spec_path = tmp_path / "semantic-spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "channels": [
                    {
                        "root_id": 101,
                        "cell_type": "DNg97",
                        "side": "left",
                        "left_total_weight": 8,
                        "right_total_weight": 2,
                        "total_motor_weight": 10,
                        "monitor_ids": [720575940000000001, 720575940000000002],
                        "source_root_ids": [101, 102],
                        "monitor_match_field": "cell_type",
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    decoder = VNCSpecDecoder(
        VNCSpecDecoderConfig(
            spec_json=str(spec_path),
            forward_scale_hz=4.0,
            turn_scale_hz=4.0,
            monitor_reduce="mean",
        )
    )
    readout = decoder.decode(
        {
            720575940000000001: 6.0,
            720575940000000002: 10.0,
        }
    )

    assert decoder.required_neuron_ids() == [720575940000000001, 720575940000000002]
    assert readout.neuron_rates["vnc_rate_dng97_left_hz"] == 8.0
    assert readout.neuron_rates["vnc_required_monitor_id_count"] == 2.0
    assert readout.neuron_rates["normalized_left_motor_rate_hz"] == 8.0
    assert readout.neuron_rates["normalized_right_motor_rate_hz"] == 8.0
    assert readout.forward_signal > 0.0


def test_decoder_factory_builds_vnc_structural_spec_decoder(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "channels": [
                    {
                        "root_id": 101,
                        "cell_type": "DNg97",
                        "side": "left",
                        "left_total_weight": 4,
                        "right_total_weight": 2,
                        "total_motor_weight": 6,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    decoder = build_motor_decoder(
        {
            "type": "vnc_structural_spec",
            "spec_json": str(spec_path),
            "command_mode": "hybrid_multidrive",
        }
    )

    assert isinstance(decoder, VNCSpecDecoder)
    assert decoder.required_neuron_ids() == [101]


def test_real_exit_nerve_vnc_config_loads_structural_decoder_with_filtered_channels() -> None:
    config = load_config("configs/mock_vnc_structural_spec_exit_nerve.yaml")
    decoder = build_motor_decoder(config.get("decoder"))

    assert isinstance(decoder, VNCSpecDecoder)
    assert decoder.config.spec_json == "outputs/metrics/manc_thoracic_structural_spec_exit_nerve.json"
    assert decoder.config.min_total_weight == 500.0

    spec_payload = json.loads(Path(decoder.config.spec_json).read_text(encoding="utf-8"))
    expected_count = sum(1 for channel in spec_payload["channels"] if float(channel["total_motor_weight"]) >= decoder.config.min_total_weight)

    assert len(decoder.channels) == expected_count
    assert len(decoder.required_neuron_ids()) == expected_count
    assert expected_count > 500


def test_real_flywire_semantic_vnc_config_loads_flywire_monitor_ids() -> None:
    config = load_config("configs/mock_vnc_structural_spec_exit_nerve_flywire_semantic.yaml")
    decoder = build_motor_decoder(config.get("decoder"))

    assert isinstance(decoder, VNCSpecDecoder)
    assert decoder.config.spec_json == "outputs/metrics/manc_thoracic_structural_spec_exit_nerve_flywire_semantic.json"
    assert decoder.config.monitor_reduce == "mean"
    assert decoder.config.weight_normalization_mode == "by_side_total"
    assert len(decoder.channels) > 500
    assert len(decoder.required_neuron_ids()) > 600
    assert min(decoder.required_neuron_ids()) > 10**12

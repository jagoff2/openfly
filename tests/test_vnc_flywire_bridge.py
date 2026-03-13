from __future__ import annotations

from pathlib import Path

from vnc.flywire_bridge import build_flywire_semantic_spec_from_files, FlyWireSemanticBridgeConfig


def test_build_flywire_semantic_spec_prefers_exact_cell_type_and_falls_back_to_hemibrain(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.json"
    annotation_path = tmp_path / "annotations.tsv"
    spec_path.write_text(
        """
{
  "channels": [
    {
      "root_id": 101,
      "cell_type": "DNg97",
      "side": "left",
      "left_total_weight": 10,
      "right_total_weight": 2,
      "total_motor_weight": 12,
      "motor_target_count": 3
    },
    {
      "root_id": 102,
      "cell_type": "DNg97",
      "side": "left",
      "left_total_weight": 14,
      "right_total_weight": 6,
      "total_motor_weight": 20,
      "motor_target_count": 5
    },
    {
      "root_id": 103,
      "cell_type": "DNa02",
      "side": "right",
      "left_total_weight": 1,
      "right_total_weight": 9,
      "total_motor_weight": 10,
      "motor_target_count": 2
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )
    annotation_path.write_text(
        "\n".join(
            [
                "root_id\tcell_type\themibrain_type\tside",
                "720575940000000001\tDNg97\t\tleft",
                "720575940000000002\tDNg97\t\tleft",
                "720575940000000003\tDNae001\tDNa02\tright",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = build_flywire_semantic_spec_from_files(
        FlyWireSemanticBridgeConfig(
            source_spec_json=str(spec_path),
            annotation_path=str(annotation_path),
            brain_completeness_path=None,
            aggregate_weights="mean",
        )
    )

    assert payload["source_channel_count"] == 3
    assert payload["bridged_channel_count"] == 2
    assert payload["matched_source_channel_count"] == 3
    assert payload["required_monitor_id_count"] == 3

    channels = {(item["cell_type"], item["side"]): item for item in payload["channels"]}
    dng97_left = channels[("DNg97", "left")]
    dna02_right = channels[("DNa02", "right")]

    assert dng97_left["monitor_match_field"] == "cell_type"
    assert dng97_left["source_channel_count"] == 2
    assert dng97_left["source_root_ids"] == [101, 102]
    assert dng97_left["left_total_weight"] == 12.0
    assert dng97_left["right_total_weight"] == 4.0
    assert dng97_left["monitor_ids"] == [720575940000000001, 720575940000000002]

    assert dna02_right["monitor_match_field"] == "hemibrain_type"
    assert dna02_right["monitor_ids"] == [720575940000000003]

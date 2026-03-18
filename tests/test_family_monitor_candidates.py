from __future__ import annotations

import json
from pathlib import Path

from scripts.build_family_monitor_candidates import build_candidates, load_annotation_table


def test_build_family_monitor_candidates_builds_bilateral_groups(tmp_path: Path) -> None:
    annotation_path = tmp_path / "annotation.tsv"
    annotation_path.write_text(
        "\n".join(
            [
                "root_id\tcell_type\themibrain_type\tside\tsuper_class\tflow",
                "1\tRelayA\t\tleft\tcentral\tintrinsic",
                "2\tRelayA\t\tright\tcentral\tintrinsic",
                "3\t\tRelayB\tleft\tascending\tafferent",
                "4\t\tRelayB\tright\tascending\tafferent",
            ]
        ),
        encoding="utf-8",
    )

    annotation_df = load_annotation_table(annotation_path)
    payload = build_candidates(annotation_df, families=["RelayA", "RelayB"], min_roots_per_side=1)

    labels = [item["candidate_label"] for item in payload["selected_paired_cell_types"]]

    assert labels == ["RelayA", "RelayB"]
    assert payload["selected_paired_cell_types"][1]["left_hemibrain_types"] == ["RelayB"]


def test_build_family_monitor_candidates_merge_logic_skips_duplicates(tmp_path: Path) -> None:
    base = {
        "selection_rule": ["base"],
        "selected_paired_cell_types": [
            {"candidate_label": "RelayA", "left_root_ids": [1], "right_root_ids": [2]},
        ],
    }
    base_path = tmp_path / "base.json"
    base_path.write_text(json.dumps(base), encoding="utf-8")

    merged_labels = {item["candidate_label"] for item in json.loads(base_path.read_text(encoding="utf-8"))["selected_paired_cell_types"]}

    assert merged_labels == {"RelayA"}

from __future__ import annotations

import json
from pathlib import Path

from scripts.run_descending_motor_atlas import _default_side_modes, _load_candidate_map, _stim_ids


def test_load_candidate_map_and_stim_ids(tmp_path: Path) -> None:
    payload = {
        "selected_paired_cell_types": [
            {
                "candidate_label": "DNp71",
                "left_root_ids": [1, 2],
                "right_root_ids": [3],
            }
        ]
    }
    path = tmp_path / "candidates.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    candidate_map = _load_candidate_map(path)

    assert candidate_map == {"DNp71": {"left": [1, 2], "right": [3]}}
    assert _stim_ids(candidate_map, "DNp71", "left") == [1, 2]
    assert _stim_ids(candidate_map, "DNp71", "right") == [3]
    assert _stim_ids(candidate_map, "DNp71", "bilateral") == [1, 2, 3]
    assert _stim_ids(candidate_map, "baseline", "baseline") == []


def test_default_side_modes_respects_bilateral_labels() -> None:
    bilateral_labels = {"DNg97", "DNp103"}

    assert _default_side_modes("DNg97", bilateral_labels) == ["bilateral"]
    assert _default_side_modes("DNp71", bilateral_labels) == ["left", "right"]

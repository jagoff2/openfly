from __future__ import annotations

from pathlib import Path

import numpy as np

from vision.inferred_lateralized import (
    InferredLateralizedFeatureExtractor,
    load_inferred_lateralized_candidates,
    select_recommended_candidates,
)


def test_load_inferred_candidates_assigns_eye_diff_polarity(tmp_path: Path) -> None:
    csv_path = tmp_path / "candidates.csv"
    csv_path.write_text(
        "\n".join(
            [
                "cell_type,mirror_selectivity_score,body_right_eye_diff,is_tracking_cell,is_flow_cell,sign_flip_consistent",
                "TmY14,0.4,0.2,True,False,True",
                "T4b,0.07,-0.03,False,True,True",
                "skip_me,0.01,0.0,True,False,True",
            ]
        ),
        encoding="utf-8",
    )

    loaded = load_inferred_lateralized_candidates(csv_path, min_score=0.02)

    assert [candidate.cell_type for candidate in loaded] == ["TmY14", "T4b"]
    assert loaded[0].right_side_polarity == 1.0
    assert loaded[1].right_side_polarity == -1.0


def test_select_recommended_candidates_keeps_tracking_and_flow_mix() -> None:
    candidates = load_inferred_lateralized_candidates(
        "outputs/metrics/inferred_lateralized_visual_candidates.csv",
        min_score=0.02,
    )

    selected = select_recommended_candidates(candidates, tracking_limit=2, flow_limit=2)

    assert [candidate.cell_type for candidate in selected] == ["TmY14", "TmY15", "T5d", "T5c"]


def test_extractor_turn_bias_matches_candidate_polarity() -> None:
    extractor = InferredLateralizedFeatureExtractor.from_probe_csv(
        Path("outputs/metrics/inferred_lateralized_visual_candidates.csv"),
        min_score=0.02,
        tracking_limit=1,
        flow_limit=1,
    )
    index_map = {"TmY14": np.array([0]), "T5d": np.array([1])}

    right_biased = np.array([[3.0, 4.0], [1.0, 1.0]], dtype=float)
    left_biased = np.array([[1.0, 1.0], [3.0, 4.0]], dtype=float)

    right_features = extractor.extract_from_array(right_biased, index_map)
    left_features = extractor.extract_from_array(left_biased, index_map)

    assert right_features.turn_bias > 0.0
    assert right_features.right_evidence > 0.0
    assert right_features.left_evidence == 0.0
    assert right_features.active_candidate_count == 2

    assert left_features.turn_bias < 0.0
    assert left_features.left_evidence > 0.0
    assert left_features.right_evidence == 0.0
